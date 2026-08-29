import SwiftUI

// ────────────────────────────────────────────────────────────
// Choosing what part of a photograph the machine gets.
//
// ONE RECTANGLE COMES OUT OF ONE PHOTOGRAPH. Every face the machine wears is
// the faucet's glass — 43:80, at three scales — so there is one shape to frame
// and framing it answers the whole question. The window is that shape, with the
// whole surface to pan and pinch on, and what it shows is what the machine gets.
//
// A FRAME CAN BE WIDER THAN THE PICTURE. A logo shot tight has no room above
// and below it to become a tall glass, and cropping is the wrong tool for a
// shortage of background — so zooming out past the photograph's own edge
// continues it in the colour its edges run into. Two things keep that from
// happening by accident: pinching back out STOPS at the picture's own frame,
// and only a pinch that begins there goes past it. Zooming out ends the moment
// the other axis reaches the photograph's edge, because past that there is
// nothing left to reveal.
// ────────────────────────────────────────────────────────────

/// How a photograph's edges carry on past themselves, so a frame wider than the
/// picture continues it rather than boxing it in black. Each edge is a short run
/// of colours along its length: a solid backdrop gives a flat one, a gradient
/// keeps its gradient, and a subject touching an edge is outvoted by the median
/// of the band it sits in rather than smeared into a streak.
struct EdgeBackground {
    var top: [Color] = [.black]
    var bottom: [Color] = [.black]
    var left: [Color] = [.black]
    var right: [Color] = [.black]

    static func detect(_ image: UIImage) -> EdgeBackground {
        let n = 64, depth = 4, steps = 9
        var px = [UInt8](repeating: 0, count: n * n * 4)
        guard let cg = image.cgImage,
              let ctx = CGContext(data: &px, width: n, height: n, bitsPerComponent: 8,
                                  bytesPerRow: n * 4, space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)
        else { return EdgeBackground() }
        ctx.interpolationQuality = .medium
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: n, height: n))

        // A median rather than a mean: a backdrop with one dark corner should
        // give the backdrop, not a shade between the two.
        func median(_ v: [(UInt8, UInt8, UInt8)]) -> Color {
            guard !v.isEmpty else { return .black }
            let m = v.count / 2
            return Color(red: Double(v.map(\.0).sorted()[m]) / 255,
                         green: Double(v.map(\.1).sorted()[m]) / 255,
                         blue: Double(v.map(\.2).sorted()[m]) / 255)
        }

        // Row 0 of a bitmap context is the picture's top row. `along` runs the
        // length of the edge and `into` runs inward from it, so one closure
        // names each edge.
        func edge(_ pick: (_ along: Int, _ into: Int) -> (Int, Int)) -> [Color] {
            (0..<steps).map { s in
                let lo = s * n / steps, hi = max(lo + 1, (s + 1) * n / steps)
                var bucket: [(UInt8, UInt8, UInt8)] = []
                for a in lo..<hi {
                    for d in 0..<depth {
                        let (x, y) = pick(a, d)
                        let i = (y * n + x) * 4
                        bucket.append((px[i], px[i + 1], px[i + 2]))
                    }
                }
                return median(bucket)
            }
        }

        return EdgeBackground(top:    edge { a, d in (a, d) },
                              bottom: edge { a, d in (a, n - 1 - d) },
                              left:   edge { a, d in (d, a) },
                              right:  edge { a, d in (n - 1 - d, a) })
    }
}

struct ImageCropView: View {
    let image: UIImage
    let onUse: (UIImage) -> Void
    let onCancel: () -> Void

    /// Where the rectangle sits on the photograph. Scale 1 is the largest
    /// rectangle of that shape the photograph can give — the frame someone
    /// uploaded. Above it is a tighter crop; below it the frame has outgrown
    /// the picture and the difference is background.
    private struct Framing: Equatable {
        var scale: CGFloat = 1
        var center = CGPoint(x: 0.5, y: 0.5)
    }

    @State private var tall = Framing()
    @State private var edges = EdgeBackground()
    /// The framing a gesture started from, so pan and pinch of the same touch
    /// are both measured against one fixed thing rather than against each other
    /// — and so the floor a pinch is allowed to reach is decided once, from
    /// where the fingers landed.
    @State private var gestureBase: Framing?

    private let tallAspect: CGFloat = 172.0 / 320.0

