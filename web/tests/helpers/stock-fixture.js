// Stock fixtures provide disposable physical inventory and manufacturing records for focused checks.
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";

const directories = [];
export function cleanupStockFixtures() {
  for (const directory of directories.splice(0))
    fs.rmSync(directory, { recursive: true, force: true });
}
export function stockFixture() {
  const folder = path.resolve(".cache/runs/stock-test-" + randomUUID()),
    ledger = path.join(folder, "ledger");
  fs.mkdirSync(ledger, { recursive: true });
  directories.push(folder);
  const material = (id, kind, children = []) => ({
    id,
    kind,
    description: id,
    bom: {
      items: children.map(([material, quantity]) => ({
        material,
        quantity,
        unit: "ea",
      })),
    },
  });
  const catalog = {
    cost_root: "HSM-1000",
    materials: [
      material("HSM-1000", "assembly", [
        ["HSM-1001", 1],
        ["HSM-1010", 1],
        ["HSM-1004", 1],
      ]),
      material("HSM-1001", "assembly", [
        ["HSM-1002", 1],
        ["HSM-1003", 2],
      ]),
      material("HSM-1002", "manufactured"),
      material("HSM-1003", "purchased"),
      material("HSM-1004", "purchased"),
      material("HSM-1010", "assembly", [["HSM-1005", 1]]),
      material("HSM-1005", "manufactured"),
    ],
  };
  const resource = (id, unit, onHand, incoming, perUnit) => ({
    id,
    name: id,
    unit,
    onHand,
    incoming,
    reserved: 0,
    estimated: false,
    asOf: "2026-11-08",
    planning: { root: catalog.cost_root, perUnit, materialAllowance: 0 },
  });
  const stock = {
    schema: 2,
    opening: { asOf: "2026-11-08", note: "Disposable test opening" },
    resources: [
      resource("petgf-black", "kg", 10, 0, 0.5),
      resource("petgf-white", "kg", 2, 0, 0.1),
      resource("screws", "pieces", 10, 0, 2),
      resource("regulators", "pieces", 0, 2, 1),
    ],
    bindings: { "HSM-1003": "screws", "HSM-1004": "regulators" },
    printing: { faucet: ["HSM-1005"], colors: {}, mixes: {} },
    kits: {},
    observations: [],
    events: [],
  };
  const forecast = {
    schemaVersion: 2,
    checkedAt: "2026-11-08",
    taxRate: 0,
    suppliers: [
      { id: "shop", name: "Shop", shippingCents: { 5: 0, 10: 0, 20: 0 } },
    ],
    items: stock.resources.map((item) => ({
      id: item.id,
      stock: item.id,
      name: item.id,
      unit: item.unit,
      supplier: "shop",
      priceBasis: "merchandise",
      status: "listed",
      note: "Fixture",
      options: [
        {
          quantity: item.id === "screws" ? 10 : 1,
          priceCents: 1000,
          label: "Fixture lot",
          available: true,
        },
      ],
    })),
    allowances: [],
    pendingPayments: [],
    notes: [],
    scope: "Fixture",
    inventoryNote: "Fixture",
    roundingNote: "Fixture",
  };
  const write = (name, value) =>
    fs.writeFileSync(
      path.join(ledger, name),
      typeof value === "string" ? value : JSON.stringify(value, null, 2),
    );
  write("materials.json", catalog);
  write("stock.json", stock);
  write("batch-forecast.json", forecast);
  write(
    "bom.md",
    "## 1. Controls\n| Part | Notes | Qty | Unit $ | Line $ |\n| Regulator | | 1 | $10 | $10 <!--@plumbing--><!--parts HSM-1004--> |\n\n## 7. Printed parts\n| Part | Qty | Material | Mass (kg) | $ |\n| Shell | 1 | PET-GF | 0.5 | $5 <!--@printed--><!--parts HSM-1002--> |\n| Faucet part | 1 | PET-GF | 0.1 | $1 <!--@printed--><!--parts HSM-1005--> |\n\n## 11. Fasteners\n| Part | Notes | Qty | Unit $ | Line $ |\n| Screw | | 2 | $1 | $2 <!--@fasteners--><!--parts HSM-1003--> |\n",
  );
  write(
    "labor.md",
    "[$100](LABOR_RATE)\n[10](BATCH_SIZE)\n## 1. Assembly\n| Operation | Notes | Minutes |\n| Assemble panel | | 5 <!--parts HSM-1001--> |\n",
  );
  return folder;
}
