// A still-camera pick changes only the component's pixels while dense models retain their moving view.
import { test } from "node:test";
import assert from "node:assert/strict";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

test("stationary component selection leaves unrelated surfaces sharp on every drawn frame", async t => {
  const { server } = await start({ port: 0 });
  const browser = await launchBrowser({ headless: true });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 400, height: 360, deviceScaleFactor: 2, hasTouch: true });
    await page.goto(`http://127.0.0.1:${server.address().port}/parts`);
    const target = await page.evaluate(async () => {
      const THREE = await import("three");
      const { scene, camera, controls, renderer, resizeRenderer, startAnimate } = await import("/js/viewer/scene.js");
      const { state } = await import("/js/viewer/state.js");
      const { setComponentPickEnabled } = await import("/js/viewer/component-picker.js");
      const { prepareMotionIndices } = await import("/js/viewer/motion-surfaces.js");
      const workspace = document.createElement("div");
      workspace.className = "cad-workspace";
      workspace.style.cssText = "position:fixed;inset:0;z-index:9999;display:block";
      workspace.innerHTML = '<header class="cad-workspace-header" style="display:none"></header><div class="cad-wrapper" style="position:absolute;inset:0"></div>';
      document.body.append(workspace);
      const host = workspace.lastElementChild, canvas = renderer.domElement;
      host.append(canvas);
      state.currentCadWrapper = host;
      state.mountedDetail = { type: "step", file: "selection-test.step" };
      const group = new THREE.Group();
      state.currentGroup = group;
      scene.add(group);
      function part(name, geo, color, x, y, z) {
        const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color }));
        mesh.userData.side = "front";
        mesh.name = name;
        mesh.position.set(x, y, z);
        group.add(mesh);
        return mesh;
      }
      const boxes = new THREE.BoxGeometry(.9, .9, .2);
      const front = part("Front", boxes, 0xcc5959, -1, -.4, .3);
      part("Behind", boxes, 0x38a968, -1, -.4, -.3);
      const sphere = new THREE.SphereGeometry(.14, 96, 48);
      sphere.deleteAttribute("uv");
      sphere.setIndex(new THREE.BufferAttribute(Uint32Array.from(sphere.index.array), 1));
      sphere.computeBoundingBox();
      sphere.computeBoundingSphere();
      await prepareMotionIndices([{ attributes: sphere.attributes, index: sphere.index }], undefined, true);
      let otherDraws = 0;
      for (let col = 0; col < 6; col++) {
        for (let row = 0; row < 8; row++) {
          const ball = part(`Ball ${col} ${row}`, sphere, 0xa0abc1, .3 + col * .32, (row - 3) * .32, 0);
          ball.onBeforeRender = () => { otherDraws++; };
        }
      }
      camera.position.set(0, 0, 5);
      camera.up.set(0, 1, 0);
      controls.target.set(0, 0, 0);
      controls.update();
      resizeRenderer();
      setComponentPickEnabled(true);

      // Sample the displayed buffer at the end of the drawing task, after all its passes.
      const copy = document.createElement("canvas");
      copy.width = canvas.width;
      copy.height = canvas.height;
      const point = front.position.clone().project(camera);
      const targetX = (1 + point.x) / 2, targetY = (1 - point.y) / 2;
      const ctx = copy.getContext("2d", { willReadFrequently: true });
      const probe = window.selectionProbe = { frames: [], lastDraw: 0, nativeWidth: canvas.width };
      let reference, lastCrop, originalColor, pickedColor, queued = false;
      const render = renderer.render.bind(renderer);
      renderer.render = (...args) => {
        render(...args);
        if (queued || renderer.getRenderTarget()) return;
        queued = true;
        queueMicrotask(() => {
          queued = false;
          ctx.drawImage(canvas, 0, 0, copy.width, copy.height);
          lastCrop = ctx.getImageData(copy.width / 2, 0, copy.width / 2, copy.height).data;
          pickedColor = ctx.getImageData(copy.width * targetX, copy.height * targetY, 1, 1).data;
          let maxDelta = 0;
          if (reference) {
            for (let i = 0; i < lastCrop.length; i++) maxDelta = Math.max(maxDelta, Math.abs(reference[i] - lastCrop[i]));
          }
          const highlight = originalColor && pickedColor.some((channel, i) => Math.abs(channel - originalColor[i]) > 1);
          probe.frames.push({ width: canvas.width, maxDelta, highlight, otherDraws, distance: camera.position.distanceTo(controls.target) });
          probe.lastDraw = performance.now();
        });
      };
      probe.record = () => {
        if (new Set(lastCrop).size < 16) throw Error("The area beside the picked component must contain visible detail");
        reference = lastCrop;
        originalColor = pickedColor;
        otherDraws = 0;
        probe.frames = [];
      };
      startAnimate();
      const rect = canvas.getBoundingClientRect();
      return { x: rect.left + targetX * rect.width, y: rect.top + targetY * rect.height };
    });
    const settled = () => page.waitForFunction(() => {
      const probe = window.selectionProbe;
      return probe.frames.length && performance.now() - probe.lastDraw > 400;
    });
    await settled();
    await page.evaluate(() => window.selectionProbe.record());
    await page.touchscreen.touchStart(target.x, target.y);
    await page.evaluate(() => new Promise(requestAnimationFrame));
    await page.touchscreen.touchEnd();
    await page.waitForSelector('.component-hide[title="Hide Front"]', { visible: true });
    await settled();
    const selection = await page.evaluate(() => window.selectionProbe.frames);
    const nativeWidth = await page.evaluate(() => window.selectionProbe.nativeWidth);

    await page.click(".component-hide");
    await page.waitForSelector('.component-show[aria-label="Show Front"]');
    await page.touchscreen.tap(target.x, target.y);
    await page.waitForSelector('.component-hide[title="Hide Behind"]', { visible: true });
    await settled();
    const distance = await page.evaluate(() => {
      const probe = window.selectionProbe;
      const last = probe.frames.at(-1);
      probe.frames = [];
      return last.distance;
    });
    await page.mouse.move(target.x, target.y);
    await page.mouse.wheel({ deltaY: -40 });
    await page.waitForFunction((width, previous) =>
      window.selectionProbe.frames.some(frame => frame.distance !== previous && frame.width < width), {}, nativeWidth, distance);
    const widths = [...new Set(selection.map(frame => frame.width))];
    const maxDelta = Math.max(...selection.map(frame => frame.maxDelta));
    t.diagnostic(`Selection widths ${widths}, maximum neighboring pixel difference ${maxDelta}, neighboring draws ${selection.at(-1).otherDraws}`);
    assert.ok(selection.some(frame => frame.highlight), "The tap must visibly highlight the selected surface");
    assert.ok(widths.every(width => width === nativeWidth) && maxDelta <= 1,
      `Stationary tap drew widths ${widths} at native width ${nativeWidth}, changing unselected detail by ${maxDelta} color levels`);
    assert.equal(selection.at(-1).otherDraws, 0, "A settled selection reuses the unchanged assembly");
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
  }
});
