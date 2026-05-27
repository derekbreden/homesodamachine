// /scene route — line-art scene renderer for technical drawings.
//
// Loads a glTF (built from CadQuery via
// hardware/printed-parts/enclosure/scene/build_scene.py) and renders it
// as line art with z-buffer occlusion. Colored parts in the glTF
// (e.g. the red ring around the CO2 port) render in their assigned
// color; default-color parts render as white surfaces with black
// silhouette + feature edges.
//
// This route is purpose-built for headless capture by
// tools/render/render-scene.js — it is NOT the interactive part viewer
// at /3d. No nav, no gizmo, no controls.
//
// URL: /scene?file=<repo-relative-glb>&view=iso-front|iso-back
//
// The file path is resolved against the repo root (so it can address
// hardware/, posts/, anywhere). The view chooses the camera pose.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(__dirname, "templates");

function readFragment(name) {
  return fs.readFileSync(path.join(TEMPLATES_DIR, name), "utf-8");
}

export function mountSceneRoutes(app, { repoRoot }) {
  // Serve the scene viewer JS bundle from web/public/scene/ at /scene/*.
  // Express's express.static is mounted in server.js on the landing
  // public dir; we mount a sibling here for /scene/* specifically.
  app.use("/scene", (req, res, next) => {
    // Only serve static files for paths like /scene/foo.js — the bare
    // /scene path falls through to renderPage below.
    if (req.path === "/" || req.path === "") return next();
    const candidate = path.join(__dirname, "..", "public", "scene", req.path);
    if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
      return res.sendFile(candidate);
    }
    return next();
  });

  // Serve glTF files from anywhere under the repo root at /glb/<path>.
  // The viewer fetches glb via this route so it can address files in
  // hardware/printed-parts/.../scene.glb without us copying them into
  // web/public.
  app.get(/^\/glb\/(.+)$/, (req, res) => {
    const rel = req.params[0];
    const abs = path.join(repoRoot, rel);
    if (!abs.startsWith(repoRoot)) return res.status(400).send("bad path");
    if (!fs.existsSync(abs)) return res.status(404).send("not found");
    res.setHeader("Content-Type", "model/gltf-binary");
    res.sendFile(abs);
  });

  app.get("/scene", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    // No nav, no footer — this surface is for headless capture and
    // direct-browser debugging only.
    // No nav, no footer — purpose-built surface, not a navigated page.
    res.send(
      renderHead({ title: "Scene · Home Soda Machine" }) +
      readFragment("scene-body.html"),
    );
  });
}
