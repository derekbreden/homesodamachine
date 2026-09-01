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

final class Grabber: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
  var seen = 0; let sem = DispatchSemaphore(value: 0); var image: CGImage?
  func captureOutput(_ o: AVCaptureOutput, didOutput sb: CMSampleBuffer, from c: AVCaptureConnection) {
    seen += 1
    guard seen >= warmup, let pb = CMSampleBufferGetImageBuffer(sb) else { return }
    let ci = CIImage(cvPixelBuffer: pb)
    image = CIContext().createCGImage(ci, from: ci.extent)
    sem.signal()
  }
}

// The prompt is a window, and a window belongs to an app that is running in the foreground.
// Left as a background process this asks correctly and the dialog opens behind whatever the
// user is looking at, which reads exactly like no dialog at all.
let nsApp = NSApplication.shared
nsApp.setActivationPolicy(.regular)
nsApp.activate(ignoringOtherApps: true)

let names = [0: "notDetermined", 1: "restricted", 2: "denied", 3: "authorized"]
let before = AVCaptureDevice.authorizationStatus(for: .video)
note("start out=\(outPath) want='\(want)' warmup=\(warmup) auth=\(names[before.rawValue] ?? "?")")

// requestAccess raises the prompt; from inside a bundle macOS has something to attribute it to.
let gate = DispatchSemaphore(value: 0)
var granted = false
AVCaptureDevice.requestAccess(for: .video) { ok in granted = ok; gate.signal() }
if gate.wait(timeout: .now() + 600) == .timedOut { fail("no answer to the camera prompt in 600 s", 3) }
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

// A preset is a promise about a shape, not about the sensor: .high on this camera hands back
// 1280x720 and the panel arrives with fewer pixels across it than it has of its own. Framing is
// a crop out of the largest format the device will give, so take the largest format.
let widest = dev.formats.max { a, b in
  let d = { (f: AVCaptureDevice.Format) -> Int32 in
    let x = CMVideoFormatDescriptionGetDimensions(f.formatDescription); return x.width * x.height }
  return d(a) < d(b)
}
if let f = widest, (try? dev.lockForConfiguration()) != nil {
  dev.activeFormat = f
  dev.unlockForConfiguration()
}
let dims = CMVideoFormatDescriptionGetDimensions(dev.activeFormat.formatDescription)
note("format \(dims.width)x\(dims.height) of \(dev.formats.count) offered")
let out = AVCaptureVideoDataOutput()
out.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
let grabber = Grabber()
out.setSampleBufferDelegate(grabber, queue: DispatchQueue(label: "panelcam"))
guard session.canAddOutput(out) else { fail("cannot add output", 6) }
session.addOutput(out)
session.startRunning()

if grabber.sem.wait(timeout: .now() + 20) == .timedOut { session.stopRunning(); fail("no frame after \(grabber.seen) delivered", 7) }
session.stopRunning()
guard let cg = grabber.image else { fail("no image from frame", 8) }
let rep = NSBitmapImageRep(cgImage: cg)
guard let png = rep.representation(using: .png, properties: [:]) else { fail("png encode", 9) }
try png.write(to: URL(fileURLWithPath: outPath))
note("OK \(dev.localizedName) \(cg.width)x\(cg.height) -> \(outPath)")
