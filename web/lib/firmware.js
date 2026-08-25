// /api/firmware — the manifest a phone reads before it pushes anything.
//
// The iOS app asks this, compares each entry's `version` against the string the machine reports
// over BLE, and for a target that differs fetches `url`, holds it to `sha256`, and hands the
// bytes plus `crc32` to `MSG_OTA_BEGIN`. The board holds the whole image to that same crc32
// before its boot partition moves.
//
// `firmware/firmware.lock.json` is the whole of what this serves, written by
// `tools/publish_firmware.py --write`. `web/scripts/fetch-firmware.mjs` puts the bytes the lock
// names under `public/firmware/` at deploy, and express.static serves them from there.
//
// AN IMAGE THE DISK DOES NOT HOLD IS STILL LISTED, carrying `available: false`. A phone that
// asks gets the same answer the lock gives — what this commit built, at what version — and finds
// out separately that one file did not arrive. Dropping it would read as "there is no such
// target", which is a different fact.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const LOCK = path.join(ROOT, "firmware", "firmware.lock.json");
const IMAGES = path.resolve(HERE, "..", "public", "firmware");

function readLock() {
  try {
    return JSON.parse(fs.readFileSync(LOCK, "utf-8"));
  } catch {
    return null;
  }
}

export function mountFirmwareRoutes(app, { commit } = {}) {
  app.get("/api/firmware", (req, res) => {
    res.set("Cache-Control", "no-store");
    const lock = readLock();
    if (!lock) {
      res.status(503).json({ error: "no firmware lock on this deploy" });
      return;
    }
    // Absolute, because the app is not a browser sitting on this origin — it has a URL and
    // nothing else to resolve one against.
    const origin = `${req.protocol}://${req.get("host")}`;
    const images = Object.entries(lock.images ?? {}).map(([target, e]) => {
      const file = path.join(IMAGES, e.file);
      const available = fs.existsSync(file);
      return {
        target,
        machine: e.machine,
        what: e.what,
        kind: e.kind ?? "app",
        version: e.version ?? null,
        bytes: e.bytes,
        crc32: e.crc32,
        sha256: e.sha256,
        url: `${origin}/firmware/${e.file}`,
        available,
      };
    });
    res.json({
      commit: lock.source?.commit ?? null,
      // The commit this container is serving, which moves independently of the lock's: a web
      // push deploys without republishing images.
      deployed: commit ?? null,
      unproven: lock.unproven?.paths ?? [],
      images,
    });
  });
}
