// Small opaque solids with matching materials share a draw while their presentation matches the batch.
import * as THREE from "three";

const maxTriangles = 8192;
const minMembers = 4;
const maxMembers = 16;
const maxBytes = 24 * 1024 * 1024;

export function isPlainIndexedSurface(geometry) {
  if (geometry.groups.length || geometry.drawRange.start || geometry.drawRange.count < geometry.index.count) return false;
  for (const name in geometry.attributes) if (name !== "position" && name !== "normal") return false;
  for (const name in geometry.morphAttributes) if (geometry.morphAttributes[name].length) return false;
  return true;
}

function memberFor(mesh, previewFor) {
  const original = mesh.geometry;
  if (mesh.userData.side !== "front" || mesh.isInstancedMesh || mesh.isSkinnedMesh ||
      !original?.index || !isPlainIndexedSurface(original) || original.index.count > maxTriangles * 3) return;
  const material = mesh.userData.baseMaterial || mesh.material;
  if (!material?.isMeshStandardMaterial || material.transparent || mesh.renderOrder) return;
  const geometry = previewFor(original) || original;
  const { position, normal } = geometry.attributes;
  if (!position || !normal || !geometry.boundingBox) return;
  if (mesh.matrixAutoUpdate) mesh.updateMatrix();
  return {
    mesh, geometry, material, matrix: mesh.matrix.clone(),
    position, normal, index: geometry.index,
    positionVersion: position.version, normalVersion: normal.version, indexVersion: geometry.index.version,
  };
}

// Only vertices referenced by the presentation's index enter the shared GPU buffer.
function writer(batch) {
  const positions = new Float32Array(batch.vertices * 3), normals = new Float32Array(positions.length);
  const indices = batch.vertices <= 65535 ? new Uint16Array(batch.indices) : new Uint32Array(batch.indices);
  const box = new THREE.Box3(), p = new THREE.Vector3(), n = new THREE.Vector3();
  let vertex = 0, offset = 0;
  function append({ geometry, matrix }) {
    const { position, normal } = geometry.attributes;
    const remap = new Uint32Array(position.count), source = geometry.index;
    const transform = new THREE.Matrix3().getNormalMatrix(matrix);
    const reflected = matrix.determinant() < 0;
    for (let i = 0; i < source.count; i++) {
      const id = source.getX(i);
      if (!remap[id]) {
        p.fromBufferAttribute(position, id).applyMatrix4(matrix).toArray(positions, vertex * 3);
        n.fromBufferAttribute(normal, id).applyNormalMatrix(transform).toArray(normals, vertex * 3);
        remap[id] = ++vertex;
      }
      const corner = i % 3;
      const at = reflected && corner ? i + (corner === 1 ? 1 : -1) : i;
      indices[offset + at] = remap[id] - 1;
    }
    offset += source.count;
    box.union(geometry.boundingBox.clone().applyMatrix4(matrix));
  }
  function finish() {
    const merged = new THREE.BufferGeometry();
    merged.setAttribute("position", new THREE.BufferAttribute(positions.slice(0, vertex * 3), 3));
    merged.setAttribute("normal", new THREE.BufferAttribute(normals.slice(0, vertex * 3), 3));
    merged.setIndex(new THREE.BufferAttribute(indices, 1));
    merged.boundingBox = box;
    merged.boundingSphere = box.getBoundingSphere(new THREE.Sphere());
    return new THREE.Mesh(merged, batch.members[0].material);
  }
  return { append, finish };
}

