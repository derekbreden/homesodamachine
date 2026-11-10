// Native surface loading, browser STEP fallback and thumbnail rendering. step-runtime.js
// holds the page's parser, materials and thumbnail renderer across hot imports.

import * as THREE from "three";
import { decodeMeshPayload } from "./mesh-payload.js";
export { decodeMeshPayload } from "./mesh-payload.js";
import { resolveScene } from "./shared-scene.js";
import { state } from "./state.js";
import { scene, camera, resetCamera, fitCameraDepth, fitFog, BG_COLOR } from "./scene.js";
import * as sceneState from "./scene.js";
import * as xray from "./xray.js";
import { getOcct, getThumbnailRuntime, stepRuntime } from "./step-runtime.js";
import { beginCadLoad, disposeCadGroup } from "./cad-resources.js";
import { setActiveEdges } from "./edge-picker.js";
import { clearPickFind } from "./pick-find.js";
import { dropHighlight } from "./part-highlight.js";
import { clearComponentPicker, loadHiddenForFile, applyHiddenComponents } from "./component-picker.js";
import { onStepReloaded } from "./component-edit.js";
import { surfaceText } from "./pick-format.js";
import { fetchMember, memberLoaded, memberUrl, rememberMember } from "./member.js";
import { FAUCET_FINISHES, faucetStyleFor, hasFaucetFinish, isFaucetFinishBody, showsInFaucetFinish } from "/contracts/faucet-options.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { stepLocation } from "/contracts/step-locations.js";
import { matchesBody, materialForFile } from "/contracts/materials.js";
import { componentUnitsInScene, unitForBody } from "/contracts/material-instances.js";

const { applyXray, syncEdgeResolution, setMeshMaterial } = xray;
// Hot loaders can share a scene module retained by an open page.
const invalidateModelBounds = () => sceneState.invalidateModelBounds?.();

// --- STEP parsing ---
async function parseStep(buffer) {
  const occt = await getOcct();
  const result = occt.ReadStepFile(buffer, null);
  backfillMeshNames(result);
  return result;
}

// Native kernel payloads carry part arrays and face contributors; print-payload
// derives viewer surfaces from print meshes. Shared scene manifests retain part
// references and placements. mesh-payload.js decodes readable flat containers and
// shared-scene.js resolves references into the same meshes contract as the browser
// STEP parser. build-data/src/payload.rs reads the flat container for bookkeeping.
// Flat positions/normals are f32 and indices/face ranges are u32. Inclusive face
// triangle ranges reach the edge picker as `brep_faces`, regardless of producer.
// Unreadable or absent payloads fall back to a standalone STEP when one exists.
// Neither path starts a geometry build.

// occt-import-js copies a product's name onto its mesh only when the product is a
// single solid. A multi-solid component (our reference sub-assemblies, the pump
// assemblies, the display) comes back with unnamed leaf meshes — the name lives
// on the owning hierarchy node instead. Walk the node tree and stamp each unnamed
// mesh with its component's name, so the edge picker's `solid:` blob line names
// the tray you clicked, not just the single-solid parts (reservoir, shell halves,
// funnel). Each mesh is listed by exactly one node, so the unnamed-only guard
// never clobbers a real per-mesh name.
function backfillMeshNames(result) {
  if (!result || !result.meshes || !result.root) return;
  const visit = (node) => {
    if (node.name && node.meshes) {
      for (const mi of node.meshes) {
        const mesh = result.meshes[mi];
        if (mesh && !mesh.name) mesh.name = node.name;
      }
    }
    (node.children || []).forEach(visit);
  };
  visit(result.root);
}

// Parts with no recorded colour take the default. Native payloads and the browser
// STEP parser carry a recorded linear RGB colour as mesh.color.
const DEFAULT_FRONT = 0x8899aa;
const BACK_DARKEN = 0.75; // back faces a shade darker so thin parts read from behind

