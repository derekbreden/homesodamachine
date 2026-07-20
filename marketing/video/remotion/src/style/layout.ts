/**
 * Shared drawing geometry for the "By Hand" board scene, authored in 1080p
 * space. Kept in one place so the board, its dimensions, and its leader
 * callouts all reference the same coordinates (a leader that points 3px off the
 * pad is the exact "amateur" tell the board itself is engineered to avoid).
 *
 * A later increment swaps this hand-authored stand-in for geometry parsed from
 * hardware/pcb/pcba/out/pcba.circuit.json — same components, real board.
 */
export const board = {
  x: 580,
  y: 372,
  w: 760,
  h: 420,
  rx: 22,
  holeR: 12,
} as const;

export const holes = [
  { x: 638, y: 430 },
  { x: 1282, y: 430 },
  { x: 638, y: 734 },
  { x: 1282, y: 734 },
] as const;

export const pads = [
  { x: 760, y: 600 },
  { x: 1020, y: 560 },
] as const;

export const traces = [
  "M 760 600 L 760 686 L 924 686 L 924 604",
  "M 1020 560 L 1020 650 L 1188 650",
  "M 852 560 L 852 720 L 1092 720",
] as const;

/** The horizontal overall-width dimension above the board. */
export const dimension = {
  y: board.y - 56,
  x1: board.x,
  x2: board.x + board.w,
  value: 84.0,
} as const;

/** The one point that earns the weld-glow accent. */
export const weldPoint = { x: 1092, y: 720 } as const;
