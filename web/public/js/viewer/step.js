// STEP-format module. Owns the occt-import-js loader (no importmap
// support, so injected manually as a classic <script>), the STEP parser,
// the mesh builder that turns occt output into a Three.js Group, the
// network + parse + scene-mount loader, and the offscreen thumbnail
// renderer (with a per-file dataURL cache via state).

import * as THREE from "three";
import { state } from "./state.js";
import { scene, camera, resetCamera, addStudioLighting, fitCameraDepth, fitFog,
         BG_COLOR, TONE_EXPOSURE } from "./scene.js";
import { applyXray, syncEdgeResolution } from "./xray.js";
import { setActiveEdges } from "./edge-picker.js";
import { clearPickFind } from "./pick-find.js";
import { clearHighlight } from "./part-highlight.js";
import { clearComponentPicker, loadHiddenForFile, applyHiddenComponents } from "./component-picker.js";
import { onStepReloaded } from "./component-edit.js";

// --- occt-import-js loader (no importmap support, loaded manually) ---
let occtReady;
export const occtPromise = new Promise((resolve) => { occtReady = resolve; });
const occtScript = document.createElement("script");
occtScript.src = "https://cdn.jsdelivr.net/npm/occt-import-js@0.0.23/dist/occt-import-js.js";
occtScript.onload = () => {
  window.occtimportjs().then((occt) => occtReady(occt));
};
document.head.appendChild(occtScript);

// --- STEP parsing ---
async function parseStep(buffer) {
  const occt = await occtPromise;
  const result = occt.ReadStepFile(buffer, null);
  backfillMeshNames(result);
  return result;
}

// The same `{ meshes: [...] }` occt hands back, decoded from the tessellation the
// export wrote beside the STEP. The viewer answers off a model's payload when it
// has one; a model without one is read from its STEP.
//
// Layout: u32 header length, that many bytes of JSON, then one blob every
// array indexes into by [byteOffset, length] — positions and normals f32,
// indices and face ranges u32. See hardware/scripts/_mesh_payload.py, which
// writes it.
//
// `fac` is `brep_faces` packed flat: [first, last, ...] inclusive TRIANGLE
// indices, one pair per BREP face, restored to the shape occt reports it in.
// edge-picker.js reconstructs every pickable edge from that grouping.
//
// A payload whose version isn't one of MESH_PAYLOAD_VERSIONS decodes to null,
// and the caller reads the STEP. The set is every version whose arrays this
// decoder can take, and it is WIDER than the one the writer stamps: 2 and 3 lay
// their triangles out identically, 3 only adding `src` for the writer's own
// staleness check. Turning 2 away would cost the surface — three payloads are in
// no build step's outs, so a deploy carries whatever the tree had, and falling
// back to the STEP for those serves the flute-less solid.
const MESH_PAYLOAD_VERSIONS = [2, 3]; // keep in sync with DECODABLE in _mesh_payload.py

export function decodeMeshPayload(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const headLen = view.getUint32(0, true);
  const head = JSON.parse(new TextDecoder().decode(bytes.subarray(4, 4 + headLen)));
  if (!MESH_PAYLOAD_VERSIONS.includes(head.v)) return null;
  const blob = bytes.buffer.slice(bytes.byteOffset + 4 + headLen, bytes.byteOffset + bytes.byteLength);
  const meshes = head.meshes.map((m) => {
    const fac = new Uint32Array(blob, m.fac[0], m.fac[1]);
    const brep_faces = [];
    for (let i = 0; i + 1 < fac.length; i += 2) brep_faces.push({ first: fac[i], last: fac[i + 1] });
    return {
      name: m.name,
      color: m.color || undefined,
      attributes: {
        position: { array: new Float32Array(blob, m.pos[0], m.pos[1]) },
        normal: { array: new Float32Array(blob, m.nrm[0], m.nrm[1]) },
      },
      index: { array: new Uint32Array(blob, m.idx[0], m.idx[1]) },
      brep_faces,
    };
  });
  return { meshes };
}

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

