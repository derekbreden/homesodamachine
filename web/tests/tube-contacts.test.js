import { test } from "node:test";
import assert from "node:assert/strict";

import {
  createTubeContactIndex,
  newTubeContacts,
  screenTubeContacts,
  segmentTriangleDistance,
} from "../public/js/viewer/tube-contacts.js";

const near = (actual, expected, tolerance = 1e-8) =>
  assert.ok(Number.isFinite(actual) && Math.abs(actual - expected) <= tolerance,
    `${actual} differs from ${expected}`);

function mesh(name, triangles) {
  const positions = Float32Array.from(triangles.flat(2));
  const indices = Uint32Array.from({ length: positions.length / 3 }, (_, i) => i);
  return { name, positions, indices };
}

const wall = [[0, -10, -10], [0, 10, -10], [0, 0, 10]];

test("tube contact screening catches a wall crossed between two distant nodes", () => {
  const result = screenTubeContacts(createTubeContactIndex([mesh("wall", [wall])]), {
    points: [[-100, 0, 0], [100, 0, 0]], radiusMm: 0.1,
  });
  assert.equal(result.status, "interference");
  assert.equal(result.contacts.length, 1);
  near(result.contacts[0].s, 100);
  near(result.contacts[0].gapMm, -0.1);
  near(result.contacts[0].point[0], 0);
});

test("capsules account for tube radius and optional surface clearance", () => {
  const index = createTubeContactIndex([mesh("wall", [wall])]);
  const route = { points: [[1, -2, 0], [1, 2, 0]], radiusMm: 0.75 };
  assert.equal(screenTubeContacts(index, route).status, "clear");
  const result = screenTubeContacts(index, route, { clearanceMm: 0.3 });
  assert.equal(result.status, "interference");
  near(result.contacts[0].gapMm, 0.25);
  assert.equal(screenTubeContacts(index, route, { clearanceMm: 0.3 }).builtMeshes, 0,
    "cached triangle tree was rebuilt");
});

test("segment to triangle distances include edges, points and degenerate faces", () => {
  near(segmentTriangleDistance([1, 1, 2], [1, 1, 4],
    [0, 0, 0], [4, 0, 0], [0, 4, 0]).distance, 2);
  near(segmentTriangleDistance([2, -1, -1], [2, -1, 1],
    [0, 0, 0], [4, 0, 0], [0, 4, 0]).distance, 1);
  near(segmentTriangleDistance([0, 3, 4], [0, 3, 4],
    [0, 0, 0], [0, 0, 0], [0, 0, 0]).distance, 5);
  near(segmentTriangleDistance([1, 1, 0], [1, 2, 0],
    [0, 0, 0], [0, 0, 0], [2, 0, 0]).distance, 1);
  near(segmentTriangleDistance([1, 1, 0], [1, 2, 0],
    [0, 0, 0], [1, 0, 0], [2, 0, 0]).distance, 1);
});

test("a finite grip exemption does not exempt later contact with the same face", () => {
  const plane = [[-100, -100, 0], [100, -100, 0], [0, 100, 0]];
  const index = createTubeContactIndex([mesh("anchor", [plane])]);
  const route = {
    points: [[-10, 0, 0], [10, 0, 0]], radiusMm: 0.5,
    allowedContacts: [{ name: "anchor", s0: 0, s1: 2 }],
  };
  const result = screenTubeContacts(index, route);
  assert.equal(result.status, "interference");
  assert.ok(result.contacts.some((contact) => contact.s >= 2), "later face contact was hidden by grip exemption");
  assert.equal(screenTubeContacts(index, {
    ...route, allowedContacts: [{ name: "anchor", s0: 0, s1: 20 }],
  }).status, "clear");
});

test("excluded tube names do not remove other bodies or their separate solid suffixes", () => {
  const index = createTubeContactIndex([
    mesh("tube-fluid-18/0", [wall]), mesh("anchor/1", [wall]),
  ]);
  const result = screenTubeContacts(index, {
    points: [[-1, 0, 0], [1, 0, 0]], radiusMm: 0.5,
    excludeNames: ["tube-fluid-18"],
  });
  assert.deepEqual(result.contacts.map((contact) => contact.name), ["anchor"]);
});

