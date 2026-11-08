// Published geometry reaches open pages from the committed pointer and shared mesh objects.
// Main resolves to a commit before its immutable pointer is read; changed files alone are adopted.

import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import { isScorecard } from "../contracts/scorecard-sidecar.js";
import { isArchivedDocumentFile, isCommittedDocumentFile } from "../contracts/documents.js";
import { websitePointers } from "../contracts/artifact-scope.js";

const run = promisify(execFile);

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WEB = path.resolve(HERE, "..");
const ROOT = path.resolve(WEB, "..");
const POINTERS = path.join(ROOT, "hardware", "cad-artifacts.json");

// THE VERDICT IS NOT CODE EITHER. `checks.json` sits under `web/public/`, which `render.yaml`
// deploys on, so every reading `checks_now.py` pinned rebuilt the container around it — 24 of
// the 24 deploying commits in the six hours this was measured, each a `npm ci` and a restart,
// none of them in parallel. A verdict twenty minutes behind describes a tree that has moved.
// `render.yaml` holds it out of the filter and this carries it, on the same look as the pointer file.
const CHECKS = path.join(WEB, "public", "checks.json");
const CHECKS_URL =
  "https://api.github.com/repos/derekbreden/homesodamachine/contents/web/public/checks.json?ref=main";

// The build times, `tools/build_times.py`'s rows, ride the same look. They come off the raw
// file, which the contents API's unauthenticated ceiling below does not count.
const BUILD_TIMES = path.join(WEB, "public", "build-times.json");
const BUILD_TIMES_URL =
  "https://raw.githubusercontent.com/derekbreden/homesodamachine/main/web/public/build-times.json";

// The poll recovers missed publication notifications.
const POLL_MS = 120_000;

// Coalescing holds a later request briefly while retaining its request to look again.
const MIN_GAP_MS = 1_000;

// A publication whose bytes are unavailable remains eligible for recovery, but a
// persistent failure must not hash the whole tree on every poll. A new pointer
// gets its own first attempt; retries of the same pointer wait up to 30 minutes.
const MAX_RETRY_MS = 30 * 60_000;
let failedAdoption = null;

let running = null;
let lookAgain = false;
let lastLook = 0;
// THE LOOK THE FLOOR TURNS AWAY IS HELD, NOT DROPPED. A cut whose post lands inside the gap of
// the one before it is the second session's geometry, and dropping the post leaves it for the
// 120s poll — twelve times the floor it was refused for. One deferred look at a time carries it
// instead: the floor is still one look per `MIN_GAP_MS`, and what a refused post now costs is
// the remainder of that gap.
let pending = null;

async function lockOnDisk() {
  try {
    return JSON.parse(await readFile(POINTERS, "utf-8"));
  } catch {
    return null;
  }
}

// WHAT SAYS THE GEOMETRY MOVED. A publish from the machine that changed it puts the members
// that moved on the release under their own hashes and leaves the bundle the pointer file already
// names where it is (`pack.py --write --publish-held`): the bundle's digest does not move with
// them, the member hashes do. Either moving is a look worth taking; a disk with no pointer file at all
// is behind by definition.
export function pointersMoved(have, pointers) {
  if (!have) return true;
  if (have.bundle?.sha256 !== pointers.bundle?.sha256) return true;
  return JSON.stringify(websitePointers(have).solids ?? {}) !== JSON.stringify(websitePointers(pointers).solids ?? {});
}

async function solidsPresent(pointers) {
  for (const rel of Object.keys(websitePointers(pointers).solids ?? {})) {
    if (isCommittedDocumentFile(rel) || isArchivedDocumentFile(rel)) continue;
    try {
      if (!(await stat(path.join(ROOT, rel))).isFile()) return false;
    } catch { return false; }
  }
  return true;
}

// Removed model parts must leave the directory the viewer walks. Only paths named by the
// previous pointer file are retired; local files that neither publication names are untouched.
export async function retireSolids(root, have, pointers, { websiteOnly = Boolean(process.env.RENDER_GIT_COMMIT) } = {}) {
  const hardware = path.resolve(root, "hardware");
  const scope = value => websiteOnly ? websitePointers(value) : value;
  const retired = Object.keys(scope(have)?.solids ?? {})
    .filter(rel => !isCommittedDocumentFile(rel) &&
      (isArchivedDocumentFile(rel) || !(rel in (scope(pointers).solids ?? {}))));
  for (const rel of retired) {
    const target = path.resolve(root, rel);
    const inside = path.relative(hardware, target);
    if (!inside || inside === ".." || inside.startsWith("../") || path.isAbsolute(inside)) {
      throw new Error(`cannot retire a path outside hardware/: ${rel}`);
    }
    await rm(target, { force: true });
  }
  return retired;
}

