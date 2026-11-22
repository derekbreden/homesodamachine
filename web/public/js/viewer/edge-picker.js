// Edge + face picker for the CAD viewer. A toggle (stacked above the x-ray
// toggle, persisted per-browser in localStorage under "step-edge-pick") that
// turns the loaded STEP into a clickable surface: hover an edge to highlight
// it, click to select it, and copy a text blob describing it. A click whose
// nearest edge sits occluded BEHIND the surface under the cursor selects the
// FACE instead (edge picking is screen-space and ignores occlusion, so on a
// busy model some hidden edge is almost always within threshold — the depth
// comparison is what makes mid-face clicks mean the face). Built so the user
// can point at a feature that isn't aligned to a cardinal axis — a rotated
// tangent line, a fillet arc, a hole rim, a pocket floor — by handing the
// agent the exact geometry instead of eyeballing a ruler tick.
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
// Each edge remembers its bordering face pair, and faces are classified from
// their sampled vertices + normals into plane / cylinder / curved (swept
// b-splines get no compact params). The copy blob carries the edge, both
// adjacent faces, and the click point — faces are usually what a pick is
// really about, and their parameters (a plane's offset, a cylinder's radius)
// are self-identifying against the generating CAD script. The same face data
// feeds the find box (pick-find.js), which parses pasted blobs back into
// highlighted entities via pick-format.js.
//
// AND THE BLOB NAMES THE SURFACE IT WAS TAKEN OFF. What is drawn here is the `.step.mesh`
// whenever one stands beside the STEP, and under `pack.BUNDLED_PAYLOAD_DIRS` that payload
// carries surface the solid does not — so `fileLine` writes the payload's own name, what its
// reduction cost, and the digest it descends from. An edge also states how many tessellation
// segments it is, and a fitted arc is reported only when its radius accounts for the path
// length actually walked: a decimated payload bridges a feature it could not draw with long
// skinny triangles, and those are pickable, real on this surface, and nothing the solid has.
//
// The cursor's screen-space window selects candidate edge bounds. Projecting their
// segments picks the nearest edge and snaps the click onto it. A worker recovers the
// topology of requested solids, and unchanged solids retain it as the assembly arrives.
//
// While the toggle is on, the whole reconstructed edge set is also drawn as a
// faint always-on layer. The x-ray crease renderer (xray.js) only draws
// dihedrals past its ~30° threshold, so tangent and shallow joins — a shave
// plane running out onto the surface it shaved, a fillet meeting its wall —
// are pickable yet invisible without it. The layer makes "if you can click
// it, you can see it" hold exactly.

import * as THREE from "three";
import { classifyFaceRange, faceIndexAtTriangle } from "./picked-face.js";
import { nearestSurface, visitSurfaceRanges } from "./surface-query.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { showsInFaucetFinish } from "/contracts/faucet-options.js";
import { scene, camera, renderer } from "./scene.js";
import * as sceneState from "./scene.js";
import { state } from "./state.js";
import { addSurfaceActions, surfacePick } from "./surface-actions.js";
import { isXrayEnabled } from "./xray.js";
import { fnum, fpt, formatFace, fileLine, MATCH_TOLERANCE } from "./pick-format.js";
import { roundFitMeasured, arcFitMeasured } from "./round-fit.js";
import { makePanelCollapse } from "./tool-rail.js";

const LS_KEY = "step-edge-pick";
const PICK_THRESHOLD_PX = 11; // cursor-to-edge distance that counts as a hit
const STRAIGHT_TOL = 1e-3;    // max deviation from the chord to call an edge straight
const HIGHLIGHT = 0xffd400;   // selected edge (warm yellow)
const HOVER = 0x59d0ff;       // hovered edge (cool cyan)
const ENDPOINT = 0xff8c3b;    // endpoint / center markers (orange)
const CLICKPOINT = 0x7CFF8A;  // click-on-edge marker (green)

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

// --- edge + face data (lazy, per loaded model) ---
let edgeSource = null;  // occt result.meshes for the live model
let isAssembly = false;
let meshRecs = null, faceTable = null, faceClass = null;
let inspectionRevision = 0;

export function setActiveEdges(result) {
  edgeSource = result?.meshes || null;
  isAssembly = !!(edgeSource && edgeSource.length > 1);
  inspectionRevision++;
  meshRecs = faceTable = faceClass = null;
  if (selection) {
    const source = selection.type === "edge" ? selection.edge.source : selection.source;
    const rec = ensureFaces().find(rec => rec?.mesh === source);
    if (!rec) clearSelection();
    else if (selection.type === "face") selection.gid = rec.base + selection.localFace;
    else selection.edge = describeEdge(rec, topologies.get(source).data, selection.edge.localEdge);
  }
  setHover(null);
  refreshEdgeLayers();
}

function ensureFaces() {
  if (meshRecs) return meshRecs;
  let faceBase = 0;
  faceTable = [];
  const solids = [];
  for (const mesh of state.currentGroup?.children || []) {
    if (mesh.userData.side === "front") solids[mesh.userData.occtIndex] = mesh;
  }
  meshRecs = (edgeSource || []).map((mesh, mi) => {
    const faces = mesh.brep_faces || [];
    const base = faceBase;
    faceBase += faces.length;
    if (!mesh.attributes?.position || !mesh.index || !mesh.brep_faces) return null;
    const solid = solids[mi];
    solid?.updateWorldMatrix(true, false);
    const rec = { mesh, mi, solid, name: mesh.name, faces, base,
      get pos() { return mesh.attributes.position.array; },
      get nrm() { return mesh.attributes.normal?.array; },
      get idx() { return mesh.index.array; },
    };
    faces.forEach((_, fi) => { faceTable[base + fi] = { rec, fi }; });
    return rec;
  });
  return meshRecs;
}

