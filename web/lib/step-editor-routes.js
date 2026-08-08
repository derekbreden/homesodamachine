// Dev-only write-back API for the 3D viewer's component editor
// (web/public/js/viewer/component-edit.js). Mirrors the PCB editor
// (lib/pcb-editor-routes.js): mounted ONLY by the dev server, so it 404s in
// production and the viewer's "Edit" toggle never appears on the public site.
//
// A component move is stored in a JSON sidecar beside the assembly's .step, and
// the assembly's GENERATOR is what applies it: each move composes onto the seat
// its body took, at placement time, so the body's own stations ride it and every
// body seated on it follows. The sidecar is written FIRST, synchronously, so the
// move is in the tree the instant Apply lands; the generator re-run that follows
// only catches the geometry up. Only a genuine generator error fails, and its
// text comes back to the panel.
//
// Only files in EDITABLE are editable — the registry both scopes the write (no
// arbitrary path gets a generator run) and gates the toggle (an unknown file
// 404s, so the viewer hides Edit). The override schema per component:
//   { translate: [dx, dy, dz], rotate: { axis: [x, y, z], deg: <number> } }
// both optional; a component with neither (or an all-zero move) is dropped.

import fs from "fs";
import path from "path";

import { editionRoot } from "./editions.js";

// step file (as the viewer references it, relative to the content root) →
// the generator that rebuilds it. The overrides sidecar sits beside the .step,
// same basename with `.overrides.json`.
//
// EMPTY. An entry belongs here only when its generator READS that sidecar and
// applies the moves as it places — the route writes the file and re-runs the
// generator, and nothing else carries the edit into the geometry. No generator
// in the tree reads one: `hardware/manifold-layout/enclosure_assembly.py`, which builds
// the enclosure assembly, seats every body from its own source. So nothing is
// editable, every route below 404s, and the viewer hides the Edit toggle.
const EDITABLE = {};

function entryFor(file) {
  return Object.prototype.hasOwnProperty.call(EDITABLE, file) ? EDITABLE[file] : null;
}

function overridesPathFor(hardwareDir, file) {
  return path.join(hardwareDir, file.replace(/\.step$/i, ".overrides.json"));
}

function generatorPathFor(hardwareDir, file, entry) {
  return path.join(hardwareDir, path.dirname(file), entry.generator);
}

function readOverrides(p) {
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf-8"));
    return data && typeof data === "object" && !Array.isArray(data) ? data : {};
  } catch {
    return {};
  }
}

