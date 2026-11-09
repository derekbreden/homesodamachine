// Purchase lots price and compare the supplier pack sizes shared by planning and purchasing.
const gcd = (a, b) => b ? gcd(b, a % b) : a;


export function lotCost(option, lots) {
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

