// /cost — build cost, planned sale price, and investment recovery.
//
// Two rollups, two ledgers:
//   * PARTS — hardware/ledger/bom.md, keyed by the hidden <!--@TAG--> category
//     marker and the line cost on each data row (the same tags hardware/scripts/
//     _bom_categories.py owns and checks).
//   * LABOR — hardware/ledger/labor.md, keyed by section, carrying an
//     attended-minute estimate per operation and the hourly rate they're priced
//     at. Section subtotals there are written by hardware/scripts/
//     _labor_totals.py; this view sums the operation rows itself rather than
//     reading those, so the page can't inherit a stale total.
// purchases.md supplies the recorded investment. The shared cost-recovery.js
// model defines the planned price and recovery arithmetic for server and browser.

import path from "path";
import fs from "fs";
import { renderHead, renderNav, renderFooter } from "./shell.js";
import {
  SALE_PRICE, SALES_HORIZON, dollars, recoveryPlan, recoveryRange,
  recoverySummary, salesBalance, renderRecoveryChart,
} from "../public/cost-recovery.js";

// Every cell this page shows is prose off a markdown table, and the ledgers
// write their numbers as docgen markers — `[value](NAME)`, so a figure has one
// authored home and every reader takes the same value. Strip the marker syntax
// back to the value, and the emphasis around it, so a cell reads as prose here.
function plainMarkdown(text) {
  return String(text)
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\*\*([^*]*)\*\*/g, "$1")
    .replace(/~~([^~]*)~~/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

// Display names mirror hardware/scripts/_bom_categories.py CATEGORIES, the
// source of truth for the taxonomy. An unknown tag falls back to a prettified
// form, so a category added there still renders (just without a hand-tuned
// label) until it's mirrored here.
const CATEGORY_NAMES = {
  sensors: "Sensors",
  wiring: "Wires & wire connectors",
  plumbing: "Tubes, connectors, adapters & safety",
  "solenoid-valves": "Solenoid valves",
  pumps: "Pumps",
  electronics: "Electronics",
  printed: "FDM printed parts",
  "cut-parts": "SendCutSend cut parts",
  pipes: "Pipes",
  refrigeration: "Refrigeration",
  "water-filter": "Water filter",
  insulation: "Insulation & foam",
  faucet: "Faucet",
  fasteners: "Fasteners",
  consumables: "Fab consumables",
  "funnel-casting": "Funnel casting",
  "ac-mains": "AC-mains hardware",
  carbonation: "Carbonation (sparge stone)",
  "cable-mgmt": "Cable management",
  "vent-filter": "Vent filter",
  welding: "Welding filler",
  "cold-kit": "Cold kit",
};

const TAG_RE = /<!--@([a-z][a-z-]*)-->/;
const MONEY_RE = /\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)/;

