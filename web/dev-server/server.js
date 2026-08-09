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
import { mountPcbEditorRoutes } from "../lib/pcb-editor-routes.js";
import { mountStepEditorRoutes } from "../lib/step-editor-routes.js";
import {
  isRunnableScript,
  findRunnableScriptsTransitivelyImporting,
  findBoardsTransitivelyImporting,
  affectedBuildOrder,
  buildOrder,
} from "./deps.js";
import { WS } from "../contracts/ws-frames.js";
import { isCardAssetPath, isCardPath } from "../contracts/cards.js";
import { walkAssemblyCards } from "../lib/walk.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// dev-server lives at /web/dev-server; the cad-venv used to run
// generators lives at the repo root under tools/cad-venv.
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const PYTHON_BIN = path.join(PROJECT_ROOT, "tools", "cad-venv", "bin", "python");

const { app, broadcast, hardwareDir: HARDWARE_DIR, editionDirs: EDITION_DIRS } = await start({ dev: true });

// PCB editor API — dev-only, not reachable on the public site. Backs the
// viewer's "Edit" toggle (web/public/js/viewer/pcb-edit.js): board component
// parse + position write-back. Absent in production, so the board is read-only
// there and the Edit toggle never appears.
mountPcbEditorRoutes(app, HARDWARE_DIR);

// STEP component editor API — dev-only, backs the viewer's 3D "Edit" toggle
// (web/public/js/viewer/component-edit.js). A move is written to a moves sidecar
// (lib/step-editor-routes.js), where the pack composes it onto the moved body's
// own seat, and this rebuild re-runs the
// assembly generator, which broadcasts the new .step so the viewer hot-reloads
// onto the real geometry. Under HSM_EDITOR (below) a clashing move is BUILT and
// saved anyway — flagged not-build-ready in the scorecard — so you can see the
// overlap you just made; only a genuine generator error exits non-zero, and its
// stderr comes back for the panel to show. Absent in production, so the Edit
// toggle never appears there.
const editorRunning = new Map(); // generator path -> AbortController (supersede a slow rebuild)

async function rebuildStepAssembly(pyFilePath) {
  const prev = editorRunning.get(pyFilePath);
  if (prev) prev.abort();
  const ac = new AbortController();
  editorRunning.set(pyFilePath, ac);

  const scriptDir = path.dirname(pyFilePath);
  const startTime = Date.now();
  console.log(`  ↪ editor rebuild: ${relForLog(pyFilePath)}`);
  try {
    let stderr = "";
    const code = await new Promise((resolve, reject) => {
      const proc = spawn(PYTHON_BIN, [pyFilePath], {
        cwd: scriptDir,
        // stderr piped (not inherited) so a generator error / SystemExit message
        // can ride back to the editor panel; stdout suppressed like runScript.
        stdio: ["ignore", "ignore", "pipe"],
        signal: ac.signal,
        killSignal: "SIGKILL",
        // HSM_EDITOR: this is the interactive editor. The generator, under it, writes a clashing
        // pack (flagged not-build-ready) instead of refusing — so the move you made is visible in
        // the reloaded geometry. A headless build still hard-stops on a clash.
        env: { ...process.env, HSM_SKIP_THUMBNAILS: "1", HSM_EDITOR: "1", HSM_BUILD_SOURCE: "dev-server (editor)" },
      });
      proc.stderr.setEncoding("utf8");
      proc.stderr.on("data", (c) => { stderr += c; if (stderr.length > 8000) stderr = stderr.slice(-8000); });
      proc.on("close", resolve);
      proc.on("error", reject);
    });

    if (code !== 0) {
      // Last non-empty line is the SystemExit reason (e.g. "pack does not close …").
      const lines = stderr.split("\n").map((l) => l.trimEnd()).filter(Boolean);
      const reason = lines[lines.length - 1] || `generator exited ${code}`;
      console.log(`  ↪ editor rebuild failed: ${reason}`);
      return { ok: false, error: reason };
    }

    // Broadcast every .step the generator rewrote (mirrors runScript), so the
    // open modal hot-reloads onto the moved geometry.
    for (const entry of fs.readdirSync(scriptDir)) {
      if (entry.startsWith(".") || !entry.endsWith(".step")) continue;
      const full = path.join(scriptDir, entry);
      if (fs.statSync(full).mtimeMs < startTime) continue;
      const relFile = relForBroadcast(full);
      console.log(`  -> ${relFile} (editor)`);
      broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
      queueThumbnail(full);
    }
    return { ok: true };
  } catch (e) {
    if (e.name === "AbortError") return { ok: false, error: "superseded by a newer move" };
    return { ok: false, error: e.message };
  } finally {
    if (editorRunning.get(pyFilePath) === ac) editorRunning.delete(pyFilePath);
  }
}

