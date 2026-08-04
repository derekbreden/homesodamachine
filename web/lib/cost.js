// /cost — what one finished unit costs, in parts and in hours.
//
// Two rollups, two ledgers:
//   * PARTS — hardware/ledger/bom.md, keyed by the hidden <!--@TAG--> category
//     marker and the line cost on each data row (the same tags hardware/scripts/
//     _bom_categories.py owns and the pre-commit gate enforces).
//   * LABOR — hardware/ledger/labor.md, keyed by section, carrying an
//     attended-minute estimate per operation and the hourly rate they're priced
//     at. Section subtotals there are written by hardware/scripts/
//     _labor_totals.py; this view sums the operation rows itself rather than
//     reading those, so the page can't inherit a stale total.
// The two are added together once, in the topline, and server-render into a
// themed page inside the shared shell.
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
    if (!tm) continue; // untagged — shouldn't happen (pre-commit enforces coverage)
    const tag = tm[1];
    const cost = parseMoney(cells[cells.length - 1]);
    // Part-name cell for display: drop the markdown link target + brackets.
    const name = cells[0].replace(/\]\([^)]*\)/g, "]").replace(/[[\]]/g, "");
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
    cat.ops.push({ name: first, cards, minutes });
  }

  const filled = cats.filter((c) => c.ops.length);
  filled.sort((a, b) => b.minutes - a.minutes);
  return {
    minutes: filled.reduce((s, c) => s + c.minutes, 0),
    rate,
    opCount: filled.reduce((s, c) => s + c.ops.length, 0),
    cats: filled,
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
.cost-items td { padding: 0.45rem 1rem; border-top: 1px solid var(--border); color: var(--text); vertical-align: top; }
.cost-items td.cost-qty { text-align: right; white-space: nowrap; color: var(--text-2); font-variant-numeric: tabular-nums; }
.cost-items td.cost-num { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; color: var(--text); }
.cost-ea { color: var(--text-3); }
.cost-secs { color: var(--text-3); font-size: 0.85em; font-variant-numeric: tabular-nums; white-space: nowrap; }
.cost-total { display: flex; justify-content: space-between; align-items: baseline; padding: 0.9rem 1rem; margin-top: 0.75rem; border-top: 2px solid var(--border); font-weight: 700; }
.cost-total .v { color: var(--accent); font-variant-numeric: tabular-nums; }
.cost-total .v2 { color: var(--text-3); font-weight: 400; font-variant-numeric: tabular-nums; margin-left: 0.6rem; }
/* The topline — the one figure the page exists to state. Parts and labor are
   two ledgers; this is the only place they are added together, so it gets the
   weight: a gradient wash across both accents, the split bar in the same two
   colours, and each half linking down to the section that derives it. */
.cost-top {
  position: relative; overflow: hidden;
  border: 1px solid var(--border); border-radius: 16px;
  background:
    radial-gradient(120% 150% at 10% 0%, rgba(68, 136, 255, 0.22), transparent 62%),
    radial-gradient(120% 150% at 95% 100%, rgba(153, 76, 230, 0.20), transparent 60%),
    var(--surface);
  padding: 1.9rem 1.75rem 1.5rem; margin: 0.25rem 0 2.75rem;
}
.cost-top-cap { font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-2); }
.cost-top-big {
  font-size: clamp(2.6rem, 9vw, 4rem); font-weight: 700; line-height: 1.05;
  letter-spacing: -0.025em; font-variant-numeric: tabular-nums;
  margin: 0.35rem 0 1.3rem; color: var(--accent);
}
@supports (-webkit-background-clip: text) or (background-clip: text) {
  .cost-top-big {
    background: linear-gradient(96deg, var(--accent) 15%, var(--chart-purple));
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
}
.cost-split { display: flex; gap: 2px; height: 10px; border-radius: 5px; overflow: hidden; background: var(--surface-2); }
.cost-split i { display: block; height: 100%; }
.cost-split .p { background: var(--accent); }
.cost-split .l { background: var(--chart-purple); }
.cost-top-legs { display: flex; flex-wrap: wrap; gap: 0.4rem 2rem; margin-top: 0.95rem; }
.cost-top-leg { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: var(--text-2); text-decoration: none; }
.cost-top-leg b { color: var(--text); font-size: 1.05rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.cost-top-leg:hover b { color: var(--accent); }
.cost-key { width: 11px; height: 11px; border-radius: 3px; background: var(--accent); flex: none; }
.cost-key.l { background: var(--chart-purple); }
/* Labor — the same ranked chart, scaled by time, priced beside it. */
.cost-rule { border: 0; border-top: 1px solid var(--border); margin: 3.25rem 0 0; }
.cost-bar.lab { grid-template-columns: minmax(130px, 1.6fr) minmax(60px, 3fr) 4.9rem 4.4rem; }
.cost-bar.lab .cost-bf { background: var(--chart-purple); }
.cost-hero.lab .cost-big, .cost-total.lab .v { color: var(--chart-purple); }
.cost-items th {
  padding: 0.4rem 1rem 0.15rem; border-top: 1px solid var(--border); font-weight: 500;
  font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-3);
}
@media (max-width: 560px) {
  .cost-top { padding: 1.5rem 1.15rem 1.25rem; }
  .cost-bar { grid-template-columns: 1fr auto 2.75rem; grid-template-areas: "l l l" "t v p"; }
  .cost-bl { grid-area: l; } .cost-bt { grid-area: t; } .cost-bv { grid-area: v; } .cost-bp { grid-area: p; }
  .cost-bar.lab { grid-template-columns: 1fr 4.6rem 4.2rem; }
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
        <td class="cost-num">${hm(o.minutes)}</td><td class="cost-qty">${cash(o.minutes)}</td>
      </tr>`).join("");
    const n = c.ops.length;
    return `<details class="cost-cat"><summary>${escape(c.name)} <span class="cost-dt">${hm(c.minutes)} &middot; ${cash(c.minutes)} &middot; ${n} op${n === 1 ? "" : "s"}</span></summary>
      <table class="cost-items"><tbody>${rows}</tbody></table></details>`;
  }).join("\n");

  return `<hr class="cost-rule">
  <h1 class="cost-title" id="labor">Labor by category</h1>
  <div class="cost-hero lab">
    <div class="cost-big">${hm(minutes)}</div>
    <div class="cost-lbl">attended time per finished unit &mdash; ${opCount} hand operations across ${cats.length} kinds of work, priced at ${rateStr(rate)} an hour</div>
  </div>
  <h2 class="cost-h2">All work, ranked</h2>
  <div class="cost-chart">
${bars}
  </div>
  <h2 class="cost-h2">Every operation</h2>
${details}
  <div class="cost-total lab"><span>Per-unit total</span><span><span class="v">${cash(minutes)}</span><span class="v2">${hm(minutes)}</span></span></div>
`;
}

// The topline: the only place the two ledgers are added together, and the first
// thing on the page.
function renderTopline(total, labor) {
  const labour = (labor.minutes / 60) * labor.rate;
  const all = total + labour;
  const pp = (total / all) * 100;
  return `<section class="cost-top">
    <div class="cost-top-cap">Total cost per unit</div>
    <div class="cost-top-big">${money(all)}</div>
    <div class="cost-split"><i class="p" style="width:${pp.toFixed(1)}%"></i><i class="l" style="width:${(100 - pp).toFixed(1)}%"></i></div>
    <div class="cost-top-legs">
      <a class="cost-top-leg" href="#parts"><i class="cost-key"></i>Parts <b>${money(total)}</b></a>
      <a class="cost-top-leg" href="#labor"><i class="cost-key l"></i>Labor <b>${money(labour)}</b> ${hm(labor.minutes)} at ${rateStr(labor.rate)}/h</a>
    </div>
  </section>
`;
}

function renderCostBody(rollup, labor) {
  const { total, rowCount, cats } = rollup;
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
        qty = escape(p.rawQty || "");
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
${labor ? renderTopline(total, labor) : ""}  <h1 class="cost-title" id="parts">Parts by category</h1>
  <div class="cost-hero">
    <div class="cost-big">${money(total)}</div>
    <div class="cost-lbl">delivered cost per finished unit &mdash; ${rowCount} ledger lines across ${cats.length} part-type categories, amortized per unit</div>
  </div>
  <p class="cost-note">Every BOM row carries a hidden category tag; this view rolls the ledger up by that tag and stays true to it. Identical parts used across subsystems are combined into one line with the true per-unit quantity; the per-each is amortized from the purchase pack, with ~ where it doesn&rsquo;t divide evenly to the cent. Ranked by per-unit cost.</p>
  <h2 class="cost-h2">All categories, ranked</h2>
  <div class="cost-chart">
${bars}
  </div>
  <h2 class="cost-h2">Full itemization</h2>
${details}
  <div class="cost-total"><span>Per-unit total</span><span class="v">${money(total)}</span></div>
${labor ? renderLaborSection(labor) : ""}</main>
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
    try {
      labor = readLaborRollup(hardwareDir);
    } catch (e) { /* no labor.md */ }
    try {
      body = renderCostBody(readCostRollup(hardwareDir), labor);
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
