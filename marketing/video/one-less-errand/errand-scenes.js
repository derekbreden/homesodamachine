const clamp = (v) => Math.max(0, Math.min(1, v));
const ease = (v) => { const t = clamp(v); return t * t * (3 - 2 * t); };
const progress = (t, a, b) => ease((t - a) / (b - a));
const lerp = (a, b, t) => a + (b - a) * t;

export async function createErrandScenes({ THREE, width = 1920, height = 1080, palette = {} }) {
  const color = { cobalt: '#1749D1', ice: '#DCE6FF', orange: '#FF9152', white: '#FFFFFF', ...palette };
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: false });
  renderer.setSize(width, height, false);
  renderer.setPixelRatio(1);
  renderer.setClearColor(color.cobalt, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-9.6, 9.6, 5.4, -5.4, 0.1, 100);
  camera.position.set(0, 7.5, 20);
  camera.lookAt(0, 0.35, 0);
  scene.add(new THREE.HemisphereLight(0xeef4ff, 0xdce6ff, 0.90));
  const key = new THREE.DirectionalLight(0xfff5e9, 2.5);
  key.position.set(-4, 14, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -10; key.shadow.camera.right = 10;
  key.shadow.camera.top = 10; key.shadow.camera.bottom = -10;
  key.shadow.normalBias = 0.03;
  key.shadow.bias = -0.0002;
  key.shadow.radius = 4;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xe1ebff, 1.7);
  fill.position.set(7, 6, -5);
  scene.add(fill);
  const front = new THREE.DirectionalLight(0xffffff, 0.55);
  front.position.set(-1, 2, 15);
  scene.add(front);

  const studio = new THREE.Scene();
  studio.background = new THREE.Color('#66718b');
  const softbox = (x, y, z, w, h, intensity = 3) => {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(intensity, intensity, intensity), side: THREE.DoubleSide }));
    panel.position.set(x, y, z); panel.lookAt(0, 1, 0); studio.add(panel);
  };
  softbox(-5, 5, 7, 5, 12, 4);
  softbox(7, 4, 3, 3, 10, 2);
  softbox(0, 9, -3, 8, 6, 4);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environment = pmrem.fromScene(studio, 0.1);
  scene.environment = environment.texture;
  const mat = (c, roughness = 0.42, metalness = 0) => new THREE.MeshStandardMaterial({ color: c, roughness, metalness });
  const enamel = mat('#F3F0E8', 0.25, 0.22);
  const aluminum = mat('#E9EEF4', 0.23, 0.96);
  const brushed = mat('#CBD2DB', 0.4, 0.9);
  const orange = mat(color.orange, 0.42, 0.12);
  const ice = mat(color.ice, 0.44, 0.02);
  const white = mat('#F7F5F0', 0.46);
  const pale = mat('#CDD8F0', 0.55);
  const dark = mat('#525A6E', 0.65);
  const rubber = mat('#303B51', 0.72);
  const glass = mat('#92B0F1', 0.18, 0.32);
  const shadowMaterial = new THREE.ShadowMaterial({ color: '#133CAF', opacity: 0.14 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), shadowMaterial);
  floor.rotation.x = -Math.PI / 2; floor.position.y = -3.55; floor.receiveShadow = true; scene.add(floor);

  function mesh(geo, material, parent, x = 0, y = 0, z = 0) {
    const object = new THREE.Mesh(geo, material);
    object.position.set(x, y, z); object.castShadow = true; object.receiveShadow = true;
    parent.add(object); return object;
  }
  function roundedGeometry(w, h, d, r = 0.07) {
    r = Math.min(r, w / 5, h / 5, d / 3);
    const x = -w / 2 + r, y = -h / 2 + r, iw = w - 2 * r, ih = h - 2 * r;
    const q = Math.min(r, iw / 3, ih / 3);
    const shape = new THREE.Shape();
    shape.moveTo(x + q, y); shape.lineTo(x + iw - q, y);
    shape.quadraticCurveTo(x + iw, y, x + iw, y + q);
    shape.lineTo(x + iw, y + ih - q); shape.quadraticCurveTo(x + iw, y + ih, x + iw - q, y + ih);
    shape.lineTo(x + q, y + ih); shape.quadraticCurveTo(x, y + ih, x, y + ih - q);
    shape.lineTo(x, y + q); shape.quadraticCurveTo(x, y, x + q, y);
    const geo = new THREE.ExtrudeGeometry(shape, { depth: d - 2 * r, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: r, bevelThickness: r, curveSegments: 5 });
    geo.translate(0, 0, -d / 2 + r); geo.computeVertexNormals(); return geo;
  }
  const box = (w, h, d, material, parent, x = 0, y = 0, z = 0, r = 0.07) => mesh(roundedGeometry(w, h, d, r), material, parent, x, y, z);
  const cyl = (r, h, material, parent, x = 0, y = 0, z = 0, segments = 48) => mesh(new THREE.CylinderGeometry(r, r, h, segments), material, parent, x, y, z);
  function pipe(points, radius, material, parent) {
    const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
    return mesh(new THREE.TubeGeometry(curve, Math.max(8, points.length * 6), radius, 8, false), material, parent);
  }
  const profile = [[0.53, 0], [0.59, 0.02], [0.62, 0.08], [0.65, 0.17], [0.70, 0.30], [0.705, 2.22], [0.69, 2.36], [0.65, 2.46], [0.60, 2.55], [0.59, 2.60]];
  const canBody = new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(r, y)), 72);
  const canUV = canBody.attributes.uv, canVertices = canBody.attributes.position;
  for (let i = 0; i < canUV.count; i++) canUV.setY(i, canVertices.getY(i) / 2.6);
  const beadGeometry = new THREE.TorusGeometry(0.589, 0.034, 8, 64);
  const bottomGeometry = new THREE.TorusGeometry(0.578, 0.030, 8, 64);
  const diskGeometry = new THREE.CylinderGeometry(0.572, 0.572, 0.034, 64);
  const grooveGeometry = new THREE.TorusGeometry(0.477, 0.009, 6, 64);
  const rivetGeometry = new THREE.SphereGeometry(0.046, 12, 8);
  const tabShape = new THREE.Shape();
  tabShape.absellipse(0, 0, 0.115, 0.20, 0, Math.PI * 2, false, 0);
  const tabHole = new THREE.Path(); tabHole.absellipse(0, -0.045, 0.057, 0.087, 0, Math.PI * 2, true, 0);
  tabShape.holes.push(tabHole);
  const tabGeometry = new THREE.ExtrudeGeometry(tabShape, { depth: 0.027, bevelEnabled: true, bevelSize: 0.013, bevelThickness: 0.009, bevelSegments: 2, steps: 1, curveSegments: 24 });
  tabGeometry.rotateX(-Math.PI / 2);
  const labelCanvas = document.createElement('canvas'); labelCanvas.width = 1024; labelCanvas.height = 1024;
  const lc = labelCanvas.getContext('2d');
  lc.fillStyle = '#F3F0E8'; lc.fillRect(0, 0, 1024, 1024);
  lc.fillStyle = color.orange;
  for (const x of [0, 512, 1024]) { lc.beginPath(); lc.arc(x, 560, 158, 0, Math.PI * 2); lc.fill(); }
  lc.fillStyle = color.ice;
  for (const x of [0, 512, 1024]) for (const [dx, dy, r] of [[-80, -193, 22], [65, -245, 37], [118, -159, 15]]) { lc.beginPath(); lc.arc(x + dx, 540 + dy, r, 0, Math.PI * 2); lc.fill(); }
  const label = new THREE.CanvasTexture(labelCanvas); label.colorSpace = THREE.SRGBColorSpace;
  label.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
  const canPaint = enamel.clone(); canPaint.map = label;
  function makeCan() {
    const g = new THREE.Group();
    mesh(canBody, canPaint, g);
    const top = mesh(beadGeometry, aluminum, g, 0, 2.61, 0); top.rotation.x = Math.PI / 2;
    const bottom = mesh(bottomGeometry, aluminum, g, 0, 0.05, 0); bottom.rotation.x = Math.PI / 2;
    mesh(diskGeometry, brushed, g, 0, 2.604, 0);
    const groove = mesh(grooveGeometry, aluminum, g, 0, 2.626, 0); groove.rotation.x = Math.PI / 2;
    const tab = mesh(tabGeometry, aluminum, g, 0, 2.638, 0.016); tab.rotation.y = -0.12;
    mesh(rivetGeometry, aluminum, g, 0, 2.668, -0.105).scale.y = 0.3;
    return g;
  }
  const hero = makeCan(); scene.add(hero);
  const pack = new THREE.Group(); scene.add(pack);
  const packCans = [];
  for (let row = 0; row < 3; row++) for (let column = 0; column < 4; column++) {
    const can = makeCan(); can.position.set((column - 1.5) * 1.42, 0.14, (row - 1) * 1.42); can.rotation.y = 0.13 * ((column + row) % 2);
    can.userData.grid = can.position.clone(); pack.add(can); packCans.push(can);
  }
  const tray = new THREE.Group(); pack.add(tray);
  box(5.95, 0.18, 4.5, ice, tray, 0, 0.08, 0);
  box(5.95, 0.67, 0.10, ice, tray, 0, 0.43, 2.22);
  box(5.95, 0.67, 0.10, ice, tray, 0, 0.43, -2.22);
  box(0.10, 0.67, 4.5, ice, tray, -2.925, 0.43, 0);
  box(0.10, 0.67, 4.5, ice, tray, 2.925, 0.43, 0);
  box(1.35, 0.08, 0.115, orange, tray, 0, 0.49, 2.28, 0.023);

  const cart = new THREE.Group(); scene.add(cart);
  const wire = mat('#ECF1FA', 0.33, 0.58);
  const basket = new THREE.Group(); cart.add(basket);
  for (let i = 0; i <= 8; i++) {
    const x = lerp(-3.13, 3.13, i / 8);
    pipe([[x, 1.34, -2.22], [x, -0.6, -1.7], [x, -0.6, 1.7], [x, 1.34, 2.22]], 0.031, wire, basket);
  }
  for (let j = 0; j <= 3; j++) {
    const y = lerp(-0.55, 1.32, j / 3), z = lerp(1.72, 2.22, j / 3);
    pipe([[-3.13, y, -z], [-3.13, y, z], [3.13, y, z], [3.13, y, -z], [-3.13, y, -z]], 0.038, wire, basket);
  }
  pipe([[-3.3, -0.75, -1.45], [2.7, -0.75, -1.45], [3.6, 1.8, -1.45], [4.0, 1.8, -1.45]], 0.07, wire, cart);
  pipe([[-3.3, -0.75, 1.45], [2.7, -0.75, 1.45], [3.6, 1.8, 1.45], [4.0, 1.8, 1.45]], 0.07, wire, cart);
  pipe([[4.0, 1.8, -1.55], [4.0, 1.8, 1.55]], 0.12, orange, cart);
  const cartWheels = [];
  for (const x of [-2.55, 2.7]) for (const z of [-1.47, 1.47]) {
    const wheel = cyl(0.31, 0.19, rubber, cart, x, -1.04, z, 32); wheel.rotation.x = Math.PI / 2; cartWheels.push(wheel);
    const hub = cyl(0.135, 0.21, aluminum, cart, x, -1.04, z, 24); hub.rotation.x = Math.PI / 2;
  }

  const car = new THREE.Group(); scene.add(car);
  box(8.9, 1.44, 3.55, white, car, 0, 0.28, 0, 0.24);
  box(4.52, 1.35, 3.16, white, car, -1.0, 1.51, 0, 0.28);
  box(2.2, 0.96, 3.20, glass, car, -1.34, 1.64, 0, 0.20);
  box(0.095, 1.08, 3.23, white, car, -0.92, 1.62, 0, 0.03);
  box(1.04, 0.79, 3.21, glass, car, 0.24, 1.55, 0, 0.16);
  box(3.0, 0.31, 3.23, white, car, -1.0, 2.23, 0, 0.12);
  box(2.3, 0.13, 2.68, pale, car, 2.65, 1.07, 0);
  const hatch = box(2.54, 0.14, 3.33, white, car, 2.71, 3.16, 0, 0.06); hatch.rotation.z = 0.23;
  for (const z of [-1.4, 1.4]) pipe([[3.63, 1.04, z], [3.95, 3.25, z]], 0.045, aluminum, car);
  for (const x of [-2.65, 2.58]) for (const z of [-1.80, 1.80]) {
    const wheel = cyl(0.75, 0.29, rubber, car, x, -0.39, z); wheel.rotation.x = Math.PI / 2;
    const hub = cyl(0.40, 0.31, aluminum, car, x, -0.39, z); hub.rotation.x = Math.PI / 2;
    const center = cyl(0.19, 0.32, pale, car, x, -0.39, z); center.rotation.x = Math.PI / 2;
  }
  box(0.16, 0.35, 0.88, orange, car, 4.47, 0.69, 1.05, 0.05);
  box(0.16, 0.33, 0.88, ice, car, -4.47, 0.65, 1.05, 0.05);
  box(0.14, 0.35, 2.8, pale, car, -4.46, -0.06, 0, 0.04);
  for (const x of [-1.8, 0.1]) box(0.43, 0.10, 0.05, aluminum, car, x, 0.9, 1.81, 0.015);

  const kitchen = new THREE.Group(); scene.add(kitchen);
  box(7.4, 0.30, 4.4, white, kitchen, 0, 0, 0, 0.09);
  box(6.9, 2.5, 3.6, pale, kitchen, 0, -1.40, -0.1, 0.08);
  for (const x of [-1.74, 1.74]) {
    box(3.30, 2.30, 0.16, white, kitchen, x, -1.4, 1.80, 0.045);
    box(1.02, 0.08, 0.13, aluminum, kitchen, x, -0.55, 1.94, 0.03);
  }

  const fridge = new THREE.Group(); scene.add(fridge);
  box(5.2, 7.3, 0.23, pale, fridge, 0, 0, -1.32, 0.08);
  box(0.30, 7.3, 2.88, white, fridge, -2.53, 0, 0, 0.08);
  box(0.30, 7.3, 2.88, white, fridge, 2.53, 0, 0, 0.08);
  box(5.2, 0.30, 2.88, white, fridge, 0, 3.5, 0, 0.08);
  box(5.2, 0.30, 2.88, white, fridge, 0, -3.5, 0, 0.08);
  const shelfHeights = [-2.99, -0.91, 1.18];
  for (const y of shelfHeights) { box(4.8, 0.08, 2.66, ice, fridge, 0, y, 0, 0.02); box(4.80, 0.055, 0.10, aluminum, fridge, 0, y, 1.33, 0.014); }
  const fridgeCans = [];
  for (let row = 0; row < 3; row++) for (let column = 0; column < 4; column++) {
    const can = makeCan(); can.scale.setScalar(0.66); can.position.set((column - 1.5) * 1.17, shelfHeights[row] + 0.06, 0.18);
    can.rotation.y = 0.18 * (column % 2); can.userData.home = can.position.clone(); fridge.add(can); fridgeCans.push(can);
  }
  const bulb = new THREE.MeshBasicMaterial({ color: '#F4F8FF' });
  box(0.07, 6.4, 0.045, bulb, fridge, -2.34, 0.0, -1.13, 0.015);
  box(0.07, 6.4, 0.045, bulb, fridge, 2.34, 0.0, -1.13, 0.015);

  const groups = [hero, pack, cart, car, kitchen, fridge];
  function reset() {
    for (const g of groups) { g.visible = false; g.position.set(0, 0, 0); g.rotation.set(0, 0, 0); g.scale.setScalar(1); }
    for (const can of packCans) { can.visible = true; can.position.copy(can.userData.grid); can.scale.setScalar(1); }
    tray.visible = true; tray.scale.setScalar(1);
    camera.zoom = 1; camera.updateProjectionMatrix();
    floor.position.y = -3.55;
  }
  const composite = document.createElement('canvas'); composite.width = width; composite.height = height;
  const compositeContext = composite.getContext('2d', { alpha: false });
  function showShelf() {
    fridge.visible = true; fridge.position.set(3.35, 0.34, 0); fridge.rotation.y = -0.09; fridge.scale.setScalar(0.94); floor.position.y = -3.11;
    for (const can of fridgeCans) { can.visible = true; can.position.copy(can.userData.home); can.scale.setScalar(0.66); }
  }
  function carryStage(stage, t) {
    floor.position.y = -2.98;
    const transfer = progress(t, 1.3, 1.85);
    if (stage === 'car') {
      car.visible = true; car.scale.setScalar(0.84); car.rotation.y = -0.22;
      car.position.set(3.1, -2.01, 0);
    } else if (stage === 'kitchen') {
      kitchen.visible = true; kitchen.scale.setScalar(0.88); kitchen.rotation.y = -0.12;
      kitchen.position.set(3.5, -0.62, 0.4);
    } else { showShelf(); return; }
    pack.visible = true;
    pack.scale.setScalar(lerp(0.44, 0.73, transfer));
    pack.rotation.y = lerp(-0.20, -0.12, transfer);
    pack.position.set(lerp(5.33, 2.9, transfer), lerp(-1.05, -0.46, transfer) + Math.sin(Math.PI * transfer) * 0.8, lerp(0.4, 0.7, transfer));
  }
  function draw(time, shot) {
    const t = Math.max(0, time); reset();
    if (shot === 'single') {
      hero.visible = true;
      const enter = progress(t, 0, 1.7);
      hero.position.set(3.15, -2.35 + 0.05 * Math.sin(t * 0.8), 0.5);
      hero.scale.setScalar(1.79);
      hero.rotation.set(lerp(-0.055, 0, enter), lerp(-0.8, -0.30, progress(t, 0, 6)), lerp(-0.07, 0.015, enter));
      floor.position.y = -2.39;
    } else if (shot === 'case') {
      pack.visible = true;
      const spread = progress(t, 0.0, 1.9);
      const lower = progress(t, 3.8, 4.8);
      const scale = lerp(1.79, 0.91, spread);
      pack.scale.setScalar(scale);
      pack.position.set(3.17, lerp(-2.35, -2.1, spread) + lower * 0.38, 0.4);
      pack.rotation.y = lerp(-0.30, -0.20, spread);
      floor.position.y = lerp(pack.position.y - 0.025, -2.55, progress(t, 3.4, 4.65));
      tray.visible = t > 0.65; tray.scale.setScalar(Math.max(0.001, progress(t, 0.65, 1.8)));
      for (let i = 0; i < packCans.length; i++) {
        const can = packCans[i], arrive = progress(t, 0.10 + i * 0.064, 1.25 + i * 0.064);
        can.visible = i === 5 || arrive > 0.001;
        can.scale.setScalar(i === 5 ? 1 : Math.max(0.001, arrive));
        can.position.copy(can.userData.grid).multiplyScalar(spread);
        can.position.y += (1 - arrive) * (i === 5 ? 0 : 1.7);
      }
      if (t > 3.4) {
        cart.visible = true; cart.scale.setScalar(0.99);
        cart.position.set(3.17 + 12 * (1 - progress(t, 3.4, 4.65)), -1.19, 0.4);
        cart.rotation.y = -0.20;
      }
    } else if (shot === 'carry') {
      let before, after, blend;
      if (t < 1.3) { before = after = 'car'; blend = 0; }
      else if (t < 1.85) { before = 'car'; after = 'kitchen'; blend = progress(t, 1.3, 1.85); }
      else if (t < 2.7) { before = after = 'kitchen'; blend = 0; }
      else if (t < 3.25) { before = 'kitchen'; after = 'shelf'; blend = progress(t, 2.7, 3.25); }
      else { before = after = 'shelf'; blend = 0; }
      carryStage(before, t);
      renderer.render(scene, camera);
      if (before === after) return renderer.domElement;
      compositeContext.globalAlpha = 1;
      compositeContext.drawImage(renderer.domElement, 0, 0);
      reset(); carryStage(after, t);
      renderer.render(scene, camera);
      compositeContext.globalAlpha = blend;
      compositeContext.drawImage(renderer.domElement, 0, 0);
      compositeContext.globalAlpha = 1;
      return composite;
    } else if (shot === 'repeat') {
      showShelf();
      for (let i = 0; i < fridgeCans.length; i++) {
        const can = fridgeCans[i];
        const remove1 = progress(t, 0.35 + i * 0.065, 0.72 + i * 0.065);
        const restock1 = progress(t, 1.90 + (11 - i) * 0.035, 2.20 + (11 - i) * 0.035);
        const remove2 = progress(t, 3.10 + i * 0.065, 3.47 + i * 0.065);
        const restock2 = progress(t, 4.72 + (11 - i) * 0.035, 5.02 + (11 - i) * 0.035);
        const remove3 = progress(t, 5.90 + i * 0.065, 6.27 + i * 0.065);
        const presence = (1 - remove1) + restock1 - remove2 + restock2 - remove3;
        const leaving = t < 1.9 ? remove1 : t < 4.72 ? remove2 : remove3;
        const arriving = t < 1.9 ? 1 : t < 4.72 ? restock1 : restock2;
        can.visible = presence > 0.002;
        can.scale.setScalar(0.66 * Math.max(0.01, presence));
        can.position.copy(can.userData.home);
        can.position.y += (1 - arriving) * 0.58 + leaving * 0.24;
        can.position.z += leaving * 0.70;
      }
    } else throw new Error(`Unknown errand shot: ${shot}`);
    renderer.render(scene, camera);
    return renderer.domElement;
  }
  function dispose() {
    const geometries = new Set(), materials = new Set();
    scene.traverse((object) => { if (object.geometry) geometries.add(object.geometry); if (object.material) for (const m of Array.isArray(object.material) ? object.material : [object.material]) materials.add(m); });
    for (const g of geometries) g.dispose(); for (const m of materials) m.dispose();
    label.dispose(); environment.dispose(); pmrem.dispose(); renderer.dispose();
  }
  return { draw, dispose };
}
