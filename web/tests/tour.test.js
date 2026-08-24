// THE TOUR NAMES SOLIDS, AND THIS TREE RENAMES SOLIDS.
//
// contracts/tour-water.js points at bodies by the name the STEP carries. A
// rename pass that moves `port-ring-water` to `bulkhead-ring-water` leaves the
// tour pointing at nothing — and pointing at nothing is not an error at
// runtime: the framing falls back to the whole model and the beat lights up
// empty, which reads as a bad camera angle rather than as a stale name. So the
// names are held against the models here, where a rename fails out loud.
//
// The body names are read straight out of the STEP's PRODUCT entries — the
// same labels occt hands the viewer and `step.js` stamps onto each mesh, with
// the `/n` suffix a multi-solid body carries stripped the same way `bodyName`
// strips it.
//
// SKIPPED WHERE THE SOLIDS ARE NOT ON DISK. They are fetched, not committed
// (hardware/cad-artifacts.lock.json), so a clone that has not run
// scripts/fetch-cad-artifacts.mjs has nothing to hold the names against.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { TOUR } from "../contracts/tour-water.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE = path.resolve(__dirname, "..", "..", "hardware");

/** Every body name in a STEP, by its assembly-node label. */
function bodyNames(rel) {
  const abs = path.join(HARDWARE, rel);
  if (!fs.existsSync(abs)) return null;
  const text = fs.readFileSync(abs, "latin1");
  const out = new Set();
  for (const m of text.matchAll(/PRODUCT\('([^']*)'/g)) {
    out.add(m[1].replace(/\/\d+$/, ""));
  }
  return out;
}

/** The model each beat is shown on: the last one named at or before it. */
function modelOf(index) {
  for (let i = index; i >= 0; i--) if (TOUR.steps[i].model) return TOUR.steps[i].model;
  return TOUR.model;
}

const models = new Map();
for (let i = 0; i < TOUR.steps.length; i++) {
  const rel = modelOf(i);
  if (!models.has(rel)) models.set(rel, bodyNames(rel));
}

const haveEvery = [...models.values()].every(Boolean);

test("every body the tour names is in the model it names it on", { skip: !haveEvery
  && "the generated solids are not on this disk" }, () => {
  const missing = [];
  for (const [i, step] of TOUR.steps.entries()) {
    const rel = modelOf(i);
    const have = models.get(rel);
    const named = [...(step.parts || []),
                   ...(step.focus || []).filter((f) => f !== "*")];
    for (const name of named) {
      if (!have.has(name)) missing.push(`step ${i + 1} (${step.title}): ${name} — ${rel}`);
    }
  }
  assert.deepEqual(missing, []);
});

test("the faintly-lit map is all in the base model", { skip: !haveEvery
  && "the generated solids are not on this disk" }, () => {
  const have = models.get(TOUR.model);
  const missing = [];
  for (const p of TOUR.paths) {
    for (const n of p.parts) if (!have.has(n)) missing.push(`${p.hue}: ${n}`);
  }
  assert.deepEqual(missing, []);
});

// The map is the whole run. A body a beat lights that no map entry carries is a
// leg drawn bright and then never again — the reader loses it the moment the
// tour moves on, which is the one thing the faint tier exists to prevent.
test("every leg a beat lights is on the map", { skip: !haveEvery
  && "the generated solids are not on this disk" }, () => {
  const mapped = new Set(TOUR.paths.flatMap((p) => p.parts));
  const loose = new Set();
  for (const s of TOUR.steps) {
    if (s.overview) continue; // an overview names the whole run, map entries included
    for (const n of s.parts || []) if (!mapped.has(n)) loose.add(n);
  }
  // Bodies that are scenery for a beat rather than legs of the run — the
  // preventer's pan and sensor, the parts inside the vessel, the words on the
  // rings — are named here so the gate reads as a list and not as a mystery.
  const SCENERY = new Set([
    "asse-drip-pan", "moisture-plate", "tube-fluid-1", "flow-regulator",
    "bulkhead-ring-water-word", "tube-collar-water-word", "bulkhead-ring-carb-word",
  ]);
  const unexplained = [...loose].filter((n) => !SCENERY.has(n) && !n.startsWith("cold-core/"));
  assert.deepEqual(unexplained, []);
});

// A beat that does not hold has to say where the camera stands, because there
// is no shot to inherit. A beat that holds must not — `dir` there is silently
// unread, which is the kind of thing a reader spends an hour disbelieving.
test("a beat states a direction exactly when it flies to one", () => {
  const wrong = [];
  for (const [i, s] of TOUR.steps.entries()) {
    if (s.hold && s.dir) wrong.push(`step ${i + 1} (${s.title}): holds and states dir`);
    if (!s.hold && !s.dir) wrong.push(`step ${i + 1} (${s.title}): flies and states no dir`);
  }
  assert.deepEqual(wrong, []);
});

// The first beat can never hold: there is no shot before it to keep.
test("the tour does not open on a held beat", () => {
  assert.equal(!!TOUR.steps[0].hold, false);
});

// A held beat is the shot before it, so it cannot be the beat that swaps the
// model — there would be nothing of its subject on screen to have framed.
test("a beat that changes the model flies to it", () => {
  const wrong = TOUR.steps
    .map((s, i) => (s.model && s.hold ? `step ${i + 1} (${s.title})` : null))
    .filter(Boolean);
  assert.deepEqual(wrong, []);
});
