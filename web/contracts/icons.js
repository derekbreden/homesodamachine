// The site's glyph vocabulary — one table, two renderers.
//
// The server draws the shell nav and the notification rows from it
// (web/lib/icons.js, which adds the notif-icon wrapper); the browser draws the
// 3D viewer's tool rail from it (web/public/js/viewer/tool-rail.js). Both
// import this file, so a glyph is drawn the same weight wherever it appears.
//
// Feather geometry throughout: a 24×24 box, no fill, 2px round-capped strokes
// in currentColor. The viewer's rail renders these at ~15px beside a label, so
// a glyph has to hold its shape with nothing finer than about 2 units apart.

export const ICON_ATTRS =
  'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  + 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';

// Inner markup for each icon — composed by iconSvg below.
export const ICON_INNER = {
  // ── Shell nav + notification rows ──────────────────────────────────────────
  // Cube — Parts (also notification kind=step).
  cube: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
  // Bar chart — Charts (also notification kind=mermaid).
  chart: '<path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path>',
  // Play in a circle — the guided walkthrough.
  tour: '<circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon>',
  // Cog — Settings.
  gear: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
  // Bell — notification toggle.
  bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path>',
  // Scissors — notification kind=dxf.
  scissors: '<circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="20" y1="4" x2="8.12" y2="15.88"></line><line x1="14.47" y1="14.48" x2="20" y2="20"></line><line x1="8.12" y1="8.12" x2="12" y2="12"></line>',
  // Pencil — Drawings (the print sheets; also notification kind=drawing).
  pencil: '<path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>',
  // Circuit board — PCB boards (carrier viewer; also notification kind=pcb).
  cpu: '<rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line>',
  // Clipboard with a checked line — notification kind=card (assembly deck).
  clipboard: '<path d="M9 2h6a1 1 0 0 1 1 1v2H8V3a1 1 0 0 1 1-1z"></path><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><polyline points="9 14 11 16 15 12"></polyline>',
  // Generic file — notification fallback.
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline>',
  // House — Home.
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
  // Dollar sign — Cost (per-unit BOM breakdown).
  dollar: '<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
  // Open book, two leaves on a spine — Updates. Two strokes, nothing finer
  // than the gap at the spine.
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>',

  // ── The 3D viewer's tool rail ──────────────────────────────────────────────
  // Magnifier — Find: type a part name or paste pick text.
  find: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
  // Four corners closing on one solid — Reset view, the part re-framed.
  "reset-view": '<path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M16 3h3a2 2 0 0 1 2 2v3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path><path d="M8 21H5a2 2 0 0 1-2-2v-3"></path><path d="M12 8.5l3.5 3.5-3.5 3.5-3.5-3.5z"></path>',
  // Struck-through circle — the pick modes off, clicks only orbit.
  "pick-off": '<circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>',
  // The nav's own Parts cube — a click selects a whole component.
  "pick-component": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
  // One edge and its two vertices — the entity the picker returns.
  "pick-edge": '<line x1="5" y1="19" x2="19" y2="5"></line><circle cx="5" cy="19" r="2.5"></circle><circle cx="19" cy="5" r="2.5"></circle>',
  // The translate gizmo — drag a component somewhere new.
  "pick-edit": '<polyline points="5 9 2 12 5 15"></polyline><polyline points="9 5 12 2 15 5"></polyline><polyline points="9 19 12 22 15 19"></polyline><polyline points="19 9 22 12 19 15"></polyline><line x1="2" y1="12" x2="22" y2="12"></line><line x1="12" y1="2" x2="12" y2="22"></line>',
  // The eye — X-ray, the one overlay that is about seeing through rather than
  // drawing on top. A dashed shell says it more precisely and loses the dashes
  // at 15px.
  xray: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>',
  // A ticked rule — Rulers. The axis triad it draws is the truer picture and
  // reads as an abstract mark at 15px, where this reads as its own label.
  rulers: '<rect x="2" y="8" width="20" height="9" rx="2"></rect><path d="M7 8v4"></path><path d="M12 8v5"></path><path d="M17 8v4"></path>',
  // ── Disclosure ─────────────────────────────────────────────────────────────
  // A chevron, drawn pointing right and turned a quarter clockwise by whatever
  // it is on when that thing stands open — the /3d branches and the viewer's
  // readout panels. ONE MARK THAT TURNS, at the stroke weight of every other
  // glyph here: the small triangles of the box-drawing block render at their
  // own weight, which at this size is a dot.
  chevron: '<polyline points="9 18 15 12 9 6"></polyline>',
};

export function iconSvg(key, className = "") {
  const cls = className ? `class="${className}" ` : "";
  return `<svg ${cls}${ICON_ATTRS}>${ICON_INNER[key] || ICON_INNER.file}</svg>`;
}
