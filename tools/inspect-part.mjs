#!/usr/bin/env node
// inspect-part draws exported part geometry and measures selected neighbours with a reusable camera.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";
import { performance } from "node:perf_hooks";
import { findParts } from "./find-part.mjs";
import { stepLocation } from "../web/contracts/step-locations.js";

const checkout = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const usage = `Usage: node tools/inspect-part.mjs <material ID or description> --output DIR
  --model FILE        Inspect an existing assembly instead of the material's own model
  --body NAME         Frame this body (repeat for related bodies)
  --feature ID        Frame an authored feature of the selected body
  --against NAME      Measure clearance from the framed body (repeat for neighbours)
  --view NAME         iso, front, back, left, right, top or bottom
  --section X,Y,Z:NX,NY,NZ
  --reuse FILE        Reuse a previous render-job.json camera and presentation
  --root PATH         Select the checkout to inspect

Rendering uses tools/run.py. No geometry build starts. inspection.json names the
exported revision; render-job.json retains the camera for the next source edit.`;

function native(root, args) {
  const answer = spawnSync(process.env.HSM_BIN || "hsm", ["--root", root, ...args], {
    cwd: root, encoding: "utf8", maxBuffer: 16 * 1024 * 1024,
  });
  if (answer.error) throw answer.error;
  let data;
  try { data = JSON.parse(answer.stdout); }
  catch { throw new Error(answer.stderr.trim() || answer.stdout.trim() || "hsm returned no JSON"); }
  if (answer.status || data.ok === false) throw new Error(data.error || answer.stderr.trim() || "hsm query failed");
  return data.result ?? data;
}

function section(value) {
  const rows = value.split(":").map((run) => run.split(",").map(Number));
  if (rows.length !== 2 || rows.some((run) => run.length !== 3 || run.some((n) => !Number.isFinite(n))) || !Math.hypot(...rows[1]))
    throw new Error("--section needs a point and a nonzero normal: X,Y,Z:NX,NY,NZ");
  return { at: rows[0], normal: rows[1] };
}

