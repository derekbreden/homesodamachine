#!/usr/bin/env node
// render-step-side-by-side.js — render TWO STEP files into a single
// side-by-side PNG against the site palette, for posts about part
// redesigns. Boots the prod server in-process, drives a SINGLE Puppeteer
// page through the existing /dev/ viewer to pose+snap each model, then
// stitches the trimmed renders together with sharp.
//
// Usage:
//   node tools/render/render-step-side-by-side.js <step-a> <step-b> <output-png> \
//        [--label-a=<txt>] [--label-b=<txt>]
// Example:
//   node tools/render/render-step-side-by-side.js \
//     printed-parts/foam-bag-shell/foam-bag-shell.step \
//     printed-parts/plan-b/foam-bag-shell-racetrack/foam-bag-shell-upper.step \
//     public/post-images/2026-04-15-foam-shell-old-vs-new.png \
//     --label-a="round (before)" --label-b="racetrack (after)"
//
// STEP paths are relative to hardware/ (matches /api/steps + /steps/*).
// Output path may be relative to repo root or absolute.
//
// Speed note: occt-import-js is fetched + parsed once on the first STEP
// load (~10-15s). The second load on the same page reuses the cached lib
// (~1s). We drive both renders on the same page to save the second cold
// start.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Site palette — matches lib/shell.js / public CSS.
const BG_HEX = "#1a1a2e";
const BORDER_HEX = "#3a3a5a";

// Composite layout knobs.
const TARGET_HEIGHT = 600;     // each render is resized to this max-height
const GAP_PX = 16;             // horizontal gap between the two renders
const HAIRLINE_PX = 1;         // vertical divider in BORDER_HEX
const PAD_PX = 24;             // outer padding around the strip
const LABEL_FONT_PX = 14;
const LABEL_GAP_PX = 12;       // gap between render and its label
const MAX_TOTAL_WIDTH = 1400;  // final composite is downscaled to fit this

function usage(msg) {
  if (msg) console.error(`render-step-side-by-side: ${msg}`);
  console.error(
    "usage: node tools/render/render-step-side-by-side.js " +
      "<step-a> <step-b> <output-png> [--label-a=<txt>] [--label-b=<txt>]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  const opts = {};
  for (const a of argv) {
    const m = a.match(/^--([a-z-]+)=(.*)$/);
    if (m) opts[m[1]] = m[2];
    else positional.push(a);
  }
  return { positional, opts };
}

// Pose camera + render one frame, then return a trimmed PNG buffer cropped
// against the site bg. Assumes the viewer is already showing the model
// (mountedStepFile === stepRel).
async function snapModel(page, stepRel) {
  // Wait for the STEP to mount (occt-import-js fetched & parsed, mesh in scene).
  await page.waitForFunction(
    (want) => window.__hsm && window.__hsm.mountedStepFile === want,
    { timeout: 60000 },
    stepRel,
  );

  // Pose camera per spec: position at center + (1,1,1)·radius·1.6, look at
  // center, up (0,1,0). Multiplied by 2 in practice — radius is half the max
  // bbox dim, so 1.6 of half-dim is too tight; 1.6·full-dim frames cleanly.
  await page.evaluate(() => {
    const { THREE, renderer, scene, camera, controls, currentGroup } = window.__hsm;
    const box = new THREE.Box3().setFromObject(currentGroup);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.x, size.y, size.z) * 0.5;
    const dir = new THREE.Vector3(1, 1, 1).normalize();
    camera.position.copy(center).add(dir.multiplyScalar(radius * 1.6 * 2));
    camera.up.set(0, 1, 0);
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
  });
  // One more compositor frame so the canvas has the new pixels.
  await new Promise((r) => setTimeout(r, 200));

  const raw = await page.screenshot({ type: "png", omitBackground: false });

  // Trim against the bg color, then re-flatten to make any transparent
  // edge pixels solid bg again.
  const trimmed = await sharp(raw)
    .trim({ background: BG_HEX, threshold: 10 })
    .flatten({ background: BG_HEX })
    .png()
    .toBuffer();
  return trimmed;
}

