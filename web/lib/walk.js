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
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    if (holdsRetiredMarker(entries)) return;
    for (const entry of entries) {
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

// Assembly instruction cards: the print-ready 4×6 HTML deck under
// `<root>/assembly/cards/` (hardware/assembly/cards/README.md). Each card is a
// self-contained page against a fixed 1800 × 1200 canvas that names its
// subsystem with a body class (`<body class="pv">`) and carries its code, title,
// and deck position in the header band. Underscore-prefixed files (_build.py and
// friends) and the rendered `out/` deck are build machinery, not cards.
//
// The deck's subsystem ORDER is the build order, and it lives in exactly one
// place — the `body.xx { --accent: ... } /* name — note */` block in the deck's
// own style.css. Reading it here means the grid orders and labels subsystems off
// the same declaration the printed cards colour themselves from, so a subsystem
// added to the deck shows up in order without a second edit. Cards whose body
// carries no subsystem class (the cover) sort ahead of everything.
//
// Returns one object per card — `{path, code, title, subsystem, subsystemLabel,
// deckpos, accent}` — already in deck order, so callers group by `subsystem` in
// arrival order rather than re-deriving the sequence.
const CARDS_REL = ["assembly", "cards"];

function readCardStyleSubsystems(cardsDir) {
  const order = [];
  let css;
  try {
    css = fs.readFileSync(path.join(cardsDir, "style.css"), "utf-8");
  } catch {
    return order;
  }
  const re = /body\.([a-z]{2})\s*\{[^}]*--accent:\s*([^;]+);[^}]*\}\s*(?:\/\*\s*([^—*]+?)\s*(?:—|\*\/))?/g;
  let m;
  while ((m = re.exec(css))) {
    const label = (m[3] || m[1]).trim();
    order.push({
      key: m[1],
      label: label.charAt(0).toUpperCase() + label.slice(1),
      accent: m[2].trim(),
    });
  }
  return order;
}

// The named entities the cards actually use in header text. Numeric refs decode
// arithmetically below, so this only has to cover the names.
const HTML_ENTITIES = {
  nbsp: " ", amp: "&", lt: "<", gt: ">", quot: '"', apos: "'",
  mdash: "—", ndash: "–", times: "×", middot: "·", Prime: "″", prime: "′",
  deg: "°", rarr: "→", larr: "←", hellip: "…", plusmn: "±", frac12: "½",
};

// Plain text out of a header fragment: drop tags, decode entities, collapse
// whitespace. The card is rendered by the browser, not here — this is only what
// the grid labels a thumbnail with.
function cardText(s) {
  return s
    .replace(/<[^>]*>/g, " ")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&([a-z][a-z0-9]*);/gi, (m, name) => HTML_ENTITIES[name] ?? m)
    .replace(/\s+/g, " ")
    .trim();
}

// Pull the identity a card prints on itself: the `.code` chip, the title, the
// `.deckpos` line, and the subsystem body class. A field the card doesn't carry
// comes back null and the caller falls back to the filename. The title reads
// from `h1` (every operation card) or `.title` (the cover, which has no header
// band).
function readCardIdentity(abs) {
  let html;
  try {
    html = fs.readFileSync(abs, "utf-8");
  } catch {
    return {};
  }
  const pick = (re) => {
    const m = re.exec(html);
    return m ? cardText(m[1]) || null : null;
  };
  return {
    subsystem: /<body[^>]*\bclass\s*=\s*"([a-z]{2})"/.exec(html)?.[1] || null,
    code: pick(/<div class="code">([\s\S]*?)<\/div>/),
    title: pick(/<h1[^>]*>([\s\S]*?)<\/h1>/) || pick(/<div class="title">([\s\S]*?)<\/div>/),
    deckpos: pick(/<div class="deckpos">\s*<b>([\s\S]*?)<\/b>/),
  };
}

export function walkAssemblyCards(rootDir) {
  const cardsDir = path.join(rootDir, ...CARDS_REL);
  let entries;
  try {
    entries = fs.readdirSync(cardsDir, { withFileTypes: true });
  } catch {
    return [];
  }
  if (holdsRetiredMarker(entries)) return [];

  const subsystems = readCardStyleSubsystems(cardsDir);
  const rank = new Map(subsystems.map((s, i) => [s.key, i]));
  const meta = new Map(subsystems.map((s) => [s.key, s]));

  const cards = [];
  for (const entry of entries) {
    if (!entry.isFile()) continue;
    if (entry.name.startsWith(".") || entry.name.startsWith("_")) continue;
    if (!entry.name.endsWith(".html")) continue;
    const id = readCardIdentity(path.join(cardsDir, entry.name));
    const sub = id.subsystem && meta.has(id.subsystem) ? id.subsystem : null;
    cards.push({
      path: [...CARDS_REL, entry.name].join("/"),
      file: entry.name,
      code: id.code || null,
      title: id.title || entry.name.replace(/\.html$/, "").replace(/-/g, " "),
      deckpos: id.deckpos,
      subsystem: sub,
      // The cover and any other class-less page group under "Deck" and lead.
      subsystemLabel: sub ? meta.get(sub).label : "Deck",
      accent: sub ? meta.get(sub).accent : null,
    });
  }

  // Deck order: class-less pages first, then subsystems in style.css order,
  // then by filename — which is the card code, so PV-01 … PV-14 fall out sorted.
  return cards.sort((a, b) => {
    const ra = a.subsystem ? rank.get(a.subsystem) + 1 : 0;
    const rb = b.subsystem ? rank.get(b.subsystem) + 1 : 0;
    return ra - rb || a.file.localeCompare(b.file);
  });
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
