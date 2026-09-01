import AVFoundation
import AppKit
import CoreMediaIO

// `open` forwards neither stdout nor stderr, so the app keeps its own log.
let logURL = URL(fileURLWithPath: NSHomeDirectory()).appendingPathComponent(".panelcam-shot.log")
func note(_ s: String) {
  let line = "\(ISO8601DateFormatter().string(from: Date()))  \(s)\n"
  if let h = try? FileHandle(forWritingTo: logURL) { h.seekToEndOfFile(); try? h.write(contentsOf: line.data(using: .utf8)!); try? h.close() }
  else { try? line.write(to: logURL, atomically: true, encoding: .utf8) }
  FileHandle.standardError.write(line.data(using: .utf8)!)
}
func fail(_ s: String, _ code: Int32) -> Never { note("FAIL \(s)"); exit(code) }

var opts = [String: String]()
do {
  let a = Array(CommandLine.arguments.dropFirst())
  var i = 0
  while i < a.count {
    let t = a[i]
    if t.hasPrefix("--") {
      let key = String(t.dropFirst(2))
      if i + 1 < a.count && !a[i + 1].hasPrefix("--") { opts[key] = a[i + 1]; i += 2 }
      else { opts[key] = "true"; i += 1 }
    } else { i += 1 }
  }
}
func opt(_ k: String, _ d: String = "") -> String { opts[k] ?? d }

let outPath = opt("out")
let want = opt("match")
let listOnly = opt("list") == "true"
let wantFormat = opt("format", "4656x3496")
let settle = Double(opt("settle", "9")) ?? 9          // seconds of frames scored
let stabilize = Double(opt("stabilize", "1.5")) ?? 1.5  // stream running, before the controls go in
let focusSettle = Double(opt("focus-settle", "2")) ?? 2 // controls in, before scoring starts
let targetScore = Double(opt("target", "0.05")) ?? 0.05   // a frame this sharp ends the search
let maxSeconds = Double(opt("max", "40")) ?? 40            // and this is how long it may look
let uvcSpec = opt("uvc")
let uvcNode = opt("uvc-node")
let uvcJs = opt("uvc-js")

if !listOnly && outPath.isEmpty { fail("need --out", 2) }

// The panel is a fifth of the frame and the rest is unlit countertop. --score names the rectangle
// the score is taken over.
var scoreRect: (w: Int, h: Int, x: Int, y: Int)?
do {
  let f = opt("score").split(separator: ":").compactMap { Int($0) }
  if f.count == 4 { scoreRect = (f[0], f[1], f[2], f[3]) }
}

// Laplacian energy over mean squared: rises with the fine detail an in-focus lens resolves, and
// does not rise with brightness.
func score(_ p: UnsafePointer<UInt8>, _ w: Int, _ h: Int, _ stride: Int, _ px: Int) -> Double {
  let r = scoreRect ?? (w / 2, h / 2, w / 4, h / 4)
  let x0 = max(1, min(r.x, w - 3)), y0 = max(1, min(r.y, h - 3))
  let x1 = min(w - 2, x0 + r.w), y1 = min(h - 2, y0 + r.h)
  var energy = 0.0, sum = 0.0, n = 0.0
  var y = y0
  while y < y1 {
    var x = x0
    while x < x1 {
      let c = y * stride + x * px
      let lap = -4 * Double(p[c])
        + Double(p[c - px]) + Double(p[c + px])
        + Double(p[c - stride]) + Double(p[c + stride])
      energy += lap * lap; sum += Double(p[c]); n += 1
      x += 2
    }
    y += 2
  }
  guard n > 0, sum > 0 else { return 0 }
  let mean = sum / n
  return (energy / n) / (mean * mean)
}

