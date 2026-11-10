// Location contract checks distinguish physical copies from compound CAD representations.
import { test } from "node:test";
import assert from "node:assert/strict";
import { instancesInScene, instanceMaterialHash, componentUnitsInScene, unitForBody } from "../contracts/material-instances.js";
import { explodeBom, occurrenceBodies, materialForComponent } from "../contracts/materials.js";
import { unitQuantities } from "../contracts/material-quantities.js";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { readMeshHeader } from "../lib/feature-catalog.js";
import { materialInstances } from "../lib/material-instances.js";
import { fileURLToPath } from "node:url";

const part = { id: "part", description: "Part", kind: "purchased" };
const catalog = item => ({ materials: [part, { id: "root", description: "Machine", kind: "assembly", bom: { items: [{ material: "part", ...item }] } }] });

test("component clicks take every body of one physical copy, and opening the part exposes its bodies", () => {
  const actual = catalog({ quantity: 2, unit: "ea", placements: [
    { label: "Left pump", bodies: ["left/head", "left/motor"] },
    { label: "Right pump", bodies: ["right/head", "right/motor"] },
  ] });
  const names = ["left/head/1", "left/motor", "right/head", "right/motor/2"];
  const units = componentUnitsInScene(actual, "root", names);
  assert.equal(units.length, 2);
  assert.equal(unitForBody(units, "left/motor").name, "left/head");
  assert.equal(unitForBody(units, "right/motor/2").label, "Right pump");
  assert.deepEqual(unitForBody(units, "left/head").bodies, ["left/head", "left/motor"]);
  assert.equal(unitForBody(units, "elsewhere"), null);
  assert.deepEqual(componentUnitsInScene(actual, "part", names), []);
});

test("component units do not combine stock quantities, unresolved copies or logical assemblies", () => {
  assert.deepEqual(componentUnitsInScene(catalog({ quantity: 2, unit: "m", bodies: ["a", "b"] }), "root", ["a", "b"]), []);
  assert.deepEqual(componentUnitsInScene(catalog({ quantity: 2, unit: "ea", bodies: ["a", "b", "c"] }), "root", ["a", "b", "c"]), []);
  const actual = catalog({ quantity: 1, bodies: ["a", "b"] });
  actual.materials[0] = { ...part, kind: "assembly" };
  assert.deepEqual(componentUnitsInScene(actual, "root", ["a", "b"]), []);
});

test("explicit tube placements keep each routed length together without combining separate runs", () => {
  const actual = catalog({ quantity: 2, unit: "m", placements: [
    { label: "Run A", bodies: ["a/start", "a/end"] },
    { label: "Run B", bodies: ["b/start", "b/end"] },
  ] });
  const units = componentUnitsInScene(actual, "root", ["a/start", "a/end", "b/start", "b/end"]);
  assert.deepEqual(units.map(unit => unit.bodies), [["a/start", "a/end"], ["b/start", "b/end"]]);
});

test("a single installed unit retains every bound body and collapses numeric solids", () => {
  const instances = instancesInScene(catalog({ quantity: 1, bodies: ["regulator", "collet"] }), "root", "part",
    ["collet/1", "regulator/1", "regulator/2", "unrelated"]);
  assert.equal(instances.length, 1);
  assert.equal(instances[0].name, "regulator");
  assert.deepEqual(instances[0].bodies, ["regulator", "collet"]);
});

test("repeated physical copies have separate locations in authored binding order", () => {
  const instances = instancesInScene(catalog({ quantity: 2, bodies: ["relay-2", "relay-1"] }), "root", "part", ["relay-1", "relay-2"]);
  assert.deepEqual(instances.map(instance => instance.bodies), [["relay-2"], ["relay-1"]]);
});

test("a compound repeated binding keeps each copy's nested geometry together", () => {
  const instances = instancesInScene(catalog({ quantity: 2, bodies: ["left", "right"] }), "root", "part",
    ["right/body", "left/body", "left/collet", "right/collet"]);
  assert.deepEqual(instances.map(instance => instance.bodies), [["left/body", "left/collet"], ["right/body", "right/collet"]]);
  assert.equal(instanceMaterialHash("root", "left/body"), "material:root?instance=left%2Fbody");
});