// A solid is one double-sided draw, and the darkening of its back faces happens
// inside that draw. xray.js clones these materials for its ghost variant and
// carries the injection across with them.
export function darkenBackFaces(shader) {
  shader.fragmentShader = shader.fragmentShader.replace(
    "#include <color_fragment>",
    `#include <color_fragment>
    if ( !gl_FrontFacing ) diffuseColor.rgb *= ${BACK_DARKEN.toFixed(3)};`,
  );
}

// Materials share the exact linear colour triple across meshes and loads. Keeping
// its precision prevents nearby catalog swatches from sharing a material by rounding.
const _matCache = stepRuntime.materials;

// hsm-finishes reads the shared-data material and routing catalogs into finishes.json.
// A body's colour selects its catalog roughness and metalness so distinct stocks
// retain their own response to light.
export const DEFAULT_FINISH = { roughness: 0.6, metalness: 0.1 };

// Native catalog colours and browser STEP conversion can differ in floating-point
// arithmetic. Match only within FINISH_TOL2; a colour outside it has no catalog finish.
const FINISH_TOL2 = 4e-4 * 4e-4;

export function loadFinishes() {
  if (!stepRuntime.finishesReady || stepRuntime.finishesVersion !== state.codeVersion) {
    stepRuntime.finishesVersion = state.codeVersion;
    const ready = fetch("/finishes.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (stepRuntime.finishesReady !== ready) return;
        stepRuntime.finishes = Array.isArray(d?.finishes) ? d.finishes : [];
        // Anything already built was built at the default, and `_matCache` would hand that
        // same material out for the rest of the session. Drop it so the table applies.
        forgetMaterials();
      })
      .catch(() => {
        if (stepRuntime.finishesReady === ready) {
          stepRuntime.finishes = [];
          forgetMaterials();
        }
      });
    stepRuntime.finishesReady = ready;
  }
  return stepRuntime.finishesReady;
}

// A body whose colour names no material takes the default rather than its nearest neighbour's
// surface: an unplaced colour is a gap in the table, and a gap should read as one.
function finishFor(color) {
  if (!color || !stepRuntime.finishes.length) return DEFAULT_FINISH;
  let best = DEFAULT_FINISH;
  let bestD = FINISH_TOL2;
  for (const f of stepRuntime.finishes) {
    const dr = f.rgb[0] - color[0], dg = f.rgb[1] - color[1], db = f.rgb[2] - color[2];
    const d = dr * dr + dg * dg + db * db;
    if (d <= bestD) { bestD = d; best = f; }
  }
  return best;
}

function materialFor(color, surface = null) {
  const key = surface ? `faucet:${surface.id}` : color ? color.join(",") : "default";
  let mat = _matCache.get(key);
  if (!mat) {
    const finish = surface || finishFor(color);
    // Surfaces sit a depth-unit back, so the feature edges xray.js draws on
    // these same triangles resolve in front of them.
    mat = new THREE.MeshStandardMaterial({
      color: color ? new THREE.Color(color[0], color[1], color[2]) : new THREE.Color(DEFAULT_FRONT),
      metalness: finish.metalness, roughness: finish.roughness,
      side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    });
    mat.onBeforeCompile = darkenBackFaces;
    mat.customProgramCacheKey = () => "hsm-back-darken";
    _matCache.set(key, mat);
  }
  return mat;
}

// Dispose cached materials so a finish-table update applies to the next mount.
export function forgetMaterials() {
  for (const material of _matCache.values()) material.dispose();
  _matCache.clear();
}

// A displayed body can have indexed mesh leaves named `<body>/<n>`. Native scene
// readers and imports retain the body's identity by removing only a trailing
// numeric index. Do that once for payloads and parsed STEPs before scorecards,
// highlights and clipboard picks name the body; assembly branches stay intact.
const bodyName = (name) => (name || "").replace(/\/\d+$/, "");

