// Part selections and installed locations uncover their geometry in solid context.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { standsIn } from "/contracts/body-path.js";
import { materialForFile } from "/contracts/materials.js";
import { instancesInScene } from "/contracts/material-instances.js";
import { state } from "./state.js";
import { camera } from "./scene.js";
import { clearHighlight, frameParts, highlightParts } from "./part-highlight.js";
import { selectComponent, setComponentPickEnabled, applyHiddenComponents, loadHiddenForFile } from "./component-picker.js";
import { isXrayEnabled, setXrayEnabled } from "./xray.js";

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

export function clearMaterialView() {
  const group = state.currentGroup;
  if (!group?.userData.instanceView?.material) return;
  delete group.userData.instanceView;
  state.autoHiddenComponents.clear();
  applyHiddenComponents();
}

// Each installed copy gets its own sight lines when a BOM row names several copies.
function materialLocations(material, members) {
  if (members.length === 1) return [members];
  const catalog = state.materialCatalog, model = materialForFile(catalog, state.mountedDetail?.file);
  const locations = instancesInScene(catalog, model?.id, material, members, { finish: state.faucetFinish })
    .map(instance => instance.bodies);
  const covered = new Set(locations.flat());
  const remaining = members.filter(body => !covered.has(body));
  if (remaining.length) locations.push(remaining);
  return locations;
}

function showContext(group, members, { locations, fly, preview = false, material = null }) {
  const names = new Set(members), previous = group.userData.instanceView;
  const reveal = material ? [] : [...state.hiddenComponents].filter(hidden => members.some(body => standsIn(body, hidden)));
  const keepView = !fly && previous && previous.names.size === names.size
    && !reveal.length && members.every(body => previous.names.has(body));
  if (isXrayEnabled() && (!keepView || !material)) setXrayEnabled(false, { persist: false });
  if (keepView) {
    previous.preview = preview;
    previous.material = material;
    return;
  }

  const view = group.userData.instanceView = { names, preview, material, rays: [] };
  state.autoHiddenComponents.clear();
  state.autoHiddenFile = state.mountedDetail?.file;
  for (const hidden of reveal) state.hiddenComponents.delete(hidden);
  applyHiddenComponents();
  if (fly) frameParts(members, { outward: true, instant: true });
  group.updateWorldMatrix(true, true);
  camera.updateMatrixWorld();
  const solids = visibleSolids(group);
  const targets = locations || materialLocations(material, members);
  view.rays = targets.flatMap(location => sightLines(solids.filter(mesh => location.includes(mesh.name))));
  uncoverContext(group, solids);
  applyHiddenComponents();
}

export function uncoverMaterialParts(material, members, { fly }) {
  showContext(state.currentGroup, members, { fly, material });
}

export function enterInstance(name, { members = [name], locations = [members], fly = true, preview = false } = {}) {
  const group = state.currentGroup;
  if (!group || !members.length) return false;
  clearHighlight({ owner: "materials" });
  showContext(group, members, { locations, fly, preview });
  setComponentPickEnabled(true);
  if (preview) highlightParts(members, { owner: "materials", fly: false, visibleOnly: true, hold: false });
  else selectComponent(name, { members });
  return true;
}

window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, event => {
  const group = state.currentGroup, view = group?.userData.instanceView;
  if (view && !view.preview && !view.material && event.detail.file === state.mountedDetail?.file && !view.names.has(event.detail.name)) {
    delete group.userData.instanceView;
  }
});
