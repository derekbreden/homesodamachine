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
      assert.equal(await page.$eval(".forecast-controls", el => el.hidden), true);
      assert.equal(await page.$eval('.forecast-plan[data-units="10"]', el => el.open), true);
      await page.click('.forecast-plan[data-units="20"] > summary');
      assert.equal(await page.$eval('.forecast-plan[data-units="20"]', el => el.open), true);
      assert.equal(await page.$eval(".forecast-supplier", el => el.open), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `supplier quantities at ${width}px`);
      assert.match(await page.$eval(".forecast-supplier", el => el.textContent), /11[0]? pieces|110/);
      await page.click('.forecast-plan[data-units="10"] .forecast-part > summary');
      assert.equal(await page.$eval('.forecast-plan[data-units="10"] .forecast-part', el => el.open), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `stock details at ${width}px`);
    }
  } finally { await page.close(); }
});

test("batch purchases rank by cost, filter Prime, regroup categories and preserve stock credits", async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  const hardware = fileURLToPath(new URL("../../../hardware", import.meta.url));
  const forecast = readBatchForecast(hardware, readLaborRollup(hardware));
  const dollars = cents => "$" + (cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const active = '.forecast-plan:not([hidden])';
  const current = active + ' .forecast-groups:not([hidden])';
  try {
    for (const width of [320, 390, 1440]) {
      await page.setViewport({ width, height: 950, deviceScaleFactor: 1 });
      await page.goto(baseUrl + "/cost", { waitUntil: "networkidle0" });
      assert.equal(await page.$eval(".forecast-controls", el => el.hidden), false);
      assert.equal(await page.$eval(active, el => el.dataset.units), "10");
      const prime = current + ' [data-group-id="amazon"]';
      assert.equal(await page.$eval(prime, el => el.open), true);
      const firstRows = await page.$$eval(prime + " .forecast-part:not([hidden])", rows => rows.map(row => ({ id: row.dataset.partId, cents: Number(row.dataset.cents) })));
      const expected = forecast.batches[0].rows.filter(row => row.supplier === "amazon" && row.quantity).sort((a, b) => b.costCents - a.costCents);
      assert.equal(firstRows[0].id, "petgf-black");
      assert.equal(firstRows.length, expected.length);
      assert.deepEqual(firstRows.map(row => row.cents), expected.map(row => row.costCents));
      assert.match(await page.$eval(prime + " .forecast-part-qty", el => el.textContent), /19 × 3 kg spool/);
      const scroll = await page.$eval(prime + " .forecast-item-scroll", el => ({ height: el.clientHeight, content: el.scrollHeight }));
      assert.ok(scroll.content > scroll.height, "Prime list scrolls within its panel");
      assert.ok(scroll.height <= 420, "list fits in a compact panel");
      await page.focus(prime + " .forecast-item-scroll");
      await page.keyboard.press("End");
      await page.waitForFunction(selector => document.querySelector(selector).scrollTop > 0, {}, prime + " .forecast-item-scroll");

      await page.select("#forecast-supplier", "amazon");
      assert.ok((await page.$eval(".forecast-result", el => el.textContent)).includes(dollars(expected.reduce((sum, row) => sum + row.costCents, 0))));
      await page.select("#forecast-group", "category");
      const sums = await page.$$eval(current + " .forecast-group:not([hidden])", groups => groups.map(group => Number(group.dataset.cents)));
      assert.deepEqual(sums, [...sums].sort((a, b) => b - a));
      assert.equal(sums.reduce((sum, cents) => sum + cents, 0), 810300);
      assert.equal(await page.$$eval(current + " .forecast-part:not([hidden])", rows => new Set(rows.map(row => row.dataset.supplier)).size), 1);
      assert.equal(await page.$$eval(current + " .forecast-part:not([hidden])", rows => new Set(rows.map(row => row.dataset.partId)).size), expected.length);

      await page.focus('input[name="forecast-units"][value="10"]');
      await page.keyboard.press("ArrowRight");
      assert.equal(await page.$eval(active, el => el.dataset.units), "20");
      assert.match(await page.$eval(".forecast-result", el => el.textContent), /\$18,065.11/);
      assert.equal(await page.$eval('[data-card-units="20"]', el => el.dataset.selected), "true");
      await page.select("#forecast-group", "supplier");
      await page.select("#forecast-supplier", "all");
      assert.ok((await page.$eval(".forecast-result", el => el.textContent)).includes(dollars(forecast.batches[1].partsCents)));
      await page.click("#forecast-show-stock");
      assert.equal(await page.$$eval(current + " .forecast-part:not([hidden])", rows => rows.length), forecast.batches[1].rows.length);
      assert.ok((await page.$eval(".forecast-result", el => el.textContent)).includes(dollars(forecast.batches[1].partsCents)), "stock credits do not alter the cash total");

      await page.select("#forecast-supplier", "jlc");
      await page.focus('input[name="forecast-units"][value="20"]');
      await page.keyboard.press("ArrowLeft");
      assert.match(await page.$eval(".forecast-result", el => el.textContent), /\$0.00.*1 stock credit/);
      const board = current + " .forecast-part:not([hidden])";
      assert.equal(await page.$eval(board, el => el.dataset.purchase), "false");
      await page.click(board + " > summary");
      assert.match(await page.$eval(board, el => el.textContent), /Batch need.*10 pieces.*On hand.*10 pieces/s);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `purchase and stock details at ${width}px`);
      await page.click("#forecast-show-stock");
      assert.match(await page.$eval(current, el => el.textContent), /No new purchases for this supplier/);
      assert.equal(await page.$$eval(current + " .forecast-group:not([hidden])", groups => groups.length), 0);
    }
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});
