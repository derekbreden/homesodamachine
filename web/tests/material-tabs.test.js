// Tab routing preserves direct access to subsections of the combined material views.
import { test } from "node:test";
import assert from "node:assert/strict";
import { materialHash, materialTab } from "../contracts/material-tabs.js";

test("relationship links enter the shared tree at their named section", () => {
  assert.deepEqual(materialTab("bom"), { tab: "structure", section: "bom" });
  assert.deepEqual(materialTab("used"), { tab: "structure", section: "used" });
});

test("stock and cost links retain their subsection within the shared scroll", () => {
  assert.deepEqual(materialTab("stock"), { tab: "stock-cost", section: "stock" });
  assert.deepEqual(materialTab("cost"), { tab: "stock-cost", section: "cost" });
});

test("locations and combined views have separate routes", () => {
  for (const tab of ["structure", "stock-cost", "location", "docs"])
    assert.deepEqual(materialTab(tab), { tab, section: null });
  for (const tab of [null, "", "unknown", "toString", "__proto__"])
    assert.deepEqual(materialTab(tab), { tab: null, section: null });
});

test("fitted clearances have a material view route", () => {
  assert.equal(materialHash("HSM-0050", { view: "clearances" }), "material:HSM-0050?view=clearances");
  assert.equal(materialHash("HSM-0050", { tab: "clearances" }), "material:HSM-0050?view=clearances");
});
