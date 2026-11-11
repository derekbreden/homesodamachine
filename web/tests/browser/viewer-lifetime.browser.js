// Run on demand: node --test tests/browser/viewer-lifetime.browser.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
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

function sharedPayload() {
  const object = payload();
  const sha = createHash("sha256").update(object).digest("hex");
  let header = Buffer.from(JSON.stringify({ v: 4, src: "fixture", meshes: [
    { name: mesh.name, asset: sha, entries: [{ name: mesh.name, color: mesh.color }] },
  ] }));
  header = Buffer.concat([header, Buffer.alloc((4 - header.length % 4) % 4, 32)]);
  const length = Buffer.alloc(4); length.writeUInt32LE(header.length);
  return { object, sha, scene: Buffer.concat([length, header]) };
}

test("live STEP reloads retain one renderer and release departed x-ray geometry", { timeout: 90000 }, async t => {
  const hardwareDir = await fs.mkdtemp(path.join(os.tmpdir(), "hsm-viewer-lifetime-"));
  let browser, server;
  try {
    await fs.mkdir(path.dirname(path.join(hardwareDir, file)), { recursive: true });
    await fs.writeFile(path.join(hardwareDir, file), "fixture");
    await fs.writeFile(path.join(hardwareDir, `${file}.mesh`), payload());
    ({ server } = await start({ port: 0, hardwareDir }));
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

for (const shared of [false, true]) test(`Find survives a ${shared ? "shared" : "packed"} model refresh, keeps the camera, and respects Clear`, { timeout: 60000 }, async () => {
  const hardwareDir = await fs.mkdtemp(path.join(os.tmpdir(), "hsm-find-refresh-"));
  let browser, server;
  try {
    await fs.mkdir(path.dirname(path.join(hardwareDir, file)), { recursive: true });
    await fs.writeFile(path.join(hardwareDir, file), "fixture");
    const current = shared ? sharedPayload() : { scene: payload() };
    await fs.writeFile(path.join(hardwareDir, `${file}.mesh`), current.scene);
    ({ server } = await start({ port: 0, hardwareDir }));
    browser = await launchBrowser();
    const page = await browser.newPage();
    if (shared) {
      await page.setRequestInterception(true);
      page.on("request", request => {
        if (new URL(request.url()).pathname === `/scene-meshes/${current.sha}`)
          return request.respond({ status: 200, contentType: "application/octet-stream", body: current.object });
        return request.continue();
      });
    }
    await page.goto(`http://127.0.0.1:${server.address().port}/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent("solid: fixture-body")}`, { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => window.__hsm?.scene.getObjectByName("pick-find")?.children.length > 0);
    await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 500)));
    const result = await page.evaluate(async file => {
      const h = window.__hsm;
      const { state } = await import("/js/viewer/state.js");
      h.camera.position.set(30, -40, 50); h.controls.target.set(0, 0, 0); h.controls.update();
      const before = [...h.camera.position.toArray(), ...h.controls.target.toArray()];
      let mounted = 0;
      const completed = event => { if (event.detail?.file === file && event.detail.complete !== false) mounted++; };
      window.addEventListener("hsm:step-mounted", completed);
      state.stepEtags.clear();
      await h.loadStepFile(file, { preserveCamera: true });
      window.removeEventListener("hsm:step-mounted", completed);
      return { highlighted: h.scene.getObjectByName("pick-find").children.length,
        mounted,
        before, after: [...h.camera.position.toArray(), ...h.controls.target.toArray()] };
    }, file);
    assert.ok(result.mounted > 0, "the fixture did not reload");
    assert.ok(result.highlighted > 0, "the selected part lost its highlight");
    assert.deepEqual(result.after, result.before, "refresh refocused the camera");
    await page.$eval('.pick-find-toggle', button => button.click());
    const cleared = await page.evaluate(async file => {
      [...document.querySelectorAll(".pick-find-buttons button")].find(button => button.textContent === "Clear").click();
      const { state } = await import("/js/viewer/state.js");
      state.stepEtags.clear();
      await window.__hsm.loadStepFile(file, { preserveCamera: true });
      return window.__hsm.scene.getObjectByName("pick-find").children.length;
    }, file);
    assert.equal(cleared, 0, "refresh revived a cleared highlight");
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
    await fs.rm(hardwareDir, { recursive: true, force: true });
  }
});

test("new shared parts extend clipping bounds while existing GPU geometry stays mounted", { timeout: 60000 }, async () => {
  const hardwareDir = await fs.mkdtemp(path.join(os.tmpdir(), "hsm-added-part-"));
  let browser, server;
  try {
    const current = sharedPayload();
    const destination = path.join(hardwareDir, `${file}.mesh`);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(path.join(hardwareDir, file), "fixture");
    await fs.writeFile(destination, current.scene);
    ({ server } = await start({ port: 0, hardwareDir }));
    browser = await launchBrowser();
    const page = await browser.newPage();
    await page.setRequestInterception(true);
    page.on("request", request => {
      if (new URL(request.url()).pathname === `/scene-meshes/${current.sha}`)
        return request.respond({ status: 200, contentType: "application/octet-stream", body: current.object });
      return request.continue();
    });
    await page.goto(`http://127.0.0.1:${server.address().port}/3d#step:${encodeURIComponent(file)}`, { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => window.__hsm?.currentGroup?.userData.sceneLoading === false);
    const before = await page.evaluate(async () => {
      const h = window.__hsm;
      h.camera.position.set(30, -40, 50); h.controls.target.set(0, 0, 0); h.controls.update();
      const { updateDepthRange } = await import("/js/viewer/scene.js");
      updateDepthRange();
      return { group: h.currentGroup.uuid, geometry: h.currentGroup.children[0].geometry.uuid, far: h.camera.far };
    });
    const head = JSON.parse(current.scene.subarray(4, 4 + current.scene.readUInt32LE(0)));
    head.src = "expanded";
    head.meshes.push({ ...head.meshes[0], name: "fixture-added",
      entries: [{ name: "fixture-added", color: mesh.color }],
      transform: [[1,0,0,200],[0,1,0,0],[0,0,1,0]],
    });
    let header = Buffer.from(JSON.stringify(head));
    header = Buffer.concat([header, Buffer.alloc((4 - header.length % 4) % 4, 32)]);
    const size = Buffer.alloc(4); size.writeUInt32LE(header.length);
    await fs.writeFile(destination, Buffer.concat([size, header]));
    const after = await page.evaluate(async file => {
      const h = window.__hsm;
      const { state } = await import("/js/viewer/state.js");
      state.stepEtags.clear();
      await h.loadStepFile(file, { preserveCamera: true });
      const { updateDepthRange } = await import("/js/viewer/scene.js");
      updateDepthRange();
      const added = h.currentGroup.getObjectByName("fixture-added");
      const distance = added.getWorldPosition(new h.THREE.Vector3()).distanceTo(h.camera.position);
      return { group: h.currentGroup.uuid, geometry: h.currentGroup.children[0].geometry.uuid,
        far: h.camera.far, distance, added: !!added };
    }, file);
    assert.equal(after.group, before.group);
    assert.equal(after.geometry, before.geometry);
    assert.equal(after.added, true);
    assert.ok(after.far > after.distance, "the new part lies beyond the cached far plane");
    assert.ok(after.far > before.far, "camera depth retained the old model bounds");
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
    await fs.rm(hardwareDir, { recursive: true, force: true });
  }
});
