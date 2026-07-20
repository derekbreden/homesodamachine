import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { shop, tracking, type, VIDEO } from "../../style/tokens";
import { board, dimension } from "../../style/layout";
import { mono } from "../../style/fonts";
import { countTo, drawOn, fadeIn } from "../../motion/draw";

/** The overall-width dimension above the board: extension lines, the dimension
 *  line drawing across, end ticks, and a value counting up to spec. */
export const DimensionLine: React.FC<{ at?: number }> = ({ at = 0 }) => {
  const frame = useCurrentFrame() - at;
  const { x1, x2, y, value } = dimension;
  const tickO = fadeIn(frame, 16, 6);
  const labelO = fadeIn(frame, 12, 10);
  const val = countTo(frame, { start: 8, duration: 26 }, value);

  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} preserveAspectRatio="none">
        {/* extension lines up from the board edges */}
        <line x1={x1} y1={board.y - 8} x2={x1} y2={y - 6} stroke={shop.dim} strokeWidth={1.5} opacity={tickO} />
        <line x1={x2} y1={board.y - 8} x2={x2} y2={y - 6} stroke={shop.dim} strokeWidth={1.5} opacity={tickO} />
        {/* the dimension line, drawing across */}
        <line x1={x1} y1={y} x2={x2} y2={y} stroke={shop.dim} strokeWidth={2} {...drawOn(frame, { start: 0, duration: 22 })} />
        {/* end ticks */}
        <line x1={x1} y1={y - 9} x2={x1} y2={y + 9} stroke={shop.dim} strokeWidth={2} opacity={tickO} />
        <line x1={x2} y1={y - 9} x2={x2} y2={y + 9} stroke={shop.dim} strokeWidth={2} opacity={tickO} />
        {/* value */}
        <text
          x={(x1 + x2) / 2}
          y={y - 16}
          textAnchor="middle"
          fill={shop.ink}
          opacity={labelO}
          fontFamily={mono}
          fontSize={type.dimValue}
          letterSpacing={tracking.leader}
          style={{ fontVariantNumeric: "tabular-nums" }}
        >
          {val.toFixed(1)}
        </text>
      </svg>
    </AbsoluteFill>
  );
};
