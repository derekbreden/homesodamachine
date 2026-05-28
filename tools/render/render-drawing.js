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
// output has black strokes inline on every line/path; the CSS rule
// !important would beat them, but sharp's renderer doesn't always honor
// `!important` — replace the inline attributes directly instead.
function recolorSvg(svgText) {
  // Recolor black strokes to <STROKE> everywhere. The CadQuery HLR
  // generator writes stroke="black"; the Blender Freestyle pipeline
  // writes stroke="rgb(0, 0, 0)". Match both (any color stays untouched,
  // e.g. the red CO2-port disc's fill="rgb(255, 0, 0)").
  return svgText.replace(
    /stroke="(?:black|#000(?:000)?|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\))"/gi,
    `stroke="${STROKE}"`,
  );
}

async function renderOne({ inPath, outPath, historicalRoot }) {
  const svgPath = resolveSvgPath(inPath, historicalRoot);
  const svgText = recolorSvg(fs.readFileSync(svgPath, "utf-8"));

  // Pick a sharp density that produces a raster wider than the source's
  // natural mm dimension but capped at MAX_WIDTH. sharp.metadata() on a
  // Sharp pipeline returns the *source* metadata (the input SVG's
  // natural-size raster at the requested density), not the post-resize
  // result — so to land at MAX_WIDTH we have to bake the resize into the
  // materialized buffer below, then re-measure that buffer for the
  // composite. (An earlier version read metadata pre-resize and built a
  // 10800-px-wide background; the foreground was resized down to 1200,
  // and the composite quietly stretched the bg to the natural source
  // dimensions in mm.)
  const buffer = Buffer.from(svgText, "utf-8");

  const foregroundPng = await sharp(buffer, { density: 192 })
    .resize({ width: MAX_WIDTH, withoutEnlargement: true })
    .png()
    .toBuffer();
  const fgMeta = await sharp(foregroundPng).metadata();
  const w = fgMeta.width || MAX_WIDTH;
  const h = fgMeta.height || MAX_WIDTH;
  const finalW = w + PADDING * 2;
  const finalH = h + PADDING * 2;

  // Composite onto a dark background with padding so the result reads
  // against the site's surface. Without this the SVG renders on a
  // transparent canvas and the strokes would be invisible against a
  // dark page (which is where post thumbnails get embedded).
  await sharp({
    create: {
      width: finalW,
      height: finalH,
      channels: 3,
      background: BG,
    },
  })
    .composite([{ input: foregroundPng, top: PADDING, left: PADDING }])
    .png()
    .toFile(path.resolve(outPath));

  console.log(`Wrote ${outPath} (${finalW} × ${finalH})`);
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

  if (at) {
    console.log(`--at ${at}: checking out historical tree...`);
    await withHistoricalTree(at, async (worktreeDir, sha) => {
      console.log(`worktree: ${worktreeDir} (sha=${sha.slice(0, 7)})`);
      await renderOne({ inPath, outPath, historicalRoot: worktreeDir });
    });
  } else {
    await renderOne({ inPath, outPath, historicalRoot: null });
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
