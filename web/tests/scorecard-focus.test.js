// The focus axes are one constant, written twice — hardware/manifold-layout/_scorecard.py's
// FOCUS_IDS and web/contracts/scorecard-sidecar.js's. The producer's copy caps the terminal
// report's detail and marks which goal is live in the sidecar; the contract's copy is what the
// 3D viewer's bar and modal lead with. Nothing links them at runtime, so they drift silently,
// and the drift is invisible in both places: each surface reads correct on its own and points
// its reader at different work.
//
// This is that link. It parses the tuple out of the Python source rather than importing it,
// because the build needs CadQuery and this suite must run without it.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FOCUS_IDS, focusAxes } from "../contracts/scorecard-sidecar.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const PRODUCER = path.join(REPO_ROOT, "hardware", "manifold-layout", "_scorecard.py");
const SIDECAR = path.join(REPO_ROOT, "hardware", "manifold-layout", "front-half.scorecard.json");

// FOCUS_IDS = ("bend-radius", "mounted") — the assignment at module scope, not a mention of the
// name in prose or in the code that reads it. Returns null when there is no such assignment,
// which the tests treat as a failure: a parse that quietly finds nothing would pass every
// comparison below against an empty list.
function producerFocusIds(src) {
  const m = src.match(/^FOCUS_IDS\s*=\s*\(([^)]*)\)/m);
  if (!m) return null;
  const ids = [...m[1].matchAll(/["']([^"']+)["']/g)].map((g) => g[1]);
  return ids.length ? ids : null;
}

// The module docstring — everything up to the closing triple quote. Where the producer states in
// prose which axes it leads with.
function moduleDocstring(src) {
  const m = src.match(/^"""([\s\S]*?)"""/);
  return m ? m[1] : null;
}

test("the producer and the contract name the same focus axes, in the same order", () => {
  const src = fs.readFileSync(PRODUCER, "utf8");
  const theirs = producerFocusIds(src);
  assert.ok(theirs, "_scorecard.py assigns FOCUS_IDS as a tuple of string literals");
  assert.deepEqual(theirs, FOCUS_IDS,
    `_scorecard.py leads with [${theirs}] and the contract with [${FOCUS_IDS}] — `
    + "one card, two surfaces, and they must point a reader at the same work");
});

test("the parse fires — it does not pass by finding nothing", () => {
  assert.equal(producerFocusIds("FOCUS_IDS = ()"), null, "an empty tuple is not a focus");
  assert.equal(producerFocusIds("# FOCUS_IDS is read below\nlimit = FOCUS_IDS"), null,
    "a mention is not an assignment");
  assert.deepEqual(producerFocusIds('FOCUS_IDS = ("a", "b")\n'), ["a", "b"]);
  assert.deepEqual(producerFocusIds("x = 1\nFOCUS_IDS = ('a',)\ny = 2\n"), ["a"]);
});

test("the producer's own prose names the axes its constant names", () => {
  const doc = moduleDocstring(fs.readFileSync(PRODUCER, "utf8"));
  assert.ok(doc, "_scorecard.py opens with a module docstring");
  for (const id of FOCUS_IDS) {
    assert.ok(doc.includes(`\`${id}\``),
      `the docstring names \`${id}\` — a header that leads with an axis the constant dropped `
      + "is the same drift one level up");
  }
});

// The sidecar is where the two copies meet: the producer marks exactly one goal `active`, and
// the viewer draws that one live and the rest gray. That goal must be the one FOCUS_IDS names.
test("the built sidecar's live goal is the goal the focus names", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));
  const live = sc.checks.filter((c) => c.kind === "goal" && c.active).map((c) => c.id);
  const goalIds = sc.checks.filter((c) => c.kind === "goal").map((c) => c.id);
  const focusGoals = FOCUS_IDS.filter((id) => goalIds.includes(id));
  assert.deepEqual(live, focusGoals, "the active goals are exactly the focus's goals");

  // And every focus axis is on the card at all — an axis the bar heads with and the card does
  // not carry draws a heading with nothing under it.
  const byId = Object.fromEntries(sc.checks.map((c) => [c.id, c]));
  for (const id of FOCUS_IDS) assert.ok(byId[id], `focus axis ${id} is a check on the card`);
  assert.deepEqual(focusAxes(sc).map((a) => a.id), FOCUS_IDS,
    "the bar counts the focus axes in the order the constant states them");
});
