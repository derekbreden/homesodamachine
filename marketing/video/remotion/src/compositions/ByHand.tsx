import React from "react";
import { AbsoluteFill, Audio, Sequence } from "remotion";
import { cold } from "../style/tokens";
import { ColdOpen } from "../scenes/ColdOpen";
import { ShopNotesScene } from "../scenes/ShopNotesScene";
import { sfx } from "../sound/cues";

/**
 * "By Hand" — the demo episode opener, and the proof of the channel system:
 * a Cold Press cold open cross-dissolving into the Shop Notes drawing world.
 *
 * Timeline (30fps):
 *   0–150    Cold open: glowing board + carbonation + kicker/subtitle
 *   120–146  Cross-dissolve (Shop Notes fades up over the cold open)
 *   120–360  Shop Notes: board draws on, dimension, leader callouts, stamp
 */
export const ByHand: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: cold.bg2 }}>
      <Sequence durationInFrames={150}>
        <ColdOpen kicker="Episode 01 · The Board" sub="Routing a circuit board with no autorouter." />
      </Sequence>

      <Sequence from={120}>
        <ShopNotesScene />
      </Sequence>

      {/* sound cues */}
      <Sequence from={116}>
        <Audio src={sfx.sting} volume={0.7} />
      </Sequence>
      <Sequence from={150}>
        <Audio src={sfx.ding} volume={0.5} />
      </Sequence>
      <Sequence from={244}>
        <Audio src={sfx.stampThud} volume={0.85} />
      </Sequence>
    </AbsoluteFill>
  );
};
