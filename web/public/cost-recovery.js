// Shared by the server-rendered cost page and its browser controls. All recovery
// arithmetic uses whole cents; a partially funded machine rounds up to a sale.
export const SALE_PRICE = 4495;
export const INVESTMENT_SCENARIO = 80000;
export const SALES_HORIZON = 50;

export function dollars(value, decimals = 2) {
  return value.toLocaleString("en-US", {
    style: "currency", currency: "USD",
    minimumFractionDigits: decimals, maximumFractionDigits: decimals,
  });
}

export function recoveryPlan({ unitCost, investment, units = 25 }) {
  for (const value of [unitCost, investment, units]) {
    if (!Number.isFinite(value) || value < 0) throw new RangeError("Recovery inputs must be nonnegative finite numbers");
  }
  if (!Number.isInteger(units)) throw new RangeError("Sales must be whole machines");
  const costCents = Math.round(unitCost * 100);
  const contributionCents = SALE_PRICE * 100 - costCents;
  const investmentCents = Math.round(investment * 100);
  // If recorded spending grows past the scenario, it remains the recovery target.
  const targetCents = Math.max(investmentCents, INVESTMENT_SCENARIO * 100);
  const recordedUnits = contributionCents > 0 ? Math.ceil(investmentCents / contributionCents) : null;
  const targetUnits = contributionCents > 0 ? Math.ceil(targetCents / contributionCents) : null;
  return {
    investment: investmentCents / 100,
    target: targetCents / 100,
    unitCost: costCents / 100,
    contribution: contributionCents / 100,
    recordedUnits, targetUnits,
    units,
    available: units * contributionCents / 100,
    balance: (units * contributionCents - investmentCents) / 100,
  };
}

export function recoveryRange(plan) {
  if (plan.recordedUnits === null) return "No recovery";
  return plan.recordedUnits === plan.targetUnits
    ? String(plan.recordedUnits)
    : `${plan.recordedUnits}\u2013${plan.targetUnits}`;
}

export function recoverySummary(plan) {
  if (plan.recordedUnits === null) {
    return "At this per-machine cost, each sale leaves no money to recover the investment.";
  }
  const first = `${plan.recordedUnits} machines cover the ${dollars(plan.investment)} recorded so far`;
  return plan.investment < plan.target
    ? `${first}; ${plan.targetUnits} cover ${dollars(plan.target, 0)} in total investment.`
    : `${first}.`;
}

export function salesBalance(plan) {
  return plan.balance < 0
    ? `${dollars(-plan.balance, 0)} of recorded investment still to recover`
    : `${dollars(plan.balance, 0)} beyond the recorded investment`;
}

// The target band is cash invested; the rising line is cumulative price less
// the modeled cost of every machine, including any additional per-machine costs.
// The fixed sales horizon makes scenarios directly comparable on the x axis.
export function renderRecoveryChart(plan) {
  const left = 64, right = 706, top = 28, bottom = 290;
  const high = Math.max(plan.target, plan.contribution * SALES_HORIZON, 10000);
  const low = Math.min(0, plan.contribution * SALES_HORIZON);
  const step = Math.ceil((high - low) / 5 / 10000) * 10000;
  const yMax = Math.ceil(high / step) * step;
  const yMin = Math.floor(low / step) * step;
  const x = (units) => left + units / SALES_HORIZON * (right - left);
  const y = (value) => bottom - (value - yMin) / (yMax - yMin) * (bottom - top);
  const f = (n) => n.toFixed(2);
  const tick = (n) => n === 0 ? "$0" : `${n < 0 ? "\u2212" : ""}$${Math.abs(n / 1000)}k`;
  const grid = [];
  for (let value = yMin; value <= yMax; value += step) {
    grid.push(`<line class="recovery-grid" x1="${left}" y1="${f(y(value))}" x2="${right}" y2="${f(y(value))}" />
      <text class="recovery-axis" x="${left - 12}" y="${f(y(value) + 4)}" text-anchor="end">${tick(value)}</text>`);
  }
  for (let units = 0; units <= SALES_HORIZON; units += 10) {
    grid.push(`<text class="recovery-axis" x="${f(x(units))}" y="${bottom + 23}" text-anchor="middle">${units}</text>`);
  }
  const band = plan.investment < plan.target
    ? `<rect class="recovery-band" x="${left}" y="${f(y(plan.target))}" width="${right - left}" height="${f(y(plan.investment) - y(plan.target))}" />
       <line class="recovery-target" x1="${left}" x2="${right}" y1="${f(y(plan.target))}" y2="${f(y(plan.target))}" />`
    : "";
  const milestones = [...new Set([plan.recordedUnits, plan.targetUnits])]
    .filter((units) => units !== null && units <= SALES_HORIZON)
    .map((units) => `<circle class="recovery-milestone" cx="${f(x(units))}" cy="${f(y(units * plan.contribution))}" r="4"><title>${units} machines: ${dollars(units * plan.contribution)} available</title></circle>`).join("");
  return `<svg class="recovery-svg" viewBox="0 0 736 350" role="img" aria-labelledby="recovery-chart-title recovery-chart-desc">
    <title id="recovery-chart-title">Investment recovery by machines sold</title>
    <desc id="recovery-chart-desc">Each sale leaves ${dollars(plan.contribution)} toward investment after ${dollars(plan.unitCost)} in modeled per-machine costs. ${recoverySummary(plan)} At ${plan.units} machines, ${dollars(plan.available)} is available. This is a planning scenario.</desc>
    ${grid.join("\n")}
    ${band}
    <line class="recovery-recorded" x1="${left}" x2="${right}" y1="${f(y(plan.investment))}" y2="${f(y(plan.investment))}" />
    <path class="recovery-line" d="M ${left} ${f(y(0))} L ${right} ${f(y(plan.contribution * SALES_HORIZON))}" />
    ${milestones}
    <line class="recovery-cursor" x1="${f(x(plan.units))}" x2="${f(x(plan.units))}" y1="${f(y(plan.available))}" y2="${bottom}" />
    <circle class="recovery-dot" cx="${f(x(plan.units))}" cy="${f(y(plan.available))}" r="6" />
    <text class="recovery-axis recovery-x-label" x="${(left + right) / 2}" y="340" text-anchor="middle">Machines sold</text>
  </svg>`;
}
