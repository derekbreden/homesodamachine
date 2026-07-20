// Dev-only component editor for the STEP viewer — the 3D sibling of the PCB
// board editor (pcb-edit.js). A toggle (shown only when the dev-only step-editor
// API answers for the open file) lets you select a placed component, drag it
// along an axis with a gizmo or type an exact offset, rotate it about a world
// axis through its own centre, and write the move back to the CAD source.
//
// Two layers, so the move feels instant but persists for real:
//   • Local preview — dragging/typing transforms the component's meshes live in
//     YOUR scene (a matrix on each mesh + its x-ray edges). No rebuild, no wait.
//   • Apply — POSTs the move to the dev server, which appends it to the assembly's
//     placement-override sidecar and re-runs the CadQuery generator (~a couple
//     minutes: it reloads every part and re-checks the pack for clashes). On
//     success the new .step hot-reloads over the preview; a move that overlaps
//     fails the rebuild and the clash reason comes back to the panel.
//
// The move is a rotate about the component's CURRENT bbox centre, then a
// translate — the same order the sidecar applies (enclosure_assembly.py), so the
// preview and the rebuilt geometry land in the same place. Each Apply appends one
// step from the pose on screen, so the baseline after a reload is the applied
// pose and the working offset resets to zero.
//
// Mutually exclusive with the edge + component-select tools over the shared
// STEP_TOOL event: arming Edit disarms them, and arming either of them disarms
// Edit (its gizmo would otherwise fight their clicks).

import * as THREE from "three";
import { TransformControls } from "three/addons/controls/TransformControls.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { scene, camera, renderer, controls } from "./scene.js";
import { state } from "./state.js";

const SEL = 0x59ff9e; // edit-select highlight — green, distinct from the other tools
const EDGE_THRESHOLD_DEG = 30;
const AXES = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] };

let enabled = false;       // NOT persisted — editing is a deliberate dev action, off each open
let available = false;     // the dev step-editor API answered for the open file
let currentFile = null;

let selection = null;      // selected component name
let center0 = null;        // THREE.Vector3 — the component's bbox centre at select time (rotation pivot)
let previewObjs = [];      // meshes + x-ray edges of the selection we drive with a matrix
let mode = "translate";
const model = { tx: 0, ty: 0, tz: 0, axis: "z", deg: 0 }; // the pending move, from the current pose

// --- selection highlight overlay ---
const overlay = new THREE.Group();
overlay.name = "component-edit";
overlay.renderOrder = 994;
scene.add(overlay);
const edgeMat = new THREE.LineBasicMaterial({ color: SEL, transparent: true, opacity: 0.95, depthTest: false });
edgeMat.depthWrite = false;

function drawHighlight() {
  clearHighlight();
  if (!selection || !state.currentGroup) return;
  const seen = new Set();
  for (const m of state.currentGroup.children) {
    if (!m.isMesh || m.name !== selection || m.visible === false || seen.has(m.geometry)) continue;
    seen.add(m.geometry);
    const line = new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry, EDGE_THRESHOLD_DEG), edgeMat);
    line.matrixAutoUpdate = false;
    line.matrix.copy(m.matrix); // ride the same preview transform as the mesh
    overlay.add(line);
  }
}
function clearHighlight() {
  for (const c of [...overlay.children]) {
    overlay.remove(c);
    if (c.geometry) c.geometry.dispose();
  }
}

// --- gizmo ---
let gizmo = null;
let proxy = null;          // the Object3D the gizmo drives; its pose feeds the model
let gizmoGesture = false;  // this pointer gesture started on a gizmo handle (don't treat as a select)

function ensureGizmo() {
  if (gizmo) return;
  proxy = new THREE.Object3D();
  scene.add(proxy);
  gizmo = new TransformControls(camera, renderer.domElement);
  gizmo.setSpace("world");
  gizmo.setTranslationSnap(1);                          // 1 mm
  gizmo.setRotationSnap(THREE.MathUtils.degToRad(5));   // 5°
  gizmo.addEventListener("dragging-changed", (e) => { controls.enabled = !e.value; });
  gizmo.addEventListener("objectChange", onGizmoChange);
  // three r169+ splits the visible helper off the controls object.
  scene.add(gizmo.getHelper ? gizmo.getHelper() : gizmo);
  detachGizmo();
}

function detachGizmo() {
  if (!gizmo) return;
  gizmo.detach();
  const helper = gizmo.getHelper ? gizmo.getHelper() : gizmo;
  helper.visible = false;
}

function showGizmo() {
  ensureGizmo();
  applyMode();
  modelToProxy();
  gizmo.attach(proxy);
  const helper = gizmo.getHelper ? gizmo.getHelper() : gizmo;
  helper.visible = true;
}

