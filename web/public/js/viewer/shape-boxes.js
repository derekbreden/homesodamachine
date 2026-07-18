// Shape boxes — the boxes each component really occupies, drawn on the model.
//
// A component is a set of bodies, and its boxes are their boxes: one wireframe per solid it is
// built from, read from the scorecard sidecar's shapes[] record. Drawn depth-test off, alongside
// the port markers (port-markers.js).
//
// Each component's boxes are tinted by how much of them is material: the emptier the boxes, the
// hotter the wire, so a body whose box is mostly air reads as such at a glance. A component still
// modelled as a bare box or cylinder is drawn dashed-bright — its box IS its geometry.
//
// One unit BoxGeometry edge set is shared across every wireframe and scaled in place, so clearing
// removes children without disposing.

import * as THREE from "three";
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";

const LS_KEY = "step-shape-boxes";

// Material fill -> wire color. A box that is nearly all material describes its body well; one
// that is nearly all air does not.
const FILL_COLORS = [
  [0.75, 0x4ad991], // tight — the boxes are close to the part
  [0.45, 0xc3e05a],
  [0.25, 0xffc857],
  [0.00, 0xff6b6b], // mostly air
];
const PRIMITIVE_COLOR = 0xb388ff; // still a bare box or cylinder

function colorFor(shape) {
  if (shape.primitive) return PRIMITIVE_COLOR;
  for (const [floor, hex] of FILL_COLORS) if (shape.fill >= floor) return hex;
  return FILL_COLORS[FILL_COLORS.length - 1][1];
}

// --- shared primitives (unit cube centred on the origin; each wire scales its own copy) ---
const _unitEdges = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));

const _mats = new Map(); // color hex -> LineBasicMaterial
function matFor(hex) {
  let m = _mats.get(hex);
  if (!m) {
    m = new THREE.LineBasicMaterial({
      color: hex, transparent: true, opacity: 0.8, depthTest: false, depthWrite: false,
    });
    _mats.set(hex, m);
  }
  return m;
}

const overlay = new THREE.Group();
overlay.name = "shape-boxes";
overlay.renderOrder = 994; // under the port markers (997) and the part highlight (995/996)
scene.add(overlay);

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let boxesFile = null;  // the model the current wireframes describe
let lastShapes = [];   // the shape record last drawn
let hitTargets = [];

function addBox(shape, box) {
  const [x0, y0, z0, x1, y1, z1] = box;
  const line = new THREE.LineSegments(_unitEdges, matFor(colorFor(shape)));
  line.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  line.scale.set(Math.max(x1 - x0, 1e-3), Math.max(y1 - y0, 1e-3), Math.max(z1 - z0, 1e-3));
  line.renderOrder = 994;
  line.userData.shape = shape;
  overlay.add(line);
  hitTargets.push(line);
}

// Draw the shape record for `file`. Returns how many boxes were drawn.
export function showShapeBoxes(shapes, file) {
  const record = Array.isArray(shapes) ? shapes : [];
  clearShapeBoxes();
  lastShapes = record;
  boxesFile = file;
  if (!enabled) return record.reduce((n, s) => n + (s.boxes || []).length, 0);
  let n = 0;
  for (const s of record) for (const b of s.boxes || []) { addBox(s, b); n++; }
  return n;
}

export function clearShapeBoxes() {
  for (const c of [...overlay.children]) overlay.remove(c); // shared geometry/materials: never disposed
  hitTargets = [];
  lastShapes = [];
  boxesFile = null;
  hideTip();
}

// Drop the overlay unless it already describes `file` — the sidecar mount lands before the STEP
// parse finishes, so the wireframes for the model now loading may already be up.
export function clearShapeBoxesExcept(file) {
  if (boxesFile !== file) clearShapeBoxes();
}

// --- hover readout ---
const _ray = new THREE.Raycaster();
_ray.params.Line.threshold = 2;
const _ndc = new THREE.Vector2();
let tipEl = null;

function hideTip() {
  if (tipEl) { tipEl.remove(); tipEl = null; }
}

function showTip(shape, clientX, clientY) {
  const wrapper = state.currentCadWrapper;
  if (!wrapper) return;
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.className = "port-tip";
    wrapper.appendChild(tipEl);
  }
  const n = shape.boxes.length;
  tipEl.textContent = "";
  const head = document.createElement("div");
  head.className = "port-tip-head";
  head.textContent = shape.component;
  const spec = document.createElement("div");
  spec.textContent = `${n} ${n === 1 ? "box holds" : "boxes hold"} ${(shape.fill * 100).toFixed(0)}% material`;
  tipEl.append(head, spec);
  if (shape.primitive) {
    const bad = document.createElement("div");
    bad.className = "port-tip-bad";
    bad.textContent = `still a bare primitive (declared ${shape.declared})`;
    tipEl.appendChild(bad);
  }
  const rect = wrapper.getBoundingClientRect();
  tipEl.style.left = Math.min(clientX - rect.left + 14, rect.width - 260) + "px";
  tipEl.style.top = Math.max(clientY - rect.top - 12, 4) + "px";
}

function active() {
  return enabled && hitTargets.length && state.mountedDetail && state.mountedDetail.type === "step";
}

renderer.domElement.addEventListener("pointermove", (e) => {
  if (!active() || e.buttons !== 0) { hideTip(); return; }
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  _ndc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  _ray.setFromCamera(_ndc, camera);
  const hits = _ray.intersectObjects(hitTargets, false);
  if (hits.length) showTip(hits[0].object.userData.shape, e.clientX, e.clientY);
  else hideTip();
});
renderer.domElement.addEventListener("pointerleave", hideTip);

// --- toggle ---
export function setShapeBoxesEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  const shapes = lastShapes, file = boxesFile; // clearShapeBoxes inside show… resets both
  showShapeBoxes(shapes, file);
}

export function makeShapeBoxToggle(count) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "shape-box-toggle";
  btn.title = "The boxes each component really occupies — one per solid it is built from, "
            + "tinted by how much of the box is material";
  function refresh() {
    btn.textContent = enabled ? `Boxes: ${count}` : "Boxes: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => { setShapeBoxesEnabled(!enabled); refresh(); });
  refresh();
  return btn;
}