function faceAtTriangle(rec, tri) {
  const index = faceIndexAtTriangle(rec?.faces, tri);
  return index < 0 ? -1 : rec.base + index;
}

// The detailed outline is optional work. Only a requested solid occupies the worker.
const topologies = new WeakMap();
let topologyWorker = null, activeJob = null;
const topologyQueue = [];
function cancelDepartedJobs(wanted) {
  if (activeJob && !wanted.has(activeJob.rec.mesh)) {
    topologyWorker?.terminate();
    topologyWorker = null;
    topologies.delete(activeJob.rec.mesh);
    activeJob.resolve(null);
    activeJob = null;
  }
  for (let i = topologyQueue.length - 1; i >= 0; i--) {
    const job = topologyQueue[i];
    if (wanted.has(job.rec.mesh)) continue;
    topologyQueue.splice(i, 1);
    topologies.delete(job.rec.mesh);
    job.resolve(null);
  }
  runTopologyJob();
}

function runTopologyJob() {
  if (activeJob || !topologyQueue.length) return;
  activeJob = topologyQueue.shift();
  const { rec, resolve, reject } = activeJob;
  try {
    topologyWorker ??= new Worker(new URL("./brep-edges-worker.js", import.meta.url));
    topologyWorker.onmessage = ({ data }) => {
      topologies.set(rec.mesh, { data });
      activeJob = null;
      resolve(data);
      runTopologyJob();
    };
    topologyWorker.onerror = event => {
      topologyWorker.terminate(); topologyWorker = null;
      topologies.delete(rec.mesh); activeJob = null;
      reject(new Error(event.message || "Could not prepare surface edges"));
      runTopologyJob();
    };
    const positions = Float32Array.from(rec.pos), indices = Uint32Array.from(rec.idx);
    const ranges = new Uint32Array(rec.faces.length * 2);
    rec.faces.forEach((face, i) => { ranges[i * 2] = face.first; ranges[i * 2 + 1] = face.last; });
    topologyWorker.postMessage({ positions, indices, ranges }, [positions.buffer, indices.buffer, ranges.buffer]);
  } catch (error) {
    topologies.delete(rec.mesh); activeJob = null; reject(error);
    runTopologyJob();
  }
}

function prepareEdges(rec) {
  const job = topologies.get(rec.mesh);
  if (job) return job.data || job.promise;
  const promise = new Promise((resolve, reject) => topologyQueue.push({ rec, resolve, reject }));
  topologies.set(rec.mesh, { promise });
  runTopologyJob();
  return promise;
}

function describeEdge(rec, data, i) {
  rec.descriptions ??= new Map();
  if (rec.descriptions.has(i)) return rec.descriptions.get(i);
  const points = [];
  for (let p = data.starts[i]; p < data.starts[i + 1]; p++) points.push(new THREE.Vector3().fromArray(data.points, p * 3));
  const edge = makeEdge(points);
  edge.solid = rec.name;
  edge.source = rec.mesh;
  edge.localEdge = i;
  edge.id = rec.mi + "/" + i;
  edge.faceIds = [data.pairs[i * 2], data.pairs[i * 2 + 1]].map(fi => fi < 0 ? -1 : rec.base + fi);
  rec.descriptions.set(i, edge);
  return edge;
}

function offView(rec, hidden = false) {
  const body = rec.solid?.name || rec.name;
  return !showsInFaucetFinish(state.mountedDetail?.file, body, state.faucetFinish) ||
    (!hidden && (rec.solid ? !rec.solid.visible || !rec.solid.layers.test(camera.layers) : state.hiddenComponents.has(body)));
}

function yieldToInput() { return new Promise(resolve => setTimeout(resolve, 0)); }

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
    // plane normal from two ~perpendicular radii (the loop is planar)
    const k = Math.max(1, Math.floor((points.length - 1) / 4));
    const axis = points[0].clone().sub(center).cross(points[k].clone().sub(center)).normalize();
    return { points, a, b, length, kind: "loop", segments: points.length - 1,
             center, radius: r / (points.length - 1), axis };
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
  if (maxDev < STRAIGHT_TOL) {
    return { points, a, b, length, kind: "straight", segments: points.length - 1,
             dir: ab.clone().normalize() };
  }

  // curved: try to fit a circle (arc) so we can report a radius + plane. A fit is taken
  // only when the arc it proposes accounts for the path length actually walked
  // (`arcFitMeasured`); anything else is reported as the curve it is, with no invented
  // radius or centre for a reader to reason from.
  const seg = points.length - 1;
  const fit = fitCircle(points);
  if (fit && arcFitMeasured(fit.radius, a.distanceTo(b), length)) {
    return { points, a, b, length, kind: "arc", segments: seg,
             center: fit.center, radius: fit.radius, axis: fit.axis, residual: fit.residual };
  }
  return { points, a, b, length, kind: "curve", segments: seg };
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

  let residual = 0;
  const lo = p1.clone(), hi = p1.clone();
  for (const p of points) {
    residual = Math.max(residual, Math.abs(p.distanceTo(center) - radius));
    lo.min(p); hi.max(p);
  }
  if (!roundFitMeasured(radius, hi.distanceTo(lo), residual)) return null;
  return { center, radius, axis: n.clone().normalize(), residual };
}

