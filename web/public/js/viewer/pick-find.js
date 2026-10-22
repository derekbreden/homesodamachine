// Find box — the edge picker's round trip, and the way in for anyone who
// only knows what a thing is called. Type a material description, part number
// or CAD key (`Faucet lever`, `HSM-000090`, `fluid-17`) and its bodies light
// up. Paste pick text — a copy-all blob, a single row, a whole
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
import { getFindData, faceHighlightGeometry, faceNearest, boxHighlightGeometry } from "./edge-picker.js";
import { scenePartNames } from "./part-highlight.js";
import { jumpToStep } from "./step-nav.js";
import { makeToolButton } from "./tool-rail.js";
import { materialForFile, materialForComponent, searchMaterials, explodeBom, occurrenceBodies, matchesBody } from "/contracts/materials.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

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
  clearLabels();
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

// The middle of a lit surface, area-weighted: where a label on a face or a box
// stands. On a curved face it falls inside the curve (a bore's, on its axis),
// which still points at the feature.
function surfaceMiddle(geo) {
  const p = geo.getAttribute("position").array, mid = new THREE.Vector3(), c = new THREE.Vector3();
  const a = new THREE.Vector3(), b = new THREE.Vector3(), d = new THREE.Vector3();
  let total = 0;
  for (let i = 0; i < p.length; i += 9) {
    a.fromArray(p, i); b.fromArray(p, i + 3); d.fromArray(p, i + 6);
    const area = b.clone().sub(a).cross(d.clone().sub(a)).length();
    mid.addScaledVector(c.copy(a).add(b).add(d).multiplyScalar(1 / 3), area);
    total += area;
  }
  return total ? mid.multiplyScalar(1 / total) : null;
}

function addFaceHighlight(gid, box) {
  const geo = faceHighlightGeometry(gid);
  return geo ? addSurfaceHighlight(geo, box) : null;
}

// Returns the lit mesh, and where on it a label stands.
function addSurfaceHighlight(geo, box) {
  geo.computeBoundingBox();
  box.union(geo.boundingBox);
  const mat = new THREE.MeshBasicMaterial({
    color: FIND, transparent: true, opacity: 0.3, side: THREE.DoubleSide,
    depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.renderOrder = 997;
  overlay.add(mesh);
  return { lit: mesh, at: surfaceMiddle(geo) };
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
// to frame them — same ease + duration as the reset-view flight. A `view:`
// line names the direction instead, upright, so a link can show a feature
// from the side it is seen from: inside a wall, under a ledge.
let flyToken = 0;
function flyToBox(box, view = null) {
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 2);
  let dir = camera.position.clone().sub(controls.target).normalize();
  if (view) {
    const az = THREE.MathUtils.degToRad(view.az), el = THREE.MathUtils.degToRad(view.el);
    dir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el));
    camera.up.set(0, 0, 1);
  }
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
  textarea.placeholder = "Type a material name, part number or CAD body\nor paste pick text — edge / face / click lines";
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
  // a visible control for the box, so the key that dismissed the box
  // dismisses the viewer next.
  else if (toggleBtn && panel.contains(document.activeElement)) {
    const drawer = toggleBtn.closest(".tool-drawer.compact:not([open])");
    (drawer?.querySelector("summary") || toggleBtn).focus();
  }
}

// What the name half of a run turned up: the parts it lit, then whatever it
// couldn't place. Both halves matter — an unknown name is usually a typo or
// a part that lives in a different file, and saying so beats a silent zero.
const SHOWN_NAMES = 6;

function materialBodies(query, available) {
  if (query.replace(/[^\p{L}\p{N}]/gu, "").length < 2) return null;
  const catalog = state.materialCatalog, file = state.mountedDetail?.file;
  const parent = materialForFile(catalog, file);
  if (!parent) return null;
  const ids = new Set(searchMaterials(catalog, query).map((material) => material.id));
  if (!ids.size) return null;
  if (ids.has(parent.id)) return [...available];
  const options = { finish: state.faucetFinish };
  const names = explodeBom(catalog, parent.id, options).filter((row) => ids.has(row.material.id))
    .flatMap((row) => occurrenceBodies(catalog, row.path, available, options));
  for (const relation of parent.relations || []) if (ids.has(relation.material))
    names.push(...[...available].filter((name) => relation.bodies?.some((body) => matchesBody(name, body))));
  return [...new Set(names)];
}

