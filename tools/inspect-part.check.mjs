// These on-demand checks keep repeated inspection questions attached to their selected geometry.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { inspectionOptions } from "./inspect-part.mjs";

function fixture(t, asRecord) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-inspection-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const selection = { query: "owner::receiver", model: "hardware/owner.step", bodies: ["owner"],
    feature: "owner::receiver", against: ["fitted-part"], overlaps: ["mating-part"], rays: ["0,0,0:0,0,1"] };
  const camera = { cam: [1,1,1], target: [0,0,0], up: [0,0,1], ortho: true,
    clip: [{axis:"x",lo:-1,hi:1}], section: {at:[0,0,0],normal:[0,1,0]} };
  const file = path.join(root, "saved.json");
  fs.writeFileSync(file, JSON.stringify(asRecord ? { received_query: selection.query, selection, render_job: camera }
    : { ...camera, inspection: selection }));
  return { root, file, selection, camera };
}

test("a saved inspection or render job carries the body, feature, neighbours, rays and camera", t => {
  for (const asRecord of [true, false]) {
    const f = fixture(t, asRecord);
    const result = inspectionOptions(undefined, { reuse: f.file, output: "after" }, f.root);
    assert.equal(result.query, f.selection.query);
    assert.deepEqual(result.options, { ...f.selection, reuse: f.file, output: "after" });
    assert.deepEqual(result.previous, f.camera);
    assert.ok(!("inspection" in result.previous));
  }
});

test("explicit measurement overrides replace saved questions", t => {
  const f = fixture(t, true);
  const result = inspectionOptions("OWNER::RECEIVER", { reuse: f.file, against: ["other"], rays: [], model: "draft.step" }, f.root);
  assert.deepEqual(result.options.against, ["other"]);
  assert.deepEqual(result.options.rays, []);
  assert.equal(result.options.model, "draft.step");
  assert.deepEqual(result.options.bodies, ["owner"]);
});

test("a different subject reuses the camera without inheriting the previous subject's questions", t => {
  const f = fixture(t, false);
  const options = { reuse: f.file, output: "after" };
  const result = inspectionOptions("different-subject", options, f.root);
  assert.equal(result.query, "different-subject");
  assert.deepEqual(result.options, options);
  assert.deepEqual(result.previous, f.camera);
});
