// Version-aware resolver for the CAD-kind detail loaders (step / dxf / glb) —
// the code that loads a part into the shared Three.js scene. Every place that
// puts a part in the modal (the open path in cad-detail.js, the live-refresh
// path in live.js) asks here for the loader instead of holding a frozen import
// binding, so a viewer-code edit is picked up in place — no page reload, so the
// live scene, camera, and open modal all survive.
//
// How a code edit is picked up without reloading the page: ES modules are cached
// by URL, so re-importing "./glb.js" returns the same frozen module. Re-importing
// "./glb.js?v=<token>" is a DIFFERENT URL — the browser fetches and evaluates the
// new source. state.codeVersion is that token: null at page load (the statically
// imported loaders below ARE the current code, nothing to re-fetch), set to the
// build commit on a prod deploy and to a change nonce on a dev viewer-source save
// (both in live.js). getLoader returns the fresh loader for the active version,
// so both opening a part and refreshing an open one run current code.
//
// Only the leaf renderer is re-imported. Its own `import { scene } from
// "./scene.js"` still resolves to the un-versioned URL, so the ONE live scene,
// renderer, camera, and the `state` singleton persist across the swap (that is
// why the camera and open modal survive, and why mixing a fresh leaf with the
// page's other modules is safe — all shared mutable state lives in state.js /
// scene.js, never in a leaf's module scope). A change to that shared infra
// (scene.js, state.js) therefore can NOT hot-swap and still needs a manual
// reload — an honest, rarely-hit boundary; the render code that actually gets
// iterated on (glb.js et al.) lives in the leaves.
//
// The set of hot-swappable leaves here is mirrored by the dev watcher in
// web/dev-server/server.js (which decides what edits broadcast CODE_CHANGED);
// keep the two in sync.

import { state } from "./state.js";
import { loadStepFile } from "./step.js";
import { loadDxfFile } from "./dxf.js";
import { loadGlbFile } from "./glb.js";

// The page-load loaders, used verbatim until a code version is active.
const STATIC = { step: loadStepFile, dxf: loadDxfFile, glb: loadGlbFile };
// Import specifiers, resolved relative to this module's URL (/js/viewer/).
const URLS = { step: "./step.js", dxf: "./dxf.js", glb: "./glb.js" };
// The loader export each leaf provides.
const EXPORTS = { step: "loadStepFile", dxf: "loadDxfFile", glb: "loadGlbFile" };

// (type@version) -> loader fn. One re-import per (type, build), reused across
// repeated opens/refreshes within the same build.
const cache = new Map();

// The current loader for a CAD kind: the page-load import when no code version
// is active, otherwise a version-busted re-import. Falls back to the static
// loader if a re-import fails (bad network / a half-deployed file) so a botched
// hot-reload never bricks the open path.
export async function getLoader(type) {
  const v = state.codeVersion;
  if (!v) return STATIC[type];
  const key = type + "@" + v;
  if (!cache.has(key)) {
    try {
      const mod = await import(`${URLS[type]}?v=${encodeURIComponent(v)}`);
      cache.set(key, mod[EXPORTS[type]]);
    } catch {
      return STATIC[type];
    }
  }
  return cache.get(key);
}
