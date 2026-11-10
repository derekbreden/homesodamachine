// Explicit build fixtures inspect commands without starting compilers, renderers or publishers.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { main, runPrintBuild } from "../dev-server/build-all.js";

const silent = { log() {}, error() {} };
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-explicit-build-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, "tools/bazel"), { recursive: true });
  fs.mkdirSync(path.join(root, "hardware"));
  const graph = {};
  for (const [name, reads] of [["part", []], ["assembly", ["hardware/part.step"]]]) {
    const source = `hardware/${name}.rs`;
    fs.writeFileSync(path.join(root, source), "fn main() {}\n");
    graph[source] = { reads, writes: [`hardware/${name}.step`], rewritten: [], program: { crate: name, name, sources: [source] } };
  }
  fs.writeFileSync(path.join(root, "tools/bazel/graph.json"), JSON.stringify(graph));
  return root;
}

test("the default starts one wrapped progressive print build and no fabrication", async () => {
  const commands = [], projectRoot = "/fixture";
  const code = await main([], { projectRoot, output: silent, runCommand: async command => { commands.push(command); return { code: 0 }; },
    listBoards() { throw new Error("default must not discover PCB boards"); }, dirty() { throw new Error("default must not check stale outputs"); } });
  assert.equal(code, 0);
  assert.deepEqual(commands, [{ file: "/fixture/tools/run", args: ["--", "/fixture/tools/hsm/target/release/hsm-print-build", "--root", "/fixture", "--", "//:everything"], cwd: "/fixture" }]);
});

test("a selected native source reaches its declared downstream assembly", async t => {
  const projectRoot = fixture(t), commands = [];
  const code = await main(["--source", "hardware/part.rs"], { projectRoot, output: silent, runCommand: async command => { commands.push(command); return { code: 0 }; } });
  assert.equal(code, 0);
  assert.deepEqual(commands[0].args.slice(-2), ["//:assembly", "//:part"]);
});

test("listing has no process side effects", async t => {
  const projectRoot = fixture(t), lines = [];
  const code = await main(["--list"], { projectRoot, output: { log: line => lines.push(line) }, runCommand() { throw new Error("--list must not build"); } });
  assert.equal(code, 0);
  assert.deepEqual(lines, ["//:part hardware/part.rs", "//:assembly hardware/assembly.rs"]);
});

test("the explicitly requested stale report preserves preexisting dirty outputs", async () => {
  let readings = 0, builds = 0;
  const code = await main(["--check"], { projectRoot: "/fixture", output: silent,
    dirty: () => readings++ ? ["hardware/existing.step", "hardware/new.step"] : ["hardware/existing.step"],
    runCommand: async () => { builds++; return { code: 0 }; } });
  assert.equal(code, 1);
  assert.equal(builds, 1);
  assert.equal(readings, 2);
});

test("PCB fabrication is separate and its detailed model uses the native command", async () => {
  const commands = [];
  const code = await main(["--pcb"], { projectRoot: "/fixture", output: silent,
    listBoards: () => [{ source: "/fixture/hardware/pcb/pcba/pcba.tsx", dir: "/fixture/hardware/pcb/pcba" }],
    runCommand: async command => { commands.push(command); return { code: 0 }; } });
  assert.equal(code, 0);
  assert.equal(commands.length, 2);
  assert.deepEqual(commands[0].args, ["--", "bun", "render-board.ts", "pcba.tsx"]);
  assert.deepEqual(commands[1].args, ["--", "/fixture/tools/hsm/target/release/hsm-pcb", "--root", "/fixture", "model", "/fixture/hardware/pcb/pcba/out/pcba.circuit.json"]);
  assert.ok(commands.every(command => command.file === "/fixture/tools/run"));
  assert.ok(commands.every(command => !command.args.some(arg => arg.includes("hsm-print-build"))));
});

test("an editor rebuild retains native failure output", async t => {
  const projectRoot = fixture(t);
  const result = await runPrintBuild({ projectRoot, sources: ["hardware/part.rs"], capture: true,
    runCommand: async (_command, options) => { assert.equal(options.capture, true); return { code: 17, stderr: "native producer failed" }; } });
  assert.deepEqual(result, { code: 17, stderr: "native producer failed" });
});
