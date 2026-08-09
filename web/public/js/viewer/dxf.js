// DXF-format module. Owns the inline parser, the wireframe + extruded
// meshers, the network + parse + scene-mount loader, the per-format
// camera reset (DXF lays flat on world XY so the framing differs from
// STEP), and the offscreen thumbnail renderer.
//
// DXF is a text format of repeating (group code, value) line pairs. We
// only handle the entity types that appear in this project's CAM-exported
// sheet-metal files: LINE, CIRCLE, ARC, LWPOLYLINE. Bigger DXFs (3DSOLID,
// SPLINE, INSERT/blocks, HATCH, TEXT) would need a real library; if a
// future part needs them, swap this for npm dxf-parser. For now the inline
// parser is ~80 lines and avoids a CDN/bundler dependency.
//
// Files lay flat on the world XY plane at Z=0. The shared scene + camera
// + OrbitControls + ViewCube already work for that — orbiting around a
// flat plate is the same UX Fusion 360 / Onshape give you when you import
// a 2D DXF onto a sketch plane. (Thickness extrusion is a future polish:
// if the user wants extruded plates, walk closed loops + ExtrudeGeometry.)
// $INSUNITS group code 70 in the HEADER section. Files in this project
// come from CadQuery (mm, INSUNITS=4) and SendCutSend (often INSUNITS=1
// inches), so we normalize to mm before handing to the viewer.

import * as THREE from "three";
import { state } from "./state.js";
import { scene, camera, controls, resizeRenderer, fitCameraDepth } from "./scene.js";
import { thumbRenderer, thumbScene, thumbCam } from "./step.js";

const DXF_UNIT_TO_MM = {
  0: 1,        // unitless — treat as mm
  1: 25.4,     // inches
  2: 304.8,    // feet
  4: 1,        // mm
  5: 10,       // cm
  6: 1000,     // meters
};

function parseDxf(text) {
  const lines = text.split(/\r?\n/);
  // Group codes come in pairs: [code, value], one per line each. Code
  // lines have leading whitespace ("  0", " 10"); values can be anything.
  const pairs = [];
  for (let i = 0; i + 1 < lines.length; i += 2) {
    const code = parseInt(lines[i].trim(), 10);
    if (Number.isNaN(code)) continue;
    pairs.push({ code, value: lines[i + 1] });
  }

  const entities = [];
  let insUnits = 0;
  let pendingHeaderVar = null;
  let inHeader = false;
  let inEntities = false;
  let cur = null;
  for (let i = 0; i < pairs.length; i++) {
    const { code, value } = pairs[i];
    const v = value.trim();

    if (code === 0 && v === "SECTION") {
      const next = pairs[i + 1];
      if (next && next.code === 2) {
        const sec = next.value.trim();
        inHeader = sec === "HEADER";
        inEntities = sec === "ENTITIES";
      }
      continue;
    }
    if (code === 0 && v === "ENDSEC") {
      if (inEntities && cur) { entities.push(cur); cur = null; }
      inHeader = false;
      inEntities = false;
      continue;
    }

    if (inHeader) {
      if (code === 9) pendingHeaderVar = v;
      else if (pendingHeaderVar === "$INSUNITS" && code === 70) {
        insUnits = parseInt(v, 10) || 0;
        pendingHeaderVar = null;
      }
      continue;
    }

    if (!inEntities) continue;

    if (code === 0) {
      if (cur) entities.push(cur);
      cur = null;
      if (v === "LINE" || v === "CIRCLE" || v === "ARC") {
        cur = { type: v };
      } else if (v === "LWPOLYLINE") {
        cur = { type: v, vertices: [], flags: 0 };
      }
      continue;
    }
    if (!cur) continue;

    const num = parseFloat(v);
    if (cur.type === "LWPOLYLINE") {
      // For LWPOLYLINE, codes 10/20 repeat per vertex (no Z).
      if (code === 10) cur.vertices.push({ x: num, y: 0 });
      else if (code === 20) {
        const last = cur.vertices[cur.vertices.length - 1];
        if (last) last.y = num;
      } else if (code === 70) cur.flags = num;
      continue;
    }
    if (code === 10) cur.x = num;
    else if (code === 20) cur.y = num;
    else if (code === 11) cur.x2 = num;
    else if (code === 21) cur.y2 = num;
    else if (code === 40) cur.r = num;
    else if (code === 50) cur.startAngle = num;
    else if (code === 51) cur.endAngle = num;
  }
  if (cur) entities.push(cur);

  // Normalize coordinates to mm so the rest of the viewer (and the
  // sidecar's thickness_mm) all share one unit. SendCutSend exports come
  // in inches (INSUNITS=1); CadQuery generators write mm (INSUNITS=4).
  const scale = DXF_UNIT_TO_MM[insUnits] ?? 1;
  if (scale !== 1) {
    for (const e of entities) {
      if ("x" in e) e.x *= scale;
      if ("y" in e) e.y *= scale;
      if ("x2" in e) e.x2 *= scale;
      if ("y2" in e) e.y2 *= scale;
      if ("r" in e) e.r *= scale;
      if (e.vertices) for (const v of e.vertices) { v.x *= scale; v.y *= scale; }
    }
  }

  return { entities, units: insUnits, scale };
}

