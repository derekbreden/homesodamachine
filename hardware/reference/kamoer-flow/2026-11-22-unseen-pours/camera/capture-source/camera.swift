import AVFoundation
import Foundation
import CoreMediaIO
func note(_ s: String){FileHandle.standardError.write(Data((s+"\n").utf8))}
func fail(_ s:String,_ i:Int32)->Never{note(s);exit(i)}
let want="0x14000032e41298",wantFormat="2320x1744:420v",listOnly=false
let gate=DispatchSemaphore(value:0)
var auth=false
AVCaptureDevice.requestAccess(for:.video){v in auth=v;gate.signal()}
guard gate.wait(timeout:.now()+8) == .success, auth else {fail("camera permission unavailable",3)}
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
  if cmioString(d, Int(kCMIODevicePropertyDeviceUID)) == want { chosen = d; chosenName = name }
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
let outlet=FileHandle.standardOutput
func emit(_ h:[String:Any],_ data:Data) throws {
 let hdr=try JSONSerialization.data(withJSONObject:h)
 var buf=Data("GPO1".utf8)
 var u=UInt32(hdr.count).littleEndian, v=UInt32(data.count).littleEndian
 withUnsafeBytes(of:&u){buf.append(contentsOf:$0)}
 withUnsafeBytes(of:&v){buf.append(contentsOf:$0)}
 buf.append(hdr)
 try outlet.write(contentsOf:buf)
 try outlet.write(contentsOf:data)
}
var seq=0
try emit(["type":"hello","source":"CoreMediaIO","unique_id":want,"selected":wantFormat],Data())
while true {
 guard let raw=CMSimpleQueueDequeue(queue) else {usleep(1000);continue}
 autoreleasepool {
 let sb=Unmanaged<CMSampleBuffer>.fromOpaque(raw).takeRetainedValue()
 guard let pb=CMSampleBufferGetImageBuffer(sb) else { return }
 let host=clock_gettime_nsec_np(CLOCK_UPTIME_RAW)
 let w=CVPixelBufferGetWidth(pb),h=CVPixelBufferGetHeight(pb)
 guard w==2320,h==1744,CVPixelBufferIsPlanar(pb) else {note("Skipping startup format \(w)x\(h)");return}
 let pts=CMTimeConvertScale(CMSampleBufferGetPresentationTimeStamp(sb),timescale:1000000000,method:.roundHalfAwayFromZero).value
 let includeChroma = seq%15==0
 var data=Data(capacity:includeChroma ? w*h*3/2 : w*h)
 CVPixelBufferLockBaseAddress(pb,.readOnly)
 for pl in 0..<(includeChroma ? 2:1){
 let base=CVPixelBufferGetBaseAddressOfPlane(pb,pl)!
 let stride=CVPixelBufferGetBytesPerRowOfPlane(pb,pl),rows=CVPixelBufferGetHeightOfPlane(pb,pl)
 if stride==w {data.append(base.assumingMemoryBound(to:UInt8.self),count:rows*w)}
 else {for y in 0..<rows {data.append(base.advanced(by:y*stride).assumingMemoryBound(to:UInt8.self),count:w)}}
 }
 CVPixelBufferUnlockBaseAddress(pb,.readOnly)
 seq+=1
 do {try emit(["type":"frame","seq":seq,"width":w,"height":h,"pts_ns":pts,"host_ns":host,"codec":includeChroma ? "nv12":"gray8"],data)}
 catch { exit(0) }
 }
}
