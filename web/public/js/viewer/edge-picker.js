// Edge picker for the CAD viewer. A toggle (stacked above the x-ray toggle,
// persisted per-browser in localStorage under "step-edge-pick") that turns the
// loaded STEP into a clickable surface: hover an edge to highlight it, click to
// select it, and copy a text blob describing it. Built so the user can point at
// a feature that isn't aligned to a cardinal axis — a rotated tangent line, a
// fillet arc, a hole rim — by handing the agent the exact geometry instead of
// eyeballing a ruler tick.
//
// occt-import-js (0.0.23) gives us a triangle mesh per solid plus `brep_faces`
// (each entry is a [first,last] range of TRIANGLE indices belonging to one BREP
// face) — but NO edges. So we reconstruct the real BREP edges from the face
// topology: a tessellation segment shared by two triangles of DIFFERENT faces
// lies on a BREP edge. Because tessellation duplicates vertices at a face
// boundary (each face carries its own normal), we match those shared segments
// by POSITION, not vertex index. Every segment along one BREP edge borders the
// same pair of faces, so we group boundary segments by their unordered
// face-pair and chain each group end-to-end. That splits cleanly at real BREP
// vertices (where the face-pair changes) and naturally drops cylinder seams
// (same face on both sides → never collected). Chain endpoints land on true
// BREP vertices, so an edge's reported endpoints are exact; interior points sit
// on the tessellated curve (within deflection) which is plenty for a click.
//
// Picking is screen-space: project every edge segment to pixels and take the
// one nearest the cursor (front-most on a near tie). Zoom-independent, and the
// click snaps onto the edge so the reported point is ON the geometry, not a
// float in space. Reconstruction is lazy (first enable / first pick) and cached
// per loaded model; setActiveEdges() invalidates it on each new load.

import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";

const LS_KEY = "step-edge-pick";
const PICK_THRESHOLD_PX = 11; // cursor-to-edge distance that counts as a hit
const QUANT = 1e4;            // position grid for boundary matching (0.1 micron)
const STRAIGHT_TOL = 1e-3;    // max deviation from the chord to call an edge straight
const HIGHLIGHT = 0xffd400;   // selected edge (warm yellow)
const HOVER = 0x59d0ff;       // hovered edge (cool cyan)
const ENDPOINT = 0xff8c3b;    // endpoint / center markers (orange)
const CLICKPOINT = 0x7CFF8A;  // click-on-edge marker (green)

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

// --- edge data (lazy, per loaded model) ---
let edgeSource = null;  // occt result.meshes for the live model
let activeEdges = null; // reconstructed BREP edges, or null until built

export function setActiveEdges(result) {
  edgeSource = (result && result.meshes) || null;
  activeEdges = null; // invalidate — rebuild on demand
  clearSelection();
  setHover(null);
}

function ensureEdges() {
  if (activeEdges) return activeEdges;
  activeEdges = edgeSource ? reconstructEdges(edgeSource) : [];
  return activeEdges;
}