// Every edition's root, resolved per request against the viewer's own cookie —
// the edit has to land in the tree the viewer is showing, and both editions
// carry an assembly at the same relative path.
mountStepEditorRoutes(app, { editionDirs: EDITION_DIRS }, rebuildStepAssembly);

// Content roots the viewer serves, and that we therefore watch, regenerate,
// and broadcast for — one per edition (web/lib/editions.js), served when the
// viewer's Edition selector picks it. The viewer fetches each file list
// relative to whichever root the edition selects, so a change must be
// broadcast with the path relative to the SAME root — the client's
// files-changed handler matches by exact string.
const CONTENT_ROOTS = Object.values(EDITION_DIRS).filter((d) => d && fs.existsSync(d));

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
// (`hardware/...` or `hardware/...`) instead of a `../` climb.
function relForLog(absPath) {
  return path.relative(PROJECT_ROOT, absPath);
}

// Script discovery and the dependency graph — import edges AND STEP-load edges
// (`importStep` / the `_load(...)` helper, usually named in an imported module
// like `enclosure_assembly.py` or `foam_assembly.py`) — live in ./deps.js, shared with the
// batch rebuilder (build-all.js) and unit-tested in web/tests/deps.test.js. The functions are
// passed CONTENT_ROOTS at each call site.

// --- Script runner ---
//
// runScript runs ONE generator and returns the basenames of the STEPs it
// (re)wrote — nothing more. Ordering the rebuild and cascading STEP-load
// dependents is the caller's job (runWave), so a shared consumer is never
// rebuilt more than once per edit. runScript only owns the process lifecycle:
// spawn, supersede an in-flight run of the same file, broadcast + queue
// thumbnails for what changed.
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
      //
      // HSM_SKIP_THUMBNAILS: a generator otherwise renders its grid PNG at
      // process exit (hardware/scripts/_cadq_export.py), which boots a headless
      // browser (render-thumbnails.js → puppeteer) for seconds to tens of
      // seconds. Inside a watcher-spawned generator that freezes the whole
      // cascade with no output until the browser finishes — and since we
      // supersede with the SIGKILL above (uncatchable), a generator killed
      // mid-render orphans that browser, stacking them up under rapid saves. So
      // the watcher skips the in-generator render and rebuilds thumbnails itself,
      // off this critical path — see queueThumbnail below.
      const proc = spawn(PYTHON_BIN, [pyFilePath], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "inherit"],
        signal: ac.signal,
        killSignal: "SIGKILL",
        env: { ...process.env, HSM_SKIP_THUMBNAILS: "1", HSM_BUILD_SOURCE: "dev-server" },
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

    if (code !== 0) return producedSteps;

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
      broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
      queueThumbnail(full);
    }
  } catch (e) {
    if (e.name === "AbortError") return producedSteps;
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

  return producedSteps;
}

