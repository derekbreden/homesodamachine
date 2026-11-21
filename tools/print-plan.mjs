#!/usr/bin/env node
// print-plan publishes a plate prepared by enclosure-print-prep as its part's print plan: the
// Print tab's replay and its catalog entry, the plan record beside the plate folder, and the
// plate's project and sliced archive in the print archive.
//
//   node tools/print-plan.mjs PLATE_DIR --material HSM-0081 [--title "..."] [--object NAME]
//        [--name ARCHIVE_NAME] [--dry-run]
//
// PLATE_DIR is the folder the preparer wrote: preparation.json, review.json and
// project-check.json beside the project and the sliced archive. The plate has to have been
// sliced and to pass its review, and its mesh, project and archive have to be the bytes the
// preparation names. `--object` picks the part on a plate that carries several.
//
// The replay is `hsm-gcode view playback --inline --data` of the whole plate, kept gzipped under
// its own SHA-256 in print-playbacks/. The catalog entry keeps its `process` lines, which are
// written by hand, and takes the title it had unless `--title` gives one. The replay it replaces
// stays one publish longer, named in the record, because the site serves it until it reads the new
// catalog; the next publish removes it when no entry names it. The record is print-plan.json in
// the folder above PLATE_DIR.
// Publishing the same plate again changes nothing. `--dry-run` encodes the replay, prints the
// entry and the record, and changes nothing.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { gunzipSync, gzipSync } from "node:zlib";
import { maxReplayBytes } from "../web/lib/print-playback.js";

const USAGE = "Usage: node tools/print-plan.mjs PLATE_DIR --material HSM-NNNN [--title TITLE] [--object NAME] [--name ARCHIVE_NAME] [--dry-run]";
const root = fileURLToPath(new URL("../", import.meta.url));
const CATALOG = "print-playbacks/catalog.json";

const sha256 = file => createHash("sha256").update(readFileSync(file)).digest("hex");
const read = file => JSON.parse(readFileSync(file, "utf8"));
const text = value => JSON.stringify(value, null, 2) + "\n";
const digest = bytes => createHash("sha256").update(bytes).digest("hex");

function options(argv) {
  const found = { paths: [] };
  for (let at = 0; at < argv.length; at += 1) {
    const argument = argv[at];
    if (argument === "--dry-run") found.dryRun = true;
    else if (["--material", "--title", "--object", "--name"].includes(argument)) found[argument.slice(2)] = argv[at += 1];
    else found.paths.push(argument);
  }
  if (found.paths.length !== 1 || !/^HSM-\d+$/.test(found.material ?? "")) throw new Error(USAGE);
  return found;
}