const DXF_ARC_SEGS = 96;
const DXF_CHAIN_TOL = 0.005; // mm — endpoint-match tolerance for chaining LINE+ARC into closed loops

function entityEndpoints(e) {
  if (e.type === "LINE") {
    return [{ x: e.x, y: e.y }, { x: e.x2, y: e.y2 }];
  }
  if (e.type === "ARC") {
    const startA = (e.startAngle ?? 0) * Math.PI / 180;
    let endA = (e.endAngle ?? 360) * Math.PI / 180;
    while (endA <= startA) endA += Math.PI * 2;
    return [
      { x: e.x + e.r * Math.cos(startA), y: e.y + e.r * Math.sin(startA) },
      { x: e.x + e.r * Math.cos(endA),   y: e.y + e.r * Math.sin(endA) },
    ];
  }
  if (e.type === "LWPOLYLINE" && (e.flags & 1) !== 1 && e.vertices.length > 0) {
    const v = e.vertices;
    return [{ x: v[0].x, y: v[0].y }, { x: v[v.length - 1].x, y: v[v.length - 1].y }];
  }
  return null;
}

function ptKey(x, y) {
  return Math.round(x / DXF_CHAIN_TOL) + "," + Math.round(y / DXF_CHAIN_TOL);
}
function ptsEqual(a, b) {
  return Math.abs(a.x - b.x) < DXF_CHAIN_TOL && Math.abs(a.y - b.y) < DXF_CHAIN_TOL;
}

// Tessellate one chained entity into points, given which endpoint we
// entered from. Pushed onto `pts` (excluding the entry point itself —
// that was already pushed by the previous step or the loop-start).
function appendEntityPoints(pts, e, enteredAt) {
  if (e.type === "LINE") {
    const eps = entityEndpoints(e);
    pts.push(ptsEqual(eps[0], enteredAt) ? eps[1] : eps[0]);
    return;
  }
  if (e.type === "ARC") {
    const cx = e.x, cy = e.y, r = e.r;
    const startA = (e.startAngle ?? 0) * Math.PI / 180;
    let endA = (e.endAngle ?? 360) * Math.PI / 180;
    while (endA <= startA) endA += Math.PI * 2;
    const eps = entityEndpoints(e);
    const forward = ptsEqual(eps[0], enteredAt);
    const span = endA - startA;
    const segs = Math.max(8, Math.ceil((span / (Math.PI * 2)) * DXF_ARC_SEGS));
    for (let i = 1; i <= segs; i++) {
      const t = i / segs;
      const a = forward ? (startA + span * t) : (endA - span * t);
      pts.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });
    }
    return;
  }
  if (e.type === "LWPOLYLINE") {
    const eps = entityEndpoints(e);
    const forward = ptsEqual(eps[0], enteredAt);
    const verts = forward ? e.vertices.slice(1) : e.vertices.slice(0, -1).reverse();
    for (const v of verts) pts.push({ x: v.x, y: v.y });
    return;
  }
}

