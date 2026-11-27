#!/usr/bin/env node
// material-number gives a new material its number. With no argument it prints the next number above
// the highest allocated and records it in hardware/ledger/materials.allocated.json, with the
// materials that have left the catalog since the register last changed. `--check` writes nothing
// and names every record whose number is retired, unallocated or shared.
import path from "node:path";
import { fileURLToPath } from "node:url";
import { allocateMaterialNumber, checkMaterialNumbers, materialNumbers } from "../web/lib/material-catalog.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), ".."),
  hardware = path.join(root, "hardware");
const args = process.argv.slice(2);
try {
  if (!args.length) {
    // Allocations in this checkout take turns on this lock.
    const { id, problems } = allocateMaterialNumber(hardware, path.join(root, ".cache/material-number.lock"));
    console.log(id);
    for (const problem of problems) console.error(problem);
  } else if (args.length === 1 && args[0] === "--check") {
    const problems = checkMaterialNumbers(hardware);
    for (const problem of problems) console.error(problem);
    if (problems.length) process.exitCode = 1;
    else console.log(`Every record holds a number allocated to it; the highest allocated is ${materialNumbers(hardware).highest}.`);
  } else {
    console.error("Use node tools/material-number.mjs for the next material number, or add --check.");
    process.exitCode = 1;
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
