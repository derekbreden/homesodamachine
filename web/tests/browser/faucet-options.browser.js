// Actual production viewer modules with small deterministic mesh payloads.
// The fixtures separate UI/material/navigation behavior from CAD build time.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { start } from "../../server.js";
import { FAUCET_STYLES } from "../../contracts/faucet-options.js";

const [sculpted, industrial] = FAUCET_STYLES;
const machine = "manifold-layout/enclosure-assembly.step";
const files = [...new Set([machine, ...FAUCET_STYLES.flatMap((s) => [s.assembly, ...Object.values(s.parts)])])];
const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
let server, browser, baseUrl;

function payload(file) {
  const names = file === machine ? ["display-cover"] : file.includes("faucet-layout/")
    ? ["shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate", "westbrass", "above_counter_gasket", "faucet_display_screen"]
    : ["part"];
  const chunks = [], meshes = [];
  let offset = 0;
  function append(array) {
    const range = [offset, array.length];
    const buffer = Buffer.from(array.buffer);
    chunks.push(buffer); offset += buffer.length;
    return range;
  }
  for (const [i, name] of names.entries()) {
    const half = file === industrial.assembly || file === industrial.parts.shell_base ? 7 : 4;
    const positions = [-1,-1,-1, 1,-1,-1, 1,1,-1, -1,1,-1, -1,-1,1, 1,-1,1, 1,1,1, -1,1,1]
      .map((n, j) => n * half + (j % 3 === 0 ? i * 25 : 0));
    meshes.push({
      name, color: [0.0331047666, 0.0331047666, 0.0363064840],
      pos: append(new Float32Array(positions)),
      nrm: append(new Float32Array(24).fill(0.57735)),
      idx: append(new Uint32Array([0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,1,2,6,1,6,5,2,3,7,2,7,6,3,0,4,3,4,7])),
      fac: append(new Uint32Array([0,1,2,3,4,5,6,7,8,9,10,11])),
    });
  }
  let header = Buffer.from(JSON.stringify({ v: 3, meshes, src: file }));
  header = Buffer.concat([header, Buffer.alloc((4 - header.length % 4) % 4, 32)]);
  const length = Buffer.alloc(4); length.writeUInt32LE(header.length);
  return Buffer.concat([length, header, ...chunks]);
}

