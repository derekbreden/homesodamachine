// The object store's face on the site: the bytes main's pointer file names, by hash, put here
// by whichever machine cut them and fetched from here by every reader.
//
//     PUT  /objects/s-<sha256>.gz     the gzipped member; kept when its bytes hash to the name
//     GET  /objects/s-<sha256>.gz     the bytes back: a redirect to the store's public URL, or
//                                     the stream itself when the store has none
//     HEAD /objects/s-<sha256>.gz     whether the store holds it
//
// THE STORE BEHIND THIS IS THE ENVIRONMENT'S CHOICE (store.js): Cloudflare R2, whose public
// URL carries every read, or a disk on this service. Either way the pointer file's `store.url`
// is this site, so a publisher and a fetcher talk to one address.
//
// NO TOKEN, BECAUSE THE POINTER FILE IS THE AUTHORITY. Anyone can put an object here, and only
// an object main's pointer file names stays: `pruneObjects` runs on the hour and removes what
// no line names once it is an hour old. So an upload nobody pointed at is gone by then, and
// whoever can push main is whoever can name bytes here, the trust the pointer file already
// carries, and a cloud session publishes here holding no secret. The size cap and the hash
// check are the rest of it.
//
// STREAMED, NOT BUFFERED. The largest member is a 62 MB STEP and the container has a few
// hundred MB; the body goes to a temporary file and through gunzip-and-hash as it arrives,
// and only a verified file is handed to the store.

import { createHash } from "node:crypto";
import { createWriteStream } from "node:fs";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { Transform } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createGunzip } from "node:zlib";

export { OBJECT_NAME } from "./store.js";
import { OBJECT_NAME } from "./store.js";

export const MAX_OBJECT_BYTES = 256 * 1024 * 1024;
export const PRUNE_AGE_MS = 60 * 60 * 1000;
export const PRUNE_EVERY_MS = 60 * 60 * 1000;

/** Hold the request body, kept in the store only when its bytes hash to the name. */
export async function receiveObject(store, name, body) {
  const m = OBJECT_NAME.exec(name);
  if (!m) return { status: 404, error: "not an object name" };
  if (await store.has(name)) {
    body.resume?.();
    return { status: 200, name, held: true };
  }
  const work = await mkdtemp(path.join(tmpdir(), "object-"));
  const part = path.join(work, name);
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
    try {
      await Promise.all([
        pipeline(src, createWriteStream(part)),
        pipeline(src, createGunzip(), hash),
      ]);
    } catch (err) {
      const status = err.message === "too large" ? 413 : 422;
      return { status, error: status === 413 ? `larger than ${MAX_OBJECT_BYTES} bytes` : `not a gzip stream: ${err.message}` };
    }
    const digest = hash.digest("hex");
    if (digest !== m[1]) return { status: 422, error: `the bytes hash to ${digest}, not to the name` };
    await store.put(name, part);
    return { status: 201, name, bytes };
  } finally {
    await rm(work, { recursive: true, force: true });
  }
}

export function mountObjectRoutes(app, { store }) {
  app.head("/objects/:name", async (req, res) => {
    const name = req.params.name;
    if (!OBJECT_NAME.test(name)) return res.status(404).end();
    res.status((await store.has(name)) ? 200 : 404).end();
  });
  app.get("/objects/:name", async (req, res) => {
    const name = req.params.name;
    if (!OBJECT_NAME.test(name)) return res.status(404).json({ error: "not an object name" });
    if (!(await store.has(name))) return res.status(404).json({ error: "no such object here" });
    const url = store.redirectUrl(name);
    if (url) return res.redirect(302, url);
    res.set({ "Content-Type": "application/gzip", "Cache-Control": "public, max-age=31536000, immutable" });
    const stream = await store.readStream(name);
    stream.on("error", () => res.destroy());
    stream.pipe(res);
  });
  app.put("/objects/:name", async (req, res) => {
    let out;
    try {
      out = await receiveObject(store, req.params.name, req);
    } catch (err) {
      out = { status: 502, error: `the store did not take it: ${err.message}` };
    }
    res.status(out.status).json(out);
  });
}

/** The hashes a pointer file names: every member, so every object worth keeping. */
export function namedBy(pointers) {
  return new Set(Object.values(pointers?.solids ?? {}));
}

/** Remove what no line names once it is old enough that no publish is still about to name it. */
export async function pruneObjects({ store, named, now = Date.now(), maxAge = PRUNE_AGE_MS }) {
  const stale = [];
  for (const { name, modified } of await store.list()) {
    const m = OBJECT_NAME.exec(name);
    if (m && named.has(m[1])) continue;
    if (now - modified < maxAge) continue;
    stale.push(name);
  }
  await store.remove(stale);
  return stale;
}

/** The hourly prune, keyed to the pointer file on this disk, which the live adopt keeps at main's. */
export function mountObjectPrune({ store, pointersPath, everyMs = PRUNE_EVERY_MS }) {
  const look = async () => {
    try {
      const pointers = JSON.parse(await readFile(pointersPath, "utf-8"));
      const removed = await pruneObjects({ store, named: namedBy(pointers) });
      if (removed.length) console.log(`[objects] pruned ${removed.length} object(s) no line names`);
    } catch (err) {
      console.error(`[objects] prune skipped: ${err.message}`);
    }
  };
  const timer = setInterval(look, everyMs);
  timer.unref();
  return timer;
}
