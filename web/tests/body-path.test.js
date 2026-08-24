// The vocabulary every reader of a body name shares — see contracts/body-path.js.
//
// This is the foundation the whole drill-down stands on: if `cold-core/evap-coil` does not
// read as "the coil, inside the core", then the panel's path, the group highlight, the group
// hide, `isolateComponent` and the tour's beats are all wrong together and in the same way.
// It is also the one part of that machinery with no Three.js in it, so it can be held here
// rather than in a browser.

import { test } from "node:test";
import assert from "node:assert/strict";

import { heldBy, leafOf, standsIn } from "../contracts/body-path.js";

test("a body at the top of a machine is held by nothing and is its own leaf", () => {
  // 137 of the appliance's bodies are this case, and it is the one that must not have moved:
  // a machine with no sub-assembly in it reads exactly as it did before there were any.
  for (const name of ["compressor", "enclosure-back-top", "tube-fluid-16", "wago-221-415"]) {
    assert.deepEqual(heldBy(name), [], `${name} should hang off nothing`);
    assert.equal(leafOf(name), name);
  }
});

test("a body inside a sub-assembly names what holds it", () => {
  assert.deepEqual(heldBy("cold-core/evap-coil"), ["cold-core"]);
  assert.equal(leafOf("cold-core/evap-coil"), "evap-coil");
});

test("a path deeper than one level reads outermost first", () => {
  // Nothing in the tree nests twice today. The rule is stated for depth rather than for the
  // one case, so the day something does, the panel walks it without being taught.
  assert.deepEqual(heldBy("a/b/c"), ["a", "a/b"]);
  assert.equal(leafOf("a/b/c"), "c");
});

test("standsIn takes a node and everything under it, and nothing beside it", () => {
  assert.ok(standsIn("cold-core", "cold-core"), "a node stands in itself");
  assert.ok(standsIn("cold-core/evap-coil", "cold-core"));
  assert.ok(!standsIn("cold-core-stack/x", "cold-core"), "a longer name is not a child");
  assert.ok(!standsIn("compressor", "cold-core"));
  assert.ok(!standsIn("cold-core", ""), "nothing stands in nothing");
});

test("a solid index is not a branch", () => {
  // `bodyName` in viewer/step.js takes a trailing `/<digits>` off before a name reaches any of
  // this, so what arrives is already a body. Held here so the two rules cannot drift: if this
  // ever sees `display/1`, it must not read `display` as a sub-assembly holding a body `1`.
  assert.deepEqual(heldBy("display"), []);
  assert.equal(leafOf("display"), "display");
});

test("an empty or missing name is answered rather than thrown on", () => {
  for (const name of ["", null, undefined]) {
    assert.deepEqual(heldBy(name), []);
    assert.equal(leafOf(name), "");
  }
});
