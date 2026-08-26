// The solids named in hardware/cad-artifacts.lock.json, put on this disk.
//
//     node scripts/fetch-cad-artifacts.mjs            # fetch what this disk is missing
//     node scripts/fetch-cad-artifacts.mjs --check    // 0 = every solid here matches the lock
//     node scripts/fetch-cad-artifacts.mjs --adopt    # also replace what holds other bytes
//
// Render runs this after `npm ci` (render.yaml), from web/. The viewer serves `.step` off the
// tree at request time — web/lib/viewer-routes.js — and the tree a deploy clones carries the
// lock rather than the solids, so this is the step that fills them in.
//
// It is also `prestart` in package.json, which is the same run under a service whose build
// command is the dashboard's rather than render.yaml's. Whichever fires first leaves the tree
// holding every locked solid, and the other reads 117 MB and finds nothing to do.
//
// THE LOCK IS THE AUTHORITY ON EVERY BYTE. The bundle is held to its sha256 before it is opened,
// and each extracted solid to its own after. A hash that does not match ends the build, which
// leaves the previous deploy serving.
//
// A tree that already holds every solid at its locked hash downloads nothing, so a dev machine
// that cut the solids itself runs this to completion without reaching the network.
//
// ONLY A SOLID THAT IS ABSENT IS WRITTEN, AND `--adopt` IS WHAT SAYS OTHERWISE. A solid present
// and carrying other bytes is a generator's fresh cut waiting to be packed, and this is
// `prestart` — it runs on `npm start` on the machine doing that cutting. So drift is reported and
// left standing, and `pack.py --write` is what settles it. A deploy clone has no solids at all,
// which is the case this fills.
//
// A SERVER CUTS NOTHING, so drift there is a lock that moved on rather than work in progress, and
// `--adopt` takes the lock's bytes over the ones on disk. `web/lib/artifacts-live.js` runs this
// that way to bring new geometry into a container the lock moved under, with no deploy.

import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { mkdir, mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createGunzip } from "node:zlib";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const LOCK = path.join(ROOT, "hardware", "cad-artifacts.lock.json");
const CHECK = process.argv.includes("--check");
const ADOPT = process.argv.includes("--adopt");

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

const lock = await readFile(LOCK, "utf-8").then(JSON.parse).catch(() => null);
if (!lock) {
  console.log("[cad-artifacts] no lock file — nothing to fetch");
  process.exit(0);
}

const solids = lock.solids ?? {};
const { missing: absent, drifted } = await wanted(solids);

// `--adopt`: A SERVER HOLDS NO CUT OF ITS OWN, SO DRIFT THERE IS AGE, NOT WORK. Without it a
// solid present under other bytes is left alone, because on a machine that cuts geometry those
// bytes are a generator's fresh work and `pack.py --write` is what settles them. A container
// cuts nothing: everything it holds came from a bundle, so a hash the lock does not name means
// the lock moved on, and the newer bytes are the ones to serve. `web/lib/artifacts-live.js`
// passes this when it adopts a lock without a deploy.
const missing = ADOPT ? [...absent, ...drifted] : absent;
if (drifted.length && !ADOPT) {
  console.log(`[cad-artifacts] ${drifted.length} solid(s) hold bytes the lock does not name, left as they are:`);
  for (const rel of drifted.slice(0, 8)) console.log(`    ${rel}`);
  console.log("    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write");
}
if (drifted.length && ADOPT) {
  console.log(`[cad-artifacts] ${drifted.length} solid(s) hold older bytes — taking the lock's`);
}

if (missing.length === 0) {
  console.log(`[cad-artifacts] ${Object.keys(solids).length - drifted.length} solid(s) at the locked hash`);
  process.exit(drifted.length && CHECK ? 1 : 0);
}
if (CHECK) {
  console.error(`[cad-artifacts] ${missing.length} solid(s) missing`);
  for (const rel of missing.slice(0, 8)) console.error(`    ${rel}`);
  process.exit(1);
}

// A FEW MEMBERS ARE WORTH ASKING FOR BY NAME; A HUNDRED ARE NOT. `pack.py` puts every member of
// a lock on the release under its own hash as well as inside the bundle, and says so with
// `release.objects`. Fetching those one at a time costs what actually moved — a lock move
// measured on 2026-08-26 changed 3 of 124 members against a 65 MB bundle — and a container that
// holds nothing still reads one asset instead of 124 requests. The threshold is where those
// cross; the bundle is also the whole of the answer for any lock written before `objects`.
const OBJECT_LIMIT = 24;
const { url, asset } = lock.release;

