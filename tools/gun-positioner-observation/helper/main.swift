// GPOCapture — camera helper for tools/gun-positioner-observation.
//
//   GPOCapture list                     video devices: unique ID, name, model, formats (JSON)
//   GPOCapture clock                    CLOCK_UPTIME_RAW and the CoreMedia host clock, in ns (JSON)
//   GPOCapture synthetic [--frames N] [--width W] [--height H] [--fps F] [--drop-at i,j]
//   GPOCapture capture --unique-id ID [--width 3840] [--height 2160] [--fps 30]
//                      [--subtypes dmb1,jpeg,420v,420f,yuvs,2vuy] [--chroma 0|1] [--seconds S]
//
// A CAMERA IS NAMED BY ITS AVFOUNDATION UNIQUE ID. Two cameras of one model share a
// name, and device indices move whenever another camera appears; a UVC camera's
// unique ID carries its USB location and vendor/product IDs, so it stays put while
// the camera stays in its port.
//
// SAMPLES ARRIVE IN THE DEVICE'S NATIVE FORMAT. AVCaptureVideoDataOutput.videoSettings
// set to an empty dictionary delivers native samples (AVCaptureVideoDataOutput.h). A
// compressed format ('dmb1', 'jpeg') is written out byte for byte as codec "jpeg". macOS
// presents UVC Motion-JPEG cameras as decoded formats instead ('420v' and 'yuvs' for the
// bench's 16MP UVC camera); those samples are written as their luma plane (codec
// "gray8"), or luma followed by the interleaved CbCr plane (codec "nv12", --chroma 1),
// without row padding. The first --subtypes entry the device offers at the requested size
// is used.
//
// STREAM: b"GPO1" | u32le header length | u32le payload length | header JSON | payload.
// pts_ns is the sample's presentation time converted to the host clock; host_ns is
// clock_gettime_nsec_np(CLOCK_UPTIME_RAW) in the sample callback; both count the same
// mach ticks as Python's time.monotonic_ns() on macOS (`clock` checks this). Dropped
// samples reported by captureOutput(_:didDrop:from:) are written as "drop" messages.
//
// No laser, motion or camera-control command exists here. Capture mode has not been run
// against a camera; list, clock and synthetic modes are exercised by the Python tests.

import AVFoundation
import AppKit
import CoreMedia
import Foundation
import ImageIO
import UniformTypeIdentifiers

signal(SIGPIPE, SIG_IGN)
let helperVersion = "1"
let output = FileHandle.standardOutput
let outputLock = NSLock()

func hostNowNs() -> UInt64 { clock_gettime_nsec_np(CLOCK_UPTIME_RAW) }

@discardableResult
func emit(_ header: [String: Any], _ payload: Data = Data()) -> Bool {
  guard let h = try? JSONSerialization.data(withJSONObject: header, options: [.sortedKeys]) else { return false }
  var packet = Data("GPO1".utf8)
  var hl = UInt32(h.count).littleEndian
  var pl = UInt32(payload.count).littleEndian
  withUnsafeBytes(of: &hl) { packet.append(contentsOf: $0) }
  withUnsafeBytes(of: &pl) { packet.append(contentsOf: $0) }
  packet.append(h)
  packet.append(payload)
  outputLock.lock()
  defer { outputLock.unlock() }
  do { try output.write(contentsOf: packet); return true } catch { return false }
}

func printJSON(_ value: Any) {
  if let d = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys, .prettyPrinted]) {
    try? output.write(contentsOf: d + Data("\n".utf8))
  }
}

func fail(_ message: String, _ code: Int32) -> Never {
  emit(["type": "error", "message": message])
  FileHandle.standardError.write(Data((message + "\n").utf8))
  exit(code)
}

func fourCC(_ v: FourCharCode) -> String {
  let bytes = [UInt8((v >> 24) & 255), UInt8((v >> 16) & 255), UInt8((v >> 8) & 255), UInt8(v & 255)]
  return String(bytes: bytes, encoding: .ascii) ?? String(v)
}

func ns(_ t: CMTime) -> Int64? {
  guard t.isValid, !t.isIndefinite else { return nil }
  return CMTimeConvertScale(t, timescale: 1_000_000_000, method: .roundHalfAwayFromZero).value
}

var options = [String: String]()
let argv = Array(CommandLine.arguments.dropFirst())
let mode = argv.first ?? ""
do {
  var i = 1
  while i < argv.count {
    let key = argv[i]
    if key.hasPrefix("--"), i + 1 < argv.count { options[String(key.dropFirst(2))] = argv[i + 1]; i += 2 } else { i += 1 }
  }
}
func opt(_ k: String, _ d: String) -> String { options[k] ?? d }

