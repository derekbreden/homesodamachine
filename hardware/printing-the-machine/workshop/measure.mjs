// Measures how large each picture is drawn on the staged pages, so the build can keep no more pixels than a page shows.
// usage: node measure.mjs <dir of staged .html> <out.json>
import fs from "fs";
import path from "path";
import { pathToFileURL } from "url";
import { ensureRunLease, launchBrowser, closeBrowser, finish } from "../../../tools/render/browser.js";

ensureRunLease();
const [dir, outFile] = process.argv.slice(2);
const files = fs.readdirSync(dir).filter((f) => f.endsWith(".html")).sort();
const browser = await launchBrowser({ timeout: 30000 });
const page = await browser.newPage();
await page.setViewport({ width: 2550, height: 3300, deviceScaleFactor: 1 });
const need = {};
const uses = {};
const fit = {};
for (const f of files) {
  await page.goto(pathToFileURL(path.join(dir, f)).href, { waitUntil: "networkidle0" });
  const found = await page.evaluate(() => {
    const out = [];
    const name = (u) => decodeURIComponent(u.split("/").pop().split("?")[0]);
    for (const el of document.querySelectorAll("img")) {
      const r = el.getBoundingClientRect();
      if (!r.width || !el.naturalWidth) continue;
      const fit = getComputedStyle(el).objectFit;
      const aspect = el.naturalWidth / el.naturalHeight;
      // cover: the picture is scaled until it covers the box; otherwise it is stretched to the box
      const w = fit === "cover" ? Math.max(r.width, r.height * aspect) : r.width;
      out.push([name(el.currentSrc || el.src), w, w / aspect]);
    }
    // any box that shows a picture as its background, enlarged by a percentage of the box's width
    for (const el of document.querySelectorAll("main div, main span, main figure")) {
      const cs = getComputedStyle(el);
      if (cs.backgroundImage === "none" || !cs.backgroundImage.includes("/art/")) continue;
      const r = el.getBoundingClientRect();
      const m = cs.backgroundImage.match(/url\("?([^")]+)"?\)/);
      const size = cs.backgroundSize.split(" ")[0];
      if (!m || !r.width) continue;
      const w = size.endsWith("%") ? (r.width * parseFloat(size)) / 100 : size.endsWith("px") ? parseFloat(size) : r.width * 2;
      out.push([name(m[1]), w, 0]);
    }
    return out;
  });
  for (const [n, w] of found) {
    need[n] = Math.max(need[n] || 0, w); // the widest the whole picture is drawn anywhere, in page pixels
    (uses[n] = uses[n] || []).push(f);
  }
  // A page whose content runs past its band is scaled, text and pictures together, until it fits.
  const z = await page.evaluate(() => {
    const main = document.querySelector("main");
    const box = main && main.querySelector(":scope > .fit");
    const end = main && main.querySelector(":scope > i.end");
    if (!box || !end) return 1;
    const over = (zoom) => {
      box.style.zoom = zoom;
      return end.getBoundingClientRect().top - main.getBoundingClientRect().bottom;
    };
    const first = over(1);
    if (first <= 0) return 1;
    const h = main.getBoundingClientRect().height;
    let zoom = Math.floor((h / (h + first)) * 1000) / 1000;
    for (let i = 0; i < 40 && over(zoom) > -8; i++) zoom = Math.round((zoom - 0.004) * 1000) / 1000;
    return zoom;
  });
  if (z < 1) fit[f.slice(3, -5)] = z;
}
await closeBrowser(browser);
fs.writeFileSync(outFile, JSON.stringify({ need, uses, fit }, null, 1));
console.log(`measured ${Object.keys(need).length} pictures on ${files.length} pages; ${Object.keys(fit).length} pages scaled to fit: ${JSON.stringify(fit)}`);
finish(0);
