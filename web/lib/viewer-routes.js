import express from "express";
import path from "path";
import fs from "fs";

import { walkFiles, walkFilesUnderDir } from "./walk.js";

function safeFile(rootDir, rel, ext) {
  if (rel.includes("..")) return null;
  const abs = path.join(rootDir, rel);
  if (!abs.startsWith(rootDir + path.sep) || !abs.endsWith(ext)) return null;
  return abs;
}

// Read the JSON sidecar (`<file>.json`) next to a part, if present.
// Documented in hardware/PARTS.md; used by /api/dxf today, available to
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

export function mountViewerRoutes(app, { hardwareDir }) {
  app.get("/api/steps", (_req, res) => {
    res.json(walkFiles(hardwareDir, ".step"));
  });

  app.get("/api/mermaid", (_req, res) => {
    res.json(walkFiles(hardwareDir, ".mmd"));
  });

  // Line-art drawings: SVGs that live in any directory named `drawings/`
  // under hardware/. The generator is tools/line-art/line_art.py; the
  // drawing scripts and outputs colocate with the part they describe.
  app.get("/api/drawings", (_req, res) => {
    res.json(walkFilesUnderDir(hardwareDir, ".svg", "drawings"));
  });

  app.get("/api/dxf", (_req, res) => {
    const paths = walkFiles(hardwareDir, ".dxf");
    // Return enriched objects so the client gets the sidecar metadata
    // (thickness_mm, material, etc.) in the same round-trip — the
    // viewer needs thickness to extrude. See hardware/PARTS.md.
    res.json(paths.map((p) => {
      const meta = readSidecar(hardwareDir, p) || {};
      return {
        path: p,
        thickness_mm: typeof meta.thickness_mm === "number" ? meta.thickness_mm : null,
        material: typeof meta.material === "string" ? meta.material : null,
      };
    }));
  });

  app.get("/api/mermaid-content/*", (req, res) => {
    const abs = safeFile(hardwareDir, req.params[0], ".mmd");
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
    const abs = safeFile(hardwareDir, rel, ".svg");
    if (!abs) return res.status(400).send("Invalid path");
    // Enforce the drawings/ directory convention so non-line-art SVGs
    // (logos, hand-drawn diagrams) aren't reachable through this endpoint.
    if (!rel.split("/").includes("drawings")) {
      return res.status(400).send("Not a drawing");
    }
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.type("image/svg+xml").send(fs.readFileSync(abs, "utf-8"));
  });

  // sendFile races against the atomic-rename window in
  // hardware/_cadq_export.py: existsSync above can pass and then the
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
    const abs = safeFile(hardwareDir, req.params[0], ".step");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });

  app.get("/dxfs/*", (req, res) => {
    const abs = safeFile(hardwareDir, req.params[0], ".dxf");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    streamFile(res, abs);
  });
}
