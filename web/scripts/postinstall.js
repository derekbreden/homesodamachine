// Postinstall: create a symlink that points the marketing/render tools at
// web/node_modules.
//
// Background: the render tools at tools/render/ (render-step.js,
// render-mermaid.js, render-drawing.js, screenshot-site.js, etc.) import
// puppeteer + sharp + marked + firebase-admin from web/node_modules. Before
// the 2026-05-11 web/ reorganization, node_modules was at the repo root and
// the tools resolved into it naturally. After the move, Node's module
// resolution can't find them — `tools/render` walks up through `tools/` and
// then the repo root, never visiting `web/`.
//
// The cleanest fix that doesn't relocate the tools or duplicate dependency
// installs is a symlink at `tools/render/node_modules` pointing at
// `web/node_modules`. Created here so every `npm install` keeps it in sync,
// no manual setup step. Best-effort — if the symlink can't be created (read-
// only volume, sandboxed CI, etc.) we log and continue rather than fail the
// install, since the web app itself doesn't depend on it.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// web/scripts → web → repo-root
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const WEB_NM = path.resolve(REPO_ROOT, "web", "node_modules");
const LINK = path.resolve(REPO_ROOT, "tools", "render", "node_modules");

if (!fs.existsSync(WEB_NM)) {
  // npm install hasn't finished writing node_modules yet — shouldn't
  // happen at this point but bail rather than create a broken link.
  console.warn(`postinstall: ${WEB_NM} does not exist; skipping render-tools symlink.`);
  process.exit(0);
}

if (!fs.existsSync(path.dirname(LINK))) {
  console.warn(`postinstall: ${path.dirname(LINK)} does not exist; skipping render-tools symlink.`);
  process.exit(0);
}

// If a symlink already exists at LINK, make sure it points where we want.
// `lstat` (not `stat`) so we see the symlink itself rather than its target.
let needsCreate = true;
try {
  const st = fs.lstatSync(LINK);
  if (st.isSymbolicLink()) {
    const cur = fs.readlinkSync(LINK);
    // The link target can be relative ("../../web/node_modules") or
    // absolute. Resolve relative to the link's parent to compare.
    const resolved = path.resolve(path.dirname(LINK), cur);
    if (resolved === WEB_NM) {
      needsCreate = false;
    } else {
      // Wrong target — remove and recreate.
      fs.unlinkSync(LINK);
    }
  } else {
    // Something non-symlink lives at LINK (maybe a stale node_modules
    // directory left over from a manual install). Leave it alone — don't
    // delete real directories.
    console.warn(`postinstall: ${LINK} exists but is not a symlink; leaving it alone.`);
    process.exit(0);
  }
} catch (e) {
  if (e.code !== "ENOENT") {
    console.warn(`postinstall: ${LINK} lstat failed: ${e.message}; skipping.`);
    process.exit(0);
  }
  // ENOENT means the link doesn't exist yet — fall through and create it.
}

if (needsCreate) {
  // Use a relative target so the symlink stays valid across worktrees /
  // moves of the repo.
  const relTarget = path.relative(path.dirname(LINK), WEB_NM);
  try {
    fs.symlinkSync(relTarget, LINK, "dir");
    console.log(`postinstall: created ${path.relative(REPO_ROOT, LINK)} -> ${relTarget}`);
  } catch (e) {
    console.warn(`postinstall: could not create ${LINK}: ${e.message}`);
  }
}
