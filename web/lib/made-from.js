// WHAT A MODEL IS REBUILT WITH, AND WHAT IT IS USED IN — read off the build's own record for the
// viewer's Related list (web/public/js/viewer/related-nav.js).
//
// `tools/hsm/build-plan/graph.json` records native producers' inputs and outputs. Requested builds
// use those dependencies; saving a source starts no build. The Related list groups that
// record, which can also include shared modules compiled into the producer's program.
//
// A file the record names is shown as the part it belongs to: another step's output is the model
// that step makes, a source in another part's folder is that part, a recipe module compiled into
// a subsystem's program is the part whose step bears its name, and anything else is the code it
// is, by the crate or folder that holds it.
import fs from "fs";
import path from "path";

// Plain names for the code the build compiles steps from. Any other crate is a subsystem's: a
// `-data` crate holds its recipes, and the rest its part programs.
const CODE_NAMES = {
  kernel: "Kernel",
  geometry: "Geometry",
  "model-export": "Model export",
  documents: "Document code",
  render: "Render code",
  guides: "Guide code",
  pages: "Page code",
  "assembly-docs": "Wiring",
  ledger: "Ledger",
  "shared-data": "Shared data",
  "build-data": "Bookkeeping",
  "build-plan": "Build plan",
  "run-slots": "Runner",
  "run-native": "Runner",
  vendor: "Vendored libraries",
  engine: "Engine",
};

// The same, for code outside tools/hsm, by its first two path segments.
const TOOL_NAMES = {
  "tools/run": "Runner",
  "tools/docgen": "Document code",
  "tools/install-guide": "Guide code",
  "web/public": "Website code",
  "brand/mark.svg": "Brand mark",
};

let cached = null;

function load(graphPath) {
  const mtimeMs = fs.statSync(graphPath).mtimeMs;
  if (cached?.graphPath === graphPath && cached.mtimeMs === mtimeMs) return cached;
  const graph = JSON.parse(fs.readFileSync(graphPath, "utf8"));
  const writer = new Map();
  const stepsIn = new Map();
  const byStem = new Map();
  for (const [step, entry] of Object.entries(graph)) {
    for (const file of entry.writes || []) writer.set(file, step);
    const folder = path.posix.dirname(step);
    if (!stepsIn.has(folder)) stepsIn.set(folder, []);
    stepsIn.get(folder).push(step);
    byStem.set(path.posix.basename(step).replace(/\.rs$/, ""), step);
  }
  const index = { graphPath, mtimeMs, graph, writer, stepsIn, byStem, groups: new Map(), users: new Map() };
  // Who takes from each part's folder, the reverse of every step's list.
  for (const step of Object.keys(graph)) {
    const { part, output } = groupsOf(index, step);
    const folders = [...part.keys(), ...[...output.values()].map((o) => path.posix.dirname("hardware/" + o.file))];
    for (const folder of folders) {
      if (!index.users.has(folder)) index.users.set(folder, new Set());
      index.users.get(folder).add(step);
    }
  }
  cached = index;
  return cached;
}

const label = (file) => path.posix.basename(file).replace(/\.step$/, "");
// A model as the list names it: by its file, or by its folder when the file says only that it
// is an assembly.
const nameOf = (file) => label(file) === "assembly" ? `${path.posix.basename(path.posix.dirname(file))} assembly` : label(file);

// The model that stands for a set of steps, root-relative to hardware/ as the viewer names models:
// the one named for the folder or a step, else the shortest named from the folder, else the
// assembly, else the shortest.
function modelAmong(index, steps, folder) {
  const models = steps.flatMap((s) => (index.graph[s]?.writes || []).filter((f) => f.endsWith(".step")))
    .map((f) => f.slice("hardware/".length))
    .sort((a, b) => label(a).length - label(b).length || a.localeCompare(b));
  const names = [folder, ...steps.map((s) => path.posix.basename(s).replace(/\.rs$/, ""))]
    .map((n) => n.replace(/_/g, "-"));
  return models.find((m) => names.includes(label(m)))
    || models.find((m) => label(m).startsWith(names[0] + "-"))
    || models.find((m) => label(m) === "assembly")
    || models[0] || null;
}

const modelOf = (index, step) => modelAmong(index, [step], path.posix.basename(path.posix.dirname(step)));

// A part, by the folder its sources stand in: its model when a step there makes one.
function partOf(index, folder) {
  const model = modelAmong(index, index.stepsIn.get(folder) || [], path.posix.basename(folder));
  return { kind: "part", key: folder, file: model, label: model ? nameOf(model) : path.posix.basename(folder) };
}

