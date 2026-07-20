import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { margin, shop, tracking, type, VIDEO } from "../../style/tokens";
import { mono } from "../../style/fonts";
import { eases } from "../../motion/easings";
import { fadeIn } from "../../motion/draw";

/** The drawing title block, bottom-right. Stamps in with a touch of overshoot
 *  (pair it with the stamp-thud cue). */
export const RevisionStamp: React.FC<{
  at?: number;
  rev?: string;
  part?: string;
  sheet?: string;
}> = ({ at = 0, rev = "A", part = "PCBA", sheet = "1 / 1" }) => {
  const frame = useCurrentFrame() - at;
  const bw = 300;
  const bh = 108;
  const bx = VIDEO.width - margin - bw;
  const by = VIDEO.height - margin - bh;
  const cx = bx + bw / 2;
  const cy = by + bh / 2;

  const p = interpolate(frame, [0, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: eases.stamp,
  });
  const scale = interpolate(p, [0, 1], [1.16, 1]);
  const rot = interpolate(p, [0, 1], [-3.5, 0]);
  const opacity = fadeIn(frame, 0, 5);

  const label = { fontFamily: mono, fontSize: type.stamp, letterSpacing: tracking.stamp } as const;

  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} preserveAspectRatio="none">
        <g
          opacity={opacity}
          transform={`translate(${cx} ${cy}) scale(${scale}) rotate(${rot}) translate(${-cx} ${-cy})`}
        >
          <rect x={bx} y={by} width={bw} height={bh} fill="rgba(12,27,44,0.65)" stroke={shop.stampLine} strokeWidth={1.5} />
          <line x1={bx} y1={by + bh / 2} x2={bx + bw} y2={by + bh / 2} stroke={shop.stampLine} strokeWidth={1} />
          <line x1={bx + bw * 0.52} y1={by} x2={bx + bw * 0.52} y2={by + bh} stroke={shop.stampLine} strokeWidth={1} />
          <text x={bx + 18} y={by + 34} fill={shop.dim} {...label}>{`REV ${rev}`}</text>
          <text x={bx + bw * 0.52 + 18} y={by + 34} fill={shop.dim} {...label}>{part}</text>
          <text x={bx + 18} y={by + bh / 2 + 34} fill={shop.dim} {...label}>SHEET</text>
          <text x={bx + bw * 0.52 + 18} y={by + bh / 2 + 34} fill={shop.dim} {...label} style={{ fontVariantNumeric: "tabular-nums" }}>{sheet}</text>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
