import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { toCreasedNormals, mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { RectAreaLightUniformsLib } from 'three/examples/jsm/lights/RectAreaLightUniformsLib.js';
import { FullScreenQuad } from 'three/examples/jsm/postprocessing/Pass.js';

// The same CAD surface as the still render. Movement gets an immediate studio
// preview; the stationary view accumulates actual bounced light, then sleeps.
export function mountStudio(root, { parts, ...model }, theme) {
  const find = selector => root.querySelector(selector);
  const stage = find('[data-stage]');
  const soft = find('[data-soft]');
  const status = find('[data-status]');
  const coarse = matchMedia('(pointer: coarse)').matches;
  const setStatus = text => { if (status.textContent !== text) status.textContent = text; };
  const themeColor = token => {
    const p = theme.rgba(token);
    return new THREE.Color(p[0] / 255, p[1] / 255, p[2] / 255).convertSRGBToLinear();
  };
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
  } catch (error) {
    find('[data-loading]').textContent = '3D could not open in this browser.';
    for (const button of root.querySelectorAll('button, input')) button.disabled = true;
    setStatus('The still image remains available.');
    return;
  }
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = .85;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  stage.append(renderer.domElement);
  RectAreaLightUniformsLib.init();

  const scene = new THREE.Scene();
  const modelGroup = new THREE.Group();
  scene.add(modelGroup);
  const materials = [];
  const batches = new Map();
  const materialCache = new Map();
  const decode = (base64, Type) => {
    const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
    return new Type(bytes.buffer);
  };
  for (const part of parts) {
    const indexed = new THREE.BufferGeometry();
    indexed.setAttribute('position', new THREE.BufferAttribute(typeof part.positions === 'string' ? decode(part.positions, Float32Array) : part.positions, 3));
    indexed.setIndex(new THREE.BufferAttribute(typeof part.indices === 'string' ? decode(part.indices, Uint16Array) : part.indices, 1));
    if (part.normals) indexed.setAttribute('normal', new THREE.BufferAttribute(part.normals, 3));
    const geometry = part.normals ? indexed : toCreasedNormals(indexed, THREE.MathUtils.degToRad(32));
    if (geometry !== indexed) indexed.dispose();
    // CAD is Z-up in millimetres; both subjects share the same Y-up studio.
    geometry.rotateX(-Math.PI / 2);
    const scale = model.scale ?? .1;
    geometry.scale(scale, scale, scale);
    const key = part.color ? JSON.stringify([part.color, part.finish, part.visibility]) : part.name;
    let material = materialCache.get(key);
    if (!material) {
      const color = part.color ? new THREE.Color(...part.color) : part.name === 'release_collet' ? new THREE.Color(.59, .66, .63) : new THREE.Color(.72, .77, .74);
      material = new THREE.MeshPhysicalMaterial({ color, metalness: 0, roughness: .28, ior: 1.46, ...part.finish });
      material.userData.visibility = part.visibility;
      // Keep cutaway surfaces in one BVH. Opacity changes expose the interior
      // without rebuilding a million-triangle scene on every panel toggle.
      if (part.visibility) material.transparent = true;
      materials.push(material); materialCache.set(key, material);
    }
    if (!batches.has(key)) batches.set(key, { geometries: [], names: [], material });
    const batch = batches.get(key);
    batch.geometries.push(geometry); batch.names.push(part.name);
  }
  for (const batch of batches.values()) {
    const geometry = batch.geometries.length === 1 ? batch.geometries[0] : mergeGeometries(batch.geometries);
    if (batch.geometries.length > 1) for (const original of batch.geometries) original.dispose();
    const mesh = new THREE.Mesh(geometry, batch.material);
    mesh.name = batch.names.join(', ');
    mesh.userData.visibility = batch.material.userData.visibility;
    mesh.userData.components = batch.names;
    mesh.castShadow = mesh.receiveShadow = true;
    modelGroup.add(mesh);
  }
  let bounds = new THREE.Box3().setFromObject(modelGroup);
  const center = bounds.getCenter(new THREE.Vector3());
  modelGroup.position.set(-center.x, -bounds.min.y, -center.z);
  modelGroup.updateMatrixWorld(true);
  bounds = new THREE.Box3().setFromObject(modelGroup);
  const target = bounds.getCenter(new THREE.Vector3());
  const camera = new THREE.OrthographicCamera(-3, 3, 2, -2, .01, 100);
  camera.position.copy(target).add(new THREE.Vector3(...(model.homeDirection || [4.9, 5.7, 9.5])));
  camera.lookAt(target);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.copy(target);
  controls.enableDamping = true;
  controls.dampingFactor = .14;
  controls.screenSpacePanning = true;
  controls.minPolarAngle = .04;
  controls.maxPolarAngle = Math.PI / 2 - .015;
  controls.minZoom = .4;
  controls.maxZoom = 6;
  controls.zoomSpeed = .85;
  controls.rotateSpeed = .65;
  controls.touches.TWO = THREE.TOUCH.DOLLY_PAN;
  const homePosition = camera.position.clone();
  const homeTarget = target.clone();

  const floorMaterial = new THREE.MeshStandardMaterial({ roughness: .78, metalness: 0 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -.012;
  floor.receiveShadow = true;
  scene.add(floor);
  // A deliberately broad neutral key makes the shape legible in both renderers.
  const key = new THREE.RectAreaLight(0xffffff, 7, 6, 5);
  key.position.set(-2, 6, 3); key.lookAt(target); scene.add(key);
  const fill = new THREE.RectAreaLight(0xdbe6ff, 2, 5, 4);
  fill.position.set(5, 3, -4); fill.lookAt(target); scene.add(fill);
  const rim = new THREE.RectAreaLight(0xffffff, 3, 4, 3);
  rim.position.set(-5, 3, -1); rim.lookAt(target); scene.add(rim);
  if (model.assembly) {
    // Keep softboxes above the camera's orbit so reverse views show the
    // assembly and its floor without looking directly into a light panel.
    key.position.set(-6, 30, 9); key.intensity = 12; key.width = 24; key.height = 20; key.lookAt(target);
    fill.position.set(15, 26, -12); fill.intensity = 2.5; fill.width = 20; fill.height = 16; fill.lookAt(target);
    rim.position.set(-15, 26, -3); rim.intensity = 5; rim.width = 16; rim.height = 12; rim.lookAt(target);
    const bounce = new THREE.RectAreaLight(0xe7efff, 7, 30, 22);
    bounce.position.set(0, 26, 40); bounce.lookAt(target); scene.add(bounce);
  }
  const previewKey = new THREE.DirectionalLight(0xffffff, 1.1);
  previewKey.position.set(-2, 6, 3);
  previewKey.castShadow = true;
  previewKey.shadow.mapSize.set(coarse ? 1024 : 2048, coarse ? 1024 : 2048);
  Object.assign(previewKey.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .1, far: 20 });
  previewKey.shadow.bias = -.00015;
  previewKey.shadow.normalBias = .008;
  previewKey.shadow.radius = 4;
  scene.add(previewKey);
  const previewFill = new THREE.HemisphereLight(0xe3edff, 0x667584, .35);
  scene.add(previewFill);
  previewKey.userData.preview = previewFill.userData.preview = true;

  let tracer = null;
  let tracedScene = null;
  let bvhWorker = null;
  let preparing = false;
  let denoiser = null;
  let displayedSamples = -1;
  let raf = 0;
  let moving = false;
  let lastMove = performance.now();
  let visible = true;
  let disposed = false;
  let firstFrame = true;
  let refinementFailed = false;
  const maxSamples = coarse ? 96 : 160;
  function requestDraw() {
    if (!raf && !disposed && visible && !document.hidden) raf = requestAnimationFrame(draw);
  }
  function updatePalette() {
    const hsl = {};
    const floorColor = themeColor('blue');
    floorColor.getHSL(hsl);
    floorColor.setHSL(hsl.h, .28, .09);
    floorMaterial.color.copy(floorColor);
    scene.background = floorColor.clone().multiplyScalar(.8);
    if (tracedScene) tracedScene.background = scene.background;
    if (tracer && !preparing) { tracer.updateEnvironment(); tracer.updateMaterials(); }
    requestDraw();
  }
  updatePalette();
  const stopTheme = theme.observe(updatePalette);
  function frame(aspect) {
    camera.updateMatrixWorld(true);
    const projected = new THREE.Box3();
    // Frame the actual surface rather than the empty corners of its bounding box.
    const point = new THREE.Vector3();
    modelGroup.traverse(mesh => {
      if (!mesh.geometry) return;
      const transform = new THREE.Matrix4().multiplyMatrices(camera.matrixWorldInverse, mesh.matrixWorld);
      const positions = mesh.geometry.attributes.position;
      for (let i = 0; i < positions.count; i++) projected.expandByPoint(point.fromBufferAttribute(positions, i).applyMatrix4(transform));
    });
    const size = projected.getSize(new THREE.Vector3());
    return { height: Math.max(size.y, size.x / aspect) * 1.18, center: projected.getCenter(new THREE.Vector3()) };
  }
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    if (width < 1 || height < 1) return;
    const aspect = width / height;
    const pixelRatio = Math.min(devicePixelRatio || 1, model.assembly && coarse ? 1.3 : 1.6, Math.sqrt(1250000 / (width * height)));
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(width, height, false);
    // Preserve the user's zoom and target through Safari's changing address bar.
    const old = camera.position.clone(), oldTarget = controls.target.clone();
    camera.position.copy(homePosition); camera.lookAt(homeTarget); camera.updateMatrixWorld(true);
    const framed = frame(aspect), h = framed.height, c = framed.center;
    camera.top = c.y + h / 2; camera.bottom = c.y - h / 2;
    camera.left = c.x - h * aspect / 2; camera.right = c.x + h * aspect / 2;
    camera.position.copy(old); camera.lookAt(oldTarget); camera.updateProjectionMatrix();
    if (!preparing) tracer?.updateCamera();
    lastMove = performance.now(); requestDraw();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(stage);
  function failRefinement(error) {
    if (refinementFailed || disposed) return;
    refinementFailed = true;
    preparing = false;
    bvhWorker?.dispose(); bvhWorker = null;
    soft.checked = false; soft.disabled = true;
    tracer?.dispose(); tracer = null;
    denoiser?.material.dispose(); denoiser?.dispose(); denoiser = null;
    root.dataset.quality = 'studio';
    setStatus('Studio lighting');
    console.warn('Soft-light refinement unavailable; interactive studio view retained.', error);
    requestDraw();
  }
  renderer.debug.onShaderError = (gl, program, vertex, fragment) => {
    failRefinement(new Error(gl.getProgramInfoLog(program) || gl.getShaderInfoLog(fragment) || gl.getShaderInfoLog(vertex)));
  };
  function draw(now) {
    raf = 0;
    const changed = controls.update();
    const live = moving || now - lastMove < 220;
    try {
      if (!tracer || preparing || !soft.checked || live || refinementFailed) {
        renderer.render(scene, camera);
        if (!refinementFailed) setStatus(live ? 'Move to explore' : preparing ? 'Preparing soft light…' : 'Studio lighting');
        root.dataset.phase = live ? 'moving' : 'ready';
      } else {
        tracer.renderSample();
        const wholeSamples = Math.floor(tracer.samples);
        if (tracer.samples < 3) {
          renderer.render(scene, camera);
        } else if (wholeSamples !== displayedSamples) {
          denoiser.material.map = tracer.target.texture;
          denoiser.render(renderer);
          displayedSamples = wholeSamples;
        }
        const done = tracer.samples >= maxSamples;
        root.dataset.phase = done ? 'ready' : 'refining';
        setStatus(done ? 'Soft light' : 'Refining light…');
      }
    } catch (error) { failRefinement(error); renderer.render(scene, camera); }
    if (firstFrame) {
      firstFrame = false;
      find('[data-poster]')?.setAttribute('hidden', '');
      find('[data-loading]')?.setAttribute('hidden', '');
      root.dataset.ready = 'true';
    }
    if (changed || live || (tracer && !preparing && soft.checked && tracer.samples < maxSamples)) requestDraw();
  }
  controls.addEventListener('start', () => { moving = true; lastMove = performance.now(); requestDraw(); });
  controls.addEventListener('end', () => { moving = false; lastMove = performance.now(); requestDraw(); });
  controls.addEventListener('change', () => {
    lastMove = performance.now();
    displayedSamples = -1;
    if (!preparing) tracer?.updateCamera();
    requestDraw();
  });
  function setMode(value) {
    controls.mouseButtons.LEFT = value === 'pan' ? THREE.MOUSE.PAN : THREE.MOUSE.ROTATE;
    controls.touches.ONE = value === 'pan' ? THREE.TOUCH.PAN : THREE.TOUCH.ROTATE;
    for (const button of root.querySelectorAll('[data-mode]')) button.setAttribute('aria-pressed', String(button.dataset.mode === value));
    find('[data-help]').textContent = coarse
      ? `One finger to ${value === 'pan' ? 'pan' : 'rotate'} · pinch to zoom · two fingers to pan`
      : `Drag to ${value === 'pan' ? 'pan' : 'rotate'} · scroll to zoom · right-drag to pan`;
  }
  for (const button of root.querySelectorAll('[data-mode]')) button.addEventListener('click', () => setMode(button.dataset.mode));
  function invalidate() { displayedSamples = -1; lastMove = performance.now(); if (!preparing) tracer?.updateCamera(); requestDraw(); }
  for (const button of root.querySelectorAll('[data-zoom]')) button.addEventListener('click', () => {
    camera.zoom = THREE.MathUtils.clamp(camera.zoom * (button.dataset.zoom === 'in' ? 1.22 : 1 / 1.22), controls.minZoom, controls.maxZoom);
    camera.updateProjectionMatrix(); invalidate();
  });
  function resetCamera() {
    // Drain any inertial movement before restoring the saved camera.
    controls.enableDamping = false; controls.update();
    controls.target.copy(homeTarget); camera.position.copy(homePosition); camera.zoom = 1;
    camera.updateProjectionMatrix(); controls.update(); controls.enableDamping = true;
    setMode('rotate'); invalidate();
  }
  find('[data-reset]').addEventListener('click', resetCamera);
  function applyCutaway(turn = false) {
    const view = find('[data-cutaway]')?.value || 'closed';
    const core = find('[data-core]')?.checked ?? true;
    const hidden = new Set(view === 'front' ? ['front-top', 'front-bottom'] : view === 'rear' ? ['back-top', 'back-bottom'] : view === 'open' ? ['front-top', 'front-bottom', 'back-top', 'back-bottom'] : []);
    if (!core) hidden.add('core');
    for (const mesh of modelGroup.children) {
      const shown = !hidden.has(mesh.userData.visibility);
      mesh.visible = shown;
      if (mesh.userData.visibility) {
        mesh.material.opacity = shown ? 1 : 0;
        mesh.material.depthWrite = shown;
      }
    }
    root.dataset.view = view;
    const note = find('[data-view-note]');
    if (note) note.textContent = `${view === 'front' ? 'Front two panels hidden.' : view === 'rear' ? 'Rear two panels hidden.' : view === 'open' ? 'All four shell panels hidden.' : 'All four shell panels fitted.'} Core insulation ${core ? 'fitted' : 'hidden'}.`;
    if (!preparing) tracer?.updateMaterials();
    if (turn) {
      const direction = view === 'rear' ? new THREE.Vector3(-4.9, 5.7, -9.5) : new THREE.Vector3(4.9, 5.7, 9.5);
      homePosition.copy(homeTarget).add(direction);
      resetCamera(); resize();
    } else invalidate();
  }
  find('[data-cutaway]')?.addEventListener('change', () => applyCutaway(true));
  find('[data-core]')?.addEventListener('change', () => applyCutaway());
  soft.addEventListener('change', () => { displayedSamples = -1; tracer?.reset(); requestDraw(); });
  function visibilityChanged() { if (document.hidden) { cancelAnimationFrame(raf); raf = 0; } else requestDraw(); }
  document.addEventListener('visibilitychange', visibilityChanged);
  const intersection = new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (visible) requestDraw(); else { cancelAnimationFrame(raf); raf = 0; }
  });
  intersection.observe(stage);
  applyCutaway(); setMode('rotate'); resize(); controls.update(); requestDraw();

  // This version uses WebGL 2 on both desktop Safari and iOS; it does not
  // require WebGPU, a native app or the installation of an AR viewer.
  import('https://esm.sh/three-gpu-pathtracer@0.0.24?external=three,three-mesh-bvh').then(async ({ WebGLPathTracer, DenoiseMaterial }) => {
    if (disposed || refinementFailed) return;
    if (!renderer.extensions.has('EXT_color_buffer_float')) throw new Error('Floating-point targets unavailable');
    tracer = new WebGLPathTracer(renderer);
    tracer.bounces = 5;
    tracer.filterGlossyFactor = .5;
    tracer.tiles.set(coarse ? 3 : 2, coarse ? 3 : 2);
    tracer.renderScale = coarse ? model.assembly ? .65 : .8 : 1;
    tracer.renderDelay = 220;
    tracer.minSamples = coarse ? 3 : 5;
    tracer.fadeDuration = 350;
    tracer.textureSize.set(128, 128);
    tracer.renderToCanvas = false;
    denoiser = new FullScreenQuad(new DenoiseMaterial({ sigma: 2.5, kSigma: 1, threshold: .12 }));
    // Share geometry/materials with a static tracing scene. Its complete shell
    // stays available while the preview changes mesh visibility during a cutaway.
    tracedScene = scene.clone();
    tracedScene.traverse(object => {
      if (object.isMesh) object.visible = true;
      if (object.userData.preview) object.visible = false;
    });
    if (model.assembly) {
      preparing = true; requestDraw();
      const { createBVHWorker } = await import('./bvh-worker-client.js');
      if (disposed) return;
      bvhWorker = createBVHWorker(); tracer.setBVHWorker(bvhWorker);
      await tracer.setSceneAsync(tracedScene, camera);
      bvhWorker.dispose(); bvhWorker = null; preparing = false;
    } else tracer.setScene(tracedScene, camera);
    if (disposed || refinementFailed) return;
    applyCutaway();
    root.dataset.quality = 'soft';
    requestDraw();
  }).catch(failRefinement);

  // Small inspection surface for this prototype's browser checks.
  const inspection = { camera, controls, renderer, scene, get samples() { return tracer?.samples || 0; }, get refining() { return Boolean(tracer && soft.checked); } };
  root.studio = inspection;
  return {
    dispose() {
      disposed = true; cancelAnimationFrame(raf); stopTheme(); resizeObserver.disconnect(); intersection.disconnect();
      document.removeEventListener('visibilitychange', visibilityChanged); controls.dispose(); bvhWorker?.dispose(); tracer?.dispose();
      denoiser?.material.dispose(); denoiser?.dispose();
      scene.traverse(object => { object.geometry?.dispose(); });
      for (const material of [...materials, floorMaterial]) material.dispose();
      renderer.dispose(); renderer.domElement.remove();
    },
  };
}
