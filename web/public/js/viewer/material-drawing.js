import { startAnimate, stopAnimate } from "./scene.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

const button = (text, label) => {
  const node = document.createElement("button");
  node.type = "button"; node.textContent = text;
  if (label) { node.setAttribute("aria-label", label); node.title = label; }
  return node;
};

// The material workspace switches views and keeps its camera-bearing model mounted.
export function mountMaterialDrawing(wrapper) {
  const workspace = wrapper.closest(".cad-workspace");
  const switcher = document.createElement("div");
  switcher.className = "material-view-switch";
  switcher.setAttribute("role", "group"); switcher.setAttribute("aria-label", "Material view");
  switcher.hidden = true;
  const model = button("3D"), drawing = button("Drawing"), print = button("Print");
  const modes = { model, drawing, print };
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
  const command = (command, extra = {}) => frame?.contentWindow?.postMessage({
    type: HSM_EVENTS.DOCUMENT_COMMAND, command, ...extra,
  }, location.origin);
  function show(nextMode) {
    if (mode === nextMode) return false;
    mode = nextMode;
    menu.open = false;
    tools.hidden = mode !== "drawing";
    if (frame) frame.hidden = mode !== "drawing";
    if (mode !== "print") { printFrame?.remove(); printFrame = null; }
    wrapper.classList.toggle("drawing-open", mode === "drawing");
    wrapper.classList.toggle("print-open", mode === "print");
    for (const [name, control] of Object.entries(modes)) control.setAttribute("aria-pressed", String(name === mode));
    if (mode !== "model") stopAnimate();
    else if (wrapper.isConnected) startAnimate();
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
    switcher.hidden = !selected && !replay;
  }
  function setPrint(id, entry) {
    if (replay?.id === id && replay?.sha256 === entry?.sha256 && replay?.title === entry?.title) return;
    if (mode === "print") show("model");
    replay = entry ? { ...entry, id } : null;
    if (replay) switcher.append(print);
    else print.remove();
    switcher.hidden = !selected && !replay;
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
  function closeView() {
    const closed = show("model");
    if (closed) model.focus();
    return closed;
  }
  const mounted = () => { if (mode !== "model") stopAnimate(); };
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
  model.addEventListener("click", () => show("model"));
  drawing.addEventListener("click", () => showDrawing());
  print.addEventListener("click", showPrint);
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.addEventListener("message", message);
  return { setDrawing, setPrint, showDrawing, drawingPath: () => selected?.path, closeView, dispose: () => {
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, mounted); window.removeEventListener("message", message);
    frame?.remove(); printFrame?.remove(); switcher.remove(); tools.remove();
  } };
}
