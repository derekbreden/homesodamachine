// Drives Bambu Connect through the macOS accessibility interface.
//
// Bambu Connect is an Electron application. Setting AXManualAccessibility on it
// exposes the Chromium tree, and AXUIElementPerformAction presses a control in
// place. The application keeps whatever window position it has and never comes
// forward, so a print can be submitted while the screen belongs to something
// else. Synthesized mouse and keyboard events cannot do this: CGEvent delivery
// to .cghidEventTap follows the frontmost application, so every click costs the
// screen.
//
// The calling process supplies the accessibility trust.

import AppKit
import ApplicationServices

let BUNDLE = "com.bambulab.bambu-connect"
let USAGE = """
usage: bambu-ax <command>

  state                      printer name, job, progress and temperatures
  tree                       every labelled or actionable element, numbered
  find <text>                elements whose label contains <text>
  press <text|#n>            AXPress a control (a #n needs --expect)
  act <text|#n> <AXAction>   any action the element advertises
  value <text|#n> <new>      set an element's value
  import <path>              Print tab, file chooser, chosen file, no keystrokes
  select <name>              choose a row in an already-open file chooser
  click <x> <y> [x y ...]    real clicks for controls the tree cannot reach
  front                      name the frontmost application

  --role <AXRole>   restrict matches      --nth <n>     pick among matches
  --expect <text>   what a #n must hold; positions renumber when the tree does
"""

func fail(_ m: String) -> Never { fputs("bambu-ax: " + m + "\n", stderr); exit(1) }

guard AXIsProcessTrusted() else {
    fail("the calling process holds no accessibility trust; grant it in System Settings > Privacy & Security > Accessibility")
}
guard let app = NSRunningApplication.runningApplications(withBundleIdentifier: BUNDLE).first else {
    fail("Bambu Connect is not running; start it without the screen using: open -g -j -a 'Bambu Connect'")
}
let axApp = AXUIElementCreateApplication(app.processIdentifier)
AXUIElementSetAttributeValue(axApp, "AXManualAccessibility" as CFString, kCFBooleanTrue)

func attr(_ e: AXUIElement, _ a: String) -> String? {
    var v: CFTypeRef?
    guard AXUIElementCopyAttributeValue(e, a as CFString, &v) == .success else { return nil }
    if let s = v as? String { return s.isEmpty ? nil : s }
    if let n = v as? NSNumber { return n.stringValue }
    return nil
}
func frame(_ e: AXUIElement) -> CGRect {
    var pr: CFTypeRef?, sr: CFTypeRef?
    AXUIElementCopyAttributeValue(e, kAXPositionAttribute as CFString, &pr)
    AXUIElementCopyAttributeValue(e, kAXSizeAttribute as CFString, &sr)
    var p = CGPoint.zero, s = CGSize.zero
    if let pr { AXValueGetValue(pr as! AXValue, .cgPoint, &p) }
    if let sr { AXValueGetValue(sr as! AXValue, .cgSize, &s) }
    return CGRect(origin: p, size: s)
}
func actionNames(_ e: AXUIElement) -> [String] {
    var a: CFArray?
    guard AXUIElementCopyActionNames(e, &a) == .success, let arr = a as? [String] else { return [] }
    return arr.filter { $0 != "AXScrollToVisible" && $0 != "AXShowMenu" }
}

struct Node { let el: AXUIElement; let role: String; let label: String?; let acts: [String]; let rect: CGRect; let idx: Int; let depth: Int }
var nodes: [Node] = []
func collect(_ e: AXUIElement, _ depth: Int) {
    if depth > 24 || nodes.count > 6000 { return }
    nodes.append(Node(el: e, role: attr(e, kAXRoleAttribute) ?? "?",
                      label: attr(e, kAXTitleAttribute) ?? attr(e, kAXDescriptionAttribute) ?? attr(e, kAXValueAttribute),
                      acts: actionNames(e), rect: frame(e), idx: nodes.count, depth: depth))
    var kids: CFTypeRef?
    if AXUIElementCopyAttributeValue(e, kAXChildrenAttribute as CFString, &kids) == .success,
       let cs = kids as? [AXUIElement] { for c in cs { collect(c, depth + 1) } }
}
func build() {
    nodes.removeAll()
    var wr: CFTypeRef?
    AXUIElementCopyAttributeValue(axApp, kAXWindowsAttribute as CFString, &wr)
    for w in (wr as? [AXUIElement] ?? []) { collect(w, 0) }
}
func describe(_ n: Node) -> String {
    let t = n.label.map { " \"\($0.prefix(70))\"" } ?? ""
    let a = n.acts.isEmpty ? "" : " [\(n.acts.joined(separator: ","))]"
    let r = n.rect.size == .zero ? "" : " @\(Int(n.rect.minX)),\(Int(n.rect.minY)) \(Int(n.rect.width))x\(Int(n.rect.height))"
    return "#\(n.idx) \(String(repeating: "  ", count: n.depth))\(n.role)\(t)\(a)\(r)"
}