// Rebuild one edit's wave: the SEED scripts (the edited file + every runnable
// that transitively imports it — their python changed, so they always run) plus
// every script that transitively LOADS a seed's STEP output. affectedBuildOrder
// sequences them producers-before-consumers and hands back what each one loads;
// we run each ONCE, skipping a pure STEP-load consumer unless a step it loads
// actually changed this wave. That reactive, run-once pass is why editing a base
// part (beduan_solenoid) now rebuilds the whole downstream tree — the valve seat,
// the cap that prints it, the assemblies that place it, the enclosures that load
// those assemblies — while the enclosure still rebuilds only once.
async function runWave(seeds) {
  const { order, loadsOf } = affectedBuildOrder(seeds, CONTENT_ROOTS);
  const seedSet = new Set(seeds);
  const changed = new Set(); // STEP basenames rewritten this wave
  for (const script of order) {
    if (seedSet.has(script)) {
      console.log(`  Running ${relForLog(script)}`);
    } else {
      // Pure STEP-load consumer: skip unless something it loads changed.
      const loads = loadsOf.get(script);
      if (!loads || ![...loads].some((s) => changed.has(s))) continue;
      console.log(`  ↪ dependent: ${relForLog(script)}`);
    }
    for (const step of await runScript(script)) changed.add(step);
  }
}

// One wave at a time. The watcher debounces per FILE, so a burst of saves — or the
// docgen substitution a generator writes back into its own source at the
// end of its own build — starts a second wave beside the first. Both spawn generators,
// both take the global CAD build lock (hardware/scripts/_run_lock.py), and the newer one
// SIGTERMs the older: the cascade dies half-run, and a dependent that never got its turn
// keeps a stale STEP. Seeds that arrive mid-wave collect here and go out as the next one.
let waveInFlight = null;
const pendingSeeds = new Set();

function queueWave(seeds) {
  for (const s of seeds) pendingSeeds.add(s);
  if (waveInFlight) return waveInFlight;
  waveInFlight = (async () => {
    try {
      while (pendingSeeds.size) {
        const batch = [...pendingSeeds];
        pendingSeeds.clear();
        await runWave(batch);
      }
    } finally {
      waveInFlight = null;
    }
  })();
  return waveInFlight;
}

// --- Background thumbnail renderer ---
//
// Each grid card shows a committed PNG per STEP (served at /thumbs/<file>.step
// .png). A generator normally renders its own at process exit
// (hardware/scripts/_cadq_export.py), but that boots a headless browser
// (tools/render/render-thumbnails.js → puppeteer) — which is why running it
// inside a watcher-spawned generator froze the cascade (see the
// HSM_SKIP_THUMBNAILS note in runScript). Generators the watcher spawns skip it,
// and we render here instead, off the critical path, so the watcher stays
// responsive and never orphans a browser on a SIGKILL supersede.
//
// Single-flight: one render-thumbnails.js at a time. STEPs produced while a
// render runs wait in `pendingThumbs` and drain as the next batch when it
// closes, so a burst of saves coalesces instead of stacking browsers. Each STEP
// is re-broadcast once its PNG lands so the card repaints against fresh bytes
// (live.js refreshStepCard, cache-busted); the STEP itself is unchanged, so an
// open modal's refetch 304s.
const THUMBNAIL_TOOL = path.join(PROJECT_ROOT, "tools", "render", "render-thumbnails.js");
const pendingThumbs = new Set(); // abs .step paths whose PNG needs a rebuild
let thumbInFlight = false;

function queueThumbnail(absStepPath) {
  pendingThumbs.add(absStepPath);
  flushThumbnails();
}

