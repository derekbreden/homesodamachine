import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { gunzipSync } from "node:zlib";

const cad = new URL("../../hardware/printed-parts/fixtures/pgfun-positioner/", import.meta.url);
const read = (file) => JSON.parse(fs.readFileSync(new URL(file, cad), "utf8"));
const scene = JSON.parse(gunzipSync(fs.readFileSync(new URL("../public/assemblies/pgfun-positioner.json.gz", import.meta.url))));

test("the moving website assembly is bound to current CAD and motion limits", () => {
  const binding = read("motion-geometry.json");
  assert.equal(scene.geometrySha256, binding.sha256, "Regenerate with tools/positioner-view.py after rebuilding CAD");
  assert.equal(scene.revision, binding.motion.revision);
  assert.deepEqual(scene.pivot, [...binding.motion.yaw_xy, binding.motion.pivot_z]);
  assert.equal(scene.softLimitDeg, binding.motion.soft_limit_deg);
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
    const vertices = Buffer.from(part.v, "base64");
    const faces = Buffer.from(part.f, "base64");
    assert.equal(vertices.length % 6, 0, part.name);
    assert.equal(faces.length % 6, 0, part.name);
    assert.ok(vertices.length && faces.length, part.name);
    for (let i = 0; i < faces.length; i += 2) assert.ok(faces.readUInt16LE(i) < vertices.length / 6, part.name);
  }
});