export function prepareMotionBatches(model, previewFor) {
  const root = new THREE.Group(), batches = [], seen = new WeakSet(), materials = new Map();
  let budget = maxBytes, sealed = false;
  const frustum = new THREE.Frustum(), projection = new THREE.Matrix4(), world = new THREE.Box3();
  const corner = new THREE.Vector3();
  root.matrixAutoUpdate = false;
  root.visible = false;
  let task = 0, building = 0, member = 0, current;
  const hidden = [];
  function prepareSlice() {
    task = 0;
    const until = performance.now() + 2;
    while (building < batches.length && performance.now() < until) {
      const batch = batches[building];
      current ??= writer(batch);
      current.append(batch.members[member++]);
      if (member < batch.members.length) continue;
      batch.proxy = current.finish();
      current = null;
      member = 0;
      building++;
    }
    if (building < batches.length) task = setTimeout(prepareSlice, 0);
  }
  function queue(members) {
    const vertices = members.reduce((sum, row) => sum + row.position.count, 0);
    const indices = members.reduce((sum, row) => sum + row.index.count, 0);
    const bytes = vertices * 24 + indices * 4;
    if (bytes > budget) return;
    budget -= bytes;
    batches.push({ members, vertices, indices });
  }
  function collect(solids, complete) {
    for (const mesh of solids) {
      if (seen.has(mesh)) continue;
      seen.add(mesh);
      const row = memberFor(mesh, previewFor);
      if (!row) continue;
      if (!materials.has(row.material)) materials.set(row.material, []);
      const waiting = materials.get(row.material);
      waiting.push(row);
      if (waiting.length === maxMembers) { queue(waiting); materials.delete(row.material); }
    }
    if (complete) {
      for (const waiting of materials.values()) if (waiting.length >= minMembers) queue(waiting);
      materials.clear();
      sealed = true;
    }
    if (!task && building < batches.length) task = setTimeout(prepareSlice, 0);
  }

  // A close view keeps Three's individual frustum culling for a batch crossing the frame.
  function inFrame(proxy) {
    world.copy(proxy.geometry.boundingBox).applyMatrix4(model.matrixWorld);
    return frustum.planes.every(plane => {
      const { x, y, z } = plane.normal;
      corner.set(x > 0 ? world.min.x : world.max.x, y > 0 ? world.min.y : world.max.y,
        z > 0 ? world.min.z : world.max.z);
      return plane.distanceToPoint(corner) >= 0;
    });
  }
  function present(camera) {
    if (!building || !model.visible || !model.parent) return;
    model.updateWorldMatrix(true, false);
    frustum.setFromProjectionMatrix(projection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
    let active = false;
    for (let i = 0; i < building; i++) {
      const { members, proxy } = batches[i];
      proxy.visible = inFrame(proxy) && members.every(row => {
        const { mesh, geometry, matrix, material, position, normal, index } = row;
        if (mesh.matrixAutoUpdate) mesh.updateMatrix();
        return mesh.visible && mesh.parent === model && !mesh.children.length && mesh.layers.test(camera.layers) &&
          mesh.geometry === geometry && mesh.material === material && !material.transparent && !mesh.renderOrder &&
          mesh.matrix.equals(matrix) && geometry.attributes.position === position && geometry.attributes.normal === normal &&
          geometry.index === index && position.version === row.positionVersion && normal.version === row.normalVersion &&
          index.version === row.indexVersion && isPlainIndexedSurface(geometry);
      });
      if (!proxy.visible) continue;
      if (!proxy.parent) root.add(proxy);
      proxy.layers.mask = camera.layers.mask;
      for (const { mesh } of members) { mesh.visible = false; hidden.push(mesh); }
      active = true;
    }
    if (!active) return;
    if (root.parent !== model.parent) model.parent.add(root);
    root.matrix.copy(model.matrix);
    root.matrixWorldNeedsUpdate = true;
    root.visible = true;
    return true;
  }
  function restore() {
    root.visible = false;
    for (const mesh of hidden) mesh.visible = true;
    hidden.length = 0;
  }
  function dispose() {
    clearTimeout(task);
    root.removeFromParent();
    for (let i = 0; i < building; i++) batches[i].proxy.geometry.dispose();
  }
  return { model, revision: model.userData.sharedHead, collect, get sealed() { return sealed; }, present, restore, dispose };
}