// Also what the store's prune keeps by (objects.js `pruneUnnamed`): this disk's pointer file is
// main's only once an adoption settles.
export async function lockOnMain() {
  const refs = await fetch('https://github.com/derekbreden/homesodamachine.git/info/refs?service=git-upload-pack');
  if (!refs.ok) throw new Error(`Main refs say ${refs.status}`);
  const commit = (await refs.text()).match(/([a-f0-9]{40}) refs\/heads\/main(?:\x00|\n)/)?.[1];
  if (!commit) throw new Error('Main has no resolved commit');
  const response = await fetch(`https://raw.githubusercontent.com/derekbreden/homesodamachine/${commit}/hardware/cad-artifacts.json`);
  if (!response.ok) throw new Error(`Main pointer says ${response.status}`);
  return response.json();
}

// The verdict on main onto this disk, when it is not already the bytes here. Its own read, so a
// GitHub that answers for one file and not the other still moves what it answered for; and its
// own failure, because a verdict this cannot fetch is a stale band on the gear and not a reason
// to leave geometry unadopted.
async function carryChecks() {
  const res = await fetch(CHECKS_URL, {
    headers: { accept: "application/vnd.github+json", "user-agent": "homesodamachine-site" },
  });
  if (!res.ok) throw new Error(`GitHub says ${res.status} ${res.statusText}`);
  const meta = await res.json();
  if (meta.encoding !== "base64" || !meta.content) throw new Error("no inline content");
  const text = Buffer.from(meta.content, "base64").toString("utf-8");
  // Parsed before it is written: a truncated verdict draws no band rather than a wrong one.
  const verdict = JSON.parse(text);
  if (!Array.isArray(verdict.checks)) throw new Error("no checks in it");
  let here = null;
  try {
    here = await readFile(CHECKS, "utf-8");
  } catch { /* a container whose clone predates the file */ }
  if (here === text) return { moved: false };
  await writeFile(CHECKS, text);
  return { moved: true, green: verdict.green === true, checks: verdict.checks.length };
}

// The build times on main onto this disk: parsed before written, failing on their own.
async function carryBuildTimes() {
  const res = await fetch(BUILD_TIMES_URL, { headers: { "user-agent": "homesodamachine-site" } });
  if (res.status === 404) return { moved: false };
  if (!res.ok) throw new Error(`GitHub says ${res.status} ${res.statusText}`);
  const text = await res.text();
  const document = JSON.parse(text);
  if (!Array.isArray(document.builds)) throw new Error("no builds in it");
  let here = null;
  try {
    here = await readFile(BUILD_TIMES, "utf-8");
  } catch { /* a container whose clone predates the file */ }
  if (here === text) return { moved: false };
  await writeFile(BUILD_TIMES, text);
  return { moved: true, builds: document.builds.length };
}

// The pointer file's own shape, before it is written anywhere. A truncated or half-published pointer file that
// reached main is a pointer file this refuses rather than one it serves.
function usable(pointers) {
  return Boolean(
    pointers &&
    typeof pointers.bundle?.sha256 === "string" &&
    pointers.release?.url?.startsWith("https://github.com/derekbreden/homesodamachine/releases/") &&
    pointers.solids &&
    Object.keys(pointers.solids).length,
  );
}

// THE SCORECARD IS COMMITTED DATA UNDER A PATH NOTHING DEPLOYS ON, WHICH IS WHY IT IS CARRIED
// HERE. `pack.py` keeps the scorecards outside the geometry tar and off the release entirely:
// the pointer file names each one's sha256 and the committed tree holds the bytes. So
// `fetch-cad-artifacts.mjs` cannot bring one down — there is no object to ask for — and
// `hardware/**` is not in `render.yaml`'s buildFilter, so the commit that moves a scorecard
// deploys nothing. Both halves are deliberate, and without this a verdict reaches the site only
// when some unrelated `web/**` push happens to rebuild the container around it, which is a bar
// describing whatever cut that push landed beside.
//
// THE POINTER FILE IS THE CHANGE DETECTOR, SO A QUIET LOOK COSTS NOTHING. `pointers.sidecars` carries each
// scorecard's sha256 and `adopt` has already fetched the pointer file, so what to ask GitHub for is
// decided against bytes already in hand. That is what makes this affordable: the poll is two
// calls every two minutes against an unauthenticated ceiling of 60/hour, and a scorecard read
// unconditionally would put the look over it.
const SIDECAR_SUFFIX = ".scorecard.json";

