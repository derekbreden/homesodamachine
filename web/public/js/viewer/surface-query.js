// Visible surface queries visit nearby solids first and skip triangle ranges outside the ray.
import * as THREE from "three";

const trianglesPerBox = 64;
const coordinates = 6;
const surfaceBounds = new WeakMap();
const arrays = new WeakMap();
const pending = new Set();
let scheduled = false;

function schedulePreparation() {
  if (scheduled || !pending.size) return;
  scheduled = true;
  if (globalThis.requestIdleCallback) requestIdleCallback(prepareSlice, { timeout: 120 });
  else setTimeout(prepareSlice, 0);
}

function prepareSlice() {
  scheduled = false;
  const deadline = performance.now() + 2;
  while (pending.size && performance.now() < deadline) {
    const entry = pending.values().next().value;
    const { positions, indices, boxes } = entry;
    const stop = Math.min(entry.next + 32, boxes.length / coordinates);
    for (; entry.next < stop; entry.next++) {
      const start = entry.next * trianglesPerBox * 3;
      const end = Math.min(start + trianglesPerBox * 3, indices.length);
      let x0 = Infinity, y0 = Infinity, z0 = Infinity;
      let x1 = -Infinity, y1 = -Infinity, z1 = -Infinity;
      for (let i = start; i < end; i++) {
        const j = indices[i] * 3;
        const x = positions[j], y = positions[j + 1], z = positions[j + 2];
        x0 = Math.min(x0, x); y0 = Math.min(y0, y); z0 = Math.min(z0, z);
        x1 = Math.max(x1, x); y1 = Math.max(y1, y); z1 = Math.max(z1, z);
      }
      const b = entry.next * coordinates;
      boxes[b] = x0; boxes[b + 1] = y0; boxes[b + 2] = z0;
      boxes[b + 3] = x1; boxes[b + 4] = y1; boxes[b + 5] = z1;
    }
    if (stop * coordinates === boxes.length) {
      pending.delete(entry);
      for (const ready of entry.waiters) ready(entry);
      entry.waiters.clear();
    }
  }
  schedulePreparation();
}

function rangesFor(positions, indices) {
  const previous = arrays.get(indices);
  if (previous?.positions === positions) return previous;
  const ranges = {
    positions, indices, next: 0, waiters: new Set(), owners: 0,
    boxes: new Float32Array(Math.ceil(indices.length / (trianglesPerBox * 3)) * coordinates),
  };
  arrays.set(indices, ranges);
  return ranges;
}

function stopUnused(ranges) {
  if (!ranges.owners && !ranges.waiters.size) pending.delete(ranges);
}

// A newly visible dense solid already has its complete picking index. Earlier geometry
// stays interactive while the incoming local arrays are prepared between paints.
export function prepareMeshSurfaces(meshes, signal) {
  signal?.throwIfAborted();
  const waiting = new Set();
  for (const mesh of meshes) {
    const positions = (mesh.localAttributes || mesh.attributes)?.position;
    const indices = mesh.localIndex || mesh.index;
    if (!positions || !indices || indices.array.length < 2048 * 3) continue;
    if (!(positions.array instanceof Float32Array)) positions.array = new Float32Array(positions.array);
    if (!(indices.array instanceof Uint32Array)) indices.array = new Uint32Array(indices.array);
    const ranges = rangesFor(positions.array, indices.array);
    if (ranges.next * coordinates < ranges.boxes.length) waiting.add(ranges);
  }
  if (!waiting.size) return;
  return new Promise((resolve, reject) => {
    function ready(ranges) {
      waiting.delete(ranges);
      if (!waiting.size) {
        signal?.removeEventListener("abort", abort);
        resolve();
      }
    }
    function abort() {
      for (const ranges of waiting) {
        ranges.waiters.delete(ready);
        stopUnused(ranges);
      }
      reject(signal.reason);
    }
    for (const ranges of waiting) {
      ranges.waiters.add(ready);
      pending.add(ranges);
    }
    signal?.addEventListener("abort", abort, { once: true });
    schedulePreparation();
  });
}

// Indexed geometry and its source payload share bounds without changing triangle order.
export function prepareSurface(geometry) {
  if (surfaceBounds.has(geometry)) return;
  const position = geometry.attributes.position, index = geometry.index;
  if (!index || index.count < 2048 * 3 || position?.itemSize !== 3 || position.isInterleavedBufferAttribute ||
      !(position.array instanceof Float32Array) || position.normalized || geometry.morphAttributes.position?.length) return;
  const ranges = rangesFor(position.array, index.array);
  surfaceBounds.set(geometry, { ranges, positionVersion: position.version, indexVersion: index.version });
  if (ranges.next * coordinates === ranges.boxes.length) return;
  ranges.owners++;
  pending.add(ranges);
  geometry.addEventListener("dispose", function forget() {
    ranges.owners--;
    stopUnused(ranges);
    surfaceBounds.delete(geometry);
    geometry.removeEventListener("dispose", forget);
  });
  schedulePreparation();
}

const localRay = new THREE.Ray(), inverse = new THREE.Matrix4();
const point = new THREE.Vector3(), box = new THREE.Box3();
const worldBounds = new WeakMap();

