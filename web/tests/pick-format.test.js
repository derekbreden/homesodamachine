// pick-format unit tests — parsing and matching of the edge-picker's copy
// blobs. The sample lines are verbatim picks from real design sessions on
// the touch-flo faucet, so the parser is tested against exactly what the
// viewer emits and what gets pasted back into the find box.

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  parsePicks,
  matchPicks,
  scoreEdge,
  formatFace,
  fpt,
} from "../public/js/viewer/pick-format.js";

const STRAIGHT_LINE =
  "edge: x=-6.500 y=-147.096 z=191.380 → x=-6.500 y=-151.041 z=194.691 · len 5.150 · straight · dir x=0.000 y=-0.766 z=0.643";
const ARC_LINE =
  "edge: x=-11.350 y=-148.488 z=199.989 → x=-6.850 y=-151.381 z=196.542 · len 7.054 · arc r=4.500 · center x=-6.850 y=-148.488 z=199.989 · axis x=0.000 y=-0.766 z=0.643";
const CIRCLE_LINE =
  "edge: circle ⌀3.028 · center x=0.054 y=-119.015 z=213.485 · circumference 9.501 · axis x=0.001 y=-0.621 z=0.784";

test("parses a straight edge line", () => {
  const { picks } = parsePicks(STRAIGHT_LINE);
  assert.equal(picks.length, 1);
  const p = picks[0];
  assert.equal(p.kind, "edge");
  assert.deepEqual(p.a, { x: -6.5, y: -147.096, z: 191.38 });
  assert.deepEqual(p.b, { x: -6.5, y: -151.041, z: 194.691 });
  assert.equal(p.len, 5.15);
});

test("parses an arc edge line with center and radius", () => {
  const { picks } = parsePicks(ARC_LINE);
  assert.equal(picks.length, 1);
  const p = picks[0];
  assert.equal(p.kind, "edge-arc");
  assert.equal(p.r, 4.5);
  assert.deepEqual(p.center, { x: -6.85, y: -148.488, z: 199.989 });
  assert.deepEqual(p.axis, { x: 0, y: -0.766, z: 0.643 });
});

test("parses a circle (loop) line", () => {
  const { picks } = parsePicks(CIRCLE_LINE);
  assert.equal(picks.length, 1);
  const p = picks[0];
  assert.equal(p.kind, "circle");
  assert.equal(p.d, 3.028);
  assert.deepEqual(p.center, { x: 0.054, y: -119.015, z: 213.485 });
});

test("parses a whole copy-all blob with file, solid, faces, click", () => {
  const blob = [
    "file: hardware/reference/touch-flo-faucet/faucet-assembly/touch-flo-faucet-assembly.step",
    "solid: shell",
    STRAIGHT_LINE,
    "faceA: plane · n x=0.000 y=-0.766 z=0.643 · thru x=0.000 y=-143.555 z=185.799",
    "faceB: cylinder · r=5.750 · axis x=-8.550 y=-113.058 z=217.477 · dir x=0.000 y=0.766 z=-0.643",
    "click: x=-10.077 y=-141.662 z=187.102",
  ].join("\n");
  const { picks, files } = parsePicks(blob);
  assert.equal(files.length, 1);
  assert.match(files[0], /touch-flo-faucet-assembly\.step$/);
  assert.deepEqual(
    picks.map((p) => p.kind),
    ["edge", "face-plane", "face-cylinder", "point"],
  );
  const plane = picks[1];
  assert.deepEqual(plane.n, { x: 0, y: -0.766, z: 0.643 });
  const cyl = picks[2];
  assert.equal(cyl.r, 5.75);
  assert.deepEqual(cyl.dir, { x: 0, y: 0.766, z: -0.643 });
});

test("prose between pick lines parses to nothing", () => {
  const { picks } = parsePicks(
    "And so 14.300 - 10.682 = 3.618 is the distance to extend.\n" +
    "Which I only mention in passing so that you know where I get 10.682 from",
  );
  assert.equal(picks.length, 0);
});

test("old standalone endpoints rows still parse as point markers", () => {
  const { picks } = parsePicks("endpoints: x=1.000 y=2.000 z=3.000 · x=4.000 y=5.000 z=6.000");
  assert.equal(picks.length, 2);
  assert.ok(picks.every((p) => p.kind === "point"));
});

// --- matching ---

