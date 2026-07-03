// The board out/ layout — the render artifacts a board produces and the viewer reads.
//
// render-board.ts renders each pcb/<dir>/<name>.tsx into sibling out/ files: the copper views
// out/<name>.{top,bottom,overlay}.svg (+ out/<name>.inner<N>.svg on a multi-layer board) and
// out/<name>.picks.json (pick-data.ts, shape in hardware/pcb/pcba/picks-schema.ts). walk.js
// builds these paths when it lists boards; viewer-routes.js confines the /api/pcb-content and
// /api/pcb-picks routes to them. One definition so the naming stays in lockstep across readers.

// Outer copper views every rendered board carries. Inner planes (inner1…innerN) are discovered.
export const FIXED_VIEWS = ["top", "bottom", "overlay"];

// Root-relative artifact paths for a board directory `dir` (root-relative) and board `name`.
export function viewFile(dir, name, view) { return `${dir}/out/${name}.${view}.svg`; }
export function picksFile(dir, name) { return `${dir}/out/${name}.picks.json`; }

// Matches out/<name>.inner<N>.svg for one board — name escaped so a dotted name can't widen the
// match — capturing the plane number.
export function innerViewRe(name) {
  return new RegExp(`^${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\.inner(\\d+)\\.svg$`);
}

// Request-path confinement: a rendered board view / pick-data under some pcb/.../out/.
// Longer view names first so `top`/`bottom` can't shadow `topmask`/`bottommask`.
export const VIEW_REQUEST_RE = /(^|\/)pcb\/.+\/out\/[^/]+\.(topmask|bottommask|top|bottom|overlay|inner\d+)\.svg$/;
export const PICKS_REQUEST_RE = /(^|\/)pcb\/.+\/out\/[^/]+\.picks\.json$/;
