import SwiftUI

// ────────────────────────────────────────────────────────────
// Choosing what part of a photograph the machine gets.
//
// TWO CROPS COME OUT OF ONE GESTURE, AND THEN THE SECOND ONE MOVES. The faucet
// fills a tall 172x320 glass and the enclosure wears a square card, so a
// photograph has to give up two different rectangles. Asking for two crops in a
// row would be answering the hardware's problem with someone's time — so the
// tall window is positioned first, and the square the enclosure takes rides
// inside it on a handle of its own.
//
// It has to move independently, because the two rectangles want different
// things out of the same photograph. A face centred for the tall glass sits
// near its top; the square that flatters it is not the square in the middle.
// Both are visible the whole time, and neither is committed until both look
// right.
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

    @State private var scale: CGFloat = 1
    @State private var committedScale: CGFloat = 1
    @State private var offset: CGSize = .zero
    @State private var committedOffset: CGSize = .zero
    // Where the enclosure's square sits inside the faucet's frame, as the
    // fraction of its travel from top to bottom. Centred until someone moves it.
    @State private var squarePos: CGFloat = 0.5
    @State private var committedSquarePos: CGFloat = 0.5

    private let aspect: CGFloat = 172.0 / 320.0

    var body: some View {
        GeometryReader { geo in
            // The window is as tall as will fit with room for the controls, and
            // as wide as the faucet's aspect makes it.
            let wh = min(geo.size.height - 210, geo.size.width / aspect)
            let ww = wh * aspect
            let window = CGSize(width: ww, height: wh)

            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    Text("Position your picture")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                        .padding(.top, 24)

                    Text("The tall frame is the faucet. Drag the handle to choose\nwhat the front display shows.")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.top, 6)

                    Spacer(minLength: 12)

                    ZStack {
                        Image(uiImage: image)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: baseW(window), height: baseH(window))
                            .scaleEffect(scale)
                            .offset(offset)
                            .frame(width: window.width, height: window.height)
                            .clipped()

                        // Everything the enclosure will not see, dimmed. The
                        // square reads as the second picture rather than as a
                        // line drawn over the first.
                        Color.black.opacity(0.42)
                            .mask(
                                ZStack {
                                    Rectangle()
                                    Rectangle()
                                        .frame(width: window.width, height: window.width)
                                        .offset(y: squareOffset(window))
                                        .blendMode(.destinationOut)
                                }
                                .compositingGroup()
                            )
                            .allowsHitTesting(false)

                        Rectangle()
                            .strokeBorder(Color.white.opacity(0.9), lineWidth: 1.5)
                            .frame(width: window.width, height: window.width)
                            .offset(y: squareOffset(window))
                            .allowsHitTesting(false)

                        // The handle that moves it. Everything outside the
                        // handle pans the photograph, so the two gestures never
                        // have to guess which one was meant.
                        Capsule()
                            .fill(Color.white.opacity(0.95))
                            .frame(width: 44, height: 5)
                            .shadow(radius: 3)
                            .offset(y: squareOffset(window) + window.width / 2 - 3)
                            .contentShape(Rectangle().inset(by: -22))
                            .gesture(
                                DragGesture()
                                    .onChanged { v in
                                        squarePos = clampPos(committedSquarePos
                                            + v.translation.height / max(1, travel(window)))
                                    }
                                    .onEnded { _ in committedSquarePos = squarePos }
                            )

                        Rectangle()
                            .strokeBorder(Color.white.opacity(0.55), lineWidth: 2)
                            .frame(width: window.width, height: window.height)
                            .allowsHitTesting(false)
                    }
                    .frame(width: window.width, height: window.height)
                    .contentShape(Rectangle())
                    .gesture(
                        SimultaneousGesture(
                            DragGesture()
                                .onChanged { v in
                                    offset = CGSize(width: committedOffset.width + v.translation.width,
                                                    height: committedOffset.height + v.translation.height)
                                }
                                .onEnded { _ in committedOffset = clamped(offset, window) ; offset = committedOffset },
                            MagnificationGesture()
                                .onChanged { m in scale = max(1, committedScale * m) }
                                .onEnded { _ in
                                    committedScale = max(1, scale)
                                    scale = committedScale
                                    committedOffset = clamped(offset, window)
                                    offset = committedOffset
                                }
                        )
                    )

                    Spacer(minLength: 12)

                    HStack(spacing: 12) {
                        Button("Cancel", action: onCancel)
                            .font(.system(size: 16))
                            .foregroundStyle(Theme.textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)

                        Button("Use This") { onUse(crop(window)) }
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(Theme.textPrimary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.white.opacity(0.12))
                            .cornerRadius(12)
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 28)
                }
            }
        }
    }

    /// How far the square can travel inside the frame, in points.
    private func travel(_ window: CGSize) -> CGFloat { window.height - window.width }

    /// Its centre, measured from the frame's centre.
    private func squareOffset(_ window: CGSize) -> CGFloat {
        (squarePos - 0.5) * travel(window)
    }

    private func clampPos(_ v: CGFloat) -> CGFloat { min(max(v, 0), 1) }

    // ── The displayed geometry ────────────────────────────────────────────
    // Aspect-fill against the window, which is the smallest scale that leaves
    // no gap. Everything below is measured from it.
    private func fill(_ window: CGSize) -> CGFloat {
        max(window.width / image.size.width, window.height / image.size.height)
    }
    private func baseW(_ window: CGSize) -> CGFloat { image.size.width * fill(window) }
    private func baseH(_ window: CGSize) -> CGFloat { image.size.height * fill(window) }

    /// Keep the window covered: the picture cannot be dragged off its own edge.
    private func clamped(_ o: CGSize, _ window: CGSize) -> CGSize {
        let w = baseW(window) * scale, h = baseH(window) * scale
        let slackX = max(0, (w - window.width) / 2)
        let slackY = max(0, (h - window.height) / 2)
        return CGSize(width: min(max(o.width, -slackX), slackX),
                      height: min(max(o.height, -slackY), slackY))
    }

    // ── Back to the source's own pixels ───────────────────────────────────
    private func crop(_ window: CGSize) -> ImageCrop {
        let s = fill(window) * scale                    // source px -> display px
        let o = clamped(offset, window)

        // The window's top-left, in the source's pixels.
        let x = (image.size.width  * s / 2 - window.width  / 2 - o.width)  / s
        let y = (image.size.height * s / 2 - window.height / 2 - o.height) / s
        let portrait = CGRect(x: x, y: y, width: window.width / s, height: window.height / s)

        // The square is where it was left, not where the middle is.
        let side = window.width / s
        let square = CGRect(x: portrait.midX - side / 2,
                            y: portrait.minY + (portrait.height - side) * squarePos,
                            width: side, height: side)

        return ImageCrop(portrait: cut(portrait), square: cut(square))
    }

    /// One rectangle of the source, upright and at full resolution.
    private func cut(_ rect: CGRect) -> UIImage {
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true

        // Through UIImage once, so an EXIF-rotated camera photo is upright
        // before anything is measured against it.
        let upright = UIGraphicsImageRenderer(size: image.size, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: image.size))
        }
        guard let cg = upright.cgImage else { return image }

        let px = CGFloat(cg.width) / image.size.width
        let inPixels = CGRect(x: rect.minX * px, y: rect.minY * px,
                              width: rect.width * px, height: rect.height * px)
            .intersection(CGRect(x: 0, y: 0, width: CGFloat(cg.width), height: CGFloat(cg.height)))
        guard !inPixels.isEmpty, let cut = cg.cropping(to: inPixels) else { return image }
        return UIImage(cgImage: cut)
    }
}