// --- BREP edge reconstruction from face-boundary topology ---
function reconstructEdges(meshes) {
  const edges = [];
  let faceBase = 0; // namespace face ids across meshes so pairs don't merge

  for (const mesh of meshes) {
    const pos = mesh.attributes && mesh.attributes.position && mesh.attributes.position.array;
    const idx = mesh.index && mesh.index.array;
    const faces = mesh.brep_faces;
    if (!pos || !idx || !faces) { faceBase += faces ? faces.length : 0; continue; }

    const triCount = idx.length / 3;
    const triFace = new Int32Array(triCount).fill(-1);
    faces.forEach((f, fi) => {
      for (let t = f.first; t <= f.last; t++) triFace[t] = faceBase + fi;
    });

    // vertex index -> position key; key -> the exact Vector3 (first seen)
    const keyToPos = new Map();
    const keyOf = (vi) => {
      const x = pos[vi * 3], y = pos[vi * 3 + 1], z = pos[vi * 3 + 2];
      const k = Math.round(x * QUANT) + "," + Math.round(y * QUANT) + "," + Math.round(z * QUANT);
      if (!keyToPos.has(k)) keyToPos.set(k, new THREE.Vector3(x, y, z));
      return k;
    };

    // mesh-edge (by unordered position pair) -> set of bordering face ids
    const meshEdges = new Map();
    const addMeshEdge = (p, q, f) => {
      if (p === q) return;
      const id = p < q ? p + "|" + q : q + "|" + p;
      let rec = meshEdges.get(id);
      if (!rec) { rec = { a: p, b: q, faces: new Set() }; meshEdges.set(id, rec); }
      rec.faces.add(f);
    };
    for (let t = 0; t < triCount; t++) {
      const ka = keyOf(idx[t * 3]), kb = keyOf(idx[t * 3 + 1]), kc = keyOf(idx[t * 3 + 2]);
      const f = triFace[t];
      addMeshEdge(ka, kb, f);
      addMeshEdge(kb, kc, f);
      addMeshEdge(kc, ka, f);
    }

    // boundary segments grouped by unordered face-pair
    const byPair = new Map();
    for (const rec of meshEdges.values()) {
      if (rec.faces.size < 2) continue; // interior to one face (incl. seams)
      const fs = [...rec.faces].sort((p, q) => p - q);
      const pk = fs[0] + "," + fs[1]; // clamp to first two if non-manifold
      let arr = byPair.get(pk);
      if (!arr) { arr = []; byPair.set(pk, arr); }
      arr.push(rec);
    }

    for (const segs of byPair.values()) {
      for (const path of chainSegments(segs)) {
        edges.push(makeEdge(path.map((k) => keyToPos.get(k))));
      }
    }
    faceBase += faces.length;
  }

  edges.forEach((e, i) => { e.id = i; });
  return edges;
}

// Chain boundary segments (all sharing one face-pair) into polylines. Walks
// through degree-2 nodes and stops at a node of any other degree — a real BREP
// vertex (junction or open end). Loops (a closed rim with no vertex) come back
// to their start.
function chainSegments(segs) {
  const adj = new Map();
  const link = (n, to, i) => {
    let a = adj.get(n);
    if (!a) { a = []; adj.set(n, a); }
    a.push({ to, i });
  };
  segs.forEach((s, i) => { link(s.a, s.b, i); link(s.b, s.a, i); });

  const used = new Array(segs.length).fill(false);
  const out = [];
  // open chains first (start at degree-1 ends), then whatever's left (loops)
  const starts = [...adj.keys()].filter((n) => adj.get(n).length === 1).concat([...adj.keys()]);

  for (const start of starts) {
    let edge = adj.get(start).find((e) => !used[e.i]);
    if (!edge) continue;
    let cur = start;
    const path = [cur];
    while (edge) {
      used[edge.i] = true;
      cur = edge.to;
      path.push(cur);
      const inc = adj.get(cur);
      if (inc.length !== 2) break; // BREP vertex
      edge = inc.find((e) => !used[e.i]);
    }
    if (path.length >= 2) out.push(path);
  }
  return out;
}

// Classify a polyline into a self-describing edge record.
function makeEdge(points) {
  const a = points[0], b = points[points.length - 1];
  let length = 0;
  for (let i = 1; i < points.length; i++) length += points[i].distanceTo(points[i - 1]);
  const closed = points.length > 2 && a.distanceTo(b) < 1e-3;

  if (closed) {
    const center = new THREE.Vector3();
    for (let i = 0; i < points.length - 1; i++) center.add(points[i]);
    center.multiplyScalar(1 / (points.length - 1));
    let r = 0;
    for (let i = 0; i < points.length - 1; i++) r += points[i].distanceTo(center);
    return { points, a, b, length, kind: "loop", center, radius: r / (points.length - 1) };
  }

  // straight: every interior point lies on the chord
  const ab = b.clone().sub(a);
  const l2 = ab.lengthSq() || 1;
  const tmp = new THREE.Vector3(), proj = new THREE.Vector3();
  let maxDev = 0;
  for (const p of points) {
    const t = tmp.copy(p).sub(a).dot(ab) / l2;
    proj.copy(ab).multiplyScalar(t).add(a);
    maxDev = Math.max(maxDev, p.distanceTo(proj));
  }
  if (maxDev < STRAIGHT_TOL) return { points, a, b, length, kind: "straight" };

  // curved: try to fit a circle (arc) so we can report a radius
  const fit = fitCircle(points);
  if (fit) return { points, a, b, length, kind: "arc", center: fit.center, radius: fit.radius };
  return { points, a, b, length, kind: "curve" };
}