// Default gray for parts that carry no color (single-solid STEPs from
// export_step). Assemblies from export_assembly carry a per-solid color that
// occt-import-js surfaces as mesh.color ([r, g, b], 0..1).
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

// Materials are shared across meshes (and across loads) by color, so an
// assembly with N same-colored solids makes one material, not N.
//
// THE KEY IS THE COLOUR ITSELF, not a rounding of it. occt hands each solid a
// float triple and the material is built from those floats, so a key that
// quantised them to a byte let two colours a byte apart share one material —
// and the one they shared carried whichever arrived first. Within a model that
// is a solid drawn in its neighbour's shade; across loads, which is what this
// cache is for, it is one model's colour turning up in the next model's
// picture. Near black the sRGB curve is steep enough that a byte of linear
// carries a couple of display steps: `1a1a1c` and `1c1c1f` are two such colours,
// and the faucet took the manifold's when they were drawn in that order.
const _matCache = new Map();

function materialFor(color) {
  const key = color ? color.join(",") : "default";
  let mat = _matCache.get(key);
  if (!mat) {
    // Surfaces sit a depth-unit back, so the feature edges xray.js draws on
    // these same triangles resolve in front of them.
    mat = new THREE.MeshStandardMaterial({
      color: color ? new THREE.Color(color[0], color[1], color[2]) : new THREE.Color(DEFAULT_FRONT),
      metalness: 0.1, roughness: 0.6,
      side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    });
    mat.onBeforeCompile = darkenBackFaces;
    mat.customProgramCacheKey = () => "hsm-back-darken";
    _matCache.set(key, mat);
  }
  return mat;
}

// Drop the shared materials, so the next mount builds its own.
//
// WHICH SOLID IS DRAWN OVER WHICH IS SET BY THE ORDER THESE WERE MADE IN.
// three.js sorts an opaque draw by `material.id` before it looks at depth, and
// ids are handed out in creation order — so on a page that has already mounted
// another model, this model's solids are drawn in an order it did not choose,
// and two faces sharing a plane swap which one survives. It is invisible while a
// person clicks from part to part and it is not invisible in a PNG: the faucet
// assembly, drawn after the packed machine on one page, differed from its own
// fresh render on 2.5% of its pixels by as much as 92 counts.
//
// tools/render/render-step-posed.js draws many pictures on one page and calls
// this between them, so each one is the picture a fresh page would draw.
export function forgetMaterials() {
  _matCache.clear();
}

// A body of several disjoint solids — the cold core, a reference sub-assembly, a
// valve's coil — is written to STEP as one component per solid, named
// `<body>/<n>` (_per_solid_color in hardware/scripts/_cadq_export.py). The body
// is what everything downstream names: a scorecard row, a highlight, the
// `solid:` line a pick copies out. Both routes into buildMesh carry the index —
// the wasm parse reads it off the component's label, the handed-over payload
// states the same name — so it comes off here, once, for both. A body naming no
// solid of its own passes through.
const bodyName = (name) => (name || "").replace(/\/\d+$/, "");

function buildMesh(result) {
  const group = new THREE.Group();

  result.meshes.forEach((mesh, occtIndex) => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.position.array), 3));
    if (mesh.attributes.normal) {
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.normal.array), 3));
    }
    if (mesh.index) {
      geo.setIndex(new THREE.BufferAttribute(new Uint32Array(mesh.index.array), 1));
    }
    geo.computeBoundingBox();

    // One double-sided draw per solid, so a thin part still reads from behind.
    // occt-import-js hands us mesh.color per solid when the STEP carries one;
    // else gray. The occt mesh index rides along so the edge picker's face
    // raycast can map a hit triangle back to its BREP face.
    const solid = new THREE.Mesh(geo, materialFor(mesh.color));
    solid.userData.occtIndex = occtIndex;
    solid.userData.side = "front"; // the name the face raycast selects on
    // Carry the component name (backfilled from the STEP assembly node) onto the mesh so
    // the scorecard's clickable rows can find a solid by name (part-highlight.js).
    solid.name = bodyName(mesh.name);
    group.add(solid);
  });

  return group;
}