function applyMode() {
  if (!gizmo) return;
  gizmo.setMode(mode === "rotate" ? "rotate" : "translate");
  // Rotate is single-axis: show only the selected ring so the gizmo can't
  // produce an off-axis quaternion the write-back can't express.
  if (mode === "rotate") {
    gizmo.showX = model.axis === "x";
    gizmo.showY = model.axis === "y";
    gizmo.showZ = model.axis === "z";
  } else {
    gizmo.showX = gizmo.showY = gizmo.showZ = true;
  }
}

function axisVec(a) { return new THREE.Vector3(...AXES[a]); }

function modelToProxy() {
  if (!proxy || !center0) return;
  proxy.position.set(center0.x + model.tx, center0.y + model.ty, center0.z + model.tz);
  proxy.quaternion.setFromAxisAngle(axisVec(model.axis), THREE.MathUtils.degToRad(model.deg));
  proxy.updateMatrixWorld(true);
}

function onGizmoChange() {
  if (!proxy || !center0) return;
  if (mode === "translate") {
    model.tx = round(proxy.position.x - center0.x);
    model.ty = round(proxy.position.y - center0.y);
    model.tz = round(proxy.position.z - center0.z);
  } else {
    const v = axisVec(model.axis);
    const q = proxy.quaternion;
    const angle = 2 * Math.acos(Math.min(1, Math.abs(q.w)));
    const sign = q.x * v.x + q.y * v.y + q.z * v.z >= 0 ? 1 : -1;
    model.deg = round(THREE.MathUtils.radToDeg(angle) * sign);
  }
  applyPreview();
  syncFields();
}

function round(n) { return Math.round(n * 100) / 100; }

// --- live preview (a matrix on each of the selection's objects) ---
const _delta = new THREE.Matrix4();
const _negC = new THREE.Matrix4();

function computeDelta() {
  proxy.updateMatrix(); // Translate(pos) * Rotate(quat), scale 1
  _negC.makeTranslation(-center0.x, -center0.y, -center0.z);
  // Delta = Translate(pos)·Rotate·Translate(-centre) == rotate about centre, then translate by pos-centre
  return _delta.multiplyMatrices(proxy.matrix, _negC);
}

function collectPreviewObjs() {
  previewObjs = [];
  if (!state.currentGroup || !selection) return;
  for (const m of state.currentGroup.children) {
    if ((m.isMesh && m.name === selection) ||
        (m.userData && m.userData.isXrayEdge && m.userData.xrayComponent === selection)) {
      m.matrixAutoUpdate = false;
      previewObjs.push(m);
    }
  }
}

function applyPreview() {
  if (!proxy || !center0) return;
  const d = computeDelta();
  for (const o of previewObjs) { o.matrix.copy(d); o.updateMatrixWorld(true); }
  for (const line of overlay.children) { line.matrix.copy(d); line.updateMatrixWorld(true); }
}

function clearPreview() {
  for (const o of previewObjs) {
    o.matrix.identity();
    o.matrixAutoUpdate = true;
    o.updateMatrixWorld(true);
  }
  previewObjs = [];
}

// --- selection ---
const _raycaster = new THREE.Raycaster();
const _ndc = new THREE.Vector2();

