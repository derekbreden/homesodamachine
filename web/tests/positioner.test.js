import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { gunzipSync } from "node:zlib";

const cad = new URL("../../hardware/printed-parts/fixtures/pgfun-positioner/", import.meta.url);
const read = (file) => JSON.parse(fs.readFileSync(new URL(file, cad), "utf8"));
const scene = JSON.parse(gunzipSync(fs.readFileSync(new URL("../public/assemblies/pgfun-positioner.json.gz", import.meta.url))));

function decode(value, Type) {
  return new Type(Uint8Array.from(Buffer.from(value, "base64")).buffer);
}

test("the moving website assembly is bound to current CAD and motion limits", () => {
  const binding = read("motion-geometry.json");
  assert.equal(scene.geometrySha256, binding.sha256, "Regenerate with tools/positioner-view.py after rebuilding CAD");
  assert.equal(scene.revision, binding.motion.revision);
  assert.deepEqual(scene.pivot, [...binding.motion.yaw_xy, binding.motion.pivot_z]);
  assert.equal(scene.softLimitDeg, binding.motion.soft_limit_deg);
  assert.equal(scene.meshFormat, "creased-f32-v1");
});

test("the scene carries every installed print and places gun and rotator on their own motion groups", () => {
  const manifest = read("print-manifest.json");
  const names = new Set(scene.parts.map((part) => part.name));
  assert.equal(names.size, scene.parts.length, "duplicate mesh names");
  for (const part of manifest.parts) {
    if (/^(?:housing-fit-|journal-fit-|camera-lens-shim)/.test(part.name)) continue;
    assert.ok(names.has(part.name), `missing installed print ${part.name}`);
  }
  const gun = scene.parts.filter((part) => part.name.startsWith("gun:"));
  const rotator = scene.parts.filter((part) => part.name.startsWith("rotator:"));
  assert.ok(gun.length && rotator.length);
  assert.ok(gun.every((part) => part.group === "pitch"));
  assert.ok(rotator.every((part) => part.group === "fixed"));
  assert.equal(scene.parts.find((part) => part.name === "pitch-motor").group, "yaw");
  assert.equal(scene.parts.find((part) => part.name === "yaw-motor").group, "fixed");
  for (const part of scene.parts) {
    const vertices = decode(part.v, Float32Array);
    const faces = decode(part.f, part.indexType === "uint32" ? Uint32Array : Uint16Array);
    const normals = decode(part.n, Int16Array);
    assert.equal(vertices.length % 3, 0, part.name);
    assert.equal(faces.length % 3, 0, part.name);
    assert.ok(vertices.length && faces.length, part.name);
    assert.equal(faces.length / 3, part.sourceFaceCount, `${part.name}: triangles lost from source`);
    assert.equal(normals.length, vertices.length, part.name);
    for (const index of faces) assert.ok(index < vertices.length / 3, part.name);
  }
});

test("the displayed printed solids remain closed, correctly oriented and match the CAD volumes", () => {
  const manifest = new Map(read("print-manifest.json").parts.map((part) => [part.name, part]));
  for (const part of scene.parts.filter((p) => p.category === "print" || p.category === "liner")) {
    const vertices = decode(part.v, Float32Array);
    const faces = decode(part.f, part.indexType === "uint32" ? Uint32Array : Uint16Array);
    // Creased normals duplicate a vertex at hard edges. Weld by its actual
    // position to check the surface that the browser draws.
    const ids = new Map();
    const welded = new Uint32Array(vertices.length / 3);
    for (let i = 0; i < welded.length; i++) {
      const point = Array.from(vertices.subarray(i * 3, i * 3 + 3)).join(",");
      if (!ids.has(point)) ids.set(point, ids.size);
      welded[i] = ids.get(point);
    }
    const edges = new Map();
    let volume = 0;
    for (let i = 0; i < faces.length; i += 3) {
      const [a, b, c] = faces.subarray(i, i + 3);
      for (const [from, to] of [[a, b], [b, c], [c, a]]) {
        const x = welded[from], y = welded[to];
        assert.notEqual(x, y, `${part.name}: collapsed triangle edge`);
        const key = `${Math.min(x, y)},${Math.max(x, y)}`;
        const edge = edges.get(key) || { count: 0, winding: 0 };
        edge.count++;
        edge.winding += x < y ? 1 : -1;
        edges.set(key, edge);
      }
      const ax = vertices[a * 3], ay = vertices[a * 3 + 1], az = vertices[a * 3 + 2];
      const bx = vertices[b * 3], by = vertices[b * 3 + 1], bz = vertices[b * 3 + 2];
      const cx = vertices[c * 3], cy = vertices[c * 3 + 1], cz = vertices[c * 3 + 2];
      volume += (ax * (by * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - by * cx)) / 6;
    }
    for (const edge of edges.values()) {
      assert.equal(edge.count, 2, `${part.name}: open or non-manifold surface`);
      assert.equal(edge.winding, 0, `${part.name}: inverted triangle`);
    }
    assert.ok(volume > 0, `${part.name}: inverted solid`);
    assert.ok(Math.abs(volume / part.sourceVolumeMm3 - 1) < 0.00001, `${part.name}: changed source volume`);
    const cadVolume = manifest.get(part.name).volume_cm3 * 1000;
    // The manifest rounds cm³ to three decimals (±0.5 mm³); add that
    // quantization budget to the CAD tessellation's volume tolerance.
    assert.ok(Math.abs(volume - cadVolume) < cadVolume * 0.005 + 0.5, `${part.name}: does not match CAD volume`);
  }
});