function escape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function money(n) {
  return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function prettifyTag(tag) {
  return tag.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// Drop the purchase pack size from a display name — both the parenthetical form
// ("(20-pk)", "(2-pack)", "(bag of 10)") and the inline form (", 100 pc",
// ", 120 pc"). The itemization shows the true per-unit quantity next to the
// name, so the pack size only muddies "×4". ASINs / part numbers in parens
// ("(B0FCF1MGT3)", "(NC)") have no pack word and are left alone; lengths and
// dimensions ("100 ft spool", "10–16 mm", "× 8 mm") aren't pc/pk and survive.
function stripPack(name) {
  return name
    .replace(/\s*\([^()]*\b(?:pk|pack|pcs?|ct|sets?|pieces?|count|bag)\b[^()]*\)/gi, "")
    .replace(/,\s*\d+\s*(?:pc|pcs|pk|pack)\b/gi, "")
    .replace(/\s{2,}/g, " ")
    .replace(/\s*,\s*$/g, "")
    .trim();
}

function parseMoney(cell) {
  const m = cell.match(MONEY_RE);
  return m ? parseFloat(m[1].replace(/,/g, "")) : 0;
}

// A BOM qty cell → a discrete piece count, or null when it's a measure sold by
// length / weight / fraction ("~5 ft", "1/2 roll", "78 g"). The leading integer
// covers "2 (of 10 pk)", "18 (2 bags of 10)", and the [N](ANCHOR) sync markers.
function parseCount(qtyCell) {
  if (!qtyCell) return null;
  if (/[/]|\b(ft|kg|g|m|oz|roll|pair)\b/i.test(qtyCell)) return null;
  const m = qtyCell.match(/^\s*\[?~?\s*(\d+)\b/);
  return m ? parseInt(m[1], 10) : null;
}

// Parse bom.md → { total, rowCount, cats: [{ tag, name, sum, parts:[{ name, qty,
// countable, cost, rawQty, sections }] }] }, sorted by cost descending. Identical
// parts — the same SKU used in more than one subsystem, e.g. the PP010822E
// adapter that appears in §3, §4 and §8 — are AGGREGATED into one line, so the
// itemization shows the true per-unit quantity (×6) and total ($10.44) instead
// of three look-alike $3.48 rows. Row selection mirrors _bom_categories.py; qty
// is the 3rd-last cell and the line cost the last, except §7's printed-parts
// table (Part | Qty | Material | Mass | $) whose qty is the second cell. The
// per-each the VIEW shows is derived as total ÷ quantity — never read from the
// ledger's Unit $ column, so a mis-entered unit can't make the display lie.
export function readCostRollup(hardwareDir) {
  const bomPath = path.join(hardwareDir, "ledger", "bom.md");
  const text = fs.readFileSync(bomPath, "utf-8");
  const byTag = new Map();
  let section = null;
  let rowCount = 0;

  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const m = raw.match(/^## (\d+)\./);
      section = m ? parseInt(m[1], 10) : null;
      continue;
    }
    if (section === null || !raw.startsWith("|")) continue;
    const cells = raw.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    if (!cells.length || cells.every((c) => /^[-:\s]*$/.test(c))) continue; // separator
    const first = cells[0].replace(/\*/g, "").trim().toLowerCase();
    if (first === "part" || first.includes("total")) continue; // header / totals row
    const tm = raw.match(TAG_RE);
    if (!tm) continue; // untagged rows are absent from this category rollup
    const tag = tm[1];
    const cost = parseMoney(cells[cells.length - 1]);
    const name = plainMarkdown(cells[0]);
    const qtyRaw = section === 7 ? (cells[1] || "") : (cells[cells.length - 3] || "");
    const count = parseCount(qtyRaw);
    rowCount += 1;

    if (!byTag.has(tag)) {
      byTag.set(tag, { tag, name: CATEGORY_NAMES[tag] || prettifyTag(tag), sum: 0, parts: new Map() });
    }
    const b = byTag.get(tag);
    b.sum += cost;

    let p = b.parts.get(name);
    if (!p) { p = { name, qty: 0, countable: true, cost: 0, rawQty: qtyRaw, sections: new Set() }; b.parts.set(name, p); }
    p.cost += cost;
    p.sections.add(section);
    if (count === null) p.countable = false;
    else p.qty += count;
  }

  const cats = [...byTag.values()].map((b) => ({
    tag: b.tag,
    name: b.name,
    sum: b.sum,
    parts: [...b.parts.values()].sort((a, b) => b.cost - a.cost),
  })).sort((a, b) => b.sum - a.sum);
  const total = cats.reduce((s, c) => s + c.sum, 0);
  return { total, rowCount, cats };
}

// Parse labor.md → { minutes, rate, opCount, cats: [{ n, name, minutes,
// ops: [{ name, cards, minutes }] }] }, sorted by minutes descending. A row's
// estimate is its last cell, matching _labor_totals.py's parse. The bold inline
// subtotal row is skipped along with headers and separators, so what the page
// shows is always the sum of the operations under it. The hourly rate comes off
// the ledger's own [$100](LABOR_RATE) marker — the view never carries a second
// copy of a number the ledger sets.
export function readLaborRollup(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "labor.md"), "utf-8");
  const rm = text.match(/\[\$([0-9][0-9,]*(?:\.[0-9]+)?)\]\(LABOR_RATE\)/);
  const rate = rm ? parseFloat(rm[1].replace(/,/g, "")) : 0;
  const cats = [];
  let cat = null;

  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const m = raw.match(/^## (\d+)\.\s*(.+?)\s*$/);
      cat = m ? { n: parseInt(m[1], 10), name: m[2], minutes: 0, ops: [] } : null;
      if (cat) cats.push(cat);
      continue;
    }
    if (!cat || !raw.startsWith("|")) continue;
    const cells = raw.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    if (cells.length < 2 || cells.every((c) => /^[-:\s]*$/.test(c))) continue; // separator
    const first = cells[0];
    if (first.toLowerCase() === "operation" || first.startsWith("**")) continue; // header / subtotal
    const m = cells[cells.length - 1].match(/^([0-9][0-9,]*)$/);
    const minutes = m ? parseInt(m[1].replace(/,/g, ""), 10) : 0;
    cat.minutes += minutes;
    // Cards cell is an em-dash when the operation has no card of its own.
    const cards = (cells[1] || "").replace(/^—$/, "");
    cat.ops.push({ name: plainMarkdown(first), cards, minutes });
  }

  const filled = cats.filter((c) => c.ops.length);
  filled.sort((a, b) => b.minutes - a.minutes);
  return {
    minutes: filled.reduce((s, c) => s + c.minutes, 0),
    rate,
    batchSize: Number(text.match(/\[(\d+)\]\(BATCH_SIZE\)/)?.[1]) || null,
    opCount: filled.reduce((s, c) => s + c.ops.length, 0),
    cats: filled,
  };
}

// Cash outlay is the purchase ledger's generated total, including paid orders
// in transit and paid items not received. Planned purchases and owner time are
// excluded. Never substitute zero when the investment data is unavailable.
export function readInvestmentRollup(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "purchases.md"), "utf-8");
  const marker = (name) => {
    const match = text.match(new RegExp(`\\[\\$([0-9][0-9,]*(?:\\.[0-9]{1,2})?)\\]\\(${name}\\)`));
    if (!match) throw new Error(`Missing investment total: ${name}`);
    return Math.round(Number(match[1].replace(/,/g, "")) * 100) / 100;
  };
  const rows = [
    { name: "Parts, tools, equipment, supplies & infrastructure", cost: marker("LEDGER_ACQUIRED_HW") },
    { name: "Paid development services", cost: marker("LEDGER_LABOR") },
    { name: "Paid orders in transit", cost: marker("LEDGER_ON_ORDER") },
    { name: "Paid items not received", cost: marker("LEDGER_MISSING") },
  ];
  const total = marker("LEDGER_GRAND_TOTAL");
  if (Math.abs(rows.reduce((sum, row) => sum + row.cost, 0) - total) > 0.011) {
    throw new Error("Investment totals do not reconcile");
  }
  return { total, rows };
}

