import fs from "node:fs";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const fragment = new URL("./templates/positioner-body.html", import.meta.url);

export function mountPositionerRoutes(app) {
  app.get("/positioner", (_req, res) => {
    res.type("html").set("Cache-Control", "no-cache").send(
      renderHead({
        title: "PGFUN positioner · Home Soda Machine",
        pageHead: '<link rel="stylesheet" href="/css/positioner.css">',
        importMap: { imports: {
          three: "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js",
          "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/",
        } },
      }) + renderNav({ active: "parts" }) + fs.readFileSync(fragment, "utf8") + renderFooter(),
    );
  });
}
