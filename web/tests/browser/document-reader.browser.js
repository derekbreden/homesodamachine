import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
let browser, server, baseUrl;
const screenshotDir = path.resolve("../.cache/pwa-pdf-reader");
const installGuide = "/read/install-guide/install-guide.pdf";
before(async () => {
  browser = await require("puppeteer").launch({ headless: true });
  ({ server } = await start({ dev: true, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
  fs.mkdirSync(screenshotDir, { recursive: true });
});
after(async () => {
  await browser?.close();
  server?.closeAllConnections?.();
  if (server) await new Promise(resolve => server.close(resolve));
});

async function rendered(page, number) {
  await page.waitForFunction(wanted => {
    const canvas = document.getElementById("pdf-canvas");
    return canvas?.dataset.page === String(wanted)
      && document.querySelector(".pdf-viewport").getAttribute("aria-busy") === "false";
  }, { timeout: 30_000 }, number);
}

async function boundedCanvas(page) {
  const result = await page.evaluate(() => {
    const canvas = document.getElementById("pdf-canvas");
    const text = document.getElementById("pdf-text");
    return {
      width: canvas.width, height: canvas.height, count: document.querySelectorAll("#pdf-canvas").length,
      overflow: document.documentElement.scrollWidth > innerWidth,
      nativeViewers: document.querySelectorAll("iframe, embed, object").length,
      text: text.textContent,
      colored: canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data.some((v, i) => i % 4 !== 3 && v < 240),
    };
  });
  assert.ok(result.width * result.height <= 4 * 1024 * 1024);
  assert.ok(result.width <= 4096 && result.height <= 4096);
  assert.equal(result.count, 1);
  assert.equal(result.overflow, false);
  assert.equal(result.nativeViewers, 0);
  assert.ok(result.text.trim().length > 0);
  assert.equal(result.colored, true, "page has rendered content");
}

test("phone guide links keep page targets, Back, page history and bounded zoom in the app", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    await page.goto(baseUrl + "/0001/get-started", { waitUntil: "domcontentloaded" });
    await Promise.all([page.waitForNavigation(), page.click(".unit-route li:first-child a")]);
    await rendered(page, 6);
    assert.equal(new URL(page.url()).pathname, installGuide);
    assert.equal(await page.$eval("#pdf-back", el => new URL(el.href).pathname), "/0001/get-started");
    await page.screenshot({ path: path.join(screenshotDir, "phone-install-page6.png") });
    await boundedCanvas(page);
    await page.click("#pdf-next");
    await rendered(page, 7);
    await page.goBack();
    await rendered(page, 6);
    await page.goForward();
    await rendered(page, 7);
    await page.evaluate(() => {
      for (let i = 0; i < 12; i++) document.getElementById("pdf-zoom-in").click();
      document.getElementById("pdf-next").click();
      document.getElementById("pdf-next").click();
    });
    await rendered(page, 9);
    await boundedCanvas(page);
    await page.click("#pdf-fit");
    await rendered(page, 9);
    await page.setViewport({ width: 844, height: 390, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    await page.waitForFunction(() => parseFloat(document.getElementById("pdf-canvas").style.width) > 700);
    await rendered(page, 9);
    await boundedCanvas(page);
    await Promise.all([page.waitForNavigation(), page.click("#pdf-back")]);
    assert.equal(new URL(page.url()).pathname, "/0001/get-started");

    // Saved raw-PDF links also reach the reader; redirects retain #page.
    await page.goto(baseUrl + "/docs/install-guide/install-guide.pdf#page=31");
    await rendered(page, 31);
    assert.equal(new URL(page.url()).pathname, installGuide);
    await page.evaluate(() => { location.hash = "page=9999"; });
    await rendered(page, 34);
    assert.equal(await page.$eval("#pdf-next", el => el.disabled), true);
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("every published PDF renders on a narrow phone without a native viewer", async () => {
  const docs = await fetch(baseUrl + "/api/documents").then(response => response.json());
  assert.ok(docs.length > 0);
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.setViewport({ width: 320, height: 740, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    for (const doc of docs) {
      await page.goto(`${baseUrl}/read/${doc.path}`, { waitUntil: "domcontentloaded" });
      await rendered(page, 1);
      await boundedCanvas(page);
      assert.equal(await page.$eval("#pdf-pages", el => Number(el.textContent)), doc.pages, doc.path);
    }
    await page.setViewport({ width: 1440, height: 950, deviceScaleFactor: 2 });
    await page.goto(baseUrl + installGuide + "#page=6");
    await rendered(page, 6);
    await page.screenshot({ path: path.join(screenshotDir, "desktop-install-page6.png") });
    await page.evaluate(() => {
      for (let i = 0; i < 12; i++) document.getElementById("pdf-zoom-in").click();
    });
    await rendered(page, 6);
    await boundedCanvas(page);
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("a PDF fetch failure stays in the app and can be retried", async () => {
  const page = await browser.newPage();
  let fail = true;
  await page.setRequestInterception(true);
  page.on("request", request => {
    if (fail && request.url().includes("/docs/install-guide/install-guide.pdf?raw=1")) {
      void request.respond({ status: 503, contentType: "text/plain", body: "Unavailable" });
    } else void request.continue();
  });
  try {
    await page.goto(baseUrl + installGuide);
    await page.waitForSelector("#pdf-retry:not([hidden])");
    assert.match(await page.$eval("#pdf-status", el => el.textContent), /Try again/);
    fail = false;
    await page.click("#pdf-retry");
    await rendered(page, 1);
    assert.equal(new URL(page.url()).pathname, installGuide);
  } finally { await page.close(); }
});