// Parse machine-time.md → { print, printWall, printers, unitsYear, turnDays,
// procs: [{ section, name, machine, hours }] }. Hours a MACHINE is busy, which
// is not costed and never reaches the topline — it answers turnaround and
// throughput, not price. The numbered sections carry the process rows (hours in
// the last cell); the derived figures come off the ledger's own docgen markers,
// which hardware/scripts/_machine_time.py writes from bom.md §7's masses.
export function readMachineRollup(hardwareDir) {
  const text = fs.readFileSync(path.join(hardwareDir, "ledger", "machine-time.md"), "utf-8");
  const marker = (name) => {
    const m = text.match(new RegExp(`\\[~?([0-9][0-9,]*(?:\\.[0-9]+)?)[^\\]]*\\]\\(${name}\\)`));
    return m ? parseFloat(m[1].replace(/,/g, "")) : 0;
  };

  const SECTION_LABEL = { 1: "Printing", 2: "Curing & baking", 3: "Soaking & holding", 4: "Running" };
  const procs = [];
  let section = null;
  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const m = raw.match(/^## (\d+)\./);
      section = m ? parseInt(m[1], 10) : null;
      continue;
    }
    if (section === null || !raw.startsWith("|")) continue;
    const cells = raw.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    if (cells.length < 4 || cells.every((c) => /^[-:\s]*$/.test(c))) continue;
    if (cells[0].startsWith("**") || /^(process|group)$/i.test(cells[0])) continue;
    const h = parseFloat(cells[cells.length - 1].replace(/^\[|\]\(\w+\)$/g, ""));
    if (!isFinite(h)) continue;
    // §1 is Group | Parts | Rate | Mass | Hours; §2-4 are Process | Machine |
    // Notes | Hours. The annotation column differs, the last cell does not.
    const note = plainMarkdown(section === 1 ? cells[2] : cells[1]);
    procs.push({ section: SECTION_LABEL[section] || "", name: plainMarkdown(cells[0]), machine: note, hours: h });
  }

  return {
    print: marker("MT_H_PRINT"),
    printWall: marker("MT_H_PRINT_WALL"),
    printers: marker("MT_PRINTERS"),
    unitsYear: marker("MT_UNITS_YEAR"),
    turnDays: marker("MT_DAYS_TURN"),
    procs,
  };
}

// Minutes → "h m" the way a person says it: 45 m, 2 h, 1 h 15 m. Mirrors
// _labor_totals.py's hm(). The ledger's estimates land on a coarse increment
// ladder on purpose; a decimal hour would put back exactly the false precision
// the ladder exists to keep out.
// A whole-dollar rate shows no cents — "$100/h", not "$100.00/h".
function rateStr(r) {
  return r % 1 ? money(r) : "$" + r.toLocaleString("en-US");
}

function hm(min) {
  const h = Math.floor(min / 60);
  const m = min % 60;
  if (!h) return `${m} m`;
  return m ? `${h} h ${m} m` : `${h} h`;
}

