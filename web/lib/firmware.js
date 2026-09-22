// /api/firmware — the manifest a phone reads before it pushes anything.
//
// The iOS app asks this, compares each entry's `version` against the string the machine reports
// over BLE, and for a target that differs fetches `url`, holds it to `sha256`, and hands the
// bytes plus `crc32` to `MSG_OTA_BEGIN`. The board holds the whole image to that same crc32
// before its boot partition moves.
//
// `firmware/firmware-images.json` is the whole of what this serves, written by
// `tools/publish_firmware.py --write`. `web/scripts/fetch-firmware.mjs` puts the bytes the pointer file
// names under `public/firmware/` at deploy, and `/firmware/<file>` below serves them from there.
//
// AN IMAGE THE DISK DOES NOT HOLD IS STILL LISTED, carrying `available: false`. A phone that
// asks gets the same answer the pointer file gives — what this commit built, at what version — and finds
// out separately that one file did not arrive. Dropping it would read as "there is no such
// target", which is a different fact.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const POINTERS = path.join(ROOT, "firmware", "firmware-images.json");
const IMAGES = path.resolve(HERE, "..", "public", "firmware");

function readPointers() {
  try {
    return JSON.parse(fs.readFileSync(POINTERS, "utf-8"));
  } catch {
    return null;
  }
}

export function mountFirmwareRoutes(app, { commit } = {}) {
  // THE VALIDATOR IS THE CONTENT. Two builds of one board are usually the same
  // number of bytes, and every file here carries the epoch as its mtime, so the
  // size-and-mtime ETag express.static derives is the same string for two
  // releases that share nothing. A caller holding either one revalidates and is
  // told it has the other. The sha256 the pointer file names is served instead,
  // strong, and answers a conditional request here rather than downstream.
  app.get("/firmware/:file", (req, res, next) => {
    const pointers = readPointers();
    const entry = Object.values(pointers?.images ?? {}).find((e) => e.file === req.params.file);
    if (!entry?.sha256) return next();
    const file = path.join(IMAGES, entry.file);
    if (!fs.existsSync(file)) return next();

    const tag = `"${entry.sha256}"`;
    res.set("ETag", tag);
    res.set("Cache-Control", "no-cache");
    res.type("application/octet-stream");
    const asked = String(req.headers["if-none-match"] || "");
    if (asked.split(",").some((t) => t.trim() === tag)) {
      res.status(304).end();
      return;
    }
    res.sendFile(file, { etag: false, lastModified: false, cacheControl: false });
  });

  app.get("/api/firmware", (req, res) => {
    res.set("Cache-Control", "no-store");
    const pointers = readPointers();
    if (!pointers) {
      res.status(503).json({ error: "no firmware pointer file on this deploy" });
      return;
    }
    // Absolute, because the app is not a browser sitting on this origin — it has a URL and
    // nothing else to resolve one against.
    //
    // The scheme comes from the proxy that terminated TLS, not from `req.protocol`: this
    // process is reached over plain HTTP behind Render's edge, so `req.protocol` is "http"
    // for every request the world made over https. An iOS app handed an http:// URL refuses
    // it — App Transport Security requires the secure connection the caller already had.
    const forwarded = String(req.headers["x-forwarded-proto"] || "").split(",")[0].trim();
    const scheme = forwarded || req.protocol;
    const origin = `${scheme}://${req.get("host")}`;
    const images = Object.entries(pointers.images ?? {}).map(([target, e]) => {
      const file = path.join(IMAGES, e.file);
      const available = fs.existsSync(file);
      return {
        target,
        machine: e.machine,
        what: e.what,
        kind: e.kind ?? "app",
        version: e.version ?? null,
        // HEAD's commit time, and the only field the phone orders two builds
        // by. The version string is what a person reads, and two builds made on
        // one day are not ordered by its date. Null from an image published
        // before this field, which reads as "not said".
        buildEpoch: e.build_epoch ?? null,
        bytes: e.bytes,
        crc32: e.crc32,
        // Art only: the crc32 over the pixels, which is what a board reports
        // about the partition it holds. `crc32` above is over the file.
        artCrc32: e.art_crc32 ?? null,
        sha256: e.sha256,
        url: `${origin}/firmware/${e.file}`,
        available,
      };
    });
    res.json({
      commit: pointers.source?.commit ?? null,
      // The commit this container is serving, which moves independently of the pointer file's: a web
      // push deploys without republishing images.
      deployed: commit ?? null,
      unproven: pointers.unproven?.paths ?? [],
      images,
    });
  });
}