// --- face classification (lazy, cached per global face id) ---
// Sampled vertices + normals decide the surface type. plane: all normals
// agree and the points are coplanar. cylinder: an axis perpendicular to
// every normal exists (built from normal cross-products) and the points
// ring it at one radius (Kåsa least-squares circle in the axis-normal
// plane). Everything else — cones, tori, the gooseneck's swept b-splines —
// reports as "curved" with a point on it: no compact params, but knowing
// it's the swept skin is itself the answer.
function classifyFace(gid) {
  if (gid == null || gid < 0) return null;
  if (!faceClass) faceClass = new Map();
  if (faceClass.has(gid)) return faceClass.get(gid);
  const entry = faceTable && faceTable[gid];
  const out = entry ? classifyFaceRange(entry.rec, entry.rec.faces[entry.fi]) : null;
  if (out && entry.rec.faces[entry.fi].sources) out.sources = entry.rec.faces[entry.fi].sources;
  faceClass.set(gid, out);
  return out;
}

// Non-indexed triangle soup of one face, for highlight overlays.
export function faceHighlightGeometry(gid) {
  const entry = faceTable && faceTable[gid];
  if (!entry) return null;
  const { rec, fi } = entry;
  const f = rec.faces[fi];
  const positions = new Float32Array((f.last - f.first + 1) * 9);
  const pos = rec.pos, idx = rec.idx;
  let next = 0;
  for (let i = f.first * 3; i < (f.last + 1) * 3; i++) {
    const v = idx[i] * 3;
    positions[next++] = pos[v]; positions[next++] = pos[v + 1]; positions[next++] = pos[v + 2];
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.userData.bodies = [rec.name];
  return geo;
}

// The body a face belongs to, by global face id; null for an unknown id.
export function faceBody(gid) {
  return (faceTable && faceTable[gid]?.rec.name) ?? null;
}

// THE FACE A POINT LIES ON, for a `face:` pick that gives a point on the face
// rather than its parameters: the face whose triangles come nearest `p`. The
// drawn surface is a reduction of the solid, so a point taken off the solid can
// stand a little off every triangle; `tol` is how far it may. Returns the global
// face id, or -1 when no shown face comes that near.
export function faceNearest(p, tol = 0.5, { hidden = false } = {}) {
  const q = new THREE.Vector3(p.x, p.y, p.z);
  const box = new THREE.Box3(q.clone(), q.clone()).expandByScalar(tol);
  const tri = new THREE.Triangle(), near = new THREE.Vector3();
  let best = -1, bestD = tol * tol;
  for (const rec of ensureFaces()) {
    if (!rec?.solid || offView(rec, hidden)) continue;
    visitSurfaceRanges(rec.solid, box, (start, end) => {
      const pos = rec.pos, idx = rec.idx;
      for (let t = start; t < end; t++) {
        const i = t * 3;
        tri.a.fromArray(pos, idx[i] * 3);
        tri.b.fromArray(pos, idx[i + 1] * 3);
        tri.c.fromArray(pos, idx[i + 2] * 3);
        const d = tri.closestPointToPoint(q, near).distanceToSquared(q);
        if (d >= bestD) continue;
        const gid = faceAtTriangle(rec, t);
        if (gid >= 0) { best = gid; bestD = d; }
      }
    });
  }
  return best;
}

// THE SURFACE INSIDE A BOX, for a `box:` pick: every shown triangle's part
// within it, cut exactly at the box's planes. A face is often more than the
// thing being pointed at — one plane carries a pocket's rim and the bar
// standing in it — and a box takes only what it holds, with a straight edge
// where it cuts. A face lying in one of its planes is the box's boundary, not
// its content, and stays dark. Non-indexed triangle soup, like
// faceHighlightGeometry, with the bodies it came off in userData.bodies; null
// when the box holds no surface. `hidden` takes in bodies hidden by hand.
export async function boxHighlightGeometry(lo, hi, { hidden = false, signal } = {}) {
  signal?.throwIfAborted();
  const revision = inspectionRevision;
  const bounds = new THREE.Box3(new THREE.Vector3(lo.x,lo.y,lo.z), new THREE.Vector3(hi.x,hi.y,hi.z));
  let slice = performance.now();
  const e = 1e-4;
  const planes = [[1, 0, 0, hi.x - e], [-1, 0, 0, -lo.x - e], [0, 1, 0, hi.y - e], [0, -1, 0, -lo.y - e],
    [0, 0, 1, hi.z - e], [0, 0, -1, -lo.z - e]];
  const out = [];
  const bodies = new Set();
  const keep = (poly) => {
    for (let i = 1; i < poly.length - 1; i++) out.push(...poly[0], ...poly[i], ...poly[i + 1]);
  };
  for (const rec of ensureFaces()) {
    if (!rec?.solid || offView(rec, hidden)) continue;
    const ranges = [];
    visitSurfaceRanges(rec.solid, bounds, (start, end) => ranges.push([start, end]));
    if (!ranges.length) continue;
    const { pos, idx } = rec;
    for (const [start, end] of ranges) for (let t = start * 3; t < end * 3; t += 3) {
      if ((t % 768 === 0) && performance.now() - slice > 4) {
        await yieldToInput();
        signal?.throwIfAborted();
        if (revision !== inspectionRevision) throw new DOMException("The displayed geometry changed", "AbortError");
        slice = performance.now();
      }
      let poly = [0, 1, 2].map((k) => [pos[idx[t + k] * 3], pos[idx[t + k] * 3 + 1], pos[idx[t + k] * 3 + 2]]);
      if (poly.every((v) => v[0] < lo.x) || poly.every((v) => v[0] > hi.x)
          || poly.every((v) => v[1] < lo.y) || poly.every((v) => v[1] > hi.y)
          || poly.every((v) => v[2] < lo.z) || poly.every((v) => v[2] > hi.z)) continue;
      for (const [nx, ny, nz, d] of planes) {
        const s = poly.map((v) => v[0] * nx + v[1] * ny + v[2] * nz - d);
        if (s.every((x) => x <= 0)) continue;
        const next = [];
        poly.forEach((a, i) => {
          const j = (i + 1) % poly.length, b = poly[j];
          if (s[i] <= 0) next.push(a);
          if ((s[i] < 0 && s[j] > 0) || (s[i] > 0 && s[j] < 0)) {
            const u = s[i] / (s[i] - s[j]);
            next.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]);
          }
        });
        poly = next;
        if (poly.length < 3) break;
      }
      if (poly.length >= 3) { keep(poly); bodies.add(rec.name); }
    }
  }
  if (!out.length) return null;
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(out, 3));
  geo.userData.bodies = [...bodies];
  return geo;
}

