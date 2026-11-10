// Explicit local builds use the native progressive print driver and a separate requested PCB path.
import path from "node:path";
import { spawn, execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { contentRoots, nativeBuildPlan, buildTargetsForSources, buildOrder } from "./deps.js";
import { walkPcbBoards } from "../lib/walk.js";

const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

export function printBuildCommand(projectRoot, targets = []) {
  return {
    file: path.join(projectRoot, "tools/run"),
    args: ["--", path.join(projectRoot, "tools/hsm/target/release/hsm-print-build"), "--root", projectRoot, "--", ...(targets.length ? targets : ["//:everything"])],
    cwd: projectRoot,
  };
}

function processRun(command, { capture = false, spawnProcess = spawn } = {}) {
  return new Promise(resolve => {
    let stderr = "";
    const child = spawnProcess(command.file, command.args, {
      cwd: command.cwd, stdio: ["ignore", "inherit", capture ? "pipe" : "inherit"],
      env: { ...process.env, ...command.env, HSM_BUILD_SOURCE: "dev-server (explicit build)" },
    });
    if (capture && child.stderr) {
      child.stderr.setEncoding("utf8");
      child.stderr.on("data", text => { stderr = (stderr + text).slice(-8000); });
    }
    child.once("error", error => resolve({ code: 1, stderr: (stderr + error.message).slice(-8000) }));
    child.once("close", code => resolve({ code: code ?? 1, stderr }));
  });
}

export function runPrintBuild({ projectRoot = PROJECT_ROOT, sources = [], capture = false, runCommand = processRun } = {}) {
  const targets = sources.length ? buildTargetsForSources(sources, projectRoot) : [];
  return runCommand(printBuildCommand(projectRoot, targets), { capture });
}

function pcbBoards(projectRoot) {
  return contentRoots(projectRoot).flatMap(root => [...walkPcbBoards(root)].map(board => ({
    source: path.join(root, board.source), dir: path.join(root, path.dirname(board.source)),
  })));
}

// PCB fabrication runs only when explicitly selected and keeps its detailed native board model.
export function pcbCommands(projectRoot, board) {
  const wrapper = path.join(projectRoot, "tools/run");
  const name = path.basename(board.source, ".tsx");
  return [
    { file: wrapper, args: ["--", "bun", "render-board.ts", path.basename(board.source)], cwd: board.dir, env: { RENDER_SOURCE: "build-all (explicit PCB)" } },
    { file: wrapper, args: ["--", path.join(projectRoot, "tools/hsm/target/release/hsm-pcb"), "--root", projectRoot, "model", path.join(board.dir, "out", `${name}.circuit.json`)], cwd: board.dir },
  ];
}

function dirtyOutputs(projectRoot) {
  const roots = contentRoots(projectRoot);
  if (!roots.length) return [];
  const output = execFileSync("git", ["status", "--porcelain=v1", "-z", "--", ...roots], { cwd: projectRoot });
  const fields = output.toString("utf8").split("\0"), paths = [];
  for (let at = 0; at < fields.length && fields[at]; at++) {
    const status = fields[at].slice(0, 2);
    paths.push(fields[at].slice(3));
    if (status.includes("R") || status.includes("C")) at++;
  }
  return paths;
}

export async function main(argv = process.argv.slice(2), {
  projectRoot = PROJECT_ROOT, runCommand = processRun, dirty = dirtyOutputs,
  listBoards = pcbBoards, output = console,
} = {}) {
  let list = false, check = false, pcb = false;
  const sources = [];
  for (let at = 0; at < argv.length; at++) {
    switch (argv[at]) {
      case "--list": list = true; break;
      case "--check": check = true; break;
      case "--pcb": pcb = true; break;
      case "--source":
        if (!argv[at + 1] || argv[at + 1].startsWith("--")) throw new Error("--source requires a declared producer or input path");
        sources.push(argv[++at]); break;
      case "--help": case "-h":
        output.log("Usage: node dev-server/build-all.js [--list] [--check] [--source SOURCE ...]\n       node dev-server/build-all.js --pcb [--list] [--check]\nThe default is the native progressive print build. PCB fabrication is explicit.");
        return 0;
      default: throw new Error(`Unknown build option ${argv[at]}`);
    }
  }
  if (pcb && sources.length) throw new Error("Select the print build's sources or the separate PCB build");
  if (list) {
    if (pcb) for (const board of listBoards(projectRoot)) output.log(path.relative(projectRoot, board.source));
    else {
      const plan = nativeBuildPlan(projectRoot);
      const selected = sources.length ? new Set(buildTargetsForSources(sources, projectRoot, plan)) : null;
      for (const producer of buildOrder(plan)) if (!selected || selected.has(producer.label)) output.log(`${producer.label} ${producer.sources.join(" ")}`);
    }
    return 0;
  }
  const before = check ? new Set(dirty(projectRoot)) : null;
  let failed = 0;
  if (pcb) {
    for (const board of listBoards(projectRoot)) for (const command of pcbCommands(projectRoot, board)) {
      const result = await runCommand(command);
      if (result.code !== 0) { output.error(`PCB build failed: ${path.relative(projectRoot, board.source)} (${result.code})`); failed++; break; }
    }
  } else {
    const result = await runPrintBuild({ projectRoot, sources, runCommand });
    if (result.code !== 0) { output.error(`Print build failed (${result.code}).`); failed++; }
  }
  const stale = check ? dirty(projectRoot).filter(file => !before.has(file)) : [];
  if (stale.length) {
    output.log("Outputs regenerated by the requested build:");
    for (const file of stale) output.log(`  ${file}`);
  }
  output.log(failed ? "Requested build failed." : check ? stale.length ? "Requested build completed with stale outputs regenerated." : "Requested build completed; nothing stale." : "Requested build completed.");
  return failed || stale.length ? 1 : 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then(code => { process.exitCode = code; }).catch(error => { console.error(error.message); process.exitCode = 1; });
}
