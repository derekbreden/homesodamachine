import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { shop, tracking, type, VIDEO } from "../../style/tokens";
import { mono } from "../../style/fonts";
import { drawOn, fadeIn } from "../../motion/draw";

type Pt = { x: number; y: number };

/** A leader line that extends from a point on the board to a mono label. Set
 *  `accent` for the one weld-glow callout; `dot` rings the origin point. */
export const LeaderCallout: React.FC<{
  from: Pt;
  to: Pt;
  label: string;
  at?: number;
  accent?: boolean;
  dot?: boolean;
}> = ({ from, to, label, at = 0, accent = false, dot = false }) => {
  const frame = useCurrentFrame() - at;
  const color = accent ? shop.weld : shop.dim;
  const textColor = accent ? shop.weldSoft : shop.ink;
  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} preserveAspectRatio="none">
        {dot && (
          <circle
            cx={from.x}
            cy={from.y}
            r={8}
            fill="none"
            stroke={color}
            strokeWidth={2.5}
            opacity={fadeIn(frame, 0, 6)}
          />
        )}
        <path
          d={`M ${from.x} ${from.y} L ${to.x} ${to.y}`}
          fill="none"
          stroke={color}
          strokeWidth={2}
          {...drawOn(frame, { start: 2, duration: 16 })}
        />
        <text
          x={to.x + 16}
          y={to.y + type.leader * 0.34}
          fill={textColor}
          opacity={fadeIn(frame, 14, 10)}
          fontFamily={mono}
          fontSize={type.leader}
          letterSpacing={tracking.leader}
        >
          {label}
        </text>
      </svg>
    </AbsoluteFill>
  );
};
