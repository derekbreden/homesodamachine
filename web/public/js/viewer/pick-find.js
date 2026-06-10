// Find box — the edge picker's round trip. Paste any pick text (a copy-all
// blob, a single row, or a whole multi-pick message from either side of the
// conversation) and every recognizable pick in it is matched against the
// loaded model's reconstructed edges and classified faces, highlighted in
// one go, and framed by the camera. The agent composes pick lines from CAD
// coordinates; this is how they come back as geometry on screen.
//
// Matching is nearest-entity with a tolerance (pick-format.js), so the
// 3-decimal rounding in copied blobs and agent-composed lines is fine.
// Unmatched lines just count against the status readout — a stale pick
// from an older revision of a part fails soft.

import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, renderer, controls } from "./scene.js";
import { state } from "./state.js";
import { parsePicks, matchPicks, pickFileToViewerPath } from "./pick-format.js";
import { getFindData, faceHighlightGeometry } from "./edge-picker.js";
import { loadStepFile } from "./step.js";

const FIND = 0xff5ce1; // found-entity highlight (magenta — distinct from select/hover)

// --- overlay ---
const overlay = new THREE.Group();
overlay.name = "pick-find";
overlay.renderOrder = 997;
scene.add(overlay);

const findLineMat = new LineMaterial({ color: FIND, linewidth: 4, depthTest: false, transparent: true, opacity: 0.95 });
findLineMat.depthWrite = false;

function syncLineRes() {
  const w = renderer.domElement.width, h = renderer.domElement.height;
  if (w && h) findLineMat.resolution.set(w, h);
}
new ResizeObserver(syncLineRes).observe(renderer.domElement);
syncLineRes();

function clearOverlay() {
  for (const child of [...overlay.children]) {
    overlay.remove(child);
    if (child.geometry) child.geometry.dispose();
    if (child.material && child.material !== findLineMat) child.material.dispose();
  }
}

function addEdgeHighlight(edge, box) {
  const flat = [];
  for (const p of edge.points) { flat.push(p.x, p.y, p.z); box.expandByPoint(p); }
  const geo = new LineGeometry();
  geo.setPositions(flat);
  const line = new Line2(geo, findLineMat);
  line.renderOrder = 999;
  line.frustumCulled = false;
  overlay.add(line);
}