const COST_CSS = `
.cost-wrap { max-width: 860px; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; width: 100%; }
.cost-title { font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0 1.25rem; letter-spacing: -0.01em; scroll-margin-top: 5rem; }
.cost-sr-only { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.cost-wrap a:focus-visible, .cost-wrap summary:focus-visible, .cost-wrap input:focus-visible { outline: 2px solid var(--action); outline-offset: 4px; }
.cost-hero {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem 1.5rem;
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 1.25rem 1.5rem; margin-bottom: 0.5rem;
}
.cost-big { font-size: 2.5rem; font-weight: 700; color: var(--accent); line-height: 1; font-variant-numeric: tabular-nums; }
.cost-lbl { font-size: 0.85rem; color: var(--text-2); max-width: 34ch; }
.cost-note { font-size: 0.75rem; color: var(--text-3); margin: 0.75rem 0 2rem; }
.cost-h2 {
  font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-2); font-weight: 600; margin: 2rem 0 1rem;
}
.cost-chart { display: flex; flex-direction: column; gap: 0.5rem; }
/* The money and percent tracks are fixed, so every bar in the chart starts and
   ends on the same two lines and their lengths compare. */
.cost-bar { display: grid; grid-template-columns: minmax(130px, 1.6fr) minmax(70px, 3fr) 4.4rem 3rem; align-items: center; gap: 0.75rem; }
.cost-bl { font-size: 0.82rem; color: var(--text); line-height: 1.25; }
.cost-bt { height: 14px; background: var(--surface-2); border-radius: 4px; overflow: hidden; }
.cost-bf { height: 100%; background: var(--chart-one); border-radius: 4px; min-width: 2px; }
.cost-bv { font-size: 0.8rem; text-align: right; font-variant-numeric: tabular-nums; color: var(--text); }
.cost-bp { font-size: 0.72rem; text-align: right; color: var(--text-2); font-variant-numeric: tabular-nums; }
.cost-cat { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem; overflow: hidden; }
.cost-cat summary {
  cursor: pointer; padding: 0.75rem 1rem; font-size: 0.85rem; font-weight: 600;
  display: flex; justify-content: flex-start; align-items: center; gap: 0.75rem; list-style: none;
}
.cost-cat summary:hover { background: var(--surface-2); }
.cost-cat summary::-webkit-details-marker { display: none; }
.cost-cat summary::after { content: "+"; color: var(--text-2); font-weight: 400; }
.cost-cat[open] summary::after { content: "\\2013"; }
/* The row's own name takes what it needs; the badge takes the rest of the way
   to the marker, so it stands on one line down the whole list. */
.cost-dt { margin-left: auto; font-weight: 400; color: var(--text-2); font-size: 0.78rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
/* Fixed columns, so the qty and the price stand on the same two lines in every
   card rather than on lines each table works out for itself. */
.cost-items { width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 0.78rem; }
.cost-items td.cost-qty { width: 8.5rem; }
.cost-items td.cost-num { width: 5.5rem; }
.cost-items td { padding: 0.45rem 1rem; border-top: 1px solid var(--border); color: var(--text); vertical-align: top; }
/* A part name is one long token as often as it is words. */
.cost-items td:first-child { overflow-wrap: anywhere; }
.cost-items td.cost-qty { text-align: right; white-space: nowrap; color: var(--text-2); font-variant-numeric: tabular-nums; }
.cost-items td.cost-num { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; color: var(--text); }
.cost-ea { color: var(--text-3); }
/* Section markers in the parts table, whole sentences in the labor and machine
   ones — both wrap. */
.cost-secs { color: var(--text-3); font-size: 0.85em; font-variant-numeric: tabular-nums; }
.cost-total { display: flex; justify-content: space-between; align-items: baseline; padding: 0.9rem 1rem; margin-top: 0.75rem; border-top: 2px solid var(--border); font-weight: 700; }
.cost-total .v { color: var(--accent); font-variant-numeric: tabular-nums; }
.cost-total .v2 { color: var(--text-3); font-weight: 400; font-variant-numeric: tabular-nums; margin-left: 0.6rem; }
/* Matching headlines for the planned build cost and the sale price. */
.cost-top {
  position: relative; overflow: hidden;
  border: 1px solid var(--border); border-radius: 16px;
  background:
    radial-gradient(120% 150% at 10% 0%, rgba(220, 230, 255, 0.12), transparent 62%),
    var(--surface);
  padding: 1.9rem 1.75rem 1.5rem; margin: 0.25rem 0 1rem;
}
.cost-top-cap { font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-2); }
.cost-top-big {
  font-size: clamp(2.6rem, 9vw, 4rem); font-weight: 700; line-height: 1.05;
  letter-spacing: -0.025em; font-variant-numeric: tabular-nums;
  margin: 0.35rem 0 1.3rem; color: var(--accent);
}
.cost-split { display: flex; gap: 2px; height: 10px; border-radius: 5px; overflow: hidden; background: var(--surface-2); }
.cost-split i { display: block; height: 100%; }
.cost-split .p { background: var(--chart-one); }
.cost-split .l { background: var(--chart-two); }
.cost-top-legs { display: flex; flex-wrap: wrap; gap: 0.4rem 2rem; margin-top: 0.95rem; }
.cost-top-leg { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: var(--text-2); text-decoration: none; }
.cost-top-leg b { color: var(--text); font-size: 1.05rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.cost-top-leg:hover b { color: var(--accent); }
.cost-key { width: 11px; height: 11px; border-radius: 3px; background: var(--chart-one); flex: none; }
.cost-key.l { background: var(--chart-two); }
.cost-key.r, .cost-split .r { background: var(--chart-three); }
.cost-top-context { font-size: 0.8rem; color: var(--text-2); margin: 1rem 0 0; line-height: 1.6; }
.cost-top-context a, .cost-prose a { color: inherit; text-underline-offset: 3px; }
.cost-price {
  border-color: var(--action);
  background: radial-gradient(120% 150% at 10% 0%, rgba(255, 145, 82, 0.16), transparent 65%), var(--surface);
}
.cost-price .cost-top-cap { color: var(--action); }
.cost-price .cost-top-big { color: var(--action); font-size: clamp(3rem, 12vw, 4.5rem); }
.cost-price .cost-top-big small { font-size: 0.85rem; color: var(--text-2); font-weight: 400; letter-spacing: 0; white-space: nowrap; }
.cost-price .cost-top-big + .cost-top-context { margin: -0.35rem 0 1.25rem; max-width: 68ch; }
.cost-price .cost-top-legs { gap: 0.6rem 1.5rem; }
.cost-recovery { margin: 2.75rem 0 3rem; scroll-margin-top: 5rem; }
.cost-prose { font-size: 0.88rem; line-height: 1.7; color: var(--text-2); margin: 0 0 1.25rem; }
.cost-prose strong { color: var(--text); font-weight: 600; }
.recovery-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem 1.75rem; margin: 1.5rem 0 1rem; }
.recovery-headline { display: flex; flex-wrap: wrap; gap: 0.25rem 0.6rem; align-items: baseline; margin: 0.3rem 0 0.5rem; }
.recovery-headline b { font-size: clamp(2rem, 6vw, 3rem); font-weight: 700; line-height: 1.15; letter-spacing: -0.025em; color: var(--action); font-variant-numeric: tabular-nums; }
.recovery-headline span { font-size: 0.9rem; color: var(--text-2); }
.recovery-summary { margin: 0; font-size: 0.84rem; color: var(--text-2); line-height: 1.65; }
.recovery-figure { margin: 1.75rem 0 0; }
.recovery-axis-title { font-size: 0.72rem; color: var(--text-2); margin-bottom: 0.25rem; }
.recovery-svg { display: block; width: 100%; height: auto; overflow: visible; }
.recovery-axis { fill: var(--text-2); font-family: inherit; font-size: 12px; font-variant-numeric: tabular-nums; }
.recovery-grid { stroke: var(--border); stroke-opacity: 0.28; }
.recovery-band { fill: var(--chart-three); fill-opacity: 0.18; }
.recovery-recorded { stroke: var(--chart-two); stroke-width: 1.5; stroke-dasharray: 3 4; }
.recovery-target { stroke: var(--chart-three); stroke-width: 1.5; stroke-dasharray: 9 5; }
.recovery-line { fill: none; stroke: var(--action); stroke-width: 3; stroke-linecap: round; }
.recovery-milestone { fill: var(--surface); stroke: var(--action); stroke-width: 2; }
.recovery-dot { fill: var(--action); stroke: var(--surface); stroke-width: 3; }
.recovery-cursor { stroke: var(--action); stroke-opacity: 0.55; stroke-dasharray: 3 4; }
.recovery-legend { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; font-size: 0.72rem; color: var(--text-2); margin: 0.5rem 0 1.25rem; }
.recovery-legend span { display: inline-flex; align-items: center; gap: 0.4rem; }
.recovery-legend i { width: 22px; border-top: 3px solid var(--action); }
.recovery-legend .recorded { border-top: 2px dotted var(--chart-two); }
.recovery-legend .target { border-top: 2px dashed var(--chart-three); }
.recovery-readout { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.25rem; padding: 1rem 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.recovery-readout p { margin: 0; font-size: 0.78rem; color: var(--text-2); }
.recovery-readout b { display: block; font-size: 1.3rem; color: var(--text); font-variant-numeric: tabular-nums; margin: 0.2rem 0; }
.recovery-readout .recovery-balance { grid-column: 1 / -1; margin-top: 0.2rem; }
.recovery-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0 0; }
.recovery-controls[hidden] { display: none; }
.recovery-control label { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0.35rem; font-size: 0.8rem; font-weight: 600; }
.recovery-control output { color: var(--action); font-variant-numeric: tabular-nums; white-space: nowrap; }
.recovery-control input { display: block; width: 100%; min-height: 36px; margin: 0.35rem 0; accent-color: var(--action); cursor: pointer; }
.recovery-control p { font-size: 0.73rem; color: var(--text-3); margin: 0; line-height: 1.6; }
.recovery-limit { font-size: 0.76rem; line-height: 1.65; color: var(--text-2); margin: 1.25rem 0 0; }
.cost-explainer { padding: 0 1rem 1rem; font-size: 0.81rem; line-height: 1.7; color: var(--text-2); }
.cost-explainer p { margin: 0.8rem 0 0; }
.cost-explainer strong { color: var(--text); }
.cost-assumptions { scroll-margin-top: 5rem; }
.cost-assumptions .cost-title { margin-top: 2rem; font-size: 1.15rem; }
.cost-assumptions p { font-size: 0.83rem; color: var(--text-2); line-height: 1.75; margin: 0.8rem 0; }
.cost-assumptions strong { color: var(--text); }
.cost-assumptions a { color: var(--text); text-underline-offset: 3px; }
/* Labor — the same ranked chart, scaled by time, priced beside it. */
.cost-rule { border: 0; border-top: 1px solid var(--border); margin: 3.25rem 0 0; }
.cost-bar.lab { grid-template-columns: minmax(130px, 1.6fr) minmax(60px, 3fr) 4.9rem 4.4rem; }
.cost-bar.lab .cost-bf { background: var(--chart-two); }
.cost-hero.lab .cost-big, .cost-total.lab .v { color: var(--chart-two); }
/* Machine time — a third colour because it is a third ledger, and because it
   must not read as money. Two derived figures lead; the processes sit under
   them, grouped the way the ledger groups them. */
.cost-hero.mach .cost-big { color: var(--chart-three); }
.cost-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 0.75rem; margin: 1.25rem 0 0.5rem; }
.cost-stat { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.15rem 1.25rem; }
.cost-statv { font-size: 1.9rem; font-weight: 700; line-height: 1.05; color: var(--chart-three); font-variant-numeric: tabular-nums; }
.cost-cap { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-2); margin-top: 0.2rem; }
.cost-statn { font-size: 0.78rem; color: var(--text-3); margin-top: 0.6rem; line-height: 1.45; }
@media (max-width: 560px) {
  .cost-top { padding: 1.5rem 1.15rem 1.25rem; }
  .recovery-panel { padding: 1.25rem 1rem; }
  .recovery-controls { grid-template-columns: 1fr; gap: 1.25rem; }
  .recovery-axis { font-size: 22px; }
  .recovery-x-label { font-size: 21px; }
  .recovery-readout { gap: 0.6rem; }
  .recovery-readout b { font-size: 1.1rem; }
  .cost-top-leg { flex-wrap: wrap; }
  .cost-bar { grid-template-columns: 1fr 4.4rem 2.75rem; grid-template-areas: "l l l" "t v p"; }
  .cost-bl { grid-area: l; } .cost-bt { grid-area: t; } .cost-bv { grid-area: v; } .cost-bp { grid-area: p; }
  .cost-bar.lab { grid-template-columns: 1fr 4.6rem 4.2rem; }
  /* The name stands on its own row here, so the space between bars has to beat
     the space inside one or the name reads against the bar above it. */
  .cost-chart { gap: 1.5rem; }
  /* The card is the width of a phone here, and the qty column carries a rate
     and a unit as often as a number. */
  .cost-items td.cost-qty { white-space: normal; }
}
`;