function contentsUrl(rel) {
  const encoded = rel.split("/").map(encodeURIComponent).join("/");
  return `https://api.github.com/repos/derekbreden/homesodamachine/contents/${encoded}?ref=main`;
}

async function shaOnDisk(abs) {
  try {
    const h = createHash("sha256");
    await pipeline(createReadStream(abs), h);
    return h.digest("hex");
  } catch {
    return null;                               // absent is a scorecard to carry, not a failure
  }
}

// A POINTER FILE NAMES ITS SCORECARDS BY PATH AND THIS WRITES FILES OFF THAT NAME, so the name is
// checked rather than trusted: a `.scorecard.json` resolving inside the tree, and nothing else.
// The pointer file is the project's own and arrives over HTTPS; this is what keeps a truncated or
// tampered one from choosing where a write lands.
function sidecarPath(rel) {
  if (typeof rel !== "string" || !rel.endsWith(SIDECAR_SUFFIX)) return null;
  const abs = path.resolve(ROOT, rel);
  return abs.startsWith(ROOT + path.sep) ? abs : null;
}

// ONE FETCH PER POINTER MOVE, BECAUSE THE POINTER FILE CAN NAME BYTES MAIN DOES NOT HOLD. `pack.py` cuts against
// the working tree and says so in `unproven`, so a scorecard's pointed-at hash can describe a file
// that was never committed. Carrying what main holds is still right — it is the newest bytes
// anyone can read — but its hash will not settle to the pointer file's, and a disk check alone would
// then ask GitHub for it on every poll forever. This remembers the pointer it acted on, so an
// unproven scorecard costs one call and not one per poll.
const carriedFor = new Map();

async function carryScorecards(pointers) {
  const carried = [];
  const failed = [];
  for (const [rel, want] of Object.entries(pointers.sidecars ?? {})) {
    const abs = sidecarPath(rel);
    if (!abs) { failed.push(`${rel} — not a path this writes`); continue; }
    if (typeof want !== "string") { failed.push(`${rel} — the pointer file names no hash for it`); continue; }
    if (carriedFor.get(rel) === want) continue;
    if ((await shaOnDisk(abs)) === want) { carriedFor.set(rel, want); continue; }
    try {
      const res = await fetch(contentsUrl(rel), {
        headers: { accept: "application/vnd.github+json", "user-agent": "homesodamachine-site" },
      });
      if (!res.ok) throw new Error(`GitHub says ${res.status} ${res.statusText}`);
      const meta = await res.json();
      if (meta.encoding !== "base64" || !meta.content) throw new Error("no inline content");
      const text = Buffer.from(meta.content, "base64").toString("utf-8");
      // Parsed and shape-checked before it is written, the same guard the viewer applies. One
      // status `isScorecard` does not name costs the whole bar, so a sidecar that would draw
      // nothing is one this leaves alone rather than installs.
      if (!isScorecard(JSON.parse(text))) throw new Error("not a scorecard the viewer reads");
      const here = await readFile(abs, "utf-8").catch(() => null);
      if (here !== text) {
        await mkdir(path.dirname(abs), { recursive: true });
        await writeFile(abs, text);
        carried.push(rel);
      }
      carriedFor.set(rel, want);
    } catch (err) {
      failed.push(`${rel} — ${err.message}`);
    }
  }
  return { carried, failed };
}

