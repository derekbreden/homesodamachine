// The local server broadcasts completed outputs and viewer code; builds run on explicit requests.
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import chokidar from "chokidar";
import { start } from "../server.js";
import { mountPcbEditorRoutes } from "../lib/pcb-editor-routes.js";
import { mountStepEditorRoutes } from "../lib/step-editor-routes.js";
import { nativeBuildPlan, buildTargetsForSources, viewerOutput } from "./deps.js";
import { runPrintBuild } from "./build-all.js";
import { WS } from "../contracts/ws-frames.js";
import { isPublishedDocument } from "../contracts/documents.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const NO_WATCH = process.argv.includes("--no-watch");
const { app, broadcast, hardwareDir: HARDWARE_DIR } = await start({ dev: true });

mountPcbEditorRoutes(app, HARDWARE_DIR);

function stamp(file) {
  try { const stat = fs.statSync(file); return `${stat.ino}:${stat.size}:${stat.mtimeMs}`; }
  catch { return null; }
}

// The closed STEP editor retains an explicit native rebuild callback for an authored editable producer.
async function rebuildStepAssembly(sourcePath) {
  try {
    const plan = nativeBuildPlan(PROJECT_ROOT);
    const targets = new Set(buildTargetsForSources([sourcePath], PROJECT_ROOT, plan));
    const outputs = [...plan.producers.values()].filter(producer => targets.has(producer.label)).flatMap(producer => [...producer.writes]);
    const before = new Map(outputs.map(file => [file, stamp(path.join(PROJECT_ROOT, file))]));
    const result = await runPrintBuild({ projectRoot: PROJECT_ROOT, sources: [sourcePath], capture: true });
    // Explicit editor requests also refresh a viewer started with --no-watch.
    const files = [...new Set(outputs.filter(file => stamp(path.join(PROJECT_ROOT, file)) !== before.get(file))
      .map(file => viewerOutput(path.join(PROJECT_ROOT, file), HARDWARE_DIR)).filter(Boolean))];
    if (files.length) broadcast({ type: WS.FILES_CHANGED, files });
    if (result.code !== 0) {
      const reason = result.stderr.split("\n").map(line => line.trim()).filter(Boolean).at(-1) || `Native print build exited ${result.code}`;
      return { ok: false, error: reason };
    }
    return { ok: true };
  } catch (error) { return { ok: false, error: error.message }; }
}

mountStepEditorRoutes(app, { hardwareDir: HARDWARE_DIR }, rebuildStepAssembly);

// Output polling notices each completed producer while the native build continues.
const WATCH_OPTS = {
  ignoreInitial: true,
  ignored: file => {
    const segments = file.split(path.sep), base = path.basename(file);
    return segments.some(segment => ["node_modules", "target", ".git", ".cache", ".cad-cache", "__pycache__"].includes(segment))
      || base.startsWith("_build-") || base.startsWith(".DS_Store") || base.endsWith(".tmp");
  },
  usePolling: true,
  interval: 200,
  binaryInterval: 400,
};
const debounce = new Map();

function onContentChange(absPath) {
  const file = viewerOutput(absPath, HARDWARE_DIR);
  if (!file) return;
  if (file.endsWith(".pdf") && (!isPublishedDocument(file) || !fs.existsSync(path.join(HARDWARE_DIR, file + ".json")))) return;
  if (debounce.has(file)) clearTimeout(debounce.get(file));
  debounce.set(file, setTimeout(() => {
    debounce.delete(file);
    console.log(`Output changed: ${file}`);
    broadcast({ type: WS.FILES_CHANGED, files: [file] });
  }, 300));
}

// The viewer reimports only the render leaves its live scene knows how to replace.
const VIEWER_JS_DIR = path.resolve(__dirname, "../public/js/viewer");
const HOT_LEAVES = new Set(["glb.js", "step.js", "dxf.js", "mermaid.js", "pcb.js"]);
const codeDebounce = new Map();
function onViewerCodeChange(absPath) {
  const base = path.basename(absPath);
  if (!HOT_LEAVES.has(base)) return;
  if (codeDebounce.has(base)) clearTimeout(codeDebounce.get(base));
  codeDebounce.set(base, setTimeout(() => {
    codeDebounce.delete(base);
    console.log(`Viewer code changed: ${path.relative(PROJECT_ROOT, absPath)}`);
    broadcast({ type: WS.CODE_CHANGED, version: String(Date.now()) });
  }, 200));
}

if (NO_WATCH) {
  console.log("Not watching (--no-watch): reload to read output changes.");
} else {
  const watcher = chokidar.watch([HARDWARE_DIR], WATCH_OPTS);
  watcher.on("add", onContentChange);
  watcher.on("change", onContentChange);
  watcher.on("unlink", onContentChange);
  chokidar.watch(VIEWER_JS_DIR, { ignoreInitial: true, usePolling: true, interval: 200 }).on("change", onViewerCodeChange);
  console.log("Watching completed outputs and viewer code. Builds run when requested.");
}
