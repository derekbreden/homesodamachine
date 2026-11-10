// The gear's dot is the whole board, reduced to one colour, on every page. It reads
// `public/checks.json`, which `repo-tools checks-now` pins when requested.
//
// artifacts-live.js refreshes this file without a deploy. These fixtures verify that the
// next page render reads the changed verdict and its gear agrees with the served JSON.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { checksNavClass } from "../lib/shell.js";

const FILE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "public", "checks.json");

function withVerdict(mutate, fn) {
  const orig = fs.readFileSync(FILE, "utf-8");
  try {
    const v = JSON.parse(orig);
    mutate(v);
    fs.writeFileSync(FILE, JSON.stringify(v, null, 1));
    return fn();
  } finally {
    fs.writeFileSync(FILE, orig);
  }
}

test("the gear follows the file, not the boot", (t) => {
  if (!fs.existsSync(FILE)) return t.skip("no verdict on this disk");
  const before = checksNavClass();
  assert.ok(before === " checks-ok" || before === " checks-red", `unexpected ${before}`);

  const red = withVerdict((v) => { v.checks[0].status = "red"; }, checksNavClass);
  assert.equal(red, " checks-red", "a red that landed after boot has to reach the dot");

  const green = withVerdict((v) => v.checks.forEach((c) => { c.status = "ok"; }), checksNavClass);
  assert.equal(green, " checks-ok", "and a board that went green has to clear it");

  assert.equal(checksNavClass(), before, "the file is what it was, so the dot is too");
});

test("a verdict this cannot read wears no colour at all", (t) => {
  if (!fs.existsSync(FILE)) return t.skip("no verdict on this disk");
  const orig = fs.readFileSync(FILE, "utf-8");
  try {
    fs.writeFileSync(FILE, "{ not json");
    assert.equal(checksNavClass(), "", "an unparsable verdict is no verdict");
  } finally {
    fs.writeFileSync(FILE, orig);
  }
  assert.notEqual(checksNavClass(), "", "and the good file reads again after it");
});
