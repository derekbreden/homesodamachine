// The model's selection: the solids one surface has picked out — a Materials row, a part
// picked in the model, a checks row from the scorecard — drawn with bright feature-edges + a
// faint shell (depth-test off, so it reads through the enclosure walls) and framed by the
// camera. A part chosen in the Materials pane or opened from a part search can also fade every
// other body behind it, while Focus is on. A click in the model never fades it: through a faded
// model a click cannot aim, which is also why x-ray starts off. Nothing is faded unless such a
// part is selected, and a selection that is the whole of what is drawn picks nothing out.
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
import { scene, camera, controls, holdCameraPose, releaseCameraPose } from "./scene.js";
import { state } from "./state.js";
import { setFocusFade } from "./xray.js";
import { makeToolChip } from "./tool-rail.js";

const HL = 0x35e0d0; // highlight cyan — distinct from pick-find magenta and edge select/hover
const EDGE_THRESHOLD_DEG = 30;
const FOCUS_KEY = "step-focus";

const overlay = new THREE.Group();
overlay.name = "part-highlight";
overlay.renderOrder = 996;
scene.add(overlay);

const edgeMat = new THREE.LineBasicMaterial({ color: HL, transparent: true, opacity: 0.95, depthTest: false });
edgeMat.depthWrite = false;

// { names, owner, onRelease, onDraw, fill, fade } — what is selected, which surface selected
// it, and whether it is filled and the rest faded.
let subject = null;
let fading = false;   // the rest of the model is faded behind the selection
let offerFocus = false; // the selection is one Focus fades around
let focusOn = (() => {
  try { return localStorage.getItem(FOCUS_KEY) !== "0"; } catch { return true; }
})();
let focusChip = null;

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
// A gesture always wins over a fly in progress.
controls.addEventListener("start", () => { flyToken++; });

function flyTo({ position, target, up = camera.up }) {
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const startUp = camera.up.clone();
  const token = ++flyToken;
  const t0 = performance.now();
  function step() {
    if (token !== flyToken) return;
    const t = Math.min((performance.now() - t0) / 400, 1);
    const ease = t * (2 - t);
    camera.position.lerpVectors(startPos, position, ease);
    camera.up.lerpVectors(startUp, up, ease).normalize();
    controls.target.lerpVectors(startTarget, target, ease);
    camera.lookAt(controls.target);
    controls.update();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function flyToBox(box) {
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 2);
  const dir = camera.position.clone().sub(controls.target).normalize();
  flyTo({ position: center.clone().addScaledVector(dir, maxDim * 2.4), target: center });
}

function solidsBox(meshes) {
  const box = new THREE.Box3();
  for (const mesh of meshes) {
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    box.union(mesh.geometry.boundingBox);
  }
  return box;
}

// The drawn bodies of the loaded model, without the x-ray edges and hit proxies beside them.
function bodies() {
  return (state.currentGroup?.children || []).filter((m) =>
    m.isMesh && !m.userData?.isXrayEdge && !m.userData?.hitOnly && m.visible !== false);
}

// Draw the selection on the geometry as it stands: edges + shell over each of its visible
// solids, and the fade over everything else.
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
      overlay.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG), edgeMat));
      const shell = new THREE.Mesh(mesh.geometry.clone(), new THREE.MeshBasicMaterial({
        color: HL, transparent: true, opacity: 0.16, side: THREE.DoubleSide,
        depthWrite: false, depthTest: false,
      }));
      shell.renderOrder = 995;
      overlay.add(shell);
    }
  }
  offerFocus = Boolean(report.shown && subject.fade);
  fading = offerFocus && focusOn;
  setFocusFade(fading ? (mesh) => want.has(mesh.name) : null);
  syncFocusChip();
  subject?.onDraw?.(report);
  return report;
}

// Select the solids named in `names` (Set or array) for `owner`, replacing whatever was
// selected, and frame them unless `fly` is false (a pick made in the model keeps the camera
// where the reader has it). `fill` draws them in the highlight, `fade` lets Focus fade the
// rest of the model, and `hold` keeps the view from before the selection to fly back to
// (false lets go of it; null leaves it as it is). `onRelease` runs when another surface takes
// the selection or it is cleared from outside. Each drawing reports { shown, hidden, whole } to
// `onDraw` and is returned: solids picked out, solids of the selection hidden from this view,
// and whether it is all of what is drawn.
export function highlightParts(names, {
  owner = null, onRelease = null, onDraw = null, fly = true, fill = true, fade = false, hold = fly ? true : null,
} = {}) {
  const previous = subject;
  subject = { names: names instanceof Set ? names : new Set(names), owner, onRelease, onDraw, fill, fade };
  if (hold) holdCameraPose();
  else if (hold === false) releaseCameraPose();
  const report = draw();
  if (fly && !report.box.isEmpty()) flyToBox(report.box);
  else if (fly) flyToken++;
  if (previous && previous.owner !== owner) previous.onRelease?.();
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

// The geometry under the selection is being replaced. Its overlay and fade go with it; the
// view held from before it stays, for the owner to draw its selection again on the new model.
export function dropHighlight() {
  subject = null;
  clearOverlay();
  fading = offerFocus = false;
  setFocusFade(null);
  syncFocusChip();
  flyToken++;
}

function syncFocusChip() {
  if (focusChip) focusChip.hidden = !offerFocus;
}

// Whether `mesh` is faded behind the selection. A click in the model goes through a faded
// body to whatever stands out behind it.
export function fadedBody(mesh) {
  return fading && !subject.names.has(mesh.name);
}

// Focus: whether the rest of the model fades behind a part chosen in the Materials pane or
// opened from a search. The switch stands in the Show row only while such a part is selected;
// the choice is kept in this browser under `step-focus`.
export function makeFocusToggle() {
  focusChip = makeToolChip({
    className: "focus-toggle",
    label: "Focus",
    icon: "focus",
    title: "Fade everything but the selection",
    read: () => focusOn,
    write: (on) => {
      focusOn = !!on;
      try { localStorage.setItem(FOCUS_KEY, focusOn ? "1" : "0"); } catch {}
      if (subject) draw();
    },
  });
  syncFocusChip();
  return focusChip;
}
