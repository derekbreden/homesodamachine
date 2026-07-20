/**
 * Frame-deterministic motion helpers. Everything here is a pure function of the
 * current frame — the requirement Remotion places on all animation.
 */
import { interpolate } from "remotion";
import { eases } from "./easings";

export type Cue = { start: number; duration: number };

/**
 * Draw an SVG stroke on across a frame range using the `pathLength={1}`
 * normalization trick, so it works on any stroked element (path / line /
 * polyline / rect / circle) with no geometry measurement. Spread the result
 * onto the element.
 */
export function drawOn(
  frame: number,
  { start, duration }: Cue,
  easing = eases.drawOn,
) {
  const p = interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });
  return { pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - p } as const;
}

/** Clamped fade-in. */
export function fadeIn(frame: number, start: number, duration: number) {
  return interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

/** Fade in → hold → fade out, all in frames. */
export function fadeInOut(
  frame: number,
  start: number,
  inDur: number,
  hold: number,
  outDur: number,
) {
  return interpolate(
    frame,
    [start, start + inDur, start + inDur + hold, start + inDur + hold + outDur],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
}

/** A number counting up to `to` across a range, with the settle ease. */
export function countTo(
  frame: number,
  { start, duration }: Cue,
  to: number,
) {
  return interpolate(frame, [start, start + duration], [0, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: eases.settle,
  });
}

/** Cheap deterministic hash → [0,1). Seeded 2D noise for particle scatter. */
export function rand(i: number, salt: number) {
  const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
  return x - Math.floor(x);
}
