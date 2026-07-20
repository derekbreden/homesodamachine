import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { weldPoint } from "../style/layout";
import { fadeIn } from "../motion/draw";
import { BlueprintGrid } from "../components/shop/BlueprintGrid";
import { BoardDrawing } from "../components/shop/BoardDrawing";
import { DimensionLine } from "../components/shop/DimensionLine";
import { LeaderCallout } from "../components/shop/LeaderCallout";
import { RevisionStamp } from "../components/shop/RevisionStamp";
import { Title } from "../components/shop/Title";
import { HandNote } from "../components/shop/HandNote";

/** The Shop Notes scene: the board as a living engineering drawing. Timings are
 *  local to this scene (frame 0 = the moment it takes over from the cold open),
 *  so the sequence handles the dissolve and the components just play. */
export const ShopNotesScene: React.FC = () => {
  const frame = useCurrentFrame();
  const intro = fadeIn(frame, 0, 26); // the fade half of the cross-dissolve
  return (
    <AbsoluteFill style={{ opacity: intro }}>
      <BlueprintGrid />
      <BoardDrawing at={10} />
      <DimensionLine at={40} />
      <LeaderCallout from={{ x: 924, y: 604 }} to={{ x: 1470, y: 474 }} label="0.20 mm" at={70} />
      <LeaderCallout from={{ x: 760, y: 686 }} to={{ x: 1470, y: 566 }} label="45° only" at={82} />
      <LeaderCallout from={weldPoint} to={{ x: 1200, y: 842 }} label="hand-placed" accent dot at={98} />
      <Title kicker="Episode 01 · The Board" title="By Hand" at={6} />
      <HandNote text={'every trace placed on purpose — no segment sits where it "ended up."'} at={104} />
      <RevisionStamp at={124} />
    </AbsoluteFill>
  );
};
