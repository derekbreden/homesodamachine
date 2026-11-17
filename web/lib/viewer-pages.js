// Mount the guide library and carry older links into the Parts workspace.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderFooter } from "./shell.js";
import { pcbMaterialHash } from "./material-catalog.js";
import { PARTS_PATH } from "../contracts/viewer-links.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(__dirname, "templates");

function readFragment(name) {
  return fs.readFileSync(path.join(TEMPLATES_DIR, name), "utf-8");
}

export function renderPartsViewer() {
  return readFragment("viewer-body.html") + '<script type="module" src="/js/viewer/parts-entry.js"></script>';
}

export function mountViewerPages(app) {
  app.get("/guides", (_req, res) => {
    res.type("html").set("Cache-Control", "no-cache");
    res.send(
      renderHead({ title: "Guides · Home Soda Machine", pageClass: "site-interior site-viewer-guides" }) +
      renderNav({ active: "guides" }) +
      `<header class="document-library-header site-light"><div class="document-library-inner"><div><h1>Guides</h1><p>Assembly instructions and shop references.</p></div><div id="document-search-slot"></div></div></header>
<main id="grid" class="site-content"><p class="empty-state" role="status">Loading…</p></main>` +
      readFragment("viewer-body.html") +
      '<script type="module" src="/js/viewer/main.js"></script>' +
      renderFooter({ siteFooter: true }),
    );
  });
  app.get("/pcb", (req, res) => {
    const source = typeof req.query.file === "string" ? req.query.file : null;
    const hash = pcbMaterialHash(source);
    res.redirect(301, PARTS_PATH + (hash ? "#" + hash : ""));
  });

  // Preserve the query and let the browser carry the original fragment.
  const movedTo = (target) => (req, res) => {
    const qsIdx = req.originalUrl.indexOf("?");
    const qs = qsIdx >= 0 ? req.originalUrl.slice(qsIdx) : "";
    res.redirect(301, target + qs);
  };
  app.get(["/3d", "/dev"], movedTo(PARTS_PATH));
  app.get("/drawings", movedTo("/guides"));
}
