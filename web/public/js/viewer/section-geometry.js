// Slice the installed mesh at the picked plane, preserving holes and each solid's placement.
import * as THREE from "three";
import { visitSectionRanges } from "./surface-query.js";
import { surfacePlacement } from "./picked-face.js";

const weld = 1e-4;

// Principal curvature gives a swept tube's local tangent even where its centreline bends.
export function sectionCurveAt({ object, faceIndex, instanceId, face, edge }) {
  if ((edge?.kind === "loop" || edge?.kind === "arc") && edge.axis) return { axis: edge.axis, radius: edge.radius };
  if (face?.kind === "cylinder") return { axis: face.dir, radius: face.r };
  if (face?.kind === "plane" || !object?.geometry || !Number.isInteger(faceIndex)) return null;
  const { geometry } = object;
  const { position, normal } = geometry.attributes;
  if (!position || !normal) return null;
  const matrix = surfacePlacement(object, instanceId);
  const normalMatrix = new THREE.Matrix3().getNormalMatrix(matrix);
  const ids = [0, 1, 2].map(i => geometry.index?.getX(faceIndex * 3 + i) ?? faceIndex * 3 + i);
  const p = ids.map(id => new THREE.Vector3().fromBufferAttribute(position, id).applyMatrix4(matrix));
  const n = ids.map(id => new THREE.Vector3().fromBufferAttribute(normal, id).applyNormalMatrix(normalMatrix));
  const ab = p[1].sub(p[0]), ac = p[2].sub(p[0]), len = ab.length();
  if (len < 1e-8) return null;
  const u = ab.divideScalar(len);
  const x = ac.dot(u), v = ac.addScaledVector(u, -x), y = v.length();
  if (y < 1e-8) return null;
  v.divideScalar(y);
  const dn = n[1].sub(n[0]).divideScalar(len);
  const dm = n[2].sub(n[0]).addScaledVector(dn, -x).divideScalar(y);
  const a = dn.dot(u), c = dm.dot(v), b = (dn.dot(v) + dm.dot(u)) / 2;
  const mid = (a + c) / 2, half = Math.hypot((a - c) / 2, b);
  const first = mid - half, second = mid + half;
  const [low, high] = Math.abs(first) < Math.abs(second) ? [first, second] : [second, first];
  if (Math.abs(high) < 1e-4 || Math.abs(low) * 2 > Math.abs(high)) return null;
  const v1 = new THREE.Vector2(b, low - a), v2 = new THREE.Vector2(low - c, b);
  const direction = (v1.lengthSq() > v2.lengthSq() ? v1 : v2).normalize();
  return { axis: u.multiplyScalar(direction.x).addScaledVector(v, direction.y), radius: 1 / Math.abs(high) };
}

function outlines(vertices, pairs) {
  const links = Array.from(vertices, () => []);
  const edges = [];
  for (const { a, b, wall, coplanar } of pairs.values()) {
    if (!wall && !coplanar) continue;
    const id = edges.push([a, b]) - 1;
    links[a].push(id);
    links[b].push(id);
  }
  const used = new Uint8Array(edges.length), paths = [];
  function trace(start, id) {
    let node = start;
    const points = [vertices[start]];
    while (id !== undefined) {
      used[id] = 1;
      const [a, b] = edges[id];
      node = node === a ? b : a;
      if (node === start) break;
      points.push(vertices[node]);
      id = links[node].find(next => !used[next]);
    }
    const closed = node === start && points.length >= 3;
    if (points.length >= 2) paths.push({ points, closed });
  }
  for (let i = 0; i < links.length; i++) {
    if (links[i].length !== 2) for (const id of links[i]) if (!used[id]) trace(i, id);
  }
  for (let id = 0; id < edges.length; id++) if (!used[id]) trace(edges[id][0], id);
  return paths;
}

