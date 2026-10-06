// Compare the pixels drawn by the production thumbnail and detail renderers.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { start } from "../../server.js";
import { PETGF_BLACK } from "../../contracts/material-finishes.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const require = createRequire(import.meta.url);
const sharp = require(require.resolve("sharp", { paths: [path.join(root, "tools/render/node_modules")] }));
const file = "manifold-layout/enclosure-assembly.step";

function payload(colors) {
  const chunks = [], meshes = [];
  let offset = 0;
  const append = (array) => {
    const range = [offset, array.length];
    const bytes = Buffer.from(array.buffer);
    chunks.push(bytes); offset += bytes.length;
    return range;
  };
  const faces = [
    { normal: [1,0,0], points: [[1,-1,-1],[1,1,-1],[1,1,1],[1,-1,1]] },
    { normal: [-1,0,0], points: [[-1,1,-1],[-1,-1,-1],[-1,-1,1],[-1,1,1]] },
    { normal: [0,1,0], points: [[1,1,-1],[-1,1,-1],[-1,1,1],[1,1,1]] },
    { normal: [0,-1,0], points: [[-1,-1,-1],[1,-1,-1],[1,-1,1],[-1,-1,1]] },
    { normal: [0,0,1], points: [[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]] },
    { normal: [0,0,-1], points: [[-1,1,-1],[1,1,-1],[1,-1,-1],[-1,-1,-1]] },
  ];
  for (const [i, color] of colors.entries()) {
    const positions = [], normals = [], indices = [], ranges = [];
    for (const [f, face] of faces.entries()) {
      positions.push(...face.points.flatMap(([x,y,z]) => [x + (i * 2 - 1) * 1.6, y, z]));
      normals.push(...Array.from({ length: 4 }, () => face.normal).flat());
      indices.push(...[0,1,2,0,2,3].map((n) => n + f * 4));
      ranges.push(f * 2, f * 2 + 1);
    }
    meshes.push({ name: `fixture-${i}`, color,
      pos: append(new Float32Array(positions)), nrm: append(new Float32Array(normals)),
      idx: append(new Uint32Array(indices)), fac: append(new Uint32Array(ranges)),
    });
  }
  let header = Buffer.from(JSON.stringify({ v: 3, meshes }));
  header = Buffer.concat([header, Buffer.alloc((4 - header.length % 4) % 4, 32)]);
  const length = Buffer.alloc(4); length.writeUInt32LE(header.length);
  return Buffer.concat([length, header, ...chunks]);
}

test("thumbnail and detail pixels agree for PET-GF and reflective metal", { timeout: 90000 }, async () => {
  const hardwareDir = await fs.mkdtemp(path.join(os.tmpdir(), "hsm-thumbnail-lighting-"));
  let browser, server;
  try {
    const finishes = JSON.parse(await fs.readFile(path.join(root, "web/public/finishes.json"), "utf8")).finishes;
    const metal = finishes.find((f) => f.metalness >= 0.9);
    assert.ok(metal, "the fixture includes a reflective production finish");
    await fs.mkdir(path.dirname(path.join(hardwareDir, file)), { recursive: true });
    await fs.writeFile(path.join(hardwareDir, file), "fixture");
    await fs.writeFile(path.join(hardwareDir, `${file}.mesh`), payload([PETGF_BLACK.rgb, metal.rgb]));
    ({ server } = await start({ dev: false, port: 0, hardwareDir }));
    browser = await launchBrowser();
    const page = await browser.newPage();
    await page.setViewport({ width: 800, height: 800 });
    await page.evaluateOnNewDocument(() => localStorage.setItem("step-xray", "0"));
    await page.goto(`http://127.0.0.1:${server.address().port}/3d?file=${encodeURIComponent(file)}`, { waitUntil: "domcontentloaded" });
    await page.waitForFunction((f) => window.__hsm?.mountedStepFile === f, { timeout: 30000 }, file);
    const images = await page.evaluate(async (f) => {
      const { renderThumbnail } = await import("/js/viewer/step.js");
      const { resetCamera, fitGroundShadow } = await import("/js/viewer/scene.js");
      const thumbnail = await renderThumbnail(f, 400);
      const h = window.__hsm;
      h.renderer.setPixelRatio(1);
      h.renderer.setSize(400, 400, false);
      h.camera.aspect = 1;
      h.camera.updateProjectionMatrix();
      resetCamera(h.currentGroup);
      fitGroundShadow(null);
      h.renderer.render(h.scene, h.camera);
      return { thumbnail, detail: h.renderer.domElement.toDataURL("image/png") };
    }, file);
    const decode = async (url) => sharp(Buffer.from(url.split(",")[1], "base64")).removeAlpha().raw().toBuffer();
    const thumbnail = await decode(images.thumbnail), detail = await decode(images.detail);
    let difference = 0, samples = 0;
    for (let i = 0; i < detail.length; i += 3) {
      if (detail[i] === 16 && detail[i+1] === 49 && detail[i+2] === 156) continue;
      for (let c = 0; c < 3; c++) difference += Math.abs(thumbnail[i+c] - detail[i+c]);
      samples += 3;
    }
    assert.ok(samples > 3000, "both solid surfaces are visible");
    assert.ok(difference / samples < 1, `thumbnail differs by ${(difference / samples).toFixed(2)} RGB levels per surface channel`);
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
    await fs.rm(hardwareDir, { recursive: true, force: true });
  }
});
