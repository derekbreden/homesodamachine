#!/usr/bin/env node
// render.js — drive scene.html with puppeteer, screenshot the rendered
// iso line-art view to PNG.
//
// Usage:
//   node tools/render/iso-line-art/render.js <out.png> [--width N] [--height N]
//
// Starts a tiny static server rooted at this directory, navigates to
// scene.html, waits for the model to load and render, then screenshots.

import path from "path";
import fs from "fs";
import http from "http";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const positional = [];
  let width = 1600;
  let height = 1200;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--width") width = parseInt(argv[++i], 10);
    else if (a === "--height") height = parseInt(argv[++i], 10);
    else positional.push(a);
  }
  return { positional, width, height };
}

function startStaticServer(rootDir) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, "http://localhost");
      let rel = decodeURIComponent(url.pathname);
      if (rel === "/" || rel === "") rel = "/scene.html";
      const filePath = path.join(rootDir, rel);
      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.statusCode = 404;
          res.end(`not found: ${rel}`);
          return;
        }
        const ext = path.extname(filePath).toLowerCase();
        const mime = {
          ".html": "text/html",
          ".js": "application/javascript",
          ".glb": "model/gltf-binary",
        }[ext] || "application/octet-stream";
        res.setHeader("Content-Type", mime);
        res.end(data);
      });
    });
    server.listen(0, () => resolve(server));
  });
}

async function main() {
  const { positional, width, height } = parseArgs(process.argv.slice(2));
  const [outRel] = positional;
  if (!outRel) {
    console.error("usage: node render.js <out.png> [--width N] [--height N]");
    process.exit(1);
  }
  const outAbs = path.isAbsolute(outRel) ? outRel : path.resolve(outRel);

  const server = await startStaticServer(__dirname);
  const port = server.address().port;
  console.log(`server up on :${port}`);

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: 1 });

    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      const t = msg.type();
      if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
    });

    const url = `http://localhost:${port}/scene.html`;
    console.log(`navigating: ${url}`);
    await page.goto(url, { waitUntil: "networkidle0", timeout: 30000 });

    // GLTFLoader.load is async; wait until at least one mesh is in the
    // scene so we know rendering has happened with content.
    await page.waitForFunction(() => {
      // Sample the canvas — non-white pixel means render happened.
      const canvas = document.querySelector("#viewport");
      if (!canvas) return false;
      const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
      if (!gl) return false;
      const pixels = new Uint8Array(4);
      gl.readPixels(canvas.width / 2, canvas.height / 2, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
      // White is (255,255,255); look for any deviation.
      return pixels[0] !== 255 || pixels[1] !== 255 || pixels[2] !== 255;
    }, { timeout: 15000 });

    // Give the rasterizer one more tick.
    await new Promise((r) => setTimeout(r, 200));

    const buf = await page.screenshot({ type: "png", omitBackground: false });
    fs.writeFileSync(outAbs, buf);
    console.log(`wrote ${outAbs} (${buf.length} bytes)`);
  } finally {
    if (browser) await browser.close();
    await new Promise((r) => server.close(r));
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
