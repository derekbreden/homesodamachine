import express from "express";
import path from "path";
import fs from "fs";

import { walkFiles, walkPcbBoards, walkDocuments } from "./walk.js";
import { DOC_SIDECAR_SUFFIX, isPublishedDocument } from "../contracts/documents.js";
import { VIEW_REQUEST_RE, PICKS_REQUEST_RE } from "../contracts/pcb-out.js";
import { sidecarFields } from "../contracts/sidecar.js";
import { SCORECARD_SUFFIX } from "../contracts/scorecard-sidecar.js";
import { mountPdfjsAssets, renderDocumentReader } from "./document-reader.js";
import { readMaterialCatalog } from "./material-catalog.js";
import { numberedModels } from "../contracts/materials.js";
import { readPartCosts } from "./part-costs.js";
import { websitePointers } from "../contracts/artifact-scope.js";
import { RETIRED_MARKER } from "./retired.js";
import { madeFrom } from "./made-from.js";

const relOf = (req) => req.params.splat.join("/");

// WHAT `hardwareDir` IS ALLOWED TO BE. `send` refuses any path with a dot-prefixed component,
// and `start({ hardwareDir })` exists so the render tools can point this at a git worktree's
// own `hardware/` — a worktree that lives under `.claude/worktrees/…` and is therefore exactly
// such a path. The traversal guard is `safeFile`, which resolves under `hardwareDir` and
// nowhere else; this only stops `send` from second-guessing the root it was handed.
const SEND_OPTS = { dotfiles: "allow" };

function safeFile(rootDir, rel, ext) {
  if (rel.includes("..")) return null;
  const abs = path.join(rootDir, rel);
  if (!abs.startsWith(rootDir + path.sep) || !abs.endsWith(ext)) return null;
  return abs;
}

// Read the JSON sidecar (`<file>.json`) next to a part, if present.
// Documented in hardware/README.md; used by /api/dxf today, available to
// future BOM / render tooling. Returns null on any failure (missing,
// malformed) — callers treat null as "no metadata" and fall back.
function readSidecar(rootDir, rel) {
  try {
    const abs = path.join(rootDir, rel + ".json");
    if (!fs.existsSync(abs)) return null;
    return JSON.parse(fs.readFileSync(abs, "utf-8"));
  } catch {
    return null;
  }
}

