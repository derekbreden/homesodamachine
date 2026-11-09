// The production workspace joins authored material demand, stock evidence and supplier packs for the cost page.
import { readBatchForecast } from './batch-forecast.js';
import { readMaterialCatalog } from './material-catalog.js';
import { readMaterialStock } from './material-stock.js';
import { planMaterial } from '../contracts/material-stock.js';
import { categoryName } from './cost-categories.js';

export const PLANNING_HORIZON = 20;

export function productionData(catalog, offers, horizon = PLANNING_HORIZON) {
  const index = new Map(catalog.materials.map(m => [m.id, m]));
  const quotes = new Map(offers.items.map(item => [item.stock, item]));
  const finishes = {};
  for (const finish of ['white', 'black']) {
    const rows = new Map(), completed = [];
    for (let units = 1; units <= horizon; units++) {
      const plan = planMaterial(catalog, catalog.cost_root, units, { finish });
      completed[units] = plan.materials.filter(row => row.fromStock > 0).map(row => ({ id: row.material, name: index.get(row.material)?.description || row.material, quantity: row.fromStock }));
      for (const input of plan.resources) {
        const resource = catalog.stock.resources[input.resource] || {}, quote = quotes.get(input.resource);
        if (!rows.has(input.resource)) rows.set(input.resource, {
          id: input.resource, name: resource.name || input.resource, unit: resource.unit || 'ea',
          category: categoryName(resource.category || quote?.category || 'supplies'), supplier: quote?.supplier || '',
          available: input.available, onHand: resource.onHand ?? null, reserved: resource.reserved || 0,
          incoming: resource.incoming || 0, estimated: Boolean(input.estimated || resource.estimated), quantityKnown: true,
          note: resource.note || 'No usable stock count recorded.', asOf: resource.asOf || null,
          href: quote?.sourceUrl || resource.href || null, quote: quote || null,
          needs: Array(horizon + 1).fill(0), active: Array(horizon + 1).fill(false), reusableNeeds: Array(horizon + 1).fill(0), uses: [],
        });
        const row = rows.get(input.resource);
        row.needs[units] = input.needed; row.active[units] = true; row.reusableNeeds[units] = input.reusable || 0; row.quantityKnown &&= input.quantityKnown;
        row.uses = [...new Set([...row.uses, ...input.uses])];
      }
      for (const gap of plan.gaps) {
        const id = 'material:' + gap.material;
        if (!rows.has(id)) rows.set(id, {
          id, name: index.get(gap.material)?.description || gap.material, unit: 'ea', category: 'Manufacturing input needed',
          supplier: '', available: null, onHand: null, incoming: 0, reserved: 0, quantityKnown: false, estimated: false,
          material: gap.material, note: gap.reason, needs: Array(horizon + 1).fill(0), uses: [gap.material], quote: null,
        });
        rows.get(id).needs[units] += gap.quantity || 1;
      }
    }
    finishes[finish] = { rows: [...rows.values()], completed };
  }
  return { horizon, root: catalog.cost_root, name: index.get(catalog.cost_root)?.description || 'Complete machine',
    stockAsOf: catalog.stock.asOf, stockNote: catalog.stock.opening.note, checkedAt: offers.checkedAt,
    taxRate: offers.taxRate, suppliers: offers.suppliers, finishes,
    materials: Object.fromEntries([...index].map(([id, m]) => [id, m.description])),
  };
}

export function readProductionPlanner(hardwareDir, labor) {
  const { data } = readBatchForecast(hardwareDir, labor);
  const catalog = readMaterialCatalog(hardwareDir);
  catalog.stock = readMaterialStock(hardwareDir, catalog);
  return productionData(catalog, data);
}

export function renderProductionPlanner(data) {
  if (!data) return '';
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return `<section class="production-planner" id="batch-forecast" aria-labelledby="planner-title">
    <div class="planner-intro"><div><p class="planner-eyebrow">Production planning</p><h2 id="planner-title">From the shelf to the next machine.</h2><p>Start with what we have. Choose purchase packs. See how far they take us.</p></div><label class="planner-finish">Faucet finish<select id="planner-finish"><option value="white">White</option><option value="black">Black</option></select></label></div>
    <p class="planner-basis">Stock evidence through <time>${data.stockAsOf.slice(0, 10)}</time> · Supplier observations ${data.checkedAt} · <a href="/build?material=${data.root}">Stock &amp; assembly records ↗</a></p>
    <div class="planner-milestones" aria-label="Cumulative production targets"></div>
    <div class="planner-legend"><span data-tone="stock">On hand</span><span data-tone="incoming">On order</span><span data-tone="planned">Proposed purchase</span><span data-tone="short">Short</span><span data-tone="unknown">Needs confirmation</span></div>
    <div class="planner-outlook" aria-label="Coverage through successive units"></div>
    <p class="planner-caption">Each unit includes everything needed for the units before it. Bars count material lines, not assembly progress. Hatched on-hand coverage uses estimated quantities.</p>
    <div class="planner-workspace"><div class="planner-materials">
      <div class="planner-section-head"><div><p class="planner-eyebrow">Follow the materials</p><h3 id="planner-focus-title"></h3></div><a id="planner-build-link" href="/build">Assembly plan ↗</a></div>
      <p id="planner-focus-note"></p>
      <div class="planner-filters"><label>Find a material<input id="planner-search" type="search" placeholder="Part, stock or material number"></label><label>Show<select id="planner-filter"><option value="attention">Needs attention</option><option value="short">Short of stock</option><option value="unknown">Needs confirmation</option><option value="planned">In my purchase plan</option><option value="all">All materials</option></select></label><label>Supplier<select id="planner-supplier"><option value="all">All suppliers</option>${data.suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}<option value="none">No supplier quote</option></select></label></div>
      <div class="planner-table-scroll" tabindex="0" role="region" aria-label="Material coverage and purchase packs"><table class="planner-table"><thead></thead><tbody></tbody></table></div>
      <div class="planner-list-footer"><span id="planner-row-count"></span><button type="button" id="planner-more">Show more materials</button></div>
    </div><aside class="planner-basket" aria-labelledby="planner-basket-title"></aside></div>
    <p class="planner-status" role="status" aria-live="polite"></p>
    <noscript><p>Enable JavaScript to adjust purchase packs and compare production scenarios. The <a href="/build?material=${data.root}">stock and assembly plan</a> is available without it.</p></noscript>
    <script id="production-planner-data" type="application/json">${json}</script>
  </section>`;
}
