// /build shows which materials a requested part or assembly can draw from stock and what is missing.
import { readMaterialCatalog } from "./material-catalog.js";
import { readPartCosts } from "./part-costs.js";
import { readMaterialStock } from "./material-stock.js";
import { materialIndex } from "../contracts/materials.js";
import { planMaterial, materialCapacity, stockSummary } from "../contracts/material-stock.js";
import { duration } from "../contracts/part-costs.js";
import { renderHead, renderNav, renderPageHeader, renderFooter } from "./shell.js";

const escape = value => String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const amount = (value, unit = "ea") => value == null ? "Not recorded" : `${Number(value.toFixed(3)).toLocaleString("en-US")} ${unit}`;
const materialHref = id => "/3d#material:" + encodeURIComponent(id) + "?panel=materials&tab=stock";
const buildHref = (id, finish) => "/build?material=" + encodeURIComponent(id) + "&finish=" + finish + "#plan";
const number = value => Number(value).toLocaleString("en-US");

function renderSources(resource) {
  const sources = (resource.sources || []).map(source => {
    const relative = source.path?.replace(/^hardware\//, "");
    if (!relative) return "";
    return `<a href="https://github.com/derekbreden/homesodamachine/blob/main/hardware/${escape(relative)}${source.line ? "#L" + source.line : ""}">${escape(relative.split("/").pop())}</a>`;
  });
  return sources.length ? `<p class="stock-evidence">Evidence: ${[...new Set(sources)].join(" · ")}</p>` : "";
}

function renderSupply(row, stock, index) {
  const resource = stock.resources[row.resource];
  const state = row.status === "short" ? `${amount(row.short, resource.unit)} short`
    : row.status === "unknown" ? row.quantityKnown ? "Count needed" : "Usage needed" : row.estimated ? "Covered · estimate" : "Covered";
  const uses = row.uses.map(id => `<a href="${materialHref(id)}">${escape(index.get(id)?.description || id)}</a>`).join(", ");
  return `<li class="stock-supply" data-status="${row.status}"><details>
    <summary><span class="stock-supply-name">${escape(resource.name)}</span><span class="stock-state">${escape(state)}</span>
      <span class="stock-supply-count">${row.quantityKnown ? "Need " + escape(amount(row.needed, resource.unit)) : "Usage not recorded"} · Available ${escape(amount(row.available, resource.unit))}${resource.incoming ? ` · ${escape(amount(resource.incoming, resource.unit))} incoming` : ""}</span></summary>
    <div class="stock-detail"><p>Used by ${uses}.</p>
      <p>${escape(resource.note)}</p>${resource.asOf ? `<p>Balance dated ${escape(resource.asOf)}${resource.estimated ? " · estimate" : ""}.</p>` : ""}
      ${resource.reserved ? `<p>${escape(amount(resource.reserved, resource.unit))} reserved.</p>` : ""}
      ${!row.quantityKnown ? `<p>The required usable quantity has not been established in this stock unit.</p>` : ""}
      ${renderSources(resource)}${resource.href ? `<p><a href="${escape(resource.href)}">Supplier listing</a></p>` : ""}</div>
  </details></li>`;
}

function renderPlan(catalog, plan) {
  const index = materialIndex(catalog), material = index.get(plan.material), stock = catalog.stock;
  const capacity = materialCapacity(catalog, material.id, plan.options);
  const completionMinutes = catalog.costs.direct[material.id]?.minutes;
  const completed = stock.builds.filter(run => run.material === material.id && (!run.finish || run.finish === plan.options.finish)
    && Number.isFinite(run.quantity) && run.quantity > 0);
  const runs = completed.filter(run => Number.isFinite(run.attendedMinutes));
  const actual = runs.length ? runs.reduce((sum, run) => sum + run.attendedMinutes, 0) / runs.reduce((sum, run) => sum + run.quantity, 0) : null;
  const shortages = plan.resources.filter(row => row.status === "short");
  const unknown = plan.resources.filter(row => row.status === "unknown");
  const covered = plan.resources.filter(row => row.status === "covered");
  const make = plan.materials.filter(row => row.make > 0);
  const credited = plan.materials.filter(row => row.fromStock > 0);
  const list = rows => `<ul class="stock-supplies">${rows.map(row => renderSupply(row, stock, index)).join("")}</ul>`;
  return `<article class="build-plan" id="plan" data-material="${material.id}">
    <div class="build-plan-heading"><div><p class="build-number">${material.id} · ${number(plan.quantity)} requested</p><h2>${escape(material.description)}</h2></div>
      <a class="build-part-link" href="${materialHref(material.id)}">Explore part →</a></div>
    ${material.bom?.scope ? `<p class="build-scope">${escape(material.bom.scope)}</p>` : ""}
    <p class="build-verdict" data-status="${plan.status}">${stockSummary(plan)}</p>
    <div class="build-metrics">
      <div><span>Material capacity</span><strong>${capacity ? `${number(capacity.quantity)}${capacity.estimated ? " · estimate" : ""}` : "Needs stock records"}</strong></div>
      <div><span>Allocated completion work / item</span><strong>${completionMinutes ? duration(completionMinutes) : "Not allocated"}</strong></div>
      <div><span>Recorded completion work / item</span><strong>${actual == null ? "No measured runs" : duration(actual)}</strong></div>
    </div>
    <p class="build-note">Completion work starts with the recorded inputs and ends with this completed item. Work already performed on its components is recorded with those components.</p>
    ${completed.length ? `<details class="build-covered"><summary>Recorded completions <span>${completed.length}</span></summary><ul class="build-work">${completed.map(run => `<li><div>${escape(new Date(run.completedAt).toLocaleString("en-US", {timeZone:"America/Chicago"}))}<small>${escape(run.note || "Completed work")}</small><small>Inputs: ${run.inputs.map(input => escape((input.resource ? stock.resources[input.resource]?.name : index.get(input.material)?.description) || input.resource || input.material) + " · " + amount(input.quantity, input.unit)).join("; ")}</small></div><span>${amount(run.quantity)} · ${run.attendedMinutes == null ? "Time not measured" : duration(run.attendedMinutes)}</span></li>`).join("")}</ul></details>` : ""}
    ${shortages.length ? `<section><h3>Short of stock</h3>${list(shortages)}</section>` : ""}
    ${unknown.length || plan.gaps.length ? `<section><h3>Stock records needed</h3>${list(unknown)}
      <ul class="stock-gaps">${plan.gaps.map(gap => `<li><a href="${materialHref(gap.material)}">${escape(index.get(gap.material)?.description || gap.material)}</a><span>${escape(gap.reason)}</span></li>`).join("")}</ul></section>` : ""}
    ${covered.length ? `<details class="build-covered"><summary>Covered materials <span>${number(covered.length)}</span></summary>${list(covered)}</details>` : ""}
    ${credited.length ? `<section><h3>Completed stock used</h3><ul class="build-work">${credited.map(row => `<li><a href="${materialHref(row.material)}">${escape(index.get(row.material)?.description || row.material)}</a><span>${amount(row.fromStock)}</span></li>`).join("")}</ul></section>` : ""}
    ${make.length ? `<details class="build-covered"><summary>Parts and assemblies to make <span>${number(make.length)}</span></summary><ul class="build-work">${make.map(row => `<li><a href="${buildHref(row.material, plan.options.finish)}">${escape(index.get(row.material)?.description || row.material)}<small>${row.material}</small></a><span>${amount(row.make)}</span></li>`).join("")}</ul></details>` : ""}
    <p class="build-note">Each plan starts with the same balances and reserves no stock. Incoming orders are shown separately. Material coverage leaves fabrication, fit and operation completion to the assembly records.</p>
  </article>`;
}

function renderWorkbench(plan) {
  return `<section class="stock-workbench" id="stock-workbench" data-material="${plan.material}" data-quantity="${plan.quantity}" data-finish="${plan.options.finish}">
    <h2>Record physical work</h2><p class="build-note">Record what was completed and the inputs actually used. Component quantities are prefilled; adjust them for the work you did.</p>
    <form id="stock-completion"><h3>Complete this item</h3><p class="stock-output"></p>
      <details class="stock-inputs"><summary>Inputs used <span id="stock-input-count"></span></summary><div id="stock-input-list"></div><button type="button" id="stock-add-input">Add an input</button></details>
      <div class="stock-fields"><label>Hands-on minutes<input id="stock-minutes" type="number" min="0" step="any" placeholder="Leave blank if not measured"></label><label>Completed at<input id="stock-completed-at" type="datetime-local" required></label></div>
      <label>Work note<textarea id="stock-work-note" rows="2" placeholder="Describe preparation, rework or anything the timing includes"></textarea></label>
      <button type="submit">Record and publish completion</button><button type="button" id="stock-another" hidden>Record another completion</button>
    </form>
    <details class="stock-count-panel"><summary>Record a receipt or stock count</summary><form id="stock-count">
      <label>Stock item<select id="stock-count-target"></select></label><div class="stock-fields"><label>Activity<select id="stock-count-kind"><option value="receipt">Received</option><option value="count">Counted on hand</option></select></label><label>Quantity <span id="stock-count-unit"></span><input id="stock-count-quantity" type="number" min="0" step="any" required></label></div>
      <label>Record note<input id="stock-count-note" placeholder="Receipt or physical count evidence"></label><button type="submit">Record and publish stock</button>
    </form></details>
    <p class="stock-record-status" role="status" aria-live="polite"></p><button type="button" id="stock-publish-retry" hidden>Retry publication</button>
  </section>`;
}

export function mountBuildRoutes(app, { hardwareDir, canRecord = false }) {
  function read() {
    const catalog = readMaterialCatalog(hardwareDir);
    catalog.costs = readPartCosts(hardwareDir, catalog);
    catalog.stock = readMaterialStock(hardwareDir, catalog);
    return catalog;
  }
  function request(catalog, query) {
    const id = typeof query.material === "string" ? query.material : catalog.cost_root;
    const quantity = query.quantity == null ? 1 : Number(query.quantity);
    const finish = query.finish === "black" ? "black" : "white";
    if (!materialIndex(catalog).has(id) || !Number.isSafeInteger(quantity) || quantity < 1)
      return null;
    return planMaterial(catalog, id, quantity, { finish });
  }
  app.get("/api/build", (req, res) => {
    res.set("Cache-Control", "no-cache");
    const catalog = read(), plan = request(catalog, req.query);
    if (!plan) return res.status(400).json({ error: "Choose a material and a positive whole quantity" });
    res.json({ ...plan, capacity: materialCapacity(catalog, plan.material, plan.options) });
  });
  app.get("/build", (req, res) => {
    res.set("Cache-Control", "no-cache");
    const catalog = read(), plan = request(catalog, req.query);
    if (!plan) return res.status(400).type("text").send("Choose a material and a positive whole quantity");
    const materials = [...catalog.materials].sort((a, b) => a.description.localeCompare(b.description));
    const costed = new Set(catalog.costs.costed);
    const assemblies = materials.filter(material => material.kind === "assembly" && costed.has(material.id));
    const assemblyCards = assemblies.map(material => {
      const candidate = planMaterial(catalog, material.id, 1, plan.options);
      return `<a class="build-assembly" href="${buildHref(material.id, plan.options.finish)}"><span class="build-number">${material.id}</span><strong>${escape(material.description)}</strong><span class="stock-state" data-status="${candidate.status}">${stockSummary(candidate)}</span></a>`;
    }).join("");
    res.type("html").send(renderHead({ title: "Build from stock · Home Soda Machine", pageClass: "site-interior", pageHead: '<link rel="stylesheet" href="/css/build.css">' })
      + renderNav({ active: "parts" })
      + renderPageHeader({ eyebrow: "Materials & assembly", title: "What can we build?", description: "Choose a part or completed assembly to see the materials on hand, the work to make it, and what is missing." })
      + `<main class="build-wrap site-content"><form class="build-form" method="get" action="/build">
        <label>Part or assembly<select name="material">${materials.map(material => `<option value="${material.id}"${material.id === plan.material ? " selected" : ""}>${material.id} · ${escape(material.description)}</option>`).join("")}</select></label>
        <label>Quantity<input name="quantity" type="number" min="1" step="1" value="${plan.quantity}" required></label>
        <label>Faucet finish<select name="finish"><option value="white"${plan.options.finish === "white" ? " selected" : ""}>White</option><option value="black"${plan.options.finish === "black" ? " selected" : ""}>Black</option></select></label><button type="submit">Check stock</button></form>
        <p class="build-opening">${escape(catalog.stock.opening.note)} <a href="https://github.com/derekbreden/homesodamachine/blob/main/hardware/ledger/stock.md">About stock and build records →</a></p>
        ${renderPlan(catalog, plan)}${canRecord ? renderWorkbench(plan) : ""}<section class="build-assemblies"><h2>Build an assembly</h2><p>Each assembly below is an independent stock plan.</p><div>${assemblyCards}</div></section></main>${canRecord ? '<script type="module" src="/stock-entry.js"></script>' : ""}`
      + renderFooter({ siteFooter: true }));
  });
}
