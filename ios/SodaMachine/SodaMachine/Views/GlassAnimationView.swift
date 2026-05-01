import SwiftUI

// ────────────────────────────────────────────────────────────
// GlassAnimationView — Animated version of AppIcon.svg.
//
// Same glass shape, liquid gradient, and highlights as the static
// SVG. Bubbles use the S3 firmware's rise/pop/respawn physics
// (from gen_animation_frames.py). No above-surface outline bubbles.
//
// All coordinates are in the SVG's 1024×1024 space, scaled at
// render time. Cycle duration matches S3 firmware (1.6s).
// ────────────────────────────────────────────────────────────

struct GlassAnimationView: View {
    private static let cycleDuration: Double = 1.6

    @State private var phase: Double = 0

    var body: some View {
        TimelineView(.animation) { timeline in
            Canvas { context, size in
                let _ = phase
                let elapsed = timeline.date.timeIntervalSinceReferenceDate
                let t = CGFloat(elapsed.truncatingRemainder(dividingBy: Self.cycleDuration) / Self.cycleDuration)
                let s = min(size.width, size.height) / 1024

                draw(context: &context, size: size, scale: s, t: t)
            }
        }
        .aspectRatio(1, contentMode: .fit)
        .onAppear {
            withAnimation(.linear(duration: 1).repeatForever(autoreverses: false)) {
                phase = 1
            }
        }
    }

    // MARK: - Constants from SVG / gen_animation_frames.py

    private static let liquidTopBase: CGFloat = 347
    private static let waveAmplitude: CGFloat = 9
    private static let bubbleBottom: CGFloat = 740
    private static let wavePoints: Int = 40
    private static let glassLeftTop: CGFloat = 310
    private static let glassRightTop: CGFloat = 714

    // 4 bubbles matching the original SVG's cx positions and radii,
    // with well-spaced phases to avoid clustering at any frame.
    // S3 has 8 but the extra 4 small ones create an ugly row at frame 0.
    private static let bubbles: [BubbleDef] = [
        BubbleDef(cx: 440, r: 42, phase: 0.0,  speed: 1, strokeOpacity: 0.2,  strokeWidth: 2.5),
        BubbleDef(cx: 580, r: 35, phase: 0.20, speed: 1, strokeOpacity: 0.2,  strokeWidth: 2.5),
        BubbleDef(cx: 500, r: 30, phase: 0.42, speed: 1, strokeOpacity: 0.18, strokeWidth: 2),
        BubbleDef(cx: 620, r: 26, phase: 0.62, speed: 1, strokeOpacity: 0.18, strokeWidth: 2),
    ]

    // MARK: - Main draw