function* sliceMesh(mesh, transform) {
  const inverse = transform.clone().invert();
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0).applyMatrix4(inverse);
  const ranges = [];
  visitSectionRanges(mesh, plane, (first, last) => ranges.push([first, last]));
  const { index, attributes, drawRange } = mesh.geometry;
  const begin = Math.ceil(drawRange.start / 3), end = (drawRange.start + drawRange.count) / 3;
  const vertices = [], pairs = new Map(), ids = new Map();
  const corners = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
  const ds = [0, 0, 0], intersections = [0, 0, 0], crossing = new THREE.Vector3(), projected = new THREE.Vector3();
  function vertexId(local) {
    projected.copy(local).applyMatrix4(transform);
    const key = Math.round(projected.x / weld) + "/" + Math.round(projected.y / weld);
    if (ids.has(key)) return ids.get(key);
    const id = vertices.push(new THREE.Vector2(projected.x, projected.y)) - 1;
    ids.set(key, id);
    return id;
  }
  function segment(a, b, coplanar = false) {
    if (a === b) return;
    const key = a < b ? a + "/" + b : b + "/" + a;
    let pair = pairs.get(key);
    if (!pair) { pair = { a, b, coplanar: false, wall: false }; pairs.set(key, pair); }
    if (coplanar) pair.coplanar = !pair.coplanar;
    else pair.wall = true;
  }
  let batch = 0;
  for (const [first, last] of ranges) {
    for (let t = Math.max(first, begin), stop = Math.min(last, end); t < stop; t++) {
      if (++batch === 1024) { batch = 0; yield; }
      for (let i = 0; i < 3; i++) {
        const id = index?.getX(t * 3 + i) ?? t * 3 + i;
        corners[i].fromBufferAttribute(attributes.position, id);
        const distance = plane.distanceToPoint(corners[i]);
        ds[i] = Math.abs(distance) < 1e-7 ? 0 : distance;
      }
      if (ds[0] > 0 && ds[1] > 0 && ds[2] > 0 || ds[0] < 0 && ds[1] < 0 && ds[2] < 0) continue;
      if (!ds[0] && !ds[1] && !ds[2]) {
        const a = vertexId(corners[0]), b = vertexId(corners[1]), c = vertexId(corners[2]);
        segment(a, b, true); segment(b, c, true); segment(c, a, true);
        continue;
      }
      let count = 0;
      for (let i = 0; i < 3; i++) {
        const j = (i + 1) % 3;
        if (!ds[i]) intersections[count++] = vertexId(corners[i]);
        else if (ds[i] * ds[j] < 0) {
          crossing.lerpVectors(corners[i], corners[j], ds[i] / (ds[i] - ds[j]));
          intersections[count++] = vertexId(crossing);
        }
      }
      if (count === 2) segment(intersections[0], intersections[1]);
    }
  }
  return outlines(vertices, pairs);
}

// Parts in the profile window arrive first. The rest of the installed cut follows on the
// same plane, so orbiting in the model or panning the profile can reveal the whole cut.
export function* sectionRows(root, worldToProfile, windowBox) {
  root.updateWorldMatrix(true, true);
  const meshes = [];
  root.traverseVisible(mesh => {
    if (mesh.isMesh && mesh.userData.side === "front" && mesh.geometry?.attributes.position) meshes.push(mesh);
  });
  const box = new THREE.Box3(), near = [], far = [];
  for (const mesh of meshes) {
    const geometry = mesh.geometry;
    if (!geometry.boundingBox) geometry.computeBoundingBox();
    const count = mesh.isInstancedMesh ? mesh.count : 1;
    for (let i = 0; i < count; i++) {
      const transform = new THREE.Matrix4().multiplyMatrices(worldToProfile, surfacePlacement(mesh, i));
      box.copy(geometry.boundingBox).applyMatrix4(transform);
      if (box.min.z > 1e-6 || box.max.z < -1e-6) continue;
      const inWindow = box.min.x <= windowBox.max.x && box.min.y <= windowBox.max.y &&
        box.max.x >= windowBox.min.x && box.max.y >= windowBox.min.y;
      (inWindow ? near : far).push({ mesh, transform });
    }
  }
  for (const { mesh, transform } of [...near, ...far]) {
    const paths = yield* sliceMesh(mesh, transform);
    if (paths.length) yield { mesh, paths };
    else yield;
  }
}

// Fill only material between the nested boundaries of a solid.
export function sectionCap(paths) {
  const rings = paths.filter(path => path.closed).map(({ points }) => ({
    points, box: new THREE.Box2().setFromPoints(points), size: Math.abs(THREE.ShapeUtils.area(points)), depth: 0, holes: [],
  })).sort((a, b) => b.size - a.size);
  function contains(loop, p) {
    let inside = false;
    for (let i = 0, j = loop.length - 1; i < loop.length; j = i++) {
      const a = loop[i], b = loop[j];
      if ((a.y > p.y) !== (b.y > p.y) && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
    }
    return inside;
  }
  const vertices = [], indices = [];
  for (let i = 0; i < rings.length; i++) {
    const ring = rings[i];
    for (let j = i - 1; j >= 0; j--) {
      const outer = rings[j];
      if (outer.box.containsBox(ring.box) && contains(outer.points, ring.points[0])) {
        ring.depth = outer.depth + 1;
        if (ring.depth % 2) outer.holes.push(ring.points);
        break;
      }
    }
  }
  for (const ring of rings) {
    if (ring.depth % 2) continue;
    const triangles = THREE.ShapeUtils.triangulateShape(ring.points, ring.holes), start = vertices.length / 3;
    for (const loop of [ring.points, ...ring.holes]) for (const p of loop) vertices.push(p.x, p.y, 0);
    for (const triangle of triangles) for (const index of triangle) indices.push(start + index);
  }
  return { vertices, indices };
}