function addFaceHighlight(gid, box) {
  const geo = faceHighlightGeometry(gid);
  if (!geo) return;
  geo.computeBoundingBox();
  box.union(geo.boundingBox);
  const mat = new THREE.MeshBasicMaterial({
    color: FIND, transparent: true, opacity: 0.3, side: THREE.DoubleSide,
    depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.renderOrder = 997;
  overlay.add(mesh);
}

function addPointHighlight(p, box) {
  const v = new THREE.Vector3(p.x, p.y, p.z);
  box.expandByPoint(v);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute([v.x, v.y, v.z], 3));
  const mat = new THREE.PointsMaterial({ color: FIND, size: 12, sizeAttenuation: false, depthTest: false, transparent: true });
  const pts = new THREE.Points(geo, mat);
  pts.renderOrder = 1000;
  pts.frustumCulled = false;
  overlay.add(pts);
}

// Keep the current view direction, re-target onto the matches, and dolly
// to frame them — same ease + duration as the reset-view flight.
let flyToken = 0;
function flyToBox(box) {
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 2);
  const dir = camera.position.clone().sub(controls.target).normalize();
  const destTarget = center;
  const destPos = center.clone().addScaledVector(dir, maxDim * 2.2);

  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const token = ++flyToken;
  const duration = 400;
  const startTime = performance.now();
  function step() {
    if (token !== flyToken) return;
    const t = Math.min((performance.now() - startTime) / duration, 1);
    const ease = t * (2 - t);
    camera.position.lerpVectors(startPos, destPos, ease);
    controls.target.lerpVectors(startTarget, destTarget, ease);
    camera.lookAt(controls.target);
    controls.update();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// --- find panel UI ---
let panel = null;
let textarea = null;
let statusEl = null;
let panelOpen = false;

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "pick-find-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Find";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Close find";
  close.addEventListener("click", () => setPanelOpen(false));
  head.appendChild(title);
  head.appendChild(close);
  panel.appendChild(head);

  textarea = document.createElement("textarea");
  textarea.className = "pick-find-input";
  textarea.rows = 5;
  textarea.placeholder = "Paste pick text — edge / face / click lines, one or many";
  textarea.spellcheck = false;
  panel.appendChild(textarea);

  const buttons = document.createElement("div");
  buttons.className = "pick-find-buttons";
  const go = document.createElement("button");
  go.type = "button";
  go.className = "edge-panel-all";
  go.textContent = "Highlight";
  go.addEventListener("click", runFind);
  const clear = document.createElement("button");
  clear.type = "button";
  clear.className = "edge-panel-all";
  clear.textContent = "Clear";
  clear.addEventListener("click", () => { clearOverlay(); setStatus(""); });
  buttons.appendChild(go);
  buttons.appendChild(clear);
  panel.appendChild(buttons);

  statusEl = document.createElement("div");
  statusEl.className = "pick-find-status";
  panel.appendChild(statusEl);
}

function setStatus(text) { if (statusEl) statusEl.textContent = text; }

function setPanelOpen(open) {
  panelOpen = open;
  if (!panel) buildPanel();
  if (state.currentCadWrapper && panel.parentElement !== state.currentCadWrapper) {
    state.currentCadWrapper.appendChild(panel);
  }
  panel.classList.toggle("show", panelOpen);
  if (panelOpen) textarea.focus();
}

async function runFind() {
  if (!state.mountedDetail || state.mountedDetail.type !== "step") return;
  const { picks, files } = parsePicks(textarea.value);
  clearOverlay();
  if (!picks.length && !files.length) { setStatus("nothing recognizable in the paste"); return; }

  // A file: line names where the picks live — go there first. The load
  // swaps the model inside the open modal (same flow live.js uses); the
  // hash is rewritten in place so close/back behave as if the user had
  // opened this file directly.
  const wanted = files.length ? pickFileToViewerPath(files[0]) : null;
  if (wanted && wanted !== state.mountedDetail.file) {
    setStatus(`opening ${wanted.split("/").pop()}…`);
    await loadStepFile(wanted);
    if (!state.mountedDetail || state.mountedDetail.file !== wanted) {
      setStatus(`couldn't open ${wanted}`);
      return;
    }
    state.currentDetail = { type: "step", file: wanted };
    history.replaceState(null, "", "#step:" + encodeURIComponent(wanted));
    const pill = document.querySelector(".cv-filename");
    if (pill) pill.textContent = wanted.split("/").pop().replace(/\.step$/i, "");
  }
  if (!picks.length) { setStatus("opened — no picks to highlight"); return; }

  const { edges, faces } = getFindData();
  const results = matchPicks(picks, edges, faces);

  const box = new THREE.Box3();
  let matched = 0;
  for (const r of results) {
    if (r.type === "edge") { addEdgeHighlight(edges[r.index], box); matched++; }
    else if (r.type === "face") { addFaceHighlight(r.index, box); matched++; }
    else if (r.type === "point") { addPointHighlight(r.pick.p, box); matched++; }
  }
  setStatus(`${matched}/${results.length} matched`);
  flyToBox(box);
}

// --- public API ---
export function clearPickFind() {
  clearOverlay();
  setStatus("");
  flyToken++; // cancel an in-flight fly-to
}

export function makePickFindToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "pick-find-toggle";
  btn.textContent = "Find picks";
  btn.title = "Paste pick text to highlight it on the model";
  btn.addEventListener("click", () => setPanelOpen(!panelOpen));
  return btn;
}