// The labor half of the page: the same ranked-bar + itemization shape as the
// parts half, with attended time scaling the bar and the money it comes to
// beside it. The rate is the ledger's.
function renderLaborSection(labor) {
  const { minutes, rate, opCount, cats } = labor;
  const mx = Math.max(...cats.map((c) => c.minutes), 1);
  const cash = (mins) => money((mins / 60) * rate);

  const bars = cats.map((c) => {
    const w = ((c.minutes / mx) * 100).toFixed(1);
    return `<div class="cost-bar lab">
      <div class="cost-bl">${escape(c.name)}</div>
      <div class="cost-bt"><div class="cost-bf" style="width:${w}%"></div></div>
      <div class="cost-bv">${hm(c.minutes)}</div><div class="cost-bp">${cash(c.minutes)}</div>
    </div>`;
  }).join("\n");

  const details = cats.map((c) => {
    const rows = c.ops.map((o) => `<tr>
        <td>${escape(o.name)}${o.cards ? ` <span class="cost-secs">${escape(o.cards)}</span>` : ""}</td>
        <td class="cost-qty">${hm(o.minutes)}</td><td class="cost-num">${cash(o.minutes)}</td>
      </tr>`).join("");
    const n = c.ops.length;
    return `<details class="cost-cat"><summary>${escape(c.name)} <span class="cost-dt">${hm(c.minutes)} &middot; ${cash(c.minutes)} &middot; ${n} op${n === 1 ? "" : "s"}</span></summary>
      <table class="cost-items"><tbody>${rows}</tbody></table></details>`;
  }).join("\n");

  return `<hr class="cost-rule">
  <h2 class="cost-title" id="labor">Labor by category</h2>
  <div class="cost-hero lab">
    <div class="cost-big">${hm(minutes)}</div>
    <div class="cost-lbl">attended time per finished unit &mdash; ${opCount} hand operations across ${cats.length} kinds of work, priced at ${rateStr(rate)} an hour</div>
  </div>
  <p class="cost-note">Planned hands-on time for a repeatable batch build, with an experienced operator and fixtures ready. Our early builds take substantially longer. These operation times are estimates.</p>
  <h3 class="cost-h2">All work, ranked</h3>
  <div class="cost-chart">
${bars}
  </div>
  <h3 class="cost-h2">Every operation</h3>
${details}
  <div class="cost-total lab"><span>Per-unit total</span><span><span class="v">${cash(minutes)}</span><span class="v2">${hm(minutes)}</span></span></div>
`;
}

