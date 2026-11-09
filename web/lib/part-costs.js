// Part-number costs, allocated from the two ledgers that price a finished unit.
//
//   * bom.md prices it line by line in delivered dollars;
//   * labor.md times it operation by operation in attended minutes.
//
// Each data row of both carries a hidden `<!--parts HSM-0010 HSM-0013:2-->`
// tag naming the part numbers it belongs to. A row's amount is divided among
// the parts present in the finished unit (`cost_root` in materials.json), by the
// weight after each colon, or by each part's quantity in the unit when no
// weights are written, and then across that part's pieces. A purchased part's
// share is its price; a made part's is the stock it is cut, printed or cast
// from; an assembly's is the supplies it consumes and the work of putting it
// together. Every dollar and minute lands somewhere, so the unit's roll-up
// through the BOM equals the ledgers' totals; a row that names no part in the
// unit stays on the unit itself as not yet allocated, and is reported.
//
// A part outside the default build — a faucet style or finish the unit does
// not ship by default — is costed in the configuration that contains it.
import fs from "node:fs";
import path from "node:path";
import { bomItems, materialIndex } from "../contracts/materials.js";
import { materialConfigurations } from "../contracts/material-quantities.js";
import { parseRun } from "../contracts/part-costs.js";

import { plainMarkdown, stripPack, readBomLines, parseTargets, cellsOf, isSeparator } from "./bom-lines.js";
export { plainMarkdown, stripPack, readBomLines, parseTargets } from "./bom-lines.js";

// The smallest lot batch-forecast.json buys each bom.md line in, on the lines
// it names by ASIN or by name. A single piece is no lot.
export function attachPurchaseLots(hardwareDir, lines) {
  let items;
  try {
    items = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger", "batch-forecast.json"), "utf-8")).items || [];
  } catch {
    return lines;
  }
  for (const item of items) {
    const lot = [...(item.options || [])].sort((a, b) => a.quantity - b.quantity)[0];
    if (!lot || (lot.quantity === 1 && item.unit === "pieces")) continue;
    const asin = /^B0[A-Z0-9]{8}$/.test(item.id) ? item.id : null;
    const byAsin = asin ? lines.filter((line) => line.href?.includes(asin)) : [];
    const name = stripPack(plainMarkdown(item.name));
    for (const line of byAsin.length ? byAsin : lines.filter((line) => line.name === name))
      line.lot = { label: lot.label, quantity: lot.quantity, unit: item.unit };
  }
  return lines;
}

export function readLaborOperations(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "labor.md"), "utf-8");
  const rate = Number(text.match(/\[\$([0-9][0-9,]*(?:\.[0-9]+)?)\]\(LABOR_RATE\)/)?.[1]?.replace(/,/g, "")) || 0;
  const batch = Number(text.match(/\[(\d+)\]\(BATCH_SIZE\)/)?.[1]) || null;
  const operations = [];
  let section = null, runColumn = -1;
  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const match = raw.match(/^## (\d+)\.\s*(.+?)\s*$/);
      section = match ? { n: Number(match[1]), name: match[2] } : null;
      continue;
    }
    if (!section || !raw.startsWith("|")) continue;
    const cells = cellsOf(raw);
    if (cells.length < 2 || isSeparator(cells)) continue;
    if (cells[0].toLowerCase() === "operation") { runColumn = cells.indexOf("Run"); continue; } // header
    if (cells[0].startsWith("**")) continue; // subtotal
    const minutes = Number(plainMarkdown(cells[cells.length - 1]).match(/^([0-9][0-9,]*(?:\.[0-9]+)?)/)?.[1]?.replace(/,/g, "")) || 0;
    operations.push({
      section: section.n,
      sectionName: section.name,
      name: plainMarkdown(cells[0]),
      minutes,
      run: runColumn > 0 && runColumn < cells.length - 1 ? parseRun(cells[runColumn]) : null,
      targets: parseTargets(raw),
    });
  }
  return { rate, batch, operations };
}

function costElement(entry, material, perPiece, fraction, pieces) {
  const { line } = entry;
  if (entry.source === "labor")
    return { kind: "labor", label: line.name, section: `${line.section}. ${line.sectionName}`, minutes: perPiece, of: line.minutes, ...(line.run && { run: line.run }) };
  // A bought part's row is its price; what a made part is cut, printed or cast
  // from is its material; anything used up in putting an assembly together, or
  // in making a part, is supplies.
  const kind = material.kind === "purchased" ? "price"
    : line.category === "consumables" || material.kind === "assembly" ? "supplies" : "stock";
  const measure = line.measure && Number.isFinite(line.measure.value)
    ? { value: line.measure.value * fraction / pieces, unit: line.measure.unit } : null;
  return {
    kind,
    label: line.stock ? `${line.stock} filament` : line.name,
    href: line.href,
    section: `${line.section}. ${line.sectionName}`,
    usd: perPiece,
    measure,
    of: line.usd,
    ...(line.lot && { lot: line.lot }),
  };
}

