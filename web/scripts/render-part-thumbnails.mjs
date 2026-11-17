// Draw the Parts page's stills from current model payloads. Run only when refreshing the stills.
import fs from "node:fs";
import path from "node:path";
import { spawnSync, execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { writeCatalogThumbnail } from "../../tools/render/catalog-thumbnail.mjs";
import { ensureRunLease } from "../../tools/run-slots.mjs";
import { FAUCET_FINISHES } from "../contracts/faucet-options.js";
import { instancesInScene } from "../contracts/material-instances.js";
import { matchesBody } from "../contracts/materials.js";
import { stepLocation } from "../contracts/step-locations.js";
import { readBomLines } from "../lib/bom-lines.js";
import { readMeshHeader } from "../lib/feature-catalog.js";
import { readMaterialCatalog } from "../lib/material-catalog.js";
import { partThumbnailDirectory, selectCatalogParts } from "../lib/parts-catalog.js";
import { encodeMeshPayload, writeBoardPayload } from "./part-thumbnail-board.mjs";

const root = fileURLToPath(new URL("../../", import.meta.url));
const hardware = path.join(root, "hardware");
const options = { finish: FAUCET_FINISHES[0].id };
const modelFiles = new Map();
const guideCover = path.join(hardware, "install-guide/install-guide.cover.png");
const boardModel = path.join(hardware, "pcb/pcba/out/pcba.glb");
const boardTexture = path.join(hardware, "pcb/pcba/out/pcba.top3d.png");

// These two installations share the ledger's same purchased screw.
const sharedScrew = { file: "faucet-layout/faucet-assembly.step", component: "base_screw_1" };

const partFraming = new Map([
  ["HSM-0001", { cam: [1, -1, 0.6], margin: 1.28 }],
  // Frame the visible faucet above the counter.
  ["HSM-0002", {
    cam: [-1, -1, 0.45], margin: 1.28, context: "drop",
    only: ["shell_*", "above_counter_plate", "lever", "faucet-display-cover-seated", "faucet_display", "faucet_display_screen"],
  }],
  ["HSM-0015", { cam: [1, -0.2, 0.44], margin: 1.36 }],
  // Center the drain tube's upper bend so its bore reads at the small catalog size.
  ["HSM-0108", { cam: [1, -0.18, 0.15], target: [0, -16, 188], span: 52 }],
  ["HSM-0537", { margin: 1.68 }],
]);

const finish = (names, color) => ({ names, color, roughness: 0.7 });
const kitFinishes = new Map([
  ["HSM-0133", [finish(["screw"], "#26282b")]],
  ["HSM-0354", [{ names: ["cell"], color: "#afb0ad", metalness: 0.62, roughness: 0.35 }]],
  ["HSM-0362", [{ names: ["washer"], color: "#a6a9b0", metalness: 0.68, roughness: 0.32 }]],
  ["HSM-0368", [finish(["cartridge"], "#f5f3ef"), finish(["quick-connect-*"], "#dfdcd6")]],
  ["HSM-0369", [finish(["tee-*"], "#ecebe5"), finish(["tee-bottom-*", "tee-top-*"], "#d6aa63"),
    finish(["tee-branch-quarter-turn-*", "tee-branch-lever-end"], "#506a93")]],
  ["HSM-0371", [finish(["*"], "#22262a"), finish(["prong-*", "ground"], "#b4a491")]],
  ["HSM-0373", [finish(["lower", "spine"], "#1245a5"), finish(["pages"], "#f3eee4"),
    { names: ["upper"], color: "#ffffff", texture: guideCover, unlit: true, tone_mapped: false }]],
]);

// The book's front cover uses its actual printed artwork on the planar cover of the guide model.
function textureBookCover(payload) {
  const source = fs.readFileSync(payload);
  const headerEnd = 4 + source.readUInt32LE(0);
  const header = JSON.parse(source.toString("utf8", 4, headerEnd));
  const body = header.meshes.find(mesh => mesh.name === "upper");
  const [start, count] = body.pos;
  const blob = source.subarray(headerEnd);
  const coords = Array.from({ length: count / 3 }, (_, i) => [0, 1].map(axis => blob.readFloatLE(start + (i * 3 + axis) * 4)));
  const axes = [0, 1].map(axis => {
    const values = coords.map(position => position[axis]);
    const low = Math.min(...values);
    return [low, Math.max(...values) - low];
  });
  const uv = Buffer.alloc(coords.length * 8);
  coords.forEach((position, i) => axes.forEach(([low, extent], axis) => {
    uv.writeFloatLE((position[axis] - low) / extent, (i * 2 + axis) * 4);
  }));
  body.uv = [blob.length, uv.length / 4];
  fs.writeFileSync(payload, encodeMeshPayload(header, [blob, uv]));
}

function sceneBodies(file) {
  if (!modelFiles.has(file)) {
    const mesh = path.join(hardware, `${file}.mesh`);
    modelFiles.set(file, fs.existsSync(mesh) ? readMeshHeader(mesh).meshes.map(body => body.name) : []);
  }
  return modelFiles.get(file);
}

function locationView({ file, component }) {
  const names = sceneBodies(file);
  if (!component) return names.length ? { step: file } : null;
  const only = names.filter(name => matchesBody(name, component)).map(name => name.replace(/\/\d+$/, ""));
  return only.length ? { step: file, only, context: "drop" } : null;
}

function partView(material, catalog, scenes) {
  for (const model of material.models || []) {
    if (model.context || (model.type && model.type !== "step")) continue;
    const view = locationView(stepLocation(model.file));
    if (view) return view;
  }
  if (material.id === "HSM-0138") {
    const view = locationView(sharedScrew);
    if (view) return { ...view, cam: [1, -1, -0.9] };
  }
  if (material.id === "HSM-0363") {
    const view = locationView({ file: "manifold-layout/enclosure-assembly.step", component: "funnel-frame-front-west-screw" });
    if (view) return { ...view, materials: [{ names: view.only, color: "#a6a9b0", metalness: 0.68, roughness: 0.32 }] };
  }
  for (const { owner, file, names } of scenes) {
    const [instance] = instancesInScene(catalog, owner, material.id, names, options);
    if (instance) return { step: file, only: instance.bodies, context: "drop" };
  }
  return null;
}

function makeJobs(catalog, materials, run) {
  const scenes = catalog.materials.flatMap(material => {
    if (!material.bom?.items?.length) return [];
    const model = material.models?.find(model => !model.context && (!model.type || model.type === "step"));
    if (!model) return [];
    const { file, component } = stepLocation(model.file);
    const names = sceneBodies(file);
    return component || !names.length ? [] : [{ owner: material.id, file, names }];
  });
  const jobs = [];
  for (const material of materials) {
    const kit = kitFinishes.get(material.id);
    const payload = path.join(run, `${material.id}.mesh`);
    const view = kit ? { payload, materials: kit }
      : material.pcb && fs.existsSync(boardModel) && fs.existsSync(boardTexture) ? boardView(payload)
      : partView(material, catalog, scenes);
    if (!view) continue;
    jobs.push({
      size: "240x240", cam: [1, -1, 0.85], frame: "look", ortho: true, margin: 1.48,
      transparent: true, fog: false, ground: false,
      ...view, ...partFraming.get(material.id), out: path.join(run, `${material.id}.png`),
    });
  }
  return jobs;
}

function boardView(payload) {
  writeBoardPayload(boardModel, payload);
  return { payload, cam: [0.6, -1, 1.25], materials: [
    { names: ["board"], color: "#d7f6e0", texture: boardTexture, roughness: 0.5 },
  ] };
}

async function main() {
  const selected = new Set(process.argv.slice(2));
  if ([...selected].some(id => !/^HSM-\d{4,}$/.test(id))) {
    throw new Error("Usage: node web/scripts/render-part-thumbnails.mjs [HSM-ID ...]");
  }
  ensureRunLease();
  const catalog = readMaterialCatalog(hardware);
  const groups = selectCatalogParts(catalog, readBomLines(hardware));
  const parts = [
    ...groups.machine.assemblies.filter(({ material }) => material),
    ...Object.values(groups).flatMap(scope => [...scope.madeToOrder, ...scope.offTheShelf]),
  ];
  const materials = [...new Map(parts.map(({ material }) => [material.id, material])).values()]
    .filter(material => !selected.size || selected.has(material.id));
  const scratch = path.join(root, ".cache/runs");
  fs.mkdirSync(scratch, { recursive: true });
  const run = fs.mkdtempSync(path.join(scratch, "parts-thumbnails-"));
  try {
    if (materials.some(material => kitFinishes.has(material.id))) {
      execFileSync("cargo", ["run", "--release", "--locked", "-j2", "--manifest-path", "tools/hsm/Cargo.toml",
        "-p", "hsm-kit-art", "--bin", "kit-art", "--", "--part-models", run], { cwd: root, stdio: "inherit" });
      textureBookCover(path.join(run, "HSM-0373.mesh"));
    }
    const jobs = makeJobs(catalog, materials, run);
    const manifest = path.join(run, "jobs.json");
    fs.writeFileSync(manifest, JSON.stringify(jobs));
    const render = spawnSync("hsm", ["render", "--root", root, "--jobs", manifest], {
      cwd: root, stdio: "inherit",
    });
    if (render.error) throw render.error;
    fs.mkdirSync(partThumbnailDirectory, { recursive: true });
    for (const job of jobs) {
      if (!fs.existsSync(job.out)) continue;
      const name = path.basename(job.out, ".png") + ".webp";
      const temporary = path.join(run, name);
      // An explicit span keeps the composed detail crop.
      if (job.span != null) {
        execFileSync("cwebp", ["-quiet", "-q", "84", job.out, "-o", temporary]);
      } else {
        await writeCatalogThumbnail(job.out, temporary);
      }
      fs.renameSync(temporary, path.join(partThumbnailDirectory, name));
    }
    const found = new Set(jobs.map(job => path.basename(job.out, ".png")));
    const missing = materials.filter(material => !found.has(material.id));
    for (const material of missing) console.log(`No model: ${material.id} ${material.description}`);
    process.exitCode = render.status === 0 ? 0 : 1;
  } finally {
    fs.rmSync(run, { recursive: true, force: true });
  }
}

await main();
