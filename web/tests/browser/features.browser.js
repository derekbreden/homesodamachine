// On-demand browser checks exercise feature links and scoped picking on the exported quadrant.
import { test } from "node:test";
import assert from "node:assert/strict";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const file = "printed-parts/enclosure/enclosure/enclosure-back-top.step";
const key = "enclosure-back-top::wago-h-well";

test("feature links and component drill-down use the same exported identity on desktop and mobile", async () => {
  const { server } = await start({ dev: false, port: 0 });
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  try {
    for (const viewport of [{ width: 1280, height: 960 }, { width: 390, height: 844, isMobile: true, hasTouch: true }]) {
      const page = await browser.newPage();
      const errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.setViewport(viewport);
      await page.setRequestInterception(true);
      page.on("request", request => request.url().endsWith("/api/objects")
        ? request.respond({ status: 200, contentType: "application/json", body: '{"objects":{}}' }) : request.continue());
      await page.goto(`http://127.0.0.1:${server.address().port}/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent(`feature: ${key}`)}`);
      await page.waitForFunction(() => window.__hsm?.currentGroup && !window.__hsm.currentGroup.userData.sceneLoading
        && window.__hsm.scene.getObjectByName("pick-find")?.children.some(child => child.isMesh), { timeout: 30000 }).catch(async error => {
          const state = await page.evaluate(() => ({ file: window.__hsm?.mountedStepFile,
            features: window.__hsm?.currentGroup?.children.flatMap(m => m.userData.features || []).map(f => f.id),
            status: document.querySelector(".pick-find-status")?.textContent,
            loading: document.querySelector(".cad-loading")?.textContent }));
          throw new Error(`${error.message}: ${JSON.stringify({ state, errors })}`);
        });
      const linked = await page.evaluate(async key => {
        const { sceneFeature } = await import("/js/viewer/features.js");
        const { selectComponent, setComponentPickEnabled } = await import("/js/viewer/component-picker.js");
        const feature = sceneFeature(key);
        setComponentPickEnabled(true); selectComponent("enclosure-back-top");
        return { id: feature?.id, source: feature?.source, count: feature?.triangles.reduce((n,[a,b])=>n+b-a+1,0),
          available: document.querySelector(".component-explore")?.textContent };
      }, key);
      assert.equal(linked.id, "wago-h-well"); assert.ok(linked.count > 0);
      assert.equal(linked.available, "Explore features");
      const point = await page.evaluate(async key => {
        const { sceneFeature } = await import("/js/viewer/features.js");
        const { THREE, camera, controls, renderer, scene, currentGroup } = window.__hsm;
        const feature = sceneFeature(key), mesh = feature.meshes[0];
        const indices = mesh.geometry.index.array, positions = mesh.geometry.getAttribute("position");
        const ray = new THREE.Raycaster(), p = new THREE.Vector3(), q = new THREE.Vector3();
        mesh.updateWorldMatrix(true, false);
        const bounds = new THREE.Box3();
        for (const [a,b] of feature.triangles) for (let i=a*3;i<(b+1)*3;i++)
          bounds.expandByPoint(q.fromBufferAttribute(positions,indices[i]).applyMatrix4(mesh.matrixWorld));
        bounds.getCenter(controls.target);
        camera.position.copy(controls.target).add(new THREE.Vector3(80,0,0));
        camera.up.set(0,0,1); camera.lookAt(controls.target); camera.updateMatrixWorld();
        controls.update(); renderer.render(scene,camera);
        const rect = renderer.domElement.getBoundingClientRect();
        for (const [a,b] of feature.triangles) for (let i=a;i<=b;i++) {
          p.set(0,0,0);
          for (let j=0;j<3;j++) p.add(q.fromBufferAttribute(positions,indices[i*3+j]));
          p.divideScalar(3).applyMatrix4(mesh.matrixWorld).project(camera);
          if (Math.abs(p.x) >= 0.95 || Math.abs(p.y) >= 0.95) continue;
          ray.setFromCamera(p,camera);
          const hit = ray.intersectObjects(currentGroup.children.filter(m=>m.userData.side==='front' && m.visible),false)[0];
          if (hit?.object === mesh && feature.triangles.some(([a,b])=>a<=hit.faceIndex && hit.faceIndex<=b))
            return {x:rect.left+(p.x+1)*rect.width/2,y:rect.top+(1-p.y)*rect.height/2};
        }
        throw new Error('No visible feature triangle for picking');
      },key);
      const pick = () => page.evaluate(({x,y}) => {
        let detail;
        const listener=e=>detail=e.detail;
        // Dispatch on the canvas so the open companion panel does not intercept the geometry test.
        const canvas=window.__hsm.renderer.domElement;
        return import('/contracts/client-events.js').then(({HSM_EVENTS})=>{
          window.addEventListener(HSM_EVENTS.MATERIAL_PICKED,listener,{once:true});
          canvas.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,bubbles:true,pointerId:1}));
          canvas.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,bubbles:true,pointerId:1}));
          return detail;
        });
      },point);
      assert.equal((await pick()).feature,undefined);
      await page.click(".component-explore");
      const rows = await page.$$eval(".component-holds-row", rows => rows.map(row => row.title));
      assert.ok(rows.includes(key));
      assert.equal((await pick()).feature,'wago-h-well');
      await page.evaluate(async () => (await import('/js/viewer/component-picker.js')).selectComponent('enclosure-back-top'));
      await page.evaluate(key => [...document.querySelectorAll(".component-holds-row")].find(row => row.title === key).click(), key);
      assert.match(await page.$eval(".component-panel .edge-panel-file", el => el.textContent), /connector well/i);
      assert.equal(await page.$eval(".component-copy", el => el.textContent), "Copy feature link");
      await page.evaluate(async () => (await import('/js/viewer/component-picker.js')).clearComponentPicker({preserve:true}));
      assert.match(await page.$eval(".component-panel .edge-panel-file", el => el.textContent), /connector well/i);
      assert.deepEqual(errors, []);
      const catalog = await page.evaluate(async file => (await (await fetch(`/api/features?file=${encodeURIComponent(file)}`)).json()).features, file);
      assert.ok(catalog.some(feature => feature.key === key));
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.close();
    }
  } finally { await closeBrowser(browser); await closeServer(server); }
});
