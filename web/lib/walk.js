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

// PCB boards: a board is a tscircuit source (`pcb/<dir>/<name>.tsx`) whose
// copper views have been rendered into a sibling `out/` by render-board.ts.
// Returns one object per board — `{source, name, dir, top, bottom, overlay,
// inners, picks}`, the view fields being root-relative SVG paths and `inners`
// the board's inner-plane views in stack order — so callers list boards (not
// raw SVGs) with their views attached. Scoped to `<root>/pcb` and skips
// node_modules so we never recurse the tscircuit toolchain's dependency tree.
// Shared by the /api/pcb route and the deploy-time change diff (lib/push.js).
export function walkPcbBoards(rootDir) {
  const pcbDir = path.join(rootDir, "pcb");
  if (!fs.existsSync(pcbDir)) return [];
  const boards = [];
  function walk(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
        continue;
      }
      if (!entry.name.endsWith(".tsx")) continue;
      const name = entry.name.replace(/\.tsx$/, "");
      // A board counts only once its views exist; the overlay is the tell.
      if (!fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) continue;
      const relDir = path.relative(rootDir, dir).split(path.sep).join("/");
      const view = (v) => `${relDir}/out/${name}.${v}.svg`;
      // Inner copper planes of a multi-layer board: out/<name>.inner<N>.svg,
      // returned in stack order (inner1 nearest the top). Discovered, not
      // assumed — a 2-layer board has none, so the viewer only offers planes
      // that were actually rendered. The name is escaped before it goes into
      // the matcher so a dotted board name can't widen the match.
      const nameRe = new RegExp(
        `^${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\.inner(\\d+)\\.svg$`,
      );
      let inners = [];
      try {
        inners = fs.readdirSync(path.join(dir, "out"))
          .map((f) => ({ f, m: nameRe.exec(f) }))
          .filter((x) => x.m)
          .sort((a, b) => +a.m[1] - +b.m[1])
          .map((x) => `${relDir}/out/${x.f}`);
      } catch {}
      // The pad picker's semantic data (pads + identity), when the distiller
      // has produced it; older boards without it simply have no picker.
      const picksRel = `${relDir}/out/${name}.picks.json`;
      const hasPicks = fs.existsSync(path.join(dir, "out", `${name}.picks.json`));
      boards.push({
        source: `${relDir}/${entry.name}`,
        name,
        dir: relDir,
        top: view("top"),
        bottom: view("bottom"),
        overlay: view("overlay"),
        inners,
        picks: hasPicks ? picksRel : null,
      });
    }
  }
  walk(pcbDir);
  return boards.sort((a, b) => a.source.localeCompare(b.source));
}