function flushThumbnails() {
  if (thumbInFlight || pendingThumbs.size === 0) return;
  const steps = [...pendingThumbs];
  pendingThumbs.clear();
  thumbInFlight = true;
  console.log(`  ↪ thumbnails: rendering ${steps.length} in background`);
  const proc = spawn("node", [THUMBNAIL_TOOL, ...steps], {
    cwd: PROJECT_ROOT,
    // stderr inherited so render-thumbnails' per-file warnings land in the log;
    // stdout (its ✓/done chatter) suppressed, matching the generator spawn.
    stdio: ["ignore", "ignore", "inherit"],
  });
  const finish = () => {
    thumbInFlight = false;
    let landed = 0;
    for (const step of steps) {
      // Best-effort: a STEP render-thumbnails couldn't draw leaves no PNG, so
      // only re-broadcast the ones that actually landed.
      if (fs.existsSync(step + ".png")) {
        broadcast({ type: WS.FILES_CHANGED, files: [relForBroadcast(step)] });
        landed++;
      }
    }
    console.log(`  ↪ thumbnails: done (${landed}/${steps.length})`);
    flushThumbnails(); // drain any saves that arrived mid-render
  };
  proc.on("close", finish);
  proc.on("error", (e) => {
    thumbInFlight = false;
    console.log(`  ↪ thumbnails: spawn failed (${e.message})`);
  });
}

// --- PCB board renderer ---
//
// A board is a tscircuit source (pcb/<dir>/<name>.tsx) whose sibling
// render-board.ts re-exports the Gerbers and composes the three copper views
// into out/. Unlike the CadQuery generators this runs `bun render-board.ts`
// (the toolchain lives in that dir's node_modules), but the lifecycle mirrors
// runScript: abort an in-flight render when a newer save lands, broadcast the
// board source once the views are rewritten so the viewer refreshes.
const pcbRunning = new Map(); // tsx path -> kill fn (terminates the in-flight render's whole process group)

async function runPcbRender(tsxPath) {
  const scriptDir = path.dirname(tsxPath);
  const renderScript = path.join(scriptDir, "render-board.ts");
  if (!fs.existsSync(renderScript)) return; // no local renderer beside this board

  // Supersede an in-flight render of this board by killing its whole process GROUP, not
  // just the `bun render-board.ts` process. render-board spawns heavy `tsci export`
  // children; a bare kill of the parent (the old AbortController SIGKILL) orphans them —
  // SIGKILL is also uncatchable, so render-board's own run-lock child-reaper never runs.
  // On rapid saves the orphans pile up and thrash the machine. SIGTERM the group first
  // (render-board's handler reaps its tsci child + temp files and exits), then a delayed
  // SIGKILL backstops any straggler. The child spawns `detached` so it leads its own
  // group — signalling -pid hits render-board + tsci, never the dev server.
  pcbRunning.get(tsxPath)?.();

  console.log(`  ↪ rendering board: ${relForLog(tsxPath)}`);
  let killer = null;
  let superseded = false;
  try {
    const code = await new Promise((resolve, reject) => {
      const proc = spawn("bun", ["render-board.ts", path.basename(tsxPath)], {
        cwd: scriptDir,
        // stdout piped so we can catch the placement-preview sentinel; stderr still
        // inherited so tsci/render errors land in the dev log.
        stdio: ["ignore", "pipe", "inherit"],
        // Tag the run so render-board's single-flight lock can name us when it
        // supersedes (or is superseded by) a hand-run of the same board.
        env: { ...process.env, RENDER_SOURCE: "dev-server" },
        // Own process group so the supersede kill can reap render-board AND its tsci
        // children together. Must NOT share the dev server's group (we negative-pid kill).
        detached: true,
      });
      killer = () => {
        superseded = true;
        try { process.kill(-proc.pid, "SIGTERM"); } catch {}
        setTimeout(() => { try { process.kill(-proc.pid, "SIGKILL"); } catch {} }, 2000).unref();
      };
      pcbRunning.set(tsxPath, killer);
      // Two-phase render: render-board paints a fast placement preview, prints the
      // sentinel below, then runs the full routed render. Broadcast on the sentinel
      // so the viewer shows the preview immediately — the watcher ignores out/, so it
      // won't notice the write on its own. The post-close broadcast then swaps in the
      // full copper. (Non-sentinel stdout is dropped; render errors ride stderr.)
      let buf = "";
      proc.stdout.setEncoding("utf8");
      proc.stdout.on("data", (chunk) => {
        buf += chunk;
        let nl;
        while ((nl = buf.indexOf("\n")) !== -1) {
          const line = buf.slice(0, nl); buf = buf.slice(nl + 1);
          if (line.trim() === "RENDER_PHASE=placement" && !superseded) {
            const relFile = relForBroadcast(tsxPath);
            console.log(`  -> ${relFile} (placement preview)`);
            broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
          }
        }
      });
      proc.on("close", resolve);
      proc.on("error", reject);
    });
    // A superseded render was killed mid-flight — its out/ is half-written, so don't
    // broadcast it (a newer render is already running and will broadcast its own result).
    if (superseded) return;
    // Don't broadcast on a failed render — that would refresh the viewer onto
    // the previous (now stale) views and hide the failure (mirrors runScript).
    if (code !== 0) {
      console.log(`  ↪ board render failed (exit ${code})`);
      return;
    }
    const relFile = relForBroadcast(tsxPath);
    console.log(`  -> ${relFile}`);
    broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
    // The copper render is done and broadcast; now kick the slow 3D (GLB) rebuild off the
    // freshly-routed circuit-json render-board just wrote. Fire-and-forget so this path — and the
    // agents iterating the PCB — never waits on OCCT; the viewer hot-swaps the model when it lands.
    runBoard3d(tsxPath);
  } catch (e) {
    console.log(`  ↪ board render failed: ${e.message}`);
  } finally {
    if (pcbRunning.get(tsxPath) === killer) pcbRunning.delete(tsxPath);
  }
}

