// Native producer metadata resolves explicit builds and served output identities without scanning source code.
import fs from "node:fs";
import path from "node:path";

export function contentRoots(projectRoot) {
  return [path.join(projectRoot, "hardware")].filter(root => fs.existsSync(root));
}

export function viewerOutput(absPath, hardwareRoot) {
  const relative = path.relative(hardwareRoot, absPath).split(path.sep).join("/");
  if (!relative || relative === ".." || relative.startsWith("../") || path.isAbsolute(relative)) return null;
  if (relative.endsWith(".step.mesh")) return relative.slice(0, -5);
  if (relative.startsWith("assembly/scenes/glb/") && relative.endsWith(".glb.mesh")) return relative.slice(0, -5);
  if (relative.endsWith(".scene.npz")) return relative.slice(0, -10) + ".step";
  if (relative.endsWith(".dxf.json") || relative.endsWith(".step.json") || relative.endsWith(".pdf.json")) return relative.slice(0, -5);
  if (relative.endsWith(".cover.png")) return relative.slice(0, -10) + ".pdf";
  if (/\.(?:step|glb|mmd|dxf|pdf)$/.test(relative)) return relative;
  const copper = relative.match(/^(pcb\/.*)\/out\/([^/]+)\.(?:overlay|top|bottom|schematic)\.(?:svg|png)$/);
  if (copper) {
    const board = `${copper[1]}/${copper[2]}.tsx`;
    if (fs.existsSync(path.join(hardwareRoot, board))) return board;
  }
  return null;
}

function repoPath(projectRoot, file) {
  const relative = path.relative(projectRoot, path.resolve(projectRoot, file));
  if (!relative || relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative))
    throw new Error(`Build source is outside the checkout: ${file}`);
  return relative.split(path.sep).join("/");
}

function retired(projectRoot, source) {
  let directory = path.dirname(path.join(projectRoot, source));
  while (directory !== projectRoot) {
    try { if (fs.statSync(path.join(directory, ".retired")).isFile()) return true; } catch {}
    const parent = path.dirname(directory);
    if (parent === directory) break;
    directory = parent;
  }
  return false;
}

const sourceStem = source => path.posix.parse(source).name.replace(/^_+|_+$/g, "").replaceAll("_", "-");

// Target names match hsm-build-plan's co-writer grouping and shared-stem naming.
function targetName(source, shared) {
  const stem = sourceStem(source);
  return stem === "build" || shared.has(stem) ? `${path.posix.basename(path.posix.dirname(source))}-${stem}` : stem;
}

function strings(value, description) {
  if (!Array.isArray(value) || value.some(item => typeof item !== "string"))
    throw new Error(`${description} must be a list of paths`);
  return value;
}