function buildMesh(result, file = null, finishId = state.faucetFinish) {
  const group = new THREE.Group();
  const finish = FAUCET_FINISHES.find((f) => f.id === finishId) || FAUCET_FINISHES[0];

  result.meshes.forEach((mesh, occtIndex) => {
    const attributes=mesh.localAttributes || mesh.attributes;
    const indices=mesh.localIndex || mesh.index;
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(attributes.position.array), 3));
    if (attributes.normal) {
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(new Float32Array(attributes.normal.array), 3));
    }
    if (indices) {
      geo.setIndex(new THREE.BufferAttribute(new Uint32Array(indices.array), 1));
    }
    geo.computeBoundingBox();

    // One double-sided draw per solid, so a thin part still reads from behind.
    // occt-import-js hands us mesh.color per solid when the STEP carries one;
    // else gray. The occt mesh index rides along so the edge picker's face
    // raycast can map a hit triangle back to its BREP face.
    const name = bodyName(mesh.name);
    let material = isFaucetFinishBody(file, name)
      ? materialFor(finish.rgb, finish) : materialFor(mesh.color);
    const owned = mesh.opacity != null && mesh.opacity < 1;
    if (owned) {material=material.clone();material.transparent=true;material.opacity=mesh.opacity;material.depthWrite=false;}
    const solid = new THREE.Mesh(geo, material);
    solid.userData.ownsMaterial=owned;
    solid.userData.occtIndex = occtIndex;
    solid.userData.features = mesh.features || [];
    solid.userData.side = "front"; // the name the face raycast selects on
    // Carry the component name (backfilled from the STEP assembly node) onto the mesh so
    // the scorecard's clickable rows can find a solid by name (part-highlight.js).
    solid.name = name;
    placeSharedMesh(solid,mesh);
    // A body only one faucet finish has (a White faucet's union) is out of the other's view.
    solid.visible = showsInFaucetFinish(file, name, finish.id);
    group.add(solid);
  });

  return group;
}

function placeSharedMesh(solid,mesh) {
  if (!mesh.geometryKey) return;
  const m=mesh.placement || [[1,0,0,0],[0,1,0,0],[0,0,1,0]];
  solid.matrix.set(...m[0],...m[1],...m[2],0,0,0,1);
  solid.matrixAutoUpdate=false;solid.matrixWorldNeedsUpdate=true;
}

export function setFaucetFinish(finishId) {
  const finish = FAUCET_FINISHES.find((f) => f.id === finishId);
  if (!finish) return;
  state.faucetFinish = finish.id;
  const file = state.mountedDetail?.file;
  const group = state.currentGroup;
  if (group && hasFaucetFinish(file)) {
    for (const mesh of group.children) {
      if (mesh.userData?.side === "front" && isFaucetFinishBody(file, mesh.name)) {
        setMeshMaterial(group, mesh, materialFor(finish.rgb, finish));
      }
    }
    // The bodies only one finish has come and go with it, alongside what the viewer hid by hand.
    if (faucetStyleFor(file)) applyHiddenComponents();
  }
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.FAUCET_OPTIONS));
}

// Prefer completed native payloads and shared manifests. Their meshes feed the
// same material and picker code as parsed STEPs; face ranges reconstruct edges
// from the drawn triangles. A payload route can exist without a standalone STEP.
// Immutable member URLs identify published revisions, while the local route
// revalidates completed output bytes. Fetching either starts no producer.
// `mounted` says this file is the one already in the scene. It carries the caller's
// If-None-Match and gates the store's own unchanged answer.
async function fetchMeshes(file, headers, { mounted = false, signal, onPart } = {}) {
  file = stepLocation(file).file;
  try {
    // THE STORE ANSWERS FIRST WHERE IT HAS THESE BYTES. Its URL carries their hash, so a URL
    // that has not moved is a model that has not moved, and a repeat open never leaves the
    // browser. A store that does not answer falls through to this site's own route below.
    const url = memberUrl(`${file}.mesh`);
    let bytes = null;
    if (url) {
      if (mounted && memberLoaded(`${file}.mesh`, url)) return { unchanged: true };
      try {
        bytes = await fetchMember(url, { signal });
      } catch { /* the site's route has the same member */ }
    }
    let resp = null;
    if (!bytes) {
      resp = await fetch(`/meshes/${file}.mesh`, { headers, signal });
      if (resp.status === 304) return { unchanged: true };
      if (!resp.ok) return null;
      bytes = new Uint8Array(await resp.arrayBuffer());
    }
    const result = await resolveScene(bytes, { sourceUrl: resp ? null : url, signal, onPart });
    if (!result) return null; // a payload this code doesn't read is no payload
    // `url` only when the store is where these bytes came from. Whoever mounts them records it
    // as what is on screen; a thumbnail asks through here too and mounts nothing.
    return { etag: resp?.headers.get("etag") ?? null, result, url: resp ? null : url };
  } catch {
    return null;
  }
}

