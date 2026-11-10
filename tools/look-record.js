#!/usr/bin/env node
// look-record.js — what drew a look, written down beside it, so the picture can be doubted.
//
// A look is a PNG in a scratch directory with a name and no date on it. The STEP it was drawn
// from is rebuilt many times an hour, and between two builds a frame goes on showing whatever
// the last render found — geometry that looks like a reading and is a memory of one.
//
//   node tools/look-record.js write --step <rel> [--also path]… \
//        --command "<the line that redraws it>" <png>…
//   node tools/look-record.js check <dir>            (0 = current, 1 = stale)
//
// Beside each PNG it leaves `<png>.scene.json`: the line that redraws the picture, and every
// repo file whose bytes could decide it — the payload drawn, the renderer that drew it, the
// finishes it reads and this tool chain — each with the hash of its bytes. `check` hashes them
// again. What that costs is reading the files, which is the whole bargain: a picture is
// expensive to draw and cheap to doubt, and the doubting is what runs often.
//
// THE RECORDED LIST IS THE READING. A source added to the render's graph after a look was taken
// is not in that look's record and cannot be — the record is of the render that happened.

import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SIDECAR = ".scene.json";

// What `hsm render` draws a look with besides the payload: its sources, shaders included, and
// the finishes it reads. A directory stands for every file under it.
const SOURCES = ["tools/hsm/render/src", "web/public/finishes.json", "tools/look.sh", "tools/look-record.js"];

function hash(file) {
  try {
    return crypto.createHash("blake2b512").update(fs.readFileSync(file)).digest("hex").slice(0, 32);
  } catch {
    return null;
  }
}

// Every file at or under `abs`.
function under(abs) {
  if (!fs.existsSync(abs)) return [];
  if (!fs.statSync(abs).isDirectory()) return [abs];
  return fs.readdirSync(abs).flatMap((name) => under(path.join(abs, name)));
}

function sources({ step, also }) {
  const files = new Set();
  for (const rel of [...SOURCES, ...also]) {
    for (const abs of under(path.isAbsolute(rel) ? rel : path.join(REPO, rel))) files.add(abs);
  }
  const payload = path.join(REPO, "hardware", `${step}.mesh`);
  if (!fs.existsSync(payload)) throw new Error(`no payload at ${payload}`);
  files.add(payload);

  const out = {};
  for (const abs of [...files].sort()) out[path.relative(REPO, abs)] = hash(abs);
  return out;
}

function write(argv) {
  const opts = { step: null, command: "", also: [] };
  const pngs = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--step") opts.step = argv[++i];
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

// A native neighborhood supplies the frame and ranked legend without rebuilding a CAD recipe.
export function neighborhoodPlan(reply) {
  if (reply.ok === false) throw new Error(reply.error || "neighborhood query failed");
  const result = reply.result ?? reply;
  const data = result.data;
  const subject = data?.subject;
  const radius = data?.within_mm;
  if (!subject?.name || ![subject.min_mm, subject.max_mm].every(row =>
    Array.isArray(row) && row.length === 3 && row.every(Number.isFinite)) ||
    !Number.isFinite(radius) || radius < 0 || !Array.isArray(data.neighbors) || !Array.isArray(data.unresolved))
    throw new Error("near-plan needs a native hsm around response");
  const neighbors = data.neighbors;
  const unresolved = data.unresolved;
  const ranked = [...new Set([...neighbors, ...unresolved].map(row => row.name))].join(",");
  const dimensions = subject.min_mm.map((value, i) => subject.max_mm[i] - value);
  const target = subject.min_mm.map((value, i) => (value + subject.max_mm[i]) / 2).join(",");
  let legend = neighbors.slice(0, 6).map(row => `${row.name} ${row.distance_mm.toFixed(2)}`).join("  ");
  if (neighbors.length > 6) legend += `  +${neighbors.length - 6} more`;
  if (unresolved.length) legend += `${legend ? "  " : ""}${unresolved.length} unresolved`;
  legend ||= "nothing";
  const lines = neighbors.map(row => `${row.distance_mm.toFixed(3)}  ${row.name}  ${row.source ?? ""}`);
  lines.push(...unresolved.map(row => `unknown  ${row.name}  ${row.error}`));
  if (!lines.length) lines.push(`nothing within ${radius} mm`);
  return [String(Math.max(...dimensions) / 2 * 1.15 + radius), target, subject.name, ranked,
    `within ${radius} mm: ${legend}`, lines.join("\n")];
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [verb, ...rest] = process.argv.slice(2);
  try {
    if (verb === "write") write(rest);
    else if (verb === "check") process.exit(check(rest[0]));
    else if (verb === "near-plan") {
      for (const value of neighborhoodPlan(JSON.parse(fs.readFileSync(0, "utf8"))))
        process.stdout.write(`${value}\0`);
    } else {
      console.error("usage: node tools/look-record.js write --step <rel> " +
                    "[--also path]… --command <line> <png>…\n" +
                    "       node tools/look-record.js check <dir>\n" +
                    "       node tools/look-record.js near-plan < native-neighborhood.json");
      process.exit(1);
    }
  } catch (err) {
    console.error(err.stack || err.message || err);
    process.exit(1);
  }
}