// Point and box requests use the triangle ranges directly. An edge request only
// reconstructs solids that could contain its endpoints or circle centre.
export async function getFindData(picks = [], { signal, hidden = false } = {}) {
  signal?.throwIfAborted();
  const revision = inspectionRevision;
  function current() {
    signal?.throwIfAborted();
    if (revision !== inspectionRevision) throw new DOMException("The displayed geometry changed", "AbortError");
  }
  const edgeQueries = picks.filter(p => p.a && p.b || p.kind === "circle");
  const classification = picks.some(p => p.kind === "face-plane" || p.kind === "face-cylinder");
  const edges = [], faces = [];
  if (!edgeQueries.length && !classification) { ensureFaces(); return { edges, faces }; }
  const box = new THREE.Box3();
  const couldHold = pick => pick.kind === "circle" ? box.containsPoint(pick.center)
    : box.containsPoint(pick.a) && box.containsPoint(pick.b);
  let slice = performance.now();
  for (const rec of ensureFaces()) {
    if (!rec?.solid || offView(rec, hidden)) continue;
    if (classification) for (let i = 0; i < rec.faces.length; i++) {
      const gid = rec.base + i;
      faces[gid] = classifyFace(gid);
      if (performance.now() - slice > 4) {
        await yieldToInput(); current(); slice = performance.now();
      }
    }
    if (!edgeQueries.length) continue;
    box.copy(rec.solid.geometry.boundingBox).applyMatrix4(rec.solid.matrixWorld).expandByScalar(MATCH_TOLERANCE * 2);
    if (!edgeQueries.some(couldHold)) continue;
    const data = await prepareEdges(rec); current();
    if (!data || offView(rec, hidden)) continue;
    for (let i = 0; i + 1 < data.starts.length; i++) {
      box.min.fromArray(data.boxes, i * 6); box.max.fromArray(data.boxes, i * 6 + 3);
      box.expandByScalar(MATCH_TOLERANCE * 2);
      if (edgeQueries.some(couldHold)) edges.push(describeEdge(rec, data, i));
      if (performance.now() - slice > 4) {
        await yieldToInput(); current(); slice = performance.now();
      }
    }
  }
  return { edges, faces };
}

// --- screen-space picking ---
const _vp = new THREE.Matrix4();
function projectPixels(p, rect, e) {
  const x = e[0] * p.x + e[4] * p.y + e[8] * p.z + e[12];
  const y = e[1] * p.x + e[5] * p.y + e[9] * p.z + e[13];
  const z = e[2] * p.x + e[6] * p.y + e[10] * p.z + e[14];
  const w = e[3] * p.x + e[7] * p.y + e[11] * p.z + e[15];
  if (w <= 1e-6) return null; // behind camera
  return { x: (x / w * 0.5 + 0.5) * rect.width, y: (-y / w * 0.5 + 0.5) * rect.height, depth: z / w, w };
}

function segDistPx(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay;
  const l2 = dx * dx + dy * dy;
  let t = l2 ? ((px - ax) * dx + (py - ay) * dy) / l2 : 0;
  t = t < 0 ? 0 : t > 1 ? 1 : t;
  const cx = ax + t * dx, cy = ay + t * dy;
  return { d: Math.hypot(px - cx, py - cy), t };
}

const pickFrustum = new THREE.Frustum(), crop = new THREE.Matrix4();
const edgeBounds = new THREE.Box3(), edgePoint = new THREE.Vector3();
function edgeCandidates(clientX, clientY) {
  const rect = renderer.domElement.getBoundingClientRect();
  const px = clientX - rect.left, py = clientY - rect.top;
  const sx = rect.width / (2 * PICK_THRESHOLD_PX), sy = rect.height / (2 * PICK_THRESHOLD_PX);
  crop.set(sx,0,0,-sx*(2*px/rect.width-1), 0,sy,0,-sy*(1-2*py/rect.height), 0,0,1,0, 0,0,0,1);
  _vp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  pickFrustum.setFromProjectionMatrix(crop.multiply(_vp));
  return { rect, px, py, recs: ensureFaces().filter(rec => {
    if (!rec?.solid || offView(rec)) return false;
    edgeBounds.copy(rec.solid.geometry.boundingBox).applyMatrix4(rec.solid.matrixWorld);
    return pickFrustum.intersectsBox(edgeBounds);
  }) };
}

