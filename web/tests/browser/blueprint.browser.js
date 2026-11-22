// A settled Blueprint view includes all bodies of exposed components and follows camera and visibility changes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { start } from '../../server.js';
import { launchBrowser, closeBrowser, closeServer } from '../../../tools/render/browser.js';

test('Blueprint classifies whole components and restores manual visibility on return to solid', {timeout:60000}, async () => {
  const {server} = await start({port:0});
  const browser = await launchBrowser({headless:true});
  try {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${server.address().port}/parts`);
    const observed = await page.evaluate(async () => {
      const THREE = await import('three');
      const {state} = await import('/js/viewer/state.js');
      const {renderer, camera, scene} = await import('/js/viewer/scene.js');
      const mode = await import('/js/viewer/xray.js');
      const {selectComponent} = await import('/js/viewer/component-picker.js');
      const group = new THREE.Group(), material = new THREE.MeshBasicMaterial({color:0x8899aa});
      function box(name, x, z, size) {
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(size, size, size/4), material);
        mesh.name = name; mesh.userData.side = 'front';
        mesh.position.set(x, 0, z);
        group.add(mesh);
        return mesh;
      }
      const panel = box('enclosure-front-top',0,1,3), valve = box('valve-v-a',0,0,.5);
      const coveredWire = box('wire-AC1-L',.6,0,.25), exposedWire = box('wire-AC1-N',2.4,0,.25);
      state.materialCatalog = await (await fetch('/api/materials')).json();
      state.mountedDetail = {type:'step',file:'manifold-layout/enclosure-assembly.step'};
      state.currentGroup = group; scene.add(group);
      renderer.setSize(220,220,false);
      camera.position.set(0,0,9); camera.up.set(0,1,0); camera.lookAt(0,0,0);
      camera.near=.01; camera.far=100; camera.aspect=1; camera.updateProjectionMatrix();
      const included = mesh => mesh.layers.test(camera.layers);
      const waitFor = async pred => {
        for (let i=0;i<300;i++) {
          if (pred()) return;
          await new Promise(resolve=>setTimeout(resolve,20));
        }
        throw Error('Blueprint visibility or feature edges did not settle');
      };
      selectComponent(valve.name);
      const marks = scene.getObjectByName('component-picker').children[0];
      const selectionFollows = () => marks.children.length > 0 && marks.children.every(mark => included(mark) === included(valve));
      mode.setXrayEnabled(true,{persist:false});
      mode.updateBlueprintView(renderer,camera,group);
      await waitFor(()=>!included(valve) && group.children.some(m=>m.userData.sourceMesh===coveredWire));
      const exposed = [panel,valve,coveredWire,exposedWire].map(included);
      const coveredSelection = selectionFollows();
      exposedWire.visible=false; mode.invalidateBlueprintVisibility();
      await waitFor(()=>!included(coveredWire));
      camera.position.z=-9; camera.lookAt(0,0,0); mode.updateBlueprintView(renderer,camera,group);
      await waitFor(()=>included(valve) && included(coveredWire));
      const visibleSelection = selectionFollows();
      camera.position.z=9; camera.lookAt(0,0,0); mode.updateBlueprintView(renderer,camera,group);
      await waitFor(()=>!included(valve));
      panel.visible=false; mode.invalidateBlueprintVisibility();
      await waitFor(()=>included(valve) && included(coveredWire));
      mode.setXrayEnabled(false,{persist:false});
      return {exposed, coveredSelection, visibleSelection, restored:[panel,valve,coveredWire,exposedWire].every(mesh=>included(mesh)&&mesh.material===material),
        manuallyHidden:!panel.visible&&!exposedWire.visible};
    });
    assert.deepEqual(observed,{exposed:[true,false,true,true],coveredSelection:true,visibleSelection:true,restored:true,manuallyHidden:true});
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
  }
});
