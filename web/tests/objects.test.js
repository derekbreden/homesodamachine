// The object store (web/lib/objects.js): an object is kept only when its bytes hash to its
// name, served back immutable, and pruned once nothing names it and it is old enough that no
// publish is still about to.

import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtemp, readdir, utimes, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gzipSync } from "node:zlib";
import { Readable } from "node:stream";
import express from "express";

import { mountObjectRoutes, namedBy, pruneObjects, receiveObject } from "../lib/objects.js";

const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");

async function serve(dir) {
  const app = express();
  mountObjectRoutes(app, { dir });
  const server = await new Promise((resolve) => {
    const s = app.listen(0, () => resolve(s));
  });
  return { base: `http://127.0.0.1:${server.address().port}`, close: () => server.close() };
}

test("an object is kept when its bytes hash to its name, and served back immutable", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "objects-"));
  const { base, close } = await serve(dir);
  try {
    const member = Buffer.from("ISO-10303-21;\nHEADER;\n");
    const name = `s-${sha(member)}.gz`;
    const gz = gzipSync(member);
    const put = await fetch(`${base}/objects/${name}`, { method: "PUT", body: gz });
    assert.equal(put.status, 201);
    assert.deepEqual(await put.json(), { status: 201, name, bytes: gz.length });
    const again = await fetch(`${base}/objects/${name}`, { method: "PUT", body: gz });
    assert.equal(again.status, 200, "an object already held is not written twice");
    const got = await fetch(`${base}/objects/${name}`);
    assert.equal(got.status, 200);
    assert.equal(got.headers.get("cache-control"), "public, max-age=31536000, immutable");
    assert.deepEqual(Buffer.from(await got.arrayBuffer()), gz);
    assert.equal((await fetch(`${base}/objects/s-${"0".repeat(64)}.gz`)).status, 404);
    assert.equal((await fetch(`${base}/objects/../etc/passwd`)).status, 404);
  } finally {
    close();
  }
});

test("bytes that hash to another name, or are not gzip, are refused and leave nothing", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "objects-"));
  const wrong = await receiveObject(dir, `s-${"a".repeat(64)}.gz`, streamOf(gzipSync(Buffer.from("x"))));
  assert.equal(wrong.status, 422);
  const plain = await receiveObject(dir, `s-${sha(Buffer.from("x"))}.gz`, streamOf(Buffer.from("not gzip")));
  assert.equal(plain.status, 422);
  assert.equal((await receiveObject(dir, "not-a-name", streamOf(Buffer.from("")))).status, 404);
  assert.deepEqual(await readdir(dir), [], "no part file survives a refusal");
});

test("prune removes what no line names once it is old, and keeps the named and the young", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "objects-"));
  const named = `s-${"1".repeat(64)}.gz`;
  const oldStray = `s-${"2".repeat(64)}.gz`;
  const youngStray = `s-${"3".repeat(64)}.gz`;
  const part = `s-${"4".repeat(64)}.gz.123.456.part`;
  for (const n of [named, oldStray, youngStray, part]) await writeFile(path.join(dir, n), "x");
  const twoHoursAgo = (Date.now() - 2 * 60 * 60 * 1000) / 1000;
  for (const n of [named, oldStray, part]) await utimes(path.join(dir, n), twoHoursAgo, twoHoursAgo);
  const pointers = { solids: { "hardware/a.step": "1".repeat(64) } };
  assert.deepEqual(namedBy(pointers), new Set(["1".repeat(64)]));
  const removed = await pruneObjects({ dir, named: namedBy(pointers) });
  assert.deepEqual(removed.sort(), [oldStray, part].sort());
  assert.deepEqual((await readdir(dir)).sort(), [named, youngStray].sort());
});

function streamOf(bytes) {
  return Readable.from([bytes]);
}
