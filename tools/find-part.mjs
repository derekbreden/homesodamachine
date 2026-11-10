#!/usr/bin/env node
// find-part resolves browser material searches to their authored models, sources and build targets.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { performance } from "node:perf_hooks";
import { createHash } from "node:crypto";
import { readMaterialCatalog } from "../web/lib/material-catalog.js";
import { readPartCosts } from "../web/lib/part-costs.js";
import { searchCatalog, explodeBom, occurrenceBodies, materialIndex, modelForMaterial } from "../web/contracts/materials.js";
import { stepLocation } from "../web/contracts/step-locations.js";
import { localFeatureCatalog } from "../web/lib/feature-catalog.js";
import { matchFeatures } from "../web/contracts/features.js";
import { instancesInScene, instanceMaterialHash } from "../web/contracts/material-instances.js";

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

// Source context joins exported feature ownership to current compiler inputs and lexical references.
function sourceContext(feature, features, graph, targets, read) {
  const source = feature.source?.match(/^(.*?)(?::(\d+))?$/);
  if (!source) return null;
  const file = source[1], line = Number(source[2] || 1), text = read(file);
  if (text === null) return { file, unavailable: true };
  const lines = text.split("\n");
  const landmarks = [...text.matchAll(/^(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(fn|struct|enum|const|type|static)\s+(\w+)/gm)]
    .map(match => ({ kind: match[1], name: match[2], line: text.slice(0, match.index).split("\n").length }));
  const symbols = new Set(landmarks.map(item => item.name));
  for (const match of text.matchAll(/\bOp::([A-Z]\w*)|\blet\s+(?:mut\s+)?\w+\s*=\s*([A-Z]\w+)\s*\{/g)) symbols.add(match[1] || match[2]);
  const constants = new Set(text.match(/\b[A-Z][A-Z_0-9]{2,}\b/g) || []);
  const occurrences = features.filter(item => item.source?.replace(/:\d+$/, "") === file);
  const producers = [...new Set(occurrences.flatMap(item => item.producers.map(producer => producer.source)))];
  const inputs = [...new Set(producers.flatMap(producer =>
    [...graph[producer]?.program?.sources || [], ...graph[producer]?.reads || []]))].filter(input => input.endsWith(".rs"));
  const references = [], parameters = [];
  for (const input of inputs) {
    if (input === file) continue;
    const content = read(input);
    if (content === null) continue;
    const matches = [];
    for (const [index, code] of content.split("\n").entries()) {
      const names = [...new Set((code.match(/\b[A-Za-z_]\w*\b/g) || []).filter(word => symbols.has(word)))];
      if (names.length) matches.push({ line: index + 1, symbols: names, text: code.trim() });
      const constant = code.match(/^\s*(?:pub(?:\([^)]*\))?\s+)?const\s+(\w+)\b/);
      if (constant && constants.has(constant[1])) parameters.push({ file: input, line: index + 1, text: code.trim() });
    }
    if (matches.length) references.push({ file: input, matches });
  }
  const labels = [...new Set(producers.flatMap(producer =>
    (graph[producer]?.writes || []).flatMap(output => [...targets.get(output) || []])))].sort();
  const consumers = Object.entries(graph).filter(([, row]) =>
    row.program?.sources?.includes(file) || row.reads?.includes(file)).map(([source, row]) => ({
      source, targets: [...new Set((row.writes || []).flatMap(output => [...targets.get(output) || []]))],
    }));
  return {
    scope: "Current source text and compiler-declared inputs. References are lexical leads, not proof of a physical dependency; exported geometry can predate source edits.",
    file, sha256: createHash("sha256").update(text).digest("hex"), exported_anchor: feature.source,
    excerpt: lines.slice(Math.max(0, line - 5), line + 5).map((text, index) => ({ line: Math.max(1, line - 4) + index, text })),
    landmarks, parameters, references, source_consumers: consumers,
    occurrences: occurrences.map(item => ({ key: item.key, file: item.file, source_model: item.source_model, url: item.url })),
    targets: labels,
    build_argv: labels.length ? ["tools/run", "--", "hsm-print-build", "--", ...labels] : null,
    build_scope: "This command selects the exported feature owners. Shared dimension or helper edits also require considering the other source consumers; references do not prove which geometry changes. Installation changes and newly added assembly sources need their assembly producer.",
  };
}

export function findParts(query, { root = checkoutRoot, limit = 20, context = false } = {}) {
  const started = performance.now();
  root = path.resolve(root);
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error("limit must be an integer from 1 to 100");
  const hardware = path.join(root, "hardware"), catalog = readMaterialCatalog(hardware);
  try { catalog.costs = readPartCosts(hardware, catalog); } catch { catalog.costs = null; }
  const index = materialIndex(catalog), graph = jsonFile(path.join(root, "tools/bazel/graph.json"), {});
  const targets = outputTargets(root), headers = new Map(), assemblyRows = new Map();
  const roots = (catalog.roots || []).map((id) => index.get(id)).filter(Boolean);
  const featureCatalog = roots.flatMap(assembly => {
    const model = modelForMaterial(catalog, assembly.id);
    if (!model) return [];
    try { return localFeatureCatalog(hardware, stepLocation(model.file).file).features; }
    catch (error) { if (error.code === "ENOENT") return []; throw error; }
  }).map(feature => ({ ...feature,
    url: `${website}#step:${encodeURIComponent(feature.file)}?find=${encodeURIComponent(`feature: ${feature.key}`)}`,
    producers: Object.entries(graph).filter(([, row]) => row.writes?.includes(feature.source_model)).map(([source, row]) => ({
      source, targets: [...new Set(row.writes.flatMap(file => [...targets.get(file) || []]))],
    })),
  }));
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
      const installed = instancesInScene(catalog, assembly.id, material.id, names);
      contexts.push({ material: assembly.id, description: assembly.description, file, bodies,
        instances: installed.map(instance => ({ ...instance, url: `${website}#${instanceMaterialHash(assembly.id, instance.name)}`,
            features: featureCatalog.filter(feature => feature.file === file && instance.bodies.some(name =>
              feature.body === name || feature.related?.includes(name))) })),
        bindings: rows.map((row) => row.path), ...(bodies.length ? { url: modelLink(file, bodies) } : {}) });
    }
    return {
      id: material.id, description: material.description, kind: material.kind,
      match: hit.match || "exact", corrections: hit.corrections || [], unmatched: hit.unmatched || [],
      models, documents: material.documents || [], contexts, producers,
      links: { material: `${website}#material:${encodeURIComponent(material.id)}?panel=materials`,
        ...(contexts.some(context => context.instances.length) ? { locations: `${website}#material:${encodeURIComponent(material.id)}?tab=location&panel=materials` } : {}),
        ...(contexts.find((context) => context.url) ? { model: contexts.find((context) => context.url).url }
          : models[0] ? { model: modelLink(models[0].file, models[0].component ? [models[0].component] : []) } : {}) },
    };
  });
  const features = matchFeatures(query, featureCatalog).slice(0, limit);
  if (context) {
    const sources = new Map();
    const read = file => {
      if (!sources.has(file)) {
        try { sources.set(file, fs.readFileSync(path.join(root, file), "utf8")); }
        catch (error) { if (error.code !== "ENOENT") throw error; sources.set(file, null); }
      }
      return sources.get(file);
    };
    if (features.length === 1) features[0].context = sourceContext(features[0], featureCatalog, graph, targets, read);
  }
  return { query, match: hits.length ? hits[0].match : features.length ? "feature" : "none", hits, features,
    ...(context && features.length !== 1 ? { context_hint: "Choose one feature key to read its source context." } : {}),
    elapsed_ms: performance.now() - started };
}

