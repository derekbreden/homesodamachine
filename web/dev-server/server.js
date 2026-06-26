// Dev wrapper around the production server. Boots the shared HTTP server,
// then attaches the watcher, Python runner, and file-change broadcast for hot
// reload — everything that only makes sense locally.
//
// URL structure is identical to production: localhost:3000/ is the landing
// page, localhost:3000/3d is the parts viewer, /charts is the diagrams
// viewer, /blog is the Updates feed, and so on. The wrapper is purely
// additive — it does NOT change any routes. `dev: true` only changes the
// commit signal sent to clients and skips the boot-time FCM push diff that
// fires on real deploys.
//
// The CadQuery scripts write atomically to their natural location next to
// the .py file (see hardware/scripts/_cadq_export.py), so this server doesn't
// redirect output into .viewer/steps/. Both this dev viewer and the
// public site read STEPs from the same place: hardware/.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import chokidar from "chokidar";

import { start } from "../server.js";
import {
  isRunnableScript,
  findGenerateScripts,
  findRunnableScriptsTransitivelyImporting,
  findBoardsTransitivelyImporting,
  findScriptsConsumingStep,
} from "./deps.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// dev-server lives at /web/dev-server; the cad-venv used to run
// generators lives at the repo root under tools/cad-venv.
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const PYTHON_BIN = path.join(PROJECT_ROOT, "tools", "cad-venv", "bin", "python");

const { broadcast, hardwareDir: HARDWARE_DIR, liteDir: LITE_DIR } = await start({ dev: true });

// Content roots the viewer serves, and that we therefore watch, regenerate,
// and broadcast for. hardware/ is the kitchen edition; pie-in-the-sky/lite/ is
// the lite edition (served when the viewer's Edition toggle is set). The
// viewer fetches each file list relative to whichever root the edition
// selects, so a change must be broadcast with the path relative to the SAME
// root — the client's files-changed handler matches by exact string.
const CONTENT_ROOTS = [HARDWARE_DIR, LITE_DIR].filter((d) => d && fs.existsSync(d));

// Path of a watched file relative to the content root that contains it — the
// form the viewer fetched it under, and therefore the form to broadcast.
function relForBroadcast(absPath) {
  for (const root of CONTENT_ROOTS) {
    const rel = path.relative(root, absPath);
    if (rel && !rel.startsWith("..") && !path.isAbsolute(rel)) return rel;
  }
  return path.relative(HARDWARE_DIR, absPath);
}

// Repo-root-relative path for logs, so files in either tree read cleanly
// (`hardware/...` or `pie-in-the-sky/lite/...`) instead of a `../` climb.
function relForLog(absPath) {
  return path.relative(PROJECT_ROOT, absPath);
}

// Script discovery and the dependency graph — import edges AND STEP-load edges
// (`importStep` / the `_load(...)` helper, usually named in an imported
// `_contents.py`) — live in ./deps.js, shared with the batch rebuilder
// (build-all.js) and unit-tested in web/tests/deps.test.js. The functions are
// passed CONTENT_ROOTS at each call site.

// --- Script runner ---
const running = new Map(); // pyFilePath -> AbortController

