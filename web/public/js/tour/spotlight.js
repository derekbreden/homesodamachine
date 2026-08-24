// THREE TIERS OF LIGHT, SO THE READER IS NEVER LOST ON THE LINE.
//
//   path    every body the water touches, faint, on screen the whole tour.
//           The map, always present, so a close-up is always read against
//           the whole run rather than floating on its own.
//   trail   the legs already crossed, brighter than the map.
//           Where we have been.
//   active  the leg on screen now: bright cyan feature edges and a thin
//           shell over the solid. Where we are.
//
// The map and the trail share one hue and the active leg takes another, so
// "the line" and "here, now" are told apart at a glance rather than by
// brightness alone.
//
// OVERLAY ONLY. The bodies' own materials are never touched, so this composes
// with the x-ray ghost the model is drawn in and clears without restoring
// anything. Everything is drawn with depth testing off, which is what lets a
// fitting buried three bodies deep read through the cabinet wall.
//
// The layers hang off the MODEL GROUP rather than off the scene, so a model
// that stands in the machine under a transform (the cold core, turned a
// quarter and seated) carries its highlights with it.

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { makeEdgeMaterial } from "../viewer/xray.js";

const EDGE_THRESHOLD_DEG = 30;

const PATH_HUE = 0x4d8dff;   // the line, and everything it has already crossed
const ACTIVE_HUE = 0x35e0d0; // the same cyan the parts viewer highlights with

// One material per tier, made once. LineMaterial widths are in pixels of a
// stated resolution, and scene.js's animate loop re-states that resolution
// every frame for every material makeEdgeMaterial has handed out — so these
// have to be made through it, and made once.
const MATS = {
  path: makeEdgeMaterial({
    color: new THREE.Color(PATH_HUE), linewidth: 1.6,
    transparent: true, opacity: 0.20, depthTest: false, depthWrite: false,
  }),
  trail: makeEdgeMaterial({
    color: new THREE.Color(PATH_HUE), linewidth: 2.2,
    transparent: true, opacity: 0.5, depthTest: false, depthWrite: false,
  }),
  out: makeEdgeMaterial({
    color: new THREE.Color(ACTIVE_HUE), linewidth: 3.0,
    transparent: true, opacity: 0.0, depthTest: false, depthWrite: false,
  }),
  active: makeEdgeMaterial({
    color: new THREE.Color(ACTIVE_HUE), linewidth: 3.0,
    transparent: true, opacity: 0.0, depthTest: false, depthWrite: false,
  }),
};

const SHELL = new THREE.MeshBasicMaterial({
  color: ACTIVE_HUE, transparent: true, opacity: 0.0,
  side: THREE.DoubleSide, depthWrite: false, depthTest: false,
});

const BASE_OPACITY = { path: 0.20, trail: 0.5, out: 0.9, active: 0.9 };
const SHELL_OPACITY = 0.15;

// A BODY BIG ENOUGH TO BE THE VIEW DOES NOT GET THE FILL. The shell reads as
// "this one" over a fitting; over the foam block, which is a third of the
// machine, it is a wash of colour across the frame that hides the run it was
// meant to point at. Past this fraction of the model's own radius a body keeps
// its bright edges and gives up its fill.
const SHELL_MAX_FRACTION = 0.24;

// Fat-line geometry per solid geometry, built the first time a tier asks for
// it and reused by every tier after — the same body is in the map, then in the
// active leg, then in the trail, and rebuilding its edges each time is the one
// expensive thing here.
let edgeCache = new WeakMap();
// The same geometries, in a list we can walk — a fat-line buffer is a GL
// allocation and lives until it is disposed, not until it is unreachable.
let edgeMade = [];

let root = null;      // our group, parented to the model group
let hostGroup = null; // the model group it hangs off
let modelRadius = 0;  // and how big it is, for the fill cutoff
const layers = {};    // tier -> { group, sig }

function edgesFor(geometry) {
  let g = edgeCache.get(geometry);
  if (!g) {
    const eg = new THREE.EdgesGeometry(geometry, EDGE_THRESHOLD_DEG);
    g = new LineSegmentsGeometry().setPositions(eg.getAttribute("position").array);
    eg.dispose();
    edgeCache.set(geometry, g);
    edgeMade.push(g);
  }
  return g;
}

/** Point the spotlight at a freshly mounted model. Everything drawn for the
 *  previous one is dropped; the edge cache is keyed by geometry, and the old
 *  geometries are gone with the old group. */
