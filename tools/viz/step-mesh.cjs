#!/usr/bin/env node
// step-mesh.cjs — read a STEP the way the /3d viewer does when no payload stands beside it.
//
//   node tools/viz/step-mesh.cjs <file.step> <out.mesh> [sha256-of-the-step]
//
// occt-import-js with no parameters is the viewer's own STEP route (web/public/js/viewer/step.js,
// `parseStep`), so a model read here is tessellated as the page would tessellate it. The result
// is written in the payload layout `hardware/scripts/_mesh_payload.py` writes beside an export
// (u32 header length, JSON header, one 4-byte-aligned blob), which is the one layout
// `tools/viz/build.py` reads. It goes to the path named, never beside the STEP: the payload in
// the tree is the export's to write.

const fs = require("fs");
const path = require("path");

const [stepPath, outPath, digest] = process.argv.slice(2);
if (!stepPath || !outPath) {
  console.error("usage: node tools/viz/step-mesh.cjs <file.step> <out.mesh> [sha256]");
  process.exit(2);
}

// The copy the payload selftest reads with; the site loads the same version from a CDN.
const occtModule = require.resolve("occt-import-js", {
  paths: [path.join(__dirname, "..", "..", "hardware", "pcb", "pcba")],
});

// The viewer stamps an unnamed leaf mesh with the name of the node that lists it
// (`backfillMeshNames`), so a multi-solid component answers to its component's name.
function backfillNames(result) {
  if (!result || !result.meshes || !result.root) return;
  const visit = (node) => {
    if (node.name && node.meshes) {
      for (const i of node.meshes) {
        const mesh = result.meshes[i];
        if (mesh && !mesh.name) mesh.name = node.name;
      }
    }
    (node.children || []).forEach(visit);
  };
  visit(result.root);
}

require(occtModule)().then((occt) => {
  const result = occt.ReadStepFile(new Uint8Array(fs.readFileSync(stepPath)), null);
  if (!result.success) {
    console.error(`occt-import-js could not read ${stepPath}`);
    process.exit(1);
  }
  backfillNames(result);
  const entries = [];
  const chunks = [];
  let offset = 0;
  const put = (Typed, values) => {
    const arr = Typed.from(values || []);
    chunks.push(Buffer.from(arr.buffer, arr.byteOffset, arr.byteLength));
    const at = [offset, arr.length];
    offset += arr.byteLength;
    return at;
  };
  for (const m of result.meshes) {
    const fac = [];
    for (const f of m.brep_faces || []) fac.push(f.first, f.last);
    entries.push({
      name: m.name || "",
      color: m.color || null,
      pos: put(Float32Array, m.attributes.position.array),
      nrm: put(Float32Array, m.attributes.normal ? m.attributes.normal.array : []),
      idx: put(Uint32Array, m.index.array),
      fac: put(Uint32Array, fac),
    });
  }
  const header = { v: 3, meshes: entries };
  if (digest) header.src = digest;
  let head = Buffer.from(JSON.stringify(header));
  const pad = (4 - ((head.length + 4) % 4)) % 4;
  head = Buffer.concat([head, Buffer.alloc(pad, 0x20)]);
  const len = Buffer.alloc(4);
  len.writeUInt32LE(head.length, 0);
  fs.writeFileSync(outPath, Buffer.concat([len, head, ...chunks]));
});
