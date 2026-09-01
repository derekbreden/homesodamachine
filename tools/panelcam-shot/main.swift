import AVFoundation
import AppKit
import CoreImage

// `open` does not forward a bundle's stdout or stderr anywhere, and the bundle has to be started
// by `open` for TCC to attribute the prompt to it. So the only account of a run that reaches the
// caller is the one the app writes down itself.
let logURL = URL(fileURLWithPath: NSHomeDirectory()).appendingPathComponent(".panelcam-shot.log")
func note(_ s: String) {
  let line = "\(ISO8601DateFormatter().string(from: Date()))  \(s)\n"
  if let h = try? FileHandle(forWritingTo: logURL) { h.seekToEndOfFile(); h.write(line.data(using: .utf8)!); try? h.close() }
  else { try? line.write(to: logURL, atomically: true, encoding: .utf8) }
  FileHandle.standardError.write(line.data(using: .utf8)!)
}
func fail(_ s: String, _ code: Int32) -> Never { note("FAIL \(s)"); exit(code) }

let args = CommandLine.arguments
guard args.count >= 2 else { fail("usage: PanelCamShot <out.png> [device-name-substring] [warmup]", 2) }
let outPath = args[1]
let want = args.count > 2 ? args[2] : ""
let warmup = args.count > 3 ? Int(args[3]) ?? 16 : 16
// macOS governs delivered size by session preset, not by activeFormat, and refuses
// inputPriority outright — so which preset is in force IS the resolution. Passing it in makes
// that testable without a rebuild, and a rebuild is a re-approval of the camera grant.
// "-" is an explicitly empty argument. `open --args` drops empty strings, which silently
// shifts every argument after them into the wrong slot.
func arg(_ i: Int) -> String { let v = args.count > i ? args[i] : ""; return v == "-" ? "" : v }
let presetArg = arg(4)
// "photo" uses AVCapturePhotoOutput, the stills API, which is not bound by the video path's
// scaling; anything else keeps the video-frame path.
let usePhoto = arg(5) == "photo"
// A requested "WxH" picks that format instead of the widest, so the ceiling can be found by
// walking up the list rather than inferred from one failure at the top of it.
let wantFormat = arg(6)
// How many frames past the warm-up are scored before the best is kept.
let candidates = Int(arg(7)) ?? 12

// KEEP THE SHARPEST FRAME, DO NOT KEEP THE Nth. This camera's autofocus goes on hunting with
// auto_focus set to 0 — absolute_focus written mid-stream comes back changed, 480 in and 370
// out — so which frame is in focus is not something the caller can time. Every frame after the
// warm-up is scored and only the best is kept, which turns the hunting from a defect into a
// sample: somewhere in the sweep the lens passes through focus, and that pass is the picture.
final class Grabber: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
  var seen = 0
  var scored = 0
  var best = -1.0
  let sem = DispatchSemaphore(value: 0)
  var image: CGImage?
  let ctx = CIContext()

  // Sum of squared horizontal luma differences on a coarse grid — an in-focus edge steps harder
  // than a blurred one. Normalised by mean so a brighter frame does not simply win.
  private func sharpness(_ pb: CVPixelBuffer) -> Double {
    CVPixelBufferLockBaseAddress(pb, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(pb, .readOnly) }
    guard let base = CVPixelBufferGetBaseAddress(pb) else { return 0 }
    let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb)
    let stride = CVPixelBufferGetBytesPerRow(pb)
    let p = base.assumingMemoryBound(to: UInt8.self)
    var energy = 0.0, sum = 0.0, n = 0.0
    var y = h / 4
    while y < h * 3 / 4 { var x = w / 4
      while x < w * 3 / 4 - 2 {
        let i = y * stride + x * 4              // BGRA
        let a = Double(p[i]) + Double(p[i + 1]) + Double(p[i + 2])
        let j = i + 8
        let b = Double(p[j]) + Double(p[j + 1]) + Double(p[j + 2])
        let d = a - b
        energy += d * d; sum += a; n += 1
        x += 2
      }
      y += 2
    }
    guard n > 0, sum > 0 else { return 0 }
    let mean = sum / n
    return (energy / n) / (mean * mean)
  }

  func captureOutput(_ o: AVCaptureOutput, didOutput sb: CMSampleBuffer, from c: AVCaptureConnection) {
    seen += 1
    guard seen >= warmup, let pb = CMSampleBufferGetImageBuffer(sb) else { return }
    let sc = sharpness(pb)
    if sc > best {
      best = sc
      let ci = CIImage(cvPixelBuffer: pb)
      image = ctx.createCGImage(ci, from: ci.extent)
    }
    scored += 1
    if scored >= candidates { sem.signal() }
  }
}