// Name the representation after the loader knows what reached the canvas. A step:
// route can draw a shared scene, a flat viewer payload or a parsed standalone STEP.
function nameSurface(file, surface) {
  const wrapper = state.currentCadWrapper;
  if (!wrapper) return;                      // headless: no chrome to name
  const here = (wrapper.closest(".cad-workspace") || wrapper).querySelector(".cad-crumb-here");
  if (here) here.title = surfaceText(file, state.mountedDetail?.scene ? 'scene' : surface);
}

// An opened component includes every body of its authored physical placement.
function componentViewBodies(location, names) {
  const material = materialForFile(state.materialCatalog, location.file);
  const units = componentUnitsInScene(state.materialCatalog, material?.id, names, { finish: state.faucetFinish });
  return unitForBody(units, location.component)?.bodies || [location.component];
}

// Completed parts replace their own GPU meshes while unfinished parts keep their last drawing.
function mountScenePart(node, meshes, head, file, location, { current, preserveCamera, componentBodies }) {
  if (!current()) return;
  if (location.component) meshes = meshes.filter(mesh => componentBodies.some(body => matchesBody(mesh.name, body)));
  if (!meshes.length) return;
  let group = state.currentGroup;
  if (group?.userData.sharedFile !== file) {
    if (group) { scene.remove(group); disposeCadGroup(group); }
    group = new THREE.Group(); group.userData.sharedFile = file;
    group.userData.parts = new Map(); state.currentGroup = group; scene.add(group);
    group.userData.fitWhenReady = !preserveCamera;
  }
  const parts = group.userData.parts;
  group.userData.sceneLoading = true;
  const prior = parts.get(node.name);
  const key = meshes.map(mesh => mesh.objectKey).join('|');
  const sameGeometry=prior && prior.meshes.length===meshes.length && meshes.every((mesh,i)=>
    mesh.geometryKey===prior.meshes[i].geometryKey && JSON.stringify(mesh.color)===JSON.stringify(prior.meshes[i].color) && mesh.opacity===prior.meshes[i].opacity);
  if (prior && prior.key!==key && sameGeometry) {
    xray.disposeXray?.(group);
    meshes.forEach((mesh,i)=>placeSharedMesh(prior.solids[i],mesh));
    prior.meshes=meshes;prior.key=key;
    invalidateModelBounds();
  } else if (!prior || prior.key !== key) {
    xray.disposeXray?.(group);
    if (prior) for (const solid of prior.solids) { group.remove(solid); solid.geometry.dispose(); if(solid.userData.ownsMaterial)solid.material.dispose(); }
    const replacement = buildMesh({ meshes }, file);
    const solids = [...replacement.children];
    for (const solid of solids) group.add(solid);
    parts.set(node.name, { meshes, solids, key });
    invalidateModelBounds();
  }
  const present = new Set(head.meshes.map(part => part.name));
  for (const [name,part] of parts) if (!present.has(name)) {
    for (const solid of part.solids) {group.remove(solid);solid.geometry.dispose();if(solid.userData.ownsMaterial)solid.material.dispose();}
    parts.delete(name);
    invalidateModelBounds();
  }
  group.userData.sharedHead = head;
  if (group.userData.sharedFrame) return;
  group.userData.sharedFrame = requestAnimationFrame(() => {
    group.userData.sharedFrame = null;
    if (!current() || state.currentGroup !== group) return;
    const latest = group.userData.sharedHead;
    const ordered = latest.meshes.flatMap(part => parts.get(part.name) ? [parts.get(part.name)] : []);
    const result = { meshes: ordered.flatMap(part => part.meshes), src: latest.src, cut: latest.cut };
    let index = 0;
    for (const part of ordered) for (const solid of part.solids) solid.userData.occtIndex = index++;
    setActiveEdges(result); clearPickFind(); dropHighlight(); clearComponentPicker({ preserve: true }); applyXray(group);
    state.mountedDetail = {type:'step',file,sourceFile:location.file,surface:'mesh',src:latest.src,cut:latest.cut,scene:true};
    nameSurface(location.file,'mesh');loadHiddenForFile(file);applyHiddenComponents();onStepReloaded();
    if (group.userData.fitWhenReady) {resetCamera(group);group.userData.fitWhenReady=false;}
    window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_MOUNTED,{detail:{file,part:node.name,revision:latest.src,complete:false}}));
  });
}

