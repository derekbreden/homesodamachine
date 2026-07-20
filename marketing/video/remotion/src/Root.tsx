import React from "react";
import { Composition } from "remotion";
import { ByHand } from "./compositions/ByHand";
import { VIDEO } from "./style/tokens";

/** Registered compositions. Add one per episode; they all draw on the shared
 *  Shop Notes + Cold Press system in src/components, src/style, src/motion. */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ByHand"
        component={ByHand}
        durationInFrames={360}
        fps={VIDEO.fps}
        width={VIDEO.width}
        height={VIDEO.height}
      />
    </>
  );
};
