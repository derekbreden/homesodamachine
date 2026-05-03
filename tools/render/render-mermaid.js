#!/usr/bin/env node
// render-mermaid.js — render a .mmd file to a PNG matching the site's dark theme.
//
// Usage: node tools/render/render-mermaid.js <mmd-file> <output-png>
//
// Path B: build a standalone HTML page that imports mermaid from the same CDN
// the dev viewer uses, render the SVG with mermaid.render(), screenshot the
// rendered SVG with puppeteer, then trim/optimize/resize via sharp.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer";
import sharp from "sharp";

// Site palette — keep in sync with viewer-body.html.
const BG = "#1a1a2e";
const PADDING = 24;
const MAX_WIDTH = 1200;

// Theme variables copied from tools/step-viewer/templates/viewer-body.html
// so the rendered diagram matches what users see at /dev/diagrams.
const THEME_VARIABLES = {
  darkMode: true,
  background: "#1a1a2e",
  primaryColor: "#2a2a4a",
  primaryTextColor: "#ffffff",
  primaryBorderColor: "#3a3a5a",
  lineColor: "#999999",
  secondaryColor: "#232342",
  tertiaryColor: "#1a1a2e",
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif",
  fontSize: "14px",
};

function buildHtml(mmdSource) {
  // The mermaid source is passed via a script-tag textContent (not a JS string
  // literal), so we don't have to escape backticks or backslashes inside the
  // diagram. We do still need to escape </script> sequences.
  const safe = mmdSource.replace(/<\/script>/gi, "<\\/script>");
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: ${BG};
  }
  body {
    padding: ${PADDING}px;
    display: inline-block;
  }
  #out svg {
    display: block;
    background: ${BG};
  }
</style>
</head>
<body>
<script id="mmd-source" type="text/plain">${safe}</script>
<div id="out"></div>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    themeVariables: ${JSON.stringify(THEME_VARIABLES)},
    flowchart: { htmlLabels: true, curve: "basis", padding: 12 },
  });
  const src = document.getElementById("mmd-source").textContent;
  try {
    const { svg } = await mermaid.render("g", src);
    document.getElementById("out").innerHTML = svg;
    // Mermaid renders width="100%" with a viewBox. Replace with explicit
    // pixel dimensions taken from the viewBox so the SVG occupies its true
    // rendered size (otherwise it collapses to a tiny default in an
    // inline-block body and the screenshot is unreadable).
    const el = document.querySelector("#out svg");
    const vb = el.getAttribute("viewBox");
    if (vb) {
      const [, , w, h] = vb.split(/[ ,]+/).map(Number);
      el.setAttribute("width", String(w));
      el.setAttribute("height", String(h));
      el.style.width = w + "px";
      el.style.height = h + "px";
    }
    window.__mmd_done = true;
  } catch (err) {
    window.__mmd_error = String((err && err.message) || err);
  }
</script>
</body>
</html>`;
}

async function main() {
  const [, , inputArg, outputArg] = process.argv;
  if (!inputArg || !outputArg) {
    console.error(
      "Usage: node tools/render/render-mermaid.js <mmd-file> <output-png>"
    );
    process.exit(2);
  }
  const inputPath = path.resolve(inputArg);
  const outputPath = path.resolve(outputArg);
  if (!fs.existsSync(inputPath)) {
    console.error(`Input not found: ${inputPath}`);
    process.exit(1);
  }
  const mmdSource = fs.readFileSync(inputPath, "utf-8");

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });
  try {
    const page = await browser.newPage();
    // Generous viewport so wide diagrams render at full size.
    await page.setViewport({ width: 2400, height: 1800, deviceScaleFactor: 2 });
    await page.setContent(buildHtml(mmdSource), { waitUntil: "networkidle0" });

    // Wait for either success flag or error.
    await page.waitForFunction(
      "window.__mmd_done === true || typeof window.__mmd_error === 'string'",
      { timeout: 30000 }
    );
    const err = await page.evaluate(() => window.__mmd_error);
    if (err) {
      throw new Error(`mermaid.render failed: ${err}`);
    }

    // If the SVG turned out wider than the viewport, expand the viewport so
    // body.screenshot captures the full content (a too-narrow viewport
    // clips the body to its visible width).
    const svgBox = await page.evaluate(() => {
      const el = document.querySelector("#out svg");
      const r = el.getBoundingClientRect();
      return { w: Math.ceil(r.width), h: Math.ceil(r.height) };
    });
    const needW = svgBox.w + PADDING * 2 + 64;
    const needH = svgBox.h + PADDING * 2 + 64;
    if (needW > 2400 || needH > 1800) {
      await page.setViewport({
        width: Math.max(2400, needW),
        height: Math.max(1800, needH),
        deviceScaleFactor: 2,
      });
    }

    // Screenshot the body so we keep the configured PADDING and BG.
    const body = await page.$("body");
    const buffer = await body.screenshot({ type: "png", omitBackground: false });

    // Trim mermaid's whitespace around the SVG, then add a uniform PADDING
    // back so the diagram has a clean dark gutter on the blog post.
    const trimmed = await sharp(buffer).trim({ background: BG }).toBuffer();
    const padded = await sharp(trimmed)
      .extend({
        top: PADDING,
        bottom: PADDING,
        left: PADDING,
        right: PADDING,
        background: BG,
      })
      .toBuffer();

    let pipe = sharp(padded);
    const m = await sharp(padded).metadata();
    if (m.width > MAX_WIDTH) {
      pipe = pipe.resize({ width: MAX_WIDTH });
    }
    await pipe.png({ compressionLevel: 9 }).toFile(outputPath);

    const finalMeta = await sharp(outputPath).metadata();
    const stat = fs.statSync(outputPath);
    console.log(
      `Rendered ${path.relative(process.cwd(), inputPath)} -> ` +
        `${path.relative(process.cwd(), outputPath)} ` +
        `(${finalMeta.width}x${finalMeta.height}, ${(stat.size / 1024).toFixed(
          1
        )} KiB)`
    );
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
