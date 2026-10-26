import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
const materialUrl = "/3d#material:HSM-000009";
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
    assert.equal(href, materialUrl);
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

test("material result links open their pane in a new page; phone drawing and Escape preserve the model", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await page.goto(baseUrl + materialUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
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
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});
