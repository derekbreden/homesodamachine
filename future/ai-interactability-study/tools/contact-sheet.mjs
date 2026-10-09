#!/usr/bin/env node
// Lays scene screenshots from thumbs/ out as labelled grids so many scenes can be looked at in one image.
//   node tools/contact-sheet.mjs <out-dir> [--cols=4] [--per=12] [--prefix=freedom,room] [--w=480]
// Writes <out-dir>/sheet-1.png, sheet-2.png, ... Each cell is thumbs/<id>.png captioned with the scene id.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const study = path.resolve(here, "..");
const thumbs = path.join(study, "thumbs");
const args = process.argv.slice(2);
const outDir = path.resolve(args.find(a => !a.startsWith("--")) ?? ".");
const opt = Object.fromEntries(args.filter(a => a.startsWith("--")).map(a => a.slice(2).split("=")));
const cols = Number(opt.cols ?? 4), per = Number(opt.per ?? 12), w = Number(opt.w ?? 480);
const prefixes = opt.prefix ? opt.prefix.split(",") : null;

const ids = fs.readdirSync(thumbs)
  .filter(f => f.endsWith(".png") && !f.includes("--"))
  .map(f => f.slice(0, -4))
  .filter(id => !prefixes || prefixes.some(p => id.startsWith(p)))
  .sort();
if (!ids.length) { console.error("no thumbs matched"); process.exit(1); }
fs.mkdirSync(outDir, { recursive: true });

const require = createRequire("/Users/derekbredensteiner/Developer/homesodamachine/tools/render/");
const puppeteer = require("puppeteer");
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ["--no-sandbox", "--allow-file-access-from-files"] });
try {
  const page = await browser.newPage();
  for (let s = 0; s * per < ids.length; s++) {
    const slice = ids.slice(s * per, (s + 1) * per);
    const cells = slice.map(id => `<figure><img src="${pathToFileURL(path.join(thumbs, id + ".png"))}"><figcaption>${id}</figcaption></figure>`).join("");
    const html = `<!doctype html><meta charset=utf-8><style>
      body{margin:0;background:#0e1114;color:#dfe5ec;font:13px/1.3 -apple-system,system-ui,sans-serif}
      main{display:grid;grid-template-columns:repeat(${cols},${w}px);gap:10px;padding:10px}
      figure{margin:0}img{width:${w}px;display:block;border:1px solid #2a323b}
      figcaption{padding:3px 2px}</style><main>${cells}</main>`;
    const file = path.join(outDir, `.sheet-${s + 1}.html`);
    fs.writeFileSync(file, html);
    await page.setViewport({ width: cols * (w + 10) + 10, height: 600 });
    await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
    await page.screenshot({ path: path.join(outDir, `sheet-${s + 1}.png`), fullPage: true });
    fs.unlinkSync(file);
    console.log(path.join(outDir, `sheet-${s + 1}.png`), slice.join(" "));
  }
} finally {
  await browser.close();
}