// The luma plane is one byte per pixel and needs no conversion, so every frame can be scored at
// the rate they arrive.
func scoreLuma(_ pb: CVPixelBuffer) -> Double {
  CVPixelBufferLockBaseAddress(pb, .readOnly)
  defer { CVPixelBufferUnlockBaseAddress(pb, .readOnly) }
  if CVPixelBufferIsPlanar(pb) {
    guard let base = CVPixelBufferGetBaseAddressOfPlane(pb, 0) else { return 0 }
    return score(base.assumingMemoryBound(to: UInt8.self),
                 CVPixelBufferGetWidthOfPlane(pb, 0), CVPixelBufferGetHeightOfPlane(pb, 0),
                 CVPixelBufferGetBytesPerRowOfPlane(pb, 0), 1)
  }
  guard let base = CVPixelBufferGetBaseAddress(pb) else { return 0 }
  let bpp = CVPixelBufferGetBytesPerRow(pb) / max(1, CVPixelBufferGetWidth(pb))
  return score(base.assumingMemoryBound(to: UInt8.self),
               CVPixelBufferGetWidth(pb), CVPixelBufferGetHeight(pb),
               CVPixelBufferGetBytesPerRow(pb), max(1, bpp))
}

let ciContext = CIContext(options: nil)

// A sample arrives either as pixels the driver has already decoded or as the camera's own JPEG.
func imageFrom(_ sb: CMSampleBuffer) -> CGImage? {
  if let pb = CMSampleBufferGetImageBuffer(sb) {
    let ci = CIImage(cvPixelBuffer: pb)
    return ciContext.createCGImage(ci, from: ci.extent)
  }
  guard let bb = CMSampleBufferGetDataBuffer(sb) else { return nil }
  var len = 0
  var ptr: UnsafeMutablePointer<Int8>?
  guard CMBlockBufferGetDataPointer(bb, atOffset: 0, lengthAtOffsetOut: nil,
                                    totalLengthOut: &len, dataPointerOut: &ptr) == kCMBlockBufferNoErr,
        let p = ptr, len > 4 else { return nil }
  let data = Data(bytes: p, count: len)
  guard let src = CGImageSourceCreateWithData(data as CFData, nil) else { return nil }
  return CGImageSourceCreateImageAtIndex(src, 0, nil)
}

// Opening the stream returns focus and exposure to auto and the camera keeps moving them after, so
// the controls are held for as long as the stream is open.
var holdProc: Process?
func holdUVC(_ spec: String) {
  guard !spec.isEmpty, !uvcNode.isEmpty, !uvcJs.isEmpty else { note("uvc skipped"); return }
  let p = Process()
  p.executableURL = URL(fileURLWithPath: uvcNode)
  p.arguments = [uvcJs, "hold", spec, "120"]
  p.standardOutput = FileHandle.nullDevice
  p.standardError = FileHandle.nullDevice
  do { try p.run(); holdProc = p; note("uvc held: \(spec)") }
  catch { note("uvc hold failed: \(error.localizedDescription)") }
}

let names = [0: "notDetermined", 1: "restricted", 2: "denied", 3: "authorized"]
let before = AVCaptureDevice.authorizationStatus(for: .video)

// The prompt is a window and belongs to a foreground app. Once the grant is given the app stays in
// the background, where a capture takes no one's keyboard.
let nsApp = NSApplication.shared
if before == .notDetermined {
  nsApp.setActivationPolicy(.regular)
  nsApp.activate(ignoringOtherApps: true)
} else {
  nsApp.setActivationPolicy(.accessory)
}
note("start out=\(outPath) want='\(want)' format=\(wantFormat) auth=\(names[before.rawValue] ?? "?")")

let gate = DispatchSemaphore(value: 0)
var granted = false
AVCaptureDevice.requestAccess(for: .video) { ok in granted = ok; gate.signal() }
if gate.wait(timeout: .now() + 3600) == .timedOut { fail("no answer to the camera prompt in 1 h", 3) }
guard granted else { fail("camera access denied", 3) }

func cmioAddr(_ sel: Int) -> CMIOObjectPropertyAddress {
  CMIOObjectPropertyAddress(mSelector: CMIOObjectPropertySelector(sel),
                            mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
                            mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMain))
}

func cmioIDs(_ obj: CMIOObjectID, _ sel: Int) -> [CMIOObjectID] {
  var addr = cmioAddr(sel)
  var size: UInt32 = 0
  guard CMIOObjectGetPropertyDataSize(obj, &addr, 0, nil, &size) == 0, size > 0 else { return [] }
  var out = [CMIOObjectID](repeating: 0, count: Int(size) / MemoryLayout<CMIOObjectID>.size)
  var used: UInt32 = 0
  let st = out.withUnsafeMutableBytes { raw -> OSStatus in
    CMIOObjectGetPropertyData(obj, &addr, 0, nil, size, &used, raw.baseAddress!)
  }
  return st == 0 ? out : []
}

