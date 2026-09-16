// The solids named in hardware/cad-artifacts.json, put on this disk.
//
//     node scripts/fetch-cad-artifacts.mjs            # fetch what this disk is missing
//     node scripts/fetch-cad-artifacts.mjs --check    // 0 = every solid here matches the pointer file
//     node scripts/fetch-cad-artifacts.mjs --adopt    # also replace what holds other bytes
//
// Render runs this after `npm ci` (render.yaml), from web/. The viewer serves `.step` off the
// tree at request time — web/lib/viewer-routes.js — and the tree a deploy clones carries the
// pointer file rather than the solids, so this is the step that fills them in.
//
// It is also `prestart` in package.json, which is the same run under a service whose build
// command is the dashboard's rather than render.yaml's. Whichever fires first leaves the tree
// holding every pointed-at solid, and the other reads 117 MB and finds nothing to do.
//
// THE POINTER FILE IS THE AUTHORITY ON EVERY BYTE. The bundle is held to its sha256 before it is opened,
// and each extracted solid to its own after. A hash that does not match ends the build, which
// leaves the previous deploy serving.
//
// A tree that already holds every solid at its pointed-at hash downloads nothing, so a dev machine
// that cut the solids itself runs this to completion without reaching the network.
//
// LOCAL STARTUP PRESERVES UNPUBLISHED CUTS. A solid present and carrying other bytes can be a
// generator's fresh cut waiting for `pack.py --write`, so local `prestart` reports drift and
// leaves it standing unless `--adopt` is passed. Render always adopts the pointer file,
// replacing any older published members inherited from its build cache.
//
// A SERVER CUTS NOTHING, so drift there is a pointer file that moved on rather than work in progress, and
// `--adopt` takes the pointer file's bytes over the ones on disk. `web/lib/artifacts-live.js` runs this
// that way to bring new geometry into a container the pointer file moved under, with no deploy.

import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { copyFile, mkdir, mkdtemp, readFile, rename, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createGunzip, createGzip } from "node:zlib";
import { fileURLToPath } from "node:url";
import { storeFromEnv } from "../lib/store.js";
import { isCommittedDocumentFile } from "../contracts/documents.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const POINTERS = path.join(ROOT, "hardware", "cad-artifacts.json");
const CHECK = process.argv.includes("--check");
// A Render build or container holds published artifacts, so cached older bytes need
// replacement even when buildCommand/prestart did not pass --adopt. A local build
// still preserves the machine's unpublished cuts unless adoption was requested.
const ADOPT = process.argv.includes("--adopt") || Boolean(process.env.RENDER_GIT_COMMIT);
// THE STORE IS THE SERVICE'S OWN DISK (web/lib/objects.js), when this runs on it. It is read
// before the network and filled from what the tree already holds, so a boot after the first
// reaches nothing outside the box. At build time the disk is not mounted and this is unset or
// absent, and the network answers as it always did.
const STORE_DIR = process.env.OBJECTS_DIR || null;

async function isDir(abs) {
  try {
    return (await stat(abs)).isDirectory();
  } catch {
    return false;
  }
}

async function sha256(file) {
  const h = createHash("sha256");
  await pipeline(createReadStream(file), h);
  return h.digest("hex");
}

async function present(rel) {
  return present_abs(path.join(ROOT, rel));
}

async function present_abs(abs) {
  try {
    return (await stat(abs)).isFile();
  } catch {
    return false;
  }
}

// What this disk is missing, and what it holds under other bytes. Absence is settled by a stat;
// only what survives that is read in full.
async function wanted(solids) {
  const missing = [];
  const here = [];
  for (const rel of Object.keys(solids)) {
    (await present(rel) ? here : missing).push(rel);
  }
  const drifted = [];
  for (const rel of here) {
    if ((await sha256(path.join(ROOT, rel))) !== solids[rel]) drifted.push(rel);
  }
  return { missing, drifted };
}

async function download(url, dest) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) throw new Error(`GET ${url} — ${res.status} ${res.statusText}`);
  await pipeline(Readable.fromWeb(res.body), createWriteStream(dest));
}

const pointers = await readFile(POINTERS, "utf-8").then(JSON.parse).catch(() => null);
if (!pointers) {
  console.log("[cad-artifacts] no pointer file — nothing to fetch");
  process.exit(0);
}

const solids = Object.fromEntries(Object.entries(pointers.solids ?? {})
  .filter(([rel]) => !isCommittedDocumentFile(rel)));
const { missing: absent, drifted } = await wanted(solids);
const OBJECTS = pointers.store?.objects ?? pointers.release?.objects ?? null;

// The configured store supplies authenticated R2 reads or the service's own disk.
// The site also fills it after listening (web/lib/store.js `fillStore`).
const STORE = OBJECTS ? await storeFromEnv().catch(() => null) : null;

