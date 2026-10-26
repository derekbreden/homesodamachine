import { state } from "./state.js";
import { materialIndex, modelForMaterial } from "/contracts/materials.js";
import { parseStepHash, walkDepth } from "./step-nav.js";
import { dismissViewerHistory } from "./viewer-history.js";

export const materialHash = (id, { tab = null } = {}) => "material:" + encodeURIComponent(id) + (tab === "bom" ? "?tab=bom" : "");

export async function openMaterial(id, pushHistory = true, { tab = null } = {}) {
  const material = materialIndex(state.materialCatalog).get(id);
  if (!material) {
    const notice = document.createElement("p"); notice.className = "material-catalog-status";
    notice.textContent = `Material ${id} is not in the catalog.`;
    state.gridEl?.querySelector(".material-route-error")?.remove();
    notice.classList.add("material-route-error"); state.gridEl?.prepend(notice); return;
  }
  const file = modelForMaterial(state.materialCatalog, id)?.file;
  if (file) {
    if (state.currentCadWrapper && pushHistory) {
      const { drillTo, jumpToStep } = await import("./step-nav.js");
      if (state.mountedDetail?.type === "step") await drillTo(file);
      else await jumpToStep(file);
      if (state.currentDetail?.file !== file) return;
    } else {
      const { openDetail } = await import("./cad-detail.js");
      openDetail(file, pushHistory);
    }
    const raw = location.hash.slice(1);
    const materialPath = raw.startsWith("step:") ? parseStepHash(raw) : history.state?.materialPath || [file];
    history.replaceState({ materialPath }, "", "#" + materialHash(id, { tab }));
    state.materialPanel?.setRoot(id);
    state.materialPanel?.show();
    if (tab === "bom") state.materialPanel?.showBom();
  } else {
    const depth = state.currentCadWrapper ? walkDepth() : 0;
    const { mountMaterialPanel } = await import("./material-panel.js");
    const workspace = document.createElement("div");
    workspace.className = "material-record-workspace";
    const panel = mountMaterialPanel(workspace, { material: id });
    state.currentDetail = null; // an existing modal's teardown must not navigate history
    ContentViewer.open({ content: workspace, filename: material.description, onClose: () => {
      panel.dispose();
      if (state.currentDetail?.type === "material") {
        state.currentDetail = null;
        dismissViewerHistory(pushHistory ? depth + 1 : 0);
      }
    } });
    state.currentDetail = { type: "material", file: id };
    if (tab === "bom") panel.showBom();
    if (pushHistory) history.pushState(null, "", "#" + materialHash(id, { tab }));
  }
}
