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

import { walkPcbBoards } from "../lib/walk.js";

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
