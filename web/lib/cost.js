// /cost — per-unit BOM cost broken down by part-type category.
//
// Reads hardware/ledger/bom.md, extracts the hidden <!--@TAG--> category marker
// and the line cost from each data row (the same tags hardware/scripts/
// _bom_categories.py owns and the pre-commit gate enforces), rolls them up by
// category, and server-renders a themed page inside the shared shell.
//
// Dev-gated in the public nav like the other engineering surfaces — see
// shell.js renderNav / BASE_CSS (a[data-nav="cost"]). The route itself always
// responds; it's the nav icon that's hidden unless html.dev-mode.

import path from "path";
import fs from "fs";
import { renderHead, renderNav, renderFooter } from "./shell.js";

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
  "funnel-casting": "Flavor-funnel casting",
  "ac-mains": "AC-mains hardware",
  carbonation: "Carbonation (sparge stone)",
  "cable-mgmt": "Cable management",
  "vent-filter": "Vent filter",
  welding: "Welding filler",
  "install-tool": "Install-kit tool",
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

// Parse bom.md → { total, itemCount, cats: [{ tag, name, sum, count, items:[{section,cost,name}] }] }
// sorted by cost descending. Mirrors the row-selection logic in
// _bom_categories.py (numbered sections only; header / separator / totals rows
// skipped; category tag + last-cell cost per row).
export function readCostRollup(hardwareDir) {
  const bomPath = path.join(hardwareDir, "ledger", "bom.md");
  const text = fs.readFileSync(bomPath, "utf-8");
  const byTag = new Map();
  let section = null;

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
    if (!tm) continue; // untagged — shouldn't happen (pre-commit enforces coverage)
    const tag = tm[1];
    const mm = cells[cells.length - 1].match(MONEY_RE);
    const cost = mm ? parseFloat(mm[1].replace(/,/g, "")) : 0;
    // Part-name cell for display: drop the markdown link target + brackets.
    const name = cells[0].replace(/\]\([^)]*\)/g, "]").replace(/[[\]]/g, "");

    if (!byTag.has(tag)) {
      byTag.set(tag, { tag, name: CATEGORY_NAMES[tag] || prettifyTag(tag), sum: 0, count: 0, items: [] });
    }
    const b = byTag.get(tag);
    b.sum += cost;
    b.count += 1;
    b.items.push({ section, cost, name });
  }

  const cats = [...byTag.values()].sort((a, b) => b.sum - a.sum);
  for (const c of cats) c.items.sort((a, b) => b.cost - a.cost);
  const total = cats.reduce((s, c) => s + c.sum, 0);
  const itemCount = cats.reduce((s, c) => s + c.count, 0);
  return { total, itemCount, cats };
}