try {
  const chosen = options(process.argv.slice(2));
  const plate = path.relative(root, path.resolve(chosen.paths[0]));
  process.chdir(root);
  const [prep, review, check] = ["preparation", "review", "project-check"].map(name => read(`${plate}/${name}.json`));
  if (!prep.sliced || !review.pass || !check.pass) throw new Error(`${plate} is not a sliced plate that passes its review`);
  const part = chosen.object ? prep.objects.find(object => object.name === chosen.object)
    : prep.objects.length === 1 ? prep.objects[0] : null;
  if (!part) throw new Error(`Name the plate's part with --object: ${prep.objects.map(object => object.name).join(", ")}`);
  for (const [file, expected] of [[part.stl, part.stl_sha256], [prep.project, prep.project_sha256], [prep.archive, prep.archive_sha256]]) {
    if (sha256(file) !== expected) throw new Error(`${file} is not the file this plate was prepared from`);
  }

  const catalog = read(CATALOG);
  const previous = catalog[chosen.material];
  const title = chosen.title ?? previous?.title;
  if (!title) throw new Error(`${chosen.material} has no catalog entry yet: give its --title`);
  const plateNumber = previous?.plate ?? 1;

  mkdirSync(".cache/runs", { recursive: true });
  const scratch = mkdtempSync(".cache/runs/print-plan-");
  let replay;
  try {
    execFileSync("tools/run", ["--", "hsm-gcode", "view", "playback", prep.archive, "--plate", String(plateNumber),
      "--layers", "all", "--inline", "--data", "--title", title, "--out", `${scratch}/replay.json`], { stdio: ["ignore", "inherit", "inherit"] });
    replay = readFileSync(`${scratch}/replay.json`);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
  if (replay.length > maxReplayBytes) throw new Error(`The replay is ${replay.length} bytes; the site reads at most ${maxReplayBytes}`);
  const hash = digest(replay);
  const head = execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim();

  // The same plate published again keeps the commits its entry and record already name.
  const again = previous?.sha256 === hash && previous.archive_sha256 === prep.archive_sha256 && previous.recipe_sha256 === prep.spec_sha256;
  const entry = {
    ...previous,
    title, sha256: hash, slice: prep.archive, plate: plateNumber, recipe: prep.spec, recipe_target: prep.piece,
    recipe_sha256: prep.spec_sha256, project_sha256: prep.project_sha256, archive_sha256: prep.archive_sha256,
    gcode_sha256: prep.gcode_sha256, kind: "plan", layers: review.layers, model_sha256: part.stl_sha256,
    recipe_commit: (again && previous.recipe_commit) || head,
  };
  catalog[chosen.material] = entry;
  const before = previous?.sha256;
  const unnamed = sha => Boolean(sha) && Object.values(catalog).every(other => other.sha256 !== sha);

  const folder = path.dirname(plate);
  const earlier = existsSync(`${folder}/print-plan.json`) ? read(`${folder}/print-plan.json`) : null;
  // A new replay leaves the one it replaces in place and removes the one the publish before left.
  const fresh = before !== hash;
  const kept = fresh ? (unnamed(before) ? before : null) : earlier?.replaced_replay_sha256 ?? null;
  const left = fresh && unnamed(earlier?.replaced_replay_sha256) ? earlier.replaced_replay_sha256 : null;
  const within = file => path.relative(folder, file);
  const beside = suffix => part.stl.replace(/\.stl$/, suffix);
  const optional = (key, file) => (file && existsSync(file) ? { [key]: file, [`${key}_sha256`]: sha256(file) } : {});
  const record = {
    purpose: `Bind the current ${prep.piece} mesh to its production project, native slice and published replay.`,
    piece: prep.piece,
    material_id: chosen.material,
    printer: prep.printer,
    connection_key: prep.connection_key,
    status: "prepared",
    prepared_utc: prep.prepared_utc,
    source_revision: (earlier?.archive_sha256 === prep.archive_sha256 && earlier.replay_sha256 === hash && earlier.source_revision) || head,
    material: prep.material,
    nozzle: prep.nozzle,
    bed_type: prep.bed_type,
    requested_z_trim_mm: prep.requested_z_trim_mm,
    emitted_z_trim_commands_mm: review.emitted_z_trim_mm,
    recipe: prep.spec,
    recipe_sha256: prep.spec_sha256,
    profile: prep.profile,
    profile_sha256: prep.profile_sha256,
    source_stl: part.stl,
    source_stl_sha256: part.stl_sha256,
    ...optional("source_fine_archive", beside(".step.npz")),
    ...optional("print_regions", part.regions?.record),
    archive: within(prep.archive),
    archive_sha256: prep.archive_sha256,
    gcode_sha256: prep.gcode_sha256,
    project: within(prep.project),
    project_sha256: prep.project_sha256,
    preparation: within(`${plate}/preparation.json`),
    native_review: within(`${plate}/review.json`),
    support_audits: readdirSync(plate).filter(name => /^support-audit-.*\.json$/.test(name)).sort().map(name => within(`${plate}/${name}`)),
    layers: review.layers,
    estimated_seconds: prep.estimated_seconds,
    minimum_bead_bed_margin_mm: review.minimum_bed_margin_mm,
    native_slicer_warnings: prep.slicer_warnings ?? [],
    project_source_mesh_checks: check.objects,
    ...optional("print_features", beside(".print-features.json")),
    replay_sha256: hash,
    replay: `print-playbacks/${hash}.json.gz`,
    ...(kept ? { replaced_replay_sha256: kept } : {}),
  };

  const archiveName = chosen.name ?? `${prep.piece}-${prep.printer.toLowerCase()}`;
  const archive = ["tools/print-archive.mjs", "add", archiveName, prep.project, prep.archive];
  if (chosen.dryRun) {
    console.log(text({ [chosen.material]: entry }) + text(record));
    execFileSync("node", [...archive, "--dry-run"], { stdio: "inherit" });
    console.log(`replay ${hash} · ${replay.length} bytes${before ? ` · the catalog names ${before}` : ""}`);
    if (left) console.log(`would remove print-playbacks/${left}.json.gz`);
  } else {
    const packed = `print-playbacks/${hash}.json.gz`;
    if (!existsSync(packed) || digest(gunzipSync(readFileSync(packed))) !== hash) writeFileSync(packed, gzipSync(replay, { level: 9 }));
    writeFileSync(CATALOG, text(catalog));
    if (left) rmSync(`print-playbacks/${left}.json.gz`, { force: true });
    writeFileSync(`${folder}/print-plan.json`, text(record));
    execFileSync("node", archive, { stdio: "inherit" });
    console.log(`${packed}\n${CATALOG} · ${chosen.material}\n${folder}/print-plan.json${left ? `\nremoved print-playbacks/${left}.json.gz` : ""}`);
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