// Circumcircle through the polyline's two ends and its midpoint, accepted only
// if every sample point sits on it. Returns {center, radius} or null.
function fitCircle(points) {
  const p1 = points[0];
  const p2 = points[Math.floor(points.length / 2)];
  const p3 = points[points.length - 1];
  const ab = p2.clone().sub(p1);
  const ac = p3.clone().sub(p1);
  const n = ab.clone().cross(ac);
  const n2 = n.lengthSq();
  if (n2 < 1e-12) return null; // collinear sample

  // circumcenter = p1 + ( |ac|^2 (n x ab) + |ab|^2 (ac x n) ) / (2 |n|^2)
  const term1 = n.clone().cross(ab).multiplyScalar(ac.lengthSq());
  const term2 = ac.clone().cross(n).multiplyScalar(ab.lengthSq());
  const center = term1.add(term2).multiplyScalar(1 / (2 * n2)).add(p1);
  const radius = center.distanceTo(p1);

  const tol = Math.max(0.05, radius * 0.02);
  for (const p of points) {
    if (Math.abs(p.distanceTo(center) - radius) > tol) return null;
  }
  return { center, radius };
}

// --- screen-space picking ---
const _vp = new THREE.Matrix4();
function projectPixels(p, rect, e) {
  const x = e[0] * p.x + e[4] * p.y + e[8] * p.z + e[12];
  const y = e[1] * p.x + e[5] * p.y + e[9] * p.z + e[13];
  const z = e[2] * p.x + e[6] * p.y + e[10] * p.z + e[14];
  const w = e[3] * p.x + e[7] * p.y + e[11] * p.z + e[15];
  if (w <= 1e-6) return null; // behind camera
  return { x: (x / w * 0.5 + 0.5) * rect.width, y: (-y / w * 0.5 + 0.5) * rect.height, depth: z / w };
}

function segDistPx(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay;
  const l2 = dx * dx + dy * dy;
  let t = l2 ? ((px - ax) * dx + (py - ay) * dy) / l2 : 0;
  t = t < 0 ? 0 : t > 1 ? 1 : t;
  const cx = ax + t * dx, cy = ay + t * dy;
  return { d: Math.hypot(px - cx, py - cy), t };
}

function pickEdge(clientX, clientY) {
  const edges = ensureEdges();
  if (!edges.length) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  const px = clientX - rect.left, py = clientY - rect.top;
  const e = _vp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse).elements;

  let best = null;
  for (const edge of edges) {
    const pts = edge.points;
    let prev = projectPixels(pts[0], rect, e);
    for (let i = 1; i < pts.length; i++) {
      const cur = projectPixels(pts[i], rect, e);
      if (prev && cur) {
        const { d, t } = segDistPx(px, py, prev.x, prev.y, cur.x, cur.y);
        if (d <= PICK_THRESHOLD_PX) {
          const depth = prev.depth + (cur.depth - prev.depth) * t;
          // nearest to cursor; front-most breaks a near tie (overlapping edges)
          if (!best || d < best.d - 1.5 || (Math.abs(d - best.d) <= 1.5 && depth < best.depth)) {
            best = { edge, d, depth, point: pts[i - 1].clone().lerp(pts[i], t) };
          }
        }
      }
      prev = cur;
    }
  }
  return best;
}

// --- overlay (highlight line + markers), drawn over everything ---
const overlay = new THREE.Group();
overlay.name = "edge-picker";
overlay.renderOrder = 999;
scene.add(overlay);

