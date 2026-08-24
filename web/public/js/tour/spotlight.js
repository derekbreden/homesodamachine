// WHAT IS LIT, AND HOW LOUDLY. Two axes, and they mean different things.
//
//   HUE says WHAT IS IN THE PIPE. Water is blue; once it has been through the
//   sparge stone it is soda and it is teal; CO2 is red and refrigerant green
//   for the tours that will want them. So the moment the water becomes soda is
//   a colour change on screen, and a run's identity is legible before any word
//   about it is read.
//
//   BRIGHTNESS says WHERE WE ARE. Four tiers of it over the same hue:
//     map     every body that fluid touches, faint, all tour long
//     trail   the legs already crossed
//     out     the leg being left, fading back into the trail
//     active  the leg on screen now — bright, with a halo under it and a
//             shell over the solid
//
// A body too big to be pointed at keeps its edges and gives up the shell:
// the fill reads as "this one" over a fitting and as a wash of colour over the
// foam block, which hides the run it was meant to point at.
//
// EVERYTHING DRAWS WITH DEPTH TESTING OFF, which is what lets a fitting buried
// three bodies deep read through the cabinet wall — and is why a body taken out
// of the view has to be skipped rather than drawn faintly. Over a hidden solid
// this is not faint, it is a bright wireframe of a thing that is not there.
//
// Overlay only: the bodies' own materials are never touched, so this composes
// with the x-ray ghost and clears without restoring anything. The layers hang
// off the MODEL GROUP, so a model standing under a transform carries them.

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { makeEdgeMaterial } from "../viewer/xray.js";

const EDGE_THRESHOLD_DEG = 30;

// The fluids, and what each one looks like.
export const HUES = {
  water: 0x4d8dff,       // cold, in from the house
  soda: 0x35e0d0,        // the same water once it has taken gas
  co2: 0xe0554d,
  refrigerant: 0x5fb56f,
  flavor: 0xd9a24c,
};
const hueOf = (name) => HUES[name] || HUES.water;

// A body big enough to BE the view does not get the fill.
const SHELL_MAX_FRACTION = 0.24;

// Per tier: how bright, how wide, and where in the draw order.
const TIERS = {
  map:    { opacity: 0.20, width: 1.6, order: 991, shell: false },
  trail:  { opacity: 0.50, width: 2.2, order: 992, shell: false },
  halo:   { opacity: 0.10, width: 6.5, order: 993, shell: false },
  out:    { opacity: 0.90, width: 3.0, order: 994, shell: false },
  active: { opacity: 0.90, width: 3.0, order: 995, shell: true },
  // The wavefront: a couple of bodies at a time, travelling the run in the
  // order the fluid takes. Direction, without a centreline to draw it on.
  crest:  { opacity: 1.00, width: 4.5, order: 996, shell: false },
};

// EVERYTHING BEHIND THE LIGHTS, TURNED DOWN. A camera-facing sheet of the
// background colour, drawn after the model and before the overlay, so the
// machine fades and what is lit does not. Louder by silence rather than by
// brightness, and it composes with every tier because it is a layer in the
// draw order and not a change to anybody's material.
//
// It cannot be a DOM scrim: the highlights are in the canvas, so a sheet over
// the canvas would dim them too.
const scrim = new THREE.Mesh(
  new THREE.PlaneGeometry(1, 1),
  new THREE.MeshBasicMaterial({
    color: 0x1a1a2e, transparent: true, opacity: 0,
    depthTest: false, depthWrite: false,
  }),
);
scrim.renderOrder = 989;
scrim.frustumCulled = false;
scrim.visible = false;

/** Keep the scrim filling the frame, just in front of the camera. */
export function fitScrim(camera) {
  if (!scrim.visible) return;
  const d = Math.max(camera.near * 2, 0.05);
  const h = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) * d;
  scrim.scale.set(h * camera.aspect * 1.1, h * 1.1, 1);
  scrim.quaternion.copy(camera.quaternion);
  scrim.position.copy(camera.position)
    .add(new THREE.Vector3(0, 0, -d).applyQuaternion(camera.quaternion));
}

// One shell material per hue — the faint fill over an active solid.
const shellMats = new Map();
function shellMat(hue) {
  let m = shellMats.get(hue);
  if (!m) {
    m = new THREE.MeshBasicMaterial({
      color: hue, transparent: true, opacity: 0,
      side: THREE.DoubleSide, depthWrite: false, depthTest: false,
    });
    shellMats.set(hue, m);
  }
  return m;
}

// One edge material per tier per hue. LineMaterial widths are in pixels of a
// stated resolution and scene.js re-states that resolution every frame for
// every material makeEdgeMaterial has handed out — so they are made through it,
// and made once.
const edgeMats = new Map();
function edgeMat(tier, hue) {
  const key = `${tier}:${hue}`;
  let m = edgeMats.get(key);
  if (!m) {
    m = makeEdgeMaterial({
      color: new THREE.Color(hue), linewidth: TIERS[tier].width,
      transparent: true, opacity: 0, depthTest: false, depthWrite: false,
    });
    edgeMats.set(key, m);
  }
  return m;
}

// Fat-line geometry per solid geometry, built the first time any layer asks and
// reused by every layer after — the same body is in the map, then in the active
// leg, then in the trail, and rebuilding its edges each time is the one
// expensive thing here.
let edgeCache = new WeakMap();
let edgeMade = [];   // the same geometries in a list we can walk: a fat-line
                     // buffer is a GL allocation and lives until it is disposed.

let root = null;      // our group, parented to the model group
let hostGroup = null; // the model group it hangs off
let modelRadius = 0;  // and how big it is, for the fill cutoff
const layers = new Map(); // key -> { group, sig, tier, hue }

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

