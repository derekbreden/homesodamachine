import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { margin, shop, tracking, type } from "../../style/tokens";
import { grotesk, mono } from "../../style/fonts";
import { eases } from "../../motion/easings";
import { fadeIn } from "../../motion/draw";

/** Shop Notes title block, top-left: a mono kicker over a heavy grotesk title
 *  that settles up into place. */
export const Title: React.FC<{ kicker: string; title: string; at?: number }> = ({
  kicker,
  title,
  at = 0,
}) => {
  const frame = useCurrentFrame() - at;
  const kO = fadeIn(frame, 0, 10);
  const tO = fadeIn(frame, 6, 12);
  const tY = interpolate(frame, [6, 26], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: eases.settle,
  });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: margin, top: margin }}>
        <div
          style={{
            fontFamily: mono,
            color: shop.cyan,
            fontSize: type.kicker,
            letterSpacing: tracking.kicker,
            textTransform: "uppercase",
            opacity: kO,
          }}
        >
          {kicker}
        </div>
        <div
          style={{
            fontFamily: grotesk,
            color: shop.ink,
            fontSize: type.title,
            fontWeight: 800,
            lineHeight: 0.98,
            letterSpacing: -1,
            marginTop: 14,
            opacity: tO,
            transform: `translateY(${tY}px)`,
          }}
        >
          {title}
        </div>
      </div>
    </AbsoluteFill>
  );
};