function nameStatus(hits) {
  const out = [];
  const found = [...new Set(hits.flatMap((h) => h.names))];
  if (found.length) {
    const labels = [...new Set(found.map((name) => materialForComponent(state.materialCatalog,
      state.mountedDetail?.file, name, { finish: state.faucetFinish })?.description || name))];
    const head = labels.slice(0, SHOWN_NAMES).join(", ");
    const rest = labels.length > SHOWN_NAMES ? ` +${labels.length - SHOWN_NAMES}` : "";
    out.push(`${found.length} CAD bod${found.length === 1 ? "y" : "ies"}: ${head}${rest}`);
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
  const { picks, files, names, view } = parsePicks(textarea.value);
  // Known material descriptions can include units, punctuation and more words
  // than the compact CAD-key grammar used by pasted geometry reports.
  for (const line of textarea.value.split("\n").map((line) => line.trim()).filter(Boolean))
    if (searchMaterials(state.materialCatalog, line).length && !names.includes(line)) names.push(line);
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
  const available = scenePartNames();
  const nameHits = names.map((query) => {
    const bodies = materialBodies(query, available);
    return bodies ? { query, names: bodies } : matchNames([query], available)[0];
  });
  if (nameHits.length) {
    for (const name of new Set(nameHits.flatMap((h) => h.names))) addPartHighlight(name, box);
    status.push(nameStatus(nameHits));
  }

  const labels = [];
  if (picks.length) {
    const { edges, faces } = getFindData();
    const results = matchPicks(picks, edges, faces);
    let matched = 0;
    for (const r of results) {
      const { pick } = r;
      let at = null, lit = null;
      if (r.type === "edge") {
        const e = edges[r.index];
        addEdgeHighlight(e, box);
        at = e.points[Math.floor(e.points.length / 2)];
        matched++;
      } else if (r.type === "face") {
        ({ lit, at } = addFaceHighlight(r.index, box) || {});
        matched++;
      } else if (r.type === "point") {
        addPointHighlight(pick.p, box);
        at = pick.p;
        matched++;
      } else if (r.type === "face-at") {
        // A point no face comes near still marks its spot, and counts against the readout.
        const gid = faceNearest(pick.p);
        if (gid >= 0) { ({ lit } = addFaceHighlight(gid, box) || {}); matched++; } else addPointHighlight(pick.p, box);
        at = pick.p;
      } else if (r.type === "box") {
        const geo = boxHighlightGeometry(pick.lo, pick.hi);
        if (geo) { ({ lit, at } = addSurfaceHighlight(geo, box)); matched++; }
      }
      if (pick.text && at) labels.push({ at: new THREE.Vector3(at.x, at.y, at.z), lit, text: pick.text });
    }
    status.push(`${matched}/${results.length} picks matched`);
  }

  setStatus(status.filter(Boolean).join(" · "));
  flyToBox(box, view);
  showLabels(labels);
}

// --- labels ---
// A pick's quoted words, pinned to it on screen: a dot on the spot, the words
// standing off it on a leader, following it as the view turns. Labels step
// clear of each other and keep inside the view however narrow. One whose spot
// the model hides from this side is drawn faint on a dashed leader: it says
// where the thing is without claiming it can be seen. A label's own lit surface
// does not hide it — the middle of a lit bar lies inside the bar, and what is
// seen of it is the lit face in front. That reading waits for the view to
// settle, since a ray through a whole model costs more than a frame, and is
// skipped on a model too heavy to cast through at all.
const SVGNS = "http://www.w3.org/2000/svg";
const LABEL_CAST_MAX_TRIS = 600000;
const ray = new THREE.Raycaster();
let labelLayer = null, labelMarks = [], labelFrame = 0, labelPose = "", labelSettle = 0;

function showLabels(list) {
  clearLabels();
  const wrapper = state.currentCadWrapper;
  if (!list.length || !wrapper) return;
  labelLayer = document.createElement("div");
  labelLayer.className = "pick-find-labels";
  const svg = document.createElementNS(SVGNS, "svg");
  labelLayer.appendChild(svg);
  labelMarks = list.map(({ at, lit, text }) => {
    const [halo, line, dot] = ["line", "line", "circle"].map((tag) => document.createElementNS(SVGNS, tag));
    halo.setAttribute("class", "pick-find-label-halo");
    line.setAttribute("class", "pick-find-label-line");
    dot.setAttribute("class", "pick-find-label-dot");
    dot.setAttribute("r", "4");
    svg.append(halo, line, dot);
    const words = document.createElement("div");
    words.className = "pick-find-label";
    words.textContent = text;
    labelLayer.appendChild(words);
    return { at, lit, parts: [halo, line, dot, words] };
  });
  wrapper.appendChild(labelLayer);
  const frame = () => { placeLabels(); labelFrame = requestAnimationFrame(frame); };
  labelFrame = requestAnimationFrame(frame);
}

function clearLabels() {
  cancelAnimationFrame(labelFrame);
  clearTimeout(labelSettle);
  labelFrame = 0;
  labelPose = "";
  if (labelLayer) labelLayer.remove();
  labelLayer = null;
  labelMarks = [];
}

function placeLabels() {
  if (!labelLayer || !labelLayer.isConnected) return;
  const W = labelLayer.clientWidth, H = labelLayer.clientHeight;
  const placed = [];
  for (const m of labelMarks) {
    const v = m.at.clone().project(camera);
    const shown = v.z > -1 && v.z < 1;
    m.parts.forEach((el) => { el.style.display = shown ? "" : "none"; });
    if (!shown) continue;
    const [halo, line, dot, words] = m.parts;
    const x = (v.x + 1) / 2 * W, y = (1 - v.y) / 2 * H;
    const dx = x > W * 0.6 ? -22 : 22, dy = -22;
    const w = words.offsetWidth, h = words.offsetHeight;
    const lx = Math.max(4, Math.min(W - w - 4, x + dx - (dx < 0 ? w : 0)));
    const fit = (top) => Math.max(4, Math.min(H - h - 4, top));
    const clear = (top) => placed.every((b) => lx >= b.x + b.w + 3 || lx + w + 3 <= b.x
      || top >= b.y + b.h + 3 || top + h + 3 <= b.y);
    const tries = [fit(y + dy - h / 2)];
    for (const b of placed) tries.push(b.y - h - 4, b.y + b.h + 4);
    const ly = tries.find((top) => top === fit(top) && clear(top)) ?? tries[0];
    placed.push({ x: lx, y: ly, w, h });
    const ex = dx < 0 ? lx + w : lx, ey = ly + h / 2;
    for (const el of [halo, line]) {
      el.setAttribute("x1", x); el.setAttribute("y1", y);
      el.setAttribute("x2", ex); el.setAttribute("y2", ey);
    }
    dot.setAttribute("cx", x);
    dot.setAttribute("cy", y);
    words.style.transform = `translate(${lx}px, ${ly}px)`;
  }
  const pose = [...camera.position.toArray(), ...controls.target.toArray(), W, H]
    .map((n) => n.toFixed(3)).join(",");
  if (pose !== labelPose) {
    labelPose = pose;
    clearTimeout(labelSettle);
    labelSettle = setTimeout(hideLabels, 150);
  }
}

function hideLabels() {
  const solids = (state.currentGroup?.children || []).filter((c) => c.isMesh && c.visible !== false);
  const tris = solids.reduce((n, c) => n + (c.geometry.index ? c.geometry.index.count : 0) / 3, 0);
  if (tris > LABEL_CAST_MAX_TRIS) return;
  for (const m of labelMarks) {
    const to = m.at.clone().sub(camera.position);
    const dist = to.length();
    ray.set(camera.position, to.normalize());
    ray.far = dist;
    const hit = ray.intersectObjects(solids, false)[0];
    const own = m.lit ? ray.intersectObject(m.lit, false)[0] : null;
    const reach = own ? own.distance : dist;
    const behind = !!hit && hit.distance < reach - Math.max(0.5, reach * 0.004);
    m.parts.forEach((el) => el.classList.toggle("is-behind", behind));
  }
}

// --- a find carried by a link ---
// `#step:<path>?find=<pick text>` (route.js) opens the model and runs its pick
// text through this box once the model is drawn, so a conversation can point at
// a feature on the piece itself, lit and labelled, with one link. The box keeps
// the text, for whoever opens it to see what lit and why.
let pendingFind = null;

export function findWhenMounted(file, text) {
  pendingFind = { file, text };
  if (state.mountedDetail?.type === "step" && state.mountedDetail.file === file) runPendingFind();
}

function runPendingFind() {
  const { text } = pendingFind;
  pendingFind = null;
  if (!panel) buildPanel();
  textarea.value = text;
  // A frame on, past the camera the open restores, which is the one it flies from.
  requestAnimationFrame(() => runFind());
}

window.addEventListener(HSM_EVENTS.STEP_MOUNTED, (e) => {
  if (pendingFind && e.detail?.file === pendingFind.file) runPendingFind();
});

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
    title: "Type a material name, part number or CAD body, or paste pick text, to highlight it on the model",
    onClick: () => setPanelOpen(!panelOpen),
  });
  btn.setAttribute("aria-expanded", panelOpen ? "true" : "false");
  toggleBtn = btn;
  return btn;
}