async function runScript(pyFilePath) {
  console.log(`  ↪ running: ${relForLog(pyFilePath)}`);
  const prev = running.get(pyFilePath);
  if (prev) prev.abort();
  const ac = new AbortController();
  running.set(pyFilePath, ac);

  const scriptDir = path.dirname(pyFilePath);
  const startTime = Date.now();
  const producedSteps = [];

  try {
    console.log(`  ↪ spawning: ${PYTHON_BIN} ${path.relative(PROJECT_ROOT, pyFilePath)}`);
    const code = await new Promise((resolve, reject) => {
      console.log(`  ↪ cwd: ${path.relative(PROJECT_ROOT, scriptDir)}`);
      // SIGKILL (not the spawn default SIGTERM): CadQuery sits inside
      // long-running OCCT calls that ignore SIGTERM for seconds at a
      // time. Under rapid saves that piles pythons up behind one
      // unresponsive root, the OS starts thrashing, and the watcher
      // looks "stuck." SIGKILL drops the aborted process immediately;
      // the atomic-write helper in _cadq_export.py already handles a
      // half-written tempfile being orphaned.
      //
      // stderr is inherited so python tracebacks land in the
      // dev-server log. Without it, "Process exited with code 1" is
      // the only signal the watcher gives — the actual OCC error,
      // syntax error, etc. is invisible and looks identical to a
      // watcher bug. stdout is still suppressed: generators print
      // diagnostic dimensions on every run and those are noise once
      // the script is working.
      const proc = spawn(PYTHON_BIN, [pyFilePath], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "inherit"],
        signal: ac.signal,
        killSignal: "SIGKILL",
      });
      console.log(`  ↪ PID: ${proc.pid}`);
      proc.on("close", resolve);
      proc.on("error", reject);
      proc.on("exit", (code) => {
        if (code !== 0) {
          reject(new Error(`Process exited with code ${code}`));
        }
      });
    });

    if (code !== 0) return;

    // Broadcast STEP files in scriptDir that were rewritten since startTime.
    // The atomic-write helper in hardware/scripts/_cadq_export.py renames into place,
    // so the mtime reflects the moment a complete file appeared. That same
    // helper also short-circuits when the new bytes match the existing file
    // exactly (timestamps are canonicalized first), so a no-op .py edit
    // produces no .step writes and nothing here broadcasts — which is the
    // right behavior, the file really hasn't changed.
    for (const entry of fs.readdirSync(scriptDir)) {
      if (entry.startsWith(".")) continue; // skip dotfiles (orphaned atomic-write temps)
      if (!entry.endsWith(".step")) continue;
      const full = path.join(scriptDir, entry);
      if (fs.statSync(full).mtimeMs < startTime) continue;
      producedSteps.push(entry);
      const relFile = relForBroadcast(full);
      console.log(`  -> ${relFile}`);
      broadcast({ type: "files-changed", files: [relFile] });
    }
  } catch (e) {
    if (e.name === "AbortError") return;
    // Script failed — leave any prior committed STEP in place.
    console.log(`  ↪ failed: ${e.message}`);
  } finally {
    // Only clear our own slot. If a newer call overwrote `running[pyFilePath]`
    // with its own AC, this finally must not delete that newer entry — the
    // next save would then see `running.has(file) === false`, skip the abort
    // step, and let two pythons race to write the same .step (older one wins
    // if it finishes last → "save 2 silently shows save 1's geometry").
    if (running.get(pyFilePath) === ac) running.delete(pyFilePath);
  }

  if (producedSteps.length === 0) return;

  // Cascade: rebuild scripts that consume (load) the STEPs we just produced —
  // following STEP-load edges through imported `_contents.py`, not just direct
  // importStep calls (see deps.js).
  const dependents = new Set();
  for (const stepName of producedSteps) {
    for (const depScript of findScriptsConsumingStep(stepName, CONTENT_ROOTS)) {
      if (depScript === pyFilePath) continue;
      dependents.add(depScript);
    }
  }
  for (const depScript of dependents) {
    console.log(`  ↪ dependent: ${relForLog(depScript)}`);
    await runScript(depScript);
  }
}

// --- PCB board renderer ---
//
// A board is a tscircuit source (pcb/<dir>/<name>.tsx) whose sibling
// render-board.ts re-exports the Gerbers and composes the three copper views
// into out/. Unlike the CadQuery generators this runs `bun render-board.ts`
// (the toolchain lives in that dir's node_modules), but the lifecycle mirrors
// runScript: abort an in-flight render when a newer save lands, broadcast the
// board source once the views are rewritten so the viewer refreshes.
const pcbRunning = new Map(); // tsx path -> AbortController

