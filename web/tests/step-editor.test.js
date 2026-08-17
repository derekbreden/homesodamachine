// The gate on the dev-only STEP component editor (lib/step-editor-routes.js).
//
// That module's EDITABLE registry is what scopes the editor: it decides which
// .step a move may be written against, and therefore which generator the route
// is allowed to spawn. A path outside it 404s, which is also how the viewer
// decides whether to show the Edit toggle at all (public/js/viewer/
// component-edit.js sets `available` off that answer).
//
// The registry is EMPTY — an entry is only sound when its generator reads the
// `.overrides.json` sidecar beside the .step, and no generator in the tree does.
// So these pin the closed gate: nothing is editable, and a write that gets
// refused leaves no sidecar behind and starts no CAD build.

import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";

import { mountStepEditorRoutes } from "../lib/step-editor-routes.js";

// The assembly the viewer actually shows, as it references it: relative to the
// content root. This is the path a caller would reach for first, so it is the
// one worth naming.
const LIVE_STEP = "manifold-layout/enclosure-assembly.step";
const SIDECAR = LIVE_STEP.replace(/\.step$/, ".overrides.json");

let tmp, hardwareDir, server, baseUrl;
let rebuilt; // generator paths handed to the rebuild, in order

before(async () => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-step-editor-"));
  hardwareDir = path.join(tmp, "hardware");
  fs.mkdirSync(path.join(hardwareDir, path.dirname(LIVE_STEP)), { recursive: true });

  const app = express();
  app.use(express.json());
  rebuilt = [];
  mountStepEditorRoutes(app, { hardwareDir }, async (generatorPath) => {
    rebuilt.push(generatorPath);
    return { ok: true };
  });
  server = app.listen(0);
  await new Promise((r) => server.once("listening", r));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => {
  server?.close();
  fs.rmSync(tmp, { recursive: true, force: true });
});

beforeEach(() => {
  rebuilt = [];
});

const sidecarWritten = () => fs.existsSync(path.join(hardwareDir, SIDECAR));

function get(file) {
  return fetch(`${baseUrl}/api/step-editor/overrides?file=${encodeURIComponent(file)}`);
}

function post(body) {
  return fetch(`${baseUrl}/api/step-editor/override`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

function del(body) {
  return fetch(`${baseUrl}/api/step-editor/overrides`, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

// --- the gate is closed -----------------------------------------------------

test("the live enclosure assembly is not editable", async () => {
  // A tripwire, not a preference: adding `manifold-layout/enclosure-assembly.step` to
  // EDITABLE only works if enclosure_assembly.py reads its `.overrides.json` and applies
  // the moves as it places. Until it does, the route writes a sidecar nothing
  // reads, spends a full CAD rebuild, and returns the body to where it started.
  const res = await get(LIVE_STEP);
  assert.equal(
    res.status, 404,
    "enclosure-assembly.step is listed as editable — confirm enclosure_assembly.py applies "
    + "the overrides sidecar",
  );
});

test("no file is editable, whatever the request names", async () => {
  for (const file of [LIVE_STEP, "printed-parts/other/other.step", "", "../../etc/passwd"]) {
    const res = await get(file);
    assert.equal(res.status, 404, `GET ${file}`);
  }
});

test("a refused write leaves no sidecar and starts no build", async () => {
  const res = await post({
    file: LIVE_STEP,
    component: "water-split",
    translate: [-21.47, 0, 11.6],
    rotate: { axis: [0, 1, 0], deg: 90 },
  });

  assert.equal(res.status, 404);
  assert.equal(sidecarWritten(), false, "POST wrote a sidecar");
  assert.deepEqual(rebuilt, [], "POST ran a generator");
});

test("a refused reset leaves no sidecar and starts no build", async () => {
  const res = await del({ file: LIVE_STEP });

  assert.equal(res.status, 404);
  assert.equal(sidecarWritten(), false, "DELETE wrote a sidecar");
  assert.deepEqual(rebuilt, [], "DELETE ran a generator");
});

test("the gate closes ahead of the request body, so a malformed one is still refused", async () => {
  // `entryFor` runs before the component check and before the root is resolved —
  // an unknown file never reaches either, so no body shape gets a different answer.
  for (const body of [{}, { file: LIVE_STEP }, { component: "water-split" },
    { file: LIVE_STEP, component: 42 }]) {
    const res = await post(body);
    assert.equal(res.status, 404, JSON.stringify(body));
  }
  assert.deepEqual(rebuilt, []);
});
