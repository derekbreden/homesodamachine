import { test } from "node:test";
import assert from "node:assert/strict";
import { timelineFor, locateTime, captionVtt } from "../contracts/tour-timeline.js";

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
