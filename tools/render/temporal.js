// temporal.js — historical-tree helper for the post-image renderers.
//
// withHistoricalTree(atSpec, callback) checks out the most-recent commit
// on `main` that landed on or before atSpec (or atSpec itself if it's a
// SHA) into a throwaway git worktree, calls callback(worktreeDir, sha),
// then removes the worktree no matter what.
//
// The point: when --at <date> is given to a render tool, the *source
// artifact* (STEP / mermaid file) should be the version that existed on
// that date — but the *tooling* (server.js, viewer-body.html, the render
// pipeline itself) should still be HEAD's. The worktree only supplies the
// historical bytes; the renderer reads them via the live tools.
//
// atSpec can be:
//   - a date string accepted by `git rev-list --before=...` (e.g.
//     "2026-04-15"): we pin to "<date> 23:59:59" so HEAD-of-day commits
//     are included.
//   - a literal SHA: passed straight to `git worktree add` after a
//     rev-parse to confirm it exists.
//
// Cleanup: try/finally always runs `git worktree remove --force`. We also
// register a process-exit hook so a hard crash (uncaught throw, SIGINT)
// still cleans up the worktree directory. Crashes can't talk to git, so
// the exit hook does a best-effort `rm -rf` on the directory and a
// best-effort `git worktree prune` on next call.

import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Look like a SHA? 7-40 hex chars. We resolve it to a real OID below.
function looksLikeSha(s) {
  return /^[0-9a-f]{7,40}$/i.test(String(s || "").trim());
}

// Resolve atSpec to a full commit SHA on the current repo.
function resolveSha(atSpec) {
  const spec = String(atSpec).trim();

  if (looksLikeSha(spec)) {
    // rev-parse to canonicalize and confirm it exists.
    try {
      const out = execFileSync("git", ["rev-parse", spec], {
        cwd: REPO_ROOT,
        encoding: "utf-8",
      }).trim();
      if (!/^[0-9a-f]{40}$/.test(out)) {
        throw new Error(`git rev-parse returned non-SHA: ${out}`);
      }
      return out;
    } catch (e) {
      throw new Error(
        `Could not resolve SHA "${spec}": ${e.message || e}`,
      );
    }
  }

  // Treat as a date. Pin to end-of-day so HEAD-of-day commits are kept.
  const before = `${spec} 23:59:59`;
  let out;
  try {
    out = execFileSync(
      "git",
      ["rev-list", "-1", `--before=${before}`, "main"],
      { cwd: REPO_ROOT, encoding: "utf-8" },
    ).trim();
  } catch (e) {
    throw new Error(
      `git rev-list failed for --before='${before}': ${e.message || e}`,
    );
  }
  if (!out) {
    throw new Error(
      `No commit found on main on or before "${spec}". (atSpec="${atSpec}")`,
    );
  }
  return out;
}

// Remove a worktree, fall back to rm -rf if the git op fails (e.g. the
// directory was already half-removed by a crash).
function removeWorktree(dir) {
  if (!dir) return;
  // First try the polite path.
  const r = spawnSync("git", ["worktree", "remove", "--force", dir], {
    cwd: REPO_ROOT,
    stdio: "ignore",
  });
  // Either way, make sure the directory is gone.
  if (fs.existsSync(dir)) {
    try {
      fs.rmSync(dir, { recursive: true, force: true });
    } catch {
      // ignore — `git worktree prune` next call will tidy up admin state
    }
  }
  // If the polite remove failed (status != 0), try a prune so git's admin
  // dir doesn't grow stale references on each invocation.
  if (r.status !== 0) {
    spawnSync("git", ["worktree", "prune"], {
      cwd: REPO_ROOT,
      stdio: "ignore",
    });
  }
}

// Track active worktrees so an exit/signal handler can clean them up if
// the normal try/finally never reaches its finally (e.g. SIGINT).
const ACTIVE_WORKTREES = new Set();
// Generic temp-dir registry for callers (e.g. the side-by-side renderer's
// staging dir) so they get the same crash-cleanup guarantees without
// duplicating signal-handler bookkeeping.
const ACTIVE_TMPDIRS = new Set();
let HANDLERS_INSTALLED = false;

function installCrashHandlers() {
  if (HANDLERS_INSTALLED) return;
  HANDLERS_INSTALLED = true;

  const onExit = () => {
    for (const dir of ACTIVE_WORKTREES) removeWorktree(dir);
    ACTIVE_WORKTREES.clear();
    for (const dir of ACTIVE_TMPDIRS) {
      try {
        fs.rmSync(dir, { recursive: true, force: true });
      } catch {
        /* best effort */
      }
    }
    ACTIVE_TMPDIRS.clear();
  };

  // Best-effort cleanup on a variety of termination paths. SIGINT/SIGTERM
  // re-exit so the process actually dies after we've cleaned up.
  process.on("exit", onExit);
  for (const sig of ["SIGINT", "SIGTERM", "SIGHUP"]) {
    process.on(sig, () => {
      onExit();
      // Re-raise the default signal handling so we exit with the
      // expected status (128 + signum, per POSIX convention).
      process.kill(process.pid, sig);
    });
  }
  process.on("uncaughtException", (err) => {
    onExit();
    // eslint-disable-next-line no-console
    console.error(err);
    process.exit(1);
  });
}

// Register / unregister a tmp dir with the crash-cleanup hooks. Used by
// callers that create their own tmp dirs alongside withHistoricalTree
// (e.g. the side-by-side renderer's staging dir).
export function registerTempDir(dir) {
  installCrashHandlers();
  ACTIVE_TMPDIRS.add(dir);
}
export function unregisterTempDir(dir) {
  ACTIVE_TMPDIRS.delete(dir);
}

