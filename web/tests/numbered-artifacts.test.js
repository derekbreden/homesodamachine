import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm, stat } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import express from "express";
import { mountViewerRoutes } from "../lib/viewer-routes.js";
import { namedBy } from "../lib/objects.js";
import { retireSolids } from "../lib/artifacts-live.js";

test("public model paths follow numbered membership and store retention keeps build inputs", async t => {
  const root = await mkdtemp(path.join(tmpdir(), "numbered-artifacts-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const hardware = path.join(root, "hardware");
  for (const folder of ["parts", "studies", "ledger"]) await mkdir(path.join(hardware, folder), { recursive: true });
  const part = "hardware/parts/part.step", study = "hardware/studies/study.step";
  await writeFile(path.join(root, part), "numbered geometry");
  await writeFile(path.join(root, study), "build-only geometry");
  const pointers = { store: { objects: "s-" }, solids: { [part]: "public", [study]: "build" },
    website: { solids: { [part]: "public" }, sidecars: {} } };
  const pointer = path.join(root, "cad-artifacts.json");
  await writeFile(pointer, JSON.stringify(pointers));
  const catalog = { materials: [{ id: "HSM-000001", models: [{ file: "parts/part.step" }] }] };
  const catalogPath = path.join(hardware, "ledger/materials.json");
  await writeFile(catalogPath, JSON.stringify(catalog));
  const old = process.env.RENDER_GIT_COMMIT;
  process.env.RENDER_GIT_COMMIT = "website-fixture";
  t.after(() => { if (old === undefined) delete process.env.RENDER_GIT_COMMIT; else process.env.RENDER_GIT_COMMIT = old; });
  const app = express();
  mountViewerRoutes(app, { hardwareDir: hardware, pointersPath: pointer, store: { publicUrl: "https://objects.example" } });
  const server = app.listen(0, "127.0.0.1");
  await new Promise(resolve => server.once("listening", resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  const get = suffix => fetch(`http://127.0.0.1:${server.address().port}${suffix}`);
  assert.equal((await get("/steps/parts/part.step")).status, 200);
  assert.equal((await get("/steps/studies/study.step")).status, 404);
  assert.deepEqual(Object.keys((await (await get("/api/objects")).json()).objects), ["parts/part.step"]);
  assert.deepEqual(namedBy(pointers), new Set(["public", "build"]));
  // A material number changes access without a filename allowlist edit.
  catalog.materials.push({ id: "HSM-000002", models: [{ file: "studies/study.step", context: true }] });
  await writeFile(catalogPath, JSON.stringify(catalog));
  assert.equal((await get("/steps/studies/study.step")).status, 200);
  // A local render/build tree retains the build input even though the site omits it.
  await retireSolids(root, { solids: pointers.solids }, pointers, { websiteOnly: false });
  assert.ok((await stat(path.join(root, study))).isFile());
});
