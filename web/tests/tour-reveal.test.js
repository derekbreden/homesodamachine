import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { ENCLOSURE_FASTENERS, REVEAL_DEFAULTS, REVEAL_STATES, corePartGroup,
  fastenerMotion, revealMotion, revealOpacity } from "../public/js/tour/reveal-plan.js";

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

test("caps clear the shell's downstroke and the shell parks beside the contents", () => {
  assert.ok(revealMotion("funnel", { enclosure: 0.38 })[2] > 0);
  assert.equal(revealMotion("enclosure-front-top", { enclosure: 0.38 })[1] || 0, 0);
  for (const name of ["funnel-drain-clamp", "funnel-drain-stub", "funnel-drain-union"]) {
    assert.deepEqual(revealMotion(name, REVEAL_STATES.open), revealMotion("funnel", REVEAL_STATES.open));
  }
  assert.ok(revealMotion("foam-cap-top", { coldCore: 0.25 })[2] > 0);
  assert.equal(revealMotion("foam-shell", { coldCore: 0.25 })[2] || 0, 0);
  const top = revealMotion("foam-cap-top", REVEAL_STATES.caps);
  const bottom = revealMotion("foam-cap-bottom", REVEAL_STATES.caps);
  assert.ok(top[2] > 0 && bottom[2] < 0);
  assert.ok(top[0] > 181 && bottom[0] > 181, "both 181 mm caps clear the shell's footprint away from the camera");
  assert.deepEqual(revealMotion("foam-shell", REVEAL_STATES.caps).map((n) => n || 0), [0, 0, 0]);
  assert.deepEqual(revealMotion("foam-shell", { coreShell: 0.4 }), [0, 0, -230]);
  assert.deepEqual(revealMotion("foam-shell", REVEAL_STATES.core), [0, 330, -60]);
  assert.deepEqual(revealMotion("copper-plug-west", REVEAL_STATES.core), revealMotion("foam-shell", REVEAL_STATES.core));
});

test("the coil, intact carbonator and reservoirs separate with all their accessories", () => {
  const groups = {
    coil: ["evap-coil", "evap-tail-inlet", "evap-tail-outlet", "probe-coil-ds18s20"],
    carbonator: ["carbonator-tube", "endcap-top", "endcap-bottom", "float-rod-carb", "float-carb",
      "water-inlet-jet-cap-nominal", "collet-co2-in", "collet-water-in", "collet-carb-water-out",
      "carbonator-elbow-prv", "prv-sv125", "prv-shroud", "probe-carbonator-ds18b20", "reed-bridge",
      "reed-carb-1", "line-co2-in", "line-water-in", "line-carb-water-out", "line-prv-vent"],
    "reservoir-a": ["reservoir-a", "reservoir-a-cap", "bulkhead-reservoir-a", "bulkhead-seal-a",
      "vent-membrane-a", "float-rod-a", "float-a", "reed-a-4", "line-reservoir-a", "line-reservoir-a-fill"],
    "reservoir-b": ["reservoir-b", "reservoir-b-cap", "bulkhead-reservoir-b", "bulkhead-seal-b",
      "vent-membrane-b", "float-rod-b", "float-b", "reed-b-4", "line-reservoir-b", "line-reservoir-b-fill"],
  };
  const vectors = { coil: [0, 0, 140], carbonator: [0, 0, -80], "reservoir-a": [0, 65, 0], "reservoir-b": [0, -65, 0] };
  for (const [group, names] of Object.entries(groups)) {
    for (const name of names) {
      assert.equal(corePartGroup(name), group, name);
      assert.deepEqual(revealMotion(name, REVEAL_STATES.spread), vectors[group], name);
      assert.deepEqual(revealMotion(`cold-core/${name}`, REVEAL_STATES.spread), vectors[group], name);
    }
  }
});