export async function withHistoricalTree(atSpec, callback) {
  if (!atSpec) throw new Error("withHistoricalTree: atSpec is required");

  installCrashHandlers();

  const sha = resolveSha(atSpec);
  const tmpRoot = os.tmpdir();
  const dir = path.join(
    tmpRoot,
    `hsm-render-${process.pid}-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 8)}`,
  );

  // --detach so the worktree doesn't try to track or create a branch.
  // --force not needed since the path is brand-new.
  try {
    execFileSync(
      "git",
      ["worktree", "add", "--detach", dir, sha],
      { cwd: REPO_ROOT, stdio: ["ignore", "ignore", "pipe"] },
    );
  } catch (e) {
    // surface git's stderr if it failed
    const stderr = e.stderr ? String(e.stderr) : "";
    throw new Error(
      `git worktree add failed for ${sha} -> ${dir}: ${e.message}\n${stderr}`,
    );
  }

  ACTIVE_WORKTREES.add(dir);

  try {
    return await callback(dir, sha);
  } finally {
    ACTIVE_WORKTREES.delete(dir);
    removeWorktree(dir);
  }
}

// Convenience: resolve --at to a SHA without checking out anything.
// Useful for log messages from the render tools.
export function resolveAtSpecSha(atSpec) {
  return resolveSha(atSpec);
}

// Boot the historical SHA's server.js in-process and call
// callback({ baseUrl, server, worktreeDir, sha }). This is the right helper
// for site screenshots, where the *renderer* (shell.js, landing.js, blog.js,
// dev-viewer.js, viewer-body.html, glass-animation.js, the icon set, etc.)
// is itself the thing being captured — feeding HEAD's server historical
// hardware/ bytes (the withHistoricalTree pattern) is not enough.
//
// Mechanics:
//   1. withHistoricalTree creates a detached worktree at the historical SHA.
//   2. We symlink HEAD's node_modules into the worktree so we don't reinstall
//      deps. Tradeoff: HEAD's deps must be ABI-compatible with the historical
//      server.js — fine for recent history (days), risky for ancient SHAs.
//   3. We dynamic-import server.js from the worktree path. Node caches ESM
//      by file URL, so two different worktrees get separate caches; the same
//      worktree path imported twice returns the cached module (which is
//      fine — start() is reentrant).
//   4. We call start({ port: 0, dev: false }) to get an ephemeral port.
//      No env vars are passed, so the historical server's database / Firebase
//      paths must degrade gracefully when DATABASE_URL /
//      FIREBASE_SERVICE_ACCOUNT_JSON are absent (current code does; check
//      the historical code path if you point this at deep history).
//   5. We resolve baseUrl = http://localhost:<port> and hand it to callback.
//   6. On callback exit (success OR throw) we close the server, then
//      withHistoricalTree's finally cleans up the worktree.
export async function withHistoricalServer(atSpec, callback) {
  return withHistoricalTree(atSpec, async (worktreeDir, sha) => {
    // Symlink HEAD's node_modules into the worktree. We use 'dir' so node
    // resolves it as a real node_modules tree (no copy, no install).
    const headNm = path.resolve(REPO_ROOT, "node_modules");
    const wtNm = path.join(worktreeDir, "node_modules");
    if (!fs.existsSync(headNm)) {
      throw new Error(
        `withHistoricalServer: HEAD has no node_modules at ${headNm}; ` +
          `run 'npm install' in the repo root first.`,
      );
    }
    // If the worktree somehow already has node_modules (shouldn't — `git
    // worktree add` doesn't carry over .gitignored paths), leave it alone.
    if (!fs.existsSync(wtNm)) {
      fs.symlinkSync(headNm, wtNm, "dir");
    }

    // Dynamic-import server.js from the worktree. Use a file:// URL so the
    // ESM loader resolves it as an absolute path; the historical server's
    // own `import "./lib/..."` lines then resolve relative to that file,
    // so we get the historical lib/ tree.
    const serverPath = path.join(worktreeDir, "server.js");
    if (!fs.existsSync(serverPath)) {
      throw new Error(
        `withHistoricalServer: ${serverPath} does not exist at sha ${sha.slice(0, 7)}.`,
      );
    }
    const serverUrl = pathToFileUrl(serverPath);
    const mod = await import(serverUrl);
    if (typeof mod.start !== "function") {
      throw new Error(
        `withHistoricalServer: server.js at sha ${sha.slice(0, 7)} ` +
          `does not export start().`,
      );
    }

    // Boot on an ephemeral port. No env vars passed — we rely on the server
    // degrading gracefully without DATABASE_URL / Firebase config.
    const { server } = await mod.start({ port: 0, dev: false });
    // app.listen returns the server synchronously; .address() is populated
    // by the time we get back here in practice (Node binds the socket
    // synchronously inside listen()). Defensive: if it isn't, wait one
    // 'listening' tick.
    if (!server.address()) {
      await new Promise((resolve) => server.once("listening", resolve));
    }
    const port = server.address().port;
    const baseUrl = `http://localhost:${port}`;

    try {
      return await callback({ baseUrl, server, worktreeDir, sha });
    } finally {
      await new Promise((resolve) => server.close(() => resolve()));
    }
  });
}

// Tiny pathToFileURL — we keep our own to avoid pulling node:url into the
// public surface of this module beyond the existing import. Same semantics
// as url.pathToFileURL for absolute paths.
function pathToFileUrl(absPath) {
  // path.posix.normalize for the URL portion; on Windows this would need
  // more work, but the renderers only run on macOS/Linux.
  const encoded = absPath
    .split(path.sep)
    .map((seg) => encodeURIComponent(seg))
    .join("/");
  return `file://${encoded.startsWith("/") ? "" : "/"}${encoded}`;
}