before(async () => {
  const puppeteer = require(require.resolve("puppeteer", { paths: [path.join(root, "tools/render/node_modules")] }));
  browser = await puppeteer.launch({ headless: true });
  ({ server } = await start({ dev: false, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  await browser?.close();
  server?.closeAllConnections?.();
  if (server) await new Promise((resolve) => server.close(resolve));
});

async function openPage(file = sculpted.assembly, xrayPreference = "0") {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  await page.evaluateOnNewDocument((preference) => {
    if (preference === null) localStorage.removeItem("step-xray");
    else localStorage.setItem("step-xray", preference);
  }, xrayPreference);
  await page.setRequestInterception(true);
  const failures = new Set();
  page.on("request", (request) => {
    const url = new URL(request.url());
    const json = (body) => request.respond({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    if (url.pathname === "/api/steps") return json(files);
    if (url.pathname === "/api/objects") return json({ objects: {} });
    if (["/api/dxf", "/api/glbs", "/api/pcb", "/api/mermaid", "/api/documents"].includes(url.pathname)) return json([]);
    if (url.pathname.startsWith("/meshes/") || url.pathname.startsWith("/steps/")) {
      const target = decodeURIComponent(url.pathname.replace(/^\/(meshes|steps)\//, "")).replace(/\.mesh$/, "");
      return request.respond(failures.has(target)
        ? { status: 503, body: "unavailable" }
        : { status: 200, contentType: "application/octet-stream", body: payload(target) });
    }
    return request.continue();
  });
  await page.goto(`${baseUrl}/3d#step:${encodeURIComponent(file)}`, { waitUntil: "domcontentloaded" });
  await mounted(page, file);
  return { page, failures };
}
const mounted = (page, file) => page.waitForFunction((f) => window.__hsm?.mountedStepFile === f, { timeout: 30000 }, file);
const choose = (page, name, value) => page.click(`.faucet-options input[name="faucet-${name}"][value="${value}"] + span`);
const materials = (page) => page.evaluate(() => Object.fromEntries(window.__hsm.currentGroup.children
  .filter((m) => m.userData.side === "front")
  .map((m) => [m.name, (m.userData.baseMaterial || m.material).color.toArray()])));
const pose = (page) => page.evaluate(() => ({
  p: window.__hsm.camera.position.toArray(), u: window.__hsm.camera.up.toArray(), t: window.__hsm.controls.target.toArray(),
}));
function samePose(actual, expected) {
  for (const axis of ["p", "u", "t"]) actual[axis].forEach((n, i) => assert.ok(Math.abs(n - expected[axis][i]) < 1e-8, `${axis}[${i}] moved`));
}

test("style swaps actual geometry in place; finish changes only printed faucet bodies", async () => {
  const { page } = await openPage();
  try {
    const initial = await materials(page);
    await page.evaluate(() => {
      const h = window.__hsm;
      h.camera.position.set(42, -127, 93); h.camera.up.set(.1, .15, .98).normalize();
      h.controls.target.set(2, 4, 6); h.controls.update();
    });
    const before = await pose(page);
    await choose(page, "finish", "white");
    const white = await materials(page);
    for (const name of ["shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate"]) assert.ok(white[name][0] > .8, name);
    for (const name of ["westbrass", "above_counter_gasket", "faucet_display_screen"]) assert.deepEqual(white[name], initial[name], name);
    samePose(await pose(page), before);
    await choose(page, "style", "industrial");
    await mounted(page, industrial.assembly);
    await page.waitForFunction(() => !document.querySelector('[name="faucet-style"]').disabled);
    samePose(await pose(page), before);
    assert.deepEqual(await materials(page), white);
    assert.equal(await page.evaluate(() => window.__hsm.currentGroup.children[0].geometry.boundingBox.max.x), 7);
    assert.ok(decodeURIComponent(await page.evaluate(() => location.hash)).includes(industrial.assembly));
    assert.equal(await page.$eval('[data-faucet]', (e) => e.dataset.file), industrial.assembly);
    await page.evaluate(async () => (await import("/js/viewer/xray.js")).setXrayEnabled(true));
    await choose(page, "finish", "black");
    await page.evaluate(async () => (await import("/js/viewer/xray.js")).setXrayEnabled(false));
    assert.deepEqual(await materials(page), initial);
    await choose(page, "style", "sculpted");
    await mounted(page, sculpted.assembly);
    samePose(await pose(page), before);
    assert.equal(await page.evaluate(() => window.__hsm.currentGroup.children[0].geometry.boundingBox.max.x), 4);
  } finally { await page.close(); }
});

test("Industrial component drilldown opens its actual part and carries the finish", async () => {
  const { page } = await openPage(industrial.assembly);
  try {
    await choose(page, "finish", "white");
    const point = await page.evaluate(async () => {
      const h = window.__hsm;
      (await import("/js/viewer/component-picker.js")).setComponentPickEnabled(true);
      h.camera.position.set(0, -80, 0); h.camera.up.set(0, 0, 1); h.controls.target.set(0, 0, 0);
      h.camera.lookAt(h.controls.target); h.controls.update(); h.camera.updateMatrixWorld(true); h.currentGroup.updateMatrixWorld(true);
      const r = h.renderer.domElement.getBoundingClientRect();
      return [r.left + r.width / 2, r.top + r.height / 2];
    });
    await page.mouse.click(...point);
    await page.waitForSelector(".component-open", { visible: true });
    assert.ok((await page.$eval(".component-open", (e) => e.title)).endsWith(industrial.parts.shell_base));
    await page.click(".component-open");
    await mounted(page, industrial.parts.shell_base);
    assert.ok((await materials(page)).part[0] > .8);
    assert.equal(await page.$eval('[name="faucet-style"]', (e) => e.closest("fieldset").hidden), true);
    await page.click(".cad-crumb-step");
    await mounted(page, industrial.assembly);
    assert.ok((await materials(page)).shell_base[0] > .8);
  } finally { await page.close(); }
});

test("failed style load leaves the mounted faucet, view, URL and selection intact", async () => {
  const { page, failures } = await openPage();
  try {
    failures.add(industrial.assembly);
    const before = await pose(page);
    await choose(page, "style", "industrial");
    await page.waitForFunction(() => document.querySelector(".faucet-options-status").textContent.includes("Couldn't load"));
    assert.equal(await page.evaluate(() => window.__hsm.mountedStepFile), sculpted.assembly);
    assert.equal(await page.$eval('[name="faucet-style"]:checked', (e) => e.value), "sculpted");
    samePose(await pose(page), before);
    assert.ok(!decodeURIComponent(await page.evaluate(() => location.hash)).includes(industrial.assembly));
  } finally { await page.close(); }
});

test("machine assembly has no faucet controls or recoloring", async () => {
  const { page } = await openPage(machine);
  try {
    assert.equal(await page.$eval(".faucet-options", (e) => e.hidden), true);
    const before = await materials(page);
    await page.evaluate(async () => (await import("/js/viewer/step.js")).setFaucetFinish("white"));
    assert.deepEqual(await materials(page), before);
  } finally { await page.close(); }
});

test("fresh faucet opens solid, explicit x-ray preference survives style changes, machine keeps its default", async () => {
  const { page } = await openPage(sculpted.assembly, null);
  try {
    const ghosted = () => page.evaluate(() => window.__hsm.currentGroup.children.find((m) => m.userData.side === "front").material.transparent);
    assert.equal(await ghosted(), false);
    assert.equal(await page.$eval(".xray-toggle", (e) => e.getAttribute("aria-pressed")), "false");
    await page.click(".xray-toggle");
    await choose(page, "style", "industrial");
    await mounted(page, industrial.assembly);
    assert.equal(await ghosted(), true);
    assert.equal(await page.evaluate(() => localStorage.getItem("step-xray")), "1");
    await page.evaluate(async (file) => {
      localStorage.removeItem("step-xray");
      await (await import("/js/viewer/step-nav.js")).jumpToStep(file);
    }, machine);
    assert.equal(await ghosted(), true);
  } finally { await page.close(); }
});

test("mobile choices stay clear of the view cube and close after choosing a finish", async () => {
  const { page } = await openPage();
  try {
    await page.setViewport({ width: 390, height: 844 });
    await page.waitForFunction(() => !document.querySelector(".faucet-options").open);
    const rects = await page.evaluate(() => ({
      panel: document.querySelector(".faucet-options").getBoundingClientRect().toJSON(),
      cube: document.querySelector(".cad-gizmo").getBoundingClientRect().toJSON(),
    }));
    assert.ok(rects.panel.right <= rects.cube.left);
    await page.click(".faucet-options > summary");
    await choose(page, "finish", "white");
    assert.equal(await page.$eval(".faucet-options", (e) => e.open), false);
    assert.match(await page.$eval(".faucet-options > summary", (e) => e.textContent), /Sculpted · White/);
    assert.ok((await materials(page)).shell_base[0] > .8);
  } finally { await page.close(); }
});
