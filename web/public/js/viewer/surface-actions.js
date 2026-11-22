// Surface commands use the point the user picked on the mounted model.
import * as THREE from "three";
import { state } from "./state.js";
import { classifyPickedSurface, surfacePlacement } from "./picked-face.js";

let faceOn = null, section = null, request = 0;

export function surfacePick(hit, face = undefined, faceId = null) {
  const { object, point, faceIndex, instanceId } = hit;
  const placement = surfacePlacement(object, instanceId);
  const normal = hit.face?.normal.clone().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(placement));
  return {
    object, point, faceIndex, faceId, instanceId, normal, kind: "face", ownerName: object.name,
    face: face === undefined ? classifyPickedSurface(hit) : face,
  };
}

export function refreshSection() { section?.refresh(); }
export function closeSection() { return section?.close() || false; }

export function clearSurfaceViews() {
  request++;
  section?.dispose();
  faceOn?.dispose();
  section = faceOn = null;
}

// Load inspection tools on demand. A dismissed model cannot receive a late command.
async function start(tool, pick) {
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
    module = await (tool === "section" ? import("./section-view.js") : import("./face-on.js"));
  } finally { pending.abort(); }
  if (ticket !== request || wrapper !== state.currentCadWrapper || group !== state.currentGroup ||
      !wrapper?.isConnected || pick.object?.parent !== group || !pick.object.visible) return;
  if (tool === "section") {
    section ??= module.createSectionView({ wrapper });
    if (section.canUse(pick)) section.start(pick);
  } else {
    faceOn ??= module.createFaceOn({ wrapper });
    if (faceOn.canUse(pick)) faceOn.start(pick);
  }
}

export function addSurfaceActions(container) {
  let pick = null;
  const button = (tool, label) => {
    const el = document.createElement("button");
    el.className = "component-command";
    el.dataset.surfaceAction = tool;
    el.type = "button";
    el.textContent = label;
    el.hidden = true;
    el.addEventListener("click", async () => {
      if (!pick) return;
      try { await start(tool, pick); }
      catch (error) {
        el.textContent = `Retry ${label}`;
        console.warn(label, error);
      }
    });
    container.appendChild(el);
    return el;
  };
  const slice = button("section", "Section here"), face = button("face-on", "Face on");
  return next => {
    pick = next?.object?.parent === state.currentGroup && next?.object?.visible ? next : null;
    slice.hidden = !pick;
    face.hidden = pick?.face?.kind !== "plane";
    slice.textContent = "Section here";
    face.textContent = "Face on";
  };
}