const glbRunning = new Map(); // tsx path -> kill fn for the in-flight background 3D (GLB) build

// Background 3D-assembly rebuild. board-3d.py turns the routed circuit-json into out/<board>.glb
// (the /3d viewer model) plus its face textures. It's SLOW — STEP model reads + OCCT meshing + a
// board-texture.ts pass — and purely a preview artifact, so it runs detached AFTER the copper
// render, never blocking it: a save's gerbers/preview land immediately and the GLB catches up a
// few seconds later, when the viewer hot-swaps it (live.js reloads on the .glb files-changed).
// It reads out/<board>.circuit.json (which render-board just wrote) directly, so it does NOT run a
// second autoroute. Single-flight per board: a newer save supersedes an in-flight build by killing
// its process GROUP (SIGTERM then a backstop SIGKILL), mirroring runPcbRender. Best-effort — any
// failure just leaves the previous GLB in place.
function runBoard3d(tsxPath) {
  const scriptDir = path.dirname(tsxPath);
  const py = path.join(scriptDir, "board-3d.py");
  if (!fs.existsSync(py)) return; // no 3D generator beside this board
  const board = path.basename(tsxPath).replace(/\.tsx$/, "");
  const cjRel = path.join("out", `${board}.circuit.json`);
  if (!fs.existsSync(path.join(scriptDir, cjRel))) return; // render-board writes this; without it board-3d.py would re-route

  glbRunning.get(tsxPath)?.(); // supersede an in-flight build of this board
  console.log(`  ↪ rebuilding 3D (GLB): ${relForLog(tsxPath)}`);
  let superseded = false;
  // Pass the .circuit.json target so board-3d.py skips ensure_circuit_json (no re-route). Own
  // process group so the supersede kill reaps board-3d.py AND its board-texture.ts child together.
  const proc = spawn(PYTHON_BIN, ["board-3d.py", cjRel], {
    cwd: scriptDir,
    stdio: ["ignore", "ignore", "inherit"], // progress/errors ride stderr into the dev log
    detached: true,
  });
  const killer = () => {
    superseded = true;
    try { process.kill(-proc.pid, "SIGTERM"); } catch {}
    setTimeout(() => { try { process.kill(-proc.pid, "SIGKILL"); } catch {} }, 2000).unref();
  };
  glbRunning.set(tsxPath, killer);
  proc.on("close", (code) => {
    if (glbRunning.get(tsxPath) === killer) glbRunning.delete(tsxPath);
    if (superseded || code !== 0) return;
    const relFile = relForBroadcast(path.join(scriptDir, "out", `${board}.glb`));
    console.log(`  -> ${relFile} (3D)`);
    broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
  });
  proc.on("error", (e) => {
    if (glbRunning.get(tsxPath) === killer) glbRunning.delete(tsxPath);
    console.log(`  ↪ 3D (GLB) rebuild failed to spawn: ${e.message}`);
  });
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
    const base = path.basename(p);
    return (
      seg.includes("__pycache__") ||
      seg.includes("node_modules") ||
      seg.includes("out") ||
      base.startsWith("_build-") ||
      base.startsWith("_build-") ||
      base.startsWith(".DS_Store")
    );
  },
  usePolling: true,
  interval: 200,
  binaryInterval: 400,
});
const debounce = new Map();

