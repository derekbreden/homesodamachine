import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const root = document.getElementById("positioner");
const stage = root.querySelector(".positioner-stage");
const loading = root.querySelector(".positioner-loading");
const swivel = root.querySelector("#positioner-swivel");
const pivot = root.querySelector("#positioner-pivot");
const auxiliary = root.querySelector("#positioner-aux");
const detail = root.querySelector("#positioner-selection");

function decode(value, Type) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Type(bytes.buffer);
}

try {
  const response = await fetch("/assemblies/pgfun-positioner.json.gz");
  if (!response.ok) throw new Error(`Assembly download failed (${response.status})`);
  const data = await new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).json();
  if (data.meshFormat !== "creased-f32-v1") throw new Error("Unsupported assembly mesh format");
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor(0, 0);
  stage.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x687182, 1.8));
  const light = new THREE.DirectionalLight(0xffffff, 2);
  light.position.set(250, -350, 650);
  scene.add(light);
  const fill = new THREE.DirectionalLight(0xffffff, 1);
  fill.position.set(-350, 200, 350);
  scene.add(fill);
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 5000);
  camera.up.set(0, 0, 1);
  camera.position.set(620, -790, 650);
  const controls = new OrbitControls(camera, renderer.domElement);
  const yawGroup = new THREE.Group();
  yawGroup.position.fromArray(data.pivot);
  const pitchGroup = new THREE.Group();
  yawGroup.add(pitchGroup);
  const auxiliaryGroup = new THREE.Group();
  scene.add(yawGroup, auxiliaryGroup);
  const meshes = [];
  let selected = null;

  const swatch = document.createElement("span");
  swatch.hidden = true;
  root.appendChild(swatch);
  const color = (token) => {
    swatch.style.color = `var(${token})`;
    return new THREE.Color(getComputedStyle(swatch).color);
  };
  const tokens = { print: "--action", metal: "--text-3", motor: "--text-3", liner: "--text", reference: "--text-2" };

  for (const part of data.parts) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(decode(part.v, Float32Array), 3));
    geometry.setAttribute("normal", new THREE.BufferAttribute(decode(part.n, Int16Array), 3, true));
    geometry.setIndex(new THREE.BufferAttribute(decode(part.f, part.indexType === "uint32" ? Uint32Array : Uint16Array), 1));
    const token = part.name.startsWith("rotator:") ? "--text-3" : tokens[part.category];
    const material = new THREE.MeshStandardMaterial({
      color: color(token), roughness: 0.65,
      metalness: part.category === "metal" ? 0.35 : 0.05,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = part.name;
    mesh.userData.colorToken = token;
    mesh.userData.motionGroup = part.group;
    const parent = part.group === "pitch" ? pitchGroup : part.group === "yaw" ? yawGroup :
      part.group === "camera" || /umbilical|controller|fan-guard/.test(part.name) ? auxiliaryGroup : scene;
    parent.add(mesh);
    meshes.push(mesh);
  }

  function render() { renderer.render(scene, camera); }

  function frameAssembly() {
    scene.updateMatrixWorld(true);
    const bounds = new THREE.Box3();
    for (const mesh of meshes) if (mesh.parent !== auxiliaryGroup || auxiliaryGroup.visible) bounds.expandByObject(mesh);
    const center = bounds.getCenter(new THREE.Vector3());
    const direction = camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(center).add(direction);
    camera.lookAt(center);
    const inverse = camera.quaternion.clone().invert();
    const vertical = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) * 0.92;
    const horizontal = vertical * camera.aspect;
    let distance = 1;
    for (const x of [bounds.min.x, bounds.max.x]) {
      for (const y of [bounds.min.y, bounds.max.y]) {
        for (const z of [bounds.min.z, bounds.max.z]) {
          const corner = new THREE.Vector3(x, y, z).sub(center).applyQuaternion(inverse);
          distance = Math.max(distance, corner.z + Math.max(Math.abs(corner.x) / horizontal, Math.abs(corner.y) / vertical));
        }
      }
    }
    camera.position.copy(center).addScaledVector(direction, distance);
    controls.target.copy(center);
    controls.update();
  }

  function applyPose() {
    yawGroup.rotation.z = THREE.MathUtils.degToRad(Number(swivel.value));
    pitchGroup.rotation.x = THREE.MathUtils.degToRad(Number(pivot.value));
    auxiliaryGroup.visible = auxiliary.checked;
    root.querySelector("#positioner-swivel-value").value = `${Number(swivel.value).toFixed(2)}°`;
    root.querySelector("#positioner-pivot-value").value = `${Number(pivot.value).toFixed(2)}°`;
    render();
  }

  for (const input of [swivel, pivot]) {
    input.min = -data.softLimitDeg;
    input.max = data.softLimitDeg;
    input.addEventListener("input", applyPose);
  }
  auxiliary.addEventListener("change", () => {
    if (selected?.parent === auxiliaryGroup && !auxiliary.checked) {
      selected.material.color.copy(color(selected.userData.colorToken));
      selected = null;
      detail.textContent = "Gun, printed fixture and existing rotator";
    }
    applyPose();
    frameAssembly();
    render();
  });
  controls.addEventListener("change", render);

  const raycaster = new THREE.Raycaster();
  let pointerDown = null;
  renderer.domElement.addEventListener("pointerdown", (event) => {
    pointerDown = [event.clientX, event.clientY];
  });
  renderer.domElement.addEventListener("pointerup", (event) => {
    if (!pointerDown || Math.hypot(event.clientX - pointerDown[0], event.clientY - pointerDown[1]) > 5) return;
    pointerDown = null;
    const rect = renderer.domElement.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2(
      (event.clientX - rect.left) / rect.width * 2 - 1,
      -(event.clientY - rect.top) / rect.height * 2 + 1,
    ), camera);
    const visible = meshes.filter((mesh) => mesh.parent !== auxiliaryGroup || auxiliaryGroup.visible);
    if (selected) selected.material.color.copy(color(selected.userData.colorToken));
    selected = raycaster.intersectObjects(visible, false)[0]?.object || null;
    if (selected) selected.material.color.copy(color("--text"));
    detail.textContent = selected ? selected.name.replace(/[:_-]+/g, " ") : "Gun, printed fixture and existing rotator";
    render();
  });
  renderer.domElement.addEventListener("pointercancel", () => { pointerDown = null; });

  function resize() {
    const rect = stage.getBoundingClientRect();
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    renderer.setSize(rect.width, rect.height, false);
    frameAssembly();
    render();
  }
  applyPose();
  resize();
  new ResizeObserver(resize).observe(stage);
  for (const input of [swivel, pivot, auxiliary]) input.disabled = false;
  loading.remove();
  root.dataset.ready = "true";
  root.dataset.geometrySha256 = data.geometrySha256;
  // Same browser inspection surface as the CAD viewer's window.__hsm.
  window.__hsmPositioner = { THREE, scene, camera, controls, renderer, yawGroup, pitchGroup, auxiliaryGroup, meshes };
} catch (error) {
  root.dataset.error = error.message;
  loading.textContent = "The assembly could not load. Reload this page, or open the fixture CAD or guide above.";
  loading.setAttribute("role", "alert");
  console.error(error);
}
