import React from "react";
import { AbsoluteFill } from "remotion";
import { cold } from "../../style/tokens";

/** The Cold Press ground: a chilled void with a single teal under-light and a
 *  heavy vignette. The stage for reveals. */
export const ColdField: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(120% 90% at 22% 8%, ${cold.bg0} 0%, ${cold.bg1} 46%, ${cold.bg2} 100%)`,
    }}
  >
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(60% 42% at 30% 118%, rgba(46,197,192,0.42), rgba(46,197,192,0) 70%)",
      }}
    />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(120% 120% at 50% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
      }}
    />
  </AbsoluteFill>
);