export function attach(group) {
  if (root && root.parent) root.parent.remove(root);
  for (const k of Object.keys(layers)) delete layers[k];
  for (const g of edgeMade) g.dispose();
  edgeMade = [];
  edgeCache = new WeakMap();
  hostGroup = group || null;
  if (!hostGroup) { root = null; modelRadius = 0; return; }
  modelRadius = new THREE.Box3().setFromObject(hostGroup)
    .getBoundingSphere(new THREE.Sphere()).radius || 0;
  root = new THREE.Group();
  root.name = "tour-spotlight";
  root.renderOrder = 990;
  hostGroup.add(root);
  for (const tier of ["path", "trail", "out", "active"]) {
    const g = new THREE.Group();
    g.renderOrder = tier === "path" ? 991 : tier === "trail" ? 992 : 994;
    root.add(g);
    layers[tier] = { group: g, sig: null };
  }
}

function bodiesNamed(names) {
  const want = names instanceof Set ? names : new Set(names || []);
  const out = [];
  const seen = new Set();
  if (!hostGroup || !want.size) return out;
  for (const m of hostGroup.children) {
    if (!m.isMesh || m.userData.isXrayEdge) continue;
    if (!m.name || !want.has(m.name)) continue;
    // A BODY TAKEN OUT OF THE VIEW STAYS OUT. Everything here draws with depth
    // testing off, so a highlight over a hidden solid is not faint — it is a
    // bright wireframe of a thing that is not on screen, floating over whatever
    // replaced it. That is the ordinary case once a beat isolates a
    // sub-assembly (component-picker.js isolateComponent): the run leading up
    // to the core is hidden while the core is being shown, and the map tier
    // would otherwise draw the whole water path across the inside of the
    // vessel.
    if (m.visible === false) continue;
    if (seen.has(m.geometry)) continue; // one highlight per solid
    seen.add(m.geometry);
    out.push(m);
  }
  return out;
}

/** Fill one tier with the named bodies. A tier already showing exactly these
 *  is left alone — the sets change once per step and the frames in between
 *  only move opacity. */
const _sphere = new THREE.Sphere();
function fillable(mesh) {
  if (!modelRadius) return true;
  if (!mesh.geometry.boundingSphere) mesh.geometry.computeBoundingSphere();
  return mesh.geometry.boundingSphere.radius <= modelRadius * SHELL_MAX_FRACTION;
}

function fill(tier, names, withShell) {
  const layer = layers[tier];
  if (!layer) return;
  const list = [...(names instanceof Set ? names : new Set(names || []))].sort();
  const sig = list.join("|");
  if (sig === layer.sig) return;
  layer.sig = sig;
  for (const c of [...layer.group.children]) layer.group.remove(c);
  for (const mesh of bodiesNamed(list)) {
    layer.group.add(new LineSegments2(edgesFor(mesh.geometry), MATS[tier]));
    if (withShell && fillable(mesh)) {
      const shell = new THREE.Mesh(mesh.geometry, SHELL);
      shell.renderOrder = 993;
      layer.group.add(shell);
    }
  }
}

/**
 * What is lit, and how brightly. Called once per frame by the player.
 *
 *   path/trail/active/out  name sets (arrays or Sets)
 *   mix                    0 at the start of a transition, 1 at its end:
 *                          `out` (the leg being left) fades from active down
 *                          to trail brightness while `active` (the leg being
 *                          arrived at) comes up. Both are on screen through
 *                          the middle of the move, which is what makes the
 *                          wide shot read as a handoff rather than a jump.
 *   pulse                  seconds, for the slow breath on the active leg.
 */
export function paint({ path, trail, active, out, mix = 1, pulse = 0 }) {
  if (!root) return;
  fill("path", path, false);
  fill("trail", trail, false);
  fill("out", out, false);
  fill("active", active, true);

  const breathe = 0.88 + 0.12 * Math.sin(pulse * 2.2);
  MATS.path.opacity = BASE_OPACITY.path;
  MATS.trail.opacity = BASE_OPACITY.trail;
  MATS.out.opacity = THREE.MathUtils.lerp(BASE_OPACITY.out, BASE_OPACITY.trail, mix);
  MATS.active.opacity = BASE_OPACITY.active * mix * breathe;
  SHELL.opacity = SHELL_OPACITY * mix;
}

/** Drop the cached fills so the next `paint` rebuilds them.
 *
 *  A tier is only rebuilt when the NAMES it holds change, which is once a beat
 *  rather than once a frame. Visibility is not in that signature: isolating a
 *  sub-assembly takes bodies out of the view without changing any beat's name
 *  set, so the layers would keep the highlights they built while those bodies
 *  were still drawn. Anything that changes what is visible says so here. */
export function invalidate() {
  for (const layer of Object.values(layers)) layer.sig = null;
}

export function clear() {
  for (const tier of Object.keys(layers)) fill(tier, [], tier === "active");
}
