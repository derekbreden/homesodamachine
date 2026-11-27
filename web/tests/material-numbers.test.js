// Material numbers: a record on a retired, unallocated, shared or malformed number is refused with
// the command that gives the next one, allocation records each number it gives, and the
// repository's catalog holds to its register.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { materialNumberProblems, allocateMaterialNumber, checkMaterialNumbers } from "../lib/material-catalog.js";

const HARDWARE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "hardware");
const record = (id, description = id) => ({ id, description });

test("a retired, unallocated, shared or malformed number is refused with the command", () => {
  const numbers = { highest: "HSM-0005", retired: ["HSM-0004"] };
  const catalog = { materials: [record("HSM-0001"), record("HSM-0004"), record("HSM-0006"), record("HSM-0002", "first"), record("HSM-0002", "second"), record("HSM-3")] };
  const problems = materialNumberProblems(catalog, numbers);
  assert.deepEqual(problems.map((problem) => problem.split(" ")[0]), ["HSM-0004", "HSM-0006", "HSM-3", "HSM-0002"]);
  for (const problem of problems) assert.match(problem, /`node tools\/material-number\.mjs`/);
  assert.deepEqual(materialNumberProblems({ materials: [record("HSM-0001"), record("HSM-0005")] }, numbers), []);
});

test("allocation gives the number above the highest allocated and every record's, and records it", (t) => {
  const root = fs.mkdtempSync(path.join(tmpdir(), "material-numbers-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const hardware = path.join(root, "hardware"), register = path.join(hardware, "ledger/materials.allocated.json");
  const lock = path.join(root, ".cache/material-number.lock");
  fs.mkdirSync(path.join(hardware, "ledger"), { recursive: true });
  fs.writeFileSync(path.join(hardware, "ledger/materials.json"), JSON.stringify({ materials: [record("HSM-0001"), record("HSM-0007")] }));
  fs.writeFileSync(register, JSON.stringify({ highest: "HSM-0005", retired: ["HSM-0004"] }));
  assert.equal(allocateMaterialNumber(hardware, lock).id, "HSM-0008");
  assert.equal(allocateMaterialNumber(hardware, lock).id, "HSM-0009");
  assert.deepEqual(JSON.parse(fs.readFileSync(register, "utf8")), { highest: "HSM-0009", retired: ["HSM-0004"] });
  assert.equal(fs.existsSync(lock), false);
});

test("every record in the repository's catalog holds a number allocated to it", () => {
  assert.deepEqual(checkMaterialNumbers(HARDWARE), []);
});
