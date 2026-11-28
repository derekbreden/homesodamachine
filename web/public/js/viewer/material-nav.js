import { state } from "./state.js";
import { materialIndex, modelForMaterial } from "/contracts/materials.js";
import { parseStepHash, walkDepth } from "./step-nav.js";
import { dismissViewerHistory } from "./viewer-history.js";
import { materialHash } from "/contracts/material-tabs.js";
export { materialHash } from "/contracts/material-tabs.js";

export async function openMaterial(id, pushHistory = true, options = {}) {
  const { instance = null } = options;
  // Links written with six-digit ids (`HSM-000546`) open the same material.
  id = id.replace(/^HSM-0*(\d+)$/, (_, n) => "HSM-" + n.padStart(4, "0"));
  const material = materialIndex(state.materialCatalog).get(id);
  if (!material) {
    const notice = document.createElement("p"); notice.className = "material-catalog-status";
    notice.textContent = `Material ${id} is not in the catalog.`;
    const host = state.gridEl ?? document.getElementById("parts-catalog");
    host?.querySelector(".material-route-error")?.remove();
    notice.classList.add("material-route-error"); notice.setAttribute("role", "alert");
    host?.prepend(notice); return;
  }
  const file = modelForMaterial(state.materialCatalog, id)?.file;
  if (file) {
    const target = instance ? { instance } : null;
    let moving = null;
    const originHash = location.hash.slice(1);
    const originID = originHash.startsWith("material:") ? decodeURIComponent(originHash.slice(9).split("?")[0]) : null;
    const originFile = originID && modelForMaterial(state.materialCatalog, originID)?.file;
    const enterPreview = instance && pushHistory && originFile && originFile !== file && state.mountedDetail?.file === file;
    if (state.currentCadWrapper && (pushHistory || state.mountedDetail?.file === file)) {
      const { drillTo, jumpToStep, enterStepPreview } = await import("./step-nav.js");
      if (enterPreview) {
        const parents = history.state?.materialPath;
        enterStepPreview(file, parents?.at(-1) === originFile ? parents : [originFile]);
      } else if (instance) moving = jumpToStep(file, { target, replace: false });
      else if (state.mountedDetail?.type === "step") await drillTo(file);
      else await jumpToStep(file);
      if (state.currentDetail?.file !== file) return;
    } else {
      const { openDetail } = await import("./cad-detail.js");
      openDetail(file, pushHistory, null, target);
    }
    const raw = location.hash.slice(1);
    const remembered = raw.startsWith("step:") ? parseStepHash(raw) : history.state?.materialPath;
    const materialPath = remembered?.at(-1) === file ? remembered : [file];
    history.replaceState({ materialPath }, "", "#" + materialHash(id, options));
    state.materialPanel?.setRoot(id);
    state.materialPanel?.applyRoute(options);
    await moving;
  } else {
    const depth = state.currentCadWrapper ? walkDepth() : 0;
    const { mountMaterialPanel } = await import("./material-panel.js");
    const workspace = document.createElement("div");
    workspace.className = "material-record-workspace";
    let actions;
    if (state.materialCatalog.fittedClearances?.records.some(fit => fit.host === id || fit.mate === id)) {
      const { mountWorkspaceHeader } = await import("./cad-detail.js");
      workspace.classList.add("cad-record-views");
      actions = mountWorkspaceHeader(workspace);
      const stage = document.createElement("div"); stage.className = "material-record-stage"; workspace.append(stage);
    }
    const materialPanel = mountMaterialPanel(workspace, { material: id });
    function escapeView(event) {
      if (event.key === "Escape" && workspace.isConnected && materialPanel.closeView()) {
        event.preventDefault(); event.stopPropagation();
      }
    }
    if (actions) document.addEventListener("keydown", escapeView, true);
    state.currentDetail = null; // an existing modal's teardown must not navigate history
    ContentViewer.open({ content: workspace, filename: material.description, onOpen: () => {
      const close = workspace.closest(".cv-card")?.querySelector(".cv-close");
      if (actions && close) actions.append(close);
    }, onClose: () => {
      document.removeEventListener("keydown", escapeView, true);
      materialPanel.dispose();
      if (state.currentDetail?.type === "material") {
        state.currentDetail = null;
        dismissViewerHistory(pushHistory ? depth + 1 : 0);
      }
    } });
    state.currentDetail = { type: "material", file: id };
    if (pushHistory) history.pushState(null, "", "#" + materialHash(id, options));
    materialPanel.applyRoute(options);
  }
}
