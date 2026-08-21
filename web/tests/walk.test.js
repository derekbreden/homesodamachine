// Discovery gate for walkPcbBoards (web/lib/walk.js): a board is the source
// named for its directory (pcb/<dir>/<dir>.tsx). This is what keeps helper
// sources and scratch/decoy boards out of the viewer — the symptom that used
// to be papered over with an out/ .gitignore allowlist. Build a fake pcb tree
// in a tmpdir and assert only the name-matches-dir source is returned, even
// when the impostors also have a rendered out/<name>.overlay.svg.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { walkFiles, walkPcbBoards, walkDocuments } from "../lib/walk.js";
import { findGenerateScripts } from "../dev-server/deps.js";

// Write a .tsx source plus a rendered overlay (the "is rendered" tell) for a
// board of the given basename inside <root>/pcb/<dir>/.
function renderFakeBoard(root, dir, name) {
  const boardDir = path.join(root, "pcb", dir);
  fs.mkdirSync(path.join(boardDir, "out"), { recursive: true });
  fs.writeFileSync(path.join(boardDir, `${name}.tsx`), "export default () => null;\n");
  fs.writeFileSync(path.join(boardDir, "out", `${name}.overlay.svg`), "<svg/>\n");
}

test("walkPcbBoards returns only the source named for its directory", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-pcb-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));

  // The real board, a helper source, and a scratch board — all rendered, all in
  // the same directory. Only pcba/pcba.tsx is the board.
  renderFakeBoard(root, "pcba", "pcba");
  renderFakeBoard(root, "pcba", "pcba_parts"); // helper: name != dir
  renderFakeBoard(root, "pcba", "_b15.tmp"); // scratch: name != dir

  const boards = walkPcbBoards(root);
  assert.deepEqual(boards.map((b) => b.source), ["pcb/pcba/pcba.tsx"]);
  assert.equal(boards[0].overlay, "pcb/pcba/out/pcba.overlay.svg");
});

test("walkPcbBoards ignores a directory whose named source is unrendered", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-pcb-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));

  // Named source present but no out/ overlay yet: not a board until rendered.
  const boardDir = path.join(root, "pcb", "widget");
  fs.mkdirSync(boardDir, { recursive: true });
  fs.writeFileSync(path.join(boardDir, "widget.tsx"), "export default () => null;\n");

  assert.deepEqual(walkPcbBoards(root), []);
});

// ── The `.retired` marker (lib/retired.js) ──────────────────────────────────
//
// What the site browses has to be what the build can rebuild. The walkers and the
// build graph read the marker from one module for exactly that reason, so the
// fixture below is walked by both and they are asserted to agree on it: a tree
// only one of them excludes is a model nothing produces, served as if it were live.
function retiredTree(t, prefix) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));

  const live = path.join(root, "live");
  const retired = path.join(root, "retired");
  const nested = path.join(retired, "attempt");

  const gen = 'if __name__ == "__main__":\n    pass\n';
  for (const [dir, name] of [[live, "widget"], [retired, "old"], [nested, "older"]]) {
    fs.mkdirSync(path.join(dir, "drawings"), { recursive: true });
    fs.writeFileSync(path.join(dir, `${name}.py`), gen);
    fs.writeFileSync(path.join(dir, `${name}.step`), "ISO-10303-21;\n");
    fs.writeFileSync(path.join(dir, `${name}.scorecard.json`), "{}\n");
    fs.writeFileSync(path.join(dir, "drawings", `${name}-iso.svg`), "<svg/>\n");
  }
  return { root, retired };
}

// The sidecar is what makes a PDF a document (web/contracts/documents.js), and
// it is the only thing that does — so a PDF a generator wrote for its own
// reasons stays out of the listing and out of `/docs`.
test("walkDocuments lists a PDF its sidecar names, and no other", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-docs-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));

  fs.mkdirSync(path.join(root, "assembly", "cards"), { recursive: true });
  fs.writeFileSync(path.join(root, "assembly", "cards", "deck.pdf"), "%PDF-1.4\n");
  fs.writeFileSync(path.join(root, "assembly", "cards", "deck.cover.png"), "png");
  fs.writeFileSync(
    path.join(root, "assembly", "cards", "deck.pdf.json"),
    JSON.stringify({ title: "Assembly card deck", subtitle: "6 × 4 in", pages: 103, cover: "deck.cover.png" }),
  );
  // A datasheet a board vendored: a PDF under the same root with no sidecar.
  fs.mkdirSync(path.join(root, "pcb"), { recursive: true });
  fs.writeFileSync(path.join(root, "pcb", "wroom.pdf"), "%PDF-1.4\n");

  const docs = walkDocuments(root);
  assert.deepEqual(docs.map((d) => d.path), ["assembly/cards/deck.pdf"]);
  assert.equal(docs[0].title, "Assembly card deck");
  assert.equal(docs[0].pages, 103);
  // The cover comes back root-relative, because that is what /thumbs/ takes.
  assert.equal(docs[0].cover, "assembly/cards/deck.cover.png");
  assert.equal(docs[0].bytes, fs.statSync(path.join(root, "assembly", "cards", "deck.pdf")).size);
});

// A sidecar whose document has not been built yet names nothing, and neither
// does one that does not parse. Either way the listing is what is on disk.
test("walkDocuments skips a sidecar with no document and one that will not parse", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-docs-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));

  fs.mkdirSync(path.join(root, "manual"), { recursive: true });
  fs.writeFileSync(path.join(root, "manual", "manual.pdf.json"), JSON.stringify({ title: "Manual" }));
  fs.mkdirSync(path.join(root, "other"), { recursive: true });
  fs.writeFileSync(path.join(root, "other", "thing.pdf"), "%PDF-1.4\n");
  fs.writeFileSync(path.join(root, "other", "thing.pdf.json"), "{ not json");

  assert.deepEqual(walkDocuments(root), []);
});

test("walkFiles skips a retired directory and everything under it", (t) => {
  const { root, retired } = retiredTree(t, "walk-retired-");

  assert.deepEqual(
    walkFiles(root, ".step").sort(),
    ["live/widget.step", "retired/attempt/older.step", "retired/old.step"],
    "precondition: all three are browsable before the marker goes down",
  );

  fs.writeFileSync(path.join(retired, ".retired"), "kept for reading\n");

  assert.deepEqual(walkFiles(root, ".step"), ["live/widget.step"]);
  // The sidecar beside a retired model goes with it — the viewer must not draw a
  // requirements bar off a card no build refreshes.
  assert.deepEqual(walkFiles(root, ".scorecard.json"), ["live/widget.scorecard.json"]);
});

test("the walkers and the build graph agree on what is retired", (t) => {
  const { root, retired } = retiredTree(t, "walk-retired-agree-");
  fs.writeFileSync(path.join(retired, ".retired"), "kept for reading\n");

  // One marker, one answer: the .step the viewer offers is the .step a generator
  // still writes. Read off the same tree by both readers.
  assert.deepEqual(
    findGenerateScripts([root]).map((p) => path.relative(root, p)),
    [path.join("live", "widget.py")],
  );
  assert.deepEqual(walkFiles(root, ".step"), ["live/widget.step"]);
});