test("undrawn BOM quantities do not create pretend locations", () => {
  assert.deepEqual(instancesInScene(catalog({ quantity: 4, bodies: ["missing"] }), "root", "part", ["elsewhere"]), []);
});

test("a stock length is not interpreted as a count of installed copies", () => {
  const units = instancesInScene(catalog({ quantity: 2, unit: "m", bodies: ["tube", "sleeve"] }),
    "root", "part", ["tube", "sleeve"]);
  assert.deepEqual(units.map(unit => unit.bodies), [["tube", "sleeve"]]);
});

test("authored placements distinguish compound copies and preserve nested frames", () => {
  const nested = { materials: [part,
    { id: "root", bom: { items: [{ material: "stage", quantity: 1, prefix: "frame/" }] } },
    { id: "stage", description: "Stage", bom: { items: [{ material: "part", quantity: 3, placements: [
      { label: "Left copy", bodies: ["left/body", "left/collet"] },
      { label: "Right copy", bodies: ["right/body", "right/collet"] },
      { label: "Undrawn copy", bodies: ["missing"] },
    ] }] } },
  ] };
  const names = ["frame/right/body/1", "frame/left/body/1", "frame/left/collet", "frame/right/collet", "left/body"];
  const units = instancesInScene(nested, "root", "part", names);
  assert.deepEqual(units.map(unit => [unit.label, unit.bodies]), [
    ["Left copy", ["frame/left/body", "frame/left/collet"]],
    ["Right copy", ["frame/right/body", "frame/right/collet"]],
  ]);
  const row = explodeBom(nested, "root").find(row => row.material.id === "part");
  assert.deepEqual(new Set(occurrenceBodies(nested, row.path, names)), new Set(names.filter(name => name.startsWith("frame/"))));
});

test("the machine's compound purchased parts resolve complete individual placements", () => {
  const hardware = fileURLToPath(new URL("../../hardware/", import.meta.url));
  const actual = readMaterialCatalog(hardware), file = "manifold-layout/enclosure-assembly.step";
  const names = readMeshHeader(hardware + file + ".mesh").meshes.map(mesh => mesh.name);
  const quantities = unitQuantities(actual, "HSM-0001", { finish: "black" });
  const units = componentUnitsInScene(actual, "HSM-0001", names, { finish: "black" });
  for (const unit of units) {
    const location = instancesInScene(actual, "HSM-0001", unit.material, names, { finish: "black" })
      .find(instance => instance.name === unit.name);
    assert.deepEqual(unit.bodies, location.bodies, unit.name);
    for (const body of unit.bodies) assert.equal(unitForBody(units, body).name, unit.name, body);
  }
  for (const id of ["HSM-0331", "HSM-0047", "HSM-0044", "HSM-0061", "HSM-0042", "HSM-0325"]) {
    const units = instancesInScene(actual, "HSM-0001", id, names);
    assert.equal(units.length, quantities.get(id), id);
    assert.equal(new Set(units.flatMap(unit => unit.bodies)).size, units.flatMap(unit => unit.bodies).length, id);
    for (const unit of units) assert.equal(materialForComponent(actual, file, unit.name).id, id, unit.name);
  }
  assert.deepEqual(instancesInScene(actual, "HSM-0001", "HSM-0044", names).map(unit => unit.label), ["Flavor A pump", "Flavor B pump"]);
  const screws = instancesInScene(actual, "HSM-0001", "HSM-0139", names);
  assert.ok(screws.length > 1 && screws.length < quantities.get("HSM-0139"));
  assert.ok(screws.every(unit => unit.bodies.length === 1));
  const tubes = materialInstances(hardware, actual, "HSM-0107").groups.find(group => group.assembly === "HSM-0002").instances;
  assert.equal(tubes.length, unitQuantities(actual, "HSM-0002", { finish: "black" }).get("HSM-0107"));
  assert.ok(tubes.every(unit => unit.bodies.length > 1));
});
