// Picked CAD faces supply world-space planes and cylinder axes to the viewer's inspection tools.
import * as THREE from "three";
import { roundFitMeasured } from "./round-fit.js";

const orderedFaces = new WeakMap();

export function faceIndexAtTriangle(faces, triangle) {
  if (!faces?.length || !Number.isInteger(triangle) || triangle < 0) return -1;
  let ordered = orderedFaces.get(faces);
  if (ordered === undefined) {
    ordered = faces.every((face, i) => !i || faces[i - 1].last < face.first);
    orderedFaces.set(faces, ordered);
  }
  if (!ordered) return faces.findLastIndex(face => face.first <= triangle && triangle <= face.last);
  let lo = 0, hi = faces.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1, face = faces[mid];
    if (triangle < face.first) hi = mid;
    else if (triangle > face.last) lo = mid + 1;
    else return mid;
  }
  return -1;
}

export function surfacePlacement(object, instanceId) {
  object.updateWorldMatrix(true, false);
  if (!object.isInstancedMesh || !Number.isInteger(instanceId)) return object.matrixWorld;
  const matrix = new THREE.Matrix4();
  object.getMatrixAt(instanceId, matrix);
  return matrix.premultiply(object.matrixWorld);
}

export function classifyPickedSurface(hit) {
  const mesh = hit?.object, faces = mesh?.userData.brepFaces;
  const face = faces?.[faceIndexAtTriangle(faces, hit?.faceIndex)];
  const geometry = mesh?.geometry, position = geometry?.attributes.position;
  if (!face || !position || !geometry.index) return null;
  const source = { pos: position.array, nrm: geometry.attributes.normal?.array, idx: geometry.index.array };
  const surface = classifyFaceRange(source, face, surfacePlacement(mesh, hit.instanceId));
  if (face.sources) surface.sources = face.sources;
  return surface;
}

// Sample just the authored face. Optional placement is applied to its samples before fitting.
export function classifyFaceRange(rec, f, placement = null) {
  const normalMatrix = placement && new THREE.Matrix3().getNormalMatrix(placement);
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
      const position = new THREE.Vector3().fromArray(rec.pos, vi * 3);
      pts.push(placement ? position.applyMatrix4(placement) : position);
      if (rec.nrm) {
        const n = new THREE.Vector3().fromArray(rec.nrm, vi * 3);
        if (normalMatrix) n.applyMatrix3(normalMatrix);
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
      if (placement) {
        a.applyMatrix4(placement);
        b.applyMatrix4(placement);
        c.applyMatrix4(placement);
      }
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
        let maxRes = 0, xlo = Infinity, xhi = -Infinity, ylo = Infinity, yhi = -Infinity;
        for (const [x, y] of xy) {
          maxRes = Math.max(maxRes, Math.abs(Math.hypot(x - cx, y - cy) - r));
          if (x < xlo) xlo = x;
          if (x > xhi) xhi = x;
          if (y < ylo) ylo = y;
          if (y > yhi) yhi = y;
        }
        // The chord is taken in the axis-normal plane: a cylinder's axial run
        // is not arc, and letting it stand in for sweep passes a flat patch.
        if (roundFitMeasured(r, Math.hypot(xhi - xlo, yhi - ylo), maxRes)) {
          const axisPoint = centroid.clone().addScaledVector(u, cx).addScaledVector(v, cy);
          return { kind: "cylinder", r, axis: axisPoint, dir: axis };
        }
      }
    }
  }
  return { kind: "curved", near: centroid };
}
