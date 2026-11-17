// Reflect published changes in the open model while preserving the camera.

import { state } from "./state.js";
import { getLoader } from "./loaders.js";
import { forgetThumbnail } from "./step.js";
import { fetchFiles } from "./main.js";
import { mountScorecard } from "./scorecard-3d.js";
import { mountMissing } from "./missing-parts.js";
import { afterGesture } from "./scene.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { stepLocation } from "/contracts/step-locations.js";

// Keep one update in flight and one request to read again after it. A save
// during a fetch must reach the next read without starting another full model.
function latestUpdate(pending, key, update) {
  const previous = pending.get(key);
  if (previous) { previous.again = true; return previous.run; }
  const entry = { again: false, run: null };
  pending.set(key, entry);
  entry.run = (async () => {
    try {
      do {
        entry.again = false;
        await update();
      } while (entry.again);
    } finally {
      pending.delete(key);
    }
  })();
  return entry.run;
}

function isOpenAs(type, file) {
  return state.currentDetail && state.currentDetail.type === type && state.currentDetail.file === file;
}

// The open view a STEP draws: the whole model, or one of its components.
function openStepOf(file) {
  const open = state.currentDetail;
  return open?.type === "step" && stepLocation(open.file).file === file ? open.file : null;
}

// One deferred reload per open file, held through the gesture and complete load.
const pendingCadReloads = new Map();

// Re-load a CAD part into the open modal, in place, camera preserved. Resolves
// the loader through getLoader so a code edit / deploy is reflected — the fresh
// leaf talks to the same live scene + state, so nothing is torn down. Waits out
// any gesture in flight (the gate in scene.js).
async function reloadCad(type, file) {
  const key = `${type}:${file}`;
  return latestUpdate(pendingCadReloads, key, async () => {
    await afterGesture();
    // The modal may have closed, or swapped files, while the gesture ran on.
    if (!isOpenAs(type, file)) return;
    const wrapper = state.currentCadWrapper;
    const load = await getLoader(type);
    if (!isOpenAs(type, file) || wrapper !== state.currentCadWrapper) return;
    await load(file, { preserveCamera: true });
    if (type === "step" && isOpenAs(type, file) && wrapper === state.currentCadWrapper && wrapper) {
      mountScorecard(wrapper, file);
      mountMissing(wrapper, file);
    }
  });
}

window.addEventListener(HSM_EVENTS.FILES_CHANGED, async (e) => {
  const files = e.detail?.files || [];
  if (files.some(file => /\.(step|dxf|glb|pdf)$/.test(file))) {
    // Resolve the current content addresses before reloading the open model.
    try { await fetchFiles(); }
    catch {
      for (const file of files) {
        state.memberUrls.delete(file);
        state.memberUrls.delete(`${file}.mesh`);
      }
    }
  }
  for (const file of files) {
    if (file.endsWith(".step")) {
      forgetThumbnail(file);
      // Reload the model in place, then re-mount the scorecard bar so a live rebuild's fresh
      // verdict (the sidecar is rewritten alongside the .step) replaces the stale one.
      const open = openStepOf(file);
      if (open) {
        // A deferred reload can outlive the modal; mountScorecard reads the
        // wrapper's isConnected.
        reloadCad("step", open);
      }
    } else if (file.endsWith(".dxf")) {
      if (isOpenAs("dxf", file)) reloadCad("dxf", file);
    } else if (file.endsWith(".glb")) {
      if (isOpenAs("glb", file)) reloadCad("glb", file);
    }
  }
});

// Claim the deploy refresh: boot.js reloads pages that don't set this,
// but the viewer refreshes in place so the open modal + camera survive.
window.__hsmDeploySoft = true;

function reloadOpenDetail() {
  const d = state.currentDetail;
  if (!d) return;
  if (d.type === "step" || d.type === "dxf" || d.type === "glb") reloadCad(d.type, d.file);
}

// Force the open detail to fully re-render on the next reloadOpenDetail rather
// than short-circuit on unchanged content — used when the render CODE moved even
// though the artifact bytes didn't (a deploy or a dev code edit). Each kind gates
// CAD loaders use ETags to skip unchanged content. Clearing them reloads the
// open model through the deployed loader.
function forceDetailRerender() {
  state.stepEtags.clear();
  state.dxfEtags.clear();
  state.glbEtags.clear();
  state.memberLoaded.clear();
}

window.addEventListener(HSM_EVENTS.DEPLOY, async (e) => {
  // commitChanged === false means a same-commit reconnect blip (nothing
  // actually shipped): just re-list to catch any add/remove, cheaply.
  // Anything else is a real new build — wipe the caches so every
  // thumbnail and the open modal re-render against the new bytes.
  const newBuild = !e.detail || e.detail.commitChanged !== false;
  if (newBuild) {
    // Adopt the new build's commit as the code-bust token so the open modal and
    // any subsequent open re-import the leaf loaders as the new deploy's code,
    // not the code this tab loaded at boot.
    if (e.detail && e.detail.commit) state.codeVersion = String(e.detail.commit);
    state.thumbnailCache.clear();
    // New build may carry new render code too, so force a full re-render (this
    // drops the ETags the pre-code-version deploy path already cleared).
    forceDetailRerender();
  }
  // AWAITED, BECAUSE THE RE-RENDER BELOW READS WHAT THIS FETCHES. `fetchFiles` re-reads
  // `/api/objects`, which is where the moved pointer file's hashes arrive. The URLs this tab
  // loaded with go on answering — an object is named by its own bytes and is never rewritten —
  // so a re-render ahead of the list rebuilds the open model from the previous cut.
  await fetchFiles();
  if (newBuild) reloadOpenDetail();
});