function pickEdge({ rect, px, py, recs }) {
  const e = _vp.elements;
  const planes = renderer.clippingPlanes;
  const testPoint = planes?.length ? new THREE.Vector3() : null;
  let best = null;
  for (const rec of recs) {
    const data = topologies.get(rec.mesh)?.data;
    if (!data) continue;
    for (let edge = 0; edge + 1 < data.starts.length; edge++) {
      edgeBounds.min.fromArray(data.boxes, edge * 6); edgeBounds.max.fromArray(data.boxes, edge * 6 + 3);
      if (!pickFrustum.intersectsBox(edgeBounds)) continue;
      const start = data.starts[edge], end = data.starts[edge + 1];
      let prev = projectPixels(edgePoint.fromArray(data.points, start * 3), rect, e);
      for (let p = start + 1; p < end; p++) {
        const cur = projectPixels(edgePoint.fromArray(data.points, p * 3), rect, e);
        if (prev && cur) {
          const { d, t } = segDistPx(px, py, prev.x, prev.y, cur.x, cur.y);
          if (d <= PICK_THRESHOLD_PX) {
            const depth = prev.depth + (cur.depth - prev.depth) * t;
            // The screen-space fraction maps back through perspective to the point under the cursor.
            const along = t * prev.w / ((1 - t) * cur.w + t * prev.w);
            if ((!best || d < best.d - 1.5 || (Math.abs(d - best.d) <= 1.5 && depth < best.depth)) &&
                (!testPoint || planes.every(plane => plane.distanceToPoint(
                  testPoint.fromArray(data.points, (p - 1) * 3).lerp(edgePoint, along)) >= -1e-5))) {
              best = { rec, data, edge, p, along, d, depth };
            }
          }
        }
        prev = cur;
      }
    }
  }
  if (!best) return null;
  const { rec, data, edge, p, along } = best;
  const point = new THREE.Vector3().fromArray(data.points, (p - 1) * 3).lerp(edgePoint.fromArray(data.points, p * 3), along);
  return { edge: describeEdge(rec, data, edge), object: rec.solid, point, d: best.d, depth: best.depth };
}

// Face under the cursor — used when a click misses every edge. Raycasts
// the rendered meshes (step.js tags each with its occt mesh index) and
// maps the original hit triangle to its authored B-rep face range.
const _raycaster = new THREE.Raycaster();
const _ndc = new THREE.Vector2();

function frontMeshes() {
  if (!state.currentGroup) return [];
  // The solid meshes, one per solid. Skip components the user hid locally
  // (component-picker.js): a hidden solid isn't in the view, so its faces
  // shouldn't be pickable either.
  return state.currentGroup.children.filter(
    (c) => c.userData && c.userData.side === "front" && c.visible !== false,
  );
}

// True occlusion test for an edge candidate: cast from the camera at the
// edge point itself and see whether any surface stands clearly in front
// of it. An edge lying ON a visible surface reads the surface at its own
// depth — not occluded.
const _occDir = new THREE.Vector3();
function edgeOccluded(edgeHit) {
  const de = edgeHit.point.distanceTo(camera.position);
  _occDir.copy(edgeHit.point).sub(camera.position).normalize();
  _raycaster.set(camera.position, _occDir);
  const hit = nearestSurface(_raycaster, frontMeshes());
  return !!hit && hit.distance < de - Math.max(0.5, de * 0.002);
}
function pickFace(clientX, clientY) {
  if (!state.currentGroup) return null;
  ensureFaces();
  if (!meshRecs) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.set(
    ((clientX - rect.left) / rect.width) * 2 - 1,
    -((clientY - rect.top) / rect.height) * 2 + 1,
  );
  _raycaster.setFromCamera(_ndc, camera);
  const hit = nearestSurface(_raycaster, frontMeshes(), h => {
    return faceAtTriangle(meshRecs[h.object.userData.occtIndex], h.faceIndex) >= 0;
  });
  if (!hit) return null;
  const rec = meshRecs[hit.object.userData.occtIndex], gid = faceAtTriangle(rec, hit.faceIndex);
  const face = classifyFace(gid);
  return { type: "face", gid, source: rec.mesh, localFace: gid - rec.base, solid: rec.name,
    face, point: hit.point, surface: surfacePick(hit, face, gid) };
}

// --- faint all-edges layer (every BREP edge, shown while picking is on) ---
// The faint lines depth-test against solid shading and follow the same
// component visibility as Blueprint's feature edges.
const ALL_EDGES_COLOR = 0xdce6f5;
const ALL_EDGES_OPACITY = 0.14;
const edgeLayers = new THREE.Group();
edgeLayers.name = "edge-picker-all-edges";
scene.add(edgeLayers);
const linesBySource = new Map();
const edgeLayerMaterial = new THREE.LineBasicMaterial({
  color: ALL_EDGES_COLOR, transparent: true, opacity: ALL_EDGES_OPACITY, depthWrite: false,
});
let layerTicket = 0, layerTimer = 0;

function refreshEdgeLayers() {
  const wanted = new Set(edgeSource || []);
  cancelDepartedJobs(wanted);
  for (const [source, line] of linesBySource) if (!wanted.has(source)) {
    edgeLayers.remove(line); line.geometry.dispose(); linesBySource.delete(source);
  }
  invalidateAllEdgesLayer();
}