// What one file the record names stands for, beside the step that read it.
function standsFor(index, step, file) {
  const own = path.posix.dirname(step);
  // A model's own files, whether a step made them or the part was bought with them.
  const model = file.match(/^hardware\/(.+?\.step)(?:\.[a-z.]+)?$/) || file.match(/^hardware\/(.+?)\.fine\.step\.npz$/);
  if (model) {
    const stepFile = model[1].endsWith(".step") ? model[1] : model[1] + ".step";
    if (path.posix.dirname("hardware/" + stepFile) === own) return { kind: "own" };
    return { kind: "output", key: stepFile, file: stepFile, label: nameOf(stepFile) };
  }
  const from = index.writer.get(file);
  if (from && from !== step) {
    const made = modelOf(index, from);
    // An output with no model, such as a report, is not a part to open.
    return made ? { kind: "output", key: made, file: made, label: nameOf(made) } : { kind: "none" };
  }
  if (file.startsWith("hardware/")) {
    const folder = path.posix.dirname(file);
    if (folder === own || folder.startsWith(own + "/")) return { kind: "own" };
    return partOf(index, folder);
  }
  const recipe = file.match(/^tools\/hsm\/([^/]+)\/src\/compiled\/(?:modules\/)?(_?)([^/]+)\.rs$/);
  if (recipe) {
    const named = index.byStem.get(recipe[3]) || index.byStem.get(recipe[2] + recipe[3]);
    if (named) {
      const folder = path.posix.dirname(named);
      return folder === own || folder.startsWith(own + "/") ? { kind: "own" } : partOf(index, folder);
    }
  }
  // A crate's manifest only packages it: a part's numbers crate keeps its numbers in the part's
  // folder, which stands as the part.
  const crate = !file.endsWith("/Cargo.toml") && file.match(/^tools\/hsm\/([^/]+)\//);
  const name = crate ? CODE_NAMES[crate[1]] || (crate[1].endsWith("-data") ? crate[1].slice(0, -5) + " recipes" : crate[1] + " programs")
    : file.startsWith("tools/hsm/") ? "Cargo files"
    : TOOL_NAMES[file.split("/").slice(0, 2).join("/")] || file.split("/").slice(0, 2).join("/");
  return { kind: "code", key: name, label: name };
}

// A step's reads, each as the part, output or code it stands for, counted.
function groupsOf(index, step) {
  if (index.groups.has(step)) return index.groups.get(step);
  const groups = { part: new Map(), output: new Map(), code: new Map() };
  for (const read of index.graph[step].reads || []) {
    const item = standsFor(index, step, read);
    if (item.kind === "own" || item.kind === "none") continue;
    const group = groups[item.kind];
    const held = group.get(item.key) || { label: item.label, file: item.file || null, files: 0 };
    held.files += 1;
    group.set(item.key, held);
  }
  index.groups.set(step, groups);
  return groups;
}

/**
 * What the build reruns the model `file` on, grouped by part, and the models built from it.
 *
 * @param {string} graphPath  tools/hsm/build-plan/graph.json
 * @param {string} file       root-relative to hardware/, as /api/steps names models
 * @returns {null | {parts: Item[], outputs: Item[], code: Item[], usedIn: Item[]}}
 *   An Item is `{label, file, files}`: `file` is the model to open, when the part has one, and
 *   `files` how many of the files the step read stand for it. `parts` are the parts whose sources
 *   the step read, `outputs` the models whose files it read, and `usedIn` the models whose steps
 *   read this part's sources or files.
 */
export function madeFrom(graphPath, file) {
  let index;
  try { index = load(graphPath); } catch { return null; }
  const step = index.writer.get("hardware/" + file);
  if (!step) return null;
  const groups = groupsOf(index, step);
  const sorted = (items) => [...items].sort((a, b) => a.label.localeCompare(b.label));
  const usedIn = new Map();
  for (const user of index.users.get(path.posix.dirname(step)) || []) {
    const model = user === step ? null : modelOf(index, user);
    if (model && !usedIn.has(model)) usedIn.set(model, { label: nameOf(model), file: model, files: 1 });
  }
  return {
    parts: sorted(groups.part.values()),
    outputs: sorted(groups.output.values()),
    code: sorted(groups.code.values()),
    usedIn: sorted(usedIn.values()),
  };
}