// The triangles the model was exported from, written beside the STEP as `<file>.mesh` by
// hardware/scripts/_cadq_export.py. The same meshes[] the wasm parse returns — everything
// downstream is untouched, edges included: the picker reconstructs those off the triangles
// rather than off the BREP.
//
// A MODEL WITH ONE ANSWERS OFF IT AND NEVER FETCHES THE STEP. The text is only ever read to
// be parsed into these, and the parse is the whole cost of opening an assembly — several
// seconds against a fraction of one, over twenty megabytes the page then throws away. A model
// without one reads the STEP and shows the same thing.
async function fetchMeshes(file, headers) {
  try {
    const resp = await fetch(`/meshes/${file}.mesh`, { headers });
    if (resp.status === 304) return { unchanged: true };
    if (!resp.ok) return null;
    const result = decodeMeshPayload(new Uint8Array(await resp.arrayBuffer()));
    if (!result) return null; // a payload this code doesn't read is no payload
    return { etag: resp.headers.get("etag"), result };
  } catch {
    return null;
  }
}

export async function loadStepFile(file, { preserveCamera = false } = {}) {
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
  const failed = (msg) => { if (pill) pill.textContent = msg; };

  try {
    // If we're refetching the same file that's already in the scene, send
    // If-None-Match so the server can answer 304 when bytes are unchanged
    // (avoids the visible re-render flash on a deploy that didn't touch
    // this file). The tessellation is rewritten whenever the STEP is, so it
    // carries that revalidation as faithfully as the STEP does.
    const headers = {};
    const prevEtag = state.stepEtags.get(file);
    if (state.mountedDetail?.type === "step" && state.mountedDetail.file === file && prevEtag) {
      headers["If-None-Match"] = prevEtag;
    }

    let result = null;
    // WHICH OF THE TWO SURFACES THIS MODEL IS. They are not always the same one: under
    // `pack.BUNDLED_PAYLOAD_DIRS` the payload carries flutes the solid does not, so a reader
    // told only the STEP's name is told the wrong file. The edge picker states this.
    let surface = "step";
    const meshed = await fetchMeshes(file, headers);
    if (meshed?.unchanged) { landed = true; return; }
    if (meshed) {
      if (meshed.etag) state.stepEtags.set(file, meshed.etag);
      result = meshed.result;
      surface = "mesh";
    } else {
      const resp = await fetch(`/steps/${file}`, { headers });
      if (resp.status === 304) { landed = true; return; }
      if (!resp.ok) { failed(`Couldn't load ${file} — ${resp.status}`); return; }
      const etag = resp.headers.get("etag");
      if (etag) state.stepEtags.set(file, etag);
      result = await parseStep(new Uint8Array(await resp.arrayBuffer()));
    }

    if (state.currentGroup) {
      scene.remove(state.currentGroup);
      state.currentGroup.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
    }

    state.currentGroup = buildMesh(result);
    applyXray(state.currentGroup); // ghost + edges if x-ray mode is on
    setActiveEdges(result); // BREP edges for the edge picker (lazy-reconstructed)
    clearPickFind(); // stale find highlights reference the old geometry
    clearHighlight(); // and a stale scorecard part-highlight does too
    clearComponentPicker();      // drop a stale component selection/hover overlay
    scene.add(state.currentGroup);
    state.mountedDetail = { type: "step", file, surface };
    loadHiddenForFile(file);     // restore this file's locally-hidden components…
    applyHiddenComponents();     // …and take them out of the freshly-built view
    onStepReloaded();            // re-seat the component editor's selection on the fresh meshes
    if (!preserveCamera) resetCamera(state.currentGroup);
    landed = true;
  } catch (err) {
    failed(`Couldn't read ${file}`);
    console.warn("loadStepFile:", err);
  } finally {
    if (loadingEl && landed) loadingEl.style.display = "none";
  }
}

