// Hot-reload-aware entry points for the self-contained detail modules
// (mermaid / drawing / pcb) — the PanZoom-path kinds that each own their whole
// open / close / refetch flow. This is the non-CAD counterpart of loaders.js:
// the CAD kinds (step / dxf / glb) share cad-detail.js and swap only a leaf
// loader, so getLoader resolves that leaf; these modules ARE their own shell, so
// the whole module is the unit that re-imports.
//
// route.js, grid.js, and live.js import the open + refetch entry points from
// here instead of the raw modules, so a viewer-code edit is picked up: each
// resolves the module under state.codeVersion (re-importing "./pcb.js?v=<token>"
// when a version is active) and forwards to its current function. All open-modal
// + pan/zoom/view state lives in the `state` singleton and per-file localStorage,
// so a freshly re-imported module operates on the live modal and restores the
// user's place — no page reload, same as the CAD family.
//
// Close is re-exported verbatim (not re-imported): teardown only reads shared
// state, so the page-load module's close is always correct, and keeping it a
// plain synchronous function preserves route.js's popstate close-then-open
// ordering. The next OPEN runs fresh code, so a shell edit is reflected then.
//
// The hot-swappable module set here is mirrored by the dev watcher in
// web/dev-server/server.js; keep the two in sync.

import { state } from "./state.js";
import * as mermaidMod from "./mermaid.js";
import * as drawingsMod from "./drawings.js";
import * as pcbMod from "./pcb.js";

const STATIC = { mmd: mermaidMod, drawing: drawingsMod, pcb: pcbMod };
const URLS = { mmd: "./mermaid.js", drawing: "./drawings.js", pcb: "./pcb.js" };

// (type@version) -> module namespace. One re-import per (type, build).
const cache = new Map();

// The current module namespace for a detail kind: the page-load import when no
// code version is active, otherwise a version-busted re-import. Falls back to
// the page-load module if a re-import fails, so a botched hot-reload never
// bricks opening a part.
async function moduleFor(type) {
  const v = state.codeVersion;
  if (!v) return STATIC[type];
  const key = type + "@" + v;
  if (!cache.has(key)) {
    try {
      cache.set(key, await import(`${URLS[type]}?v=${encodeURIComponent(v)}`));
    } catch {
      return STATIC[type];
    }
  }
  return cache.get(key);
}

// Open (card click / deep-link / popstate-open): resolve current code. These
// were always async (they await a content fetch before opening), so the extra
// resolve step doesn't change the call semantics route.js/grid.js already rely on.
export async function openMmdDetail(file, push = true)     { return (await moduleFor("mmd")).openMmdDetail(file, push); }
export async function openDrawingDetail(file, push = true) { return (await moduleFor("drawing")).openDrawingDetail(file, push); }
export async function openPcbDetail(file, push = true)     { return (await moduleFor("pcb")).openPcbDetail(file, push); }

// Refetch (open-modal live refresh): resolve current code so a code edit
// re-renders in place. live.js clears the content sentinels first on a code-only
// change (see forceDetailRerender) so these don't short-circuit on unchanged bytes.
export async function refetchOpenMmd(file)     { return (await moduleFor("mmd")).refetchOpenMmd(file); }
export async function refetchOpenDrawing(file) { return (await moduleFor("drawing")).refetchOpenDrawing(file); }
export async function refetchOpenPcb(file)     { return (await moduleFor("pcb")).refetchOpenPcb(file); }

// Close: page-load functions, synchronous, state-only teardown (see header).
export const closeMmdDetail = mermaidMod.closeMmdDetail;
export const closeDrawingDetail = drawingsMod.closeDrawingDetail;
export const closePcbDetail = pcbMod.closePcbDetail;
