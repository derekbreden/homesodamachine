// These on-demand checks exercise shared search decisions and source discovery without a build.
import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { findParts, checkoutRoot } from "./find-part.mjs";
import { readMaterialCatalog } from "../web/lib/material-catalog.js";
import { readPartCosts } from "../web/lib/part-costs.js";
import { searchCatalog } from "../web/contracts/materials.js";

const catalog = readMaterialCatalog(path.join(checkoutRoot, "hardware"));
catalog.costs = readPartCosts(path.join(checkoutRoot, "hardware"), catalog);
const ids = (hits) => hits.map((hit) => hit.material?.id || hit.id || hit.line.label);

test("browser and local search return the same ordered candidates", () => {
  for (const query of ["water regulator", "pisco", "meanwell", "pisko", "water reservoir snap", "thread tape"]) {
    assert.deepEqual(ids(findParts(query).hits), ids(searchCatalog(catalog, query).slice(0, 20)), query);
  }
});

test("an exact material identity stays unambiguous", () => {
  const result = findParts("HSM-000332");
  assert.equal(result.match, "exact");
  assert.deepEqual(ids(result.hits), ["HSM-0332"]);
});

test("regulators precede connected tubes and caps, and a water qualifier selects the water regulator", () => {
  const regulators = ids(searchCatalog(catalog, "regulator"));
  assert.deepEqual(new Set(regulators.slice(0, 3)), new Set(["HSM-0331", "HSM-0332", "HSM-0370"]));
  const water = ids(searchCatalog(catalog, "Water Regulator"));
  assert.equal(water[0], "HSM-0332");
  for (const id of ["HSM-0295", "HSM-0300", "HSM-0451"]) assert.ok(water.indexOf(id) > 0, id);
  assert.equal(ids(searchCatalog(catalog, "regulator inlet tube"))[0], "HSM-0295");
});

test("named objects lead their supports, tools and connected parts across the catalog", () => {
  for (const [query, expected] of [["fan", "HSM-0543"], ["funnel", "HSM-0070"], ["coil", "HSM-0015"], ["water port connector", "HSM-0013"]]) {
    assert.equal(ids(searchCatalog(catalog, query))[0], expected, query);
  }
  assert.deepEqual(new Set(ids(searchCatalog(catalog, "pump")).slice(0, 2)), new Set(["HSM-0044", "HSM-0178"]));
  assert.deepEqual(new Set(ids(searchCatalog(catalog, "temperature probe"))), new Set(["HSM-0016", "HSM-0017"]));
});

test("object relevance is independent of purchase status and catalog allocation order", () => {
  const materials = [
    { id: "tube", description: "Water regulator inlet tube · white LLDPE", kind: "purchased", aliases: ["tube-to-regulator", "above_core_regulator"] },
    { id: "cap", description: "Water regulator snap cap", kind: "purchased", aliases: ["regulator-cap"] },
    { id: "device", description: "Fixed water regulator", kind: "manufactured" },
    { id: "assembly", description: "Water regulator and check assembly", kind: "assembly" },
  ];
  const expected = ids(searchCatalog({ materials }, "water regulator"));
  assert.equal(expected[0], "device");
  assert.equal(expected[1], "assembly");
  assert.deepEqual(ids(searchCatalog({ materials: [...materials].reverse() }, "water regulator")), expected);
  assert.equal(ids(searchCatalog({ materials }, "regulator cap"))[0], "cap");
});

test("precise identifiers and alternate names retain their meaning", () => {
  const fixture = { materials: [
    { id: "related", description: "ZX3000 regulator cap", aliases: ["water-regulator"] },
    { id: "device", description: "Maker pressure controller", manufacturer_number: "ZX3000", aliases: ["water regulator"] },
    { id: "prefix", description: "Regulatory housing" },
  ] };
  assert.equal(ids(searchCatalog(fixture, "ZX3000"))[0], "device");
  assert.equal(ids(searchCatalog(fixture, "water regulator"))[0], "device");
  assert.equal(ids(searchCatalog({ materials: [{ id: "long", description: "Regulatory tube" }, { id: "exact", description: "Regulator tube" }] }, "regulator"))[0], "exact");
});

test("a plausible typo is labeled and an actual spelling wins", () => {
  const result = findParts("pisko");
  assert.equal(result.match, "suggestion");
  assert.ok(result.hits.some((hit) => hit.id === "HSM-0331"));
  assert.ok(result.hits.every((hit) => hit.corrections.some(({ from, to }) => from === "pisko" && to === "pisco")));
  const fixture = { materials: [{ id: "a", description: "Pisko valve" }, { id: "b", description: "Pisco regulator" }] };
  assert.deepEqual(ids(searchCatalog(fixture, "pisko")), ["a"]);
});

test("an incorrect remembered word stays visible without becoming a synonym", () => {
  const result = findParts("water reservoir snap");
  assert.equal(result.match, "suggestion");
  assert.ok(result.hits.some((hit) => hit.id === "HSM-0451"));
  assert.ok(result.hits.every((hit) => hit.unmatched.includes("reservoir") && !hit.corrections.length));
  assert.ok(!findParts("reservoir").hits.some((hit) => hit.id === "HSM-0451"));
});

test("source and assembly links follow the existing build and occurrence records", () => {
  const [cap] = findParts("HSM-0451").hits;
  assert.ok(cap.producers.some((producer) => producer.source.endsWith("rear_equipment_caps.rs") && producer.targets.includes("//:rear-equipment-caps")));
  const machine = cap.contexts.find((context) => context.material === "HSM-0001");
  assert.ok(machine.bodies.includes("regulator-snap-cap"));
  assert.ok(decodeURIComponent(cap.links.model).includes("solid: regulator-snap-cap"));
  assert.equal(findParts("HSM-0046").hits[0].producers.length, 0);
});