/** Point the spotlight at a freshly mounted model. */
export function attach(group) {
  if (root && root.parent) root.parent.remove(root);
  layers.clear();
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
  // The scrim rides the SCENE, not the model — it is a sheet in front of the
  // camera and owes nothing to where the machine stands.
  if (hostGroup.parent) hostGroup.parent.add(scrim);
}

const _sphere = new THREE.Sphere();
function fillable(mesh) {
  if (!modelRadius) return true;
  if (!mesh.geometry.boundingSphere) mesh.geometry.computeBoundingSphere();
  return mesh.geometry.boundingSphere.radius <= modelRadius * SHELL_MAX_FRACTION;
}

function bodiesNamed(names) {
  const want = names instanceof Set ? names : new Set(names || []);
  const out = [];
  const seen = new Set();
  if (!hostGroup || !want.size) return out;
  for (const m of hostGroup.children) {
    if (!m.isMesh || m.userData.isXrayEdge) continue;
    if (!m.name || !want.has(m.name)) continue;
    if (m.visible === false) continue;   // taken out of the view: taken out of the light
    if (seen.has(m.geometry)) continue;  // one highlight per solid
    seen.add(m.geometry);
    out.push(m);
  }
  return out;
}

/** Fill one layer. A layer already holding exactly these bodies at this hue is
 *  left alone — the sets change once a beat and the frames between only move
 *  opacity. */
function fill(key, tier, hue, names) {
  let layer = layers.get(key);
  if (!layer) {
    const group = new THREE.Group();
    group.renderOrder = TIERS[tier].order;
    root.add(group);
    layer = { group, sig: null };
    layers.set(key, layer);
  }
  const list = [...(names instanceof Set ? names : new Set(names || []))].sort();
  const sig = `${hue}|${list.join("|")}`;
  if (sig === layer.sig) return;
  layer.sig = sig;
  for (const c of [...layer.group.children]) layer.group.remove(c);
  for (const mesh of bodiesNamed(list)) {
    layer.group.add(new LineSegments2(edgesFor(mesh.geometry), edgeMat(tier, hue)));
    if (TIERS[tier].shell && fillable(mesh)) {
      const s = new THREE.Mesh(mesh.geometry, shellMat(hue));
      s.renderOrder = TIERS[tier].order - 1;
      layer.group.add(s);
    }
  }
}

/**
 * Called once per frame by the player.
 *
 *   paths      [{hue, parts}] — the map, one entry per fluid
 *   hue        the beat's own fluid, for its active/trail/crest tiers
 *   trail/active/out   name sets
 *   crest      the wavefront's bodies right now, if the beat is flowing
 *   mix        0 at a move's start, 1 at its end: `out` fades back into the
 *              trail while `active` comes up, so the handoff is visible
 *   quiet      0..1, how far the machine behind the lights is turned down
 *   reveal     0..1 of `active` lit so far, IN THE ORDER THE BEAT NAMES THEM
 *   haloWidth  0..1 of the halo's full width — narrow on a wide shot, where
 *              neighbouring halos would otherwise meet and turn a run into a smear
 */
export function paint({ paths = [], hue = "water", trail, active, out, crest,
                        mix = 1, pulse = 0, quiet = 0, reveal = 1, haloWidth = 1 }) {
  if (!root) return;
  const H = hueOf(hue);
  const list = active instanceof Set ? [...active] : (active || []);
  const lit = reveal >= 1 ? list
    : list.slice(0, Math.max(1, Math.round(list.length * reveal)));

  paths.forEach((p, i) => fill(`map${i}`, "map", hueOf(p.hue), p.parts));
  fill("trail", "trail", H, trail);
  fill("out", "out", H, out);
  fill("halo", "halo", H, lit);
  fill("active", "active", H, lit);
  fill("crest", "crest", H, crest);

  // Brightness is set on the MATERIALS, which are shared per tier per hue —
  // reading it back off a layer's children would miss an empty layer and leave
  // its material carrying the last beat's value.
  const breathe = 0.88 + 0.12 * Math.sin(pulse * 2.2);
  for (const p of paths) edgeMat("map", hueOf(p.hue)).opacity = TIERS.map.opacity;
  edgeMat("trail", H).opacity = TIERS.trail.opacity;
  edgeMat("out", H).opacity =
    THREE.MathUtils.lerp(TIERS.out.opacity, TIERS.trail.opacity, mix);
  edgeMat("active", H).opacity = TIERS.active.opacity * mix * breathe;
  edgeMat("crest", H).opacity = TIERS.crest.opacity * mix;

  const halo = edgeMat("halo", H);
  halo.opacity = TIERS.halo.opacity * mix * breathe;
  // Narrow on a wide shot. Past about three times the bright line, neighbouring
  // halos meet and a fitting stops being a shape and becomes a blob — which is
  // the opposite of pointing at it.
  halo.linewidth = TIERS.halo.width * THREE.MathUtils.clamp(haloWidth, 0.25, 1);

  shellMat(H).opacity = 0.15 * mix;

  scrim.visible = quiet > 0.002;
  scrim.material.opacity = THREE.MathUtils.clamp(quiet, 0, 1);
}

/** Drop the cached fills so the next `paint` rebuilds them. A layer is rebuilt
 *  when the names it holds change, which is once a beat; visibility is not in
 *  that signature, so anything that changes what is drawn says so here. */
export function invalidate() {
  for (const layer of layers.values()) layer.sig = null;
}

export function clear() {
  for (const layer of layers.values()) { layer.sig = null; layer.group.clear(); }
}