func cmioString(_ obj: CMIOObjectID, _ sel: Int) -> String {
  var addr = cmioAddr(sel)
  var value: Unmanaged<CFString>?
  var used: UInt32 = 0
  let st = withUnsafeMutablePointer(to: &value) { p -> OSStatus in
    CMIOObjectGetPropertyData(obj, &addr, 0, nil, UInt32(MemoryLayout<Unmanaged<CFString>?>.size), &used, p)
  }
  guard st == 0, let v = value else { return "" }
  return v.takeRetainedValue() as String
}

func cmioFormats(_ stream: CMIOStreamID) -> [CMFormatDescription] {
  var addr = cmioAddr(Int(kCMIOStreamPropertyFormatDescriptions))
  var value: Unmanaged<CFArray>?
  var used: UInt32 = 0
  let st = withUnsafeMutablePointer(to: &value) { p -> OSStatus in
    CMIOObjectGetPropertyData(stream, &addr, 0, nil, UInt32(MemoryLayout<Unmanaged<CFArray>?>.size), &used, p)
  }
  guard st == 0, let v = value else { return [] }
  return (v.takeRetainedValue() as? [CMFormatDescription]) ?? []
}

func cmioSetFormat(_ stream: CMIOStreamID, _ fmt: CMFormatDescription) -> OSStatus {
  var addr = cmioAddr(Int(kCMIOStreamPropertyFormatDescription))
  var raw = Unmanaged.passUnretained(fmt).toOpaque()
  return CMIOObjectSetPropertyData(stream, &addr, 0, nil,
                                   UInt32(MemoryLayout<UnsafeMutableRawPointer>.size), &raw)
}

func fourCC(_ v: FourCharCode) -> String {
  let b = [UInt8((v >> 24) & 255), UInt8((v >> 16) & 255), UInt8((v >> 8) & 255), UInt8(v & 255)]
  return String(bytes: b, encoding: .ascii) ?? "\(v)"
}
func dims(_ f: CMFormatDescription) -> CMVideoDimensions { CMVideoFormatDescriptionGetDimensions(f) }

let system = CMIOObjectID(kCMIOObjectSystemObject)
var chosen: CMIOObjectID?
var chosenName = ""
for d in cmioIDs(system, Int(kCMIOHardwarePropertyDevices)) {
  let name = cmioString(d, Int(kCMIOObjectPropertyName))
  if want.isEmpty || name.lowercased().contains(want.lowercased()) { chosen = d; chosenName = name }
}
guard let deviceID = chosen else { fail("no camera matching '\(want)'", 10) }
note("device \(chosenName)")

guard let streamID = cmioIDs(deviceID, Int(kCMIODevicePropertyStreams)).first else {
  fail("device publishes no stream", 11) }

let formats = cmioFormats(streamID)
guard !formats.isEmpty else { fail("stream publishes no formats", 12) }
if listOnly {
  for f in formats { note("  \(dims(f).width)x\(dims(f).height) \(fourCC(CMFormatDescriptionGetMediaSubType(f)))") }
  exit(0)
}

let parts = wantFormat.split(separator: "x").compactMap { Int32($0) }
guard parts.count == 2 else { fail("--format wants WxH", 13) }
let matching = formats.filter { dims($0).width == parts[0] && dims($0).height == parts[1] }
guard let fmt = matching.first else {
  fail("no format \(wantFormat); have \(formats.map { "\(dims($0).width)x\(dims($0).height)" })", 13) }

let setStatus = cmioSetFormat(streamID, fmt)
note("format \(dims(fmt).width)x\(dims(fmt).height) \(fourCC(CMFormatDescriptionGetMediaSubType(fmt))) status \(setStatus)")

var queueRef: Unmanaged<CMSimpleQueue>?
let qst = CMIOStreamCopyBufferQueue(streamID, { _, _, _ in }, nil, &queueRef)
guard qst == 0, let queue = queueRef?.takeRetainedValue() else { fail("no buffer queue (status \(qst))", 14) }

let started = CMIODeviceStartStream(deviceID, streamID)
guard started == 0 else { fail("stream would not start (status \(started))", 15) }

var best = -1.0
var bestImage: CGImage?
var seen = 0, scored = 0
var hist = [String: Int]()

