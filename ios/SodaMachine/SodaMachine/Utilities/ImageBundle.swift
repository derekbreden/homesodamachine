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
//     2   86x160   its picker tile — the faucet's own shape, halved
//     3   60x60    its detail header
//     4  120x120   its channel button
//
// WHAT IS CROPPED IS NOT DECIDED HERE. ImageCropView takes the two rectangles
// a person positioned — one tall for the faucet, one square for the enclosure —
// and this reduces each to the sizes its board draws. A centre crop chosen by
// arithmetic would put the wrong half of most photographs on the machine.
//
// WHICH RECTANGLE A RENDITION COMES FROM IS ITS OWN SHAPE'S ANSWER, not its
// position in the list. The picker tile is tall because the picker is choosing
// what the faucet will wear, so it is cut from the faucet's window — reducing
// it from the square would make the one preview that is supposed to show the
// tall crop show the other one.

struct ImageBundle {

    /// One rendition's geometry, matching IMAGE_BUNDLE on the wire, and which
    /// of the two rectangles someone positioned it is reduced from.
    struct Size {
        let w: Int
        let h: Int
        var tall: Bool { h > w }
    }

    static let sizes: [Size] = [
        Size(w: 172, h: 320),
        Size(w: 240, h: 240),
        Size(w:  86, h: 160),
        Size(w:  60, h:  60),
        Size(w: 120, h: 120),
    ]

    static var byteCount: Int { sizes.reduce(0) { $0 + $1.w * $1.h * 2 } }

    /// Every rendition, concatenated in wire order. Nil if the crop will not
    /// draw — refused here rather than half-written into a board's flash.
    static func make(from crop: ImageCrop) -> Data? {
        var out = Data(capacity: byteCount)
        for size in sizes {
            // The tall ones are the faucet's glass and the tile that previews
            // it; the square ones are the enclosure's card and the smaller
            // faces cut from the same square.
            let source = size.tall ? crop.portrait : crop.square
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

    // ── Back the other way ────────────────────────────────────────────────
    // A picture belongs to the machine, so a phone that did not send one still
    // has to be able to show it. The same decode serves both directions: what
    // is cached at upload time is decoded out of the bundle just built, so it
    // is byte-for-byte what the board would send back if asked.
    static func decode(_ pixels: Data, _ size: Size) -> UIImage? {
        let want = size.w * size.h * 2
        guard pixels.count >= want else { return nil }
        var rgba = [UInt8](repeating: 255, count: size.w * size.h * 4)
        pixels.withUnsafeBytes { (raw: UnsafeRawBufferPointer) in
            for i in 0..<(size.w * size.h) {
                let lo = UInt16(raw[i * 2]), hi = UInt16(raw[i * 2 + 1])
                let v = lo | (hi << 8)
                // Five and six bits back up to eight, replicating the high bits
                // into the low ones so white stays white rather than near-white.
                let r = UInt8((v >> 11) & 0x1F), g = UInt8((v >> 5) & 0x3F), b = UInt8(v & 0x1F)
                rgba[i * 4]     = (r << 3) | (r >> 2)
                rgba[i * 4 + 1] = (g << 2) | (g >> 4)
                rgba[i * 4 + 2] = (b << 3) | (b >> 2)
            }
        }
        guard let ctx = CGContext(data: &rgba, width: size.w, height: size.h,
                                  bitsPerComponent: 8, bytesPerRow: size.w * 4,
                                  space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue),
              let cg = ctx.makeImage() else { return nil }
        return UIImage(cgImage: cg)
    }

    /// The face the faucet wears, out of a whole bundle.
    static func face(of bundle: Data) -> UIImage? {
        decode(bundle, sizes[0])
    }
}