export async function loadStepFile(file, { preserveCamera = false } = {}) {
  const location = stepLocation(file);
  const load = beginCadLoad();
  const { current, signal } = load;
  if (state.currentGroup?.userData.sharedFrame) {
    cancelAnimationFrame(state.currentGroup.userData.sharedFrame);
    state.currentGroup.userData.sharedFrame = null;
  }
  await loadFinishes();   // before any material is built, so none is built at the default
  if (!current()) { load.finish(); return; }
  // Loading pill lives inside the current step wrapper (or none if the
  // headless tool drove loadStepFile directly). Tolerate either.
  const loadingEl = state.currentCadWrapper && state.currentCadWrapper.querySelector(".cad-loading");
  const pill = loadingEl && loadingEl.querySelector("span");
  if (pill) pill.textContent = "Loading…";
  if (loadingEl) loadingEl.style.display = "block";
  // A load that ends without a model on the canvas leaves the scrim up saying
  // so. Hiding it would leave a featureless dark viewport and a live toolbar
  // over nothing.
  let landed = false;
  const failed = (msg) => { if (pill && current()) pill.textContent = msg; };

  try {
    // If we're refetching the same file that's already in the scene, send
    // If-None-Match so the server can answer 304 when bytes are unchanged
    // (avoids the visible re-render flash on a deploy that didn't touch
    // this file). Revalidation follows the payload or STEP actually requested.
    const headers = {};
    const prevEtag = state.stepEtags.get(file);
    // THE FILE THE CANVAS ALREADY HOLDS, which is what a return with nothing mounted leaves on
    // screen. The ETag round trip below and the store's URL comparison further down both ask
    // this first.
    const mounted = state.mountedDetail?.type === "step"
      && state.mountedDetail.file === file;
    if (mounted && prevEtag) {
      headers["If-None-Match"] = prevEtag;
    }

    let result = null;
    // The picker names the representation actually drawn, including its source
    // binding and reduction metadata when the payload records them.
    let surface = "step";
    let componentBodies = null;
    const meshed = await fetchMeshes(file, headers, { mounted, signal, onPart: (node, meshes, head) => {
      if (!current()) return;
      if (location.component && !componentBodies) componentBodies = componentViewBodies(location,
        head.meshes.flatMap(part => part.entries?.map(entry => entry.name) || [part.name]));
      mountScenePart(node, meshes, head, file, location, {current,preserveCamera,componentBodies});
      if (loadingEl && state.currentGroup?.userData.sharedFile === file) loadingEl.style.display = 'none';
    }});
    if (!current()) return;

    if (meshed?.unchanged) { landed = true; return; }
    if (meshed) {
      if (meshed.etag) state.stepEtags.set(file, meshed.etag);
      if (meshed.url) rememberMember(`${location.file}.mesh`, meshed.url);
      result = meshed.result;
      surface = "mesh";
    } else {
      const url = memberUrl(location.file);
      let text = null;
      if (url) {
        if (mounted && memberLoaded(location.file, url)) { landed = true; return; }
        try {
          text = await fetchMember(url, { signal });
          rememberMember(location.file, url);
        } catch { /* the site's route has the same member */ }
      }
      if (!text) {
        const resp = await fetch(`/steps/${file}`, { headers, signal });
        if (resp.status === 304) { landed = true; return; }
        if (!resp.ok) { failed(`Couldn't load ${file} — ${resp.status}`); return; }
        const etag = resp.headers.get("etag");
        if (etag) state.stepEtags.set(file, etag);
        text = new Uint8Array(await resp.arrayBuffer());
      }
      result = await parseStep(text);
    }

    if (!current()) return;

    if (result.scene) {
      await new Promise(requestAnimationFrame);
      if (!current()) return;
      if (state.currentGroup?.userData.sharedFile !== file) {failed('No parts could be loaded');return;}
      state.currentGroup.userData.failedParts = result.errors;
      state.currentGroup.userData.sceneLoading = false;
      if (result.errors.length) console.warn('Parts retain their last available geometry:',result.errors);
      if (!preserveCamera) resetCamera(state.currentGroup);
      const style=faucetStyleFor(file);
      if (style) {state.faucetStyle=style.id;window.dispatchEvent(new CustomEvent(HSM_EVENTS.FAUCET_OPTIONS));}
      if (location.component) window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED,{detail:{file,name:location.component}}));
      window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_MOUNTED,{detail:{file,revision:result.src,complete:true}}));
      landed = true;
      return;
    }

    if (location.component) {
      const bodies = componentViewBodies(location, result.meshes.map(mesh => mesh.name));
      result = { ...result, meshes: result.meshes.filter(mesh => bodies.some(body => matchesBody(mesh.name, body))) };
      if (!result.meshes.length) { failed(`Component ${location.component} is not in this model`); return; }
    }

    if (state.currentGroup) {
      scene.remove(state.currentGroup);
      disposeCadGroup(state.currentGroup);
    }

    state.currentGroup = buildMesh(result, file);
    applyXray(state.currentGroup); // ghost + edges if x-ray mode is on
    setActiveEdges(result); // face-range edges for the picker, lazily reconstructed from triangles
    clearPickFind(); // stale find highlights reference the old geometry
    dropHighlight(); // and the selection's overlay and fade; its owner draws it again on STEP_MOUNTED
    clearComponentPicker();      // drop a stale component selection/hover overlay
    scene.add(state.currentGroup);
    state.mountedDetail = {
      type: "step", file, sourceFile: location.file, surface,
      src: (result && result.src) || null,
      cut: (result && result.cut) || null,
    };
    nameSurface(location.file, surface);
    loadHiddenForFile(file);     // restore this file's locally-hidden components…
    applyHiddenComponents();     // …and take them out of the freshly-built view
    onStepReloaded();            // re-seat the component editor's selection on the fresh meshes
    if (!preserveCamera) resetCamera(state.currentGroup);
    const style = faucetStyleFor(file);
    if (style) state.faucetStyle = style.id;
    window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_MOUNTED, { detail: { file } }));
    if (location.component) window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED, { detail: { file, name: location.component } }));
    if (style) window.dispatchEvent(new CustomEvent(HSM_EVENTS.FAUCET_OPTIONS));
    landed = true;
  } catch (err) {
    if (err.name !== "AbortError") {
      failed(`Couldn't read ${file}`);
      console.warn("loadStepFile:", err);
    }
  } finally {
    if (loadingEl && landed && current()) loadingEl.style.display = "none";
    load.finish();
  }
}

