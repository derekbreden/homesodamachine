import React from "react";
import { AbsoluteFill } from "remotion";
import { cold } from "../../style/tokens";

/** Cobalt ground with a broad ice-blue light beneath the subject. */
export const ColdField: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(120% 90% at 22% 8%, ${cold.bg0} 0%, ${cold.bg1} 46%, ${cold.bg2} 100%)`,
    }}
  >
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(60% 42% at 30% 118%, rgba(220,230,255,0.18), rgba(220,230,255,0) 70%)",
      }}
    />
  </AbsoluteFill>
);
