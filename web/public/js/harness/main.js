import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
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
  const state = { selection: null, opened: null, step: null, reveal: false, explode: 0, labels: true, view: 'overall' };
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
  const model = buildHarness(scene, data);
  const board = await loadBoard(scene, data);
  // PCB labels is an inspection of the native board alone. A separate camera
  // layer keeps the lifted bench plug from covering the real silkscreen.
  board.root.traverse(item => item.layers.enable(1));
  scene.traverse(item => { if (item.isLight) item.layers.enable(1); });
  const pinMarker = new THREE.Mesh(new THREE.TorusGeometry(.9, .12, 6, 32), new THREE.MeshBasicMaterial({ color: 0xe98526, depthTest: false }));
  pinMarker.rotation.x = Math.PI / 2; pinMarker.layers.enable(1); pinMarker.renderOrder = 10; pinMarker.visible = false; scene.add(pinMarker);
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 1800);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.dampingFactor = .12;
  controls.minDistance = 8; controls.maxDistance = 850;
  controls.maxPolarAngle = Math.PI * .49; controls.zoomToCursor = true;
  let frame = 0, visible = true, transition = null, openedEnds = null;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const vec = p => new THREE.Vector3(...p);
  const recordFor = () => records.find(row => row.id === state.selection);

  function requestRender() { if (!frame && visible) frame = requestAnimationFrame(render); }
  function showStage() {
    const bounds = stage.getBoundingClientRect();
    if (bounds.top < 55 || bounds.bottom > innerHeight) stage.scrollIntoView({ block: 'start', behavior: reduced.matches ? 'instant' : 'smooth' });
  }
  function moveCamera(target, position, immediate = false) {
    if (immediate || reduced.matches) {
      transition = null; camera.position.copy(position); controls.target.copy(target); controls.update();
    } else transition = { start: performance.now(), from: camera.position.clone(), fromTarget: controls.target.clone(), to: position, target };
    requestRender();
  }
  function fit(bounds, direction, immediate = false, padding = 1.12) {
    const target = bounds.getCenter(new THREE.Vector3());
    const normal = vec(direction).normalize();
    const right = new THREE.Vector3().crossVectors(camera.up, normal).normalize();
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
    camera.layers.set(name === 'pcb' ? 1 : 0);
    light.castShadow = name !== 'pcb';
    if (name === 'pcb') {
      fit(board.bounds, [data.id === 'J13' ? -.4 : .4, 1, .65], immediate, 1.15);
    } else if (name === 'connector') {
      fit(model.boundsFor('connector'), [-1, .8, 1], immediate, 1.12);
    } else {
      const bounds = state.opened
        ? new THREE.Box3(vec([-113, 0, -18]), vec([120, 36, 18]))
        : new THREE.Box3().setFromObject(model.root).union(board.bounds);
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

  function partInfo(key) {
    if (key === 'pcb') return [`Native PCB · ${data.id}`, 'The actual header mesh and original fabrication pixels, cropped from the machine’s PCB. Use PCB labels to read its printed silkscreen.', [['Header', `${data.id} · ${data.name}`], ['Mating direction', 'Vertical top entry · plug shown lifted above it']]];
    if (key === 'connector') return [`${data.housing} JST plug`, data.id === 'J2' ? 'Five contacts occupy cavities 1, 2, 4, 5 and 6. Cavity 3 / OUT4 stays empty. The plug’s circuit-1 mark aligns with COM on the PCB.' : 'Four contacts occupy cavities 1–4. The plug’s circuit-1 mark aligns with AM2 on the PCB.', [['Housing', data.housing], ['Contact', data.contact], ['Pitch', `${data.pitchMm} mm`]]];
    if (key === 'dress') return ['Slip-on pieces', data.dress.description, [['Sleeve', data.dress.sleeve], ...(data.dress.collars ? [['Collars & ties', `${data.dress.collars} heat-shrink collars · ${data.dress.ties} zip ties`]] : [])]];
    if (key === 'wago') return ['One +12 V feed · four branches', 'The COM conductor enters one ferruled Wago port. Four separate ferruled wires leave for V-I, V-J, the fan and V-K. Each switched return runs directly to its own PCB output.', [['Block', 'Wago 221-415'], ['Wire ends', '5 separate bootlace ferrules'], ['Positive stock', '4 × 450 mm blanks · trim at fitting']]];
    if (key === 'pogo' || key === 'terminals') return data.id === 'J13' ? ['Fixed male pogo half', 'Four conductors terminate on four individual solder tails. Each joint receives its own heat-shrink sleeve. The marked end is the machine −X end.', [['Order from +X', 'AM2 · AM1 · BM2 · BM1'], ['Pitch', '2.54 mm'], ['Ends', '4 soldered joints · 4 separate sleeves']]] : ['Far-end terminations', 'The COM feed and four positives use individual ferrules at the Wago. The three valves each receive positive and switched-return disconnects; both fan ends remain provisional.', [['Ferrules', '5'], ['Valve disconnects', '6'], ['Fan ends', '2 · interface provisional']]];
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
        ['Slip on before finishing', record.sharedDress ? 'Shared PET mesh · 2 heat-shrink collars · 2 zip ties around the four-wire trunk' : record.right === 'solder' ? 'One heat-shrink sleeve · covers this solder joint only' : 'No shared mesh on this branch'],
      ];
    } else {
      [title, detail, rows] = partInfo(key);
      const related = key === 'wago' ? records.filter(row => row.net === 'COM') : ['connector', 'pcb'].includes(key) ? records.filter(row => row.pin) : key === 'dress' ? records.filter(row => row.sharedDress || row.right === 'solder') : records;
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
      const hidden = !state.labels || !!state.opened || ['pcb', 'connector', 'end'].includes(state.view) || p.z > 1 || p.z < -1 || Math.abs(p.x) > 1.05 || Math.abs(p.y) > 1.05 || (state.step === 'cut' && !['ribbons', 'connector', 'pcb'].includes(label.key)) || (['jst', 'dress'].includes(state.step) && ['wago', 'FAN', 'OUT1', 'OUT2', 'OUT3', 'pogo'].includes(label.key));
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
      if (t === 1) transition = null;
    }
    const changing = controls.update();
    renderer.render(scene, camera); placeLabels();
    if (changing || transition) requestRender();
  }
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix();
    // Refitting follows a resize, never an ordinary conductor selection.
    view(state.view === 'end' ? 'overall' : state.view, true);
  }
  function update() {
    model.update(state);
    board.root.visible = !state.opened || openedEnds?.sourceIsPcb;
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
    root.dataset.harnessSelection = state.selection || '';
    root.dataset.harnessOpened = state.opened || '';
    requestRender();
  }
  function select(key) {
    if (state.opened) return;
    state.selection = state.selection === key ? null : key;
    tab('wires'); inspect(); update();
  }
  function closeConductor() {
    if (!state.opened) return;
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
  $('[data-harness-wires]').addEventListener('change', event => { state.reveal = event.target.checked; update(); });
  $('[data-harness-labels]').addEventListener('change', event => { state.labels = event.target.checked; requestRender(); });
  $('[data-harness-explode]').addEventListener('input', event => {
    state.explode = Number(event.target.value) / 100; $('[data-harness-explode-value]').textContent = `${event.target.value}%`; update();
  });
  $('[data-harness-reset]').addEventListener('click', () => {
    closeConductor(); state.step = null; state.selection = null; state.explode = 0; state.reveal = false; state.labels = true;
    $('[data-harness-labels]').checked = true; $('[data-harness-wires]').checked = false;
    $('[data-harness-explode]').value = 0; $('[data-harness-explode-value]').textContent = '0%';
    tab('wires'); inspect(); update(); view('overall');
  });
  const full = $('[data-harness-fullscreen]');
  full.addEventListener('click', async () => {
    try { if (document.fullscreenElement) await document.exitFullscreen(); else await $('.harness-workbench').requestFullscreen(); }
    catch { full.hidden = true; }
  });
  if (!document.fullscreenEnabled) full.hidden = true;
  document.addEventListener('fullscreenchange', () => { full.textContent = document.fullscreenElement === $('.harness-workbench') ? 'Close expanded view' : 'Expand'; resize(); });

  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
  let down = null;
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
  renderer.domElement.addEventListener('pointerdown', event => { down = [event.clientX, event.clientY]; });
  renderer.domElement.addEventListener('pointercancel', () => { down = null; });
  renderer.domElement.addEventListener('pointerup', event => {
    const click = down && Math.hypot(event.clientX - down[0], event.clientY - down[1]) <= 5;
    down = null; if (!click || state.opened) return;
    const hit = pick(event); if (hit) select(model.tagFor(hit.object));
  });
  renderer.domElement.addEventListener('pointermove', event => {
    if (down || state.opened) return;
    renderer.domElement.style.cursor = pick(event) ? 'pointer' : 'grab';
  });
  stage.addEventListener('keydown', event => {
    if (event.target !== stage || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', 'Home'].includes(event.key)) return;
    event.preventDefault(); transition = null;
    if (event.key === 'Home') { view('overall'); return; }
    const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
    if (event.key === 'ArrowLeft') spherical.theta -= .12;
    if (event.key === 'ArrowRight') spherical.theta += .12;
    if (event.key === 'ArrowUp') spherical.phi = Math.max(.02, spherical.phi - .12);
    if (event.key === 'ArrowDown') spherical.phi = Math.min(Math.PI * .48, spherical.phi + .12);
    if (['+', '=', '-'].includes(event.key)) spherical.radius = THREE.MathUtils.clamp(spherical.radius * (event.key === '-' ? 1.12 : .88), controls.minDistance, controls.maxDistance);
    camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update(); requestRender();
  });
  renderer.domElement.addEventListener('webglcontextlost', event => {
    event.preventDefault(); $('.harness-loading').hidden = false;
    $('.harness-loading').textContent = '3D graphics paused. Reload to restore the model; text connections and build instructions are available below.';
    root.classList.remove('is-interactive');
  });
  controls.addEventListener('change', requestRender);
  controls.addEventListener('start', () => { transition = null; });
  new ResizeObserver(resize).observe(stage);
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (visible) requestRender(); }).observe(stage);
  root.classList.add('is-interactive');
  $$('.harness-toolbar, .harness-scene-controls, .harness-tabs').forEach(element => { element.hidden = false; });
  $('.harness-loading').hidden = true;
  inspect(); update(); resize(); root.dataset.harnessReady = 'true';
}
