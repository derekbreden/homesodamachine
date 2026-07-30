// Edition routing for the dev-only STEP component editor (lib/step-editor-routes.js).
//
// The editable path in that module's registry is relative to a content root, and
// the editions mirror each other's filenames — `printed-parts/enclosure/
// enclosure-assembly/enclosure-assembly.step` resolves in BOTH trees. So a root
// bound once at mount time doesn't fail loudly when the viewer is showing the
// other machine; it silently writes the override into the default edition and
// rebuilds that generator, leaving the assembly on screen untouched.
//
// These pin the resolution to the same per-request signal the viewer's own read
// endpoints use (the `hsmEdition` cookie, ?edition= override, fallback on an
// unknown id), so an edit lands in the tree it was made in.

import { test, before, after, beforeEach } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";

import { mountStepEditorRoutes } from "../lib/step-editor-routes.js";

const FILE = "printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step";
const SIDECAR = FILE.replace(/\.step$/, ".overrides.json");

let tmp, editionDirs, server, baseUrl;
let rebuilt; // generator paths handed to the rebuild, in order

before(async () => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-step-editor-"));
  editionDirs = { kitchen: path.join(tmp, "hardware"), thin: path.join(tmp, "thin", "hardware") };
  for (const root of Object.values(editionDirs)) {
    fs.mkdirSync(path.join(root, path.dirname(FILE)), { recursive: true });
  }

  const app = express();
  app.use(express.json());
  rebuilt = [];
  mountStepEditorRoutes(app, { editionDirs }, async (generatorPath) => {
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
  for (const root of Object.values(editionDirs)) {
    fs.rmSync(path.join(root, SIDECAR), { force: true });
  }
});

const sidecarPath = (edition) => path.join(editionDirs[edition], SIDECAR);
const readSidecar = (edition) => {
  try { return JSON.parse(fs.readFileSync(sidecarPath(edition), "utf-8")); } catch { return null; }
};
const writeSidecar = (edition, data) =>
  fs.writeFileSync(sidecarPath(edition), JSON.stringify(data, null, 2) + "\n", "utf-8");

function get(qs, cookie) {
  return fetch(`${baseUrl}/api/step-editor/overrides?${qs}`, {
    headers: cookie ? { cookie } : {},
  });
}

function post(body, cookie) {
  return fetch(`${baseUrl}/api/step-editor/override`, {
    method: "POST",
    headers: { "content-type": "application/json", ...(cookie ? { cookie } : {}) },
    body: JSON.stringify(body),
  });
}

// --- reads ------------------------------------------------------------------

test("GET reads the sidecar of the edition the cookie names", async () => {
  writeSidecar("kitchen", { "water-split": [{ translate: [1, 0, 0] }] });
  writeSidecar("thin", { "water-split": [{ translate: [2, 0, 0] }] });

  const res = await get(`file=${encodeURIComponent(FILE)}`, "hsmEdition=thin");
  const body = await res.json();
  assert.deepEqual(body.overrides["water-split"], [{ translate: [2, 0, 0] }]);
});

test("GET with no cookie falls back to the default edition", async () => {
  writeSidecar("kitchen", { "water-split": [{ translate: [1, 0, 0] }] });
  writeSidecar("thin", { "water-split": [{ translate: [2, 0, 0] }] });

  const body = await (await get(`file=${encodeURIComponent(FILE)}`)).json();
  assert.deepEqual(body.overrides["water-split"], [{ translate: [1, 0, 0] }]);
});

test("GET ?edition= overrides the cookie", async () => {
  writeSidecar("kitchen", { "water-split": [{ translate: [1, 0, 0] }] });
  writeSidecar("thin", { "water-split": [{ translate: [2, 0, 0] }] });

  const body = await (await get(
    `file=${encodeURIComponent(FILE)}&edition=thin`, "hsmEdition=kitchen",
  )).json();
  assert.deepEqual(body.overrides["water-split"], [{ translate: [2, 0, 0] }]);
});

test("GET with an unknown edition falls back rather than erroring", async () => {
  writeSidecar("kitchen", { "water-split": [{ translate: [1, 0, 0] }] });

  const res = await get(`file=${encodeURIComponent(FILE)}`, "hsmEdition=nonesuch");
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.deepEqual(body.overrides["water-split"], [{ translate: [1, 0, 0] }]);
});

// --- writes -----------------------------------------------------------------

test("POST writes into the cookie's edition and leaves the other tree alone", async () => {
  const res = await post({
    file: FILE,
    component: "water-split",
    translate: [-21.47, 0, 11.6],
    rotate: { axis: [0, 1, 0], deg: 90 },
  }, "hsmEdition=thin");

  assert.equal((await res.json()).ok, true);
  assert.deepEqual(readSidecar("thin")["water-split"], [
    { translate: [-21.47, 0, 11.6], rotate: { axis: [0, 1, 0], deg: 90 } },
  ]);
  assert.equal(readSidecar("kitchen"), null);
});

test("POST rebuilds the generator in the cookie's edition", async () => {
  await post({ file: FILE, component: "water-split", translate: [1, 2, 3] }, "hsmEdition=thin");

  assert.deepEqual(rebuilt, [
    path.join(editionDirs.thin, path.dirname(FILE), "enclosure_assembly.py"),
  ]);
});

test("POST with no cookie stays in the default edition", async () => {
  await post({ file: FILE, component: "water-split", translate: [1, 2, 3] });

  assert.ok(readSidecar("kitchen"));
  assert.equal(readSidecar("thin"), null);
  assert.deepEqual(rebuilt, [
    path.join(editionDirs.kitchen, path.dirname(FILE), "enclosure_assembly.py"),
  ]);
});

test("DELETE clears and rebuilds within the cookie's edition", async () => {
  writeSidecar("kitchen", { "water-split": [{ translate: [1, 0, 0] }] });
  writeSidecar("thin", { "water-split": [{ translate: [2, 0, 0] }] });

  const res = await fetch(`${baseUrl}/api/step-editor/overrides`, {
    method: "DELETE",
    headers: { "content-type": "application/json", cookie: "hsmEdition=thin" },
    body: JSON.stringify({ file: FILE }),
  });

  assert.equal((await res.json()).ok, true);
  assert.equal(readSidecar("thin"), null);
  assert.deepEqual(readSidecar("kitchen"), { "water-split": [{ translate: [1, 0, 0] }] });
});

// --- the registry still gates, per edition ----------------------------------

test("a file outside the editable registry 404s whatever the edition", async () => {
  for (const cookie of ["hsmEdition=thin", "hsmEdition=kitchen"]) {
    const res = await get("file=printed-parts/other/other.step", cookie);
    assert.equal(res.status, 404);
  }
});