function main(args) {
  const words = [], options = {};
  let json = false;
  while (args.length) {
    const arg = args.shift();
    if (arg === "--json") json = true;
    else if (arg === "--context") options.context = true;
    else if (arg === "--limit") options.limit = Number(args.shift());
    else if (arg === "--root") { options.root = args.shift(); if (!options.root) throw new Error("--root needs a path"); }
    else if (arg === "--help" || arg === "-h") {
      console.log("Usage: node tools/find-part.mjs <description, feature or HSM-id> [--context] [--json] [--limit N] [--root PATH]");
      return;
    } else if (arg.startsWith("--")) throw new Error(`unknown option ${arg}`);
    else words.push(arg);
  }
  if (!words.length) throw new Error("supply a description or material ID; use --help for usage");
  const result = findParts(words.join(" "), options);
  if (json) console.log(JSON.stringify(result, null, 2));
  else {
    if (result.match === "suggestion") console.log("No exact matches. Possible matches follow; use an HSM-id to choose one.");
    if (result.context_hint) console.log(result.context_hint);
    if (!result.hits.length && !result.features.length) console.log("No matches.");
    for (const hit of result.hits) {
      if (hit.line) { console.log(`${hit.line.label} · costed on ${hit.line.holders.map(({ id }) => id).join(", ")}`); continue; }
      console.log(`${hit.id}  ${hit.description}`);
      if (hit.unmatched.length) console.log(`  Unmatched: ${hit.unmatched.join(", ")}`);
      if (hit.corrections.length) console.log(`  Spelling: ${hit.corrections.map(({ from, to }) => `${from} → ${to}`).join(", ")}`);
      if (hit.links.model) console.log(`  ${hit.links.model}`);
      for (const producer of hit.producers) console.log(`  ${producer.source}${producer.targets.length ? " · " + producer.targets.join(" ") : ""}`);
    }
    for (const feature of result.features) {
      console.log(`${feature.label} · ${feature.key}\n  ${feature.url}\n  ${feature.source}`);
      for (const producer of feature.producers) console.log(`  ${producer.targets.join(" ")}`);
      if (feature.context) {
        const c = feature.context;
        if (c.unavailable) { console.log(`  Source unavailable: ${c.file}`); continue; }
        console.log(`  Shared source: ${[...new Set(c.occurrences.map(item => item.key))].join(", ")}`);
        if (c.build_argv) console.log(`  Feature build: ${c.build_argv.join(" ")}`);
        for (const item of c.source_consumers) console.log(`  Source consumer: ${item.source} · ${item.targets.join(" ")}`);
        console.log(`  ${c.build_scope}`);
        for (const item of c.landmarks) console.log(`  ${c.file}:${item.line} ${item.kind} ${item.name}`);
        for (const item of c.parameters) console.log(`  ${item.file}:${item.line} ${item.text}`);
        for (const item of c.references) {
          for (const match of item.matches.slice(0, 6)) console.log(`  ${item.file}:${match.line} ${match.text}`);
          if (item.matches.length > 6) console.log(`  ${item.file}: ${item.matches.length - 6} further references in --json`);
        }
        console.log(`  ${c.scope}`);
      }
    }
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(`find-part: ${error.message}`); process.exitCode = 1; }
}
