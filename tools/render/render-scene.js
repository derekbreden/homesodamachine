#!/usr/bin/env node
// render-scene.js — render a multi-part CadQuery glTF scene as a PNG
// through the /scene viewer (three.js, z-buffer occlusion, line-art
// aesthetic).
//
// Sibling to render-step.js. The STEP path goes through the
// occt-import-js viewer at /3d and produces a single-part shaded
// screenshot; this path goes through the line-art renderer at /scene
// and produces a multi-part drawing with colored markings occluded
// correctly by the geometry in front of them.
//
// Usage:
//   node tools/render/render-scene.js <glb-repo-relative> <output-png> [--view iso-front|iso-back] [--size WxH]
// Example:
//   node tools/render/render-scene.js \
//     hardware/printed-parts/enclosure/scene/scene.glb \
//     hardware/printed-parts/enclosure/scene/iso-front.png \
//     --view iso-front

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../web/server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function usage(msg) {
  if (msg) console.error(`render-scene: ${msg}`);
  console.error(
    "usage: node tools/render/render-scene.js <glb-repo-relative> <output-png> [--view iso-front|iso-back] [--size WxH]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  let view = "iso-front";
  let size = { w: 1600, h: 1200 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--view") view = argv[++i];
    else if (a.startsWith("--view=")) view = a.slice(7);
    else if (a === "--size") {
      const v = argv[++i];
      const m = /^(\d+)x(\d+)$/.exec(v || "");
      if (!m) usage(`bad --size: ${v}`);
      size = { w: +m[1], h: +m[2] };
    } else if (a.startsWith("--size=")) {
      const m = /^(\d+)x(\d+)$/.exec(a.slice(7));
      if (!m) usage(`bad --size: ${a}`);
      size = { w: +m[1], h: +m[2] };
    } else {
      positional.push(a);
    }
  }
  return { positional, view, size };
}

async function renderOne({ glbRel, outAbs, view, size }) {
  const glbAbs = path.join(REPO_ROOT, glbRel);
  if (!fs.existsSync(glbAbs)) {
    throw new Error(`glb file not found: ${glbAbs}`);
  }

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
    await page.setViewport({ width: size.w, height: size.h, deviceScaleFactor: 2 });

    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      const t = msg.type();
      if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
    });

    const url = `http://localhost:${port}/scene?file=${encodeURIComponent(glbRel)}&view=${encodeURIComponent(view)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    // Wait for the scene module to expose its handle.
    console.log("waiting for scene module...");
    await page.waitForFunction(
      () => window.__hsm_scene && window.__hsm_scene.scene,
      { timeout: 30000 },
    );

    // Wait for the glb to load + render. The viewer sets ready=true after
    // poseFor + render; surfaces a load error via .error.
    console.log("waiting for scene to mount...");
    await page.waitForFunction(
      () => window.__hsm_scene && (window.__hsm_scene.ready || window.__hsm_scene.error),
      { timeout: 60000 },
    );
    const err = await page.evaluate(() => window.__hsm_scene.error || null);
    if (err) throw new Error(`scene load: ${err}`);

    // Re-render once after layout settles, so the canvas at the final
    // viewport size captures with the framed model. The auto-load path
    // already rendered, but the canvas may have been sized before the
    // viewport finalized.
    await page.evaluate(() => {
      window.__hsm_scene.poseFor(new URLSearchParams(location.search).get("view") || "iso-front");
      window.__hsm_scene.render();
    });
    await new Promise((r) => setTimeout(r, 100));

    console.log("snapping screenshot...");
    const raw = await page.screenshot({ type: "png", omitBackground: false });

    // Trim white margins to fit the model tightly, then re-pad with a small
    // border so the strokes don't hug the image edge.
    console.log("trimming + padding...");
    const trimmed = await sharp(raw)
      .trim({ background: "#ffffff", threshold: 10 })
      .toBuffer();
    const meta = await sharp(trimmed).metadata();
    const PAD = 16;
    const buf = await sharp(trimmed)
      .extend({
        top: PAD, bottom: PAD, left: PAD, right: PAD,
        background: "#ffffff",
      })
      .png()
      .toBuffer();
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
  const { positional, view, size } = parseArgs(process.argv.slice(2));
  const [glbRel, outRel] = positional;
  if (!glbRel || !outRel) usage("missing arguments");
  if (view !== "iso-front" && view !== "iso-back") usage(`bad --view: ${view}`);

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  await renderOne({ glbRel, outAbs, view, size });
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
