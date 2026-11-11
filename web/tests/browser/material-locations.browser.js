// On-demand browser checks follow visual location previews into unobstructed installed views.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { start } from "../../server.js";
import { launchBrowser, closeBrowser, closeServer } from "../../../tools/render/browser.js";

const machine = "manifold-layout/enclosure-assembly.step";
// Panel layout checks reuse the loaded assembly between installed selections.
const focusTabs = process.env.HSM_LOCATIONS_BROWSER_FOCUS === 'tabs';
const recordsOnly = process.env.HSM_LOCATIONS_BROWSER_FOCUS === 'records';
const waitReady = page => page.waitForFunction(() => window.__hsm?.currentGroup && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 45000 });
const settle = page => page.evaluate(() => new Promise(resolve => setTimeout(resolve, 650)));

test(recordsOnly ? "material record trees and combined sections retain their state through refreshes"
  : "locations preview compounds and repeated copies, preserve selection and hide only obstructions", async () => {
  const { server } = process.env.HSM_LOCATIONS_BROWSER_BASE ? {} : await start({ port: 0 });
  const origin = process.env.HSM_LOCATIONS_BROWSER_BASE || `http://127.0.0.1:${server.address().port}`;
  const output = process.env.HSM_LOCATIONS_BROWSER_OUTPUT;
  const browser = await launchBrowser({ headless: true, protocolTimeout: 120000 });
  const results = [];
  try {
    for (const viewport of [{ width: 1280, height: 960 }, { width: 390, height: 844, isMobile: true, hasTouch: true }]) {
      const page = await browser.newPage(), errors = [];
      page.setDefaultNavigationTimeout(120000);
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
        assert.deepEqual(await page.$$eval('.material-tabs button', nodes => nodes.map(node => node.textContent)),
          ['BOM & Where used', 'Stock & Cost', 'Location']);
        assert.equal(await page.$('.material-locations'), null);
        assert.match(await page.$eval('.material-parent-tree', node => node.textContent), /Soda machine/);
        assert.match(await page.$eval('.material-parent-tree', node => node.textContent), /Direct parent/);
        assert.equal(await page.$eval('.material-tree-focus', node => node.dataset.material), 'HSM-0331');
        assert.deepEqual(await page.$$eval('.material-structure > section', nodes => nodes.map(node => node.getAttribute('aria-label'))), ['Where used', 'BOM']);
        assert.equal(await page.$('.material-assembly-records'), null);
        assert.ok(await page.evaluate(async () => {
          const {state}=await import('/js/viewer/state.js');
          const {HSM_EVENTS}=await import('/contracts/client-events.js');
          const before=document.querySelector('.material-tree-focus');
          window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_MOUNTED,{detail:{file:state.mountedDetail.file,complete:false}}));
          if(before!==document.querySelector('.material-tree-focus')) return false;
          state.materialCatalog={...state.materialCatalog};
          state.materialPanel.sync();
          if(!state.materialCatalogTag || before!==document.querySelector('.material-tree-focus')) return false;
          const tag=state.materialCatalogTag;
          state.materialCatalogTag=tag+'-changed';
          state.materialPanel.sync();
          const changed=before!==document.querySelector('.material-tree-focus');
          state.materialCatalogTag=tag; state.materialPanel.sync();
          return changed;
        }), 'Unchanged records retain their tree while mesh updates and refetches arrive');
        await capture('pisco-structure');
        await page.click('.material-tabs [data-tab="stock-cost"]');
        assert.deepEqual(await page.$$eval('.material-tab-content > section', nodes => nodes.map(node => node.getAttribute('aria-label'))), ['Stock', 'Cost']);
        assert.ok(await page.evaluate(() => {
          const stock = document.querySelector('[data-material-section="stock"]').getBoundingClientRect();
          const cost = document.querySelector('[data-material-section="cost"]').getBoundingClientRect();
          return cost.top >= stock.bottom;
        }));
        await capture('pisco-stock-cost');
        await page.evaluate(async () => (await import('/js/viewer/state.js')).state.materialPanel.applyRoute({tab:'cost',panel:'materials'}));
        await settle(page);
        assert.equal(await page.$eval('.material-tabs [aria-selected="true"]', node => node.dataset.tab), 'stock-cost');
        if (recordsOnly) {
          await page.evaluate(async () => (await import('/js/viewer/state.js')).state.materialPanel.applyRoute({tab:'used',panel:'materials'}));
          await settle(page);
          assert.equal(await page.$eval('.material-tabs [aria-selected="true"]', node => node.dataset.tab), 'structure');
          assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
          assert.deepEqual(errors, []);
          results.push({width:viewport.width,records:true});
          continue;
        }
        await page.click('.material-tabs [data-tab="location"]');
        await page.waitForFunction(machine => window.__hsm?.mountedStepFile === machine
          && !window.__hsm.currentGroup.userData.sceneLoading
          && document.querySelector('.material-locations')?.dataset.instance === 'gas-regulator', { timeout: 45000 }, machine);
        await settle(page);
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
          await page.click('.material-tabs [data-tab="stock-cost"]');
          await page.waitForFunction(() => window.__hsm?.mountedStepFile === 'reference/compact-inline-candidates/geometry/candidate-regulator.step'
            && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 15000 });
          await page.click('.material-tabs [data-tab="location"]');
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
        if (!focusTabs) {
        await page.goBack();
        await page.waitForFunction(() => document.querySelector('.material-locations')?.dataset.instance === 'gas-regulator'
          && !window.__hsm.currentGroup.userData.sceneLoading, { timeout: 30000 });
        assert.match(await page.evaluate(() => location.hash), /material:HSM-0331/);
        await page.goForward();
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator'
          && !document.querySelector('.cad-workspace').classList.contains('materials-open'), { timeout: 15000 });
        await page.reload();
        await waitReady(page);
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator', { timeout: 15000 });
        await settle(page);
        assert.equal(await page.$eval('.materials-toggle', button => button.getAttribute('aria-expanded')), 'false');
        }

        await page.evaluate(async () => (await import('/js/viewer/material-nav.js')).openMaterial('HSM-0001', true, { panel: 'materials', tab: 'structure' }));
        const firstBranch = await page.$('.bom-tree > .bom-node:has(> .bom-row > .bom-disclosure:not(:disabled))');
        assert.ok(firstBranch);
        const childID = await firstBranch.$eval('.bom-number', node => node.textContent);
        await (await firstBranch.$('.bom-disclosure')).click();
        assert.ok(await page.$('.bom-branch > .bom-node'));
        await capture('assembly-tree');
        const selectedBranch = await page.$('.bom-tree > .bom-node:has(> .bom-row > .bom-disclosure[aria-expanded="true"]) > .bom-row > .bom-select');
        await selectedBranch.click();
        assert.equal(await page.$eval('.material-tree-focus', node => node.dataset.material), childID);
        assert.ok(await page.$('.bom-tree > .bom-node'));
        assert.equal(await page.$('.bom-own'), null);
        await page.evaluate(async () => (await import('/js/viewer/material-nav.js')).openMaterial('HSM-0559', true, { panel: 'materials', tab: 'structure' }));
        await capture('pisco-assembly-tree');
        await page.locator('.bom-select').filter(node => node.textContent.includes('HSM-0331')).click();
        await settle(page);
        await page.click('.materials-toggle');
        await page.waitForFunction(() => document.querySelector('.component-panel.show .component-body-name')?.textContent === 'CAD body: gas-regulator');
        await page.waitForFunction(async () => (await import('/js/viewer/state.js')).state.autoHiddenComponents.has('enclosure-back-top'));
        await capture('pisco-pane-closed');

        if (focusTabs) {
          await page.evaluate(async () => {
            const {state}=await import('/js/viewer/state.js');
            const {explodeBom}=await import('/contracts/materials.js');
            await (await import('/js/viewer/material-nav.js')).openMaterial('HSM-0001',true,{panel:'materials',tab:'structure'});
            const row=explodeBom(state.materialCatalog,'HSM-0001').find(row=>row.material.id==='HSM-0047');
            state.materialPanel.select(row.material.id,row.path);
          });
          await page.click('.material-tabs [data-tab="location"]');
          assert.match(await page.evaluate(()=>location.hash), /material:HSM-0047\?tab=location/);
        } else await page.goto(`${origin}/3d#material:HSM-0047?tab=location&panel=materials`);
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
