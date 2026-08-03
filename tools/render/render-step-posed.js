#!/usr/bin/env node
// render-step-posed.js — render a STEP file to PNG with a caller-posed camera,
// for imagery that needs a specific viewpoint (assembly instruction cards).
// Same server + /3d viewer path as render-step.js; differs in taking the
// camera, framing, background, and output size from the CLI instead of the
// fixed isometric pose.
//
// Usage:
//   node tools/render/render-step-posed.js <step-file-relative> <output-png> [options]
//
// Options:
//   --cam x,y,z      camera direction from target (unnormalized ok). Default 1,1,1
//   --target x,y,z   look-at point in model coords. Default: bbox center
//   --zoom f         perspective only: distance = f · bbox-radius along --cam.
//                    Default 3.0. Under --ortho the half-height is the frame and
//                    it fits the subject; tools/render/render-view.js takes an
//                    orthographic half-height in millimetres as --span.
//   --up x,y,z       camera up. Default 0,1,0
//   --size WxH       viewport + output size. Default 1600x1200
//   --bg #hex        background. Default #1a1a2e (site navy)
//   --trim           trim to background and cap long side 1600 (default: off —
//                    cards want the exact framed viewport)
//   --ortho          orthographic projection (dimension-drawing look)
//   --edition id     which machine's tree the step path is in (web/lib/editions.js).
//                    Default kitchen.
//
// The step path is relative to the edition's content root (matches /api/steps +
// /steps/*).

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../web/server.js";
import { DEFAULT_EDITION, EDITION_IDS, editionById } from "../../web/lib/editions.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function usage(msg) {
  if (msg) console.error(`render-step-posed: ${msg}`);
  console.error(
    "usage: node tools/render/render-step-posed.js <step-file-relative> <output-png> " +
      "[--cam x,y,z] [--target x,y,z] [--zoom f] [--up x,y,z] [--size WxH] [--bg #hex] [--trim] [--ortho] " +
      "[--edition id]",
  );
  process.exit(1);
}

function vec(s, name) {
  const parts = String(s).split(",").map(Number);
  if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n)))
    usage(`bad ${name}: ${s}`);
  return parts;
}

function parseArgs(argv) {
  const positional = [];
  const opts = {
    cam: [1, 1, 1],
    target: null,
    zoom: 3.0,
    up: [0, 1, 0],
    width: 1600,
    height: 1200,
    bg: "#1a1a2e",
    trim: false,
    ortho: false,
    edition: DEFAULT_EDITION,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = (flag) => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a.startsWith("--cam")) opts.cam = vec(val("cam"), "--cam");
    else if (a.startsWith("--target")) opts.target = vec(val("target"), "--target");
    else if (a.startsWith("--zoom")) opts.zoom = Number(val("zoom"));
    else if (a.startsWith("--up")) opts.up = vec(val("up"), "--up");
    else if (a.startsWith("--size")) {
      const m = String(val("size")).match(/^(\d+)x(\d+)$/);
      if (!m) usage(`bad --size`);
      opts.width = Number(m[1]);
      opts.height = Number(m[2]);
    } else if (a.startsWith("--bg")) opts.bg = val("bg");
    else if (a.startsWith("--edition")) opts.edition = val("edition");
    else if (a === "--trim") opts.trim = true;
    else if (a === "--ortho") opts.ortho = true;
    else positional.push(a);
  }
  if (!Number.isFinite(opts.zoom) || opts.zoom <= 0) usage("bad --zoom");
  return { positional, opts };
}