let args = Array(CommandLine.arguments.dropFirst())
guard let cmd = args.first else { fail(USAGE) }
func opt(_ name: String) -> String? {
    guard let i = args.firstIndex(of: name), i + 1 < args.count else { return nil }
    return args[i + 1]
}
func matches(_ query: String, role: String? = nil) -> [Node] {
    build()
    if query.hasPrefix("#"), let i = Int(query.dropFirst()) { return nodes.filter { $0.idx == i } }
    let want = role ?? opt("--role")
    let q = query.lowercased()
    return nodes.filter { n in
        guard let l = n.label?.lowercased(), l.contains(q) else { return false }
        if let want, n.role != want { return false }
        return true
    }
}
// A #n is a position in the last tree, and the tree renumbers whenever the
// screen changes. Acting on a carried-over number presses whatever now holds
// it, silently and wrongly, so a #n must say what it expects to find there.
func resolve(_ query: String, role: String? = nil, preferring action: String? = nil) -> Node {
    if query.hasPrefix("#") {
        guard let expect = opt("--expect") else {
            fail("""
                \(query) is a position, not an identity, and positions renumber whenever \
                the tree changes. Say what belongs there: --expect "<label or role>". \
                Matching by label needs no --expect.
                """)
        }
        guard let n = matches(query, role: role).first else { fail("no element at \(query)") }
        let found = "\(n.role) \(n.label ?? "")"
        guard found.lowercased().contains(expect.lowercased()) else {
            fail("\(query) now holds \(describe(n)) — expected \(expect); re-read the tree")
        }
        return n
    }
    var ms = matches(query, role: role)
    if let action { let p = ms.filter { $0.acts.contains(action) }; if !p.isEmpty { ms = p } }
    if let nth = opt("--nth"), let n = Int(nth) {
        guard n < ms.count else { fail("--nth \(n) out of range; \(ms.count) matches") }
        return ms[n]
    }
    guard !ms.isEmpty else { fail("no match for \(query)") }
    guard ms.count == 1 else {
        fputs("ambiguous — \(ms.count) matches, choose with --nth:\n", stderr)
        for (i, m) in ms.enumerated() { fputs("  --nth \(i): \(describe(m))\n", stderr) }
        exit(2)
    }
    return ms[0]
}
// A chooser row is an AXRow wrapping cells. AXOpen on the cell is refused; the
// row answers AXSelected, and the panel's Open button acts on the selection.
func ancestor(_ e: AXUIElement, role wanted: String) -> AXUIElement? {
    var cur = e
    for _ in 0..<8 {
        var p: CFTypeRef?
        guard AXUIElementCopyAttributeValue(cur, kAXParentAttribute as CFString, &p) == .success,
              let parent = p else { return nil }
        let pe = parent as! AXUIElement
        if attr(pe, kAXRoleAttribute) == wanted { return pe }
        cur = pe
    }
    return nil
}

// Selecting a chooser row is the only route that takes. AXOpen on the cell is
// refused (-25205), AXConfirm reports success and does nothing, and a click
// lands without the panel acting on it: the panel reads its selection, so set
// that and press Open.
func selectRow(_ e: AXUIElement) -> Bool {
    guard let r = ancestor(e, role: "AXRow") else { return false }
    return AXUIElementSetAttributeValue(r, kAXSelectedAttribute as CFString, kCFBooleanTrue) == .success
}
// A sidebar row navigates on AXOpen, but the action lives on its AXCell, not on
// the AXStaticText that carries the name.
func openCell(_ e: AXUIElement) -> Bool {
    if let c = ancestor(e, role: "AXCell"),
       AXUIElementPerformAction(c, "AXOpen" as CFString) == .success { return true }
    return selectRow(e)
}

