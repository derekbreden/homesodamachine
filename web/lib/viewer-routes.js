import express from "express";
import path from "path";
import fs from "fs";

import { walkFiles, walkFilesUnderDir, walkPcbBoards } from "./walk.js";
import { VIEW_REQUEST_RE, PICKS_REQUEST_RE } from "../../contracts/pcb-out.js";

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

// The viewer serves one of two content roots, chosen per request by the
// hidden Edition toggle (Settings, dev-mode only). Kitchen (the default) is
// the hardware/ tree; Lite is pie-in-the-sky/lite/. The client mirrors its
// localStorage choice into an `hsmEdition` cookie before first paint (see
// lib/shell.js), so every list endpoint and file stream below resolves
// against the matching root without any per-fetch plumbing on the client.
// A ?edition= query param overrides the cookie, which keeps the endpoints
// curl-testable.
function cookieEdition(cookieHeader) {
  if (!cookieHeader) return null;
  for (const part of cookieHeader.split(";")) {
    const eq = part.indexOf("=");
    if (eq === -1) continue;
    if (part.slice(0, eq).trim() === "hsmEdition") return part.slice(eq + 1).trim();
  }
  return null;
}

function editionRoot(req, { hardwareDir, liteDir }) {
  const q = typeof req.query.edition === "string" ? req.query.edition : null;
  const edition = q || cookieEdition(req.headers.cookie) || "kitchen";
  return edition === "lite" ? liteDir : hardwareDir;
}

export function mountViewerRoutes(app, { hardwareDir, liteDir }) {
  const rootFor = (req) => editionRoot(req, { hardwareDir, liteDir });

  app.get("/api/steps", (req, res) => {
    res.json(walkFiles(rootFor(req), ".step"));
  });

  app.get("/api/mermaid", (req, res) => {
    res.json(walkFiles(rootFor(req), ".mmd"));
  });

  // Line-art drawings: SVGs that live in any directory named `drawings/`
  // under the active root. The generator is tools/line-art/line_art.py; the
  // drawing scripts and outputs colocate with the part they describe.
  app.get("/api/drawings", (req, res) => {
    res.json(walkFilesUnderDir(rootFor(req), ".svg", "drawings"));
  });

  // PCB boards with their three rendered copper views (see walkPcbBoards).
  app.get("/api/pcb", (req, res) => {
    res.json(walkPcbBoards(rootFor(req)));
  });

  app.get("/api/dxf", (req, res) => {
    const rootDir = rootFor(req);
    const paths = walkFiles(rootDir, ".dxf");
    // Return enriched objects so the client gets the sidecar metadata
    // (thickness_mm, material, etc.) in the same round-trip — the
    // viewer needs thickness to extrude. See hardware/README.md.
    res.json(paths.map((p) => {
      const meta = readSidecar(rootDir, p) || {};
      return {
        path: p,
        thickness_mm: typeof meta.thickness_mm === "number" ? meta.thickness_mm : null,
        material: typeof meta.material === "string" ? meta.material : null,
      };
    }));
  });

  app.get("/api/mermaid-content/*", (req, res) => {
    const abs = safeFile(rootFor(req), req.params[0], ".mmd");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.type("text/plain").send(fs.readFileSync(abs, "utf-8"));
  });

  // Line-art SVG content. The viewer inlines the SVG into the DOM so
  // PanZoom can wrap it directly (like mermaid does after render). Path
  // must be inside a `drawings/` directory (we don't expose arbitrary
  // SVGs that may live elsewhere in the tree).
  app.get("/api/drawing-content/*", (req, res) => {
    const rel = req.params[0];
    const abs = safeFile(rootFor(req), rel, ".svg");
    if (!abs) return res.status(400).send("Invalid path");
    // Enforce the drawings/ directory convention so non-line-art SVGs
    // (logos, hand-drawn diagrams) aren't reachable through this endpoint.
    if (!rel.split("/").includes("drawings")) {
      return res.status(400).send("Not a drawing");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    // Line-art is regenerated live too; revalidate so a reload never serves a
    // stale drawing (same reasoning as the PCB views below).
    res.set("Cache-Control", "no-cache");
    res.type("image/svg+xml").send(fs.readFileSync(abs, "utf-8"));
  });

  // PCB view SVG content. Only the rendered board views under a `pcb/.../out/`
  // directory are reachable — the fixed Top/Bottom/Overlay plus any inner
  // copper planes (inner1, inner2, …) — not arbitrary SVGs that may live
  // elsewhere in the tree.
  app.get("/api/pcb-content/*", (req, res) => {
    const rel = req.params[0];
    const abs = safeFile(rootFor(req), rel, ".svg");
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
  app.get("/api/pcb-picks/*", (req, res) => {
    const rel = req.params[0];
    const abs = safeFile(rootFor(req), rel, ".json");
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

  // sendFile races against the atomic-rename window in
  // hardware/scripts/_cadq_export.py: existsSync above can pass and then the
  // file vanish for a few ms while a regen writes a new temp + rename.
  // sendFile's NotFoundError bubbles up to Express's default handler
  // which prints a stack trace to stderr — noisy and looks alarming.
  // Pass a callback so we own the error path and just send a 404 / 503
  // instead.
  function streamFile(res, abs) {
    res.type("application/octet-stream").sendFile(abs, (err) => {
      if (!err) return;
      if (res.headersSent) return; // already streaming; the client will see a truncated body
      if (err.code === "ENOENT" || err.status === 404) {
        return res.status(404).send("Not found");
      }
      res.status(500).send("File send error");
    });
  }

  app.get("/steps/*", (req, res) => {
    const abs = safeFile(rootFor(req), req.params[0], ".step");
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
  app.get("/thumbs/*", (req, res) => {
    const abs = safeFile(rootFor(req), req.params[0], ".png");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.set("Cache-Control", "no-cache");
    res.type("image/png").sendFile(abs, (err) => {
      if (!err || res.headersSent) return;
      if (err.code === "ENOENT" || err.status === 404) return res.status(404).send("Not found");
      res.status(500).send("File send error");
    });
  });

  app.get("/dxfs/*", (req, res) => {
    const abs = safeFile(rootFor(req), req.params[0], ".dxf");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });
}
