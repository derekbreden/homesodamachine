import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { TOUR } from "../contracts/tour-water.js";
import { motionEnd, timelineFor } from "../contracts/tour-timeline.js";

const HARDWARE = fileURLToPath(new URL("../../hardware/", import.meta.url));
const modelPath = path.join(HARDWARE, TOUR.model);
const CHANNELS = [
  "enclosure", "park", "coldCore", "carbonator",
  "coreIsolation", "coreCaps", "coreShell", "coreSpread",
];
const CLOSED = Object.fromEntries(CHANNELS.map((key) => [key, 0]));
const byId = (id) => {
  const step = TOUR.steps.find((candidate) => candidate.id === id);
  assert.ok(step, `missing scene: ${id}`);
  return step;
};
const referencedParts = (step) => [
  ...step.parts, ...(step.focus || []), ...(step.context || []),
  ...(step.subjects || []).flatMap((subject) => subject.parts),
];

// Generated solids are fetched separately from a fresh checkout.
test("every highlighted, framed, contextual and labelled body exists in the assembly", {
  skip: !fs.existsSync(modelPath) && "the generated solid is not on this disk",
}, () => {
  const products = fs.readFileSync(modelPath, "latin1").matchAll(/PRODUCT\('([^']*)'/g);
  const names = new Set([...products].map((m) => m[1].replace(/\/\d+$/, "")));
  const missing = TOUR.steps.flatMap((step) => referencedParts(step)
    .filter((name) => name !== "*" && !names.has(name))
    .map((name) => `${step.id}: ${name}`));
  assert.deepEqual(missing, []);
});

test("the 19-scene narrative carries readable captions through a 130-second timeline", () => {
  assert.equal(TOUR.steps.length, 19);
  assert.equal(timelineFor(TOUR.steps).duration, 130_000);
  const ids = new Set();
  for (const step of TOUR.steps) {
    assert.match(step.id, /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/);
    assert.ok(!ids.has(step.id), `duplicate scene id: ${step.id}`);
    ids.add(step.id);
    assert.ok(Number.isSafeInteger(step.dwell) && step.dwell > 0, step.title);
    for (const key of ["chapter", "title", "body", "label"]) {
      assert.ok(step[key]?.trim(), `${step.id}: ${key}`);
    }
    assert.ok(step.dwell >= step.body.split(/\s+/).length * 300, `caption too fast: ${step.id}`);
    assert.equal(step.dir.length, 3, step.id);
    assert.ok(step.dir.every(Number.isFinite) && step.dir.some((n) => n !== 0), step.id);
    assert.ok(Number.isFinite(step.pad) && step.pad > 0, step.id);
    assert.ok((step.focus || step.parts).length > 0, step.id);
    assert.equal(step.model, undefined, "the entire tour stays in one assembly");
    for (const state of [step.reveal, ...(step.frameReveal ? [step.frameReveal] : [])]) {
      assert.deepEqual(Object.keys(state).sort(), [...CHANNELS].sort(), step.id);
      for (const channel of CHANNELS) {
        assert.ok(Number.isFinite(state[channel]) && state[channel] >= 0
          && state[channel] <= 1, `${step.id}: ${channel}`);
      }
    }
    for (const [channel, range] of Object.entries(step.motions || {})) {
      assert.ok(CHANNELS.includes(channel), `${step.id}: unknown motion ${channel}`);
      assert.equal(range.length, 2, step.id);
      assert.ok(range.every(Number.isFinite) && range[0] >= 0 && range[1] > range[0], step.id);
    }
    assert.ok(motionEnd(step) <= step.dwell, `${step.id}: unfinished motion`);
  }
});

test("screws release before the enclosure opens and the internal narrative begins", () => {
  const steps = TOUR.steps;
  assert.deepEqual(steps[0].reveal, CLOSED);
  assert.deepEqual(steps.at(-1).reveal, CLOSED);
  const screws = steps.findIndex((s) => s.reveal.enclosure > 0 && s.reveal.enclosure < 1);
  const opened = steps.findIndex((s) => s.reveal.enclosure === 1);
  const firstInternal = steps.findIndex((s) => s.parts.length > 0);
  assert.ok(screws > 0 && screws < opened && opened < firstInternal);
  assert.equal(steps[opened].reveal.park, 0, "quadrants remain visible as they separate");
  assert.equal(steps[firstInternal].reveal.park, 1, "quadrants clear the internal view");
  for (const step of steps.filter((s) => s.parts.length)) assert.equal(step.reveal.enclosure, 1, step.id);
});