// Machine time: hours a machine is busy, grouped the way the ledger groups them.
// Deliberately NOT costed and deliberately below the labor total — the two
// derived figures (throughput, turnaround) are the point, so they lead.
function renderMachineSection(mach) {
  const { print, printWall, printers, unitsYear, turnDays, procs } = mach;
  const groups = [...new Set(procs.map((p) => p.section))];

  const details = groups.map((g) => {
    const rows = procs.filter((p) => p.section === g);
    const sum = rows.reduce((s, p) => s + p.hours, 0);
    const body = rows.map((p) => `<tr>
        <td>${escape(p.name)}${p.machine ? ` <span class="cost-secs">${escape(p.machine)}</span>` : ""}</td>
        <td class="cost-num">${hm(Math.round(p.hours * 60))}</td>
      </tr>`).join("");
    return `<details class="cost-cat"><summary>${escape(g)} <span class="cost-dt">${hm(Math.round(sum * 60))} &middot; ${rows.length} process${rows.length === 1 ? "" : "es"}</span></summary>
      <table class="cost-items"><tbody>${body}</tbody></table></details>`;
  }).join("\n");

  return `<hr class="cost-rule">
  <h2 class="cost-title" id="machine">Machine time</h2>
  <div class="cost-hero mach">
    <div class="cost-big">${hm(Math.round(print * 60))}</div>
    <div class="cost-lbl">printer time per finished unit &mdash; ${hm(Math.round(printWall * 60))} of wall clock across ${printers} H2Cs, and the longest pole in the build by an order of magnitude</div>
  </div>
  <p class="cost-note"><strong>Not in the total above.</strong> These are the hours a machine is busy and nobody is on it, which is what turnaround and throughput are read off &mdash; not what a unit is worth. The attended minutes are the labor section; the two ledgers share no rows.</p>
  <div class="cost-stats">
    <div class="cost-stat">
      <div class="cost-statv">~${unitsYear.toLocaleString("en-US")}</div><div class="cost-cap">units a year</div>
      <div class="cost-statn">At 65&nbsp;% printer duty. The printers are the constraint and nothing else is within an order of magnitude &mdash; a third H2C is the only purchase that moves this number.</div>
    </div>
    <div class="cost-stat">
      <div class="cost-statv">${turnDays} days</div><div class="cost-cap">turnaround, one unit</div>
      <div class="cost-statn">Cold start to packed carton, with everything that can overlap the print doing so. A second unit behind the first costs only the bottleneck&rsquo;s ${hm(Math.round(printWall * 60))}.</div>
    </div>
  </div>
  <h3 class="cost-h2">Every process a machine owns</h3>
${details}
`;
}

// The estimated build cost combines the parts and labor ledgers below the price.
function renderTopline(total, labor) {
  const labour = (labor.minutes / 60) * labor.rate;
  const all = total + labour;
  const pp = (total / all) * 100;
  return `<section class="cost-top" aria-label="Estimated build cost">
    <div class="cost-top-cap">Estimated cost per unit</div>
    <div class="cost-top-big">${money(all)}</div>
    <div class="cost-split"><i class="p" style="width:${pp.toFixed(1)}%"></i><i class="l" style="width:${(100 - pp).toFixed(1)}%"></i></div>
    <div class="cost-top-legs">
      <a class="cost-top-leg" href="#parts"><i class="cost-key"></i>Parts <b>${money(total)}</b></a>
      <a class="cost-top-leg" href="#labor"><i class="cost-key l"></i>Labor <b>${money(labour)}</b> ${hm(labor.minutes)} at ${rateStr(labor.rate)}/h</a>
    </div>
    <p class="cost-top-context">Parts plus planned batch labor. Our early builds take substantially longer. <a href="#assumptions">What we&rsquo;re assuming</a></p>
  </section>
`;
}