async function runPcbRender(tsxPath) {
  const scriptDir = path.dirname(tsxPath);
  const renderScript = path.join(scriptDir, "render-board.ts");
  if (!fs.existsSync(renderScript)) return; // no local renderer beside this board

  const prev = pcbRunning.get(tsxPath);
  if (prev) prev.abort();
  const ac = new AbortController();
  pcbRunning.set(tsxPath, ac);

  console.log(`  ↪ rendering board: ${relForLog(tsxPath)}`);
  try {
    const code = await new Promise((resolve, reject) => {
      const proc = spawn("bun", ["render-board.ts", path.basename(tsxPath)], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "inherit"],
        // Tag the run so render-board's single-flight lock can name us when it
        // supersedes (or is superseded by) a hand-run of the same board.
        env: { ...process.env, RENDER_SOURCE: "dev-server" },
        signal: ac.signal,
        killSignal: "SIGKILL",
      });
      proc.on("close", resolve);
      proc.on("error", reject);
    });
    // Don't broadcast on a failed render — that would refresh the viewer onto
    // the previous (now stale) views and hide the failure (mirrors runScript).
    if (code !== 0) {
      console.log(`  ↪ board render failed (exit ${code})`);
      return;
    }
    const relFile = relForBroadcast(tsxPath);
    console.log(`  -> ${relFile}`);
    broadcast({ type: "files-changed", files: [relFile] });
  } catch (e) {
    if (e.name === "AbortError") return;
    console.log(`  ↪ board render failed: ${e.message}`);
  } finally {
    if (pcbRunning.get(tsxPath) === ac) pcbRunning.delete(tsxPath);
  }
}

// --- File watcher ---
//
// Polling is deliberate. chokidar 4 dropped fsevents and now uses Node's
// `fs.watch(..., { recursive: true })` on macOS, which is kqueue-backed.
// Under load — multiple atomic editor saves, generator scripts writing
// .step files, Python regenerating .pyc files inside __pycache__/ —
// recursive kqueue silently drops events and sometimes stops reporting
// for the watched root entirely. The symptom is a dev server that
// reloads a few times then "stops working until restart." Polling at
// 200 ms costs a few percent of one core (we're watching ~150 files)
// and gives us a deterministic event loop instead.
//
// `__pycache__` is ignored both to cut down on the event volume (every
// generator run rewrites a .pyc) and because we never act on .pyc
// changes anyway.
const watcher = chokidar.watch(CONTENT_ROOTS, {
  ignoreInitial: true,
  // __pycache__: every generator run rewrites .pyc. node_modules: the PCB
  // toolchain (hardware/pcb/*/node_modules) is a large tree we never act on,
  // and polling it would swamp the 200ms loop.
  ignored: (p) => {
    const seg = p.split(path.sep);
    return seg.includes("__pycache__") || seg.includes("node_modules");
  },
  usePolling: true,
  interval: 200,
  binaryInterval: 400,
});
const debounce = new Map();

