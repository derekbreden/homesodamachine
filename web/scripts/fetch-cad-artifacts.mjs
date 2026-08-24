// The solids named in hardware/cad-artifacts.lock.json, put on this disk.
//
//     node scripts/fetch-cad-artifacts.mjs            # fetch what is missing or wrong
//     node scripts/fetch-cad-artifacts.mjs --check    // 0 = every solid here matches the lock
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
// ONLY A SOLID THAT IS ABSENT IS WRITTEN. A solid present and carrying other bytes is a generator's
// fresh cut waiting to be packed, and this is `prestart` — it runs on `npm start` on the machine
// doing that cutting. So drift is reported and left standing, and `pack.py --write` is what settles
// it. A deploy clone has no solids at all, which is the case this fills.

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
const { missing, drifted } = await wanted(solids);

// Named either way: a solid carrying other bytes is what `pack.py --write` is for, and saying so
// is the whole of what happens to it here.
if (drifted.length) {
  console.log(`[cad-artifacts] ${drifted.length} solid(s) hold bytes the lock does not name, left as they are:`);
  for (const rel of drifted.slice(0, 8)) console.log(`    ${rel}`);
  console.log("    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write");
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

const { url, asset } = lock.release;
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