let frontBefore = NSWorkspace.shared.frontmostApplication?.localizedName ?? "?"
func reportFocus() {
    let after = NSWorkspace.shared.frontmostApplication?.localizedName ?? "?"
    print("frontmost: \(frontBefore) -> \(after)\(frontBefore == after ? "  (screen kept)" : "  *** SCREEN TAKEN ***")")
}
@discardableResult
func perform(_ n: Node, _ action: String) -> Bool {
    let e = AXUIElementPerformAction(n.el, action as CFString)
    if e != .success { fputs("bambu-ax: \(action) on \(describe(n)) returned \(e.rawValue)\n", stderr) }
    return e == .success
}
func settle(_ s: Double = 0.9) { Thread.sleep(forTimeInterval: s) }

// The chooser and the importer both arrive on their own schedule. Wait on the
// element rather than on a guessed duration.
// Spin the runloop rather than sleeping: NSWorkspace's frontmost application
// only updates when this process handles the notification, so a sleeping poll
// reads its own stale answer forever.
func waitFor(_ seconds: Double, _ found: () -> Bool) -> Bool {
    let deadline = Date().addingTimeInterval(seconds)
    while Date() < deadline {
        if found() { return true }
        RunLoop.current.run(until: Date().addingTimeInterval(0.1))
    }
    return found()
}

