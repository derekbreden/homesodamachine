// What the missing-parts mark reads (web/contracts/missing-parts.js): which runs a machine's
// published facts say it does not complete, and which bodies in the scene stand for a run's
// ends. The machine's own facts are read when the build has written them.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FACTS_SUFFIX, factsPathFor, missingRuns, lacks, said, bodyOf, sceneBodies } from "../contracts/missing-parts.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const FACTS = path.join(REPO_ROOT, "hardware", "manifold-layout", "enclosure-assembly.facts.json");

const run = (id, status, absent = {}) => ({
  id, frm: "foam-assembly.reservoir-b", to: "valve-v-h.inlet", status, length: 1,
  missing_native_routes: absent.tubes ?? [], missing_fittings: absent.fittings ?? [],
});

test("a run the machine does not complete is missing, and a complete one is not", () => {
  const facts = { runs: [
    run("fluid-24", "complete"), run("fluid-26", "incomplete", { tubes: ["fluid-26"] }), run("water-5", "complete"),
  ] };
  assert.deepEqual(missingRuns(facts), [
    { id: "fluid-26", from: "foam-assembly.reservoir-b", to: "valve-v-h.inlet", tubes: ["fluid-26"], fittings: [], wiring: false, why: "" },
  ]);
  const [told] = missingRuns({ runs: [{ ...run("fluid-26", "incomplete", { tubes: ["fluid-26"] }), why: "missing station valve-v-h.inlet" }] });
  assert.equal(told.why, "missing station valve-v-h.inlet");
  assert.deepEqual(missingRuns({ runs: [run("fluid-26", "complete")] }), []);
});

test("a run with no verdict counts as missing, and facts with no runs list none", () => {
  assert.deepEqual(missingRuns({ runs: [{ id: "fluid-26", frm: "a.b", to: "c.d" }] }),
    [{ id: "fluid-26", from: "a.b", to: "c.d", tubes: [], fittings: [], wiring: false, why: "" }]);
  assert.deepEqual(missingRuns({}), []);
  assert.deepEqual(missingRuns(null), []);
  assert.deepEqual(missingRuns({ runs: "none" }), []);
});

test("a missing run is said to be without exactly the tubes and fittings its facts name", () => {
  const [tube] = missingRuns({ runs: [run("fluid-26", "incomplete", { tubes: ["fluid-26"] })] });
  assert.equal(lacks(tube), "tube fluid-26 is not routed");
  const [fitting] = missingRuns({ runs: [run("fluid-2", "incomplete", { fittings: ["Y-A-1"] })] });
  assert.equal(lacks(fitting), "fitting Y-A-1 is not in the machine");
  const [both] = missingRuns({ runs: [run("fluid-2", "incomplete", { tubes: ["fluid-2", "fluid-3"], fittings: ["Y-A-1"] })] });
  assert.equal(lacks(both), "tube fluid-2 is not routed, tube fluid-3 is not routed, fitting Y-A-1 is not in the machine");
  const [neither] = missingRuns({ runs: [{ id: "fluid-26", frm: "a.b", to: "c.d" }] });
  assert.equal(lacks(neither), "not complete");
  assert.equal(lacks({ id: "fluid-26", from: "a.b", to: "c.d" }), "not complete");
});

test("a wire the facts list as not routed is missing, and so is wiring left out whole", () => {
  const facts = {
    runs: [run("fluid-24", "complete")],
    wiring_not_routed: [
      { id: "wire-J2-FAN", frm: "J2.FAN", to: "fan.negative", why: "its course ended in an error" },
      { id: "wiring", frm: "", to: "", why: "a terminal did not resolve" },
    ],
  };
  const [wire, whole] = missingRuns(facts);
  assert.deepEqual(wire, { id: "wire-J2-FAN", from: "J2.FAN", to: "fan.negative", tubes: [], fittings: [],
    wiring: true, why: "its course ended in an error" });
  assert.equal(said(wire), "wire-J2-FAN — J2.FAN to fan.negative: wire is not routed");
  assert.equal(said(whole), "wiring: not in the machine");
  const [tube] = missingRuns({ runs: [run("fluid-26", "incomplete", { tubes: ["fluid-26"] })] });
  assert.equal(said(tube), "fluid-26 — foam-assembly.reservoir-b to valve-v-h.inlet: tube fluid-26 is not routed");
  // No part of the list says a thing cannot be routed: only that it is not.
  for (const entry of [wire, whole, tube]) assert.doesNotMatch(said(entry), /can't|cannot|could not/i);
});

test("a model's facts sit beside its STEP", () => {
  assert.equal(factsPathFor("manifold-layout/enclosure-assembly.step"),
    "manifold-layout/enclosure-assembly" + FACTS_SUFFIX);
});

test("a run's ends resolve to the bodies the scene draws", () => {
  const names = ["valve-v-h", "cold-core/valve-v-b", "cold-core/foam-shell", "cold-core/foam-cap-bottom", "psu"];
  assert.equal(bodyOf("valve-v-h.inlet"), "valve-v-h");
  assert.deepEqual(sceneBodies("valve-v-h", names), ["valve-v-h"]);
  assert.deepEqual(sceneBodies("valve-v-b", names), ["cold-core/valve-v-b"]);
  assert.deepEqual(sceneBodies("foam-assembly", names), ["cold-core/foam-shell", "cold-core/foam-cap-bottom"]);
  assert.deepEqual(sceneBodies("Y-A-1", names), []);
  assert.deepEqual(sceneBodies("J2", [...names, "terminal-J2"]), ["terminal-J2"]);
});

test("the machine's own facts give every run a verdict the mark reads", (t) => {
  if (!fs.existsSync(FACTS)) return t.skip("no built machine facts");
  const facts = JSON.parse(fs.readFileSync(FACTS, "utf8"));
  assert.ok(Array.isArray(facts.runs) && facts.runs.length, "the facts list the machine's runs");
  for (const r of facts.runs) {
    assert.equal(typeof r.id, "string");
    assert.ok(r.status === "complete" || r.status === "incomplete", `${r.id} states complete or incomplete`);
    assert.equal(typeof r.frm, "string", `${r.id} names the port it leaves`);
    assert.equal(typeof r.to, "string", `${r.id} names the port it reaches`);
  }
  const missing = missingRuns(facts);
  assert.equal(missing.length, facts.runs.filter((r) => r.status === "incomplete").length);
});