test("core isolation preserves the subject throughout a reversible fade", () => {
  for (const amount of [0, 0.25, 0.5, 0.75, 1]) {
    for (const name of ["cold-core/foam-shell", "cold-core/evap-coil", "cold-core/reservoir-a"]) {
      assert.equal(revealOpacity(name, { coreIsolation: amount }), 1);
    }
    const opacity = revealOpacity("pcba", { coreIsolation: amount });
    assert.ok(opacity >= 0 && opacity <= 1);
    assert.equal(opacity + revealOpacity("pcba", { coreIsolation: 1 - amount }), 1);
  }
  assert.equal(revealOpacity("pcba", REVEAL_STATES.isolated), 0);
  assert.equal(revealOpacity("pcba", REVEAL_STATES.open), 1);
});

test("parked covers become translucent during the spread and return before closing", () => {
  const covers = ["foam-shell", "copper-plug-west", "copper-plug-port", "foam-cap-top",
    "foam-cap-lid-top", "foam-cap-bottom", "foam-cap-lid-bottom"];
  for (const name of covers) {
    assert.equal(revealOpacity(`cold-core/${name}`, REVEAL_STATES.core), 1, name);
    assert.ok(Math.abs(revealOpacity(`cold-core/${name}`, REVEAL_STATES.spread) - 0.12) < 1e-12, name);
    assert.ok(Math.abs(revealOpacity(name, { coreSpread: 0.5 }) - 0.56) < 1e-12, name);
    const amounts = [0, 0.25, 0.5, 0.75, 1];
    const forward = amounts.map((coreSpread) => revealOpacity(name, { coreSpread }));
    const backward = [...amounts].reverse().map((coreSpread) => revealOpacity(name, { coreSpread }));
    assert.deepEqual(forward.reverse(), backward, name);
  }
  for (const name of ["cold-core/evap-coil", "cold-core/carbonator-tube", "cold-core/reservoir-a", "cold-core/reservoir-b"]) {
    assert.equal(revealOpacity(name, REVEAL_STATES.spread), 1, name);
  }
  assert.equal(revealOpacity("pcba", REVEAL_STATES.spread), 0);
  assert.equal(revealOpacity("pcba", { coreSpread: 1 }), 1);
});

test("seeking through the reverse sequence retraces every pose exactly", () => {
  const names = ["enclosure-front-top", "foam-shell", "foam-cap-top", "foam-cap-lid-top", "foam-cap-bottom",
    "foam-cap-lid-bottom", "evap-coil", "carbonator-tube", "reservoir-a", "reservoir-b"];
  const states = Array.from({ length: 21 }, (_, i) => ({ ...REVEAL_STATES.spread, coreCaps: i / 20, coreShell: i / 20, coreSpread: i / 20 }));
  for (const name of names) {
    const forward = states.map((state) => revealMotion(name, state));
    const reverse = [...states].reverse().map((state) => revealMotion(name, state));
    assert.deepEqual(reverse, forward.reverse(), name);
    assert.deepEqual(revealMotion(name, REVEAL_DEFAULTS).map((n) => n || 0), [0, 0, 0]);
  }
});

test("the actual core payload leaves no accessory behind and fits its covers beside the contents", (t) => {
  const payload = new URL("../../hardware/manifold-layout/enclosure-assembly.step.mesh", import.meta.url);
  if (!fs.existsSync(payload)) return t.skip("CAD payload is not materialized");
  const bytes = fs.readFileSync(payload);
  const headerLength = bytes.readUInt32LE(0);
  const header = JSON.parse(bytes.subarray(4, 4 + headerLength).toString());
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  let bodies = 0;
  for (const mesh of header.meshes.filter((m) => m.name.startsWith("cold-core/"))) {
    assert.ok(corePartGroup(mesh.name), `unassigned accessory: ${mesh.name}`);
    const delta = revealMotion(mesh.name, REVEAL_STATES.spread);
    const [offset, count] = mesh.pos;
    for (let i = 0; i < count; i++) {
      const axis = i % 3;
      const coordinate = bytes.readFloatLE(4 + headerLength + offset + i * 4) + delta[axis];
      lo[axis] = Math.min(lo[axis], coordinate);
      hi[axis] = Math.max(hi[axis], coordinate);
    }
    bodies++;
  }
  assert.ok(bodies > 50, "the complete cold core is present");
  for (let axis = 0; axis < 3; axis++) assert.ok(hi[axis] - lo[axis] < [620, 800, 620][axis], `${"XYZ"[axis]} extent: ${hi[axis] - lo[axis]}`);
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
