// /spin — the cap-weld rotation, drawn.
//
// One page, one fragment, and the geometry lives in public/js/spin/. It draws
// the carbonator's closure joint turning under a stationary head, which is the
// one thing hardware/assembly/weld-rotation-rig.md asserts and the one thing a
// written procedure cannot show: what 1.2 RPM feels like for 49 seconds.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FRAGMENT = path.join(__dirname, "templates", "spin-body.html");

export function mountSpinRoutes(app) {
  app.get("/spin", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    // Same reason as the tour and the viewer pages: iOS Safari in standalone
    // will otherwise serve cached HTML and skip the conditional GET.
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({ title: "Cap-weld rotation · Home Soda Machine" }) +
      renderNav({ surface: "dev", active: null }) +
      fs.readFileSync(FRAGMENT, "utf-8") +
      renderFooter(),
    );
  });
}
