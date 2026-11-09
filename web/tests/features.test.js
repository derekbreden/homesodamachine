// Surface identities retain their membership and installed instance without geometry production.
import { test } from "node:test";
import assert from "node:assert/strict";
import { featureKey, splitFeatureKey, containsTriangle, featureIndices, objectFeatures, matchFeatures, validFeatures } from "../contracts/features.js";

test("a feature remains distinct in repeated installed instances", () => {
  const object = { meshes: [{ features: [{ id: "mount", label: "Relay mount", related: ["relay-2"], triangles: [[0,1],[4,4]] }] }] };
  const a = objectFeatures({ entries: [{ name: "first" }] }, object)[0];
  const b = objectFeatures({ entries: [{ name: "second" }] }, object)[0];
  assert.notEqual(a.key, b.key);
  assert.deepEqual(splitFeatureKey(a.key), { body: "first", id: "mount" });
  assert.equal(featureKey("first", "mount"), a.key);
  assert.deepEqual(matchFeatures("relay mount", [a,b]), [a,b]);
  assert.deepEqual(matchFeatures(a.key, [a,b]), [a]);
  assert.ok(containsTriangle(a, 1)); assert.ok(!containsTriangle(a, 3));
  assert.deepEqual([...featureIndices(new Uint32Array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]), a)], [0,1,2,3,4,5,12,13,14]);
});

test("membership ranges are ordered, disjoint and inside the existing mesh", () => {
  const feature = triangles => ({ id: "well", label: "Connector well", triangles });
  assert.equal(validFeatures([feature([[0,1],[4,5]])], 6).length, 1);
  for (const ranges of [[[4,5],[0,1]], [[0,3],[2,4]], [[0,6]], [[-1,1]]])
    assert.equal(validFeatures([feature(ranges)], 6).length, 0);
  assert.equal(matchFeatures("mains live", [{id:"well",label:"Well",related:["wago-h"]}]).length,1);
});

test("remembered grip words find handholds while exact feature identities win", () => {
  const handhold = { key: "enclosure-back-bottom::west-handhold", id: "west-handhold", label: "west lifting handhold" };
  for (const query of ["grip", "grips", "west grip", "lifting grips"])
    assert.deepEqual(matchFeatures(query, [handhold]), [handhold]);
  const grip = { key: "reservoir::grip", id: "grip", label: "Bottle grip" };
  assert.deepEqual(matchFeatures("grip", [handhold, grip]), [grip]);
  assert.deepEqual(matchFeatures(handhold.key, [handhold, grip]), [handhold]);
});
