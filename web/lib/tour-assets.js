import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import express from "express";

/** The URL of every tour module changes together when its client code changes. */
export function tourAssetVersion(roots) {
  const hash = createHash("sha256");
  for (const [namespace, root] of Object.entries(roots).sort(([a], [b]) => a.localeCompare(b))) {
    function visit(directory, relative = "") {
      for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
        const name = relative ? `${relative}/${entry.name}` : entry.name;
        const absolute = path.join(directory, entry.name);
        if (entry.isDirectory()) visit(absolute, name);
        else if (entry.isFile() && /\.(?:js|css)$/.test(entry.name)) {
          const bytes = fs.readFileSync(absolute);
          hash.update(`${namespace}/${name}\0${bytes.length}\0`);
          hash.update(bytes);
        }
      }
    }
    visit(root);
  }
  return hash.digest("hex").slice(0, 20);
}

export function mountTourAssets(app, roots) {
  const version = tourAssetVersion(roots);
  const prefix = `/tour-assets/${version}`;
  for (const [namespace, root] of Object.entries(roots)) {
    app.use(`${prefix}/${namespace}`, express.static(root, {
      cacheControl: false,
      setHeaders(res) { res.setHeader("Cache-Control", "no-cache"); },
    }));
  }
  // A request for another build must never receive this build's modules.
  app.use("/tour-assets", (_req, res) => {
    res.set("Cache-Control", "no-store").status(404).send("Tour asset not found");
  });
  return { version, prefix };
}