const selLineMat = new LineMaterial({ color: HIGHLIGHT, linewidth: 4.5, depthTest: false, transparent: true });
const hoverLineMat = new LineMaterial({ color: HOVER, linewidth: 3, depthTest: false, transparent: true, opacity: 0.95 });
selLineMat.depthWrite = false;
hoverLineMat.depthWrite = false;

function syncLineRes() {
  const w = renderer.domElement.width, h = renderer.domElement.height;
  if (w && h) { selLineMat.resolution.set(w, h); hoverLineMat.resolution.set(w, h); }
}
new ResizeObserver(syncLineRes).observe(renderer.domElement);
syncLineRes();

function lineFromPoints(points, mat) {
  const flat = [];
  for (const p of points) flat.push(p.x, p.y, p.z);
  const geo = new LineGeometry();
  geo.setPositions(flat);
  const line = new Line2(geo, mat);
  line.renderOrder = 999;
  line.frustumCulled = false;
  return line;
}

function markerPoints(vecs, color) {
  const flat = [];
  for (const v of vecs) flat.push(v.x, v.y, v.z);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(flat, 3));
  const mat = new THREE.PointsMaterial({ color, size: 11, sizeAttenuation: false, depthTest: false, transparent: true });
  const pts = new THREE.Points(geo, mat);
  pts.renderOrder = 1000;
  pts.frustumCulled = false;
  return pts;
}

function disposeObj(obj) {
  if (!obj) return;
  overlay.remove(obj);
  if (obj.geometry) obj.geometry.dispose();
  if (obj.material && obj.material.dispose && obj.material !== selLineMat && obj.material !== hoverLineMat) {
    obj.material.dispose();
  }
}

// --- selection + hover state ---
let selObjs = { line: null, ends: null, click: null };
let selection = null;
let hoverLine = null;
let hoverId = -1;

function clearSelection() {
  disposeObj(selObjs.line); disposeObj(selObjs.ends); disposeObj(selObjs.click);
  selObjs = { line: null, ends: null, click: null };
  selection = null;
  hidePanel();
}

function drawSelection(sel) {
  clearSelection();
  syncLineRes();
  const e = sel.edge;
  selObjs.line = lineFromPoints(e.points, selLineMat);
  overlay.add(selObjs.line);
  const endVecs = e.kind === "loop" ? [e.center] : [e.a, e.b];
  selObjs.ends = markerPoints(endVecs, ENDPOINT);
  overlay.add(selObjs.ends);
  selObjs.click = markerPoints([sel.point], CLICKPOINT);
  overlay.add(selObjs.click);
  selection = sel;
  setHover(null);
  showPanel(sel);
}

function setHover(hit) {
  const id = hit ? hit.edge.id : -1;
  if (id === hoverId) return;
  hoverId = id;
  disposeObj(hoverLine);
  hoverLine = null;
  if (hit && (!selection || hit.edge.id !== selection.edge.id)) {
    syncLineRes();
    hoverLine = lineFromPoints(hit.edge.points, hoverLineMat);
    overlay.add(hoverLine);
  }
}

// --- text formatting for the copy blob ---
function fnum(n) { const s = n.toFixed(3); return s === "-0.000" ? "0.000" : s; }
function fpt(v) { return `(${fnum(v.x)}, ${fnum(v.y)}, ${fnum(v.z)})`; }

function edgeText(sel) {
  const e = sel.edge;
  if (e.kind === "loop") {
    return `circle ⌀${(e.radius * 2).toFixed(3)} · center ${fpt(e.center)} · circumference ${e.length.toFixed(3)}`;
  }
  let tail;
  if (e.kind === "straight") tail = `len ${e.length.toFixed(3)} · straight`;
  else if (e.kind === "arc") tail = `len ${e.length.toFixed(3)} · arc r=${e.radius.toFixed(3)}`;
  else tail = `len ${e.length.toFixed(3)} · curve`;
  return `${fpt(e.a)} → ${fpt(e.b)} · ${tail}`;
}
function endsText(sel) {
  const e = sel.edge;
  return e.kind === "loop" ? fpt(e.center) : `${fpt(e.a)} · ${fpt(e.b)}`;
}
function clickText(sel) { return fpt(sel.point); }
function allText(sel) {
  const endsLabel = sel.edge.kind === "loop" ? "center" : "endpoints";
  return `edge: ${edgeText(sel)}\n${endsLabel}: ${endsText(sel)}\nclick: ${clickText(sel)}`;
}

