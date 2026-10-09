#!/usr/bin/env node
// Consistency audit of the collection: node tools/audit.mjs
// Reports scenes with missing metadata, dangling ids and links, missing thumbnails, idea files without scenes.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const study = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const p = (...a) => path.join(study, ...a);
const ex = f => fs.existsSync(p(f));
const problems = [];
const note = (id, msg) => problems.push(`${id}: ${msg}`);

const ids = fs.readdirSync(p("scenes")).filter(d => ex(`scenes/${d}/index.html`)).sort();
const set = new Set(ids);
const metas = {};
for (const id of ids) {
  const html = fs.readFileSync(p("scenes", id, "index.html"), "utf8");
  const m = html.match(/<script[^>]*id=["']scene-meta["'][^>]*>([\s\S]*?)<\/script>/);
  if (!m) { note(id, "no scene-meta block"); continue; }
  let meta;
  try { meta = JSON.parse(m[1]); } catch (e) { note(id, `scene-meta is not valid JSON (${e.message})`); continue; }
  metas[id] = meta;
  if (meta.id !== id) note(id, `meta.id is "${meta.id}"`);
  for (const k of ["title", "by", "origin", "summary", "status"]) if (!meta[k]) note(id, `meta.${k} missing`);
  if (!meta.how) note(id, "meta.how missing");
  else for (const k of ["motion", "load", "reference", "observe", "use"]) if (!meta.how[k]) note(id, `meta.how.${k} missing`);
  if (!meta.software) note(id, "meta.software missing");
  for (const b of [...(meta.branchOf || []), ...(meta.combines || [])]) if (!set.has(b)) note(id, `branchOf/combines names "${b}", which is not a scene`);
  for (const f of [...(meta.notes || []), ...(meta.sources || [])]) {
    const target = path.resolve(p("scenes", id), f);
    if (!fs.existsSync(target)) note(id, `linked file missing: ${f}`);
  }
  if (!ex(`thumbs/${id}.png`)) note(id, "no thumbnail");
  if (!/id=["']?(?:sec|panel)|sections\s*:/.test(html) && !/sections/.test(html)) note(id, "no explanatory sections found");
  const by = meta.by;
  if (by && !ex(`explorers/${by}`) && by !== "coordinator") note(id, `explorer "${by}" has no directory`);
}

// idea files vs scenes
const explorers = fs.readdirSync(p("explorers")).filter(d => fs.statSync(p("explorers", d)).isDirectory());
for (const e of explorers) {
  if (!ex(`explorers/${e}/index.md`)) note(`explorers/${e}`, "no index.md");
  if (!ex(`sourcing/${e}.md`)) note(`sourcing/${e}.md`, "missing");
  const dir = p("explorers", e, "ideas");
  if (!fs.existsSync(dir)) { note(`explorers/${e}`, "no ideas/ directory"); continue; }
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith(".md"))) {
    const base = f.slice(0, -3);
    if (!set.has(base)) note(`explorers/${e}/ideas/${f}`, "idea file has no scene of its own");
  }
}
// scenes without an idea file
for (const id of ids) {
  const by = (metas[id] || {}).by;
  if (!by || by === "coordinator") continue;
  const dir = p("explorers", by, "ideas");
  const has = fs.existsSync(dir) && fs.readdirSync(dir).some(f => f.startsWith(id));
  if (!has) note(id, "no idea file in explorers/" + by + "/ideas/");
}
// exchange files
const exDir = p("exchange");
console.log(`${ids.length} scenes, ${fs.existsSync(exDir) ? fs.readdirSync(exDir).length : 0} exchange files, ${explorers.length} explorers`);
if (!problems.length) console.log("no problems");
else { console.log(`${problems.length} findings:`); for (const x of problems) console.log("  " + x); }
