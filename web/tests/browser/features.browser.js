// On-demand browser checks follow component navigation through assemblies and named features.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const file = process.env.HSM_FEATURE_BROWSER_FILE || "printed-parts/enclosure/enclosure/enclosure-back-top.step";
const key = "enclosure-back-top::wago-h-well";

test("feature links and component drill-down use the same exported identity on desktop and mobile", async () => {
  const { server } = process.env.HSM_FEATURE_BROWSER_BASE ? {} : await start({ port: 0 });
  const origin = process.env.HSM_FEATURE_BROWSER_BASE || `http://127.0.0.1:${server.address().port}`;
  const output = process.env.HSM_FEATURE_BROWSER_OUTPUT;
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  try {
    for (const viewport of [{ width: 1280, height: 960 }, { width: 390, height: 844, isMobile: true, hasTouch: true }]) {
      const page = await browser.newPage();
      const errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.setViewport(viewport);
      if (!process.env.HSM_FEATURE_BROWSER_BASE) {
        await page.setRequestInterception(true);
        page.on("request", request => request.url().endsWith("/api/objects")
          ? request.respond({ status: 200, contentType: "application/json", body: '{"objects":{}}' }) : request.continue());
      }
      await page.goto(`${origin}/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent(`feature: ${key}`)}`);
      await page.waitForFunction(() => window.__hsm?.currentGroup && !window.__hsm.currentGroup.userData.sceneLoading
        && window.__hsm.scene.getObjectByName("pick-find")?.children.some(child => child.isMesh), { timeout: 30000 }).catch(async error => {
          const state = await page.evaluate(() => ({ file: window.__hsm?.mountedStepFile,
            features: window.__hsm?.currentGroup?.children.flatMap(m => m.userData.features || []).map(f => f.id),
            status: document.querySelector(".pick-find-status")?.textContent,
            loading: document.querySelector(".cad-loading")?.textContent }));
          throw new Error(`${error.message}: ${JSON.stringify({ state, errors })}`);
        });
      if (file==='manifold-layout/enclosure-assembly.step') {
        await page.evaluate(async()=>{
          const {state}=await import('/js/viewer/state.js');
          const picker=await import('/js/viewer/component-picker.js');
          picker.clearComponentPicker();
          state.hiddenComponents=new Set(['enclosure-back-bottom','enclosure-front-bottom','cold-core/foam-shell']);
          picker.applyHiddenComponents();
        });
        assert.equal(await page.$eval('.component-panel',el=>/\bholds\b/i.test(el.innerText)),false);
        assert.equal(await page.$$eval('.component-hidden-row',rows=>rows.length),3);
        if(output) {
          fs.mkdirSync(output,{recursive:true});
          await page.screenshot({path:path.join(output,`${viewport.width}-hidden.png`)});
        }
        await page.evaluate(async()=>{
          const {state}=await import('/js/viewer/state.js');
          state.hiddenComponents.clear();
          (await import('/js/viewer/component-picker.js')).applyHiddenComponents();
        });
      }
      const linked = await page.evaluate(async key => {
        const { sceneFeature } = await import("/js/viewer/features.js");
        const { selectComponent, setComponentPickEnabled } = await import("/js/viewer/component-picker.js");
        const feature = sceneFeature(key);
        setComponentPickEnabled(true); selectComponent("enclosure-back-top");
        return { id: feature?.id, source: feature?.source, count: feature?.triangles.reduce((n,[a,b])=>n+b-a+1,0) };
      }, key);
      assert.equal(linked.id, "wago-h-well"); assert.ok(linked.count > 0);
      assert.equal(await page.$('.component-explore'),null);
      const point = () => page.evaluate(async key => {
        const { sceneFeature } = await import("/js/viewer/features.js");
        const { THREE, camera, controls, renderer, scene, currentGroup } = window.__hsm;
        const feature = sceneFeature(key), mesh = feature.meshes[0];
        for (const other of currentGroup.children) if (other.isMesh && other.name !== mesh.name) other.visible=false;
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
      const pick = async () => page.evaluate(({x,y}) => {
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
      },await point());
      if (file==='manifold-layout/enclosure-assembly.step') {
        assert.equal((await pick()).feature,undefined);
        await page.click('.component-actions .component-open');
        await page.waitForFunction(file=>window.__hsm.mountedStepFile!==file
          && !window.__hsm.currentGroup.userData.sceneLoading,{timeout:30000},file);
      }
      assert.equal(await page.$eval('.component-panel',el=>/\bholds\b/i.test(el.innerText)),false);
      assert.equal((await pick()).feature,'wago-h-well');
      assert.equal(await page.$('.component-explore'),null);
      assert.match(await page.$eval(".component-panel .edge-panel-file", el => el.textContent), /connector well/i);
      assert.ok(await page.$eval('.component-held-here',el=>el.getBoundingClientRect().width>80));
      assert.equal(await page.$eval(".component-copy", el => el.title), "Copy feature link");
      await page.evaluate(async () => (await import('/js/viewer/component-picker.js')).clearComponentPicker({preserve:true}));
      assert.match(await page.$eval(".component-panel .edge-panel-file", el => el.textContent), /connector well/i);
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>window.__copiedFeatureLink=text}}));
      await page.click('.component-copy');
      assert.match(await page.evaluate(()=>window.__copiedFeatureLink),/find=feature%3A%20enclosure-back-top%3A%3Awago-h-well/);
      assert.deepEqual(errors, []);
      const catalog = await page.evaluate(async file => (await (await fetch(`/api/features?file=${encodeURIComponent(file)}`)).json()).features, file);
      assert.ok(catalog.some(feature => feature.key === key));
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (output) {
        fs.mkdirSync(output,{recursive:true});
        await page.screenshot({path:path.join(output,`${viewport.width}.png`)});
        const mounted=await page.evaluate(()=>({file:window.__hsm.mountedStepFile,
          revision:window.__hsm.currentGroup.userData.sharedHead?.src,
          nodes:window.__hsm.currentGroup.userData.sharedHead?.meshes.filter(n=>n.name==='enclosure-back-top'),
          parts:window.__hsm.currentGroup.children.filter(m=>m.userData.side==='front' && m.name==='enclosure-back-top')
            .map(m=>({name:m.name,features:m.userData.features.map(f=>f.id)}))}));
        fs.writeFileSync(path.join(output,`${viewport.width}.json`),JSON.stringify({origin,viewport,linked,mounted,feature_count:catalog.length,errors},null,2)+'\n');
      }
      if (file==='manifold-layout/enclosure-assembly.step') {
        await page.goBack();
        await page.waitForFunction(file=>window.__hsm.mountedStepFile===file
          && !window.__hsm.currentGroup.userData.sceneLoading,{timeout:30000},file);
        assert.equal((await pick()).feature,undefined);
        await page.evaluate(async () => {
          for (const mesh of window.__hsm.currentGroup.children) if(mesh.isMesh) mesh.visible=true;
          (await import('/js/viewer/component-picker.js')).applyHiddenComponents();
        });
        if (await page.$eval('.materials-toggle', button => button.getAttribute('aria-expanded') !== 'true'))
          await page.click('.materials-toggle');
        await page.type('.material-panel .material-search input','HSM-0047');
        await page.waitForFunction(()=>['relay-1','relay-2'].every(name=>[...document.querySelectorAll('.material-panel .material-search-results a')]
          .some(a=>decodeURIComponent(a.href).includes(`instance=${name}`))));
        assert.equal(await page.$$eval('.material-panel .material-search-entry',rows=>rows.length),1);
        await page.waitForSelector('.material-panel .material-search-locations > summary', { visible: true });
        await page.$eval('.material-panel .material-search-locations > summary', node => node.click());
        const instances=await page.$$eval('.material-panel .material-search-location',links=>links.map(a=>decodeURIComponent(a.href)));
        assert.equal(new Set(instances).size,2);
        await page.evaluate(()=>[...document.querySelectorAll('.material-panel .material-search-results a')]
          .find(a=>decodeURIComponent(a.href).includes('instance=relay-2')).click());
        await page.waitForFunction(()=>document.querySelector('.component-panel .component-identity')?.textContent.includes('relay-2'));
        assert.match(await page.$eval('.component-panel .component-identity',el=>el.textContent),/relay-2/);
        if (await page.$eval('.materials-toggle', button => button.getAttribute('aria-expanded') !== 'true'))
          await page.click('.materials-toggle');
        const search=await page.$('.material-panel .material-search input');
        await search.type(key);
        await page.waitForFunction(key=>[...document.querySelectorAll('.material-panel .material-search-results a')]
          .some(a=>decodeURIComponent(a.href).includes(`find=feature: ${key}`)),{},key);
        if(output) fs.writeFileSync(path.join(output,`${viewport.width}-navigation.json`),JSON.stringify({instances,feature_search:key,errors},null,2)+'\n');
      }
      assert.deepEqual(errors,[]);
      await page.close();
    }
    if (file==='manifold-layout/enclosure-assembly.step') {
      const page=await browser.newPage();
      await page.goto(`${origin}/3d`);
      await page.waitForSelector('.material-search input');
      await page.type('.material-search input',key);
      await page.waitForFunction(key=>[...document.querySelectorAll('.material-search-results a')]
        .some(a=>decodeURIComponent(a.href).includes(`find=feature: ${key}`)),{},key);
      assert.ok(await page.evaluate(()=>!window.__hsm.currentGroup));
      await page.close();
    }
  } finally { await closeBrowser(browser); if(server) await closeServer(server); }
});