function pickComponent(clientX, clientY) {
  if (!state.currentGroup) return null;
  const targets = state.currentGroup.children.filter(
    (c) => c.userData && c.userData.side === "front" && c.visible !== false && c.name,
  );
  if (!targets.length) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.set(((clientX - rect.left) / rect.width) * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
  _raycaster.setFromCamera(_ndc, camera);
  const hits = _raycaster.intersectObjects(targets, false);
  return hits.length ? hits[0].object.name || null : null;
}

function componentCenter(name) {
  const box = new THREE.Box3();
  for (const m of state.currentGroup.children) {
    if (m.isMesh && m.name === name) {
      if (!m.geometry.boundingBox) m.geometry.computeBoundingBox();
      box.union(m.geometry.boundingBox);
    }
  }
  return box.isEmpty() ? new THREE.Vector3() : box.getCenter(new THREE.Vector3());
}

function selectComponent(name) {
  clearPreview();
  selection = name;
  center0 = componentCenter(name);
  model.tx = model.ty = model.tz = 0; model.deg = 0;
  collectPreviewObjs();
  drawHighlight();
  showGizmo();
  showPanel();
  setStatus("", "");
}

function clearSelection() {
  clearPreview();
  clearHighlight();
  detachGizmo();
  selection = null;
  center0 = null;
  hidePanel();
}

// --- panel ---
let panel = null;

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "edge-panel component-edit-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Edit";
  const nameEl = document.createElement("span");
  nameEl.className = "edge-panel-file";
  const close = document.createElement("button");
  close.type = "button"; close.className = "edge-panel-close"; close.textContent = "×"; close.title = "Clear selection";
  close.addEventListener("click", clearSelection);
  head.append(title, nameEl, close);
  panel.appendChild(head);
  panel._nameEl = nameEl;

  // Move / Rotate mode
  const modeRow = document.createElement("div");
  modeRow.className = "component-edit-mode";
  const moveBtn = tab("Move", () => setMode("translate"));
  const rotBtn = tab("Rotate", () => setMode("rotate"));
  modeRow.append(moveBtn, rotBtn);
  panel.appendChild(modeRow);
  panel._moveBtn = moveBtn; panel._rotBtn = rotBtn;

  // Move fields (dx/dy/dz)
  const moveFields = document.createElement("div");
  moveFields.className = "component-edit-fields component-edit-move";
  panel._moveInputs = {};
  for (const ax of ["tx", "ty", "tz"]) {
    const { wrap, input } = numField(ax[1].toUpperCase(), (v) => { model[ax] = v; onFieldChange(); });
    panel._moveInputs[ax] = input;
    moveFields.appendChild(wrap);
  }
  panel.appendChild(moveFields);
  panel._moveFields = moveFields;

  // Rotate fields (axis + degrees)
  const rotFields = document.createElement("div");
  rotFields.className = "component-edit-fields component-edit-rot";
  const axisSel = document.createElement("select");
  axisSel.className = "component-edit-axis";
  for (const a of ["x", "y", "z"]) {
    const o = document.createElement("option"); o.value = a; o.textContent = a.toUpperCase(); axisSel.appendChild(o);
  }
  axisSel.value = model.axis;
  axisSel.addEventListener("change", () => { model.axis = axisSel.value; model.deg = 0; applyMode(); onFieldChange(); });
  const { wrap: degWrap, input: degInput } = numField("°", (v) => { model.deg = v; onFieldChange(); });
  rotFields.append(labeled("axis", axisSel), degWrap);
  panel.appendChild(rotFields);
  panel._rotFields = rotFields; panel._axisSel = axisSel; panel._degInput = degInput;

  // Actions
  const actions = document.createElement("div");
  actions.className = "component-edit-actions";
  const applyBtn = document.createElement("button");
  applyBtn.type = "button"; applyBtn.className = "edge-panel-all component-edit-apply"; applyBtn.textContent = "Apply to source";
  applyBtn.addEventListener("click", apply);
  const resetBtn = document.createElement("button");
  resetBtn.type = "button"; resetBtn.className = "component-edit-reset"; resetBtn.textContent = "Reset";
  resetBtn.title = "Clear this component's overrides and rebuild";
  resetBtn.addEventListener("click", reset);
  actions.append(applyBtn, resetBtn);
  panel.appendChild(actions);
  panel._applyBtn = applyBtn;

  const status = document.createElement("div");
  status.className = "component-edit-status";
  panel.appendChild(status);
  panel._status = status;
}

function tab(label, onClick) {
  const b = document.createElement("button");
  b.type = "button"; b.className = "component-edit-tab"; b.textContent = label;
  b.addEventListener("click", onClick);
  return b;
}
function labeled(label, el) {
  const w = document.createElement("label");
  w.className = "component-edit-field";
  const s = document.createElement("span"); s.textContent = label;
  w.append(s, el);
  return w;
}
function numField(label, onCommit) {
  const input = document.createElement("input");
  input.type = "number"; input.step = "1"; input.value = "0"; input.className = "component-edit-num";
  const commit = () => { const v = parseFloat(input.value); onCommit(Number.isFinite(v) ? v : 0); };
  input.addEventListener("input", commit);
  return { wrap: labeled(label, input), input };
}

function onFieldChange() {
  modelToProxy();
  applyPreview();
}

function setMode(m) {
  mode = m;
  applyMode();
  modelToProxy();
  syncFields();
  if (panel) {
    panel._moveBtn.classList.toggle("on", mode === "translate");
    panel._rotBtn.classList.toggle("on", mode === "rotate");
    panel._moveFields.style.display = mode === "translate" ? "" : "none";
    panel._rotFields.style.display = mode === "rotate" ? "" : "none";
  }
}

function syncFields() {
  if (!panel) return;
  panel._moveInputs.tx.value = String(model.tx);
  panel._moveInputs.ty.value = String(model.ty);
  panel._moveInputs.tz.value = String(model.tz);
  panel._axisSel.value = model.axis;
  panel._degInput.value = String(model.deg);
}

function showPanel() {
  if (!panel) buildPanel();
  if (state.currentCadWrapper && panel.parentElement !== state.currentCadWrapper) {
    state.currentCadWrapper.appendChild(panel);
  }
  panel._nameEl.textContent = selection || "";
  panel._nameEl.title = selection || "";
  setMode(mode);
  syncFields();
  panel.classList.add("show");
}
function hidePanel() { if (panel) panel.classList.remove("show"); }

