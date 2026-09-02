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
let wantFormat = opt("format", "4656x3496")       // WxH, or WxH:fourcc to pick one of the stream's codings
let dwell = Double(opt("dwell", "0.3")) ?? 0.3    // seconds of frames scored at each focus value
let maxSeconds = Double(opt("max", "30")) ?? 30   // the sweep gives up after this
let uvcSpec = opt("uvc")                          // control=value,… applied once the stream runs
let uvcNode = opt("uvc-node")
let uvcJs = opt("uvc-js")
let dumpDir = opt("dump")                         // every scored frame written here, for measuring
let dumpMax = Int(opt("dump-max", "8")) ?? 8
let dumpEvery = max(1, Int(opt("dump-every", "1")) ?? 1)

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

// The camera's controls, through `uvc.js serve`: one process for the whole capture, a line out and
// the register read back on a line in, in about two milliseconds. The stream itself is macOS's;
// the control interface is reached beside it and never disturbs a frame.
final class UVC {
  let proc = Process()
  let toNode = Pipe(), fromNode = Pipe()
  var pending = Data()
  init?(node: String, js: String) {
    guard !node.isEmpty, !js.isEmpty else { return nil }
    proc.executableURL = URL(fileURLWithPath: node)
    proc.arguments = [js, "serve"]
    proc.standardInput = toNode
    proc.standardOutput = fromNode
    proc.standardError = FileHandle.nullDevice
    do { try proc.run() } catch { note("uvc serve failed: \(error.localizedDescription)"); return nil }
  }
  func ask(_ line: String) -> String {
    toNode.fileHandleForWriting.write((line + "\n").data(using: .utf8)!)
    while true {
      if let nl = pending.firstIndex(of: 10) {
        let answer = String(data: pending[pending.startIndex..<nl], encoding: .utf8) ?? ""
        pending.removeSubrange(pending.startIndex...nl)
        return answer.trimmingCharacters(in: .whitespaces)
      }
      let more = fromNode.fileHandleForReading.availableData
      if more.isEmpty { return "" }
      pending.append(more)
    }
  }
  func get(_ name: String) -> Int? { Int(ask("get \(name)")) }
  @discardableResult func set(_ name: String, _ value: Int) -> Int? { Int(ask("set \(name) \(value)")) }
  func close() {
    toNode.fileHandleForWriting.write("quit\n".data(using: .utf8)!)
    try? toNode.fileHandleForWriting.close()
    proc.terminate()
  }
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

let formatSpec = wantFormat.split(separator: ":").map(String.init)
let parts = formatSpec[0].split(separator: "x").compactMap { Int32($0) }
guard parts.count == 2 else { fail("--format wants WxH or WxH:fourcc", 13) }
let wantCoding = formatSpec.count > 1 ? formatSpec[1] : ""
let matching = formats.filter {
  dims($0).width == parts[0] && dims($0).height == parts[1]
    && (wantCoding.isEmpty || fourCC(CMFormatDescriptionGetMediaSubType($0)) == wantCoding) }
guard let fmt = matching.first else {
  fail("no format \(wantFormat); have \(formats.map { "\(dims($0).width)x\(dims($0).height):\(fourCC(CMFormatDescriptionGetMediaSubType($0)))" })", 13) }

let setStatus = cmioSetFormat(streamID, fmt)
note("format \(dims(fmt).width)x\(dims(fmt).height) \(fourCC(CMFormatDescriptionGetMediaSubType(fmt))) status \(setStatus)")

var queueRef: Unmanaged<CMSimpleQueue>?
let qst = CMIOStreamCopyBufferQueue(streamID, { _, _, _ in }, nil, &queueRef)
guard qst == 0, let queue = queueRef?.takeRetainedValue() else { fail("no buffer queue (status \(qst))", 14) }

let started = CMIODeviceStartStream(deviceID, streamID)
guard started == 0 else { fail("stream would not start (status \(started))", 15) }

var best = -1.0
var bestImage: CGImage?
var seen = 0, scored = 0, dumped = 0, dumpable = 0
var hist = [String: Int]()

// A frame's bytes as the camera delivered them, beside the PNG made from them, so the two can be
// compared and a coding's range and chroma layout read off the file.
func dump(_ sb: CMSampleBuffer, _ pb: CVPixelBuffer, _ sc: Double) {
  guard !dumpDir.isEmpty, dumped < dumpMax else { return }
  dumpable += 1
  guard dumpable % dumpEvery == 1 || dumpEvery == 1 else { return }
  dumped += 1
  let code = fourCC(CVPixelBufferGetPixelFormatType(pb))
  let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb)
  let stem = String(format: "%@/%03d_%@_%dx%d_%.5f", dumpDir, dumped, code, w, h, sc)
  CVPixelBufferLockBaseAddress(pb, .readOnly)
  if CVPixelBufferIsPlanar(pb) {
    for pl in 0..<CVPixelBufferGetPlaneCount(pb) {
      let stride = CVPixelBufferGetBytesPerRowOfPlane(pb, pl), ph = CVPixelBufferGetHeightOfPlane(pb, pl)
      let d = Data(bytes: CVPixelBufferGetBaseAddressOfPlane(pb, pl)!, count: stride * ph)
      try? d.write(to: URL(fileURLWithPath: "\(stem)_p\(pl)_s\(stride).raw"))
    }
  } else {
    let stride = CVPixelBufferGetBytesPerRow(pb)
    let d = Data(bytes: CVPixelBufferGetBaseAddress(pb)!, count: stride * h)
    try? d.write(to: URL(fileURLWithPath: "\(stem)_s\(stride).raw"))
  }
  CVPixelBufferUnlockBaseAddress(pb, .readOnly)
  // One PNG per run is enough to compare the file the pipeline saves against the bytes it came from.
  if dumped == 1, let img = imageFrom(sb),
     let png = NSBitmapImageRep(cgImage: img).representation(using: .png, properties: [:]) {
    try? png.write(to: URL(fileURLWithPath: "\(stem).png"))
    note("dump \(code) \(w)x\(h) planar=\(CVPixelBufferIsPlanar(pb)) -> \(dumpDir)")
  }
}

