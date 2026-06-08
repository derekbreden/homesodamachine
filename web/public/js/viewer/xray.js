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
// files keeps the mode), and the toggle re-applies to the live group.
// Defaults to off.

import * as THREE from "three";
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
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

// base shading material -> its x-ray clone. WeakMap so a clone dies with the
// (cached) base material it shadows; one clone per base, reused across
// meshes and across loads.
const _xrayMatCache = new WeakMap();
function xrayVariant(base) {
  let m = _xrayMatCache.get(base);
  if (!m) {
    m = base.clone(); // preserves color + side (BackSide on back-face mats)
    m.transparent = true;
    m.opacity = SURFACE_OPACITY;
    m.depthWrite = false;
    _xrayMatCache.set(base, m);
  }
  return m;
}

// part color (hex) -> shared edge line material, so same-colored solids
// share one. Edges are opaque so they read crisply and anchor the depth
// buffer; the faint surfaces blend around them.
const _edgeMatCache = new Map();
function edgeMaterial(color) {
  const key = color.getHex();
  let m = _edgeMatCache.get(key);
  if (!m) {
    m = new THREE.LineBasicMaterial({ color: color.clone() });
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
  const meshes = group.children.filter((c) => c.isMesh);
  if (enabled) {
    // buildMesh adds a front + back mesh per solid sharing one geometry;
    // dedupe so each solid gets exactly one set of edges.
    const seenGeo = new Set();
    for (const mesh of meshes) {
      if (!mesh.userData.baseMaterial) mesh.userData.baseMaterial = mesh.material;
      const base = mesh.userData.baseMaterial;
      if (!seenGeo.has(mesh.geometry)) {
        seenGeo.add(mesh.geometry);
        const eg = new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG);
        const line = new THREE.LineSegments(eg, edgeMaterial(base.color));
        line.userData.isXrayEdge = true;
        group.add(line);
      }
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
