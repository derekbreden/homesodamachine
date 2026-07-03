// Conformance test for the picks.json contract (web/contracts/picks-schema.ts).
//
// The board sidecar crosses from the tscircuit builder (pick-data.ts, TS) to the browser
// viewer (pcb.js / pcb-pick.js / pcb-edit.js, untyped JS). TS pins the producer end; this pins
// the consumer end — load the committed pcba.picks.json and assert it still matches the shape
// the viewer reads, so a producer change that drops or renames a field fails here instead of
// silently in the UI. Skips when no board has been rendered (out/ is a build artifact).

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const PICKS = path.join(REPO_ROOT, "hardware", "pcb", "pcba", "out", "pcba.picks.json");

const isNum = (v) => typeof v === "number";
const isStr = (v) => typeof v === "string";
const nullOr = (pred) => (v) => v === null || pred(v);
const isObj = (v) => v != null && typeof v === "object" && !Array.isArray(v);

test("pcba.picks.json conforms to the picks-schema contract", (t) => {
  if (!fs.existsSync(PICKS)) return t.skip("no rendered board with picks");
  const p = JSON.parse(fs.readFileSync(PICKS, "utf8"));

  // Top level (PicksFile).
  assert.ok(isStr(p.board), "board is a string");
  assert.ok(isNum(p.unitsPerMm), "unitsPerMm is a number");
  assert.ok(p.size === null || (isObj(p.size) && isNum(p.size.width) && isNum(p.size.height)), "size is null | {width, height}");
  for (const k of ["pads", "vias", "traces", "errors"]) assert.ok(Array.isArray(p[k]), `${k} is an array`);
  assert.ok(isObj(p.clearance) && nullOr(isNum)(p.clearance.floor) && Array.isArray(p.clearance.tight), "clearance is {floor, tight[]}");
  assert.ok(p.capAudit === null || isObj(p.capAudit), "capAudit is null | object");

  // Pad.
  if (p.pads.length) {
    const pad = p.pads[0];
    assert.ok(isNum(pad.x) && isNum(pad.y), "pad has x, y");
    assert.ok(pad.kind === "through-hole" || pad.kind === "smt-pad", "pad kind is through-hole | smt-pad");
    for (const k of ["ref", "pin", "net"]) assert.ok(k in pad, `pad carries ${k}`);
    assert.ok(nullOr(isNum)(pad.pinNum), "pad pinNum is number | null");
    assert.ok(nullOr(isNum)(pad.pad), "pad pad is number | null");
  }

  // Via.
  if (p.vias.length) {
    const v = p.vias[0];
    assert.ok(isNum(v.x) && isNum(v.y), "via has x, y");
    for (const k of ["net", "fromLayer", "toLayer", "outer"]) assert.ok(k in v, `via carries ${k}`);
  }

  // Trace.
  if (p.traces.length) {
    const tr = p.traces[0];
    for (const k of ["net", "from", "to", "width", "points"]) assert.ok(k in tr, `trace carries ${k}`);
    assert.ok(Array.isArray(tr.points), "trace points is an array");
    if (tr.points.length) {
      const pt = tr.points[0];
      assert.ok(Array.isArray(pt) && pt.length === 2 && isNum(pt[0]) && isNum(pt[1]), "trace point is [number, number]");
    }
  }

  // Clearance pairs (ClearancePair).
  for (const pair of p.clearance.tight) {
    assert.ok(isNum(pair.gap) && isStr(pair.a) && isStr(pair.b), "clearance pair is {gap, a, b}");
  }

  // DRC errors (BoardError).
  for (const e of p.errors) {
    assert.ok(isStr(e.kind) && isStr(e.text), "error is {kind, text}");
  }

  // Cap-decoupling audit (CapAudit).
  if (p.capAudit) {
    assert.ok(Array.isArray(p.capAudit.rows), "capAudit.rows is an array");
    assert.ok(isNum(p.capAudit.flagged), "capAudit.flagged is a number");
    for (const r of p.capAudit.rows) {
      for (const k of ["cap", "near", "role", "gap", "budget", "over"]) assert.ok(k in r, `capAudit row carries ${k}`);
      assert.ok(nullOr(isNum)(r.gap), "capAudit row gap is number | null");
      assert.ok(typeof r.over === "boolean", "capAudit row over is boolean");
    }
  }
});
