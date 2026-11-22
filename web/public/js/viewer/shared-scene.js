// Assemblies share immutable part meshes; each completed object can replace its previous surface independently.
import { decodeMeshPayload } from './mesh-payload.js';
import { fetchMember } from './member.js';

const objects = new Map();
// Unchanged instances retain their world arrays for picking across partial reloads.
const instances = new Map();
const CACHE_BYTES = 256 * 1024 * 1024;
const INSTANCE_BYTES = 512 * 1024 * 1024;
let retainedBytes = 0;
let instanceBytes = 0;

function retainInstance(key, meshes) {
  // Reserve room for the world arrays an inspection of a placed mesh may need.
  const bytes = meshes.reduce((sum, mesh) => {
    const { position, normal } = mesh.localAttributes;
    const localBytes = position.array.byteLength + normal.array.byteLength + mesh.localIndex.array.byteLength;
    return sum + localBytes * (mesh.placement ? 2 : 1);
  }, 0);
  instances.set(key,{meshes,bytes});instanceBytes+=bytes;
  for(const [name,value]of instances){
    if(instanceBytes<=INSTANCE_BYTES)break;
    if(name!==key){instances.delete(name);instanceBytes-=value.bytes;}
  }
}

export function sceneHeader(bytes) {
  if (bytes.length < 4) return null;
  const n = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).getUint32(0, true);
  const head = JSON.parse(new TextDecoder().decode(bytes.subarray(4, 4 + n)));
  return head.v === 4 ? head : null;
}

function objectUrl(hash, sourceUrl) {
  if (!/^[a-f0-9]{64}$/.test(hash)) throw new Error('Invalid mesh object');
  return sourceUrl ? new URL(`s-${hash}.gz`, sourceUrl).href : `/scene-meshes/${hash}`;
}

async function object(hash, sourceUrl, priority) {
  if (objects.has(hash)) {
    const held = objects.get(hash); objects.delete(hash); objects.set(hash, held);
    return held.promise;
  }
  const held = { bytes: 0, promise: null };
  held.promise = (async () => {
    let bytes;
    // A detail load can join this same download after a thumbnail is canceled.
    try { bytes = await fetchMember(objectUrl(hash, sourceUrl), { priority }); }
    catch { bytes = await fetchMember(`/scene-meshes/${hash}`, { priority }); }
    const result = decodeMeshPayload(bytes);
    if (!result) throw new Error(`Unsupported mesh object ${hash}`);
    held.bytes = bytes.length; retainedBytes += held.bytes;
    for (const [key, entry] of objects) {
      if (retainedBytes <= CACHE_BYTES) break;
      if (key !== hash && entry.bytes) { objects.delete(key); retainedBytes -= entry.bytes; }
    }
    return result.meshes;
  })().catch(error => { objects.delete(hash); retainedBytes -= held.bytes; throw error; });
  objects.set(hash, held);
  return held.promise;
}

// Surface inspection reads world coordinates; drawing uses the local arrays and the mesh matrix.
function placedArray(source, matrix, normalize = false) {
  let saved;
  return { get array() {
    if (saved) return saved;
    const [[xx, xy, xz, tx], [yx, yy, yz, ty], [zx, zy, zz, tz]] = matrix;
    saved = new Float32Array(source.length);
    for (let i = 0; i < source.length; i += 3) {
      const x = source[i], y = source[i + 1], z = source[i + 2];
      const a = xx * x + xy * y + xz * z + tx;
      const b = yx * x + yy * y + yz * z + ty;
      const c = zx * x + zy * y + zz * z + tz;
      const scale = normalize ? 1 / (Math.hypot(a, b, c) || 1) : 1;
      saved[i] = a * scale;
      saved[i + 1] = b * scale;
      saved[i + 2] = c * scale;
    }
    return saved;
  } };
}

