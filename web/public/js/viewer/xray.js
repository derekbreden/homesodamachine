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
// files keeps the mode) and inside renderThumbnail (so the server-baked grid
// thumbnails match the detail view). The toggle re-applies to the live detail
// group only — grid thumbnails are static server-rendered PNGs and always
// show the x-ray look. Defaults to ON; an explicit toggle is remembered.

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { state } from "./state.js";

const LS_KEY = "step-xray";

// Surface opacity in x-ray mode. Low because the edges carry the structure;
// this just hints the solid's bulk. With depthWrite off, stacked surfaces
// all blend (no near surface hiding the ones behind it), so this multiplies
// up fast through nested parts — keep it faint.
const SURFACE_OPACITY = 0.14;

// Crease angle above which an edge is drawn. ~30° keeps real feature edges
// (hole rims, the ends of a cylinder, fillet-to-flat transitions) while
// dropping the facet-to-facet seams that tessellation leaves on curved
// walls.
const EDGE_THRESHOLD_DEG = 30;

let enabled = (() => {
  try {
    const v = localStorage.getItem(LS_KEY);
    return v === null ? true : v === "1"; // default on; respect an explicit choice
  } catch { return true; }
})();

// base shading material -> its x-ray clone. WeakMap so a clone dies with the
// (cached) base material it shadows; one clone per base, reused across
// meshes and across loads.
const _xrayMatCache = new WeakMap();
function xrayVariant(base) {
  let m = _xrayMatCache.get(base);
  if (!m) {
    m = base.clone(); // preserves color + side
    // Material.copy() carries the declared properties, not the own ones a
    // caller hung on the instance — the back-face darkening step.js injects
    // is both of those, so it comes across by hand.
    m.onBeforeCompile = base.onBeforeCompile;
    m.customProgramCacheKey = base.customProgramCacheKey;
    m.transparent = true;
    m.opacity = SURFACE_OPACITY;
    m.depthWrite = false;
    // A transparent double-sided material is drawn back pass then front pass,
    // which lays a solid's two skins over each other and blends the ghost to
    // twice its stated opacity. One pass, one skin, one SURFACE_OPACITY.
    m.forceSinglePass = true;
    _xrayMatCache.set(base, m);
  }
  return m;
}

// Edges are drawn as screen-space quads with analytic coverage, at EDGE_WIDTH
// device pixels. A GL line is one pixel wide with no partial coverage, so on a
// sub-pixel camera move it is either in a pixel or out of it: across the
// enclosure assembly's 48,000 feature-edge segments that reads as a shimmer over
// the whole frame. Against the same nudge, measured on edges alone, a hard pixel
// flip lands on 0.67% of the frame here where the GL line put it on 1.22%.
const EDGE_WIDTH = 1.4;

// Every LineMaterial ever handed out. `linewidth` is in pixels OF ITS OWN
// `resolution`, so each one has to be told the size of the buffer it is about
// to be drawn into — the live canvas, the 400×400 thumbnail, or whatever size a
// tool in tools/render/ has set. `syncEdgeResolution` is that telling, and every
// render path calls it.
const _edgeMats = new Set();
const _bufSize = new THREE.Vector2();

export function makeEdgeMaterial(params = {}) {
  const m = new LineMaterial({ linewidth: EDGE_WIDTH, alphaToCoverage: true, ...params });
  m.resolution.copy(_bufSize);
  _edgeMats.add(m);
  return m;
}

export function syncEdgeResolution(renderer) {
  renderer.getDrawingBufferSize(_bufSize);
  for (const m of _edgeMats) m.resolution.copy(_bufSize);
}

// part color (hex) -> shared edge line material, so same-colored solids
// share one. Edges are opaque so they read crisply and anchor the depth
// buffer; the faint surfaces blend around them.
const _edgeMatCache = new Map();
function edgeMaterial(color) {
  const key = color.getHex();
  let m = _edgeMatCache.get(key);
  if (!m) {
    m = makeEdgeMaterial({ color: color.clone() });
    _edgeMatCache.set(key, m);
  }
  return m;
}

function removeXrayEdges(group) {
  for (let i = group.children.length - 1; i >= 0; i--) {
    const c = group.children[i];
    if (c.userData && c.userData.isXrayEdge) {
      group.remove(c);
      if (c.geometry) c.geometry.dispose();
    }
  }
}

// Idempotent: clears any prior x-ray edges, then either swaps each mesh to
// its ghost clone and adds feature edges (when on) or restores the saved
// originals (when off). Safe to call on a null group or in either state.
export function applyXray(group) {
  if (!group) return;
  removeXrayEdges(group);
  // LineSegments2 extends Mesh, so the edges this adds would answer to isMesh
  // on the next pass. removeXrayEdges has already taken them out above; the
  // guard says so where a reader is looking at the filter.
  const meshes = group.children.filter((c) => c.isMesh && !c.userData.isXrayEdge);
  if (enabled) {
    for (const mesh of meshes) {
      if (!mesh.userData.baseMaterial) mesh.userData.baseMaterial = mesh.material;
      const base = mesh.userData.baseMaterial;
      const eg = new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG);
      const lg = new LineSegmentsGeometry().setPositions(eg.getAttribute("position").array);
      eg.dispose();
      const line = new LineSegments2(lg, edgeMaterial(base.color));
      line.userData.isXrayEdge = true;
      // Carry the component name so a locally-hidden component (component-picker.js)
      // takes its feature edges out of the ghost too — otherwise the wireframe of a
      // hidden solid keeps obstructing the view. Born hidden if already hidden, so
      // toggling x-ray on doesn't resurrect a hidden part's edges.
      line.userData.xrayComponent = mesh.name || "";
      line.visible = !(mesh.name && state.hiddenComponents && state.hiddenComponents.has(mesh.name));
      group.add(line);
      mesh.material = xrayVariant(base);
    }
  } else {
    for (const mesh of meshes) {
      if (mesh.userData.baseMaterial) mesh.material = mesh.userData.baseMaterial;
    }
  }
}

export function setXrayEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  applyXray(state.currentGroup);
}

export function isXrayEnabled() {
  return enabled;
}

export function makeXrayToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "xray-toggle";
  function refresh() {
    btn.textContent = enabled ? "X-ray: on" : "X-ray: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => {
    setXrayEnabled(!enabled);
    refresh();
  });
  refresh();
  return btn;
}
