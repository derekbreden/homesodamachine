// Component navigation checks physical units at assembly depth and bodies inside opened parts.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { start } from "../../server.js";
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
    const hover = scene.getObjectByName("component-picker").children[1].children.length;
    let picked;
    window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, event => { picked = event.detail; }, { once: true });
    canvas.dispatchEvent(new PointerEvent("pointerdown", { ...hitPoint, bubbles: true, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent("pointerup", { ...hitPoint, bubbles: true, pointerId: 1 }));
    renderer.render(scene,camera);
    return { picked, hover, highlight: scene.getObjectByName("component-picker").children[0].children.length,
      expected: new Set(selected.map(mesh => mesh.geometry)).size * 2 };
  }, { body, members });
}

test("assembly clicks and hiding keep physical copies together; opening exposes their internal bodies", async () => {
  const base = process.env.HSM_COMPONENT_BROWSER_BASE;
  const { server } = base ? {} : await start({ dev: false, port: 0 });
  const origin = base || `http://127.0.0.1:${server.address().port}`;
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  const output = process.env.HSM_COMPONENT_BROWSER_OUTPUT;
  try {
    const page = await browser.newPage(), errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.setViewport(process.env.HSM_COMPONENT_BROWSER_MOBILE === "1"
      ? { width: 390, height: 844, isMobile: true, hasTouch: true } : { width: 1280, height: 960 });
    if (!base) {
      await page.setRequestInterception(true);
      page.on("request", request => request.url().endsWith("/api/objects")
        ? request.respond({ status: 200, contentType: "application/json", body: '{"objects":{}}' }) : request.continue());
    }
    const loaded = file => page.waitForFunction(file => window.__hsm?.mountedStepFile === file
      && !window.__hsm.currentGroup?.userData.sceneLoading, { timeout: 90000 }, file);
    await page.goto(`${origin}/3d#step:${encodeURIComponent(machine)}`);
    await loaded(machine);
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
    if (await page.$eval(".component-panel", panel => panel.classList.contains("collapsed")))
      await page.click(".component-panel .edge-panel-collapse");
    await page.click(".component-show-all");
    for (const body of ["pump-b-mount", "coil-v-c", "bulkhead-drain-nut", "nameplate-ink"]) {
      const unit = units.find(unit => unit.bodies.includes(body)); assert.ok(unit, body);
      const result = await clickBody(page,body,unit.bodies);
      assert.equal(result.picked.name,unit.name,body);
      assert.equal(result.picked.feature,undefined,body);
      assert.equal(result.hover,result.expected,body);
      assert.equal(result.highlight,result.expected,body);
      if (await page.$eval(".component-panel", panel => panel.classList.contains("collapsed")))
        await page.click(".component-panel .edge-panel-collapse");
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
    const harness = units.find(unit => unit.name === "terminal-J13"); assert.ok(harness);
    await clickBody(page,harness.name,harness.bodies);
    await page.click(".component-actions .component-open");
    await loaded(machine+"?component=terminal-J13");
    assert.deepEqual(await page.evaluate(() => [...new Set(window.__hsm.currentGroup.children
      .filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))].sort()),[...harness.bodies].sort());
    assert.equal((await clickBody(page,"wire-J13-AM1",["wire-J13-AM1"])).picked.name,"wire-J13-AM1");
    assert.deepEqual(errors,[]);
    if (output) fs.writeFileSync(path.join(output,"navigation.json"),JSON.stringify({ origin, units: units.length, checked: ["pump","valve","bulkhead","nameplate","opened pump","opened harness"], errors },null,2)+"\n");
    await page.close();
  } finally { await closeBrowser(browser); if (server) await closeServer(server); }
});
