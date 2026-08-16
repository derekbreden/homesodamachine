// Find box — the edge picker's round trip, and the way in for anyone who
// only knows what a thing is CALLED. Type a component name (`fluid-17`,
// `seaflo-pump`, or just `tee` for all seven) and every solid answering to
// it lights up. Paste pick text — a copy-all blob, a single row, a whole
// multi-pick message from either side of the conversation — and every
// recognizable pick in it is matched against the loaded model's
// reconstructed edges and classified faces. Both land in one overlay,
// framed by one camera move: the box finds things, however you name them.
//
// Name matching ignores case and separators and widens to substrings only
// when nothing matches exactly (pick-format.js), so there is no format to
// memorize. Pick matching is nearest-entity with a tolerance, so the
// 3-decimal rounding in copied blobs and agent-composed lines is fine.
// Whatever fails to match just counts against the status readout — a stale
// pick from an older revision of a part fails soft.

import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, renderer, controls } from "./scene.js";
import { state } from "./state.js";
import { parsePicks, matchPicks, matchNames, pickFileToViewerPath } from "./pick-format.js";
import { getFindData, faceHighlightGeometry } from "./edge-picker.js";
import { scenePartNames } from "./part-highlight.js";
import { jumpToStep } from "./step-nav.js";
import { makeToolButton } from "./tool-rail.js";

const FIND = 0xff5ce1; // found-entity highlight (magenta — distinct from select/hover)
const EDGE_THRESHOLD_DEG = 30; // feature-edge angle for a whole-solid highlight

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

// A whole named solid: its feature edges plus a faint shell, depth-test off
// so it reads through the enclosure walls. Same shape as part-highlight.js's
// scorecard highlight, in the find box's own magenta — one color for
// everything this box turned up, whether it was named or pasted.
function addPartHighlight(name, box) {
  if (!state.currentGroup) return;
  const seen = new Set();
  for (const mesh of state.currentGroup.children) {
    // Locally hidden stays hidden — the same rule the pickers and the scorecard
    // highlight keep (component-picker.js).
    if (!mesh.isMesh || mesh.name !== name || mesh.visible === false
        || seen.has(mesh.geometry)) continue;
    seen.add(mesh.geometry); // front + back share one geometry — one highlight per solid
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG),
      new THREE.LineBasicMaterial({ color: FIND, transparent: true, opacity: 0.95, depthTest: false, depthWrite: false }),
    );
    edges.renderOrder = 998;
    overlay.add(edges);
    const shell = new THREE.Mesh(mesh.geometry.clone(), new THREE.MeshBasicMaterial({
      color: FIND, transparent: true, opacity: 0.16, side: THREE.DoubleSide,
      depthWrite: false, depthTest: false,
    }));
    shell.renderOrder = 997;
    overlay.add(shell);
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    box.union(mesh.geometry.boundingBox);
  }
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
let toggleBtn = null;

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
  textarea.placeholder = "Type a part name — fluid-17, seaflo-pump, tee\nor paste pick text — edge / face / click lines";
  textarea.spellcheck = false;
  // Enter runs it, because a name is one word and reaching for a button to
  // finish typing one word is the wrong shape. Shift+Enter still breaks the
  // line, for a hand-assembled list.
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); runFind(); }
  });
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
  if (toggleBtn) toggleBtn.setAttribute("aria-expanded", panelOpen ? "true" : "false");
  if (panelOpen) textarea.focus();
  // Closing hides the element holding focus, which drops focus to the document
  // — outside the <dialog>, where Escape stops reaching it. Hand focus back to
  // the control the box was opened from, so the key that dismissed the box
  // dismisses the viewer next.
  else if (toggleBtn && panel.contains(document.activeElement)) toggleBtn.focus();
}

// What the name half of a run turned up: the parts it lit, then whatever it
// couldn't place. Both halves matter — an unknown name is usually a typo or
// a part that lives in a different file, and saying so beats a silent zero.
const SHOWN_NAMES = 6;

