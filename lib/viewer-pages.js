// Server-renders the two viewer pages: /3d (parts — prints + cuts) and
// /charts (mermaid diagrams). Both pages share the same body fragment
// (tools/dev-server/templates/viewer-body.html), which decides what to
// render based on location.pathname. The server picks the page title and
// active nav item based on which route was hit; everything else is in the
// fragment.
//
// Old route layout (pre-rename, kept as 301 redirects so prior FCM
// notification deep links and bookmarks still land somewhere):
//   /dev          → /3d
//   /dev/diagrams → /charts
//   /dev/mermaid  → /charts
//   /dev/settings → /settings
//
// Settings used to be a third section here; it now lives at /settings
// (lib/settings.js), reachable via the gear in the nav.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(
  __dirname,
  "..",
  "tools",
  "dev-server",
  "templates",
);

function readFragment(name) {
  return fs.readFileSync(path.join(TEMPLATES_DIR, name), "utf-8");
}

const TITLES = {
  parts: "Parts · Home Soda Machine",
  charts: "Charts · Home Soda Machine",
};

export function mountViewerPages(app) {
  function renderPage(active) {
    return (_req, res) => {
      res.set("Content-Type", "text/html; charset=utf-8");
      // Same heuristic-cache concern as the public HTML routes: without
      // an explicit Cache-Control, iOS Safari (especially in PWA
      // standalone) may serve cached HTML and skip the conditional GET
      // on the ETag, leaving a notification-driven navigation pointing
      // at a stale viewer page. The SW reload-bridge in shell.js
      // HEAD_TAGS catches the same-document case; this catches the
      // browser-cached case.
      res.set("Cache-Control", "no-cache");
      res.send(
        renderHead({ title: TITLES[active] }) +
        renderNav({ surface: "dev", active }) +
        readFragment("viewer-body.html") +
        renderFooter(),
      );
    };
  }

  // Express's default `strict: false` routing makes /3d and /3d/ equivalent.
  app.get("/3d", renderPage("parts"));
  app.get("/charts", renderPage("charts"));

  // Legacy redirects. /dev?file=foo and /dev/?file=foo were the deep-link
  // shape baked into FCM notifications before the rename; preserve the
  // query string so a user tapping a stale notification still lands on
  // their file.
  const devToParts = (req, res) => {
    const qsIdx = req.originalUrl.indexOf("?");
    const qs = qsIdx >= 0 ? req.originalUrl.slice(qsIdx) : "";
    res.redirect(301, "/3d" + qs);
  };
  app.get("/dev", devToParts);
  app.get("/dev/", devToParts);
  app.get("/dev/diagrams", (_req, res) => res.redirect(301, "/charts"));
  app.get("/dev/mermaid", (_req, res) => res.redirect(301, "/charts"));
  app.get("/dev/settings", (_req, res) => res.redirect(301, "/settings"));
}
