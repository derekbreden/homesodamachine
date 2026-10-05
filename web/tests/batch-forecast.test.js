import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { calculateBatch, optimizePurchase, readBatchForecast, renderBatchForecast } from "../lib/batch-forecast.js";
import { readLaborRollup } from "../lib/cost.js";

const hardware = fileURLToPath(new URL("../../hardware", import.meta.url));
const lot = (quantity, priceCents, extra = {}) => ({ quantity, priceCents, label: `${quantity}-pack`, ...extra });

test("whole lots minimize batch cash, mixing sizes and accepting useful excess stock", () => {
  const options = [lot(1, 252), lot(10, 2134), lot(300, 62251)];
  const plan = optimizePurchase(19, options);
  assert.equal(plan.quantity, 20);
  assert.equal(plan.costCents, 4268);
  assert.equal(plan.remaining, 1);
  assert.equal(optimizePurchase(11, options).costCents, 2386);
  const filament = optimizePurchase(69.00115, [lot(3, 7499), lot(1, 2999)]);
  assert.equal(filament.quantity, 70);
  assert.deepEqual(filament.packages.map(pack => pack.count), [23, 1]);
  assert.ok(filament.costCents < 24 * 7499);
});

test("discount tiers can make an extra quantity the least expensive order", () => {
  const plan = optimizePurchase(90, [lot(1, 200, { tiers: [{ minimum: 100, priceCents: 100 }] })]);
  assert.equal(plan.quantity, 100);
  assert.equal(plan.costCents, 10000);
});

test("available lots are preferred; a missing source remains a positive allowance", () => {
  assert.equal(optimizePurchase(10, [lot(10, 1000, { available: false }), lot(1, 200)]).costCents, 2000);
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

test("the sourced plan covers the current BOM, including shared parts and unpriced requirements", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  assert.deepEqual(forecast.batches.map(batch => batch.units), [5, 10, 20]);
  assert.equal(forecast.bomChanged, false, "BOM changed: review the dated supplier forecast");
  const bomRows = fs.readFileSync(path.join(hardware, "ledger/bom.md"), "utf8").split("\n")
    .flatMap((line, index) => line.startsWith("|") && line.includes("<!--@") ? [index + 1] : []);
  const covered = new Set([...forecast.data.items.flatMap(item => item.bomLines), ...forecast.data.excludedBomLines.map(row => row.line)]);
  assert.deepEqual([...covered].sort((a, b) => a - b), bomRows);
  assert.equal(forecast.data.bomRowCount, bomRows.length);
  for (const batch of forecast.batches) {
    for (const row of batch.rows) {
      assert.ok(row.onHand + row.incoming + row.quantity + 1e-8 >= row.required, row.name);
      assert.ok(row.quantity ? row.costCents > 0 : row.costCents === 0, row.name);
    }
    const valves = batch.rows.find(row => row.id === "B07NWCQJK9");
    assert.equal(valves.required, 11 * batch.units);
    const tees = batch.rows.find(row => row.bomLines.includes(53));
    assert.equal(tees.required, 8 * batch.units);
    assert.equal(batch.rows.filter(row => row.bomLines.includes(53)).length, 1);
    const copper = batch.rows.find(row => row.id === "B0DKSW5VL9");
    assert.equal(copper.packages[0].count, { 5: 1, 10: 3, 20: 6 }[batch.units]);
    const rod = batch.rows.find(row => row.bomLines.includes(267));
    assert.equal(rod.packages[0].count, { 5: 2, 10: 5, 20: 10 }[batch.units]);
    const foam = batch.rows.find(row => row.bomLines.includes(202));
    assert.equal(foam.packages[0].count, { 5: 5, 10: 11, 20: 23 }[batch.units]);
    const keystones = batch.rows.find(row => row.bomLines.includes(226));
    assert.equal(keystones.quantity, batch.units === 20 ? 10 : 0);
    const red = batch.rows.find(row => row.bomLines.includes(79));
    assert.equal(red.required, batch.units * 2.5);
    assert.equal(red.quantity, 0);
    assert.equal(batch.rows.find(row => row.bomLines.includes(92)).costCents, 1340 * batch.units);
  }
});

test("known availability shortages are visible and are included in the budget", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const [, ten, twenty] = forecast.batches;
  assert.equal(ten.rows.find(row => row.id === "B01G2F6EMY").quantity, 9);
  assert.match(twenty.rows.find(row => row.id === "B01G2F6EMY").issues.join(" "), /9 more lots/);
  assert.doesNotMatch(twenty.rows.find(row => row.id === "B07D23JJMR").issues.join(" "), /more lot/);
  for (const batch of forecast.batches) {
    const aero = batch.rows.find(row => row.id === "asa-aero");
    assert.equal(aero.costCents, 0);
    assert.equal(aero.estimated, true);
  }
  const html = renderBatchForecast(forecast);
  assert.match(html, /ASA Aero White.*out of stock/);
  assert.match(html, /aria-label="estimate or availability unresolved"/);
  assert.doesNotMatch(html, /NaN|Infinity|undefined/);
  assert.match(html, /no new purchase is budgeted/);
  assert.match(html, /approximately 12 kg Black PET-GF15, 4 kg Clear PETG and 10 kg Black PETG/);
  assert.doesNotMatch(html, /Existing parts inventory is not credited|Full new-purchase budgets/);
});

