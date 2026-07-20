/**
 * The channel sound kit. Points at the existing SFX library shared with the
 * footage pipeline (marketing/video/sfx/), exposed to Remotion through
 * public/sfx (a symlink). Replace these v1 placeholders with curated cues as
 * specific moments start to matter — the keys here stay stable.
 */
import { staticFile } from "remotion";

export const sfx = {
  /** Under the Cold Press → Shop Notes dissolve. */
  sting: staticFile("sfx/sting.wav"),
  /** A soft transient as the board resolves / a leader lands. */
  ding: staticFile("sfx/ding.wav"),
  /** The revision stamp landing. */
  stampThud: staticFile("sfx/stamp-thud.wav"),
  /** A dimension tick / small UI accent. */
  click: staticFile("sfx/click.wav"),
  /** Motion whoosh for larger moves. */
  whoosh: staticFile("sfx/whoosh.wav"),
} as const;
