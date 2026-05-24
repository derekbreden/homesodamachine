#!/usr/bin/env node
// render-drawing.js — render a line-art .svg file (under any drawings/
// directory in hardware/) to a PNG that matches the site's dark theme.
//
// Usage:
//   node tools/render/render-drawing.js <svg-file> <output-png> [--at <date|sha>]
//
// --at <date|sha>
//   Read the .svg source from a throwaway git worktree at the resolved
//   commit (most recent commit on `main` on or before <date> 23:59:59, or
//   the literal SHA). Errors non-zero if the file didn't exist at that SHA.
//
// Approach: the drawing is already an SVG with explicit width/height in mm
// and a matching viewBox; we don't need a browser to render anything.
// Recolor strokes to white-on-dark by injecting a <style> block (the
// generator writes stroke="black" inline; the style overrides without
// touching the source file), then rasterize via sharp.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

import { withHistoricalTree } from "./temporal.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Site palette — keep in sync with viewer-body.html.
const BG = "#1a1a2e";
const STROKE = "#ffffff";
const PADDING = 24;
const MAX_WIDTH = 1200;

function parseArgs(argv) {
  const positional = [];
  let at = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--at") {
      at = argv[++i] || null;
    } else if (a.startsWith("--at=")) {
      at = a.slice(5);
    } else {
      positional.push(a);
    }
  }
  return { positional, at };
}

function resolveSvgPath(input, historicalRoot) {
  // The user can pass an absolute path, a repo-relative path
  // (hardware/printed-parts/.../drawings/foo.svg), or a path relative to
  // hardware/ (printed-parts/.../drawings/foo.svg). Try each in order.
  const root = historicalRoot || REPO_ROOT;
  const candidates = [
    input,
    path.resolve(root, input),
    path.resolve(root, "hardware", input),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c) && c.endsWith(".svg")) return c;
  }
  throw new Error(`Could not find SVG: ${input}`);
}

// Insert a <style> block right after the opening <svg ...> tag so the
// rasterizer sees white strokes against the dark background. Generator
// output has stroke="black" inline on every line/path; the CSS rule
// !important would beat them, but sharp's renderer doesn't always honor
// `!important` — replace the inline attributes directly instead.
function recolorSvg(svgText) {
  // Replace stroke="black" with stroke="<STROKE>" everywhere. The
  // generator only writes "black"; any other color stays untouched.
  return svgText.replace(/stroke="black"/g, `stroke="${STROKE}"`);
}

async function main() {
  const { positional, at } = parseArgs(process.argv.slice(2));
  if (positional.length < 2) {
    console.error(
      "Usage: node tools/render/render-drawing.js <svg-file> <output-png> [--at <date|sha>]",
    );
    process.exit(1);
  }
  const [inPath, outPath] = positional;

  await withHistoricalTree(at, async (historicalRoot) => {
    const svgPath = resolveSvgPath(inPath, historicalRoot);
    const svgText = recolorSvg(fs.readFileSync(svgPath, "utf-8"));

    // sharp can rasterize SVG directly. Density 192 gives a roughly 2x
    // upscaled raster of the source's mm dimensions — sharper than the
    // default 72 dpi and small enough to keep file sizes modest.
    const buffer = Buffer.from(svgText, "utf-8");
    let img = sharp(buffer, { density: 192 });

    const meta = await img.metadata();
    let width = meta.width || MAX_WIDTH;
    if (width > MAX_WIDTH) {
      const scale = MAX_WIDTH / width;
      img = img.resize({ width: MAX_WIDTH });
      width = MAX_WIDTH;
      // Don't need to track height; sharp preserves aspect.
    }

    // Composite onto a dark background with padding so the result reads
    // against the site's surface. Without this the SVG renders on a
    // transparent canvas and the strokes would be invisible against a
    // dark page (which is where post thumbnails get embedded).
    const baseMeta = await img.clone().metadata();
    const w = baseMeta.width || width;
    const h = baseMeta.height || width;
    const finalW = w + PADDING * 2;
    const finalH = h + PADDING * 2;

    const bg = sharp({
      create: {
        width: finalW,
        height: finalH,
        channels: 3,
        background: BG,
      },
    }).png();

    await bg
      .composite([{ input: await img.png().toBuffer(), top: PADDING, left: PADDING }])
      .toFile(path.resolve(outPath));

    console.log(`Wrote ${outPath} (${finalW} × ${finalH})`);
  });
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