// A finite number, else null. Guards the JSON body against NaN/strings.
function num(v) {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

function cleanVec3(v) {
  if (!Array.isArray(v) || v.length !== 3) return null;
  const out = v.map(num);
  return out.every((c) => c !== null) ? out : null;
}

// Normalize one component's override; returns a compact override object, or null
// when the move is empty (no translate + no rotation) so the entry is dropped.
function cleanOverride(body) {
  const out = {};
  const t = cleanVec3(body.translate);
  if (t && t.some((c) => c !== 0)) out.translate = t;
  const r = body.rotate;
  if (r && typeof r === "object") {
    const axis = cleanVec3(r.axis);
    const deg = num(r.deg);
    if (axis && deg !== null && deg % 360 !== 0 && axis.some((c) => c !== 0)) {
      out.rotate = { axis, deg };
    }
  }
  return Object.keys(out).length ? out : null;
}

/**
 * Mount the dev-only step-editor API.
 * @param app express app
 * @param editionDirs every edition's content root, keyed by id (lib/editions.js).
 *   Resolved PER REQUEST, not once at mount: the editable path below is relative
 *   to a content root and the editions mirror each other's filenames, so a root
 *   fixed at mount time sends every edit into the default edition's tree no
 *   matter which machine the viewer is showing.
 * @param rebuild async (generatorPath) => { ok, error } — runs the generator,
 *   captures failure output, and broadcasts the new .step on success. Supplied
 *   by the dev server, which owns the Python runner + the WebSocket.
 */
export function mountStepEditorRoutes(app, { editionDirs }, rebuild) {
  const rootFor = (req) => editionRoot(req, editionDirs);

  // Current overrides for a file (the editor loads these on open so the panel
  // shows a component's live offset). 404 if the file isn't editable — the
  // viewer uses that to decide whether to show the Edit toggle at all.
  app.get("/api/step-editor/overrides", (req, res) => {
    const file = String(req.query.file || "");
    const entry = entryFor(file);
    if (!entry) return res.status(404).json({ error: "not editable" });
    res.json({ file, overrides: readOverrides(overridesPathFor(rootFor(req), file)) });
  });

  // Write (or clear) one component's override, then rebuild. Body:
  //   { file, component, translate?, rotate?, clear? }
  app.post("/api/step-editor/override", async (req, res) => {
    const { file, component } = req.body || {};
    const entry = entryFor(String(file || ""));
    if (!entry) return res.status(404).json({ error: "not editable" });
    if (!component || typeof component !== "string") {
      return res.status(400).json({ error: "missing component" });
    }

    const hardwareDir = rootFor(req);
    const ovPath = overridesPathFor(hardwareDir, file);
    const overrides = readOverrides(ovPath);
    if (req.body.clear) {
      delete overrides[component];
    } else {
      const clean = cleanOverride(req.body);
      // Append the move as another step (the editor sends a delta from the pose
      // it's showing — the just-applied geometry after a reload). Steps compose
      // in order, each rotate about the then-current centre, so iterative edits
      // accumulate instead of the last one replacing the rest. A zeroed move
      // adds nothing.
      if (clean) {
        const prior = overrides[component];
        const list = Array.isArray(prior) ? prior : prior ? [prior] : [];
        list.push(clean);
        overrides[component] = list;
      }
    }

    // Snapshot so a failed rebuild rolls the sidecar back to the last good
    // state — otherwise a move that clashed would stay in the file and poison
    // the next Apply (which appends onto it). The viewer keeps showing the
    // attempted move as a local preview; the source just doesn't record it.
    const before = snapshot(ovPath);
    writeOverrides(ovPath, overrides);
    const result = await rebuild(generatorPathFor(hardwareDir, file, entry));
    if (!result.ok) restore(ovPath, before);
    res.json({ ok: result.ok, error: result.error || null, overrides: result.ok ? overrides : readOverrides(ovPath) });
  });

  // Clear every override for a file (Reset all), then rebuild.
  app.delete("/api/step-editor/overrides", async (req, res) => {
    const file = String((req.body && req.body.file) || req.query.file || "");
    const entry = entryFor(file);
    if (!entry) return res.status(404).json({ error: "not editable" });
    const hardwareDir = rootFor(req);
    writeOverrides(overridesPathFor(hardwareDir, file), {});
    const result = await rebuild(generatorPathFor(hardwareDir, file, entry));
    res.json({ ok: result.ok, error: result.error || null, overrides: {} });
  });
}

// Empty sidecar → remove the file (so a clean tree carries no zero-content
// artifact); otherwise pretty-print it, matching the repo's JSON sidecars.
function writeOverrides(p, overrides) {
  if (!Object.keys(overrides).length) {
    try { fs.unlinkSync(p); } catch {}
    return;
  }
  fs.writeFileSync(p, JSON.stringify(overrides, null, 2) + "\n", "utf-8");
}

// Raw-text snapshot of the sidecar (null if absent), and its restore — used to
// roll back a write whose rebuild failed.
function snapshot(p) {
  try { return fs.readFileSync(p, "utf-8"); } catch { return null; }
}
function restore(p, snap) {
  if (snap === null) { try { fs.unlinkSync(p); } catch {} }
  else fs.writeFileSync(p, snap, "utf-8");
}