function placed(mesh, node, index) {
  const entry = node.entries[index];
  const out = { ...mesh, name: entry.name, color: entry.color?.slice(0,3) || undefined, opacity: entry.color?.[3],
    geometryKey: `${node.asset}:${index}`, placement: node.transform,
    localAttributes: mesh.attributes, localIndex: mesh.index,
    objectKey: `${node.asset}:${index}:${JSON.stringify(node.transform || null)}:${JSON.stringify(entry.color)}` };
  if (!node.transform) return out;
  const m = node.transform;
  const a = m.map(row => row.slice(0, 3));
  const det = a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
  const co = [
    [a[1][1]*a[2][2]-a[1][2]*a[2][1], a[1][2]*a[2][0]-a[1][0]*a[2][2], a[1][0]*a[2][1]-a[1][1]*a[2][0]],
    [a[0][2]*a[2][1]-a[0][1]*a[2][2], a[0][0]*a[2][2]-a[0][2]*a[2][0], a[0][1]*a[2][0]-a[0][0]*a[2][1]],
    [a[0][1]*a[1][2]-a[0][2]*a[1][1], a[0][2]*a[1][0]-a[0][0]*a[1][2], a[0][0]*a[1][1]-a[0][1]*a[1][0]],
  ];
  const normalMatrix = co.map(row => [...row.map(value => value / det), 0]);
  out.attributes = {
    position: placedArray(mesh.attributes.position.array, m),
    normal: placedArray(mesh.attributes.normal.array, normalMatrix, true),
  };
  if (det < 0) {
    let indices;
    out.index = { get array() {
      if (indices) return indices;
      indices = mesh.index.array.slice();
      for (let i = 0; i < indices.length; i += 3) {
        const second = indices[i + 1];
        indices[i + 1] = indices[i + 2];
        indices[i + 2] = second;
      }
      return indices;
    } };
  }
  return out;
}

export async function resolveScene(bytes, { sourceUrl, signal, onPart, preparePart, select, onTarget, priority } = {}) {
  signal?.throwIfAborted();
  const head = sceneHeader(bytes);
  if (!head) return decodeMeshPayload(bytes);
  const { first = [], only = false } = select?.(head) || {};
  const selected = new Set(first);
  const context = only ? [] : head.meshes.map((_, index) => index).filter(index => !selected.has(index));
  const results = new Array(head.meshes.length), errors = [];
  const concurrency = priority === "low" ? 4 : 16;
  let mountTime = 0, nextPaint = null;
  function mount(node, meshes) {
    if (!onPart) return;
    const start = performance.now();
    onPart(node, meshes, head);
    mountTime += performance.now() - start;
    if (mountTime < 4 || nextPaint) return;
    // A warm cache can supply the entire assembly in microtasks before Safari paints.
    nextPaint = new Promise(resolve => {
      if (globalThis.document?.visibilityState === "visible") requestAnimationFrame(resolve);
      else setTimeout(resolve, 0);
    }).then(() => { mountTime = 0; nextPaint = null; });
  }
  async function readNodes(indices) {
    let next = 0;
    const worker = async () => {
      while (next < indices.length) {
        if (nextPaint) await nextPaint;
        // Other readers sharing the frame may already have claimed the last part.
        if (next >= indices.length) return;
        const index = indices[next++], node = head.meshes[index];
        try {
          signal?.throwIfAborted();
          const key=JSON.stringify([node.asset,node.transform||null,node.entries]);
          const held=instances.get(key);
          if(held){
            instances.delete(key);instances.set(key,held);results[index]=held.meshes;
          }else{
            const meshes = await object(node.asset, sourceUrl, priority);
            signal?.throwIfAborted();
            results[index]=meshes.map((mesh,i)=>placed(mesh,node,i));retainInstance(key,results[index]);
          }
          if (preparePart) await preparePart(results[index], signal);
          if (nextPaint) await nextPaint;
          signal?.throwIfAborted();
          mount(node, results[index]);
        } catch (error) {
          if (error.name === 'AbortError') throw error;
          errors.push({ name: node.name, message: error.message });
        }
      }
    };
    await Promise.all(Array.from({length:Math.min(concurrency,indices.length)},worker));
  }
  if (first.length) {
    await readNodes(first);
    if (context.length && first.every(index => results[index])) await onTarget?.();
  }
  await readNodes(context);
  return { meshes: results.flatMap(value=>value || []), src: head.src, cut: head.cut,
    scene: head, errors };
}