// Assembly deck (hardware/assembly/cards). Cards are hand-authored HTML, not a
// generated artifact, so there is nothing to re-run on an edit: the viewer loads
// the same file in an iframe and only needs to be told to re-frame it. An edit
// to the deck's shared style.css or to a render under img/ restyles or redraws
// cards we can't attribute, so those broadcast the whole deck instead of one
// file. Returns true when it claimed the path, so the listeners can bail.
//
// Wired to `add` as well as `change` — the deck grows a card at a time, and a
// card that appears while the grid is open should show up there without a
// reload (the client re-lists when a broadcast names a card it has no tile for).
function maybeBroadcastCard(absPath) {
  const relFile = relForBroadcast(absPath).split(path.sep).join("/");
  if (!isCardAssetPath(relFile)) return false;
  if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
  debounce.set(
    absPath,
    setTimeout(() => {
      debounce.delete(absPath);
      const single = isCardPath(relFile);
      const files = single ? [relFile] : walkAssemblyCards(HARDWARE_DIR).map((c) => c.path);
      if (files.length === 0) return;
      console.log(`Card changed: ${relFile}${single ? "" : ` -> refresh ${files.length} card(s)`}`);
      broadcast({ type: WS.FILES_CHANGED, files });
    }, 300),
  );
  return true;
}

watcher.on("add", (absPath) => { maybeBroadcastCard(absPath); });

