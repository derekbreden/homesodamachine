// The fitted record as the catalog carries it to the page: which materials have a print file
// published, and what Derek said of the ones he has tried (contracts/fitted.js). Read from
// hardware/ledger/fitted.json and the artifact pointer file when the catalog is asked for.
import fs from "node:fs";
import path from "node:path";
import { printedMaterials, fittedRows } from "../contracts/fitted.js";

export function readFitted(hardwareDir, catalog, pointersPath) {
  const record = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/fitted.json"), "utf8"));
  let printFiles = [];
  try {
    const solids = JSON.parse(fs.readFileSync(pointersPath, "utf8")).solids || {};
    printFiles = Object.keys(solids)
      .filter((rel) => rel.startsWith("hardware/") && rel.endsWith(".stl"))
      .map((rel) => rel.slice("hardware/".length, -".stl".length));
  } catch { /* a checkout with no pointer file knows of no print files */ }
  return { printed: printedMaterials(catalog, printFiles), rows: fittedRows(record) };
}