test("inventory and in-transit orders are deducted before whole-lot rounding and freight", () => {
  const data = {
    taxRate: 0.1, suppliers: [{ id: "stock", shippingCents: { 10: 800, 20: 800 } }], allowances: [],
    items: [{ id: "part", supplier: "stock", perUnit: 1, priceBasis: "merchandise", status: "listed", inventory: { onHand: 4, incoming: 6 }, options: [lot(6, 600)] }],
    pendingPayments: [{ name: "Open order", costCents: 600 }],
  };
  const ten = calculateBatch(data, 10, null);
  assert.equal(ten.rows[0].shortfall, 0);
  assert.equal(ten.rows[0].quantity, 0);
  assert.equal(ten.inboundCents, 0);
  assert.equal(ten.taxCents, 0);
  assert.equal(ten.cashCents, 600, "only the possible unpaid balance, with no duplicate order or tax");
  const twenty = calculateBatch(data, 20, null);
  assert.equal(twenty.rows[0].shortfall, 10);
  assert.equal(twenty.rows[0].quantity, 12);
  assert.equal(twenty.rows[0].remaining, 2);
  assert.equal(twenty.cashCents, 2800);
  assert.throws(() => calculateBatch({ ...data, items: [{ ...data.items[0], inventory: { onHand: -1 } }] }, 10, null), RangeError);
});

test("current stock changes the actual PCB, filament and pending-order purchase lists", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const [, ten, twenty] = forecast.batches;
  const row = (batch, id) => batch.rows.find(row => row.id === id);
  const boards = ten.rows.find(row => row.bomLines.includes(15));
  assert.equal(boards.onHand, 10);
  assert.equal(boards.quantity, 0);
  assert.equal(twenty.rows.find(row => row.id === boards.id).quantity, 10);
  assert.equal(row(ten, "petgf-black").quantity, 57);
  assert.equal(row(twenty, "petgf-black").quantity, 126);
  assert.equal(row(ten, "petg-clear").quantity, 7);
  assert.equal(row(ten, "petg-clear").costCents, 9514, "seven new refills use the six-roll tier");
  assert.equal(row(twenty, "petg-clear").quantity, 17);
  assert.equal(row(ten, "petg-black").quantity, 0);
  assert.equal(row(twenty, "petg-black").quantity, 0);
  assert.equal(row(ten, "B0GCBNTBT8").quantity, 0);
  assert.equal(row(twenty, "B0GCBNTBT8").quantity, 10);
  assert.equal(row(ten, "B0DFWTJSYD").quantity, 0);
  assert.equal(row(twenty, "B0DFWTJSYD").quantity, 0);
  assert.equal(row(ten, "B0DFYKBQ2S").quantity, 0);
  assert.equal(row(twenty, "B0DFYKBQ2S").quantity, 50);
  assert.equal(ten.suppliers.find(supplier => supplier.id === "lcsc").shippingCents, 0);
  assert.equal(twenty.suppliers.find(supplier => supplier.id === "lcsc").shippingCents, 4000);
  assert.equal(ten.pendingCents, 15563);
  assert.equal(twenty.pendingCents, ten.pendingCents, "same opening orders, not doubled for twenty");
  assert.equal(row(ten, "16awg-kit").packages[0].count, 2);
  assert.equal(row(twenty, "16awg-kit").packages[0].count, 4);
});

