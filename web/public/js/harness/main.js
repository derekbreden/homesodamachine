import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { buildHarness } from './model.js';

const root = document.getElementById('j2-harness');
const data = JSON.parse(document.getElementById('j2-harness-data').textContent);
const stage = root.querySelector('.harness-stage');
const $ = selector => root.querySelector(selector);
const $$ = selector => [...root.querySelectorAll(selector)];
const state = { selection: null, step: null, reveal: false, explode: 0, labels: true, view: 'overall' };
const facts = items => {
  const dl = $('[data-harness-selection-facts]');
  dl.replaceChildren(...items.map(([term, description]) => {
    const row = document.createElement('div');
    const dt = document.createElement('dt'); dt.textContent = term;
    const dd = document.createElement('dd'); dd.textContent = description;
    row.append(dt, dd); return row;
  }));
};
function inspector(key) {
  const pin = data.pins.find(pin => pin.net === key);
  let title, detail, rows;
  if (pin) {
    title = `J2 ${pin.pin} · ${pin.net}`;
    detail = pin.detail;
    rows = [['Ribbon lead', `${pin.ribbon}${pin.conductor}${pin.stripe ? ' · white-striped insulation' : ''}`], ['Bench cut', pin.cutMm ? `${pin.cutMm} mm · trim at fitting` : 'Discard A3 · cavity empty'], ['Other end', pin.destination], ['Termination', pin.termination]];
  } else if (key === 'ribbons') {
    title = 'Two 3P ribbon blanks'; detail = 'Cut one 650 mm blank for A and one for B. Count from each white-striped edge before separating the leads; the map assigns each of the six stock conductors.';
    rows = [['Ribbon A', 'A1 stripe → COM; A2 → FAN; A3 discarded'], ['Ribbon B', 'B1 stripe → OUT3; B2 → OUT2; B3 → OUT1'], ['Short branch', 'Peel B1 / OUT3 off before the four-wire trunk']];
  } else if (key === 'connector') {
    title = 'The JST end'; detail = 'Six cavities at 2.5 mm pitch. Five female contacts seat from the wire side. The housing mark identifies cavity 1 / COM; cavity 3 is empty.';
    rows = [['Housing', data.housing], ['Contacts', `5 × ${data.contact}`], ['Populated cavities', '1, 2, 4, 5, 6']];
  } else if (key === 'dress') {
    title = 'Everything slipped over'; detail = data.dress.description;
    rows = [['Mesh', data.dress.sleeve], ['End finish', '2 heat-shrink collars + 2 zip ties'], ['Fit', 'Proposed dressing; keep the shared installed corridor bare']];
  } else if (key === 'wago') {
    title = 'One feed, four positives'; detail = 'All five Wago ports share +12 V. COM is the incoming feed; four separate bulk-wire branches supply the three valves and the fan. Switched returns bypass this block.';
    rows = [['Lever block', '1 × Wago 221-415'], ['Crimped feed ends', '5 individual bootlace ferrules'], ['Branch stock', '4 × 450 mm · trim per landing']];
  } else {
    title = 'The finished harness'; detail = 'JST-XH at the board, two 3P ribbons with white index stripes, a dressed four-wire trunk, a short V-K branch and a five-port positive fan-out.';
    rows = [['Board end', '1 × XHP-6 + 5 contacts'], ['Wire stock', '22 AWG · 3P + 3P'], ['Far end', '5 ferrules + 6 valve disconnects + 2 provisional fan ends']];
  }
  $('[data-harness-selection-title]').textContent = title;
  $('[data-harness-selection-detail]').textContent = detail;
  $('[data-harness-clear]').hidden = !key;
  facts(rows);
}

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.domElement.setAttribute('aria-label', '3D model of J2: five active black wires, striped COM and OUT3, braided sleeve, heat-shrink collars, zip ties, Wago fan-out and crimp terminals.');
renderer.domElement.setAttribute('role', 'img');
stage.prepend(renderer.domElement);
const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xf5f8ff, 0x71829e, 2.5));
const keyLight = new THREE.DirectionalLight(0xffffff, 3.5);
keyLight.position.set(-65, 160, -100);
keyLight.castShadow = true;
Object.assign(keyLight.shadow.camera, { left: -160, right: 160, top: 120, bottom: -120, near: 1, far: 500 });
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.bias = -.0005;
scene.add(keyLight);
const fill = new THREE.DirectionalLight(0xcbdcff, 1.8);
fill.position.set(70, 60, 110); scene.add(fill);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 400), new THREE.ShadowMaterial({ opacity: .12 }));
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
const grid = new THREE.GridHelper(500, 50, 0x97aecf, 0xa6bad6);
grid.material.transparent = true; grid.material.opacity = .22; grid.position.y = -.12; scene.add(grid);
const model = buildHarness(scene, data);
const camera = new THREE.PerspectiveCamera(33, 1, .1, 1500);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = .12;
controls.minDistance = 15; controls.maxDistance = 650;
controls.maxPolarAngle = Math.PI * .49;
controls.enablePan = true;
controls.zoomToCursor = true;
const cameraViews = {
  overall: { position: [142, 190, 205], target: [14, 2, -1] },
  top: { position: [14, 275, 0], target: [14, 2, -1] },
  connector: { position: [-60, 29, 25], target: [-92, 3.5, 0] },
};
let frame = 0, visible = true, transition = null;
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
function requestRender() { if (!frame && visible) frame = requestAnimationFrame(render); }
function view(name, immediate = false) {
  state.view = name;
  let goal = cameraViews[name];
  if (name === 'connector') {
    const bounds = new THREE.Box3().setFromObject(model.connector);
    const target = bounds.getCenter(new THREE.Vector3());
    const radius = bounds.getBoundingSphere(new THREE.Sphere()).radius;
    const distance = radius / Math.sin(THREE.MathUtils.degToRad(33 / 2)) * 1.2;
    const position = target.clone().addScaledVector(new THREE.Vector3(1.25, 1, 1.1).normalize(), distance);
    goal = { position: position.toArray(), target: target.toArray() };
  }
  $$('[data-harness-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessView === name)));
  if (immediate || reduced.matches) {
    transition = null;
    camera.position.fromArray(goal.position); controls.target.fromArray(goal.target); controls.update();
  } else {
    transition = { start: performance.now(), from: camera.position.clone(), fromTarget: controls.target.clone(), to: new THREE.Vector3(...goal.position), target: new THREE.Vector3(...goal.target) };
  }
  requestRender();
}
const labels = model.anchors.map(anchor => {
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'harness-label'; button.dataset.key = anchor.key;
  const name = document.createElement('span'); name.textContent = anchor.title;
  const detail = document.createElement('small'); detail.textContent = anchor.subtitle;
  button.append(name, detail);
  button.addEventListener('click', () => select(anchor.key));
  $('.harness-labels').append(button);
  return { ...anchor, button, vector: new THREE.Vector3(...anchor.point) };
});
function render(now) {
  frame = 0;
  if (transition) {
    const t = Math.min(1, (now - transition.start) / 450), ease = 1 - (1 - t) ** 3;
    camera.position.lerpVectors(transition.from, transition.to, ease);
    controls.target.lerpVectors(transition.fromTarget, transition.target, ease);
    if (t === 1) transition = null;
  }
  const changing = controls.update();
  renderer.render(scene, camera);
  const { width, height } = stage.getBoundingClientRect();
  const placed = [];
  for (const label of labels) {
    const p = label.vector.clone();
    if (label.key === 'dress') p.y += state.explode * 24;
    if (label.key === 'connector') p.x -= state.explode * 17;
    if (label.key === 'wago') p.y += state.explode * 14;
    p.project(camera);
    const hidden = !state.labels || p.z > 1 || p.z < -1 || Math.abs(p.x) > 1.08 || Math.abs(p.y) > 1.08 || (label.raw && state.step !== 'cut') || (state.step === 'cut' && !label.raw && label.key !== 'connector') || (['jst', 'dress'].includes(state.step) && ['wago', 'FAN', 'OUT1', 'OUT2', 'OUT3'].includes(label.key));
    label.button.hidden = hidden;
    if (hidden) continue;
    const w = label.button.offsetWidth, h = label.button.offsetHeight;
    let x = Math.max(w / 2 + 4, Math.min(width - w / 2 - 4, (p.x + 1) * width / 2));
    let y = Math.max(h + 5, Math.min(height - 16, (-p.y + 1) * height / 2 - 12));
    // Keep the projected labels readable when the whole harness is fitted to a phone.
    for (const prev of placed) if (Math.abs(x - prev.x) < (w + prev.w) / 2 + 4 && Math.abs(y - prev.y) < Math.max(h, prev.h) + 3) y = Math.min(height - 16, prev.y + h + 7);
    placed.push({ x, y, w, h });
    label.button.style.left = `${x}px`; label.button.style.top = `${y}px`;
  }
  if (changing || transition) requestRender();
}
function resize() {
  const { width, height } = stage.getBoundingClientRect();
  if (!width || !height) return;
  renderer.setSize(width, height, false); camera.aspect = width / height;
  // Keep a whole bench piece in frame at narrow widths without crushing the desktop view.
  camera.fov = state.view === 'connector' ? 33 : Math.min(65, Math.max(33, 33 / camera.aspect * 1.65));
  camera.updateProjectionMatrix(); requestRender();
}
new ResizeObserver(resize).observe(stage);
new IntersectionObserver(entries => {
  visible = entries[0].isIntersecting;
  if (visible) requestRender();
}).observe(stage);
controls.addEventListener('change', requestRender);
controls.addEventListener('start', () => { transition = null; });
function update() {
  model.update(state);
  $$('[data-harness-pin]').forEach(button => button.setAttribute('aria-pressed', String(data.pins.find(pin => pin.pin === Number(button.dataset.harnessPin)).net === state.selection)));
  $$('[data-harness-row]').forEach(row => row.classList.toggle('is-selected', data.pins.find(pin => pin.pin === Number(row.dataset.harnessRow)).net === state.selection));
  labels.forEach(label => label.button.setAttribute('aria-pressed', String(label.key === state.selection)));
  requestRender();
}
function select(key) {
  state.selection = state.selection === key ? null : key;
  inspector(state.selection); update();
}
$$('[data-harness-pin], [data-harness-select]').forEach(button => button.addEventListener('click', () => select(data.pins.find(pin => pin.pin === Number(button.dataset.harnessPin || button.dataset.harnessSelect)).net)));
$('[data-harness-clear]').addEventListener('click', () => { state.selection = null; inspector(null); update(); });
$$('[data-harness-view]').forEach(button => button.addEventListener('click', () => { view(button.dataset.harnessView); resize(); }));
$('[data-harness-reset]').addEventListener('click', () => {
  state.explode = 0; state.reveal = false; state.selection = null;
  state.labels = true; $('[data-harness-labels]').checked = true;
  $('[data-harness-explode]').value = 0; $('[data-harness-explode-value]').textContent = '0%'; $('[data-harness-wires]').checked = false;
  showStep(null); view('overall'); resize();
});
$('[data-harness-wires]').addEventListener('change', event => { state.reveal = event.target.checked; update(); });
$('[data-harness-labels]').addEventListener('change', event => { state.labels = event.target.checked; requestRender(); });
$('[data-harness-explode]').addEventListener('input', event => {
  state.explode = Number(event.target.value) / 100;
  $('[data-harness-explode-value]').textContent = `${event.target.value}%`; update();
  if (state.view === 'connector') view('connector', true);
});
function showStep(id) {
  state.step = id; state.selection = null;
  const index = data.steps.findIndex(step => step.id === id), step = data.steps[index];
  $$('[data-harness-step]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.harnessStep === id)));
  $('[data-harness-finished]').setAttribute('aria-pressed', String(!id));
  const panel = $('.harness-step-detail'); panel.hidden = !step;
  if (step) {
    $('[data-harness-step-index]').textContent = `${index + 1} / ${data.steps.length} · ${step.minutes} min`;
    $('[data-harness-step-title]').textContent = step.title;
    $('[data-harness-step-copy]').textContent = step.instruction;
    $('[data-harness-prev]').disabled = index === 0;
    $('[data-harness-next]').textContent = index === data.steps.length - 1 ? 'Finished view' : 'Next step';
  }
  inspector(['connector', 'dress', 'ribbons'].includes(step?.focus) ? step.focus : null);
  update(); view(id === 'jst' ? 'connector' : 'overall'); resize();
}
$$('[data-harness-step]').forEach(button => button.addEventListener('click', () => showStep(button.dataset.harnessStep)));
$('[data-harness-finished]').addEventListener('click', () => showStep(null));
$('[data-harness-prev]').addEventListener('click', () => showStep(data.steps[data.steps.findIndex(step => step.id === state.step) - 1]?.id || null));
$('[data-harness-next]').addEventListener('click', () => showStep(data.steps[data.steps.findIndex(step => step.id === state.step) + 1]?.id || null));
let matingFace = false;
$('[data-harness-face]').addEventListener('click', () => {
  matingFace = !matingFace;
  $('.harness-pin-strip').replaceChildren(...[...$$('[data-harness-pin]')].reverse());
  $('.harness-pin-strip').setAttribute('aria-label', `J2 cavities, ${matingFace ? 'mating-face' : 'wire-entry'} view`);
  $('[data-harness-face-label]').textContent = matingFace ? 'Mating-face view · circuit 1 mark at the right · order is mirrored' : 'Wire-entry view · orient the circuit 1 mark to the left';
  $('[data-harness-face]').textContent = matingFace ? 'Show wire entry' : 'Show mating face';
});
const full = $('[data-harness-fullscreen]');
full.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await $('.harness-visual').requestFullscreen();
  } catch { full.hidden = true; }
});
if (!document.fullscreenEnabled) full.hidden = true;
document.addEventListener('fullscreenchange', () => { full.textContent = document.fullscreenElement ? 'Close expanded view' : 'Expand'; resize(); });
const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
let down = null;
renderer.domElement.addEventListener('pointerdown', event => { down = [event.clientX, event.clientY]; });
renderer.domElement.addEventListener('pointerup', event => {
  if (!down || Math.hypot(event.clientX - down[0], event.clientY - down[1]) > 5) return;
  down = null;
  const bounds = stage.getBoundingClientRect();
  pointer.set((event.clientX - bounds.left) / bounds.width * 2 - 1, -(event.clientY - bounds.top) / bounds.height * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(model.pickables).find(hit => {
    for (let item = hit.object; item; item = item.parent) if (!item.visible) return false;
    return true;
  });
  if (hit) select(model.tagFor(hit.object));
});
stage.addEventListener('keydown', event => {
  if (event.target !== stage) return;
  const keys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', 'Home'];
  if (!keys.includes(event.key)) return;
  event.preventDefault(); transition = null;
  if (event.key === 'Home') { view('overall'); resize(); return; }
  const offset = camera.position.clone().sub(controls.target), spherical = new THREE.Spherical().setFromVector3(offset);
  if (event.key === 'ArrowLeft') spherical.theta -= .12;
  if (event.key === 'ArrowRight') spherical.theta += .12;
  if (event.key === 'ArrowUp') spherical.phi = Math.max(.02, spherical.phi - .12);
  if (event.key === 'ArrowDown') spherical.phi = Math.min(Math.PI * .48, spherical.phi + .12);
  if (['+', '=', '-'].includes(event.key)) spherical.radius = THREE.MathUtils.clamp(spherical.radius * (event.key === '-' ? 1.12 : .88), controls.minDistance, controls.maxDistance);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update(); requestRender();
});
renderer.domElement.addEventListener('webglcontextlost', event => {
  event.preventDefault(); $('.harness-loading').textContent = '3D graphics paused. Reload to restore the model; the complete wire map and instructions remain available below.'; $('.harness-loading').hidden = false;
});
root.classList.add('is-interactive');
$$('.harness-toolbar, .harness-scene-controls, [data-harness-finished], [data-harness-face]').forEach(element => { element.hidden = false; });
$('.harness-loading').hidden = true;
view('overall', true); resize(); update();
root.dataset.harnessReady = 'true';
