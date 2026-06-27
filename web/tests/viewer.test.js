// Viewer-page smoke test via puppeteer.
//
// The route smoke (smoke.test.js) only verifies that GET /3d responds 200
// with HTML — it doesn't verify the page actually renders the parts grid,
// because that requires JS execution + a fetch round-trip to /api/steps
// and /api/dxf. This test fills that gap: open /3d in a real browser,
// wait for the grid to populate, assert the subsystem subheaders we
// expect ("Cold Core", "Faucet", "Flavor", "Reference", "Carbonation")
// all appear in the DOM.
//
// Skipped automatically if puppeteer's Chromium isn't downloaded — useful
// in CI scenarios where chrome installs are gated. Costs ~3-5 seconds
// when it runs; smoke.test.js is the priority and stays fast.

import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { start } from "../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

let server;
let baseUrl;
let puppeteer;
let browser;

before(async () => {
  // Lazy-import puppeteer so a missing-Chromium environment doesn't
  // prevent the file from loading. We'll skip the test cleanly below.
  try {
    puppeteer = (await import("puppeteer")).default;
  } catch {
    puppeteer = null;
  }
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

test("/3d renders subsystem subheaders after JS hydrates", async (t) => {
  if (!puppeteer) return t.skip("puppeteer unavailable");
  // Skip if both hardware kinds (printed + cut) are empty — the test
  // would have nothing to assert on. The route-smoke /api/steps test
  // covers the empty-tree boot case.
  const haveAny =
    fs.existsSync(path.join(REPO_ROOT, "hardware", "printed-parts")) ||
    fs.existsSync(path.join(REPO_ROOT, "hardware", "cut-parts")) ||
    fs.existsSync(path.join(REPO_ROOT, "hardware", "reference"));
  if (!haveAny) return t.skip("hardware tree empty");

  try {
    browser = await puppeteer.launch({ headless: true });
  } catch (e) {
    return t.skip(`puppeteer launch failed: ${e.message}`);
  }
  const page = await browser.newPage();
  await page.goto(`${baseUrl}/3d`, { waitUntil: "domcontentloaded" });

  // Wait for the grid to populate. The viewer JS fetches /api/steps and
  // /api/dxf, then renders subsection-header divs per category. 10s is a
  // generous timeout — typical render is well under a second.
  await page.waitForSelector(".subsection-header", { timeout: 10_000 });

  const headers = await page.$$eval(".subsection-header", (els) =>
    els.map((el) => el.textContent.trim()),
  );

  // Expected subheaders match the folder shape under
  // hardware/printed-parts/, hardware/cut-parts/, and top-level dirs like
  // hardware/reference/. If any go missing, the viewer has either lost a
  // file kind or the category-derivation logic regressed.
  const expected = ["Cold Core", "Faucet", "Flavor", "Reference", "Carbonation"];
  for (const want of expected) {
    assert.ok(
      headers.includes(want),
      `expected subheader "${want}" in [${headers.join(", ")}]`,
    );
  }
});

test("/pcb board modal shows the board's outer dimensions", async (t) => {
  if (!puppeteer) return t.skip("puppeteer unavailable");
  // Needs a rendered board with a picks sidecar (the dimensions source).
  const picksPath = path.join(
    REPO_ROOT, "hardware", "pcb", "carrier", "out", "mini.picks.json",
  );
  if (!fs.existsSync(picksPath)) return t.skip("no rendered board with picks");

  // Reuse the browser the prior test launched; launch one if it skipped.
  if (!browser) {
    try {
      browser = await puppeteer.launch({ headless: true });
    } catch (e) {
      return t.skip(`puppeteer launch failed: ${e.message}`);
    }
  }
  const page = await browser.newPage();
  try {
    await page.goto(`${baseUrl}/pcb`, { waitUntil: "domcontentloaded" });

    // Open the first board by deep-link hash and read the dimensions chip.
    // Asserting against the board's own picks `size` keeps this dynamic — it
    // tracks a resize instead of pinning a magic number.
    const board = await page.evaluate(() =>
      fetch("/api/pcb").then((r) => r.json()).then((b) => b[0]),
    );
    assert.ok(board && board.picks, "expected a board with a picks sidecar from /api/pcb");

    const size = await page.evaluate(
      (p) => fetch(`/api/pcb-picks/${p}`).then((r) => r.json()).then((j) => j.size),
      board.picks,
    );
    // picks.json is a render artifact; if it predates the size field, skip
    // rather than fail (a re-render adds it — see pick-data.ts).
    if (!size || !size.width || !size.height) {
      return t.skip("board picks lack size — re-render needed");
    }

    await page.evaluate((src) => {
      location.hash = "pcb:" + encodeURIComponent(src);
    }, board.source);

    await page.waitForSelector(".pcb-dims", { timeout: 10_000 });
    const chip = await page.$eval(".pcb-dims", (el) => el.textContent.trim());

    const fmt = (n) => (Math.round(n * 10) / 10).toString();
    const want = `${fmt(size.width)} × ${fmt(size.height)} mm`;
    assert.equal(chip, want, `dims chip "${chip}" should equal "${want}"`);
  } finally {
    await page.close().catch(() => {});
  }
});

test("/pcb view toggle exposes inner copper planes in stack order", async (t) => {
  if (!puppeteer) return t.skip("puppeteer unavailable");
  if (!browser) {
    try {
      browser = await puppeteer.launch({ headless: true });
    } catch (e) {
      return t.skip(`puppeteer launch failed: ${e.message}`);
    }
  }
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
    // Overlay. Inner keys come from the board's own inners list, so this tracks
    // a 4-layer board the same as a 6-layer one.
    const views = await page.$$eval(".pcb-view-toggle .pcb-view-btn", (els) =>
      els.map((e) => e.dataset.view),
    );
    const innerKeys = board.inners.map((p) => "inner" + p.match(/\.inner(\d+)\.svg$/)[1]);
    assert.deepEqual(views, ["top", ...innerKeys, "bottom", "overlay"]);

    // Clicking an inner button activates it (the view actually switches).
    const firstInner = innerKeys[0];
    await page.click(`.pcb-view-btn[data-view="${firstInner}"]`);
    const active = await page.$eval(".pcb-view-btn.active", (e) => e.dataset.view);
    assert.equal(active, firstInner, "clicked inner button should become active");
  } finally {
    await page.close().catch(() => {});
  }
});