watcher.on("change", (absPath) => {
  // Shared library changed — rebuild all scripts.
  if (absPath.includes("/cadlib/") && absPath.endsWith(".py")) {
    if (debounce.has("cadlib")) clearTimeout(debounce.get("cadlib"));
    debounce.set(
      "cadlib",
      setTimeout(async () => {
        debounce.delete("cadlib");
        console.log(`Shared lib changed: ${relForLog(absPath)}`);
        for (const f of findGenerateScripts(CONTENT_ROOTS)) {
          console.log(`  Rebuilding ${relForLog(f)}`);
          try {
            await runScript(f);
          } catch (e) {
            // Newer change aborted this run; bail out and let the new
            // change's cascade redo everything.
            break;
          }
        }
      }, 500),
    );
    return;
  }

  // Mermaid file changed — broadcast update.
  if (absPath.endsWith(".mmd")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const relFile = relForBroadcast(absPath);
        console.log(`Mermaid changed: ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // DXF file changed — broadcast update. DXFs are hand-exported (no
  // generator script to re-run) so we just notice the file and forward.
  if (absPath.endsWith(".dxf")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const relFile = relForBroadcast(absPath);
        console.log(`DXF changed: ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // Line-art SVG inside a drawings/ directory changed — broadcast update.
  // Drawings are produced by their own .py script (run on edit below);
  // here we just notice the resulting SVG and forward to the viewer.
  if (absPath.endsWith(".svg") && absPath.split(path.sep).includes("drawings")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const relFile = relForBroadcast(absPath);
        console.log(`Drawing changed: ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // Sidecar metadata file changed — broadcast a change for the part it
  // belongs to. `foo.dxf.json` -> broadcast `foo.dxf`; `foo.step.json`
  // -> broadcast `foo.step`. The viewer's hsm:files-changed handler
  // refetches the part and its updated thickness (since /api/dxf
  // returns sidecar fields in the same response). See hardware/README.md.
  if (absPath.endsWith(".dxf.json") || absPath.endsWith(".step.json")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const baseAbs = absPath.replace(/\.json$/, "");
        const relFile = relForBroadcast(baseAbs);
        console.log(`Sidecar changed: ${relForLog(absPath)} -> refresh ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // PCB source changed — re-render the board(s) it feeds and broadcast each so
  // the viewer refreshes the card + open modal. A board source renders itself; a
  // shared include (`carrier_parts.tsx`) follows the import chain to the boards
  // that pull it in (`mini.tsx`), since the include has no `<board>` of its own.
  // (node_modules is already filtered by the watcher's `ignored`.)
  if (absPath.endsWith(".tsx") && absPath.split(path.sep).includes("pcb")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const segs = absPath.split(path.sep);
        const pcbRoot = segs.slice(0, segs.indexOf("pcb") + 1).join(path.sep);
        const boards = findBoardsTransitivelyImporting(absPath, pcbRoot);
        if (boards.length === 0) {
          console.log(`Changed: ${relForLog(absPath)} (no board imports it — nothing to render)`);
          return;
        }
        console.log(`Changed: ${relForLog(absPath)}`);
        for (const board of boards) runPcbRender(board).catch(() => {});
      }, 500),
    );
    return;
  }

  // Any .py change. The runnable set is:
  //   1. The file itself, if it's a runnable script (generator or drawing).
  //   2. Every other runnable script that transitively imports the file's
  //      module — covers shared `_foo.py` modules anywhere under hardware/,
  //      plus the cross-tree case where a generator like
  //      `co2_coupling_body.py` is consumed by a drawing's `_appliance_model`
  //      and needs to cascade all the way to the `enclosure-iso-*` SVGs.
  // The cadlib handler at the top of this listener is the shotgun version
  // of step 2: anything in `/cadlib/` rebuilds every generator, no walk.
  if (absPath.endsWith(".py")) {
    const moduleName = path.basename(absPath, ".py");
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(async () => {
        debounce.delete(absPath);
        const toRun = [];
        if (isRunnableScript(absPath)) toRun.push(absPath);
        for (const dep of findRunnableScriptsTransitivelyImporting(moduleName, CONTENT_ROOTS)) {
          if (dep !== absPath) toRun.push(dep);
        }
        if (toRun.length === 0) return;
        console.log(`Changed: ${relForLog(absPath)}`);
        for (const dep of toRun) {
          console.log(`  Running ${relForLog(dep)}`);
          try {
            await runScript(dep);
          } catch (e) {
            // A newer change aborted this run; the new change's
            // cascade will rebuild from scratch. Stop this cascade so
            // we don't keep chasing a moving target.
            break;
          }
        }
      }, 500),
    );
    return;
  }
});

console.log("Watching for changes...");
