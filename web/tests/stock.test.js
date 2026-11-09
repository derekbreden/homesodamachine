// Stock tests exercise physical completion and the shared build and purchase projections on disposable ledgers.
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { readMaterialStock } from "../lib/material-stock.js";
import { readStockLedger } from "../lib/stock-ledger.js";
import { readBatchForecast } from "../lib/batch-forecast.js";
import { readPartCosts } from "../lib/part-costs.js";
import {
  completionProposal,
  recordStockEvent,
  stockTarget,
} from "../lib/stock-operations.js";
import { planMaterial } from "../contracts/material-stock.js";

import { stockFixture, cleanupStockFixtures } from "./helpers/stock-fixture.js";
afterEach(cleanupStockFixtures);

const catalog = (folder) => {
  const value = readMaterialCatalog(folder);
  value.stock = readMaterialStock(folder, value);
  return value;
};
const record = (folder, event) =>
  recordStockEvent(folder, {
    id: randomUUID(),
    occurredAt: "2026-11-08T18:00:00Z",
    ...event,
  });
const count = (folder, material, quantity, extra = {}) =>
  record(folder, { kind: "count", material, quantity, ...extra });
const row = (forecast, id) =>
  forecast.batches[0].rows.find((item) => item.stock === id);

test("a completion consumes components, adds its output and records work once", () => {
  const folder = stockFixture();
  count(folder, "HSM-1002", 2);
  const before = readBatchForecast(folder, null),
    value = catalog(folder),
    proposal = completionProposal(value, "HSM-1001");
  const result = record(folder, {
    ...proposal,
    attendedMinutes: 7,
    note: "Assembled from ready components",
  });
  const after = readStockLedger(folder);
  assert.equal(after.resources.screws.onHand, 8);
  assert.equal(after.materials["HSM-1002"].onHand, 1);
  assert.equal(after.materials["HSM-1001"].onHand, 1);
  assert.equal(after.resources["petgf-black"].onHand, 10);
  assert.equal(after.builds[0].attendedMinutes, 7);
  assert.equal(after.builds[0].quantity, 1);
  const forecast = readBatchForecast(folder, null);
  assert.equal(
    forecast.batches[0].cashCents,
    before.batches[0].cashCents,
    "embodied inputs are not bought again",
  );
  assert.equal(row(forecast, "screws").required, 8);
  const retry = recordStockEvent(folder, {
    ...proposal,
    occurredAt: result.event.occurredAt,
    attendedMinutes: 7,
    note: "Assembled from ready components",
  });
  assert.equal(retry.duplicate, true);
  assert.equal(readStockLedger(folder).resources.screws.onHand, 8);
});

test("completed stock satisfies build and purchase demand without remaking its contents", () => {
  const folder = stockFixture();
  count(folder, "HSM-1002", 1);
  record(folder, {
    ...completionProposal(catalog(folder), "HSM-1001"),
    attendedMinutes: 4,
  });
  const value = catalog(folder),
    plan = planMaterial(value, "HSM-1001");
  assert.equal(plan.materials[0].fromStock, 1);
  assert.equal(plan.resources.length, 0);
  const forecast = readBatchForecast(folder, null);
  assert.equal(row(forecast, "screws").required, 8);
  assert.equal(row(forecast, "petgf-black").required, 2);
});

test("manufacturing inputs remain available when prices change", () => {
  const folder = stockFixture(),
    before = catalog(folder).stock.inputs;
  const file = path.join(folder, "ledger/bom.md");
  fs.writeFileSync(
    file,
    fs
      .readFileSync(file, "utf8")
      .replaceAll("$10", "$99")
      .replaceAll("$5", "$50")
      .replaceAll("$1", "$20")
      .replaceAll("$2", "$40"),
  );
  assert.deepEqual(catalog(folder).stock.inputs, before);
});

test("receipts make ordered stock available in both projections", () => {
  const folder = stockFixture();
  record(folder, { kind: "receipt", material: "HSM-1004", quantity: 1 });
  const value = catalog(folder),
    stock = readStockLedger(folder);
  assert.equal(stock.resources.regulators.onHand, 1);
  assert.equal(stock.resources.regulators.incoming, 1);
  assert.equal(planMaterial(value, "HSM-1004").status, "covered");
  const forecast = readBatchForecast(folder, null);
  assert.equal(row(forecast, "regulators").onHand, 1);
  assert.equal(row(forecast, "regulators").incoming, 1);
});

test("counting a purchased material updates its supplier stock identity", () => {
  const folder = stockFixture();
  count(folder, "HSM-1003", 6);
  const stock = readStockLedger(folder);
  assert.equal(stock.resources.screws.onHand, 6);
  assert.equal(stock.materials["HSM-1003"], undefined);
  assert.deepEqual(stockTarget(catalog(folder), "HSM-1003"), {
    resource: "screws",
  });
});

test("reservations reduce availability consistently", () => {
  const folder = stockFixture();
  record(folder, {
    kind: "count",
    resource: "screws",
    quantity: 10,
    reserved: 4,
  });
  assert.equal(catalog(folder).stock.resources.screws.available, 6);
  const forecast = readBatchForecast(folder, null);
  assert.equal(row(forecast, "screws").available, 6);
});

