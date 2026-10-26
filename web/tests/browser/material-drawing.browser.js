import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
const materialUrl = "/3d#material:HSM-000009";
const searchUrl = materialUrl + "?panel=materials";
const capFile = "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step";
let browser, server, baseUrl;
before(async () => {
  browser = await require("puppeteer").launch({ headless: true });
  ({ server } = await start({ dev: true, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  await browser?.close();
  server?.closeAllConnections?.();
  if (server) await new Promise(resolve => server.close(resolve));
});

async function materialReady(page, file = capFile) {
  await page.waitForFunction(wanted => window.__hsm?.mountedStepFile === wanted
    && window.__hsm.currentGroup, { timeout: 30_000 }, file);
}
async function drawingReady(page) {
  await page.waitForSelector(".material-drawing-view:not([hidden])");
  const frame = await (await page.$(".material-drawing-view")).contentFrame();
  await frame.waitForFunction(() => document.querySelector("#pdf-canvas")?.dataset.page === "1"
    && document.querySelector(".pdf-viewport")?.getAttribute("aria-busy") === "false",
  { timeout: 30_000 });
  return frame;
}
async function cameraPose(page) {
  return page.evaluate(() => {
    const h = window.__hsm;
    return { position: h.camera.position.toArray(), up: h.camera.up.toArray(),
      target: h.controls.target.toArray() };
  });
}
async function assertPane(page, open) {
  assert.equal(!!await page.$(".cad-workspace.materials-open"), open);
  assert.equal(await page.$eval(".materials-toggle", button => button.getAttribute("aria-expanded")), String(open));
  assert.equal(await page.$eval(".material-panel", panel => getComputedStyle(panel).display !== "none"), open);
}

test("3D thumbnails and model navigation start closed after an open materials pane", async () => {
  const page = await browser.newPage();
  const card = '.card[data-material="HSM-000180"] .assembly-model-link';
  const file = "printed-parts/calibration/soda-studies/the-pour.step";
  try {
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(baseUrl + "/3d", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(card);
    assert.equal(await page.$eval(card, link => link.getAttribute("href")), "/3d#material:HSM-000180");
    await page.click(card);
    await materialReady(page, file);
    await assertPane(page, false);
    await page.click(".materials-toggle");
    await assertPane(page, true);
    const canvas = await page.$("canvas.cad-viewport");
    await page.evaluate(() => { location.hash = "material:HSM-000009"; });
    await materialReady(page);
    await assertPane(page, false);
    assert.equal(await canvas.evaluate(node => node === document.querySelector("canvas.cad-viewport")), true);
    await page.goBack();
    await materialReady(page, file);
    await assertPane(page, false);
    await page.goForward();
    await materialReady(page);
    await assertPane(page, false);
    await page.click(".materials-toggle");
    await page.type(".material-panel .material-search input", "HSM-000009");
    await page.click(".material-panel .material-search-results a");
    await page.waitForFunction(() => location.hash.endsWith("?panel=materials"));
    await assertPane(page, true); // The same model can be entered as a search result.
    await page.click(".cv-close");
    await page.waitForSelector(".cad-workspace", { hidden: true });
    await page.click(card);
    await materialReady(page, file);
    await assertPane(page, false);
  } finally { await page.close(); }
});

test("material search opens the pane and features a working drawing beside the preserved 3D view", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(baseUrl + "/3d", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".material-search input");
    await page.type(".material-search input", "HSM-000009");
    await page.waitForSelector(".material-search-results a");
    const href = await page.$eval(".material-search-results a", link => link.getAttribute("href"));
    assert.equal(href, searchUrl);
    const linked = await browser.newPage();
    try {
      await linked.setViewport({ width: 1440, height: 1000 });
      await linked.goto(baseUrl + href, { waitUntil: "domcontentloaded" });
      await materialReady(linked);
      await assertPane(linked, true);
    } finally { await linked.close(); }
    await page.click(".material-search-results a");
    await materialReady(page);
    assert.ok(await page.$(".cad-workspace.materials-open"));
    assert.equal(await page.$eval(".materials-toggle", button => button.getAttribute("aria-expanded")), "true");
    const featured = await page.$eval(".material-drawing-feature", link => ({
      bottom: link.getBoundingClientRect().bottom,
      tabs: document.querySelector(".material-tabs").getBoundingClientRect().top,
    }));
    assert.ok(featured.bottom < featured.tabs, "drawing should be above the relationship tabs");
    const pose = await cameraPose(page);
    const modelCanvas = await page.$("canvas.cad-viewport");
    await page.click(".material-drawing-feature");
    const frame = await drawingReady(page);
    assert.equal(await page.$eval(".material-view-switch button[aria-pressed=true]", button => button.textContent), "Drawing");
    assert.match(await frame.$eval("#pdf-text", text => text.textContent), /END-CAP-01/);
    assert.equal(await frame.$("#site-nav"), null, "embedded reading should keep the parent viewer's navigation");
    assert.equal(await frame.$eval(".pdf-heading a", link => link.textContent), "Open full drawing");
    const fit = await frame.$eval(".pdf-paper", paper => ({
      width: paper.clientWidth, height: paper.clientHeight,
      viewportWidth: paper.parentElement.clientWidth, viewportHeight: paper.parentElement.clientHeight,
      scrollWidth: paper.parentElement.scrollWidth,
    }));
    assert.ok(fit.width <= fit.viewportWidth && fit.height <= fit.viewportHeight, "the initial drawing view should fit the entire sheet");
    assert.ok(fit.scrollWidth <= fit.viewportWidth, "fit page should not introduce horizontal scrolling");
    assert.ok(await page.$(".cad-workspace.materials-open"), "desktop pane should remain open beside the drawing");
    await page.click(".material-view-switch button:first-child");
    assert.deepEqual(await cameraPose(page), pose);
    assert.equal(await modelCanvas.evaluate(canvas => canvas === document.querySelector("canvas.cad-viewport")), true);
    assert.equal(await page.$eval(".material-drawing-view", iframe => iframe.hidden), true);
    await page.click(".material-view-switch button:last-child");
    await drawingReady(page);

    // Selecting another search result while reading must discard the old part's
    // drawing and return to the newly selected material's model.
    await page.type(".material-panel .material-search input", "HSM-000008");
    await page.click(".material-panel .material-search-results a");
    await materialReady(page, "cut-parts/carbonation/carbonator-tube/carbonator-tube.step");
    assert.equal(await page.$(".material-drawing-view"), null);
    assert.equal(await page.$eval(".material-view-switch", control => control.hidden), true);
    await page.goBack();
    await materialReady(page);
    assert.ok(await page.$(".cad-workspace.materials-open .material-drawing-feature"));
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("phone searches start closed; manually opened materials and drawing preserve the model", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await page.goto(baseUrl + "/3d", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".material-search input");
    await page.type(".material-search input", "HSM-000009");
    await page.click(".material-search-results a");
    await materialReady(page);
    await assertPane(page, false);
    await page.click(".materials-toggle");
    assert.ok(await page.$(".cad-workspace.materials-open .material-drawing-feature"));
    const pose = await cameraPose(page);
    await page.click(".material-drawing-feature");
    const frame = await drawingReady(page);
    assert.equal(await page.$(".cad-workspace.materials-open"), null);
    assert.equal(await page.$eval(".materials-toggle", button => button.getAttribute("aria-expanded")), "false");
    assert.equal(await frame.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await frame.click("#pdf-zoom-in");
    await frame.waitForFunction(() => document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false");
    await page.keyboard.press("Escape");
    await page.waitForSelector(".cad-wrapper:not(.drawing-open)");
    assert.equal(await page.$eval(".material-view-switch button[aria-pressed=true]", button => button.textContent), "3D");
    assert.deepEqual(await cameraPose(page), pose);
    await page.click(".materials-toggle");
    assert.ok(await page.$(".cad-workspace.materials-open .material-drawing-feature"));
    await page.type(".material-panel .material-search input", "HSM-000008");
    await page.click(".material-panel .material-search-results a");
    await materialReady(page, "cut-parts/carbonation/carbonator-tube/carbonator-tube.step");
    await assertPane(page, false);
    await page.goBack();
    await materialReady(page);
    await assertPane(page, false);
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("direct links and responsive layout apply the pane rules without storing a preference", async () => {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(baseUrl + materialUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, false);
    await page.goto(baseUrl + searchUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, true);
    await page.setViewport({ width: 390, height: 844 });
    await page.waitForFunction(() => !document.querySelector(".cad-workspace.materials-open"));
    await assertPane(page, false);
    await page.click(".materials-toggle");
    await assertPane(page, true);
    await page.reload({ waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, false);
    await page.goto(baseUrl + materialUrl + "?tab=bom", { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, false);
    await page.setViewport({ width: 1440, height: 1000 });
    await page.reload({ waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, true);
  } finally { await page.close(); }
});