export function inspectPart(query, options = {}) {
  const started = performance.now();
  const root = path.resolve(options.root || checkout);
  if (!options.output) throw new Error("--output DIR is required");
  const found = findParts(query, { root, limit: 20 });
  const exactId = found.hits.find((hit) => hit.id?.toLowerCase() === query.toLowerCase());
  const featureHit = !options.feature && (found.features?.find(f => f.key === query)
    || (found.match !== "exact" && found.features?.length === 1 ? found.features[0] : null));
  const hit = exactId || (found.match === "exact" && found.hits.length === 1 ? found.hits[0] : null)
    || (featureHit ? { kind: "feature", description: featureHit.label, models: [{ file: featureHit.file }], contexts: [] } : null);
  if (!hit) {
    const candidates = found.hits.map((item) => `${item.id}: ${item.description}`).join("\n");
    throw new Error(`Choose a material ID for this inspection. ${found.match === "suggestion" ? "Search returned suggestions." : "Search is ambiguous or empty."}\n${candidates}`);
  }
  if (!hit.id && !featureHit) throw new Error("A ledger cost line has no model of its own; select one of its material holders with tools/find-part.mjs");
  const own = hit.models?.find((model) => !model.context && (!model.type || model.type === "step"));
  const representation = own || hit.models?.find((model) => !model.type || model.type === "step");
  const chosen = options.model || representation?.file;
  if (!chosen) throw new Error(`${hit.id} has no authored model. Choose an existing assembly with --model and --body.\n${JSON.stringify(hit.links)}`);
  const location = stepLocation(chosen);
  if (!options.model && representation?.component) location.component = representation.component;
  const model = location.file.replace(/^hardware\//, "");
  const binding = hit.contexts?.find((context) => context.file === model);
  const requested = options.bodies?.length ? options.bodies : featureHit ? [featureHit.body] : location.component ? [location.component] : binding?.bodies || [];
  const out = path.resolve(root, options.output);
  fs.mkdirSync(out, { recursive: true });
  const snapshot = path.join(out, "inspection.step.mesh");
  // One payload snapshot keeps unrelated producer updates from changing this inspection mid-draw.
  fs.copyFileSync(path.join(root, "hardware", model + ".mesh"), snapshot);
  try {
    const lookups = (requested.length ? requested : [""]).map((name) => native(root, ["--scene", snapshot, "where", name]));
    const all = { ...lookups[0], data: { parts: [...new Map(lookups.flatMap((lookup) => lookup.data.parts).map((part) => [part.name, part])).values()] } };
    if (lookups.some((lookup) => lookup.payload_sha256 !== all.payload_sha256)) throw new Error("The exported model changed during lookup; repeat the inspection");
    const bodies = requested.length ? [...new Set(requested.flatMap((name) => {
      const exact = all.data.parts.filter((part) => part.name === name);
      const matches = exact.length ? exact : all.data.parts.filter((part) => part.name.startsWith(name + "/"));
      if (!matches.length) throw new Error(`No body ${JSON.stringify(name)} in ${model}; use node tools/find-part.mjs ${JSON.stringify(hit.id)} --json for its authored representations.`);
      return matches.map((part) => part.name);
    }))] : all.data.parts.map((part) => part.name);
    if (!bodies.length) throw new Error(`No exported bodies in ${model}`);
    if (options.against?.length && bodies.length !== 1) throw new Error("--against requires one exact --body in the selected model");

    const featureKey = featureHit?.key || (options.feature ? `${bodies[0]}::${options.feature}` : null);
    const feature = featureKey ? native(root, ["--scene", snapshot, "features", featureKey]).data.features?.[0] : null;
    if (featureKey && !feature) throw new Error(`No exported construction feature ${featureKey}`);
    const measured = (options.against || []).map((other) => native(root, ["--scene", snapshot, "gap", featureKey || bodies[0], other]));
    const previous = options.reuse ? JSON.parse(fs.readFileSync(path.resolve(root, options.reuse), "utf8")) : null;
    const job = {
      ...(previous || { frame: "look", view: options.view || "iso", ortho: true,
        size: "1200x960", ground: false, fog: false, solid: true, annotate: true,
        labels: true, grid: false, context: "drop", title: hit.description }),
      step: model, payload: snapshot, out: path.join(out, "view.png"), only: bodies,
      ...(options.against?.length ? { xray: options.against } : {}),
      ...(options.section ? { section: section(options.section) } : {}),
      ...(feature && !previous ? { target: feature.min_mm.map((n,i)=>(n+feature.max_mm[i])/2),
        span: Math.max(...feature.size_mm,1)*0.7,
        distance: Math.max(...feature.size_mm,1)*3,
        clip: ['x','y','z'].map((axis,i)=>({axis,
          lo:feature.min_mm[i]-Math.max(...feature.size_mm,1)*0.1,
          hi:feature.max_mm[i]+Math.max(...feature.size_mm,1)*0.1})),
        materials: [{names:bodies,color:'#b6b8bf',roughness:0.8,metalness:0}] } : {}),
    };
    if (options.view && previous) throw new Error("Use either --view or --reuse to choose the camera");
    const jobs = path.join(out, "render-input.json");
    fs.writeFileSync(jobs, JSON.stringify([job], null, 2) + "\n");
    const drawing = spawnSync("python3", [path.join(root, "tools/run.py"), "--", process.env.HSM_BIN || "hsm", "--root", root,
      "render", "--jobs", jobs, "--json"], { cwd: root, encoding: "utf8", maxBuffer: 16 * 1024 * 1024 });
    if (drawing.error) throw drawing.error;
    if (drawing.status) throw new Error(drawing.stderr.trim() || drawing.stdout.trim() || "render failed");
    const report = JSON.parse(drawing.stdout)[0];
    if (report.error) throw new Error(report.error);
    if (report.payload_sha256 !== all.payload_sha256) throw new Error("The exported model changed between measurement and drawing; repeat the inspection");
    const camera = report.camera;
    if (!camera?.position || !camera.target || !camera.up) throw new Error("Native renderer returned no reusable camera");
    const direction = camera.position.map((v, i) => v - camera.target[i]);
    const frozen = { ...job, cam: direction, up: camera.up, target: camera.target,
      distance: Math.hypot(...direction), ortho: camera.projection === "orthographic" };
    delete frozen.payload;
    delete frozen.view;
    if (camera.half != null) frozen.span = camera.half;
    fs.writeFileSync(path.join(out, "render-job.json"), JSON.stringify(frozen, null, 2) + "\n");
    const result = {
      purpose: "This inspection binds a local view and neighbour measurements to exported geometry.",
      received_query: query, material: hit, model, feature, payload_sha256: all.payload_sha256,
      source_sha256: all.source_sha256 ?? all.step_sha256 ?? null,
      scope: "Exported geometry; source edits appear after their producer exports new payloads.",
      bodies: all.data.parts.filter((part) => bodies.includes(part.name)), measurements: measured,
      view: report, elapsed_ms: performance.now() - started,
    };
    fs.writeFileSync(path.join(out, "inspection.json"), JSON.stringify(result, null, 2) + "\n");
    fs.rmSync(jobs);
    return { output: out, image: job.out, record: path.join(out, "inspection.json"), camera: path.join(out, "render-job.json"), elapsed_ms: result.elapsed_ms };
  } finally { fs.rmSync(snapshot, { force: true }); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const args = process.argv.slice(2), words = [], options = { bodies: [], against: [] };
    for (let at = 0; at < args.length; at++) {
      const key = args[at];
      if (key === "--help" || key === "-h") { console.log(usage); process.exit(0); }
      if (!key.startsWith("--")) { words.push(key); continue; }
      if (!["--output", "--model", "--body", "--feature", "--against", "--view", "--section", "--reuse", "--root"].includes(key)) throw new Error(`Unknown option ${key}`);
      if (!args[at + 1] || args[at + 1].startsWith("--")) throw new Error(`Missing value for ${key}`);
      const value = args[++at];
      if (key === "--body") options.bodies.push(value);
      else if (key === "--against") options.against.push(value);
      else options[key.slice(2)] = value;
    }
    if (!words.length) throw new Error(usage);
    console.log(JSON.stringify(inspectPart(words.join(" "), options), null, 2));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
