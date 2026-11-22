// Blueprint draws whole exposed components with translucent faces and their feature edges.
import * as THREE from 'three';
import { HSM_EVENTS } from '/contracts/client-events.js';
import {createXrayRenderer} from './xray-render.js';
import {createBlueprintExposure} from './blueprint-visibility.js';
import {requestFeatureEdges} from './feature-edges.js';
import * as picker from './component-units.js';
import * as scene from './scene.js';
import {state} from './state.js';
import {makeToolChip} from './tool-rail.js';

const preference = 'step-blueprint';
let chip, enabled = false;
try { enabled = (localStorage.getItem(preference) ?? localStorage.getItem('step-xray')) === '1'; } catch {}
const invalidate = () => scene.requestCadRender?.();
const rendering = createXrayRenderer({enabled, requestEdges:requestFeatureEdges, invalidate});
const layerMasks = new Map();
let group = null, classifier = null, exposed = null, timer = 0, revision = 0, reading = false;
let viewMatrix = new THREE.Matrix4(), projection = new THREE.Matrix4(), width = 0, height = 0;
const size = new THREE.Vector2();
const solidOwner = solid => picker.componentOwner?.(solid.name) || solid.name || solid.uuid;

function restoreLayer(solid) {
  if (!layerMasks.has(solid)) return;
  solid.layers.mask = layerMasks.get(solid);
  layerMasks.delete(solid);
}
function releaseView() {
  clearTimeout(timer); timer = 0;
  revision++;
  for (const solid of layerMasks.keys()) restoreLayer(solid);
  classifier?.dispose();
  classifier = null;
  group = null;
  exposed = null;
  width = height = 0;
  window.dispatchEvent(new Event(HSM_EVENTS.BLUEPRINT_VISIBILITY));
}
function paint() {
  if (!group || !exposed) return;
  let changed = false;
  for (const solid of group.children) {
    if (solid.userData.side !== 'front') continue;
    if (exposed.has(solidOwner(solid))) {
      changed ||= layerMasks.has(solid);
      restoreLayer(solid);
    } else {
      changed ||= !layerMasks.has(solid);
      if (!layerMasks.has(solid)) layerMasks.set(solid, solid.layers.mask);
      solid.layers.mask = 0;
    }
  }
  rendering.apply(group, true, solid => solid.visible && !layerMasks.has(solid));
  if (changed) window.dispatchEvent(new Event(HSM_EVENTS.BLUEPRINT_VISIBILITY));
  invalidate();
}
async function classify() {
  timer = 0;
  if (!enabled || !group || reading) return;
  const ticket = revision, mounted = group;
  const solids = group.children.filter(mesh => mesh.userData.side === 'front');
  const current = () => ticket === revision && group === mounted;
  reading = true;
  try {
    classifier ||= createBlueprintExposure();
    const names = await classifier.exposedComponents(scene.renderer, scene.camera, solids, solidOwner, current);
    if (!current() || !names) return;
    exposed = names;
    paint();
  } catch (error) {
    if (ticket !== revision || group !== mounted) return;
    console.warn('Blueprint visibility:', error);
    // Keep components accessible if the browser loses its offscreen target.
    exposed = new Set(solids.map(solidOwner));
    paint();
  } finally {
    reading = false;
    if (enabled && group && revision !== ticket && !timer) invalidateBlueprintVisibility();
  }
}
export function invalidateBlueprintVisibility() {
  if (!enabled || !group) return;
  revision++;
  clearTimeout(timer);
  timer = setTimeout(classify, 160);
}
export function updateBlueprintView(renderer, camera, mounted) {
  if (!enabled || !mounted || group !== mounted) return;
  camera.updateWorldMatrix(true, false);
  renderer.getDrawingBufferSize(size);
  if (viewMatrix.equals(camera.matrixWorld) && projection.equals(camera.projectionMatrix)
      && width === size.x && height === size.y) return;
  viewMatrix.copy(camera.matrixWorld);
  projection.copy(camera.projectionMatrix);
  width = size.x; height = size.y;
  invalidateBlueprintVisibility();
}

export const makeEdgeMaterial = params => rendering.makeEdgeMaterial(params);
export const syncEdgeResolution = rendering.syncEdgeResolution;
export const forgetEdgeMaterials = rendering.forgetEdgeMaterials;
export function applyXray(mounted, on = enabled) {
  if (!mounted || mounted !== state.currentGroup) return;
  if (group && group !== mounted) { rendering.restore(group); releaseView(); }
  if (!on) {
    if (group) { releaseView(); rendering.apply(mounted, false); }
    invalidate();
    return;
  }
  group = mounted;
  if (exposed) paint();
  invalidateBlueprintVisibility();
  invalidate();
}
export function disposeXray(mounted) {
  if (group === mounted) releaseView();
  rendering.dispose(mounted);
}
export function releaseBlueprintSolid(solid) {
  restoreLayer(solid);
  rendering.release(solid);
}
export function setMeshMaterial(_group, mesh, material) {
  rendering.setMeshMaterial(mesh, material, enabled && !!exposed && !layerMasks.has(mesh));
}
export function setXrayEnabled(on, {persist = true} = {}) {
  enabled = !!on;
  rendering.setEnabled(enabled);
  if (persist) { try { localStorage.setItem(preference, enabled ? '1' : '0'); } catch {} }
  applyXray(state.currentGroup);
  chip?.refresh();
}
export function isXrayEnabled() { return enabled; }
export function makeXrayToggle() {
  chip = makeToolChip({
    className:'blueprint-toggle', label:'Blueprint', icon:'xray',
    title:'Draw the complete outline of each exposed component',
    read:isXrayEnabled, write:setXrayEnabled,
  });
  return chip;
}
