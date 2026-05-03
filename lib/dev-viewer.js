// Server-renders the dev viewer SPA. One body fragment
// (tools/step-viewer/templates/viewer-body.html) handles two sections —
// Prints and Diagrams — by reading location.pathname in the client. The
// server renders shell.head + shell.nav (with the matching active state
// and devPrefix) around the same fragment for every section URL.
//
// Settings used to be a third section here; it now lives at /settings
// (lib/settings.js), reachable via the gear in the nav. Old /dev/settings
// links 301 to /settings.
//
// Mounting:
//   prod   → mountDevViewerRoutes(app, { prefix: "/dev" })
//   dev    → mountDevViewerRoutes(app, { prefix: "" })  // viewer at root

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(
  __dirname,
  "..",
  "tools",
  "step-viewer",
  "templates",
);

function readFragment(name) {
  return fs.readFileSync(path.join(TEMPLATES_DIR, name), "utf-8");
}

const TITLES = {
  prints: "Prints · Home Soda Machine",
  diagrams: "Diagrams · Home Soda Machine",
};

export function mountDevViewerRoutes(app, { prefix = "/dev" } = {}) {
  const root = prefix || "/";

  function renderSection(active) {
    return (_req, res) => {
      res.set("Content-Type", "text/html; charset=utf-8");
      res.send(
        renderHead({ title: TITLES[active] }) +
        renderNav({ surface: "dev", active, devPrefix: prefix }) +
        readFragment("viewer-body.html") +
        renderFooter(),
      );
    };
  }

  app.get(root, renderSection("prints"));
  app.get(`${prefix}/diagrams`, renderSection("diagrams"));

  // Legacy aliases — /dev/settings used to render the SPA's settings
  // section, /dev/mermaid was the old standalone diagrams page.
  if (prefix) {
    app.get(`${prefix}/settings`, (_req, res) => res.redirect(301, "/settings"));
    app.get(`${prefix}/mermaid`, (_req, res) =>
      res.redirect(301, `${prefix}/diagrams`),
    );
  }
}
