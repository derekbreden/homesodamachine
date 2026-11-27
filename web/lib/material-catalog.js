import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { materialHash } from "../contracts/material-tabs.js";

// Associates published board views with their material workspaces.
const PCB_MATERIALS = new Map([["HSM-0048", "pcb/pcba/pcba.tsx"]]);

export function readMaterialCatalog(hardwareDir) {
  const catalog = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/materials.json"), "utf8"));
  for (const material of catalog.materials) {
    const board = PCB_MATERIALS.get(material.id);
    if (board) material.pcb = board;
    const imported = material.bom?.imports;
    if (!imported) continue;
    const sourcePath = path.resolve(hardwareDir, imported.source);
    if (!sourcePath.startsWith(path.resolve(hardwareDir) + path.sep)) throw new Error("Invalid material source");
    const source = JSON.parse(fs.readFileSync(sourcePath, "utf8"));
    for (const group of ["parts", "hardware"]) for (const part of source[group] || []) {
      const mapping = imported[group]?.[part.name];
      if (!mapping) continue;
      const { relationship, ...binding } = mapping;
      const item = { ...binding, quantity: part.quantity, unit: "ea", note: part.role, source: imported.source };
      if (relationship) (material.relations ||= []).push({ ...item, kind: relationship });
      else material.bom.items.push(item);
    }
    delete material.bom.imports;
  }
  return catalog;
}

export function pcbMaterialHash(source) {
  for (const [id, board] of PCB_MATERIALS) {
    if (!source || source === board) return materialHash(id, { view: "pcb" });
  }
  return null;
}

// MATERIAL NUMBERS. A record's id holds a number given to that material alone. The register holds
// the highest number ever allocated and the numbers of materials that have left the catalog;
// `node tools/material-number.mjs` allocates from it and materialNumberProblems holds every record to it.
const CATALOG = "ledger/materials.json";
export const ALLOCATED = "ledger/materials.allocated.json";
const TAKE_NEXT = "Take the next number with `node tools/material-number.mjs`";

export const materialId = (number) => "HSM-" + String(number).padStart(4, "0");

// The number an id carries when it is written as materials.md's Identity gives it, else null.
export function materialNumber(id) {
  const match = /^HSM-(\d+)$/.exec(id ?? "");
  return match && materialId(Number(match[1])) === id ? Number(match[1]) : null;
}

const byNumber = (ids) => [...new Set(ids)].sort((a, b) => materialNumber(a) - materialNumber(b));
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));

// What keeps a record from its number: an id that is no material number, a retired number, one
// above the highest allocated, or one two records share.
export function materialNumberProblems(catalog, numbers) {
  const highest = materialNumber(numbers.highest), retired = new Set(numbers.retired);
  const named = (material) => `${material.id} (${material.description})`;
  const holders = new Map(), problems = [];
  for (const material of catalog.materials) {
    const number = materialNumber(material.id);
    if (number === null) problems.push(`${named(material)} is not a material number. ${TAKE_NEXT}.`);
    else if (retired.has(material.id))
      problems.push(`${named(material)} is retired, the number of a material that has left the catalog. ${TAKE_NEXT}; a material that returns keeps its own number, out of \`retired\` in hardware/${ALLOCATED}.`);
    else if (number > highest)
      problems.push(`${named(material)} is above ${numbers.highest}, the highest number allocated. ${TAKE_NEXT}.`);
    if (number !== null) holders.set(number, [...(holders.get(number) || []), material]);
  }
  for (const [number, held] of holders)
    if (held.length > 1)
      problems.push(`${materialId(number)} is held by ${held.length} records: ${held.map((m) => m.description).join("; ")}. ${TAKE_NEXT} for all but one.`);
  return problems;
}

