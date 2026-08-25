// The Related rail's rule, held against the tree it reads
// (contracts/related-steps.js).
//
// The rule is a naming convention, so the way it goes wrong is silent: a mold
// whose directory does not name the part it casts is a mold the viewer never
// offers, and the rail shows an empty space that looks exactly like a part with
// no tooling. The last test here is the alarm — every `-mold` directory in the
// tree has to resolve back to a part.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { relatedSteps, KIND_CAPTIONS } from "../contracts/related-steps.js";
import { walkFiles } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HW = path.join(path.resolve(__dirname, "..", ".."), "hardware");

// The same list the viewer works from — `/api/steps` is this call.
const ALL = walkFiles(HW, ".step").sort();

const FUNNEL = "printed-parts/zone-c/funnel/funnel.step";
const MOLD_DIR = "printed-parts/zone-c/funnel-mold";

test("the funnel offers all three mold models", () => {
  const rel = relatedSteps(FUNNEL, ALL);
  const molds = rel.filter((r) => r.file.startsWith(MOLD_DIR + "/"));
  assert.equal(molds.length, 3, JSON.stringify(rel, null, 2));
  for (const m of molds) assert.equal(m.kind, "from");
});

test("each mold half offers the funnel back", () => {
  for (const half of ALL.filter((f) => f.startsWith(MOLD_DIR + "/"))) {
    const rel = relatedSteps(half, ALL);
    const back = rel.find((r) => r.file === FUNNEL);
    assert.ok(back, `${half} does not reach the funnel`);
    assert.equal(back.kind, "of");
  }
});

test("a directory's own models are offered beside each other", () => {
  const bridge = "printed-parts/cold-core/reed-bridge/reed-bridge.step";
  const rel = relatedSteps(bridge, ALL);
  assert.deepEqual(
    rel.map((r) => [r.file, r.kind]),
    [["printed-parts/cold-core/reed-bridge/reed-bridge-setting-gauge.step", "beside"]],
  );
});

test("a name that merely shares a prefix is not related", () => {
  // Both live under cold-core and both begin "foam"; neither extends the other
  // at a separator.
  const cap = "printed-parts/cold-core/foam-cap/foam-cap-top.step";
  const rel = relatedSteps(cap, ALL).map((r) => r.file);
  assert.ok(!rel.some((f) => f.includes("/foam-assembly/")), rel.join("\n"));
});

test("generated trees offer nothing and are offered nothing", () => {
  const scene = ALL.find((f) => f.split("/").includes("out"));
  assert.ok(scene, "no generated model in the tree to check");
  assert.deepEqual(relatedSteps(scene, ALL), []);
  for (const f of ALL) {
    for (const r of relatedSteps(f, ALL)) {
      assert.ok(!r.file.split("/").includes("out"), `${f} -> ${r.file}`);
    }
  }
});

test("the walk above a model is not offered a second time", () => {
  const withTrail = relatedSteps(FUNNEL, ALL, [`${MOLD_DIR}/funnel-mold-core.step`]);
  assert.ok(!withTrail.some((r) => r.file.endsWith("funnel-mold-core.step")));
});

test("every kind the rule returns has a caption", () => {
  const kinds = new Set();
  for (const f of ALL) for (const r of relatedSteps(f, ALL)) kinds.add(r.kind);
  for (const k of kinds) assert.ok(KIND_CAPTIONS[k], `no caption for ${k}`);
});

// The alarm. A mold reaches its part by being named for it; one parked
// anywhere else is unreachable and looks like nothing.
test("every mold directory resolves to the part it casts", () => {
  const dirs = new Set(ALL.map((f) => f.slice(0, f.lastIndexOf("/"))));
  const molds = [...dirs].filter((d) => /(^|\/)[^/]*[-_]mold[^/]*$/.test(d));
  assert.ok(molds.length, "no mold directory in the tree");
  for (const dir of molds) {
    const any = ALL.find((f) => f.startsWith(dir + "/"));
    const rel = relatedSteps(any, ALL);
    assert.ok(
      rel.some((r) => r.kind === "of"),
      `${dir}/ names no part — the viewer cannot offer it from one`,
    );
  }
});

test("no related file is a path the tree does not hold", () => {
  for (const f of ALL) {
    for (const r of relatedSteps(f, ALL)) {
      assert.ok(fs.existsSync(path.join(HW, r.file)), `${f} -> ${r.file}`);
    }
  }
});
