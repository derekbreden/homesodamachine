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
// Picking is screen-space: project every edge segment to pixels and take the
// one nearest the cursor (front-most on a near tie). Zoom-independent, and the
// click snaps onto the edge so the reported point is ON the geometry, not a
// float in space. Reconstruction is lazy (first enable / first pick) and cached
// per loaded model; setActiveEdges() invalidates it on each new load.
//
// While the toggle is on, the whole reconstructed edge set is also drawn as a
// faint always-on layer. The x-ray crease renderer (xray.js) only draws
// dihedrals past its ~30° threshold, so tangent and shallow joins — a shave
// plane running out onto the surface it shaved, a fillet meeting its wall —
// are pickable yet invisible without it. The layer makes "if you can click
// it, you can see it" hold exactly.

import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";
import { fnum, fpt, formatFace } from "./pick-format.js";

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

// --- edge + face data (lazy, per loaded model) ---
let edgeSource = null;  // occt result.meshes for the live model
let activeEdges = null; // reconstructed BREP edges, or null until built
let isAssembly = false; // >1 solid — then occt carries real component names
let meshRecs = null;    // per occt-mesh: {name, pos, idx, nrm, faces, triFace}
let faceTable = null;   // global face id -> {rec, fi}
let faceClass = null;   // global face id -> classified record (cache)

