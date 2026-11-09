// Location contract checks distinguish physical copies from compound CAD representations.
import { test } from "node:test";
import assert from "node:assert/strict";
import { instancesInScene, instanceMaterialHash } from "../contracts/material-instances.js";

const part = { id: "part", description: "Part" };
const catalog = item => ({ materials: [part, { id: "root", description: "Machine", bom: { items: [{ material: "part", ...item }] } }] });

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
