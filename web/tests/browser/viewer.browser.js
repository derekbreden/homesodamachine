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
  const started = await start({ port: 0 });
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

// The card scales in as the viewer opens, and a model can mount before it stands at
// full size. A pixel read off the canvas before then is not the pixel under the
// pointer once the card settles.
function settled(page) {
  return page.waitForFunction(() => {
    const canvas = window.__hsm.renderer.domElement;
    return Math.abs(canvas.getBoundingClientRect().width - canvas.clientWidth) < 0.5;
  });
}

test("the board material loads PCB code and layers when requested", async (t) => {
  const boards = await fetch(`${baseUrl}/api/pcb`).then(r => r.json());
  const board = boards.find(b => b.source === "pcb/pcba/pcba.tsx" && b.inners?.length);
  if (!board) return t.skip("control board layers are unavailable");

  const page = await browser.newPage();
  try {
    const requests = [];
    page.on("request", req => {
      const { pathname } = new URL(req.url());
      if (/^\/api\/pcb(?:$|-)|\/pcb[^/]*\.js$|\/pan-zoom[^/]*\.js$|\/pcb\.css$/.test(pathname)) {
        requests.push(pathname);
      }
    });
    await page.setViewport({ width: 1440, height: 900 });
    await page.goto(`${baseUrl}/3d#material:HSM-0048`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".material-view-switch button:last-child", { visible: true });
    await page.waitForFunction(() => window.__hsm?.mountedStepFile === "printed-parts/electronics/pcba-tray/pcba-board.step"
      && window.__hsm.currentGroup);
    await settled(page);
    assert.deepEqual(requests, []);
    const canvas = await page.$("canvas.cad-viewport");
    assert.equal(await page.$eval(".material-view-switch button:last-child", button => button.textContent), "PCB");
    assert.equal(await page.$eval(".material-view-switch button[aria-pressed=true]", button => button.textContent), "3D");

    await page.click(".material-view-switch button:last-child");
    await page.waitForSelector(".pcb-view-toggle .pcb-view-btn", { timeout: 10_000 });
    for (const path of ["/js/viewer/pcb.js", "/css/pcb.css", "/api/pcb", "/api/pcb-content/" + board.overlay]) {
      assert.ok(requests.includes(path), `opening the PCB view should request ${path}`);
    }

    const views = await page.$$eval(".pcb-view-toggle .pcb-view-btn", (els) =>
      els.map((e) => e.dataset.view),
    );
    const innerKeys = board.inners.map((p) => "inner" + p.match(/\.inner(\d+)\.svg$/)[1]);
    const maskKeys = ["topmask", "bottommask"].filter((k) => board[k]);
    assert.deepEqual(views, ["top", ...innerKeys, "bottom", "overlay", ...maskKeys]);

    const firstInner = innerKeys[0];
    await page.click(`.pcb-view-btn[data-view="${firstInner}"]`);
    const active = await page.$eval(".pcb-view-btn.active", (e) => e.dataset.view);
    assert.equal(active, firstInner, "clicked inner button should become active");

    await page.click(".materials-toggle");
    await page.waitForFunction(() => {
      const pane = document.querySelector(".material-pcb-view").getBoundingClientRect();
      const board = document.querySelector(".pcb-svg").getBoundingClientRect();
      return board.width > 0 && board.left >= pane.left - 1 && board.right <= pane.right + 1
        && Math.abs((board.left + board.right) - (pane.left + pane.right)) < 2;
    });
    await page.click(".material-view-switch button:first-child");
    assert.equal(await page.$(".material-pcb-view"), null);
    assert.equal(await canvas.evaluate(node => node === document.querySelector("canvas.cad-viewport")), true);
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d opening a selected component and returning keep the exact view", async () => {
  const page = await browser.newPage();
  const assembly = "manifold-layout/enclosure-assembly.step";
  const part = "printed-parts/enclosure/enclosure/enclosure-back-top.step";
  try {
    await page.goto(`${baseUrl}/3d#step:${encodeURIComponent(assembly)}`, {
      waitUntil: "domcontentloaded",
    });
    await page.waitForFunction(
      (wanted) => window.__hsm?.mountedStepFile === wanted && window.__hsm.currentGroup,
      { timeout: 30_000 },
      assembly,
    );
    await settled(page);

    // Look squarely at a patch of the rear wall that nothing stands in front of,
    // then select it through the same canvas gesture a person uses. The patch is
    // searched for: fittings through the wall move, the wall stays.
    const canvasPoint = await page.evaluate(async () => {
      const h = window.__hsm;
      const { setComponentPickEnabled } = await import("/js/viewer/component-picker.js");
      setComponentPickEnabled(true);
      // A click lands on a whole pixel, so the ray is cast through that pixel.
      const rect = h.renderer.domElement.getBoundingClientRect();
      const click = [Math.round(rect.left + rect.width / 2), Math.round(rect.top + rect.height / 2)];
      const ndc = new h.THREE.Vector2(((click[0] - rect.left) / rect.width) * 2 - 1,
        -((click[1] - rect.top) / rect.height) * 2 + 1);
      const front = h.currentGroup.children.filter((c) => c.userData?.side === "front" && c.visible !== false && c.name);
      const ray = new h.THREE.Raycaster();
      const look = (x, z) => {
        h.camera.position.set(x, 650, z);
        h.camera.up.set(0, 0, 1);
        h.controls.target.set(x, 467, z);
        h.camera.lookAt(h.controls.target);
        h.controls.update();
        h.camera.updateMatrixWorld();
        ray.setFromCamera(ndc, h.camera);
        return ray.intersectObjects(front, false)[0]?.object.name === "enclosure-back-top";
      };
      // Clear for a centimetre around, and looking at the middle of it last.
      const patch = (x, z) => [[x + 10, z], [x - 10, z], [x, z + 10], [x, z - 10], [x, z]]
        .every(([px, pz]) => look(px, pz));
      for (let z = 300; z >= 180; z -= 20) {
        for (let x = 80; x >= -80; x -= 20) if (patch(x, z)) return click;
      }
      return null;
    });
    assert.ok(canvasPoint, "some patch of the rear wall should face the camera unobstructed");
    await page.mouse.click(...canvasPoint);
    await page.waitForFunction(() =>
      document.querySelector(".component-panel .edge-panel-file")?.title === "enclosure-back-top",
    );

    const before = await page.evaluate((destination) => {
      const h = window.__hsm;
      // A destination view already stored for this file must not displace the
      // live assembly view carried by Open part.
      localStorage.setItem(`step-camera:${destination}`, JSON.stringify({
        p: [1, 2, 3], u: [0, 1, 0], t: [4, 5, 6],
      }));
      return {
        position: h.camera.position.toArray(),
        up: h.camera.up.toArray(),
        target: h.controls.target.toArray(),
      };
    }, part);

    await page.click(".component-panel .component-open");
    await page.waitForFunction(
      (wanted) => window.__hsm?.mountedStepFile === wanted && window.__hsm.currentGroup,
      { timeout: 30_000 },
      part,
    );

    const after = await page.evaluate(() => {
      const h = window.__hsm;
      return {
        position: h.camera.position.toArray(),
        up: h.camera.up.toArray(),
        target: h.controls.target.toArray(),
        components: [...new Set(h.currentGroup.children
          .filter((c) => c.isMesh && c.userData?.side === "front")
          .map((c) => c.name))],
      };
    });
    assert.deepEqual(after.position, before.position, "camera position moved during component drill");
    assert.deepEqual(after.up, before.up, "camera roll moved during component drill");
    assert.deepEqual(after.target, before.target, "orbit focus moved during component drill");
    assert.deepEqual(after.components, ["enclosure-back-top"]);

    // Move again while looking at the part alone. Taking the top-left ancestor
    // reveals the assembly around that live view instead of restoring the view
    // the assembly had before the drill.
    const beforeReturn = await page.evaluate(() => {
      const h = window.__hsm;
      h.camera.position.set(42, 575, 327);
      h.camera.up.set(0.12, 0.04, 0.99).normalize();
      h.controls.target.set(76, 466, 304);
      h.camera.lookAt(h.controls.target);
      h.controls.update();
      return {
        position: h.camera.position.toArray(),
        up: h.camera.up.toArray(),
        target: h.controls.target.toArray(),
      };
    });

    await page.click(".cad-crumb-step");
    await page.waitForFunction(
      (wanted) => window.__hsm?.mountedStepFile === wanted && window.__hsm.currentGroup,
      { timeout: 30_000 },
      assembly,
    );

    const returned = await page.evaluate(() => {
      const h = window.__hsm;
      const components = [...new Set(h.currentGroup.children
        .filter((c) => c.isMesh && c.userData?.side === "front")
        .map((c) => c.name))];
      return {
        position: h.camera.position.toArray(),
        up: h.camera.up.toArray(),
        target: h.controls.target.toArray(),
        hasBackTop: components.includes("enclosure-back-top"),
        componentCount: components.length,
      };
    });
    assert.deepEqual(returned.position, beforeReturn.position, "camera position moved on return");
    assert.deepEqual(returned.up, beforeReturn.up, "camera roll moved on return");
    assert.deepEqual(returned.target, beforeReturn.target, "orbit focus moved on return");
    assert.ok(returned.hasBackTop);
    assert.ok(returned.componentCount > 1, "the larger assembly did not return around back-top");
  } finally {
    await page.evaluate(async (files) => {
      // Let scene.js's trailing 250 ms control-change save land first, then
      // remove the views this test deliberately writes.
      await new Promise((resolve) => setTimeout(resolve, 350));
      for (const file of files) localStorage.removeItem(`step-camera:${file}`);
      localStorage.removeItem("step-component-pick");
    }, [assembly, part]).catch(() => {});
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
    await settled(page);

    // Look through the open front below the ceiling, keeping the model centre
    // as the orbit target. Pick a visible rear-wall patch beyond that target.
    const before = await page.evaluate(() => {
      const h = window.__hsm;
      const box = new h.THREE.Box3().setFromObject(h.currentGroup);
      const center = box.getCenter(new h.THREE.Vector3());
      h.controls.target.copy(center);
      h.camera.up.set(0, 0, 1);
      h.camera.position.set(center.x, box.min.y - (box.max.y - box.min.y), center.z);
      h.camera.lookAt(center);
      h.controls.update();
      h.camera.updateMatrixWorld();
      const ndc = new h.THREE.Vector2();
      const ray = new h.THREE.Raycaster();
      const rect = h.renderer.domElement.getBoundingClientRect();
      let hit, client;
      for (const point of [[0.12, 0.08], [-0.12, 0.08], [0.12, -0.08], [-0.12, -0.08], [0, 0]]) {
        // The wheel arrives on a whole pixel, and the zoom pins the surface under
        // that pixel, so the picked point is cast through the same one.
        client = [Math.round(rect.left + (point[0] + 1) * rect.width / 2),
          Math.round(rect.top + (1 - point[1]) * rect.height / 2)];
        ndc.set(((client[0] - rect.left) / rect.width) * 2 - 1, -((client[1] - rect.top) / rect.height) * 2 + 1);
        ray.setFromCamera(ndc, h.camera);
        const candidate = ray.intersectObject(h.currentGroup, true)
          .find((x) => x.face && x.object.isMesh && x.object.visible);
        if (candidate?.point.y > center.y + 100 && Math.abs(candidate.face.normal.y) > 0.99) {
          hit = candidate;
          break;
        }
      }
      if (!hit) return null;
      return {
        point: hit.point.toArray(),
        center: center.toArray(),
        target: h.controls.target.toArray(),
        pointTargetDistance: hit.point.distanceTo(h.controls.target),
        client,
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
    await page.evaluate(async (file) => {
      await new Promise((resolve) => setTimeout(resolve, 350));
      localStorage.removeItem(`step-camera:${file}`);
    }, file).catch(() => {});
    await page.close().catch(() => {});
  }
});

test("/3d zoom crosses a picked surface instead of stalling against it", async () => {
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
    await settled(page);

    // The centre ray from the default framing lands on the model's nearest
    // surface. Wheel toward it until the camera stands on its far side.
    const before = await page.evaluate(() => {
      const h = window.__hsm;
      const ray = new h.THREE.Raycaster();
      ray.setFromCamera(new h.THREE.Vector2(0, 0), h.camera);
      const hit = ray.intersectObject(h.currentGroup, true)
        .find((x) => x.face && x.object.isMesh && x.object.visible);
      if (!hit) return null;
      const rect = h.renderer.domElement.getBoundingClientRect();
      const forward = h.camera.getWorldDirection(new h.THREE.Vector3());
      return {
        point: hit.point.toArray(),
        forward: forward.toArray(),
        client: [rect.left + rect.width / 2, rect.top + rect.height / 2],
        beyond: hit.point.clone().sub(h.camera.position).dot(forward),
      };
    });
    assert.ok(before && before.beyond > 0, "the centre ray should hit a surface ahead of the camera");

    await page.mouse.move(...before.client);
    let travelled = -before.beyond;
    for (let i = 0; i < 40 && !(travelled > 1); i++) {
      await page.mouse.wheel({ deltaY: -300 });
      await new Promise((resolve) => setTimeout(resolve, 150));
      travelled = await page.evaluate(({ point, forward }) => {
        const h = window.__hsm;
        return h.camera.position.clone().sub(new h.THREE.Vector3(...point))
          .dot(new h.THREE.Vector3(...forward));
      }, before);
    }
    assert.ok(travelled > 1,
      `camera should pass the picked surface's plane; stalled ${(-travelled).toFixed(2)}mm short`);
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d a short counter-scroll reverses on its first frame and settles there", async () => {
  const page = await browser.newPage();
  const file = "printed-parts/enclosure/enclosure/enclosure-back-top.step";
  try {
    await page.goto(`${baseUrl}/3d#step:${encodeURIComponent(file)}`, { waitUntil: "domcontentloaded" });
    await page.waitForFunction(file => window.__hsm?.mountedStepFile === file, {}, file);
    await settled(page);
    const movement = await page.evaluate(async () => {
      const { camera, renderer, THREE } = window.__hsm;
      const canvas = renderer.domElement, rect = canvas.getBoundingClientRect();
      const forward = camera.getWorldDirection(new THREE.Vector3());
      const initial = camera.position.clone();
      const wheel = deltaY => canvas.dispatchEvent(new WheelEvent("wheel", {
        cancelable: true, clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2, deltaY,
      }));
      const next = () => new Promise(requestAnimationFrame);
      wheel(-65);
      await next();
      const inward = camera.position.clone();
      // The faster leg has not painted when the counter-scroll arrives.
      wheel(-30); wheel(3);
      await next();
      const reversed = camera.position.clone();
      await next(); await next();
      return {
        inward: inward.clone().sub(initial).dot(forward),
        reversed: reversed.clone().sub(inward).dot(forward),
        coast: camera.position.distanceTo(reversed),
      };
    });
    assert.ok(movement.inward > 0 && movement.reversed < 0, JSON.stringify(movement));
    assert.ok(Math.abs(movement.reversed) < movement.inward && movement.coast < 1e-7, JSON.stringify(movement));
  } finally { await page.close(); }
});