let names = [0: "notDetermined", 1: "restricted", 2: "denied", 3: "authorized"]
let before = AVCaptureDevice.authorizationStatus(for: .video)

// COME FORWARD ONLY TO ASK. The prompt is a window and belongs to a foreground app: left as a
// background process this asks correctly and the dialog opens behind whatever the user is
// looking at, which reads exactly like no dialog at all. But every later capture is a silent
// background errand, and activating for those steals the keyboard from whoever is typing —
// once per photograph. Grant already given, stay out of the way.
let nsApp = NSApplication.shared
if before == .notDetermined {
  nsApp.setActivationPolicy(.regular)
  nsApp.activate(ignoringOtherApps: true)
} else {
  nsApp.setActivationPolicy(.accessory)
}
note("start out=\(outPath) want='\(want)' warmup=\(warmup) preset='\(presetArg)' auth=\(names[before.rawValue] ?? "?")")

// requestAccess raises the prompt; from inside a bundle macOS has something to attribute it to.
final class Snapper: NSObject, AVCapturePhotoCaptureDelegate {
  let sem = DispatchSemaphore(value: 0); var data: Data?
  func photoOutput(_ o: AVCapturePhotoOutput, didFinishProcessingPhoto p: AVCapturePhoto, error: Error?) {
    if let e = error { note("photo error \(e.localizedDescription)") }
    data = p.fileDataRepresentation()
    sem.signal()
  }
}

let gate = DispatchSemaphore(value: 0)
var granted = false
AVCaptureDevice.requestAccess(for: .video) { ok in granted = ok; gate.signal() }
// An ad-hoc signature is the binary's own hash, so every rebuild is a new app to TCC and the
// grant has to be given again. The prompt therefore has to outlast a walk away from the desk:
// a capture that fails because nobody was in the room teaches nothing and costs the click twice.
if gate.wait(timeout: .now() + 3600) == .timedOut { fail("no answer to the camera prompt in 1 h", 3) }
note("requestAccess -> \(granted) (auth now \(names[AVCaptureDevice.authorizationStatus(for: .video).rawValue] ?? "?"))")
guard granted else { fail("camera access denied", 3) }

let devices = AVCaptureDevice.DiscoverySession(
  deviceTypes: [.builtInWideAngleCamera, .external, .continuityCamera],
  mediaType: .video, position: .unspecified).devices
guard let dev = want.isEmpty ? devices.first
      : devices.first(where: { $0.localizedName.lowercased().contains(want.lowercased()) }) else {
  fail("no camera matching '\(want)'; saw \(devices.map{$0.localizedName})", 4) }
note("device \(dev.localizedName)")

let session = AVCaptureSession()
guard let input = try? AVCaptureDeviceInput(device: dev), session.canAddInput(input) else { fail("cannot add input", 5) }
session.addInput(input)