test("five machines use opening stock and whole packs, with small-order reserves and separate labor", () => {
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const [five, ten, twenty] = forecast.batches;
  const row = id => five.rows.find(row => row.id === id);
  assert.equal(row("petgf-black").shortfall, 22.5);
  assert.equal(row("petgf-black").quantity, 23);
  assert.deepEqual(row("petgf-black").packages.map(pack => [pack.count, pack.option.quantity]), [[7, 3], [2, 1]]);
  assert.equal(row("petgf-black").costCents, 58491);
  assert.equal(row("petg-clear").quantity, 2);
  assert.equal(row("petg-clear").costCents, 3038);
  assert.equal(row("petg-black").quantity, 0);
  assert.equal(row("16awg-kit").packages[0].count, 1, "reserve for the limiting colour after the existing kit credit");
  assert.equal(row("B07NWCQJK9").quantity, 41, "55 solenoids minus 14 credited");
  assert.equal(row("B01G2F6EMY").quantity, 4);
  for (const id of ["jlc", "metals", "scs", "midwest", "kj", "waveshare", "lcsc", "riteav"]) {
    const supplier = five.suppliers.find(supplier => supplier.id === id);
    assert.equal(supplier.costCents, 0, id);
    assert.equal(supplier.shippingCents, 0, `${id}: no new shipment`);
  }
  assert.equal(five.suppliers.find(supplier => supplier.id === "bambu").shippingCents, 1000);
  assert.equal(five.pendingCents, ten.pendingCents, "same existing-order reserve, not half the ten-machine balance");
  assert.equal(five.partsCents, 358663);
  assert.equal(five.inboundCents, 3500);
  assert.equal(five.taxCents, 24039);
  assert.equal(five.allowances.find(allowance => allowance.id === "shop").costCents, 12500);
  assert.equal(five.cashCents, 474265);
  assert.equal(five.laborHours, 51.25);
  assert.equal(five.laborCents, 512500);
  assert.equal(five.totalCents, 986765);
  assert.ok(five.cashCents < ten.cashCents / 2, "inventory makes this a separate calculation");
  assert.equal(ten.cashCents, 1156174);
  assert.equal(twenty.cashCents, 2792377);
  const html = renderBatchForecast(forecast);
  assert.match(html, /value="5" checked/);
  assert.match(html, /data-units="5" open/);
  assert.match(html, /<th scope="col">5 machines<\/th>/);
  assert.match(html, /\$4,742.65/);
});

test("delivered historical invoices are not taxed twice; paid labor remains separate", () => {
  const data = {
    taxRate: 0.1, suppliers: [{ id: "test", shippingCents: { 10: 100, 20: 100 } }], allowances: [],
    items: [
      { id: "invoice", supplier: "test", perUnit: 1, priceBasis: "delivered", options: [lot(10, 10000)], status: "estimate" },
      { id: "catalog", supplier: "test", perUnit: 1, priceBasis: "merchandise", options: [lot(1, 100)], status: "listed" },
    ],
  };
  const batch = calculateBatch(data, 10, { minutes: 60, rate: 100, opCount: 1 });
  assert.equal(batch.partsCents, 11000);
  assert.equal(batch.taxCents, 110);
  assert.equal(batch.cashCents, 11210);
  assert.equal(batch.laborCents, 100000);
  assert.equal(batch.totalCents, 111210);
  assert.equal(calculateBatch(data, 10, null).laborCents, null);
  assert.throws(() => calculateBatch({ ...data, taxRate: NaN }, 10, null), RangeError);
});
