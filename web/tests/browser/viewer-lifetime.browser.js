// Run on demand: node --test tests/browser/viewer-lifetime.browser.js
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const file = "manifold-layout/enclosure-assembly.step";
const mesh = {
  name: "fixture-body", color: [0.2, 0.3, 0.4],
  attributes: {
    position: { array: [-1,-1,-1, 1,-1,-1, 1,1,-1, -1,1,-1, -1,-1,1, 1,-1,1, 1,1,1, -1,1,1] },
    normal: { array: Array(24).fill(0.57735) },
  },
  index: { array: [0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,1,2,6,1,6,5,2,3,7,2,7,6,3,0,4,3,4,7] },
  brep_faces: Array.from({ length: 6 }, (_, i) => ({ first: i * 2, last: i * 2 + 1 })),
};

function payload() {
  const chunks = [];
  let offset = 0;
  const append = array => {
    const range = [offset, array.length];
    const bytes = Buffer.from(array.buffer);
    chunks.push(bytes); offset += bytes.length;
    return range;
  };
  const entry = {
    name: mesh.name, color: mesh.color,
    pos: append(new Float32Array(mesh.attributes.position.array)),
    nrm: append(new Float32Array(mesh.attributes.normal.array)),
    idx: append(new Uint32Array(mesh.index.array)),
    fac: append(new Uint32Array(mesh.brep_faces.flatMap(f => [f.first, f.last]))),
  };
  let header = Buffer.from(JSON.stringify({ v: 3, meshes: [entry] }));
  header = Buffer.concat([header, Buffer.alloc((4 - header.length % 4) % 4, 32)]);
  const length = Buffer.alloc(4); length.writeUInt32LE(header.length);
  return Buffer.concat([length, header, ...chunks]);
}