// Walk LINE / ARC / open-LWPOLYLINE entities and find closed loops by
// matching endpoints (within DXF_CHAIN_TOL). Each loop comes back as an
// ordered array of {x,y} points around its perimeter — ready to feed
// into THREE.Shape / THREE.Path.
function findClosedChains(openEntities) {
  if (openEntities.length === 0) return [];
  for (let i = 0; i < openEntities.length; i++) openEntities[i]._id = i;

  const adjacency = new Map(); // ptKey -> [{entity, endpointIdx}]
  for (const e of openEntities) {
    const eps = entityEndpoints(e);
    if (!eps) continue;
    for (let i = 0; i < 2; i++) {
      const k = ptKey(eps[i].x, eps[i].y);
      if (!adjacency.has(k)) adjacency.set(k, []);
      adjacency.get(k).push({ entity: e, endpointIdx: i });
    }
  }

  const used = new Set();
  const loops = [];
  for (const startEntity of openEntities) {
    if (used.has(startEntity._id)) continue;
    const startEps = entityEndpoints(startEntity);
    if (!startEps) { used.add(startEntity._id); continue; }

    const points = [{ x: startEps[0].x, y: startEps[0].y }];
    appendEntityPoints(points, startEntity, startEps[0]);
    used.add(startEntity._id);

    let currentEnd = startEps[1];
    let safety = openEntities.length + 1;
    let closed = false;
    while (safety-- > 0) {
      if (ptsEqual(currentEnd, startEps[0])) { closed = true; break; }
      const k = ptKey(currentEnd.x, currentEnd.y);
      const candidates = (adjacency.get(k) || []).filter((c) => !used.has(c.entity._id));
      if (candidates.length === 0) break; // dead end → not a closed loop
      const next = candidates[0];
      used.add(next.entity._id);
      const nextEps = entityEndpoints(next.entity);
      const enteredAt = nextEps[next.endpointIdx];
      const exitAt = next.endpointIdx === 0 ? nextEps[1] : nextEps[0];
      appendEntityPoints(points, next.entity, enteredAt);
      currentEnd = exitAt;
    }
    if (closed) {
      // Drop the trailing duplicate of the start point if the last appended point matches.
      if (points.length > 1 && ptsEqual(points[points.length - 1], points[0])) points.pop();
      loops.push(points);
    }
  }
  return loops;
}

function pointsFromCircle(e) {
  const pts = [];
  const cx = e.x, cy = e.y, r = e.r;
  for (let i = 0; i < DXF_ARC_SEGS; i++) {
    const a = (i / DXF_ARC_SEGS) * Math.PI * 2;
    pts.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });
  }
  return pts;
}

function signedArea(pts) {
  let a = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    a += pts[i].x * pts[j].y - pts[j].x * pts[i].y;
  }
  return a / 2;
}
function pointsArea(pts) { return Math.abs(signedArea(pts)); }
function ensureWinding(pts, wantCCW) {
  return (signedArea(pts) > 0) === wantCCW ? pts : pts.slice().reverse();
}

// Wireframe fallback — LINE / CIRCLE / ARC / LWPOLYLINE rendered as
// LineSegments at Z=0. Used when there's no thickness sidecar (or no
// closed loops to extrude).
function buildDxfWireframe(parsed) {
  const positions = [];
  const pushSeg = (x1, y1, x2, y2) => positions.push(x1, y1, 0, x2, y2, 0);
  for (const e of parsed.entities) {
    if (e.type === "LINE") {
      pushSeg(e.x ?? 0, e.y ?? 0, e.x2 ?? 0, e.y2 ?? 0);
    } else if (e.type === "CIRCLE") {
      const cx = e.x ?? 0, cy = e.y ?? 0, r = e.r ?? 0;
      let prev = null;
      for (let i = 0; i <= DXF_ARC_SEGS; i++) {
        const a = (i / DXF_ARC_SEGS) * Math.PI * 2;
        const x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
        if (prev) pushSeg(prev.x, prev.y, x, y);
        prev = { x, y };
      }
    } else if (e.type === "ARC") {
      const cx = e.x ?? 0, cy = e.y ?? 0, r = e.r ?? 0;
      const start = (e.startAngle ?? 0) * Math.PI / 180;
      let end = (e.endAngle ?? 360) * Math.PI / 180;
      while (end <= start) end += Math.PI * 2;
      const span = end - start;
      const segs = Math.max(8, Math.ceil((span / (Math.PI * 2)) * DXF_ARC_SEGS));
      let prev = null;
      for (let i = 0; i <= segs; i++) {
        const a = start + span * (i / segs);
        const x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
        if (prev) pushSeg(prev.x, prev.y, x, y);
        prev = { x, y };
      }
    } else if (e.type === "LWPOLYLINE") {
      const verts = e.vertices;
      for (let i = 0; i < verts.length - 1; i++) {
        pushSeg(verts[i].x, verts[i].y, verts[i + 1].x, verts[i + 1].y);
      }
      if ((e.flags & 1) === 1 && verts.length > 1) {
        const a = verts[verts.length - 1], b = verts[0];
        pushSeg(a.x, a.y, b.x, b.y);
      }
    }
  }
  const group = new THREE.Group();
  if (positions.length === 0) return group;
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(positions), 3));
  group.add(new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x88ccff })));
  return group;
}

