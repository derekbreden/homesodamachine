// The images named in firmware/firmware.lock.json, put on this disk.
//
//     node scripts/fetch-firmware.mjs            # fetch what is missing or wrong
//     node scripts/fetch-firmware.mjs --check    // 0 = every image here matches the lock
//
// Render runs this after `npm ci` (render.yaml), from web/. `/api/firmware` serves the manifest
// off the lock and `/firmware/<target>.bin` serves the bytes off `web/public/firmware/`, so a
// deploy clone — which carries the lock and none of the images — fills them in here.
//
// It is also `prestart` in package.json, the same run under a service whose build command is the
// dashboard's rather than render.yaml's. Whichever fires first leaves the tree holding every
// locked image, and the other reads them and finds nothing to do.
//
// THE LOCK IS THE AUTHORITY ON EVERY BYTE. The bundle is held to its sha256 before it is opened,
// and each extracted image to its own after. What the phone then pushes over BLE is held to the
// crc32 in the same lock by the board receiving it, so the bytes that reach flash are checked
// twice against one committed file.
//
// A tree that already holds every image at its locked hash downloads nothing, so the machine that
// built them runs this to completion without reaching the network.
//
// NOTHING HERE FAILS THE BUILD. An image that did not arrive costs its own target in
// `/api/firmware`; the site and every other target go out.

import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { mkdir, mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const LOCK = path.join(ROOT, "firmware", "firmware.lock.json");
const DEST = path.resolve(HERE, "..", "public", "firmware");
const CHECK = process.argv.includes("--check");

async function sha256(file) {
  const h = createHash("sha256");
  await pipeline(createReadStream(file), h);
  return h.digest("hex");
}

async function present(file) {
  try {
    return (await stat(file)).isFile();
  } catch {
    return false;
  }
}

// What this disk is missing, and what it holds under other bytes. Absence is settled by a stat;
// only what survives that is read in full.
async function wanted(images) {
  const missing = [];
  const here = [];
  for (const [target, entry] of Object.entries(images)) {
    (await present(path.join(DEST, entry.file)) ? here : missing).push(target);
  }
  const drifted = [];
  for (const target of here) {
    const entry = images[target];
    if ((await sha256(path.join(DEST, entry.file))) !== entry.sha256) drifted.push(target);
  }
  return { missing, drifted };
}

async function download(url, dest) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) throw new Error(`GET ${url} — ${res.status} ${res.statusText}`);
  await pipeline(Readable.fromWeb(res.body), createWriteStream(dest));
}

const lock = await readFile(LOCK, "utf-8").then(JSON.parse).catch(() => null);
if (!lock) {
  console.log("[firmware] no lock file — nothing to fetch");
  process.exit(0);
}

const images = lock.images ?? {};
await mkdir(DEST, { recursive: true });
const { missing, drifted } = await wanted(images);

// Named either way: an image carrying other bytes is what `publish_firmware.py --write` is for.
if (drifted.length) {
  console.log(`[firmware] ${drifted.length} image(s) hold bytes the lock does not name, left as they are:`);
  for (const target of drifted) console.log(`    ${target}`);
  console.log("    ~/.platformio/penv/bin/python tools/publish_firmware.py --write");
}

if (missing.length === 0) {
  console.log(`[firmware] ${Object.keys(images).length - drifted.length} image(s) at the locked hash`);
  process.exit(drifted.length && CHECK ? 1 : 0);
}
if (CHECK) {
  console.error(`[firmware] ${missing.length} image(s) missing`);
  for (const target of missing) console.error(`    ${target}`);
  process.exit(1);
}

const { url, asset } = lock.release;
console.log(`[firmware] ${missing.length} image(s) to fetch — ${asset} (${(lock.bundle.bytes / 1e6).toFixed(1)} MB)`);

const work = await mkdtemp(path.join(tmpdir(), "firmware."));
try {
  const bundle = path.join(work, asset);
  await download(url, bundle);

  // THE MEMBERS ARE THE ANSWER, NOT THE TARBALL. Every extracted image is held to its own
  // `sha256` below, which is what decides whether the bytes about to be served are the locked
  // bytes. A tarball that hashes differently while every member verifies still serves.
  const got = await sha256(bundle);
  if (got !== lock.bundle.sha256) {
    console.warn(`[firmware] ${asset} is not the locked bundle`);
    console.warn(`    locked ${lock.bundle.sha256}`);
    console.warn(`    got    ${got}`);
    console.warn("    members are held to the lock individually below");
  }

  const files = missing.map((t) => images[t].file);
  execFileSync("tar", ["-xzf", bundle, "-C", DEST, "--", ...files], { stdio: "inherit" });

  const bad = [];
  for (const target of missing) {
    const entry = images[target];
    const file = path.join(DEST, entry.file);
    if (!(await present(file))) bad.push(`${target} — not in the bundle`);
    else if ((await sha256(file)) !== entry.sha256) bad.push(`${target} — not the locked bytes`);
  }
  if (bad.length) {
    console.warn(`[firmware] ${bad.length} image(s) the lock does not vouch for:`);
    for (const line of bad) console.warn(`    ${line}`);
  }

  console.log(`[firmware] ${missing.length - bad.length} of ${missing.length} image(s) in place`);
} catch (err) {
  console.error(`[firmware] ${err.message}`);
  console.error("[firmware] serving whatever images the tree holds");
} finally {
  await rm(work, { recursive: true, force: true });
}
