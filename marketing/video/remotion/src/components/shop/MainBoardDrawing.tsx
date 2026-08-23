import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { shop, VIDEO } from "../../style/tokens";
import { board, holes, pads, traces } from "../../style/layout";
import { drawOn, fadeIn } from "../../motion/draw";

/** The board itself, drawing on like a pen on a drawing: panel → outline →
 *  mounting holes → traces → pads. Every stroke is frame-deterministic. */
export const BoardDrawing: React.FC<{ at?: number }> = ({ at = 0 }) => {
  const frame = useCurrentFrame() - at;
  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} preserveAspectRatio="none">
        {/* panel fill, fading in behind the outline */}
        <rect
          x={board.x}
          y={board.y}
          width={board.w}
          height={board.h}
          rx={board.rx}
          fill="rgba(12,27,44,0.6)"
          opacity={fadeIn(frame, 16, 12)}
        />
        {/* outline */}
        <rect
          x={board.x}
          y={board.y}
          width={board.w}
          height={board.h}
          rx={board.rx}
          fill="none"
          stroke={shop.ink}
          strokeWidth={3}
          {...drawOn(frame, { start: 0, duration: 26 })}
        />
        {/* mounting holes */}
        {holes.map((h, i) => (
          <circle
            key={i}
            cx={h.x}
            cy={h.y}
            r={board.holeR}
            fill="none"
            stroke={shop.ink}
            strokeWidth={2.5}
            {...drawOn(frame, { start: 20 + i * 3, duration: 12 })}
          />
        ))}
        {/* traces */}
        {traces.map((d, i) => (
          <path
            key={i}
            d={d}
            fill="none"
            stroke={shop.cyan}
            strokeWidth={3}
            strokeLinecap="square"
            {...drawOn(frame, { start: 30 + i * 8, duration: 22 })}
          />
        ))}
        {/* pads */}
        {pads.map((p, i) => (
          <rect
            key={i}
            x={p.x - 11}
            y={p.y - 11}
            width={22}
            height={22}
            rx={3}
            fill={shop.cyan}
            opacity={fadeIn(frame, 46 + i * 6, 8)}
          />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
