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
