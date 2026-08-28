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
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

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

async function adopt({ broadcast, setRecent, commit, hardwareDir, detect }) {
  const have = await bundleOnDisk();
  const lock = await lockOnMain();
  if (!usable(lock)) throw new Error("the lock on main is not one this can read");
  if (lock.bundle.sha256 === have) return { moved: false };

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
