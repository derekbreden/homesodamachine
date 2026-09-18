import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
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

test("inventory links open the list; navigation and preparation survive reloads", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.goto(baseUrl + "/0001", { waitUntil: "networkidle0" });
    await page.click('a[href="#included"]');
    assert.equal(await page.$eval("#included", el => el.open), true);
    await page.reload({ waitUntil: "networkidle0" });
    assert.equal(await page.$eval("#included", el => el.open), true);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "networkidle0" }),
      page.click('.unit-nav a[href="/0001/get-started"]'),
    ]);
    await page.click('input[name="kit"]');
    await page.reload({ waitUntil: "networkidle0" });
    assert.equal(await page.$eval('input[name="kit"]', el => el.checked), true);
    assert.equal(await page.$eval('input[name="supplies"]', el => el.checked), false);
    assert.equal(await page.$$eval(".unit-route a", links => links.length), 7);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "networkidle0" }),
      page.click('.unit-nav a[href="/0001/guides"]'),
    ]);
    assert.equal(await page.$$eval(".unit-document", links => links.length), 3);
    await page.goBack({ waitUntil: "networkidle0" });
    assert.equal(new URL(page.url()).pathname, "/0001/get-started");
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("all three pages fit phone and desktop widths, including without JavaScript", async () => {
  const page = await browser.newPage();
  try {
    await page.setJavaScriptEnabled(false);
    for (const width of [320, 390, 1024, 1440]) {
      await page.setViewport({ width, height: 950, deviceScaleFactor: 1 });
      for (const route of ["/0001", "/0001/get-started", "/0001/guides"]) {
        await page.goto(baseUrl + route, { waitUntil: "networkidle0" });
        const result = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > window.innerWidth,
          images: [...document.querySelectorAll(".unit-page img")].every(img => img.complete && img.naturalWidth > 0),
          heading: document.querySelector("h1")?.textContent,
          activeLinks: document.querySelectorAll('.unit-nav [aria-current="page"]').length,
        }));
        assert.equal(result.overflow, false, `${route} at ${width}px`);
        assert.equal(result.images, true, `${route} artwork at ${width}px`);
        assert.ok(result.heading);
        assert.equal(result.activeLinks, 1);
      }
    }
    await page.goto(baseUrl + "/0001");
    await page.click("#included summary");
    assert.equal(await page.$eval("#included", el => el.open), true);
  } finally { await page.close(); }
});
