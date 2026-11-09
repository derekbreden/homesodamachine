// Purchasing forecast tests check physical requirements, supplier lots, cash and batch labor.
import { test } from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import {
  calculateBatch,
  laborMinutes,
  optimizePurchase,
  readBatchForecast,
} from "../lib/batch-forecast.js";
import { readLaborRollup } from "../lib/cost.js";
import { parseRun, runMinutes } from "../contracts/part-costs.js";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { readMaterialStock } from "../lib/material-stock.js";
import { planMaterial } from "../contracts/material-stock.js";

const hardware = fileURLToPath(new URL("../../hardware", import.meta.url));
const lot = (quantity, priceCents, extra = {}) => ({
  quantity,
  priceCents,
  label: `${quantity}-pack`,
  ...extra,
});

test("whole lots minimize batch cash, mixing sizes and accepting useful excess stock", () => {
  const options = [lot(1, 252), lot(10, 2134), lot(300, 62251)];
  const plan = optimizePurchase(19, options);
  assert.equal(plan.quantity, 20);
  assert.equal(plan.costCents, 4268);
  assert.equal(plan.remaining, 1);
  assert.equal(optimizePurchase(11, options).costCents, 2386);
  const filament = optimizePurchase(69.00115, [lot(3, 7499), lot(1, 2999)]);
  assert.equal(filament.quantity, 70);
  assert.deepEqual(
    filament.packages.map((pack) => pack.count),
    [23, 1],
  );
  assert.ok(filament.costCents < 24 * 7499);
});

test("discount tiers can make an extra quantity the least expensive order", () => {
  const plan = optimizePurchase(90, [
    lot(1, 200, { tiers: [{ minimum: 100, priceCents: 100 }] }),
  ]);
  assert.equal(plan.quantity, 100);
  assert.equal(plan.costCents, 10000);
});

test("available lots are preferred; a missing source remains a positive allowance", () => {
  assert.equal(
    optimizePurchase(10, [lot(10, 1000, { available: false }), lot(1, 200)])
      .costCents,
    2000,
  );
  const plan = optimizePurchase(0.971, [lot(1, 4999, { available: false })]);
  assert.equal(plan.costCents, 4999);
  assert.equal(plan.packages[0].option.available, false);
  assert.throws(() => optimizePurchase(10, [lot(10, 0)]), RangeError);
  assert.throws(() => optimizePurchase(NaN, [lot(10, 100)]), RangeError);
});

test("fractional quantities are covered without rounding a purchase down", () => {
  const options = [lot(5, 85), lot(25, 375), lot(50, 700), lot(100, 1200)];
  assert.equal(optimizePurchase(101.1, options).quantity, 105);
  assert.equal(optimizePurchase(101.1, options).costCents, 1285);
  assert.equal(optimizePurchase(20, [lot(1, 196.11)]).costCents, 3922);
});

test("purchase requirements follow the physical BOM and expose missing quotes", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const catalog = readMaterialCatalog(hardware);
  catalog.stock = readMaterialStock(hardware, catalog);
  assert.deepEqual(
    forecast.batches.map((batch) => batch.units),
    [5, 10, 20],
  );
  for (const batch of forecast.batches) {
    const plan = planMaterial(catalog, catalog.cost_root, batch.units, {
      finish: "white",
    });
    const needs = new Map(plan.resources.map((row) => [row.resource, row]));
    for (const row of batch.rows) {
      const need = needs.get(row.stock);
      if (need?.quantityKnown)
        assert.equal(row.required, need.needed, row.name);
      else if (need) assert.equal(row.requirementUnknown, true, row.name);
      else assert.equal(row.required, 0, row.name);
    }
    for (const gap of plan.gaps)
      assert.ok(
        batch.undefinedInputs.some((item) => item.material === gap.material),
      );
    assert.ok(
      batch.unpriced.every(
        (item) => item.quantity == null || item.quantity > 0,
      ),
    );
  }

});

test("a missing supplier remains visible and positively budgeted", () => {
  const data = {
    taxRate: 0,
    suppliers: [{ id: "shop", shippingCents: { 5: 0 } }],
    allowances: [],
    items: [
      {
        id: "part",
        name: "Part",
        supplier: "shop",
        unit: "pieces",
        perUnit: 1,
        priceBasis: "merchandise",
        status: "unavailable",
        inventory: { onHand: 1, incoming: 0 },
        options: [lot(1, 100, { available: false })],
      },
    ],
  };
  const batch = calculateBatch(data, 5, null);
  assert.equal(batch.rows[0].quantity, 4);
  assert.equal(batch.rows[0].costCents, 400);
  assert.match(batch.rows[0].issues.join(" "), /Out of stock/);
});

