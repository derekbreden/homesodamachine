#!/usr/bin/env node
// Capture a mobile-aspect-ratio screenshot of a URL and save as a compressed PNG.
//
// Usage:
//   node tools/render/screenshot-site.js <url> <output-png> [--width=390] [--height=844]
//
// Defaults to iPhone 13/14 viewport (390x844) at 2x DPR (so the PNG is 780x1688
// and stays sharp on retina displays). Sends an iPhone Safari user agent so the
// site renders its mobile layout. Waits for networkidle0 plus document.fonts.ready
// so Montserrat is loaded before capture (otherwise initial paint shows the
// system fallback). Adds a short settle delay so the landing-page glass canvas
// has time to render its first frame.

import path from "path";
import fs from "fs";
import puppeteer from "puppeteer";
import sharp from "sharp";

const IPHONE_UA =
  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 " +
  "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";

function parseArgs(argv) {
  const positional = [];
  const flags = {};
  for (const arg of argv) {
    const m = arg.match(/^--([^=]+)=(.*)$/);
    if (m) {
      flags[m[1]] = m[2];
    } else if (arg.startsWith("--")) {
      flags[arg.slice(2)] = true;
    } else {
      positional.push(arg);
    }
  }
  return { positional, flags };
}

function usageAndExit(message) {
  if (message) console.error(`error: ${message}`);
  console.error(
    "usage: node tools/render/screenshot-site.js <url> <output-png> [--width=390] [--height=844]",
  );
  process.exit(message ? 1 : 0);
}

const { positional, flags } = parseArgs(process.argv.slice(2));
if (flags.help || flags.h) usageAndExit();
if (positional.length < 2) usageAndExit("missing <url> and/or <output-png>");

const [url, outputArg] = positional;
const width = Number(flags.width ?? 390);
const height = Number(flags.height ?? 844);
if (!Number.isFinite(width) || width <= 0) usageAndExit("invalid --width");
if (!Number.isFinite(height) || height <= 0) usageAndExit("invalid --height");

const outputPath = path.resolve(outputArg);
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

const browser = await puppeteer.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.setUserAgent(IPHONE_UA);
  await page.setViewport({ width, height, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: "networkidle0", timeout: 60_000 });

  // Wait for Montserrat (and any other webfonts) to actually load. Without
  // this the first paint can use the system fallback and the screenshot
  // looks wrong.
  await page.evaluate(() => document.fonts.ready);

  // Give Canvas2D loops (the landing page's GlassAnimation) a beat to draw
  // their first frame, otherwise we may capture an empty canvas.
  await new Promise((resolve) => setTimeout(resolve, 600));

  const rawPng = await page.screenshot({ type: "png", fullPage: false });
  const compressed = await sharp(rawPng)
    .png({ compressionLevel: 9, palette: false })
    .toBuffer();
  fs.writeFileSync(outputPath, compressed);

  const { size } = fs.statSync(outputPath);
  console.log(
    `wrote ${outputPath} (${width * 2}x${height * 2}, ${size} bytes)`,
  );
} finally {
  await browser.close();
}