// `--adopt`: A SERVER HOLDS NO CUT OF ITS OWN, SO DRIFT THERE IS AGE, NOT WORK. Without it a
// solid present under other bytes is left alone, because on a machine that cuts geometry those
// bytes are a generator's fresh work and `pack.py --write` is what settles them. A container
// cuts nothing: everything it holds came from a bundle, so a hash the pointer file does not name means
// the pointer file moved on, and the newer bytes are the ones to serve. `web/lib/artifacts-live.js`
// passes this when it adopts a pointer file without a deploy.
const missing = ADOPT ? [...absent, ...drifted] : absent;
if (drifted.length && !ADOPT) {
  console.log(`[cad-artifacts] ${drifted.length} solid(s) hold bytes the pointer file does not name, left as they are:`);
  for (const rel of drifted.slice(0, 8)) console.log(`    ${rel}`);
  console.log("    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write");
}
if (drifted.length && ADOPT) {
  console.log(`[cad-artifacts] ${drifted.length} solid(s) hold older bytes — taking the pointer file's`);
}

if (missing.length === 0) {
  console.log(`[cad-artifacts] ${Object.keys(solids).length - drifted.length} solid(s) at the pointed-at hash`);
  process.exit(drifted.length && CHECK ? 1 : 0);
}
if (CHECK) {
  console.error(`[cad-artifacts] ${missing.length} solid(s) missing`);
  for (const rel of missing.slice(0, 8)) console.error(`    ${rel}`);
  process.exit(1);
}

// EVERY MEMBER IS WORTH ASKING FOR BY NAME, AND THE WHOLE POINTER FILE IS TOO. `pack.py` puts every
// member of a pointer file on the release under its own hash as well as inside the bundle, and says so
// with `release.objects`. Asking by name costs what actually moved; the bundle costs the tree
// however little did. There is no member count at which the bundle is the cheaper read:
// measured on 2026-08-27, the 263 objects of this pointer file come to 143.0 MB against a bundle of
// 144.2 MB, because each member is gzipped on its own and the tar's framing is not carried.
// Even the worst case — every member moving at once, which is what a colour or a deflection
// change does — reads less by name than by bundle, and `check_release_room.py` holds that
// premise so the day it stops being true is a red row rather than a slow deploy.
//
// SO WHAT IS LEFT IS ROUND TRIPS, AND THE LANES BELOW ARE WHAT ANSWER THAT. The bundle stays
// the whole of the answer for a pointer file written before `objects`, and the fallthrough below keeps
// it as the answer for any member that does not arrive by name.
const { url, asset } = pointers.release ?? {};
// WHERE AN OBJECT COMES FROM, IN ORDER: this service's own disk or authenticated R2 read;
// the site's store route; the release, the archive the store falls back to. Direct R2 reads
// let a replacement deployment hydrate even when the running site's public redirect is down.
const STORE_URL = pointers.store?.url ?? null;
const RELEASE_BASE = url ? url.slice(0, url.lastIndexOf("/") + 1) : null;

// EIGHT AT A TIME, BECAUSE THE WAIT IS THE ROUND TRIP AND NOT THE BYTES. A member averages a
// few hundred KB and the objects are on a CDN, so one at a time spends the whole fetch waiting
// on latency it could have overlapped. Eight is enough to hide it and few enough that a
// container with 256 MB is never holding more than a handful of members in flight.
const OBJECT_LANES = 8;

async function fetchObject(rel) {
  const dest = path.join(ROOT, rel);
  const gz = dest + ".gz.part";
  const part = `${dest}.${process.pid}.part`;
  const name = `${OBJECTS}${solids[rel]}.gz`;
  const onDisk = STORE_DIR ? path.join(STORE_DIR, name) : null;
  await mkdir(path.dirname(dest), { recursive: true });
  try {
    if (onDisk && await present_abs(onDisk)) {
      await copyFile(onDisk, gz);
    } else {
      let last = new Error("nowhere to fetch from");
      let got = false;
      if (STORE?.kind === "r2") {
        try {
          await pipeline(await STORE.readStream(name), createWriteStream(gz));
          got = true;
        } catch (err) {
          last = err;
        }
      }
      if (!got) {
        for (const base of [STORE_URL, RELEASE_BASE].filter(Boolean)) {
          try {
            await download(`${base}${name}`, gz);
            got = true;
            break;
          } catch (err) {
            last = err;
          }
        }
      }
      if (!got) throw last;
    }
    await pipeline(createReadStream(gz), createGunzip(), createWriteStream(part));
    if ((await sha256(part)) !== solids[rel]) throw new Error("not the pointed-at bytes");
    await rename(part, dest);
    if (STORE && STORE.kind === "disk" && onDisk && !(await present_abs(onDisk)) && await isDir(STORE_DIR)) {
      await STORE.put(name, gz);
    }
  } finally {
    await rm(gz, { force: true });
    await rm(part, { force: true });
  }
}

