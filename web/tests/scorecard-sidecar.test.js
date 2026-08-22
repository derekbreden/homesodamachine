// Conformance test for the scorecard sidecar contract (web/contracts/scorecard-sidecar.js).
//
// The verdict crosses from the CadQuery build (hardware/manifold-layout/_scorecard.py, Python)
// to the browser viewer (public/js/viewer/scorecard-3d.js, untyped JS). This pins the consumer
// end: load the committed enclosure-assembly.scorecard.json and assert it still matches the shape
// the viewer reads (via the contract's own isScorecard guard), so a producer change that drops
// or renames a field fails here instead of silently drawing no badge. Skips when unbuilt.

import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { isScorecard, scorecardPathFor, SCORECARD_SUFFIX, sizeText,
  MM_PER_INCH } from "../contracts/scorecard-sidecar.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
// The live pack's sidecar, written by hardware/manifold-layout/enclosure_assembly.py. The tests
// skip themselves until that build has written one.
const sidecarIn = (...root) => path.join(REPO_ROOT, ...root, "manifold-layout",
  "enclosure-assembly.scorecard.json");
const SIDECAR = sidecarIn("hardware");
// The cold core's own sidecar, written by hardware/cold-core-layout/cold_core_assembly.py.
const COLD_SIDECAR = path.join(REPO_ROOT, "hardware", "cold-core-layout",
  "cold-core-assembly.scorecard.json");

test("the artifact lock pins every committed viewer scorecard", (t) => {
  const lock = JSON.parse(fs.readFileSync(
    path.join(REPO_ROOT, "hardware", "cad-artifacts.lock.json"), "utf8"));
  if (!lock.sidecars) return t.skip("this source commit predates scorecard pinning");
  const entries = Object.entries(lock.sidecars);
  assert.ok(entries.length, "the lock names at least one viewer scorecard");
  for (const [rel, expected] of entries) {
    assert.ok(rel.startsWith("hardware/") && rel.endsWith(".scorecard.json"),
      `${rel} is a confined scorecard path`);
    const full = path.resolve(REPO_ROOT, rel);
    assert.ok(full.startsWith(path.join(REPO_ROOT, "hardware") + path.sep),
      `${rel} stays under hardware/`);
    assert.ok(fs.existsSync(full), `${rel} is committed beside its lock`);
    const actual = createHash("sha256").update(fs.readFileSync(full)).digest("hex");
    assert.equal(actual, expected, `${rel} matches the lock`);
  }
});

test("enclosure scorecard sidecar conforms to the contract", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));

  // The contract's own guard — the exact predicate the viewer uses to decide to draw a badge.
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

  // The three scored goal axes exist by id, each deferred — `active` false is what the viewer
  // draws gray.
  const goalById = Object.fromEntries(goals.map((c) => [c.id, c]));
  for (const id of ["placed", "located", "routed"]) {
    assert.ok(goalById[id], `goal axis ${id} present`);
    assert.equal(goalById[id].active, false, `${id} is deferred`);
  }
  // The fastening and the corner grade are requirements the machine is held to.
  const gateById = Object.fromEntries(gates.map((c) => [c.id, c]));
  for (const id of ["mounted", "bend-radius"]) assert.ok(gateById[id], `gate ${id} present`);
  assert.equal(sc.gatesPass, gates.every((c) => c.status === "pass"));
});

// ── Size ────────────────────────────────────────────────────────────────────────────────────
// Both rows are measured off the placed solids, and they hold each other: the assembly population
// is every body AND the printed box, so its box contains the box drawn around the shells alone.
test("the size table measures the printed box and the assembly around it", (t) => {
  if (!fs.existsSync(SIDECAR)) return t.skip("no built scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(SIDECAR, "utf8"));
  assert.ok(isScorecard(sc), "sidecar passes isScorecard");

  assert.ok(Array.isArray(sc.size), "sidecar carries a size table");
  const byId = Object.fromEntries(sc.size.map((s) => [s.id, s]));
  for (const id of ["enclosure", "assembly"]) assert.ok(byId[id], `size row ${id} present`);

  for (const s of sc.size) {
    for (let i = 0; i < 3; i++) {
      assert.ok(s.max[i] > s.min[i], `${s.id} axis ${i} has extent`);
      assert.ok(Math.abs(s.mm[i] - (s.max[i] - s.min[i])) < 1e-6,
        `${s.id} axis ${i}: mm is max − min`);
    }
  }

  const { enclosure, assembly } = byId;
  for (let i = 0; i < 3; i++) {
    assert.ok(assembly.min[i] <= enclosure.min[i] + 1e-6, `assembly box holds the box, axis ${i} low`);
    assert.ok(assembly.max[i] >= enclosure.max[i] - 1e-6, `assembly box holds the box, axis ${i} high`);
  }
});

test("sizeText renders one measurement in both units", () => {
  assert.equal(sizeText({ mm: [223, 474, 358] }),
    "223.0 × 474.0 × 358.0 mm · 8.78 × 18.66 × 14.09 in");
  assert.equal(MM_PER_INCH, 25.4);
});

test("scorecardPathFor maps a STEP path to its sidecar", () => {
  assert.equal(
    scorecardPathFor("manifold-layout/enclosure-assembly.step"),
    "manifold-layout/enclosure-assembly" + SCORECARD_SUFFIX);
});

// ── Bends ───────────────────────────────────────────────────────────────────────────────────
// The cold core's card carries a bend row per drawn line — `_scenes.core_names` reads an `id`
// off each one for the core's line names, so a row without one drops a body out of every scene.
test("every cold-core bend row is named and grades its own corners", (t) => {
  if (!fs.existsSync(COLD_SIDECAR)) return t.skip("no built cold-core scorecard sidecar");
  const sc = JSON.parse(fs.readFileSync(COLD_SIDECAR, "utf8"));
  assert.ok(isScorecard(sc), "cold-core sidecar passes isScorecard");

  assert.ok(Array.isArray(sc.bends) && sc.bends.length, "sidecar carries a bend table");
  const named = new Set();
  for (const b of sc.bends) {
    assert.ok(typeof b.id === "string" && b.id.length, "a bend row names itself");
    assert.ok(!named.has(b.id), `${b.id} is named once — a scene's line names are a set`);
    named.add(b.id);
    for (const a of [b.frm, b.to]) {
      assert.equal(typeof a, "string");
      assert.ok(a.includes("."), `${b.id} anchor "${a}" is component.port`);
    }
    assert.ok(Array.isArray(b.corners), `${b.id} carries its corners`);
    assert.ok(b.corners.every((c) => c.radius >= b.radius - 1e-9),
      `${b.id}: the line's radius is its tightest corner's`);
  }
});

// Prove the guard fires — a check that never rejects is worthless.
test("isScorecard rejects malformed input", () => {
  assert.equal(isScorecard(null), false);
  assert.equal(isScorecard({}), false);
  assert.equal(isScorecard({ gatesPass: "yes", checks: [] }), false);
  assert.equal(isScorecard({ gatesPass: true, checks: [{ kind: "gate" }] }), false);
  const base = { gatesPass: true, checks: [] };
  assert.equal(isScorecard(base), true);
  // A size row missing an axis is rejected; a whole one passes.
  const size = { id: "enclosure", label: "the printed box", min: [0, 0, 0], max: [1, 2, 3], mm: [1, 2, 3] };
  assert.equal(isScorecard({ ...base, size: [{ ...size, mm: [1, 2] }] }), false);
  assert.equal(isScorecard({ ...base, size: [size] }), true);
});