func devices() -> [AVCaptureDevice] {
  var types: [AVCaptureDevice.DeviceType] = [.builtInWideAngleCamera]
  if #available(macOS 14.0, *) { types += [.external, .continuityCamera, .deskViewCamera] } else { types.append(.externalUnknown) }
  return AVCaptureDevice.DiscoverySession(deviceTypes: types, mediaType: .video, position: .unspecified).devices
}

func describe(_ f: AVCaptureDevice.Format) -> [String: Any] {
  let d = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
  return ["subtype": fourCC(CMFormatDescriptionGetMediaSubType(f.formatDescription)),
          "width": Int(d.width), "height": Int(d.height),
          "fps": f.videoSupportedFrameRateRanges.map { [$0.minFrameRate, $0.maxFrameRate] }]
}

switch mode {
case "list":
  printJSON(devices().map { d in
    ["unique_id": d.uniqueID, "name": d.localizedName, "model_id": d.modelID,
     "manufacturer": d.manufacturer, "device_type": d.deviceType.rawValue,
     "formats": d.formats.map(describe)] as [String: Any]
  })
  exit(0)

case "clock":
  let raw = hostNowNs()
  let host = ns(CMClockGetTime(CMClockGetHostTimeClock())) ?? -1
  printJSON(["uptime_raw_ns": raw, "host_time_clock_ns": host])
  exit(0)

case "synthetic":
  let frames = Int(opt("frames", "10")) ?? 10
  let width = Int(opt("width", "64")) ?? 64
  let height = Int(opt("height", "36")) ?? 36
  let fps = Double(opt("fps", "30")) ?? 30
  let drops = Set(opt("drop-at", "").split(separator: ",").compactMap { Int($0) })
  let interval = UInt64(1e9 / fps)
  emit(["type": "hello", "mode": "synthetic", "helper_version": helperVersion, "width": width, "height": height,
        "clock": "pts_ns and host_ns: CLOCK_UPTIME_RAW"])
  let space = CGColorSpaceCreateDeviceGray()
  var seq = 0, dropped = 0
  for i in 0..<frames {
    let pts = hostNowNs()
    if drops.contains(i) {
      emit(["type": "drop", "pts_ns": pts, "host_ns": hostNowNs(), "reason": "synthetic"])
      dropped += 1
    } else {
      guard let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: width,
                                space: space, bitmapInfo: CGImageAlphaInfo.none.rawValue) else { fail("context", 4) }
      ctx.setFillColor(gray: CGFloat(i % 10) / 10, alpha: 1)
      ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
      let jpeg = NSMutableData()
      guard let image = ctx.makeImage(),
            let dest = CGImageDestinationCreateWithData(jpeg, UTType.jpeg.identifier as CFString, 1, nil) else {
        fail("jpeg encoder", 4)
      }
      CGImageDestinationAddImage(dest, image, nil)
      CGImageDestinationFinalize(dest)
      seq += 1
      if opt("codec", "jpeg") == "gray8" {
        var luma = Data(count: width * height)
        luma.withUnsafeMutableBytes { raw in
          let p = raw.bindMemory(to: UInt8.self)
          for k in 0..<(width * height) { p[k] = UInt8((k + i * 7) % 251) }
        }
        emit(["type": "frame", "seq": seq, "pts_ns": pts, "host_ns": hostNowNs(), "duration_ns": interval,
              "subtype": "420v", "codec": "gray8", "range": "video", "width": width, "height": height], luma)
      } else {
        emit(["type": "frame", "seq": seq, "pts_ns": pts, "host_ns": hostNowNs(), "duration_ns": interval,
              "subtype": "jpeg", "codec": "jpeg", "width": width, "height": height], jpeg as Data)
      }
    }
    usleep(UInt32(interval / 1000))
  }
  emit(["type": "bye", "frames": seq, "drops": dropped])
  exit(0)

case "capture":
  break

default:
  FileHandle.standardError.write(Data("usage: GPOCapture list | clock | synthetic | capture --unique-id ID\n".utf8))
  exit(2)
}

// ---- capture -------------------------------------------------------------------------------

let uniqueID = opt("unique-id", "")
guard !uniqueID.isEmpty else { fail("capture needs --unique-id (see `GPOCapture list`)", 2) }
guard let device = AVCaptureDevice(uniqueID: uniqueID) else { fail("no video device with unique id \(uniqueID)", 10) }
let wantW = Int32(opt("width", "3840")) ?? 3840
let wantH = Int32(opt("height", "2160")) ?? 2160
let wantFps = Double(opt("fps", "30")) ?? 30
let subtypeOrder = opt("subtypes", "dmb1,jpeg,420v,420f,yuvs,2vuy").split(separator: ",").map(String.init)
let subtypes = Set(subtypeOrder)
let wantChroma = opt("chroma", "0") == "1"
let seconds = Double(opt("seconds", "0")) ?? 0

