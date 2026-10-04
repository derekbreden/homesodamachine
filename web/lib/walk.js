// Shared recursive directory walker. Returns paths relative to rootDir,
// filtered by extension(s). Used by lib/viewer-routes.js for the /api
// endpoints and by lib/push.js for the boot-time hash diff.
//
// Pass a single extension string (".step") or an array ([".step", ".dxf"]);
// the result is an array of forward-slash relative paths. Returns [] if
// rootDir doesn't exist (the dev server points at directories that may
// not yet be populated).
//
// Every walker here skips a retired tree (lib/retired.js), on the same marker
// the build graph reads. What the site browses is therefore what the build can
// rebuild: a file no generator produces is not offered as if it were live.

import path from "path";
import fs from "fs";

import { viewFile, picksFile, innerViewRe } from "../contracts/pcb-out.js";
import { DOC_SIDECAR_SUFFIX, coverPathFor, isPublishedDocument } from "../contracts/documents.js";
import { holdsRetiredMarker } from "./retired.js";

export function walkFiles(rootDir, exts) {
  const extList = Array.isArray(exts) ? exts : [exts];
  const out = [];
  function walk(dir, rel) {
    if (!fs.existsSync(dir)) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    if (holdsRetiredMarker(entries)) return;
    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue; // skip dotfiles (orphaned atomic-write temps, etc.)
      if (entry.name === "node_modules") continue; // never surface dependency artifacts
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

// Documents: the PDFs the site hands over whole. A `.pdf` is one when a
// `<name>.pdf.json` sidecar stands
// beside it (web/contracts/documents.js); the sidecar names it and counts its
// pages, and its cover is the picture the grid shows. Every other `.pdf` under
// the root belongs to whatever wrote it.
//
// The byte count is read here rather than carried in the sidecar: it is a fact
// about the file on this disk, and a sidecar that stated it would be one more
// thing that can disagree with the file it sits next to.
export function walkDocuments(rootDir) {
  const out = [];
  for (const rel of walkFiles(rootDir, DOC_SIDECAR_SUFFIX)) {
    const pdfRel = rel.slice(0, -DOC_SIDECAR_SUFFIX.length) + ".pdf";
    if (!isPublishedDocument(pdfRel)) continue;
    const abs = path.join(rootDir, pdfRel);
    if (!fs.existsSync(abs)) continue;   // a sidecar whose document has not been built
    let meta;
    try {
      meta = JSON.parse(fs.readFileSync(path.join(rootDir, rel), "utf-8"));
    } catch {
      continue;                          // a sidecar that does not parse names nothing
    }
    out.push({
      path: pdfRel,
      title: meta.title || path.basename(pdfRel, ".pdf"),
      subtitle: meta.subtitle || "",
      pages: meta.pages || 0,
      cover: meta.cover ? coverPathFor(pdfRel, meta.cover) : null,
      coverSize: Array.isArray(meta.cover_size) ? meta.cover_size : null,
      bytes: fs.statSync(abs).size,
    });
  }
  return out.sort((a, b) => a.title.localeCompare(b.title));
}

// PCB boards: a board is the tscircuit source named for its own directory —
// `pcb/<dir>/<dir>.tsx`, e.g. pcb/pcba/pcba.tsx — rendered into a sibling `out/`
// by render-board.ts. The name-matches-dir rule is the whole gate: helper sources
// that share the directory (parts.tsx, routing.ts) and scratch/decoy
// boards (_b15.tmp.tsx and friends) are not the board and never appear, so nothing
// can masquerade as a board no matter what got rendered into out/. This is the same
// kind of structural discriminator the other walkers use — drawings by parent-dir
// name, posts by filename pattern — not an out/ allowlist. Returns one object per
// board — `{source, name, dir, top, bottom, overlay, inners, picks}`, the view
// fields being root-relative SVG paths and `inners` the board's inner-plane views
// in stack order — so callers list boards (not raw SVGs) with their views attached.
// Scoped to `<root>/pcb` and skips node_modules so we never recurse the tscircuit
// toolchain's dependency tree. Shared by the /api/pcb route and the deploy-time
// change diff (lib/push.js).
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
    if (holdsRetiredMarker(entries)) return;
    for (const entry of entries) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
        continue;
      }
      if (!entry.name.endsWith(".tsx")) continue;
      const name = entry.name.replace(/\.tsx$/, "");
      // The board is the source named for its directory; helper and scratch .tsx
      // that share the dir are not boards (see header).
      if (name !== path.basename(dir)) continue;
      // A board counts only once its views exist; the overlay is the tell.
      if (!fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) continue;
      const relDir = path.relative(rootDir, dir).split(path.sep).join("/");
      const view = (v) => viewFile(relDir, name, v);
      // Inner copper planes of a multi-layer board: out/<name>.inner<N>.svg,
      // returned in stack order (inner1 nearest the top). Discovered, not
      // assumed — a 2-layer board has none, so the viewer only offers planes
      // that were actually rendered. The name is escaped before it goes into
      // the matcher so a dotted board name can't widen the match.
      const nameRe = innerViewRe(name);
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
      const picksRel = picksFile(relDir, name);
      const hasPicks = fs.existsSync(path.join(dir, "out", `${name}.picks.json`));
      // Solder-mask views (out/<name>.{top,bottom}mask.svg) — the exposed-copper map for
      // each outer face. Present on any freshly-rendered board; discovered, not assumed, so
      // an older render without them just doesn't offer the toggle.
      const maskView = (v) => fs.existsSync(path.join(dir, "out", `${name}.${v}.svg`)) ? view(v) : null;
      boards.push({
        source: `${relDir}/${entry.name}`,
        name,
        dir: relDir,
        top: view("top"),
        bottom: view("bottom"),
        overlay: view("overlay"),
        inners,
        topmask: maskView("topmask"),
        bottommask: maskView("bottommask"),
        picks: hasPicks ? picksRel : null,
      });
    }
  }
  walk(pcbDir);
  return boards.sort((a, b) => a.source.localeCompare(b.source));
}
