#!/usr/bin/env node
// Capture a mobile-aspect-ratio screenshot of a URL and save as a compressed PNG.
//
// Usage:
//   node tools/render/screenshot-site.js <url-or-path> <output-png>
//                                        [--width=390] [--height=844]
//                                        [--at <date|sha>]
//
// Defaults to iPhone 13/14 viewport (390x844) at 2x DPR (so the PNG is 780x1688
// and stays sharp on retina displays). Sends an iPhone Safari user agent so the
// site renders its mobile layout. Waits for networkidle0 plus document.fonts.ready
// so Montserrat is loaded before capture (otherwise initial paint shows the
// system fallback). Adds a short settle delay so the landing-page glass canvas
// has time to render its first frame.
//
// --at <date|sha>
//   Boot the historical server from a throwaway git worktree at the resolved
//   commit (most recent commit on `main` on or before <date> 23:59:59, or the
//   literal SHA), then screenshot http://localhost:<ephemeral-port><path>.
//   With --at, the first arg MUST be a path (e.g. "/", "/blog", "/dev"), not
//   a full URL — the tool prefixes baseUrl itself.
//   Without --at, current behavior is preserved: the first arg is treated as
//   a fully-qualified URL and puppeteer hits it directly.

import path from "path";
import fs from "fs";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { withHistoricalServer } from "./temporal.js";

const IPHONE_UA =
  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 " +
  "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";

function parseArgs(argv) {
  const positional = [];
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const m = arg.match(/^--([^=]+)=(.*)$/);
    if (m) {
      flags[m[1]] = m[2];
    } else if (arg === "--at") {
      flags.at = argv[++i] ?? "";
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
    "usage: node tools/render/screenshot-site.js <url-or-path> <output-png> " +
      "[--width=390] [--height=844] [--at <date|sha>]",
  );
  process.exit(message ? 1 : 0);
}

const { positional, flags } = parseArgs(process.argv.slice(2));
if (flags.help || flags.h) usageAndExit();
if (positional.length < 2)
  usageAndExit("missing <url-or-path> and/or <output-png>");

const [target, outputArg] = positional;
const at = flags.at || null;
const width = Number(flags.width ?? 390);
const height = Number(flags.height ?? 844);
if (!Number.isFinite(width) || width <= 0) usageAndExit("invalid --width");
if (!Number.isFinite(height) || height <= 0) usageAndExit("invalid --height");

const looksLikeFullUrl = /^https?:\/\//i.test(target);
if (at && looksLikeFullUrl) {
  usageAndExit(
    "with --at, the first argument must be a path (e.g. '/', '/blog'), " +
      "not a full URL; the tool prefixes http://localhost:<port> itself",
  );
}
if (!at && !looksLikeFullUrl) {
  usageAndExit(
    "without --at, the first argument must be a fully-qualified URL " +
      "(e.g. 'https://homesodamachine.com/')",
  );
}

const outputPath = path.resolve(outputArg);
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

// Capture one screenshot at `url` and write it to outputPath.
async function capture(url) {
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
}

if (at) {
  console.log(`--at ${at}: booting historical server from worktree...`);
  await withHistoricalServer(at, async ({ baseUrl, sha }) => {
    const pathPart = target.startsWith("/") ? target : `/${target}`;
    const url = `${baseUrl}${pathPart}`;
    console.log(`historical server up (sha=${sha.slice(0, 7)}); fetching ${url}`);
    await capture(url);
  });
} else {
  await capture(target);
}
