#!/usr/bin/env node
// render-dxf.js — render a DXF cut part as an isometric PNG against the
// site palette by booting the prod server in-process, driving Puppeteer
// through the existing /3d viewer (which extrudes the flat outline by
// the sidecar's thickness_mm into a real 3D plate), and trimming +
// resizing the frame with sharp.
//
// Usage:
//   node tools/render/render-dxf.js <dxf-file-relative> <output-png> [--at <date|sha>]
// Example:
//   node tools/render/render-dxf.js \
//     cut-parts/faucet/touch-flo-under-counter-plate/touch-flo-under-counter-plate.dxf \
//     public/post-images/touch-flo-under-counter-plate.png
//
// The dxf path is relative to hardware/ (matches /api/dxf + /dxfs/*).
// Output path may be relative to repo root or absolute.
//
// The viewer needs the part's `<file>.dxf.json` sidecar (see
// hardware/README.md) for thickness_mm. Without one, the screenshot is
// the wireframe top-down view, not an extruded plate.
//
// --at <date|sha>
//   Render the source DXF as it existed at a past commit. Accepts either
//   a date (resolved to the most recent commit on `main` on or before
//   <date> 23:59:59) or a literal SHA. The current HEAD's tooling is
//   used (server.js, viewer-body.html, this script); only the DXF bytes
//   come from the historical worktree. If the file did not exist at
//   that SHA, the tool exits non-zero with a clear error.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { PARSE_TIMEOUT, closeBrowser, launchBrowser, sweepAbandonedBrowsers } from "./browser.js";
import sharp from "sharp";

import { start } from "../../web/server.js";
import { withHistoricalTree } from "./temporal.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const BG_HEX = "#1a1a2e";

function usage(msg) {
  if (msg) console.error(`render-dxf: ${msg}`);
  console.error(
    "usage: node tools/render/render-dxf.js <dxf-file-relative> <output-png> [--at <date|sha>]",
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

// Render the DXF at <hardwareDir>/<dxfRel> to <outAbs>. hardwareDir is
// passed through to server.start so the viewer reads from the historical
// worktree when --at is set.
async function renderOne({ dxfRel, outAbs, hardwareDir }) {
  const dxfAbs = path.join(hardwareDir, dxfRel);
  if (!fs.existsSync(dxfAbs)) {
    throw new Error(`dxf file not found: ${dxfAbs}`);
  }

  const { server } = await start({ port: 0, dev: false, hardwareDir });
  const port = server.address().port;
  console.log(`server up on :${port}`);

  let browser;
  try {
    browser = await launchBrowser({ protocolTimeout: PARSE_TIMEOUT + 60000 });
    const page = await browser.newPage();
    await page.setViewport({ width: 1600, height: 1200, deviceScaleFactor: 1 });

    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      const t = msg.type();
      if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
    });

    const url = `http://localhost:${port}/3d?file=${encodeURIComponent(dxfRel)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    console.log("waiting for viewer module...");
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera,
      { timeout: 30000 },
    );

    console.log("waiting for DXF to mount...");
    await page.waitForFunction(
      (want) => window.__hsm && window.__hsm.mountedDxfFile === want,
      { timeout: 30000 },
      dxfRel,
    );

    // Hide chrome so the screenshot only contains the rendered model.
    // Same overrides as render-step.js since both surface inside the
    // shared ContentViewer modal with a .cad-wrapper.
    //
    // Anything that lives inside .cad-wrapper but ISN'T the renderer
    // canvas must be hidden too, or sharp's trim() will anchor on it
    // and leave dead space around the part. The list below covers every
    // chrome element cad-detail.js attaches alongside the viewport:
    // gizmo cube, loading pill, ruler toggle, reset-view button. If a
    // new chrome element gets added to the wrapper, add it here too.
    await page.addStyleTag({
      content: `
        nav, #site-nav, .nav-gear, footer, #site-footer,
        .cv-filename, .cv-close, .cv-backdrop,
        #gizmoCanvas,
        .cad-wrapper > .cad-loading,
        .cad-wrapper > .ruler-toggle,
        .cad-wrapper > .reset-view { display: none !important; }
        .cv-card {
          width: 100vw !important; height: 100vh !important;
          max-width: 100vw !important; max-height: 100vh !important;
          border-radius: 0 !important;
        }
        body, html, .cv-card, .cv-content, .cad-wrapper, #viewport {
          background: ${BG_HEX} !important;
        }
      `,
    });

    // Pose the camera 3/4 isometric. Same factor (1.6) as render-step
    // for visual consistency between Prints and Cuts in blog posts.
    // Up is +Z so the plate's top stays on top of the screen — DXF
    // extrudes in +Z, unlike STEPs which use the natural Y-up.
    console.log("posing camera + rendering frame...");
    await page.evaluate(() => {
      const { THREE, renderer, scene, camera, controls, currentGroup } = window.__hsm;
      const box = new THREE.Box3().setFromObject(currentGroup);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const radius = Math.max(size.x, size.y, size.z) * 0.5;
      const offset = new THREE.Vector3(1, 1, 1).multiplyScalar(radius * 1.6);
      camera.position.copy(center).add(offset);
      camera.up.set(0, 0, 1);
      camera.lookAt(center);
      controls.target.copy(center);
      controls.update();
      renderer.setSize(window.innerWidth, window.innerHeight, false);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.render(scene, camera);
    });

    await new Promise((r) => setTimeout(r, 200));

    console.log("snapping screenshot...");
    const raw = await page.screenshot({ type: "png", omitBackground: false });

    console.log("trimming + resizing...");
    let img = sharp(raw).trim({ background: BG_HEX, threshold: 10 });
    const meta = await img.metadata();
    if (meta.width && meta.height) {
      img = img.resize({
        width: 1200,
        height: 1600,
        fit: "inside",
        withoutEnlargement: true,
      });
    }
    const buf = await img.flatten({ background: BG_HEX }).png().toBuffer();
    fs.writeFileSync(outAbs, buf);
    const finalMeta = await sharp(buf).metadata();
    console.log(
      `wrote ${outAbs} (${finalMeta.width}x${finalMeta.height}, ${buf.length} bytes)`,
    );
  } finally {
    await closeBrowser(browser);
    await new Promise((resolve, reject) =>
      server.close((err) => (err ? reject(err) : resolve())),
    );
  }
}

async function main() {
  sweepAbandonedBrowsers("render-dxf");
  const { positional, at } = parseArgs(process.argv.slice(2));
  const [dxfRel, outRel] = positional;
  if (!dxfRel || !outRel) usage("missing arguments");

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  if (at) {
    console.log(`--at ${at}: checking out historical tree...`);
    await withHistoricalTree(at, async (worktreeDir, sha) => {
      console.log(`worktree: ${worktreeDir} (sha=${sha.slice(0, 7)})`);
      const hardwareDir = path.join(worktreeDir, "hardware");
      await renderOne({ dxfRel, outAbs, hardwareDir });
    });
  } else {
    const hardwareDir = path.join(REPO_ROOT, "hardware");
    await renderOne({ dxfRel, outAbs, hardwareDir });
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
