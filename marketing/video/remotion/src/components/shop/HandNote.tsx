import React from "react";
import { AbsoluteFill } from "remotion";
import { useCurrentFrame } from "remotion";
import { margin, shop, type } from "../../style/tokens";
import { hand } from "../../style/fonts";
import { fadeIn } from "../../motion/draw";

/** The restrained handwritten margin note, top-right. Used once per scene, if
 *  at all — the human aside in an otherwise precise drawing. */
export const HandNote: React.FC<{ text: string; at?: number; width?: number }> = ({
  text,
  at = 0,
  width = 540,
}) => {
  const frame = useCurrentFrame() - at;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          right: margin,
          top: margin + 4,
          width,
          textAlign: "right",
          transform: "rotate(-3deg)",
          transformOrigin: "top right",
          fontFamily: hand,
          color: shop.cyanSoft,
          fontSize: type.note + 10,
          lineHeight: 1.1,
          opacity: fadeIn(frame, 0, 14),
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
