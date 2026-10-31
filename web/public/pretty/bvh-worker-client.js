import { Box3 } from 'three';
import { MeshBVH } from 'three-mesh-bvh';

// The library worker's transferable-buffer protocol, with a same-origin entry
// that Safari can open without a bundler or a cross-origin Worker constructor.
export function createBVHWorker() {
  const worker = new Worker(new URL('./bvh-worker.js', import.meta.url), { type: 'module' });
  let pending = null;
  worker.onerror = event => {
    pending?.reject(new Error(event.message || 'Assembly preparation failed'));
    pending = null;
  };
  worker.onmessage = ({ data }) => {
    if (!pending) return;
    if (data.error) {
      pending.reject(new Error(data.error.message || String(data.error))); pending = null;
    } else if (data.serialized) {
      const { geometry, resolve, reject } = pending;
      pending = null;
      try {
        geometry.attributes.position.array = data.position;
        if (data.serialized.index) geometry.index.array = data.serialized.index;
        const bvh = MeshBVH.deserialize(data.serialized, geometry, { setIndex: false });
        geometry.boundingBox = bvh.getBoundingBox(new Box3());
        resolve(bvh);
      } catch (error) { reject(error); }
    } else pending.onProgress?.(data.progress);
  };
  return {
    generate(geometry, options = {}) {
      if (pending) return Promise.reject(new Error('Assembly preparation already running'));
      return new Promise((resolve, reject) => {
        pending = { geometry, resolve, reject, onProgress: options.onProgress };
        const position = geometry.attributes.position.array, index = geometry.index.array;
        worker.postMessage({ position, index, options: { ...options, onProgress: null, includedProgressCallback: Boolean(options.onProgress), groups: [...geometry.groups] } }, [position.buffer, index.buffer]);
      });
    },
    dispose() {
      worker.terminate(); pending?.reject(new Error('Assembly preparation stopped')); pending = null;
    },
  };
}
