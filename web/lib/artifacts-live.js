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

// Two minutes is 30 calls an hour against an unauthenticated ceiling of 60, which leaves room
// for the posts and for anything else on this address asking GitHub the same way.
const POLL_MS = 120_000;

// The floor under `/api/artifacts/refresh`, so the endpoint cannot be used to make this container
// fetch 65 MB in a loop. Several sessions publishing at once land inside one of these.
const MIN_GAP_MS = 10_000;

let running = null;
let lastLook = 0;

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

/** Look once, coalescing with any look already in flight. Never throws. */
export function refreshArtifacts(ctx, { force = false } = {}) {
  if (running) return running;
  const now = Date.now();
  if (!force && now - lastLook < MIN_GAP_MS) return Promise.resolve({ skipped: true });
  lastLook = now;
  running = adopt(ctx)
    .then((r) => {
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