export function invalidateAllEdgesLayer() {
  const ticket = ++layerTicket;
  clearTimeout(layerTimer);
  edgeLayers.visible = enabled;
  if (!enabled || !edgeSource) return;
  pickTicket++;
  hoverPoint = null;
  setHover(null);
  const recs = ensureFaces().filter(rec => rec?.solid);
  const selectedSource = selection?.edge?.source || selection?.source;
  for (const rec of recs) {
    const line = linesBySource.get(rec.mesh);
    const shown = !offView(rec);
    if (line) line.visible = shown;
    if (!shown && rec.mesh === selectedSource) clearSelection();
  }
  async function drawEdges() {
    let slice = performance.now();
    for (const rec of recs) {
      if (ticket !== layerTicket) return;
      if (offView(rec) || linesBySource.has(rec.mesh)) continue;
      const data = await prepareEdges(rec);
      if (ticket !== layerTicket) return;
      if (data?.lines.length && !offView(rec)) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.BufferAttribute(data.points, 3));
        geo.setIndex(new THREE.BufferAttribute(data.lines, 1));
        geo.boundingSphere = rec.solid.geometry.boundingBox.getBoundingSphere(new THREE.Sphere()).applyMatrix4(rec.solid.matrixWorld);
        const line = new THREE.LineSegments(geo, edgeLayerMaterial);
        linesBySource.set(rec.mesh, line);
        edgeLayers.add(line);
        sceneState.requestCadRender?.();
      }
      if (performance.now() - slice > 4) { await yieldToInput(); slice = performance.now(); }
    }
  }
  layerTimer = setTimeout(() => drawEdges().catch(error => console.warn("Surface edges:", error)), 0);
  sceneState.requestCadRender?.();
}

window.addEventListener(HSM_EVENTS.BLUEPRINT_VISIBILITY, invalidateAllEdgesLayer);

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
let selObjs = { line: null, face: null, ends: null, click: null };
let selection = null; // {type:"edge", edge, point} | {type:"face", gid, solid, face, point}
let hoverLine = null;
let hoverId = -1;

function clearSelection() {
  if (selection) sceneState.requestCadRender?.();
  disposeObj(selObjs.line); disposeObj(selObjs.face); disposeObj(selObjs.ends); disposeObj(selObjs.click);
  selObjs = { line: null, face: null, ends: null, click: null };
  selection = null;
  hidePanel();
}

function drawSelection(sel) {
  clearSelection();
  syncLineRes();
  if (sel.type === "face") {
    const geo = faceHighlightGeometry(sel.gid);
    if (geo) {
      const mat = new THREE.MeshBasicMaterial({
        color: HIGHLIGHT, transparent: true, opacity: 0.35, side: THREE.DoubleSide,
        depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
      });
      selObjs.face = new THREE.Mesh(geo, mat);
      selObjs.face.renderOrder = 998;
      overlay.add(selObjs.face);
    }
  } else {
    const e = sel.edge;
    selObjs.line = lineFromPoints(e.points, selLineMat);
    overlay.add(selObjs.line);
    const endVecs = e.kind === "loop" ? [e.center] : [e.a, e.b];
    selObjs.ends = markerPoints(endVecs, ENDPOINT);
    overlay.add(selObjs.ends);
  }
  selObjs.click = markerPoints([sel.point], CLICKPOINT);
  overlay.add(selObjs.click);
  selection = sel;
  setHover(null);
  showPanel(sel);
  sceneState.requestCadRender?.();
}

function setHover(hit) {
  const id = hit ? hit.edge.id : -1;
  if (id === hoverId) return;
  hoverId = id;
  disposeObj(hoverLine);
  hoverLine = null;
  if (hit && (!selection || selection.type !== "edge" || hit.edge.id !== selection.edge.id)) {
    syncLineRes();
    hoverLine = lineFromPoints(hit.edge.points, hoverLineMat);
    overlay.add(hoverLine);
  }
  sceneState.requestCadRender?.();
}

// --- text formatting for the copy blob ---
// fnum/fpt/formatFace come from pick-format.js so the find box parses
// exactly what we emit.
function edgeText(sel) {
  const e = sel.edge;
  // HOW MANY TESSELLATION SEGMENTS THE EDGE IS, on every kind. One long segment between two
  // BREP vertices is a chain the surface never curved along, and on a decimated payload it is
  // how a collapsed feature is bridged — a reading a length alone cannot distinguish from a
  // drawn edge of the same length.
  const seg = e.segments != null ? ` · ${e.segments} seg` : "";
  if (e.kind === "loop") {
    return `circle ⌀${(e.radius * 2).toFixed(3)} · center ${fpt(e.center)} · circumference ${e.length.toFixed(3)} · axis ${fpt(e.axis)}${seg}`;
  }
  let tail;
  if (e.kind === "straight") tail = `len ${e.length.toFixed(3)} · straight · dir ${fpt(e.dir)}`;
  else if (e.kind === "arc") {
    tail = `len ${e.length.toFixed(3)} · arc r=${e.radius.toFixed(3)} · center ${fpt(e.center)} · axis ${fpt(e.axis)}`;
    if (e.residual != null) tail += ` · fit ±${e.residual.toFixed(3)}`;
  } else tail = `len ${e.length.toFixed(3)} · curve`;
  return `${fpt(e.a)} → ${fpt(e.b)} · ${tail}${seg}`;
}
function clickText(sel) { return fpt(sel.point); }
function sourceText(records) {
  if (!Array.isArray(records)) return "";
  const where = (src) => src === null ? "unknown source" : typeof src === "string" ? src : "";
  return records.map(record => {
    if (record === null) return "unknown provenance";
    const source = where(record?.src);
    if (!source) return "";
    let text = `${source}${record.op ? ` · ${record.op}` : ""}`;
    const via = record.via;
    if (via && typeof via === "object" && where(via.src)) text += ` · via ${via.op ? `${via.op} at ` : ""}${where(via.src)}`;
    return text;
  }).filter(Boolean).join("; ");
}
function selFaceTexts(sel) {
  if (sel.type === "face") return { a: formatFace(sel.face), sourcesA: sourceText(sel.face.sources), b: null };
  const ids = sel.edge.faceIds || [];
  const a = classifyFace(ids[0]), b = classifyFace(ids[1]);
  return { a: formatFace(a), b: formatFace(b), sourcesA: sourceText(a?.sources), sourcesB: sourceText(b?.sources) };
}

