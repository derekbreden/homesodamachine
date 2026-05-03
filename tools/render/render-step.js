#!/usr/bin/env node
// render-step.js — render a STEP file as an isometric PNG against the site
// palette by booting the prod server in-process, driving Puppeteer through
// the existing /dev/ viewer, and trimming + resizing the frame with sharp.
//
// Usage:
//   node tools/render/render-step.js <step-file-relative> <output-png>
// Example:
//   node tools/render/render-step.js \
//     printed-parts/foam-bag-shell/foam-bag-shell.step \
//     public/post-images/foam-bag-shell.png
//
// The step path is relative to hardware/ (matches /api/steps + /steps/*).
// Output path may be relative to repo root or absolute.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const BG_HEX = "#1a1a2e";

function usage(msg) {
  if (msg) console.error(`render-step: ${msg}`);
  console.error("usage: node tools/render/render-step.js <step-file-relative> <output-png>");
  process.exit(1);
}

async function main() {
  const [, , stepRel, outRel] = process.argv;
  if (!stepRel || !outRel) usage("missing arguments");

  // Validate the STEP exists relative to hardware/.
  const stepAbs = path.join(REPO_ROOT, "hardware", stepRel);
  if (!fs.existsSync(stepAbs)) usage(`step file not found: ${stepAbs}`);

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

    // Hide chrome (nav, back button, filename, gizmo cube) and force the
    // backdrop to the site bg so trim() has a clean color to crop against.
    await page.addStyleTag({
      content: `
        nav, #site-nav, #back, #filename, .nav-gear, footer, #site-footer,
        #detail > canvas:nth-of-type(2) { display: none !important; }
        body, html, #detail, #viewport { background: ${BG_HEX} !important; }
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

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
