#!/usr/bin/env node
// look-record.js — what drew a look, written down beside it, so the picture can be doubted.
//
// A look is a PNG in a scratch directory with a name and no date on it. The STEP it was drawn
// from is rebuilt many times an hour, and between two builds a frame goes on showing whatever
// the last render found — geometry that looks like a reading and is a memory of one.
//
//   node tools/look-record.js write --step <rel> [--edition id] [--also path]… \
//        --command "<the line that redraws it>" <png>…
//   node tools/look-record.js check <dir>            (0 = current, 1 = stale)
//
// Beside each PNG it leaves `<png>.scene.json`: the line that redraws the picture, and every
// repo file whose text could decide it — the STEP itself, this tool chain, and the viewer
// modules the frame is composed in — each with the hash of its bytes. `check` hashes them
// again. What that costs is reading the files, which is the whole bargain: a picture is
// expensive to draw and cheap to doubt, and the doubting is what runs often.
//
// THE RECORDED LIST IS THE READING. A source added to the render's graph after a look was taken
// is not in that look's record and cannot be — the record is of the render that happened.

import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { EDITION_DIRS } from "../web/lib/editions.js";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SIDECAR = ".scene.json";

// The two entries the drawing is walked from: the composer, which pulls in the server that
// serves the STEP and names the viewer modules it drives; and the page those modules mount in.
const ROOTS = ["tools/render/render-view.js", "web/public/js/viewer/main.js"];
// Read rather than imported, so no walk reaches them.
const LEAVES = ["tools/look.sh", "tools/look-record.js"];

// `from "x"`, `import "x"`, `import("x")`. A specifier that resolves to no file in the repo —
// every bare package name, and anything this catches inside a comment — is dropped below.
const SPEC = /(?:\bfrom\s*|\bimport\s*\(?\s*)["']([^"']+)["']/g;

function hash(file) {
  try {
    return crypto.createHash("blake2b512").update(fs.readFileSync(file)).digest("hex").slice(0, 32);
  } catch {
    return null;
  }
}

// A specifier as a file on disk. Relative resolves against the importing file; absolute is a
// URL the server answers out of web/public, which is how the in-page dynamic imports read.
function resolve(spec, from) {
  let base;
  if (spec.startsWith(".")) base = path.resolve(path.dirname(from), spec);
  else if (spec.startsWith("/")) base = path.join(REPO, "web", "public", spec);
  else return null;
  for (const cand of [base, `${base}.js`, path.join(base, "index.js")]) {
    if (fs.existsSync(cand) && fs.statSync(cand).isFile()) return cand;
  }
  return null;
}

function walk(roots) {
  const seen = new Set();
  const queue = roots.map((r) => path.join(REPO, r)).filter((f) => fs.existsSync(f));
  while (queue.length) {
    const file = queue.pop();
    if (seen.has(file) || file.includes(`${path.sep}node_modules${path.sep}`)) continue;
    seen.add(file);
    const text = fs.readFileSync(file, "utf8");
    for (const m of text.matchAll(SPEC)) {
      const hit = resolve(m[1], file);
      if (hit && !seen.has(hit)) queue.push(hit);
    }
  }
  return seen;
}

function sources({ step, edition, also }) {
  const files = walk(ROOTS);
  for (const rel of [...LEAVES, ...also]) {
    const abs = path.isAbsolute(rel) ? rel : path.join(REPO, rel);
    if (fs.existsSync(abs)) files.add(abs);
  }
  const dir = EDITION_DIRS[edition];
  if (!dir) throw new Error(`unknown edition ${edition} (have ${Object.keys(EDITION_DIRS).join(", ")})`);
  const stepAbs = path.join(REPO, dir, step);
  if (!fs.existsSync(stepAbs)) throw new Error(`no STEP at ${stepAbs}`);
  files.add(stepAbs);

  const out = {};
  for (const abs of [...files].sort()) out[path.relative(REPO, abs)] = hash(abs);
  return out;
}

function write(argv) {
  const opts = { edition: "kitchen", step: null, command: "", also: [] };
  const pngs = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--edition") opts.edition = argv[++i];
    else if (a === "--step") opts.step = argv[++i];
    else if (a === "--command") opts.command = argv[++i];
    else if (a === "--also") opts.also.push(argv[++i]);
    else pngs.push(a);
  }
  if (!opts.step) throw new Error("write: --step is required");
  const map = sources(opts);
  let written = 0;
  for (const png of pngs) {
    if (!fs.existsSync(png)) continue;
    fs.writeFileSync(
      png + SIDECAR,
      JSON.stringify({ command: opts.command, sources: map }, null, 2) + "\n",
    );
    written++;
  }
  console.log(`  recorded  ${written} look(s) against ${Object.keys(map).length} sources`);
}

// "current", "stale" — the verdict on one PNG, and why.
function state(png) {
  const side = png + SIDECAR;
  if (!fs.existsSync(side)) return ["stale", "the picture carries no record of what drew it", ""];
  let held;
  try {
    held = JSON.parse(fs.readFileSync(side, "utf8"));
  } catch {
    return ["stale", "the record beside it will not parse", ""];
  }
  const src = held.sources || {};
  const names = Object.keys(src);
  if (!names.length) return ["stale", "the record names no sources", held.command || ""];
  const moved = names.filter((rel) => hash(path.join(REPO, rel)) !== src[rel]).sort();
  if (moved.length) {
    const head = moved.slice(0, 3).join(", ") + (moved.length > 3 ? ` and ${moved.length - 3} more` : "");
    return ["stale", `${moved.length} of ${names.length} sources moved: ${head}`, held.command || ""];
  }
  return ["current", `current against ${names.length} sources`, held.command || ""];
}

function check(dir) {
  if (!dir || !fs.existsSync(dir)) {
    console.log(`no looks in ${dir} yet`);
    return 0;
  }
  const pngs = fs.readdirSync(dir).filter((f) => f.endsWith(".png")).sort();
  if (!pngs.length) {
    console.log(`no looks in ${dir} yet`);
    return 0;
  }
  const width = Math.max(...pngs.map((p) => p.length));
  let bad = 0;
  for (const p of pngs) {
    const [verdict, detail, command] = state(path.join(dir, p));
    console.log(`  ${p.padEnd(width)}  ${verdict.padEnd(8)} ${detail}`);
    if (verdict !== "current") {
      bad++;
      if (command) console.log(`      run ${command}`);
    }
  }
  console.log(`\n${pngs.length - bad}/${pngs.length} looks carry the picture their sources draw`);
  return bad ? 1 : 0;
}

const [verb, ...rest] = process.argv.slice(2);
try {
  if (verb === "write") write(rest);
  else if (verb === "check") process.exit(check(rest[0]));
  else {
    console.error("usage: node tools/look-record.js write --step <rel> [--edition id] " +
                  "[--also path]… --command <line> <png>…\n" +
                  "       node tools/look-record.js check <dir>");
    process.exit(1);
  }
} catch (err) {
  console.error(err.stack || err.message || err);
  process.exit(1);
}