// --- Thumbnail rendering ---
// SIZED BY THE CALLER, because a picture drawn smaller than it is shown is a
// picture nobody wants: the /3d cards take half the page each and a dense display
// doubles that again (`thumbSize` in grid.js). This is the square it starts at,
// and what a caller naming no size gets.
const THUMB_SIZE = 400;
const thumbRenderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
thumbRenderer.setSize(THUMB_SIZE, THUMB_SIZE);
thumbRenderer.setPixelRatio(1);
thumbRenderer.setClearColor(BG_COLOR);
thumbRenderer.toneMapping = THREE.ACESFilmicToneMapping;
thumbRenderer.toneMappingExposure = TONE_EXPOSURE;
const thumbScene = new THREE.Scene();
const thumbCam = new THREE.PerspectiveCamera(45, 1, 1, 1000);
addStudioLighting(thumbScene);

// Frame a group front-iso in the offscreen scene, snap it, and tear it down.
// Shared with glb.js so every 3D thumbnail is composed the same way.
export function snapThumbnail(group, px = THUMB_SIZE) {
  // The drawing buffer only, so the canvas keeps no style of its own — nothing
  // puts this element on a page.
  if (thumbRenderer.domElement.width !== px) thumbRenderer.setSize(px, px, false);
  thumbScene.add(group);

  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = maxDim * 2.5;
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

  thumbScene.remove(group);
  group.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
  return dataURL;
}

// Build + shade + snap an occt-shaped result. Both thumbnail sources end here,
// so where the meshes came from can't change how the part looks.
export function renderMeshes(result, px) {
  const group = buildMesh(result);
  applyXray(group); // match the detail view's x-ray mode in the thumbnail
  return snapThumbnail(group, px);
}

// THE THUMBNAIL DRAWS WHAT THE DETAIL VIEW DRAWS. `loadStepFile` answers off the payload beside
// a STEP and only parses the solid when there is none, so a thumbnail that went straight to the
// solid would be a picture of a different model wherever the two carry different surfaces — the
// enclosure's pieces, whose flutes are in the payload and not in the B-rep
// (hardware/scripts/flute_payload.py). Where no payload stands, both read the STEP and this is
// the same fetch it always was.
// Every picture of one model, whatever size it was asked at — what a live reload
// drops so the next card redraws from the model that just changed.
export function forgetThumbnail(file) {
  for (const key of state.thumbnailCache.keys()) {
    if (key.slice(0, key.lastIndexOf("@")) === file) state.thumbnailCache.delete(key);
  }
}

export async function renderThumbnail(file, px = THUMB_SIZE) {
  // THE SIZE IS PART OF WHAT IS CACHED. A card asks at its own width, and the
  // same model shown at two widths is two pictures; keying on the file alone
  // would hand the second one the first one's pixels.
  const key = `${file}@${px}`;
  if (state.thumbnailCache.has(key)) return state.thumbnailCache.get(key);

  try {
    const meshed = await fetchMeshes(file, {});
    if (meshed && meshed.result) {
      const fromPayload = renderMeshes(meshed.result, px);
      state.thumbnailCache.set(key, fromPayload);
      return fromPayload;
    }
    const resp = await fetch(`/steps/${file}`);
    if (!resp.ok) return null;
    const buf = new Uint8Array(await resp.arrayBuffer());
    const dataURL = renderMeshes(await parseStep(buf), px);
    state.thumbnailCache.set(key, dataURL);
    return dataURL;
  } catch {
    return null;
  }
}

// thumbScene is also reused by dxf.js's renderDxfThumbnail — same offscreen
// renderer, just a different group producer. Re-exported so dxf.js doesn't
// need its own duplicate setup.
export { thumbRenderer, thumbScene, thumbCam };
