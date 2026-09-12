// The tube audit is tied to the geometry and routing source it was sampled from.
// Hashes are cached by file stat; opening the panel never starts a CAD build.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

export const TUBE_ASSEMBLY = "manifold-layout/enclosure-assembly.step";
const SHA256 = /^[a-f0-9]{64}$/;
const REQUIRED_INPUTS = ["hardware/scripts/tube_routes.py", "hardware/scripts/_routing.py",
  "hardware/manifold-layout/enclosure_assembly.py", "hardware/printed-parts/cold-core/_cold_core_interface.py"];
const hashes = new Map();
const object = (x) => x !== null && typeof x === "object" && !Array.isArray(x);
const xyz = (x) => Array.isArray(x) && x.length === 3 && x.every(Number.isFinite);

function digest(file) {
  try {
    const stat = fs.statSync(file);
    const key = `${stat.size}:${stat.mtimeMs}:${stat.ctimeMs}`;
    const cached = hashes.get(file);
    if (cached?.key === key) return cached.hash;
    const hash = crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
    hashes.set(file, { key, hash });
    return hash;
  } catch { return null; }
}

function payloadSource(file) {
  let fd;
  try {
    fd = fs.openSync(file, "r");
    const length = Buffer.alloc(4);
    if (fs.readSync(fd, length, 0, 4, 0) !== 4) return null;
    const n = length.readUInt32LE();
    if (!n || n > 2 * 1024 * 1024) return null;
    const raw = Buffer.alloc(n);
    if (fs.readSync(fd, raw, 0, n, 4) !== n) return null;
    return JSON.parse(raw.toString("utf8")).src || null;
  } catch { return null; }
  finally { if (fd !== undefined) fs.closeSync(fd); }
}

function inside(root, relative) {
  if (typeof relative !== "string" || path.isAbsolute(relative)) return null;
  const file = path.resolve(root, relative);
  return file.startsWith(root + path.sep) ? file : null;
}

export function tubeDataErrors(data) {
  const errors = [];
  if (data?.version !== 1) errors.push("Unsupported tube-data version.");
  if (!data?.source || !SHA256.test(data.source.step_sha256 || "")) errors.push("Missing assembly source digest.");
  if (!SHA256.test(data?.source?.payload_src || "")) errors.push("Missing viewer source digest.");
  if (!SHA256.test(data?.source?.payload_sha256 || "")) errors.push("Missing viewer surface digest.");
  if (!object(data?.source?.inputs) || !Object.keys(data.source.inputs).length ||
      Object.values(data.source.inputs).some((hash) => !SHA256.test(hash))) errors.push("Missing routing input digests.");
  if (REQUIRED_INPUTS.some((file) => !SHA256.test(data?.source?.inputs?.[file] || ""))) {
    errors.push("The tube exporter, routing and anchor sources need fingerprints.");
  }
  if (!Array.isArray(data?.runs) || !data.runs.length) errors.push("No tube routes are recorded.");
  const ids = new Set();
  for (const run of Array.isArray(data?.runs) ? data.runs : []) {
    if (!object(run)) { errors.push("Invalid tube route."); continue; }
    if (typeof run.id !== "string" || !run.id || ids.has(run.id)) errors.push("Tube names must be unique.");
    ids.add(run.id);
    if (!Array.isArray(run.points) || run.points.length < 2 || run.points.length > 10000 ||
        run.points.some((p) => !xyz(p))) {
      errors.push(`${run.id}: invalid centreline.`);
    }
    if (!(Number.isFinite(run.radius_mm) && run.radius_mm > 0)) errors.push(`${run.id}: invalid tube radius.`);
    if (!Array.isArray(run.s) || run.s.length !== run.points?.length || run.s[0] !== 0 ||
        run.s.some((s, i) => !Number.isFinite(s) || (i > 0 && s <= run.s[i - 1]))) {
      errors.push(`${run.id}: invalid arc-length coordinates.`);
    }
    const length = Array.isArray(run.s) ? run.s.at(-1) : 0;
    if (!Array.isArray(run.holds)) errors.push(`${run.id}: invalid restraints.`);
    for (const hold of Array.isArray(run.holds) ? run.holds : []) {
      if (!object(hold) || !Number.isFinite(hold.s) || hold.s < 0 || hold.s > length) {
        errors.push(`${run.id}: restraint outside the tube.`);
      } else if (!xyz(hold.point) || !xyz(hold.tangent) || !(Math.hypot(...hold.tangent) > 0) ||
          !Number.isFinite(hold.clamp_length_mm) || hold.clamp_length_mm < 0) {
        errors.push(`${run.id}: invalid restraint geometry.`);
      }
    }
  }
  return errors;
}

export function readTubeRoutes(hardwareDir) {
  const root = path.resolve(hardwareDir, "..");
  const file = path.join(root, "web/public/tube-routes.json");
  if (!fs.existsSync(file)) return { code: 404, body: { error: "Tube route data has not been generated for this assembly." } };
  let data;
  try { data = JSON.parse(fs.readFileSync(file, "utf8")); }
  catch { return { code: 503, body: { error: "Tube route data is unreadable. Regenerate the tube audit." } }; }
  const errors = tubeDataErrors(data);
  if (errors.length) return { code: 503, body: { error: "Tube route data is invalid.", detail: errors } };
  const staleReasons = [];
  const model = path.join(hardwareDir, TUBE_ASSEMBLY);
  if (digest(model) !== data.source.step_sha256) staleReasons.push("The assembly STEP has changed since the tube audit was generated.");
  if (payloadSource(model + ".mesh") !== data.source.payload_src) staleReasons.push("The viewer model has a different source from this tube audit.");
  if (data.source.payload_sha256 && digest(model + ".mesh") !== data.source.payload_sha256) {
    staleReasons.push("The displayed assembly surface has changed since the tube audit was generated.");
  }
  for (const [relative, hash] of Object.entries(data.source.inputs || {})) {
    const input = inside(root, relative);
    if (!input || !SHA256.test(hash) || digest(input) !== hash) staleReasons.push(`Routing input changed: ${relative}`);
  }
  return { code: 200, body: { ...data, status: staleReasons.length ? "stale" : "current", staleReasons } };
}

export function mountTubeRoutes(app, { hardwareDir }) {
  app.get("/api/tube-routes/*splat", (req, res) => {
    if (req.params.splat.join("/") !== TUBE_ASSEMBLY) return res.status(404).json({ error: "No tube audit for this model." });
    res.set("Cache-Control", "no-store");
    const { code, body } = readTubeRoutes(hardwareDir);
    res.status(code).json(body);
  });
}