test("inventory and in-transit orders are deducted before whole-lot rounding and freight", () => {
  const data = {
    taxRate: 0.1,
    suppliers: [{ id: "stock", shippingCents: { 10: 800, 20: 800 } }],
    allowances: [],
    items: [
      {
        id: "part",
        supplier: "stock",
        perUnit: 1,
        priceBasis: "merchandise",
        status: "listed",
        inventory: { onHand: 4, incoming: 6 },
        options: [lot(6, 600)],
      },
    ],
    pendingPayments: [{ name: "Open order", costCents: 600 }],
  };
  const ten = calculateBatch(data, 10, null);
  assert.equal(ten.rows[0].shortfall, 0);
  assert.equal(ten.rows[0].quantity, 0);
  assert.equal(ten.inboundCents, 0);
  assert.equal(ten.taxCents, 0);
  assert.equal(
    ten.cashCents,
    600,
    "only the possible unpaid balance, with no duplicate order or tax",
  );
  const twenty = calculateBatch(data, 20, null);
  assert.equal(twenty.rows[0].shortfall, 10);
  assert.equal(twenty.rows[0].quantity, 12);
  assert.equal(twenty.rows[0].remaining, 2);
  assert.equal(twenty.cashCents, 2800);
  assert.throws(
    () =>
      calculateBatch(
        { ...data, items: [{ ...data.items[0], inventory: { onHand: -1 } }] },
        10,
        null,
      ),
    RangeError,
  );
});

test("purchasing and buildability read the same balances and units", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const catalog = readMaterialCatalog(hardware);
  catalog.stock = readMaterialStock(hardware, catalog);
  for (const item of forecast.data.items) {
    const stock = catalog.stock.resources[item.stock];
    assert.equal(item.inventory.onHand, stock.onHand, item.name);
    assert.equal(item.inventory.incoming, stock.incoming, item.name);
    assert.equal(item.inventory.reserved || 0, stock.reserved || 0, item.name);
    assert.equal(item.unit, stock.unit, item.name);
  }
});

test("purchase cash and the full-batch labor benchmark stay separate", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const [five, ten, twenty] = forecast.batches;
  assert.equal(five.pendingCents, ten.pendingCents);
  assert.equal(ten.pendingCents, twenty.pendingCents);
  for (const batch of forecast.batches) {
    assert.equal(batch.totalCents, batch.cashCents + batch.laborCents);
    assert.ok(
      batch.rows.every((row) =>
        row.quantity ? row.costCents > 0 : row.costCents === 0,
      ),
    );
  }
  const labor = readLaborRollup(hardware);
  assert.equal(
    Math.round(ten.laborHours * 60 * 1000),
    Math.round(labor.minutes * 10 * 1000),
  );
  assert.ok(five.laborHours / 5 > ten.laborHours / 10);
  assert.ok(twenty.laborHours / 20 < ten.laborHours / 10);

});

test("delivered historical invoices are not taxed twice; paid labor remains separate", () => {
  const data = {
    taxRate: 0.1,
    suppliers: [{ id: "test", shippingCents: { 10: 100, 20: 100 } }],
    allowances: [],
    items: [
      {
        id: "invoice",
        supplier: "test",
        perUnit: 1,
        priceBasis: "delivered",
        options: [lot(10, 10000)],
        status: "estimate",
      },
      {
        id: "catalog",
        supplier: "test",
        perUnit: 1,
        priceBasis: "merchandise",
        options: [lot(1, 100)],
        status: "listed",
      },
    ],
  };
  const batch = calculateBatch(data, 10, {
    minutes: 60,
    rate: 100,
    opCount: 1,
  });
  assert.equal(batch.partsCents, 11000);
  assert.equal(batch.taxCents, 110);
  assert.equal(batch.cashCents, 11210);
  assert.equal(batch.laborCents, 100000);
  assert.equal(batch.totalCents, 111210);
  assert.equal(calculateBatch(data, 10, null).laborCents, null);
  assert.throws(
    () => calculateBatch({ ...data, taxRate: NaN }, 10, null),
    RangeError,
  );
});

test("a run's setup is shared by the batch; per-machine work is not", () => {
  const run = parseRun("15 m setup a plate of 30 · 30 s a float · 3 a machine");
  assert.deepEqual(run, {
    setup: 15,
    run: "plate",
    cap: 30,
    each: 0.5,
    piece: "float",
    per: 3,
  });
  assert.equal(runMinutes(run, 10), 3, "one plate of thirty for ten machines");
  assert.equal(
    runMinutes(run, 1),
    16.5,
    "one plate of three for a single machine",
  );
  assert.equal(runMinutes(run, 20), 3, "two full plates for twenty");
  const batchRun = parseRun("20 m setup a batch · 3 m a vessel · 1 a machine");
  assert.equal(batchRun.cap, null);
  assert.equal(runMinutes(batchRun, 5), 7);
  assert.equal(
    parseRun("20 m setup a plate · 3 m a vessel · 1 a machine"),
    null,
    "a plate needs its size",
  );
  const labor = {
    minutes: 13,
    rate: 60,
    opCount: 2,
    cats: [
      {
        ops: [
          { minutes: 10, run: null },
          { minutes: 3, run },
        ],
      },
    ],
  };
  assert.equal(laborMinutes(labor, 10), 13);
  assert.equal(laborMinutes(labor, 1), 26.5);
  assert.equal(
    laborMinutes({ minutes: 60 }, 5),
    60,
    "a flat figure stays flat",
  );
});