let grabber = Grabber()
let snapper = Snapper()
let photoOut = AVCapturePhotoOutput()
let out = AVCaptureVideoDataOutput()
if usePhoto {
  guard session.canAddOutput(photoOut) else { fail("cannot add photo output", 6) }
  session.addOutput(photoOut)
} else {
  // BGRA so the scorer has one byte layout to read. The preset governs size, not this, so
  // asking for a pixel format costs no resolution.
  out.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
  out.setSampleBufferDelegate(grabber, queue: DispatchQueue(label: "panelcam"))
  guard session.canAddOutput(out) else { fail("cannot add output", 6) }
  session.addOutput(out)
}
// A preset is a promise about a shape, not about the sensor, and the session applies one
// whenever its outputs change: set activeFormat before addOutput and addOutput puts it back,
// which is how 4656x3496 was selected and 1920x1080 arrived. Assigning activeFormat is itself
// what switches the session to input priority, so it has to happen after the graph is built.
session.beginConfiguration()
// Without this the session keeps applying a preset of its own over activeFormat, and the
// assignment below is accepted, reads back, and is then quietly overridden: activeFormat says
// 4656x3496 while 1920x1080 is delivered. On macOS the preset has to be stood down by name.
// AVCaptureSession.Preset.inputPriority is marked unavailable on macOS, but the underlying
// string constant is what the session actually compares against, and it honours it.
// THE PRESET IS THE RESOLUTION, and activeFormat is not. Every format asked for on this camera
// — 1600x1200 through 4656x3496 — came back as 1920x1080, because that is what the default
// .high preset means; the format is honoured for what the sensor reads out and the session then
// scales to the preset. macOS refuses .inputPriority outright, so the only lever is to name the
// largest preset the session will take.
let ladder = presetArg.isEmpty
  ? ["AVCaptureSessionPreset3840x2160", "AVCaptureSessionPresetHigh"]
  : [presetArg]
for name in ladder {
  let p = AVCaptureSession.Preset(rawValue: name)
  if session.canSetSessionPreset(p) { session.sessionPreset = p; break }
  note("preset \(name) refused")
}
let dimsOf = { (f: AVCaptureDevice.Format) -> CMVideoDimensions in
  CMVideoFormatDescriptionGetDimensions(f.formatDescription) }
var widest = dev.formats.max { a, b in
  dimsOf(a).width * dimsOf(a).height < dimsOf(b).width * dimsOf(b).height }
if !wantFormat.isEmpty {
  let parts = wantFormat.split(separator: "x").compactMap { Int32($0) }
  if parts.count == 2,
     let f = dev.formats.first(where: { dimsOf($0).width == parts[0] && dimsOf($0).height == parts[1] }) {
    widest = f
  } else { note("no format \(wantFormat); keeping the widest") }
}
if let f = widest, (try? dev.lockForConfiguration()) != nil {
  dev.activeFormat = f
  dev.unlockForConfiguration()
}
session.commitConfiguration()
let dims = CMVideoFormatDescriptionGetDimensions(dev.activeFormat.formatDescription)
note("format \(dims.width)x\(dims.height) of \(dev.formats.count) offered, preset \(session.sessionPreset.rawValue)")

session.startRunning()

if usePhoto {
  // Defaults only. Asking for a size the output does not publish throws an ObjC exception the
  // Swift side cannot catch, and the process aborts with nothing written down.
  let ps = AVCapturePhotoSettings()
  note("photo codecs \(photoOut.availablePhotoCodecTypes.map { $0.rawValue })")
  Thread.sleep(forTimeInterval: 1.5)          // let exposure settle before the one exposure taken
  photoOut.capturePhoto(with: ps, delegate: snapper)
  if snapper.sem.wait(timeout: .now() + 60) == .timedOut { session.stopRunning(); fail("no photo", 7) }
  session.stopRunning()
  guard let d = snapper.data, let rep = NSBitmapImageRep(data: d) else { fail("no photo data", 8) }
  guard let png = rep.representation(using: .png, properties: [:]) else { fail("png encode", 9) }
  try png.write(to: URL(fileURLWithPath: outPath))
  note("OK \(dev.localizedName) \(rep.pixelsWide)x\(rep.pixelsHigh) -> \(outPath)")
} else {
  if grabber.sem.wait(timeout: .now() + 60) == .timedOut { session.stopRunning(); fail("no frame after \(grabber.seen) delivered, \(grabber.scored) scored", 7) }
  session.stopRunning()
  guard let cg = grabber.image else { fail("no image from frame", 8) }
  let rep = NSBitmapImageRep(cgImage: cg)
  guard let png = rep.representation(using: .png, properties: [:]) else { fail("png encode", 9) }
  try png.write(to: URL(fileURLWithPath: outPath))
  note("OK \(dev.localizedName) \(cg.width)x\(cg.height) best=\(String(format: "%.4f", grabber.best)) of \(grabber.scored) -> \(outPath)")
}
