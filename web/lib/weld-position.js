import fs from "node:fs";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const fragment = new URL("./templates/weld-position-body.html", import.meta.url);

export function mountWeldPositionRoutes(app) {
  app.get("/weld-position", (_req, res) => {
    res.type("html").set("Cache-Control", "no-cache").send(
      renderHead({
        title: "Gun at the joint · Home Soda Machine",
        pageHead: '<link rel="stylesheet" href="/css/weld-position.css">',
        importMap: { imports: {
          three: "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js",
          "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/",
        } },
      }) + renderNav() + fs.readFileSync(fragment, "utf8") + renderFooter(),
    );
  });
}