test("reusable equipment covers a batch and remains after completion", () => {
  const folder = stockFixture(),
    file = path.join(folder, "ledger/stock.json"),
    stock = JSON.parse(fs.readFileSync(file, "utf8"));
  stock.resources.push({
    id: "bath",
    name: "Bath",
    unit: "ea",
    onHand: 1,
    planning: { root: "HSM-1000", perUnit: 1, reusable: true },
  });
  fs.writeFileSync(file, JSON.stringify(stock));
  fs.appendFileSync(
    path.join(folder, "ledger/bom.md"),
    "\n## 12. Shop\n| Bath | | 1 | $1 | $1 <!--@consumables--><!--parts HSM-1002--> |\n",
  );
  const value = catalog(folder);
  const plan = planMaterial(value, "HSM-1000", 20, { finish: "white" });
  const bath = plan.resources.find((input) => input.resource === "bath");
  assert.equal(bath.needed, 1);
  assert.equal(bath.status, "covered");
  const proposal = completionProposal(value, "HSM-1002");
  assert.ok(!proposal.inputs.some((input) => input.resource === "bath"));
  record(folder, proposal);
  assert.equal(readStockLedger(folder).resources.bath.onHand, 1);
  assert.throws(
    () =>
      record(folder, {
        ...proposal,
        id: randomUUID(),
        inputs: [{ resource: "bath", quantity: 1, unit: "ea" }],
      }),
    /Reusable/,
  );
});

test("provisional purchasing reserves shrink with completed-stock credits", () => {
  const folder = stockFixture(),
    file = path.join(folder, "ledger/stock.json"),
    stock = JSON.parse(fs.readFileSync(file, "utf8"));
  const material = stock.resources.find((item) => item.id === "petgf-black");
  material.onHand = 0;
  material.planning.purchaseReserve = { 5: 10, 10: 20, 20: 40 };
  fs.writeFileSync(file, JSON.stringify(stock));
  const before = row(readBatchForecast(folder, null), "petgf-black");
  assert.equal(before.required, 2.5);
  assert.equal(before.quantity, 10);
  count(folder, "HSM-1002", 4);
  const after = row(readBatchForecast(folder, null), "petgf-black");
  assert.equal(after.required, 0.5);
  assert.equal(after.quantity, 2);
  count(folder, "HSM-1000", 5, { finish: "white" });
  assert.equal(row(readBatchForecast(folder, null), "petgf-black"), undefined);
});

test("finish applies to colored parts and stays off common assemblies", () => {
  const folder = stockFixture();
  const proposal = completionProposal(catalog(folder), "HSM-1001", 1, "black");
  assert.equal(proposal.output.finish, undefined);
  assert.equal(
    proposal.inputs.find((input) => input.material === "HSM-1002").finish,
    undefined,
  );
  count(folder, "HSM-1005", 1, { finish: "white" });
  assert.equal(
    planMaterial(catalog(folder), "HSM-1005", 1, { finish: "white" })
      .materials[0].fromStock,
    1,
  );
  assert.equal(
    planMaterial(catalog(folder), "HSM-1005", 1, { finish: "black" })
      .materials[0].fromStock,
    0,
  );
  assert.throws(() => count(folder, "HSM-1005", 1), /finish/);
});

test("a new completion makes additional output even when some is already held", () => {
  const folder = stockFixture();
  count(folder, "HSM-1001", 2);
  const proposal = completionProposal(catalog(folder), "HSM-1001");
  assert.equal(proposal.inputs.length, 2);
  record(folder, proposal);
  assert.equal(readStockLedger(folder).materials["HSM-1001"].onHand, 3);
});

test("bad data and a conflicting retry leave the whole ledger unchanged", () => {
  const folder = stockFixture(),
    file = path.join(folder, "ledger/stock.json");
  const before = fs.readFileSync(file, "utf8");
  const proposal = completionProposal(catalog(folder), "HSM-1001");
  assert.throws(() =>
    record(folder, {
      ...proposal,
      inputs: [{ resource: "screws", quantity: -1 }],
    }),
  );
  assert.equal(fs.readFileSync(file, "utf8"), before);
  assert.equal(fs.existsSync(file + ".lock"), false);
  const result = record(folder, proposal);
  const stable = fs.readFileSync(file, "utf8");
  assert.throws(
    () =>
      recordStockEvent(folder, {
        ...result.event,
        output: { material: "HSM-1001", quantity: 2 },
      }),
    /different work/,
  );
  assert.equal(fs.readFileSync(file, "utf8"), stable);
});

test("recorded use beyond an estimated balance remains visible and asks for a count", () => {
  const folder = stockFixture();
  const proposal = completionProposal(catalog(folder), "HSM-1001");
  proposal.inputs = [{ resource: "screws", quantity: 12, unit: "pieces" }];
  record(folder, proposal);
  const stock = readStockLedger(folder);
  assert.equal(stock.resources.screws.onHand, -2);
  assert.equal(stock.resources.screws.available, 0);
  assert.equal(stock.resources.screws.needsCount, true);
  assert.doesNotThrow(() => readBatchForecast(folder, null));
});

test("missing opening counts do not invent a remaining balance", () => {
  const folder = stockFixture();
  record(folder, completionProposal(catalog(folder), "HSM-1001"));
  const stock = readStockLedger(folder);
  assert.equal(stock.materials["HSM-1002"].onHand, null);
  assert.equal(stock.materials["HSM-1001"].onHand, 1);
});

test("a stock writer holds the ledger while another writer is active", () => {
  const folder = stockFixture(),
    lock = path.join(folder, "ledger/stock.json.lock");
  fs.writeFileSync(lock, JSON.stringify({ pid: process.pid }));
  assert.throws(() => count(folder, "HSM-1002", 1), /retry/);
  fs.rmSync(lock);
  count(folder, "HSM-1002", 1);
  assert.equal(readStockLedger(folder).materials["HSM-1002"].onHand, 1);
});

test("physical definitions price through the same material configurations", () => {
  const folder = stockFixture(),
    value = catalog(folder);
  value.costs = readPartCosts(folder, value);
  assert.equal(value.costs.ledger.usd, 18);
  assert.equal(value.costs.direct["HSM-1002"].elements[0].measure.value, 0.5);
});