async function fetchObjects(rels) {
  const queue = [...rels];
  const failed = [];
  const lane = async () => {
    for (let rel = queue.shift(); rel !== undefined; rel = queue.shift()) {
      try {
        await fetchObject(rel);
      } catch (err) {
        failed.push(`${rel} — ${err.message}`);
      }
    }
  };
  await Promise.all(Array.from({ length: Math.min(OBJECT_LANES, rels.length) }, lane));
  return failed;
}

if (OBJECTS && (STORE || STORE_DIR || STORE_URL || RELEASE_BASE)) {
  console.log(`[cad-artifacts] ${missing.length} solid(s) to fetch, by name`);
  const failed = await fetchObjects(missing);
  if (!failed.length) {
    console.log(`[cad-artifacts] ${missing.length} of ${missing.length} solid(s) in place`);
    process.exit(0);
  }
  // WHAT ONE ROUTE COULD NOT SETTLE, THE OTHER STILL CARRIES. The bundle holds every member of
  // this pointer file too, so a missing object or a bad gunzip falls through to it rather than costing
  // the site a solid.
  console.warn(`[cad-artifacts] ${failed.length} solid(s) did not come by name — reading the bundle`);
  for (const line of failed.slice(0, 8)) console.warn(`    ${line}`);
}
if (!url) {
  console.error("[cad-artifacts] no bundle to fall back to");
  process.exit(1);
}

console.log(`[cad-artifacts] ${missing.length} solid(s) to fetch — ${asset} (${(pointers.bundle.bytes / 1e6).toFixed(1)} MB)`);

const work = await mkdtemp(path.join(tmpdir(), "cad-artifacts."));
try {
  const bundle = path.join(work, asset);
  await download(url, bundle);

  // THE MEMBERS ARE THE ANSWER, NOT THE TARBALL. Every extracted solid is held to
  // `pointers.solids[rel]` below, which is strictly stronger than this for the only question that
  // decides anything — are the bytes about to be served the pointed-at bytes. So a tarball that
  // hashes differently while every member verifies is not a reason to serve nothing.
  const got = await sha256(bundle);
  if (got !== pointers.bundle.sha256) {
    console.warn(`[cad-artifacts] ${asset} is not the pointed-at bundle`);
    console.warn(`    pointed at ${pointers.bundle.sha256}`);
    console.warn(`    got    ${got}`);
    console.warn("    members are held to the pointer file individually below");
  }

  // Extract away from the served tree. An incomplete archive or a member with another hash
  // leaves the existing model in place; only verified bytes cross the final atomic rename.
  const extracted = path.join(work, "members");
  await mkdir(extracted);
  execFileSync("tar", ["-xzf", bundle, "-C", extracted, "--", ...missing], { stdio: "inherit" });

  const bad = [];
  for (const rel of missing) {
    const staged = path.join(extracted, rel);
    if (!(await present_abs(staged))) {
      bad.push(`${rel} — not in the bundle`);
      continue;
    }
    const dest = path.join(ROOT, rel);
    const part = `${dest}.${process.pid}.part`;
    await mkdir(path.dirname(dest), { recursive: true });
    try {
      // A sibling temporary file keeps the rename on the destination's filesystem.
      await copyFile(staged, part);
      if ((await sha256(part)) !== solids[rel]) {
        bad.push(`${rel} — not the pointed-at bytes`);
        continue;
      }
      await rename(part, dest);
    } finally {
      await rm(part, { force: true });
    }
  }
  // A SOLID THAT DID NOT ARRIVE IS ONE SOLID. Failing here failed the Render build, and a
  // failed build leaves the PREVIOUS deploy serving — so a bundle this could not settle held
  // back the site whole, including for a push that only touched `web/` and wanted nothing from
  // it. What is here is served; what is not is named. A `.step` that is absent costs its own
  // page, and a `.step.mesh` costs a wasm parse (`viewer-routes` 404s it by design).
  if (bad.length) {
    console.warn(`[cad-artifacts] ${bad.length} solid(s) the pointer file does not vouch for:`);
    for (const line of bad.slice(0, 12)) console.warn(`    ${line}`);
  }

  console.log(`[cad-artifacts] ${missing.length - bad.length} of ${missing.length} solid(s) in place`);
} catch (err) {
  // Nothing here fails the build. The site serves whatever solids the tree holds, which is what
  // it is for; a deploy withheld shows the last cut and says nothing about this one.
  console.error(`[cad-artifacts] ${err.message}`);
  console.error("[cad-artifacts] serving whatever the tree holds");
} finally {
  await rm(work, { recursive: true, force: true });
}
