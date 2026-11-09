#!/usr/bin/env node
// find-part resolves browser material searches to their authored models, sources and build targets.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { performance } from "node:perf_hooks";
import { readMaterialCatalog } from "../web/lib/material-catalog.js";
import { readPartCosts } from "../web/lib/part-costs.js";
import { searchCatalog, explodeBom, occurrenceBodies, materialIndex, modelForMaterial } from "../web/contracts/materials.js";
import { stepLocation } from "../web/contracts/step-locations.js";

export const checkoutRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const website = "https://homesodamachine.com/3d";

function jsonFile(file, fallback) {
  try { return JSON.parse(fs.readFileSync(file, "utf8")); }
  catch (error) { if (error.code === "ENOENT") return fallback; throw error; }
}

function sceneNames(root, file) {
  const filename = path.join(root, "hardware", file + ".mesh");
  let handle;
  try {
    handle = fs.openSync(filename, "r");
    const length = Buffer.alloc(4);
    if (fs.readSync(handle, length, 0, 4, 0) !== 4) return [];
    const size = length.readUInt32LE(), header = Buffer.alloc(size);
    if (fs.readSync(handle, header, 0, size, 4) !== size) return [];
    return JSON.parse(header.toString("utf8")).meshes.map((mesh) => mesh.name);
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  } finally { if (handle !== undefined) fs.closeSync(handle); }
}

// Existing generated output declarations supply target names without starting Bazel or guessing crate names.
function outputTargets(root) {
  const targets = new Map();
  let text;
  try { text = fs.readFileSync(path.join(root, "BUILD.bazel"), "utf8"); }
  catch (error) { if (error.code === "ENOENT") return targets; throw error; }
  for (const block of text.matchAll(/^genrule\(\s*\n([\s\S]*?)^\)/gm)) {
    const name = block[1].match(/^\s*name\s*=\s*"([^"]+)"/m)?.[1];
    const outputs = block[1].match(/^\s*outs\s*=\s*\[([\s\S]*?)\]/m)?.[1];
    if (!name || !outputs) continue;
    for (const [, output] of outputs.matchAll(/"([^"]+)"/g)) {
      const at = output.indexOf("hardware/");
      if (at < 0) continue;
      const file = output.slice(at);
      if (!targets.has(file)) targets.set(file, new Set());
      targets.get(file).add("//:" + name);
    }
  }
  return targets;
}

const modelLink = (file, bodies = []) => `${website}#step:${encodeURIComponent(file)}`
  + (bodies.length ? "?find=" + encodeURIComponent(bodies.map((name) => `solid: ${name}`).join("\n")) : "");

