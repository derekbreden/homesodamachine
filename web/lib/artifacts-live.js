// New geometry onto an open page, without a deploy.
//
// The site deploys on a push, and the lock used to be one of the paths that triggered it — so a
// cut reached the browser by rebuilding the container around it. That is 40 of the 55 deploying
// commits on a working day, each a `npm ci`, a 65 MB fetch and a restart, and they do not run in
// parallel. Four landing inside two minutes puts the fourth eight minutes out.
//
// The lock is not code. This adopts it in place: read the lock GitHub holds, and if it names a
// bundle this disk does not have, run `fetch-cad-artifacts.mjs --adopt` to bring the members
// down, then say what moved on the same `files-changed` frame a deploy sends. The viewer's
// listener (public/js/viewer/live.js) reloads an open model in place, keeping the camera.
//
// THE API AND NOT `raw`, BECAUSE `raw` IS FIVE MINUTES STALE. `raw.githubusercontent.com` serves
// `cache-control: max-age=300`, and measured against a commit seconds old it returns the previous
// bytes through a cache-buster and a `no-cache` request header alike. `/repos/:o/:r/contents/:p`
// answers with the commit that is actually on main, inlines this 19 KB file as base64, and costs
// one call. Unauthenticated is 60/hour against a poll every 2 minutes.
//
// TOLD, AND ALSO ASKED. `publish_now.py` posts to `/api/artifacts/refresh` the moment it pins, so
// the usual case is seconds. The poll is what makes the removal from `buildFilter` safe: if the
// post never arrives — a laptop offline, an endpoint renamed — geometry is late by a poll rather
// than absent until someone pushes code. The post carries no lock and no trust; it says "look
// now", and what is read is still GitHub's.
//
// A COLD BOOT IS STILL THE BUILD'S JOB. `fetch-cad-artifacts.mjs` runs in `buildCommand` and
// `prestart` as before, so a container starts holding what its own clone's lock named. This only
// carries it forward from there.
//
// IT REPORTS AND HOLDS NOTHING. Every failure here leaves the container serving the solids it
// already has, which is the previous cut. CLAUDE.md, "Nothing withholds".

import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import { isScorecard } from "../contracts/scorecard-sidecar.js";

const run = promisify(execFile);

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WEB = path.resolve(HERE, "..");
const ROOT = path.resolve(WEB, "..");
const LOCK = path.join(ROOT, "hardware", "cad-artifacts.lock.json");

const LOCK_URL =
  "https://api.github.com/repos/derekbreden/homesodamachine/contents/hardware/cad-artifacts.lock.json?ref=main";

// THE VERDICT IS NOT CODE EITHER. `checks.json` sits under `web/public/`, which `render.yaml`
// deploys on, so every reading `checks_now.py` pinned rebuilt the container around it — 24 of
// the 24 deploying commits in the six hours this was measured, each a `npm ci` and a restart,
// none of them in parallel. A verdict twenty minutes behind describes a tree that has moved.
// `render.yaml` holds it out of the filter and this carries it, on the same look as the lock.
const CHECKS = path.join(WEB, "public", "checks.json");
const CHECKS_URL =
  "https://api.github.com/repos/derekbreden/homesodamachine/contents/web/public/checks.json?ref=main";

// Two minutes is 30 calls an hour against an unauthenticated ceiling of 60, which leaves room
// for the posts and for anything else on this address asking GitHub the same way.
const POLL_MS = 120_000;

// The floor under `/api/artifacts/refresh`, so the endpoint cannot be used to make this container
// fetch 65 MB in a loop. Several sessions publishing at once land inside one of these, and
// `.githooks/post-commit` fires `publish_now.py` on every commit, so back-to-back cuts are the
// resting state rather than a burst.
const MIN_GAP_MS = 10_000;

let running = null;
let lastLook = 0;
// THE LOOK THE FLOOR TURNS AWAY IS HELD, NOT DROPPED. A cut whose post lands inside the gap of
// the one before it is the second session's geometry, and dropping the post leaves it for the
// 120s poll — twelve times the floor it was refused for. One deferred look at a time carries it
// instead: the floor is still one look per `MIN_GAP_MS`, and what a refused post now costs is
// the remainder of that gap.
let pending = null;

async function bundleOnDisk() {
  try {
    return JSON.parse(await readFile(LOCK, "utf-8")).bundle?.sha256 ?? null;
  } catch {
    return null;
  }
}

