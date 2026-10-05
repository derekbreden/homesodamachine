import { categoryName } from "./cost-categories.js";

const money = cents => "$" + (cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const count = n => n.toLocaleString("en-US", { maximumFractionDigits: 3 });
const escape = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const star = '<sup class="forecast-star" aria-label="estimate or availability unresolved">*</sup>';

function purchaseLabel(row) {
  if (!row.quantity) return "Covered by stock";
  if (row.unit === "pieces" && row.packages.every(pack => pack.option.quantity === 1)) return `${count(row.quantity)} pieces`;
  return row.packages.map(pack => `${count(pack.count)} × ${pack.option.label.split(":")[0].replace(/^one /, "")}`).join(" + ");
}

function renderPart(row, suppliers) {
  const supplier = suppliers.find(supplier => supplier.id === row.supplier);
  const source = row.sourceUrl && /^https:\/\//.test(row.sourceUrl)
    ? `<a href="${escape(row.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escape(row.name)}</a>` : escape(row.name);
  const lots = row.packages.map(pack => `${count(pack.count)} × ${escape(pack.option.label)}`).join(" + ");
  return `<details class="forecast-part" data-part-id="${escape(row.id)}" data-supplier="${escape(row.supplier)}" data-category="${escape(row.category || "supplies")}" data-cents="${row.costCents}" data-purchase="${row.quantity > 0}"${row.quantity ? "" : " hidden"}>
    <summary><span class="forecast-part-name"><span title="${escape(row.name)}">${escape(row.name)}</span>${row.estimated ? star : ""}</span><span class="forecast-part-qty">${escape(purchaseLabel(row))}</span><span class="forecast-part-cost">${money(row.costCents)}</span><span class="forecast-marker" aria-hidden="true"></span></summary>
    <div class="forecast-part-evidence">
      <p><b>${escape(supplier.name)} · ${lots || "No new purchase"}.</b></p>
      <dl class="forecast-stock">
        <div><dt>Batch need</dt><dd>${count(row.required)} ${escape(row.unit)}</dd></div>
        <div><dt>On hand</dt><dd>${count(row.onHand)} ${escape(row.unit)}</dd></div>
        <div><dt>Already ordered</dt><dd>${count(row.incoming)} ${escape(row.unit)}</dd></div>
        <div><dt>Shortfall</dt><dd>${count(row.shortfall)} ${escape(row.unit)}</dd></div>
        <div><dt>Buying</dt><dd>${count(row.quantity)} ${escape(row.unit)}</dd></div>
        <div><dt>Left after batch</dt><dd>${count(row.remaining)} ${escape(row.unit)}</dd></div>
      </dl>
      <p>${source}</p><p>${escape(row.note)}</p><p><b>Stock basis:</b> ${escape(row.inventory.note)}</p>
      ${row.issues.length ? `<ul>${row.issues.map(issue => `<li>${escape(issue)}</li>`).join("")}</ul>` : ""}
      <p>${row.priceBasis === "delivered" ? "Delivered-price allowance; tax not added again." : "Merchandise price; new freight and tax are in the cash budget."}</p>
    </div>
  </details>`;
}

function renderGroup({ id, name, rows, note, shippingCents }, batch, kind, maximum, open, includeRows = false) {
  const cents = rows.reduce((sum, row) => sum + row.costCents, 0);
  const buying = rows.filter(row => row.quantity).length;
  return `<details class="forecast-group${kind === "supplier" ? " forecast-supplier" : ""}" data-group-id="${escape(id)}"${open ? " open" : ""}${buying ? "" : " hidden"}>
    <summary><span class="forecast-group-name">${escape(name)}</span><span class="cost-bt" aria-hidden="true"><span class="cost-bf" style="width:${(cents / maximum * 100).toFixed(1)}%"></span></span><span class="forecast-group-cost">${money(cents)}</span><span class="forecast-group-percent">${batch.partsCents ? (cents / batch.partsCents * 100).toFixed(1) : "0.0"}%</span><span class="forecast-marker" aria-hidden="true"></span></summary>
    <div class="forecast-item-scroll" tabindex="0" role="region" aria-label="${escape(name)} items for ${batch.units} machines"><div class="forecast-group-items">${includeRows ? rows.map(row => renderPart(row, batch.suppliers)).join("") : ""}</div></div>
    ${note ? `<details class="forecast-source-note"><summary>Supplier pricing &amp; availability</summary><p>${escape(note)}</p><p>New inbound freight / import reserve: ${money(shippingCents)}${star}.</p></details>` : ""}
  </details>`;
}

function renderPurchasePlan(batch, defaultUnits) {
  const ranked = [...batch.rows].sort((a, b) => b.costCents - a.costCents || a.name.localeCompare(b.name));
  const suppliers = batch.suppliers.map(supplier => ({ ...supplier, rows: ranked.filter(row => row.supplier === supplier.id) })).sort((a, b) => b.costCents - a.costCents);
  const categoryIds = [...new Set(ranked.map(row => row.category || "supplies"))];
  const categories = categoryIds.map(id => {
    const rows = ranked.filter(row => (row.category || "supplies") === id);
    return { id, name: categoryName(id), rows, costCents: rows.reduce((sum, row) => sum + row.costCents, 0) };
  }).sort((a, b) => b.costCents - a.costCents);
  const maximum = Math.max(...categories.map(category => category.costCents), 1);
  const supplierMaximum = Math.max(...suppliers.map(supplier => supplier.costCents), 1);
  return `<details class="forecast-plan" data-units="${batch.units}"${batch.units === defaultUnits ? " open" : ""}>
    <summary>First ${batch.units} machines · ${money(batch.partsCents)} in new parts &amp; materials${star}</summary>
    <div class="forecast-groups" data-group-by="category">${categories.map((category, index) => renderGroup(category, batch, "category", maximum, index === 0, true)).join("")}</div>
    <div class="forecast-groups" data-group-by="supplier" hidden>${suppliers.map(supplier => renderGroup(supplier, batch, "supplier", supplierMaximum, false)).join("")}</div>
  </details>`;
}

export function renderBatchForecast(forecast) {
  if (!forecast) return "";
  const { data, batches, bomChanged } = forecast;
  const first = batches[0];
  const largest = batches.at(-1);
  const cells = value => batches.map(batch => `<td>${money(value(batch))}${star}</td>`).join("");
  const tableRow = (label, key, className = "") => `<tr${className ? ` class="${className}"` : ""}><th scope="row">${escape(label)}</th>${cells(batch => batch[key])}</tr>`;
  const date = new Date(data.checkedAt + "T12:00:00Z").toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  const unavailable = first.rows.filter(row => row.status === "unavailable").map(row => {
    const rows = batches.map(batch => batch.rows.find(other => other.id === row.id));
    return `<p><strong>${escape(row.name)} replenishment is out of stock${star}.</strong> ${rows.some(other => other.quantity) ? `The new-purchase budgets include ${rows.map(other => money(other.costCents)).join(" / ")} pending replenishment.` : `The provisional ${count(row.onHand)} ${escape(row.unit)} on hand covers all three batches; no new purchase is budgeted. ${largest.units} machines need ${count(rows.at(-1).required)} ${escape(row.unit)} including the print allowance. If less remains, replenishment needs a source.`}</p>`;
  }).join("");
  const shortages = largest.rows.filter(row => row.packages.some(pack => pack.option.listedPackages !== undefined && pack.count > pack.option.listedPackages)).map(row => `${row.name}: ${row.issues.find(issue => /more lot/.test(issue))}`).join(" ");
  return `<section class="cost-forecast" id="batch-forecast" aria-labelledby="forecast-heading" data-checked-at="${data.checkedAt}">
    <h2 class="cost-title" id="forecast-heading">From today&rsquo;s stock to 5, 10 &amp; 20 machines</h2>
    <p class="cost-prose">Additional spending from ${date} inventory. Each plan starts with the same stock and buys the shortfall in whole supplier packs.</p>
    ${bomChanged ? `<p class="forecast-alert">${star} The BOM has changed since these supplier quantities were checked. This dated forecast needs a quantity review.</p>` : ""}
    <div class="forecast-cards">${batches.map(batch => `<div data-card-units="${batch.units}"><div class="cost-top-cap">First ${batch.units} machines</div><strong>${money(batch.cashCents)}${star}</strong><p>Additional cash from current stock</p><small>${money(batch.cashCents / batch.units)} per machine · supplies &amp; delivery included</small></div>`).join("")}</div>
    <h3 class="cost-h2">What we still need to buy</h3>
    <p class="cost-note forecast-intro">Bars and items are ranked by cost. Expand an item for stock and source details. The cash budget and paid labor breakdown are below.</p>
    <div class="forecast-controls" hidden>
      <fieldset class="forecast-units"><legend>Batch</legend>${batches.map(batch => `<label><input type="radio" name="forecast-units" value="${batch.units}"${batch === first ? " checked" : ""}><span>${batch.units} machines</span></label>`).join("")}</fieldset>
      <label class="forecast-select">Group by<select id="forecast-group"><option value="category">Parts category</option><option value="supplier">Supplier</option></select></label>
      <label class="forecast-select">Supplier<select id="forecast-supplier"><option value="all">All suppliers</option>${data.suppliers.map(supplier => `<option value="${escape(supplier.id)}">${escape(supplier.name)}</option>`).join("")}</select></label>
      <label class="forecast-show-stock"><input type="checkbox" id="forecast-show-stock"> Include parts covered by stock</label>
    </div>
    <p class="forecast-result" role="status" aria-live="polite" hidden></p>
    ${batches.map(batch => renderPurchasePlan(batch, first.units)).join("")}
    <noscript><style>.forecast-groups[data-group-by="category"] .forecast-group[hidden], .forecast-part[hidden] { display: block !important; }</style></noscript>
    <p class="cost-note forecast-footnote">${star} Estimated stock, pricing or supply. Prices and quantities checked ${date}; availability details are below.</p>
    <details class="forecast-assumptions forecast-budget"><summary>Cash budget, delivery &amp; paid labor</summary>
      <p class="forecast-table-help">Scroll sideways to compare all three plans.</p>
      <div class="forecast-scroll" tabindex="0" role="region" aria-label="Batch expense comparison"><table class="forecast-comparison"><caption class="cost-sr-only">Batch expense forecast</caption><thead><tr><th scope="col">Expense</th>${batches.map(batch => `<th scope="col">${batch.units} machines</th>`).join("")}</tr></thead><tbody>
        ${tableRow("New whole parts & material purchases", "partsCents")}${tableRow("New inbound freight / import reserve", "inboundCents")}${tableRow(`Tax reserve on new purchases (${count(data.taxRate * 100)}%)`, "taxCents")}
        ${tableRow("New delivered purchases", "procurementCents", "forecast-subtotal")}
        ${tableRow("Possible unpaid balance on orders already placed", "pendingCents")}
        ${data.allowances.map(allowance => `<tr><th scope="row">${escape(allowance.name)}</th>${cells(batch => batch.allowances.find(other => other.id === allowance.id).costCents)}</tr>`).join("")}
        ${tableRow("Additional cash, supplies & delivery", "cashCents", "forecast-total")}
        ${first.laborCents !== null ? `<tr><th scope="row">Planned labor at ${money(Math.round(first.laborCents / first.laborHours))}/h<span>${batches.map(batch => count(batch.laborHours)).join(" / ")} attended hours</span></th>${cells(batch => batch.laborCents)}</tr>${tableRow("Including paid build labor", "totalCents", "forecast-total")}` : `<tr><th colspan="${batches.length + 1}">Labor estimate unavailable; add build labor to the purchase budget.</th></tr>`}
      </tbody></table></div>
      <p>New purchases include approximately ${batches.map(batch => `${money(batch.leftoverCents)} (${batch.units} machines)`).join(", ")} of excess stock, before freight and tax; it remains part of the cash outlay. The possible-payment reserve is released when those existing orders are confirmed paid. Paying for build labor adds the amount shown above.</p>
    </details>
    <details class="forecast-assumptions"><summary>Availability &amp; supply gaps${star}</summary>
      <div class="forecast-alert">${unavailable}${shortages ? `<p><strong>Stock limits for ${largest.units} machines${star}.</strong> ${escape(shortages)}</p>` : ""}<p>Exact Prime sources remain unresolved for several plumbing/refrigeration parts, the flow meter and short M3 inserts. Custom fabrication, PCB assembly and some harness/refrigeration selections use explicit allowances. Expand the relevant purchase for the item, quantity and source.</p></div>
    </details>
    <details class="forecast-assumptions"><summary>Inventory credits, pending orders &amp; allowances</summary>
      <p><b>Opening filament stock${star}:</b> approximately 12 kg Black PET-GF15, 4 kg Clear PETG and 10 kg Black PETG. Ten usable batch-2 boards, ten carbonator tube cuts, twenty endcaps and other credited parts reduce new orders. Remaining quantities from older purchase records are estimates; include parts covered by stock to see every credit.</p>
      <p>${escape(data.scope)}</p><p>${escape(data.inventoryNote)}</p><p>${escape(data.roundingNote)}</p>
      ${first.pendingPayments.map(payment => `<p><b>${escape(payment.name)} · ${money(payment.costCents)}${star}.</b> ${escape(payment.note)}</p>`).join("")}
      ${data.allowances.map(allowance => `<p><b>${escape(allowance.name)}${star}.</b> ${escape(allowance.note)}</p>`).join("")}
      <ul>${data.notes.map(note => `<li>${escape(note)}</li>`).join("")}</ul>
      <p>Filament includes a provisional 15% allowance for supports, purge and rejected prints. Finished printed parts without a counted usable balance receive no additional credit. Printed material totals and small colour splits require production-yield confirmation. Incomplete cuts and colour/size-specific stock may not supply another complete machine. ${data.bomRowCount} BOM lines are covered.</p>
    </details>
  </section>`;
}

export const BATCH_FORECAST_CSS = `
.cost-forecast { margin: 2.8rem 0 3rem; scroll-margin-top: 4.5rem; }
.forecast-cards { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1rem; margin: 1.5rem 0; }
.forecast-cards > div { border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; background: var(--surface); }
.forecast-cards [data-selected="true"] { border-color: var(--accent); }
.forecast-cards strong { display: block; font-size: clamp(1.15rem,3.2vw,2rem); color: var(--accent); font-variant-numeric: tabular-nums; margin-top: .3rem; }
.forecast-cards p { font-size: .85rem; margin: .6rem 0; }
.forecast-cards small, .forecast-comparison th span { color: var(--text-3); font-size: .75rem; }
.forecast-star { font-size: .75em; color: var(--accent); margin-left: .1em; }
.forecast-intro, .forecast-footnote { margin-bottom: 1rem; }
.forecast-controls:not([hidden]) { display: flex; flex-wrap: wrap; gap: .8rem 1rem; align-items: end; margin: 1rem 0 .75rem; }
.forecast-units { border: 0; padding: 0; margin: 0; display: flex; min-width: 0; }
.forecast-units legend, .forecast-select { font-size: .72rem; color: var(--text-2); }
.forecast-units legend { margin-bottom: .3rem; padding: 0; }
.forecast-units label { position: relative; cursor: pointer; }
.forecast-units input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.forecast-units span { display: block; padding: .55rem .65rem; border: 1px solid var(--border); background: var(--surface); font-size: .78rem; }
.forecast-units label:first-of-type span { border-radius: 6px 0 0 6px; }
.forecast-units label + label span { border-left: 0; }
.forecast-units label:last-of-type span { border-radius: 0 6px 6px 0; }
.forecast-units input:checked + span { background: var(--accent); color: var(--on-action); }
.forecast-units input:focus-visible + span { outline: 2px solid var(--action); outline-offset: 3px; }
.forecast-select { display: grid; gap: .3rem; min-width: 0; }
.forecast-select select { border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text); font: inherit; font-size: .78rem; padding: .55rem .5rem; width: 100%; min-width: 0; box-sizing: border-box; }
.forecast-select select:focus-visible { outline: 2px solid var(--action); outline-offset: 3px; }
.forecast-show-stock { flex-basis: 100%; display: flex; gap: .4rem; align-items: center; font-size: .75rem; color: var(--text-2); }
.forecast-show-stock input { accent-color: var(--accent); }
.forecast-result { font-size: .8rem; color: var(--text-2); margin: 1rem 0; }
.forecast-result b { color: var(--text); font-variant-numeric: tabular-nums; }
.forecast-plan > summary { cursor: pointer; padding: .8rem 0; font-size: .85rem; }
.cost-forecast[data-enhanced] .forecast-plan > summary { display: none; }
.forecast-group { border: 1px solid var(--border); border-radius: 8px; margin: .5rem 0; overflow: hidden; background: var(--surface); }
.forecast-group > summary { display: grid; grid-template-columns: minmax(120px,1.6fr) minmax(55px,2fr) 6.2rem 3.1rem .7rem; gap: .6rem; align-items: center; padding: .65rem .8rem; cursor: pointer; list-style: none; }
.forecast-group > summary:hover, .forecast-part > summary:hover { background: var(--surface-2); }
.forecast-group > summary::-webkit-details-marker, .forecast-part > summary::-webkit-details-marker { display: none; }
.forecast-group-name { font-size: .8rem; font-weight: 600; overflow-wrap: anywhere; }
.forecast-group .cost-bf { display: block; }
.forecast-group-cost, .forecast-group-percent, .forecast-part-cost { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.forecast-group-cost { font-size: .8rem; }
.forecast-group-percent { font-size: .7rem; color: var(--text-2); }
.forecast-marker { color: var(--text-2); text-align: right; font-size: .9rem; }
.forecast-marker::after { content: "+"; }
.forecast-group[open] > summary .forecast-marker::after, .forecast-part[open] > summary .forecast-marker::after { content: "−"; }
.forecast-item-scroll { max-height: 26rem; overflow-y: auto; overscroll-behavior: contain; scrollbar-gutter: stable; background: var(--bg); border-top: 1px solid var(--border); }
.forecast-item-scroll:focus-visible { outline: 2px solid var(--action); outline-offset: -2px; }
.forecast-part { border-bottom: 1px solid var(--border); }
.forecast-part:last-child { border-bottom: 0; }
.forecast-part > summary { display: grid; grid-template-columns: minmax(0,1fr) 10rem 5.6rem .7rem; align-items: start; gap: .65rem; padding: .5rem .8rem; cursor: pointer; list-style: none; font-size: .76rem; line-height: 1.45; }
.forecast-part-name { min-width: 0; display: flex; align-items: baseline; }
.forecast-part-name > span { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; overflow-wrap: anywhere; }
.forecast-part-qty { color: var(--text-2); text-align: right; font-size: .72rem; overflow-wrap: anywhere; }
.forecast-part-evidence { margin: .4rem .8rem 1rem; padding: .75rem; border-radius: 6px; background: var(--surface); font-size: .75rem; line-height: 1.6; color: var(--text-2); overflow-wrap: anywhere; }
.forecast-part-evidence p { margin: .5rem 0; }
.forecast-part-evidence ul { margin: .5rem 0; padding-left: 1.2rem; }
.forecast-part-evidence li { margin: .3rem 0; }
.forecast-stock { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: .6rem; margin: .8rem 0; font-variant-numeric: tabular-nums; }
.forecast-stock dt { font-size: .68rem; color: var(--text-3); }
.forecast-stock dd { margin: .15rem 0 0; color: var(--text); }
.forecast-source-note { border-top: 1px solid var(--border); color: var(--text-2); font-size: .72rem; }
.forecast-source-note > summary { cursor: pointer; padding: .5rem .8rem; }
.forecast-source-note p { margin: .6rem .8rem; line-height: 1.6; }
.forecast-scroll { overflow-x: auto; max-width: 100%; padding: 0 .8rem; }
.forecast-scroll:focus-visible { outline: 2px solid var(--action); outline-offset: -2px; }
.forecast-table-help { display: none; }
.forecast-comparison { width: 100%; min-width: 28rem; border-collapse: collapse; font-size: .8rem; }
.forecast-comparison th { text-align: left; font-weight: 500; }
.forecast-comparison th:first-child { width: 35%; }
.forecast-comparison td, .forecast-comparison th { padding: .7rem .45rem; border-bottom: 1px solid var(--border); vertical-align: top; }
.forecast-comparison td { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.forecast-comparison thead th:not(:first-child) { text-align: right; }
.forecast-comparison thead th { white-space: nowrap; }
.forecast-comparison th span { display: block; margin-top: .3rem; }
.forecast-subtotal, .forecast-total { background: var(--surface); }
.forecast-total td, .forecast-total th { font-weight: 700; }
.forecast-alert { padding: .7rem .8rem; border-left: 3px solid var(--accent); background: var(--surface); font-size: .8rem; line-height: 1.65; margin: .8rem; }
.forecast-alert p { margin: .4rem 0; }
.forecast-assumptions { border: 1px solid var(--border); border-radius: 8px; margin: .5rem 0; scroll-margin-top: 4.5rem; }
.forecast-assumptions > summary { padding: .8rem; cursor: pointer; font-size: .8rem; }
.forecast-assumptions > p, .forecast-assumptions > ul { font-size: .78rem; line-height: 1.65; color: var(--text-2); margin: .8rem; }
.forecast-assumptions li { margin: .5rem 0; }
@media (max-width: 560px) {
  .forecast-cards { grid-template-columns: repeat(2,minmax(0,1fr)); gap: .6rem; }
  .forecast-cards > div:first-child { grid-column: 1 / -1; }
  .forecast-cards > div { padding: .85rem .65rem; }
  .forecast-cards strong { font-size: clamp(1.15rem,5.5vw,1.8rem); }
  .forecast-cards p { font-size: .75rem; }
  .forecast-cards small { font-size: .68rem; }
  .forecast-controls:not([hidden]) { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }
  .forecast-units { grid-column: 1 / -1; }
  .forecast-show-stock { grid-column: 1 / -1; }
  .forecast-group > summary { grid-template-columns: minmax(0,1fr) 5.6rem 2.6rem .6rem; grid-template-areas: "name name name marker" "bar cost pct marker"; gap: .45rem; }
  .forecast-group-name { grid-area: name; }
  .forecast-group > summary > .cost-bt { grid-area: bar; height: 10px; }
  .forecast-group-cost { grid-area: cost; }
  .forecast-group-percent { grid-area: pct; }
  .forecast-group > summary > .forecast-marker { grid-area: marker; }
  .forecast-part > summary { grid-template-columns: minmax(0,1fr) 4.9rem .5rem; grid-template-areas: "name cost marker" "qty qty marker"; gap: .2rem .5rem; padding: .5rem .6rem; }
  .forecast-part-name { grid-area: name; }
  .forecast-part-cost { grid-area: cost; }
  .forecast-part-qty { grid-area: qty; text-align: left; }
  .forecast-part > summary > .forecast-marker { grid-area: marker; }
  .forecast-stock { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .forecast-part-evidence { margin: .3rem .6rem .7rem; padding: .65rem; }
  .forecast-comparison { font-size: .7rem; }
  .forecast-table-help { display: block; }
  .forecast-comparison th, .forecast-comparison td { padding: .65rem .15rem; }
  .forecast-scroll { padding: 0 .4rem; }
}
`;