// The open file as the viewer fetched it (content-root-relative), plus the repo-relative
// locator for the Copy-all blob and the bare name for the header. The locator is composed by
// `fileLine` off the whole mount, not off the path alone, so it names the surface that was
// actually drawn and what that surface cost.
function currentFile() { return (state.mountedDetail && state.mountedDetail.file) || null; }
function repoPath(file) {
  return fileLine(file, state.mountedDetail);
}
function headerName(file) { return file.split("/").pop().replace(/\.step$/i, ""); }

// The clicked component's name, or null when there's none worth showing. Only
// assemblies carry real component names; single-solid STEPs get a generic occt
// translator string, which is noise. One helper so the panel row and the copy
// blob agree on what (if anything) to show.
function solidName(sel) {
  const s = sel.type === "face" ? sel.solid : sel.edge.solid;
  return isAssembly && s && !/^Open CASCADE STEP translator/.test(s) ? s : null;
}

function allText(sel) {
  const lines = [];
  const file = currentFile();
  if (file) {
    lines.push(`file: ${repoPath(file)}`);
  }
  const solid = solidName(sel);
  if (solid) {
    lines.push(`solid: ${solid}`);
  }
  if (sel.type === "face") {
    const face = selFaceTexts(sel);
    lines.push(`face: ${face.a}`);
    if (face.sourcesA) lines.push(`sources: ${face.sourcesA}`);
  } else {
    const faces = selFaceTexts(sel);
    lines.push(`edge: ${edgeText(sel)}`);
    if (showFaces && faces.a) lines.push(`faceA: ${faces.a}`);
    if (showFaces && faces.b) lines.push(`faceB: ${faces.b}`);
    if (showFaces && faces.sourcesA) lines.push(`faceA sources: ${faces.sourcesA}`);
    if (showFaces && faces.sourcesB) lines.push(`faceB sources: ${faces.sourcesB}`);
  }
  lines.push(`click: ${clickText(sel)}`);
  return lines.join("\n");
}

// --- copy panel ---
let panel = null;

// An edge's two bordering faces are mostly noise on this (axis-aligned, named-
// solid) geometry — the edge coordinates already imply them. So they're hidden by
// default; a subtle header checkbox brings them back, panel + copy, for the cases
// they earn their keep (a bore rim, two coincident edges). A FACE pick still shows
// the face it selected — that's the pick, not a bordering face. Persisted across
// loads/sessions in localStorage.
const FACES_KEY = "hsmPickFaces";
let showFaces = (() => { try { return localStorage.getItem(FACES_KEY) === "1"; } catch { return false; } })();

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "edge-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Edge";
  const fileEl = document.createElement("span");
  fileEl.className = "edge-panel-file";
  const facesToggle = document.createElement("label");
  facesToggle.className = "edge-panel-faces";
  facesToggle.title = "Include the edge's bordering faces in the copy";
  const facesBox = document.createElement("input");
  facesBox.type = "checkbox";
  facesBox.checked = showFaces;
  const facesLab = document.createElement("span");
  facesLab.textContent = "faces";
  facesToggle.appendChild(facesBox);
  facesToggle.appendChild(facesLab);
  facesBox.addEventListener("change", () => {
    showFaces = facesBox.checked;
    try { localStorage.setItem(FACES_KEY, showFaces ? "1" : "0"); } catch {}
    if (selection) showPanel(selection); // re-render the blob for the live selection
  });
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", () => clearSelection());
  head.appendChild(title);
  head.appendChild(fileEl);
  head.appendChild(facesToggle);
  head.appendChild(makePanelCollapse(panel, "step-edge-panel-collapsed"));
  head.appendChild(close);
  panel.appendChild(head);
  panel._fileEl = fileEl;

  const actions = document.createElement("div");
  actions.className = "edge-surface-actions";
  panel._surfaceActions = addSurfaceActions(actions);
  panel.appendChild(actions);

  const text = document.createElement("textarea");
  text.className = "edge-panel-text";
  text.readOnly = true;
  text.spellcheck = false;
  panel.appendChild(text);
  panel._text = text;

  const copy = document.createElement("button");
  copy.type = "button";
  copy.className = "edge-panel-all";
  copy.textContent = "Copy";
  copy.addEventListener("click", () => { if (selection) copyText(panel._text.value, copy); });
  panel.appendChild(copy);
}

