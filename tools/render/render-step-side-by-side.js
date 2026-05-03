#!/usr/bin/env node
// render-step-side-by-side.js — render TWO STEP files into a single
// side-by-side PNG against the site palette, for posts about part
// redesigns. Boots the prod server in-process, drives a SINGLE Puppeteer
// page through the existing /dev/ viewer to pose+snap each model, then
// stitches the trimmed renders together with sharp.
//
// Usage:
//   node tools/render/render-step-side-by-side.js <step-a> <step-b> <output-png> \
//        [--label-a=<txt>] [--label-b=<txt>] \
//        [--at <date|sha>] [--at-a <date|sha>] [--at-b <date|sha>]
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
// --at <date|sha>           apply the same historical pin to BOTH STEPs.
// --at-a <date|sha>         pin only STEP A (overrides --at).
// --at-b <date|sha>         pin only STEP B (overrides --at).
//   When a pin is set, the corresponding STEP is read from a throwaway git
//   worktree at the resolved commit (most recent commit on `main` on or
//   before <date> 23:59:59, or the literal SHA). All other tooling (this
//   script, server.js, viewer-body.html) stays at HEAD. If a STEP didn't
//   exist at its pinned SHA, the tool exits non-zero with a clear error.
//   The pinned source bytes are staged into a temp combined hardwareDir
//   that the server is pointed at, so the in-page viewer can load both
//   STEPs from one origin (occt-import-js stays cached between renders).
//
// Speed note: occt-import-js is fetched + parsed once on the first STEP
// load (~10-15s). The second load on the same page reuses the cached lib
// (~1s). We drive both renders on the same page to save the second cold
// start.

import path from "path";
import fs from "fs";
import os from "os";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../server.js";
import { withHistoricalTree, registerTempDir, unregisterTempDir } from "./temporal.js";

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
      "<step-a> <step-b> <output-png> [--label-a=<txt>] [--label-b=<txt>] " +
      "[--at <date|sha>] [--at-a <date|sha>] [--at-b <date|sha>]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  const opts = {};
  // Support both --foo=bar and --foo bar (the latter for --at since dates
  // and SHAs don't contain '=').
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const eq = a.match(/^--([a-z-]+)=(.*)$/);
    if (eq) {
      opts[eq[1]] = eq[2];
      continue;
    }
    if (a === "--at" || a === "--at-a" || a === "--at-b") {
      opts[a.slice(2)] = argv[++i] || "";
      continue;
    }
    positional.push(a);
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

