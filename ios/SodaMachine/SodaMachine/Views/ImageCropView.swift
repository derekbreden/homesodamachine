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
// Nothing is resampled here. This produces the two rectangles at full source
// resolution and ImageBundle does every reduction from those, once.
// ────────────────────────────────────────────────────────────

struct ImageCrop {
    let portrait: UIImage   // 172:320, for the faucet
    let square: UIImage     // 1:1, for the enclosure's card and its smaller sizes
}

struct ImageCropView: View {
    let image: UIImage
    let onUse: (ImageCrop) -> Void
    let onCancel: () -> Void

    /// Which shape the window is currently showing.
    private enum Face: Hashable { case faucet, display }

    /// Where one rectangle sits on the photograph. Scale 1 is the largest
    /// rectangle of that shape the photograph can give, so it means the same
    /// thing to both of them; centre is a fraction of the source, so it survives
    /// a change of scale and of window size.
    private struct Framing: Equatable {
        var scale: CGFloat = 1
        var center = CGPoint(x: 0.5, y: 0.5)
    }

    @State private var active: Face = .faucet
    @State private var tall = Framing()
    @State private var square = Framing()
    @State private var squareFollows = true
    /// The framing a gesture started from, so pan and pinch of the same touch
    /// are both measured against one fixed thing rather than against each other.
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
        let r = rect(framing(face), aspect: aspect(face))
        let k = size.width / max(r.width, 1)     // display points per source pixel

        return Image(uiImage: image)
            .resizable()
            .frame(width: image.size.width * k, height: image.size.height * k)
            .offset(x: (image.size.width / 2 - r.midX) * k,
                    y: (image.size.height / 2 - r.midY) * k)
            .frame(width: size.width, height: size.height)
            .clipped()
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
                    f.scale = min(max(base.scale * m, 1), maxScale(active))
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
            tall = clamp(f, aspect: tallAspect)
        case .display:
            square = clamp(f, aspect: 1)
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
        return Framing(scale: maxSide / max(t.width, 1),
                       center: CGPoint(x: t.midX / image.size.width,
                                       y: t.midY / image.size.height))
    }

    /// The rectangle a framing selects, in the source's own pixels.
    private func rect(_ f: Framing, aspect a: CGFloat) -> CGRect {
        let (w, h) = extent(f, aspect: a)
        let c = center(f, w, h)
        return CGRect(x: c.x - w / 2, y: c.y - h / 2, width: w, height: h)
    }

    private func extent(_ f: Framing, aspect a: CGFloat) -> (CGFloat, CGFloat) {
        let w = min(image.size.width, image.size.height * a) / max(f.scale, 1)
        return (w, w / a)
    }

    /// Kept inside the photograph: no crop has an edge off the picture.
    private func center(_ f: Framing, _ w: CGFloat, _ h: CGFloat) -> CGPoint {
        CGPoint(x: min(max(f.center.x * image.size.width, w / 2), image.size.width - w / 2),
                y: min(max(f.center.y * image.size.height, h / 2), image.size.height - h / 2))
    }

    private func clamp(_ f: Framing, aspect a: CGFloat) -> Framing {
        let (w, h) = extent(f, aspect: a)
        let c = center(f, w, h)
        return Framing(scale: f.scale,
                       center: CGPoint(x: c.x / image.size.width, y: c.y / image.size.height))
    }

    /// A photograph cannot be zoomed past its own resolution: the tightest crop
    /// allowed is the one that still fills the rendition it feeds.
    private func maxScale(_ face: Face) -> CGFloat {
        let a = aspect(face)
        let widest = min(image.size.width, image.size.height * a)
        return max(1, widest / (face == .faucet ? 172 : 240))
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

    /// One rectangle of the source, at full resolution.
    private func cut(_ rect: CGRect, from upright: UIImage) -> UIImage {
        guard let cg = upright.cgImage else { return image }
        let px = CGFloat(cg.width) / image.size.width
        let inPixels = CGRect(x: rect.minX * px, y: rect.minY * px,
                              width: rect.width * px, height: rect.height * px)
            .intersection(CGRect(x: 0, y: 0, width: CGFloat(cg.width), height: CGFloat(cg.height)))
        guard !inPixels.isEmpty, let cut = cg.cropping(to: inPixels) else { return image }
        return UIImage(cgImage: cut)
    }
}
