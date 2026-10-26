import { startAnimate, stopAnimate } from "./scene.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

// The drawing replaces the visible model, while its canvas, camera and selection
// stay mounted. Only the selected material's own drawing is offered here.
export function mountMaterialDrawing(wrapper, { onShowDrawing } = {}) {
  const switcher = document.createElement("div");
  switcher.className = "material-view-switch";
  switcher.setAttribute("role", "group");
  switcher.setAttribute("aria-label", "Material view");
  switcher.hidden = true;
  const model = document.createElement("button");
  model.type = "button"; model.textContent = "3D";
  model.setAttribute("aria-pressed", "true");
  const drawing = document.createElement("button");
  drawing.type = "button"; drawing.textContent = "Drawing";
  drawing.setAttribute("aria-pressed", "false");
  switcher.append(model, drawing);
  wrapper.parentElement.prepend(switcher);

  let selected = null, frame = null, showing = false;
  function showModel() {
    if (!showing) return false;
    showing = false;
    wrapper.classList.remove("drawing-open");
    if (frame) frame.hidden = true;
    model.setAttribute("aria-pressed", "true");
    drawing.setAttribute("aria-pressed", "false");
    if (wrapper.isConnected) startAnimate();
    return true;
  }
  function showDrawing(doc = selected) {
    if (!doc) return;
    setDrawing(doc);
    if (!frame) {
      frame = document.createElement("iframe");
      frame.className = "material-drawing-view";
      frame.title = doc.title || "Engineering drawing";
      frame.src = "/read/" + doc.path.split("/").map(encodeURIComponent).join("/") + "?embed=1";
      wrapper.append(frame);
    }
    showing = true;
    frame.hidden = false;
    wrapper.classList.add("drawing-open");
    model.setAttribute("aria-pressed", "false");
    drawing.setAttribute("aria-pressed", "true");
    onShowDrawing?.();
    stopAnimate();
  }
  function setDrawing(doc) {
    if (selected?.path === doc?.path) return;
    showModel();
    frame?.remove(); frame = null;
    selected = doc;
    switcher.hidden = !doc;
  }
  const mounted = () => { if (showing) stopAnimate(); };
  const message = event => {
    if (!frame || event.source !== frame.contentWindow || event.origin !== location.origin
        || event.data?.type !== HSM_EVENTS.DOCUMENT_ESCAPE) return;
    showModel(); model.focus();
  };
  model.addEventListener("click", showModel);
  drawing.addEventListener("click", () => showDrawing());
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, mounted);
  window.addEventListener("message", message);
  return { setDrawing, showDrawing, closeDrawing: () => {
    const closed = showModel();
    if (closed) model.focus();
    return closed;
  }, dispose: () => {
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, mounted);
    window.removeEventListener("message", message);
    frame?.remove(); switcher.remove();
  } };
}
