// X-ray render mode for the CAD viewer. A toggle (stacked above the rulers
// toggle, persisted per-browser in localStorage under "step-xray") that
// switches the loaded assembly from solid shading to a ghosted view:
// every solid's surfaces drop to a low opacity and every solid gets its
// feature edges drawn as crisp lines. The faint surfaces give bulk; the
// edges carry the structure — so you can read a part nested inside a part
// nested inside a part, which solid shading hides.
//
// Why edges + ghost rather than plain transparency: low-opacity surfaces
// alone blend into mush — you can tell *something* is in there but not
// what. Drawing each solid's feature edges (EdgesGeometry at a ~30° crease
// threshold, so the tessellation facets on curved walls stay quiet) keeps
// every part's silhouette legible through the ghost. depthWrite is off on
// the surfaces so a near shell never hides the ones stacked behind it —
// everything blends, which is the point.
//
// Materials note: the live shading materials are shared with the offscreen
// thumbnail renderer (step.js's _matCache), so we must NOT mutate them in
// place — a transparent thumbnail would leak out. Instead each mesh's
// material is swapped for a cached x-ray *clone* and the original parked on
// mesh.userData.baseMaterial, to be restored on toggle off.
//
// step.js calls applyXray() on the group after every load (so switching
// files keeps the mode) and inside renderThumbnail (so a grid card matches the
// detail view it opens). The toggle re-applies to the live detail group only.
// Every model opens solid. Turning x-ray on is remembered across models.

import { createXrayRenderer } from "./xray-render.js";
import { state } from "./state.js";
import { makeToolChip } from "./tool-rail.js";

const LS_KEY = "step-xray";
let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();
const rendering = createXrayRenderer({
  enabled,
  isMeshVisible: mesh => !(mesh.name && state.hiddenComponents?.has(mesh.name)),
});

// These exports also serve STEP thumbnails and the standalone render tools.
export const makeEdgeMaterial = params => rendering.makeEdgeMaterial(params);
export const syncEdgeResolution = renderer => rendering.syncEdgeResolution(renderer);
export const forgetEdgeMaterials = () => rendering.forgetEdgeMaterials();
export function applyXray(group, on = enabled) { rendering.apply(group, on); }
export function setMeshMaterial(group, mesh, material) {
  rendering.setMeshMaterial(group, mesh, material, enabled);
}

export function setXrayEnabled(on, { persist = true } = {}) {
  enabled = !!on;
  rendering.setEnabled(enabled);
  if (persist) {
    try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  }
  applyXray(state.currentGroup);
}

export function isXrayEnabled() {
  return enabled;
}

export function makeXrayToggle() {
  return makeToolChip({
    className: "xray-toggle",
    label: "X-ray",
    icon: "xray",
    title: "Ghost every solid's surfaces and draw its feature edges, so nested parts read through",
    read: isXrayEnabled,
    write: setXrayEnabled,
  });
}