test("BVH screening agrees with all-triangle distances for nearby and distant segments", () => {
  const triangles = Array.from({ length: 96 }, (_, i) => {
    const x = i * 0.7 - 20;
    const y = 5 * Math.sin(i * 1.7);
    const z = 5 * Math.cos(i * 2.3);
    return [[x, y - 1, z - 1], [x + 0.5, y + 1, z - 1], [x - 0.5, y, z + 1]];
  });
  const index = createTubeContactIndex([mesh("fixture", triangles)]);
  for (const y of [0, 2, 5, 20]) {
    const p = [-5, y, 0], q = [25, y, 0], radiusMm = 1.4;
    const nearest = Math.min(...triangles.map((tri) => segmentTriangleDistance(p, q, ...tri).distance));
    const result = screenTubeContacts(index, { points: [p, q], radiusMm });
    assert.equal(result.status, nearest <= radiusMm ? "interference" : "clear");
    if (result.contacts.length) near(result.contacts[0].gapMm, nearest - radiusMm, 1e-6);
  }
});

test("contact result truncation preserves interference counts", () => {
  const index = createTubeContactIndex([mesh("wall", [wall])]);
  const result = screenTubeContacts(index, {
    points: [[-5, 0, 0], [5, 0, 0], [-5, 0, 0], [5, 0, 0]], radiusMm: 0.5,
  }, { maxContacts: 1 });
  assert.equal(result.status, "interference");
  assert.equal(result.contacts.length, 1);
  assert.equal(result.totalContacts, 3);
  assert.equal(result.truncated, true);
});

test("resampling the same straight tube does not invent new surface contacts", () => {
  const face = [[-100, -100, 0], [100, -100, 0], [0, 100, 0]];
  const index = createTubeContactIndex([mesh("panel", [face])]);
  const nominalArcLengths = [0, 10, 20];
  const arcLengths = Array.from({ length: 401 }, (_, i) => i * 0.05);
  const route = (arc) => ({
    points: arc.map((s) => [s - 10, 0, 0.2]), arcLengths: arc, radiusMm: 0.5,
  });
  const nominal = screenTubeContacts(index, route(nominalArcLengths));
  const fine = screenTubeContacts(index, route(arcLengths), { maxContacts: 500 });
  assert.equal(nominal.totalContacts, 2);
  assert.equal(fine.totalContacts, 400);
  assert.equal(fine.truncated, false);
  assert.deepEqual(newTubeContacts(nominal, fine, { nominalArcLengths, arcLengths }), []);
  assert.deepEqual(newTubeContacts(fine, nominal, {
    nominalArcLengths: arcLengths, arcLengths: nominalArcLengths,
  }), [], "contact comparison depends on which unchanged sampling is nominal");
});

test("new contact comparison distinguishes remote patches and other bodies", () => {
  const nearPatch = { name: "panel", s: 5, segment: 0 };
  const remotePatch = { name: "panel", s: 65, segment: 6 };
  const otherBody = { name: "pump", s: 5, segment: 0 };
  const arcLengths = Array.from({ length: 11 }, (_, i) => i * 10);
  assert.deepEqual(newTubeContacts({ contacts: [nearPatch] }, {
    contacts: [nearPatch, remotePatch, otherBody],
  }, { nominalArcLengths: arcLengths, arcLengths }), [remotePatch, otherBody]);
});

test("comparison preserves uncertainty when a nominal contact list is capped", () => {
  const nominal = {
    contacts: [{ name: "panel", s: 5, segment: 0 }], totalContacts: 2, truncated: true,
  };
  const possibleNew = { name: "panel", s: 65, segment: 6 };
  const scenario = { contacts: [possibleNew], totalContacts: 1, truncated: false };
  const arcLengths = Array.from({ length: 11 }, (_, i) => i * 10);
  assert.deepEqual(newTubeContacts(nominal, scenario, {
    nominalArcLengths: arcLengths, arcLengths,
  }), [possibleNew], "an omitted nominal contact cannot be inferred as a match");
  assert.equal(nominal.truncated, true, "comparison erased the incomplete-baseline flag");
  assert.equal(scenario.truncated, false);
});