switch cmd {
case "click":
    // A few controls are plain divs. Chromium synthesizes clicks only for
    // button and link roles, so AXPress is a no-op on them, and an event sent
    // with postToPid never arrives. The global tap is the only delivery, and it
    // follows the frontmost application — so borrow the front, click, and give
    // it back. Every coordinate in one call shares the one borrow.
    let nums = args.dropFirst().compactMap { Double($0) }
    guard nums.count >= 2, nums.count % 2 == 0 else { fail("click needs x y pairs") }
    let points = stride(from: 0, to: nums.count, by: 2).map { CGPoint(x: nums[$0], y: nums[$0 + 1]) }
    let started = Date()
    let previous = NSWorkspace.shared.frontmostApplication
    let cursor = CGEvent(source: nil)?.location

    app.activate()
    guard waitFor(3, { NSWorkspace.shared.frontmostApplication?.bundleIdentifier == BUNDLE }) else {
        fail("Bambu Connect would not come forward; nothing was clicked")
    }
    let source = CGEventSource(stateID: .hidSystemState)
    for p in points {
        for type in [CGEventType.mouseMoved, .leftMouseDown, .leftMouseUp] {
            CGEvent(mouseEventSource: source, mouseType: type, mouseCursorPosition: p, mouseButton: .left)?
                .post(tap: .cghidEventTap)
            Thread.sleep(forTimeInterval: 0.05)
        }
        Thread.sleep(forTimeInterval: 0.25)
    }
    if let cursor { CGWarpMouseCursorPosition(cursor) }
    if args.contains("--keep") {
        print("clicked \(points.map { "(\(Int($0.x)),\(Int($0.y)))" }.joined(separator: " ")) — front held")
        exit(0)
    }
    previous?.activate()
    _ = waitFor(3, { NSWorkspace.shared.frontmostApplication?.processIdentifier == previous?.processIdentifier })
    let back = NSWorkspace.shared.frontmostApplication?.localizedName ?? "?"
    let held = Date().timeIntervalSince(started)
    print("clicked \(points.map { "(\(Int($0.x)),\(Int($0.y)))" }.joined(separator: " "))")
    print(String(format: "front borrowed %.2fs, returned to %@%@", held, back,
                 back == frontBefore ? "" : "  *** NOT RESTORED ***"))

case "select":
    guard args.count > 1 else { fail("select needs the name of a row in the open chooser") }
    let want = args[1]
    guard !matches("Open", role: "AXButton").isEmpty else { fail("no file chooser is open") }
    guard let target = matches(want, role: "AXTextField").first else {
        fail("no chooser row matching \(want)")
    }
    guard selectRow(target.el) else { fail("\(target.label ?? want) is not a selectable chooser row") }
    guard let openButton = matches("Open", role: "AXButton").first else { fail("no Open button") }
    perform(openButton, "AXPress")
    let closed = waitFor(20, { matches("Open", role: "AXButton").isEmpty })
    print("select \(target.label ?? want) -> \(closed ? "chooser closed" : "chooser still open")")
    reportFocus()
    if !closed { exit(1) }

case "front":
    print(frontBefore)

case "tree":
    build()
    for n in nodes where n.label != nil || !n.acts.isEmpty { print(describe(n)) }
    print("--- \(nodes.count) nodes ---")

case "find":
    guard args.count > 1 else { fail("find needs text") }
    let ms = matches(args[1])
    if ms.isEmpty { print("no match") } else { for m in ms { print(describe(m)) } }

case "press":
    guard args.count > 1 else { fail("press needs a target") }
    let t = resolve(args[1], preferring: "AXPress")
    print("press \(describe(t)) -> \(perform(t, "AXPress") ? "ok" : "failed")")
    reportFocus()

case "act":
    guard args.count > 2 else { fail("act needs a target and an action") }
    let t = resolve(args[1], preferring: args[2])
    print("\(args[2]) \(describe(t)) -> \(perform(t, args[2]) ? "ok" : "failed")")
    reportFocus()

case "value":
    guard args.count > 2 else { fail("value needs a target and a new value") }
    let t = resolve(args[1])
    let e = AXUIElementSetAttributeValue(t.el, kAXValueAttribute as CFString, args[2] as CFTypeRef)
    print("value \(describe(t)) -> \(e == .success ? "ok" : "err \(e.rawValue)")")
    reportFocus()

case "state":
    build()
    let text = nodes.compactMap { $0.role == "AXStaticText" ? $0.label : nil }
    print(text.joined(separator: " | "))

case "import":
    guard args.count > 1 else { fail("import needs a file path") }
    let path = (args[1] as NSString).expandingTildeInPath
    guard FileManager.default.fileExists(atPath: path) else { fail("no such file: \(path)") }
    let name = (path as NSString).lastPathComponent

    // The Print tab carries the importer; pressing it while already there is harmless.
    if let tab = matches("Print", role: "AXLink").first { perform(tab, "AXPress"); settle() }
    guard let importer = matches("Import Gcode 3MF", role: "AXButton").first else {
        fail("no Import Gcode 3MF button on the Print tab")
    }
    perform(importer, "AXPress")
    guard waitFor(15, { !matches("Open", role: "AXButton").isEmpty }) else {
        fail("the file chooser did not open")
    }

    // Walk to the file's directory one component at a time. Each row answers
    // AXOpen, which is what a double-click sends, so no keystroke is needed.
    func row(_ label: String) -> Node? {
        matches(label, role: "AXTextField").first { $0.label == label }
    }
    func choose(_ n: Node) -> Bool { selectRow(n.el) }
    if row(name) == nil {
        let home = (NSHomeDirectory() as NSString).lastPathComponent
        if let side = matches(home, role: "AXStaticText").first {
            guard openCell(side.el) else { fail("could not open the home row in the chooser sidebar") }
            settle()
        }
        let rel = path.hasPrefix(NSHomeDirectory() + "/")
            ? String(path.dropFirst(NSHomeDirectory().count + 1))
            : path
        for part in rel.split(separator: "/").dropLast() {
            guard let d = row(String(part)) else { fail("could not reach \(part) in the chooser") }
            guard choose(d) else { fail("could not select \(part) in the chooser") }
            if let open = matches("Open", role: "AXButton").first { perform(open, "AXPress") }
            _ = waitFor(8, { row(String(part)) == nil })
        }
    }
    guard let target = row(name) else { fail("\(name) is not listed in the chooser") }
    guard choose(target) else { fail("could not select \(name) in the chooser") }
    guard let openButton = matches("Open", role: "AXButton").first else { fail("no Open button") }
    perform(openButton, "AXPress")
    let loaded = waitFor(20, {
        matches("Open", role: "AXButton").isEmpty && !matches(name).isEmpty
    })
    print("import \(name) -> \(loaded ? "loaded" : "NOT loaded")")
    reportFocus()
    if !loaded { exit(1) }

default:
    fail(USAGE)
}
