// On-demand browser checks follow visual location previews into unobstructed installed views.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const machine = "manifold-layout/enclosure-assembly.step";
const waitReady = page => page.waitForFunction(() => window.__hsm?.currentGroup && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 45000 });
const settle = page => page.evaluate(() => new Promise(resolve => setTimeout(resolve, 650)));

test("locations preview compounds and repeated copies, preserve selection and hide only obstructions", async () => {
  const { server } = process.env.HSM_LOCATIONS_BROWSER_BASE ? {} : await start({ dev: false, port: 0 });
  const origin = process.env.HSM_LOCATIONS_BROWSER_BASE || `http://127.0.0.1:${server.address().port}`;
  const output = process.env.HSM_LOCATIONS_BROWSER_OUTPUT;
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  const results = [];
  try {
    for (const viewport of [{ width: 1280, height: 960 }, { width: 390, height: 844, isMobile: true, hasTouch: true }]) {
      const page = await browser.newPage(), errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.setViewport(viewport);
      if (!process.env.HSM_LOCATIONS_BROWSER_BASE) {
        await page.setRequestInterception(true);
        page.on("request", request => request.url().endsWith("/api/objects")
          ? request.respond({ status: 200, contentType: "application/json", body: '{"objects":{}}' }) : request.continue());
      }
      const capture = async label => {
        if (!output) return;
        fs.mkdirSync(output, { recursive: true });
        await page.screenshot({ path: path.join(output, `${viewport.width}-${label}.png`) });
      };
      try {
        await page.goto(`${origin}/3d#material:HSM-0331?panel=materials`);
        await waitReady(page);
        const used = await page.$('.material-tabs button:last-child');
        assert.match(await used.evaluate(button => button.textContent), /Where used/);
        await used.click();
        await page.waitForFunction(machine => window.__hsm?.mountedStepFile === machine
          && !window.__hsm.currentGroup.userData.sceneLoading
          && document.querySelector('.material-locations')?.dataset.instance === 'gas-regulator', { timeout: 45000 }, machine);
        await settle(page);
        assert.equal(await page.$eval('.material-assembly-records', node => node.open), false);
        assert.match(await page.$eval('.material-panel h2', node => node.textContent), /PISCO/);
        assert.equal(await page.$eval('.location-position', node => node.textContent), '1 / 1');
        assert.match(await page.$eval('.location-go', node => node.href), /instance=gas-regulator/);
        if (viewport.isMobile) assert.ok(await page.$eval('.location-go', node => {
          const rect = node.getBoundingClientRect();
          const pane = node.closest('.material-panel').getBoundingClientRect();
          return rect.top >= pane.top && rect.bottom <= pane.bottom;
        }), 'Location controls stay visible beside the phone preview');
        await capture('pisco-preview');
        if (!viewport.isMobile) {
          const cost = await page.evaluateHandle(() => [...document.querySelectorAll('.material-tabs button')].find(button => button.textContent === 'Cost'));
          await cost.asElement().click();
          await page.waitForFunction(() => window.__hsm?.mountedStepFile === 'reference/compact-inline-candidates/geometry/candidate-regulator.step'
            && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 15000 });
          const usedAgain = await page.evaluateHandle(() => [...document.querySelectorAll('.material-tabs button')].find(button => button.textContent === 'Where used'));
          await usedAgain.asElement().click();
          await page.waitForFunction(machine => window.__hsm?.mountedStepFile === machine && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 30000 }, machine);
          await settle(page);
        }
        await page.evaluate(async () => (await import('/js/viewer/xray.js')).setXrayEnabled(true, { persist: false }));
        await page.click('.location-go');
        await page.waitForFunction(async () => {
          const { state } = await import('/js/viewer/state.js');
          return !document.querySelector('.cad-workspace').classList.contains('materials-open')
            && document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator'
            && state.autoHiddenComponents.size > 0;
        }, { timeout: 15000 });
        const entered = await page.evaluate(async () => {
          const { state } = await import('/js/viewer/state.js');
          const { fadedBody } = await import('/js/viewer/part-highlight.js');
          const { isXrayEnabled } = await import('/js/viewer/xray.js');
          return { hidden: [...state.autoHiddenComponents], faded: state.currentGroup.children.some(mesh => mesh.isMesh && fadedBody(mesh)),
            xray: isXrayEnabled(), selectedMeshes: window.__hsm.scene.getObjectByName('component-picker').children[0].children.filter(child => child.isMesh).length };
        });
        assert.ok(entered.hidden.includes('enclosure-back-top'), JSON.stringify(entered));
        assert.equal(entered.faded, false); assert.equal(entered.xray, false);
        assert.equal(await page.$eval('.xray-toggle', node => node.getAttribute('aria-pressed')), 'false');
        assert.ok(entered.selectedMeshes >= 4, JSON.stringify(entered));
        if (viewport.isMobile) {
          assert.ok(await page.$eval('.component-panel', node => node.getBoundingClientRect().height < 110));
          assert.ok(await page.$eval('.component-held-here', node => node.getBoundingClientRect().width > 80));
        }
        await capture('pisco-entered');
        await page.reload();
        await waitReady(page);
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator', { timeout: 15000 });
        await settle(page);
        assert.equal(await page.$eval('.materials-toggle', button => button.getAttribute('aria-expanded')), 'false');

        await page.evaluate(async () => (await import('/js/viewer/material-nav.js')).openMaterial('HSM-0559', true, { panel: 'materials' }));
        const row = await page.evaluateHandle(() => [...document.querySelectorAll('.bom-select')].find(row => row.textContent.includes('HSM-0331')));
        assert.ok(row?.asElement());
        await row.asElement().click();
        await settle(page);
        await page.click('.materials-toggle');
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator');
        await page.waitForFunction(async () => (await import('/js/viewer/state.js')).state.autoHiddenComponents.has('enclosure-back-top'));
        await capture('pisco-pane-closed');

        await page.goto(`${origin}/3d#material:HSM-0047?tab=used&panel=materials`);
        await page.waitForFunction(() => document.querySelector('.location-position')?.textContent === '1 / 2'
          && !window.__hsm?.currentGroup?.userData.sceneLoading, { timeout: 45000 });
        await settle(page);
        assert.equal(await page.$eval('.material-locations', node => node.dataset.instance), 'relay-2');
        await page.click('.location-next'); await settle(page);
        assert.equal(await page.$eval('.material-locations', node => node.dataset.instance), 'relay-1');
        await capture('relay-second');
        await page.click('.location-all'); await settle(page);
        assert.equal(await page.$eval('.location-all', node => node.getAttribute('aria-pressed')), 'true');
        const all = await page.evaluate(async () => {
          const { state } = await import('/js/viewer/state.js');
          const { fadedBody } = await import('/js/viewer/part-highlight.js');
          return ['relay-1', 'relay-2'].map(name => state.currentGroup.children.filter(mesh => mesh.name === name).every(mesh => !fadedBody(mesh)));
        });
        assert.deepEqual(all, [true, true]);
        await capture('relay-all');
        assert.equal(await page.$eval('.location-go', node => node.hidden), true);
        await page.click('.location-next');
        await page.click('.location-go');
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: relay-2');
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
        assert.deepEqual(errors, []);
        results.push({ width: viewport.width, entered });
      } catch (error) {
        await capture('failure');
        error.message += '\n' + JSON.stringify(await page.evaluate(() => ({ hash: location.hash, file: window.__hsm?.mountedStepFile,
          note: document.querySelector('.material-locations')?.innerText, selection: document.querySelector('.component-panel')?.innerText,
          loading: document.querySelector('.cad-loading')?.textContent }))) + '\n' + errors.join('\n');
        throw error;
      } finally { await page.close(); }
    }
    if (output) fs.writeFileSync(path.join(output, 'RESULTS.json'), JSON.stringify(results, null, 2) + '\n');
  } finally { await closeBrowser(browser); await closeServer(server); }
});