function showPanel(sel) {
  if (!panel) buildPanel();
  if (state.currentCadWrapper && panel.parentElement !== state.currentCadWrapper) {
    state.currentCadWrapper.appendChild(panel);
  }
  panel.querySelector(".edge-panel-title").textContent = sel.type === "face" ? "Face" : "Edge";
  const file = currentFile();
  panel._fileEl.textContent = file ? headerName(file) : "";
  panel._fileEl.title = file ? repoPath(file) : "";
  panel._surfaceActions(sel.surface);
  // On screen before the blob is measured: the panel is display:none until it
  // carries `show`, and a hidden textarea reports a scrollHeight of 0.
  panel.classList.add("show");

  const blob = allText(sel);
  // Sized to the blob as it wraps at the panel's width, not to its newlines —
  // a pick line runs to two or three rows in a 430px box, and the panel has
  // room in hand either way.
  const ta = panel._text;
  ta.value = blob;
  ta.rows = 2;
  const cs = getComputedStyle(ta);
  const line = parseFloat(cs.lineHeight) || 18;
  const pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
  ta.rows = Math.min(14, Math.max(2, Math.ceil((ta.scrollHeight - pad) / line)));
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
let downX = 0, downY = 0, pickTicket = 0, hoverFrame = 0, hoverPoint = null;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }

renderer.domElement.addEventListener("pointerdown", (e) => {
  pickTicket++; hoverPoint = null;
  downX = e.clientX; downY = e.clientY;
});
renderer.domElement.addEventListener("wheel", () => { pickTicket++; hoverPoint = null; }, { passive: true });
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!active()) return;
  if (renderer.domElement.parentElement?.classList.contains("cad-gesturing")) return;
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return; // a drag, not a click
  // Edge picking is screen-space and ignores occlusion, so on a busy
  // model some hidden edge is almost always within the pick threshold.
  // Occlusion is tested along the ray TO THE EDGE POINT, not against
  // the surface under the cursor: an edge lying flush on a visible
  // surface (a coplanar boolean seam, a tangent join) ties with it in
  // depth, while the surface point under the cursor sits measurably
  // nearer on a grazing view — comparing those two stole flush edges
  // and answered with the face. Occluded means something solid stands
  // clearly in front of the edge point itself. Blueprint shows edges through
  // translucent faces of the included components, so a visible bore seam or
  // rear edge can win a click anywhere on one of those components.
  const { clientX, clientY } = e;
  const candidates = edgeCandidates(clientX, clientY);
  const face = pickFace(clientX, clientY);
  function selectAt(candidates) {
    const edge = pickEdge(candidates);
    if (edge && (!face || isXrayEnabled() || !edgeOccluded(edge))) {
      drawSelection({ type: "edge", edge: edge.edge, point: edge.point,
        surface: { kind: "edge", edge: edge.edge, object: edge.object, point: edge.point, ownerName: edge.object.name } });
    } else if (face) drawSelection(face);
    else clearSelection();
  }
  selectAt(candidates);
  const missing = candidates.recs.filter(rec => !topologies.get(rec.mesh)?.data);
  if (!missing.length) return;
  const ticket = ++pickTicket, revision = inspectionRevision;
  const pose = camera.matrixWorld.clone();
  async function refine() {
    for (const rec of missing) {
      if (!active() || pickTicket !== ticket || revision !== inspectionRevision || !pose.equals(camera.matrixWorld)) return;
      await prepareEdges(rec);
    }
    if (active() && pickTicket === ticket && revision === inspectionRevision && pose.equals(camera.matrixWorld)) {
      selectAt(edgeCandidates(clientX, clientY));
    }
  }
  setTimeout(() => refine().catch(error => console.warn("Surface pick:", error)), 0);
});
renderer.domElement.addEventListener("pointermove", e => {
  if (!active() || e.buttons || e.pointerType === "touch") { hoverPoint = null; return; }
  hoverPoint = [e.clientX, e.clientY];
  if (hoverFrame) return;
  hoverFrame = requestAnimationFrame(() => {
    hoverFrame = 0;
    if (active() && hoverPoint) setHover(pickEdge(edgeCandidates(...hoverPoint)));
  });
});
renderer.domElement.addEventListener("pointerleave", () => { hoverPoint = null; setHover(null); });

// --- public API ---
export function clearEdgePicker() {
  clearSelection();
  setHover(null);
  edgeSource = null;
  inspectionRevision++;
  refreshEdgeLayers();
  isAssembly = false;
  meshRecs = null;
  faceTable = null;
  faceClass = null;
}

export function setEdgePickEnabled(on) {
  enabled = !!on;
  pickTicket++; hoverPoint = null;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  if (enabled) {
    invalidateAllEdgesLayer();
    // Arming edge-select disarms the component picker so a click doesn't feed
    // both. Only announce on arm, so disarming can't ping-pong.
    window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_TOOL, { detail: "edge" }));
  } else {
    clearSelection();
    setHover(null);
    invalidateAllEdgesLayer();
  }
}

export function isEdgePickEnabled() { return enabled; }

// pick-mode.js registers the segmented control's sync here, so a mode armed
// anywhere else brings the control with it.
let toggleRefresh = null;
export function setEdgeToggleRefresh(fn) { toggleRefresh = fn; }
export function syncEdgeToggle() { if (toggleRefresh) toggleRefresh(); }

// Another STEP tool (the component picker) armed itself — stand down if it
// wasn't us.
window.addEventListener(HSM_EVENTS.STEP_TOOL, (e) => {
  if (e.detail !== "edge" && enabled) {
    enabled = false;
    try { localStorage.setItem(LS_KEY, "0"); } catch {}
    clearSelection();
    setHover(null);
    invalidateAllEdgesLayer();
    if (toggleRefresh) toggleRefresh();
  }
});
