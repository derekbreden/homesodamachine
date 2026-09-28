import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { DIM, INNER_RADIUS, CAP_TOP, JOINT, CLEARANCE, WIRE_GUIDE_END, WIRE_TIP, GRIP_BASE, LOCAL_ROLL_AXIS, posePoint } from "./pose.js";

const root = document.getElementById("weld-position");
const stage = root.querySelector(".weld-stage");
const loading = root.querySelector(".weld-loading");
const vector = p => new THREE.Vector3(...p);
const joint = vector(JOINT);

try {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  stage.append(renderer.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x687182, 1.8));
  const light = new THREE.DirectionalLight(0xffffff, 2);
  light.position.set(120, -180, 400);
  scene.add(light);
  const fill = new THREE.DirectionalLight(0xffffff, 1);
  fill.position.set(-200, 200, 220);
  scene.add(fill);

  const materials = {
    metal: new THREE.MeshStandardMaterial({ metalness: 0.32, roughness: 0.38 }),
    cap: new THREE.MeshStandardMaterial({ metalness: 0.22, roughness: 0.65 }),
    gun: new THREE.MeshStandardMaterial({ metalness: 0.12, roughness: 0.6 }),
    grip: new THREE.MeshStandardMaterial({ metalness: 0.06, roughness: 0.85 }),
    wire: new THREE.MeshBasicMaterial(),
    laser: new THREE.MeshBasicMaterial(),
    fan: new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false }),
    tangent: new THREE.LineDashedMaterial({ dashSize: 4, gapSize: 3, transparent: true, opacity: 0.7, depthTest: false }),
    edge: new THREE.LineBasicMaterial({ transparent: true, opacity: 0.45 }),
  };

  function theme() {
    // Resolving through a DOM swatch supports CSS variables and color-mix().
    const swatch = document.createElement("span");
    root.append(swatch);
    const color = name => {
      swatch.style.color = `var(${name})`;
      return new THREE.Color(getComputedStyle(swatch).color);
    };
    materials.metal.color.copy(color("--weld-metal"));
    materials.cap.color.copy(color("--weld-metal")).multiplyScalar(0.48);
    materials.gun.color.copy(color("--weld-gun"));
    materials.grip.color.copy(color("--weld-gun")).multiplyScalar(0.5);
    materials.wire.color.copy(color("--weld-wire"));
    materials.laser.color.copy(color("--weld-laser"));
    materials.fan.color.copy(color("--weld-laser"));
    materials.tangent.color.copy(color("--weld-muted"));
    materials.edge.color.copy(color("--weld-muted"));
    swatch.remove();
  }
  theme();

  function cylinderBetween(parent, a, b, radius, material, endRadius = radius) {
    const av = vector(a), bv = vector(b), delta = bv.clone().sub(av);
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(endRadius, radius, delta.length(), 24), material);
    mesh.position.copy(av).add(bv).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), delta.normalize());
    parent.add(mesh);
    return mesh;
  }

  const tubeProfile = [
    [DIM.tubeOd / 2, 0], [DIM.tubeOd / 2, DIM.tubeHeight],
    [INNER_RADIUS, DIM.tubeHeight], [INNER_RADIUS, 0], [DIM.tubeOd / 2, 0],
  ].map(([r, z]) => new THREE.Vector2(r, z));
  const tubeGeometry = new THREE.LatheGeometry(tubeProfile, 192);
  tubeGeometry.rotateX(Math.PI / 2);
  const tube = new THREE.Mesh(tubeGeometry, materials.metal);
  tube.name = "Tube";
  scene.add(tube);

  const capShape = new THREE.Shape();
  capShape.absarc(0, 0, DIM.capDiameter / 2, 0, Math.PI * 2, false);
  for (const x of [-DIM.portOffset, DIM.portOffset]) {
    const hole = new THREE.Path();
    hole.absarc(x, 0, DIM.portDiameter / 2, 0, Math.PI * 2, true);
    capShape.holes.push(hole);
  }
  const capGeometry = new THREE.ExtrudeGeometry(capShape, {
    depth: DIM.capThickness, bevelEnabled: false, curveSegments: 64,
  });
  capGeometry.translate(0, 0, CAP_TOP - DIM.capThickness);
  const cap = new THREE.Mesh(capGeometry, materials.cap);
  cap.name = "Recessed endcap";
  scene.add(cap);

  for (const [radius, z] of [[DIM.tubeOd / 2, DIM.tubeHeight], [INNER_RADIUS, DIM.tubeHeight], [DIM.capDiameter / 2, CAP_TOP]]) {
    const points = Array.from({ length: 193 }, (_, i) => {
      const angle = i / 192 * Math.PI * 2;
      return new THREE.Vector3(radius * Math.cos(angle), radius * Math.sin(angle), z);
    });
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), materials.edge));
  }

  const gripBase = vector(posePoint(GRIP_BASE));
  const rollDirection = gripBase.clone().sub(joint).normalize();
  const tangent = new THREE.Line(new THREE.BufferGeometry().setFromPoints([
    joint.clone().addScaledVector(rollDirection, -18),
    gripBase.clone().addScaledVector(rollDirection, 85),
  ]), materials.tangent);
  tangent.computeLineDistances();
  tangent.renderOrder = 5;
  scene.add(tangent);
  const labels = [];
  for (const [point, name] of [[joint, "Laser dot"], [gripBase, "Grip base"]]) {
    const marker = new THREE.Mesh(new THREE.SphereGeometry(1.3, 16, 12), materials.laser);
    marker.position.copy(point);
    scene.add(marker);
    const label = document.createElement("span");
    label.className = "weld-point-label text-small";
    label.textContent = name;
    stage.append(label);
    labels.push({ point, label });
  }

  // Local +Z goes from nozzle to back of gun; -Y is the grip/wire-guide side.
  // Overall envelope follows the manual's 253 × 143 × 34 mm drawing.
  // The housing sections, grip and wire bracket are a visual proxy for a scan.
  const gun = new THREE.Group();
  gun.name = "X1 Pro gun proxy";
  scene.add(gun);
  cylinderBetween(gun, [0, 0, 0], [0, 0, 23], 2.2, materials.grip, 5);
  cylinderBetween(gun, [0, 0, 23], [0, 0, 54], 8.5, materials.metal);
  cylinderBetween(gun, [0, 0, 54], [0, 0, 100], 5.5, materials.metal);
  cylinderBetween(gun, [0, 0, 100], [0, 0, 118], 12, materials.grip);
  const housing = new THREE.Mesh(new THREE.BoxGeometry(DIM.gunWidth, 34, 135), materials.gun);
  housing.position.set(0, 0, 185.5);
  gun.add(housing);
  const gripStart = new THREE.Vector3(0, -25, 172);
  const gripEnd = new THREE.Vector3(0, -111, 232);
  const grip = new THREE.Mesh(new THREE.BoxGeometry(30, gripStart.distanceTo(gripEnd) + 16, 28), materials.grip);
  grip.position.copy(gripStart).add(gripEnd).multiplyScalar(0.5);
  grip.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), gripEnd.clone().sub(gripStart).normalize());
  gun.add(grip);

  // The umbilical exits the grip. The external wire conduit runs beside it,
  // then separately to the guide. Their short paths show the distinction;
  // their diameters and bends are schematic rather than a cable-fit model.
  const base = vector(GRIP_BASE), localAxis = vector(LOCAL_ROLL_AXIS);
  const cableEnd = base.clone().addScaledVector(localAxis, 70);
  const gripDirection = gripEnd.clone().sub(gripStart).normalize();
  const cableCurve = new THREE.CubicBezierCurve3(base,
    base.clone().addScaledVector(gripDirection, 24),
    cableEnd.clone().addScaledVector(localAxis, -25), cableEnd);
  gun.add(new THREE.Mesh(new THREE.TubeGeometry(cableCurve, 32, 5.5, 12, false), materials.grip));

  const guideEnd = WIRE_GUIDE_END;
  const wireTarget = WIRE_TIP;
  const guideBack = vector(guideEnd).sub(vector(wireTarget)).normalize().multiplyScalar(40).add(vector(guideEnd)).toArray();
  cylinderBetween(gun, guideBack, guideEnd, 2.5, materials.grip);
  cylinderBetween(gun, [0, -12, 110], guideBack, 2, materials.gun);
  cylinderBetween(gun, guideEnd, wireTarget, 0.48, materials.wire);
  const side = new THREE.Vector3(23, 0, 0);
  const feedCurve = new THREE.CatmullRomCurve3([
    cableEnd.clone().add(side),
    base.clone().add(side),
    base.clone().addScaledVector(localAxis, -35).add(side),
    vector(guideBack).addScaledVector(localAxis, 40).addScaledVector(side, 0.3),
    vector(guideBack).addScaledVector(localAxis, 14),
    vector(guideBack),
  ]);
  gun.add(new THREE.Mesh(new THREE.TubeGeometry(feedCurve, 64, 1.8, 10, false), materials.wire));

  const sweep = new THREE.Group();
  scene.add(sweep);
  const hitTester = new THREE.Raycaster();
  function clearSweep() {
    for (const child of [...sweep.children]) {
      child.geometry.dispose();
      sweep.remove(child);
    }
  }
  function updatePose(degrees) {
    const origin = vector(posePoint([0, 0, 0], degrees));
    const basis = [0, 1, 2].map(axis => {
      const p = [0, 0, 0]; p[axis] = 1;
      return vector(posePoint(p, degrees)).sub(origin);
    });
    gun.position.copy(origin);
    gun.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(...basis));
    scene.updateMatrixWorld(true);
    clearSweep();

    // A straight 2 mm sweep is only an orientation aid. Intersect real surfaces
    // so its footprint cannot appear through the wall. It is not a calibrated
    // scan pattern or a prediction of energy delivered to either surface.
    const hits = [];
    for (let i = 0; i <= 40; i++) {
      const focalPoint = vector(posePoint([-1 + i / 20, 0, -CLEARANCE], degrees));
      hitTester.set(origin, focalPoint.clone().sub(origin).normalize());
      const hit = hitTester.intersectObjects([tube, cap], false)[0];
      if (hit) hits.push(hit.point);
    }
    for (let i = 1; i < hits.length; i++) {
      if (hits[i].distanceTo(hits[i - 1]) < 1) {
        cylinderBetween(sweep, hits[i - 1].toArray(), hits[i].toArray(), 0.16, materials.laser);
      }
    }
    if (hits.length) {
      const middle = hits[Math.floor(hits.length / 2)];
      cylinderBetween(sweep, origin.toArray(), middle.toArray(), 0.16, materials.laser);
      const triangle = new THREE.BufferGeometry().setFromPoints([origin, hits[0], hits.at(-1)]);
      triangle.computeVertexNormals();
      sweep.add(new THREE.Mesh(triangle, materials.fan));
    }
    root.querySelector("[data-roll-value]").textContent = `${degrees}°`;
    root.querySelector("[data-roll]").value = degrees;
    root.dataset.rollDegrees = degrees;
    render();
  }

  const camera = new THREE.OrthographicCamera(-220, 220, 220, -220, 0.1, 3000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = false;
  controls.minZoom = 0.5;
  controls.maxZoom = 12;
  controls.addEventListener("change", render);
  let frameHeight = 480;
  let view = "overall";
  function render() {
    renderer.render(scene, camera);
    const { width, height } = stage.getBoundingClientRect();
    for (const { point, label } of labels) {
      const p = point.clone().project(camera);
      const x = (p.x + 1) * width / 2, y = (1 - p.y) * height / 2;
      label.hidden = Math.abs(p.x) > 0.94 || Math.abs(p.y) > 0.94 || Math.abs(p.z) > 1;
      label.style.left = `${Math.min(width - label.offsetWidth - 6, Math.max(6, x + 9))}px`;
      label.style.top = `${Math.max(4, y - 22)}px`;
    }
  }
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    const visibleHeight = Math.max(frameHeight, frameHeight * 0.92 / (width / height));
    camera.top = visibleHeight / 2; camera.bottom = -visibleHeight / 2;
    camera.left = -visibleHeight * width / height / 2;
    camera.right = -camera.left;
    camera.updateProjectionMatrix();
    render();
  }
  function setView(next) {
    view = next;
    camera.zoom = 1;
    camera.up.set(0, 0, 1);
    if (view === "top") {
      controls.target.set(15, -135, CAP_TOP);
      camera.position.set(15, -135, CAP_TOP + 600);
      camera.up.set(0, 1, 0);
      frameHeight = 440;
    } else if (view === "joint") {
      controls.target.copy(joint).add(new THREE.Vector3(-5, -6, 12));
      camera.position.copy(controls.target).add(new THREE.Vector3(-150, 40, 100));
      frameHeight = 92;
    } else {
      controls.target.set(15, -100, 180);
      camera.position.set(-480, 100, 440);
      frameHeight = 480;
    }
    controls.update();
    resize();
    root.querySelectorAll("[data-view]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.view === view)));
  }

  let roll = 35;
  function applyState(saved) {
    const value = saved?.modelContent ?? saved;
    if (Number.isFinite(value?.roll)) roll = Math.max(0, Math.min(80, value.roll));
    updatePose(roll);
    setView(["overall", "top", "joint"].includes(value?.view) ? value.view : "overall");
  }
  function saveState() {
    window.openai?.setWidgetState?.({ modelContent: { roll, view }, privateContent: null }).catch(() => {});
  }
  root.querySelector("[data-roll]").addEventListener("input", event => {
    roll = Number(event.target.value); updatePose(roll); saveState();
  });
  root.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => {
    setView(button.dataset.view); saveState();
  }));
  window.addEventListener("openai:set_globals", event => {
    if (event.detail?.globals?.widgetState) applyState(event.detail.globals.widgetState);
  });
  new ResizeObserver(resize).observe(stage);
  new MutationObserver(() => { theme(); render(); }).observe(document.documentElement, { attributes: true, attributeFilter: ["class", "style"] });
  applyState(window.openai?.widgetState);
  loading.remove();
  root.dataset.ready = "true";
} catch (error) {
  loading.textContent = "The 3D view could not load. Reload to try again.";
  loading.setAttribute("role", "alert");
  console.error(error);
}
