import { startAnimate, stopAnimate } from "./scene.js";
import { state } from "./state.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { materialHash, openMaterial } from "./material-nav.js";
import { mountMaterialBench } from "./material-bench.js";
import { modelForMaterial } from "/contracts/materials.js";
import { clearSurfaceViews } from "./surface-actions.js";

const button = (text, label) => {
  const node = document.createElement("button");
  node.type = "button"; node.textContent = text;
  if (label) { node.setAttribute("aria-label", label); node.title = label; }
  return node;
};

// The material workspace switches views and keeps its camera-bearing model mounted.
export function mountMaterialDrawing(wrapper, { hideMaterials, recordOnly = false }) {
  const workspace = wrapper.closest(".cad-workspace, .cad-record-views");
  const switcher = document.createElement("div");
  switcher.className = "material-view-switch";
  switcher.setAttribute("role", "group"); switcher.setAttribute("aria-label", "Material view");
  switcher.hidden = true;
  const model = button(recordOnly ? "Material" : "3D"), drawing = button("Drawing"), print = button("Print"), pcb = button("PCB");
  const bench = button("Bench", "Bench photos");
  const clearances = button("Clearances");
  const modes = { model, drawing, print, pcb, bench, clearances };
  for (const [name, control] of Object.entries(modes)) control.setAttribute("aria-pressed", String(name === "model"));
  switcher.append(model);
  workspace.querySelector(".cad-view-slot").append(switcher);

  const tools = document.createElement("div"); tools.className = "drawing-tools"; tools.hidden = true;
  tools.setAttribute("role", "group"); tools.setAttribute("aria-label", "Drawing controls");
  const out = button("−", "Zoom out"), fit = button("Fit", "Fit drawing to page"), into = button("+", "Zoom in");
  for (const control of [out, fit, into]) control.disabled = true;
  const zoom = document.createElement("div"); zoom.className = "drawing-zoom";
  zoom.append(out, fit, into);
  const menu = document.createElement("details"); menu.className = "workspace-menu drawing-menu";
  const summary = document.createElement("summary"); summary.textContent = "⋯";
  summary.setAttribute("aria-label", "Drawing actions"); summary.title = "Drawing actions";
  const menuBody = document.createElement("div"); menuBody.className = "workspace-menu-body";
  const menuZoom = document.createElement("div"); menuZoom.className = "drawing-menu-zoom";
  const zoomLabel = document.createElement("span"); zoomLabel.textContent = "Zoom";
  const menuOut = button("−", "Zoom out"), menuIn = button("+", "Zoom in");
  menuZoom.append(zoomLabel, menuOut, menuIn);
  const pages = document.createElement("div"); pages.className = "drawing-pages"; pages.hidden = true;
  const prev = button("←", "Previous page"), next = button("→", "Next page");
  const pageLabel = document.createElement("label"); pageLabel.textContent = "Page ";
  const page = document.createElement("input"); page.type = "number"; page.min = "1"; page.value = "1";
  page.inputMode = "numeric"; pageLabel.append(page);
  const total = document.createElement("span");
  pages.append(prev, pageLabel, total, next);
  const full = document.createElement("a"); full.className = "drawing-full-link";
  full.textContent = "Open full drawing"; full.target = "_blank"; full.rel = "noopener";
  const download = document.createElement("a"); download.className = "drawing-download";
  download.textContent = "Download PDF"; download.setAttribute("download", "");
  menuBody.append(menuZoom, pages, full, download); menu.append(summary, menuBody);
  tools.append(zoom, menu); workspace.querySelector(".cad-document-slot").append(tools);

  let selected = null, frame = null, replay = null, printFrame = null, mode = "model";
  let board = null, boardView = null;
  let benchMaterial = null, benchView = null;
  let fitMaterial = null, fitCatalog = null, fits = [], fitView = null, fitRequest = null;
  const syncSwitcher = () => { switcher.hidden = !selected && !replay && !board && !benchMaterial && !fits.length; };
  const command = (command, extra = {}) => frame?.contentWindow?.postMessage({
    type: HSM_EVENTS.DOCUMENT_COMMAND, command, ...extra,
  }, location.origin);
  function removeBoardView() {
    boardView?.controller.abort();
    boardView?.host.remove();
    boardView = null;
  }
  function show(nextMode) {
    if (mode === nextMode) return false;
    clearSurfaceViews();
    const linkedMaterial = mode === "clearances" ? fitMaterial : mode === "bench" ? benchMaterial : null;
    if (linkedMaterial) {
      const [identity, query] = location.hash.slice(1).split("?");
      if (identity === materialHash(linkedMaterial.id) && new URLSearchParams(query).get("view") === mode) {
        history.replaceState(history.state, "", "#" + materialHash(linkedMaterial.id, { view: nextMode }));
      }
    }
    if (mode === "clearances") {
      fitRequest?.abort(); fitRequest = null;
      fitView?.dispose(); fitView = null;
    } else if (mode === "bench") {
      benchView?.dispose(); benchView = null;
    }
    mode = nextMode;
    menu.open = false;
    tools.hidden = mode !== "drawing";
    if (frame) frame.hidden = mode !== "drawing";
    if (mode !== "print") { printFrame?.remove(); printFrame = null; }
    if (mode !== "pcb") removeBoardView();
    wrapper.classList.toggle("drawing-open", mode === "drawing");
    wrapper.classList.toggle("print-open", mode === "print");
    wrapper.classList.toggle("pcb-open", mode === "pcb");
    wrapper.classList.toggle("clearances-open", mode === "clearances");
    for (const [name, control] of Object.entries(modes)) control.setAttribute("aria-pressed", String(name === mode));
    if (mode !== "model" && mode !== "bench") stopAnimate();
    else if (!recordOnly && wrapper.isConnected) startAnimate();
    return true;
  }
  function showDrawing(doc = selected) {
    if (!doc) return;
    setDrawing(doc);
    if (!frame) {
      frame = document.createElement("iframe"); frame.className = "material-drawing-view";
      frame.title = doc.title || "Engineering drawing";
      frame.src = "/read/" + doc.path.split("/").map(encodeURIComponent).join("/") + "?embed=1&controls=host";
      frame.addEventListener("load", () => command("state"));
      wrapper.append(frame);
    }
    show("drawing");
  }
  function setDrawing(doc) {
    if (selected?.path === doc?.path) { selected = doc; return; }
    if (mode === "drawing") show("model");
    frame?.remove(); frame = null; selected = doc;
    for (const control of [out, fit, into, menuOut, menuIn]) control.disabled = true;
    if (doc) {
      const path = doc.path.split("/").map(encodeURIComponent).join("/");
      full.href = "/read/" + path; download.href = "/docs/" + path + "?download=1";
      drawing.title = doc.title;
      model.after(drawing);
    } else drawing.remove();
    syncSwitcher();
  }
  function setPrint(id, entry) {
    if (replay?.id === id && replay?.sha256 === entry?.sha256 && replay?.title === entry?.title) return;
    if (mode === "print") show("model");
    replay = entry ? { ...entry, id } : null;
    if (replay) switcher.append(print);
    else print.remove();
    syncSwitcher();
  }
  function showPrint() {
    if (!replay || printFrame) return;
    printFrame = document.createElement("iframe");
    printFrame.className = "material-print-view";
    printFrame.title = replay.title;
    printFrame.setAttribute("sandbox", "allow-scripts");
    printFrame.src = "/print-playback/" + encodeURIComponent(replay.id);
    wrapper.append(printFrame);
    show("print");
  }
  function setBench(material) {
    const next = material?.print_cases ? material : null;
    if (next?.id === benchMaterial?.id) return;
    if (mode === "bench") show("model");
    benchMaterial = next;
    if (next) switcher.append(bench);
    else bench.remove();
    syncSwitcher();
  }
  function showBench(options = {}) {
    if (!benchMaterial) return;
    const file = benchMaterial.models?.find(model => !model.type || model.type === "step")?.file;
    if (!file) return;
    if (state.currentDetail?.file !== file) {
      openMaterial(benchMaterial.id, true, { view: "bench", ...options });
      return;
    }
    hideMaterials();
    show("bench");
    history.replaceState(history.state, "", "#" + materialHash(benchMaterial.id, { ...options, view: "bench" }));
    benchView ||= mountMaterialBench(wrapper, benchMaterial, file);
    benchView.go(options);
  }
  function setPcb(source = null) {
    if (source === board) return;
    if (mode === "pcb") show("model");
    board = source;
    if (board) switcher.append(pcb);
    else pcb.remove();
    syncSwitcher();
  }
  async function showPcb() {
    if (!board || (boardView && !boardView.failed)) return;
    removeBoardView();
    const source = board;
    const controller = new AbortController();
    const host = document.createElement("div");
    host.className = "material-pcb-view pcb-wrapper";
    const status = document.createElement("p");
    status.className = "material-pcb-status";
    status.setAttribute("role", "status");
    status.textContent = "Loading PCB view…";
    host.append(status);
    const view = { host, controller, failed: false };
    boardView = view;
    wrapper.append(host);
    show("pcb");
    try {
      const version = state.codeVersion ? `?v=${encodeURIComponent(state.codeVersion)}` : "";
      const { mountPcbView } = await import(`./pcb.js${version}`);
      if (!controller.signal.aborted) await mountPcbView(host, source, controller.signal);
      status.remove();
    } catch (error) {
      if (controller.signal.aborted) return;
      view.failed = true;
      status.textContent = "PCB view unavailable. Select PCB to retry.";
      console.warn("PCB view:", error.message);
    }
  }
  function setClearances(material, catalog) {
    if (fitMaterial?.id === material?.id && fitCatalog === catalog) return;
    const next = material ? catalog?.records.filter(fit => fit.host === material.id || fit.mate === material.id) || [] : [];
    const updating = mode === "clearances" && fitMaterial?.id === material?.id && next.length > 0;
    if (updating && JSON.stringify([next, catalog.allowance]) === JSON.stringify([fits, fitCatalog.allowance])) {
      fitCatalog = catalog; fitMaterial = material; fits = next;
      return;
    }
    if (mode === "clearances") show("model");
    fitMaterial = material; fitCatalog = catalog; fits = next;
    if (fits.length) switcher.append(clearances);
    else clearances.remove();
    syncSwitcher();
    if (updating) showClearances();
  }
  async function showClearances() {
    if (!fits.length || mode === "clearances") return;
    if (!recordOnly && state.currentDetail?.file !== modelForMaterial(state.materialCatalog, fitMaterial.id)?.file) {
      await openMaterial(fitMaterial.id, true, { view: "clearances" });
      return;
    }
    hideMaterials(); show("clearances");
    history.replaceState(history.state, "", "#" + materialHash(fitMaterial.id, { view: "clearances" }));
    const request = new AbortController(); fitRequest = request;
    try {
      const { mountClearances } = await import("./material-clearances.js");
      if (!request.signal.aborted) fitView = mountClearances(wrapper, fitMaterial, fits, state.materialCatalog);
    } catch (error) {
      if (request.signal.aborted) return;
      const status = button("Retry loading fitted surfaces"); status.className = "fit-load-error";
      status.addEventListener("click", () => { show("model"); showClearances(); });
      wrapper.append(status); fitView = { dispose: () => status.remove() };
      console.warn("Clearances view:", error);
    }
  }
  function applyRoute(view, options) {
    if (view === "clearances") showClearances();
    else if (view === "pcb") showPcb();
    else if (view === "print") showPrint();
    else if (view === "bench") showBench(options);
    else if (mode === "pcb" || mode === "print" || mode === "bench" || mode === "clearances") show("model");
  }
  function closeView() {
    if (mode === "pcb" || mode === "print") {
      const url = new URL(location.href);
      const [hash, query] = url.hash.split("?");
      const params = new URLSearchParams(query);
      if (params.get("view") === mode) {
        params.delete("view");
        url.hash = hash + (params.size ? "?" + params : "");
        history.replaceState(history.state, "", url);
      }
    }
    const closed = show("model");
    if (closed) model.focus();
    return closed;
  }
  const mounted = () => { if (mode !== "model" && mode !== "bench") stopAnimate(); };
  const message = event => {
    if (event.source === printFrame?.contentWindow && event.origin === "null" && event.data?.type === HSM_EVENTS.DOCUMENT_ESCAPE) {
      closeView();
      return;
    }
    if (!frame || event.source !== frame.contentWindow || event.origin !== location.origin) return;
    if (event.data?.type === HSM_EVENTS.DOCUMENT_ESCAPE && mode === "drawing") closeView();
    if (event.data?.type !== HSM_EVENTS.DOCUMENT_STATE) return;
    const state = event.data;
    out.disabled = !state.ready || state.zoom <= 0.5;
    into.disabled = !state.ready || state.zoom >= 4; fit.disabled = !state.ready;
    menuOut.disabled = out.disabled; menuIn.disabled = into.disabled;
    page.value = state.page; page.max = state.pages;
    total.textContent = "of " + state.pages; pages.hidden = state.pages <= 1;
    prev.disabled = state.page <= 1; next.disabled = state.page >= state.pages;
    fit.title = "Fit drawing to page · " + Math.round(state.zoom * 100) + "%";
  };
  out.addEventListener("click", () => command("zoom-out")); into.addEventListener("click", () => command("zoom-in"));
  menuOut.addEventListener("click", () => command("zoom-out")); menuIn.addEventListener("click", () => command("zoom-in"));
  fit.addEventListener("click", () => command("fit"));
  prev.addEventListener("click", () => command("page", { page: Number(page.value) - 1 }));
  next.addEventListener("click", () => command("page", { page: Number(page.value) + 1 }));
  page.addEventListener("change", () => command("page", { page: page.value }));
  page.addEventListener("keydown", event => { if (event.key === "Enter") { command("page", { page: page.value }); page.blur(); } });
  model.addEventListener("click", closeView);
  drawing.addEventListener("click", () => showDrawing());
  print.addEventListener("click", showPrint);
  bench.addEventListener("click", () => { if (mode !== "bench") showBench(); });
  pcb.addEventListener("click", showPcb);
  clearances.addEventListener("click", showClearances);
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.addEventListener("message", message);
  return { setDrawing, setPrint, setPcb, setBench, setClearances, showDrawing, applyRoute, drawingPath: () => selected?.path, closeView,
    closeInspection: () => { if (mode === "bench" || mode === "clearances") closeView(); }, dispose: () => {
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.removeEventListener("message", message);
    fitRequest?.abort(); fitView?.dispose(); benchView?.dispose(); removeBoardView(); frame?.remove(); printFrame?.remove(); switcher.remove(); tools.remove();
  } };
}