// The viewer serves hardware/, and every path below resolves against it.
//
// Endpoints + response shapes: web/contracts/api-shapes.js.
export function mountViewerRoutes(app, { hardwareDir, store, pointersPath }) {
  mountPdfjsAssets(app);

  // Public deployments expose catalog models. Local render servers also read
  // temporary, unnumbered scene inputs without publishing them.
  function publishedFile(rel, pointers = null) {
    if (!process.env.RENDER_GIT_COMMIT) return true;
    for (let parent = path.dirname(rel); ; parent = path.dirname(parent)) {
      if (fs.existsSync(path.join(hardwareDir, parent, RETIRED_MARKER))) return false;
      if (parent === ".") break;
    }
    try {
      pointers ||= JSON.parse(fs.readFileSync(pointersPath, "utf8"));
      const key = "hardware/" + rel;
      if (key in (pointers.website?.solids ?? {}) || key in (pointers.website?.sidecars ?? {})) return true;
      const model = rel.replace(/\.step\.(mesh|json)$/, ".step")
        .replace(/\.(scorecard|facts|frame)\.json$/, ".step");
      return numberedModels(readMaterialCatalog(hardwareDir), [model]).length > 0;
    } catch { return false; }
  }

  app.get("/api/materials", (_req, res) => {
    res.set("Cache-Control", "no-cache");
    let catalog;
    try { catalog = readMaterialCatalog(hardwareDir); }
    catch (error) { return res.status(503).json({ error: "Material catalog unavailable" }); }
    // Costs ride with the catalog; a checkout without the ledgers serves parts uncosted.
    try { catalog.costs = readPartCosts(hardwareDir, catalog); } catch { catalog.costs = null; }
    res.json(catalog);
  });

  // WHERE THE PAGE FETCHES A MODEL'S BYTES, when the store has a public address. Every member
  // the pointer file names is on the store under the hash of its own bytes, so a URL built
  // from that hash names those bytes and no others: the browser caches it forever, and the
  // edge serves it without this container in the path. `base` is null where the store carries
  // no such address — a laptop, a test, a signed-URL store — and the page reads `/steps`,
  // `/meshes` and `/models` off this disk as it always does.
  //
  // The map is keyed the way the page names a file, which is a path under hardware/.
  app.get("/api/objects", (_req, res) => {
    const base = store?.publicUrl || null;
    if (!base || !pointersPath) return res.json({ base: null, objects: {} });
    let pointers;
    try {
      pointers = JSON.parse(fs.readFileSync(pointersPath, "utf-8"));
    } catch {
      return res.json({ base: null, objects: {} });
    }
    const prefix = pointers.store?.objects ?? pointers.release?.objects;
    if (!prefix) return res.json({ base: null, objects: {} });
    const objects = {};
    for (const [rel, hash] of Object.entries(websitePointers(pointers).solids ?? {})) {
      if (!rel.startsWith("hardware/")) continue;
      if (!/\.(step|step\.mesh|glb)$/.test(rel)) continue;
      if (!publishedFile(rel.slice("hardware/".length), pointers)) continue;
      objects[rel.slice("hardware/".length)] = `${base}/${prefix}${hash}.gz`;
    }
    res.json({ base, objects });
  });

  // The models a part number names. Local tools can inspect a catalog-free fixture.
  app.get("/api/steps", (req, res) => {
    const files = walkFiles(hardwareDir, ".step");
    let catalog = null;
    try { catalog = readMaterialCatalog(hardwareDir); } catch { /* listed whole */ }
    res.json(catalog ? numberedModels(catalog, files) : process.env.RENDER_GIT_COMMIT ? [] : files);
  });

  app.get("/api/glbs", (req, res) => {
    res.json(walkFiles(hardwareDir, ".glb").filter(rel => publishedFile(rel)));
  });

  app.get("/api/mermaid", (req, res) => {
    res.json(walkFiles(hardwareDir, ".mmd"));
  });

  // PCB boards with their three rendered copper views (see walkPcbBoards).
  app.get("/api/pcb", (req, res) => {
    res.json(walkPcbBoards(hardwareDir));
  });

  // Documents: the PDFs the site hands over whole (see walkDocuments and
  // web/contracts/documents.js). Each
  // entry carries what it is called, how many pages it runs to, how big the
  // file is, and the cover to show for it.
  app.get("/api/documents", (req, res) => {
    res.set("Cache-Control", "no-cache");
    res.json(walkDocuments(hardwareDir));
  });

  // Old external links have a permanent retirement response, even if an
  // earlier artifact bundle still has a deck on disk.
  app.get("/cards/*splat", (_req, res) => {
    res.status(410).send("Assembly cards are archived. Letter shop guides are on /guides.");
  });

  app.get("/api/dxf", (req, res) => {
    const paths = walkFiles(hardwareDir, ".dxf");
    // Return enriched objects so the client gets the sidecar metadata
    // (thickness_mm, material, etc.) in the same round-trip — the
    // viewer needs thickness to extrude. See hardware/README.md.
    res.json(paths.map((p) => ({ path: p, ...sidecarFields(readSidecar(hardwareDir, p)) })));
  });

  app.get("/api/mermaid-content/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".mmd");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.type("text/plain").send(fs.readFileSync(abs, "utf-8"));
  });

  // PCB view SVG content. Only the rendered board views under a `pcb/.../out/`
  // directory are reachable — the fixed Top/Bottom/Overlay plus any inner
  // copper planes (inner1, inner2, …) — not arbitrary SVGs that may live
  // elsewhere in the tree.
  app.get("/api/pcb-content/*splat", (req, res) => {
    const rel = relOf(req);
    const abs = safeFile(hardwareDir, rel, ".svg");
    if (!abs) return res.status(400).send("Invalid path");
    if (!VIEW_REQUEST_RE.test(rel)) {
      return res.status(400).send("Not a board view");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    // These views are re-rendered live (the watcher rewrites out/ on every board
    // save). Without a cache directive the browser is free to heuristically cache
    // the SVG and serve a stale copy on reload — Safari does, so a re-render only
    // shows up over the live-reload socket, never on refresh. no-cache keeps the
    // ETag (cheap 304s) but forces revalidation, so a reload always gets the
    // current copper.
    res.set("Cache-Control", "no-cache");
    res.type("image/svg+xml").send(fs.readFileSync(abs, "utf-8"));
  });

  // PCB pad-picker data — the distilled pads + identity for one board (see
  // hardware/pcb/pcba/pick-data.ts). Same `pcb/.../out/` confinement as the
  // view content, restricted to the `.picks.json` the distiller writes.
  app.get("/api/pcb-picks/*splat", (req, res) => {
    const rel = relOf(req);
    const abs = safeFile(hardwareDir, rel, ".json");
    if (!abs) return res.status(400).send("Invalid path");
    if (!PICKS_REQUEST_RE.test(rel)) {
      return res.status(400).send("Not pick data");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    // Re-rendered in lockstep with the views above — same no-cache so the pad
    // picker's hit targets don't lag a stale render.
    res.set("Cache-Control", "no-cache");
    res.type("application/json").send(fs.readFileSync(abs, "utf-8"));
  });

  // The 3D-model scorecard sidecar — the requirements verdict beside a STEP
  // (e.g. enclosure-assembly.scorecard.json, written by enclosure_assembly.py). Read by
  // the 3D viewer's scorecard bar + modal (public/js/viewer/scorecard-3d.js). Confined to
  // *.scorecard.json under hardware/; a 404 is normal — a model with no scorecard
  // just gets no bar. no-cache so a live regen isn't shown stale.
  app.get("/api/step-scorecard/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), SCORECARD_SUFFIX);
    if (!abs) return res.status(400).send("Invalid path");
    if (!publishedFile(relOf(req))) return res.status(404).send("Not found");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.set("Cache-Control", "no-cache");
    res.type("application/json").send(fs.readFileSync(abs, "utf-8"));
  });

  // What the build remakes a model on and what it remakes, read off the build's own record
  // (lib/made-from.js) for the Related list (public/js/viewer/related-nav.js). A model the site
  // does not list is named and not linked.
  const graphPath = path.join(hardwareDir, "..", "tools", "bazel", "graph.json");
  app.get("/api/made-from/*splat", (req, res) => {
    const rel = relOf(req);
    if (rel.includes("..") || !rel.endsWith(".step")) return res.status(400).send("Invalid path");
    if (!publishedFile(rel)) return res.status(404).send("Not found");
    const made = madeFrom(graphPath, rel);
    if (!made) return res.status(404).send("Not found");
    let listed = null;
    try { listed = new Set(numberedModels(readMaterialCatalog(hardwareDir), Object.values(made).flat().map((i) => i.file).filter(Boolean))); } catch { /* none linked */ }
    for (const item of Object.values(made).flat()) if (item.file && !listed?.has(item.file)) item.file = null;
    res.set("Cache-Control", "no-cache");
    res.json(made);
  });

  // sendFile races against the atomic-rename window in
  // hardware/scripts/_cadq_export.py: existsSync above can pass and then the
  // file vanish for a few ms while a regen writes a new temp + rename.
  // sendFile's NotFoundError bubbles up to Express's default handler
  // which prints a stack trace to stderr — noisy and looks alarming.
  // Pass a callback so we own the error path and just send a 404 / 503
  // instead.
  function streamFile(res, abs) {
    res.type("application/octet-stream").sendFile(abs, SEND_OPTS, (err) => {
      if (!err) return;
      if (res.headersSent) return; // already streaming; the client will see a truncated body
      if (err.code === "ENOENT" || err.status === 404) {
        return res.status(404).send("Not found");
      }
      res.status(500).send("File send error");
    });
  }

  app.get("/steps/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".step");
    if (!abs) return res.status(400).send("Invalid path");
    if (!publishedFile(relOf(req))) return res.status(404).send("Not found");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  app.get("/models/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".glb");
    if (!abs) return res.status(400).send("Invalid path");
    if (!publishedFile(relOf(req))) return res.status(404).send("Not found");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  // The tessellation the generator already had, written beside its STEP as
  // `<file>.step.mesh` by hardware/scripts/_cadq_export.py. The page reads these
  // instead of parsing the STEP through occt-import-js in wasm. Not committed —
  // a 404 here is normal, and step.js parses the STEP instead.
  app.get("/meshes/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".mesh");
    if (!abs) return res.status(400).send("Invalid path");
    if (!publishedFile(relOf(req))) return res.status(404).send("Not found");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  // Committed pictures, served beside the file they are of: a PDF's cover
  // (`/guides`) and a scene's `.glb` still. `/3d` fetches neither — its cards
  // draw the model. The 404 path is normal. no-cache so a live regen or deploy is
  // picked up via ETag revalidation rather than a stale hit.
  app.get("/thumbs/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".png");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.set("Cache-Control", "no-cache");
    res.type("image/png").sendFile(abs, SEND_OPTS, (err) => {
      if (!err || res.headersSent) return;
      if (err.code === "ENOENT" || err.status === 404) return res.status(404).send("Not found");
      res.status(500).send("File send error");
    });
  });

  app.get("/dxfs/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".dxf");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  // Reading and downloading share the publication gate: only a PDF with its
  // document sidecar is reachable, and retired documents stay retired.
  function documentFile(req, res) {
    const rel = relOf(req);
    const abs = safeFile(hardwareDir, rel, ".pdf");
    if (!abs) { res.status(400).send("Invalid path"); return null; }
    if (!isPublishedDocument(rel)) { res.status(410).send("Document no longer published"); return null; }
    if (!fs.existsSync(path.join(hardwareDir, rel.slice(0, -4) + DOC_SIDECAR_SUFFIX))) {
      res.status(400).send("Not a document"); return null;
    }
    if (!fs.existsSync(abs)) { res.status(404).send("Not found"); return null; }
    return { rel, abs };
  }

  app.get("/read/*splat", (req, res) => {
    const doc = documentFile(req, res);
    if (!doc) return;
    const meta = readSidecar(hardwareDir, doc.rel);
    res.set("Cache-Control", "no-cache");
    res.type("html").send(renderDocumentReader({
      file: doc.rel, title: meta?.title || path.basename(doc.rel, ".pdf"),
      embedded: req.query.embed === "1",
      hostControls: req.query.controls === "host",
    }));
  });

  // HTML navigations (including saved /docs links and notification links) go
  // to the in-app reader. PDF.js and API clients still receive the PDF bytes,
  // with byte ranges available. An explicit download is an attachment.
  app.get("/docs/*splat", (req, res) => {
    const doc = documentFile(req, res);
    if (!doc) return;
    const { rel, abs } = doc;
    res.set("Cache-Control", "no-cache");
    res.vary("Accept");
    if (req.query.raw !== "1" && req.query.download !== "1" && req.get("Accept")?.includes("text/html")) {
      return res.redirect(302, `/read/${rel.split("/").map(encodeURIComponent).join("/")}`);
    }
    if (req.query.download === "1") res.attachment(path.basename(abs));
    else res.set("Content-Disposition", `inline; filename="${path.basename(abs)}"`);
    res.type("application/pdf").sendFile(abs, SEND_OPTS, (err) => {
      if (!err || res.headersSent) return;
      if (err.code === "ENOENT" || err.status === 404) return res.status(404).send("Not found");
      res.status(500).send("File send error");
    });
  });
}
