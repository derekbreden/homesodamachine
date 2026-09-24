#!/usr/bin/env node
// shot.mjs — look at a built page the way a reader will, before anyone else does.
//
//   node tools/viz/shot.mjs PAGE.html OUT.png            desktop light beside phone dark, one PNG
//   node tools/viz/shot.mjs PAGE.html OUT.png --desktop  960 px wide, light
//   node tools/viz/shot.mjs PAGE.html OUT.png --phone    390 px wide at 2x, dark
//
// The page is wrapped in the skeleton the Artifact publisher wraps it in (doctype, viewport meta,
// the small reset), loaded from a file, and captured once every 3D stage has drawn its first frame
// (`window.__vizReady`). What it cannot see it says: every console error, every request that
// failed, and every stage that shows an error instead of a model is printed, because a PNG of a
// blank stage and a PNG of a slow one look alike.

import fs from "fs";
import os from "os";
import path from "path";
import { createRequire } from "module";
import { closeBrowser, launchBrowser, sweepAbandonedBrowsers } from "../render/browser.js";

const require = createRequire(import.meta.url);
const sharp = require(require.resolve("sharp", { paths: [path.join(import.meta.dirname, "..", "render")] }));

const [pagePath, outPath, ...flags] = process.argv.slice(2);
if (!pagePath || !outPath) {
  console.error("usage: node tools/viz/shot.mjs PAGE.html OUT.png [--desktop|--phone]");
  process.exit(2);
}

const SKELETON_HEAD = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#faf9f7}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>`;

const LOOKS = {
  desktop: { width: 960, height: 800, deviceScaleFactor: 1, scheme: "light" },
  phone: { width: 390, height: 844, deviceScaleFactor: 2, scheme: "dark" },
};

async function capture(browser, file, look) {
  const page = await browser.newPage();
  const said = [];
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") said.push(`console ${m.type()}: ${m.text()}`); });
  page.on("pageerror", (e) => said.push(`page error: ${e.message}`));
  page.on("requestfailed", (r) => said.push(`request failed: ${r.url().slice(0, 120)} (${r.failure()?.errorText})`));
  await page.setViewport({ width: look.width, height: look.height, deviceScaleFactor: look.deviceScaleFactor });
  await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: look.scheme }]);
  await page.goto("file://" + file, { waitUntil: "load", timeout: 120000 });
  await page.waitForFunction(() => window.__vizReady === true, { timeout: 120000 }).catch(() => said.push("the page never said it was ready (120 s)"));
  const reading = await page.evaluate(() => {
    const stages = [...document.querySelectorAll(".viz-stage[data-3d]")];
    return {
      stages: stages.length,
      drawn: stages.filter((s) => s.querySelector("canvas")).length,
      errors: [...document.querySelectorAll(".viz-note.is-error")].map((n) => n.textContent),
      width: document.documentElement.scrollWidth,
    };
  });
  const png = await page.screenshot({ fullPage: true, type: "png" });
  await page.close();
  const name = `${look.width}px ${look.scheme}`;
  console.log(`${name}: ${reading.drawn}/${reading.stages} 3D stages drawn`
    + (reading.width > look.width ? `, page scrolls sideways (${reading.width}px)` : ""));
  for (const e of reading.errors) console.log(`  stage error: ${e}`);
  for (const s of said) console.log(`  ${s}`);
  return png;
}

await sweepAbandonedBrowsers("viz");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "viz-shot-"));
const wrapped = path.join(tmp, "page.html");
fs.writeFileSync(wrapped, SKELETON_HEAD + fs.readFileSync(pagePath, "utf8") + "</body></html>");

const which = flags.includes("--desktop") ? ["desktop"] : flags.includes("--phone") ? ["phone"] : ["desktop", "phone"];
const browser = await launchBrowser({ protocolTimeout: 180000 });
try {
  const shots = [];
  for (const w of which) shots.push(await capture(browser, wrapped, LOOKS[w]));
  if (shots.length === 1) {
    fs.writeFileSync(outPath, shots[0]);
  } else {
    const metas = await Promise.all(shots.map((s) => sharp(s).metadata()));
    const gap = 24;
    const width = metas.reduce((w, m) => w + m.width, 0) + gap * (metas.length + 1);
    const height = Math.max(...metas.map((m) => m.height)) + gap * 2;
    let left = gap;
    const layers = shots.map((s, i) => { const l = { input: s, left, top: gap }; left += metas[i].width + gap; return l; });
    await sharp({ create: { width, height, channels: 3, background: "#c9ced9" } }).composite(layers).png().toFile(outPath);
  }
  console.log(outPath);
} finally {
  await closeBrowser(browser);
  fs.rmSync(tmp, { recursive: true, force: true });
}