export function setActiveEdges(result) {
  edgeSource = (result && result.meshes) || null;
  isAssembly = !!(edgeSource && edgeSource.length > 1);
  activeEdges = null; // invalidate — rebuild on demand
  meshRecs = null;
  faceTable = null;
  faceClass = null;
  clearSelection();
  setHover(null);
  disposeAllEdgesLayer();
  ensureAllEdgesLayer(); // no-op unless the toggle is on
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
  meshRecs = [];
  faceTable = [];

  for (const mesh of meshes) {
    const pos = mesh.attributes && mesh.attributes.position && mesh.attributes.position.array;
    const idx = mesh.index && mesh.index.array;
    const faces = mesh.brep_faces;
    if (!pos || !idx || !faces) {
      meshRecs.push(null);
      faceBase += faces ? faces.length : 0;
      continue;
    }

    const triCount = idx.length / 3;
    const triFace = new Int32Array(triCount).fill(-1);
    faces.forEach((f, fi) => {
      for (let t = f.first; t <= f.last; t++) triFace[t] = faceBase + fi;
    });

    const nrm = mesh.attributes.normal && mesh.attributes.normal.array;
    const rec = { name: mesh.name, pos, idx, nrm, faces, triFace };
    meshRecs.push(rec);
    faces.forEach((f, fi) => { faceTable[faceBase + fi] = { rec, fi }; });

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

    for (const [pk, segs] of byPair.entries()) {
      const faceIds = pk.split(",").map(Number);
      for (const path of chainSegments(segs)) {
        const e = makeEdge(path.map((k) => keyToPos.get(k)));
        e.solid = mesh.name; // assembly component name (occt), for the blob
        e.faceIds = faceIds; // the two bordering BREP faces
        edges.push(e);
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
    // plane normal from two ~perpendicular radii (the loop is planar)
    const k = Math.max(1, Math.floor((points.length - 1) / 4));
    const axis = points[0].clone().sub(center).cross(points[k].clone().sub(center)).normalize();
    return { points, a, b, length, kind: "loop", center, radius: r / (points.length - 1), axis };
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
    return { points, a, b, length, kind: "straight", dir: ab.clone().normalize() };
  }

  // curved: try to fit a circle (arc) so we can report a radius + plane
  const fit = fitCircle(points);
  if (fit) return { points, a, b, length, kind: "arc", center: fit.center, radius: fit.radius, axis: fit.axis };
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
  return { center, radius, axis: n.clone().normalize() };
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
  const out = entry ? classifyFaceImpl(entry.rec, entry.rec.faces[entry.fi]) : null;
  faceClass.set(gid, out);
  return out;
}

function classifyFaceImpl(rec, f) {
  const seen = new Set();
  const pts = [];
  const nrms = [];
  const triCount = f.last - f.first + 1;
  const stride = Math.max(1, Math.ceil(triCount / 300));
  for (let t = f.first; t <= f.last; t += stride) {
    for (let k = 0; k < 3; k++) {
      const vi = rec.idx[t * 3 + k];
      if (seen.has(vi)) continue;
      seen.add(vi);
      pts.push(new THREE.Vector3(rec.pos[vi * 3], rec.pos[vi * 3 + 1], rec.pos[vi * 3 + 2]));
      if (rec.nrm) {
        const n = new THREE.Vector3(rec.nrm[vi * 3], rec.nrm[vi * 3 + 1], rec.nrm[vi * 3 + 2]);
        if (n.lengthSq() > 1e-12) nrms.push(n.normalize());
      }
    }
  }
  const centroid = new THREE.Vector3();
  for (const p of pts) centroid.add(p);
  if (pts.length) centroid.multiplyScalar(1 / pts.length);
  if (pts.length < 3) return { kind: "curved", near: centroid };

  // no vertex normals in the mesh — fall back to sampled triangle normals
  if (!nrms.length) {
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
    for (let t = f.first; t <= f.last; t += stride) {
      a.fromArray(rec.pos, rec.idx[t * 3] * 3);
      b.fromArray(rec.pos, rec.idx[t * 3 + 1] * 3);
      c.fromArray(rec.pos, rec.idx[t * 3 + 2] * 3);
      const n = b.clone().sub(a).cross(c.clone().sub(a));
      if (n.lengthSq() > 1e-12) nrms.push(n.normalize());
    }
    if (!nrms.length) return { kind: "curved", near: centroid };
  }

  // plane?
  const navg = new THREE.Vector3();
  for (const n of nrms) navg.add(n);
  if (navg.lengthSq() > 1e-9) {
    navg.normalize();
    let planar = true;
    for (const n of nrms) if (Math.abs(n.dot(navg)) < 0.999) { planar = false; break; }
    if (planar) {
      let maxOff = 0;
      const d = new THREE.Vector3();
      for (const p of pts) maxOff = Math.max(maxOff, Math.abs(d.copy(p).sub(centroid).dot(navg)));
      if (maxOff < 0.02) return { kind: "plane", n: navg, thru: centroid };
    }
  }

  // cylinder?
  const axis = new THREE.Vector3();
  const n0 = nrms[0];
  for (let i = 1; i < nrms.length; i++) {
    const c = new THREE.Vector3().crossVectors(n0, nrms[i]);
    if (c.lengthSq() < 1e-6) continue;
    if (axis.lengthSq() > 0 && c.dot(axis) < 0) c.negate();
    axis.add(c);
  }
  if (axis.lengthSq() > 1e-9) {
    axis.normalize();
    let cyl = true;
    for (const n of nrms) if (Math.abs(n.dot(axis)) > 0.02) { cyl = false; break; }
    if (cyl) {
      const u = new THREE.Vector3();
      u.crossVectors(axis, Math.abs(axis.x) > 0.9 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0)).normalize();
      const v = new THREE.Vector3().crossVectors(axis, u);
      // Kåsa circle fit: x² + y² = A·x + B·y + C, center (A/2, B/2)
      let Sxx = 0, Sxy = 0, Syy = 0, Sx = 0, Sy = 0, Sxz = 0, Syz = 0, Sz = 0;
      const xy = [];
      const d = new THREE.Vector3();
      for (const p of pts) {
        d.copy(p).sub(centroid);
        const x = d.dot(u), y = d.dot(v), z = x * x + y * y;
        xy.push([x, y]);
        Sxx += x * x; Sxy += x * y; Syy += y * y; Sx += x; Sy += y;
        Sxz += x * z; Syz += y * z; Sz += z;
      }
      const N = xy.length;
      const det3 = (m) =>
        m[0] * (m[4] * m[8] - m[5] * m[7]) - m[1] * (m[3] * m[8] - m[5] * m[6]) + m[2] * (m[3] * m[7] - m[4] * m[6]);
      const D = det3([Sxx, Sxy, Sx, Sxy, Syy, Sy, Sx, Sy, N]);
      if (Math.abs(D) > 1e-9) {
        const A = det3([Sxz, Sxy, Sx, Syz, Syy, Sy, Sz, Sy, N]) / D;
        const B = det3([Sxx, Sxz, Sx, Sxy, Syz, Sy, Sx, Sz, N]) / D;
        const C = det3([Sxx, Sxy, Sxz, Sxy, Syy, Syz, Sx, Sy, Sz]) / D;
        const cx = A / 2, cy = B / 2;
        const r = Math.sqrt(Math.max(0, C + cx * cx + cy * cy));
        let maxRes = 0;
        for (const [x, y] of xy) maxRes = Math.max(maxRes, Math.abs(Math.hypot(x - cx, y - cy) - r));
        if (r > 1e-3 && maxRes <= Math.max(0.05, 0.02 * r)) {
          const axisPoint = centroid.clone().addScaledVector(u, cx).addScaledVector(v, cy);
          return { kind: "cylinder", r, axis: axisPoint, dir: axis };
        }
      }
    }
  }
  return { kind: "curved", near: centroid };
}

// Non-indexed triangle soup of one face, for highlight overlays.
export function faceHighlightGeometry(gid) {
  const entry = faceTable && faceTable[gid];
  if (!entry) return null;
  const { rec, fi } = entry;
  const f = rec.faces[fi];
  const positions = [];
  for (let t = f.first; t <= f.last; t++) {
    for (let k = 0; k < 3; k++) {
      const vi = rec.idx[t * 3 + k];
      positions.push(rec.pos[vi * 3], rec.pos[vi * 3 + 1], rec.pos[vi * 3 + 2]);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  return geo;
}

// Everything the find box needs: reconstructed edges plus every face
// classified. Classification is cached, so repeated finds are cheap.
export function getFindData() {
  const edges = ensureEdges();
  const faces = [];
  if (faceTable) {
    for (let gid = 0; gid < faceTable.length; gid++) {
      faces[gid] = faceTable[gid] ? classifyFace(gid) : null;
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

// Face under the cursor — used when a click misses every edge. Raycasts
// the rendered meshes (step.js tags each with its occt mesh index) and
// maps the hit triangle back to its BREP face via triFace.
const _raycaster = new THREE.Raycaster();
const _ndc = new THREE.Vector2();
function pickFace(clientX, clientY) {
  if (!state.currentGroup) return null;
  ensureEdges(); // builds meshRecs + faceTable
  if (!meshRecs) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.set(
    ((clientX - rect.left) / rect.width) * 2 - 1,
    -((clientY - rect.top) / rect.height) * 2 + 1,
  );
  _raycaster.setFromCamera(_ndc, camera);
  // Front meshes only — the back copies share geometry and would double
  // the triangle scan for the same answer.
  const candidates = state.currentGroup.children.filter(
    (c) => c.userData && c.userData.side === "front",
  );
  const hits = _raycaster.intersectObjects(candidates, false);
  for (const h of hits) {
    const mi = h.object.userData ? h.object.userData.occtIndex : undefined;
    if (mi == null || h.faceIndex == null) continue;
    const rec = meshRecs[mi];
    if (!rec) continue;
    const gid = rec.triFace[h.faceIndex];
    if (gid == null || gid < 0) continue;
    return { type: "face", gid, solid: rec.name, face: classifyFace(gid), point: h.point.clone() };
  }
  return null;
}

// --- faint all-edges layer (every BREP edge, shown while picking is on) ---
// Depth-tested (hidden edges stay hidden in solid shading; in x-ray the
// surfaces don't write depth, so it reads through the ghost like the crease
// lines do) and faint enough to sit under them.
const ALL_EDGES_COLOR = 0xdce6f5;
const ALL_EDGES_OPACITY = 0.14;
let allEdgesLine = null;

function disposeAllEdgesLayer() {
  if (!allEdgesLine) return;
  scene.remove(allEdgesLine);
  allEdgesLine.geometry.dispose();
  allEdgesLine.material.dispose();
  allEdgesLine = null;
}

function ensureAllEdgesLayer() {
  if (!enabled || !edgeSource) return;
  if (allEdgesLine) { allEdgesLine.visible = true; return; }
  const edges = ensureEdges();
  if (!edges.length) return;
  const flat = [];
  for (const e of edges) {
    const p = e.points;
    for (let i = 1; i < p.length; i++) {
      flat.push(p[i - 1].x, p[i - 1].y, p[i - 1].z, p[i].x, p[i].y, p[i].z);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(flat, 3));
  const mat = new THREE.LineBasicMaterial({
    color: ALL_EDGES_COLOR,
    transparent: true,
    opacity: ALL_EDGES_OPACITY,
    depthWrite: false,
  });
  allEdgesLine = new THREE.LineSegments(geo, mat);
  allEdgesLine.name = "edge-picker-all-edges";
  allEdgesLine.frustumCulled = false;
  scene.add(allEdgesLine);
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
let selObjs = { line: null, face: null, ends: null, click: null };
let selection = null; // {type:"edge", edge, point} | {type:"face", gid, solid, face, point}
let hoverLine = null;
let hoverId = -1;

function clearSelection() {
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
}

// --- text formatting for the copy blob ---
// fnum/fpt/formatFace come from pick-format.js so the find box parses
// exactly what we emit.
function edgeText(sel) {
  const e = sel.edge;
  if (e.kind === "loop") {
    return `circle ⌀${(e.radius * 2).toFixed(3)} · center ${fpt(e.center)} · circumference ${e.length.toFixed(3)} · axis ${fpt(e.axis)}`;
  }
  let tail;
  if (e.kind === "straight") tail = `len ${e.length.toFixed(3)} · straight · dir ${fpt(e.dir)}`;
  else if (e.kind === "arc") tail = `len ${e.length.toFixed(3)} · arc r=${e.radius.toFixed(3)} · center ${fpt(e.center)} · axis ${fpt(e.axis)}`;
  else tail = `len ${e.length.toFixed(3)} · curve`;
  return `${fpt(e.a)} → ${fpt(e.b)} · ${tail}`;
}
function clickText(sel) { return fpt(sel.point); }
function selFaceTexts(sel) {
  if (sel.type === "face") return { a: formatFace(sel.face), b: null };
  const ids = sel.edge.faceIds || [];
  return { a: formatFace(classifyFace(ids[0])), b: formatFace(classifyFace(ids[1])) };
}

// The open file as the viewer fetched it (edition-root-relative), plus the
// repo-relative path for the Copy-all locator and the bare name for the header.
function currentFile() { return (state.mountedDetail && state.mountedDetail.file) || null; }
function repoPath(file) {
  let lite = false;
  try { lite = localStorage.getItem("hsmEdition") === "lite"; } catch {}
  return (lite ? "pie-in-the-sky/lite" : "hardware") + "/" + file;
}
function headerName(file) { return file.split("/").pop().replace(/\.step$/i, ""); }

function allText(sel) {
  const lines = [];
  const file = currentFile();
  if (file) lines.push(`file: ${repoPath(file)}`);
  // Only assemblies carry real component names; single-solid STEPs get a
  // generic translator string from occt, which is noise — skip it.
  const solid = sel.type === "face" ? sel.solid : sel.edge.solid;
  if (isAssembly && solid && !/^Open CASCADE STEP translator/.test(solid)) {
    lines.push(`solid: ${solid}`);
  }
  if (sel.type === "face") {
    lines.push(`face: ${selFaceTexts(sel).a}`);
  } else {
    const faces = selFaceTexts(sel);
    lines.push(`edge: ${edgeText(sel)}`);
    if (faces.a) lines.push(`faceA: ${faces.a}`);
    if (faces.b) lines.push(`faceB: ${faces.b}`);
  }
  lines.push(`click: ${clickText(sel)}`);
  return lines.join("\n");
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
  const fileEl = document.createElement("span");
  fileEl.className = "edge-panel-file";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", () => clearSelection());
  head.appendChild(title);
  head.appendChild(fileEl);
  head.appendChild(close);
  panel.appendChild(head);
  panel._fileEl = fileEl;

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
    faceA: mkRow("Face A"),
    faceB: mkRow("Face B"),
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
  const isFace = sel.type === "face";
  const faces = selFaceTexts(sel);
  panel.querySelector(".edge-panel-title").textContent = isFace ? "Face" : "Edge";
  panelRows.edge.row.style.display = isFace ? "none" : "";
  if (!isFace) panelRows.edge.val.textContent = edgeText(sel);
  panelRows.faceA.lab.textContent = isFace ? "Face" : "Face A";
  panelRows.faceA.row.style.display = faces.a ? "" : "none";
  panelRows.faceA.val.textContent = faces.a || "";
  panelRows.faceB.row.style.display = !isFace && faces.b ? "" : "none";
  panelRows.faceB.val.textContent = faces.b || "";
  panelRows.click.val.textContent = clickText(sel);
  const file = currentFile();
  panel._fileEl.textContent = file ? headerName(file) : "";
  panel._fileEl.title = file ? repoPath(file) : "";
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
  // Edge picking is screen-space and ignores occlusion, so on a busy
  // model some hidden edge is almost always within the pick threshold.
  // Compare against the surface under the cursor: an edge clearly BEHIND
  // it is occluded — the user is looking at the face, so pick the face.
  const edgeHit = pickEdge(e.clientX, e.clientY);
  const faceHit = pickFace(e.clientX, e.clientY);
  let sel = null;
  if (edgeHit && faceHit) {
    const de = edgeHit.point.distanceTo(camera.position);
    const df = faceHit.point.distanceTo(camera.position);
    sel = df < de - Math.max(0.5, de * 0.002)
      ? faceHit
      : { type: "edge", edge: edgeHit.edge, point: edgeHit.point };
  } else if (edgeHit) {
    sel = { type: "edge", edge: edgeHit.edge, point: edgeHit.point };
  } else if (faceHit) {
    sel = faceHit;
  }
  if (sel) drawSelection(sel);
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
  disposeAllEdgesLayer();
  edgeSource = null;
  activeEdges = null;
  isAssembly = false;
  meshRecs = null;
  faceTable = null;
  faceClass = null;
}

export function setEdgePickEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  if (enabled) {
    ensureAllEdgesLayer();
  } else {
    clearSelection();
    setHover(null);
    if (allEdgesLine) allEdgesLine.visible = false;
  }
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