async function adopt({ broadcast, setRecent, commit, hardwareDir, detect }) {
  const have = await lockOnDisk();
  const pointers = await lockOnMain();
  if (!usable(pointers)) throw new Error("the pointer file on main is not one this can read");

  // AHEAD OF THE BUNDLE GATE, BECAUSE A VERDICT MOVES WITHOUT THE GEOMETRY MOVING. The
  // scorecards sit outside the tar, so `bundle.sha256` is not a function of them: a checker
  // that answers on a tree whose solids did not change leaves the bundle where it was. Read
  // after the gate, that scorecard would wait for the next cut of something else.
  const sidecars = {carried:[],failed:[]};
  carryScorecards(pointers).then(result=>Object.assign(sidecars,result))
    .catch(error=>console.error(`[artifacts-live] scorecards: ${error.message}`));

  const key = createHash("sha256").update(JSON.stringify(pointers)).digest("hex");
  if (failedAdoption?.key !== key) failedAdoption = null;
  if (failedAdoption && Date.now() < failedAdoption.retryAt) {
    return { moved: false, scorecards: sidecars.carried.length, retryAt: failedAdoption.retryAt };
  }

  // A partial startup keeps its current pointer file while some named files are absent.
  // The same publication remains recoverable when its objects become available.
  if (!pointersMoved(have, pointers) && await solidsPresent(pointers)) {
    failedAdoption = null;
    return { moved: false, scorecards: sidecars.carried.length };
  }

  await writeFile(POINTERS, JSON.stringify(pointers, null, 2) + "\n");
  // The fetcher is the authority on bytes — it holds the bundle to the pointer file's sha256 and every
  // member to its own — so this runs it rather than reimplementing that. `cwd` is `web/`, the
  // directory both of its other callers run it from.
  const before = websitePointers(have || {}).solids || {};
  const entries = Object.entries(websitePointers(pointers).solids || {});
  const changed = (await Promise.all(entries.map(async ([name,hash])=>{
    if (before[name] !== hash) return name;
    try { if ((await stat(path.join(ROOT,name))).isFile()) return null; } catch { /* absent */ }
    return name;
  }))).filter(Boolean);
  const selection = changed.length ? [`--only=${changed.join(",")}`] : [];
  let stdout;
  try {
    ({ stdout } = await run(process.execPath,
      [path.join(WEB, "scripts", "fetch-cad-artifacts.mjs"), "--adopt", ...selection],
      { cwd: WEB, maxBuffer: 8 << 20 }));
    await run(process.execPath,
      [path.join(WEB, "scripts", "fetch-cad-artifacts.mjs"), "--adopt", "--check", ...selection],
      { cwd: WEB, maxBuffer: 8 << 20 });
  } catch (err) {
    const delay = Math.min((failedAdoption?.delay ?? POLL_MS / 2) * 2, MAX_RETRY_MS);
    failedAdoption = { key, delay, retryAt: Date.now() + delay };
    if (have) await writeFile(POINTERS, JSON.stringify(have, null, 2) + "\n");
    else await rm(POINTERS, { force: true });
    console.warn(`[artifacts-live] retrying this publication in ${delay / 60_000} minute(s)`);
    throw err;
  }
  failedAdoption = null;
  for (const line of stdout.trim().split("\n")) if (line.trim()) console.log(line);
  await retireSolids(ROOT, have, pointers);

  // The same reading a deploy takes, off the same tables: what is on this disk now against what
  // this site last said. A member the pointer file re-pointed to bytes it already had moves nothing.
  const files = [...new Set(changed.filter(file=>/\.(step|step\.mesh|glb|glb\.mesh)$/.test(file)).map(file=>file.replace(/^hardware\//, "").replace(/\.mesh$/, "")))];
  if (files.length) {
    broadcast({ type: "files-changed", commit, files });
    setRecent({ commit, ts: Date.now(), files });
  }
  return { moved: true, bundle: pointers.bundle.sha256, files: files.length };
}

/** Look once, coalescing with any look already in flight or already deferred. Never throws. */
export function refreshArtifacts(ctx, { force = false } = {}) {
  if (running) {lookAgain=true;return running;}
  const now = Date.now();
  if (!force && now - lastLook < MIN_GAP_MS) {
    if (!pending) {
      pending = new Promise((resolve) => {
        const t = setTimeout(() => {
          pending = null;                        // cleared first, so the next post can defer too
          resolve(refreshArtifacts(ctx));
        }, MIN_GAP_MS - (now - lastLook));
        t.unref?.();                             // a held look does not keep the process alive
      });
    }
    return pending;
  }
  lastLook = now;
  running = adopt(ctx).then(result=>{
    if (result.moved) console.log(`[artifacts-live] adopted ${result.bundle.slice(0,16)} — ${result.files} file(s) pushed`);
    return result;
  }).catch(error=>{
    console.error(`[artifacts-live] ${error.message} — serving the solids already here`);
    return {error:error.message};
  }).finally(()=>{
    running=null;
    if (lookAgain) {lookAgain=false;setTimeout(()=>refreshArtifacts(ctx,{force:true}),0).unref?.();}
  });
  return running;
}

/** The poll, and the endpoint that makes the usual case immediate. */
export function mountArtifactsLive(app, ctx) {
  app.post("/api/artifacts/refresh", (_req, res) => {
    // Answered before the work, because the caller is `publish_now.py` running detached off a
    // commit hook and nothing there should wait on a 65 MB fetch.
    res.json({ looking: true });
    refreshArtifacts(ctx);
  });

  const timer = setInterval(() => {
    refreshArtifacts(ctx);
    Promise.allSettled([carryChecks(),carryBuildTimes()]);
  }, POLL_MS);
  timer.unref();
  return timer;
}
