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
const watcher = chokidar.watch("**/*generate_step_cadquery*.py", {
  cwd: HARDWARE_DIR,
  ignoreInitial: true,
});

const debounce = new Map();
watcher.on("change", (relPath) => {
  const abs = path.join(HARDWARE_DIR, relPath);
  if (debounce.has(abs)) clearTimeout(debounce.get(abs));
  debounce.set(
    abs,
    setTimeout(() => {
      debounce.delete(abs);
      console.log(`Changed: ${relPath}`);
      runScript(abs);
    }, 500)
  );
});

// --- Initial build ---
async function buildAll() {
  const glob = (await import("node:fs")).readdirSync;
  // Find all matching .py files
  const pyFiles = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (/generate_step_cadquery.*\.py$/.test(entry.name)) pyFiles.push(full);
    }
  }
  walk(HARDWARE_DIR);

  console.log(`Building ${pyFiles.length} scripts...`);
  for (const f of pyFiles) {
    console.log(`  ${path.relative(HARDWARE_DIR, f)}`);
    await runScript(f);
  }
  console.log("Initial build complete.");
}

// --- Start ---
server.listen(PORT, async () => {
  console.log(`Step viewer: http://localhost:${PORT}`);
  await buildAll();
  console.log("Watching for changes...");
});
