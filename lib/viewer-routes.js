import express from "express";
import path from "path";
import fs from "fs";

function isIgnoredPath(p) {
  return p.includes(`${path.sep}plan-b${path.sep}`);
}

function walkFiles(dir, rel, ext, out) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (isIgnoredPath(full)) continue;
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
}

export const VIEWER_DEFAULTS = { isIgnoredPath };