function renderPrice(unitCost) {
  const contribution = unitCost === null ? null : SALE_PRICE - unitCost;
  const costShare = unitCost === null ? 0 : Math.min(100, unitCost / SALE_PRICE * 100);
  return `<section class="cost-top cost-price" aria-label="Planned sale price">
    <div class="cost-top-cap">Planned sale price</div>
    <div class="cost-top-big">${dollars(SALE_PRICE, 0)} <small>per machine</small></div>
    <p class="cost-top-context">The price covers the planned cost of building your machine and helps pay back what we&rsquo;ve put into developing it.</p>
    ${contribution === null ? `<p class="cost-top-context">The build cost estimate is currently incomplete.</p>` : `
    <div class="cost-split" aria-hidden="true"><i class="l" style="width:${costShare.toFixed(1)}%"></i><i class="r" style="width:${(100 - costShare).toFixed(1)}%"></i></div>
    <div class="cost-top-legs">
      <a class="cost-top-leg" href="#parts"><i class="cost-key l"></i>Build cost <b>${money(unitCost)}</b></a>
      <a class="cost-top-leg" href="#recovery"><i class="cost-key r"></i>Toward investment <b>${money(contribution)}</b></a>
    </div>
    <p class="cost-top-context">The amount toward investment is before the selling and support costs we still need to budget.</p>`}
  </section>`;
}

function renderRecovery(unitCost, labor, investment) {
  if (unitCost === null || !investment) {
    return `<section class="cost-recovery"><h2 class="cost-title" id="recovery">Paying back the investment</h2><p class="cost-prose">Recovery estimates are unavailable while cost or investment figures are incomplete.</p></section>`;
  }
  const plan = recoveryPlan({ unitCost, investment: investment.total });
  const investmentRows = investment.rows.map((row) => `<tr><td>${escape(row.name)}</td><td class="cost-num">${money(row.cost)}</td></tr>`).join("");
  return `<section class="cost-recovery" id="recovery" aria-labelledby="recovery-heading"
      data-unit-cost="${unitCost}" data-investment="${investment.total}">
    <h2 class="cost-title" id="recovery-heading">Paying back the investment</h2>
    <p class="cost-prose">We have <strong>${money(investment.total)}</strong> in recorded cash outlay: parts, prototypes, tools, equipment, supplies and paid development work.${plan.target > plan.investment ? ` The shaded range extends to <strong>${dollars(plan.target, 0)}</strong> to allow for further potential investment.` : ""} Our own development time is additional and unpriced.</p>
    <details class="cost-cat">
      <summary>What&rsquo;s in the investment? <span class="cost-dt">${money(investment.total)}</span></summary>
      <table class="cost-items"><caption class="cost-sr-only">Recorded investment by purchase status</caption><tbody>${investmentRows}</tbody></table>
      <div class="cost-explainer"><p>Cash recorded in our 2026 purchase ledger, including equipment and inventory we still own. This is the amount we are aiming to earn back while continuing to fund the parts and labor for each machine.</p></div>
    </details>
    <div class="recovery-panel">
      <div class="cost-top-cap">Machines to recover the investment</div>
      <div class="recovery-headline"><b data-recovery="range">${recoveryRange(plan)}</b><span data-recovery="unit-label">${plan.recordedUnits === null ? "at this per-machine cost" : "machines"}</span></div>
      <p class="recovery-summary" data-recovery="summary" aria-live="polite">${recoverySummary(plan)}</p>
      <figure class="recovery-figure">
        <div class="recovery-axis-title">Cumulative money available toward investment</div>
        <div data-recovery="chart">${renderRecoveryChart(plan)}</div>
        <figcaption class="recovery-legend">
          <span><i></i>After per-machine costs</span>
          <span><i class="recorded"></i>${dollars(plan.investment, 0)} recorded</span>
          ${plan.target > plan.investment ? `<span><i class="target"></i>${dollars(plan.target, 0)} scenario</span>` : ""}
        </figcaption>
      </figure>
      <div class="recovery-readout">
        <p>Per machine<b data-recovery="contribution">${money(plan.contribution)}</b>toward investment</p>
        <p>At <span data-recovery="sold">${plan.units} machines</span><b data-recovery="available">${dollars(plan.available, 0)}</b>available toward investment</p>
        <p class="recovery-balance" data-recovery="balance">${salesBalance(plan)}</p>
      </div>
      <div class="recovery-controls" hidden>
        <div class="recovery-control">
          <label for="sales-units">Machines sold <output for="sales-units" data-recovery="units">${plan.units}</output></label>
          <input id="sales-units" type="range" min="0" max="${SALES_HORIZON}" step="1" value="${plan.units}" aria-describedby="sales-help">
          <p id="sales-help">Explore 0&ndash;${SALES_HORIZON} paid sales at ${dollars(SALE_PRICE, 0)} each. This is a scenario; sales timing is not forecast.</p>
        </div>
        <div class="recovery-control">
          <label for="machine-cost">Per machine cost <output for="machine-cost" data-recovery="machine-cost">${money(unitCost)}</output></label>
          <input id="machine-cost" type="range" min="${unitCost}" max="${Math.max(unitCost + 2500, SALE_PRICE)}" step="50" value="${unitCost}" aria-valuetext="${money(unitCost)} per machine" aria-describedby="cost-help">
          <p id="cost-help">Starts at ${money(unitCost)} for parts and planned labor. Increase this total to allow for other per-machine costs.</p>
        </div>
      </div>
      <p class="recovery-limit">Available toward investment = machines sold &times; (${dollars(SALE_PRICE, 0)} &minus; per-machine cost). Selling costs, support, overhead and taxes still have to come out of this money unless included in the cost you select.</p>
    </div>
    <div class="cost-assumptions" id="assumptions">
      <h3 class="cost-title">Where the estimates need care</h3>
      <p><strong>The build cost is an estimate.</strong> The <a href="#labor">${hm(labor.minutes)} labor allowance</a> assumes a practiced operator, fixtures ready${labor.batchSize ? ` and a batch of ${labor.batchSize} machines` : " and machines built in batches"}. We&rsquo;re still developing that process. The per-machine cost slider lets you explore a larger allowance for making and supporting each machine.</p>
      <p><strong>The investment is recorded cash.</strong> It includes paid development services, but puts no dollar value on our own design, software, testing or process-development time. The calculation sets aside the full parts cost on every sale to replenish inventory, including parts we have already bought.</p>
      <p><strong>There are costs still to budget.</strong> Payment fees, delivery or installation, warranty and support, ongoing overhead, further development and taxes are not included in the per-unit estimate. These reduce the money available to repay the investment and can push recovery further out. Passing the line on this chart does not mean all of that money is profit.</p>
    </div>
  </section>`;
}

