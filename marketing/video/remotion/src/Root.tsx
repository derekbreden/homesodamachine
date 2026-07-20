import React from "react";
import { Composition } from "remotion";
import { ByHand } from "./compositions/ByHand";
import { SeamTwoJobs, SEAM_DURATION } from "./compositions/SeamTwoJobs";
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
      <Composition
        id="SeamTwoJobs"
        component={SeamTwoJobs}
        durationInFrames={SEAM_DURATION}
        fps={VIDEO.fps}
        width={VIDEO.width}
        height={VIDEO.height}
      />
    </>
  );
};
