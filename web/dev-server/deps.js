// Dependency-graph analysis over the CAD generator scripts. NO side effects
// (no server, no watcher, no spawning) so it is unit-testable (web/tests/
// deps.test.js) and shared by both the live watcher (dev-server/server.js) and
// the batch rebuilder (dev-server/build-all.js).
//
// Two kinds of edge connect the scripts:
//
//   1. Python import — a runnable generator imports a shared `_module.py`
//      (which may import another, transitively). Editing the module must
//      rebuild every runnable that reaches it.
//
//   2. STEP-load — a script reads another script's `.step` OUTPUT, via
//      `cq.importers.importStep(...)` or the `_load(...)` helper. The file is
//      usually named in an imported `_contents.py`, NOT in the runnable that
//      consumes it: `enclosure_assembly.py` (which `import _contents`) consumes
//      `source-select-assembly.step` without ever naming that file or calling
//      importStep itself.
//
// Tracking only (1) is the bug this module fixes. A part's STEP could change
// and every enclosure or assembly that merely *loads* it stayed stale until some
// unrelated import-edge edit happened to re-run the generator — a real,
// week-long staleness (valve-manifold widened 2026-06-08; the assemblies that
// load its trays weren't rebuilt until an unrelated reservoir edit on 06-14
// re-triggered them). See web/tests/deps.test.js for the regression.

import fs from "fs";
import path from "path";

export const MAIN_RE = /^if\s+__name__\s*==\s*["']__main__["']\s*:/m;

// The content roots the viewer serves and the generators live under: hardware/
// (kitchen edition) and pie-in-the-sky/lite/ (lite edition). Mirrors the
// HARDWARE_DIR/LITE_DIR the server resolves, but derived from the repo root so
// callers that don't boot the server (build-all, tests) get the same set.
export function contentRoots(projectRoot) {
  return [
    path.join(projectRoot, "hardware"),
    path.join(projectRoot, "pie-in-the-sky", "lite"),
  ].filter((d) => fs.existsSync(d));
}

function readSource(file) {
  try {
    return fs.readFileSync(file, "utf-8");
  } catch {
    return null;
  }
}

// A "runnable" script is a non-`_`-prefixed .py with a `__main__` block — a
// generator/drawing meant to run directly, vs. an imported `_module.py`.
// Content detection (not name/dir) means a new script live-reloads with no
// registration.
export function isRunnableScript(pyFilePath) {
  const base = path.basename(pyFilePath);
  if (!base.endsWith(".py")) return false;
  if (base.startsWith("_")) return false;
  const source = readSource(pyFilePath);
  return source != null && MAIN_RE.test(source);
}

function walk(roots, suffix) {
  const out = [];
  function rec(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name === "__pycache__") continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) rec(full);
      else if (entry.name.endsWith(suffix)) out.push(full);
    }
  }
  for (const root of roots) rec(root);
  return out;
}

export function findAllPythonFiles(roots) {
  return walk(roots, ".py");
}

export function findGenerateScripts(roots) {
  return walk(roots, ".py").filter(isRunnableScript);
}

// Walk the import graph backward from a module to every runnable script that
// transitively imports it — covers shared `_foo.py` chains and the Blender
// `--python` subprocess edge (`_blender_render.py` hands `_blender_scene.py` to
// Blender as a path, never importing it). Without the transitive walk, edits to
// a leaf module silently rebuild nothing.
export function findRunnableScriptsTransitivelyImporting(moduleName, roots) {
  const allPyFiles = walk(roots, ".py");
  const visited = new Set();
  const dependents = new Set();
  const queue = [moduleName];

  while (queue.length > 0) {
    const mod = queue.shift();
    if (visited.has(mod)) continue;
    visited.add(mod);

    const importRe = new RegExp(`(?:^|\\s)(?:from|import)\\s+${mod}\\b`, "m");
    // Require the `--python` flag so a bare doc-comment mention of the filename
    // can't masquerade as a subprocess dependency.
    const scriptRefRe = new RegExp(`["'/]${mod}\\.py\\b`, "m");
    for (const pyFile of allPyFiles) {
      const source = readSource(pyFile);
      if (source == null) continue;
      const importsIt = importRe.test(source);
      const runsViaBlender = source.includes("--python") && scriptRefRe.test(source);
      if (!importsIt && !runsViaBlender) continue;
      if (isRunnableScript(pyFile)) dependents.add(pyFile);
      // Keep walking THROUGH this file whether or not it's runnable: a generator
      // can double as a base module that other generators import as its python
      // (`bag_circuit_tray` is both a tray and the geometry `nozzle_gate_tray`
      // and `source_select_tray` build on). Stopping at the
      // first runnable would leave those downstream trays stale when the root
      // module changes — and they can't be caught by the STEP-load cascade
      // either, since they import the tray's python, not its .step. `visited`
      // dedupes, so re-queuing a shared basename is safe.
      queue.push(path.basename(pyFile, ".py"));
    }
  }

  return Array.from(dependents);
}

