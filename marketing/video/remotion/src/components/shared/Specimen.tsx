import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { eases } from "../../motion/easings";

/**
 * A CAD render presented as a glowing specimen. The source renders are pale/gold
 * wireframes on a dark-navy square; `mixBlendMode: screen` drops the navy toward
 * the dark ground so only the linework glows, and a radial mask fades the square
 * edges. Works over both Cold Press (void) and Shop Notes (blueprint) grounds.
 */
export const Specimen: React.FC<{
  src: string; // e.g. "assets/faucet/assembly.png"
  at?: number;
  size?: number; // px in 1080 space (renders are square)
  cx?: string; // center x (css), default "50%"
  cy?: string; // center y (css), default "50%"
  push?: number; // slow scale drift over the beat
  glow?: string;
  rotate?: number;
  fade?: number;
  opacity?: number;
}> = ({
  src,
  at = 0,
  size = 780,
  cx = "50%",
  cy = "50%",
  push = 0.06,
  glow = "rgba(46,197,192,0.32)",
  rotate = 0,
  fade = 18,
  opacity = 1,
}) => {
  const frame = useCurrentFrame() - at;
  const o =
    interpolate(frame, [0, fade], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: eases.dissolve,
    }) * opacity;
  const scale = interpolate(frame, [0, 150], [1, 1 + push], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const mask = "radial-gradient(circle at 50% 50%, #000 50%, transparent 76%)";
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: cx,
          top: cy,
          width: size,
          height: size,
          transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotate}deg)`,
          opacity: o,
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: "20%",
            background: `radial-gradient(circle, ${glow}, transparent 70%)`,
            filter: "blur(26px)",
          }}
        />
        <Img
          src={staticFile(src)}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "contain",
            mixBlendMode: "screen",
            WebkitMaskImage: mask,
            maskImage: mask,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