// --- Thumbnail rendering ---
// SIZED BY THE CALLER, because a picture drawn smaller than it is shown is a
// picture nobody wants: the /3d cards take half the page each and a dense display
// doubles that again (`thumbSize` in grid.js). This is the square it starts at,
// and what a caller naming no size gets.
const THUMB_SIZE = 400;

// Frame a group front-iso in the offscreen scene, snap it, and tear it down.
// Shared with glb.js so every 3D thumbnail is composed the same way.
function snapThumbnail(group, px = THUMB_SIZE, presentation = "viewer") {
  const { renderer: thumbRenderer, scene: thumbScene, camera: thumbCam } = getThumbnailRuntime();
  // The drawing buffer only, so the canvas keeps no style of its own — nothing
  // puts this element on a page.
  if (thumbRenderer.domElement.width !== px || thumbRenderer.domElement.height !== px) {
    thumbRenderer.setSize(px, px, false);
  }
  const shelf = presentation === "shelf";
  const background = shelf ? 0xe6ecf5 : BG_COLOR;
  thumbRenderer.setClearColor(background);
  thumbScene.fog.color.set(background);
  thumbScene.add(group);

  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = maxDim * (shelf ? 2.25 : 2.5);
  // +Z-up CAD-standard front-iso — matches resetCamera in scene.js so
  // the thumbnail shows the same orientation as the detail view's
  // default. Camera at +X, -Y, +Z (front-right-above).
  const el = Math.atan(1 / Math.sqrt(2));
  const az = -Math.PI / 4;
  thumbCam.up.set(0, 0, 1);
  thumbCam.position.set(
    center.x + dist * Math.cos(el) * Math.cos(az),
    center.y + dist * Math.cos(el) * Math.sin(az),
    center.z + dist * Math.sin(el)
  );
  thumbCam.lookAt(center);
  fitCameraDepth(thumbCam, center, size.length() / 2);
  fitFog(thumbScene, dist, size.length() / 2);
  syncEdgeResolution(thumbRenderer);

  thumbRenderer.render(thumbScene, thumbCam);
  const dataURL = thumbRenderer.domElement.toDataURL();

  return dataURL;
}