async function renderOne({ stepRel, outAbs, opts }) {
  const edition = editionById(opts.edition);
  if (!edition) usage(`unknown --edition ${opts.edition} (have ${EDITION_IDS.join(", ")})`);
  const hardwareDir = path.join(REPO_ROOT, ...edition.dir);
  const stepAbs = path.join(hardwareDir, stepRel);
  if (!fs.existsSync(stepAbs)) throw new Error(`step file not found: ${stepAbs}`);

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
    await page.setViewport({
      width: opts.width,
      height: opts.height,
      deviceScaleFactor: 1,
    });

    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      const t = msg.type();
      if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
    });

    const url = `http://localhost:${port}/3d?file=${encodeURIComponent(stepRel)}`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    console.log("waiting for viewer module...");
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera,
      { timeout: 30000 },
    );

    console.log("waiting for STEP to mount (occt-import-js parse)...");
    await page.waitForFunction(
      (want) => window.__hsm && window.__hsm.mountedStepFile === want,
      { timeout: 120000 },
      stepRel,
    );

    // Same chrome-hiding rationale as render-step.js: everything in the
    // wrapper that isn't the renderer canvas must be hidden or it lands in
    // the frame.
    await page.addStyleTag({
      content: `
        nav, #site-nav, .nav-gear, footer, #site-footer,
        .cv-filename, .cv-close, .cv-backdrop,
        #gizmoCanvas,
        .cad-wrapper > .cad-loading,
        .cad-wrapper > .ruler-toggle,
        .cad-wrapper > .reset-view { display: none !important; }
        /* No interactive chrome of any kind belongs in a still frame. */
        button, [role="button"] { display: none !important; }
        /* Scorecard HUD (sc-* classes, scorecard-3d.js) rides on assemblies. */
        [class^="sc-"], [class*=" sc-"] { display: none !important; }
        .cv-card {
          width: 100vw !important; height: 100vh !important;
          max-width: 100vw !important; max-height: 100vh !important;
          border-radius: 0 !important;
        }
        body, html, .cv-card, .cv-content, .cad-wrapper, #viewport {
          background: ${opts.bg} !important;
        }
      `,
    });

    console.log("posing camera + rendering frame...");
    await page.evaluate(async (o) => {
      const { THREE, renderer, scene, camera, controls, currentGroup } = window.__hsm;

      // scene.js's animate() closes over its own module binding of `camera` and
      // calls controls.update() every frame, so it renders the module's camera at
      // whatever pose the controls carry, not the one set here. It stops, and the
      // controls come off with it. ES modules are singletons, so this is the
      // running instance.
      const sceneMod = await import("/js/viewer/scene.js");
      sceneMod.stopAnimate();
      controls.enabled = false;

      const box = new THREE.Box3().setFromObject(currentGroup);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const radius = Math.max(size.x, size.y, size.z) * 0.5;
      const target = o.target
        ? new THREE.Vector3(...o.target)
        : center.clone();
      const dir = new THREE.Vector3(...o.cam).normalize();
      const aspect = window.innerWidth / window.innerHeight;
      let cam = camera;
      if (o.ortho) {
        // An orthographic camera framing the subject. Its half-height is the
        // frame, so distance along `dir` only has to clear the near plane.
        const half = radius * 1.1;
        cam = new THREE.OrthographicCamera(
          -half * aspect, half * aspect, half, -half, 0.01, radius * 100,
        );
        window.__hsm.camera = cam;
      } else {
        cam.aspect = aspect;
      }
      cam.position.copy(target).add(dir.multiplyScalar(radius * o.zoom));
      cam.up.set(...o.up);
      cam.lookAt(target);
      controls.object = cam;
      controls.target.copy(target);
      renderer.setSize(window.innerWidth, window.innerHeight, false);
      cam.updateProjectionMatrix();
      cam.updateMatrixWorld(true);

      // The viewer's WebGLRenderer is built without preserveDrawingBuffer, so the
      // drawing buffer is undefined once the browser has composited it and a
      // screenshot taken after that reads back blank. Re-render every frame, from
      // the posed camera, so whenever the capture lands there is a fresh frame in
      // the buffer.
      const draw = () => {
        renderer.render(scene, cam);
        window.__hsmPosedRaf = requestAnimationFrame(draw);
      };
      draw();
    }, opts);

    await new Promise((r) => setTimeout(r, 200));

    console.log("snapping screenshot...");
    const raw = await page.screenshot({ type: "png", omitBackground: false });

    let buf = raw;
    if (opts.trim) {
      let img = sharp(raw).trim({ background: opts.bg, threshold: 10 });
      const meta = await img.metadata();
      if (meta.width && meta.height) {
        img = img.resize({
          width: 1600,
          height: 1600,
          fit: "inside",
          withoutEnlargement: true,
        });
      }
      buf = await img.flatten({ background: opts.bg }).png().toBuffer();
    }
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
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [stepRel, outRel] = positional;
  if (!stepRel || !outRel) usage("missing arguments");
  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });
  await renderOne({ stepRel, outAbs, opts });
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
