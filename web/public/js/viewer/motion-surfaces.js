// Dense models draw reduced surfaces during interaction and use the inspection mesh at rest.
import * as THREE from "three";

const DENSE_TRIANGLES = 350_000;
const MIN_TRIANGLES = 1_024;
const PIXEL_ERROR = 1.25;

// Local payload arrays survive live placement changes and repeated opens.
const reductions = new WeakMap();
const records = new WeakMap();
const waitingSurfaces = new WeakSet();
const center = new THREE.Vector3();
const pending = [];
let model = null, mountedWork = null, dense = false, current = null, worker = null;
let idleTimer = 0, unavailable = false;

function closeWorker() {
  worker?.terminate();
  worker = null;
}

function finish(job, data) {
  if (data?.reduced?.length && data.reduced.length < job.indices.length) {
    job.reduced = data.reduced;
    job.deviation = data.deviation;
  }
  job.resolve();
  job.resolve = job.waiting = job.signals = null;
}

function workerFailed() {
  unavailable = true;
  closeWorker();
  if (current) finish(current);
  current = null;
  for (const job of pending.splice(0)) finish(job);
}

function next() {
  clearTimeout(idleTimer);
  if (current || unavailable) return;
  let job;
  while ((job = pending.shift())) {
    if (![...job.signals].every(signal => signal?.aborted)) break;
    reductions.delete(job.indices);
    finish(job);
  }
  if (!job) {
    if (worker) idleTimer = setTimeout(closeWorker, 750);
    return;
  }
  current = job;
  try {
    if (!worker) {
      worker = new Worker(new URL("./motion-surface-worker.js", import.meta.url), { type: "module" });
      worker.onerror = workerFailed;
      worker.onmessageerror = workerFailed;
      worker.onmessage = ({ data }) => {
        finish(current, data);
        current = null;
        next();
      };
    }
    // Each payload can contain several solids. Transfer just this solid's ranges.
    const positions = job.positions.slice();
    const indices = job.indices.slice();
    worker.postMessage({ positions, indices }, [positions.buffer, indices.buffer]);
  } catch { workerFailed(); }
}

function prepareIndex(positions, indices, signal) {
  if (unavailable || signal?.aborted || indices?.length < MIN_TRIANGLES * 3
      || !(indices instanceof Uint32Array) || !(positions instanceof Float32Array)) return;
  let job = reductions.get(indices);
  if (job?.positions === positions) {
    job.signals?.add(signal);
    return job.waiting;
  }
  job = { positions, indices, signals: new Set([signal]) };
  job.waiting = new Promise(resolve => { job.resolve = resolve; });
  reductions.set(indices, job);
  pending.push(job);
  next();
  return job.waiting;
}

// A referenced scene declares its byte sizes before individual mesh arrays arrive.
export function denseSceneNodes(nodes) {
  return nodes.reduce((sum, node) => sum + (node.bytes || 0), 0) > DENSE_TRIANGLES * 24;
}

export const hasDenseSurfaces = () => dense;

// Incoming parts have a usable motion surface when they first appear in a dense assembly.
export async function prepareMotionIndices(meshes, signal, needsMotion) {
  if (needsMotion === undefined) {
    needsMotion = meshes.reduce((n, mesh) => n + ((mesh.localIndex || mesh.index)?.array.length || 0) / 3, 0) >= DENSE_TRIANGLES;
  }
  if (!needsMotion) return;
  await Promise.all(meshes.map(mesh => prepareIndex((mesh.localAttributes || mesh.attributes)?.position.array,
    (mesh.localIndex || mesh.index)?.array, signal)));
  signal?.throwIfAborted();
}

function attachSurface(geometry) {
  if (records.has(geometry)) return;
  const job = reductions.get(geometry.index.array);
  if (!job?.reduced || job.positions !== geometry.attributes.position.array) return;
  const preview = new THREE.BufferGeometry();
  preview.attributes = { ...geometry.attributes };
  preview.setIndex(new THREE.BufferAttribute(job.reduced, 1));
  preview.boundingBox = geometry.boundingBox;
  preview.boundingSphere = geometry.boundingSphere;
  records.set(geometry, { preview, deviation: job.deviation });
  geometry.addEventListener("dispose", function release() {
    geometry.removeEventListener("dispose", release);
    records.delete(geometry);
    preview.dispose();
  });
}

// Earlier scene manifests can cross the drawing threshold as their parts arrive.
export function prepareMotionSurfaces(group) {
  if (group !== model) {
    mountedWork?.abort();
    mountedWork = group ? new AbortController() : null;
    model = group;
  }
  const surfaces = (group?.children || []).filter(mesh => mesh.userData.side === "front" && mesh.geometry?.index);
  dense = surfaces.reduce((count, mesh) => count + mesh.geometry.index.count / 3, 0) >= DENSE_TRIANGLES;
  if (unavailable || !dense) return;
  for (const mesh of surfaces) {
    const geometry = mesh.geometry;
    if (records.has(geometry) || waitingSurfaces.has(geometry) || geometry.index.count < MIN_TRIANGLES * 3) continue;
    const signal = mountedWork.signal;
    const task = prepareIndex(geometry.attributes.position.array, geometry.index.array, signal);
    if (task) {
      waitingSurfaces.add(geometry);
      task.then(() => {
        waitingSurfaces.delete(geometry);
        if (!signal.aborted && mesh.parent === group) attachSurface(geometry);
      });
    } else attachSurface(geometry);
  }
}

// The original geometry stays on every mesh for selection, surface tracking and measurements.
export function drawMovingSurfaces(scene, camera, height, render) {
  const swapped = [];
  if (dense) {
    camera.updateMatrixWorld();
    const focal = camera.projectionMatrix.elements[5] * height / 2;
    scene.traverseVisible(mesh => {
      if (mesh.userData.side !== "front" || !mesh.layers.test(camera.layers)) return;
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