// Build, shade and capture the shared meshes contract. Both thumbnail sources end here,
// so where the meshes came from can't change how the part looks.
export function renderMeshes(result, px, file = null, finishId = state.faucetFinish, presentation = "viewer") {
  const group = buildMesh(result, file, finishId);
  try {
    applyXray(group);
    return snapThumbnail(group, px, presentation);
  } finally {
    group.removeFromParent();
    disposeCadGroup(group);
  }
}

// Thumbnails use the detail view's native surface/scene loader and the same STEP
// fallback. They therefore draw the representation that the detail view can open.
// Every picture of one model, whatever size it was asked at — what a live reload
// drops so the next card redraws from the model that just changed.
export function forgetThumbnail(file) {
  for (const key of state.thumbnailCache.keys()) {
    if (key.startsWith(`${file}@`)) state.thumbnailCache.delete(key);
  }
}

export async function renderThumbnail(file, px = THUMB_SIZE, finishId = state.faucetFinish, presentation = "viewer") {
  // THE SIZE IS PART OF WHAT IS CACHED. A card asks at its own width, and the
  // same model shown at two widths is two pictures; keying on the file alone
  // would hand the second one the first one's pixels.
  const key = `${file}@${px}@${presentation}${hasFaucetFinish(file) ? `@${finishId}` : ""}`;
  if (state.thumbnailCache.has(key)) return state.thumbnailCache.get(key);
  await loadFinishes();

  try {
    const meshed = await fetchMeshes(file, {});
    if (meshed && meshed.result) {
      const fromPayload = renderMeshes(meshed.result, px, file, finishId, presentation);
      state.thumbnailCache.set(key, fromPayload);
      return fromPayload;
    }
    const resp = await fetch(`/steps/${file}`);
    if (!resp.ok) return null;
    const buf = new Uint8Array(await resp.arrayBuffer());
    const dataURL = renderMeshes(await parseStep(buf), px, file, finishId, presentation);
    state.thumbnailCache.set(key, dataURL);
    return dataURL;
  } catch {
    return null;
  }
}
