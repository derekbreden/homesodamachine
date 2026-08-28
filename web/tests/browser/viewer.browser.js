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

test("/3d zoom reaches the picked rear surface and leaves it as the orbit focus", async () => {
  const page = await browser.newPage();
  const file = "printed-parts/enclosure/enclosure/enclosure-back-top.step";
  try {
    await page.goto(`${baseUrl}/3d#step:${encodeURIComponent(file)}`, {
      waitUntil: "domcontentloaded",
    });
    await page.waitForFunction(
      (wanted) => window.__hsm?.mountedStepFile === wanted && window.__hsm.currentGroup,
      { timeout: 30_000 },
      file,
    );

    // In the default front-right-above view, this ray lands on the inside of
    // the Y+ rear wall, well beyond the model-centre target. That is the exact
    // case a centre-only TrackballControls dolly can never reach.
    const before = await page.evaluate(() => {
      const h = window.__hsm;
      const ndc = new h.THREE.Vector2(0.15, 1 / 3);
      const ray = new h.THREE.Raycaster();
      ray.setFromCamera(ndc, h.camera);
      const hit = ray.intersectObject(h.currentGroup, true)
        .find((x) => x.face && x.object.isMesh && x.object.visible);
      if (!hit) return null;
      const rect = h.renderer.domElement.getBoundingClientRect();
      const box = new h.THREE.Box3().setFromObject(h.currentGroup);
      return {
        point: hit.point.toArray(),
        center: box.getCenter(new h.THREE.Vector3()).toArray(),
        target: h.controls.target.toArray(),
        pointTargetDistance: hit.point.distanceTo(h.controls.target),
        client: [
          rect.left + (ndc.x + 1) * rect.width / 2,
          rect.top + (1 - ndc.y) * rect.height / 2,
        ],
        ndc: ndc.toArray(),
      };
    });
    assert.ok(before, "the regression ray should hit the rear wall");
    assert.ok(before.point[1] > before.center[1] + 100,
      "the picked wall must be beyond the original centre target");

    await page.mouse.move(...before.client);
    await page.mouse.wheel({ deltaY: -800 });
    await new Promise((resolve) => setTimeout(resolve, 1_000));

    const afterZoom = await page.evaluate((point) => {
      const h = window.__hsm;
      const p = new h.THREE.Vector3(...point);
      const projected = p.clone().project(h.camera);
      return {
        camera: h.camera.position.toArray(),
        target: h.controls.target.toArray(),
        pointTargetDistance: p.distanceTo(h.controls.target),
        ndc: [projected.x, projected.y],
      };
    }, before.point);

    assert.ok(afterZoom.camera[1] > before.target[1] + 50,
      "camera should travel beyond the old centre instead of stalling at it");
    assert.ok(afterZoom.pointTargetDistance < before.pointTargetDistance * 0.2,
      "the picked surface should become the orbit focus");
    assert.ok(Math.abs(afterZoom.ndc[0] - before.ndc[0]) < 0.04
      && Math.abs(afterZoom.ndc[1] - before.ndc[1]) < 0.04,
      `zoom should keep the picked surface pinned beneath the pointer: ${JSON.stringify({
        before: before.ndc, after: afterZoom.ndc,
      })}`);

    // A subsequent orbit should still be centred close enough to that surface
    // that it remains in the viewport instead of swinging away around the
    // enclosure's bounding-box centre.
    await page.mouse.move(...before.client);
    await page.mouse.down();
    await page.mouse.move(before.client[0] + 80, before.client[1], { steps: 4 });
    await page.mouse.up();
    await new Promise((resolve) => setTimeout(resolve, 700));
    const afterOrbit = await page.evaluate((point) => {
      const h = window.__hsm;
      const p = new h.THREE.Vector3(...point);
      const projected = p.clone().project(h.camera);
      return {
        pointTargetDistance: p.distanceTo(h.controls.target),
        ndc: [projected.x, projected.y],
      };
    }, before.point);
    assert.ok(afterOrbit.pointTargetDistance < before.pointTargetDistance * 0.2);
    assert.ok(Math.abs(afterOrbit.ndc[0]) < 1 && Math.abs(afterOrbit.ndc[1]) < 1,
      "the focused rear-wall feature should remain in view after orbiting");
  } finally {
    await page.close().catch(() => {});
  }
});