const EDGES = [
  { kind: "straight", a: { x: -6.5, y: -147.096, z: 191.38 }, b: { x: -6.5, y: -151.041, z: 194.691 }, length: 5.15 },
  { kind: "straight", a: { x: 6.5, y: -147.096, z: 191.38 }, b: { x: 6.5, y: -151.041, z: 194.691 }, length: 5.15 },
  {
    kind: "arc",
    a: { x: -11.35, y: -148.488, z: 199.989 }, b: { x: -6.85, y: -151.381, z: 196.542 },
    length: 7.054, radius: 4.5, center: { x: -6.85, y: -148.488, z: 199.989 },
  },
  { kind: "loop", center: { x: 0.054, y: -119.015, z: 213.485 }, radius: 1.514, length: 9.501 },
];

const FACES = [
  { kind: "plane", n: { x: 0, y: -0.766, z: 0.643 }, thru: { x: 0, y: -143.555, z: 185.799 } },
  { kind: "cylinder", r: 5.75, axis: { x: -8.55, y: -113.058, z: 217.477 }, dir: { x: 0, y: 0.766, z: -0.643 } },
  { kind: "curved", near: { x: 1, y: 2, z: 3 } },
];

test("matches each pick kind to the right entity", () => {
  const blob = [
    STRAIGHT_LINE,
    ARC_LINE,
    CIRCLE_LINE,
    "faceA: plane · n x=0.000 y=-0.766 z=0.643 · thru x=2.000 y=-143.555 z=185.799", // thru offset IN the plane still matches
    "faceB: cylinder · r=5.750 · axis x=-8.550 y=-120.000 z=223.000 · dir x=0.000 y=-0.766 z=0.643", // axis point elsewhere on the line, dir flipped
    "click: x=1.000 y=2.000 z=3.000",
  ].join("\n");
  const { picks } = parsePicks(blob);
  const results = matchPicks(picks, EDGES, FACES);

  assert.deepEqual(
    results.map((r) => r.type),
    ["edge", "edge", "edge", "face", "face", "point"],
  );
  assert.equal(results[0].index, 0); // the -x straight, not its +x mirror
  assert.equal(results[1].index, 2);
  assert.equal(results[2].index, 3);
  assert.equal(results[3].index, 0);
  assert.equal(results[4].index, 1);
});

test("reversed endpoints still match the same edge", () => {
  const reversed =
    "edge: x=-6.500 y=-151.041 z=194.691 → x=-6.500 y=-147.096 z=191.380 · len 5.150 · straight · dir x=0.000 y=0.766 z=-0.643";
  const { picks } = parsePicks(reversed);
  const [r] = matchPicks(picks, EDGES, FACES);
  assert.equal(r.type, "edge");
  assert.equal(r.index, 0);
});

test("a pick from elsewhere in space matches nothing", () => {
  const { picks } = parsePicks(
    "edge: x=100.000 y=100.000 z=100.000 → x=110.000 y=100.000 z=100.000 · len 10.000 · straight · dir x=1.000 y=0.000 z=0.000",
  );
  const [r] = matchPicks(picks, EDGES, FACES);
  assert.equal(r.type, null);
});

test("scoreEdge prefers the exact edge over its lateral mirror", () => {
  const { picks } = parsePicks(STRAIGHT_LINE);
  assert.ok(scoreEdge(picks[0], EDGES[0]) < scoreEdge(picks[0], EDGES[1]));
});

test("formatFace round-trips through parsePicks", () => {
  const plane = { kind: "plane", n: { x: 0, y: -0.766, z: 0.643 }, thru: { x: 1.5, y: -140, z: 188.5 } };
  const { picks } = parsePicks(`faceA: ${formatFace(plane)}`);
  assert.equal(picks[0].kind, "face-plane");
  assert.deepEqual(picks[0].thru, { x: 1.5, y: -140, z: 188.5 });

  const cyl = { kind: "cylinder", r: 7.525, axis: { x: -3.175, y: -139.57, z: 185.065 }, dir: { x: 0, y: 0.643, z: 0.766 } };
  const { picks: p2 } = parsePicks(`face: ${formatFace(cyl)}`);
  assert.equal(p2[0].kind, "face-cylinder");
  assert.equal(p2[0].r, 7.525);
});

test("fpt formats negative zero away", () => {
  assert.equal(fpt({ x: -0.0001, y: 1, z: -2 }), "x=0.000 y=1.000 z=-2.000");
});