// Render a small SVG label as a PNG, transparent bg, white Montserrat 14px.
async function renderLabelPng(text, widthPx) {
  // Escape XML special chars in the label.
  const safe = String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
  const heightPx = Math.ceil(LABEL_FONT_PX * 1.6);
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${widthPx}" height="${heightPx}">
      <style>
        text { font-family: Montserrat, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, sans-serif;
               font-size: ${LABEL_FONT_PX}px; fill: #ffffff; }
      </style>
      <text x="50%" y="50%" text-anchor="middle" dominant-baseline="central">${safe}</text>
    </svg>
  `;
  return sharp(Buffer.from(svg)).png().toBuffer();
}

async function main() {
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [stepA, stepB, outRel] = positional;
  if (!stepA || !stepB || !outRel) usage("missing arguments");
  const labelA = opts["label-a"] || null;
  const labelB = opts["label-b"] || null;

  const stepAabs = path.join(REPO_ROOT, "hardware", stepA);
  const stepBabs = path.join(REPO_ROOT, "hardware", stepB);
  if (!fs.existsSync(stepAabs)) usage(`step A not found: ${stepAabs}`);
  if (!fs.existsSync(stepBabs)) usage(`step B not found: ${stepBabs}`);

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  // Boot the prod server on an ephemeral port.
  const { server } = await start({ port: 0, dev: false });
  const port = server.address().port;
  console.log(`server up on :${port}`);

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1600, height: 1200, deviceScaleFactor: 1 });

    // Surface page errors so a hung wait points at the cause.
    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      const t = msg.type();
      if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
    });

    // First STEP: navigate with ?file=<A> so the viewer's normal init path
    // runs (sets up canvas, animation loop, calls loadStepFile).
    const url = `http://localhost:${port}/dev/?file=${encodeURIComponent(stepA)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    console.log("waiting for viewer module + occt-import-js (cold start)...");
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera && window.__hsm.loadStepFile,
      { timeout: 30000 },
    );

    // Hide chrome (nav, back button, filename, gizmo cube). The detail
    // view's second canvas is the gizmo — hide it. Force the bg color so
    // sharp's trim() has a clean color to crop against.
    await page.addStyleTag({
      content: `
        nav, #site-nav, #back, #filename, .nav-gear, footer, #site-footer,
        #detail > canvas:nth-of-type(2) { display: none !important; }
        body, html, #detail, #viewport { background: ${BG_HEX} !important; }
      `,
    });

    console.log(`snapping ${stepA}...`);
    const pngA = await snapModel(page, stepA);
    console.log(`  ${pngA.length} bytes (trimmed)`);

    // Second STEP: switch in-place via the exposed loadStepFile() — no
    // navigation, occt-import-js stays cached.
    console.log(`switching to ${stepB} on the same page...`);
    await page.evaluate((file) => window.__hsm.loadStepFile(file), stepB);

    console.log(`snapping ${stepB}...`);
    const pngB = await snapModel(page, stepB);
    console.log(`  ${pngB.length} bytes (trimmed)`);

    console.log("compositing side-by-side...");

    // Resize each render to a common max-height while preserving aspect.
    const aResized = await sharp(pngA)
      .resize({ height: TARGET_HEIGHT, withoutEnlargement: false })
      .flatten({ background: BG_HEX })
      .png()
      .toBuffer();
    const bResized = await sharp(pngB)
      .resize({ height: TARGET_HEIGHT, withoutEnlargement: false })
      .flatten({ background: BG_HEX })
      .png()
      .toBuffer();
    const aMeta = await sharp(aResized).metadata();
    const bMeta = await sharp(bResized).metadata();

    const renderRowH = TARGET_HEIGHT;
    const labelStripH = (labelA || labelB)
      ? LABEL_GAP_PX + Math.ceil(LABEL_FONT_PX * 1.6)
      : 0;

    const stripWidth = aMeta.width + GAP_PX + bMeta.width;
    const compW = stripWidth + PAD_PX * 2;
    const compH = renderRowH + labelStripH + PAD_PX * 2;

    // Build composite layers: each render at its column, optional hairline
    // divider centered in the gap, optional labels under each render.
    const composites = [
      { input: aResized, top: PAD_PX, left: PAD_PX },
      { input: bResized, top: PAD_PX, left: PAD_PX + aMeta.width + GAP_PX },
    ];

    // Hairline divider — 1 px wide vertical line in the border color,
    // centered between the two renders, spanning the render row.
    const dividerSvg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${HAIRLINE_PX}" height="${renderRowH}">
        <rect x="0" y="0" width="${HAIRLINE_PX}" height="${renderRowH}" fill="${BORDER_HEX}"/>
      </svg>
    `;
    const dividerPng = await sharp(Buffer.from(dividerSvg)).png().toBuffer();
    composites.push({
      input: dividerPng,
      top: PAD_PX,
      left: PAD_PX + aMeta.width + Math.floor(GAP_PX / 2) - Math.floor(HAIRLINE_PX / 2),
    });

    if (labelA) {
      const labelPng = await renderLabelPng(labelA, aMeta.width);
      composites.push({
        input: labelPng,
        top: PAD_PX + renderRowH + LABEL_GAP_PX,
        left: PAD_PX,
      });
    }
    if (labelB) {
      const labelPng = await renderLabelPng(labelB, bMeta.width);
      composites.push({
        input: labelPng,
        top: PAD_PX + renderRowH + LABEL_GAP_PX,
        left: PAD_PX + aMeta.width + GAP_PX,
      });
    }

    // Build the canvas at full size, composite everything onto it, then
    // optionally downscale the final image to MAX_TOTAL_WIDTH.
    let composite = sharp({
      create: {
        width: compW,
        height: compH,
        channels: 3,
        background: BG_HEX,
      },
    }).composite(composites);

    let finalBuf = await composite.png().toBuffer();
    let finalMeta = await sharp(finalBuf).metadata();
    if (finalMeta.width && finalMeta.width > MAX_TOTAL_WIDTH) {
      finalBuf = await sharp(finalBuf)
        .resize({ width: MAX_TOTAL_WIDTH })
        .flatten({ background: BG_HEX })
        .png()
        .toBuffer();
      finalMeta = await sharp(finalBuf).metadata();
    }

    fs.writeFileSync(outAbs, finalBuf);
    console.log(
      `wrote ${outAbs} (${finalMeta.width}x${finalMeta.height}, ${finalBuf.length} bytes)`,
    );
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve, reject) =>
      server.close((err) => (err ? reject(err) : resolve())),
    );
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
