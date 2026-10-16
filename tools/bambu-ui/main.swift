// Foreground mouse input and live accessibility readings for Bambu Connect.
// Requests and replies are newline-delimited JSON on stdin and stdout.
import AppKit
import ApplicationServices
import ScreenCaptureKit
import Vision

let bundle = "com.bambulab.bambu-connect"
struct Failure: Error { let message: String }
func refuse(_ text: String) throws -> Never { throw Failure(message: text) }
func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else { return nil }
    return value
}
func text(_ element: AXUIElement, _ name: String) -> String {
    if let value = attribute(element, name) as? String { return value }
    if let value = attribute(element, name) as? NSNumber { return value.stringValue }
    return ""
}
func bounds(_ element: AXUIElement) -> CGRect {
    var point = CGPoint.zero, size = CGSize.zero
    if let value = attribute(element, kAXPositionAttribute) {
        AXValueGetValue(value as! AXValue, .cgPoint, &point)
    }
    if let value = attribute(element, kAXSizeAttribute) {
        AXValueGetValue(value as! AXValue, .cgSize, &size)
    }
    return CGRect(origin: point, size: size)
}
func tick(_ seconds: Double = 0.1) { RunLoop.current.run(until: Date().addingTimeInterval(seconds)) }
func wait(_ seconds: Double, _ predicate: () -> Bool) -> Bool {
    let end = Date().addingTimeInterval(seconds)
    repeat { if predicate() { return true }; tick() } while Date() < end
    return false
}
struct Node {
    let element: AXUIElement
    let parent: Int
    let role: String
    let label: String
    let rect: CGRect
    let enabled: Bool
}
var app: NSRunningApplication?
var root: AXUIElement?
var nodes: [Node] = []
let previousApp = NSWorkspace.shared.frontmostApplication
let previousPointer = CGEvent(source: nil)?.location
func foreground() -> Bool { NSWorkspace.shared.frontmostApplication?.bundleIdentifier == bundle }
func requireForeground() throws {
    tick(0.02)
    guard foreground() else { try refuse("Bambu Connect lost focus; no input was sent") }
}
func collect(_ element: AXUIElement, parent: Int, depth: Int) {
    guard depth < 50, nodes.count < 12000 else { return }
    let role = text(element, kAXRoleAttribute)
    let label = [kAXTitleAttribute, kAXDescriptionAttribute, kAXValueAttribute]
        .map { text(element, $0) }.first { !$0.isEmpty } ?? ""
    let index = nodes.count
    nodes.append(Node(element: element, parent: parent, role: role, label: label,
                      rect: bounds(element), enabled: text(element, kAXEnabledAttribute) != "0"))
    for child in attribute(element, kAXChildrenAttribute) as? [AXUIElement] ?? [] {
        collect(child, parent: index, depth: depth + 1)
    }
}
func snapshot() -> [[String: Any]] {
    tick(0.04)
    nodes = []
    if let root {
        for window in attribute(root, kAXWindowsAttribute) as? [AXUIElement] ?? [] {
            collect(window, parent: -1, depth: 0)
        }
    }
    return nodes.enumerated().map { index, node in
        ["id": index, "parent": node.parent, "role": node.role, "label": node.label,
         "enabled": node.enabled, "rect": [node.rect.minX, node.rect.minY, node.rect.width, node.rect.height]]
    }
}
func resolve(_ request: [String: Any]) throws -> Node {
    _ = snapshot()
    guard let label = request["label"] as? String else { try refuse("label is required") }
    let prefix = request["prefix"] as? Bool ?? false
    let matches = nodes.filter {
        ($0.label == label || (prefix && $0.label.hasPrefix(label + " ")))
        && (request["role"] == nil || $0.role == request["role"] as? String)
    }
    if let occurrence = request["nth"] as? Int, matches.indices.contains(occurrence) { return matches[occurrence] }
    guard matches.count == 1 else { try refuse("Expected one \(request["role"] ?? "element") named \(label), found \(matches.count)") }
    return matches[0]
}
func mouse(_ point: CGPoint, expected: AXUIElement? = nil) throws {
    try requireForeground()
    if let expected {
        let owner: AXUIElement
        if text(expected, kAXRoleAttribute) == kAXRadioButtonRole,
           let parent = attribute(expected, kAXParentAttribute) {
            owner = parent as! AXUIElement
        } else {
            owner = expected
        }
        var hit: AXUIElement?
        AXUIElementCopyElementAtPosition(AXUIElementCreateSystemWide(), Float(point.x), Float(point.y), &hit)
        var target = hit
        var matches = false
        var seen: [String] = []
        for _ in 0..<16 {
            guard let element = target else { break }
            seen.append(text(element, kAXRoleAttribute) + " " + text(element, kAXTitleAttribute))
            if CFEqual(element, owner) { matches = true; break }
            target = attribute(element, kAXParentAttribute).map { $0 as! AXUIElement }
        }
        guard matches else { try refuse("Control is covered at \(Int(point.x)),\(Int(point.y)): \(seen.joined(separator: " > ")); no click was sent") }
    }
    let source = CGEventSource(stateID: .hidSystemState)
    for kind in [CGEventType.mouseMoved, .leftMouseDown, .leftMouseUp] {
        guard let event = CGEvent(mouseEventSource: source, mouseType: kind,
                                  mouseCursorPosition: point, mouseButton: .left) else {
            try refuse("Could not create mouse event")
        }
        event.post(tap: .cghidEventTap)
        tick(0.07)
    }
    tick(0.2)
}
func key(_ code: CGKeyCode, flags: CGEventFlags = []) throws {
    try requireForeground()
    for down in [true, false] {
        guard let event = CGEvent(keyboardEventSource: nil, virtualKey: code, keyDown: down) else {
            try refuse("Could not create keyboard event")
        }
        event.flags = flags
        event.post(tap: .cghidEventTap)
        tick(0.05)
    }
}