export function findParts(query, { root = checkoutRoot, limit = 20 } = {}) {
  const started = performance.now();
  root = path.resolve(root);
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error("limit must be an integer from 1 to 100");
  const hardware = path.join(root, "hardware"), catalog = readMaterialCatalog(hardware);
  try { catalog.costs = readPartCosts(hardware, catalog); } catch { catalog.costs = null; }
  const index = materialIndex(catalog), graph = jsonFile(path.join(root, "tools/bazel/graph.json"), {});
  const targets = outputTargets(root), headers = new Map(), assemblyRows = new Map();
  const roots = (catalog.roots || []).map((id) => index.get(id)).filter(Boolean);
  for (const assembly of roots) assemblyRows.set(assembly.id, explodeBom(catalog, assembly.id));
  const hits = searchCatalog(catalog, query).slice(0, limit).map((hit) => {
    if (!hit.material) return { match: "exact", line: { ...hit.line, kinds: [...hit.line.kinds] } };
    const material = hit.material;
    const models = (material.models || []).map((model) => ({ ...model, ...stepLocation(model.file) }));
    const resolved = modelForMaterial(catalog, material.id);
    if (!models.length && resolved) models.push({ ...resolved, ...stepLocation(resolved.file) });
    const files = new Set(models.flatMap(({ file }) => ["hardware/" + file, "hardware/" + file + ".mesh", "hardware/" + file.replace(/\.step$/, ".step.npz")]));
    const producers = Object.entries(graph).filter(([, row]) => row.writes?.some((file) => files.has(file))).map(([source, row]) => ({
      source,
      targets: [...new Set(row.writes.flatMap((file) => [...targets.get(file) || []]))],
      ...(row.program ? { program: { crate: row.program.crate, name: row.program.name } } : {}),
      inputs: (row.reads || []).filter((file) => file.startsWith("hardware/") && /\.(rs|json)$/.test(file)),
    }));
    const contexts = [];
    for (const assembly of roots) {
      const rows = assemblyRows.get(assembly.id).filter((row) => row.material.id === material.id);
      if (!rows.length) rows.push(...(assembly.relations || [])
        .filter((relation) => relation.material === material.id && relation.bodies?.length)
        .map((relation) => ({ path: [relation] })));
      if (!rows.length) continue;
      const model = modelForMaterial(catalog, assembly.id);
      if (!model) continue;
      const { file } = stepLocation(model.file);
      if (!headers.has(file)) headers.set(file, sceneNames(root, file));
      const names = headers.get(file), bodies = [...new Set(rows.flatMap((row) => occurrenceBodies(catalog, row.path, names)))];
      contexts.push({ material: assembly.id, description: assembly.description, file, bodies,
        bindings: rows.map((row) => row.path), ...(bodies.length ? { url: modelLink(file, bodies) } : {}) });
    }
    return {
      id: material.id, description: material.description, kind: material.kind,
      match: hit.match || "exact", corrections: hit.corrections || [], unmatched: hit.unmatched || [],
      models, documents: material.documents || [], contexts, producers,
      links: { material: `${website}#material:${encodeURIComponent(material.id)}?panel=materials`,
        ...(contexts.find((context) => context.url) ? { model: contexts.find((context) => context.url).url }
          : models[0] ? { model: modelLink(models[0].file, models[0].component ? [models[0].component] : []) } : {}) },
    };
  });
  return { query, match: hits.length ? hits[0].match : "none", hits, elapsed_ms: performance.now() - started };
}

function main(args) {
  const words = [], options = {};
  let json = false;
  while (args.length) {
    const arg = args.shift();
    if (arg === "--json") json = true;
    else if (arg === "--limit") options.limit = Number(args.shift());
    else if (arg === "--root") { options.root = args.shift(); if (!options.root) throw new Error("--root needs a path"); }
    else if (arg === "--help" || arg === "-h") {
      console.log("Usage: node tools/find-part.mjs <description or HSM-id> [--json] [--limit N] [--root PATH]");
      return;
    } else if (arg.startsWith("--")) throw new Error(`unknown option ${arg}`);
    else words.push(arg);
  }
  if (!words.length) throw new Error("supply a description or material ID; use --help for usage");
  const result = findParts(words.join(" "), options);
  if (json) console.log(JSON.stringify(result, null, 2));
  else {
    if (result.match === "suggestion") console.log("No exact matches. Possible matches follow; use an HSM-id to choose one.");
    if (!result.hits.length) console.log("No matches.");
    for (const hit of result.hits) {
      if (hit.line) { console.log(`${hit.line.label} · costed on ${hit.line.holders.map(({ id }) => id).join(", ")}`); continue; }
      console.log(`${hit.id}  ${hit.description}`);
      if (hit.unmatched.length) console.log(`  Unmatched: ${hit.unmatched.join(", ")}`);
      if (hit.corrections.length) console.log(`  Spelling: ${hit.corrections.map(({ from, to }) => `${from} → ${to}`).join(", ")}`);
      if (hit.links.model) console.log(`  ${hit.links.model}`);
      for (const producer of hit.producers) console.log(`  ${producer.source}${producer.targets.length ? " · " + producer.targets.join(" ") : ""}`);
    }
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(`find-part: ${error.message}`); process.exitCode = 1; }
}
