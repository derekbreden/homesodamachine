import SwiftUI
import UIKit

struct StudyViewport: Sendable {
    let id: String
    let title: String
    let width: CGFloat
    let height: CGFloat
    static let all: [StudyViewport] = [
        .init(id: "phone", title: "iPhone portrait", width: 402, height: 874),
        .init(id: "cover", title: "Duo cover", width: 466, height: 678),
        .init(id: "duo", title: "Duo open", width: 890, height: 626),
        .init(id: "ipad-portrait", title: "iPad portrait", width: 834, height: 1194),
        .init(id: "ipad", title: "iPad landscape", width: 1194, height: 834),
        .init(id: "narrow", title: "Narrow window", width: 320, height: 720),
        .init(id: "landscape", title: "iPhone landscape", width: 874, height: 402)
    ]
}

@main
struct SodaMachineStudyApp: App {
    var body: some Scene {
        WindowGroup {
            StudyRoot()
                .task {
                    if ProcessInfo.processInfo.arguments.contains("--render") {
                        await StudyCapture.render()
                    }
                }
        }
    }
}

@MainActor
enum StudyCapture {
    static var capturing = false
    static var hostWindow: UIWindow?

    static func render() async {
        guard !capturing else { return }
        capturing = true
        guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return }
        let directory = URL.documentsDirectory.appending(path: "renders")
        try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let window = UIWindow(windowScene: scene)
        window.overrideUserInterfaceStyle = .dark
        hostWindow = window
        var manifest: [[String: Any]] = []
        let quick = ProcessInfo.processInfo.arguments.contains("--quick")
        let args = ProcessInfo.processInfo.arguments
        let selected = args.firstIndex(of: "--routes").flatMap { i in i + 1 < args.count ? args[i + 1] : nil }
        let requested = Set(selected?.split(separator: ",").map(String.init) ?? [])
        let routes = quick ? [StudyRoute.home, .sound, .crop] : StudyRoute.allCases.filter { requested.isEmpty || requested.contains($0.rawValue) }
        let viewports = quick ? [StudyViewport.all[0], StudyViewport.all[2], StudyViewport.all[4]] : StudyViewport.all
        for viewport in viewports {
            for route in routes {
                let size = CGSize(width: viewport.width, height: viewport.height)
                let root = StudyRoot(initialRoute: route)
                    .environment(\.dynamicTypeSize, .large)
                    .frame(width: size.width, height: size.height)
                let host = UIHostingController(rootView: root)
                host.safeAreaRegions = []
                window.rootViewController = host
                window.frame = CGRect(origin: .zero, size: size)
                window.isHidden = false
                host.view.frame = CGRect(origin: .zero, size: size)
                host.view.setNeedsLayout()
                host.view.layoutIfNeeded()
                try? await Task.sleep(for: .milliseconds(120))
                host.view.frame = CGRect(origin: .zero, size: size)
                host.view.layoutIfNeeded()
                let format = UIGraphicsImageRendererFormat()
                format.scale = 2
                format.opaque = true
                let image = UIGraphicsImageRenderer(size: size, format: format).image { _ in
                    host.view.drawHierarchy(in: CGRect(origin: .zero, size: size), afterScreenUpdates: true)
                }
                let filename = "\(viewport.id)-\(route.rawValue).png"
                try? image.pngData()?.write(to: directory.appending(path: filename))
                manifest.append(["file": filename, "viewport": viewport.id, "title": viewport.title,
                                 "route": route.rawValue, "screen": route.title,
                                 "width": Int(viewport.width), "height": Int(viewport.height), "scale": 2])
            }
        }
        if let data = try? JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys]) {
            try? data.write(to: directory.appending(path: "manifest.json"))
        }
        try? Data("Native SwiftUI content renders; iOS 18.5; no device bezel, status bar, keyboard or system accessory/photo sheet.\n".utf8)
            .write(to: directory.appending(path: "COMPLETE.txt"))
        window.isHidden = true
        hostWindow = nil
    }
}