async function lockOnMain() {
  const res = await fetch(LOCK_URL, {
    headers: { accept: "application/vnd.github+json", "user-agent": "homesodamachine-site" },
  });
  if (!res.ok) throw new Error(`GitHub says ${res.status} ${res.statusText}`);
  const meta = await res.json();
  if (meta.encoding !== "base64" || !meta.content) throw new Error("no inline content");
  return JSON.parse(Buffer.from(meta.content, "base64").toString("utf-8"));
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

// The lock's own shape, before it is written anywhere. A truncated or half-published lock that
// reached main is a lock this refuses rather than one it serves.
function usable(lock) {
  return Boolean(
    lock &&
    typeof lock.bundle?.sha256 === "string" &&
    lock.release?.url?.startsWith("https://github.com/derekbreden/homesodamachine/releases/") &&
    lock.solids &&
    Object.keys(lock.solids).length,
  );
}

// THE SCORECARD IS COMMITTED DATA UNDER A PATH NOTHING DEPLOYS ON, WHICH IS WHY IT IS CARRIED
// HERE. `pack.py` keeps the scorecards outside the geometry tar and off the release entirely:
// the lock names each one's sha256 and the committed tree holds the bytes. So
// `fetch-cad-artifacts.mjs` cannot bring one down — there is no object to ask for — and
// `hardware/**` is not in `render.yaml`'s buildFilter, so the commit that moves a scorecard
// deploys nothing. Both halves are deliberate, and without this a verdict reaches the site only
// when some unrelated `web/**` push happens to rebuild the container around it, which is a bar
// describing whatever cut that push landed beside.
//
// THE LOCK IS THE CHANGE DETECTOR, SO A QUIET LOOK COSTS NOTHING. `lock.sidecars` carries each
// scorecard's sha256 and `adopt` has already fetched the lock, so what to ask GitHub for is
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

// A LOCK NAMES ITS SCORECARDS BY PATH AND THIS WRITES FILES OFF THAT NAME, so the name is
// checked rather than trusted: a `.scorecard.json` resolving inside the tree, and nothing else.
// The lock is the project's own and arrives over HTTPS; this is what keeps a truncated or
// tampered one from choosing where a write lands.
function sidecarPath(rel) {
  if (typeof rel !== "string" || !rel.endsWith(SIDECAR_SUFFIX)) return null;
  const abs = path.resolve(ROOT, rel);
  return abs.startsWith(ROOT + path.sep) ? abs : null;
}

// ONE FETCH PER PIN, BECAUSE THE LOCK CAN NAME BYTES MAIN DOES NOT HOLD. `pack.py` cuts against
// the working tree and says so in `unproven`, so a scorecard's locked hash can describe a file
// that was never committed. Carrying what main holds is still right — it is the newest bytes
// anyone can read — but its hash will not settle to the lock's, and a disk check alone would
// then ask GitHub for it on every poll forever. This remembers the pin it acted on, so an
// unproven scorecard costs one call and not one per poll.
const carriedFor = new Map();

async function carryScorecards(lock) {
  const carried = [];
  const failed = [];
  for (const [rel, want] of Object.entries(lock.sidecars ?? {})) {
    const abs = sidecarPath(rel);
    if (!abs) { failed.push(`${rel} — not a path this writes`); continue; }
    if (typeof want !== "string") { failed.push(`${rel} — the lock names no hash for it`); continue; }
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
  const have = await bundleOnDisk();
  const lock = await lockOnMain();
  if (!usable(lock)) throw new Error("the lock on main is not one this can read");

  // AHEAD OF THE BUNDLE GATE, BECAUSE A VERDICT MOVES WITHOUT THE GEOMETRY MOVING. The
  // scorecards sit outside the tar, so `bundle.sha256` is not a function of them: a checker
  // that answers on a tree whose solids did not change leaves the bundle where it was. Read
  // after the gate, that scorecard would wait for the next cut of something else.
  const sidecars = await carryScorecards(lock);
  if (sidecars.carried.length) {
    console.log(`[artifacts-live] carried ${sidecars.carried.length} scorecard(s) — `
      + sidecars.carried.join(", "));
  }
  for (const line of sidecars.failed) {
    console.error(`[artifacts-live] ${line} — the bar is the one already here`);
  }

  if (lock.bundle.sha256 === have) return { moved: false, scorecards: sidecars.carried.length };

  await writeFile(LOCK, JSON.stringify(lock, null, 2) + "\n");
  // The fetcher is the authority on bytes — it holds the bundle to the lock's sha256 and every
  // member to its own — so this runs it rather than reimplementing that. `cwd` is `web/`, the
  // directory both of its other callers run it from.
  const { stdout } = await run(process.execPath,
    [path.join(WEB, "scripts", "fetch-cad-artifacts.mjs"), "--adopt"],
    { cwd: WEB, maxBuffer: 8 << 20 });
  for (const line of stdout.trim().split("\n")) if (line.trim()) console.log(line);

  // The same reading a deploy takes, off the same tables: what is on this disk now against what
  // this site last said. A member the lock re-pinned to bytes it already had moves nothing.
  const files = (await Promise.all(detect.map((d) => d(hardwareDir)))).flat();
  if (files.length) {
    broadcast({ type: "files-changed", commit, files });
    setRecent({ commit, ts: Date.now(), files });
  }
  return { moved: true, bundle: lock.bundle.sha256, files: files.length };
}

/** Look once, coalescing with any look already in flight or already deferred. Never throws. */
export function refreshArtifacts(ctx, { force = false } = {}) {
  if (running) return running;
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
  running = Promise.allSettled([adopt(ctx), carryChecks()])
    .then(([geometry, checks]) => {
      if (checks.status === "fulfilled" && checks.value.moved) {
        console.log(`[artifacts-live] carried the verdict — `
          + `${checks.value.green ? "green" : "RED"}, ${checks.value.checks} check(s)`);
      } else if (checks.status === "rejected") {
        console.error(`[artifacts-live] ${checks.reason.message} — the band is the one already here`);
      }
      if (geometry.status === "rejected") throw geometry.reason;
      const r = geometry.value;
      if (r.moved) {
        console.log(`[artifacts-live] adopted ${r.bundle.slice(0, 16)} — ${r.files} file(s) pushed`);
      }
      return r;
    })
    .catch((err) => {
      console.error(`[artifacts-live] ${err.message} — serving the solids already here`);
      return { error: err.message };
    })
    .finally(() => { running = null; });
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

  const timer = setInterval(() => refreshArtifacts(ctx), POLL_MS);
  timer.unref();
  return timer;
}
