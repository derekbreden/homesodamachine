// The purchasing forecast turns shared net material demand into supplier lots and a quoted cash budget.
import fs from "node:fs";
import path from "node:path";
import { runMinutes } from "../contracts/part-costs.js";
import { readStockLedger } from "./stock-ledger.js";
import { readMaterialCatalog } from "./material-catalog.js";
import { readMaterialStock } from "./material-stock.js";
import { planMaterial } from "../contracts/material-stock.js";

const gcd = (a, b) => b ? gcd(b, a % b) : a;

// Attended minutes a machine takes when `units` are built together. An
// operation with a run spreads each setup over that batch's pieces; every other
// operation is its ledger minutes. A labor figure without operations is flat.
export function laborMinutes(labor, units) {
  const ops = (labor.cats || []).flatMap(cat => cat.ops);
  if (!ops.length) return labor.minutes;
  return ops.reduce((total, op) => total + (op.run ? runMinutes(op.run, units) : op.minutes), 0);
}

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
  if (![5, 10, 20].includes(units)) throw new RangeError("Forecast supports batches of 5, 10 or 20");
  if (!Number.isFinite(data.taxRate) || data.taxRate < 0 || data.taxRate > 1) throw new RangeError("Invalid tax reserve");
  const suppliers = data.suppliers.map(supplier => ({ ...supplier, rows: [], costCents: 0, shippingCents: supplier.shippingCents[String(units)] }));
  if (suppliers.some(supplier => !Number.isInteger(supplier.shippingCents) || supplier.shippingCents < 0)) throw new RangeError("Invalid freight reserve");
  let merchandiseCents = 0;
  let leftoverCents = 0;
  const rows = data.items.map(item => {
    const required = item.fixedQuantity ?? item.perUnit * units * (1 + (item.materialAllowance || 0));
    const onHand = item.inventory?.onHand ?? null;
    const incoming = item.inventory?.incoming ?? 0;
    const available = onHand == null ? 0 : Math.max(0, onHand - (item.inventory?.reserved || 0));
    if (![required, available, incoming].every(n => Number.isFinite(n) && n >= 0) || (onHand != null && onHand < 0 && !item.inventory?.needsCount)) throw new RangeError("Invalid requirement or inventory credit");
    const openingStock = available + incoming;
    const shortfall = Math.max(0, required - openingStock);
    const target = Math.max(shortfall, (item.minimumPurchaseQuantity?.[String(units)] || 0) - openingStock);
    let purchase = target > 1e-8 ? optimizePurchase(target, item.options) : { quantity: 0, costCents: 0, packages: [] };
    purchase.required = required;
    purchase.remaining = Math.max(0, openingStock + purchase.quantity - required);
    const issues = [];
    if (item.status === "unavailable" || purchase.packages.some(pack => pack.option.available === false)) issues.push(purchase.quantity ? "Out of stock; replenishment price estimated." : "Supplier out of stock; this plan relies on the credited inventory.");
    if (item.status === "unconfirmed" && purchase.quantity) issues.push("Exact Prime offer unconfirmed; historical delivered-price allowance.");
    if (item.status === "estimate") issues.push("Estimated quantity, price or compatibility; see note.");
    if (item.inventory?.estimated) issues.push("Remaining usable inventory is estimated; see stock note.");
    if (item.requirementUnknown) issues.push("Usable input quantity is unresolved; the physical planning allowance is provisional.");
    if (incoming) issues.push("Already ordered; delivery pending. Arrival is required before assembly.");
    for (const pack of purchase.packages) {
      if (pack.option.listedPackages !== undefined && pack.count > pack.option.listedPackages) {
        const missing = pack.count - pack.option.listedPackages;
        issues.push(`Listed stock: ${pack.option.listedPackages} lots; ${missing} more ${missing === 1 ? "lot needs" : "lots need"} a source or replenishment.`);
      }
    }
    const row = { ...item, ...purchase, onHand, available, incoming, openingStock, shortfall, issues, estimated: issues.length > 0 };
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
  const minutes = labor ? laborMinutes(labor, units) : 0;
  const laborHours = labor && labor.rate > 0 && labor.opCount > 0 && minutes > 0 ? minutes / 60 * units : null;
  const laborCents = laborHours === null ? null : Math.round(laborHours * labor.rate * 100);
  return { units, rows, suppliers, allowances, pendingPayments, pendingCents, partsCents, inboundCents, taxCents, procurementCents, cashCents, leftoverCents: Math.round(leftoverCents), laborHours, laborCents, totalCents: laborCents === null ? null : cashCents + laborCents };
}

export function readBatchForecast(hardwareDir, labor) {
  const data = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger", "batch-forecast.json"), "utf8"));
  const stock = readStockLedger(hardwareDir);
  const catalog = readMaterialCatalog(hardwareDir);
  catalog.stock = readMaterialStock(hardwareDir, catalog);
  const index = new Map(catalog.materials.map(material => [material.id, material]));
  for (const item of data.items) {
    const balance = catalog.stock.resources[item.stock];
    item.inventory = { ...balance, note: balance.note || "No stock count recorded" };
    item.unit = balance.unit;
    item.perUnit = balance.planning.perUnit;
    item.materialAllowance = balance.planning.materialAllowance;
    item.category = balance.category || "supplies";
  }
  data.inventoryAsOf = stock.asOf.slice(0, 10);
  const offered = new Set(data.items.map(item => item.stock));
  const batches = [5, 10, 20].map(units => {
    const plan = planMaterial(catalog, catalog.cost_root, units, { finish: "white" });
    const needs = new Map(plan.resources.map(row => [row.resource, row]));
    const gross = planMaterial({ ...catalog, stock: { ...catalog.stock, materials: {} } }, catalog.cost_root, units, { finish: "white" });
    const grossNeeds = new Map(gross.resources.map(row => [row.resource, row]));
    const remaining = plan.materials.find(row => row.material === catalog.cost_root)?.make || 0;
    const items = data.items.map(item => {
      const need = needs.get(item.stock);
      const fixedQuantity = !need ? 0 : need.quantityKnown ? need.needed : item.perUnit * remaining * (1 + (item.materialAllowance || 0));
      const reserve = catalog.stock.resources[item.stock].planning?.purchaseReserve?.[String(units)];
      const original = grossNeeds.get(item.stock);
      const fraction = need?.quantityKnown && original?.quantityKnown && original.needed > 0 ? need.needed / original.needed : remaining / units;
      return { ...item, fixedQuantity, requirementUnknown: Boolean(need && !need.quantityKnown),
        minimumPurchaseQuantity: need && reserve ? { [units]: reserve * fraction } : null };
    });
    const batch = calculateBatch({ ...data, items: items.filter(item => needs.has(item.stock)) }, units, labor);
    batch.unpriced = plan.resources.filter(row => !offered.has(row.resource)).flatMap(row => {
      const resource = catalog.stock.resources[row.resource];
      const short = row.quantityKnown ? Math.max(0, row.needed - (resource.available || 0) - (resource.incoming || 0)) : null;
      return short === 0 ? [] : [{ id: row.resource, name: resource.name, quantity: short, unit: resource.unit, href: resource.href }];
    });
    batch.undefinedInputs = plan.gaps.map(gap => ({ ...gap, name: index.get(gap.material)?.description || gap.material }));
    batch.requirementUnknown = batch.rows.some(row => row.requirementUnknown);
    return batch;
  });
  return { data, batches, bomChanged: false };
}

export { renderBatchForecast, BATCH_FORECAST_CSS } from "./batch-forecast-view.js";
