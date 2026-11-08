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
  const bytes = meshes.reduce((sum,mesh)=>sum+
    mesh.attributes.position.array.byteLength+mesh.attributes.normal.array.byteLength+mesh.index.array.byteLength+
    (mesh.attributes===mesh.localAttributes?0:mesh.localAttributes.position.array.byteLength+mesh.localAttributes.normal.array.byteLength)+
    (mesh.index===mesh.localIndex?0:mesh.localIndex.array.byteLength),0);
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

async function object(hash, sourceUrl) {
  if (objects.has(hash)) {
    const held = objects.get(hash); objects.delete(hash); objects.set(hash, held);
    return held.promise;
  }
  const held = { bytes: 0, promise: null };
  held.promise = (async () => {
    let bytes;
    try { bytes = await fetchMember(objectUrl(hash, sourceUrl)); }
    catch { bytes = await fetchMember(`/scene-meshes/${hash}`); }
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
  const transform = (array, normal) => {
    const result = new Float32Array(array.length);
    for (let i=0; i<array.length; i+=3) {
      const p = array.subarray(i,i+3);
      const q = normal ? co.map(row => row.reduce((v,c,k)=>v+c*p[k]/det,0))
        : m.map(row => row[3]+row.slice(0,3).reduce((v,c,k)=>v+c*p[k],0));
      const length = normal ? Math.hypot(...q) || 1 : 1;
      result.set(q.map(v=>v/length),i);
    }
    return result;
  };
  out.attributes = { position: { array: transform(mesh.attributes.position.array, false) },
    normal: { array: transform(mesh.attributes.normal.array, true) } };
  if (det < 0) {
    const indices = new Uint32Array(mesh.index.array);
    for (let i=0; i<indices.length; i+=3) [indices[i+1],indices[i+2]]=[indices[i+2],indices[i+1]];
    out.index = { array: indices };
  }
  return out;
}

export async function resolveScene(bytes, { sourceUrl, signal, onPart } = {}) {
  const head = sceneHeader(bytes);
  if (!head) return decodeMeshPayload(bytes);
  let next = 0;
  const results = new Array(head.meshes.length), errors = [];
  const worker = async () => {
    while (next < head.meshes.length) {
      const index = next++, node = head.meshes[index];
      try {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        const key=JSON.stringify([node.asset,node.transform||null,node.entries]);
        const held=instances.get(key);
        if(held){
          instances.delete(key);instances.set(key,held);results[index]=held.meshes;
        }else{
          const meshes = await object(node.asset, sourceUrl);
          if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
          results[index]=meshes.map((mesh,i)=>placed(mesh,node,i));retainInstance(key,results[index]);
        }
        onPart?.(node,results[index],head);
      } catch (error) {
        if (error.name === 'AbortError') throw error;
        errors.push({ name: node.name, message: error.message });
      }
    }
  };
  await Promise.all(Array.from({length:Math.min(16,head.meshes.length)},worker));
  return { meshes: results.flatMap(value=>value || []), src: head.src, cut: head.cut,
    scene: head, errors };
}