export function nativeBuildPlan(projectRoot) {
  projectRoot = path.resolve(projectRoot);
  const graphPath = path.join(projectRoot, "tools/hsm/build-plan/graph.json");
  const graph = JSON.parse(fs.readFileSync(graphPath, "utf8"));
  if (!graph || typeof graph !== "object" || Array.isArray(graph)) throw new Error("Native build graph must be an object");
  let classification = {};
  try { classification = JSON.parse(fs.readFileSync(path.join(projectRoot, "tools/hsm/build-plan/inventory.json"), "utf8")); }
  catch (error) { if (error.code !== "ENOENT") throw error; }
  const inert = file => (classification.inert_suffixes || []).some(suffix => file.toLowerCase().endsWith(suffix))
    || (classification.inert_basenames || []).includes(path.posix.basename(file).toLowerCase());
  const entries = [];
  for (const [source, row] of Object.entries(graph).sort(([a], [b]) => a.localeCompare(b))) {
    repoPath(projectRoot, source);
    if (retired(projectRoot, source)) continue;
    const writes = [...new Set([...strings(row.writes || [], `${source} writes`),
      ...strings(classification.implicit_solids?.[source] || [], `${source} implicit outputs`)])].filter(file => !inert(file));
    if (!writes.length) continue;
    if (!row.program || typeof row.program.crate !== "string" || !row.program.crate
        || typeof row.program.name !== "string" || !row.program.name)
      throw new Error(`${source} has no declared native program; refresh its native build-graph entry`);
    if (!fs.existsSync(path.join(projectRoot, source))) throw new Error(`Build-graph source is absent: ${source}`);
    const reads = new Set([...strings(row.reads || [], `${source} reads`), ...strings(row.program.sources || [], `${source} compiler sources`),
      ...strings(row.program.runtime_inputs || [], `${source} runtime sources`), source].filter(file => !inert(file)));
    const rewritten = new Set(strings(row.rewritten || [], `${source} rewritten outputs`));
    entries.push({ source, writes, reads, rewritten, program: row.program });
  }

  const parents = new Map(entries.map(entry => [entry.source, entry.source]));
  const home = new Map();
  function find(source) {
    while (parents.get(source) !== source) source = parents.get(source);
    return source;
  }
  for (const entry of entries) for (const output of entry.writes) {
    const first = home.get(output);
    if (first) {
      const a = find(first), b = find(entry.source);
      if (a !== b) parents.set(a < b ? b : a, a < b ? a : b);
    } else home.set(output, entry.source);
  }
  const cohorts = new Map();
  for (const entry of entries) {
    const key = find(entry.source);
    if (!cohorts.has(key)) cohorts.set(key, []);
    cohorts.get(key).push(entry);
  }
  const seen = new Set(), shared = new Set();
  for (const { source } of entries) {
    const stem = sourceStem(source);
    if (seen.has(stem)) shared.add(stem);
    seen.add(stem);
  }
  const producers = new Map(), bySource = new Map(), byOutput = new Map();
  // This adapter selects target identities; the native planner validates each cohort's executable declaration.
  for (const cohort of cohorts.values()) {
    const sources = cohort.map(entry => entry.source).sort();
    const target = targetName(sources[0], shared);
    if (producers.has(target)) throw new Error(`Native target name is ambiguous: ${target}`);
    const writes = new Set(cohort.flatMap(entry => entry.writes));
    const docs = new Set(cohort.flatMap(entry => [...entry.rewritten]).filter(file => writes.has(file)));
    const solids = new Set([...writes].filter(file => !docs.has(file)));
    const optional = file => docs.has(file) && /\.(?:png|json)$/.test(file);
    const reads = new Set([...cohort.flatMap(entry => [...entry.reads]), ...docs].filter(file => !solids.has(file) && !optional(file)
      && !(file.endsWith(".step.mesh") && solids.has(file.slice(0, -5)))));
    producers.set(target, { target, label: `//:${target}`, sources, reads, writes, dependencies: new Set(), dependents: new Set() });
    for (const source of sources) bySource.set(source, target);
    for (const output of writes) if (!docs.has(output) || optional(output)) byOutput.set(output, target);
  }
  for (const producer of producers.values()) for (const input of producer.reads) {
    const dependency = byOutput.get(input);
    if (dependency && dependency !== producer.target) {
      producer.dependencies.add(dependency);
      producers.get(dependency).dependents.add(producer.target);
    }
  }
  return { projectRoot, producers, bySource, byOutput };
}

export function buildTargetsForSources(requests, projectRoot, plan = nativeBuildPlan(projectRoot)) {
  const selected = new Set();
  for (const request of requests) {
    const target = request.replace(/^\/\/:|^:/, "");
    if (plan.producers.has(target)) { selected.add(target); continue; }
    const source = repoPath(plan.projectRoot, request);
    const direct = plan.bySource.get(source) || plan.byOutput.get(source);
    if (direct) selected.add(direct);
    let found = Boolean(direct);
    for (const producer of plan.producers.values()) if (producer.reads.has(source)) { selected.add(producer.target); found = true; }
    if (!found) throw new Error(`No declared native producer reads or writes ${source}`);
  }
  const pending = [...selected];
  while (pending.length) for (const dependent of plan.producers.get(pending.shift()).dependents) {
    if (!selected.has(dependent)) { selected.add(dependent); pending.push(dependent); }
  }
  return [...selected].sort().map(target => `//:${target}`);
}

export function buildOrder(plan) {
  const visited = new Set(), active = [];
  const result = [];
  function visit(target) {
    if (active.includes(target)) throw new Error(`Native producer cycle: ${[...active, target].join(" -> ")}`);
    if (visited.has(target)) return;
    active.push(target);
    for (const dependency of [...plan.producers.get(target).dependencies].sort()) visit(dependency);
    active.pop(); visited.add(target); result.push(plan.producers.get(target));
  }
  for (const target of [...plan.producers.keys()].sort()) visit(target);
  return result;
}
