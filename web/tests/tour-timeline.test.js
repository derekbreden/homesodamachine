import { test } from "node:test";
import assert from "node:assert/strict";
import { timelineFor, locateTime, captionVtt, stageAt, motionEnd } from "../contracts/tour-timeline.js";
import { TOUR } from "../contracts/tour-water.js";

const steps = [
  { dwell: 1250, enter: 600, body: "The enclosure opens." },
  { dwell: 2750, enter: 900, body: "Water enters the machine." },
];

test("beat durations include camera travel and form a continuous timeline", () => {
  assert.deepEqual(timelineFor(steps), {
    beats: [
      { index: 0, start: 0, end: 1250, duration: 1250 },
      { index: 1, start: 1250, end: 4000, duration: 2750 },
    ],
    duration: 4000,
  });
});

test("seeking clamps to the tour and hands exact boundaries to the next beat", () => {
  const timeline = timelineFor(steps);
  for (const [time, index, local, progress] of [
    [-200, 0, 0, 0], [0, 0, 0, 0], [625, 0, 625, 0.5],
    [1250, 1, 0, 0], [2625, 1, 1375, 0.5],
    [4000, 1, 2750, 1], [9000, 1, 2750, 1],
  ]) {
    const at = locateTime(timeline, time);
    assert.deepEqual({ index: at.index, local: at.local, progress: at.progress },
      { index, local, progress }, `seek ${time}`);
    assert.equal(at.time, Math.max(0, Math.min(time, 4000)));
  }
  assert.equal(locateTime(timeline, Number.NaN).time, 0);
});

test("downloaded captions share exact beat timing and narration", () => {
  assert.equal(captionVtt(steps),
    "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.250\nThe enclosure opens.\n\n"
    + "2\n00:00:01.250 --> 00:00:04.000\nWater enters the machine.\n");
});

test("caption timestamps carry minutes and hours without losing milliseconds", () => {
  const captions = captionVtt([
    { dwell: 3_599_750, body: "First." },
    { dwell: 1000, body: "Second." },
  ]);
  assert.match(captions, /00:00:00\.000 --> 00:59:59\.750/);
  assert.match(captions, /00:59:59\.750 --> 01:00:00\.750/);
});

test("motionEnd includes late channel tracks as well as the default motion", () => {
  assert.equal(motionEnd({ dwell: 1000 }), 700);
  assert.equal(motionEnd({ dwell: 1000, motion: 250 }), 250);
  assert.equal(motionEnd({ dwell: 1000, motion: 250, motions: { caps: [400, 900] } }), 900);
  assert.equal(motionEnd({ dwell: 1000, motions: { caps: [100, 300] } }), 700);
  assert.equal(motionEnd({ dwell: 1000, motion: 0 }), 0);
});

test("staggered staging holds each layer until its window and settles it before the next", () => {
  const sequence = [
    { dwell: 1000, reveal: { coreIsolation: 1, coreSpread: 1, coreShell: 1, coreCaps: 1 } },
    { dwell: 2000, motion: 1700,
      reveal: { coreIsolation: 1, coreSpread: 0, coreShell: 0, coreCaps: 0 },
      motions: { coreSpread: [200, 600], coreShell: [800, 1200], coreCaps: [1300, 1700] } },
  ];
  for (const [time, spread, shell, caps] of [
    [-100, 1, 1, 1], [200, 1, 1, 1], [400, 0.5, 1, 1],
    [600, 0, 1, 1], [800, 0, 1, 1], [1000, 0, 0.5, 1],
    [1200, 0, 0, 1], [1300, 0, 0, 1], [1500, 0, 0, 0.5],
    [1700, 0, 0, 0], [3000, 0, 0, 0],
  ]) {
    assert.deepEqual(stageAt(sequence, 1, time), {
      coreIsolation: 1, coreSpread: spread, coreShell: shell, coreCaps: caps,
    }, `local time ${time}`);
  }
});

test("new and removed reveal channels interpolate from and to their closed value", () => {
  const sequence = [
    { dwell: 1000, motion: 1000, reveal: { enclosure: 1 } },
    { dwell: 1000, motion: 1000, reveal: { coreIsolation: 1 } },
  ];
  assert.deepEqual(stageAt(sequence, 0, 0), { enclosure: 0 });
  assert.deepEqual(stageAt(sequence, 0, 500), { enclosure: 0.5 });
  assert.deepEqual(stageAt(sequence, 1, 500), { enclosure: 0.5, coreIsolation: 0.5 });
  assert.deepEqual(stageAt(sequence, 1, 1000), { enclosure: 0, coreIsolation: 1 });
});

test("every scene boundary is continuous and each motion reaches its target before the cut", () => {
  for (let index = 0; index < TOUR.steps.length; index++) {
    const step = TOUR.steps[index];
    assert.deepEqual(stageAt(TOUR.steps, index, motionEnd(step)), step.reveal, step.id);
    assert.deepEqual(stageAt(TOUR.steps, index, step.dwell), step.reveal, step.id);
    if (index) {
      const previous = TOUR.steps[index - 1];
      assert.deepEqual(stageAt(TOUR.steps, index, 0),
        stageAt(TOUR.steps, index - 1, previous.dwell), `${previous.id} → ${step.id}`);
    }
  }
});

test("seeking forward, backward or directly to a frame produces the same staging", () => {
  const timeline = timelineFor(TOUR.steps);
  const contract = structuredClone(TOUR.steps);
  const times = timeline.beats.flatMap((beat) => [beat.start, beat.start + beat.duration / 2, beat.end]);
  const atTime = (time) => {
    const at = locateTime(timeline, time);
    return stageAt(TOUR.steps, at.index, at.local);
  };
  const expected = times.map(atTime);
  for (let index = times.length - 1; index >= 0; index--) {
    assert.deepEqual(atTime(times[index]), expected[index], `backward seek ${times[index]}`);
  }
  for (const index of [31, 2, 45, 15, 0, 38, times.length - 1]) {
    assert.deepEqual(atTime(times[index]), expected[index], `direct seek ${times[index]}`);
  }
  assert.deepEqual(TOUR.steps, contract, "seeking never mutates the story or prior reveal states");
});