// The camera prompt is a window and belongs to a foreground app (as in PanelCamShot).
if AVCaptureDevice.authorizationStatus(for: .video) == .notDetermined {
  NSApplication.shared.setActivationPolicy(.regular)
  NSApplication.shared.activate(ignoringOtherApps: true)
}
let gate = DispatchSemaphore(value: 0)
var granted = false
AVCaptureDevice.requestAccess(for: .video) { ok in granted = ok; gate.signal() }
if gate.wait(timeout: .now() + 3600) == .timedOut { fail("no answer to the camera permission prompt", 3) }
guard granted else { fail("camera access denied", 3) }

let candidates = device.formats.filter {
  let d = CMVideoFormatDescriptionGetDimensions($0.formatDescription)
  return d.width == wantW && d.height == wantH && subtypes.contains(fourCC(CMFormatDescriptionGetMediaSubType($0.formatDescription)))
}
func rank(_ f: AVCaptureDevice.Format) -> Int {
  subtypeOrder.firstIndex(of: fourCC(CMFormatDescriptionGetMediaSubType(f.formatDescription))) ?? Int.max
}
let ordered = candidates.sorted { rank($0) < rank($1) }
let format = ordered.first { $0.videoSupportedFrameRateRanges.contains { $0.minFrameRate <= wantFps && wantFps <= $0.maxFrameRate } }
  ?? ordered.first
guard let chosen = format else {
  fail("no \(wantW)x\(wantH) format in \(subtypes.sorted()); device offers \(device.formats.map(describe))", 13)
}

final class Sink: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
  var seq = 0
  var drops = 0
  var syncClock: CMClock?

  func hostNs(_ t: CMTime) -> Int64? {
    guard let clock = syncClock else { return ns(t) }
    return ns(CMSyncConvertTime(t, from: clock, to: CMClockGetHostTimeClock()))
  }

  // Luma (and optionally chroma) of a decoded sample, without row padding.
  func planes(_ pb: CVPixelBuffer) -> (Data, String, String)? {
    CVPixelBufferLockBaseAddress(pb, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(pb, .readOnly) }
    let pf = CVPixelBufferGetPixelFormatType(pb)
    let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb)
    var data = Data(capacity: wantChroma ? w * h * 3 / 2 : w * h)
    switch pf {
    case kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange, kCVPixelFormatType_420YpCbCr8BiPlanarFullRange:
      for plane in 0..<(wantChroma ? 2 : 1) {
        guard let base = CVPixelBufferGetBaseAddressOfPlane(pb, plane) else { return nil }
        let stride = CVPixelBufferGetBytesPerRowOfPlane(pb, plane)
        let rows = CVPixelBufferGetHeightOfPlane(pb, plane)
        for r in 0..<rows { data.append(base.advanced(by: r * stride).assumingMemoryBound(to: UInt8.self), count: w) }
      }
      let range = pf == kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange ? "video" : "full"
      return (data, wantChroma ? "nv12" : "gray8", range)
    case kCVPixelFormatType_422YpCbCr8_yuvs, kCVPixelFormatType_422YpCbCr8:
      guard let base = CVPixelBufferGetBaseAddress(pb) else { return nil }
      let stride = CVPixelBufferGetBytesPerRow(pb)
      let first = pf == kCVPixelFormatType_422YpCbCr8_yuvs ? 0 : 1      // YUYV vs UYVY
      var row = [UInt8](repeating: 0, count: w)
      for r in 0..<h {
        let p = base.advanced(by: r * stride).assumingMemoryBound(to: UInt8.self)
        for x in 0..<w { row[x] = p[2 * x + first] }
        data.append(contentsOf: row)
      }
      return (data, "gray8", "video")
    default:
      return nil
    }
  }

  func captureOutput(_ output: AVCaptureOutput, didOutput sample: CMSampleBuffer, from connection: AVCaptureConnection) {
    let received = hostNowNs()
    var header: [String: Any] = ["type": "frame", "host_ns": received]
    var payload = Data()
    if let block = CMSampleBufferGetDataBuffer(sample) {
      let length = CMBlockBufferGetDataLength(block)
      payload = Data(count: length)
      let status = payload.withUnsafeMutableBytes {
        CMBlockBufferCopyDataBytes(block, atOffset: 0, dataLength: length, destination: $0.baseAddress!)
      }
      guard status == kCMBlockBufferNoErr else { return }
      header["codec"] = "jpeg"
    } else if let pb = CMSampleBufferGetImageBuffer(sample) {
      guard let (data, codec, range) = planes(pb) else {
        fail("unsupported native pixel format \(fourCC(CVPixelBufferGetPixelFormatType(pb)))", 14)
      }
      payload = data
      header["codec"] = codec
      header["range"] = range
      header["pixel_format"] = fourCC(CVPixelBufferGetPixelFormatType(pb))
      header["width"] = CVPixelBufferGetWidth(pb)
      header["height"] = CVPixelBufferGetHeight(pb)
    } else {
      return
    }
    seq += 1
    header["seq"] = seq
    if let pts = hostNs(CMSampleBufferGetPresentationTimeStamp(sample)) { header["pts_ns"] = pts }
    if let dur = ns(CMSampleBufferGetDuration(sample)) { header["duration_ns"] = dur }
    if let desc = CMSampleBufferGetFormatDescription(sample) {
      let d = CMVideoFormatDescriptionGetDimensions(desc)
      header["subtype"] = fourCC(CMFormatDescriptionGetMediaSubType(desc))
      if header["width"] == nil { header["width"] = Int(d.width); header["height"] = Int(d.height) }
    }
    if !emit(header, payload) { exit(0) }   // the reader has gone
  }

  func captureOutput(_ output: AVCaptureOutput, didDrop sample: CMSampleBuffer, from connection: AVCaptureConnection) {
    drops += 1
    var header: [String: Any] = ["type": "drop", "host_ns": hostNowNs()]
    if let pts = hostNs(CMSampleBufferGetPresentationTimeStamp(sample)) { header["pts_ns"] = pts }
    if let reason = CMGetAttachment(sample, key: kCMSampleBufferAttachmentKey_DroppedFrameReason, attachmentModeOut: nil) {
      header["reason"] = "\(reason)"
    }
    if !emit(header) { exit(0) }
  }
}

