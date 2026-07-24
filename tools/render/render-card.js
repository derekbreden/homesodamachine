#!/usr/bin/env node
// render-card.js — render a local HTML file to a PNG at an exact pixel size.
// For print artifacts (4x6 assembly instruction cards) where the pixel grid
// IS the deliverable: no device emulation, no trimming, no resampling.
//
// Usage:
//   node tools/render/render-card.js <input.html> <output-png> [options]
//   node tools/render/render-card.js --batch <dir> <out-dir> [options]
//
// Options:
//   --size WxH   viewport = output pixels at DPR 1. Default 1800x1200 (6x4in @ 300dpi)
//   --dpr f      deviceScaleFactor; output = size · dpr. Default 1
//                (1.2 → 2160x1440 = 360dpi, the EcoTank's native grid)
//
// Batch mode renders every *.html in <dir> (sorted) to <out-dir>/<name>.png in
// one browser session, and reports any card whose content overflows the
// viewport — an overflowing card is a layout bug, not a printable card.

import path from "path";
import fs from "fs";
import { pathToFileURL } from "url";
import puppeteer from "puppeteer";

function usage(msg) {
  if (msg) console.error(`render-card: ${msg}`);
  console.error(
    "usage: node tools/render/render-card.js <input.html> <output-png> [--size WxH] [--dpr f]\n" +
      "       node tools/render/render-card.js --batch <dir> <out-dir> [--size WxH] [--dpr f]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  const opts = { width: 1800, height: 1200, dpr: 1, batch: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a.startsWith("--size")) {
      const m = String(val()).match(/^(\d+)x(\d+)$/);
      if (!m) usage("bad --size");
      opts.width = Number(m[1]);
      opts.height = Number(m[2]);
    } else if (a.startsWith("--dpr")) opts.dpr = Number(val());
    else if (a === "--batch") opts.batch = true;
    else positional.push(a);
  }
  if (!Number.isFinite(opts.dpr) || opts.dpr <= 0) usage("bad --dpr");
  return { positional, opts };
}

async function renderPage(page, htmlAbs, outAbs, opts) {
  await page.goto(pathToFileURL(htmlAbs).href, {
    waitUntil: "networkidle0",
    timeout: 60000,
  });
  // Fonts can land after networkidle0; block on the font readiness promise.
  await page.evaluate(() => document.fonts.ready);

  // A card that scrolls is a card that will be cropped at print — and so is
  // one whose flex/grid children get clipped inside an overflow:hidden root
  // without ever growing scrollWidth/Height. Catch both: scan every element's
  // border box against the canvas (2px grace for antialiased edges).
  const overflow = await page.evaluate(() => {
    const W = document.documentElement.clientWidth;
    const H = document.documentElement.clientHeight;
    let x = document.documentElement.scrollWidth - W;
    let y = document.documentElement.scrollHeight - H;
    const clipped = [];
    for (const el of document.querySelectorAll("body *")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      const over = Math.max(r.right - W, r.bottom - H);
      if (over > 2) {
        clipped.push(
          `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""}+${Math.round(over)}px`,
        );
        x = Math.max(x, r.right - W);
        y = Math.max(y, r.bottom - H);
      }
    }
    return { x: Math.max(0, Math.round(x)), y: Math.max(0, Math.round(y)), clipped: clipped.slice(0, 5) };
  });

  await page.screenshot({
    path: outAbs,
    type: "png",
    clip: { x: 0, y: 0, width: opts.width, height: opts.height },
  });
  return overflow;
}

async function main() {
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [inRel, outRel] = positional;
  if (!inRel || !outRel) usage("missing arguments");

  const jobs = [];
  if (opts.batch) {
    const dir = path.resolve(inRel);
    const outDir = path.resolve(outRel);
    fs.mkdirSync(outDir, { recursive: true });
    const files = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(".html"))
      .sort();
    if (!files.length) usage(`no .html files in ${dir}`);
    for (const f of files) {
      jobs.push({
        htmlAbs: path.join(dir, f),
        outAbs: path.join(outDir, f.replace(/\.html$/, ".png")),
      });
    }
  } else {
    const outAbs = path.resolve(outRel);
    fs.mkdirSync(path.dirname(outAbs), { recursive: true });
    jobs.push({ htmlAbs: path.resolve(inRel), outAbs });
  }

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--force-color-profile=srgb"],
  });
  let overflowed = 0;
  try {
    const page = await browser.newPage();
    await page.setViewport({
      width: opts.width,
      height: opts.height,
      deviceScaleFactor: opts.dpr,
    });
    for (const job of jobs) {
      const overflow = await renderPage(page, job.htmlAbs, job.outAbs, opts);
      const flag =
        overflow.x > 0 || overflow.y > 0
          ? `  OVERFLOW x=${overflow.x}px y=${overflow.y}px [${overflow.clipped.join(", ")}]`
          : "";
      if (flag) overflowed++;
      console.log(`wrote ${job.outAbs}${flag}`);
    }
  } finally {
    await browser.close();
  }
  if (overflowed) {
    console.error(`${overflowed} card(s) overflow the ${opts.width}x${opts.height} canvas`);
    process.exit(2);
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
