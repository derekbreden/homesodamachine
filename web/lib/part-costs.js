// Part-number costs, allocated from the two ledgers that price a finished unit.
//
//   * bom.md prices it line by line in delivered dollars;
//   * labor.md times it operation by operation in attended minutes.
//
// Each data row of both carries a hidden `<!--parts HSM-000010 HSM-000013:2-->`
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
import { FAUCET_FINISHES } from "../contracts/faucet-options.js";

const PARTS_RE = /<!--parts\s+([\s\S]*?)-->/;
const TARGET_RE = /HSM-\d{6}(?::\d+(?:\.\d+)?)?/g;
const CATEGORY_RE = /<!--@([a-z][a-z-]*)-->/;
const MONEY_RE = /\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)/;
const COMMENT_RE = /<!--[\s\S]*?-->/g;

// Every cell the ledgers hold is prose off a markdown table, and their numbers
// are docgen markers — `[value](NAME)`. Strip the marker syntax back to the
// value, and the emphasis around it, so a cell reads as prose.
export function plainMarkdown(text) {
  return String(text)
    .replace(COMMENT_RE, "")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\*\*([^*]*)\*\*/g, "$1")
    .replace(/~~([^~]*)~~/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

// Drop the purchase pack size from a display name — both the parenthetical form
// ("(20-pk)", "(2-pack)", "(bag of 10)") and the inline form (", 100 pc",
// ", 120 pc"). ASINs and part numbers in parentheses carry no pack word and stay;
// lengths and dimensions ("100 ft spool", "10–16 mm") are not pc/pk and survive.
export function stripPack(name) {
  return name
    .replace(/\s*\([^()]*\b(?:pk|pack|pcs?|ct|sets?|pieces?|count|bag)\b[^()]*\)/gi, "")
    .replace(/,\s*\d+\s*(?:pc|pcs|pk|pack)\b/gi, "")
    .replace(/\s{2,}/g, " ")
    .replace(/\s*,\s*$/g, "")
    .trim();
}

const cellsOf = (row) => row.replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
const isSeparator = (cells) => cells.every((cell) => /^[-:\s]*$/.test(cell));
const parseMoney = (cell) => {
  const match = String(cell).replace(COMMENT_RE, "").match(MONEY_RE);
  return match ? parseFloat(match[1].replace(/,/g, "")) : 0;
};

export function parseTargets(text) {
  const tag = String(text).match(PARTS_RE);
  if (!tag) return null;
  return [...tag[1].matchAll(TARGET_RE)].map(([token]) => {
    const [id, weight] = token.split(":");
    return { id, weight: weight == null ? null : Number(weight) };
  });
}

// A quantity cell → a discrete piece count, or null when it is a measure sold
// by length, weight or fraction ("~5 ft", "1/2 roll", "78 g").
function parseCount(cell) {
  const text = plainMarkdown(cell);
  if (/[/]|\b(ft|kg|g|m|in|inches|oz|roll|pair|set|sets|collars?|columns?)\b/i.test(text)) return null;
  const match = text.match(/^~?\s*(\d+)\b/);
  return match ? parseInt(match[1], 10) : null;
}

// A quantity cell → { value, unit } when it is a length or a mass per build.
function parseMeasure(cell) {
  const match = plainMarkdown(cell).match(/^~?\s*([0-9]+(?:\.[0-9]+)?)\s*(ft|m|mm|in|inches|g|kg)\b/i);
  if (!match) return null;
  const unit = match[2].toLowerCase() === "inches" ? "in" : match[2].toLowerCase();
  return { value: Number(match[1]), unit };
}

export function readBomLines(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "bom.md"), "utf-8");
  const lines = [];
  let section = null;
  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const match = raw.match(/^## (\d+)\.\s*(.+?)\s*$/);
      section = match ? { n: Number(match[1]), name: match[2] } : null;
      continue;
    }
    if (!section || !raw.startsWith("|")) continue;
    const category = raw.match(CATEGORY_RE)?.[1];
    if (!category) continue; // a data row is one that carries a category
    const cells = cellsOf(raw);
    if (isSeparator(cells)) continue;
    // §7's printed parts read Part | Qty | Material | Mass (kg) | $; every other
    // table reads Part | Notes | Qty | Unit $ | Line $.
    const printed = section.n === 7;
    const qty = printed ? cells[1] : cells[cells.length - 3];
    lines.push({
      section: section.n,
      sectionName: section.name,
      name: printed ? plainMarkdown(cells[0]) : stripPack(plainMarkdown(cells[0])),
      href: cells[0].match(/\]\((https?:[^)\s]+)\)/)?.[1] || null,
      qty: plainMarkdown(qty || ""),
      count: parseCount(qty || ""),
      measure: printed ? { value: Number(plainMarkdown(cells[3])), unit: "kg" } : parseMeasure(qty || ""),
      stock: printed ? plainMarkdown(cells[2]).replace(/\s*\([^)]*[×,][^)]*\)/g, "") : null,
      usd: parseMoney(cells[cells.length - 1]),
      category,
      targets: parseTargets(raw),
    });
  }
  return lines;
}

