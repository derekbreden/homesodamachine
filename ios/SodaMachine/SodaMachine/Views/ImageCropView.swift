import SwiftUI

// ────────────────────────────────────────────────────────────
// Choosing what part of a photograph the machine gets.
//
// TWO RECTANGLES COME OUT OF ONE PHOTOGRAPH. The faucet fills a tall 172x320
// glass and the front display wears a square card, so a picture has to give up
// two different shapes. They want different things out of it: a face composed
// for the tall glass sits high in the frame, and the square that flatters the
// same face is neither the middle of that glass nor the same distance away.
//
// ONE IS FRAMED AT A TIME AND BOTH ARE ALWAYS VISIBLE. The big window is
// whichever shape is being framed, with the whole surface to pan and pinch on;
// the two previews under it are the finished faces, live, and tapping one makes
// it the window. Nothing about the second shape is a second screen, and nothing
// about it is a smaller version of the first one's gestures.
//
// THE SQUARE FOLLOWS UNTIL SOMEONE FRAMES IT. Left alone it is the square
// inscribed in the faucet's frame, so the two faces stay recognisably the same
// picture and one gesture still answers the whole question. It detaches the
// moment it is touched, and a button on its preview puts it back.
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

struct ImageCrop {
    let portrait: UIImage   // 172:320, for the faucet
    let square: UIImage     // 1:1, for the enclosure's card and its smaller sizes
}

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
    let onUse: (ImageCrop) -> Void
    let onCancel: () -> Void

    /// Which shape the window is currently showing.
    private enum Face: Hashable { case faucet, display }

    /// Where one rectangle sits on the photograph. Scale 1 is the largest
    /// rectangle of that shape the photograph can give — the frame someone
    /// uploaded. Above it is a tighter crop; below it the frame has outgrown
    /// the picture and the difference is background.
    private struct Framing: Equatable {
        var scale: CGFloat = 1
        var center = CGPoint(x: 0.5, y: 0.5)
    }

    @State private var active: Face = .faucet
    @State private var tall = Framing()
    @State private var square = Framing()
    @State private var squareFollows = true
    @State private var edges = EdgeBackground()
    /// The framing a gesture started from, so pan and pinch of the same touch
    /// are both measured against one fixed thing rather than against each other
    /// — and so the floor a pinch is allowed to reach is decided once, from
    /// where the fingers landed.
    @State private var gestureBase: Framing?

    private let tallAspect: CGFloat = 172.0 / 320.0

    var body: some View {
        GeometryReader { geo in
            // The window is the largest rectangle of the active shape that fits
            // in what the titles, the previews and the buttons leave. The band
            // it sits in is the taller shape's height whichever shape is in it,
            // so switching faces moves the window's edges and nothing else —
            // the previews and the buttons are where they were.
            let room = CGSize(width: geo.size.width - 48, height: geo.size.height - 340)
            let window = fit(aspect(active), in: room)
            let band = fit(tallAspect, in: room).height

            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    Text("Position your picture")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                        .padding(.top, 24)

                    Text("Tap either face to frame it. Drag to move, pinch to zoom.")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.top, 6)
                        .padding(.horizontal, 24)

                    Spacer(minLength: 8)

                    view(of: active, size: window)
                        .overlay(
                            Rectangle()
                                .strokeBorder(Color.white.opacity(0.55), lineWidth: 2)
                        )
                        .contentShape(Rectangle())
                        .gesture(gesture(window))
                        .frame(height: band)

                    Spacer(minLength: 8)

                    HStack(alignment: .top, spacing: 26) {
                        preview(.faucet)
                        preview(.display)
                    }
                    .padding(.bottom, 4)

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

    // ── The two faces, under the window ───────────────────────────────────
    // Each is the rendition itself at a size you can judge, not a diagram of
    // where a rectangle sits. The one being framed is lit; the other is the
    // answer you are getting for free.

    private func preview(_ face: Face) -> some View {
        let side: CGFloat = 96
        let size = CGSize(width: side * aspect(face), height: side)
        let on = active == face

        return VStack(spacing: 6) {
            view(of: face, size: size)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(on ? Color.white : Color.white.opacity(0.22),
                                lineWidth: on ? 2 : 1)
                )
                .opacity(on ? 1 : 0.55)
                .overlay(alignment: .topLeading) {
                    // Only ever on the square, and only once it is on its own:
                    // the way back to following the faucet, which is otherwise
                    // a framing someone would have to rebuild by hand.
                    if face == .display && !squareFollows {
                        Button { squareFollows = true; square = Framing() } label: {
                            Image(systemName: "arrow.uturn.backward.circle.fill")
                                .font(.system(size: 18))
                                .symbolRenderingMode(.palette)
                                .foregroundStyle(.white, .black.opacity(0.5))
                        }
                        .buttonStyle(.plain)
                        .padding(5)
                    }
                }

            Text(face == .faucet ? "Faucet" : "Front display")
                .font(.system(size: 11, weight: on ? .medium : .regular))
                .foregroundStyle(on ? Theme.textPrimary : Theme.textSecondary)
        }
        .contentShape(Rectangle())
        .onTapGesture { withAnimation(.easeInOut(duration: 0.18)) { active = face } }
    }

    // ── Drawing a rectangle of the photograph ─────────────────────────────
    // One function draws the window and both previews, so a preview cannot
    // drift from what the window says — it is the same crop at another size.

    private func view(of face: Face, size: CGSize) -> some View {
        let a = aspect(face)
        let r = rect(framing(face), aspect: a)
        let k = size.width / max(r.width, 1)     // display points per source pixel
        let shown = CGSize(width: image.size.width * k, height: image.size.height * k)
        let at = CGPoint(x: (image.size.width / 2 - r.midX) * k,
                         y: (image.size.height / 2 - r.midY) * k)

        return ZStack {
            bands(size, shown, at, a)
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
    private func bands(_ size: CGSize, _ shown: CGSize, _ at: CGPoint, _ a: CGFloat) -> some View {
        if extendsVertically(a) {
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
                let base = gestureBase ?? framing(active)
                if gestureBase == nil { gestureBase = base }

                var f = base
                if let m = v.second {
                    // Coming back out stops at the photograph's own frame.
                    // Starting a pinch already there is the only way past it,
                    // which makes going past a second, deliberate ask.
                    let floor = base.scale <= 1.0001 ? minScale(aspect(active)) : 1
                    f.scale = min(max(base.scale * m, floor), maxScale(active))
                }
                if let d = v.first {
                    // Measured at the scale this frame is drawn at, so a pinch
                    // and a drag in one touch track the finger rather than
                    // fighting over it.
                    let k = window.width / max(rect(f, aspect: aspect(active)).width, 1)
                    f.center = CGPoint(
                        x: base.center.x - d.translation.width / (k * image.size.width),
                        y: base.center.y - d.translation.height / (k * image.size.height))
                }
                set(f)
            }
            .onEnded { _ in gestureBase = nil }
    }

    /// Framing the active shape is what detaches the square from the faucet.
    private func set(_ f: Framing) {
        switch active {
        case .faucet:
            tall = clamp(f, .faucet)
        case .display:
            square = clamp(f, .display)
            squareFollows = false
        }
    }

    // ── Geometry ──────────────────────────────────────────────────────────

    private func aspect(_ face: Face) -> CGFloat { face == .faucet ? tallAspect : 1 }

    private func framing(_ face: Face) -> Framing {
        face == .faucet ? tall : effectiveSquare
    }

    /// Where the square sits while it is following: the one inscribed in the
    /// faucet's frame. That is the same picture the glass wears, squared — what
    /// someone who only framed the tall shape was asking for.
    private var effectiveSquare: Framing {
        guard squareFollows else { return square }
        let t = rect(tall, aspect: tallAspect)
        let maxSide = min(image.size.width, image.size.height)
        return clamp(Framing(scale: maxSide / max(t.width, 1),
                             center: CGPoint(x: t.midX / max(image.size.width, 1),
                                             y: t.midY / max(image.size.height, 1))),
                     .display)
    }

    /// The rectangle a framing selects, in the source's own pixels. It may
    /// reach past them, and what lies past them is background.
    private func rect(_ f: Framing, aspect a: CGFloat) -> CGRect {
        let (w, h) = extent(f, aspect: a)
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

    private func clamp(_ f: Framing, _ face: Face) -> Framing {
        let a = aspect(face)
        var g = f
        g.scale = min(max(f.scale, minScale(a)), maxScale(face))
        let (w, h) = extent(g, aspect: a)
        g.center = CGPoint(x: bound(g.center.x * image.size.width, w, image.size.width) / max(image.size.width, 1),
                           y: bound(g.center.y * image.size.height, h, image.size.height) / max(image.size.height, 1))
        return g
    }

    /// A photograph cannot be zoomed past its own resolution: the tightest crop
    /// allowed is the one that still fills the rendition it feeds.
    private func maxScale(_ face: Face) -> CGFloat {
        let widest = min(image.size.width, image.size.height * aspect(face))
        return max(1, widest / (face == .faucet ? 172 : 240))
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

    private func fit(_ a: CGFloat, in room: CGSize) -> CGSize {
        let h = min(room.height, room.width / a)
        return CGSize(width: h * a, height: h)
    }

    // ── Back to the source's own pixels ───────────────────────────────────

    private func crop() -> ImageCrop {
        // Through UIImage once, so an EXIF-rotated camera photo is upright
        // before either rectangle is measured against it.
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        let upright = UIGraphicsImageRenderer(size: image.size, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: image.size))
        }
        return ImageCrop(portrait: cut(rect(tall, aspect: tallAspect), from: upright),
                         square: cut(rect(effectiveSquare, aspect: 1), from: upright))
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
