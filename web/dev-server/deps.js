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

// --- Per-call memo --------------------------------------------------------
//
// These functions call each other in nested loops: dependencyGraph asks
// findScriptsConsumingStep once per produced STEP, and every shared-module hit
// inside that runs a full import walk, which re-walks the trees and re-reads
// every source from disk. The repeats are pure waste — across one top-level
// call the filesystem is fixed, which the code already assumes when it reads
// the same file dozens of times and expects the same bytes.
//
// `memoized` hangs a scratch cache off the outermost call and drops it on the
// way out, so the next call after an edit sees fresh bytes. Nested calls find
// the cache already installed and reuse it; an unwrapped call still returns the
// same answer, just uncached.
let memo = null;

function memoized(fn) {
  return function (...args) {
    if (memo) return fn.apply(this, args);
    memo = {
      walk: new Map(),
      source: new Map(),
      runnable: new Map(),
      producers: new Map(),
      importers: new Map(),
      consumers: new Map(),
    };
    try {
      return fn.apply(this, args);
    } finally {
      memo = null;
    }
  };
}

const rootsKey = (roots) => roots.join("\0");

function readSource(file) {
  if (memo && memo.source.has(file)) return memo.source.get(file);
  let source;
  try {
    source = fs.readFileSync(file, "utf-8");
  } catch {
    source = null;
  }
  if (memo) memo.source.set(file, source);
  return source;
}

// hardware/scripts holds the shared modules and the command-line tools the repo is worked
// WITH — the export helper, the build lock, the geometry probe, the pin-map check. None of
// them produce content, and the ones that take arguments have nothing to do when spawned
// bare. Their imports still build the graph below, so editing one rebuilds the generators
// that read it.
const TOOLING_DIR = path.join("hardware", "scripts");

// A "runnable" script is a non-`_`-prefixed .py with a `__main__` block — a
// generator/drawing meant to run directly, vs. an imported `_module.py`.
// Content detection (not name/dir) means a new script live-reloads with no
// registration.
export function isRunnableScript(pyFilePath) {
  if (memo && memo.runnable.has(pyFilePath)) return memo.runnable.get(pyFilePath);
  const runnable = computeRunnable(pyFilePath);
  if (memo) memo.runnable.set(pyFilePath, runnable);
  return runnable;
}

function computeRunnable(pyFilePath) {
  const base = path.basename(pyFilePath);
  if (!base.endsWith(".py")) return false;
  if (base.startsWith("_")) return false;
  if (path.dirname(pyFilePath).endsWith(TOOLING_DIR)) return false;
  const source = readSource(pyFilePath);
  return source != null && MAIN_RE.test(source);
}

