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
