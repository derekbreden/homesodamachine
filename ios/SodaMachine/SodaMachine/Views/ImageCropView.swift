import SwiftUI

// ────────────────────────────────────────────────────────────
// Choosing what part of a photograph the machine gets.
//
// TWO CROPS COME OUT OF ONE GESTURE. The faucet fills a tall 172x320 glass and
// the enclosure wears a square card, so a photograph has to give up two
// different rectangles. Asking for two crops in a row would be answering the
// hardware's problem with the person's time — so the tall window is what is
// positioned, and the square the enclosure will take is drawn inside it while
// that happens. What both displays get is visible before either is committed.
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

                    Text("The tall frame is the faucet. The square inside it is\nwhat the front display shows.")
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

                        // The square the enclosure takes, over the tall frame
                        // the faucet takes. Both are the same gesture.
                        Rectangle()
                            .strokeBorder(Color.white.opacity(0.85), lineWidth: 1.5)
                            .frame(width: window.width, height: window.width)
                        Rectangle()
                            .strokeBorder(Color.white.opacity(0.5), lineWidth: 2)
                            .frame(width: window.width, height: window.height)
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

        // The square shares its centre, and its side is the window's width.
        let side = window.width / s
        let square = CGRect(x: portrait.midX - side / 2, y: portrait.midY - side / 2,
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
