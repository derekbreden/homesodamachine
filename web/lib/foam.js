// /foam shows what the fill model says each foam pour will do: where the foam ends up, where it
// does not, and how it got there.
import fs from "node:fs";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const fragment = new URL("./templates/foam-body.html", import.meta.url);

export function mountFoamRoutes(app) {
  app.get("/foam", (_req, res) => {
    res.type("html").set("Cache-Control", "no-cache").send(
      renderHead({
        title: "Foam pours · Home Soda Machine",
        pageHead: '<link rel="stylesheet" href="/css/foam.css">',
        importMap: { imports: {
          three: "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js",
          "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/",
        } },
      }) + renderNav({ active: "parts" }) + fs.readFileSync(fragment, "utf8") + renderFooter(),
    );
  });
}