test("the cold core isolates before caps, shell and inner assemblies separate in order", () => {
  const first = (channel) => TOUR.steps.findIndex((step) => step.reveal[channel] > 0);
  const isolated = first("coreIsolation");
  const caps = first("coreCaps");
  const shell = first("coreShell");
  const spread = first("coreSpread");
  assert.ok(isolated > 0 && isolated < caps && caps < shell && shell < spread);
  assert.equal(TOUR.steps[isolated].id, "cold-core");
  assert.equal(TOUR.steps[caps].id, "core-caps");
  assert.equal(TOUR.steps[shell].id, "core-shell");
  assert.equal(TOUR.steps[spread].id, "core-spread");
  assert.ok(TOUR.steps[isolated].parts.includes("cold-core/foam-shell"));
  for (const step of TOUR.steps.slice(isolated, TOUR.steps.indexOf(byId("core-in-machine")))) {
    assert.equal(step.reveal.coreIsolation, 1, step.id);
  }
  for (const step of TOUR.steps) {
    assert.equal(step.reveal.coldCore, 0, "the independent channels own the core staging");
    assert.equal(step.reveal.carbonator, 0, "the complete carbonator stays together");
    if (step.parts.some((name) => name.startsWith("cold-core/") && !name.startsWith("cold-core/foam-"))) {
      assert.equal(step.reveal.coreCaps, 1, step.id);
      assert.equal(step.reveal.coreShell, 1, step.id);
      assert.equal(step.reveal.coreSpread, 1, step.id);
    }
  }
});

test("the coil, carbonator and both reservoirs retain shared context and stable labels", () => {
  const bodies = ["cold-core/evap-coil", "cold-core/carbonator-tube", "cold-core/reservoir-a", "cold-core/reservoir-b"];
  const ids = ["core-spread", "copper-coil", "carbonator", "flavor-reservoirs"];
  const actors = byId(ids[0]).subjects;
  assert.equal(actors.length, 4);
  assert.equal(new Set(actors.map((subject) => subject.id)).size, 4);
  assert.deepEqual(actors.flatMap((subject) => subject.parts).sort(), [...bodies].sort());
  for (const id of ids) {
    const step = byId(id);
    assert.deepEqual(step.subjects, actors, id);
    const frame = new Set([...step.focus, ...step.context]);
    for (const body of bodies) assert.ok(frame.has(body), `${id}: ${body} left the composition`);
    assert.ok(step.contextWeight >= 0 && step.contextWeight <= 1, id);
    for (const subject of step.subjects) assert.ok(subject.text.trim(), `${id}: ${subject.id}`);
  }
});

test("reassembly reverses the spread, shell and caps before the machine returns", () => {
  const reassemble = byId("core-reassemble");
  const returnMachine = byId("core-in-machine");
  const [spread, shell, caps] = ["coreSpread", "coreShell", "coreCaps"].map((channel) => {
    assert.equal(reassemble.reveal[channel], 0, channel);
    assert.equal(reassemble.frameReveal[channel], 1, `${channel}: the whole exploded core stays framed`);
    return reassemble.motions[channel];
  });
  assert.ok(spread[0] > 0, "the camera has time to widen before reassembly");
  assert.ok(spread[1] <= shell[0] && shell[1] <= caps[0], "each layer returns in order");
  assert.equal(reassemble.reveal.coreIsolation, 1);
  assert.equal(returnMachine.reveal.coreIsolation, 0);
  assert.equal(TOUR.steps.indexOf(returnMachine), TOUR.steps.indexOf(reassemble) + 1);
  const closing = byId("ready-to-pour");
  assert.ok(closing.motions.park[1] <= closing.motions.enclosure[0], "quadrants return before they close");
});
