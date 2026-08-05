// pick-format unit tests — parsing and matching of the edge-picker's copy
// blobs. The sample lines are verbatim picks from real design sessions on
// the touch-flo faucet, so the parser is tested against exactly what the
// viewer emits and what gets pasted back into the find box.

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  parsePicks,
  parseNames,
  matchPicks,
  matchNames,
  normalizeName,
  scoreEdge,
  formatFace,
  fpt,
  pickFileToViewerPath,
} from "../public/js/viewer/pick-format.js";
import { EDITION_DIRS } from "../lib/editions.js";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

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
  const { picks, names } = parsePicks(
    "And so 14.300 - 10.682 = 3.618 is the distance to extend.\n" +
    "Which I only mention in passing so that you know where I get 10.682 from",
  );
  assert.equal(picks.length, 0);
  // Neither line is name-shaped: the first carries bare numbers and an `=`,
  // the second is longer than any list of names.
  assert.deepEqual(names, []);
});

test("old standalone endpoints rows still parse as point markers", () => {
  const { picks } = parsePicks("endpoints: x=1.000 y=2.000 z=3.000 · x=4.000 y=5.000 z=6.000");
  assert.equal(picks.length, 2);
  assert.ok(picks.every((p) => p.kind === "point"));
});

// --- names ---
// Verbatim component names off the kitchen enclosure assembly — what
// export_assembly writes into the STEP and step.js stamps onto each mesh.
const SCENE_NAMES = new Set([
  "bag-a-tray-assembly", "co2-1", "co2-2", "condenser+fan", "display",
  "enclosure_back_top", "fluid-1", "fluid-17", "fluid-18", "fluid-2",
  "foam-assembly", "pcba", "psu", "seaflo-pump", "tee-y-a", "tee-y-d",
  "tee-y-e", "water-3",
]);

// What the find box does end to end: type into it, get parts back. Every
// name case goes through BOTH halves — a query the parser splits before the
// matcher can weigh it is a query that doesn't work, whatever each half
// says on its own.
const found = (typed) => {
  const { names } = parsePicks(typed);
  return [...new Set(matchNames(names, SCENE_NAMES).flatMap((h) => h.names))];
};

test("a bare name is a name query", () => {
  const { picks, files, names } = parsePicks("fluid-17");
  assert.equal(picks.length, 0);
  assert.equal(files.length, 0);
  assert.deepEqual(names, ["fluid-17"]);
  assert.deepEqual(found("fluid-17"), ["fluid-17"]);
});

test("several names on one line, comma- or space-separated", () => {
  assert.deepEqual(found("fluid-17, fluid-18"), ["fluid-17", "fluid-18"]);
  assert.deepEqual(found("fluid-17 water-3"), ["fluid-17", "water-3"]);
});

test("case and separators are noise", () => {
  assert.equal(normalizeName("Fluid_17"), "fluid17");
  // Including a SPACE where the name has a hyphen: `fluid 17` is one name
  // typed loosely, not two, and only the matcher can know that.
  for (const q of ["fluid-17", "FLUID-17", "Fluid 17", "fluid_17", "fluid.17", "  fluid-17  "]) {
    assert.deepEqual(found(q), ["fluid-17"], q);
  }
});

test("an exact name stands alone against the prefixes it shares", () => {
  // `fluid-1` must not drag in fluid-17 and fluid-18 — the run you asked for
  // is the run you get.
  assert.deepEqual(found("fluid-1"), ["fluid-1"]);
});

test("a name nothing matches exactly widens to every name holding it", () => {
  assert.deepEqual(found("fluid"), ["fluid-1", "fluid-2", "fluid-17", "fluid-18"]);
  assert.deepEqual(found("tee"), ["tee-y-a", "tee-y-d", "tee-y-e"]);
});

test("a single character does not sweep the assembly", () => {
  assert.deepEqual(found("f"), []);
});