// A board is a tscircuit source that declares a `<board>` — the renderable that
// `render-board.ts` turns into Gerbers + copper views. Sibling `.tsx` files
// without a `<board>` (e.g. `parts.tsx`) are includes: footprint
// libraries and rosters the boards import, never rendered on their own.
function isBoardTsx(source) {
  return /<board\b/.test(source);
}

// Walk the board import graph backward from a changed `.tsx` to every board that
// transitively imports it, scoped to the `pcb/` tree the file lives in. A change
// to a shared include (`parts.tsx`) thus rebuilds the boards that pull it
// in (`pcba.tsx`), mirroring the Python cascade — rendering the include itself
// would only fail ("no renderable layers"), since an include has no `<board>`.
// If the changed file is itself a board, it's returned as the sole dependent.
export function findBoardsTransitivelyImporting(changedTsxPath, pcbRoot) {
  // Skip the toolchain's own sources and editor/temp artifacts (`._foo.tsx`,
  // the dot-prefixed scratch boards `_clrsweep` & co. write): neither is a board
  // the watcher should ever rebuild.
  const allTsx = walk([pcbRoot], ".tsx").filter(
    (f) => !f.split(path.sep).includes("node_modules") && !path.basename(f).startsWith("."),
  );
  const source = readSource(changedTsxPath);
  if (source != null && isBoardTsx(source)) return [changedTsxPath];

  const boards = new Set();
  const visited = new Set();
  const queue = [path.basename(changedTsxPath, ".tsx")];

  while (queue.length > 0) {
    const mod = queue.shift();
    if (visited.has(mod)) continue;
    visited.add(mod);

    // A relative import names the module by basename: `from "./parts"`
    // (or a deeper `../foo/parts`), with or without the `.tsx` suffix.
    const importRe = new RegExp(`from\\s+["'][^"']*\\b${escapeRegExp(mod)}(?:\\.tsx)?["']`, "m");
    for (const tsx of allTsx) {
      if (path.basename(tsx, ".tsx") === mod) continue; // don't match a file to itself
      const src = readSource(tsx);
      if (src == null || !importRe.test(src)) continue;
      if (isBoardTsx(src)) boards.add(tsx);
      else queue.push(path.basename(tsx, ".tsx"));
    }
  }

  return Array.from(boards);
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// True if `source` names `stepBasename` as a whole filename token. Boundaries
// on BOTH sides matter: the right guard `(?![\w.])` keeps `tray.step` from
// matching inside `tray.step.png`; the left guard `(?<![\w.\-])` keeps the
// hyphen-joined `assembly.step` from matching inside `source-select-assembly.step`
// (a real collision that otherwise invents reverse edges and cycles). A path
// separator or quote before the name is fine — that's how a real reference
// reads, e.g. `_VM / "tray" / "tray.step"`.
function referencesStep(source, stepBasename) {
  return new RegExp("(?<![\\w.\\-])" + escapeRegExp(stepBasename) + "(?![\\w.])").test(source);
}

// Map each produced `.step` (by basename) to the runnable script that writes
// it. Convention (from _cadq_export usage): a generator writes its STEP into
// its OWN directory via `export_step/_assembly(..., _here.parent / "X.step")`,
// so the producer of `dir/X.step` is the runnable in `dir` whose source names
// "X.step". A directory can hold several runnables (a tray + its assembly),
// each producing a different step; matching on the filename disambiguates.
// Reference STEPs with no generator (e.g. `kamoer-kphm400.step`) simply have no
// entry.
export function buildProducerMap(roots) {
  const producerOf = new Map();
  for (const step of walk(roots, ".step")) {
    const base = path.basename(step);
    const dir = path.dirname(step);
    let entries;
    try {
      entries = fs.readdirSync(dir);
    } catch {
      continue;
    }
    for (const name of entries) {
      if (!name.endsWith(".py")) continue;
      const script = path.join(dir, name);
      if (!isRunnableScript(script)) continue;
      const source = readSource(script);
      if (source != null && referencesStep(source, base)) {
        producerOf.set(base, script);
        break;
      }
    }
  }
  return producerOf;
}

// Runnable scripts that CONSUME `stepBasename` (load it as input) — the
// STEP-load dependents the import graph misses. A .py file consumes the step if
// it names it and is not its producer. A runnable match is itself a consumer; a
// shared-module match (e.g. `_contents.py`) resolves to the runnables that
// transitively import that module. `producerOf` is computed if not supplied.
export function findScriptsConsumingStep(stepBasename, roots, producerOf) {
  producerOf = producerOf || buildProducerMap(roots);
  const producer = producerOf.get(stepBasename);
  const consumers = new Set();
  for (const pyFile of walk(roots, ".py")) {
    if (pyFile === producer) continue;
    const source = readSource(pyFile);
    if (source == null || !referencesStep(source, stepBasename)) continue;
    if (isRunnableScript(pyFile)) {
      consumers.add(pyFile);
    } else {
      // A shared module names the step; the real consumers are the runnable
      // scripts that import it. (Two `_contents.py` share a basename, so both
      // editions' importers resolve — harmless: each genuinely loads the part,
      // and an over-rebuild is a no-op write.)
      for (const dep of findRunnableScriptsTransitivelyImporting(
        path.basename(pyFile, ".py"),
        roots,
      )) {
        if (dep !== producer) consumers.add(dep);
      }
    }
  }
  return Array.from(consumers);
}

// consumer script -> Set(producer scripts it depends on), over STEP-load edges.
// (Import-only edges don't need ordering here: a shared module isn't built, and
// runnables that import each other are rare; the watcher handles import edits
// directly. This graph exists to order a full rebuild.)
export function dependencyGraph(roots) {
  const scripts = findGenerateScripts(roots);
  const producerOf = buildProducerMap(roots);
  const deps = new Map(scripts.map((s) => [s, new Set()]));
  for (const [stepBase, producer] of producerOf) {
    for (const consumer of findScriptsConsumingStep(stepBase, roots, producerOf)) {
      if (consumer === producer) continue;
      if (!deps.has(consumer)) deps.set(consumer, new Set());
      deps.get(consumer).add(producer);
    }
  }
  return deps;
}

// Topological build order: producers before the scripts that load their STEPs
// (DFS post-order). A cycle (none expected in a CAD build graph) degrades to
// "built, possibly out of order" rather than dropping nodes.
export function buildOrder(roots) {
  const deps = dependencyGraph(roots);
  const order = [];
  const done = new Set();
  const onStack = new Set();
  function visit(node) {
    if (done.has(node) || onStack.has(node)) return;
    onStack.add(node);
    for (const dep of deps.get(node) || []) visit(dep);
    onStack.delete(node);
    done.add(node);
    order.push(node);
  }
  for (const node of deps.keys()) visit(node);
  return order;
}

// The scoped, reactive slice of buildOrder the live watcher walks for one edit.
// Given the SEED scripts that must rebuild (the transitive import closure of the
// edited module), return { order, loadsOf }:
//   - `order`: the seeds PLUS every script that transitively LOADS a seed's STEP
//     output, sorted producers-before-consumers, each script exactly once.
//   - `loadsOf`: script -> Set(STEP basenames it consumes), so the caller can
//     skip a pure STEP-load consumer whose inputs didn't actually change.
// This is what lets a base-part edit rebuild the whole downstream tree without
// the old recursive cascade re-running a shared consumer once per producer — the
// enclosure that loads all four tray assemblies rebuilds once, after them, not
// four times interleaved. Import-only seeds carry no STEP-load edge, so their
// order among themselves is arbitrary (correct: a Python import reads the
// dependency's source at run time, independent of its STEP).
export function affectedBuildOrder(seeds, roots) {
  const producerOf = buildProducerMap(roots);
  const loadsOf = new Map();     // consumer script -> Set(step basename it loads)
  const consumersOf = new Map(); // producer script -> Set(consumer scripts)
  for (const [stepBase, producer] of producerOf) {
    for (const consumer of findScriptsConsumingStep(stepBase, roots, producerOf)) {
      if (consumer === producer) continue;
      if (!loadsOf.has(consumer)) loadsOf.set(consumer, new Set());
      loadsOf.get(consumer).add(stepBase);
      if (!consumersOf.has(producer)) consumersOf.set(producer, new Set());
      consumersOf.get(producer).add(consumer);
    }
  }
  // Everything the seeds can reach forward over producer→consumer STEP-load edges.
  // (Not closed backward over producers — a producer a consumer loads but that
  // itself didn't change stays out; its committed STEP is the correct input.)
  const affected = new Set(seeds);
  const queue = [...seeds];
  while (queue.length > 0) {
    const s = queue.shift();
    for (const c of consumersOf.get(s) || []) {
      if (!affected.has(c)) {
        affected.add(c);
        queue.push(c);
      }
    }
  }
  // Seeds first, then their STEP-load consumers — each group in buildOrder's
  // producers-first order. Seeds are the upstream parts the user is editing, so
  // they rebuild first (fast feedback) and the heavy downstream (enclosures) is
  // deferred. Safe because a seed never STEP-loads a consumer's output (that
  // would be a cycle: consumers are strictly downstream of the seeds).
  const topo = buildOrder(roots).filter((s) => affected.has(s));
  const seedSet = new Set(seeds);
  const order = [...topo.filter((s) => seedSet.has(s)), ...topo.filter((s) => !seedSet.has(s))];
  return { order, loadsOf };
}
