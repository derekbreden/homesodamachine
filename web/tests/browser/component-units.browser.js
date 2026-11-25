// Component navigation checks physical units at assembly depth and bodies inside opened parts.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { start } from "../../server.js";
import { readMeshHeader } from "../../lib/feature-catalog.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const machine = "manifold-layout/enclosure-assembly.step";

async function clickBody(page, body, members) {
  return page.evaluate(async ({ body, members }) => {
    const { state } = await import("/js/viewer/state.js");
    const picker = await import("/js/viewer/component-picker.js");
    const { HSM_EVENTS } = await import("/contracts/client-events.js");
    const { THREE, camera, controls, renderer, scene, currentGroup } = window.__hsm;
    state.hiddenComponents.clear(); state.autoHiddenComponents.clear();
    picker.applyHiddenComponents(); picker.setComponentPickEnabled(true);
    (await import("/js/viewer/xray.js")).setXrayEnabled(false, { persist: false });
    const fronts = currentGroup.children.filter(mesh => mesh.userData?.side === "front");
    for (const mesh of currentGroup.children) if (mesh.isMesh) mesh.visible = members.includes(mesh.name);
    const target = fronts.find(mesh => mesh.name === body);
    if (!target) throw new Error(`Missing body ${body}`);
    const selected = fronts.filter(mesh => members.includes(mesh.name));
    const box = new THREE.Box3(); for (const mesh of selected) box.expandByObject(mesh);
    const center = box.getCenter(new THREE.Vector3()), distance = box.getSize(new THREE.Vector3()).length() * 2;
    const indices = target.geometry.index.array, positions = target.geometry.getAttribute("position");
    const point = new THREE.Vector3(), vertex = new THREE.Vector3(), ray = new THREE.Raycaster();
    let hitPoint;
    for (const direction of [[1,1,1],[-1,-1,-1],[1,-1,1],[-1,1,-1]]) {
      controls.target.copy(center); camera.position.copy(center).addScaledVector(new THREE.Vector3(...direction).normalize(), distance);
      camera.up.set(0,0,1); controls.update(); camera.updateMatrixWorld(); currentGroup.updateMatrixWorld(true);
      const stride = Math.max(1, Math.floor(indices.length / 1800));
      for (let triangle = 0; triangle < indices.length / 3; triangle += stride) {
        point.set(0,0,0);
        for (let j = 0; j < 3; j++) point.add(vertex.fromBufferAttribute(positions,indices[triangle*3+j]));
        point.divideScalar(3).applyMatrix4(target.matrixWorld).project(camera);
        if (Math.abs(point.x) >= 0.95 || Math.abs(point.y) >= 0.95) continue;
        ray.setFromCamera(point,camera);
        if (ray.intersectObjects(selected,false)[0]?.object.name !== body) continue;
        const rect = renderer.domElement.getBoundingClientRect();
        hitPoint = { clientX: rect.left+(point.x+1)*rect.width/2, clientY: rect.top+(1-point.y)*rect.height/2 };
        break;
      }
      if (hitPoint) break;
    }
    if (!hitPoint) throw new Error(`No visible surface of ${body}`);
    const canvas = renderer.domElement;
    canvas.dispatchEvent(new PointerEvent("pointermove", { ...hitPoint, bubbles: true, buttons: 0 }));
    await new Promise(requestAnimationFrame);
    const marks = scene.getObjectByName("component-picker");
    const fills = group => group.children.filter(child => child.isMesh);
    const hover = fills(marks.children[1]).length;
    let picked;
    window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, event => { picked = event.detail; }, { once: true });
    canvas.dispatchEvent(new PointerEvent("pointerdown", { ...hitPoint, bubbles: true, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent("pointerup", { ...hitPoint, bubbles: true, pointerId: 1 }));
    renderer.render(scene,camera);
    const highlight = fills(marks.children[0]);
    return { picked, hover, highlight: highlight.length,
      borrowed: highlight.every(fill => selected.some(mesh => mesh.geometry === fill.geometry)), expected: selected.length };
  }, { body, members });
}

test("assembly clicks and hiding keep physical copies together; opening exposes their internal bodies", async () => {
  const base = process.env.HSM_COMPONENT_BROWSER_BASE;
  const { server } = base ? {} : await start({ port: 0 });
  const origin = base || `http://127.0.0.1:${server.address().port}`;
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  const output = process.env.HSM_COMPONENT_BROWSER_OUTPUT;
  try {
    const page = await browser.newPage(), errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.setViewport(process.env.HSM_COMPONENT_BROWSER_MOBILE === "1"
      ? { width: 390, height: 844, isMobile: true, hasTouch: true } : { width: 1280, height: 960 });
    let heldRequest, lateBody;
    if (!base) {
      const head = readMeshHeader(fileURLToPath(new URL(`../../../hardware/${machine}.mesh`, import.meta.url)));
      const late = head.meshes.find(node => node.name === "wire-J11-AOUT");
      lateBody = late.name;
      let hold = true;
      let take;
      heldRequest = new Promise(resolve => { take = resolve; });
      await page.setRequestInterception(true);
      page.on("request", request => {
        if (request.url().endsWith("/api/objects"))
          return request.respond({ status: 200, contentType: "application/json", body: '{"objects":{}}' });
        if (hold && request.url().endsWith("/scene-meshes/" + late.asset)) {
          hold = false; take(request); return;
        }
        return request.continue();
      });
    }
    const loaded = file => page.waitForFunction(file => window.__hsm?.mountedStepFile === file
      && !window.__hsm.currentGroup?.userData.sceneLoading, { timeout: 90000 }, file);
    await page.goto(`${origin}/3d#step:${encodeURIComponent(machine)}`, { waitUntil: "domcontentloaded" });
    if (heldRequest) {
      await page.waitForFunction(file => window.__hsm?.mountedStepFile === file
        && window.__hsm.currentGroup.children.some(mesh => mesh.name === "wire-AC1-L"), {}, machine);
      const delayed = await Promise.race([heldRequest, new Promise((_, reject) =>
        setTimeout(() => reject(new Error("The late wire was never requested")), 15000).unref())]);
      await page.evaluate(async lateBody => {
        const group = window.__hsm.currentGroup;
        const picker = await import("/js/viewer/component-picker.js");
        picker.setComponentPickEnabled(true); picker.selectComponent("wire-AC1-L");
        document.querySelector(".component-hide").click();
        group.addEventListener("childadded", ({child}) => {
          if (child.name === lateBody) window.__wireVisibleOnArrival = child.visible;
        });
      }, lateBody);
      await delayed.continue();
    }
    await loaded(machine);
    if (heldRequest) {
      assert.equal(await page.evaluate(() => window.__wireVisibleOnArrival), false);
      await page.click('.component-show[aria-label="Show Wiring"]');
    }
    const units = await page.evaluate(async () => {
      const { componentUnitsInScene } = await import("/contracts/material-instances.js");
      const { state } = await import("/js/viewer/state.js");
      return componentUnitsInScene(state.materialCatalog, "HSM-0001",
        state.currentGroup.children.filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name));
    });
    const migrated = await page.evaluate(async () => {
      const { state } = await import("/js/viewer/state.js");
      state.hiddenComponents = new Set(["pump-b-head", "pump-b-boss"]);
      (await import("/js/viewer/component-picker.js")).applyHiddenComponents();
      return { hidden: [...state.hiddenComponents], visible: state.currentGroup.children
        .filter(mesh => mesh.userData?.side === "front" && mesh.name.startsWith("pump-b-")).some(mesh => mesh.visible) };
    });
    assert.deepEqual(migrated.hidden,["pump-b-head"]);
    assert.equal(migrated.visible,false);
    assert.equal(await page.$$eval(".component-hidden-row",rows => rows.length),1);
    await page.waitForSelector(".component-show-all", { hidden: true });
    await page.click(".component-hidden-toggle");
    await page.waitForSelector(".component-show-all", { visible: true });
    await page.click(".component-show-all");
    for (const body of ["pump-b-mount", "coil-v-c", "bulkhead-drain-nut", "nameplate-ink"]) {
      const unit = units.find(unit => unit.bodies.includes(body)); assert.ok(unit, body);
      const result = await clickBody(page,body,unit.bodies);
      assert.equal(result.picked.name,unit.name,body);
      assert.equal(result.picked.feature,undefined,body);
      assert.equal(result.hover,result.expected,body);
      assert.equal(result.highlight,result.expected,body);
      assert.equal(result.borrowed,true,body);
      if (output && body === "pump-b-mount") {
        fs.mkdirSync(output,{ recursive: true });
        await page.screenshot({ path: path.join(output,"pump-selection.png") });
      }
      await page.click(".component-hide");
      const hidden = await page.evaluate(({ members }) => {
        const group = window.__hsm.currentGroup;
        return { bodies: group.children.filter(mesh => mesh.userData?.side === "front" && members.includes(mesh.name)).map(mesh => mesh.visible),
          otherPump: group.children.filter(mesh => mesh.userData?.side === "front" && mesh.name.startsWith("pump-a-")).every(mesh => mesh.visible) };
      },{ members: unit.bodies });
      assert.ok(hidden.bodies.every(visible => !visible),body);
      assert.ok(hidden.otherPump,body);
      assert.equal(await page.$$eval(".component-hidden-row", rows => rows.length),1,body);
      assert.ok(await page.$eval(".component-hidden-row .component-show", button =>
        !button.textContent.trim() && /^Show .+/.test(button.getAttribute("aria-label"))), body);
      if (body === "pump-b-mount") {
        await page.waitForFunction(() => {
          const tile = document.querySelector(".component-hidden-thumb canvas");
          if (!tile || tile.hidden) return false;
          const { data } = tile.getContext("2d").getImageData(0, 0, tile.width, tile.height);
          return new Set(new Uint32Array(data.buffer)).size > 5;
        });
      }
      await page.click(".component-hidden-row .component-show");
      assert.ok(await page.evaluate(members => window.__hsm.currentGroup.children
        .filter(mesh => mesh.userData?.side === "front" && members.includes(mesh.name)).every(mesh => mesh.visible),unit.bodies));
    }
    const pump = units.find(unit => unit.bodies.includes("pump-b-mount"));
    await clickBody(page,"pump-b-mount",pump.bodies);
    await page.click(".component-actions .component-open");
    await loaded("reference/kamoer-kphm400/kamoer-kphm400.step");
    const bodies = await page.evaluate(() => [...new Set(window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))]);
    assert.ok(bodies.length > 1);
    const inside = await clickBody(page,bodies[0],[bodies[0]]);
    assert.equal(inside.picked.name,bodies[0]);
    await page.click(".component-hide");
    assert.ok(await page.evaluate(name => window.__hsm.currentGroup.children.some(mesh =>
      mesh.userData?.side === "front" && mesh.name !== name && mesh.visible),bodies[0]));
    await page.goBack(); await loaded(machine);
    const wire = "wire-AC1-L";
    const wiring = await page.evaluate(() => [...new Set(window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front" && /^(wire-|terminal-)/.test(mesh.name)).map(mesh => mesh.name))]);
    assert.ok(wiring.includes(wire) && wiring.includes("terminal-J13"));
    assert.equal((await clickBody(page,wire,[wire])).picked.name,"Wiring");
    await page.click(".component-hide");
    assert.equal(await page.$$eval(".component-hidden-row", rows => rows.length),1);
    assert.ok(await page.$('.component-show[aria-label="Show Wiring"]'));
    const checkWiring = expected => page.evaluate(({ wiring, expected }) => {
      const bodies = window.__hsm.currentGroup.children.filter(mesh => mesh.userData?.side === "front");
      return bodies.filter(mesh => wiring.includes(mesh.name)).every(mesh => mesh.visible === expected)
        && bodies.filter(mesh => /^(wago-|wiring-junction-)/.test(mesh.name)).every(mesh => mesh.visible);
    }, { wiring, expected });
    assert.ok(await checkWiring(false));
    assert.deepEqual(await page.evaluate(file => JSON.parse(localStorage.getItem("step-hidden:"+file)),machine),["Wiring"]);
    await page.click('.component-show[aria-label="Show Wiring"]');
    assert.ok(await checkWiring(true));
    await clickBody(page,wire,[wire]);
    await page.click(".component-actions .component-open");
    await loaded(machine+"?component=Wiring");
    assert.equal(await page.$eval(".component-panel .component-hide", button => button.getClientRects().length), 0);
    assert.equal(await page.evaluate(() => window.__hsm.scene.getObjectByName("component-picker").children[0].children.length), 0);
    assert.deepEqual(await page.evaluate(() => [...new Set(window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))].sort()),wiring.sort());
    assert.equal((await clickBody(page,wire,[wire])).picked.name,wire);
    await page.click(".component-hide");
    assert.ok(await page.evaluate(wire => window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front" && mesh.name !== wire).every(mesh => mesh.visible),wire));
    await page.goBack(); await loaded(machine);
    assert.ok(await checkWiring(true));
    const harness = units.find(unit => unit.name === "terminal-J13"); assert.ok(harness);
    await page.evaluate(async file => (await import("/js/viewer/step-nav.js")).drillTo(file), machine+"?component=terminal-J13");
    await loaded(machine+"?component=terminal-J13");
    assert.deepEqual(await page.evaluate(() => [...new Set(window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))].sort()),[...harness.bodies].sort());
    assert.equal((await clickBody(page,"wire-J13-AM1",["wire-J13-AM1"])).picked.name,"wire-J13-AM1");
    assert.deepEqual(errors,[]);
    if (output) fs.writeFileSync(path.join(output,"navigation.json"),JSON.stringify({ origin, units: units.length, checked: ["pump","valve","bulkhead","nameplate","opened pump","Wiring","opened harness"], errors },null,2)+"\n");
    await page.close();
  } finally { await closeBrowser(browser); if (server) await closeServer(server); }
});