function renderCostBody(rollup, labor, mach, investment) {
  const { total, rowCount, cats } = rollup;
  const mx = Math.max(...cats.map((c) => c.sum), 1);
  const unitCost = labor && labor.rate > 0 && labor.opCount > 0
    ? Math.round((total + (labor.minutes / 60) * labor.rate) * 100) / 100 : null;

  const bars = cats.map((c) => {
    const w = ((c.sum / mx) * 100).toFixed(1);
    const pct = ((c.sum / total) * 100).toFixed(1);
    return `<div class="cost-bar">
      <div class="cost-bl">${escape(c.name)}</div>
      <div class="cost-bt"><div class="cost-bf" style="width:${w}%"></div></div>
      <div class="cost-bv">${money(c.sum)}</div><div class="cost-bp">${pct}%</div>
    </div>`;
  }).join("\n");

  const details = cats.map((c) => {
    const rows = c.parts.map((p) => {
      let qty;
      if (p.countable) {
        qty = "&times;" + p.qty;
        if (p.qty > 1) {
          const each = Math.round((p.cost / p.qty) * 100) / 100;
          // Per-each is total ÷ qty — never the ledger's Unit $ column, which
          // can be mis-entered. Amortized pack-fraction costs don't always
          // divide to the cent, so mark those "~" rather than hiding the
          // per-each (which left multi-qty rows looking like they were missing
          // one). Skip only a per-each that would round to $0.00.
          if (each >= 0.01) {
            const approx = Math.abs(each * p.qty - p.cost) >= 0.005;
            qty += ` <span class="cost-ea">@ ${approx ? "~" : ""}${money(each)}</span>`;
          }
        }
      } else {
        qty = escape(plainMarkdown(p.rawQty || ""));
      }
      const secs = p.sections.size > 1
        ? ` <span class="cost-secs">§${[...p.sections].sort((a, b) => a - b).join(",")}</span>`
        : "";
      return `<tr><td>${escape(stripPack(p.name))}${secs}</td><td class="cost-qty">${qty}</td><td class="cost-num">${money(p.cost)}</td></tr>`;
    }).join("");
    const n = c.parts.length;
    return `<details class="cost-cat"><summary>${escape(c.name)} <span class="cost-dt">${money(c.sum)} &middot; ${n} part${n === 1 ? "" : "s"}</span></summary>
      <table class="cost-items"><tbody>${rows}</tbody></table></details>`;
  }).join("\n");

  return `<main class="cost-wrap">
  <h1 class="cost-sr-only">Price, cost &amp; investment</h1>
${renderPrice(unitCost)}
${unitCost !== null ? renderTopline(total, labor) : ""}
${renderRecovery(unitCost, labor, investment)}
  <h2 class="cost-title" id="parts">Parts by category</h2>
  <div class="cost-hero">
    <div class="cost-big">${money(total)}</div>
    <div class="cost-lbl">delivered cost per finished unit &mdash; ${rowCount} ledger lines across ${cats.length} part-type categories, amortized per unit</div>
  </div>
  <p class="cost-note">Parts are priced from our purchase records, including shipping and tax; parts not yet purchased use estimated prices. Packs are divided across the machines they supply. Repeated parts are combined into one line, with ~ marking a rounded per-piece price. Expand any category below to see every part.</p>
  <h3 class="cost-h2">All categories, ranked</h3>
  <div class="cost-chart">
${bars}
  </div>
  <h3 class="cost-h2">Full itemization</h3>
${details}
  <div class="cost-total"><span>Per-unit total</span><span class="v">${money(total)}</span></div>
${labor ? renderLaborSection(labor) : ""}${mach ? renderMachineSection(mach) : ""}</main>
<script type="module" src="/cost.js"></script>
`;
}

export function mountCostRoutes(app, { hardwareDir }) {
  app.get("/cost", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    let body;
    // Labor is optional: a checkout without labor.md renders the parts half
    // alone rather than losing the page.
    let labor = null;
    let mach = null;
    let investment = null;
    try {
      labor = readLaborRollup(hardwareDir);
    } catch (e) { /* no labor.md */ }
    try {
      mach = readMachineRollup(hardwareDir);
    } catch (e) { /* no machine-time.md */ }
    try {
      investment = readInvestmentRollup(hardwareDir);
    } catch (e) { /* missing or inconsistent purchase totals */ }
    try {
      body = renderCostBody(readCostRollup(hardwareDir), labor, mach, investment);
    } catch (e) {
      // A stripped checkout (no bom.md) shouldn't 500 — render an empty state.
      body = `<main class="cost-wrap"><h1 class="cost-title">Cost &amp; price</h1>${renderPrice(null)}<p class="cost-note">Cost data unavailable.</p></main>`;
    }
    res.send(
      renderHead({ title: "Price & Cost · Home Soda Machine", pageStyles: COST_CSS }) +
      renderNav({ active: "cost" }) +
      body +
      renderFooter(),
    );
  });
}