export function readLaborOperations(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "labor.md"), "utf-8");
  const rate = Number(text.match(/\[\$([0-9][0-9,]*(?:\.[0-9]+)?)\]\(LABOR_RATE\)/)?.[1]?.replace(/,/g, "")) || 0;
  const operations = [];
  let section = null;
  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const match = raw.match(/^## (\d+)\.\s*(.+?)\s*$/);
      section = match ? { n: Number(match[1]), name: match[2] } : null;
      continue;
    }
    if (!section || !raw.startsWith("|")) continue;
    const cells = cellsOf(raw);
    if (cells.length < 2 || isSeparator(cells)) continue;
    if (cells[0].toLowerCase() === "operation" || cells[0].startsWith("**")) continue; // header / subtotal
    const minutes = Number(plainMarkdown(cells[cells.length - 1]).match(/^([0-9][0-9,]*)/)?.[1]?.replace(/,/g, "")) || 0;
    operations.push({
      section: section.n,
      sectionName: section.name,
      name: plainMarkdown(cells[0]),
      minutes,
      targets: parseTargets(raw),
    });
  }
  return { rate, operations };
}

// Total pieces of each material in one unit, through every assembly level.
// `swap` replaces a material with its variant wherever it occurs.
function unitQuantities(catalog, rootId, options, swap = null) {
  const index = materialIndex(catalog);
  const totals = new Map([[rootId, 1]]);
  (function visit(id, quantity, seen) {
    if (seen.has(id)) return;
    const next = new Set([...seen, id]);
    for (const item of bomItems(index.get(id), options)) {
      if (typeof item.quantity !== "number") continue;
      const child = swap?.get(item.material) || item.material;
      const pieces = quantity * item.quantity;
      totals.set(child, (totals.get(child) || 0) + pieces);
      visit(child, pieces, next);
    }
  })(rootId, 1, new Set());
  return totals;
}

// The default build first — the first faucet finish and the faucet style the
// unit names — then each other finish, then each variant of a part in the unit.
function configurations(catalog, rootId) {
  const [first, ...others] = FAUCET_FINISHES.map((finish) => finish.id);
  const base = { options: { finish: first }, swap: null };
  const configs = [base, ...others.map((finish) => ({ options: { finish }, swap: null }))];
  const present = unitQuantities(catalog, rootId, base.options);
  for (const material of catalog.materials)
    for (const relation of present.has(material.id) ? material.relations || [] : [])
      if (relation.kind === "variant" && !present.has(relation.material))
        configs.push({ options: base.options, swap: new Map([[material.id, relation.material]]) });
  return configs.map((config) => ({ ...config, quantities: unitQuantities(catalog, rootId, config.options, config.swap) }));
}

function costElement(entry, material, perPiece, fraction, pieces) {
  const { line } = entry;
  if (entry.source === "labor")
    return { kind: "labor", label: line.name, section: `${line.section}. ${line.sectionName}`, minutes: perPiece, of: line.minutes };
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
  };
}

export function allocatePartCosts(catalog, { lines, operations, rate }) {
  const index = materialIndex(catalog);
  const rootId = catalog.cost_root;
  if (!index.has(rootId)) throw new Error("materials.json names no cost_root in the catalog");
  const configs = configurations(catalog, rootId);
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
    options: configs[0].options,
    costed: [...home.keys()],
    ledger: { usd, minutes, lines: lines.length, operations: operations.length },
    unallocated,
    direct,
    findings,
  };
}

export function readPartCosts(hardwareDir, catalog) {
  const { rate, operations } = readLaborOperations(hardwareDir);
  return allocatePartCosts(catalog, { lines: readBomLines(hardwareDir), operations, rate });
}
