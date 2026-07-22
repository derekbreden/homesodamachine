// Highlight a named solid (or a few) in the loaded STEP scene — the scorecard modal's detail
// rows click through to the geometry they name. Draws bright feature-edges + a faint shell over
// the referenced meshes (depth-test off, so it reads through the enclosure walls) and flies the
// camera to frame them. Overlay-only: the base meshes' materials are never touched, so it
// composes with x-ray and clears cleanly. Mirrors pick-find.js's overlay + fly-to, but at the
// whole-solid level (a component name) rather than a pick coordinate.
//
// The name match works because export_assembly names each solid (foam-assembly, seaflo-pump, …)
// and step.js buildMesh stamps that name onto the THREE.Mesh — the same names the scorecard's
// registry uses, so a detail row's text and a scene mesh share one key.

import * as THREE from "three";
import { scene, camera, controls } from "./scene.js";
import { state } from "./state.js";

const HL = 0x35e0d0; // highlight cyan — distinct from pick-find magenta and edge select/hover
const EDGE_THRESHOLD_DEG = 30;

const overlay = new THREE.Group();
overlay.name = "part-highlight";
overlay.renderOrder = 996;
scene.add(overlay);

const edgeMat = new THREE.LineBasicMaterial({ color: HL, transparent: true, opacity: 0.95, depthTest: false });
edgeMat.depthWrite = false;

function clearOverlay() {
  for (const c of [...overlay.children]) {
    overlay.remove(c);
    if (c.geometry) c.geometry.dispose();        // edges + cloned shells are ours to dispose
    if (c.material && c.material !== edgeMat) c.material.dispose();
  }
}

// The distinct component names in the loaded model (STEP assembly node names, stamped onto each
// mesh by buildMesh). The scorecard uses this to decide which rows are clickable — a row is
// clickable only when it names a part that's actually in the scene.
export function scenePartNames() {
  const names = new Set();
  if (!state.currentGroup) return names;
  for (const m of state.currentGroup.children) {
    if (m.isMesh && m.name) names.add(m.name);
  }
  return names;
}

let flyToken = 0;
function flyToBox(box) {
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 2);
  const dir = camera.position.clone().sub(controls.target).normalize();
  const destPos = center.clone().addScaledVector(dir, maxDim * 2.4);
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const token = ++flyToken;
  const t0 = performance.now();
  function step() {
    if (token !== flyToken) return;
    const t = Math.min((performance.now() - t0) / 400, 1);
    const ease = t * (2 - t);
    camera.position.lerpVectors(startPos, destPos, ease);
    controls.target.lerpVectors(startTarget, center, ease);
    camera.lookAt(controls.target);
    controls.update();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Highlight every mesh whose name is in `names` (Set or array): bright edges + a faint shell
// over each, framed by the camera. Returns the count highlighted.
export function highlightParts(names) {
  clearOverlay();
  const want = names instanceof Set ? names : new Set(names);
  if (!state.currentGroup || !want.size) return 0;
  const box = new THREE.Box3();
  const seen = new Set();
  let n = 0;
  for (const mesh of state.currentGroup.children) {
    if (!mesh.isMesh || !want.has(mesh.name) || seen.has(mesh.geometry)) continue;
    seen.add(mesh.geometry); // front + back share one geometry — one highlight per solid
    // Ride the mesh's world matrix, not raw geometry: committed parts sit at identity (geometry
    // is already world-space), but a part under an active editor preview carries a live transform —
    // copying it lands the highlight (and the fly-to) on the moved pose, right where the clash is.
    const m = mesh.matrixWorld;
    const eg = new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG);
    const edges = new THREE.LineSegments(eg, edgeMat);
    edges.matrixAutoUpdate = false; edges.matrix.copy(m);
    overlay.add(edges);
    const shell = new THREE.Mesh(mesh.geometry.clone(), new THREE.MeshBasicMaterial({
      color: HL, transparent: true, opacity: 0.16, side: THREE.DoubleSide,
      depthWrite: false, depthTest: false,
    }));
    shell.matrixAutoUpdate = false; shell.matrix.copy(m);
    shell.renderOrder = 995;
    overlay.add(shell);
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    box.union(mesh.geometry.boundingBox.clone().applyMatrix4(m));
    n++;
  }
  if (n) flyToBox(box);
  return n;
}

export function isHighlightActive() {
  return overlay.children.length > 0;
}

export function clearHighlight() {
  clearOverlay();
  flyToken++; // cancel an in-flight fly-to
}
