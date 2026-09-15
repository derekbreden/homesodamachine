// The object store: the bytes main's pointer file names, held by hash on this service's disk,
// put here by whichever machine cut them and served from here.
//
//     PUT  /objects/s-<sha256>.gz     the gzipped member; kept when its bytes hash to the name
//     GET  /objects/s-<sha256>.gz     the same bytes back, immutable
//
// THE DISK IS THE STORE. render.yaml attaches it at OBJECTS_DIR, it persists across deploys, and
// `fetch-cad-artifacts.mjs` fills it from the tree a deploy built and reads it back on every
// boot after, so a container starts from its own disk and not from the network. The GitHub
// release stays what it was, an archive the fetcher falls back to for an object the disk and
// the store do not hold.
//
// NO TOKEN, BECAUSE THE POINTER FILE IS THE AUTHORITY. Anyone can put an object here, and only
// an object main's pointer file names stays: `pruneObjects` runs on the hour and removes what
// no line names once it is an hour old. So an upload nobody pointed at is gone by then, and
// whoever can push main is whoever can name bytes here — the trust the pointer file already
// carries, and the reason a cloud session, which the release refuses, can publish here without
// holding a secret. The size cap and the hash check are the rest of it.
//
// STREAMED, NOT BUFFERED. The largest member is a 62 MB STEP and the container has a few
// hundred MB; the body goes to the disk and through gunzip-and-hash as it arrives, and nothing
// holds it whole.

import { createHash } from "node:crypto";
import { createWriteStream } from "node:fs";
import { mkdir, readdir, readFile, rename, rm, stat } from "node:fs/promises";
import path from "node:path";
import { Transform } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createGunzip } from "node:zlib";

export const OBJECT_NAME = /^s-([0-9a-f]{64})\.gz$/;
export const MAX_OBJECT_BYTES = 256 * 1024 * 1024;
export const PRUNE_AGE_MS = 60 * 60 * 1000;
export const PRUNE_EVERY_MS = 60 * 60 * 1000;

async function isFile(abs) {
  try {
    return (await stat(abs)).isFile();
  } catch {
    return false;
  }
}

/** Hold the request body on disk under `name`, kept only when its bytes hash to the name. */
export async function receiveObject(dir, name, body) {
  const m = OBJECT_NAME.exec(name);
  if (!m) return { status: 404, error: "not an object name" };
  const final = path.join(dir, name);
  if (await isFile(final)) {
    body.resume?.();
    return { status: 200, name, held: true };
  }
  await mkdir(dir, { recursive: true });
  const part = `${final}.${process.pid}.${Date.now()}.part`;
  let bytes = 0;
  const counted = new Transform({
    transform(chunk, _enc, cb) {
      bytes += chunk.length;
      if (bytes > MAX_OBJECT_BYTES) return cb(new Error("too large"));
      cb(null, chunk);
    },
  });
  const hash = createHash("sha256");
  const src = body.pipe(counted);
  try {
    await Promise.all([
      pipeline(src, createWriteStream(part)),
      pipeline(src, createGunzip(), hash),
    ]);
  } catch (err) {
    await rm(part, { force: true });
    const status = err.message === "too large" ? 413 : 422;
    return { status, error: status === 413 ? `larger than ${MAX_OBJECT_BYTES} bytes` : `not a gzip stream: ${err.message}` };
  }
  const digest = hash.digest("hex");
  if (digest !== m[1]) {
    await rm(part, { force: true });
    return { status: 422, error: `the bytes hash to ${digest}, not to the name` };
  }
  await rename(part, final);
  return { status: 201, name, bytes };
}

export function mountObjectRoutes(app, { dir }) {
  app.get("/objects/:name", async (req, res) => {
    const name = req.params.name;
    if (!OBJECT_NAME.test(name)) return res.status(404).json({ error: "not an object name" });
    const abs = path.join(dir, name);
    if (!(await isFile(abs))) return res.status(404).json({ error: "no such object here" });
    res.sendFile(abs, {
      headers: { "Content-Type": "application/gzip", "Cache-Control": "public, max-age=31536000, immutable" },
    });
  });
  app.put("/objects/:name", async (req, res) => {
    const out = await receiveObject(dir, req.params.name, req);
    res.status(out.status).json(out);
  });
}

/** The hashes a pointer file names: every member, so every object worth keeping. */
export function namedBy(pointers) {
  return new Set(Object.values(pointers?.solids ?? {}));
}

/** Remove what no line names once it is old enough that no publish is still about to name it. */
export async function pruneObjects({ dir, named, now = Date.now(), maxAge = PRUNE_AGE_MS }) {
  const removed = [];
  let entries;
  try {
    entries = await readdir(dir);
  } catch {
    return removed;
  }
  for (const entry of entries) {
    const abs = path.join(dir, entry);
    const m = OBJECT_NAME.exec(entry);
    if (m && named.has(m[1])) continue;
    let st;
    try {
      st = await stat(abs);
    } catch {
      continue;
    }
    if (!st.isFile() || now - st.mtimeMs < maxAge) continue;
    await rm(abs, { force: true });
    removed.push(entry);
  }
  return removed;
}

/** The hourly prune, keyed to the pointer file on this disk, which the live adopt keeps at main's. */
export function mountObjectPrune({ dir, pointersPath, everyMs = PRUNE_EVERY_MS }) {
  const look = async () => {
    try {
      const pointers = JSON.parse(await readFile(pointersPath, "utf-8"));
      const removed = await pruneObjects({ dir, named: namedBy(pointers) });
      if (removed.length) console.log(`[objects] pruned ${removed.length} object(s) no line names`);
    } catch (err) {
      console.error(`[objects] prune skipped: ${err.message}`);
    }
  };
  const timer = setInterval(look, everyMs);
  timer.unref();
  return timer;
}