function setStatus(msg, kind) {
  if (!panel) return;
  panel._status.textContent = msg;
  panel._status.className = "component-edit-status" + (kind ? " " + kind : "");
  if (panel._applyBtn) panel._applyBtn.disabled = kind === "busy";
}

// --- write-back ---
function hasMove() {
  return model.tx || model.ty || model.tz || model.deg % 360 !== 0;
}

async function apply() {
  if (!selection || !hasMove()) { setStatus("nothing to apply", "err"); return; }
  const body = { file: currentFile, component: selection, translate: [model.tx, model.ty, model.tz] };
  if (model.deg % 360 !== 0) body.rotate = { axis: AXES[model.axis], deg: model.deg };
  setStatus("Rebuilding… (~2 min, checking clearances)", "busy");
  try {
    const r = await fetch("/api/step-editor/override", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    const j = await r.json();
    // On success the server broadcasts the new .step; live.js hot-reloads it and
    // onStepReloaded() re-syncs. Keep the preview until then so the move doesn't
    // flicker back to the old pose while the rebuild runs.
    if (j.ok) setStatus("Applied — reloading…", "ok");
    else setStatus(j.error ? `Not applied — ${j.error}` : "rebuild failed", "err");
  } catch (e) {
    setStatus(`request failed — ${e.message}`, "err");
  }
}

async function reset() {
  if (!selection) return;
  setStatus("Resetting… (~2 min)", "busy");
  try {
    const r = await fetch("/api/step-editor/override", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file: currentFile, component: selection, clear: true }),
    });
    const j = await r.json();
    if (j.ok) setStatus("Reset — reloading…", "ok");
    else setStatus(j.error ? `Reset failed — ${j.error}` : "reset failed", "err");
  } catch (e) {
    setStatus(`request failed — ${e.message}`, "err");
  }
}

// step.js calls this after every (re)load of the STEP group. When our applied
// move lands (or any hot reload), re-resolve the selection against the fresh
// meshes: the new geometry already carries the applied pose, so the working
// offset resets to zero and the gizmo re-seats on the new centre.
export function onStepReloaded() {
  if (!enabled || !selection) return;
  const names = new Set();
  for (const m of state.currentGroup.children) if (m.isMesh && m.name) names.add(m.name);
  if (!names.has(selection)) { clearSelection(); return; }
  const keep = selection;
  previewObjs = [];        // old meshes are gone; don't touch them
  selectComponent(keep);   // recompute centre + gizmo + overlay against the new group
  setStatus("Applied ✓", "ok");
}

// --- pointer wiring (select on click, unless the gesture was on a gizmo handle) ---
let downX = 0, downY = 0;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }

renderer.domElement.addEventListener("pointerdown", (e) => {
  downX = e.clientX; downY = e.clientY;
  gizmoGesture = !!(gizmo && gizmo.axis); // pointer is over a gizmo handle
});
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!active()) return;
  if (gizmoGesture) { gizmoGesture = false; return; }
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return; // a drag/orbit, not a click
  const name = pickComponent(e.clientX, e.clientY);
  if (name) selectComponent(name);
  else clearSelection();
});

// --- enable / mutual exclusion / teardown ---
export function setComponentEditEnabled(on) {
  if (on && !available) return;
  enabled = !!on;
  if (enabled) {
    window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_TOOL, { detail: "edit" }));
  } else {
    clearSelection();
    controls.enabled = true;
  }
}
export function isComponentEditEnabled() { return enabled; }

let toggleRefresh = null;
window.addEventListener(HSM_EVENTS.STEP_TOOL, (e) => {
  if (e.detail !== "edit" && enabled) {
    enabled = false;
    clearSelection();
    controls.enabled = true;
    if (toggleRefresh) toggleRefresh();
  }
});

export function clearComponentEdit() {
  clearSelection();
  enabled = false;
  controls.enabled = true;
  if (toggleRefresh) toggleRefresh();
}

// Toggle — hidden until the dev-only editor API confirms this file is editable
// (so it never shows on the public site, and only for assemblies wired for it).
export function makeComponentEditToggle(file) {
  currentFile = file;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "component-edit-toggle off";
  btn.style.display = "none";
  function refresh() {
    btn.textContent = enabled ? "Edit component: on" : "Edit component: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => { setComponentEditEnabled(!enabled); refresh(); });
  toggleRefresh = refresh;
  refresh();

  available = false;
  fetch(`/api/step-editor/overrides?file=${encodeURIComponent(file)}`)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error("unavailable"))))
    .then(() => { available = true; btn.style.display = ""; })
    .catch(() => { available = false; });

  return btn;
}
