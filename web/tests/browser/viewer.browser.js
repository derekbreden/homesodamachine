// The browser pass. Runs on demand:
//
//     npm run test:browser
//
// `npm test`'s glob is `tests/**/*.test.js` and does not reach `.browser.js`.
//
// Puppeteer is tools/render's dependency (tools/render/package.json), installed by
// hand on the machine that renders. This file resolves it there.

import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

import { start } from "../../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
const RENDER_MODULES = path.join(REPO_ROOT, "tools", "render", "node_modules");

const require = createRequire(import.meta.url);

function loadPuppeteer() {
  try {
    return require(require.resolve("puppeteer", { paths: [RENDER_MODULES] }));
  } catch (e) {
    throw new Error(
      `puppeteer does not resolve from ${RENDER_MODULES}: ${e.message}\n` +
        `  install it where it lives:  cd ${path.join(REPO_ROOT, "tools", "render")} && npm install`,
    );
  }
}

let server;
let baseUrl;
let browser;

before(async () => {
  const puppeteer = loadPuppeteer();
  browser = await puppeteer.launch({ headless: true });
  const started = await start({ dev: false, port: 0 });
  server = started.server;
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  if (browser) await browser.close().catch(() => {});
  if (server) {
    server.closeAllConnections?.();
    await new Promise((resolve) => server.close(resolve));
  }
});

test("/pcb view toggle exposes inner copper planes in stack order", async (t) => {
  const page = await browser.newPage();
  try {
    await page.goto(`${baseUrl}/pcb`, { waitUntil: "domcontentloaded" });

    // Find a multi-layer board (one /api/pcb advertises inner planes for).
    const board = await page.evaluate(() =>
      fetch("/api/pcb").then((r) => r.json()).then((b) => b.find((x) => x.inners && x.inners.length)),
    );
    if (!board) return t.skip("no board with inner planes");

    await page.evaluate((src) => {
      location.hash = "pcb:" + encodeURIComponent(src);
    }, board.source);
    await page.waitForSelector(".pcb-view-toggle .pcb-view-btn", { timeout: 10_000 });

    // The toggle's order is the physical stack: Top → inner planes → Bottom →
    // Overlay, then any solder-mask views as adjuncts at the end. Inner + mask keys
    // come from the board's own fields.
    const views = await page.$$eval(".pcb-view-toggle .pcb-view-btn", (els) =>
      els.map((e) => e.dataset.view),
    );
    const innerKeys = board.inners.map((p) => "inner" + p.match(/\.inner(\d+)\.svg$/)[1]);
    const maskKeys = ["topmask", "bottommask"].filter((k) => board[k]);
    assert.deepEqual(views, ["top", ...innerKeys, "bottom", "overlay", ...maskKeys]);

    // Clicking an inner button activates it.
    const firstInner = innerKeys[0];
    await page.click(`.pcb-view-btn[data-view="${firstInner}"]`);
    const active = await page.$eval(".pcb-view-btn.active", (e) => e.dataset.view);
    assert.equal(active, firstInner, "clicked inner button should become active");
  } finally {
    await page.close().catch(() => {});
  }
});
