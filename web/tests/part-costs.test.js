// Cost allocation keeps missing prices distinct from authored free parts.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { readBomLines, readPartCosts } from "../lib/part-costs.js";
import { directCost, rollupCost } from "../contracts/part-costs.js";
import { renderPartCostTree } from "../lib/part-cost-view.js";

test("an unpriced part remains unknown while an explicitly free part is costed", (t) => {
  const hardware = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-part-costs-"));
  fs.mkdirSync(path.join(hardware, "ledger"));
  t.after(() => fs.rmSync(hardware, { recursive: true, force: true }));
  fs.writeFileSync(path.join(hardware, "ledger", "bom.md"), `## 1. Parts
| Part | Qty | Unit $ | Line $ |
| Earth washer | 2 | — | — <!--@fasteners--><!--parts HSM-0200--> |
| Supplied spacer | 1 | $0.00 | $0.00 <!--@fasteners--><!--parts HSM-0201--> |
| Purchased screw | 3 | $4.00 | $12.00 <!--@fasteners--><!--parts HSM-0202--> |
`);
  fs.writeFileSync(path.join(hardware, "ledger", "labor.md"), `[$60](LABOR_RATE)
## 1. Assembly
| Operation | Minutes |
| Fit hardware <!--parts HSM-0001--> | 4 |
`);
  const catalog = {
    cost_root: "HSM-0001",
    materials: [
      { id: "HSM-0001", description: "Fixture assembly", kind: "assembly", bom: { items: [
        { material: "HSM-0200", quantity: 1 },
        { material: "HSM-0201", quantity: 1 },
        { material: "HSM-0202", quantity: 3 },
      ] } },
      { id: "HSM-0200", description: "Earth washer", kind: "purchased" },
      { id: "HSM-0201", description: "Supplied spacer", kind: "purchased" },
      { id: "HSM-0202", description: "Purchased screw", kind: "purchased" },
    ],
  };
  assert.deepEqual(readBomLines(hardware).map((line) => line.usd), [null, 0, 12]);
  catalog.costs = readPartCosts(hardware, catalog);
  assert.equal(directCost(catalog, "HSM-0200"), null);
  assert.equal(rollupCost(catalog, "HSM-0200").costed, false);
  assert.equal(directCost(catalog, "HSM-0201").elements[0].usd, 0);
  assert.equal(rollupCost(catalog, "HSM-0201").costed, true);
  assert.equal(rollupCost(catalog, "HSM-0201").usd, 0);
  assert.equal(rollupCost(catalog, "HSM-0202").usd, 4);
  assert.equal(catalog.costs.ledger.usd, 12);
  assert.equal(catalog.costs.unallocated.usd, 0);
  assert.deepEqual(rollupCost(catalog, "HSM-0001"), {
    usd: 16, parts: 12, labor: 4, minutes: 4, costed: true,
  });
  assert.ok(catalog.costs.findings.some((finding) => finding.kind === "unpriced" && finding.material === "HSM-0200"));
  assert.ok(catalog.costs.findings.some((finding) => finding.kind === "uncosted" && finding.material === "HSM-0200"));
  assert.ok(catalog.costs.findings.some((finding) => finding.kind === "count" && finding.materials.includes("HSM-0200")));

  const html = renderPartCostTree(catalog);
  const washerRow = html.match(/<span class="cost-node-name"><a [^>]*>Earth washer<\/a>[\s\S]*?<\/div>/)?.[0];
  const spacerRow = html.match(/<span class="cost-node-name"><a [^>]*>Supplied spacer<\/a>[\s\S]*?<\/div>/)?.[0];
  assert.ok(washerRow);
  assert.match(washerRow, /cost-node-value">—<\/span>/);
  assert.doesNotMatch(washerRow, /\$0\.00/);
  assert.match(spacerRow, /cost-node-value">\$0\.00<\/span>/);
  assert.doesNotMatch(html, /NaN|Infinity/);
});