function distanceToMesh(ray, mesh) {
  const geometry = mesh.geometry;
  let entry = worldBounds.get(mesh);
  const position = geometry.attributes.position;
  if (!position?.count) return Infinity;
  const changed = entry?.geometry === geometry && (entry.position !== position || entry.version !== position.version);
  if (!geometry.boundingBox || changed) geometry.computeBoundingBox();
  if (changed && geometry.boundingSphere) geometry.computeBoundingSphere();
  if (!entry || entry.geometry !== geometry || !entry.matrix.equals(mesh.matrixWorld) ||
      changed || !entry.local.equals(geometry.boundingBox)) {
    entry ??= { matrix: new THREE.Matrix4(), local: new THREE.Box3(), world: new THREE.Box3() };
    entry.geometry = geometry;
    entry.position = position;
    entry.version = position.version;
    entry.matrix.copy(mesh.matrixWorld);
    entry.local.copy(geometry.boundingBox);
    entry.world.copy(entry.local).applyMatrix4(entry.matrix);
    worldBounds.set(mesh, entry);
  }
  if (entry.world.containsPoint(ray.origin)) return 0;
  return ray.intersectBox(entry.world, point) ? point.distanceTo(ray.origin) : Infinity;
}

function visible(mesh) {
  for (let node = mesh; node; node = node.parent) if (!node.visible) return false;
  return true;
}

// A coordinate inspection visits only original triangle ranges overlapping its world-space box.
export function visitSurfaceRanges(mesh, bounds, visit) {
  const geometry = mesh.geometry;
  const length = geometry.index?.count || geometry.attributes.position?.count || 0;
  if (!length) return;
  const local = bounds.clone().applyMatrix4(inverse.copy(mesh.matrixWorld).invert());
  if (!geometry.boundingBox) geometry.computeBoundingBox();
  if (!local.intersectsBox(geometry.boundingBox)) return;
  const binding = surfaceBounds.get(geometry), entry = binding?.ranges;
  if (!entry || entry.positions !== geometry.attributes.position.array || entry.indices !== geometry.index?.array ||
      binding.positionVersion !== geometry.attributes.position.version || binding.indexVersion !== geometry.index?.version) {
    visit(0, length / 3);
    return;
  }
  let open = -1;
  for (let i = 0; i < entry.next; i++) {
    const offset = i * coordinates, values = entry.boxes;
    const overlaps = values[offset] <= local.max.x && values[offset + 1] <= local.max.y && values[offset + 2] <= local.max.z &&
      values[offset + 3] >= local.min.x && values[offset + 4] >= local.min.y && values[offset + 5] >= local.min.z;
    if (overlaps) {
      if (open < 0) open = i * trianglesPerBox;
    } else if (open >= 0) {
      visit(open, i * trianglesPerBox);
      open = -1;
    }
  }
  if (open < 0) open = entry.next * trianglesPerBox;
  if (open < length / 3) visit(open, length / 3);
}

function castRanges(raycaster, mesh, hits) {
  const geometry = mesh.geometry, binding = surfaceBounds.get(geometry), entry = binding?.ranges;
  const { start, count } = geometry.drawRange;
  if (!entry?.next || mesh.raycast !== THREE.Mesh.prototype.raycast || start % 3 ||
      entry.positions !== geometry.attributes.position.array || entry.indices !== geometry.index?.array ||
      binding.positionVersion !== geometry.attributes.position.version || binding.indexVersion !== geometry.index?.version) {
    mesh.raycast(raycaster, hits);
    return;
  }
  localRay.copy(raycaster.ray).applyMatrix4(inverse.copy(mesh.matrixWorld).invert());
  const end = Math.min(start + count, geometry.index.count);
  const stride = trianglesPerBox * 3;
  let open = -1;
  // Joining adjacent hit boxes lets Three resolve its own draw range, material side, UV and face.
  try {
    for (let i = Math.floor(start / stride); i < entry.next && i * stride < end; i++) {
      const offset = i * coordinates;
      box.min.fromArray(entry.boxes, offset);
      box.max.fromArray(entry.boxes, offset + 3);
      if (localRay.intersectsBox(box)) {
        if (open < 0) open = Math.max(start, i * stride);
      } else if (open >= 0) {
        geometry.setDrawRange(open, i * stride - open);
        mesh.raycast(raycaster, hits);
        open = -1;
      }
    }
    // An unfinished index still tests every triangle beyond the prepared prefix.
    if (open < 0) open = Math.max(start, entry.next * stride);
    if (open < end) {
      geometry.setDrawRange(open, end - open);
      mesh.raycast(raycaster, hits);
    }
  } finally { geometry.setDrawRange(start, count); }
}

export function nearestSurface(raycaster, meshes, acceptHit) {
  const candidates = [], hits = [];
  const far = raycaster.far;
  let nearest = null, nearestOrder = Infinity;
  for (const mesh of Array.isArray(meshes) ? meshes : [meshes]) {
    if (!mesh?.isMesh || !raycaster.layers.test(mesh.layers) || !visible(mesh)) continue;
    const ordinary = mesh.raycast === THREE.Mesh.prototype.raycast && !mesh.morphTargetInfluences;
    const distance = ordinary ? distanceToMesh(raycaster.ray, mesh) : 0;
    if (Number.isFinite(distance) && distance <= far) candidates.push({ mesh, distance, order: candidates.length });
  }
  candidates.sort((a, b) => a.distance - b.distance);
  try {
    for (const { mesh, distance, order } of candidates) {
      if (distance > raycaster.far) break;
      hits.length = 0;
      castRanges(raycaster, mesh, hits);
      for (const hit of hits) {
        if ((!nearest || hit.distance < nearest.distance || (hit.distance === nearest.distance && order < nearestOrder))
            && (!acceptHit || acceptHit(hit))) {
          nearest = hit;
          nearestOrder = order;
        }
      }
      if (nearest) raycaster.far = nearest.distance;
    }
  } finally { raycaster.far = far; }
  return nearest;
}
