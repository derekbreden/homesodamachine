// The server's half of the glyph table. The table itself is
// contracts/icons.js, which the browser imports over HTTP for the 3D viewer's
// tool rail; this file names the shell nav's glyphs and wraps the
// notification-row ones in the class that page's CSS expects.

import { iconSvg } from "../contracts/icons.js";

// Shell nav glyphs.
export const HOME_SVG      = iconSvg("home");
export const PARTS_SVG     = iconSvg("cube");
export const GUIDES_SVG    = iconSvg("book");
export const DOLLAR_SVG    = iconSvg("dollar");
export const LATEST_SVG    = iconSvg("history");
export const BELL_SVG      = iconSvg("bell");

// Map from notification `kind` to glyph (with the notif-icon class the
// notifications page CSS expects).
const NOTIF_KIND_TO_INNER = {
  step:    "cube",
  dxf:     "scissors",
  drawing: "pencil",
  pcb:     "cpu",
  card:    "clipboard",
};

export function notifIconSvg(kind) {
  return iconSvg(NOTIF_KIND_TO_INNER[kind] || "file", "notif-icon");
}

// Every notification-kind icon as a string, suitable for JSON.stringify and
// interpolation into a client-side <script> block.
export const NOTIF_ICON_BY_KIND = {
  step:    notifIconSvg("step"),
  dxf:     notifIconSvg("dxf"),
  drawing: notifIconSvg("drawing"),
  pcb:     notifIconSvg("pcb"),
  card:    notifIconSvg("card"),
  default: notifIconSvg("default"),
};