// The lens travels the whole time the stream is open, whatever auto_focus is set to, so the frame
// that is in focus is one of the ones it passes through. Every frame is scored and the sharpest
// kept; a frame only becomes an image when it beats the one held.
func drain(for seconds: Double, scoring: Bool) {
  let deadline = Date().addingTimeInterval(seconds)
  while Date() < deadline {
    guard let raw = CMSimpleQueueDequeue(queue) else { usleep(3000); continue }
    let sb = Unmanaged<CMSampleBuffer>.fromOpaque(raw).takeRetainedValue()
    seen += 1
    if let f = CMSampleBufferGetFormatDescription(sb) {
      let d = dims(f)
      hist["\(d.width)x\(d.height)", default: 0] += 1
    }
    guard scoring, let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
    let sc = scoreLuma(pb)
    scored += 1
    if sc > best, let img = imageFrom(sb) { best = sc; bestImage = img }
  }
}

func uvcRun(_ args: [String]) -> String? {
  guard !uvcNode.isEmpty, !uvcJs.isEmpty else { return nil }
  let p = Process()
  p.executableURL = URL(fileURLWithPath: uvcNode)
  p.arguments = [uvcJs] + args
  let pipe = Pipe()
  p.standardOutput = pipe
  p.standardError = FileHandle.nullDevice
  do { try p.run() } catch { return nil }
  let d = pipe.fileHandleForReading.readDataToEndOfFile()
  p.waitUntilExit()
  return String(data: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
}

// absolute_focus reads back the number last written while the lens stands somewhere else: held at
// 420 and 580 this panel measures 752 and 697, held at 500 and 660 it measures 126 and 130. The
// range is walked, every frame is scored, and the sharpest is kept. The value that produced it is
// reported.
var bestFocus = ""
func bracketFocus(_ lo: Int, _ hi: Int, _ step: Int, dwell: Double) {
  var v = lo
  while v <= hi {
    _ = uvcRun(["set", "absolute_focus", String(v)])
    drain(for: dwell, scoring: false)
    let before = best
    drain(for: dwell, scoring: true)
    if best > before { bestFocus = String(v) }
    v += step
  }
}

var focusRange: (lo: Int, hi: Int, step: Int)?
do {
  let f = opt("focus-range").split(separator: ":").compactMap { Int($0) }
  if f.count == 3, f[2] > 0 { focusRange = (f[0], f[1], f[2]) }
}

// The bracket owns the lens, so the held controls are everything except the one being walked.
var holdSpec = uvcSpec
if focusRange != nil {
  holdSpec = uvcSpec.split(separator: ",").filter { !$0.hasPrefix("absolute_focus=") }.joined(separator: ",")
}

drain(for: stabilize, scoring: false)
holdUVC(holdSpec)
drain(for: focusSettle, scoring: false)
// About one pass in three ends soft where its neighbours end sharp — 0.090, 0.010, 0.099 on the
// same panel, under autofocus and under the bracket alike. Passes repeat until a frame reaches
// --target, or --max seconds have gone.
if let r = focusRange {
  let deadline = Date().addingTimeInterval(maxSeconds)
  var passes = 0
  repeat {
    passes += 1
    bracketFocus(r.lo, r.hi, r.step, dwell: settle)
  } while best < targetScore && Date() < deadline
  note("focus bracket \(r.lo)..\(r.hi) step \(r.step) -> best at \(bestFocus) in \(passes) pass(es)")
} else {
  let deadline = Date().addingTimeInterval(maxSeconds)
  repeat { drain(for: settle, scoring: true) } while best < targetScore && Date() < deadline
}

_ = CMIODeviceStopStream(deviceID, streamID)
holdProc?.terminate()
let seenDims = hist.sorted { $0.value > $1.value }.map { "\($0.key)×\($0.value)" }.joined(separator: " ")
guard let img = bestImage else { fail("no frame kept; saw [\(seenDims)]", 16) }
guard let png = NSBitmapImageRep(cgImage: img).representation(using: .png, properties: [:]) else {
  fail("png encode", 9) }
do { try png.write(to: URL(fileURLWithPath: outPath)) }
catch { fail("write \(outPath): \(error.localizedDescription)", 17) }
note("OK \(chosenName) \(img.width)x\(img.height) best=\(String(format: "%.5f", best)) of \(scored) scored, \(seen) seen -> \(outPath)")
