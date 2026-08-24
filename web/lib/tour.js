// /tour — the guided walkthrough. One page, one fragment, and the whole of
// what it says lives in contracts/tour-water.js, which the browser fetches at
// /contracts/tour-water.js like any other contract.
//
// The route takes an optional step in the path — /tour/5 — as well as the
// `#5` the player itself writes, so a link into a beat is typeable.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRAGMENT = path.join(__dirname, "templates", "tour-body.html");

export function mountTourRoutes(app) {
  function render(_req, res) {
    res.set("Content-Type", "text/html; charset=utf-8");
    // Same reason as the viewer pages: without this, iOS Safari in standalone
    // will serve cached HTML and skip the conditional GET, leaving a tour that
    // is a deploy behind the words it is reading.
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({ title: "Walkthrough · Home Soda Machine" }) +
      renderNav({ surface: "dev", active: "tour" }) +
      fs.readFileSync(FRAGMENT, "utf-8") +
      renderFooter(),
    );
  }

  app.get("/tour", render);
  // /tour/5 is the same page; the client reads the number off the path and
  // rewrites it as the hash it keeps the position in.
  app.get("/tour/:step", (req, res) => {
    const n = Number.parseInt(req.params.step, 10);
    if (!Number.isInteger(n) || n < 1) return res.redirect(302, "/tour");
    res.redirect(302, `/tour#${n}`);
  });
}
