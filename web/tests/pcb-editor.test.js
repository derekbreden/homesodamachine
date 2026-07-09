// Write-back tests for the dev-only PCB component editor (lib/pcb-editor-routes.js).
//
// updatePositionInTsx rewrites a component's placement literal in the board
// .tsx source. Matching is by NUMBER, not string: the source parser rounds
// positions to 2 decimals, so a source `at(-25.0, 12.5)` reaches the client as
// (-25, 12.5) and an exact-string match would silently miss it (the prototype's
// bug). These pin the three placement idioms used on the real board — `{...at()}`,
// `pcbX=/pcbY=`, and bare `x=/y=` — plus the not-found guard.

import { test } from "node:test";
import assert from "node:assert/strict";

import { updatePositionInTsx, updateRotationInTsx } from "../lib/pcb-editor-routes.js";

test("at() spread: matches a trailing-zero literal and rewrites it", () => {
  const src = `    <resistor name="R7" footprint="0603" {...at(-25.0, 12.5)} />`;
  const out = updatePositionInTsx(src, "R7", -25, 12.5, -25.05, 12.5);
  assert.equal(out, `    <resistor name="R7" footprint="0603" {...at(-25.05, 12.5)} />`);
});

test("pcbX/pcbY: rewrites both, leaves rotation untouched", () => {
  const src = `    <Wroom name="U1" pcbX={-31.15} pcbY={-1} pcbRotation={180} />`;
  const out = updatePositionInTsx(src, "U1", -31.15, -1, -30, 2.5);
  assert.equal(out, `    <Wroom name="U1" pcbX={-30} pcbY={2.5} pcbRotation={180} />`);
});

test("bare x/y: rewrites without disturbing pcbX-like neighbours", () => {
  const src = `    <Ds3231Smd name="U6" x={-9} y={-28} />`;
  const out = updatePositionInTsx(src, "U6", -9, -28, -9.5, -28.05);
  assert.equal(out, `    <Ds3231Smd name="U6" x={-9.5} y={-28.05} />`);
});

test("x/y with a fractional literal rounds-trips through 2-decimal parse", () => {
  const src = `    <Cap name="C10" x={-20.5} y={15.42} rot={90} />`;
  const out = updatePositionInTsx(src, "C10", -20.5, 15.42, -20.5, 15.5);
  assert.equal(out, `    <Cap name="C10" x={-20.5} y={15.5} rot={90} />`);
});

test("only the named component on a multi-line source is rewritten", () => {
  const src = [
    `    <resistor name="R7" {...at(-25.0, 12.5)} />`,
    `    <resistor name="R8" {...at(-25.0, 12.5)} />`,
  ].join("\n");
  const out = updatePositionInTsx(src, "R8", -25, 12.5, 0, 0);
  assert.equal(out, [
    `    <resistor name="R7" {...at(-25.0, 12.5)} />`,
    `    <resistor name="R8" {...at(0, 0)} />`,
  ].join("\n"));
});

test("throws when the ref/position can't be found", () => {
  const src = `    <Wroom name="U1" pcbX={-31.15} pcbY={-1} />`;
  assert.throws(() => updatePositionInTsx(src, "U1", 5, 5, 0, 0), /Could not find position/);
  assert.throws(() => updatePositionInTsx(src, "U9", -31.15, -1, 0, 0), /Could not find position/);
});

// --- rotation write-back (updateRotationInTsx) ------------------------------

test("rotation: rewrites an existing pcbRotation, leaving position untouched", () => {
  const src = `    <Wroom name="U1" pcbX={-31.15} pcbY={-1} pcbRotation={180} />`;
  const out = updateRotationInTsx(src, "U1", 270);
  assert.equal(out, `    <Wroom name="U1" pcbX={-31.15} pcbY={-1} pcbRotation={270} />`);
});

test("rotation: rewrites the Cap `rot` shorthand", () => {
  const src = `    <Cap name="C10" x={-20.5} y={15.42} rot={90} />`;
  const out = updateRotationInTsx(src, "C10", 0);
  assert.equal(out, `    <Cap name="C10" x={-20.5} y={15.42} rot={0} />`);
});

test("rotation: a Jst rewrites its `rot` literal like any other wrapper", () => {
  // A Jst now carries an ordinary numeric `rot` (0 = opening north, CCW), so the
  // editor rotates it through the generic `rot={…}` path — no `side` special case.
  const src = `    <Jst name="J11" x={-54.4} y={-34.03} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} label="GAS" rot={90} />`;
  const out = updateRotationInTsx(src, "J11", 180);
  assert.equal(out, `    <Jst name="J11" x={-54.4} y={-34.03} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} label="GAS" rot={180} />`);
});

test("rotation: inserts the `rot` prop (not pcbRotation) for a Jst with none", () => {
  const src = `    <Jst name="J3" count={4} {...at(-29.58, -34.03)} label="FAUCET" />`;
  const out = updateRotationInTsx(src, "J3", 90);
  assert.equal(out, `    <Jst name="J3" count={4} {...at(-29.58, -34.03)} label="FAUCET" rot={90} />`);
});

test("rotation: inserts pcbRotation on a bare {...at()} component that has none", () => {
  const src = `    <resistor name="R7" footprint="0603" {...at(-25, 12.5)} />`;
  const out = updateRotationInTsx(src, "R7", 90);
  assert.equal(out, `    <resistor name="R7" footprint="0603" {...at(-25, 12.5)} pcbRotation={90} />`);
});

test("rotation: inserts the `rot` prop (not pcbRotation) for a Cap with none", () => {
  const src = `    <Cap name="C7" capacitance="0.1uF" {...at(-50, -17)} />`;
  const out = updateRotationInTsx(src, "C7", 90);
  assert.equal(out, `    <Cap name="C7" capacitance="0.1uF" {...at(-50, -17)} rot={90} />`);
});

test("rotation: normalizes to an integer and only touches the named line", () => {
  const src = [
    `    <Wroom name="U1" pcbX={0} pcbY={0} pcbRotation={0} />`,
    `    <Wroom name="U2" pcbX={0} pcbY={0} pcbRotation={0} />`,
  ].join("\n");
  const out = updateRotationInTsx(src, "U2", 90);
  assert.equal(out, [
    `    <Wroom name="U1" pcbX={0} pcbY={0} pcbRotation={0} />`,
    `    <Wroom name="U2" pcbX={0} pcbY={0} pcbRotation={90} />`,
  ].join("\n"));
});

test("rotation: throws when the ref can't be found", () => {
  const src = `    <Wroom name="U1" pcbX={0} pcbY={0} pcbRotation={0} />`;
  assert.throws(() => updateRotationInTsx(src, "U9", 90), /Could not find component/);
});
