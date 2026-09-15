// The object store (web/lib/objects.js over web/lib/store.js): an object is kept only when its
// bytes hash to its name, served back immutable, and pruned once nothing names it and it is old
// enough that no publish is still about to. The disk store runs for real; R2 runs against a
// fake client that records the commands it is sent.

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
import { DiskStore, R2Store, fillStore, storeFromEnv } from "../lib/store.js";

const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");

async function serve(store) {
  const app = express();
  mountObjectRoutes(app, { store });
  const server = await new Promise((resolve) => {
    const s = app.listen(0, () => resolve(s));
  });
  return { base: `http://127.0.0.1:${server.address().port}`, close: () => server.close() };
}

test("disk: an object is kept when its bytes hash to its name, served back immutable, HEAD answers", async () => {
  const store = new DiskStore(await mkdtemp(path.join(tmpdir(), "objects-")));
  const { base, close } = await serve(store);
  try {
    const member = Buffer.from("ISO-10303-21;\nHEADER;\n");
    const name = `s-${sha(member)}.gz`;
    const gz = gzipSync(member);
    assert.equal((await fetch(`${base}/objects/${name}`, { method: "HEAD" })).status, 404);
    const put = await fetch(`${base}/objects/${name}`, { method: "PUT", body: gz });
    assert.equal(put.status, 201);
    assert.deepEqual(await put.json(), { status: 201, name, bytes: gz.length });
    assert.equal((await fetch(`${base}/objects/${name}`, { method: "PUT", body: gz })).status, 200, "held once");
    assert.equal((await fetch(`${base}/objects/${name}`, { method: "HEAD" })).status, 200);
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

test("bytes that hash to another name, or are not gzip, are refused and leave nothing behind", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "objects-"));
  const store = new DiskStore(dir);
  const wrong = await receiveObject(store, `s-${"a".repeat(64)}.gz`, Readable.from([gzipSync(Buffer.from("x"))]));
  assert.equal(wrong.status, 422);
  const plain = await receiveObject(store, `s-${sha(Buffer.from("x"))}.gz`, Readable.from([Buffer.from("not gzip")]));
  assert.equal(plain.status, 422);
  assert.equal((await receiveObject(store, "not-a-name", Readable.from([Buffer.from("")]))).status, 404);
  assert.deepEqual(await readdir(dir).catch(() => []), [], "nothing was kept");
});

test("disk: prune removes what no line names once it is old, and keeps the named and the young", async () => {
  const dir = await mkdtemp(path.join(tmpdir(), "objects-"));
  const named = `s-${"1".repeat(64)}.gz`;
  const oldStray = `s-${"2".repeat(64)}.gz`;
  const youngStray = `s-${"3".repeat(64)}.gz`;
  for (const n of [named, oldStray, youngStray]) await writeFile(path.join(dir, n), "x");
  const twoHoursAgo = (Date.now() - 2 * 60 * 60 * 1000) / 1000;
  for (const n of [named, oldStray]) await utimes(path.join(dir, n), twoHoursAgo, twoHoursAgo);
  const pointers = { solids: { "hardware/a.step": "1".repeat(64) } };
  assert.deepEqual(namedBy(pointers), new Set(["1".repeat(64)]));
  const removed = await pruneObjects({ store: new DiskStore(dir), named: namedBy(pointers) });
  assert.deepEqual(removed, [oldStray]);
  assert.deepEqual((await readdir(dir)).sort(), [named, youngStray].sort());
});

/** An S3 client that keeps objects in a Map and records what it was asked. */
function fakeR2(initial = {}) {
  const objects = new Map(Object.entries(initial));
  const log = [];
  return {
    objects,
    log,
    async send(cmd) {
      const kind = cmd.constructor.name;
      const { Bucket, Key } = cmd.input;
      log.push([kind, Key ?? cmd.input.Delete?.Objects?.map((o) => o.Key)]);
      assert.equal(Bucket, "bucket");
      switch (kind) {
        case "HeadObjectCommand":
          if (objects.has(Key)) return {};
          throw Object.assign(new Error("NotFound"), { name: "NotFound", $metadata: { httpStatusCode: 404 } });
        case "PutObjectCommand": {
          const chunks = [];
          for await (const c of cmd.input.Body) chunks.push(c);
          objects.set(Key, { body: Buffer.concat(chunks), modified: Date.now() });
          return {};
        }
        case "ListObjectsV2Command":
          return { Contents: [...objects].map(([k, v]) => ({ Key: k, LastModified: new Date(v.modified) })), IsTruncated: false };
        case "DeleteObjectsCommand":
          for (const { Key: k } of cmd.input.Delete.Objects) objects.delete(k);
          return {};
        case "GetObjectCommand":
          return { Body: Readable.from([objects.get(Key).body]) };
        default:
          throw new Error(`unexpected ${kind}`);
      }
    },
  };
}

