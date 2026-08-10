// Feather-style SVG icons used in two places that previously held
// independent copies of the same glyphs:
//   - lib/shell.js nav (PARTS_SVG, CHARTS_SVG, DRAWINGS_SVG, GEAR_SVG, BELL_SVG)
//   - lib/notifications.js inline-JS iconSvg(kind) per-row glyphs
// Bare glyphs live here as <svg> strings; notifIconSvg adds the
// notif-icon class. Either way, the source of truth is one file.

const ATTRS = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';

// Inner markup for each icon — composed by the exports below.
const INNER = {
  // Cube — Parts (also notification kind=step).
  cube: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
  // Bar chart — Charts (also notification kind=mermaid).
  chart: '<path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path>',
  // Cog — Settings.
  gear: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
  // Bell — notification toggle.
  bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path>',
  // Scissors — notification kind=dxf.
  scissors: '<circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="20" y1="4" x2="8.12" y2="15.88"></line><line x1="14.47" y1="14.48" x2="20" y2="20"></line><line x1="8.12" y1="8.12" x2="12" y2="12"></line>',
  // Newspaper — notification kind=post.
  newspaper: '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"></path>',
  // Pencil — Drawings (line-art SVGs; also notification kind=drawing).
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
  // Trunk with two branches — Build (the assembly tree). One node at the top,
  // two beneath it, which is the whole claim the page makes: things run beside
  // each other.
  tree: '<rect x="9" y="2" width="6" height="5" rx="1"></rect><rect x="2" y="17" width="6" height="5" rx="1"></rect><rect x="16" y="17" width="6" height="5" rx="1"></rect><path d="M12 7v4"></path><path d="M5 17v-2a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2"></path>',
};

function svg(innerKey, className = "") {
  const cls = className ? `class="${className}" ` : "";
  return `<svg ${cls}${ATTRS}>${INNER[innerKey]}</svg>`;
}

// Shell nav glyphs.
export const HOME_SVG      = svg("home");
export const UPDATES_SVG   = svg("newspaper");
export const PARTS_SVG     = svg("cube");
export const CHARTS_SVG    = svg("chart");
export const DRAWINGS_SVG  = svg("pencil");
export const PCB_SVG       = svg("cpu");
export const DOLLAR_SVG    = svg("dollar");
export const TREE_SVG      = svg("tree");
export const GEAR_SVG      = svg("gear");
export const BELL_SVG      = svg("bell");

// Map from notification `kind` to feather glyph (with the notif-icon
// class the notifications page CSS expects).
const NOTIF_KIND_TO_INNER = {
  step:    "cube",
  dxf:     "scissors",
  mermaid: "chart",
  drawing: "pencil",
  pcb:     "cpu",
  card:    "clipboard",
  post:    "newspaper",
};

export function notifIconSvg(kind) {
  return svg(NOTIF_KIND_TO_INNER[kind] || "file", "notif-icon");
}

// Map of every notification-kind icon as a string, suitable for
// JSON.stringify and interpolation into a client-side <script> block.
export const NOTIF_ICON_BY_KIND = {
  step:    notifIconSvg("step"),
  dxf:     notifIconSvg("dxf"),
  mermaid: notifIconSvg("mermaid"),
  drawing: notifIconSvg("drawing"),
  pcb:     notifIconSvg("pcb"),
  card:    notifIconSvg("card"),
  post:    notifIconSvg("post"),
  default: notifIconSvg("default"),
};
