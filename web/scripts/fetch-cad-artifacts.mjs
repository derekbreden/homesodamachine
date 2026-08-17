// The solids named in hardware/cad-artifacts.lock.json, put on this disk.
//
//     node scripts/fetch-cad-artifacts.mjs            # fetch what is missing or wrong
//     node scripts/fetch-cad-artifacts.mjs --check    // 0 = every solid here matches the lock
//
// Render runs this after `npm ci` (render.yaml), from web/. The viewer serves `.step` off the
// tree at request time — web/lib/viewer-routes.js — and the tree a deploy clones carries the
// lock rather than the solids, so this is the step that fills them in.
//
// THE LOCK IS THE AUTHORITY ON EVERY BYTE. The bundle is held to its sha256 before it is opened,
// and each solid to its own after extraction. A hash that does not match ends the build, which
// leaves the previous deploy serving.
//
// A tree that already holds every solid at its locked hash downloads nothing, so a dev machine
// that cut the solids itself runs this to completion without reaching the network.

import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const LOCK = path.join(ROOT, "hardware", "cad-artifacts.lock.json");
const CHECK = process.argv.includes("--check");

async function sha256(file) {
  const h = createHash("sha256");
  await pipeline(createReadStream(file), h);
  return h.digest("hex");
}

async function present(rel) {
  try {
    return (await stat(path.join(ROOT, rel))).isFile();
  } catch {
    return false;
  }
}

// Which solids this disk does not already hold at the hash the lock names. Absence is settled by
// a stat and costs nothing; what survives that is read in full, because a solid of the right size
// and the wrong bytes is the case the hash is here for.
async function wanted(solids) {
  const missing = [];
  for (const rel of Object.keys(solids)) {
    if (!(await present(rel))) missing.push(rel);
  }
  if (missing.length) return { missing, stale: [] };
  const stale = [];
  for (const [rel, want] of Object.entries(solids)) {
    if ((await sha256(path.join(ROOT, rel))) !== want) stale.push(rel);
  }
  return { missing: [], stale };
}

async function download(url, dest) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) throw new Error(`GET ${url} — ${res.status} ${res.statusText}`);
  await pipeline(Readable.fromWeb(res.body), createWriteStream(dest));
}

const lock = await readFile(LOCK, "utf-8").then(JSON.parse).catch(() => null);
if (!lock) {
  console.log("[cad-artifacts] no lock file — nothing to fetch");
  process.exit(0);
}

const solids = lock.solids ?? {};
const { missing, stale } = await wanted(solids);
const count = missing.length + stale.length;

if (count === 0) {
  console.log(`[cad-artifacts] ${Object.keys(solids).length} solid(s) already at the locked hash`);
  process.exit(0);
}
if (CHECK) {
  console.error(`[cad-artifacts] ${missing.length} missing, ${stale.length} not the locked bytes`);
  for (const rel of [...missing, ...stale].slice(0, 8)) console.error(`    ${rel}`);
  process.exit(1);
}

const { url, asset } = lock.release;
console.log(`[cad-artifacts] ${count} solid(s) to fetch — ${asset} (${(lock.bundle.bytes / 1e6).toFixed(1)} MB)`);

const work = await mkdtemp(path.join(tmpdir(), "cad-artifacts."));
try {
  const bundle = path.join(work, asset);
  await download(url, bundle);

  const got = await sha256(bundle);
  if (got !== lock.bundle.sha256) {
    throw new Error(`${asset} is not the locked bundle\n  locked ${lock.bundle.sha256}\n  got    ${got}`);
  }

  // Members are repo-relative, so the tree is where they land, and they land at the epoch: the
  // bundle carries no mtime. What reads one is `_cadq_export._current` and check_thumbnails.py,
  // both asking whether `<file>.step.png` was drawn from the solid beside it. That picture is in
  // git, committed against these exact bytes, so a solid arriving older than it is the true
  // answer — a solid stamped `now` would say every fetched picture wants redrawing.
  execFileSync("tar", ["-xzf", bundle, "-C", ROOT], { stdio: "inherit" });

  const bad = [];
  for (const [rel, want] of Object.entries(solids)) {
    if (!(await present(rel))) bad.push(`${rel} — not in the bundle`);
    else if ((await sha256(path.join(ROOT, rel))) !== want) bad.push(`${rel} — not the locked bytes`);
  }
  if (bad.length) throw new Error(`extracted tree disagrees with the lock:\n  ${bad.join("\n  ")}`);

  console.log(`[cad-artifacts] ${Object.keys(solids).length} solid(s) in place`);
} catch (err) {
  console.error(`[cad-artifacts] ${err.message}`);
  process.exit(1);
} finally {
  await rm(work, { recursive: true, force: true });
}