function nameStatus(hits) {
  const out = [];
  const found = [...new Set(hits.flatMap((h) => h.names))];
  if (found.length) {
    const head = found.slice(0, SHOWN_NAMES).join(", ");
    const rest = found.length > SHOWN_NAMES ? ` +${found.length - SHOWN_NAMES}` : "";
    out.push(`${found.length} part${found.length === 1 ? "" : "s"}: ${head}${rest}`);
  }
  const missed = hits.filter((h) => !h.names.length).map((h) => h.query);
  if (missed.length) out.push(`nothing named ${missed.join(", ")}`);
  return out.join(" · ");
}

async function runFind() {
  // The box is on screen from the moment the modal opens; a big assembly is
  // still parsing for seconds after that. Say so rather than doing nothing.
  if (!state.mountedDetail || state.mountedDetail.type !== "step") {
    setStatus("still loading the model — try again in a moment");
    return;
  }
  const { picks, files, names } = parsePicks(textarea.value);
  clearOverlay();
  if (!picks.length && !files.length && !names.length) {
    setStatus("nothing recognizable — type a part name, or paste pick text");
    return;
  }

  // A file: line names where the picks live — go there first. step-nav.js
  // swaps the model inside the open modal and brings the rest of what the modal
  // is showing with it (name, scorecard, which file the editor writes to),
  // rewriting the hash in place so close/back behave as if this file had
  // been opened directly.
  const wanted = files.length ? pickFileToViewerPath(files[0]) : null;
  if (wanted && wanted !== state.mountedDetail.file) {
    setStatus(`opening ${wanted.split("/").pop()}…`);
    if (!(await jumpToStep(wanted))) {
      setStatus(`couldn't open ${wanted}`);
      return;
    }
  }
  if (!picks.length && !names.length) { setStatus("opened — nothing to highlight"); return; }

  const box = new THREE.Box3();
  const status = [];

  // Names first — they're resolved against the meshes, which are already
  // built, while the picks may still be waiting on the edge reconstruction.
  const nameHits = matchNames(names, scenePartNames());
  if (nameHits.length) {
    for (const name of new Set(nameHits.flatMap((h) => h.names))) addPartHighlight(name, box);
    status.push(nameStatus(nameHits));
  }

  if (picks.length) {
    const { edges, faces } = getFindData();
    const results = matchPicks(picks, edges, faces);
    let matched = 0;
    for (const r of results) {
      if (r.type === "edge") { addEdgeHighlight(edges[r.index], box); matched++; }
      else if (r.type === "face") { addFaceHighlight(r.index, box); matched++; }
      else if (r.type === "point") { addPointHighlight(r.pick.p, box); matched++; }
    }
    status.push(`${matched}/${results.length} picks matched`);
  }

  setStatus(status.filter(Boolean).join(" · "));
  flyToBox(box);
}

// --- public API ---
// Highlights only — step.js calls this on every load, including the swaps the
// box itself drives, and a box that closed the moment it found something would
// be answering out of an empty room.
export function clearPickFind() {
  clearOverlay();
  setStatus("");
  flyToken++; // cancel an in-flight fly-to
}

// The modal is going. The panel and its text outlive it (the box reopens
// holding the last query), so what has to reset is the open flag — otherwise
// the first Find click in the next modal toggles a panel nothing can see.
export function closePickFind() {
  clearPickFind();
  panelOpen = false;
  if (panel) panel.classList.remove("show");
  toggleBtn = null;
}

// Escape's first stop while the box is open. Answers whether it took the key.
export function closeTopPickFind() {
  if (!panelOpen) return false;
  setPanelOpen(false);
  return true;
}

export function makePickFindToggle() {
  const btn = makeToolButton({
    className: "pick-find-toggle",
    label: "Find",
    icon: "find",
    title: "Type a part name, or paste pick text, to highlight it on the model",
    onClick: () => setPanelOpen(!panelOpen),
  });
  btn.setAttribute("aria-expanded", panelOpen ? "true" : "false");
  toggleBtn = btn;
  return btn;
}
