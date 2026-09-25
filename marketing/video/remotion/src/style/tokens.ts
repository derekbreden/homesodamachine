/**
 * Channel design tokens — the single source of truth for the Home Soda Machine
 * series. Two worlds, one system:
 *
 *   SHOP NOTES  — the primary language. An engineering drawing brought to life:
 *                 blueprint ground, dimensioned linework, leader callouts, a
 *                 revision stamp, one weld-glow accent. Built to explain.
 *   COLD PRESS  — reserved for cold opens and hero reveals. Chilled, cinematic:
 *                 cobalt, rising carbonation, and ice-blue light.
 *
 * All sizes are authored in 1080p pixel space (the render is 1920×1080).
 */

export const VIDEO = { width: 1920, height: 1080, fps: 30 } as const;

/** SHOP NOTES — blueprint world (committed; not theme-reactive, it's footage). */
export const shop = {
  ground: "#1749d1",
  groundDeep: "#10319c",
  gridLine: "rgba(220,230,255,0.12)",
  gridLineBold: "rgba(220,230,255,0.22)",
  ink: "#ffffff",
  cyan: "#dce6ff",
  cyanSoft: "#ffffff",
  dim: "#dce6ff",
  stampLine: "#dce6ff",
  weld: "#ff9152",
  weldSoft: "#ffb98f",
} as const;

/** COLD PRESS — chilled cinematic world (committed). */
export const cold = {
  bg0: "#2d60e5",
  bg1: "#1749d1",
  bg2: "#1749d1",
  teal: "#dce6ff",
  tealLine: "#dce6ff",
  chill: "#ffffff",
  sub: "#dce6ff",
  amber: "#ff9152",
  bubble: "rgba(220,230,255,0.9)",
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