// --- copy panel ---
let panel = null;
let panelRows = null;

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "edge-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Edge";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", () => clearSelection());
  head.appendChild(title);
  head.appendChild(close);
  panel.appendChild(head);

  const mkRow = (label) => {
    const row = document.createElement("div");
    row.className = "edge-row";
    const lab = document.createElement("span");
    lab.className = "edge-row-label";
    lab.textContent = label;
    const val = document.createElement("span");
    val.className = "edge-row-val";
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "edge-row-copy";
    copy.textContent = "Copy";
    row.appendChild(lab);
    row.appendChild(val);
    row.appendChild(copy);
    panel.appendChild(row);
    const doCopy = () => copyText(val.textContent, copy);
    val.addEventListener("click", doCopy);
    copy.addEventListener("click", doCopy);
    return { row, lab, val, copy };
  };

  panelRows = {
    edge: mkRow("Edge"),
    ends: mkRow("Endpoints"),
    click: mkRow("Click"),
  };

  const all = document.createElement("button");
  all.type = "button";
  all.className = "edge-panel-all";
  all.textContent = "Copy all";
  all.addEventListener("click", () => { if (selection) copyText(allText(selection), all); });
  panel.appendChild(all);
  panel._allBtn = all;
}

function showPanel(sel) {
  if (!panel) buildPanel();
  if (state.currentCadWrapper && panel.parentElement !== state.currentCadWrapper) {
    state.currentCadWrapper.appendChild(panel);
  }
  panelRows.edge.val.textContent = edgeText(sel);
  panelRows.ends.val.textContent = endsText(sel);
  panelRows.ends.lab.textContent = sel.edge.kind === "loop" ? "Center" : "Endpoints";
  panelRows.click.val.textContent = clickText(sel);
  panel.classList.add("show");
}

function hidePanel() { if (panel) panel.classList.remove("show"); }

function copyText(text, btn) {
  const done = () => {
    const prev = btn.textContent;
    btn.textContent = "✓";
    btn.classList.add("edge-copied");
    setTimeout(() => { btn.textContent = prev; btn.classList.remove("edge-copied"); }, 1100);
  };
  try {
    navigator.clipboard.writeText(text).then(done, () => fallbackCopy(text, done));
  } catch { fallbackCopy(text, done); }
}
function fallbackCopy(text, done) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand("copy"); done(); } catch {}
  document.body.removeChild(ta);
}

// --- pointer wiring (attached once; act only when enabled + STEP open) ---
let downX = 0, downY = 0;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }

renderer.domElement.addEventListener("pointerdown", (e) => {
  downX = e.clientX; downY = e.clientY;
});
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!active()) return;
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return; // a drag, not a click
  const hit = pickEdge(e.clientX, e.clientY);
  if (hit) drawSelection(hit);
  else clearSelection(); // click on empty space clears
});
renderer.domElement.addEventListener("pointermove", (e) => {
  if (!active() || e.buttons !== 0) { return; }
  setHover(pickEdge(e.clientX, e.clientY));
});

// --- public API ---
export function clearEdgePicker() {
  clearSelection();
  setHover(null);
  edgeSource = null;
  activeEdges = null;
}

export function setEdgePickEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  if (!enabled) { clearSelection(); setHover(null); }
}

export function isEdgePickEnabled() { return enabled; }

export function makeEdgePickToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "edge-pick-toggle";
  function refresh() {
    btn.textContent = enabled ? "Select edge: on" : "Select edge: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => { setEdgePickEnabled(!enabled); refresh(); });
  refresh();
  return btn;
}
