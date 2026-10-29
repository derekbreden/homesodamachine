import { startAnimate, stopAnimate } from "./scene.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

const button = (text, label) => {
  const node = document.createElement("button");
  node.type = "button"; node.textContent = text;
  if (label) { node.setAttribute("aria-label", label); node.title = label; }
  return node;
};

// The workspace owns navigation and document controls. The embedded reader
// renders the sheet; its camera-bearing model stays mounted behind it.
export function mountMaterialDrawing(wrapper) {
  const workspace = wrapper.closest(".cad-workspace");
  const switcher = document.createElement("div");
  switcher.className = "material-view-switch";
  switcher.setAttribute("role", "group"); switcher.setAttribute("aria-label", "Material view");
  switcher.hidden = true;
  const model = button("3D"), drawing = button("Drawing");
  model.setAttribute("aria-pressed", "true"); drawing.setAttribute("aria-pressed", "false");
  switcher.append(model, drawing);
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

  let selected = null, frame = null, showing = false;
  const command = (command, extra = {}) => frame?.contentWindow?.postMessage({
    type: HSM_EVENTS.DOCUMENT_COMMAND, command, ...extra,
  }, location.origin);
  function showModel() {
    if (!showing) return false;
    showing = false; menu.open = false; tools.hidden = true;
    wrapper.classList.remove("drawing-open");
    if (frame) frame.hidden = true;
    model.setAttribute("aria-pressed", "true"); drawing.setAttribute("aria-pressed", "false");
    if (wrapper.isConnected) startAnimate();
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
    showing = true; frame.hidden = false; tools.hidden = false;
    wrapper.classList.add("drawing-open");
    model.setAttribute("aria-pressed", "false"); drawing.setAttribute("aria-pressed", "true");
    stopAnimate();
  }
  function setDrawing(doc) {
    if (selected?.path === doc?.path) { selected = doc; return; }
    showModel(); frame?.remove(); frame = null; selected = doc;
    switcher.hidden = !doc;
    for (const control of [out, fit, into, menuOut, menuIn]) control.disabled = true;
    if (doc) {
      const path = doc.path.split("/").map(encodeURIComponent).join("/");
      full.href = "/read/" + path; download.href = "/docs/" + path + "?download=1";
      drawing.title = doc.title;
    }
  }
  const mounted = () => { if (showing) stopAnimate(); };
  const message = event => {
    if (!frame || event.source !== frame.contentWindow || event.origin !== location.origin) return;
    if (event.data?.type === HSM_EVENTS.DOCUMENT_ESCAPE) { showModel(); model.focus(); }
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
  model.addEventListener("click", showModel); drawing.addEventListener("click", () => showDrawing());
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.addEventListener("message", message);
  return { setDrawing, showDrawing, drawingPath: () => selected?.path, showing: () => showing, closeDrawing: () => {
    const closed = showModel(); if (closed) model.focus(); return closed;
  }, dispose: () => {
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.removeEventListener("message", message);
    frame?.remove(); switcher.remove(); tools.remove();
  } };
}