test("a name the model doesn't hold comes back empty, carrying the query", () => {
  const [hit] = matchNames(["flud-17"], SCENE_NAMES);
  assert.equal(hit.query, "flud-17");
  assert.deepEqual(hit.names, []);
});

test("a scorecard's component.port reference lands on the component", () => {
  assert.deepEqual(found("tee-y-d.Y-D-3"), ["tee-y-d"]);
  assert.deepEqual(found("foam-assembly.reservoir-B"), ["foam-assembly"]);
});

test("a copy blob's solid: line stands alone but never over its own picks", () => {
  assert.deepEqual(parsePicks("solid: fluid-17").names, ["fluid-17"]);
  const blob = ["solid: fluid-17", STRAIGHT_LINE].join("\n");
  const { picks, names } = parsePicks(blob);
  assert.equal(picks.length, 1);
  assert.deepEqual(names, []); // the picks are the target; the solid is the container
});

test("a name query survives the words around it", () => {
  assert.deepEqual(found("show me fluid-17"), ["fluid-17"]);
});

test("parseNames keeps a line whole but for its commas", () => {
  assert.deepEqual(parseNames("fluid 17"), ["fluid 17"]);       // one loose name
  assert.deepEqual(parseNames("psu, pcba"), ["psu", "pcba"]);   // two
  assert.deepEqual(parseNames("condenser+fan"), ["condenser+fan"]);
  assert.deepEqual(parseNames("enclosure_back_top"), ["enclosure_back_top"]);
});

test("parseNames rejects what isn't a name", () => {
  assert.deepEqual(parseNames("a = b"), []);                    // punctuation no name carries
  assert.deepEqual(parseNames("one two three four five"), []);  // too long to be a list
  assert.deepEqual(parseNames("  "), []);
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

test("pick_text.py composer output round-trips through the parser", (t) => {
  // hardware/scripts/pick_text.py is the CAD-side composer; its demo
  // emits one line of each kind off a small solid. Skipped when the
  // CadQuery venv isn't present (CI without the toolchain).
  const venvPython = path.join(REPO_ROOT, "tools", "cad-venv", "bin", "python");
  const script = path.join(REPO_ROOT, "hardware", "scripts", "pick_text.py");
  if (!fs.existsSync(venvPython) || !fs.existsSync(script)) {
    return t.skip("cad venv or pick_text.py unavailable");
  }
  const out = execFileSync(venvPython, [script], { encoding: "utf8", timeout: 120_000 });
  const { picks } = parsePicks(out);
  const kinds = picks.map((p) => p.kind).sort();
  assert.deepEqual(kinds, ["circle", "edge", "edge-arc", "face-cylinder", "face-plane", "point"]);
  // Every non-empty line parsed — the composer emits nothing the parser drops.
  assert.equal(picks.length, out.trim().split("\n").length);
});

test("pickFileToViewerPath strips the repo prefix per edition", () => {
  const roots = Object.values(EDITION_DIRS);
  assert.equal(
    pickFileToViewerPath("hardware/printed-parts/faucet/touch-flo-mounting-gasket/touch-flo-mounting-gasket.step", roots),
    "printed-parts/faucet/touch-flo-mounting-gasket/touch-flo-mounting-gasket.step",
  );
  // The nested root is stripped WHOLE — `hardware/` must not shorten it, or a thin
  // pick opens the kitchen file of the same name.
  assert.equal(
    pickFileToViewerPath("hardware/printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step", roots),
    "printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step",
  );
  assert.equal(pickFileToViewerPath("reference/a/b.step", roots), "reference/a/b.step");
});

test("every edition's content root round-trips a copy blob", () => {
  // What the picker composes (`<root>/<viewer path>`) is what the Find box takes
  // apart. Adding an edition must not need this test edited — it walks the list.
  const roots = Object.values(EDITION_DIRS);
  for (const dir of roots) {
    const viewerPath = "printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step";
    assert.equal(pickFileToViewerPath(`${dir}/${viewerPath}`, roots), viewerPath, dir);
  }
});