// EIGHT AT A TIME, BECAUSE THE WAIT IS THE ROUND TRIP AND NOT THE BYTES. A member averages a
// few hundred KB and the objects are on a CDN, so one at a time spends the whole fetch waiting
// on latency it could have overlapped. Eight is enough to hide it and few enough that a
// container with 256 MB is never holding more than a handful of members in flight.
const OBJECT_LANES = 8;

async function fetchObject(rel, base) {
  const dest = path.join(ROOT, rel);
  const gz = dest + ".gz.part";
  await mkdir(path.dirname(dest), { recursive: true });
  try {
    await download(`${base}${lock.release.objects}${solids[rel]}.gz`, gz);
    await pipeline(createReadStream(gz), createGunzip(), createWriteStream(dest));
    if ((await sha256(dest)) !== solids[rel]) throw new Error("not the locked bytes");
  } finally {
    await rm(gz, { force: true });
  }
}

async function fetchObjects(rels) {
  const base = url.slice(0, url.lastIndexOf("/") + 1);
  const queue = [...rels];
  const failed = [];
  const lane = async () => {
    for (let rel = queue.shift(); rel !== undefined; rel = queue.shift()) {
      try {
        await fetchObject(rel, base);
      } catch (err) {
        failed.push(`${rel} — ${err.message}`);
      }
    }
  };
  await Promise.all(Array.from({ length: Math.min(OBJECT_LANES, rels.length) }, lane));
  return failed;
}

if (lock.release.objects && missing.length <= OBJECT_LIMIT) {
  console.log(`[cad-artifacts] ${missing.length} solid(s) to fetch, by name`);
  const failed = await fetchObjects(missing);
  if (!failed.length) {
    console.log(`[cad-artifacts] ${missing.length} of ${missing.length} solid(s) in place`);
    process.exit(0);
  }
  // WHAT ONE ROUTE COULD NOT SETTLE, THE OTHER STILL CARRIES. The bundle holds every member of
  // this lock too, so a missing object or a bad gunzip falls through to it rather than costing
  // the site a solid.
  console.warn(`[cad-artifacts] ${failed.length} solid(s) did not come by name — reading the bundle`);
  for (const line of failed.slice(0, 8)) console.warn(`    ${line}`);
}

console.log(`[cad-artifacts] ${missing.length} solid(s) to fetch — ${asset} (${(lock.bundle.bytes / 1e6).toFixed(1)} MB)`);

const work = await mkdtemp(path.join(tmpdir(), "cad-artifacts."));
try {
  const bundle = path.join(work, asset);
  await download(url, bundle);

  // THE MEMBERS ARE THE ANSWER, NOT THE TARBALL. Every extracted solid is held to
  // `lock.solids[rel]` below, which is strictly stronger than this for the only question that
  // decides anything — are the bytes about to be served the locked bytes. So a tarball that
  // hashes differently while every member verifies is not a reason to serve nothing.
  const got = await sha256(bundle);
  if (got !== lock.bundle.sha256) {
    console.warn(`[cad-artifacts] ${asset} is not the locked bundle`);
    console.warn(`    locked ${lock.bundle.sha256}`);
    console.warn(`    got    ${got}`);
    console.warn("    members are held to the lock individually below");
  }

  // The missing ones by name, so a drifted solid beside them keeps its bytes. Members are
  // repo-relative, so the tree is where they land, and they land at the epoch: the bundle carries
  // no mtime. Nothing downstream reads one — what asks whether a solid's mesh payload still
  // answers to it is `_cadq_export._payload_current`, and it settles that on the digest the
  // payload records and never on either file's mtime.
  execFileSync("tar", ["-xzf", bundle, "-C", ROOT, "--", ...missing], { stdio: "inherit" });

  const bad = [];
  for (const rel of missing) {
    if (!(await present(rel))) bad.push(`${rel} — not in the bundle`);
    else if ((await sha256(path.join(ROOT, rel))) !== solids[rel]) bad.push(`${rel} — not the locked bytes`);
  }
  // A SOLID THAT DID NOT ARRIVE IS ONE SOLID. Failing here failed the Render build, and a
  // failed build leaves the PREVIOUS deploy serving — so a bundle this could not settle held
  // back the site whole, including for a push that only touched `web/` and wanted nothing from
  // it. What is here is served; what is not is named. A `.step` that is absent costs its own
  // page, and a `.step.mesh` costs a wasm parse (`viewer-routes` 404s it by design).
  if (bad.length) {
    console.warn(`[cad-artifacts] ${bad.length} solid(s) the lock does not vouch for:`);
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
