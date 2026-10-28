// The /cost page's part-number tree: the finished unit's cost through its BOM,
// each level ranked by cost, with the work and supplies an assembly carries
// itself beneath its contents. Bars share the unit's scale, so lengths compare
// at every depth; each name opens the part in the explorer.
import { bomItems, materialIndex } from "../contracts/materials.js";
import { rollupCost, laborUsd, money, duration, COST_KINDS } from "../contracts/part-costs.js";

function escape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const explorerHref = (id) => `/3d#material:${encodeURIComponent(id)}?panel=materials`;
const width = (part, whole) => whole > 0 ? (Math.max(0, part) / whole * 100).toFixed(2) : "0";

export function renderPartCostTree(catalog) {
  const costs = catalog?.costs;
  if (!costs) return "";
  const index = materialIndex(catalog), memo = new Map();
  const roll = (id) => rollupCost(catalog, id, costs.options, memo);
  const unit = roll(costs.root);
  const share = (usd) => `${(usd / unit.usd * 100).toFixed(1)}%`;
  const bar = (parts, labor) => `<span class="cost-split" aria-hidden="true"><i class="p" style="width:${width(parts, unit.usd)}%"></i><i class="l" style="width:${width(labor, unit.usd)}%"></i></span>`;

  function row({ depth, name, meta, parts, labor, costed = true, branch = false }) {
    const usd = parts + labor;
    return `<span class="cost-node-row" style="--depth:${depth}"${branch ? "" : ' data-leaf=""'}>
      <span class="cost-node-name">${name}${meta ? `<small>${meta}</small>` : ""}</span>
      <span class="cost-node-bar">${costed ? bar(parts, labor) : ""}</span>
      <span class="cost-node-value">${costed ? money(usd) : "—"}</span>
      <span class="cost-node-share">${costed ? share(usd) : ""}</span>
    </span>`;
  }

  // What an assembly carries itself, one row per kind, after its contents.
  function own(id, depth, pieces) {
    const elements = costs.direct[id]?.elements || [];
    return COST_KINDS.map((kind) => {
      const list = elements.filter((element) => element.kind === kind.id);
      if (!list.length) return "";
      const parts = list.reduce((sum, element) => sum + (element.usd || 0), 0) * pieces;
      const minutes = list.reduce((sum, element) => sum + (element.minutes || 0), 0) * pieces;
      const label = kind.id === "labor" ? "Labor on this assembly" : kind.id === "unallocated" ? kind.label : `${kind.label} for this assembly`;
      const meta = kind.id === "labor" ? `${list.length} operation${list.length === 1 ? "" : "s"} · ${duration(minutes)}`
        : list.length === 1 ? escape(list[0].label) : `${list.length} ledger lines${minutes ? " · " + duration(minutes) : ""}`;
      return `<div class="cost-node cost-node-own">${row({ depth, name: `<span>${label}</span>`, meta, parts, labor: laborUsd(catalog, minutes) })}</div>`;
    }).join("");
  }

  function node(id, depth, quantity, seen) {
    const material = index.get(id);
    const cost = roll(id);
    const items = seen.has(id) ? [] : bomItems(material, costs.options).filter((item) => typeof item.quantity === "number");
    const name = `<a href="${explorerHref(id)}">${escape(material.description)}</a>`;
    const meta = `${id}${quantity !== 1 ? ` · ×${+quantity.toFixed(3)}` : ""}`;
    const head = row({ depth, name, meta, parts: quantity * cost.parts, labor: quantity * cost.labor, costed: cost.costed, branch: items.length > 0 });
    if (!items.length) return `<div class="cost-node">${head}</div>`;
    const next = new Set([...seen, id]);
    const children = items
      .map((item) => ({ item, usd: item.quantity * roll(item.material).usd }))
      .sort((a, b) => b.usd - a.usd)
      .map(({ item }) => node(item.material, depth + 1, quantity * item.quantity, next))
      .join("");
    return `<details class="cost-node"${depth === 0 ? " open" : ""}><summary>${head}</summary>${children}${own(id, depth + 1, quantity)}</details>`;
  }

  const parts = Object.keys(costs.direct).length;
  return `
  <h2 class="cost-title" id="by-part">Cost by part</h2>
  <p class="cost-note">Every delivered dollar and attended minute in the two ledgers, on the part number it buys, makes or puts together: ${parts} part number${parts === 1 ? " carries" : "s carry"} cost of their own, and each assembly adds the work and supplies of putting it together. Each name opens that part in the explorer.</p>
  <div class="cost-tree">${node(costs.root, 0, 1, new Set())}</div>`;
}

export const PART_COST_CSS = `
.cost-tree { border-top: 1px solid var(--border); }
.cost-node > summary { list-style: none; cursor: pointer; }
.cost-node > summary::-webkit-details-marker { display: none; }
.cost-node-row { display: grid; grid-template-columns: minmax(0, 2.2fr) minmax(60px, 3fr) 5.4rem 3rem; align-items: center; gap: 0.75rem; padding: 0.6rem 0.25rem 0.6rem calc(1.4rem + min(var(--depth), 6) * 1rem); border-bottom: 1px solid var(--border); position: relative; }
.cost-node > summary:hover > .cost-node-row { background: var(--surface-2); }
.cost-node > summary > .cost-node-row::before { content: "+"; position: absolute; left: calc(0.35rem + min(var(--depth), 6) * 1rem); color: var(--text-2); }
.cost-node[open] > summary > .cost-node-row::before { content: "\\2013"; }
.cost-node-name { display: grid; gap: 0.15rem; min-width: 0; font-size: 0.82rem; line-height: 1.4; overflow-wrap: anywhere; }
.cost-node-name a { color: var(--text); text-decoration: none; }
.cost-node-name a:hover { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }
.cost-node-name small { color: var(--text-2); font: 0.7rem/1.3 ui-monospace, monospace; }
.cost-node-own .cost-node-name > span { color: var(--text-2); }
.cost-node-own .cost-node-name small { font-family: inherit; }
.cost-node-bar .cost-split { height: 8px; }
.cost-node-value { text-align: right; font-size: 0.82rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.cost-node-share { text-align: right; font-size: 0.72rem; color: var(--text-2); font-variant-numeric: tabular-nums; }
@media (max-width: 560px) {
  .cost-node-row { grid-template-columns: minmax(0, 1fr) 5rem 2.75rem; grid-template-areas: "n n n" "b v s"; row-gap: 0.4rem; }
  .cost-node-name { grid-area: n; } .cost-node-bar { grid-area: b; } .cost-node-value { grid-area: v; } .cost-node-share { grid-area: s; }
  .cost-node-row { padding-left: calc(1.2rem + min(var(--depth), 4) * 0.6rem); }
  .cost-node > summary > .cost-node-row::before { left: calc(0.25rem + min(var(--depth), 4) * 0.6rem); }
}
`;
