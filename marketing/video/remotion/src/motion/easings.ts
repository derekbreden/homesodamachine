/**
 * Named channel eases. The motion vocabulary is deliberately small so every
 * episode moves the same way.
 */
import { Easing } from "remotion";

export const eases = {
  /** Linework drawing itself on — leader lines, dimensions, board outline. */
  drawOn: Easing.inOut(Easing.cubic),
  /** A value or element coming to rest — dimension counts, title slide. */
  settle: Easing.out(Easing.cubic),
  /** Cross-world dissolves (Cold Press → Shop Notes). Material-standard. */
  dissolve: Easing.bezier(0.4, 0.0, 0.2, 1),
  /** A stamp / reaction landing with a touch of overshoot. */
  stamp: Easing.out(Easing.back(2.2)),
} as const;