test("live STEP reloads retain one renderer and release departed x-ray geometry", { timeout: 90000 }, async t => {
  const hardwareDir = await fs.mkdtemp(path.join(os.tmpdir(), "hsm-viewer-lifetime-"));
  let browser, server;
  try {
    await fs.mkdir(path.dirname(path.join(hardwareDir, file)), { recursive: true });
    await fs.writeFile(path.join(hardwareDir, file), "fixture");
    await fs.writeFile(path.join(hardwareDir, `${file}.mesh`), payload());
    ({ server } = await start({ dev: false, port: 0, hardwareDir }));
    browser = await launchBrowser();
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.evaluateOnNewDocument(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      const canvases = new WeakSet();
      window.__webglContexts = 0;
      HTMLCanvasElement.prototype.getContext = function(type, ...args) {
        const context = original.call(this, type, ...args);
        if (context && type.startsWith("webgl") && !canvases.has(this)) {
          canvases.add(this); window.__webglContexts++;
        }
        return context;
      };
    });
    await page.setRequestInterception(true);
    const stepSource = await fs.readFile(fileURLToPath(new URL("../../public/js/viewer/step.js", import.meta.url)), "utf8");
    page.on("request", request => {
      const url = new URL(request.url());
      if (url.pathname === "/js/viewer/step.js" && url.searchParams.get("v") === "lifetime-compat") {
        return request.respond({ status: 200, contentType: "text/javascript",
          body: stepSource.replace('from "./xray.js"', 'from "/test-legacy-xray.js"') });
      }
      if (url.pathname === "/test-legacy-xray.js") {
        return request.respond({ status: 200, contentType: "text/javascript",
          body: 'export { applyXray, syncEdgeResolution, setMeshMaterial } from "/js/viewer/xray.js";' });
      }
      if (request.url().includes("occt-import-js.js")) {
        return request.respond({ status: 200, contentType: "text/javascript", body:
          `window.occtimportjs = async () => { window.__occtStarts = (window.__occtStarts || 0) + 1; return { ReadStepFile: () => (${JSON.stringify({ meshes: [mesh] })}) }; };` });
      }
      return request.continue();
    });
    await page.goto(`http://127.0.0.1:${server.address().port}/3d?file=${encodeURIComponent(file)}`, { waitUntil: "domcontentloaded" });
    await page.waitForFunction(f => window.__hsm?.mountedStepFile === f, { timeout: 30000 }, file);
    const readback = await page.evaluate(async (f, sample) => {
      const h = window.__hsm;
      const { state } = await import("/js/viewer/state.js");
      const { getLoader } = await import("/js/viewer/loaders.js");
      const { getThumbnailRuntime } = await import("/js/viewer/step-runtime.js");
      const { setXrayEnabled } = await import("/js/viewer/xray.js");
      getThumbnailRuntime();
      const contexts = window.__webglContexts;
      h.camera.position.set(30, -40, 50);
      h.controls.target.set(0, 0, 0); h.controls.update();
      const pose = h.camera.position.toArray();
      const geometries = [], thumbnails = [];
      for (let i = 1; i <= 6; i++) {
        state.codeVersion = `lifetime-${i}`;
        state.stepEtags.clear();
        const load = await getLoader("step");
        setXrayEnabled(true, { persist: false });
        await load(f, { preserveCamera: true });
        h.renderer.render(h.scene, h.camera);
        // Edges detached by toggling off must still be released on replacement.
        setXrayEnabled(false, { persist: false });
        await load(f, { preserveCamera: true });
        h.renderer.render(h.scene, h.camera);
        geometries.push(h.renderer.info.memory.geometries);
        const mod = await import(`/js/viewer/step.js?v=lifetime-${i}`);
        thumbnails.push(mod.renderMeshes(sample, 64).startsWith("data:image/png"));
      }
      return { contextsBefore: contexts, contextsAfter: window.__webglContexts,
        geometries, thumbnails, parserStarts: window.__occtStarts || 0,
        poseBefore: pose, poseAfter: h.camera.position.toArray() };
    }, file, { meshes: [mesh] });
    assert.equal(readback.contextsAfter, readback.contextsBefore, "hot loaders accumulated WebGL contexts");
    assert.equal(new Set(readback.geometries).size, 1, "detached x-ray geometry accumulated across reloads");
    assert.equal(readback.parserStarts, 0, "payload-backed deep links started the STEP parser");
    assert.ok(readback.thumbnails.every(Boolean), "a hot loader failed to draw its thumbnail");
    assert.deepEqual(readback.poseAfter, readback.poseBefore, "reload moved the camera");

    const fallback = "manifold-layout/fallback.step";
    await fs.writeFile(path.join(hardwareDir, fallback), "fixture");
    const parsed = await page.evaluate(async f => {
      const { getOcct } = await import("/js/viewer/step-runtime.js");
      const [first, second] = await Promise.all([getOcct(), getOcct()]);
      const { loadStepFile } = await import("/js/viewer/step.js?v=lifetime-fallback");
      await loadStepFile(f, { preserveCamera: true });
      return { shared: first === second, starts: window.__occtStarts, mounted: window.__hsm.mountedStepFile };
    }, fallback);
    assert.equal(parsed.shared, true);
    assert.equal(parsed.starts, 1, "fallback loads created multiple STEP parser instances");
    assert.equal(parsed.mounted, fallback);
    // An open tab retains its shared modules when a fresh leaf arrives on deploy.
    const compatible = await page.evaluate(async f => {
      const { loadStepFile } = await import("/js/viewer/step.js?v=lifetime-compat");
      await loadStepFile(f, { preserveCamera: true });
      return window.__hsm.mountedStepFile;
    }, file);
    assert.equal(compatible, file, "the new loader rejected an older tab's x-ray API");
    assert.deepEqual(errors, []);
    t.diagnostic(JSON.stringify({ ...readback, fallbackParserStarts: parsed.starts }));
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
    await fs.rm(hardwareDir, { recursive: true, force: true });
  }
});
