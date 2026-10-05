import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

const gcd = (a, b) => b ? gcd(b, a % b) : a;

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
  const bomLines = bom.split("\n");
  for (const item of data.items) {
    item.category = item.bomLines.map(line => bomLines[line - 1]?.match(/<!--@([a-z][a-z-]*)-->/)?.[1]).find(Boolean) || "supplies";
  }
  return { data, bomChanged, batches: [5, 10, 20].map(units => calculateBatch(data, units, labor)) };
}

export { renderBatchForecast, BATCH_FORECAST_CSS } from "./batch-forecast-view.js";
