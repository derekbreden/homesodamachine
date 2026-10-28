#!/usr/bin/env node
// How bom.md's dollars and labor.md's minutes land on part numbers.
//
//   node web/scripts/part-costs.mjs            totals, reconciliation and findings
//   node web/scripts/part-costs.mjs --tree     the finished unit's costed BOM, every level
//   node web/scripts/part-costs.mjs HSM-000004 one material: its own cost and its roll-up
//
// web/lib/part-costs.js does the allocation; this prints what it decided.
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { readPartCosts } from "../lib/part-costs.js";
import { bomItems, materialIndex } from "../contracts/materials.js";
import { rollupCost, money, duration, runText } from "../contracts/part-costs.js";

const hardwareDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../hardware");
const catalog = readMaterialCatalog(hardwareDir);
catalog.costs = readPartCosts(hardwareDir, catalog);
const { costs } = catalog;
const index = materialIndex(catalog);
const args = process.argv.slice(2);
const memo = new Map();
const roll = (id) => rollupCost(catalog, id, costs.options, memo);

function describe(id) {
  const material = index.get(id);
  const own = costs.direct[id];
  const total = roll(id);
  console.log(`${id} ${material?.description || "(not in catalog)"} [${material?.kind}]`);
  console.log(`  roll-up ${money(total.usd)} = parts ${money(total.parts)} + labor ${money(total.labor)} (${duration(total.minutes)})`);
  for (const element of own?.elements || []) {
    const amount = element.kind === "labor" ? `${duration(element.minutes)} of ${element.of} m` : money(element.usd);
    const measure = element.measure ? ` · ${+element.measure.value.toFixed(3)} ${element.measure.unit}` : "";
    console.log(`  ${element.kind.padEnd(11)} ${amount.padStart(14)}  ${element.label}${measure}  (${element.section || ""})`);
    if (element.run) console.log(`  ${"".padEnd(26)}  ${runText(element.run, costs.batch)}`);
    if (element.lot) console.log(`  ${"".padEnd(26)}  Lot: ${element.lot.label}`);
  }
}

function tree(id, depth = 0, quantity = 1, seen = new Set()) {
  const material = index.get(id), total = roll(id);
  const own = costs.direct[id];
  const line = `${"  ".repeat(depth)}${quantity === 1 ? "" : quantity + " × "}${material.description} ${id}`;
  console.log(`${line.padEnd(96)} ${money(quantity * total.usd).padStart(11)}${own?.minutes ? "  labor " + duration(own.minutes) : ""}`);
  if (seen.has(id)) return;
  for (const item of bomItems(material, costs.options))
    tree(item.material, depth + 1, item.quantity, new Set([...seen, id]));
}

if (args[0]?.startsWith("HSM-")) {
  for (const id of args) describe(id);
} else if (args.includes("--tree")) {
  tree(costs.root);
} else {
  const total = roll(costs.root);
  const ledgerLabor = costs.ledger.minutes * costs.rate / 60;
  console.log(`Finished unit ${costs.root} ${index.get(costs.root).description}`);
  console.log(`  ledgers     parts ${money(costs.ledger.usd)} (${costs.ledger.lines} rows) + labor ${money(ledgerLabor)} (${duration(costs.ledger.minutes)}, ${costs.ledger.operations} operations)`);
  console.log(`  roll-up     parts ${money(total.parts)} + labor ${money(total.labor)} = ${money(total.usd)}`);
  console.log(`  unallocated ${money(costs.unallocated.usd)} and ${duration(costs.unallocated.minutes)}`);
  const kinds = {};
  for (const finding of costs.findings) (kinds[finding.kind] ||= []).push(finding);
  for (const [kind, list] of Object.entries(kinds)) {
    console.log(`\n${kind} (${list.length})`);
    for (const finding of list) {
      if (kind === "untagged" || kind === "absent")
        console.log(`  ${finding.where}  ${finding.source === "labor" ? duration(finding.amount) : money(finding.amount)}${finding.materials ? "  → " + finding.materials.join(" ") : ""}`);
      else if (kind === "count")
        console.log(`  ${finding.materials.join(" ")}  ledger ${finding.ledger}, catalog ${finding.catalog}  (${finding.rows.join("; ")})`);
      else if (kind === "unknown") console.log(`  ${finding.where}  ${finding.material}`);
      else console.log(`  ${finding.material} ${finding.description}`);
    }
  }
}
