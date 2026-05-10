import express from "express";
import path from "path";
import fs from "fs";

function walkFiles(dir, rel, ext, out) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkFiles(full, path.join(rel, entry.name), ext, out);
    else if (entry.name.endsWith(ext)) out.push(path.join(rel, entry.name));
  }
}

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
    const out = [];
    walkFiles(hardwareDir, "", ".step", out);
    res.json(out);
  });

  app.get("/api/mermaid", (_req, res) => {
    const out = [];
    walkFiles(hardwareDir, "", ".mmd", out);
    res.json(out);
  });

  app.get("/api/dxf", (_req, res) => {
    const paths = [];
    walkFiles(hardwareDir, "", ".dxf", paths);
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

  app.get("/steps/*", (req, res) => {
    const abs = safeFile(hardwareDir, req.params[0], ".step");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.type("application/octet-stream").sendFile(abs);
  });

  app.get("/dxfs/*", (req, res) => {
    const abs = safeFile(hardwareDir, req.params[0], ".dxf");
    if (!abs) return res.status(400).send("Invalid path");
    if (!fs.existsSync(abs)) return res.status(404).send("Not found");
    res.type("application/octet-stream").sendFile(abs);
  });
}
