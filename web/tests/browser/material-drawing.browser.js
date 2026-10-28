import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
const materialUrl = "/3d#material:HSM-000009";
const searchUrl = materialUrl + "?panel=materials";
const capFile = "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step";
const reviewDir = path.resolve(".cache/material-workspace");
let browser, server, baseUrl;
before(async () => {
  browser = await require("puppeteer").launch({ headless: true });
  ({ server } = await start({ dev: true, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
  fs.mkdirSync(reviewDir, { recursive: true });
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

test("one workspace toolbar contains navigation, view mode and document controls on desktop and phone", async () => {
  const page = await browser.newPage();
  const parentFile = "printed-parts/calibration/soda-studies/the-pour.step";
  try {
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(baseUrl + "/3d#material:HSM-000180", { waitUntil: "domcontentloaded" });
    await materialReady(page, parentFile);
    await page.click(".materials-toggle");
    await page.type(".material-panel .material-search input", "HSM-000009");
    await page.click(".material-panel .material-search-results a");
    await materialReady(page);
    const layout = await page.evaluate(() => {
      const crumb = document.querySelector(".cad-crumb.show").getBoundingClientRect();
      const switcher = document.querySelector(".material-view-switch").getBoundingClientRect();
      const header = document.querySelector(".cad-workspace-header").getBoundingClientRect();
      return { height: header.height, sameRow: Math.abs((crumb.top + crumb.bottom) - (switcher.top + switcher.bottom)) < 2,
        titleHidden: getComputedStyle(document.querySelector(".cv-filename")).display === "none" };
    });
    assert.ok(layout.height <= 80 && layout.sameRow, "navigation and view mode should share one toolbar row");
    assert.equal(layout.titleHidden, true);
    await page.click(".material-view-switch button:last-child");
    await drawingReady(page);
    await page.screenshot({ path: path.join(reviewDir, "desktop-drawing.png") });
    assert.equal(await page.$eval(".cad-crumb.show", crumb => getComputedStyle(crumb).visibility), "visible");
    await page.click(".cad-crumb-step");
    await materialReady(page, parentFile);
    await page.setViewport({ width: 390, height: 844 });
    await page.goForward();
    await materialReady(page);
    await assertPane(page, false);
    assert.equal(await page.$eval(".cad-crumb.show", crumb => {
      const rect = crumb.getBoundingClientRect();
      const toggle = document.querySelector(".materials-toggle").getBoundingClientRect();
      const header = document.querySelector(".cad-workspace-header").getBoundingClientRect();
      return rect.right <= toggle.left && header.height <= 132 && document.documentElement.scrollWidth <= innerWidth;
    }), true, "phone navigation should clear Materials and use at most two toolbar rows");
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
    assert.match(await page.$eval(".material-tabs [aria-selected=true]", tab => tab.textContent), /Documents/);
    assert.equal(await page.$eval(".material-document:first-child", link => link.classList.contains("material-drawing-feature")), true);
    assert.equal(await page.$eval(".material-tabs", tabs => tabs.textContent.includes("BOM (0)")), false);
    const pose = await cameraPose(page);
    const modelCanvas = await page.$("canvas.cad-viewport");
    await page.click(".material-drawing-feature");
    const frame = await drawingReady(page);
    assert.equal(await page.$eval(".material-view-switch button[aria-pressed=true]", button => button.textContent), "Drawing");
    assert.match(await frame.$eval("#pdf-text", text => text.textContent), /END-CAP-01/);
    assert.equal(await frame.$("#site-nav"), null, "embedded reading should keep the parent viewer's navigation");
    assert.equal(await frame.$eval(".pdf-heading", heading => getComputedStyle(heading).display), "none");
    assert.equal(await frame.$eval(".pdf-toolbar", toolbar => getComputedStyle(toolbar).display), "none");
    assert.equal(await frame.$eval(".pdf-viewport", viewport => Math.abs(viewport.clientHeight - innerHeight) <= 1), true);
    await page.click(".drawing-menu > summary");
    assert.equal(await page.$eval(".drawing-pages", pages => pages.hidden), true, "single-sheet drawings need no pagination");
    assert.match(await page.$eval(".drawing-download", link => link.href), /\?download=1$/);
    assert.match(await page.$eval(".drawing-full-link", link => link.href), /endcap-circular-2hole-drawing\.pdf$/);
    await page.keyboard.press("Escape");
    assert.equal(await page.$eval(".drawing-menu", menu => menu.open), false);
    assert.equal(await page.$eval(".material-view-switch button[aria-pressed=true]", button => button.textContent), "Drawing");
    await page.click(".drawing-menu > summary");
    await frame.click(".pdf-viewport");
    await page.waitForFunction(() => !document.querySelector(".drawing-menu").open);
    const fit = await frame.$eval(".pdf-paper", paper => ({
      width: paper.clientWidth, height: paper.clientHeight,
      viewportWidth: paper.parentElement.clientWidth, viewportHeight: paper.parentElement.clientHeight,
      scrollWidth: paper.parentElement.scrollWidth,
    }));
    assert.ok(fit.width <= fit.viewportWidth && fit.height <= fit.viewportHeight, "the initial drawing view should fit the entire sheet");
    assert.ok(fit.scrollWidth <= fit.viewportWidth, "fit page should not introduce horizontal scrolling");
    await page.click(".drawing-zoom button:last-child");
    await frame.waitForFunction(width => parseFloat(document.querySelector("#pdf-canvas").style.width) > width * 1.15
      && document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false", {}, fit.width);
    await page.click(".drawing-zoom button:nth-child(2)");
    await frame.waitForFunction(width => Math.abs(parseFloat(document.querySelector("#pdf-canvas").style.width) - width) < 2
      && document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false", {}, fit.width);
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
    await page.click(".drawing-zoom button:last-child");
    await frame.waitForFunction(() => document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false");
    await page.screenshot({ path: path.join(reviewDir, "phone-drawing.png") });
    await frame.click(".pdf-viewport");
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

test("narrow phones keep touch controls in two rows and move zoom steps into the drawing menu", async () => {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 320, height: 740, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await page.goto(baseUrl + materialUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await page.click(".material-view-switch button:last-child");
    const frame = await drawingReady(page);
    assert.equal(await page.$eval(".cad-workspace-header", header => header.getBoundingClientRect().height <= 132), true);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.click(".drawing-menu > summary");
    assert.equal(await page.$eval(".drawing-menu-zoom", controls => getComputedStyle(controls).display), "flex");
    await page.click(".drawing-menu-zoom button:last-child");
    await page.waitForFunction(() => document.querySelector(".drawing-zoom button:nth-child(2)").title.includes("125%"));
    await page.keyboard.press("Escape");
    await frame.waitForFunction(() => document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false");
    await page.screenshot({ path: path.join(reviewDir, "narrow-phone-drawing.png") });
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
    await page.setViewport({ width: 844, height: 390, isMobile: true, hasTouch: true });
    await page.goto(baseUrl + searchUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await assertPane(page, false);
    await page.click(".material-view-switch button:last-child");
    await drawingReady(page);
    assert.equal(await page.$eval(".cad-workspace-header", header => header.getBoundingClientRect().height <= 80), true,
      "landscape phones should keep one toolbar row");
    await page.screenshot({ path: path.join(reviewDir, "landscape-phone-drawing.png") });
  } finally { await page.close(); }
});

test("multi-page drawings expose pagination in the document menu", async () => {
  const page = await browser.newPage();
  const guide = fs.readFileSync(new URL("../../../hardware/install-guide/install-guide.pdf", import.meta.url));
  try {
    await page.setRequestInterception(true);
    page.on("request", request => {
      if (request.url().includes("/docs/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf?raw=1")) {
        void request.respond({ status: 200, contentType: "application/pdf", body: guide });
      } else void request.continue();
    });
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(baseUrl + materialUrl, { waitUntil: "domcontentloaded" });
    await materialReady(page);
    await page.click(".material-view-switch button:last-child");
    const frame = await drawingReady(page);
    await page.click(".drawing-menu > summary");
    assert.equal(await page.$eval(".drawing-pages", controls => controls.hidden), false);
    assert.equal(await page.$eval(".drawing-pages input", input => input.max), "34");
    await page.click('.drawing-pages button[aria-label="Next page"]');
    await frame.waitForFunction(() => document.querySelector("#pdf-canvas").dataset.page === "2"
      && document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false");
    assert.equal(await page.$eval(".drawing-pages input", input => input.value), "2");
  } finally { await page.close(); }
});