// Extruded DXF: collect closed loops (CIRCLE, closed LWPOLYLINE, plus
// LINE+ARC chains that close), pick the largest as outer, the rest as
// holes, build THREE.Shape, extrude by thickness_mm. Falls back to
// wireframe if there's no thickness or no closed loops.
function buildDxfMesh(parsed, thicknessMm) {
  const closedLoops = []; // array of point arrays
  const openEntities = [];
  for (const e of parsed.entities) {
    if (e.type === "CIRCLE") {
      closedLoops.push(pointsFromCircle(e));
    } else if (e.type === "LWPOLYLINE" && (e.flags & 1) === 1) {
      closedLoops.push(e.vertices.map((v) => ({ x: v.x, y: v.y })));
    } else if (e.type === "LINE" || e.type === "ARC" || e.type === "LWPOLYLINE") {
      openEntities.push(e);
    }
  }
  for (const loop of findClosedChains(openEntities)) closedLoops.push(loop);

  if (!thicknessMm || closedLoops.length === 0) return buildDxfWireframe(parsed);

  // Largest = outer, rest = holes. THREE.Shape wants outer CCW, holes CW.
  closedLoops.sort((a, b) => pointsArea(b) - pointsArea(a));
  const outerPts = ensureWinding(closedLoops[0], true);
  const holesPts = closedLoops.slice(1).map((p) => ensureWinding(p, false));

  const shape = new THREE.Shape(outerPts.map((p) => new THREE.Vector2(p.x, p.y)));
  for (const hole of holesPts) {
    shape.holes.push(new THREE.Path(hole.map((p) => new THREE.Vector2(p.x, p.y))));
  }

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: thicknessMm,
    bevelEnabled: false,
    curveSegments: 64,
  });
  geo.computeVertexNormals();

  // Steel-blue plate — matched to STEP's neutral metal look so prints
  // and cuts read as part of the same family in the viewer.
  const mat = new THREE.MeshStandardMaterial({ color: 0x8899aa, metalness: 0.2, roughness: 0.55 });
  const mesh = new THREE.Mesh(geo, mat);

  // Edge wireframe at 30° threshold — picks out the perimeter top/bottom
  // and any sharp corners without showing the triangulation of curves.
  const edges = new THREE.EdgesGeometry(geo, 30);
  const edgeLines = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({ color: 0xaaccff, transparent: true, opacity: 0.7 }),
  );

  const group = new THREE.Group();
  group.add(mesh);
  group.add(edgeLines);
  return group;
}

export async function loadDxfFile(file, { preserveCamera = false } = {}) {
  const loadingEl = state.currentCadWrapper && state.currentCadWrapper.querySelector(".cad-loading");
  if (loadingEl) loadingEl.style.display = "block";

  try {
    const headers = {};
    const prevEtag = state.dxfEtags.get(file);
    if (state.mountedDetail?.type === "dxf" && state.mountedDetail.file === file && prevEtag) {
      headers["If-None-Match"] = prevEtag;
    }
    const resp = await fetch(`/dxfs/${file}`, { headers });
    if (resp.status === 304) return;
    if (!resp.ok) return;
    const etag = resp.headers.get("etag");
    if (etag) state.dxfEtags.set(file, etag);

    const text = await resp.text();
    const parsed = parseDxf(text);

    if (state.currentGroup) {
      scene.remove(state.currentGroup);
      state.currentGroup.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
    }

    const meta = state.dxfMeta.get(file) || {};
    const thickness = typeof meta.thickness_mm === "number" ? meta.thickness_mm : null;
    state.currentGroup = buildDxfMesh(parsed, thickness);
    scene.add(state.currentGroup);
    state.mountedDetail = { type: "dxf", file };
    if (!preserveCamera) resetDxfCamera(state.currentGroup, !!thickness);
  } finally {
    if (loadingEl) loadingEl.style.display = "none";
  }
}

