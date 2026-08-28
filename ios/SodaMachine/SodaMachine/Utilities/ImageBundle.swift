import UIKit

// ════════════════════════════════════════════════════════════
//  A picture, in the pixels the machine's panels already draw
// ════════════════════════════════════════════════════════════
//
// THE PHONE DOES ALL OF THIS, AND THAT IS THE POINT. A board that receives
// RGB565 at exactly the size it draws needs no decoder, no scaler and no
// working buffer: it writes what arrives straight into flash and hands LVGL a
// pointer into it. Every cost of turning a photograph into a face is paid once,
// here, on the device that has a real image pipeline and a battery.
//
// So a picture crossing BLE is a bundle: every size either glass wears it at,
// each resampled from the original rather than zoomed from one another, in the
// order IMAGE_BUNDLE names in firmware/lib/proto_link/proto_msg.h.
//
//     0  172x320   the faucet, filling its whole glass
//     1  240x240   the enclosure's card
//     2   96x96    its picker thumb
//     3   60x60    its detail header
//     4  120x120   its channel button
//
// WHAT IS CROPPED IS NOT DECIDED HERE. ImageCropView takes the two rectangles
// a person positioned — one tall for the faucet, one square for the enclosure —
// and this reduces each to the sizes its board draws. A centre crop chosen by
// arithmetic would put the wrong half of most photographs on the machine.

struct ImageBundle {

    /// One rendition's geometry, matching IMAGE_BUNDLE on the wire.
    struct Size {
        let w: Int
        let h: Int
    }

    static let sizes: [Size] = [
        Size(w: 172, h: 320),
        Size(w: 240, h: 240),
        Size(w:  96, h:  96),
        Size(w:  60, h:  60),
        Size(w: 120, h: 120),
    ]

    static var byteCount: Int { sizes.reduce(0) { $0 + $1.w * $1.h * 2 } }

    /// Every rendition, concatenated in wire order. Nil if the crop will not
    /// draw — refused here rather than half-written into a board's flash.
    static func make(from crop: ImageCrop) -> Data? {
        var out = Data(capacity: byteCount)
        for (i, size) in sizes.enumerated() {
            // Index 0 is the faucet's tall glass; the rest are the enclosure's
            // square card and the smaller faces cut from the same square.
            let source = (i == 0) ? crop.portrait : crop.square
            guard let scaled = resize(source, to: size),
                  let pixels = rgb565(scaled, w: size.w, h: size.h) else { return nil }
            out.append(pixels)
        }
        return out.count == byteCount ? out : nil
    }

    /// What the faucet will actually show, for the app to put beside the
    /// picture someone chose — the same reduction, so the preview is the
    /// result rather than an impression of it.
    static func preview(from crop: ImageCrop) -> UIImage? {
        resize(crop.portrait, to: sizes[0]).map { UIImage(cgImage: $0) }
    }

    // ── Reduction ─────────────────────────────────────────────────────────
    // The rectangle already has the right aspect, so this only makes it small.
    private static func resize(_ image: UIImage, to size: Size) -> CGImage? {
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        let target = CGSize(width: size.w, height: size.h)
        return UIGraphicsImageRenderer(size: target, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: target))
        }.cgImage
    }

    // ── 8:8:8 down to 5:6:5 ───────────────────────────────────────────────
    // Ordered dither, because a sky or a gradient quantised flat to five bits
    // bands visibly, and these are photographs on a lit panel a foot from
    // someone's face. The 4x4 matrix is cheap, deterministic, and leaves a
    // solid colour solid.
    private static let bayer4: [[Int]] = [
        [ 0,  8,  2, 10],
        [12,  4, 14,  6],
        [ 3, 11,  1,  9],
        [15,  7, 13,  5],
    ]

    private static func rgb565(_ cg: CGImage, w: Int, h: Int) -> Data? {
        var rgba = [UInt8](repeating: 0, count: w * h * 4)
        guard let ctx = CGContext(data: &rgba, width: w, height: h,
                                  bitsPerComponent: 8, bytesPerRow: w * 4,
                                  space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)
        else { return nil }
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))

        var out = Data(capacity: w * h * 2)
        for y in 0..<h {
            for x in 0..<w {
                let i = (y * w + x) * 4
                // Scaled per channel by the width of the gap that channel is
                // being quantised across: three bits lost on red and blue,
                // two on green.
                let t = bayer4[y & 3][x & 3]
                let r = clamp(Int(rgba[i])     + (t / 2) - 4)
                let g = clamp(Int(rgba[i + 1]) + (t / 4) - 2)
                let b = clamp(Int(rgba[i + 2]) + (t / 2) - 4)
                let v = UInt16((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
                out.append(UInt8(v & 0xFF))          // little-endian, as the panel reads it
                out.append(UInt8((v >> 8) & 0xFF))
            }
        }
        return out
    }

    private static func clamp(_ v: Int) -> Int { v < 0 ? 0 : (v > 255 ? 255 : v) }
}