watcher.on("change", (absPath) => {
  // Shared library changed — rebuild all scripts.
  if (absPath.includes("/cadlib/") && absPath.endsWith(".py")) {
    if (debounce.has("cadlib")) clearTimeout(debounce.get("cadlib"));
    debounce.set(
      "cadlib",
      setTimeout(async () => {
        debounce.delete("cadlib");
        console.log(`Shared lib changed: ${relForLog(absPath)}`);
        // A shared lib can feed anything, so rebuild every generator — but in
        // dependency order (producers before the scripts that load their STEPs),
        // each once, so a consumer isn't rebuilt against a stale input.
        for (const f of buildOrder(CONTENT_ROOTS)) {
          console.log(`  Rebuilding ${relForLog(f)}`);
          await runScript(f);
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
        broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
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
        broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
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
        broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
      }, 300),
    );
    return;
  }

  // Assembly card changed — broadcast update (see maybeBroadcastCard).
  if (maybeBroadcastCard(absPath)) return;

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
        broadcast({ type: WS.FILES_CHANGED, files: [relFile] });
      }, 300),
    );
    return;
  }

  // PCB source changed — re-render the board(s) it feeds and broadcast each so
  // the viewer refreshes the card + open modal. A board source renders itself; a
  // shared include (`parts.tsx`) follows the import chain to the boards
  // that pull it in (`pcba.tsx`), since the include has no `<board>` of its own.
  // (node_modules is already filtered by the watcher's `ignored`.)
  if (absPath.endsWith(".tsx") && absPath.split(path.sep).includes("pcb")) {
    // Skip build temp files (_build-*.tmp.tsx) written by the PCB render
    // pipeline so the watcher doesn't re-trigger on its own artifacts.
    if (path.basename(absPath).startsWith("_build-")) return;
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

  // Any .py change. The SEED scripts that must rebuild are:
  //   1. The file itself, if it's a runnable script (generator or drawing).
  //   2. Every other runnable script that transitively imports the file's
  //      module — covers shared `_foo.py` modules anywhere under hardware/, a
  //      generator that doubles as a base module (`bag_circuit_tray`, imported
  //      by the other trays), and the cross-tree case where `enclosure_assembly` feeds
  //      a drawing's `_appliance_model` → the `enclosure-iso-*` SVGs.
  // runWave then extends those seeds along STEP-load edges (the enclosures that
  // load the tray assemblies) and runs the lot once each, producers first.
  // The cadlib handler at the top of this listener is the shotgun version of
  // step 2: anything in `/cadlib/` rebuilds every generator, no walk.
  if (absPath.endsWith(".py")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(async () => {
        debounce.delete(absPath);
        const seeds = [];
        if (isRunnableScript(absPath)) seeds.push(absPath);
        for (const dep of findRunnableScriptsTransitivelyImporting(absPath, CONTENT_ROOTS)) {
          if (dep !== absPath) seeds.push(dep);
        }
        if (seeds.length === 0) return;
        console.log(`Changed: ${relForLog(absPath)}`);
        await queueWave(seeds);
      }, 500),
    );
    return;
  }
});

// --- Viewer source hot-reload ---
//
// The watcher above covers what the viewer SERVES (hardware artifacts). This
// covers the viewer's own render CODE: editing a hot-swappable detail module
// shows up live without a manual browser reload, the same in-place way an
// artifact change does. We broadcast CODE_CHANGED with a fresh token; the client
// (live.js) re-imports that module under the token and re-renders the open modal,
// keeping the camera / pan-zoom and the live scene.
//
// The hot set is the render modules the client knows how to re-import: the CAD
// leaf loaders (glb/step/dxf — loaders.js) and the self-contained PanZoom detail
// modules (mermaid/drawings/pcb — detail-shims.js). Scoped to those on purpose:
// a change to shared infra (scene.js, state.js), a detail sub-module
// (pcb-pick.js, pcb-edit.js), or the shell (main.js, grid.js, cad-detail.js)
// can't be swapped without rebuilding, so we don't pretend — those still need a
// manual refresh. express.static serves the edited file's new bytes on the next
// request, so no server restart is involved for client JS.
const VIEWER_JS_DIR = path.resolve(__dirname, "../public/js/viewer");
// keep in sync with loaders.js (CAD leaves) + detail-shims.js (PanZoom kinds)
const HOT_LEAVES = new Set(["glb.js", "step.js", "dxf.js", "mermaid.js", "drawings.js", "pcb.js"]);
const codeDebounce = new Map();
chokidar
  .watch(VIEWER_JS_DIR, { ignoreInitial: true, usePolling: true, interval: 200 })
  .on("change", (absPath) => {
    const base = path.basename(absPath);
    if (!HOT_LEAVES.has(base)) return;
    if (codeDebounce.has(base)) clearTimeout(codeDebounce.get(base));
    codeDebounce.set(
      base,
      setTimeout(() => {
        codeDebounce.delete(base);
        console.log(`Viewer code changed: ${relForLog(absPath)}`);
        broadcast({ type: WS.CODE_CHANGED, version: String(Date.now()) });
      }, 200),
    );
  });

console.log("Watching for changes...");
