// Dev wrapper around the production server. Boots the shared HTTP server in
// dev mode (viewer at /), then attaches the watcher, Python runner, and
// WebSocket broadcast — everything that only makes sense locally.
//
// The CadQuery scripts now write atomically to their natural location next to
// the .py file (see hardware/_cadq_export.py), so this server no longer
// redirects output into .viewer/steps/. Both this dev viewer and the public
// site read STEPs from the same place: hardware/.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import chokidar from "chokidar";

import { start } from "../../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const PYTHON_BIN = path.join(PROJECT_ROOT, "tools", "cad-venv", "bin", "python");

function isIgnoredPath(p) {
  return p.includes(`${path.sep}plan-b${path.sep}`);
}

const { broadcast, hardwareDir: HARDWARE_DIR } = await start({ dev: true });

// --- Script discovery ---
function findGenerateScripts() {
  const scripts = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (isIgnoredPath(full)) continue;
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
    const code = await new Promise((resolve, reject) => {
      const proc = spawn(PYTHON_BIN, [pyFilePath], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "ignore"],
        signal: ac.signal,
      });
      proc.on("close", resolve);
      proc.on("error", reject);
    });

    if (code !== 0) return;

    // Broadcast STEP files in scriptDir that were rewritten since startTime.
    // The atomic-write helper renames into place, so the mtime reflects the
    // moment a complete file appeared.
    for (const entry of fs.readdirSync(scriptDir)) {
      if (!entry.endsWith(".step")) continue;
      const full = path.join(scriptDir, entry);
      if (fs.statSync(full).mtimeMs < startTime) continue;
      producedSteps.push(entry);
      const relFile = path.relative(HARDWARE_DIR, full);
      console.log(`  -> ${relFile}`);
      broadcast({ type: "updated", file: relFile });
    }
  } catch (e) {
    if (e.name === "AbortError") return;
    // Script failed — leave any prior committed STEP in place.
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
  if (isIgnoredPath(absPath)) return;

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
        broadcast({ type: "mermaid-updated", file: relFile });
      }, 300),
    );
    return;
  }

  // generate_step*.py changed — re-run that script.
  if (!/generate_step.*\.py$/.test(absPath)) return;
  if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
  debounce.set(
    absPath,
    setTimeout(() => {
      debounce.delete(absPath);
      console.log(`Changed: ${path.relative(HARDWARE_DIR, absPath)}`);
      runScript(absPath);
    }, 500),
  );
});

console.log("Watching for changes...");
