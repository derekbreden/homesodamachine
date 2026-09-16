import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";
import { mountTourRoutes } from "../lib/tour.js";
import { tourAssetVersion } from "../lib/tour-assets.js";

test("a tour page loads its entry, nested modules, contracts and CSS from one asset version", async (t) => {
  const app = express();
  mountTourRoutes(app);
  const server = app.listen(0, "127.0.0.1");
  await new Promise((resolve) => server.once("listening", resolve));
  t.after(() => new Promise((resolve) => { server.closeAllConnections(); server.close(resolve); }));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const page = await fetch(`${origin}/tour`);
  assert.equal(page.headers.get("cache-control"), "no-cache");
  const html = await page.text();
  const version = html.match(/data-tour-version="([a-f0-9]{20})"/)?.[1];
  assert.ok(version, "the page identifies the client graph it loaded");
  assert.match(html, new RegExp(`<meta name="tour-assets-version" content="${version}">`));
  const prefix = `/tour-assets/${version}`;
  const imports = JSON.parse(html.match(/<script type="importmap">([\s\S]*?)<\/script>/)[1]).imports;
  assert.equal(imports["/js/"], `${prefix}/js/`);
  assert.equal(imports["/contracts/"], `${prefix}/contracts/`);
  assert.ok(html.indexOf('<script type="importmap">') < html.indexOf('<script type="module" src="/boot.js">'),
    "the map applies before the shared boot module can resolve its imports");
  const entry = html.match(/<script type="module" src="([^"]+\/js\/tour\/main\.js)"/)[1];
  assert.equal(entry, `${prefix}/js/tour/main.js`);
  assert.match(html, new RegExp(`href="${prefix}/css/tour\\.css"`));
  assert.match(html, new RegExp(`href="${prefix}/css/viewer\\.css"`));

  // Native URL resolution keeps relative dependencies in the same namespace;
  // the import map brings root-relative contracts into that namespace too.
  const mainUrl = new URL(entry, origin);
  const revealUrl = new URL("./reveal.js", mainUrl);
  const planUrl = new URL("./reveal-plan.js", revealUrl);
  const viewerUrl = new URL("../viewer/step.js", mainUrl);
  const contractUrl = new URL(`${imports["/contracts/"]}tour-water.js`, origin);
  for (const url of [mainUrl, revealUrl, planUrl, viewerUrl, contractUrl,
    new URL(`${prefix}/css/tour.css`, origin)]) {
    const response = await fetch(url);
    assert.equal(response.status, 200, url.pathname);
    assert.equal(response.headers.get("cache-control"), "no-cache", url.pathname);
    assert.match(response.headers.get("content-type"), url.pathname.endsWith(".css") ? /^text\/css/ : /^text\/javascript/);
    assert.ok((await response.text()).length > 0);
  }
  const main = await (await fetch(mainUrl)).text();
  assert.match(main, /from "\.\/reveal\.js"/);
  assert.match(main, /from "\/contracts\/tour-water\.js"/);
  const reveal = await (await fetch(revealUrl)).text();
  assert.match(reveal, /from "\.\/reveal-plan\.js"/);

  const unknown = version[0] === "0" ? `1${version.slice(1)}` : `0${version.slice(1)}`;
  for (const asset of [`/tour-assets/${unknown}/js/tour/main.js`, `${prefix}/js/tour/missing.js`]) {
    const response = await fetch(`${origin}${asset}`);
    assert.equal(response.status, 404, asset);
    assert.equal(response.headers.get("cache-control"), "no-store");
  }
});

test("the asset version covers nested code and contracts, with deterministic path ordering", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tour-assets-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const roots = Object.fromEntries(["js", "css", "contracts"].map((name) => [name, path.join(directory, name)]));
  for (const root of Object.values(roots)) fs.mkdirSync(root);
  fs.mkdirSync(path.join(roots.js, "tour"));
  const module = path.join(roots.js, "tour/main.js");
  const contract = path.join(roots.contracts, "story.js");
  const style = path.join(roots.css, "tour.css");
  fs.writeFileSync(module, 'import "/contracts/story.js";');
  fs.writeFileSync(contract, "export const duration = 130;");
  fs.writeFileSync(style, ".tour { color: white; }");
  const initial = tourAssetVersion(roots);
  assert.equal(tourAssetVersion(Object.fromEntries(Object.entries(roots).reverse())), initial);
  fs.writeFileSync(path.join(roots.js, "notes.txt"), "not a client asset");
  assert.equal(tourAssetVersion(roots), initial);
  for (const file of [module, contract, style]) {
    const previous = tourAssetVersion(roots);
    fs.appendFileSync(file, "\n/* change */");
    assert.notEqual(tourAssetVersion(roots), previous, file);
  }
});