// Render the side-by-side output by booting a server pointed at hardwareDir
// and loading the two given relative paths from it.
async function renderPair({
  stepAviewerRel,
  stepBviewerRel,
  hardwareDir,
  outAbs,
  labelA,
  labelB,
}) {
  // Validate both files exist relative to hardwareDir.
  const aAbs = path.join(hardwareDir, stepAviewerRel);
  const bAbs = path.join(hardwareDir, stepBviewerRel);
  if (!fs.existsSync(aAbs)) throw new Error(`step A not found: ${aAbs}`);
  if (!fs.existsSync(bAbs)) throw new Error(`step B not found: ${bAbs}`);

  const { server } = await start({ port: 0, dev: false, hardwareDir });
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
    const url = `http://localhost:${port}/dev/?file=${encodeURIComponent(stepAviewerRel)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    console.log("waiting for viewer module + occt-import-js (cold start)...");
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera && window.__hsm.loadStepFile,
      { timeout: 30000 },
    );

    // Hide chrome so the screenshot only contains the rendered model. The
    // STEP detail now lives inside the ContentViewer modal — hide the
    // filename pill, close X, gizmo cube; expand the modal card to the
    // full viewport so the canvas covers everything; force backgrounds to
    // the site bg so sharp's trim() has a clean color to crop against.
    await page.addStyleTag({
      content: `
        nav, #site-nav, .nav-gear, footer, #site-footer,
        .cv-filename, .cv-close, .cv-backdrop,
        #gizmoCanvas { display: none !important; }
        .cv-card {
          width: 100vw !important; height: 100vh !important;
          max-width: 100vw !important; max-height: 100vh !important;
          border-radius: 0 !important;
        }
        body, html, .cv-card, .cv-content, .step-wrapper, #viewport {
          background: ${BG_HEX} !important;
        }
      `,
    });

    console.log(`snapping ${stepAviewerRel}...`);
    const pngA = await snapModel(page, stepAviewerRel);
    console.log(`  ${pngA.length} bytes (trimmed)`);

    // Second STEP: switch in-place via the exposed loadStepFile() — no
    // navigation, occt-import-js stays cached.
    console.log(`switching to ${stepBviewerRel} on the same page...`);
    await page.evaluate((file) => window.__hsm.loadStepFile(file), stepBviewerRel);

    console.log(`snapping ${stepBviewerRel}...`);
    const pngB = await snapModel(page, stepBviewerRel);
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

// Recursively copy a file (creating parent dirs in dest).
function copyFile(srcAbs, destAbs) {
  fs.mkdirSync(path.dirname(destAbs), { recursive: true });
  fs.copyFileSync(srcAbs, destAbs);
}

// Build a temp combined hardwareDir holding the two source files at
// distinct sub-paths so the viewer URLs don't collide. Returns:
//   { stagedDir, stepAviewerRel, stepBviewerRel, cleanup }
// stagedDir is the directory the server should be pointed at. stepARel
// and stepBRel are the original user-supplied relative paths inside the
// historical hardware/ tree (since they may have come from different
// commits, we can't just pass them through).
function stageHardware({ aSrcAbs, aRel, bSrcAbs, bRel }) {
  const stagedDir = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-render-stage-"));
  // Register before any I/O so a crash mid-copy still cleans up the empty
  // tmp dir.
  registerTempDir(stagedDir);
  // Mirror under __a/<aRel> and __b/<bRel> so paths can collide between A
  // and B without overwriting (e.g. both "foam-bag-shell.step" from
  // different SHAs).
  const aDest = path.join(stagedDir, "__a", aRel);
  const bDest = path.join(stagedDir, "__b", bRel);
  copyFile(aSrcAbs, aDest);
  copyFile(bSrcAbs, bDest);
  const cleanup = () => {
    unregisterTempDir(stagedDir);
    try {
      fs.rmSync(stagedDir, { recursive: true, force: true });
    } catch {
      /* best effort */
    }
  };
  return {
    stagedDir,
    stepAviewerRel: path.posix.join("__a", aRel.split(path.sep).join("/")),
    stepBviewerRel: path.posix.join("__b", bRel.split(path.sep).join("/")),
    cleanup,
  };
}

// Resolve hardwareDir + stepRel for one side. If pinned, run inside a
// `withHistoricalTree(at, ...)` callback that resolves the file's absolute
// path inside the worktree; if not pinned, resolve against REPO_ROOT/hardware.
// The async `inner` is invoked with { srcAbs, rel } where srcAbs is the
// readable absolute path of the source file. The worktree (if any) survives
// for the duration of the inner callback.
async function withSidePath(at, rel, inner) {
  if (!at) {
    const srcAbs = path.join(REPO_ROOT, "hardware", rel);
    if (!fs.existsSync(srcAbs)) {
      throw new Error(`step file not found at HEAD: ${srcAbs}`);
    }
    return inner({ srcAbs, rel });
  }
  return withHistoricalTree(at, async (worktreeDir, sha) => {
    const srcAbs = path.join(worktreeDir, "hardware", rel);
    if (!fs.existsSync(srcAbs)) {
      throw new Error(
        `step file not found at sha=${sha.slice(0, 7)} (--at ${at}): ${rel}`,
      );
    }
    return inner({ srcAbs, rel, sha });
  });
}

async function main() {
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [stepA, stepB, outRel] = positional;
  if (!stepA || !stepB || !outRel) usage("missing arguments");
  const labelA = opts["label-a"] || null;
  const labelB = opts["label-b"] || null;

  // --at-a / --at-b override --at for that side.
  const atA = opts["at-a"] || opts["at"] || null;
  const atB = opts["at-b"] || opts["at"] || null;

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  // Fast path: no historical pin on either side. Just point the server at
  // REPO_ROOT/hardware as before.
  if (!atA && !atB) {
    const stepAabs = path.join(REPO_ROOT, "hardware", stepA);
    const stepBabs = path.join(REPO_ROOT, "hardware", stepB);
    if (!fs.existsSync(stepAabs)) usage(`step A not found: ${stepAabs}`);
    if (!fs.existsSync(stepBabs)) usage(`step B not found: ${stepBabs}`);
    await renderPair({
      stepAviewerRel: stepA,
      stepBviewerRel: stepB,
      hardwareDir: path.join(REPO_ROOT, "hardware"),
      outAbs,
      labelA,
      labelB,
    });
    return;
  }

  // At least one side is pinned. Resolve each side's source file under its
  // (optional) worktree, stage both into a combined temp hardwareDir, and
  // point the server there.
  if (atA) console.log(`--at-a ${atA}: resolving A from past commit...`);
  if (atB) console.log(`--at-b ${atB}: resolving B from past commit...`);

  // Nest the two withSidePath calls so both worktrees are alive while the
  // staging dir is built (we copy out of them) — though after that the
  // worktrees are no longer needed. We still let the closures run to
  // completion before returning so cleanup is deterministic.
  await withSidePath(atA, stepA, async ({ srcAbs: aSrcAbs, rel: aRel }) => {
    await withSidePath(atB, stepB, async ({ srcAbs: bSrcAbs, rel: bRel }) => {
      const { stagedDir, stepAviewerRel, stepBviewerRel, cleanup } =
        stageHardware({ aSrcAbs, aRel, bSrcAbs, bRel });
      try {
        console.log(`staged hardwareDir: ${stagedDir}`);
        await renderPair({
          stepAviewerRel,
          stepBviewerRel,
          hardwareDir: stagedDir,
          outAbs,
          labelA,
          labelB,
        });
      } finally {
        cleanup();
      }
    });
  });
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
