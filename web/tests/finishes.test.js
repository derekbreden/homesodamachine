// The finish table, held across the two languages that have to agree on it.
//
// A COLOUR IS HALF OF WHAT A MATERIAL LOOKS LIKE. The other half — how the stock takes the
// light — cannot ride a STEP, which carries `COLOUR_RGB` and nothing else, so it is carried
// beside the model in `web/public/finishes.json` and found again by the colour it belongs to.
// hardware/scripts/_finishes.py writes that file and web/public/js/viewer/step.js reads it,
// which are different languages in different trees with no import between them.
//
// WHAT DISAGREEMENT COSTS IS SILENCE, again. `finishFor` answers a colour it cannot place with
// the default, and the default is a plausible surface — so a table that stopped matching would
// not throw and would not look broken. It would draw the whole machine in one plastic, which is
// the thing this table exists to stop.
//
// The two facts that have to hold are the tolerance and the gap. A finish is matched on DISTANCE
// because neither end can share a rounding: the palette is linear, where the black end is
// crowded enough that a byte holds two of its colours. That only works while the radius is
// smaller than the gap between the two nearest materials — otherwise a body could sit inside two
// rows at once and take whichever the loop met first.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..", "..");

const read = (rel) => fs.readFileSync(path.join(ROOT, rel), "utf8");
const table = () => JSON.parse(read("web/public/finishes.json")).finishes;

// `const FINISH_TOL2 = 4e-4 * 4e-4;` -> 4e-4, the radius step.js actually matches inside.
function viewerTolerance() {
  const js = read("web/public/js/viewer/step.js");
  const m = /FINISH_TOL2\s*=\s*([0-9.e-]+)\s*\*\s*([0-9.e-]+)/.exec(js);
  assert.ok(m, "step.js states no FINISH_TOL2");
  assert.equal(m[1], m[2], "FINISH_TOL2 is a squared radius: state it as r * r");
  return Number(m[1]);
}

const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

test("every row is a linear triple with a finish on it", () => {
  const rows = table();
  assert.ok(rows.length > 40, `only ${rows.length} materials — the table is not the tree's`);
  for (const r of rows) {
    assert.equal(r.rgb.length, 3, `${JSON.stringify(r)} is not a triple`);
    for (const c of r.rgb) {
      assert.ok(Number.isFinite(c) && c >= 0 && c <= 1, `${c} is not a linear component`);
    }
    assert.ok(r.roughness >= 0 && r.roughness <= 1, `roughness ${r.roughness} is out of range`);
    assert.ok(r.metalness >= 0 && r.metalness <= 1, `metalness ${r.metalness} is out of range`);
  }
});

test("no two materials sit inside one match radius", () => {
  const rows = table();
  const tol = viewerTolerance();
  let closest = Infinity;
  let pair = null;
  for (let i = 0; i < rows.length; i++) {
    for (let j = i + 1; j < rows.length; j++) {
      const d = dist(rows[i].rgb, rows[j].rgb);
      if (d < closest) { closest = d; pair = [rows[i], rows[j]]; }
    }
  }
  // Two radii, because a body between two rows must fall outside BOTH of them to be ambiguous.
  assert.ok(
    closest > 2 * tol,
    `two materials stand ${closest} apart, inside twice the ${tol} match radius — a body ` +
    `between them would take whichever the loop met first: ${JSON.stringify(pair)}`,
  );
});

test("the table carries no duplicate colour", () => {
  const seen = new Map();
  for (const r of table()) {
    const k = r.rgb.join(",");
    const had = seen.get(k);
    assert.ok(
      !had || (had.roughness === r.roughness && had.metalness === r.metalness),
      `colour ${k} is given two finishes — ${JSON.stringify(had)} and ${JSON.stringify(r)}`,
    );
    seen.set(k, r);
  }
});

test("the viewer's default is a finish no material claims", () => {
  // A colour the table does not name has to read AS unnamed. If the default were also some
  // material's figure, a gap in the table would be invisible in the picture.
  const js = read("web/public/js/viewer/step.js");
  const m = /DEFAULT_FINISH = \{ roughness: ([0-9.]+), metalness: ([0-9.]+) \}/.exec(js);
  assert.ok(m, "step.js states no DEFAULT_FINISH");
  const [, rough, metal] = m;
  const clash = table().find(
    (r) => r.roughness === Number(rough) && r.metalness === Number(metal),
  );
  assert.ok(!clash, `DEFAULT_FINISH is also ${JSON.stringify(clash)}'s surface`);
});
