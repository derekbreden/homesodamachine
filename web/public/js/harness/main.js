import * as THREE from 'three';
import { createNavigation } from '../viewer/navigation.js';
import { createAxisRulers } from '../viewer/axis-rulers.js';
import { createXrayRenderer } from '../viewer/xray-render.js';
import { conductorRecords } from './conductors.js';
import { loadBoard } from './board.js';

// Each bench owns its scene and state; loading a second guide cannot change the
// first. Only the explicit Open button calls model.open().
export async function initHarness(root) {
  if (root.dataset.harnessReady) return;
  const data = JSON.parse(root.querySelector('[data-harness-data]').textContent);
  const records = conductorRecords(data);
  const $ = selector => root.querySelector(selector);
  const $$ = selector => [...root.querySelectorAll(selector)];
  const stage = $('.harness-stage');
  const state = { selection: null, opened: null, step: null, reveal: false, xray: false, explode: 0, labels: true, view: 'overall' };
  const hiddenParts = new Set(), hiddenObjects = new Map();
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor(0, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute('aria-label', `${data.id} harness. Click a conductor to highlight it; Open conductor is a separate action.`);
  renderer.domElement.setAttribute('role', 'img');
  stage.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const content = new THREE.Group(); scene.add(content);
  scene.add(new THREE.HemisphereLight(0xf5f8ff, 0x71829e, 2.5));
  const light = new THREE.DirectionalLight(0xffffff, 3.5);
  light.position.set(-65, 160, 100); light.castShadow = true;
  Object.assign(light.shadow.camera, { left: -160, right: 160, top: 120, bottom: -120, near: 1, far: 500 });
  light.shadow.mapSize.set(2048, 2048); light.shadow.bias = -.0005; scene.add(light);
  const fill = new THREE.DirectionalLight(0xcbdcff, 1.8);
  fill.position.set(70, 60, -110); scene.add(fill);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 400), new THREE.ShadowMaterial({ opacity: .10 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -.4; floor.receiveShadow = true; scene.add(floor);
  const grid = new THREE.GridHelper(500, 50, 0x97aecf, 0xa6bad6);
  grid.material.transparent = true; grid.material.opacity = .13; grid.position.y = -.35; scene.add(grid);
  const { buildHarness } = await import(data.id === 'J13' ? './j13-model.js' : './model.js');
  const model = buildHarness(content, data);
  const board = await loadBoard(content, data);
  // PCB labels is an inspection of the native board alone. A separate camera
  // layer keeps the lifted bench plug from covering the real silkscreen.
  board.root.traverse(item => item.layers.enable(1));
  scene.traverse(item => { if (item.isLight) item.layers.enable(1); });
  const pinMarker = new THREE.Mesh(new THREE.TorusGeometry(.9, .12, 6, 32), new THREE.MeshBasicMaterial({ color: 0xe98526, depthTest: false }));
  pinMarker.rotation.x = Math.PI / 2; pinMarker.layers.enable(1); pinMarker.renderOrder = 10; pinMarker.visible = false; scene.add(pinMarker);
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 1800);
  let frame = 0, visible = true, transition = null, openedEnds = null;
  let cameraReady = false, saveTimer = 0;
  let boundsDirty = true, boundsLayer = 0;
  const contentBounds = new THREE.Box3();
  const poseKey = `harness-camera:${data.id}`;
  const navigation = createNavigation({
    camera, renderer, getGroup: () => content, getBounds: visibleBounds,
    defaultUp: new THREE.Vector3(0, 1, 0), invalidate: requestRender,
    gizmoClassName: 'harness-gizmo',
  });
  const controls = navigation.controls;
  stage.append(navigation.gizmoCanvas);
  const rulers = createAxisRulers({ scene, camera, controls, renderer, invalidate: requestRender });
  rulers.group.layers.enable(1);
  const xray = createXrayRenderer();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const vec = p => new THREE.Vector3(...p);
  const recordFor = () => records.find(row => row.id === state.selection);

  function requestRender() { if (!frame && visible) frame = requestAnimationFrame(render); }
  function visibleBounds() {
    if (!boundsDirty && boundsLayer === camera.layers.mask) return contentBounds;
    contentBounds.makeEmpty();
    content.updateWorldMatrix(true, true);
    content.traverseVisible(item => {
      if (!item.isMesh || item.userData.hitOnly || item.userData.isXrayEdge || !camera.layers.test(item.layers)) return;
      if (!item.geometry.boundingBox) item.geometry.computeBoundingBox();
      contentBounds.union(item.geometry.boundingBox.clone().applyMatrix4(item.matrixWorld));
    });
    boundsDirty = false; boundsLayer = camera.layers.mask;
    return contentBounds;
  }
  function savePose() {
    if (cameraReady && !transition && !state.opened && !state.step && ['overall', 'top'].includes(state.view)) {
      navigation.savePose(poseKey);
      try { localStorage.setItem(`${poseKey}:aspect`, String(camera.aspect)); } catch { /* Storage is optional. */ }
    }
  }
  function adaptAspect(previous, next) {
    if (!(previous > 0) || previous === next) return;
    // Preserve the horizontal framing and the user's pan/rotation when moving
    // between the wide thumbnail and the tall full-screen bench.
    transition = null; navigation.dropStalledGesture();
    camera.position.sub(controls.target).multiplyScalar(previous / next).add(controls.target);
    controls.update();
  }
  function showStage() {
    const bounds = stage.getBoundingClientRect();
    if (bounds.top < 55 || bounds.bottom > innerHeight) stage.scrollIntoView({ block: 'start', behavior: reduced.matches ? 'instant' : 'smooth' });
  }
  function moveCamera(target, position, immediate = false) {
    navigation.dropStalledGesture();
    const up = vec([0, 1, 0]);
    if (immediate || reduced.matches) {
      transition = null; camera.position.copy(position); camera.up.copy(up); controls.target.copy(target); controls.update();
    } else transition = { start: performance.now(), from: camera.position.clone(), fromUp: camera.up.clone(), fromTarget: controls.target.clone(), to: position, target, up };
    requestRender();
  }
  function fit(bounds, direction, immediate = false, padding = 1.12) {
    const target = bounds.getCenter(new THREE.Vector3());
    const normal = vec(direction).normalize();
    const right = new THREE.Vector3().crossVectors(vec([0, 1, 0]), normal).normalize();
    const up = new THREE.Vector3().crossVectors(normal, right).normalize();
    const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2), tanH = tanV * camera.aspect;
    let distance = 12;
    for (const x of [bounds.min.x, bounds.max.x]) for (const y of [bounds.min.y, bounds.max.y]) for (const z of [bounds.min.z, bounds.max.z]) {
      const corner = vec([x, y, z]).sub(target), depth = corner.dot(normal);
      distance = Math.max(distance, Math.abs(corner.dot(right)) / tanH + depth, Math.abs(corner.dot(up)) / tanV + depth);
    }
    moveCamera(target, target.clone().addScaledVector(normal, distance * padding), immediate);
  }
  function markView(name) {
    state.view = name;
    $$('[data-harness-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessView === name)));
  }
  function view(name, immediate = false) {
    markView(name);
    if (name !== 'pcb') {
      rulers.setEnabled(false); $('[data-harness-rulers]').checked = false;
    }
    camera.layers.set(name === 'pcb' ? 1 : 0);
    light.castShadow = name !== 'pcb';
    if (name === 'pcb') {
      fit(board.bounds, [data.id === 'J13' ? -.4 : .4, 1, .65], immediate, 1.15);
    } else if (name === 'connector') {
      fit(model.boundsFor('connector'), [-1, .8, 1], immediate, 1.12);
    } else {
      const bounds = visibleBounds();
      if (bounds.isEmpty()) return;
      fit(bounds, name === 'top' ? [0, 1, .001] : [.12, 1, 1.2], immediate, 1.18);
    }
    requestRender();
  }
  function tab(name) {
    $$('[data-harness-tab]').forEach(button => {
      const active = button.dataset.harnessTab === name;
      button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
    });
    $$('[data-harness-panel]').forEach(panel => { panel.hidden = panel.dataset.harnessPanel !== name; });
  }
  function definitionList(container, items) {
    container.replaceChildren(...items.map(([term, description]) => {
      const row = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = term; dd.textContent = description; row.append(dt, dd); return row;
    }));
  }
  const j2Parts = [
    ['JST end', '1 XHP-6 housing · 5 SXH-001T-P0.6 contacts · cavity 3 empty'],
    ['Cable', '2 × 650 mm 3P ribbon blanks · 4 × 450 mm bulk-wire positive blanks · 22 AWG black silicone'],
    ['Slip on first', '1/2 in PET mesh · 2 heat-shrink collars · 2 zip ties'],
    ['Far ends', '5 ferrules · Wago 221-415 · 6 valve disconnects · 2 provisional fan ends'],
    ['Tools', 'Stripper · SN-2549 JST crimper · ferrule and terminal crimpers · heat gun · flush cutters · multimeter'],
  ];
  definitionList($('[data-harness-materials]'), data.materials?.map(row => [row.label, row.detail]) || j2Parts);
  const sleeved = data.dress.sleeve !== 'None';
  const pumpPart = key => model.anchors.find(anchor => anchor.key === key && anchor.conductors);

  function partInfo(key) {
    const pump = pumpPart(key);
    if (pump) return [`${pump.name} · Faston receptacles`, data.overview, [...pump.conductors.map(row => [`${row.ribbon} · ${row.net}`, row.to]), ['Each end', pump.conductors[0].toPart]]];
    if (key === 'pcb') return [`Native PCB · ${data.id}`, 'The actual header mesh and original fabrication pixels, cropped from the machine’s PCB. Use PCB labels to read its printed silkscreen.', [['Header', `${data.id} · ${data.name}`], ['Mating direction', 'Vertical top entry · plug shown lifted above it']]];
    if (key === 'connector') return [`${data.housing} JST plug`, data.id === 'J2' ? 'Five contacts occupy cavities 1, 2, 4, 5 and 6. Cavity 3 / OUT4 stays empty. The plug’s circuit-1 mark aligns with COM on the PCB.' : 'Four contacts occupy cavities 1–4. The plug’s circuit-1 mark aligns with AM2 on the PCB.', [['Housing', data.housing], ['Contact', data.contact], ['Pitch', `${data.pitchMm} mm`]]];
    if (key === 'dress') return ['Slip-on pieces', data.dress.description, [['Sleeve', data.dress.sleeve], ...(data.dress.collars ? [['Collars & ties', `${data.dress.collars} heat-shrink collars · ${data.dress.ties} zip ties`]] : [])]];
    if (key === 'wago') return ['One +12 V feed · four branches', 'The COM conductor enters one ferruled Wago port. Four separate ferruled wires leave for V-I, V-J, the fan and V-K. Each switched return runs directly to its own PCB output.', [['Block', 'Wago 221-415'], ['Wire ends', '5 separate bootlace ferrules'], ['Positive stock', '4 × 450 mm blanks · trim at fitting']]];
    if (key === 'terminals') return ['Far-end terminations', 'The COM feed and four positives use individual ferrules at the Wago. The three valves each receive positive and switched-return disconnects; both fan ends remain provisional.', [['Ferrules', '5'], ['Valve disconnects', '6'], ['Fan ends', '2 · interface provisional']]];
    return ['Ribbon stock', data.ribbons.map(row => row.description).join(' '), data.ribbons.map(row => [`Ribbon ${row.id}`, `${row.poles}P · ${row.cutMm} mm blank · stripe → ${row.stripeNet}`])];
  }
  function inspect() {
    const record = recordFor(), key = state.selection;
    $('[data-harness-wire-list]').hidden = !!key;
    $('.harness-selection').hidden = !key;
    $('.harness-connection').hidden = !record;
    $('[data-harness-open]').hidden = !record;
    $('[data-harness-open]').disabled = !!state.opened;
    $('[data-harness-open]').textContent = state.opened ? 'Conductor open' : 'Open conductor ↗';
    $('[data-harness-hide]').disabled = !key || !!state.opened;
    const partWires = $('[data-harness-part-wires]'); partWires.replaceChildren();
    if (!key) return;
    let title, detail, rows;
    if (record) {
      title = record.title; detail = record.note;
      $('[data-harness-from]').textContent = record.from;
      $('[data-harness-to]').textContent = record.to;
      rows = [
        ['Wire', `${record.ribbon ? `Ribbon ${record.ribbon}` : 'Bulk wire'} · ${record.stripe ? 'white-striped edge' : 'plain black'} · 22 AWG`],
        ['Bench cut', `${record.cutMm} mm${record.port ? ' blank · trim at fitting' : ''}`],
        ['From end', record.fromPart], ['To end', record.toPart],
        ['Slip on before finishing', record.sharedDress ? 'Shared PET mesh · 2 heat-shrink collars · 2 zip ties around the four-wire trunk' : sleeved ? 'No shared mesh on this branch' : data.dress.sleeve],
      ];
    } else {
      [title, detail, rows] = partInfo(key);
      const related = pumpPart(key)?.conductors || (key === 'wago' ? records.filter(row => row.net === 'COM') : ['connector', 'pcb'].includes(key) ? records.filter(row => row.pin) : key === 'dress' ? records.filter(row => row.sharedDress) : records);
      related.forEach(row => {
        const button = document.createElement('button'); button.type = 'button';
        button.dataset.harnessRelated = row.id; button.textContent = row.title;
        button.addEventListener('click', () => select(row.id)); partWires.append(button);
      });
    }
    $('[data-harness-selection-title]').textContent = title;
    $('[data-harness-selection-detail]').textContent = detail;
    definitionList($('[data-harness-selection-facts]'), rows);
  }

  const svg = $('.harness-leaders'), namespace = 'http://www.w3.org/2000/svg';
  const labels = model.anchors.map((anchor, index) => {
    const button = document.createElement('button'); button.type = 'button';
    button.className = 'harness-label'; button.dataset.key = anchor.key; button.textContent = anchor.title;
    button.addEventListener('click', () => select(anchor.key)); $('.harness-labels').append(button);
    const line = document.createElementNS(namespace, 'line'), dot = document.createElementNS(namespace, 'circle');
    dot.setAttribute('r', '2.8'); svg.append(line, dot);
    return { ...anchor, button, line, dot, slot: anchor.slot || [[.14, .15], [.15, .36], [.5, .14], [.86, .18]][index % 4] };
  });
  function placeLabels() {
    const { width, height } = stage.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    for (const label of labels) {
      let point = label.key === 'pcb' ? board.anchor.clone() : model.pointFor(label);
      if (label.key !== 'pcb' && state.explode) {
        const bounds = model.boundsFor(label.key);
        if (!bounds.isEmpty()) point = bounds.getCenter(new THREE.Vector3());
      }
      const p = point.project(camera);
      const hidden = hiddenParts.has(label.key) || !state.labels || !!state.opened || ['pcb', 'connector', 'end'].includes(state.view) || p.z > 1 || p.z < -1 || Math.abs(p.x) > 1.05 || Math.abs(p.y) > 1.05 || (state.step === 'cut' && !['ribbons', 'connector', 'pcb'].includes(label.key)) || (['jst', 'dress'].includes(state.step) && (['wago', 'FAN', 'OUT1', 'OUT2', 'OUT3'].includes(label.key) || !!label.conductors));
      label.button.hidden = hidden; label.line.style.display = hidden ? 'none' : ''; label.dot.style.display = hidden ? 'none' : '';
      if (hidden) continue;
      const x = Math.max(label.button.offsetWidth / 2 + 6, Math.min(width - label.button.offsetWidth / 2 - 6, label.slot[0] * width));
      const y = label.slot[1] * height;
      label.button.style.left = `${x}px`; label.button.style.top = `${y}px`;
      const px = (p.x + 1) * width / 2, py = (1 - p.y) * height / 2;
      for (const [name, value] of Object.entries({ x1: x, y1: y, x2: px, y2: py })) label.line.setAttribute(name, value);
      label.dot.setAttribute('cx', px); label.dot.setAttribute('cy', py);
      label.line.classList.toggle('is-selected', label.key === state.selection);
      label.dot.classList.toggle('is-selected', label.key === state.selection);
    }
  }
  function render(now) {
    frame = 0;
    if (transition) {
      const t = Math.min(1, (now - transition.start) / 400), ease = 1 - (1 - t) ** 3;
      camera.position.lerpVectors(transition.from, transition.to, ease); controls.target.lerpVectors(transition.fromTarget, transition.target, ease);
      camera.up.lerpVectors(transition.fromUp, transition.up, ease).normalize();
      if (t === 1) transition = null;
    }
    const changing = navigation.update(now);
    xray.syncEdgeResolution(renderer);
    rulers.update();
    renderer.render(scene, camera); placeLabels();
    if (changing || transition) requestRender();
  }
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    if (!width || !height) return;
    const previousAspect = camera.aspect;
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix();
    if (cameraReady) adaptAspect(previousAspect, camera.aspect);
    navigation.resize(); requestRender();
  }
  function update() {
    xray.restore(content);
    for (const [item, wasVisible] of hiddenObjects) item.visible = wasVisible;
    hiddenObjects.clear();
    model.update(state);
    board.root.visible = !state.opened || openedEnds?.sourceIsPcb;
    content.traverse(item => {
      if (!hiddenParts.has(item.userData.key)) return;
      hiddenObjects.set(item, item.visible); item.visible = false;
    });
    xray.apply(content, state.xray);
    boundsDirty = true;
    board.select(board.root.visible && state.selection === 'pcb' ? 'pcb' : null);
    const record = recordFor();
    pinMarker.visible = !!record?.pin && board.root.visible;
    if (pinMarker.visible) pinMarker.position.copy(board.pinPoint(record.pin)).add(vec([0, .25, 0]));
    $$('[data-harness-select]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessSelect === state.selection)));
    labels.forEach(label => label.button.setAttribute('aria-pressed', String(label.key === state.selection)));
    $$('[data-harness-step]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessStep === state.step)));
    $('[data-harness-finished]').setAttribute('aria-pressed', String(!state.step));
    $('.harness-step-detail').hidden = !state.step;
    $('.harness-open-banner').hidden = !state.opened;
    $('[data-harness-view="pcb"]').disabled = !!state.opened && !openedEnds?.sourceIsPcb;
    $('[data-harness-view="connector"]').disabled = !!state.opened;
    $('[data-harness-explode]').disabled = !!state.opened;
    $('[data-harness-show-all]').disabled = !hiddenParts.size;
    $('[data-harness-show-all]').textContent = hiddenParts.size ? `Show all (${hiddenParts.size} hidden)` : 'Show all';
    $('[data-harness-find]').disabled = !!state.opened;
    $('[data-harness-rulers]').disabled = !!state.opened && !openedEnds?.sourceIsPcb;
    root.dataset.harnessSelection = state.selection || '';
    root.dataset.harnessOpened = state.opened || '';
    requestRender();
  }
  function select(key) {
    if (state.opened) return;
    hiddenParts.delete(key);
    state.selection = state.selection === key ? null : key;
    $('[data-harness-find]').value = ''; findParts();
    tab('wires'); inspect(); update();
  }
  const searchable = [
    ...records.map(row => ({ key: row.id, title: row.title, text: `${row.title} ${row.id} ${row.from} ${row.to} ${row.fromPart} ${row.toPart} ${row.note}` })),
    ...model.anchors.filter(anchor => !records.some(row => row.id === anchor.key)).map(anchor => ({ key: anchor.key, title: anchor.title, text: `${anchor.title} ${partInfo(anchor.key).flat(2).join(' ')}` })),
  ];
  function findParts() {
    const query = $('[data-harness-find]').value.trim().toLowerCase();
    const results = $('[data-harness-find-results]');
    results.hidden = !query;
    if (!query) { results.replaceChildren(); return; }
    const matches = searchable.filter(row => query.split(/\s+/).every(word => row.text.toLowerCase().includes(word)));
    const buttons = matches.map(row => {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = row.title;
      button.addEventListener('click', () => select(row.key)); return button;
    });
    if (!buttons.length) {
      const empty = document.createElement('p'); empty.textContent = 'No matching conductor or part.'; buttons.push(empty);
    }
    results.replaceChildren(...buttons);
  }
  function closeConductor() {
    if (!state.opened) return;
    xray.restore(content);
    model.close(); state.opened = null; openedEnds = null;
    inspect(); update(); view('overall');
  }
  function showStep(id) {
    closeConductor(); state.step = id; state.selection = null; tab('build');
    const index = data.steps.findIndex(step => step.id === id), step = data.steps[index];
    $$('[data-harness-step]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessStep === id)));
    $('[data-harness-finished]').setAttribute('aria-pressed', String(!id));
    $('.harness-step-detail').hidden = !step;
    if (step) {
      $('[data-harness-step-index]').textContent = `${index + 1} / ${data.steps.length} · ${step.minutes} min`;
      $('[data-harness-step-title]').textContent = step.title; $('[data-harness-step-copy]').textContent = step.instruction;
      $('[data-harness-prev]').disabled = index === 0;
      $('[data-harness-next]').textContent = index === data.steps.length - 1 ? 'Finished view' : 'Next step';
    }
    inspect(); update(); view(id === 'jst' ? 'connector' : 'overall');
  }
  function focusEnd(which) {
    const record = recordFor(); if (!record) return;
    const ends = state.opened ? openedEnds : model.endpointsFor(record.id);
    const point = ends[which].clone();
    markView('end');
    rulers.setEnabled(false); $('[data-harness-rulers]').checked = false;
    camera.layers.set(0); light.castShadow = true;
    if (which === 'from' && ends.sourceIsPcb) {
      // Includes the native silk and selected contact above its actual pin.
      point.lerp(board.pinPoint(record.pin), .4);
      moveCamera(point, point.clone().add(vec([-20, 32, 22])));
    } else moveCamera(point, point.clone().add(vec([12, 23, 26])));
    showStage();
  }

  $$('[data-harness-select]').forEach(button => button.addEventListener('click', () => select(button.dataset.harnessSelect)));
  $('[data-harness-clear]').addEventListener('click', () => { closeConductor(); state.selection = null; inspect(); update(); });
  $('[data-harness-open]').addEventListener('click', () => {
    const record = recordFor(); if (!record || state.opened) return;
    state.opened = record.id; state.step = null;
    xray.restore(content);
    openedEnds = model.open(record.id);
    $('[data-harness-open-title]').textContent = record.title;
    inspect(); update(); view('overall'); showStage();
  });
  $('[data-harness-close]').addEventListener('click', closeConductor);
  $$('[data-harness-focus]').forEach(button => button.addEventListener('click', () => focusEnd(button.dataset.harnessFocus)));
  $$('[data-harness-tab]').forEach(button => {
    button.addEventListener('click', () => { tab(button.dataset.harnessTab); if (button.dataset.harnessTab !== 'build' && state.step) showFinished(); });
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault(); const tabs = $$('[data-harness-tab]'), index = tabs.indexOf(button);
      const next = tabs[(index + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; next.click(); next.focus();
    });
  });
  function showFinished() { state.step = null; update(); view('overall'); }
  $$('[data-harness-view]').forEach(button => button.addEventListener('click', () => view(button.dataset.harnessView)));
  $$('[data-harness-step]').forEach(button => button.addEventListener('click', () => showStep(button.dataset.harnessStep)));
  $('[data-harness-finished]').addEventListener('click', () => showStep(null));
  $('[data-harness-prev]').addEventListener('click', () => showStep(data.steps[data.steps.findIndex(step => step.id === state.step) - 1]?.id || null));
  $('[data-harness-next]').addEventListener('click', () => showStep(data.steps[data.steps.findIndex(step => step.id === state.step) + 1]?.id || null));
  $('[data-harness-wires]')?.addEventListener('change', event => { state.reveal = event.target.checked; update(); });
  $('[data-harness-xray]').addEventListener('change', event => { state.xray = event.target.checked; update(); });
  $('[data-harness-rulers]').addEventListener('change', event => {
    const enabled = event.target.checked;
    if (enabled && state.view !== 'pcb') view('pcb');
    rulers.setEnabled(enabled); requestRender();
  });
  $('[data-harness-find]').addEventListener('input', findParts);
  $('[data-harness-hide]').addEventListener('click', () => {
    if (!state.selection || state.opened) return;
    hiddenParts.add(state.selection); state.selection = null; inspect(); update();
  });
  $('[data-harness-show-all]').addEventListener('click', () => { hiddenParts.clear(); update(); });
  $$('[data-harness-nav]').forEach(button => button.addEventListener('click', () => {
    navigation.setMode(button.dataset.harnessNav);
    $$('[data-harness-nav]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    stage.dataset.navigation = navigation.mode;
  }));
  $('[data-harness-labels]').addEventListener('change', event => { state.labels = event.target.checked; requestRender(); });
  $('[data-harness-explode]').addEventListener('input', event => {
    state.explode = Number(event.target.value) / 100; $('[data-harness-explode-value]').textContent = `${event.target.value}%`; update();
  });
  $('[data-harness-reset]').addEventListener('click', () => {
    try { localStorage.removeItem(poseKey); } catch { /* Storage is optional. */ }
    view('overall');
  });
  const workbench = $('.harness-workbench'), launch = $('[data-harness-launch]');
  const mobile = matchMedia('(max-width: 960px)');
  const home = document.createComment(`${data.id} workbench`);
  workbench.before(home);
  const dialog = document.createElement('dialog');
  dialog.className = 'harness-dialog';
  dialog.setAttribute('aria-label', `${data.id} ${data.name} interactive harness`);
  const dialogHeading = document.createElement('header'), dialogTitle = document.createElement('strong'), dialogClose = document.createElement('button');
  dialogHeading.className = 'harness-dialog-heading';
  dialogTitle.textContent = `${data.id} · ${data.name}`;
  dialogClose.type = 'button'; dialogClose.textContent = 'Close ×'; dialogClose.dataset.harnessDismiss = '';
  dialogHeading.append(dialogTitle, dialogClose); dialog.append(dialogHeading); root.append(dialog);
  let opener = null;
  function previewMode() {
    const preview = mobile.matches && !dialog.open;
    root.classList.toggle('is-preview', preview);
    launch.hidden = !preview;
    stage.tabIndex = preview ? -1 : 0;
    renderer.domElement.setAttribute('aria-hidden', String(preview));
  }
  function expand() {
    if (dialog.open) return;
    opener = document.activeElement;
    dialog.append(workbench); dialog.showModal();
    visible = true;
    document.documentElement.classList.add('harness-modal-open');
    previewMode(); resize(); dialogClose.focus();
  }
  dialogClose.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    navigation.clearTouches(); clearPicking(); savePose();
    home.after(workbench);
    document.documentElement.classList.toggle('harness-modal-open', !!document.querySelector('.harness-dialog[open]'));
    previewMode(); resize(); opener?.focus({ preventScroll: true });
  });
  launch.addEventListener('click', expand);
  $('[data-harness-fullscreen]').addEventListener('click', expand);
  mobile.addEventListener('change', previewMode);

  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
  let down = null, multiTouch = false, suppressClickUntil = 0;
  const pointers = new Set();
  function clearPicking() { pointers.clear(); down = null; multiTouch = false; suppressClickUntil = performance.now() + 350; }
  window.addEventListener('blur', clearPicking);
  document.addEventListener('visibilitychange', () => { if (document.hidden) clearPicking(); });
  const pick = event => {
    const bounds = stage.getBoundingClientRect();
    pointer.set((event.clientX - bounds.left) / bounds.width * 2 - 1, -(event.clientY - bounds.top) / bounds.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    raycaster.layers.mask = camera.layers.mask;
    return raycaster.intersectObjects([...model.pickables, ...board.pickables]).find(hit => {
      for (let item = hit.object; item; item = item.parent) if (!item.visible) return false;
      if (model.tagFor(hit.object) === 'dress' && (state.reveal || recordFor())) return false;
      return true;
    });
  };
  renderer.domElement.addEventListener('pointerdown', event => {
    pointers.add(event.pointerId);
    if (pointers.size > 1) { multiTouch = true; down = null; }
    else down = { id: event.pointerId, x: event.clientX, y: event.clientY, moved: false };
  });
  renderer.domElement.addEventListener('pointercancel', event => {
    pointers.delete(event.pointerId); down = null;
    if (!pointers.size) multiTouch = false;
  });
  renderer.domElement.addEventListener('pointerup', event => {
    const click = event.button === 0 && !multiTouch && !navigation.isTouchGesture() && performance.now() > suppressClickUntil && down?.id === event.pointerId && !down.moved && Math.hypot(event.clientX - down.x, event.clientY - down.y) <= 5;
    if (multiTouch) suppressClickUntil = performance.now() + 350;
    pointers.delete(event.pointerId); down = null;
    if (!pointers.size) multiTouch = false;
    if (!click || state.opened) return;
    const hit = pick(event); if (hit) select(model.tagFor(hit.object));
  });
  renderer.domElement.addEventListener('pointermove', event => {
    if (down?.id === event.pointerId && Math.hypot(event.clientX - down.x, event.clientY - down.y) > 5) down.moved = true;
    if (down || multiTouch || state.opened) return;
    renderer.domElement.style.cursor = navigation.mode === 'pan' ? 'move' : navigation.mode === 'zoom' ? 'ns-resize' : pick(event) ? 'pointer' : 'grab';
  });
  // Navigation owns all gestures. Picking only suppresses incidental taps.
  renderer.domElement.addEventListener('gesturestart', () => { down = null; suppressClickUntil = performance.now() + 350; });
  renderer.domElement.addEventListener('gestureend', () => { down = null; suppressClickUntil = performance.now() + 350; });
  stage.addEventListener('click', event => {
    if (multiTouch || performance.now() <= suppressClickUntil) { event.preventDefault(); event.stopImmediatePropagation(); }
  }, true);
  stage.addEventListener('keydown', event => {
    if (event.target !== stage || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', 'Home'].includes(event.key)) return;
    event.preventDefault(); transition = null; navigation.dropStalledGesture();
    if (event.key === 'Home') { view('overall'); return; }
    const offset = camera.position.clone().sub(controls.target);
    const right = vec([1, 0, 0]).applyQuaternion(camera.quaternion), up = camera.up.clone().normalize();
    const horizontal = event.key === 'ArrowLeft' ? -1 : event.key === 'ArrowRight' ? 1 : 0;
    const vertical = event.key === 'ArrowUp' ? 1 : event.key === 'ArrowDown' ? -1 : 0;
    if (event.shiftKey) {
      const delta = right.multiplyScalar(horizontal).addScaledVector(up, vertical).multiplyScalar(offset.length() * .06);
      camera.position.add(delta); controls.target.add(delta);
    } else if (horizontal || vertical) {
      const rotation = new THREE.Quaternion().setFromAxisAngle(horizontal ? up : right, (horizontal || vertical) * .12);
      offset.applyQuaternion(rotation); camera.up.applyQuaternion(rotation);
      camera.position.copy(controls.target).add(offset);
    } else {
      offset.multiplyScalar(event.key === '-' ? 1.12 : .88);
      camera.position.copy(controls.target).add(offset);
    }
    controls.update(); requestRender();
  });
  renderer.domElement.addEventListener('webglcontextlost', event => {
    event.preventDefault(); $('.harness-loading').hidden = false;
    $('.harness-loading').textContent = '3D graphics paused. Reload to restore the model; text connections and build instructions are available below.';
    root.classList.remove('is-interactive');
  });
  controls.addEventListener('change', () => {
    requestRender(); clearTimeout(saveTimer); saveTimer = setTimeout(savePose, 250);
  });
  controls.addEventListener('start', () => { transition = null; });
  window.addEventListener('pagehide', savePose);
  new ResizeObserver(resize).observe(stage);
  new IntersectionObserver(entries => { visible = dialog.open || entries[0].isIntersecting; if (visible) requestRender(); }).observe(stage);
  root.classList.add('is-interactive');
  $$('.harness-toolbar, .harness-navigation, .harness-find, .harness-scene-controls, .harness-tabs').forEach(element => { element.hidden = false; });
  $('.harness-loading').hidden = true;
  previewMode(); inspect(); update(); resize(); view('overall', true);
  if (navigation.applyPose(poseKey)) {
    try { adaptAspect(Number(localStorage.getItem(`${poseKey}:aspect`)), camera.aspect); } catch { /* Storage is optional. */ }
  }
  cameraReady = true; root.dataset.harnessReady = 'true';
}
