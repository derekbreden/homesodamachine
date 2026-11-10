// Synthetic popovers exercise Vision and the selector without opening any application.
func fixtureImage(x: CGFloat, y: CGFloat, scale: CGFloat, kind: String, duplicate: Bool) -> CGImage {
    let width = Int(1600*scale), height = Int(1200*scale)
    let bitmap = NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:width,pixelsHigh:height,
        bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,
        colorSpaceName:.deviceRGB,bytesPerRow:width*4,bitsPerPixel:32)!
    let graphics = NSGraphicsContext(bitmapImageRep:bitmap)!
    NSGraphicsContext.saveGraphicsState()
    graphics.cgContext.translateBy(x:0,y:CGFloat(height))
    graphics.cgContext.scaleBy(x:scale,y:-scale)
    NSGraphicsContext.current = NSGraphicsContext(cgContext:graphics.cgContext,flipped:true)
    func rectangle(_ rect: CGRect, _ colour: NSColor) { colour.setFill(); NSBezierPath(rect:rect).fill() }
    func label(_ text: String, _ x: CGFloat, _ y: CGFloat, _ size: CGFloat, _ colour: NSColor) {
        (text as NSString).draw(at:NSPoint(x:x,y:y),withAttributes:[.font:NSFont(name:"Helvetica",size:size)!, .foregroundColor:colour])
    }
    rectangle(CGRect(x:0,y:0,width:1600,height:1200),NSColor(white:0.92,alpha:1))
    rectangle(CGRect(x:1100,y:650,width:120,height:150),.black)
    label("Ext",1130,670,25,.white);label("TPU",1130,710,25,.white)
    label("AMS",250,120,28,.black);rectangle(CGRect(x:250,y:170,width:130,height:130),NSColor(white:0.86,alpha:1));label("TPU",275,205,25,.black)
    func external(_ x: CGFloat, _ y: CGFloat) {
        rectangle(CGRect(x:x-20,y:y-20,width:370,height:205),.white)
        label("External",x,y,28,.black);rectangle(CGRect(x:x,y:y+55,width:120,height:115),.black)
        label("Ext",x+36,y+70,25,.white);label(kind,x+30,y+115,25,.white)
    }
    external(x,y);if duplicate {external(850,150)}
    NSGraphicsContext.restoreGraphicsState()
    return bitmap.cgImage!
}
var results: [[String:Any]] = []
let cases: [(String,CGFloat,CGFloat,CGFloat,String,Bool)] = [
    ("left-popover-below",180,750,1,"TPU",false),
    ("right-popover-above-left",500,340,1,"TPU",false),
    ("resized-window",90,420,0.7,"TPU",false),
    ("retina-window",500,340,2,"TPU",false),
    ("wrong-external-type",500,340,1,"PET-CF",false),
    ("ambiguous-external",160,520,1,"TPU",true)]
for (name,x,y,scale,kind,duplicate) in cases {
    let image = fixtureImage(x:x,y:y,scale:scale,kind:kind,duplicate:duplicate)
    do {
        let choice = try externalChoice(recognizedText(image),filament:"TPU")
        guard kind == "TPU" && !duplicate else { fatalError("\(name): accepted an ambiguous or wrong filament") }
        guard choice.rect.midX > (x+30)*scale && choice.rect.midX < (x+90)*scale
            && choice.rect.midY > (y+60)*scale && choice.rect.midY < (y+110)*scale else {
            fatalError("\(name): chose \(choice.rect)")
        }
        results.append(["name":name,"point":[choice.rect.midX,choice.rect.midY]])
    } catch {
        guard kind != "TPU" || duplicate else { fatalError("\(name): \(error)") }
        results.append(["name":name,"rejected":true])
    }
}
let record: [String:Any] = ["native_ocr_cases":results,"scope":"Synthetic AppKit popovers through native Vision; no printer connection or application input."]
print(String(data:try! JSONSerialization.data(withJSONObject:record,options:[.sortedKeys]),encoding:.utf8)!)