    private func draw(context: inout GraphicsContext, size: CGSize, scale s: CGFloat, t: CGFloat) {
        let glassPath = Path { p in
            p.move(to: CGPoint(x: 310 * s, y: 247 * s))
            p.addLine(to: CGPoint(x: 340 * s, y: 747 * s))
            p.addQuadCurve(to: CGPoint(x: 380 * s, y: 777 * s), control: CGPoint(x: 345 * s, y: 777 * s))
            p.addLine(to: CGPoint(x: 644 * s, y: 777 * s))
            p.addQuadCurve(to: CGPoint(x: 684 * s, y: 747 * s), control: CGPoint(x: 679 * s, y: 777 * s))
            p.addLine(to: CGPoint(x: 714 * s, y: 247 * s))
            p.closeSubpath()
        }

        // 1. Glass body fill
        context.fill(glassPath, with: .color(.white.opacity(0.06)))

        // 2. Clipped liquid + surface + bubbles
        context.drawLayer { ctx in
            ctx.clip(to: glassPath)

            // Liquid fill with wavy top edge (matches S3 make_liquid_path)
            let waveShift = sin(t * 2 * .pi) * Self.waveAmplitude
            let liquidPath = Path { p in
                // Wavy top edge (same curve as SVG surface highlight, animated)
                p.move(to: CGPoint(x: 300 * s, y: (347 + waveShift) * s))
                p.addQuadCurve(
                    to: CGPoint(x: 512 * s, y: (352 - waveShift) * s),
                    control: CGPoint(x: 400 * s, y: (327 + waveShift) * s)
                )
                p.addQuadCurve(
                    to: CGPoint(x: 724 * s, y: (342 + waveShift) * s),
                    control: CGPoint(x: 624 * s, y: (377 - waveShift) * s)
                )
                // Down right side, across bottom, up left side
                p.addLine(to: CGPoint(x: 724 * s, y: 800 * s))
                p.addLine(to: CGPoint(x: 300 * s, y: 800 * s))
                p.closeSubpath()
            }
            let lx: CGFloat = 300 * s
            let ly: CGFloat = 327 * s  // top of wave range
            let lw: CGFloat = 424 * s
            let lh: CGFloat = 473 * s  // to bottom of liquid
            ctx.fill(liquidPath, with: .linearGradient(
                Gradient(stops: [
                    .init(color: Theme.liquidStop0, location: 0),
                    .init(color: Theme.liquidStop1, location: 0.5),
                    .init(color: Theme.liquidStop2, location: 1),
                ]),
                startPoint: CGPoint(x: lx, y: ly),
                endPoint: CGPoint(x: lx + lw, y: ly + lh)
            ))

            // Surface highlight wave (follows the same wavy edge)
            let wavePath = Path { p in
                p.move(to: CGPoint(x: 300 * s, y: (347 + waveShift) * s))
                p.addQuadCurve(
                    to: CGPoint(x: 512 * s, y: (352 - waveShift) * s),
                    control: CGPoint(x: 400 * s, y: (327 + waveShift) * s)
                )
                p.addQuadCurve(
                    to: CGPoint(x: 724 * s, y: (342 + waveShift) * s),
                    control: CGPoint(x: 624 * s, y: (377 - waveShift) * s)
                )
                p.addLine(to: CGPoint(x: 724 * s, y: (367 + waveShift) * s))
                p.addQuadCurve(
                    to: CGPoint(x: 512 * s, y: (372 - waveShift) * s),
                    control: CGPoint(x: 624 * s, y: (397 - waveShift) * s)
                )
                p.addQuadCurve(
                    to: CGPoint(x: 300 * s, y: (367 + waveShift) * s),
                    control: CGPoint(x: 400 * s, y: (347 + waveShift) * s)
                )
                p.closeSubpath()
            }
            ctx.fill(wavePath, with: .color(.white.opacity(0.12)))

            // Bubbles — S3 rise/pop/respawn physics
            for bubble in Self.bubbles {
                guard let state = bubbleState(bubble: bubble, t: t) else { continue }
                let (cx, cy, r, opacity) = state
                guard cy > 250 && cy < 780 else { continue }

                let center = CGPoint(x: cx * s, y: cy * s)
                let radius = r * s
                let rect = CGRect(x: center.x - radius, y: center.y - radius,
                                  width: radius * 2, height: radius * 2)
                let circle = Path(ellipseIn: rect)

                ctx.drawLayer { bubbleCtx in
                    bubbleCtx.opacity = Double(opacity)
                    bubbleCtx.fill(circle, with: .radialGradient(
                        Gradient(stops: [
                            .init(color: .white.opacity(0.5), location: 0),
                            .init(color: .white.opacity(0.1), location: 1),
                        ]),
                        center: center, startRadius: 0, endRadius: radius
                    ))
                    bubbleCtx.stroke(circle, with: .color(.white.opacity(bubble.strokeOpacity)),
                                     lineWidth: bubble.strokeWidth * s)
                }
            }
        }

        // 3. Glass body stroke
        context.stroke(glassPath, with: .color(.white.opacity(0.25)), lineWidth: 4 * s)

        // 4. Glass rim highlight
        let rimPath = Path { p in
            p.move(to: CGPoint(x: 310 * s, y: 247 * s))
            p.addLine(to: CGPoint(x: 714 * s, y: 247 * s))
        }
        context.stroke(rimPath, with: .color(.white.opacity(0.35)),
                       style: StrokeStyle(lineWidth: 5 * s, lineCap: .round))

        // 5. Glass left edge highlight
        let edgePath = Path { p in
            p.move(to: CGPoint(x: 314 * s, y: 257 * s))
            p.addLine(to: CGPoint(x: 342 * s, y: 737 * s))
        }
        context.stroke(edgePath, with: .color(.white.opacity(0.1)),
                       style: StrokeStyle(lineWidth: 8 * s, lineCap: .round))

        // 6. Glass surface highlight overlay
        context.fill(glassPath, with: .linearGradient(
            Gradient(stops: [
                .init(color: .white.opacity(0.15), location: 0),
                .init(color: .white.opacity(0), location: 0.4),
            ]),
            startPoint: CGPoint(x: 310 * s, y: 0),
            endPoint: CGPoint(x: 714 * s, y: 0)
        ))
    }

    // MARK: - Bubble physics (ported from gen_animation_frames.py)

    private func bubbleState(bubble: BubbleDef, t: CGFloat) -> (CGFloat, CGFloat, CGFloat, CGFloat)? {
        let bt = (t * CGFloat(bubble.speed) + bubble.phase).truncatingRemainder(dividingBy: 1.0)

        let r = bubble.r
        let bubbleTop = Self.liquidTopBase + r + Self.waveAmplitude

        if bt < 0.75 {
            // Rising phase: bottom to surface with ease-out
            let riseT = bt / 0.75
            let easeT: CGFloat = 1 - pow(1 - riseT, 1.5)
            let cy = Self.bubbleBottom - easeT * (Self.bubbleBottom - bubbleTop)
            let cx = bubble.cx + 8 * sin(riseT * .pi * 3 + bubble.phase * 10)
            let growR = r * (1.0 + riseT * 0.15)
            return (cx, cy, growR, 0.8)
        } else if bt < 0.85 {
            // Popping phase: at surface, shrinking and fading
            let popT = (bt - 0.75) / 0.10
            let cy = bubbleTop
            let cx = bubble.cx
            let opacity: CGFloat = 0.8 * (1 - popT)
            let popR = r * (1.15 - popT * 0.5)
            return (cx, cy, popR, opacity)
        } else {
            return nil  // invisible during respawn delay
        }
    }
}

private struct BubbleDef {
    let cx: CGFloat
    let r: CGFloat
    let phase: CGFloat
    let speed: Int
    let strokeOpacity: Double
    let strokeWidth: CGFloat
}