let session = AVCaptureSession()
let sink = Sink()
let queue = DispatchQueue(label: "gpocapture.samples")
session.beginConfiguration()
do {
  let input = try AVCaptureDeviceInput(device: device)
  guard session.canAddInput(input) else { fail("session refused the device input", 11) }
  session.addInput(input)
} catch { fail("device input: \(error.localizedDescription)", 11) }
let videoOut = AVCaptureVideoDataOutput()
videoOut.videoSettings = [:]
videoOut.alwaysDiscardsLateVideoFrames = true
videoOut.setSampleBufferDelegate(sink, queue: queue)
guard session.canAddOutput(videoOut) else { fail("session refused the data output", 12) }
session.addOutput(videoOut)
do {
  try device.lockForConfiguration()
  device.activeFormat = chosen
  if chosen.videoSupportedFrameRateRanges.contains(where: { $0.minFrameRate <= wantFps && wantFps <= $0.maxFrameRate }) {
    let frame = CMTime(value: 1_000_000, timescale: CMTimeScale(wantFps * 1_000_000))
    device.activeVideoMinFrameDuration = frame
    device.activeVideoMaxFrameDuration = frame
  }
  device.unlockForConfiguration()
} catch { fail("device configuration: \(error.localizedDescription)", 13) }
session.commitConfiguration()
if #available(macOS 12.3, *) { sink.syncClock = session.synchronizationClock }

emit(["type": "hello", "mode": "capture", "helper_version": helperVersion, "unique_id": device.uniqueID,
      "name": device.localizedName, "model_id": device.modelID, "active_format": describe(device.activeFormat),
      "requested": ["width": Int(wantW), "height": Int(wantH), "fps": wantFps, "subtypes": subtypeOrder,
                    "chroma": wantChroma],
      "clock": "pts_ns: presentation time converted to CMClockGetHostTimeClock; host_ns: CLOCK_UPTIME_RAW"])

let finish: () -> Never = {
  session.stopRunning()
  queue.sync {}
  emit(["type": "bye", "frames": sink.seq, "drops": sink.drops])
  exit(0)
}
for sig in [SIGTERM, SIGINT] {
  signal(sig, SIG_IGN)
  let source = DispatchSource.makeSignalSource(signal: sig, queue: .main)
  source.setEventHandler { finish() }
  source.resume()
  objc_setAssociatedObject(session, "signal\(sig)", source, .OBJC_ASSOCIATION_RETAIN)
}
session.startRunning()
if seconds > 0 {
  DispatchQueue.main.asyncAfter(deadline: .now() + seconds) { finish() }
}
dispatchMain()
