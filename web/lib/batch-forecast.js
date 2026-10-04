import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

const gcd = (a, b) => b ? gcd(b, a % b) : a;
const money = cents => "$" + (cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const count = n => n.toLocaleString("en-US", { maximumFractionDigits: 3 });
const escape = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const star = '<sup class="forecast-star" aria-label="estimate or availability unresolved">*</sup>';

function lotCost(option, lots) {
  let price = option.priceCents;
  for (const tier of [...(option.tiers || [])].sort((a, b) => a.minimum - b.minimum)) {
    if (lots >= tier.minimum) price = tier.priceCents;
  }
  return lots * price;
}

// Compare whole purchase lots, including a mix of sizes. Capacity can mean
// usable full cuts rather than raw length (three evaporators per copper coil).
// Milligram/millimetre precision is reduced by the lots' common divisor so
// fractional consumption does not require a large dynamic-programming table.
export function optimizePurchase(required, options) {
  if (!Number.isFinite(required) || required <= 0 || !options?.length) throw new RangeError("Invalid purchase requirement");
  for (const option of options) {
    if (!Number.isFinite(option.quantity) || option.quantity <= 0 || !Number.isFinite(option.priceCents) || option.priceCents <= 0) throw new RangeError("Invalid purchase lot");
    for (const tier of option.tiers || []) {
      if (!Number.isInteger(tier.minimum) || tier.minimum < 1 || !Number.isFinite(tier.priceCents) || tier.priceCents <= 0) throw new RangeError("Invalid purchase tier");
    }
  }
  const available = options.filter(option => option.available !== false);
  const candidates = available.length ? available : options;
  const sizes = candidates.map(option => Math.round(option.quantity * 1000));
  if (sizes.some(size => size === 0)) throw new RangeError("Lot below quantity precision");
  const divisor = sizes.reduce(gcd);
  const capacities = sizes.map(size => size / divisor);
  const target = Math.ceil(required * 1000 / divisor - 1e-8);
  const tierCapacities = candidates.flatMap((option, index) => (option.tiers || []).map(tier => tier.minimum * capacities[index]));
  const limit = Math.max(target + Math.max(...capacities) - 1, ...tierCapacities);
  if (limit > 100000) throw new RangeError("Purchase range too large");
  let states = new Map([[0, { cost: 0, lots: [] }]]);
  for (const [index, option] of candidates.entries()) {
    const next = new Map();
    const capacity = capacities[index];
    const maxLots = Math.max(Math.ceil(target / capacity), ...(option.tiers || []).map(tier => tier.minimum));
    for (const [quantity, state] of states) {
      for (let lots = 0; lots <= maxLots && quantity + lots * capacity <= limit; lots++) {
        const covered = quantity + lots * capacity;
        const cost = state.cost + lotCost(option, lots);
        if (!next.has(covered) || cost < next.get(covered).cost) next.set(covered, { cost, lots: [...state.lots, lots] });
      }
    }
    states = next;
  }
  let best;
  for (const [quantity, state] of states) {
    if (quantity < target) continue;
    if (!best || state.cost < best.cost - 1e-8 || (Math.abs(state.cost - best.cost) < 1e-8 && quantity < best.quantity)) best = { ...state, quantity };
  }
  if (!best) throw new RangeError("No purchase plan covers requirement");
  const quantity = best.quantity * divisor / 1000;
  return {
    required, quantity, remaining: Math.max(0, quantity - required), costCents: Math.round(best.cost),
    packages: candidates.flatMap((option, index) => best.lots[index] ? [{ count: best.lots[index], option }] : []),
  };
}

export function calculateBatch(data, units, labor) {
  if (![10, 20].includes(units)) throw new RangeError("Forecast supports batches of 10 or 20");
  if (!Number.isFinite(data.taxRate) || data.taxRate < 0 || data.taxRate > 1) throw new RangeError("Invalid tax reserve");
  const suppliers = data.suppliers.map(supplier => ({ ...supplier, rows: [], costCents: 0, shippingCents: supplier.shippingCents[String(units)] }));
  if (suppliers.some(supplier => !Number.isInteger(supplier.shippingCents) || supplier.shippingCents < 0)) throw new RangeError("Invalid freight reserve");
  let merchandiseCents = 0;
  let leftoverCents = 0;
  const rows = data.items.map(item => {
    const required = item.fixedQuantity ?? item.perUnit * units * (1 + (item.materialAllowance || 0));
    const onHand = item.inventory?.onHand ?? 0;
    const incoming = item.inventory?.incoming ?? 0;
    if (![required, onHand, incoming].every(n => Number.isFinite(n) && n >= 0)) throw new RangeError("Invalid requirement or inventory credit");
    const openingStock = onHand + incoming;
    const shortfall = Math.max(0, required - openingStock);
    let target = Math.max(shortfall, (item.minimumPurchaseQuantity?.[String(units)] || 0) - openingStock);
    // A colour kit must cover its limiting colour, not just aggregate feet.
    // The provisional gross kit allocation is reduced by the existing kit.
    if (item.packageCounts) {
      const lots = item.packageCounts[String(units)];
      if (!Number.isInteger(lots) || lots < 1 || lots * item.options[0].quantity < required) throw new RangeError("Invalid provisional lot count");
      target = Math.max(target, lots * item.options[0].quantity - openingStock);
    }
    let purchase = target > 1e-8 ? optimizePurchase(target, item.options) : { quantity: 0, costCents: 0, packages: [] };
    purchase.required = required;
    purchase.remaining = Math.max(0, openingStock + purchase.quantity - required);
    const issues = [];
    if (item.status === "unavailable" || purchase.packages.some(pack => pack.option.available === false)) issues.push(purchase.quantity ? "Out of stock; replenishment price estimated." : "Supplier out of stock; this plan relies on the credited inventory.");
    if (item.status === "unconfirmed" && purchase.quantity) issues.push("Exact Prime offer unconfirmed; historical delivered-price allowance.");
    if (item.status === "estimate") issues.push("Estimated quantity, price or compatibility; see note.");
    if (item.inventory?.estimated) issues.push("Remaining usable inventory is estimated; see stock note.");
    if (incoming) issues.push("Already ordered; delivery pending. Arrival is required before assembly.");
    for (const pack of purchase.packages) {
      if (pack.option.listedPackages !== undefined && pack.count > pack.option.listedPackages) {
        const missing = pack.count - pack.option.listedPackages;
        issues.push(`Listed stock: ${pack.option.listedPackages} lots; ${missing} more ${missing === 1 ? "lot needs" : "lots need"} a source or replenishment.`);
      }
    }
    const row = { ...item, ...purchase, onHand, incoming, openingStock, shortfall, issues, estimated: issues.length > 0 };
    const supplier = suppliers.find(supplier => supplier.id === item.supplier);
    if (!supplier) throw new Error(`Missing supplier ${item.supplier}`);
    supplier.rows.push(row);
    supplier.costCents += purchase.costCents;
    if (item.priceBasis === "merchandise") merchandiseCents += purchase.costCents;
    else if (item.priceBasis !== "delivered") throw new Error("Unknown price basis");
    if (purchase.quantity) leftoverCents += purchase.costCents * Math.max(0, purchase.quantity - shortfall) / purchase.quantity;
    return row;
  });
  const partsCents = rows.reduce((total, row) => total + row.costCents, 0);
  // Existing stock does not trigger a new supplier shipment.
  for (const supplier of suppliers) if (!supplier.rows.some(row => row.quantity > 0)) supplier.shippingCents = 0;
  const inboundCents = suppliers.reduce((total, supplier) => total + supplier.shippingCents, 0);
  const taxCents = Math.round((merchandiseCents + inboundCents) * data.taxRate);
  const procurementCents = partsCents + inboundCents + taxCents;
  const allowances = data.allowances.map(allowance => ({ ...allowance, costCents: allowance.perUnitCents !== undefined ? allowance.perUnitCents * units : allowance.batchCents[String(units)] }));
  if (allowances.some(allowance => !Number.isInteger(allowance.costCents) || allowance.costCents < 0)) throw new RangeError("Invalid production allowance");
  const pendingPayments = data.pendingPayments || [];
  if (pendingPayments.some(payment => !Number.isInteger(payment.costCents) || payment.costCents < 0)) throw new RangeError("Invalid pending-payment reserve");
  const pendingCents = pendingPayments.reduce((total, payment) => total + payment.costCents, 0);
  const cashCents = procurementCents + pendingCents + allowances.reduce((total, allowance) => total + allowance.costCents, 0);
  const laborHours = labor && labor.rate > 0 && labor.opCount > 0 && labor.minutes > 0 ? labor.minutes / 60 * units : null;
  const laborCents = laborHours === null ? null : Math.round(laborHours * labor.rate * 100);
  return { units, rows, suppliers, allowances, pendingPayments, pendingCents, partsCents, inboundCents, taxCents, procurementCents, cashCents, leftoverCents: Math.round(leftoverCents), laborHours, laborCents, totalCents: laborCents === null ? null : cashCents + laborCents };
}

export function readBatchForecast(hardwareDir, labor) {
  const data = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger", "batch-forecast.json"), "utf8"));
  if (data.schemaVersion !== 2 || !/^\d{4}-\d{2}-\d{2}$/.test(data.checkedAt) || !/^\d{4}-\d{2}-\d{2}$/.test(data.inventoryAsOf) || !Number.isFinite(data.taxRate) || data.taxRate < 0 || data.taxRate > 1) throw new Error("Invalid batch forecast");
  if (data.items.some(item => !item.inventory)) throw new Error("Missing inventory reconciliation");
  if (new Set(data.items.map(item => item.id)).size !== data.items.length) throw new Error("Duplicate purchase SKU");
  const bom = fs.readFileSync(path.join(hardwareDir, "ledger", "bom.md"), "utf8");
  const bomChanged = createHash("sha256").update(bom).digest("hex") !== data.bomSha256;
  return { data, bomChanged, batches: [10, 20].map(units => calculateBatch(data, units, labor)) };
}

function purchaseCell(row) {
  const lots = row.packages.map(pack => `${count(pack.count)} × ${escape(pack.option.label)}`).join("<br>");
  return `<td><b>${lots || "No new purchase"}${row.estimated ? star : ""}</b><span>Need ${count(row.required)} ${escape(row.unit)} · on hand ${count(row.onHand)}${row.incoming ? ` · already ordered ${count(row.incoming)}` : ""}.</span><span>Shortfall ${count(row.shortfall)} · buy ${count(row.quantity)} · ${money(row.costCents)} new.</span><span>${count(row.remaining)} ${escape(row.unit)} left after batch.</span>${row.issues.filter(issue => /^(Out of stock|Supplier out of stock|Listed stock|Already ordered)/.test(issue)).map(issue => `<em>${escape(issue)}</em>`).join("")}</td>`;
}

export function renderBatchForecast(forecast) {
  if (!forecast) return "";
  const { data, batches: [ten, twenty], bomChanged } = forecast;
  const tableRow = (label, key, estimated = true) => `<tr><th scope="row">${escape(label)}</th><td>${money(ten[key])}${estimated ? star : ""}</td><td>${money(twenty[key])}${estimated ? star : ""}</td></tr>`;
  const supplierDetails = ten.suppliers.map((supplier, index) => {
    const other = twenty.suppliers[index];
    const rows = supplier.rows.map((row, rowIndex) => {
      const name = row.sourceUrl && /^https:\/\//.test(row.sourceUrl) ? `<a href="${escape(row.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escape(row.name)}</a>` : escape(row.name);
      return `<tr><th scope="row">${name}${row.estimated || other.rows[rowIndex].estimated ? star : ""}<span>${escape(row.note)}</span><span><b>Stock basis:</b> ${escape(row.inventory.note)}</span><small>${row.priceBasis === "delivered" ? "Delivered-price allowance; tax not added again." : "Merchandise price; new freight/tax below."}</small></th>${purchaseCell(row)}${purchaseCell(other.rows[rowIndex])}</tr>`;
    }).join("");
    return `<details class="forecast-supplier"><summary><span>${escape(supplier.name)}</span><b>${money(supplier.costCents)} / ${money(other.costCents)}</b></summary><p>${escape(supplier.note)}</p><div class="forecast-scroll" tabindex="0" role="region" aria-label="${escape(supplier.name)} purchase quantities"><table class="forecast-orders"><caption>Additional purchases after existing stock · 10 / 20 machines</caption><thead><tr><th scope="col">Part, source &amp; stock basis</th><th scope="col">10 machines</th><th scope="col">20 machines</th></tr></thead><tbody>${rows}</tbody><tfoot><tr><th scope="row">New parts / materials</th><td>${money(supplier.costCents)}</td><td>${money(other.costCents)}</td></tr><tr><th scope="row">New inbound freight / import allowance${star}</th><td>${money(supplier.shippingCents)}</td><td>${money(other.shippingCents)}</td></tr></tfoot></table></div></details>`;
  }).join("");
  const date = new Date(data.checkedAt + "T12:00:00Z").toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  const unavailable = ten.rows.filter(row => row.status === "unavailable").map(row => {
    const other = twenty.rows.find(other => other.id === row.id);
    return `<p><strong>${escape(row.name)} replenishment is out of stock${star}.</strong> ${row.quantity || other.quantity ? `The new-purchase budget includes ${money(row.costCents)} / ${money(other.costCents)} pending replenishment.` : `The provisional ${count(row.onHand)} ${escape(row.unit)} on hand covers both batches; no new purchase is budgeted. Twenty machines need ${count(other.required)} ${escape(row.unit)} including the print allowance. If less remains, replenishment needs a source.`}</p>`;
  }).join("");
  const shortages = twenty.rows.filter(row => row.packages.some(pack => pack.option.listedPackages !== undefined && pack.count > pack.option.listedPackages)).map(row => `${row.name}: ${row.issues.find(issue => /more lot/.test(issue))}`).join(" ");
  return `<section class="cost-forecast" id="batch-forecast" aria-labelledby="forecast-heading" data-checked-at="${data.checkedAt}">
    <h2 class="cost-title" id="forecast-heading">From today&rsquo;s stock to 10 &amp; 20 machines</h2>
    <p class="cost-prose">Additional spending from the inventory available on ${date}. Each alternative starts with the same stock and covers the first 10 or 20 machines in total. Existing paid parts cost nothing more to acquire; only the shortfall is bought, in whole supplier packs and usable cut lengths. ${data.bomRowCount} BOM lines are covered.</p>
    ${bomChanged ? `<p class="forecast-alert">${star} The BOM has changed since these supplier quantities were checked. This dated forecast needs a quantity review.</p>` : ""}
    <div class="forecast-cards">${[ten, twenty].map(batch => `<div><div class="cost-top-cap">First ${batch.units} machines</div><strong>${money(batch.cashCents)}${star}</strong><p>Additional cash budget from current stock</p><small>${money(batch.cashCents / batch.units)} per machine · supplies &amp; delivery included</small></div>`).join("")}</div>
    <p class="cost-note"><b>Opening filament stock${star}:</b> approximately 12 kg Black PET-GF15, 4 kg Clear PETG and 10 kg Black PETG. The ten usable batch-2 boards, ten carbonator tube cuts, twenty endcaps and other credited parts reduce new orders. Remaining quantities from older purchase records are estimates; the supplier rows show every credit.</p>
    <div class="forecast-scroll"><table class="forecast-comparison"><caption class="cost-sr-only">Batch expense forecast</caption><thead><tr><th scope="col">Expense</th><th scope="col">10 machines</th><th scope="col">20 machines</th></tr></thead><tbody>
      ${tableRow("New whole parts & material purchases", "partsCents")}${tableRow("New inbound freight / import reserve", "inboundCents")}${tableRow(`Tax reserve on new purchases (${count(data.taxRate * 100)}%)`, "taxCents")}
      <tr class="forecast-subtotal"><th scope="row">New delivered purchases</th><td>${money(ten.procurementCents)}${star}</td><td>${money(twenty.procurementCents)}${star}</td></tr>
      ${tableRow("Possible unpaid balance on orders already placed", "pendingCents")}
      ${ten.allowances.map((allowance, index) => `<tr><th scope="row">${escape(allowance.name)}</th><td>${money(allowance.costCents)}${star}</td><td>${money(twenty.allowances[index].costCents)}${star}</td></tr>`).join("")}
      <tr class="forecast-total"><th scope="row">Additional cash, supplies &amp; delivery</th><td>${money(ten.cashCents)}${star}</td><td>${money(twenty.cashCents)}${star}</td></tr>
      ${ten.laborCents !== null ? `<tr><th scope="row">Planned labor at ${money(laborRate(ten))}/h<span>${count(ten.laborHours)} / ${count(twenty.laborHours)} attended hours</span></th><td>${money(ten.laborCents)}${star}</td><td>${money(twenty.laborCents)}${star}</td></tr><tr class="forecast-total"><th scope="row">Including paid build labor</th><td>${money(ten.totalCents)}${star}</td><td>${money(twenty.totalCents)}${star}</td></tr>` : `<tr><th colspan="3">Labor estimate unavailable; add build labor to the purchase budget.</th></tr>`}
    </tbody></table></div>
    <p class="cost-note">${star} Estimate, uncounted inventory or supply unresolved. New purchases include approximately ${money(ten.leftoverCents)} / ${money(twenty.leftoverCents)} of excess stock, before freight and tax; it remains part of the cash outlay. The possible-payment reserve is released when those existing orders are confirmed paid. Owner build labor can be unpaid; paying the planned labor adds the amount shown above.</p>
    <div class="forecast-alert">${unavailable}${shortages ? `<p><strong>Stock limits for 20 machines${star}.</strong> ${escape(shortages)}</p>` : ""}<p>Exact Prime sources remain unresolved for several plumbing/refrigeration parts, the flow meter and short M3 inserts. Custom fabrication, PCB assembly and some harness/refrigeration selections use explicit allowances. Expand the supplier rows for the exact item, quantity and source.</p></div>
    <details class="forecast-assumptions"><summary>Inventory credits, pending orders &amp; allowances</summary><p>${escape(data.scope)}</p><p>${escape(data.inventoryNote)}</p><p>${escape(data.roundingNote)}</p>${ten.pendingPayments.map(payment => `<p><b>${escape(payment.name)} · ${money(payment.costCents)}${star}.</b> ${escape(payment.note)}</p>`).join("")}${data.allowances.map(allowance => `<p><b>${escape(allowance.name)}${star}.</b> ${escape(allowance.note)}</p>`).join("")}<p>${escape(shortages)}</p><ul>${data.notes.map(note => `<li>${escape(note)}</li>`).join("")}</ul><p>Filament includes a provisional 15% allowance for supports, purge and rejected prints. Finished printed parts without a counted usable balance receive no additional credit. Printed material totals and small colour splits require production-yield confirmation. Incomplete cuts and colour/size-specific stock may not supply another complete machine.</p></details>
    <h3 class="cost-h2">What we still need to buy</h3><p class="cost-note">Summary prices are new parts/materials for 10 / 20 machines. Expand for batch need, on hand, already ordered, shortfall, purchase lots and stock left after the batch. Shipping and tax reserves are separate.</p>
    ${supplierDetails}
  </section>`;
}

function laborRate(batch) { return Math.round(batch.laborCents / batch.laborHours); }

export const BATCH_FORECAST_CSS = `
.cost-forecast { margin: 2.8rem 0 3rem; scroll-margin-top: 4.5rem; }
.forecast-cards { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 1rem; margin: 1.5rem 0; }
.forecast-cards > div { border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; background: var(--surface); }
.forecast-cards strong { display: block; font-size: clamp(1.5rem,4vw,2.3rem); color: var(--accent); font-variant-numeric: tabular-nums; margin-top: .3rem; }
.forecast-cards p { font-size: .85rem; margin: .6rem 0; }
.forecast-cards small, .forecast-comparison th span { color: var(--text-3); font-size: .75rem; }
.forecast-star { font-size: .75em; color: var(--accent); margin-left: .1em; }
.forecast-scroll { overflow-x: auto; max-width: 100%; }
.forecast-comparison, .forecast-orders { width: 100%; border-collapse: collapse; font-size: .85rem; }
.forecast-comparison th, .forecast-orders th { text-align: left; font-weight: 500; }
.forecast-comparison td, .forecast-comparison th, .forecast-orders td, .forecast-orders th { padding: .8rem .55rem; border-bottom: 1px solid var(--border); vertical-align: top; }
.forecast-comparison td { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.forecast-comparison thead th:not(:first-child) { text-align: right; }
.forecast-comparison th span { display: block; margin-top: .3rem; }
.forecast-subtotal, .forecast-total { background: var(--surface); }
.forecast-total td, .forecast-total th { font-weight: 700; }
.forecast-alert { padding: .85rem 1rem; border-left: 3px solid var(--accent); background: var(--surface); font-size: .85rem; line-height: 1.65; margin: 1.25rem 0; }
.forecast-alert p { margin: .4rem 0; }
.forecast-supplier, .forecast-assumptions { border: 1px solid var(--border); border-radius: 8px; margin: .7rem 0; scroll-margin-top: 4.5rem; }
.forecast-supplier summary, .forecast-assumptions summary { padding: .9rem 1rem; cursor: pointer; font-size: .85rem; }
.forecast-supplier summary b { float: right; font-variant-numeric: tabular-nums; font-weight: 500; }
.forecast-supplier > p, .forecast-assumptions p, .forecast-assumptions ul { font-size: .8rem; line-height: 1.65; color: var(--text-3); margin: .8rem 1rem; }
.forecast-assumptions li { margin: .5rem 0; }
.forecast-orders { min-width: 670px; table-layout: fixed; }
.forecast-orders th:first-child { width: 46%; }
.forecast-orders caption { text-align: left; padding: .6rem 1rem; font-size: .75rem; color: var(--text-3); }
.forecast-orders th span, .forecast-orders td span, .forecast-orders td em, .forecast-orders th small { display: block; margin-top: .45rem; font-size: .75rem; font-weight: 400; line-height: 1.55; }
.forecast-orders th span, .forecast-orders td span, .forecast-orders th small { color: var(--text-3); }
.forecast-orders td b { font-size: .8rem; font-weight: 600; line-height: 1.6; }
.forecast-orders td em { color: var(--accent); font-style: normal; }
@media (max-width: 560px) {
  .forecast-cards { grid-template-columns: 1fr; }
  .forecast-comparison { font-size: .72rem; }
  .forecast-comparison th, .forecast-comparison td { padding: .65rem .2rem; }
  .forecast-supplier summary b { float: none; display: block; margin: .45rem 0 0 1rem; }
  .forecast-orders { min-width: 0; table-layout: auto; }
  .forecast-orders caption { display: block; }
  .forecast-orders thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
  .forecast-orders tbody, .forecast-orders tfoot, .forecast-orders tr { display: block; width: 100%; }
  .forecast-orders tr { border-bottom: 1px solid var(--border); }
  .forecast-orders th:first-child { display: block; width: auto; padding: .9rem .6rem .3rem; border-bottom: 0; }
  .forecast-orders td { display: inline-block; width: 50%; box-sizing: border-box; border-bottom: 0; padding: .7rem .6rem .9rem; }
  .forecast-orders td::before { display: block; font-size: .7rem; color: var(--text-3); margin-bottom: .4rem; }
  .forecast-orders td:nth-of-type(1)::before { content: "10 machines"; }
  .forecast-orders td:nth-of-type(2)::before { content: "20 machines"; }
}
`;
