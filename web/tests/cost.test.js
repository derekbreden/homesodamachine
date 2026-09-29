import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { mountCostRoutes, readInvestmentRollup } from "../lib/cost.js";
import { recoveryPlan, renderRecoveryChart } from "../public/cost-recovery.js";

const example = { unitCost: 2403.35, investment: 42383.86 };

test("recovery funds each build before repaying the investment, rounded up to whole sales", () => {
  const plan = recoveryPlan(example);
  assert.equal(plan.contribution, 2091.65);
  assert.equal(plan.recordedUnits, 21);
  assert.equal(plan.targetUnits, 39);
  assert.equal(plan.available, 52291.25);
  assert.equal(plan.balance, 9907.39);
  assert.ok(recoveryPlan({ ...example, units: 20 }).balance < 0);
  assert.ok(recoveryPlan({ ...example, units: 21 }).balance >= 0);
  assert.ok(recoveryPlan({ ...example, units: 38 }).available < 80000);
  assert.ok(recoveryPlan({ ...example, units: 39 }).available >= 80000);
});

test("a higher per-machine cost reduces the amount available to recover investment", () => {
  const plan = recoveryPlan({ ...example, unitCost: 2903.35 });
  assert.equal(plan.unitCost, 2903.35);
  assert.equal(plan.contribution, 1591.65);
  assert.equal(plan.recordedUnits, 27);
  assert.equal(plan.targetUnits, 51);
  assert.equal(plan.available, 39791.25);
  assert.equal(plan.balance, -2592.61);
});

test("cents determine the first sale that fully recovers the investment", () => {
  assert.equal(recoveryPlan({ unitCost: 4494, investment: 2 }).recordedUnits, 2);
  assert.equal(recoveryPlan({ unitCost: 4494, investment: 2.01 }).recordedUnits, 3);
  assert.deepEqual(recoveryPlan({ ...example, unitCost: 2403.3499999999995 }), recoveryPlan(example));
  const noneSold = recoveryPlan({ ...example, units: 0 });
  assert.equal(noneSold.available, 0);
  assert.equal(noneSold.balance, -42383.86);
});

test("zero or negative contribution has no recovery point and a finite chart", () => {
  for (const unitCost of [4495, 5000]) {
    const plan = recoveryPlan({ ...example, unitCost });
    assert.equal(plan.recordedUnits, null);
    assert.equal(plan.targetUnits, null);
    assert.doesNotMatch(renderRecoveryChart(plan), /NaN|Infinity/);
    assert.match(renderRecoveryChart(plan), /leaves no money to recover/);
  }
});

test("investment above the planning scenario remains the amount to recover", () => {
  const plan = recoveryPlan({ ...example, investment: 90000 });
  assert.equal(plan.target, 90000);
  assert.equal(plan.targetUnits, plan.recordedUnits);
  assert.doesNotMatch(renderRecoveryChart(plan), /class="recovery-band"/);
});

test("invalid estimates cannot produce a plausible recovery figure", () => {
  for (const value of [NaN, Infinity, -1]) {
    assert.throws(() => recoveryPlan({ ...example, investment: value }), RangeError);
  }
  assert.throws(() => recoveryPlan({ ...example, units: 2.5 }), RangeError);
});

function fixture(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-cost-"));
  fs.mkdirSync(path.join(dir, "ledger"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function investmentText(total = "42,383.86") {
  return `[$36,201.81](LEDGER_ACQUIRED_HW)
[$5,437.54](LEDGER_LABOR)
[$691.44](LEDGER_ON_ORDER)
[$53.07](LEDGER_MISSING)
[$${total}](LEDGER_GRAND_TOTAL)`;
}

test("recorded investment includes paid orders and losses, and must reconcile", (t) => {
  const dir = fixture(t);
  const ledger = path.join(dir, "ledger", "purchases.md");
  fs.writeFileSync(ledger, investmentText());
  assert.equal(readInvestmentRollup(dir).total, 42383.86);
  fs.writeFileSync(ledger, investmentText("45,000.00"));
  assert.throws(() => readInvestmentRollup(dir), /do not reconcile/);
  fs.writeFileSync(ledger, "No recorded total");
  assert.throws(() => readInvestmentRollup(dir), /Missing investment total/);
});

test("the sale price survives missing ledgers without claiming a free build or recovered investment", (t) => {
  const dir = fixture(t);
  let handler, html;
  mountCostRoutes({ get: (_route, fn) => { handler = fn; } }, { hardwareDir: dir });
  const res = { set() {}, send(value) { html = value; } };
  handler({}, res);
  assert.match(html, /\$4,495/);
  assert.match(html, /Cost data unavailable/);
  assert.doesNotMatch(html, /data-recovery="range"/);

  fs.writeFileSync(path.join(dir, "ledger", "bom.md"), `## 1. Parts
| Part | Qty | Unit $ | Line $ |
| Example part | 1 | $10.00 | $10.00 <!--@electronics--> |`);
  handler({}, res);
  assert.match(html, /\$4,495/);
  assert.match(html, /Recovery estimates are unavailable/);
  assert.doesNotMatch(html, /data-recovery="range"/);
});
