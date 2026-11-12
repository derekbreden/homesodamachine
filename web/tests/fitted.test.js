// The fitted record as the site reads it (web/contracts/fitted.js): which materials have a print
// file, what the record says of each, and which are not fitted yet. The repository's own record
// is held to the catalog it names.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { printedMaterials, fittedRows, fittedState, notFitted } from "../contracts/fitted.js";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { readFitted } from "../lib/fitted.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const HARDWARE = path.join(REPO_ROOT, "hardware");

const catalog = { materials: [
  { id: "HSM-1", models: [{ file: "printed-parts/a/a.step" }] },
  { id: "HSM-2", models: [{ file: "printed-parts/b/b.step" }] },
  { id: "HSM-3", models: [{ file: "reference/c/c.step" }] },
  { id: "HSM-4" },
] };

test("a material with a print file beside its model is a printed one", () => {
  assert.deepEqual(printedMaterials(catalog, ["printed-parts/a/a", "printed-parts/b/b", "printed-parts/z/z"]), ["HSM-1", "HSM-2"]);
  assert.deepEqual(printedMaterials(catalog, []), []);
});

test("the record's rows sort by material, each material's latest first", () => {
  const rows = fittedRows({ fitted: [
    { material: "HSM-1", date: "2026-09-20", said: "fits", tried: "on the valve", record: "x.json" },
    { material: "HSM-1", date: "2026-10-25", said: "looks good", tried: "again" },
    { material: "HSM-9", said: "works" },
    { material: "HSM-2" },
  ] });
  assert.deepEqual(rows["HSM-1"].map((row) => row.date), ["2026-10-25", "2026-09-20"]);
  assert.deepEqual(rows["HSM-1"][1], { date: "2026-09-20", said: "fits", tried: "on the valve", record: "x.json" });
  assert.deepEqual(rows["HSM-9"], [{ date: "", said: "works", tried: "" }]);
  assert.equal(rows["HSM-2"], undefined, "a row with no words is no row");
  assert.deepEqual(fittedRows(null), {});
});

test("a printed part is fitted or not fitted yet, and other parts say nothing", () => {
  const fitted = { printed: ["HSM-1", "HSM-2"], rows: { "HSM-1": [{ date: "2026-09-20", said: "fits", tried: "" }], "HSM-3": [{ date: "2026-10-01", said: "ok", tried: "" }] } };
  assert.equal(fittedState(fitted, "HSM-1").fitted, true);
  assert.deepEqual(fittedState(fitted, "HSM-2"), { fitted: false, rows: [] });
  assert.equal(fittedState(fitted, "HSM-3").fitted, true, "a row counts on a part with no print file too");
  assert.equal(fittedState(fitted, "HSM-4"), null);
  assert.equal(fittedState(null, "HSM-1"), null);
  assert.deepEqual(notFitted(fitted, ["HSM-2", "HSM-1", "HSM-4", "HSM-2"]), ["HSM-2"]);
});

test("the repository's record names materials of the catalog and gives each row its words", () => {
  const record = JSON.parse(fs.readFileSync(path.join(HARDWARE, "ledger", "fitted.json"), "utf8"));
  const ids = new Set(readMaterialCatalog(HARDWARE).materials.map((m) => m.id));
  assert.ok(record.fitted.length, "the record holds rows");
  for (const row of record.fitted) {
    assert.ok(ids.has(row.material), `${row.material} is a material of the catalog`);
    assert.match(row.date, /^\d{4}-\d{2}-\d{2}$/, `${row.material} gives the day`);
    assert.ok(row.said && row.tried, `${row.material} gives his words and what he tried`);
  }
});

test("the catalog the site serves carries the record", () => {
  const read = readMaterialCatalog(HARDWARE);
  const fitted = readFitted(HARDWARE, read, path.join(HARDWARE, "cad-artifacts.json"));
  assert.ok(fitted.printed.length > 0, "print files are found");
  assert.equal(fittedState(fitted, "HSM-0268").fitted, true, "the faucet lever is fitted");
  const none = readFitted(HARDWARE, read, path.join(HARDWARE, "no-such-pointer.json"));
  assert.deepEqual(none.printed, [], "a checkout with no pointer file knows of no print files");
});
