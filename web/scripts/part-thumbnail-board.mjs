// Read the native PCB export's placed triangle arrays into a payload for hsm-render.
import fs from "node:fs";

export function encodeMeshPayload(header, blocks) {
  const json = Buffer.from(JSON.stringify(header));
  const padded = Buffer.alloc(Math.ceil(json.length / 4) * 4, 32);
  json.copy(padded);
  const prefix = Buffer.alloc(4);
  prefix.writeUInt32LE(padded.length);
  return Buffer.concat([prefix, padded, ...blocks]);
}

const identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function compose(a, b) {
  return b.map((_, i) => {
    const row = i % 4;
    const col = i - row;
    return a[row] * b[col] + a[4 + row] * b[col + 1] + a[8 + row] * b[col + 2] + a[12 + row] * b[col + 3];
  });
}

export function writeBoardPayload(glbPath, payload) {
  const glb = fs.readFileSync(glbPath);
  const jsonEnd = 20 + glb.readUInt32LE(12);
  const source = JSON.parse(glb.toString("utf8", 20, jsonEnd));
  const binStart = jsonEnd + 8;
  const meshes = [], blocks = [];
  let offset = 0;
  function append(array) {
    const range = [offset, array.length];
    const bytes = Buffer.from(array.buffer, array.byteOffset, array.byteLength);
    offset += bytes.length;
    blocks.push(bytes);
    return range;
  }

  function vectorArray(index) {
    const accessor = source.accessors[index];
    const view = source.bufferViews[accessor.bufferView];
    if (accessor.type !== "VEC3" || accessor.componentType !== 5126 || view.byteStride) {
      throw new Error("PCB GLB vectors must be tightly packed floats");
    }
    const start = binStart + (view.byteOffset || 0) + (accessor.byteOffset || 0);
    return new Float32Array(glb.buffer, glb.byteOffset + start, accessor.count * 3);
  }

  function project(input, transform, kind) {
    const output = new Float32Array(input.length);
    for (let i = 0; i < input.length; i += 3) {
      const [x, y, z] = input.subarray(i, i + 3);
      for (let row = 0; row < 3; row++) {
        output[i + row] = x * transform[row] + y * transform[4 + row] + z * transform[8 + row];
        if (kind === "position") output[i + row] = (output[i + row] + transform[12 + row]) * 1000;
      }
    }
    return output;
  }

  function visit(nodeIndex, parent) {
    const node = source.nodes[nodeIndex];
    const transform = node.matrix ? compose(parent, node.matrix) : parent;
    for (const primitive of source.meshes[node.mesh]?.primitives || []) {
      if (primitive.mode !== 4 || primitive.indices !== undefined) throw new Error("PCB GLB needs triangle arrays");
      const position = source.accessors[primitive.attributes.POSITION];
      const pos = vectorArray(primitive.attributes.POSITION);
      const nrm = vectorArray(primitive.attributes.NORMAL);
      const color = source.materials[primitive.material]?.pbrMetallicRoughness?.baseColorFactor?.slice(0, 3);
      const entry = { name: node.name, color, pos: append(project(pos, transform, "position")),
        nrm: append(project(nrm, transform, "normal")), idx: append(Uint32Array.from({ length: position.count }, (_, i) => i)),
        fac: [offset, 0] };
      if (node.name === "board") {
        const uvs = new Float32Array(position.count * 2);
        for (let i = 0; i < position.count; i++) for (const axis of [0, 1]) {
          uvs[i * 2 + axis] = (pos[i * 3 + axis] - position.min[axis]) / (position.max[axis] - position.min[axis]);
        }
        entry.uv = append(uvs);
      }
      meshes.push(entry);
    }
    for (const child of node.children || []) visit(child, transform);
  }

  for (const node of source.scenes[source.scene].nodes) visit(node, identity);
  if (!meshes.some(mesh => mesh.name === "board")) throw new Error("PCB GLB has no board slab");
  fs.writeFileSync(payload, encodeMeshPayload({ v: 3, meshes }, blocks));
}
