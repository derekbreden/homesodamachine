// Browser mesh decoding preserves the arrays, face ranges and provenance written by the generator.
import { validFeatures } from "/contracts/features.js";
const MESH_PAYLOAD_VERSIONS = [2, 3, 4];

export function decodeMeshPayload(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const headLen = view.getUint32(0, true);
  const head = JSON.parse(new TextDecoder().decode(bytes.subarray(4, 4 + headLen)));
  if (!MESH_PAYLOAD_VERSIONS.includes(head.v)) return null;
  if (head.v === 4) return { meshes: [], scene: head, src: head.src, cut: head.cut };
  const blob = bytes.buffer.slice(bytes.byteOffset + 4 + headLen, bytes.byteOffset + bytes.byteLength);
  const meshes = head.meshes.map((m) => {
    const fac = new Uint32Array(blob, m.fac[0], m.fac[1]);
    const sources = Array.isArray(m.face_sources) && m.face_sources.length === fac.length / 2
      ? m.face_sources : null;
    const brep_faces = [];
    for (let i = 0; i + 1 < fac.length; i += 2) {
      const face = { first: fac[i], last: fac[i + 1] };
      if (Array.isArray(sources?.[i / 2])) face.sources = sources[i / 2];
      brep_faces.push(face);
    }
    return {
      name: m.name,
      color: m.color || undefined,
      attributes: {
        position: { array: new Float32Array(blob, m.pos[0], m.pos[1]) },
        normal: { array: new Float32Array(blob, m.nrm[0], m.nrm[1]) },
      },
      index: { array: new Uint32Array(blob, m.idx[0], m.idx[1]) },
      brep_faces,
      features: validFeatures(m.features, m.idx[1] / 3),
    };
  });
  // THE HEADER'S PROVENANCE COMES OUT WITH THE TRIANGLES. `src` is the digest of the STEP
  // this surface was cut from and `cut` is what the reduction measured against its budget;
  // the edge picker states both on a pick, because a coordinate off this surface is a
  // coordinate off a surface, and which one it was is half of what it means. Either may be
  // absent — a payload that stated neither is still a payload.
  return { meshes, src: head.src, cut: head.cut };
}