// Every frame is scored and the sharpest kept; a frame only becomes an image when it beats the one
// held. Returns the best score seen in this window.
@discardableResult
func drain(for seconds: Double, scoring: Bool) -> Double {
  let deadline = Date().addingTimeInterval(seconds)
  var windowBest = -1.0
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
    dump(sb, pb, sc)
    windowBest = max(windowBest, sc)
    if sc > best, let img = imageFrom(sb) { best = sc; bestImage = img }
  }
  return windowBest
}

// Frames are flowing before a control is touched, so what is written is what the frames show.
drain(for: 0.5, scoring: false)

let uvc = UVC(node: uvcNode, js: uvcJs)
if uvc == nil { note("uvc skipped") }

// Each control is written once and read back; the registers hold for as long as the stream runs.
// A mismatch is written a second time and then reported, not fought.
if let u = uvc, !uvcSpec.isEmpty {
  var applied = [String]()
  for pair in uvcSpec.split(separator: ",") {
    let kv = pair.split(separator: "=").map(String.init)
    guard kv.count == 2, let v = Int(kv[1]) else { continue }
    var got = u.set(kv[0], v)
    if got != v { got = u.set(kv[0], v) }
    applied.append(got == v ? "\(kv[0])=\(v)" : "\(kv[0])=\(v)?\(got.map(String.init) ?? "none")")
  }
  note("controls \(applied.joined(separator: " "))")
  drain(for: 0.3, scoring: false)
}

var focusRange: (lo: Int, hi: Int, step: Int)?
do {
  let f = opt("focus-range").split(separator: ":").compactMap { Int($0) }
  if f.count == 3, f[2] > 0 { focusRange = (f[0], f[1], f[2]) }
}

// THE LENS MOVES ONLY WHEN THE REGISTER CHANGES, AND PARKS WHEN THE STREAM STARTS. absolute_focus
// keeps the last number written across a stream start while the lens sits at its rest position;
// writing that same number back is a no-op, and any other number moves the lens. Where it lands for
// a number depends on the direction it came from — about sixty units of hysteresis — so every sweep
// first parks the lens below the range and then walks up through it, and the sharpest frame seen
// on the way is the picture. Sharpness halves within about forty units of the peak either side,
// so a step scoring under half the best, two or more steps past it, is the far side of it.
var bestFocus = -1
if let r = focusRange {
  guard let u = uvc else { fail("a focus sweep needs --uvc-node and --uvc-js", 18) }
  let t0 = Date()
  let park = max(1, r.lo - 100)
  if u.get("absolute_focus") == park { u.set("absolute_focus", park + 1) }
  u.set("absolute_focus", park)
  drain(for: 0.7, scoring: false)
  var trace = [String]()
  var steps = 0
  var v = r.lo
  while v <= r.hi && Date().timeIntervalSince(t0) < maxSeconds {
    u.set("absolute_focus", v)
    steps += 1
    drain(for: 0.2, scoring: false)             // the frames already in flight show the old position
    let before = best
    let here = drain(for: dwell, scoring: true)
    trace.append("\(v):" + String(format: "%.4f", max(here, 0)))
    if best > before { bestFocus = v }
    else if v >= bestFocus + 2 * r.step && here < 0.5 * best { break }
    v += r.step
  }
  note("focus \(r.lo)..\(r.hi) step \(r.step) -> best \(String(format: "%.5f", best)) at \(bestFocus), \(steps) steps in \(String(format: "%.1f", Date().timeIntervalSince(t0))) s")
  note("trace \(trace.joined(separator: " "))")
} else {
  let deadline = Date().addingTimeInterval(maxSeconds)
  repeat { drain(for: dwell, scoring: true) } while bestImage == nil && Date() < deadline
}

_ = CMIODeviceStopStream(deviceID, streamID)
uvc?.close()
let seenDims = hist.sorted { $0.value > $1.value }.map { "\($0.key)×\($0.value)" }.joined(separator: " ")
guard let img = bestImage else { fail("no frame kept; saw [\(seenDims)]", 16) }
guard let png = NSBitmapImageRep(cgImage: img).representation(using: .png, properties: [:]) else {
  fail("png encode", 9) }
do { try png.write(to: URL(fileURLWithPath: outPath)) }
catch { fail("write \(outPath): \(error.localizedDescription)", 17) }
note("OK \(chosenName) \(img.width)x\(img.height) best=\(String(format: "%.5f", best)) of \(scored) scored, \(seen) seen -> \(outPath)")
