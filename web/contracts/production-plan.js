// Production scenarios project cumulative material coverage and proposed purchase packs without changing stock.
import { optimizePurchase, lotCost } from './purchase-lots.js';

export const EPSILON = 1e-8;
export const optionKey = option => JSON.stringify([option.quantity, option.priceCents, option.label]);
export const usable = row => Number.isFinite(row.available) ? Math.max(0, row.available) : 0;
export const amountNeeded = (row, units) => row.needs[units] || 0;
export const freshScenario = () => ({ finish: 'white', focus: 2, horizon: 10, buyFor: 2, orders: {}, custom: {} });

export function purchaseFor(row, scenario) {
  const packs = (row.quote?.options || []).map(option => ({
    option, count: scenario.orders?.[row.id]?.[optionKey(option)] || 0,
  })).filter(pack => Number.isSafeInteger(pack.count) && pack.count > 0);
  const custom = scenario.custom?.[row.id];
  if (custom && Number.isFinite(custom.quantity) && custom.quantity > 0 && Number.isSafeInteger(custom.count) && custom.count > 0) {
    packs.push({ option: { quantity: custom.quantity, priceCents: Number.isSafeInteger(custom.priceCents) && custom.priceCents > 0 ? custom.priceCents : null, label: 'Custom pack', custom: true }, count: custom.count });
  }
  const usableQuantity = packs.filter(pack => pack.option.available !== false).reduce((sum, pack) => sum + pack.count * pack.option.quantity, 0);
  const quantity = packs.reduce((sum, pack) => sum + pack.count * pack.option.quantity, 0);
  const costCents = packs.reduce((sum, pack) => sum + (pack.option.priceCents == null ? 0 : lotCost(pack.option, pack.count)), 0);
  return { packs, quantity, usableQuantity, costCents, unpriced: packs.some(pack => pack.option.priceCents == null),
    unavailable: packs.some(pack => pack.option.available === false), custom: packs.some(pack => pack.option.custom) };
}

export function materialBalance(row, units, purchase = { quantity: 0 }) {
  const required = amountNeeded(row, units), before = amountNeeded(row, units - 1);
  const reusable = row.reusableNeeds?.[units] || 0;
  const consumed = Math.max(0, required - reusable);
  const previousConsumed = Math.max(0, before - (row.reusableNeeds?.[units - 1] || 0));
  const supplied = usable(row) + (row.incoming || 0) + (purchase.usableQuantity ?? purchase.quantity);
  return { required, reusable, consumed, previousConsumed, added: Math.max(0, required - before),
    onHandBefore: Math.max(0, usable(row) - previousConsumed), projectedAfter: row.quantityKnown ? Math.max(0, supplied - consumed) : null,
    atLeast: row.available == null };
}

export function coverageFor(row, units, purchase = { quantity: 0 }) {
  const needed = amountNeeded(row, units), onHand = usable(row), incoming = row.incoming || 0;
  if (needed <= EPSILON && (row.quantityKnown || !row.active?.[units])) return 'unused';
  if (!row.quantityKnown) return 'unknown';
  if (onHand + EPSILON >= needed) return row.estimated ? 'estimate' : 'stock';
  if (onHand + incoming + EPSILON >= needed) return 'incoming';
  if (onHand + incoming + (purchase.usableQuantity ?? purchase.quantity) + EPSILON >= needed) return 'planned';
  return row.available == null ? 'unknown' : 'short';
}

export function remainingPurchase(row, units, purchase = { quantity: 0 }) {
  if (!row.quantityKnown || !row.quote?.options?.length) return null;
  const short = Math.max(0, amountNeeded(row, units) - usable(row) - (row.incoming || 0) - (purchase.usableQuantity ?? purchase.quantity));
  if (short <= EPSILON) return { quantity: 0, costCents: 0, packages: [] };
  return optimizePurchase(short, row.quote.options);
}

export function fillPurchasePlan(data, scenario, units) {
  const next = structuredClone(scenario);
  next.buyFor = units;
  for (const row of data.finishes[next.finish].rows) {
    const customOnly = { ...next, orders: {} };
    const suggestion = remainingPurchase(row, units, purchaseFor(row, customOnly));
    delete next.orders[row.id];
    if (suggestion?.packages.length && suggestion.packages.every(pack => pack.option.available !== false)) next.orders[row.id] = Object.fromEntries(suggestion.packages.map(pack => [optionKey(pack.option), pack.count]));
  }
  return next;
}

export function projectProduction(data, scenario) {
  const rows = data.finishes[scenario.finish].rows.map(row => ({ ...row, purchase: purchaseFor(row, scenario) }));
  const units = Array.from({ length: data.horizon }, (_, i) => {
    const quantity = i + 1, counts = { stock: 0, estimate: 0, incoming: 0, planned: 0, short: 0, unknown: 0 };
    let extraPartsCents = 0, baselinePartsCents = 0, unquoted = 0, unavailable = 0, definitions = 0, usageUnknown = 0, countUnknown = 0;
    for (const row of rows) {
      const status = coverageFor(row, quantity, row.purchase);
      if (status === 'unused') continue;
      counts[status]++;
      if (status === 'unknown') { if (row.material) definitions++; else if (!row.quantityKnown) usageUnknown++; else countUnknown++; }
      const remaining = remainingPurchase(row, quantity, row.purchase);
      const baseline = remainingPurchase(row, quantity);
      if (remaining) {
        extraPartsCents += remaining.costCents;
        if (remaining.packages.some(pack => pack.option.available === false)) unavailable++;
      } else if (!['stock', 'estimate', 'incoming', 'planned'].includes(status)) unquoted++;
      if (baseline) baselinePartsCents += baseline.costCents;
    }
    return { quantity, counts, lines: Object.values(counts).reduce((a, b) => a + b, 0), extraPartsCents, baselinePartsCents, unquoted, unavailable, definitions, usageUnknown, countUnknown,
      ready: !counts.short && !counts.unknown && !counts.incoming && !counts.planned && !counts.estimate,
      covered: !counts.short && !counts.unknown };
  });
  const buying = rows.filter(row => row.purchase.quantity > EPSILON);
  const partsCents = buying.reduce((sum, row) => sum + row.purchase.costCents, 0);
  const activeSuppliers = new Set(buying.map(row => row.quote?.supplier).filter(Boolean));
  const freight = data.suppliers.filter(s => activeSuppliers.has(s.id)).map(s => {
    const bracket = Object.keys(s.shippingCents).map(Number).sort((a, b) => a - b).find(n => n >= scenario.buyFor) || data.horizon;
    return { id: s.id, name: s.name, bracket, cents: s.shippingCents[String(bracket)] || 0 };
  });
  const freightCents = freight.reduce((sum, row) => sum + row.cents, 0);
  const merchandise = buying.reduce((sum, row) => sum + row.purchase.packs.reduce((parts, pack) => parts + (pack.option.priceCents != null && (pack.option.custom || row.quote?.priceBasis !== 'delivered') ? lotCost(pack.option, pack.count) : 0), 0), 0);
  const taxCents = Math.round((merchandise + freightCents) * data.taxRate);
  return { rows, units, buying, budget: { partsCents, freightCents, taxCents, totalCents: partsCents + freightCents + taxCents, freight,
    unpriced: buying.filter(row => row.purchase.unpriced).length, unavailable: buying.filter(row => row.purchase.unavailable).length },
    firstShort: units.find(unit => unit.counts.short || unit.counts.unknown)?.quantity || null };
}
