// The browser decodes the flat part and referenced scene formats that native writers stamp.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), "utf8");
const browserSource = read("web/public/js/viewer/mesh-payload.js");
const features = new URL("../contracts/features.js", import.meta.url).href;
const { decodeMeshPayload } = await import(`data:text/javascript,${encodeURIComponent(
  browserSource.replace('"/contracts/features.js"', JSON.stringify(features)),
)}`);

function version(file, name) {
  const match = new RegExp(`^pub const ${name}: u32 = (\\d+);`, "m").exec(read(file));
  assert.ok(match, `${file} declares its writer format`);
  return Number(match[1]);
}
const meshVersion = version("tools/hsm/kernel/src/write.rs", "MESH_PAYLOAD_VERSION");
const sceneVersion = version("hardware/assembly/scenes/model_export/payload.rs", "SCENE_PAYLOAD_VERSION");

function packet(header, blob = new Uint8Array()) {
  const text = new TextEncoder().encode(JSON.stringify(header));
  const size = Math.ceil(text.length / 4) * 4;
  const bytes = new Uint8Array(4 + size + blob.length);
  new DataView(bytes.buffer).setUint32(0, size, true);
  bytes.fill(32, 4, 4 + size);
  bytes.set(text, 4);
  bytes.set(blob, 4 + size);
  return bytes;
}

test("the page decodes the native flat writer's arrays and face provenance", () => {
  const blob = new Uint8Array(92);
  new Float32Array(blob.buffer, 0, 9).set([0, 0, 0, 1, 0, 0, 0, 1, 0]);
  new Float32Array(blob.buffer, 36, 9).set([0, 0, 1, 0, 0, 1, 0, 0, 1]);
  new Uint32Array(blob.buffer, 72, 3).set([0, 1, 2]);
  new Uint32Array(blob.buffer, 84, 2).set([0, 0]);
  const sources = [{ file: "fixture.rs", line: 1 }];
  const mesh = { name: "fixture", pos: [0, 9], nrm: [36, 9], idx: [72, 3], fac: [84, 2], face_sources: [sources] };
  const decoded = decodeMeshPayload(packet({ v: meshVersion, meshes: [mesh], src: "source-digest" }, blob));
  assert.equal(decoded.src, "source-digest");
  assert.equal(decoded.meshes[0].name, mesh.name);
  assert.deepEqual([...decoded.meshes[0].attributes.position.array], [0, 0, 0, 1, 0, 0, 0, 1, 0]);
  assert.deepEqual([...decoded.meshes[0].index.array], [0, 1, 2]);
  assert.deepEqual(decoded.meshes[0].brep_faces, [{ first: 0, last: 0, sources }]);
});

test("the page retains native scene references for the scene reader", () => {
  const scene = { v: sceneVersion, meshes: [{ name: "fixture", source: "fixture.step.mesh", source_sha256: "source-digest" }] };
  const decoded = decodeMeshPayload(packet(scene));
  assert.deepEqual(decoded.scene, scene);
  assert.deepEqual(decoded.meshes, []);
});
