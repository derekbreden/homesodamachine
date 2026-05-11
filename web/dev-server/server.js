// Dev wrapper around the production server. Boots the shared HTTP server,
// then attaches the watcher, Python runner, and SSE broadcast for hot
// reload — everything that only makes sense locally.
//
// URL structure is identical to production: localhost:3000/ is the landing
// page, localhost:3000/3d is the parts viewer, /charts is the diagrams
// viewer, /blog is the Updates feed, and so on. The wrapper is purely
// additive — it does NOT change any routes. `dev: true` only changes the
// commit signal sent over SSE and skips the boot-time FCM push diff that
// fires on real deploys.
//
// The CadQuery scripts write atomically to their natural location next to
// the .py file (see hardware/_cadq_export.py), so this server doesn't
// redirect output into .viewer/steps/. Both this dev viewer and the
// public site read STEPs from the same place: hardware/.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import chokidar from "chokidar";

import { start } from "../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// dev-server lives at /web/dev-server; the cad-venv used to run
// generators lives at the repo root under tools/cad-venv.
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const PYTHON_BIN = path.join(PROJECT_ROOT, "tools", "cad-venv", "bin", "python");

const { broadcast, hardwareDir: HARDWARE_DIR } = await start({ dev: true });

// --- Script discovery ---
function findGenerateScripts() {
  const scripts = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (/generate_step.*\.py$/.test(entry.name)) scripts.push(full);
    }
  }
  walk(HARDWARE_DIR);
  return scripts;
}

// Find scripts that consume a given .step filename via cq.importers.importStep().
// In this project, STEP filenames are unique and importStep is the only way a
// .py script reads another script's output, so this heuristic is precise.
function findScriptsImportingStep(stepFilename) {
  const dependents = [];
  for (const script of findGenerateScripts()) {
    let source;
    try {
      source = fs.readFileSync(script, "utf-8");
    } catch {
      continue;
    }
    if (source.includes(stepFilename) && source.includes("importStep")) {
      dependents.push(script);
    }
  }
  return dependents;
}

// --- Script runner ---
const running = new Map(); // pyFilePath -> AbortController

async function runScript(pyFilePath) {
  console.log(`  ↪ running: ${path.relative(HARDWARE_DIR, pyFilePath)}`);
  if (running.has(pyFilePath)) {
    running.get(pyFilePath).abort();
    running.delete(pyFilePath);
  }
  const ac = new AbortController();
  running.set(pyFilePath, ac);

  const scriptDir = path.dirname(pyFilePath);
  const startTime = Date.now();
  const producedSteps = [];

  try {
    console.log(`  ↪ spawning: ${PYTHON_BIN} ${path.relative(PROJECT_ROOT, pyFilePath)}`);
    const code = await new Promise((resolve, reject) => {
      console.log(`  ↪ cwd: ${path.relative(PROJECT_ROOT, scriptDir)}`);
      const proc = spawn(PYTHON_BIN, [pyFilePath], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "ignore"],
        signal: ac.signal,
      });
      console.log(`  ↪ PID: ${proc.pid}`);
      proc.on("close", resolve);
      proc.on("error", reject);
      proc.on("message", (msg) => {
        console.log(`  [${path.basename(pyFilePath)}] ${msg}`);
      });
      proc.on("exit", (code) => {
        if (code !== 0) {
          reject(new Error(`Process exited with code ${code}`));
        }
      });
    });

    if (code !== 0) return;

    // Broadcast STEP files in scriptDir that were rewritten since startTime.
    // The atomic-write helper in hardware/_cadq_export.py renames into place,
    // so the mtime reflects the moment a complete file appeared. That same
    // helper also short-circuits when the new bytes match the existing file
    // exactly (timestamps are canonicalized first), so a no-op .py edit
    // produces no .step writes and nothing here broadcasts — which is the
    // right behavior, the file really hasn't changed.
    for (const entry of fs.readdirSync(scriptDir)) {
      if (!entry.endsWith(".step")) continue;
      const full = path.join(scriptDir, entry);
      if (fs.statSync(full).mtimeMs < startTime) continue;
      producedSteps.push(entry);
      const relFile = path.relative(HARDWARE_DIR, full);
      console.log(`  -> ${relFile}`);
      broadcast({ type: "files-changed", files: [relFile] });
    }
  } catch (e) {
    if (e.name === "AbortError") return;
    // Script failed — leave any prior committed STEP in place.
    console.log(`  ↪ failed: ${e.message}`);
  } finally {
    running.delete(pyFilePath);
  }

  if (producedSteps.length === 0) return;

  // Cascade: rebuild scripts that import the STEPs we just produced.
  const dependents = new Set();
  for (const stepName of producedSteps) {
    for (const depScript of findScriptsImportingStep(stepName)) {
      if (depScript === pyFilePath) continue;
      dependents.add(depScript);
    }
  }
  for (const depScript of dependents) {
    console.log(`  ↪ dependent: ${path.relative(HARDWARE_DIR, depScript)}`);
    await runScript(depScript);
  }
}