const COST_CSS = `
.cost-wrap { max-width: 860px; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; width: 100%; }
.cost-title { font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0 1.25rem; letter-spacing: -0.01em; }
.cost-hero {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem 1.5rem;
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 1.25rem 1.5rem; margin-bottom: 0.5rem;
}
.cost-big { font-size: 2.5rem; font-weight: 700; color: var(--accent); line-height: 1; font-variant-numeric: tabular-nums; }
.cost-lbl { font-size: 0.85rem; color: var(--text-2); max-width: 34ch; }
.cost-note { font-size: 0.75rem; color: var(--text-3); margin: 0.75rem 2px 2rem; }
.cost-h2 {
  font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-2); font-weight: 600; margin: 2rem 0 1rem;
}
.cost-chart { display: flex; flex-direction: column; gap: 0.5rem; }
.cost-bar { display: grid; grid-template-columns: minmax(130px, 1.6fr) minmax(70px, 3fr) auto 3rem; align-items: center; gap: 0.75rem; }
.cost-bl { font-size: 0.82rem; color: var(--text); line-height: 1.25; }
.cost-bt { height: 14px; background: var(--surface-2); border-radius: 4px; overflow: hidden; }
.cost-bf { height: 100%; background: var(--accent); border-radius: 4px; min-width: 2px; }
.cost-bv { font-size: 0.8rem; text-align: right; font-variant-numeric: tabular-nums; color: var(--text); }
.cost-bp { font-size: 0.72rem; text-align: right; color: var(--text-2); font-variant-numeric: tabular-nums; }
.cost-cat { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem; overflow: hidden; }
.cost-cat summary {
  cursor: pointer; padding: 0.75rem 1rem; font-size: 0.85rem; font-weight: 600;
  display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; list-style: none;
}
.cost-cat summary::-webkit-details-marker { display: none; }
.cost-cat summary::after { content: "+"; color: var(--text-2); font-weight: 400; }
.cost-cat[open] summary::after { content: "\\2013"; }
.cost-dt { font-weight: 400; color: var(--text-2); font-size: 0.78rem; font-variant-numeric: tabular-nums; }
.cost-items { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.cost-items td { padding: 0.4rem 1rem; border-top: 1px solid var(--border); color: var(--text-2); }
.cost-items td:nth-child(2) { color: var(--text); }
.cost-sec { color: var(--text-3); white-space: nowrap; }
.cost-num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.cost-total { display: flex; justify-content: space-between; align-items: baseline; padding: 0.9rem 1rem; margin-top: 0.75rem; border-top: 2px solid var(--border); font-weight: 700; }
.cost-total .v { color: var(--accent); font-variant-numeric: tabular-nums; }
@media (max-width: 560px) {
  .cost-bar { grid-template-columns: 1fr auto 2.75rem; grid-template-areas: "l l l" "t v p"; }
  .cost-bl { grid-area: l; } .cost-bt { grid-area: t; } .cost-bv { grid-area: v; } .cost-bp { grid-area: p; }
}
`;

function renderCostBody(rollup) {
  const { total, itemCount, cats } = rollup;
  const mx = Math.max(...cats.map((c) => c.sum), 1);

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
    const rows = c.items.map((it) =>
      `<tr><td class="cost-sec">&sect;${it.section}</td><td>${escape(it.name)}</td><td class="cost-num">${money(it.cost)}</td></tr>`
    ).join("");
    return `<details class="cost-cat"><summary>${escape(c.name)} <span class="cost-dt">${money(c.sum)} &middot; ${c.count}</span></summary>
      <table class="cost-items"><tbody>${rows}</tbody></table></details>`;
  }).join("\n");

  return `<main class="cost-wrap">
  <h1 class="cost-title">Cost by category</h1>
  <div class="cost-hero">
    <div class="cost-big">${money(total)}</div>
    <div class="cost-lbl">delivered cost per finished unit &mdash; ${itemCount} line items across ${cats.length} part-type categories, amortized per unit</div>
  </div>
  <p class="cost-note">Every BOM row carries a hidden category tag; this view rolls the ledger up by that tag and stays true to it. Ranked by per-unit cost.</p>
  <h2 class="cost-h2">All categories, ranked</h2>
  <div class="cost-chart">
${bars}
  </div>
  <h2 class="cost-h2">Full itemization</h2>
${details}
  <div class="cost-total"><span>Per-unit total</span><span class="v">${money(total)}</span></div>
</main>
`;
}

export function mountCostRoutes(app, { hardwareDir }) {
  app.get("/cost", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    let body;
    try {
      body = renderCostBody(readCostRollup(hardwareDir));
    } catch (e) {
      // A stripped checkout (no bom.md) shouldn't 500 — render an empty state.
      body = `<main class="cost-wrap"><h1 class="cost-title">Cost by category</h1><p class="cost-note">Cost data unavailable.</p></main>`;
    }
    res.send(
      renderHead({ title: "Cost · Home Soda Machine", pageStyles: COST_CSS }) +
      renderNav({ surface: "dev", active: "cost" }) +
      body +
      renderFooter(),
    );
  });
}