struct VisibleText {
    let value: String
    let rect: CGRect // Image pixels, top-left origin.
}
func recognizedText(_ image: CGImage) throws -> [VisibleText] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]
    try VNImageRequestHandler(cgImage: image).perform([request])
    return (request.results ?? []).compactMap { result in
        guard let candidate = result.topCandidates(1).first, candidate.confidence >= 0.8 else { return nil }
        let box = result.boundingBox
        return VisibleText(value: candidate.string, rect: CGRect(
            x: box.minX * Double(image.width), y: (1-box.maxY) * Double(image.height),
            width: box.width * Double(image.width), height: box.height * Double(image.height)))
    }
}
func filamentWord(_ text: String) -> String {
    text.uppercased().filter { $0.isLetter || $0.isNumber }
}
func externalChoice(_ words: [VisibleText], filament: String) throws -> VisibleText {
    // Connect's popover has an External heading and one Ext/type tile for
    // the selected nozzle. Locate their visible relationship, not its offset
    // from the source tile. The selected tile in the dialog has no such heading.
    let headings = words.filter { $0.value.lowercased() == "external" }
    let labels = words.filter { $0.value.lowercased() == "ext" }
    let types = words.filter { filamentWord($0.value) == filamentWord(filament) }
    var choices: [VisibleText] = []
    for label in labels {
        let heading = headings.contains { h in
            let unit = max(h.rect.height,label.rect.height)
            return label.rect.minY >= h.rect.maxY && label.rect.minY-h.rect.maxY < 10*unit
                && label.rect.midX >= h.rect.minX && label.rect.midX-h.rect.minX < 15*unit
        }
        let matchingType = types.contains { t in
            let unit = max(t.rect.height,label.rect.height)
            return t.rect.minY >= label.rect.maxY && t.rect.minY-label.rect.maxY < 4*unit
                && abs(t.rect.midX-label.rect.midX) < max(t.rect.width,label.rect.width)
        }
        if heading && matchingType { choices.append(label) }
    }
    guard choices.count == 1 else {
        try refuse("Expected one visible External > Ext \(filament) choice, found \(choices.count)")
    }
    return choices[0]
}
func capturePrintWindow() throws -> (CGImage, CGRect) {
    guard CGPreflightScreenCaptureAccess() else {
        try refuse("Screen recording access is unavailable; the filament popover cannot be read")
    }
    var content: SCShareableContent?, contentError: Error?, contentDone = false
    SCShareableContent.getExcludingDesktopWindows(true, onScreenWindowsOnly: false) { value,error in
        content = value; contentError = error; contentDone = true
    }
    guard wait(10,{ contentDone }) else { try refuse("Timed out reading Bambu Connect's window") }
    if let error = contentError { throw error }
    guard let pid = app?.processIdentifier,
          let window = content?.windows.first(where: {
              $0.owningApplication?.processID == pid && $0.title == "Bambu Connect (Beta)"
          }) else { try refuse("The Bambu Connect print window was not found") }
    let configuration = SCStreamConfiguration()
    configuration.width = Int(window.frame.width*2)
    configuration.height = Int(window.frame.height*2)
    configuration.showsCursor = false
    configuration.ignoreShadowsSingleWindow = true
    var image: CGImage?, imageError: Error?, imageDone = false
    SCScreenshotManager.captureImage(contentFilter: SCContentFilter(desktopIndependentWindow: window),
                                    configuration: configuration) { value,error in
        image = value; imageError = error; imageDone = true
    }
    guard wait(10,{ imageDone }) else { try refuse("Timed out capturing Bambu Connect's print window") }
    if let error = imageError { throw error }
    guard let image else { try refuse("Bambu Connect's window capture is empty") }
    return (image,window.frame)
}
func handle(_ request: [String: Any]) throws -> [String: Any] {
    switch request["command"] as? String {
    case "focus":
        guard AXIsProcessTrusted() else { try refuse("This caller has no macOS Accessibility permission") }
        if NSRunningApplication.runningApplications(withBundleIdentifier: bundle).isEmpty {
            let config = NSWorkspace.OpenConfiguration(); config.activates = false
            guard let url = NSWorkspace.shared.urlForApplication(withBundleIdentifier: bundle) else {
                try refuse("Bambu Connect is not installed")
            }
            NSWorkspace.shared.openApplication(at: url, configuration: config) { _, _ in }
        }
        guard wait(30, { app = NSRunningApplication.runningApplications(withBundleIdentifier: bundle).first; return app != nil }),
              let app else { try refuse("Bambu Connect did not start") }
        root = AXUIElementCreateApplication(app.processIdentifier)
        AXUIElementSetAttributeValue(root!, "AXManualAccessibility" as CFString, kCFBooleanTrue)
        app.activate()
        guard wait(5, foreground) else { try refuse("Bambu Connect did not come forward") }
        guard wait(20, { !snapshot().isEmpty }) else { try refuse("Bambu Connect has no accessible window") }
        if let window = nodes.first(where: { $0.role == kAXWindowRole && $0.label == "Bambu Connect (Beta)" }) {
            AXUIElementPerformAction(window.element, kAXRaiseAction as CFString)
        }
        tick(0.3)
        return ["nodes": snapshot()]
    case "snapshot": return ["nodes": snapshot(), "foreground": foreground()]
    case "click":
        let node = try resolve(request)
        guard node.enabled, node.rect.width > 0, node.rect.height > 0 else {
            try refuse("Control \(node.label) is disabled or has no visible bounds")
        }
        try mouse(CGPoint(x: node.rect.midX, y: node.rect.midY), expected: node.element)
        return ["clicked": node.label]
    case "click_offsets":
        let node = try resolve(request)
        guard let offsets = request["offsets"] as? [[Double]], !offsets.isEmpty,
              offsets.allSatisfy({ $0.count == 2 }) else { try refuse("offsets must be x/y pairs") }
        for (i, offset) in offsets.enumerated() {
            try mouse(CGPoint(x: node.rect.minX + offset[0], y: node.rect.minY + offset[1]),
                      expected: i == 0 ? node.element : nil)
        }
        return ["clicked": node.label]
    case "read_window_text":
        let (image,frame) = try capturePrintWindow()
        let words = try recognizedText(image)
        return ["frame": [frame.minX,frame.minY,frame.width,frame.height],
                "text": words.map { ["text":$0.value,
                                      "rect":[$0.rect.minX,$0.rect.minY,$0.rect.width,$0.rect.height]] }]
    case "select_external":
        let node = try resolve(request)
        guard let filament = request["filament"] as? String,
              let nozzle = request["nozzle"] as? Int, [1,2].contains(nozzle),
              let divider = nodes.first(where: {
                  $0.role == kAXStaticTextRole && $0.label == "Right Nozzle"
              })?.rect.minX else { try refuse("Filament and nozzle columns are required") }
        guard (node.rect.minX >= divider ? 2 : 1) == nozzle else {
            try refuse("The filament tile is in the wrong nozzle column")
        }
        try mouse(CGPoint(x:node.rect.midX,y:node.rect.midY),expected:node.element)
        var choice: VisibleText?, shotFrame = CGRect.zero, shotSize = CGSize.zero
        var lastError = "The filament popover did not appear"
        for _ in 0..<3 {
            let (image,frame) = try capturePrintWindow()
            do {
                choice = try externalChoice(recognizedText(image),filament:filament)
                shotFrame = frame; shotSize = CGSize(width:image.width,height:image.height)
                break
            } catch { lastError = (error as? Failure)?.message ?? error.localizedDescription }
            tick(0.2)
        }
        guard let choice else { try refuse(lastError + "; no spool choice was clicked") }
        let point = CGPoint(x:shotFrame.minX+choice.rect.midX/shotSize.width*shotFrame.width,
                            y:shotFrame.minY+choice.rect.midY/shotSize.height*shotFrame.height)
        guard shotFrame.contains(point) else { try refuse("The spool choice is outside Bambu Connect") }
        _ = snapshot()
        guard let currentFrame = nodes.first(where: {
            $0.role == kAXWindowRole && $0.label == "Bambu Connect (Beta)"
        })?.rect, abs(currentFrame.minX-shotFrame.minX) < 1,
              abs(currentFrame.minY-shotFrame.minY) < 1,
              abs(currentFrame.width-shotFrame.width) < 1,
              abs(currentFrame.height-shotFrame.height) < 1 else {
            try refuse("Bambu Connect moved while the spool choice was being read")
        }
        try mouse(point)
        return ["clicked":"External > Ext \(filament)","nozzle":nozzle,
                "point":[point.x,point.y]]
    case "open_path":
        guard let path = request["path"] as? String, FileManager.default.fileExists(atPath: path) else {
            try refuse("The import file does not exist")
        }
        guard snapshot().contains(where: { $0["role"] as? String == kAXSheetRole }) else {
            try refuse("No file chooser is open")
        }
        func pathField() -> AXUIElement? {
            _ = snapshot()
            return nodes.first(where: { text($0.element, kAXIdentifierAttribute) == "PathTextField" })?.element
        }
        if pathField() == nil { try key(5, flags: [.maskCommand, .maskShift]) }
        guard wait(5, { pathField() != nil }), let field = pathField() else {
            try refuse("The Go to Folder path field did not appear")
        }
        guard AXUIElementSetAttributeValue(field, kAXValueAttribute as CFString, path as CFString) == .success,
              text(field, kAXValueAttribute) == path else { try refuse("The import path was not entered") }
        try key(36)
        guard wait(8, { pathField() == nil }) else { try refuse("Go to Folder did not accept the import path") }
        return [:]
    default: try refuse("Unknown command")
    }
}
while let line = readLine() {
    do {
        guard let request = try JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any] else {
            try refuse("Expected a JSON request")
        }
        let result = try handle(request).merging(["ok": true]) { left, _ in left }
        print(String(data: try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]), encoding: .utf8)!)
    } catch {
        let message = (error as? Failure)?.message ?? error.localizedDescription
        let data = try! JSONSerialization.data(withJSONObject: ["ok": false, "error": message])
        print(String(data: data, encoding: .utf8)!)
    }
    fflush(stdout)
}
if foreground() {
    if let point = previousPointer { CGWarpMouseCursorPosition(point) }
    previousApp?.activate()
}
