// Share a solid's feature outline across selections and prepare detailed edges away from input handling.
import * as THREE from 'three';

const outlines = new WeakMap();
const pending = new Set();
let worker, active = null, wake = 0;

function schedule() {
  if (!wake && !active && pending.size) wake = setTimeout(pump, 0);
}
function pump() {
  wake = 0;
  if (active || !pending.size) return;
  const job = [...pending].find(item => item.priority) || pending.values().next().value;
  pending.delete(job);
  active = job;
  try {
    if (!worker) {
      const current = new Worker(new URL('./feature-edge-worker.js', import.meta.url), { type: 'module' });
      worker = current;
      current.onmessage = ({data}) => {
        if (worker !== current) return;
        const geometry = new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(data, 3));
        finish(geometry);
      };
      current.onerror = () => {
        if (worker !== current) return;
        current.terminate();
        worker = null;
        finish(null);
      };
    }
    const position = job.source.getAttribute('position');
    // CAD geometry uses tightly packed floats. Other Three.js attribute layouts use their accessors.
    let positions;
    if (position.array instanceof Float32Array && !position.isInterleavedBufferAttribute && position.itemSize === 3 && !position.normalized) positions = position.array.slice();
    else {
      positions = new Float32Array(position.count * 3);
      const point = new THREE.Vector3();
      for (let i = 0; i < position.count; i++) point.fromBufferAttribute(position, i).toArray(positions, i*3);
    }
    const indices = job.source.index?.array.slice();
    worker.postMessage({positions, indices}, indices ? [positions.buffer, indices.buffer] : [positions.buffer]);
  } catch { finish(null); }
}
function finish(edges) {
  const job = active;
  active = null;
  if (edges && outlines.get(job.source) === job) {
    job.edges = edges;
    for (const deliver of job.listeners) deliver(edges);
  } else edges?.dispose();
  job.listeners.clear();
  schedule();
}
function discard(job) {
  pending.delete(job);
  job.listeners.clear();
  if (active === job) { worker?.terminate(); worker = null; active = null; schedule(); }
  job.edges?.dispose();
  outlines.delete(job.source);
  job.source.removeEventListener('dispose', job.dispose);
}

// The caller borrows the returned outline for the source geometry's lifetime.
export function requestFeatureEdges(source, onReady, {priority = false} = {}) {
  const position = source.getAttribute('position');
  if (!position) return () => {};
  let job = outlines.get(source);
  if (job && (job.positionVersion !== position.version || job.indexVersion !== source.index?.version)) { discard(job); job = null; }
  if (!job) {
    job = {source, listeners:new Set(), priority, edges:null, positionVersion:position.version, indexVersion:source.index?.version};
    job.dispose = () => discard(job);
    outlines.set(source, job); source.addEventListener('dispose', job.dispose);
  }
  if (!job.edges && priority && (source.index?.count ?? position.count) <= 384 && !active && !pending.has(job)) job.edges = new THREE.EdgesGeometry(source, 30);
  if (job.edges) { onReady(job.edges); return () => {}; }
  job.priority ||= priority;
  job.listeners.add(onReady);
  if (active !== job) pending.add(job);
  schedule();
  return () => {
    job.listeners.delete(onReady);
    if (!job.listeners.size && !job.edges && outlines.get(source) === job) discard(job);
  };
}

// Overlay geometry stays in the solid's local coordinates so a highlight can share its buffers.
export function markSolid(group, mesh, {lineMaterial, fillMaterial, priority = true, onChange}) {
  mesh.updateWorldMatrix(true, false);
  const holder = new THREE.Group();
  holder.matrix.copy(mesh.matrixWorld);
  holder.matrixAutoUpdate = false;
  if (fillMaterial) {
    const fill = new THREE.Mesh(mesh.geometry, fillMaterial);
    fill.renderOrder = group.renderOrder;
    holder.add(fill);
  }
  group.add(holder);
  const cancel = requestFeatureEdges(mesh.geometry, edges => {
    const line = new THREE.LineSegments(edges, lineMaterial);
    line.renderOrder = group.renderOrder + 1;
    holder.add(line);
    onChange?.();
  }, {priority});
  holder.addEventListener('removed', cancel);
}
