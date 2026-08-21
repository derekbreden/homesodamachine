import express from "express";
import path from "path";
import fs from "fs";

import { walkFiles, walkFilesUnderDir, walkPcbBoards, walkDocuments } from "./walk.js";
import { isCardAssetPath } from "../contracts/cards.js";
import { DOC_SIDECAR_SUFFIX } from "../contracts/documents.js";
import { VIEW_REQUEST_RE, PICKS_REQUEST_RE } from "../contracts/pcb-out.js";
import { sidecarFields } from "../contracts/sidecar.js";
import { SCORECARD_SUFFIX } from "../contracts/scorecard-sidecar.js";
import { PRINTS_DIR } from "../contracts/prints.js";

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
export function mountViewerRoutes(app, { hardwareDir }) {

  app.get("/api/steps", (req, res) => {
    res.json(walkFiles(hardwareDir, ".step"));
  });

  app.get("/api/glbs", (req, res) => {
    res.json(walkFiles(hardwareDir, ".glb"));
  });

  app.get("/api/mermaid", (req, res) => {
    res.json(walkFiles(hardwareDir, ".mmd"));
  });

  // Print sheets: SVGs that live in any directory named `prints-and-guides/`
  // under the active root. A sheet's generator writes the .svg the site shows
  // and the .pdf that goes to the printer side by side, next to the geometry
  // the sheet is drawn of.
  app.get("/api/drawings", (req, res) => {
    res.json(walkFilesUnderDir(hardwareDir, ".svg", PRINTS_DIR));
  });

  // PCB boards with their three rendered copper views (see walkPcbBoards).
  app.get("/api/pcb", (req, res) => {
    res.json(walkPcbBoards(hardwareDir));
  });

  // Documents: the PDFs the site hands over whole — the assembly deck, the
  // owner's manual (see walkDocuments and web/contracts/documents.js). Each
  // entry carries what it is called, how many pages it runs to, how big the
  // file is, and the cover to show for it.
  app.get("/api/documents", (req, res) => {
    res.set("Cache-Control", "no-cache");
    res.json(walkDocuments(hardwareDir));
  });

  // Card assets — the page itself plus the shared stylesheet and the renders it
  // embeds. The viewer loads a card into an iframe at this URL, so the card's
  // own relative `style.css` and `img/…` references resolve against it and the
  // browser lays the card out exactly as the print renderer does. Confined to
  // the deck directory and the asset types a card can reference; build
  // machinery in the same folder stays unreachable.
  app.get("/cards/*splat", (req, res) => {
    const rel = relOf(req);
    if (!isCardAssetPath(rel)) return res.status(400).send("Not a card asset");
    const abs = path.join(hardwareDir, rel);
    if (!abs.startsWith(hardwareDir + path.sep)) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    // Cards are edited live while the deck is being written; revalidate so a
    // reload never shows a stale card (same reasoning as the drawing and PCB
    // content routes above).
    res.set("Cache-Control", "no-cache");
    res.type(path.extname(abs)).sendFile(abs, SEND_OPTS, (err) => {
      if (!err || res.headersSent) return;
      if (err.code === "ENOENT" || err.status === 404) return res.status(404).send("Not found");
      res.status(500).send("File send error");
    });
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

  // Print-sheet SVG content. The viewer inlines the SVG into the DOM so
  // PanZoom can wrap it directly (like mermaid does after render). Path
  // must be inside a `prints-and-guides/` directory (we don't expose
  // arbitrary SVGs that may live elsewhere in the tree).
  app.get("/api/drawing-content/*splat", (req, res) => {
    const rel = relOf(req);
    const abs = safeFile(hardwareDir, rel, ".svg");
    if (!abs) return res.status(400).send("Invalid path");
    // Enforce the prints-and-guides/ directory convention so the SVGs a
    // generator writes for its own use — line art a sheet embeds, logos,
    // hand-drawn diagrams — aren't reachable through this endpoint.
    if (!rel.split("/").includes(PRINTS_DIR)) {
      return res.status(400).send("Not a drawing");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    // A sheet is regenerated live too; revalidate so a reload never serves a
    // stale drawing (same reasoning as the PCB views below).
    res.set("Cache-Control", "no-cache");
    res.type("image/svg+xml").send(fs.readFileSync(abs, "utf-8"));
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
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.set("Cache-Control", "no-cache");
    res.type("application/json").send(fs.readFileSync(abs, "utf-8"));
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
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  app.get("/models/*splat", (req, res) => {
    const abs = safeFile(hardwareDir, relOf(req), ".glb");
    if (!abs) return res.status(400).send("Invalid path");
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
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  // Server-rendered STEP thumbnails: `<file>.step.png` siblings produced by
  // the part's own export (hardware/scripts/_cadq_export.py shells out to
  // tools/render/render-thumbnails.js). The grid downloads these instead of
  // fetching the (often multi-MB) STEP and rendering it in the browser. The
  // 404 path is normal — a STEP with no committed thumbnail yet falls back to
  // a client render in the grid. no-cache so a live regen or deploy is picked
  // up via ETag revalidation rather than a stale hit.
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

  // A document, opened in a tab rather than downloaded — the deck a bench
  // builds from, the manual that ships in the carton. What makes a `.pdf` here
  // reachable is its `<name>.pdf.json` sidecar, which is the same thing that
  // puts it in the listing above; every other PDF under hardware/ belongs to
  // whatever wrote it and is not offered. `inline` so a click reads it instead
  // of filling a downloads folder, and no-cache so a rebuilt document is not
  // served stale off a tab opened before it.
  app.get("/docs/*splat", (req, res) => {
    const rel = relOf(req);
    const abs = safeFile(hardwareDir, rel, ".pdf");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(path.join(hardwareDir, rel.slice(0, -4) + DOC_SIDECAR_SUFFIX))) {
      return res.status(400).send("Not a document");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.set("Cache-Control", "no-cache");
    res.set("Content-Disposition", `inline; filename="${path.basename(abs)}"`);
    res.type("application/pdf").sendFile(abs, SEND_OPTS, (err) => {
      if (!err || res.headersSent) return;
      if (err.code === "ENOENT" || err.status === 404) return res.status(404).send("Not found");
      res.status(500).send("File send error");
    });
  });
}
