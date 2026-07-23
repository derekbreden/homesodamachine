// Port markers — the located axis drawn on the geometry it describes.
//
// Every port in the scorecard sidecar's ports[] inventory becomes a disc at its world coordinate,
// sized to its bore Ø and facing the way it exits its body, with a short stub along that normal.
// Depth-test off, so the markers read through the enclosure walls (the part-highlight.js idiom).
// The disc is true to scale; the stub is a fixed length and holds its width at any zoom.
//
// Hovering a marker names its port, kind, bore, face, coordinate, and what it mates to — the rows
// the scorecard modal lists, read off the model instead.
//
// One unit CircleGeometry and one material per color are shared across every marker and scaled in
// place, so clearing removes children without disposing.

import * as THREE from "three";
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";

const LS_KEY = "step-ports";
const STUB_LEN = 10;   // mm along the face normal
const UNSIZED_R = 2;   // mm disc radius when diam is null
const HOVER_SLOP = 3;  // mm raycast threshold on the stub lines
const SEG = 32;

// Body face a port exits -> its outward normal. scorecard.py's Port.face vocabulary: one of the
// six body faces by name, or — where a fitting is clocked off the world axes, as the junction
// column's rolled elbows and the tees hung between them are — the axis given directly as a vector.
const FACE_NORMAL = {
  "x-": [-1, 0, 0], "x+": [1, 0, 0],
  "y-": [0, -1, 0], "y+": [0, 1, 0],
  "z-": [0, 0, -1], "z+": [0, 0, 1],
};

// The unit normal a port exits along, or null when the face is neither vocabulary — a marker with
// no readable direction is drawn as bad rather than pointed somewhere plausible.
function faceNormal(face) {
  if (typeof face === "string") return FACE_NORMAL[face] ?? null;
  if (!Array.isArray(face) || face.length !== 3) return null;
  const m = Math.hypot(face[0], face[1], face[2]);
  return m > 1e-9 ? [face[0] / m, face[1] / m, face[2] / m] : null;
}

// A port's face for display, mirroring scorecard.py's face_name.
function faceLabel(face) {
  if (typeof face === "string") return face.replace("-", "−");
  const n = faceNormal(face);
  return n ? `(${n.map((c) => (c < 0 ? "−" : "+") + Math.abs(c).toFixed(3)).join(", ")})` : "?";
}

// What the port carries.
const KIND_COLOR = {
  fluid: 0x3fa9f5,        // water, CO2, flavor
  refrigerant: 0xff7a45,  // the sealed loop
  electrical: 0xffd23f,   // wire
};
const BAD_COLOR = 0xff3b5c; // any status but "ok": off-surface, unpositioned, or unsized

// --- shared primitives (unit-sized; each marker scales its own copy) ---
const _unitDisc = new THREE.CircleGeometry(1, SEG);
const _unitRing = (() => {
  const pts = [];
  for (let i = 0; i <= SEG; i++) {
    const a = (i / SEG) * Math.PI * 2;
    pts.push(Math.cos(a), Math.sin(a), 0);
  }
  return new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
})();
const _unitStub = new THREE.BufferGeometry()
  .setAttribute("position", new THREE.Float32BufferAttribute([0, 0, 0, 0, 0, 1], 3));

const _mats = new Map(); // color hex -> { fill, line }
function matsFor(hex) {
  let m = _mats.get(hex);
  if (!m) {
    m = {
      fill: new THREE.MeshBasicMaterial({
        color: hex, transparent: true, opacity: 0.4, side: THREE.DoubleSide,
        depthTest: false, depthWrite: false,
      }),
      line: new THREE.LineBasicMaterial({
        color: hex, transparent: true, opacity: 0.95, depthTest: false, depthWrite: false,
      }),
    };
    _mats.set(hex, m);
  }
  return m;
}

const overlay = new THREE.Group();
overlay.name = "port-markers";
overlay.renderOrder = 997; // above part-highlight (995/996)
scene.add(overlay);

let enabled = (() => {
  try {
    const v = localStorage.getItem(LS_KEY);
    return v === null ? true : v === "1";
  } catch { return true; }
})();

let markersFile = null; // the model the current markers describe
let lastPorts = [];     // the inventory last drawn
let hitTargets = [];    // discs + stubs, each carrying userData.port

// --- building ---
const _q = new THREE.Quaternion();
const _localUp = new THREE.Vector3(0, 0, 1); // the unit primitives' own normal / stub direction
const _n = new THREE.Vector3();