test("r2: a verified upload is put to the bucket, HEAD answers from it, and GET redirects to the public URL", async () => {
  const client = fakeR2();
  const store = new R2Store({ client, bucket: "bucket", publicUrl: "https://pub-x.r2.dev/" });
  const { base, close } = await serve(store);
  try {
    const member = Buffer.from("ISO-10303-21;\nr2\n");
    const name = `s-${sha(member)}.gz`;
    const gz = gzipSync(member);
    const put = await fetch(`${base}/objects/${name}`, { method: "PUT", body: gz });
    assert.equal(put.status, 201);
    assert.deepEqual(client.objects.get(name).body, gz, "the store holds the gzipped bytes");
    assert.equal((await fetch(`${base}/objects/${name}`, { method: "HEAD" })).status, 200);
    const got = await fetch(`${base}/objects/${name}`, { redirect: "manual" });
    assert.equal(got.status, 302);
    assert.equal(got.headers.get("location"), `https://pub-x.r2.dev/${name}`);
    assert.equal((await fetch(`${base}/objects/s-${"0".repeat(64)}.gz`, { redirect: "manual" })).status, 404);
    assert.deepEqual(client.log.map(([k]) => k).slice(0, 2), ["HeadObjectCommand", "PutObjectCommand"]);
  } finally {
    close();
  }
});

test("r2: without a public URL the bytes stream through the site", async () => {
  const gz = gzipSync(Buffer.from("member"));
  const name = `s-${sha(Buffer.from("member"))}.gz`;
  const client = fakeR2({ [name]: { body: gz, modified: Date.now() } });
  const { base, close } = await serve(new R2Store({ client, bucket: "bucket", publicUrl: null }));
  try {
    const got = await fetch(`${base}/objects/${name}`);
    assert.equal(got.status, 200);
    assert.deepEqual(Buffer.from(await got.arrayBuffer()), gz);
  } finally {
    close();
  }
});

test("r2: prune lists the bucket once and deletes the old unnamed in one batch", async () => {
  const old = Date.now() - 2 * 60 * 60 * 1000;
  const named = `s-${"1".repeat(64)}.gz`;
  const oldStray = `s-${"2".repeat(64)}.gz`;
  const youngStray = `s-${"3".repeat(64)}.gz`;
  const client = fakeR2({
    [named]: { body: Buffer.from("a"), modified: old },
    [oldStray]: { body: Buffer.from("b"), modified: old },
    [youngStray]: { body: Buffer.from("c"), modified: Date.now() },
  });
  const store = new R2Store({ client, bucket: "bucket", publicUrl: null });
  const removed = await pruneObjects({ store, named: new Set(["1".repeat(64)]) });
  assert.deepEqual(removed, [oldStray]);
  assert.deepEqual([...client.objects.keys()].sort(), [named, youngStray].sort());
  assert.deepEqual(client.log.map(([k]) => k), ["ListObjectsV2Command", "DeleteObjectsCommand"]);
});

test("the environment names the store: R2 with a key pair, the disk with a directory, else none", async () => {
  assert.equal(await storeFromEnv({}), null);
  assert.equal((await storeFromEnv({ OBJECTS_DIR: "/tmp/x" })).kind, "disk");
  const r2 = await storeFromEnv({ R2_ACCOUNT_ID: "acct", R2_ACCESS_KEY_ID: "k", R2_SECRET_ACCESS_KEY: "s",
                                  R2_BUCKET: "b", R2_PUBLIC_URL: "https://pub.r2.dev/", OBJECTS_DIR: "/tmp/x" });
  assert.equal(r2.kind, "r2");
  assert.equal(r2.redirectUrl("s-1.gz"), "https://pub.r2.dev/s-1.gz");
});

test("the fill puts what the store lacks, skips what it has and what this tree cut differently", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "tree-"));
  const a = Buffer.from("member a"), b = Buffer.from("member b"), c = Buffer.from("member c");
  await writeFile(path.join(root, "a.step"), a);
  await writeFile(path.join(root, "b.step"), b);
  await writeFile(path.join(root, "c.step"), Buffer.from("a fresh cut, not the pointed-at bytes"));
  const pointers = {
    store: { objects: "s-" },
    solids: { "a.step": sha(a), "b.step": sha(b), "c.step": sha(c), "gone.step": sha(Buffer.from("x")) },
  };
  const store = new DiskStore(await mkdtemp(path.join(tmpdir(), "objects-")));
  await writeFile(path.join(store.dir, `s-${sha(b)}.gz`), gzipSync(b));   // already held
  const lines = [];
  assert.equal(await fillStore({ store, root, pointers, log: (l) => lines.push(l) }), 1);
  assert.deepEqual((await store.list()).map((o) => o.name).sort(), [`s-${sha(a)}.gz`, `s-${sha(b)}.gz`].sort());
  assert.match(lines[0], /1 of 3 member\(s\) put on the disk store/);
  assert.equal(await fillStore({ store, root, pointers, log: () => {} }), 0, "a second pass sends nothing new");
  assert.equal(await fillStore({ store: null, root, pointers }), 0);
  assert.equal(await fillStore({ store, root, pointers: { solids: {} } }), 0, "no prefix, no fill");
});
