import { test } from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";
import { mountTubeRoutes, readTubeRoutes, TUBE_ASSEMBLY, tubeDataErrors } from "../lib/tube-routes.js";

const hash = (value) => crypto.createHash("sha256").update(value).digest("hex");
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "tube-data-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const hardwareDir = path.join(root, "hardware");
  const model = path.join(hardwareDir, TUBE_ASSEMBLY);
  const file = path.join(root, "web/public/tube-routes.json");
  const input = path.join(root, "hardware/scripts/tube_routes.py");
  for (const target of [model, file, input]) fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(model, "assembly STEP");
  fs.writeFileSync(input, "route source");
  const source = hash(fs.readFileSync(model));
  const header = Buffer.from(JSON.stringify({ src: source, version: 3 }));
  const prefix = Buffer.alloc(4); prefix.writeUInt32LE(header.length);
  const payload = Buffer.concat([prefix, header, Buffer.from("surfaces")]);
  fs.writeFileSync(model + ".mesh", payload);
  const inputs = {};
  for (const relative of ["hardware/scripts/tube_routes.py", "hardware/scripts/_routing.py",
    "hardware/manifold-layout/enclosure_assembly.py", "hardware/printed-parts/cold-core/_cold_core_interface.py"]) {
    const target = path.join(root, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, "route source");
    inputs[relative] = hash("route source");
  }
  const data = {
    version: 1,
    source: { assembly_step: "hardware/" + TUBE_ASSEMBLY, step_sha256: source,
      payload_src: source, payload_sha256: hash(payload), inputs },
    runs: [{ id: "fluid-18", material: "lldpe-1/4", points: [[0, 0, 0], [10, 0, 0]],
      s: [0, 10], radius_mm: 3.175, holds: [] }],
  };
  const write = () => fs.writeFileSync(file, JSON.stringify(data));
  write();
  return { root, hardwareDir, model, input, file, data, write };
}

test("current tube routes require matching STEP, displayed surface and source inputs", (t) => {
  const f = fixture(t);
  assert.deepEqual(tubeDataErrors(f.data), []);
  const result = readTubeRoutes(f.hardwareDir);
  assert.equal(result.code, 200);
  assert.equal(result.body.status, "current");
  assert.deepEqual(result.body.staleReasons, []);
  assert.equal(result.body.runs[0].id, "fluid-18");
});

test("a viewer surface graft is stale even when its embedded STEP source is unchanged", (t) => {
  const f = fixture(t);
  assert.equal(readTubeRoutes(f.hardwareDir).body.status, "current");
  fs.appendFileSync(f.model + ".mesh", "another surface");
  const result = readTubeRoutes(f.hardwareDir);
  assert.equal(result.body.status, "stale");
  assert.deepEqual(result.body.staleReasons, ["The displayed assembly surface has changed since the tube audit was generated."]);
});

test("changed routing inputs invalidate a cached audit before rebuilding CAD", (t) => {
  const f = fixture(t);
  readTubeRoutes(f.hardwareDir);
  fs.writeFileSync(f.input, "changed route source");
  const result = readTubeRoutes(f.hardwareDir);
  assert.equal(result.body.status, "stale");
  assert.ok(result.body.staleReasons.includes("Routing input changed: hardware/scripts/tube_routes.py"));
});

test("missing or truncated CAD refuses a current result", (t) => {
  const f = fixture(t);
  fs.unlinkSync(f.model);
  fs.writeFileSync(f.model + ".mesh", Buffer.from([1, 2]));
  const result = readTubeRoutes(f.hardwareDir);
  assert.equal(result.body.status, "stale");
  assert.equal(result.body.staleReasons.length, 3);
});

test("missing, unreadable and malformed route data give useful errors instead of throwing", (t) => {
  const f = fixture(t);
  fs.unlinkSync(f.file);
  assert.equal(readTubeRoutes(f.hardwareDir).code, 404);
  fs.writeFileSync(f.file, "{");
  assert.equal(readTubeRoutes(f.hardwareDir).code, 503);
  for (const mutate of [
    (data) => { data.runs = [null]; },
    (data) => { data.runs[0].holds = {}; },
    (data) => { data.runs[0].holds = [null]; },
    (data) => { data.runs[0].s = [0, 0]; },
    (data) => { data.runs[0].points = [[0, 0, null], [10, 0, 0]]; },
    (data) => { data.source.inputs = ["bad source"]; },
    (data) => { delete data.source.payload_sha256; },
  ]) {
    const data = structuredClone(f.data); mutate(data);
    fs.writeFileSync(f.file, JSON.stringify(data));
    assert.equal(readTubeRoutes(f.hardwareDir).code, 503);
  }
});

test("source input paths outside the repository never count as current", (t) => {
  const f = fixture(t);
  f.data.source.inputs["../outside.py"] = hash("route source"); f.write();
  assert.equal(readTubeRoutes(f.hardwareDir).body.status, "stale");
});

test("tube API serves only the audited assembly without caching freshness", async (t) => {
  const f = fixture(t), app = express();
  mountTubeRoutes(app, { hardwareDir: f.hardwareDir });
  const server = app.listen(0, "127.0.0.1");
  await new Promise((resolve) => server.once("listening", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const base = `http://127.0.0.1:${server.address().port}`;
  const response = await fetch(base + "/api/tube-routes/" + TUBE_ASSEMBLY);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("cache-control"), "no-store");
  assert.equal((await response.json()).status, "current");
  assert.equal((await fetch(base + "/api/tube-routes/cold-core/foam-cap/lid.step")).status, 404);
});
