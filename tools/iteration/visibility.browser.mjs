// This on-demand browser fixture verifies draw eligibility with the viewer's actual Three.js camera and renderer.
import test from "node:test";
import assert from "node:assert/strict";
import { launchBrowser, closeBrowser } from "../render/browser.js";
import { observeExpectedFrame, partKey } from "./measure.mjs";

test("draw eligibility excludes hidden, transparent, off-camera and depth-clipped targets while preserving partial updates", { timeout: 120000 }, async () => {
  let browser;
  try {
    browser = await launchBrowser();
    const page = await browser.newPage();
    await page.goto("https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step", { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => window.__hsm?.THREE && window.__hsm.renderer.domElement.getBoundingClientRect().width > 0, { timeout: 60000 });
    const nodes = ["a", "b"].map((name) => ({ name, asset: `new-${name}`, entries: [{ name, color: [0, 0, 0] }], transform: null }));
    const target = { revision: "fixture", parts: nodes.map((node) => ({ name: node.name, asset: node.asset, key: partKey(node) })) };
    await page.evaluate((nodes) => {
      const original = window.__hsm, { THREE, renderer } = original;
      const scene = new THREE.Scene(), group = new THREE.Group(), holder = new THREE.Group();
      scene.add(group); group.add(holder);
      const camera = new THREE.PerspectiveCamera(45, 1, 1, 100);
      camera.position.set(0, 0, 10); camera.lookAt(0, 0, 0); camera.updateProjectionMatrix();
      const solids = nodes.map((node, i) => {
        const solid = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: "white" }));
        solid.position.x = i ? 1 : -1; holder.add(solid); return solid;
      });
      group.userData.sharedHead = { src: "fixture", meshes: nodes };
      group.userData.parts = new Map(nodes.map((node, i) => [node.name, { key: "old", solids: [solids[i]] }]));
      window.__iterationFixture = { original, originalRender: renderer.render, renderer, scene, group, holder, camera, solids, frames: [] };
      window.__hsmIterationFrame = async (frame) => window.__iterationFixture.frames.push(frame);
      window.__hsm = { THREE, renderer, scene, camera, currentGroup: group };
    }, nodes);
    const observing = page.evaluate(observeExpectedFrame, target, 15000);
    await page.waitForFunction(() => window.__hsm.renderer.render !== window.__iterationFixture.originalRender);
    const checks = await page.evaluate((target) => {
      const f = window.__iterationFixture, { renderer, scene, camera, group, holder, solids, frames } = f;
      const checks = {};
      const draw = () => renderer.render(scene, camera);
      draw(); checks.oldGpu = frames.length;
      target.parts.forEach((part) => { group.userData.parts.get(part.name).key = part.key; });
      holder.visible = false; draw(); checks.hiddenAncestor = frames.length; holder.visible = true;
      solids.forEach((solid) => { solid.position.x += 1000; }); draw(); checks.outsideFrustum = frames.length;
      solids.forEach((solid) => { solid.position.x -= 1000; solid.material.opacity = 0; }); draw(); checks.transparent = frames.length;
      solids.forEach((solid) => { solid.material.opacity = 1; });
      camera.far = 9.9; camera.updateProjectionMatrix(); draw(); checks.partialFarClip = frames.length;
      camera.far = 100; camera.near = 10.1; camera.updateProjectionMatrix(); draw(); checks.partialNearClip = frames.length;
      camera.near = 1; camera.updateProjectionMatrix();
      renderer.clippingPlanes = [new window.__hsm.THREE.Plane(new window.__hsm.THREE.Vector3(1, 0, 0), -10)];
      draw(); checks.globalClipping = frames.length; renderer.clippingPlanes = [];
      renderer.localClippingEnabled = true;
      solids.forEach((solid) => { solid.material.clippingPlanes = [new window.__hsm.THREE.Plane(new window.__hsm.THREE.Vector3(1, 0, 0), -10)]; });
      draw(); checks.materialClipping = frames.length;
      solids.forEach((solid) => { solid.material.clippingPlanes = []; }); renderer.localClippingEnabled = false;
      solids[1].visible = false; draw(); checks.first = frames.map((frame) => frame.matched);
      solids[0].visible = false; solids[1].visible = true; draw(); checks.separate = frames.map((frame) => frame.matched);
      solids[0].visible = true; draw(); checks.all = frames.map((frame) => frame.matched);
      return checks;
    }, target);
    const result = await observing;
    for (const name of ["oldGpu", "hiddenAncestor", "outsideFrustum", "transparent", "partialFarClip", "partialNearClip", "globalClipping", "materialClipping"]) assert.equal(checks[name], 0, name);
    assert.deepEqual(checks.first, [["a"]]);
    assert.deepEqual(checks.separate, [["a"], ["b"]]);
    assert.deepEqual(checks.all, [["a"], ["b"], ["a", "b"]]);
    assert.equal(result.frames.length, 3);
    assert.match(result.frames[0].eligibility, /occlusion is not established/);
    assert.equal(await page.evaluate(() => window.__hsm.renderer.render === window.__iterationFixture.originalRender), true);
    await page.evaluate(() => {
      const f = window.__iterationFixture;
      for (const solid of f.solids) { solid.geometry.dispose(); solid.material.dispose(); }
      window.__hsm = f.original; delete window.__hsmIterationFrame; delete window.__iterationFixture;
    });
  } finally { await closeBrowser(browser); }
});
