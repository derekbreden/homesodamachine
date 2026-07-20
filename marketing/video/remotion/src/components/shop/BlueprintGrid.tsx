import React from "react";
import { AbsoluteFill } from "remotion";
import { grid, shop, VIDEO } from "../../style/tokens";

/** The Shop Notes ground: a fine engineering grid over blueprint indigo, with a
 *  bold line every few cells and a soft vignette to seat the drawing. */
export const BlueprintGrid: React.FC = () => {
  const bold = grid.size * grid.boldEvery;
  return (
    <AbsoluteFill style={{ backgroundColor: shop.ground }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}
        preserveAspectRatio="none"
      >
        <defs>
          <pattern id="fine" width={grid.size} height={grid.size} patternUnits="userSpaceOnUse">
            <path
              d={`M ${grid.size} 0 L 0 0 0 ${grid.size}`}
              fill="none"
              stroke={shop.gridLine}
              strokeWidth={grid.stroke}
            />
          </pattern>
          <pattern id="bold" width={bold} height={bold} patternUnits="userSpaceOnUse">
            <path
              d={`M ${bold} 0 L 0 0 0 ${bold}`}
              fill="none"
              stroke={shop.gridLineBold}
              strokeWidth={grid.stroke * 1.5}
            />
          </pattern>
          <radialGradient id="vig" cx="50%" cy="45%" r="78%">
            <stop offset="52%" stopColor="rgba(0,0,0,0)" />
            <stop offset="100%" stopColor="rgba(3,8,14,0.6)" />
          </radialGradient>
        </defs>
        <rect width={VIDEO.width} height={VIDEO.height} fill="url(#fine)" />
        <rect width={VIDEO.width} height={VIDEO.height} fill="url(#bold)" />
        <rect width={VIDEO.width} height={VIDEO.height} fill="url(#vig)" />
      </svg>
    </AbsoluteFill>
  );
};
