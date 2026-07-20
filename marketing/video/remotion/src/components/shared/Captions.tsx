import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { margin, type } from "../../style/tokens";
import { grotesk } from "../../style/fonts";

export type CaptionCue = { text: string; start: number; end: number };

/**
 * Burned-in narration captions, timed to the script. Two jobs: the video reads
 * with the sound off, and — since narration is recorded later — these cues are
 * the timing guide the narrator reads against. Neutral treatment so it sits over
 * both the Cold Press and Shop Notes worlds.
 */
export const Captions: React.FC<{ cues: CaptionCue[]; fade?: number }> = ({ cues, fade = 6 }) => {
  const frame = useCurrentFrame();
  const active = cues.find((c) => frame >= c.start && frame < c.end);
  if (!active) return null;
  const inP = interpolate(frame, [active.start, active.start + fade], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const outP = interpolate(frame, [active.end - fade, active.end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(inP, outP);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center" }}>
      <div
        style={{
          opacity,
          maxWidth: 1180,
          margin: `0 ${margin}px ${margin}px`,
          padding: "18px 30px",
          borderRadius: 12,
          background: "rgba(6,12,20,0.62)",
          border: "1px solid rgba(159,196,221,0.18)",
          backdropFilter: "blur(2px)",
          fontFamily: grotesk,
          fontWeight: 600,
          fontSize: type.body,
          lineHeight: 1.25,
          color: "#eef6ff",
          textAlign: "center",
          textWrap: "balance",
        }}
      >
        {active.text}
      </div>
    </AbsoluteFill>
  );
};
