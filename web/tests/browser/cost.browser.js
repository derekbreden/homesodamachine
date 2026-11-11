// Browser checks exercise the production workspace, saved scenarios and the cost disclosures on desktop and phone.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { start } from "../../server.js";

const require = createRequire(new URL("../../../tools/render/package.json", import.meta.url));
let browser, server, baseUrl;
before(async () => {
  browser = await require("puppeteer").launch({ headless: true });
  ({ server } = await start({ port: 0 }));
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
    await page.click('.cost-contents a[href="#recovery"]');
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
    assert.equal(await page.$eval('[data-recovery-overview="range"]', el => el.textContent), "No recovery");
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test('production planning starts at unit two, updates pack coverage, and restores this browser’s scenario', async () => {
  const page = await browser.newPage(), errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto(baseUrl + '/cost', { waitUntil: 'networkidle0' });
    await page.evaluate(() => localStorage.removeItem('hsm-production-scenario-v1'));
    await page.reload({ waitUntil: 'networkidle0' });
    await page.waitForSelector('.production-planner[data-enhanced="true"]');
    assert.match(await page.$eval('#planner-focus-title', el => el.textContent), /second unit/);
    assert.equal(await page.$eval('.planner-milestone[aria-pressed="true"]', el => el.dataset.focus), '2');
    assert.equal(await page.$eval('.planner-basket-total > strong', el => el.textContent), '$0.00');
    const before = await page.$eval('.planner-milestone[data-focus="2"] .planner-forecast-money', el => el.textContent);
    await page.click('#planner-fill');
    await page.waitForFunction(() => document.querySelectorAll('.planner-basket-items > button').length > 0);
    assert.notEqual(await page.$eval('.planner-basket-total > strong', el => el.textContent), '$0.00');
    assert.notEqual(await page.$eval('.planner-milestone[data-focus="2"] .planner-forecast-money', el => el.textContent), before);
    const basket = await page.$eval('.planner-basket-total > strong', el => el.textContent);
    await page.reload({ waitUntil: 'networkidle0' });
    await page.waitForSelector('.production-planner[data-enhanced="true"]');
    assert.equal(await page.$eval('.planner-basket-total > strong', el => el.textContent), basket);
    await page.select('#planner-buy-for', '10');
    await page.click('#planner-fill');
    assert.equal(await page.$eval('.planner-milestone[aria-pressed="true"]', el => el.dataset.focus), '10');
    await page.evaluate(() => document.querySelector('.planner-basket-items button').click());
    await page.waitForSelector('.planner-detail input[data-kind="pack"]');
    const input = await page.$eval('.planner-detail input[data-kind="pack"]:not([disabled])', el => el.id);
    await page.$eval('#' + input, el => { el.value = Number(el.value) + 1; el.dispatchEvent(new Event('input', { bubbles: true })); });
    assert.ok((await page.$$eval('.planner-basket-items > button', els => els.length)) > 0);
    const packsBefore = await page.$eval('#' + input, el => Number(el.value));
    await page.evaluate(() => document.querySelector('.planner-detail .planner-stepper button:last-child:not([disabled])').click());
    assert.equal(await page.$eval('#' + input, el => Number(el.value)), packsBefore + 1);
    await page.click('#planner-reset');
    assert.equal(await page.$eval('.planner-basket-total > strong', el => el.textContent), '$0.00');
    assert.deepEqual(errors, []);
  } finally { await page.close(); }
});

test('the unit outlook, material packs and economics fit phone and desktop widths', async () => {
  const page = await browser.newPage();
  try {
    for (const width of [320, 390, 1440]) {
      await page.setViewport({ width, height: 950, deviceScaleFactor: 1 });
      await page.goto(baseUrl + '/cost', { waitUntil: 'networkidle0' });
      await page.waitForSelector('.production-planner[data-enhanced="true"]');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `page at ${width}`);
      await page.select('#planner-filter', 'all');
      await page.evaluate(() => document.querySelector('.planner-material-toggle').click());
      await page.waitForSelector('.planner-detail');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `expanded material at ${width}`);
      await page.select('#planner-horizon', '20');
      assert.equal(await page.$$eval('.planner-unit-strip button', els => els.length), 20);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `outlook at ${width}`);
      await page.evaluate(() => document.querySelector('.cost-contents a[href="#parts"]').click());
      assert.equal(await page.$eval('#unit-cost-panel', el => el.open), true);
      await page.evaluate(() => document.querySelector('.cost-contents a[href="#recovery"]').click());
      assert.equal(await page.$eval('#investment-panel', el => el.open), true);
    }
  } finally { await page.close(); }
});

test('stock and cost records remain reachable without JavaScript', async () => {
  const page = await browser.newPage();
  try {
    await page.setJavaScriptEnabled(false);
    await page.setViewport({ width: 390, height: 950 });
    await page.goto(baseUrl + '/cost', { waitUntil: 'networkidle0' });
    assert.ok(await page.$('.production-planner a[href^="/build?material="]'));
    await page.click('.cost-contents a[href="#parts"]');
    assert.equal(await page.$eval('#unit-cost-panel', el => el.open), true);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  } finally { await page.close(); }
});
