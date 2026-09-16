import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { ENCLOSURE_FASTENERS, REVEAL_STATES, fastenerMotion, revealMotion } from "../public/js/tour/reveal-plan.js";

test("the tour's six screw facsimiles stand on the enclosure's seam axes", () => {
  const facts = JSON.parse(fs.readFileSync(new URL("../../hardware/manifold-layout/enclosure-assembly.facts.json", import.meta.url)));
  const source = fs.readFileSync(new URL("../../hardware/printed-parts/enclosure/enclosure/enclosure.py", import.meta.url), "utf8");
  const iface = fs.readFileSync(new URL("../../hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py", import.meta.url), "utf8");
  const slip = fs.readFileSync(new URL("../../hardware/printed-parts/cadlib/fits.py", import.meta.url), "utf8");
  const slipValue = Number(slip.match(/^slip\s*=\s*([\d.]+)/m)[1]);
  const wall = Number(iface.match(/^wall\s*=\s*([\d.]+)/m)[1]);
  assert.equal(ENCLOSURE_FASTENERS.axisY, facts.box.y_joint + (3 + 2 * slipValue + 2 * wall) / 2);
  assert.equal(ENCLOSURE_FASTENERS.headSeatDepth, Number(source.match(/^head_cbore_depth\s*=\s*([\d.]+)/m)[1]));
  assert.equal(ENCLOSURE_FASTENERS.shankLength, Number(source.match(/^screw_len\s*=\s*([\d.]+)/m)[1]));
  const expected = facts.box.y_bosses.map(([, x, , z]) => [x, z]);
  const actual = [-1, 1].flatMap((sign) => ENCLOSURE_FASTENERS.levels.map((z) => [sign * ENCLOSURE_FASTENERS.exteriorX, z]));
  assert.deepEqual(actual, expected);
});

test("every seam screw clears its socket before any enclosure quadrant moves", () => {
  for (let i = 0; i < 6; i++) {
    assert.ok(fastenerMotion(REVEAL_STATES.screws.enclosure, i).distance > ENCLOSURE_FASTENERS.shankLength);
    assert.ok(fastenerMotion(REVEAL_STATES.screws.enclosure, i).turns >= 6);
  }
  for (const name of ["enclosure-front-top", "enclosure-back-top", "enclosure-front-bottom", "enclosure-back-bottom"]) {
    assert.deepEqual(revealMotion(name, REVEAL_STATES.screws).map((n) => n || 0), [0, 0, 0]);
    assert.ok(revealMotion(name, REVEAL_STATES.open).some((n) => Math.abs(n) > 100));
  }
});

test("each display and printed wall label travels with its enclosure quadrant", () => {
  for (const value of [0.45, 0.62, 0.85, 1]) {
    const state = { enclosure: value };
    for (const name of ["display", "display-cover", "display-gasket", "pump-jack"]) {
      assert.deepEqual(revealMotion(name, state), revealMotion("enclosure-front-top", state));
    }
    for (const name of ["nameplate", "nameplate-ink", "bulkhead-ring-water", "bulkhead-ring-water-word"]) {
      assert.deepEqual(revealMotion(name, state), revealMotion("enclosure-back-top", state));
    }
  }
});

test("nested layers open before the carbonator wall and close deterministically on seek", () => {
  assert.ok(revealMotion("funnel", { enclosure: 0.38 })[2] > 0);
  assert.equal(revealMotion("enclosure-front-top", { enclosure: 0.38 })[1] || 0, 0);
  for (const name of ["funnel-drain-clamp", "funnel-drain-stub", "funnel-drain-union"]) {
    assert.deepEqual(revealMotion(name, REVEAL_STATES.open), revealMotion("funnel", REVEAL_STATES.open));
  }
  assert.ok(revealMotion("foam-cap-top", { coldCore: 0.25 })[2] > 0);
  assert.equal(revealMotion("foam-shell", { coldCore: 0.25 })[2] || 0, 0);
  assert.deepEqual(revealMotion("carbonator-tube", REVEAL_STATES.core), [0, 0, 0]);
  assert.deepEqual(revealMotion("carbonator-tube", REVEAL_STATES.carbonator), revealMotion("evap-coil", REVEAL_STATES.carbonator));
  for (const name of ["foam-shell", "foam-cap-top", "foam-cap-lid-bottom", "carbonator-tube", "evap-coil"]) {
    assert.deepEqual(revealMotion(`cold-core/${name}`, REVEAL_STATES.carbonator), revealMotion(name, REVEAL_STATES.carbonator));
  }
  for (const name of ["sparge-stone-1", "reservoir-a", "reservoir-b", "endcap-bottom"]) {
    assert.deepEqual(revealMotion(name, REVEAL_STATES.carbonator), [0, 0, 0]);
  }
  for (const name of ["enclosure-front-top", "foam-shell", "carbonator-tube"]) {
    const first = revealMotion(name, { enclosure: 0.7, coldCore: 0.6, carbonator: 0.5 });
    revealMotion(name, REVEAL_STATES.carbonator);
    revealMotion(name, REVEAL_STATES.closed);
    assert.deepEqual(revealMotion(name, { enclosure: 0.7, coldCore: 0.6, carbonator: 0.5 }), first);
    assert.deepEqual(revealMotion(name, REVEAL_STATES.closed).map((n) => n || 0), [0, 0, 0]);
  }
});

test("park clears the rear close-ups while preserving internal seats and closed transforms", () => {
  const parked = { ...REVEAL_STATES.open, park: 1 };
  for (const name of ["enclosure-front-top", "enclosure-front-bottom"]) {
    assert.equal(revealMotion(name, parked)[1] - revealMotion(name, REVEAL_STATES.open)[1], -1200);
  }
  for (const name of ["enclosure-back-top", "enclosure-back-bottom", "bulkhead-ring-water"]) {
    assert.equal(revealMotion(name, parked)[1] - revealMotion(name, REVEAL_STATES.open)[1], 1200);
  }
  for (const name of ["bulkhead-water", "digiten-flow", "pcba", "pump-a-head"]) {
    assert.deepEqual(revealMotion(name, parked), [0, 0, 0]);
  }
  assert.equal(revealMotion("funnel", parked)[2] - revealMotion("funnel", REVEAL_STATES.open)[2], 500);
  for (const name of ["enclosure-front-top", "enclosure-back-top", "funnel"]) {
    assert.deepEqual(revealMotion(name, { ...REVEAL_STATES.closed, park: 1 }).map((n) => n || 0), [0, 0, 0]);
  }
});