function walk(roots, suffix) {
  const key = `${suffix}\0${rootsKey(roots)}`;
  if (memo && memo.walk.has(key)) return memo.walk.get(key);
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
  if (memo) memo.walk.set(key, out);
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
export const findRunnableScriptsTransitivelyImporting = memoized(importersOf);

function importersOf(changedPath, roots) {
  const key = `${path.resolve(changedPath)}\0${rootsKey(roots)}`;
  if (memo && memo.importers.has(key)) return memo.importers.get(key);
  const allPyFiles = walk(roots, ".py");
  const visited = new Set();
  const dependents = new Set();
  const queue = [path.resolve(changedPath)];

  // Which edition (content root) a file belongs to, and which module names each
  // edition defines for itself. An importer in another edition that has its own
  // copy of the module resolves to that copy, never to this one.
  const absRoots = roots.map((r) => path.resolve(r));
  const rootOf = (p) => absRoots.find((r) => {
    const rp = path.relative(r, p);
    return rp && !rp.startsWith("..") && !path.isAbsolute(rp);
  });
  const modulesByRoot = new Map(absRoots.map((r) => [r, new Set()]));
  for (const f of allPyFiles) {
    const r = rootOf(path.resolve(f));
    if (r) modulesByRoot.get(r).add(path.basename(f, ".py"));
  }

  while (queue.length > 0) {
    const modPath = queue.shift();
    if (visited.has(modPath)) continue;
    visited.add(modPath);
    const mod = path.basename(modPath, ".py");

    const importRe = new RegExp(`(?:^|\\s)(?:from|import)\\s+${escapeRegExp(mod)}\\b`, "m");
    // Require the `--python` flag so a bare doc-comment mention of the filename
    // can't masquerade as a subprocess dependency.
    const scriptRefRe = new RegExp(`["'/]${escapeRegExp(mod)}\\.py\\b`, "m");
    for (const pyFile of allPyFiles) {
      const abs = path.resolve(pyFile);
      if (abs === modPath) continue;
      const source = readSource(pyFile);
      if (source == null) continue;
      const importsIt = importRe.test(source);
      const runsViaBlender = source.includes("--python") && scriptRefRe.test(source);
      if (!importsIt && !runsViaBlender) continue;
      // Resolve `mod` the way Python will from this file: a sibling module in the
      // importer's own directory is sys.path[0] and wins. Follow the import edge
      // only when that resolution IS the file that changed. The two editions mirror
      // each other's filenames (_contents.py, enclosure.py, enclosure_assembly.py,
      // power_assembly.py, power_tray.py), so a bare-name match rebuilt lite for a
      // hardware edit it never imports — a whole second assembly competing for the
      // same cores. With no sibling the module comes from a shared dir on sys.path
      // (hardware/scripts/_cadq_export.py), and that edge stands.
      let edge = runsViaBlender;
      if (importsIt) {
        // A sibling module in the importer's own directory is sys.path[0] and wins.
        const sibling = path.join(path.dirname(abs), `${mod}.py`);
        const siblingWins = fs.existsSync(sibling) && path.resolve(sibling) !== modPath;
        // Otherwise, if the importer lives in a different edition that defines this
        // module itself, it reaches its own copy through its own sys.path — not this
        // one. (lite/funnel.py imports `enclosure_assembly` from the lite tree.)
        const changedRoot = rootOf(modPath);
        const fileRoot = rootOf(abs);
        const otherEdition =
          fileRoot && changedRoot && fileRoot !== changedRoot &&
          modulesByRoot.get(fileRoot).has(mod);
        if (!siblingWins && !otherEdition) edge = true;
      }
      if (!edge) continue;
      if (isRunnableScript(pyFile)) dependents.add(pyFile);
      // Keep walking THROUGH this file whether or not it's runnable: a generator
      // can double as a base module that other generators import as its python
      // (`bag_circuit_tray` is both a tray and the geometry `nozzle_gate_tray`
      // and `source_select_tray` build on). Stopping at the
      // first runnable would leave those downstream trays stale when the root
      // module changes — and they can't be caught by the STEP-load cascade
      // either, since they import the tray's python, not its .step. Queue the
      // file, not its basename, so the next hop resolves against this edition's
      // copy rather than every tree that happens to share the name. `visited`
      // dedupes.
      queue.push(abs);
    }
  }

  const out = Array.from(dependents);
  if (memo) memo.importers.set(key, out);
  return out;
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
export const findBoardsTransitivelyImporting = memoized(boardsImporting);

function boardsImporting(changedTsxPath, pcbRoot) {
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
export const buildProducerMap = memoized(producerMap);

function producerMap(roots) {
  const key = rootsKey(roots);
  if (memo && memo.producers.has(key)) return memo.producers.get(key);
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
  if (memo) memo.producers.set(key, producerOf);
  return producerOf;
}

// Runnable scripts that CONSUME `stepBasename` (load it as input) — the
// STEP-load dependents the import graph misses. A .py file consumes the step if
// it names it and is not its producer. A runnable match is itself a consumer; a
// shared-module match (e.g. `_contents.py`) resolves to the runnables that
// transitively import that module. `producerOf` is computed if not supplied.
export const findScriptsConsumingStep = memoized(consumersOfStep);

function consumersOfStep(stepBasename, roots, producerOf) {
  producerOf = producerOf || buildProducerMap(roots);
  // Reuse a cached answer only when the producer map is the one this call tree
  // derived from `roots` — a caller supplying its own map gets a fresh walk.
  const key = `${stepBasename}\0${rootsKey(roots)}`;
  const shared = memo != null && producerOf === memo.producers.get(rootsKey(roots));
  if (shared && memo.consumers.has(key)) return memo.consumers.get(key);
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
      // scripts that import it — resolved from this file, so an edition only
      // pulls in the importers that actually load its own copy.
      for (const dep of findRunnableScriptsTransitivelyImporting(pyFile, roots)) {
        if (dep !== producer) consumers.add(dep);
      }
    }
  }
  const out = Array.from(consumers);
  if (shared) memo.consumers.set(key, out);
  return out;
}

// consumer script -> Set(producer scripts it depends on), over STEP-load edges.
// (Import-only edges don't need ordering here: a shared module isn't built, and
// runnables that import each other are rare; the watcher handles import edits
// directly. This graph exists to order a full rebuild.)
export const dependencyGraph = memoized(graphOf);

function graphOf(roots) {
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
export const buildOrder = memoized(orderOf);

function orderOf(roots) {
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
export const affectedBuildOrder = memoized(affectedOrderOf);

function affectedOrderOf(seeds, roots) {
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
