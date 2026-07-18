// Conformance test for the scorecard sidecar contract (web/contracts/scorecard-sidecar.js).
//
// The verdict crosses from the CadQuery build (hardware/.../scorecard.py, Python) to the
// browser viewer (public/js/viewer/scorecard-3d.js, untyped JS). This pins the consumer end:
// load the committed enclosure-assembly.scorecard.json and assert it still matches the shape
// the viewer reads (via the contract's own isScorecard guard), so a producer change that drops
// or renames a field fails here instead of silently drawing no bar. Skips when unbuilt.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { isScorecard, scorecardPathFor, SCORECARD_SUFFIX } from "../contracts/scorecard-sidecar.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const SIDECAR = path.join(REPO_ROOT, "hardware", "printed-parts", "enclosure",
  "enclosure-assembly", "enclosure-assembly.scorecard.json");

test("enclosure scorecard sidecar conforms to the contract", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));

  // The contract's own guard — the exact predicate the viewer uses to decide to draw a bar.
  assert.ok(isScorecard(sc), "sidecar passes isScorecard");

  // Gates + goals both present; every check carries the fields the modal reads.
  const gates = sc.checks.filter((c) => c.kind === "gate");
  const goals = sc.checks.filter((c) => c.kind === "goal");
  assert.ok(gates.length >= 1, "has at least one gate");
  assert.ok(goals.length >= 1, "has at least one goal");
  for (const c of sc.checks) {
    for (const k of ["id", "label", "kind", "status", "value", "target", "detail", "active"]) {
      assert.ok(k in c, `check carries ${k}`);
    }
    assert.ok(c.detail.every((d) => typeof d === "string"), "detail rows are strings");
  }

  // The five goal axes exist by id, and the focus/deferred split is encoded in `active`.
  const goalById = Object.fromEntries(goals.map((c) => [c.id, c]));
  for (const id of ["placed", "located", "shaped", "routed", "held"]) {
    assert.ok(goalById[id], `goal axis ${id} present`);
  }
  assert.equal(goalById.placed.active, true, "placed is a focus axis");
  assert.equal(goalById.located.active, true, "located is a focus axis");
  assert.equal(goalById.shaped.active, true, "shaped is a focus axis");
  assert.equal(goalById.routed.active, false, "routed is deferred");
  assert.equal(goalById.held.active, false, "held is deferred");
});

test("the port inventory carries a coordinate and a bore for every located connector", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));

  assert.ok(Array.isArray(sc.ports), "sidecar carries a ports array");
  assert.ok(sc.ports.length >= 1, "at least one port declared");
  for (const p of sc.ports) {
    for (const k of ["component", "name", "kind", "pos", "face", "diam", "mates", "status", "note"]) {
      assert.ok(k in p, `port ${p.name} carries ${k}`);
    }
    // A port that the audit calls 'ok' (its component counts toward `located`) must have BOTH a
    // 3-coordinate position AND a numeric bore — the PCBA per-pad specificity this axis enforces.
    if (p.status === "ok") {
      assert.ok(Array.isArray(p.pos) && p.pos.length === 3, `located port ${p.name} has an (x,y,z)`);
      assert.equal(typeof p.diam, "number", `located port ${p.name} has a bore Ø`);
    }
  }
});

test("scorecardPathFor maps a STEP path to its sidecar", () => {
  assert.equal(
    scorecardPathFor("printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step"),
    "printed-parts/enclosure/enclosure-assembly/enclosure-assembly" + SCORECARD_SUFFIX);
});

// Prove the guard fires — a check that never rejects is worthless.
test("isScorecard rejects malformed input", () => {
  assert.equal(isScorecard(null), false);
  assert.equal(isScorecard({}), false);
  assert.equal(isScorecard({ gatesPass: "yes", placed: 0, located: 0, shaped: 0, routed: 0, held: 0, checks: [] }), false);
  assert.equal(isScorecard({ gatesPass: true, placed: 0, located: 0, shaped: 0, routed: 0, held: 0, checks: [{ kind: "gate" }] }), false);
  // A malformed ports entry (pos not a triple, diam not numeric) is rejected — the guard fires.
  const base = { gatesPass: true, placed: 0, located: 0, shaped: 0, routed: 0, held: 0, checks: [] };
  assert.equal(isScorecard({ ...base, ports: [{ component: "x", name: "p", pos: [1, 2], diam: 6, mates: "y", status: "ok" }] }), false);
  assert.equal(isScorecard({ ...base, ports: [{ component: "x", name: "p", pos: null, diam: "big", mates: "y", status: "no-pos" }] }), false);
  // A well-formed ports entry (and an absent ports field) both pass.
  assert.equal(isScorecard({ ...base, ports: [{ component: "x", name: "p", pos: [1, 2, 3], diam: 6.35, mates: "y", status: "ok" }] }), true);
  assert.equal(isScorecard(base), true);
});
