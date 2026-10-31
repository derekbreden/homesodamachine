// Read the same published, colored tessellation as /3d. No second assembly
// file or CAD rebuild is needed for the studio view.
const member = 'manifold-layout/enclosure-assembly.step.mesh';

async function readBytes(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Assembly answered ${response.status}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) return bytes;
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

function visibilityFor(name) {
  if (name === 'display-cover') return 'front-top';
  if (/^enclosure-(front|back)-(top|bottom)$/.test(name)) return name.slice('enclosure-'.length);
  if (name.startsWith('cold-core/foam-')) return 'core';
  return null;
}

export async function loadEnclosure() {
  const finishesPromise = fetch('/finishes.json').then(r => r.ok ? r.json() : {}).then(d => d.finishes || []).catch(() => []);
  let bytes;
  try {
    const response = await fetch('/api/objects', { cache: 'no-store' });
    const { objects } = await response.json();
    if (!objects?.[member]) throw new Error('No published member URL');
    bytes = await readBytes(objects[member]);
  } catch {
    bytes = await readBytes(`/meshes/${member}`);
  }
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const headerSize = view.getUint32(0, true);
  const head = JSON.parse(new TextDecoder().decode(bytes.subarray(4, 4 + headerSize)));
  if (![2, 3].includes(head.v)) throw new Error('Unsupported assembly tessellation');
  const blob = bytes.buffer.slice(bytes.byteOffset + 4 + headerSize, bytes.byteOffset + bytes.byteLength);
  const finishes = await finishesPromise;
  const minimum = [Infinity, Infinity, Infinity], maximum = [-Infinity, -Infinity, -Infinity];
  const parts = head.meshes.map(mesh => {
    const positions = new Float32Array(blob, ...mesh.pos);
    for (let i = 0; i < positions.length; i += 3) for (let axis = 0; axis < 3; axis++) {
      minimum[axis] = Math.min(minimum[axis], positions[i + axis]);
      maximum[axis] = Math.max(maximum[axis], positions[i + axis]);
    }
    const color = mesh.color || [.25, .3, .35];
    // The material table uses the same linear RGB and matching radius as step.js.
    const finish = finishes.find(f => f.rgb.reduce((sum, value, i) => sum + (value - color[i]) ** 2, 0) <= 4e-4 ** 2);
    return {
      name: mesh.name, color,
      finish: finish ? { roughness: finish.roughness, metalness: finish.metalness } : { roughness: .6, metalness: .1 },
      visibility: visibilityFor(mesh.name), positions,
      normals: new Float32Array(blob, ...mesh.nrm),
      indices: new Uint32Array(blob, ...mesh.idx),
    };
  });
  return { name: 'Full enclosure', assembly: true, homeDirection: [-4.9, 5.7, -9.5], sourceSha256: head.src, scale: 4 / Math.max(...maximum.map((value, i) => value - minimum[i])), parts };
}