// DXF lives on the world XY plane (extrudes upward in +Z when there's a
// thickness). For extruded plates we land on a 3/4 isometric so the
// thickness is visible from the moment the modal opens — that's the
// whole point of the sidecar. For wireframe-only (no sidecar) we fall
// back to top-down since there's nothing to see edge-on. Distance is
// aspect-aware so a wide plate doesn't clip in a narrow phone viewport.
export function resetDxfCamera(group, hasThickness) {
  resizeRenderer(); // make sure camera.aspect reflects the wrapper

  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const sx = Math.max(size.x, 1);
  const sy = Math.max(size.y, 1);
  const sz = Math.max(size.z, 0);
  const fovRad = camera.fov * Math.PI / 180;
  const aspect = camera.aspect || 1;
  // Project the bounding box onto the camera plane for whichever view
  // we're picking, then size the distance so it fits in BOTH dimensions.
  const distFor = (hView, vView) => {
    const distH = vView / (2 * Math.tan(fovRad / 2));
    const distW = hView / (aspect * 2 * Math.tan(fovRad / 2));
    return Math.max(distH, distW);
  };

  if (hasThickness) {
    // Isometric — camera offset by (1,1,1) normalized from the bbox
    // center. `center` is already the middle of the extruded volume
    // (i.e. z = thickness/2), so no extra Z bias is needed.
    const planar = Math.max(sx, sy);
    const dist = distFor(planar, planar * 0.85 + sz) * 1.2;
    const off = dist / Math.sqrt(3);
    camera.position.set(center.x + off, center.y + off, center.z + off);
    camera.up.set(0, 0, 1);
    camera.lookAt(center);
    controls.target.copy(center);
  } else {
    // Top-down for the un-sidecar'd wireframe case.
    const dist = distFor(sx, sy) * 1.15;
    camera.position.set(center.x, center.y, center.z + dist);
    camera.up.set(0, 1, 0);
    camera.lookAt(center);
    controls.target.copy(center);
  }
  controls.update();
}

export async function renderDxfThumbnail(file) {
  if (state.dxfThumbCache.has(file)) return state.dxfThumbCache.get(file);

  try {
    const resp = await fetch(`/dxfs/${file}`);
    if (!resp.ok) return null;
    const text = await resp.text();
    const parsed = parseDxf(text);
    const meta = state.dxfMeta.get(file) || {};
    const thickness = typeof meta.thickness_mm === "number" ? meta.thickness_mm : null;
    const group = buildDxfMesh(parsed, thickness);
    thumbScene.add(group);

    const box = new THREE.Box3().setFromObject(group);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxPlanar = Math.max(size.x, size.y, 1);
    if (thickness) {
      // Same iso framing as the detail view, so thumbs and the modal
      // open look like the same part.
      const dist = maxPlanar * 1.6;
      const off = dist / Math.sqrt(3);
      thumbCam.position.set(center.x + off, center.y + off, center.z + off + size.z);
      thumbCam.up.set(0, 0, 1);
      thumbCam.lookAt(center.x, center.y, center.z + size.z / 2);
    } else {
      // Wireframe → top-down, edge-on iso would show nothing.
      thumbCam.position.set(center.x, center.y, center.z + maxPlanar * 1.4);
      thumbCam.up.set(0, 1, 0);
      thumbCam.lookAt(center);
    }
    fitCameraDepth(thumbCam, center, size.length() / 2);

    thumbRenderer.render(thumbScene, thumbCam);
    const dataURL = thumbRenderer.domElement.toDataURL();

    thumbScene.remove(group);
    group.traverse((c) => { if (c.geometry) c.geometry.dispose(); });

    state.dxfThumbCache.set(file, dataURL);
    return dataURL;
  } catch {
    return null;
  }
}
