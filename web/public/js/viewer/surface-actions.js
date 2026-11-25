// Surface tools use the mounted model and preserve a picked point when one is available.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { state } from "./state.js";
import { classifyPickedSurface, surfacePlacement } from "./picked-face.js";
import { makeToolButton } from "./tool-rail.js";

let faceOn = null, section = null, pendingSection = null, request = 0;
const surfacePicks = new WeakMap();

export function surfacePick(hit, face = undefined, faceId = null) {
  const { object, point, faceIndex, instanceId } = hit;
  const placement = surfacePlacement(object, instanceId);
  const normal = hit.face?.normal.clone().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(placement));
  return {
    object, point, faceIndex, faceId, instanceId, normal, kind: "face", ownerName: object.name,
    face: face === undefined ? classifyPickedSurface(hit) : face,
  };
}

function sectionReady() {
  return state.currentGroup?.children.some(mesh => mesh.isMesh && mesh.visible && mesh.userData.side === "front");
}

function syncSectionToggle() {
  const toggle = state.currentCadWrapper?.querySelector(".section-tool-toggle");
  if (toggle) toggle.disabled = !sectionReady();
}
window.addEventListener(HSM_EVENTS.STEP_MOUNTED, syncSectionToggle);

export function refreshSection() {
  syncSectionToggle();
  section?.refresh();
}

export function closeSection() {
  if (pendingSection) {
    const { toggle } = pendingSection;
    pendingSection = null;
    toggle.removeAttribute("aria-busy");
    const focus = toggle.closest(".tool-drawer.compact:not([open])")?.querySelector("summary") || toggle;
    if (focus.getClientRects().length) focus.focus({ preventScroll: true });
    return true;
  }
  return section?.close() || false;
}

export function clearSurfaceViews() {
  request++;
  pendingSection?.toggle.removeAttribute("aria-busy");
  pendingSection = null;
  section?.close(false);
  faceOn?.dispose();
  section = faceOn = null;
}

function currentPick(pick) {
  return pick?.object?.parent === state.currentGroup && pick?.object?.visible ? pick : null;
}

export function makeSectionToggle(wrapper) {
  const toggle = makeToolButton({
    className: "section-tool-toggle",
    label: "Section",
    icon: "section",
    title: "Position a section plane and preview the cut",
    onClick: async () => {
      if (closeSection() || !sectionReady()) return;
      const root = state.currentGroup;
      const control = Array.from(wrapper.querySelectorAll('[data-surface-action="face-on"]')).find(button =>
        button.closest(":is(.component-panel,.edge-panel).show")?.getClientRects().length &&
        currentPick(surfacePicks.get(button)));
      const pick = control && surfacePicks.get(control);
      const opening = { toggle };
      pendingSection = opening;
      toggle.setAttribute("aria-busy", "true");
      try {
        const { startSectionPreview } = await import("./section-view.js");
        if (pendingSection === opening && state.currentCadWrapper === wrapper && state.currentGroup === root &&
            wrapper.isConnected && sectionReady()) {
          section = startSectionPreview({ wrapper, toggle, pick: currentPick(pick) });
        }
      } catch (error) {
        console.warn("Section", error);
      } finally {
        if (pendingSection === opening) {
          pendingSection = null;
          toggle.removeAttribute("aria-busy");
        }
      }
    },
  });
  toggle.disabled = true;
  toggle.setAttribute("aria-expanded", "false");
  return toggle;
}

// Load Face on only on demand. A dismissed model cannot receive a late command.
async function startFaceOn(pick) {
  const ticket = ++request;
  const wrapper = state.currentCadWrapper;
  const group = state.currentGroup;
  const pending = new AbortController();
  const supersede = () => { if (request === ticket) request++; };
  for (const type of ["pointerdown", "wheel", "keydown"]) {
    document.addEventListener(type, supersede, { capture: true, passive: true, signal: pending.signal });
  }
  let module;
  try {
    module = await import("./face-on.js");
  } finally { pending.abort(); }
  if (ticket !== request || wrapper !== state.currentCadWrapper || group !== state.currentGroup ||
      !wrapper?.isConnected || !currentPick(pick)) return;
  faceOn ??= module.createFaceOn({ wrapper });
  if (faceOn.canUse(pick)) faceOn.start(pick);
}

export function addSurfaceActions(container) {
  const face = document.createElement("button");
  face.className = "component-command";
  face.dataset.surfaceAction = "face-on";
  face.type = "button";
  face.textContent = "Face on";
  face.hidden = true;
  face.addEventListener("click", async () => {
    const pick = currentPick(surfacePicks.get(face));
    if (!pick) return;
    try { await startFaceOn(pick); }
    catch (error) {
      face.textContent = "Retry Face on";
      console.warn("Face on", error);
    }
  });
  container.appendChild(face);
  return next => {
    const pick = currentPick(next);
    surfacePicks.set(face, pick);
    face.hidden = pick?.face?.kind !== "plane";
    face.textContent = "Face on";
  };
}
