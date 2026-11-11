// Installed locations keep their context solid and uncover the selected parts.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { standsIn } from "/contracts/body-path.js";
import { state } from "./state.js";
import { camera } from "./scene.js";
import { clearHighlight, frameParts, highlightParts } from "./part-highlight.js";
import { selectComponent, setComponentPickEnabled, applyHiddenComponents, loadHiddenForFile } from "./component-picker.js";
import { setXrayEnabled } from "./xray.js";

function visibleSolids(group) {
  return group.children.filter(mesh => mesh.userData?.side === "front" && mesh.visible !== false);
}

// Fix the rays in the entrance pose so later context can be tested as it arrives.
function sightLines(selected) {
  const box = new THREE.Box3(), p = new THREE.Vector3();
  for (const mesh of selected) box.expandByObject(mesh);
  if (box.isEmpty()) return [];
  const min = new THREE.Vector2(Infinity, Infinity), max = new THREE.Vector2(-Infinity, -Infinity);
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    p.set(x, y, z).project(camera);
    min.min(p); max.max(p);
  }
  const rays = [], point = new THREE.Vector2();
  for (const u of [0.25, 0.5, 0.75]) for (const v of [0.25, 0.5, 0.75]) {
    const ray = new THREE.Raycaster();
    point.set(THREE.MathUtils.lerp(min.x, max.x, u), THREE.MathUtils.lerp(min.y, max.y, v));
    ray.setFromCamera(point, camera);
    const hit = ray.intersectObjects(selected, false)[0];
    if (hit) {
      ray.far = hit.distance - 0.01;
      rays.push(ray);
    }
  }
  return rays;
}

// Run before an arriving solid can be painted over the selected location.
export function uncoverContext(group, solids) {
  const view = group.userData.instanceView;
  if (!view?.rays.length || group !== state.currentGroup) return;
  const shown = view.shown ? [...view.shown] : [];
  const hits = [];
  for (const mesh of solids) {
    if (!mesh.visible || view.names.has(mesh.name) || shown.some(body => standsIn(mesh.name, body))) continue;
    mesh.updateWorldMatrix(true, false);
    for (const ray of view.rays) {
      ray.intersectObject(mesh, false, hits);
      if (!hits.length) continue;
      state.autoHiddenComponents.add(mesh.name);
      mesh.visible = false;
      hits.length = 0;
      break;
    }
  }
}

export function clearInstancePreview() {
  const group = state.currentGroup;
  if (!group?.userData.instanceView?.preview) return;
  delete group.userData.instanceView;
  state.autoHiddenComponents.clear();
  loadHiddenForFile(state.mountedDetail?.file);
  applyHiddenComponents();
}

export function enterInstance(name, { members = [name], locations = [members], fly = true, preview = false } = {}) {
  const group = state.currentGroup;
  if (!group || !members.length) return false;
  const names = new Set(members), previous = group.userData.instanceView;
  const keepView = !fly && previous && previous.names.size === names.size
    && members.every(body => previous.names.has(body));
  setXrayEnabled(false, { persist: false });
  if (!keepView) {
    clearHighlight({ owner: "materials" });
    state.autoHiddenComponents.clear();
    state.autoHiddenFile = state.mountedDetail?.file;
    for (const hidden of state.hiddenComponents) {
      if (members.some(body => standsIn(body, hidden))) state.hiddenComponents.delete(hidden);
    }
    applyHiddenComponents();
    if (fly) frameParts(members, { outward: true, instant: true });
    group.updateWorldMatrix(true, true);
    camera.updateMatrixWorld();
    const solids = visibleSolids(group);
    const rays = locations.flatMap(location => sightLines(solids.filter(mesh => location.includes(mesh.name))));
    group.userData.instanceView = { names, preview, rays };
    uncoverContext(group, solids);
    applyHiddenComponents();
  } else previous.preview = preview;
  setComponentPickEnabled(true);
  if (preview) highlightParts(members, { owner: "materials", fly: false, fill: true, fade: false, hold: false });
  else selectComponent(name, { members });
  return true;
}

window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, event => {
  const group = state.currentGroup, view = group?.userData.instanceView;
  if (view && !view.preview && event.detail.file === state.mountedDetail?.file && !view.names.has(event.detail.name)) {
    delete group.userData.instanceView;
  }
});
