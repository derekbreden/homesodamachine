// The site's glyph vocabulary — one table, two renderers.
//
// Shared by the navigation and the viewer’s tool rail.
//
// Feather geometry throughout: a 24×24 box, no fill, 2px round-capped strokes
// in currentColor. The viewer's rail renders these at ~15px beside a label, so
// a glyph has to hold its shape with nothing finer than about 2 units apart.

export const ICON_ATTRS =
  'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  + 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';

// Inner markup for each icon — composed by iconSvg below.
export const ICON_INNER = {
  // ── Shell nav ──────────────────────────────────────────
  // Cube for Parts.
  cube: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
  // Generic file glyph.
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline>',
  // House — Home.
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
  // Dollar sign — Cost (per-unit BOM breakdown).
  dollar: '<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
  // Open book, two leaves on a spine — Guides, and the unit page's install
  // guide. Two strokes, nothing finer than the gap at the spine.
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>',
  // A clock turned back on itself — Latest, where Changes and Updates both
  // begin: what happened lately, newest first.
  history: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l4 2"></path>',

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
  // The eye — X-ray, the one overlay that is about seeing through rather than
  // drawing on top. A dashed shell says it more precisely and loses the dashes
  // at 15px.
  xray: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>',
  // A ticked rule — Rulers. The axis triad it draws is the truer picture and
  // reads as an abstract mark at 15px, where this reads as its own label.
  rulers: '<rect x="2" y="8" width="20" height="9" rx="2"></rect><path d="M7 8v4"></path><path d="M12 8v5"></path><path d="M17 8v4"></path>',
  // Corner brackets around a point — Focus, the selection standing out from a
  // model faded around it.
  // ── Disclosure ─────────────────────────────────────────────────────────────
  // A chevron, drawn pointing right and turned a quarter clockwise by whatever
  // it is on when that thing stands open — the /3d branches and the viewer's
  // readout panels. ONE MARK THAT TURNS, at the stroke weight of every other
  // glyph here: the small triangles of the box-drawing block render at their
  // own weight, which at this size is a dot.
  chevron: '<polyline points="9 18 15 12 9 6"></polyline>',
  "arrow-right": '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>',
  "arrow-down": '<path d="M12 5v14"></path><path d="m5 12 7 7 7-7"></path>',
  "arrow-up-right": '<path d="M7 17 17 7M7 7h10v10"></path>',
  snowflake: '<path d="M12 2v20M20.66 7l-17.32 10M20.66 17 3.34 7M8 4l4 4 4-4M8 20l4-4 4 4M3 11l5.5-1.5L7 4M21 13l-5.5 1.5L17 20M3 13l5.5 1.5L7 20M21 11l-5.5-1.5L17 4"></path>',
  "glass-water": '<path d="m6 3 1.8 17.1a1 1 0 0 0 1 .9h6.4a1 1 0 0 0 1-.9L18 3Z"></path><path d="M6.5 8c2-1 3 .5 5.5.5s3.5-1.5 5.5-.5"></path>',
  droplets: '<path d="M7 3S2 8.5 2 12a5 5 0 0 0 10 0c0-3.5-5-9-5-9ZM17 8s-4 4.5-4 7.5a4 4 0 0 0 8 0C21 12.5 17 8 17 8Z"></path>',
};

export function iconSvg(key, className = "") {
  const cls = className ? `class="${className}" ` : "";
  return `<svg ${cls}${ICON_ATTRS}>${ICON_INNER[key] || ICON_INNER.file}</svg>`;
}
