/**
 * Channel design tokens — the single source of truth for the Home Soda Machine
 * series. Two worlds, one system:
 *
 *   SHOP NOTES  — the primary language. An engineering drawing brought to life:
 *                 blueprint ground, dimensioned linework, leader callouts, a
 *                 revision stamp, one weld-glow accent. Built to explain.
 *   COLD PRESS  — reserved for cold opens and hero reveals. Chilled, cinematic:
 *                 a cold void, rising carbonation, a single teal light.
 *
 * All sizes are authored in 1080p pixel space (the render is 1920×1080).
 */

export const VIDEO = { width: 1920, height: 1080, fps: 30 } as const;

/** SHOP NOTES — blueprint world (committed; not theme-reactive, it's footage). */
export const shop = {
  ground: "#0f2033", // blueprint indigo
  groundDeep: "#0b1826",
  gridLine: "#22415f",
  gridLineBold: "#2c5074",
  ink: "#eef6ff", // chalk white — titles
  cyan: "#7fd4ff", // copper linework / traces
  cyanSoft: "#a9e2ff",
  dim: "#9fc0dd", // dimension + graphite annotation
  stampLine: "#6f90ad",
  weld: "#ff8a3c", // the one warm accent — weld glow
  weldSoft: "#ffb27a",
} as const;

/** COLD PRESS — chilled cinematic world (committed). */
export const cold = {
  bg0: "#16273b",
  bg1: "#0c1622",
  bg2: "#070d16",
  teal: "#2ec5c0",
  tealLine: "#3fb9b6",
  chill: "#eafcff", // condensation white — titles
  sub: "#9fc4cc",
  amber: "#c98a3c", // cola-amber warm counterpoint
  bubble: "rgba(190,240,240,0.9)",
} as const;

/** Type scale — px at 1080p. */
export const type = {
  kicker: 26,
  title: 128,
  titleSm: 88,
  h2: 60,
  body: 34,
  note: 34,
  dimValue: 30,
  leader: 30,
  stamp: 22,
} as const;

/** Letter-spacing (px) for the tracked, uppercase mono voice. */
export const tracking = {
  kicker: 7,
  stamp: 3,
  leader: 1,
} as const;

/** Blueprint grid. */
export const grid = { size: 64, stroke: 1.2, boldEvery: 4 } as const;

/** Global frame margin (safe-area gutter). */
export const margin = 96;
