// Highlights the geometry selected by Materials or a model check.
//
// One surface holds the selection at a time. A surface that takes it from another tells the
// other through its `onRelease`, so the Materials panel never names a part the model has
// stopped showing. Leaving a selection flies the camera back to the view from before it
// (scene.js holds that view, and keeps it as the file's camera while the selection is up).
//
// The name match works because export_assembly names each solid (foam-assembly, seaflo-pump, …)
// and step.js buildMesh stamps that name onto the THREE.Mesh — the same names the scorecard's
// registry and the material catalog's bindings use.

import * as THREE from "three";
import { scene, camera, controls, holdCameraPose, releaseCameraPose, visibleShare } from "./scene.js";
import { state } from "./state.js";

const HL = 0x35e0d0; // highlight cyan — distinct from pick-find magenta and edge select/hover
const EDGE_THRESHOLD_DEG = 30;

const overlay = new THREE.Group();
overlay.name = "part-highlight";
overlay.renderOrder = 996;
scene.add(overlay);

const edgeMat = new THREE.LineBasicMaterial({ color: HL, transparent: true, opacity: 0.95, depthTest: false, depthWrite: false });
const visibleEdgeMat = new THREE.LineBasicMaterial({ color: HL, depthWrite: false });

let subject = null;

function clearOverlay() {
  for (const c of [...overlay.children]) {
    overlay.remove(c);
    if (c.geometry) c.geometry.dispose();        // edges + cloned shells are ours to dispose
    if (c.material && c.material !== edgeMat && c.material !== visibleEdgeMat) c.material.dispose();
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
// A gesture always wins over a fly in progress.
controls.addEventListener("start", () => { flyToken++; });

function flyTo({ position, target, up = camera.up }) {
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const startUp = camera.up.clone();
  const token = ++flyToken;
  const t0 = performance.now();
  return new Promise(resolve => {
    function step() {
      if (token !== flyToken) { resolve(false); return; }
      const t = Math.min((performance.now() - t0) / 400, 1);
      const ease = t * (2 - t);
      camera.position.lerpVectors(startPos, position, ease);
      camera.up.lerpVectors(startUp, up, ease).normalize();
      controls.target.lerpVectors(startTarget, target, ease);
      camera.lookAt(controls.target);
      controls.update();
      if (t < 1) requestAnimationFrame(step);
      else resolve(true);
    }
    requestAnimationFrame(step);
  });
}

// Frame `box` in the part of the canvas a phone's Materials sheet leaves uncovered.
function flyToBox(box, direction = null, instant = false) {
  if (box.isEmpty()) return Promise.resolve(false);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 2);
  const dir = direction || camera.position.clone().sub(controls.target).normalize();
  const position = center.clone().addScaledVector(dir, maxDim * 2.4 / visibleShare());
  if (!instant) return flyTo({ position, target: center });
  flyToken++;
  camera.position.copy(position);
  controls.target.copy(center);
  controls.update();
  return Promise.resolve(true);
}

// Installed locations face out from the assembly so its nearby context stays in view.
export function frameParts(names, { outward = false, instant = false } = {}) {
  const want = new Set(names), meshes = bodies(), picked = meshes.filter(mesh => want.has(mesh.name));
  const box = solidsBox(picked);
  let direction = null;
  if (outward && !box.isEmpty()) {
    const whole = solidsBox(meshes), size = whole.getSize(new THREE.Vector3());
    direction = box.getCenter(new THREE.Vector3()).sub(whole.getCenter(new THREE.Vector3()));
    direction.divide(size.max(new THREE.Vector3(1, 1, 1)));
    if (direction.length() < 0.1) direction = null;
    else direction.normalize();
  }
  return flyToBox(box, direction, instant);
}

function solidsBox(meshes) {
  const box = new THREE.Box3();
  for (const mesh of meshes) {
    mesh.updateWorldMatrix(true, false);
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    box.union(mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld));
  }
  return box;
}

// The drawn bodies of the loaded model, without the x-ray edges and hit proxies beside them.
function bodies() {
  return (state.currentGroup?.children || []).filter((m) =>
    m.isMesh && !m.userData?.isXrayEdge && !m.userData?.hitOnly && m.visible !== false);
}

