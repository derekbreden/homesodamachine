import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { start } from "../../server.js";
import { readBatchForecast } from "../../lib/batch-forecast.js";
import { readLaborRollup } from "../../lib/cost.js";

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

test("keyboard controls update the recovery figure, sales balance and accessible chart", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  try {
    await page.goto(baseUrl + "/cost", { waitUntil: "networkidle0" });
    assert.equal(await page.$eval(".recovery-controls", el => el.hidden), false);
    const contribution = () => page.$eval('[data-recovery="contribution"]', el => Number(el.textContent.replace(/[^\d.-]/g, "")));
    const initial = await contribution();
    const initialPath = await page.$eval(".recovery-line", el => el.getAttribute("d"));
    await page.focus("#machine-cost");
    for (let n = 0; n < 10; n++) await page.keyboard.press("ArrowRight");
    assert.equal(await contribution(), Math.round((initial - 500) * 100) / 100);
    assert.notEqual(await page.$eval(".recovery-line", el => el.getAttribute("d")), initialPath);
    assert.match(await page.$eval("#machine-cost", el => el.getAttribute("aria-valuetext")), /per machine/);
    const sliderCost = await page.$eval("#machine-cost", el => Number(el.value));
    assert.equal(await page.$eval('[data-recovery="machine-cost"]', el => Number(el.textContent.replace(/[^\d.-]/g, ""))), sliderCost);

    await page.focus("#sales-units");
    await page.keyboard.press("Home");
    assert.equal(await page.$eval('[data-recovery="available"]', el => el.textContent), "$0");
    assert.match(await page.$eval("#recovery-chart-desc", el => el.textContent), /At 0 machines, \$0.00 is available/);

    await page.focus("#machine-cost");
    await page.keyboard.press("End");
    assert.equal(await page.$eval('[data-recovery="range"]', el => el.textContent), "No recovery");
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test("price, chart and cost disclosures work without JavaScript and fit phone widths", async () => {
  const page = await browser.newPage();
  try {
    await page.setJavaScriptEnabled(false);
    for (const width of [320, 390, 768, 1440]) {
      await page.setViewport({ width, height: 950, deviceScaleFactor: 1 });
      await page.goto(baseUrl + "/cost", { waitUntil: "networkidle0" });
      assert.equal(await page.$eval(".recovery-controls", el => el.hidden), true);
      assert.match(await page.$eval(".cost-price", el => el.textContent), /\$4,495/);
      assert.equal(await page.$eval("main > section", el => el.classList.contains("cost-price")), true);
      assert.ok(await page.$(".recovery-svg"));
      assert.match(await page.$eval("#batch-forecast", el => el.textContent), /From today’s stock to 10 & 20 machines/);
      const hardware = fileURLToPath(new URL("../../../hardware", import.meta.url));
      const cash = readBatchForecast(hardware, readLaborRollup(hardware)).batches[0].cashCents / 100;
      assert.ok((await page.$eval(".forecast-cards", el => el.textContent)).includes("$" + cash.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `page at ${width}px`);
      await page.click("#recovery details summary");
      assert.equal(await page.$eval("#recovery details", el => el.open), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `investment at ${width}px`);
      await page.click("main > details.cost-cat summary");
      assert.equal(await page.$eval("main > details.cost-cat", el => el.open), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `parts at ${width}px`);
      await page.click(".forecast-supplier summary");
      assert.equal(await page.$eval(".forecast-supplier", el => el.open), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `supplier quantities at ${width}px`);
      assert.match(await page.$eval(".forecast-supplier", el => el.textContent), /11[0]? pieces|110/);
    }
  } finally { await page.close(); }
});
