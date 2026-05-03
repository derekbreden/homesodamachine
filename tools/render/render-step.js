#!/usr/bin/env node
// render-step.js — render a STEP file as an isometric PNG against the site
// palette by booting the prod server in-process, driving Puppeteer through
// the existing /dev/ viewer, and trimming + resizing the frame with sharp.
//
// Usage:
//   node tools/render/render-step.js <step-file-relative> <output-png> [--at <date|sha>]
// Example:
//   node tools/render/render-step.js \
//     printed-parts/foam-bag-shell/foam-bag-shell.step \
//     public/post-images/foam-bag-shell.png
//
// The step path is relative to hardware/ (matches /api/steps + /steps/*).
// Output path may be relative to repo root or absolute.
//
// --at <date|sha>
//   Render the source STEP as it existed at a past commit. Accepts either a
//   date (resolved to the most recent commit on `main` on or before
//   <date> 23:59:59) or a literal SHA. The current HEAD's tooling is used
//   (server.js, viewer-body.html, this script); only the STEP bytes come
//   from the historical worktree. If the file did not exist at that SHA,
//   the tool exits non-zero with a clear error.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../server.js";
import { withHistoricalTree } from "./temporal.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const BG_HEX = "#1a1a2e";

function usage(msg) {
  if (msg) console.error(`render-step: ${msg}`);
  console.error(
    "usage: node tools/render/render-step.js <step-file-relative> <output-png> [--at <date|sha>]",
  );
  process.exit(1);
}

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

// Render the STEP at <hardwareDir>/<stepRel> to <outAbs>. hardwareDir is
// passed through to server.start so the viewer reads from the historical
// worktree when --at is set.
async function renderOne({ stepRel, outAbs, hardwareDir }) {
  // Validate the STEP exists relative to hardwareDir.
  const stepAbs = path.join(hardwareDir, stepRel);
  if (!fs.existsSync(stepAbs)) {
    throw new Error(`step file not found: ${stepAbs}`);
  }

  // Boot the prod server on an ephemeral port, pointed at hardwareDir.
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

    const url = `http://localhost:${port}/dev/?file=${encodeURIComponent(stepRel)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    // Wait for the viewer module to expose its handles (added in
    // viewer-body.html). occt-import-js is downloaded via a CDN <script>
    // tag, so this can take a few seconds on first load.
    console.log("waiting for viewer module...");
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera,
      { timeout: 30000 },
    );

    // Wait for the STEP itself to mount (viewer sets mountedStepFile after
    // occt-import-js parses the buffer and the mesh is added to the scene).
    console.log("waiting for STEP to mount (occt-import-js parse)...");
    await page.waitForFunction(
      (want) => window.__hsm && window.__hsm.mountedStepFile === want,
      { timeout: 60000 },
      stepRel,
    );

    // Hide chrome so the screenshot only contains the rendered model. The
    // STEP detail now lives inside the ContentViewer modal — hide the
    // filename pill, close X, and gizmo cube; expand the modal card to the
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

    // Pose the camera isometrically per spec: position at center + (1,1,1)
    // normalized · radius · 1.6, look at center, up (0,1,0). Rendering one
    // frame here matters — the viewer's animate loop is driven by
    // OrbitControls.update; without an explicit render the canvas could
    // capture pre-pose pixels.
    console.log("posing camera + rendering frame...");
    await page.evaluate(() => {
      const { THREE, renderer, scene, camera, controls, currentGroup } = window.__hsm;
      const box = new THREE.Box3().setFromObject(currentGroup);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const radius = Math.max(size.x, size.y, size.z) * 0.5;
      // Spec: position at center + (1,1,1) · radius · 1.6 (each component
      // gets radius · 1.6, so distance = sqrt(3) · radius · 1.6 ≈ 2.77r).
      const offset = new THREE.Vector3(1, 1, 1).multiplyScalar(radius * 1.6);
      camera.position.copy(center).add(offset);
      camera.up.set(0, 1, 0);
      camera.lookAt(center);
      controls.target.copy(center);
      controls.update();
      // Make sure the canvas matches the puppeteer viewport.
      renderer.setSize(window.innerWidth, window.innerHeight, false);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.render(scene, camera);
    });

    // Give the browser one more frame so the canvas is composited.
    await new Promise((r) => setTimeout(r, 200));

    console.log("snapping screenshot...");
    const raw = await page.screenshot({ type: "png", omitBackground: false });

    console.log("trimming + resizing...");
    let img = sharp(raw).trim({ background: BG_HEX, threshold: 10 });
    const meta = await img.metadata();
    if (meta.width && meta.width > 1200) {
      img = img.resize({ width: 1200 });
    }
    // Re-flatten on the bg so trim's transparent edges (if any) become solid.
    const buf = await img.flatten({ background: BG_HEX }).png().toBuffer();
    fs.writeFileSync(outAbs, buf);
    const finalMeta = await sharp(buf).metadata();
    console.log(
      `wrote ${outAbs} (${finalMeta.width}x${finalMeta.height}, ${buf.length} bytes)`,
    );
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve, reject) =>
      server.close((err) => (err ? reject(err) : resolve())),
    );
  }
}

async function main() {
  const { positional, at } = parseArgs(process.argv.slice(2));
  const [stepRel, outRel] = positional;
  if (!stepRel || !outRel) usage("missing arguments");

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  if (at) {
    console.log(`--at ${at}: checking out historical tree...`);
    await withHistoricalTree(at, async (worktreeDir, sha) => {
      console.log(`worktree: ${worktreeDir} (sha=${sha.slice(0, 7)})`);
      const hardwareDir = path.join(worktreeDir, "hardware");
      await renderOne({ stepRel, outAbs, hardwareDir });
    });
  } else {
    const hardwareDir = path.join(REPO_ROOT, "hardware");
    await renderOne({ stepRel, outAbs, hardwareDir });
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