// Draw visible edges for Materials and mark referenced geometry through walls for checks.
function draw() {
  clearOverlay();
  const report = { shown: 0, hidden: 0, whole: false, box: new THREE.Box3() };
  const want = subject?.names;
  const visible = bodies();
  const picked = want ? visible.filter((m) => want.has(m.name)) : [];
  if (want && state.currentGroup) {
    for (const m of state.currentGroup.children) {
      if (m.isMesh && m.visible === false && want.has(m.name)) report.hidden++;
    }
  }
  report.box = solidsBox(picked);
  report.whole = picked.length > 0 && picked.length === visible.length;
  const solids = [];
  const seen = new Set();
  for (const mesh of report.whole ? [] : picked) {
    if (seen.has(mesh.geometry)) continue;
    seen.add(mesh.geometry); // front + back share one geometry — one highlight per solid
    solids.push(mesh);
  }
  report.shown = solids.length;
  if (subject?.fill) {
    for (const mesh of solids) {
      mesh.updateWorldMatrix(true, false);
      if (subject.visibleOnly) {
        const edges = new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG).applyMatrix4(mesh.matrixWorld);
        overlay.add(new THREE.LineSegments(edges, visibleEdgeMat));
        continue;
      }
      const geometry = mesh.geometry.clone().applyMatrix4(mesh.matrixWorld);
      overlay.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry, EDGE_THRESHOLD_DEG), edgeMat));
      const shell = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
        color: HL, transparent: true, opacity: 0.16, side: THREE.DoubleSide,
        depthWrite: false, depthTest: false,
      }));
      shell.renderOrder = 995;
      overlay.add(shell);
    }
  }
  subject?.onDraw?.(report);
  return report;
}

// Select the solids named in `names` (Set or array) for `owner`, replacing whatever was
// selected, and frame them unless `fly` is false (a pick made in the model keeps the camera
// where the reader has it). `fill` draws the highlight, `visibleOnly` limits it to visible
// edges, and `hold` keeps the view from before the selection to fly back to
// (false lets go of it; null leaves it as it is). `onRelease` runs when another surface takes
// the selection or it is cleared from outside. Each drawing reports { shown, hidden, whole } to
// `onDraw` and is returned: solids picked out, solids of the selection hidden from this view,
// and whether it is all of what is drawn.
export function highlightParts(names, {
  owner = null, onRelease = null, onDraw = null, fly = true, fill = true, visibleOnly = false, hold = fly ? true : null,
} = {}) {
  const previous = subject;
  if (previous && previous.owner !== owner) {
    subject = null;
    previous.onRelease?.();
  }
  subject = { names: names instanceof Set ? names : new Set(names), owner, onRelease, onDraw, fill, visibleOnly };
  if (hold) holdCameraPose();
  else if (hold === false) releaseCameraPose();
  const report = draw();
  if (fly && !report.box.isEmpty()) flyToBox(report.box);
  else if (fly) flyToken++;
  return report;
}

// Draw the selection again on the geometry as it now stands — after a hide or a finish change.
export function refreshHighlight() {
  if (subject) draw();
}

function end(owner, back) {
  if (owner && subject && subject.owner !== owner) return false;
  const previous = subject;
  subject = null;
  const pose = releaseCameraPose();
  if (!previous && !pose) return false;
  draw();
  if (back && pose) flyTo(pose);
  else flyToken++; // cancel an in-flight fly-to
  if (previous && previous.owner !== owner) previous.onRelease?.();
  return true;
}

// End the selection where the camera is. `owner` names the surface asking: it ends only its
// own selection and is not told about it; with no owner, whoever held it is told.
export function clearHighlight({ owner = null } = {}) {
  return end(owner, false);
}

// End the selection and fly back to the view from before it, if one was held.
export function leaveHighlight({ owner = null } = {}) {
  return end(owner, true);
}

// The geometry under the selection is being replaced. Its overlay goes with it; the
// view held from before it stays, for the owner to draw its selection again on the new model.
export function dropHighlight() {
  subject = null;
  clearOverlay();
  flyToken++;
}
