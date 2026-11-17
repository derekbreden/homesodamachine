// Parts and Guides share lib/templates/viewer-body.html.
// The server renders the page title and navigation. The viewer uses the path
// to pick the catalog it renders.
//
// Redirects keep existing links and bookmarks working.
//   /dev          → /3d
//   /drawings     → /guides (the printed guides carry homesodamachine.com/drawings)
//   /pcb          → the board's material workspace

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderPageHeader, renderFooter } from "./shell.js";
import { pcbMaterialHash } from "./material-catalog.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(__dirname, "templates");

function readFragment(name) {
  return fs.readFileSync(path.join(TEMPLATES_DIR, name), "utf-8");
}

const TITLES = {
  parts: "Parts · Home Soda Machine",
  guides: "Guides · Home Soda Machine",
};

const INTRO = {
  parts: { eyebrow: "Parts", title: "Explore the machine.", description: "The soda machine, the faucet, and the tools that bring them together. Open a model to explore its parts and documents." },
  guides: { title: "Guides", description: "Assembly instructions and shop references." },
};

export function mountViewerPages(app) {
  function renderPage(active) {
    return (_req, res) => {
      res.set("Content-Type", "text/html; charset=utf-8");
      // Revalidate the shell on navigation so it loads the current viewer.
      res.set("Cache-Control", "no-cache");
      res.send(
        renderHead({ title: TITLES[active], pageClass: `site-interior site-viewer-${active}` }) +
        renderNav({ active }) +
        (active === "guides" ? `<header class="document-library-header site-light"><div class="document-library-inner"><div><h1>${INTRO.guides.title}</h1><p>${INTRO.guides.description}</p></div><div id="document-search-slot"></div></div></header>` : renderPageHeader(INTRO[active])) +
        readFragment("viewer-body.html") +
        renderFooter({ siteFooter: true }),
      );
    };
  }

  // Express's default `strict: false` routing makes /3d and /3d/ equivalent.
  app.get("/3d", renderPage("parts"));
  app.get("/guides", renderPage("guides"));
  app.get("/pcb", (req, res) => {
    const source = typeof req.query.file === "string" ? req.query.file : null;
    const hash = pcbMaterialHash(source);
    res.redirect(301, `/3d${hash ? "#" + hash : ""}`);
  });

  // Preserve file and guide-search queries on legacy links.
  const movedTo = (target) => (req, res) => {
    const qsIdx = req.originalUrl.indexOf("?");
    const qs = qsIdx >= 0 ? req.originalUrl.slice(qsIdx) : "";
    res.redirect(301, target + qs);
  };
  app.get("/dev", movedTo("/3d"));
  app.get("/dev/", movedTo("/3d"));
  app.get("/drawings", movedTo("/guides"));
}