// --- File watcher ---
const watcher = chokidar.watch(HARDWARE_DIR, { ignoreInitial: true });
const debounce = new Map();

watcher.on("change", (absPath) => {
  // Shared library changed — rebuild all scripts.
  if (absPath.includes("/cadlib/") && absPath.endsWith(".py")) {
    if (debounce.has("cadlib")) clearTimeout(debounce.get("cadlib"));
    debounce.set(
      "cadlib",
      setTimeout(async () => {
        debounce.delete("cadlib");
        console.log(`Shared lib changed: ${path.relative(HARDWARE_DIR, absPath)}`);
        for (const f of findGenerateScripts()) {
          console.log(`  Rebuilding ${path.relative(HARDWARE_DIR, f)}`);
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
        const relFile = path.relative(HARDWARE_DIR, absPath);
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
        const relFile = path.relative(HARDWARE_DIR, absPath);
        console.log(`DXF changed: ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // Sidecar metadata file changed — broadcast a change for the part it
  // belongs to. `foo.dxf.json` -> broadcast `foo.dxf`; `foo.step.json`
  // -> broadcast `foo.step`. The viewer's hsm:files-changed handler
  // refetches the part and its updated thickness (since /api/dxf
  // returns sidecar fields in the same response). See hardware/PARTS.md.
  if (absPath.endsWith(".dxf.json") || absPath.endsWith(".step.json")) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        const baseAbs = absPath.replace(/\.json$/, "");
        const relFile = path.relative(HARDWARE_DIR, baseAbs);
        console.log(`Sidecar changed: ${path.relative(HARDWARE_DIR, absPath)} -> refresh ${relFile}`);
        broadcast({ type: "files-changed", files: [relFile] });
      }, 300),
    );
    return;
  }

  // generate_step*.py changed — re-run that script.
  if (/generate_step.*\.py$/.test(absPath)) {
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(() => {
        debounce.delete(absPath);
        console.log(`Changed: ${path.relative(HARDWARE_DIR, absPath)}`);
        runScript(absPath);
      }, 500),
    );
    return;
  }

  // Shared private module (e.g. `_foam_bag_geometry.py`) changed — find
  // every generator that imports it by module name and re-run those. The
  // cadlib handler above is a coarser version of the same idea: anything
  // in /cadlib/ rebuilds every generator. This handler is the targeted
  // version for shared modules that sit alongside a small set of related
  // generators (like the three foam-bag-shell / foam-cap / copper-plugs
  // siblings that all import `_foam_bag_geometry`). Without this handler,
  // editing such a module would silently fail to trigger rebuilds.
  if (absPath.endsWith(".py")) {
    const moduleName = path.basename(absPath, ".py");
    if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
    debounce.set(
      absPath,
      setTimeout(async () => {
        debounce.delete(absPath);
        const importRe = new RegExp(`(?:^|\\s)(?:from|import)\\s+${moduleName}\\b`, "m");
        const dependents = [];
        for (const script of findGenerateScripts()) {
          let source;
          try {
            source = fs.readFileSync(script, "utf-8");
          } catch {
            continue;
          }
          if (importRe.test(source)) dependents.push(script);
        }
        if (dependents.length === 0) return;
        console.log(`Shared module changed: ${path.relative(HARDWARE_DIR, absPath)}`);
        for (const dep of dependents) {
          console.log(`  Rebuilding ${path.relative(HARDWARE_DIR, dep)}`);
          await runScript(dep);
        }
      }, 500),
    );
    return;
  }
});

console.log("Watching for changes...");