export function allocatePartCosts(catalog, { lines, operations, rate, batch = null }) {
  const index = materialIndex(catalog);
  const rootId = catalog.cost_root;
  if (!index.has(rootId)) throw new Error("materials.json names no cost_root in the catalog");
  const configs = materialConfigurations(catalog, rootId);
  const base = configs[0].quantities;
  const home = new Map();
  configs.forEach((config, c) => { for (const id of config.quantities.keys()) if (!home.has(id)) home.set(id, c); });

  const direct = {};
  const findings = [];
  const unallocated = { usd: 0, minutes: 0 };
  const add = (id, element) => {
    const entry = direct[id] ||= { usd: 0, minutes: 0, elements: [] };
    entry.usd += element.usd || 0;
    entry.minutes += element.minutes || 0;
    entry.elements.push(element);
  };

  const entries = [
    ...lines.map((line) => ({ source: "bom", line, amount: line.usd })),
    ...operations.map((line) => ({ source: "labor", line, amount: line.minutes })),
  ];
  for (const entry of entries) {
    const { line, amount } = entry;
    const where = entry.source === "bom" ? `bom.md §${line.section} ${line.name}` : `labor.md §${line.section} ${line.name}`;
    const targets = line.targets || [];
    if (!line.targets) findings.push({ kind: "untagged", where, amount, source: entry.source });
    for (const target of targets) if (!index.has(target.id)) findings.push({ kind: "unknown", where, material: target.id });
    let placed = false;
    configs.forEach((config, c) => {
      const present = targets.filter((target) => index.has(target.id) && config.quantities.get(target.id) > 0);
      const weight = (target) => target.weight ?? config.quantities.get(target.id);
      const sum = present.reduce((total, target) => total + weight(target), 0);
      if (!sum) return;
      if (c === 0) placed = true;
      for (const target of present) {
        if (home.get(target.id) !== c) continue;
        const pieces = config.quantities.get(target.id), fraction = weight(target) / sum;
        add(target.id, costElement(entry, index.get(target.id), amount * fraction / pieces, fraction, pieces));
      }
    });
    if (!placed) {
      if (entry.source === "bom") unallocated.usd += amount; else unallocated.minutes += amount;
      if (line.targets) findings.push({ kind: "absent", where, amount, source: entry.source, materials: targets.map((target) => target.id) });
    }
  }
  if (unallocated.usd) add(rootId, { kind: "unallocated", label: "bom.md rows not yet on a part number", usd: unallocated.usd });
  if (unallocated.minutes) add(rootId, { kind: "unallocated", label: "labor.md operations not yet on a part number", minutes: unallocated.minutes });

  // A purchased part's ledger count against the catalog's pieces in the unit.
  const groups = new Map();
  for (const line of lines) {
    const ids = (line.targets || []).map((target) => target.id).filter((id) => index.get(id)?.kind === "purchased");
    if (!ids.length || ids.length !== line.targets.length || line.count == null) continue;
    const key = [...new Set(ids)].sort().join(" ");
    const group = groups.get(key) || { ids: key.split(" "), ledger: 0, rows: [] };
    group.ledger += line.count; group.rows.push(`§${line.section} ${line.name}`);
    groups.set(key, group);
  }
  for (const group of groups.values()) {
    const catalogCount = group.ids.reduce((total, id) => total + (base.get(id) || 0), 0);
    if (catalogCount && catalogCount !== group.ledger)
      findings.push({ kind: "count", materials: group.ids, ledger: group.ledger, catalog: catalogCount, rows: group.rows });
  }

  // A part in the unit with no cost of its own and nothing costed beneath it.
  for (const id of base.keys()) {
    const material = index.get(id);
    if (direct[id] || bomItems(material, configs[0].options).length) continue;
    findings.push({ kind: "uncosted", material: id, description: material?.description });
  }

  const usd = lines.reduce((total, line) => total + line.usd, 0);
  const minutes = operations.reduce((total, op) => total + op.minutes, 0);
  return {
    root: rootId,
    rate,
    batch,
    options: configs[0].options,
    costed: [...home.keys()],
    ledger: { usd, minutes, lines: lines.length, operations: operations.length },
    unallocated,
    direct,
    findings,
  };
}

export function readPartCosts(hardwareDir, catalog) {
  const { rate, batch, operations } = readLaborOperations(hardwareDir);
  const lines = attachPurchaseLots(hardwareDir, readBomLines(hardwareDir));
  return allocatePartCosts(catalog, { lines, operations, rate, batch });
}