// The numbers of records committed since the register last changed that HEAD no longer holds:
// materials that have left the catalog since. The next allocation records them as retired.
export function retiredSinceRegister(hardwareDir) {
  const run = (cwd, args) => execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], maxBuffer: 1 << 30 });
  let root;
  try { root = run(hardwareDir, ["rev-parse", "--show-toplevel"]).trim(); } catch { return []; }
  const git = (...args) => { try { return run(root, args); } catch { return ""; } };
  const catalog = path.relative(root, path.join(hardwareDir, CATALOG));
  const last = git("log", "-1", "--format=%H", "--", path.relative(root, path.join(hardwareDir, ALLOCATED))).trim();
  if (!last) return [];
  const blobAt = (rev) => git("rev-parse", "--verify", "-q", `${rev}:${catalog}`).trim();
  const ids = (blob) => { try { return JSON.parse(git("cat-file", "blob", blob)).materials.map((m) => m.id); } catch { return []; } };
  const lastAndParents = git("rev-list", "--parents", "-n", "1", last).trim().split(" ");
  const versionsSince = git("log", "-m", "--format=", "--raw", "--no-abbrev", "--no-renames", `${last}..HEAD`, "--", catalog)
    .split("\n").map((line) => line.split(/\s+/)[3]);
  const held = new Set(ids(blobAt("HEAD"))), left = new Set();
  for (const blob of new Set([...lastAndParents.map(blobAt), ...versionsSince]))
    if (blob && !/^0+$/.test(blob)) for (const id of ids(blob)) if (materialNumber(id) !== null && !held.has(id)) left.add(id);
  return byNumber([...left]);
}

// The register as the rule reads it, with the retirements committed since it last changed.
export function materialNumbers(hardwareDir) {
  const register = readJson(path.join(hardwareDir, ALLOCATED));
  return { ...register, retired: byNumber([...register.retired, ...retiredSinceRegister(hardwareDir)]) };
}

// The rule applied to the checkout's catalog.
export function checkMaterialNumbers(hardwareDir) {
  return materialNumberProblems(readJson(path.join(hardwareDir, CATALOG)), materialNumbers(hardwareDir));
}

// Allocates the next number above the highest allocated and above every record's, and records it
// in the register with the retirements committed since the register last changed. Allocations in
// one checkout take turns on `lock`. Returns the number and what the catalog's records still break.
export function allocateMaterialNumber(hardwareDir, lock) {
  return holding(lock, () => {
    const file = path.join(hardwareDir, ALLOCATED);
    const register = readJson(file), catalog = readJson(path.join(hardwareDir, CATALOG));
    if (materialNumber(register.highest) === null) throw new Error(`hardware/${ALLOCATED} names no highest number.`);
    const recorded = new Set(catalog.materials.map((m) => m.id)), retired = retiredSinceRegister(hardwareDir);
    const next = Math.max(...[register.highest, ...register.retired, ...recorded].map((id) => materialNumber(id) ?? 0)) + 1;
    register.highest = materialId(next);
    register.retired = byNumber([...register.retired, ...retired.filter((id) => !recorded.has(id))]);
    const temporary = `${file}.${process.pid}.tmp`;
    try {
      fs.writeFileSync(temporary, JSON.stringify(register, null, 2) + "\n");
      fs.renameSync(temporary, file);
    } finally {
      fs.rmSync(temporary, { force: true });
    }
    return { id: register.highest, problems: materialNumberProblems(catalog, { ...register, retired: byNumber([...register.retired, ...retired]) }) };
  });
}

// A lock file names its holder's process; one whose holder has gone is taken over.
function holding(lock, work) {
  fs.mkdirSync(path.dirname(lock), { recursive: true });
  const deadline = Date.now() + 10_000;
  let descriptor;
  for (;;) {
    try {
      descriptor = fs.openSync(lock, "wx");
      break;
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
      if (abandoned(lock)) fs.rmSync(lock, { force: true });
      else if (Date.now() > deadline) throw new Error(`Another allocation holds ${lock}; retry in a moment.`);
      else Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 50);
    }
  }
  try {
    fs.writeFileSync(descriptor, String(process.pid));
    return work();
  } finally {
    fs.closeSync(descriptor);
    fs.rmSync(lock, { force: true });
  }
}

function abandoned(lock) {
  try {
    const pid = Number(fs.readFileSync(lock, "utf8"));
    if (!pid) return Date.now() - fs.statSync(lock).mtimeMs > 10_000;
    process.kill(pid, 0);
    return false;
  } catch (error) {
    return error.code === "ESRCH";
  }
}