function addMarker(port) {
  const [x, y, z] = port.pos;
  const nrm = faceNormal(port.face);
  _n.set(...(nrm ?? [0, 0, 1]));
  _q.setFromUnitVectors(_localUp, _n);
  const { fill, line } = matsFor(
    nrm && port.status === "ok" ? (KIND_COLOR[port.kind] ?? 0xffffff) : BAD_COLOR);
  const r = port.diam ? port.diam / 2 : UNSIZED_R;

  const place = (o, s) => {
    o.position.set(x, y, z);
    o.quaternion.copy(_q);
    o.scale.setScalar(s);
    o.renderOrder = 997;
    o.userData.port = port;
    overlay.add(o);
    return o;
  };
  const disc = place(new THREE.Mesh(_unitDisc, fill), r);        // the bore
  place(new THREE.Line(_unitRing, line), r);                     // its rim
  const stub = place(new THREE.Line(_unitStub, line), STUB_LEN); // the exit direction
  hitTargets.push(disc, stub);
}

// Draw the inventory for `file`, skipping ports with no position. Returns how many carry one —
// the model's marker count, whether or not the overlay is currently enabled.
export function showPorts(ports, file) {
  const inventory = Array.isArray(ports) ? ports : [];
  clearPorts();
  lastPorts = inventory;
  markersFile = file;
  const positioned = inventory.filter((p) => Array.isArray(p.pos) && p.pos.length === 3);
  if (enabled) for (const p of positioned) addMarker(p);
  return positioned.length;
}

export function clearPorts() {
  for (const c of [...overlay.children]) overlay.remove(c); // shared geometry/materials: never disposed
  hitTargets = [];
  lastPorts = [];
  markersFile = null;
  hideTip();
}

// Drop the overlay unless it already describes `file`. The sidecar mount lands before the STEP
// parse finishes, so the markers for the model now loading may already be up.
export function clearPortsExcept(file) {
  if (markersFile !== file) clearPorts();
}

// --- hover readout ---
const _ray = new THREE.Raycaster();
_ray.params.Line.threshold = HOVER_SLOP;
const _ndc = new THREE.Vector2();
let tipEl = null;

function hideTip() {
  if (tipEl) { tipEl.remove(); tipEl = null; }
}

function showTip(port, clientX, clientY) {
  const wrapper = state.currentCadWrapper;
  if (!wrapper) return;
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.className = "port-tip";
    wrapper.appendChild(tipEl);
  }
  const pos = port.pos.map((v) => Math.round(v * 100) / 100).join(", ");
  const face = faceLabel(port.face);
  const size = port.diam ? `Ø${port.diam}` : "Ø —";
  tipEl.textContent = "";
  const head = document.createElement("div");
  head.className = "port-tip-head";
  head.textContent = `${port.component} · ${port.name}`;
  const spec = document.createElement("div");
  spec.textContent = `${port.kind} · ${size} · ${face} · (${pos})`;
  const mates = document.createElement("div");
  mates.className = "port-tip-mates";
  mates.textContent = `→ ${port.mates}`;
  tipEl.append(head, spec, mates);
  if (port.status !== "ok") {
    const bad = document.createElement("div");
    bad.className = "port-tip-bad";
    bad.textContent = port.status;
    tipEl.appendChild(bad);
  }
  const rect = wrapper.getBoundingClientRect();
  tipEl.style.left = Math.min(clientX - rect.left + 14, rect.width - 260) + "px";
  tipEl.style.top = Math.max(clientY - rect.top - 12, 4) + "px";
}

function active() {
  return enabled && hitTargets.length && state.mountedDetail && state.mountedDetail.type === "step";
}

function portAt(clientX, clientY) {
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  _ndc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  _ray.setFromCamera(_ndc, camera);
  const hits = _ray.intersectObjects(hitTargets, false);
  return hits.length ? hits[0].object.userData.port : null;
}

renderer.domElement.addEventListener("pointermove", (e) => {
  if (!active() || e.buttons !== 0) { hideTip(); return; }
  const port = portAt(e.clientX, e.clientY);
  if (port) showTip(port, e.clientX, e.clientY);
  else hideTip();
});
renderer.domElement.addEventListener("pointerleave", hideTip);

// --- toggle ---
export function setPortsEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  const ports = lastPorts, file = markersFile; // clearPorts inside showPorts resets both
  showPorts(ports, file);
}

export function isPortsEnabled() {
  return enabled;
}

export function makePortToggle(count) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "port-toggle";
  btn.title = "Every located connector at its coordinate, drawn at its bore Ø";
  function refresh() {
    btn.textContent = enabled ? `Ports: ${count}` : "Ports: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => {
    setPortsEnabled(!enabled);
    refresh();
  });
  refresh();
  return btn;
}
