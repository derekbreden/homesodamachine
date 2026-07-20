import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { VIDEO } from "../../style/tokens";
import { rand } from "../../motion/draw";

/** Rising carbonation — the Cold Press signature. Each bubble's position is a
 *  pure function of the frame (seeded scatter + a sine wobble), so the motion is
 *  deterministic and loops without seams. */
export const Bubbles: React.FC<{ count?: number }> = ({ count = 26 }) => {
  const frame = useCurrentFrame();
  const t = frame / VIDEO.fps;
  const H = VIDEO.height;
  const W = VIDEO.width;
  const rise = H + 260;

  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        <defs>
          <radialGradient id="bub" cx="34%" cy="30%" r="70%">
            <stop offset="0%" stopColor="rgba(200,245,245,0.95)" />
            <stop offset="60%" stopColor="rgba(120,205,205,0.28)" />
            <stop offset="72%" stopColor="rgba(120,205,205,0)" />
          </radialGradient>
        </defs>
        {Array.from({ length: count }).map((_, i) => {
          const x = rand(i, 1) * W;
          const size = 6 + rand(i, 2) * 24;
          const speed = 46 + rand(i, 3) * 82;
          const phase = rand(i, 4);
          const y = H + 60 - (((t * speed) + phase * rise) % rise);
          const prog = Math.max(0, Math.min(1, 1 - y / H));
          const op = Math.sin(prog * Math.PI) * 0.7;
          const wob = Math.sin(t * 0.8 + i) * 9;
          return <circle key={i} cx={x + wob} cy={y} r={size / 2} fill="url(#bub)" opacity={op} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};