    var body: some View {
        GeometryReader { geo in
            // The window is the largest glass-shaped rectangle that fits in
            // what the titles and the buttons leave. It is the only rendition
            // of the picture on this screen, because every face the machine
            // wears is this one at another size.
            let window = fit(in: CGSize(width: geo.size.width - 48,
                                        height: geo.size.height - 220))

            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    Text("Position your picture")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                        .padding(.top, 24)

                    Text("Drag to move, pinch to zoom.")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.top, 6)
                        .padding(.horizontal, 24)

                    Spacer(minLength: 8)

                    view(size: window)
                        .overlay(
                            Rectangle()
                                .strokeBorder(Color.white.opacity(0.55), lineWidth: 2)
                        )
                        .contentShape(Rectangle())
                        .gesture(gesture(window))

                    Spacer(minLength: 8)

                    HStack(spacing: 12) {
                        Button("Cancel", action: onCancel)
                            .font(.system(size: 16))
                            .foregroundStyle(Theme.textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)

                        Button("Use This") { onUse(crop()) }
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(Theme.textPrimary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.white.opacity(0.12))
                            .cornerRadius(12)
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 12)
                    .padding(.bottom, 28)
                }
            }
        }
        .task {
            // Off the main thread: nothing on screen needs it until someone
            // zooms past the picture's own edge.
            let source = image
            edges = await Task.detached(priority: .userInitiated) {
                EdgeBackground.detect(source)
            }.value
        }
    }

    // ── Drawing the rectangle of the photograph ───────────────────────────

    private func view(size: CGSize) -> some View {
        let r = rect(tall)
        let k = size.width / max(r.width, 1)     // display points per source pixel
        let shown = CGSize(width: image.size.width * k, height: image.size.height * k)
        let at = CGPoint(x: (image.size.width / 2 - r.midX) * k,
                         y: (image.size.height / 2 - r.midY) * k)

        return ZStack {
            bands(size, shown, at)
            Image(uiImage: image)
                .resizable()
                .frame(width: shown.width, height: shown.height)
                .offset(x: at.x, y: at.y)
        }
        .frame(width: size.width, height: size.height)
        .clipped()
    }

    /// What fills the frame where the photograph has run out. Only ever one
    /// pair of edges — zooming out stops the moment the other axis reaches the
    /// picture — so this is two runs of colour meeting under the middle of the
    /// photograph, where the seam cannot be seen. Each is laid out across the
    /// photograph's own extent, so its colours sit over the columns they were
    /// taken from and the join at the picture's edge disappears.
    @ViewBuilder
    private func bands(_ size: CGSize, _ shown: CGSize, _ at: CGPoint) -> some View {
        if extendsVertically(tallAspect) {
            VStack(spacing: 0) {
                LinearGradient(colors: edges.top, startPoint: .leading, endPoint: .trailing)
                LinearGradient(colors: edges.bottom, startPoint: .leading, endPoint: .trailing)
            }
            .frame(width: shown.width, height: (size.height + shown.height) * 2)
            .offset(x: at.x, y: at.y)
        } else {
            HStack(spacing: 0) {
                LinearGradient(colors: edges.left, startPoint: .top, endPoint: .bottom)
                LinearGradient(colors: edges.right, startPoint: .top, endPoint: .bottom)
            }
            .frame(width: (size.width + shown.width) * 2, height: shown.height)
            .offset(x: at.x, y: at.y)
        }
    }

    // ── The gesture ───────────────────────────────────────────────────────
    // Pan and pinch, on the whole window, applied to whichever shape is in it.
    // There is no second gesture surface, because there is no longer a second
    // rectangle sharing this one.

    private func gesture(_ window: CGSize) -> some Gesture {
        SimultaneousGesture(DragGesture(minimumDistance: 0), MagnificationGesture())
            .onChanged { v in
                let base = gestureBase ?? tall
                if gestureBase == nil { gestureBase = base }

                var f = base
                if let m = v.second {
                    // Coming back out stops at the photograph's own frame.
                    // Starting a pinch already there is the only way past it,
                    // which makes going past a second, deliberate ask.
                    let floor = base.scale <= 1.0001 ? minScale(tallAspect) : 1
                    f.scale = min(max(base.scale * m, floor), maxScale())
                }
                if let d = v.first {
                    // Measured at the scale this frame is drawn at, so a pinch
                    // and a drag in one touch track the finger rather than
                    // fighting over it.
                    let k = window.width / max(rect(f).width, 1)
                    f.center = CGPoint(
                        x: base.center.x - d.translation.width / (k * image.size.width),
                        y: base.center.y - d.translation.height / (k * image.size.height))
                }
                tall = clamp(f)
            }
            .onEnded { _ in gestureBase = nil }
    }

    // ── Geometry ──────────────────────────────────────────────────────────

    /// The rectangle a framing selects, in the source's own pixels. It may
    /// reach past them, and what lies past them is background.
    private func rect(_ f: Framing) -> CGRect {
        let (w, h) = extent(f, aspect: tallAspect)
        let cx = bound(f.center.x * image.size.width, w, image.size.width)
        let cy = bound(f.center.y * image.size.height, h, image.size.height)
        return CGRect(x: cx - w / 2, y: cy - h / 2, width: w, height: h)
    }

    private func extent(_ f: Framing, aspect a: CGFloat) -> (CGFloat, CGFloat) {
        let w = min(image.size.width, image.size.height * a) / max(f.scale, 0.01)
        return (w, w / a)
    }

    /// A frame narrower than the photograph has to stay inside it; a frame
    /// wider than the photograph has to keep all of it. The same sentence
    /// either way: no edge of the frame may cut into nothing.
    private func bound(_ c: CGFloat, _ extent: CGFloat, _ source: CGFloat) -> CGFloat {
        let lo = extent / 2, hi = source - extent / 2
        return min(max(c, min(lo, hi)), max(lo, hi))
    }

    private func clamp(_ f: Framing) -> Framing {
        var g = f
        g.scale = min(max(f.scale, minScale(tallAspect)), maxScale())
        let (w, h) = extent(g, aspect: tallAspect)
        g.center = CGPoint(x: bound(g.center.x * image.size.width, w, image.size.width) / max(image.size.width, 1),
                           y: bound(g.center.y * image.size.height, h, image.size.height) / max(image.size.height, 1))
        return g
    }

    /// A photograph cannot be zoomed past its own resolution: the tightest crop
    /// allowed is the one that still fills the largest rendition it feeds.
    private func maxScale() -> CGFloat {
        let widest = min(image.size.width, image.size.height * tallAspect)
        return max(1, widest / CGFloat(ImageBundle.sizes[0].w))
    }

    /// How far out a frame can grow: until its other axis reaches the edge of
    /// the photograph. Past that both axes would be background, which reveals
    /// nothing and only makes the picture smaller.
    private func minScale(_ a: CGFloat) -> CGFloat {
        let w = image.size.width, h = image.size.height * a
        guard w > 0, h > 0 else { return 1 }
        return min(w, h) / max(w, h)
    }

    /// Which pair of edges a frame wider than the picture has to continue.
    /// A window narrower than the photograph runs out of height first.
    private func extendsVertically(_ a: CGFloat) -> Bool {
        a < image.size.width / max(image.size.height, 1)
    }

    private func fit(in room: CGSize) -> CGSize {
        let h = min(room.height, room.width / tallAspect)
        return CGSize(width: h * tallAspect, height: h)
    }

    // ── Back to the source's own pixels ───────────────────────────────────

    private func crop() -> UIImage {
        // Through UIImage once, so an EXIF-rotated camera photo is upright
        // before the rectangle is measured against it.
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        let upright = UIGraphicsImageRenderer(size: image.size, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: image.size))
        }
        return cut(rect(tall), from: upright)
    }

    /// One rectangle of the source at full resolution — and where the rectangle
    /// reaches past the source, the colour its edges run into.
    private func cut(_ rect: CGRect, from upright: UIImage) -> UIImage {
        guard let cg = upright.cgImage else { return image }
        let px = CGFloat(cg.width) / max(image.size.width, 1)
        let r = CGRect(x: rect.minX * px, y: rect.minY * px,
                       width: rect.width * px, height: rect.height * px)
        let whole = CGRect(x: 0, y: 0, width: CGFloat(cg.width), height: CGFloat(cg.height))

        // Inside the photograph: its own pixels, untouched.
        if whole.insetBy(dx: -0.5, dy: -0.5).contains(r), let inside = cg.cropping(to: r) {
            return UIImage(cgImage: inside)
        }

        let size = CGSize(width: max(r.width.rounded(), 1), height: max(r.height.rounded(), 1))
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        return UIGraphicsImageRenderer(size: size, format: format).image { c in
            let g = c.cgContext
            let vertical = extendsVertically(rect.width / max(rect.height, 1))
            let x0 = -r.minX, y0 = -r.minY

            /// One edge's colours, run across the photograph's own extent and
            /// held at their end colours beyond it.
            func band(_ colors: [Color], _ area: CGRect) {
                let cs = colors.count >= 2 ? colors : colors + colors
                guard !area.isEmpty,
                      let grad = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(),
                                            colors: cs.map { UIColor($0).cgColor } as CFArray,
                                            locations: nil) else { return }
                g.saveGState()
                g.clip(to: area)
                g.drawLinearGradient(
                    grad,
                    start: vertical ? CGPoint(x: x0, y: 0) : CGPoint(x: 0, y: y0),
                    end: vertical ? CGPoint(x: x0 + whole.width, y: 0)
                                  : CGPoint(x: 0, y: y0 + whole.height),
                    options: [.drawsBeforeStartLocation, .drawsAfterEndLocation])
                g.restoreGState()
            }

            // The seam between them falls under the middle of the photograph,
            // where the photograph itself covers it.
            if vertical {
                let seam = whole.midY + y0
                band(edges.top, CGRect(x: 0, y: 0, width: size.width, height: seam))
                band(edges.bottom, CGRect(x: 0, y: seam, width: size.width, height: size.height - seam))
            } else {
                let seam = whole.midX + x0
                band(edges.left, CGRect(x: 0, y: 0, width: seam, height: size.height))
                band(edges.right, CGRect(x: seam, y: 0, width: size.width - seam, height: size.height))
            }
            UIImage(cgImage: cg).draw(in: CGRect(x: x0, y: y0,
                                                 width: whole.width, height: whole.height))
        }
    }
}
