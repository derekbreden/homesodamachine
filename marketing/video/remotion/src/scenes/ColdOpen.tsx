import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { cold, margin, tracking, type, VIDEO } from "../style/tokens";
import { pads, traces } from "../style/layout";
import { grotesk, mono } from "../style/fonts";
import { drawOn, fadeIn } from "../motion/draw";
import { ColdField } from "../components/cold/ColdField";
import { Bubbles } from "../components/cold/Bubbles";

/** Cold Press cold open: the board materializes as glowing teal linework out of
 *  a chilled void full of rising carbonation, with a mono kicker + subtitle
 *  low-left. Atmosphere and tease — the title lands later, in Shop Notes. */
export const ColdOpen: React.FC<{ kicker: string; sub: string }> = ({ kicker, sub }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <ColdField />
      <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} preserveAspectRatio="none">
        {/* Glow is faked with a soft wide halo stroke under a sharp core — no
            SVG filter (feGaussianBlur does not render in Remotion's headless
            Chromium). */}
        {traces.map((d, i) => {
          const dr = drawOn(frame, { start: 10 + i * 10, duration: 28 });
          return (
            <g key={i}>
              <path d={d} fill="none" stroke={cold.teal} strokeWidth={16} strokeLinecap="round" opacity={0.16} {...dr} />
              <path d={d} fill="none" stroke={cold.tealLine} strokeWidth={3} strokeLinecap="square" {...dr} />
            </g>
          );
        })}
        {pads.map((p, i) => {
          const o = fadeIn(frame, 42 + i * 6, 10);
          return (
            <g key={i}>
              <circle cx={p.x} cy={p.y} r={18} fill={cold.teal} opacity={o * 0.22} />
              <circle cx={p.x} cy={p.y} r={7} fill={cold.teal} opacity={o} />
            </g>
          );
        })}
      </svg>
      </AbsoluteFill>
      <Bubbles />
      <div style={{ position: "absolute", left: margin, bottom: margin }}>
        <div
          style={{
            fontFamily: mono,
            color: cold.teal,
            fontSize: type.kicker,
            letterSpacing: tracking.kicker,
            textTransform: "uppercase",
            opacity: fadeIn(frame, 24, 12),
          }}
        >
          {kicker}
        </div>
        <div
          style={{
            fontFamily: grotesk,
            color: cold.sub,
            fontSize: 40,
            marginTop: 14,
            opacity: fadeIn(frame, 36, 14),
          }}
        >
          {sub}
        </div>
      </div>
    </AbsoluteFill>
  );
};
