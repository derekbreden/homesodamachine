// Installed-location views uncover the selected unit while keeping its surroundings solid.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { standsIn } from "/contracts/body-path.js";
import { state } from "./state.js";
import { camera } from "./scene.js";
import { clearHighlight, frameParts } from "./part-highlight.js";
import { selectComponent, setComponentPickEnabled, applyHiddenComponents } from "./component-picker.js";
import { setXrayEnabled } from "./xray.js";

let sequence = 0;
const nextFrame = () => new Promise(requestAnimationFrame);

export async function enterInstance(name, { members = [name], fly = true } = {}) {
  const token = ++sequence, file = state.mountedDetail?.file;
  const names = new Set(members);
  let cancelled = false;
  const current = () => !cancelled && token === sequence && file === state.mountedDetail?.file;
  const picked = event => { if (event.detail.name !== name) cancelled = true; };
  clearHighlight({ owner: "materials" });
  state.autoHiddenComponents.clear();
  state.autoHiddenFile = file;
  for (const hidden of state.hiddenComponents) {
    if (members.some(body => standsIn(body, hidden))) state.hiddenComponents.delete(hidden);
  }
  setXrayEnabled(false, { persist: false });
  applyHiddenComponents();
  setComponentPickEnabled(true);
  selectComponent(name, { members });
  window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, picked);
  try {
    await nextFrame();
    if (fly && !await frameParts(members, { outward: true })) return;
    await nextFrame();
    if (!current()) return;
    const started = performance.now(), group = state.currentGroup;
    const meshes = group.children.filter(mesh => mesh.userData?.side === "front" && mesh.visible !== false);
    const selected = meshes.filter(mesh => names.has(mesh.name));
    const others = meshes.filter(mesh => !names.has(mesh.name));
    const box = new THREE.Box3(), p = new THREE.Vector3();
    group.updateWorldMatrix(true, true);
    camera.updateMatrixWorld();
    for (const mesh of selected) box.expandByObject(mesh);
    if (box.isEmpty()) return;
    const min = new THREE.Vector2(Infinity, Infinity), max = new THREE.Vector2(-Infinity, -Infinity);
    for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
      p.set(x, y, z).project(camera);
      min.min(p); max.max(p);
    }
    const ray = new THREE.Raycaster(), point = new THREE.Vector2(), blockers = new Set();
    for (const u of [0.25, 0.5, 0.75]) for (const v of [0.25, 0.5, 0.75]) {
      if (!current() || state.currentGroup !== group) return;
      point.set(THREE.MathUtils.lerp(min.x, max.x, u), THREE.MathUtils.lerp(min.y, max.y, v));
      ray.setFromCamera(point, camera);
      ray.far = Infinity;
      const target = ray.intersectObjects(selected, false)[0];
      if (target) {
        ray.far = target.distance - 0.01;
        for (const hit of ray.intersectObjects(others, false)) blockers.add(hit.object.name);
      }
      await nextFrame();
    }
    if (!current()) return;
    state.autoHiddenComponents = blockers;
    applyHiddenComponents();
    return { name, bodies: members, hidden: [...blockers], milliseconds: performance.now() - started };
  } finally { window.removeEventListener(HSM_EVENTS.MATERIAL_PICKED, picked); }
}
