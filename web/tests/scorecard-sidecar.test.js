// Conformance test for the scorecard sidecar contract (web/contracts/scorecard-sidecar.js).
//
// The verdict crosses from the CadQuery build (hardware/manifold-layout/_scorecard.py, Python)
// to the browser viewer (public/js/viewer/scorecard-3d.js, untyped JS). This pins the consumer
// end: load the committed enclosure-assembly.scorecard.json and assert it still matches the shape
// the viewer reads (via the contract's own isScorecard guard), so a producer change that drops
// or renames a field fails here instead of silently drawing no bar. Skips when unbuilt.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { isScorecard, scorecardPathFor, SCORECARD_SUFFIX, FOCUS_IDS, focusAxes, failingBends,
  bendPinned, unmountedComponents } from "../contracts/scorecard-sidecar.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
// The live pack's sidecar, written by hardware/manifold-layout/enclosure_assembly.py. The tests
// skip themselves until that build has written one.
const sidecarIn = (...root) => path.join(REPO_ROOT, ...root, "manifold-layout",
  "enclosure-assembly.scorecard.json");
const SIDECAR = sidecarIn("hardware");

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

  // The six goal axes exist by id, and the live/deferred split is encoded in `active`.
  const goalById = Object.fromEntries(goals.map((c) => [c.id, c]));
  for (const id of ["placed", "located", "shaped", "routed", "held", "mounted"]) {
    assert.ok(goalById[id], `goal axis ${id} present`);
  }
  assert.equal(goalById.mounted.active, true, "mounted is the live axis");
  for (const id of ["placed", "located", "shaped", "routed", "held"]) {
    assert.equal(goalById[id].active, false, `${id} is deferred`);
  }
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
    scorecardPathFor("manifold-layout/enclosure-assembly.step"),
    "manifold-layout/enclosure-assembly" + SCORECARD_SUFFIX);
});

// ── Focus ───────────────────────────────────────────────────────────────────────────────────
// The bar says the two focus axes and the modal leads with them, both counted off `bends` and
// `mounts`. A producer that emits an axis without its table draws a bar reading 0/0.
test("the sidecar carries both focus axes and the tables their counts read", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));
  assert.ok(isScorecard(sc), "sidecar passes isScorecard");

  const byId = Object.fromEntries(sc.checks.map((c) => [c.id, c]));
  for (const id of FOCUS_IDS) assert.ok(byId[id], `focus axis ${id} present as a check`);
  assert.equal(byId.mounted.active, true, "mounted is a live goal axis");

  const axes = focusAxes(sc);
  assert.equal(axes.length, 2, "both focus axes count");
  const [bend, mount] = axes;
  assert.equal(bend.id, "bend-radius");
  assert.ok(bend.total > 0, "corners counted off the bends table");
  assert.ok(bend.done <= bend.total, "corners at spec cannot exceed corners");
  assert.equal(mount.id, "mounted");
  assert.equal(mount.total, sc.mounts.length, "mounted counts every component");
  assert.equal(mount.done, sc.mounts.filter((m) => m.by).length);
  // The counts the bar prints must be the ones the gate/goal reached its verdict on.
  assert.equal(bend.status === "pass", bend.done === bend.total);
  assert.equal(mount.status === "pass", mount.done === mount.total);

  // A carrier is a placed component or a printed piece of the enclosure, and it is named — a
  // joint printed into nothing has nowhere for its screw to go.
  for (const m of sc.mounts) {
    assert.equal(typeof m.held, "string", `${m.component} declares what holds it`);
    if (m.by !== null) assert.ok(m.by.length, `${m.component} names the part it mounts into`);
  }
});

test("the focus panels itemize down to the body a fix moves", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));

  // Unmounted rows are exactly the gap the axis reports, one row each.
  const loose = unmountedComponents(sc);
  assert.equal(loose.length, sc.mounts.length - sc.mounts.filter((m) => m.by).length);
  assert.ok(loose.every((m) => !m.by), "every listed row is an open joint");

  // Failing runs carry the two anchors the panel turns into clickable part names, and a pinned
  // run — one whose legs cannot seat a legal radius either — sorts ahead of one that is only a
  // number to raise.
  const short = failingBends(sc);
  for (const b of short) {
    for (const a of [b.frm, b.to]) {
      assert.equal(typeof a, "string");
      assert.ok(a.includes("."), `${b.id} anchor "${a}" is component.port`);
    }
  }
  const firstLoose = short.findIndex((b) => !bendPinned(b));
  if (firstLoose !== -1) {
    assert.ok(short.slice(firstLoose).every((b) => !bendPinned(b)), "pinned runs sort first");
  }
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
