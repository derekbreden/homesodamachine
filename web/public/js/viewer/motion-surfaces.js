// Dense models draw reduced surfaces during interaction and use the inspection mesh at rest.
import * as THREE from "three";

const DENSE_TRIANGLES = 350_000;
const MIN_TRIANGLES = 1_024;
const PIXEL_ERROR = 1.25;

const records = new WeakMap();
const center = new THREE.Vector3();
let model = null, dense = false, pending = [], current = null, worker = null;
let idleTimer = 0, unavailable = false;

function stopWorker() {
  clearTimeout(idleTimer);
  worker?.terminate();
  worker = null;
  current = null;
}

function next() {
  clearTimeout(idleTimer);
  if (current || unavailable) return;
  const geometry = pending.shift();
  if (!geometry) {
    if (worker) idleTimer = setTimeout(stopWorker, 750);
    return;
  }
  try {
    if (!worker) {
      worker = new Worker(new URL("./motion-surface-worker.js", import.meta.url), { type: "module" });
      worker.onmessage = completed;
      worker.onerror = () => { unavailable = true; pending = []; stopWorker(); };
    }
    current = geometry;
    // Each payload can contain several solids. Transfer just this solid's ranges.
    const positions = geometry.attributes.position.array.slice();
    const indices = geometry.index.array.slice();
    worker.postMessage({ positions, indices }, [positions.buffer, indices.buffer]);
  } catch {
    unavailable = true;
    pending = [];
    stopWorker();
  }
}

function completed({ data }) {
  const geometry = current;
  current = null;
  if (geometry && data?.reduced?.length && data.reduced.length < geometry.index.count) {
    const preview = new THREE.BufferGeometry();
    preview.attributes = { ...geometry.attributes };
    preview.setIndex(new THREE.BufferAttribute(data.reduced, 1));
    preview.boundingBox = geometry.boundingBox;
    preview.boundingSphere = geometry.boundingSphere;
    records.set(geometry, { preview, deviation: data.deviation });
    geometry.addEventListener("dispose", function release() {
      geometry.removeEventListener("dispose", release);
      records.delete(geometry);
      preview.dispose();
    });
  } else if (geometry) {
    records.set(geometry, null);
  }
  next();
}

// Replacements and partial arrivals use the same geometry lifetime as the mounted scene.
export function prepareMotionSurfaces(group) {
  if (group !== model) {
    stopWorker();
    model = group;
  }
  const surfaces = (group?.children || []).filter(mesh => mesh.userData.side === "front" && mesh.geometry?.index);
  dense = surfaces.reduce((count, mesh) => count + mesh.geometry.index.count / 3, 0) >= DENSE_TRIANGLES;
  if (unavailable || !dense) { pending = []; return; }
  const candidates = new Set(surfaces.map(mesh => mesh.geometry));
  if (current && !candidates.has(current)) stopWorker();
  pending = [...candidates].filter(geometry => geometry !== current && !records.has(geometry)
    && geometry.index.count >= MIN_TRIANGLES * 3 && geometry.attributes.position.itemSize === 3)
    .sort((a, b) => b.index.count - a.index.count);
  next();
}

// The original geometry stays on every mesh for selection, surface tracking and measurements.
export function drawMovingSurfaces(scene, camera, height, render) {
  const swapped = [];
  if (dense) {
    camera.updateMatrixWorld();
    const focal = camera.projectionMatrix.elements[5] * height / 2;
    scene.traverseVisible(mesh => {
      const geometry = mesh.geometry;
      const record = geometry && records.get(geometry);
      if (!record) return;
      const scale = mesh.matrixWorld.getMaxScaleOnAxis();
      center.copy(geometry.boundingSphere.center).applyMatrix4(mesh.matrixWorld).applyMatrix4(camera.matrixWorldInverse);
      const depth = Math.max(camera.near, -center.z - geometry.boundingSphere.radius * scale);
      if (record.deviation * scale * focal > PIXEL_ERROR * depth) return;
      swapped.push([mesh, geometry]);
      mesh.geometry = record.preview;
    });
  }
  try { render(); }
  finally { for (const [mesh, geometry] of swapped) mesh.geometry = geometry; }
  return swapped.length > 0;
}
