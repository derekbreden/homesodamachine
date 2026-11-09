import { state } from "./state.js";
import { materialIndex, modelForMaterial } from "/contracts/materials.js";
import { parseStepHash, walkDepth } from "./step-nav.js";
import { dismissViewerHistory } from "./viewer-history.js";

export function materialHash(id, { tab = null, panel = null, instance = null } = {}) {
  const query = new URLSearchParams();
  if (["bom", "cost", "stock", "used"].includes(tab)) query.set("tab", tab);
  if (panel === "materials") query.set("panel", panel);
  if (instance) query.set("instance", instance);
  return "material:" + encodeURIComponent(id) + (query.size ? "?" + query : "");
}

export async function openMaterial(id, pushHistory = true, { tab = null, panel = null, instance = null, fly = true } = {}) {
  // Links written with six-digit ids (`HSM-000546`) open the same material.
  id = id.replace(/^HSM-0*(\d+)$/, (_, n) => "HSM-" + n.padStart(4, "0"));
  const material = materialIndex(state.materialCatalog).get(id);
  if (!material) {
    const notice = document.createElement("p"); notice.className = "material-catalog-status";
    notice.textContent = `Material ${id} is not in the catalog.`;
    state.gridEl?.querySelector(".material-route-error")?.remove();
    notice.classList.add("material-route-error"); state.gridEl?.prepend(notice); return;
  }
  const file = modelForMaterial(state.materialCatalog, id)?.file;
  if (file) {
    if (state.currentCadWrapper && (pushHistory || state.mountedDetail?.file === file)) {
      const { drillTo, jumpToStep } = await import("./step-nav.js");
      if (instance) await jumpToStep(file);
      else if (state.mountedDetail?.type === "step") await drillTo(file);
      else await jumpToStep(file);
      if (state.currentDetail?.file !== file) return;
    } else {
      const { openDetail } = await import("./cad-detail.js");
      openDetail(file, pushHistory);
    }
    const raw = location.hash.slice(1);
    const remembered = raw.startsWith("step:") ? parseStepHash(raw) : history.state?.materialPath;
    const materialPath = remembered?.at(-1) === file ? remembered : [file];
    history.replaceState({ materialPath }, "", "#" + materialHash(id, { tab, panel, instance }));
    state.materialPanel?.setRoot(id);
    state.materialPanel?.applyRoute({ tab, panel, instance, fly });
  } else {
    const depth = state.currentCadWrapper ? walkDepth() : 0;
    const { mountMaterialPanel } = await import("./material-panel.js");
    const workspace = document.createElement("div");
    workspace.className = "material-record-workspace";
    const materialPanel = mountMaterialPanel(workspace, { material: id });
    state.currentDetail = null; // an existing modal's teardown must not navigate history
    ContentViewer.open({ content: workspace, filename: material.description, onClose: () => {
      materialPanel.dispose();
      if (state.currentDetail?.type === "material") {
        state.currentDetail = null;
        dismissViewerHistory(pushHistory ? depth + 1 : 0);
      }
    } });
    state.currentDetail = { type: "material", file: id };
    materialPanel.applyRoute({ tab, panel });
    if (pushHistory) history.pushState(null, "", "#" + materialHash(id, { tab, panel }));
  }
}
