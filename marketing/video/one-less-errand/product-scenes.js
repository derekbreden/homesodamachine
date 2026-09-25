import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { FAUCET_STYLES, FAUCET_FINISHES, isFaucetFinishBody } from "/contracts/faucet-options.js";

const clamp = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { const p = clamp(x); return p * p * (3 - 2 * p); };
const mix = (a, b, p) => a + (b - a) * p;
const enter = (t, a, b) => ease((t - a) / (b - a));

// Mesh payloads keep the assembly's millimetres and +Z-up coordinate frame.
async function payload(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Product geometry ${response.status}: ${url}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  const n = new DataView(bytes.buffer).getUint32(0, true);
  const header = JSON.parse(new TextDecoder().decode(bytes.subarray(4, n + 4)));
  if (![2, 3].includes(header.v)) throw new Error(`Unknown mesh payload version ${header.v}`);
  const blob = bytes.buffer.slice(n + 4);
  return header.meshes.map((m) => ({
    name: m.name, color: m.color,
    positions: new Float32Array(blob, m.pos[0], m.pos[1]),
    normals: new Float32Array(blob, m.nrm[0], m.nrm[1]),
    indices: new Uint32Array(blob, m.idx[0], m.idx[1]),
  }));
}

export async function createProductScenes({ THREE, width = 1920, height = 1080, palette = {} }) {
  const colors = { cobalt: "#1749D1", ice: "#DCE6FF", orange: "#FF9152", white: "#FFFFFF", ...palette };
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "high-performance" });
  renderer.setSize(width, height);
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.localClippingEnabled = true;
  const canvas = renderer.domElement;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#F3F0E8");
  const camera = new THREE.OrthographicCamera(-400, 400, 225, -225, 1, 5000);
  camera.up.set(0, 0, 1);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environment = pmrem.fromScene(new RoomEnvironment(), 0.055);
  scene.environment = environment.texture;
  scene.environmentIntensity = 0.48;
  pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff, 0xc8bdad, 0.62));
  const key = new THREE.DirectionalLight(0xfff8ec, 2.4);
  key.position.set(-280, -400, 640);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xdce6ff, 1.6);
  rim.position.set(260, 360, 320);
  scene.add(rim);
  const fill = new THREE.DirectionalLight(0xffffff, 0.3);
  fill.position.set(500, -700, 90);
  scene.add(fill);

  const basicMat = (color, roughness = 0.65, metalness = 0) => new THREE.MeshStandardMaterial({ color, roughness, metalness });
  const warmMat = basicMat("#F3F0E8", 0.8);
  const counterMat = new THREE.MeshBasicMaterial({ color: "#F3F0E8", toneMapped: false });
  const counterSolidMat = basicMat("#F8F6F0", 0.7);
  const cobaltMat = new THREE.MeshBasicMaterial({ color: colors.cobalt, toneMapped: false });
  const woodMat = basicMat("#CAB59A", 0.83);
  const shadowMap = (() => {
    const c = document.createElement("canvas"); c.width = c.height = 256;
    const g = c.getContext("2d");
    const gradient = g.createRadialGradient(128, 128, 8, 128, 128, 126);
    gradient.addColorStop(0, "rgba(64,53,40,.30)"); gradient.addColorStop(0.4, "rgba(64,53,40,.15)"); gradient.addColorStop(1, "rgba(64,53,40,0)");
    g.fillStyle = gradient; g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  })();
  function box(x, y, z, mat, at = [0, 0, 0]) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(x, y, z), mat);
    mesh.position.set(...at); return mesh;
  }
  function contactShadow(w, h, position) {
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: shadowMap, transparent: true, depthWrite: false, opacity: 0.7 }));
    mesh.position.set(...position); return mesh;
  }
  const counter = box(2800, 1800, 28, counterMat, [0, 50, -20]);
  scene.add(counter);
  const counterLine = box(2800, 4, 3, basicMat("#E3DDD2"), [0, 550, -6.5]);
  scene.add(counterLine);

  // Only the exterior and the visible above-counter hardware are drawn.
  // Clipping leaves tubes in their source geometry while the countertop hides their run.
  const shown = new Set(["westbrass", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x", "lever", "above_counter_plate", "above_counter_gasket", "shell_base", "shell_tip", "faucet-display-cover-seated", "faucet_display", "faucet_display_screen"]);
  const payloads = await Promise.all(FAUCET_STYLES.map((style) => payload(`/meshes/${style.assembly}.mesh`)));
  const geometries = payloads.map((meshes) => meshes.filter((m) => shown.has(m.name)).map((m) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(m.positions, 3));
    geometry.setAttribute("normal", new THREE.BufferAttribute(m.normals, 3));
    geometry.setIndex(new THREE.BufferAttribute(m.indices, 1));
    if (m.name === "faucet_display_screen") {
      const uv = new Float32Array(m.positions.length / 3 * 2);
      for (let i = 0; i < m.positions.length / 3; i++) {
        uv[i * 2] = (m.positions[i * 3] + 8.88) / 17.76;
        uv[i * 2 + 1] = (m.positions[i * 3 + 2] - 199.62) / (225.1 - 199.62);
      }
      geometry.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
    }
    return { ...m, geometry };
  }));
  const displayCanvas = document.createElement("canvas"); displayCanvas.width = 240; displayCanvas.height = 440;
  const dc = displayCanvas.getContext("2d");
  const displayTexture = new THREE.CanvasTexture(displayCanvas);
  displayTexture.colorSpace = THREE.SRGBColorSpace;
  displayTexture.anisotropy = 4;
  const screenMaterial = new THREE.MeshBasicMaterial({ map: displayTexture, toneMapped: false });
  function display(selected = 0, progress = 0) {
    dc.fillStyle = colors.cobalt; dc.fillRect(0, 0, 240, 440);
    dc.textAlign = "center"; dc.textBaseline = "middle";
    dc.font = "600 23px Montserrat, sans-serif"; dc.fillStyle = colors.white; dc.fillText("CHOOSE", 120, 45);
    for (let i = 0; i < 2; i++) {
      dc.fillStyle = selected === i ? colors.white : colors.ice;
      dc.globalAlpha = selected === i ? 1 : 0.46;
      dc.beginPath(); dc.roundRect(22, 87 + i * 146, 196, 122, 19); dc.fill(); dc.globalAlpha = 1;
      dc.fillStyle = colors.cobalt; dc.font = "600 56px Montserrat, sans-serif"; dc.fillText(String(i + 1).padStart(2, "0"), 119, 143 + i * 146);
      dc.font = "500 16px Montserrat, sans-serif"; dc.fillText("FLAVOR", 120, 183 + i * 146);
    }
    dc.fillStyle = colors.orange; dc.fillRect(22, 391, 196 * progress, 6);
    displayTexture.needsUpdate = true;
  }
  const fixtures = [];
  function fixture(styleIndex, finishIndex) {
    const style = FAUCET_STYLES[styleIndex], finish = FAUCET_FINISHES[finishIndex];
    const group = new THREE.Group();
    const lever = new THREE.Group(); lever.position.z = 46; group.add(lever);
    const surface = new THREE.MeshStandardMaterial({ color: new THREE.Color(...finish.rgb), roughness: finish.roughness, metalness: finish.metalness, clippingPlanes: [new THREE.Plane(new THREE.Vector3(0, 0, 1), 6)] });
    const hardware = basicMat("#23242A", 0.63, 0.1);
    hardware.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0, 0, 1), 6)];
    for (const m of geometries[styleIndex]) {
      const mat = m.name === "faucet_display_screen" ? screenMaterial : isFaucetFinishBody(style.assembly, m.name) ? surface : hardware;
      const mesh = new THREE.Mesh(m.geometry, mat); mesh.name = m.name;
      if (m.name === "lever") { mesh.position.z = -46; lever.add(mesh); } else group.add(mesh);
    }
    const shadow = contactShadow(165, 150, [0, -6, -5.9]); group.add(shadow);
    scene.add(group);
    const result = { group, surface, style, finish, shadow, lever };
    fixtures.push(result); return result;
  }
  const sculptedBlack = fixture(0, 0), industrialBlack = fixture(1, 0), sculptedWhite = fixture(0, 1), industrialWhite = fixture(1, 1);

  const glass = new THREE.Group();
  const glassMat = new THREE.MeshPhysicalMaterial({ color: "#D8ECFF", roughness: 0.07, metalness: 0.12, transparent: true, opacity: 0.13, side: THREE.DoubleSide, depthWrite: false });
  const profile = [new THREE.Vector2(0, 1), new THREE.Vector2(29, 1), new THREE.Vector2(31, 4), new THREE.Vector2(35.2, 118), new THREE.Vector2(34.2, 120), new THREE.Vector2(33, 118), new THREE.Vector2(29.2, 7), new THREE.Vector2(0, 7)];
  const vessel = new THREE.Mesh(new THREE.LatheGeometry(profile, 72), glassMat);
  // Lathe's Y axis becomes the scene's Z axis.
  vessel.rotation.x = Math.PI / 2;
  glass.add(vessel);
  const rimMaterial = new THREE.MeshBasicMaterial({ color: "#859CB9", transparent: true, opacity: 0.54, depthWrite: false });
  const glassRim = new THREE.Mesh(new THREE.TorusGeometry(34.3, 0.6, 8, 80), rimMaterial); glassRim.position.z = 119; glass.add(glassRim);
  const glassFoot = new THREE.Mesh(new THREE.TorusGeometry(29.2, 0.75, 8, 80), rimMaterial); glassFoot.position.z = 4; glass.add(glassFoot);
  const water = new THREE.Mesh(new THREE.CylinderGeometry(31.6, 28.8, 1, 72), new THREE.MeshPhysicalMaterial({ color: "#D69932", roughness: 0.18, transparent: true, opacity: 0.72, metalness: 0, depthWrite: false }));
  water.rotation.x = Math.PI / 2; glass.add(water);
  const waterTop = new THREE.Mesh(new THREE.CircleGeometry(31.6, 72), new THREE.MeshBasicMaterial({ color: "#F4BC61", transparent: true, opacity: 0.5 })); glass.add(waterTop);
  const ice = [];
  const iceMat = new THREE.MeshPhysicalMaterial({ color: "#DCEAFF", roughness: 0.17, metalness: 0.06, transparent: true, opacity: 0.82, depthWrite: false });
  for (let i = 0; i < 5; i++) {
    const cube = new THREE.Mesh(new RoundedBoxGeometry(21, 22, 24, 3, 2.3), iceMat);
    cube.rotation.set(0.12 + i * 0.46, 0.25 + i * 0.38, i * 0.84);
    ice.push(cube); glass.add(cube);
  }
  const bubbles = [];
  const bubbleGeometry = new THREE.SphereGeometry(0.75, 8, 6);
  const bubbleMat = new THREE.MeshBasicMaterial({ color: "#FFFFFF", transparent: true, opacity: 0.75 });
  for (let i = 0; i < 30; i++) { const b = new THREE.Mesh(bubbleGeometry, bubbleMat); bubbles.push(b); glass.add(b); }
  glass.position.set(0, -180, -5);
  const glassShadow = contactShadow(145, 120, [0, -180, -5.8]);
  const coaster = new THREE.Mesh(new THREE.CylinderGeometry(45, 45, 2.6, 80), new THREE.MeshStandardMaterial({ color: colors.cobalt, roughness: 0.73 }));
  coaster.rotation.x = Math.PI / 2; coaster.position.set(0, -180, -4.8);
  scene.add(glass, glassShadow, coaster);

  const stream = new THREE.Group();
  const streamPath = new THREE.CatmullRomCurve3([new THREE.Vector3(0, -134, 180), new THREE.Vector3(0, -145, 163), new THREE.Vector3(0, -162, 136), new THREE.Vector3(0, -180, 90)]);
  const streamBody = new THREE.Mesh(new THREE.TubeGeometry(streamPath, 36, 1.05, 9, false), new THREE.MeshBasicMaterial({ color: "#7CAECE", transparent: true, opacity: 0.34, depthWrite: false }));
  const flavorPath = new THREE.CatmullRomCurve3([new THREE.Vector3(-3.175, -139.57, 185.07), new THREE.Vector3(-3.175, -154, 160), new THREE.Vector3(-4, -173, 128), new THREE.Vector3(-4, -187, 90)]);
  const flavorStream = new THREE.Mesh(new THREE.TubeGeometry(flavorPath, 36, 0.43, 7, false), new THREE.MeshBasicMaterial({ color: "#C58A30", transparent: true, opacity: 0.66, depthWrite: false }));
  stream.add(flavorStream);
  stream.add(streamBody);
  const glints = [];
  for (let i = 0; i < 9; i++) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.6, 8, 6), new THREE.MeshBasicMaterial({ color: "#FFFFFF", transparent: true, opacity: 0.8 })); stream.add(b); glints.push(b); }
  scene.add(stream);

  const cabinet = new THREE.Group();
  cabinet.add(box(30, 610, 706, woodMat, [-350, 55, -386]), box(30, 610, 706, woodMat, [350, 55, -386]), box(730, 610, 28, woodMat, [0, 55, -753]), box(730, 20, 710, basicMat("#DCD2C1"), [0, 350, -390]));
  const cabinetShadow = contactShadow(1100, 900, [0, 50, -769]); cabinet.add(cabinetShadow);
  const floor = box(7000, 7000, 20, counterMat, [0, 0, -782]); cabinet.add(floor);
  const machine = new THREE.Group();
  const machineData = await payload("/meshes/manifold-layout/enclosure-assembly.step.mesh");
  const exterior = (name) => name.startsWith("enclosure-") || name.startsWith("nameplate") || name.startsWith("display") || name.startsWith("funnel") || name === "pump-jack";
  for (const m of machineData.filter((m) => exterior(m.name))) {
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(m.positions, 3)); g.setAttribute("normal", new THREE.BufferAttribute(m.normals, 3)); g.setIndex(new THREE.BufferAttribute(m.indices, 1));
    const color = m.color ? new THREE.Color(...m.color) : new THREE.Color("#28292D");
    const mat = new THREE.MeshStandardMaterial({ color, metalness: m.name.includes("ink") ? 0 : 0.05, roughness: 0.7 });
    const mesh = new THREE.Mesh(g, mat); mesh.name = m.name; machine.add(mesh);
  }
  machine.position.set(65, -150, -717); cabinet.add(machine);
  const hosePath = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, -33), new THREE.Vector3(-10, 20, -150), new THREE.Vector3(40, 225, -270), new THREE.Vector3(65, 322, -448)]);
  cabinet.add(new THREE.Mesh(new THREE.TubeGeometry(hosePath, 32, 8, 10, false), basicMat("#47474A", 0.9)));
  scene.add(cabinet);

  const target = new THREE.Vector3();
  const direction = new THREE.Vector3();
  function view({ h = 415, angle = 32, elevation = 18, center = [0, -65, 105], offset = -330 }) {
    const a = angle * Math.PI / 180, e = elevation * Math.PI / 180;
    target.set(...center);
    direction.set(Math.sin(a) * Math.cos(e), -Math.cos(a) * Math.cos(e), Math.sin(e));
    camera.position.copy(target).addScaledVector(direction, 1500); camera.lookAt(target);
    camera.left = -h * width / height / 2; camera.right = h * width / height / 2; camera.top = h / 2; camera.bottom = -h / 2;
    camera.setViewOffset(width, height, offset * width / 1920, 0, width, height);
    camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  }
  const cameraRight = new THREE.Vector3();
  function moveAcross(group, x, z = 0, forward = 0) {
    cameraRight.setFromMatrixColumn(camera.matrixWorld, 0);
    group.position.copy(cameraRight).multiplyScalar(x); group.position.z = z; group.position.y += forward;
  }
  function liquid(t, fillAmount = 0) {
    const level = 8 + fillAmount * 78;
    water.visible = waterTop.visible = fillAmount > 0.01;
    water.scale.y = level - 7; water.position.z = (level + 7) / 2; waterTop.position.z = level;
    for (let i = 0; i < ice.length; i++) {
      const a = i * 2.399, radius = 11 + (i % 2) * 3;
      ice[i].position.set(Math.cos(a) * radius, Math.sin(a) * radius, 19 + Math.floor(i / 2) * 20 + fillAmount * (20 - Math.floor(i / 2) * 3));
      ice[i].rotation.z = i * 0.84 + fillAmount * 0.12 * Math.sin(t * 0.8 + i);
    }
    bubbles.forEach((b, i) => {
      const p = (t * (0.13 + (i % 4) * 0.018) + i * 0.731) % 1;
      b.visible = fillAmount > 0.1; b.position.set(Math.cos(i * 2.399) * (10 + i % 17), Math.sin(i * 2.399) * (10 + i % 17), 8 + p * (level - 11));
      b.scale.setScalar(0.6 + (i % 3) * 0.3);
    });
  }
  function reset() {
    fixtures.forEach(({ group, surface, lever }) => { lever.rotation.x = 0; group.visible = false; group.position.set(0, 0, 0); group.rotation.set(0, 0, 0); group.scale.setScalar(1); surface.opacity = 1; });
    glass.visible = glassShadow.visible = false; stream.visible = cabinet.visible = false;
    counter.visible = true; counterLine.visible = false; counter.material = counterMat; coaster.visible = false;
    counter.scale.set(1, 1, 1); counter.position.set(0, 50, -20);
    scene.background.set("#F3F0E8");
    glass.position.set(0, -180, -5); glass.rotation.set(0, 0, 0); glass.scale.setScalar(1);
    view({});
  }
  function draw(time, shot = "reveal", { cobalt = false } = {}) {
    const t = Math.max(0, time);
    reset(); display(["pour", "closing", "sculpted", "industrial", "finishes", "four"].includes(shot) ? 1 : 0, shot === "select" ? enter(t, 1.4, 4.8) : 0);
    sculptedBlack.group.visible = true;
    if (shot === "reveal" || shot === "closing") {
      const p = ease(t / 6);
      view({ h: mix(425, 400, p), angle: mix(36, 31, p), elevation: 17, center: [0, -75, 110] });
      glass.visible = glassShadow.visible = coaster.visible = true;
      liquid(t, shot === "closing" ? 0.92 : 0);
    } else if (shot === "under") {
      const p = enter(t, 0.15, 2.7);
      cabinet.visible = true; counter.material = counterSolidMat;
      counter.scale.set(0.31, 0.39, 1); counter.position.y = 55;
      counterLine.visible = false;
      view({ h: mix(440, 1390, p), angle: mix(32, 22, p), elevation: mix(18, 10, p), center: [0, -40, mix(100, -285, p)], offset: -370 });
    } else if (shot === "select") {
      const detail = ease(t / 2.2), pullback = enter(t, 2.2, 5.9);
      view({ h: mix(mix(180, 168, detail), 393, pullback), angle: mix(mix(14, 10, detail), 31, pullback), elevation: mix(28, 17, pullback), center: [0, mix(-113, -77, pullback), mix(195, 109, pullback)], offset: mix(-355, -330, pullback) });
      display(t > 2.2 ? 1 : 0, enter(t, 2.2, 3.2));
      glass.visible = glassShadow.visible = coaster.visible = true;
      liquid(t, 0);
      sculptedBlack.lever.rotation.x = 0.23 * enter(t, 6.5, 7.0);
    } else if (shot === "pour") {
      view({ h: 393, angle: 31, elevation: 17, center: [0, -77, 109] });
      glass.visible = glassShadow.visible = coaster.visible = true;
      const poured = enter(t, 1.0, 8.9);
      liquid(t, poured * 0.93);
      stream.visible = t >= 1.0 && t < 8.9;
      streamBody.material.opacity = 0.38 * enter(t, 1.0, 1.18) * (1 - enter(t, 8.64, 8.9));
      streamPath.points[3].z = 12 + poured * 71;
      streamBody.geometry.dispose(); streamBody.geometry = new THREE.TubeGeometry(streamPath, 36, 1.05, 9, false);
      flavorPath.points[3].z = streamPath.points[3].z;
      flavorStream.geometry.dispose(); flavorStream.geometry = new THREE.TubeGeometry(flavorPath, 36, 0.43, 7, false);
      flavorStream.material.opacity = 0.66 * enter(t, 1.03, 1.2) * (1 - enter(t, 8.59, 8.83));
      sculptedBlack.lever.rotation.x = 0.23 * (1 - enter(t, 8.62, 9.0));
      display(1, 1);
      glints.forEach((b, i) => { b.position.copy(streamPath.getPoint((t * 1.1 + i / glints.length) % 1)); });
    } else if (shot === "sculpted" || shot === "industrial") {
      sculptedBlack.group.visible = shot === "sculpted"; industrialBlack.group.visible = shot === "industrial";
      const p = ease(t / 8);
      view({ h: 343, angle: mix(48, 34, p), elevation: 13, center: [0, -62, 117], offset: -340 });
    } else if (shot === "finishes") {
      sculptedWhite.group.visible = true;
      scene.background.set(colors.cobalt); counter.material = cobaltMat;
      const p = enter(t, 0, 1.6);
      view({ h: 403, angle: 34, elevation: 14, center: [0, -66, 116], offset: -330 });
      moveAcross(sculptedBlack.group, -125 - (1 - p) * 12);
      moveAcross(sculptedWhite.group, 125 + (1 - p) * 12);
    } else if (shot === "four") {
      scene.background.set(colors.cobalt); counter.material = cobaltMat;
      view({ h: 480, angle: 34, elevation: 12, center: [0, -65, 114], offset: -60 });
      const row = [sculptedBlack, sculptedWhite, industrialBlack, industrialWhite];
      row.forEach((f, i) => {
        f.group.visible = true;
        const p = enter(t, i * 0.14, 1.5 + i * 0.14);
        moveAcross(f.group, (i - 1.5) * 182 + (1 - p) * 25);
      });
    }
    if (cobalt) { scene.background.set(colors.cobalt); counter.material = cobaltMat; }
    renderer.render(scene, camera);
    return canvas;
  }
  function dispose() {
    scene.traverse((node) => { node.geometry?.dispose(); if (Array.isArray(node.material)) node.material.forEach((m) => m.dispose()); else node.material?.dispose(); });
    environment.dispose(); displayTexture.dispose(); shadowMap.dispose(); renderer.dispose();
  }
  return { draw, dispose, fourLabelPositions: [486, 895, 1305, 1715], backgroundFor: (shot) => ["finishes", "four"].includes(shot) ? colors.cobalt : "#F3F0E8" };
}