test("a sleeve elsewhere on a coarse segment does not enlarge its bare portion", () => {
  const face = [[0, -5, 0], [4, -5, 0], [2, 5, 0]];
  const index = createTubeContactIndex([mesh("face", [face])]);
  const route = { points: [[0, 0, 2], [20, 0, 2]], radiusMm: 1 };
  assert.equal(screenTubeContacts(index, {
    ...route, radiusRanges: [{ s0: 10, s1: 20, radiusMm: 3 }],
  }).status, "clear");
  const local = screenTubeContacts(index, {
    ...route, radiusRanges: [{ s0: 1, s1: 3, radiusMm: 3 }],
  });
  assert.equal(local.status, "interference");
  near(local.contacts[0].radiusMm, 3);
  assert.ok(local.contacts[0].s >= 1 && local.contacts[0].s <= 3);
});

test("sleeve windows follow supplied developed arc length rather than sampled chords", () => {
  const face = [[9, -4, 0], [11, -4, 0], [10, 4, 0]];
  const index = createTubeContactIndex([mesh("face", [face])]);
  const route = {
    points: [[0, 0, 2], [20, 0, 2]], radiusMm: 1,
    radiusRanges: [{ s0: 18, s1: 22, radiusMm: 3 }],
  };
  assert.equal(screenTubeContacts(index, route).status, "clear");
  const result = screenTubeContacts(index, { ...route, arcLengths: [0, 40] });
  assert.equal(result.status, "interference");
  assert.ok(result.contacts[0].s >= 18 && result.contacts[0].s <= 22);
  assert.ok(result.contacts[0].point[0] >= 9 && result.contacts[0].point[0] <= 11);
});

test("overlapping sleeve windows use the largest active radius", () => {
  const face = [[9, -4, 0], [11, -4, 0], [10, 4, 0]];
  const index = createTubeContactIndex([mesh("face", [face])]);
  const route = {
    points: [[0, 0, 3], [20, 0, 3]], radiusMm: 1,
    radiusRanges: [{ s0: 0, s1: 10, radiusMm: 2.5 }],
  };
  assert.equal(screenTubeContacts(index, route).status, "clear");
  const result = screenTubeContacts(index, {
    ...route, radiusRanges: [...route.radiusRanges, { s0: 8, s1: 12, radiusMm: 4 }],
  });
  assert.equal(result.status, "interference");
  near(result.contacts[0].radiusMm, 4);
  near(result.contacts[0].gapMm, -1);
});

test("invalid sleeve windows and contact arc lengths are rejected", () => {
  const index = createTubeContactIndex([]);
  const route = { points: [[0, 0, 0], [20, 0, 0]], radiusMm: 1 };
  for (const ranges of [null, {}, [null], [{ s0: 2, s1: 2, radiusMm: 3 }],
    [{ s0: 2, s1: 1, radiusMm: 3 }], [{ s0: -1, s1: 1, radiusMm: 3 }],
    [{ s0: 0, s1: 1, radiusMm: -1 }], [{ s0: 0, s1: Infinity, radiusMm: 3 }]]) {
    assert.throws(() => screenTubeContacts(index, { ...route, radiusRanges: ranges }), /sleeve/i);
  }
  for (const arcLengths of [[0], [10, 0], [0, NaN]]) {
    assert.throws(() => screenTubeContacts(index, { ...route, arcLengths }), /arc length/i);
  }
});

test("surface screening states that fully embedded spans are outside its detection", () => {
  const square = (x) => [
    [[x, -10, -10], [x, 10, -10], [x, 10, 10]],
    [[x, -10, -10], [x, 10, 10], [x, -10, 10]],
  ];
  const faces = [
    ...square(-10), ...square(10),
    ...square(-10).map((tri) => tri.map(([x, y, z]) => [y, x, z])),
    ...square(10).map((tri) => tri.map(([x, y, z]) => [y, x, z])),
    ...square(-10).map((tri) => tri.map(([x, y, z]) => [y, z, x])),
    ...square(10).map((tri) => tri.map(([x, y, z]) => [y, z, x])),
  ];
  const result = screenTubeContacts(createTubeContactIndex([mesh("solid-box", faces)]), {
    points: [[-1, 0, 0], [1, 0, 0]], radiusMm: 0.5,
  });
  assert.equal(result.method, "capsule-surface");
  assert.equal(result.status, "clear");
  assert.ok(result.limitations.some((text) => /inside a solid|enclosed inside/i.test(text)),
    "surface-only result lost its volume limitation");
});
