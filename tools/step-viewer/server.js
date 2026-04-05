import { createServer } from "http";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import express from "express";
import chokidar from "chokidar";
import { WebSocketServer } from "ws";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const HARDWARE_DIR = path.join(PROJECT_ROOT, "hardware");
const VIEWER_DIR = path.join(PROJECT_ROOT, ".viewer", "steps");
const PYTHON_BIN = path.join(PROJECT_ROOT, "tools", "cad-venv", "bin", "python");
const WRAPPER_SCRIPT = path.join(__dirname, "run_redirected.py");
const PORT = process.env.PORT || 3000;

// Ensure output dir exists
fs.mkdirSync(VIEWER_DIR, { recursive: true });

// --- Express ---
const app = express();
app.use(express.static(path.join(__dirname, "public")));
app.use("/steps", express.static(VIEWER_DIR));

app.get("/api/steps", (_req, res) => {
  const files = [];
  function walk(dir, rel) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) walk(path.join(dir, entry.name), path.join(rel, entry.name));
      else if (entry.name.endsWith(".step")) files.push(path.join(rel, entry.name));
    }
  }
  if (fs.existsSync(VIEWER_DIR)) walk(VIEWER_DIR, "");
  res.json(files);
});

const server = createServer(app);

// --- WebSocket ---
const wss = new WebSocketServer({ server });

function broadcast(msg) {
  const data = JSON.stringify(msg);
  for (const client of wss.clients) {
    if (client.readyState === 1) client.send(data);
  }
}

// --- Script runner ---
const running = new Map(); // pyFilePath -> AbortController

async function runScript(pyFilePath) {
  // Kill previous run of the same script
  if (running.has(pyFilePath)) {
    running.get(pyFilePath).abort();
    running.delete(pyFilePath);
  }

  const ac = new AbortController();
  running.set(pyFilePath, ac);

  const scriptDir = path.dirname(pyFilePath);
  const relDir = path.relative(HARDWARE_DIR, scriptDir);
  const destDir = path.join(VIEWER_DIR, relDir);
  fs.mkdirSync(destDir, { recursive: true });

  const startTime = Date.now();

  try {
    const code = await new Promise((resolve, reject) => {
      const proc = spawn(PYTHON_BIN, [WRAPPER_SCRIPT, pyFilePath, destDir], {
        cwd: scriptDir,
        stdio: ["ignore", "ignore", "ignore"],
        signal: ac.signal,
      });
      proc.on("close", resolve);
      proc.on("error", reject);
    });

    if (code !== 0) return;

    // Broadcast any .step files written to destDir since startTime
    for (const entry of fs.readdirSync(destDir)) {
      if (!entry.endsWith(".step")) continue;
      if (fs.statSync(path.join(destDir, entry)).mtimeMs < startTime) continue;
      const relFile = path.join(relDir, entry);
      console.log(`  -> ${relFile}`);
      broadcast({ type: "updated", file: relFile });
    }
  } catch (e) {
    if (e.name === "AbortError") return;
    // Script failed — do nothing
  } finally {
    running.delete(pyFilePath);
  }
}

// --- File watcher ---
const watcher = chokidar.watch(HARDWARE_DIR, {
  ignoreInitial: true,
});

// Collect all generate_step*.py paths for rebuild-all on shared lib changes
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

const debounce = new Map();
watcher.on("change", (absPath) => {
  // Shared library changed — rebuild all scripts
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
      }, 500)
    );
    return;
  }

  if (!/generate_step.*\.py$/.test(absPath)) return;
  if (debounce.has(absPath)) clearTimeout(debounce.get(absPath));
  debounce.set(
    absPath,
    setTimeout(() => {
      debounce.delete(absPath);
      console.log(`Changed: ${path.relative(HARDWARE_DIR, absPath)}`);
      runScript(absPath);
    }, 500)
  );
});

// --- Initial build ---
async function buildAll() {
  const pyFiles = findGenerateScripts();
  console.log(`Building ${pyFiles.length} scripts...`);
  for (const f of pyFiles) {
    console.log(`  ${path.relative(HARDWARE_DIR, f)}`);
    await runScript(f);
  }
  console.log("Initial build complete.");
}

// --- Clean viewer dir ---
async function cleanViewerDir() {
  if (!fs.existsSync(VIEWER_DIR)) return;
  for (const entry of fs.readdirSync(VIEWER_DIR, { withFileTypes: true })) {
    const full = path.join(VIEWER_DIR, entry.name);
    if (entry.isDirectory()) fs.rmSync(full, { recursive: true });
    else fs.unlinkSync(full);
  }
}

// --- Start ---
server.listen(PORT, async () => {
  console.log(`Step viewer: http://localhost:${PORT}`);
  await cleanViewerDir();
  await buildAll();
  console.log("Watching for changes...");
});
