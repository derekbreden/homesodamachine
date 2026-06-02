// Shared recursive directory walker. Returns paths relative to rootDir,
// filtered by extension(s). Used by lib/viewer-routes.js for the /api
// endpoints and by lib/push.js for the boot-time hash diff.
//
// Pass a single extension string (".step") or an array ([".step", ".dxf"]);
// the result is an array of forward-slash relative paths. Returns [] if
// rootDir doesn't exist (the dev server points at directories that may
// not yet be populated).

import path from "path";
import fs from "fs";

export function walkFiles(rootDir, exts) {
  const extList = Array.isArray(exts) ? exts : [exts];
  const out = [];
  function walk(dir, rel) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith(".")) continue; // skip dotfiles (orphaned atomic-write temps, etc.)
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full, path.join(rel, entry.name));
      else if (extList.some((e) => entry.name.endsWith(e))) {
        out.push(path.join(rel, entry.name));
      }
    }
  }
  walk(rootDir, "");
  return out;
}

// Variant that only returns files inside a directory whose basename is
// `parentDirName`. Used for line-art drawings: line_art.py writes its
// SVGs into per-part `drawings/` folders (e.g.
// hardware/printed-parts/enclosure/drawings/enclosure-iso.svg), and the
// walker filters out any other .svg files that happen to live elsewhere
// in the tree (logos, hand-drawn diagrams, etc).
export function walkFilesUnderDir(rootDir, exts, parentDirName) {
  const extList = Array.isArray(exts) ? exts : [exts];
  const out = [];
  function walk(dir, rel, insideParent) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith(".")) continue; // skip dotfiles (orphaned atomic-write temps, etc.)
      const full = path.join(dir, entry.name);
      const childInside = insideParent || entry.name === parentDirName;
      if (entry.isDirectory()) {
        walk(full, path.join(rel, entry.name), childInside);
      } else if (insideParent && extList.some((e) => entry.name.endsWith(e))) {
        out.push(path.join(rel, entry.name));
      }
    }
  }
  walk(rootDir, "", false);
  return out;
}
