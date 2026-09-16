import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { TOUR } from "../contracts/tour-water.js";
import { timelineFor } from "../contracts/tour-timeline.js";

const HARDWARE = fileURLToPath(new URL("../../hardware/", import.meta.url));
const modelPath = path.join(HARDWARE, TOUR.model);

// Generated solids are fetched separately from a fresh checkout.
test("every highlighted and framed body exists in the assembly", {
  skip: !fs.existsSync(modelPath) && "the generated solid is not on this disk",
}, () => {
  const products = fs.readFileSync(modelPath, "latin1").matchAll(/PRODUCT\('([^']*)'/g);
  const names = new Set([...products].map((m) => m[1].replace(/\/\d+$/, "")));
  const missing = TOUR.steps.flatMap((step, i) =>
    [...step.parts, ...(step.focus || [])]
      .filter((name) => name !== "*" && !names.has(name))
      .map((name) => `beat ${i + 1}: ${name}`),
  );
  assert.deepEqual(missing, []);
});

test("the short narrative carries captions, labels and complete camera poses", () => {
  const duration = timelineFor(TOUR.steps).duration;
  assert.ok(duration >= 90_000 && duration <= 120_000, `${duration} ms`);
  for (const step of TOUR.steps) {
    assert.ok(Number.isSafeInteger(step.dwell) && step.dwell > 0, step.title);
    for (const key of ["title", "body", "label"]) assert.ok(step[key]?.trim(), `${step.title}: ${key}`);
    assert.ok(step.dwell >= step.body.split(/\s+/).length * 240, `caption too fast: ${step.title}`);
    assert.equal(step.dir.length, 3, step.title);
    assert.ok(step.dir.every(Number.isFinite) && step.dir.some((n) => n !== 0), step.title);
    assert.ok(Number.isFinite(step.pad) && step.pad > 0, step.title);
    assert.ok((step.focus || step.parts).length > 0, step.title);
    assert.equal(step.model, undefined, "the entire tour stays in one assembly");
    for (const layer of ["enclosure", "coldCore", "carbonator"]) {
      assert.ok(Number.isFinite(step.reveal[layer]) && step.reveal[layer] >= 0
        && step.reveal[layer] <= 1, `${step.title}: ${layer}`);
    }
  }
});

test("screws and enclosure move before the narrative reaches internal parts", () => {
  const steps = TOUR.steps;
  const closed = { enclosure: 0, coldCore: 0, carbonator: 0 };
  assert.deepEqual(steps[0].reveal, closed);
  assert.deepEqual(steps.at(-1).reveal, closed);
  const screws = steps.findIndex((s) => s.reveal.enclosure > 0 && s.reveal.enclosure < 1);
  const opened = steps.findIndex((s) => s.reveal.enclosure === 1);
  const firstInternal = steps.findIndex((s) => s.parts.length > 0);
  assert.ok(screws > 0 && screws < opened && opened < firstInternal);
  for (const step of steps.filter((s) => s.parts.length)) assert.equal(step.reveal.enclosure, 1, step.title);
});

test("each covering is introduced before revealing the parts it contains", () => {
  const steps = TOUR.steps;
  const explains = (name) => steps.findIndex((s) => s.parts.includes(name));
  const coreOpening = steps.findIndex((s) => s.reveal.coldCore > 0);
  const carbonatorOpening = steps.findIndex((s) => s.reveal.carbonator > 0);
  const shell = explains("cold-core/foam-shell");
  const carbonator = explains("cold-core/carbonator-tube");
  assert.ok(shell >= 0 && shell < coreOpening);
  assert.ok(coreOpening <= explains("cold-core/evap-coil"));
  assert.ok(carbonator >= 0 && carbonator < carbonatorOpening);
  assert.equal(steps[explains("cold-core/sparge-stone")].reveal.carbonator, 1);
  assert.match(steps[carbonatorOpening].body, /cutaway/i);
  for (const step of steps) {
    if (step.parts.some((p) => p.startsWith("cold-core/") && !p.startsWith("cold-core/foam-"))) {
      assert.equal(step.reveal.coldCore, 1, step.title);
    }
  }
});
