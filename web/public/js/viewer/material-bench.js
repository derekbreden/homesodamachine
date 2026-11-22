// A print case pairs the dated bench photograph and its observations with landmarks on the current model.
import { HSM_EVENTS } from "/contracts/client-events.js";
import { instanceBody } from "/contracts/features.js";
import { materialHash } from "/contracts/material-tabs.js";
import { findWhenMounted } from "./pick-find.js";
import { setComponentPickEnabled } from "./component-picker.js";

const node = (tag, className, text) => {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
};
function link(text, href) {
  const a = node("a", "", text);
  a.href = href;
  return a;
}

export function mountMaterialBench(wrapper, material, file) {
  const stage = wrapper.closest(".cad-stage");
  const pane = node("aside", "material-bench");
  pane.setAttribute("aria-label", "Bench photos");
  const modelLabel = node("span", "bench-model-label", "Current model");
  wrapper.append(modelLabel);
  stage.classList.add("bench-open");
  stage.append(pane);
  const controller = new AbortController();
  let data = null, requested = {}, current = null, selected = null, find = null;
  const selector = node("select");
  selector.setAttribute("aria-label", "Choose a recorded print");
  const title = node("h2", "", "Bench photos");
  const head = node("header", "bench-head");
  const date = node("time", "bench-date");
  head.append(title, selector, date);
  const figure = node("div", "bench-figure");
  const marks = node("div", "bench-landmarks");
  marks.setAttribute("role", "group");
  marks.setAttribute("aria-label", "Locate in the photo and model");
  const detail = node("div", "bench-observation");
  detail.setAttribute("aria-live", "polite");
  const pick = node("button", "bench-pick", "Pick a receiver in 3D");
  pick.type = "button";
  const hint = node("span", "bench-pick-hint");
  hint.setAttribute("role", "status");
  pick.addEventListener("click", () => {
    setComponentPickEnabled(true);
    hint.textContent = "Tap a receiver on the current model.";
  });
  const evidence = node("div", "bench-evidence");

  function locate(feature, focusModel = true) {
    const mark = current.landmarks.find(m => m.feature === feature) || current.landmarks[0];
    selected = mark.feature;
    hint.textContent = "";
    for (const control of pane.querySelectorAll("button[data-landmark]")) {
      control.setAttribute("aria-pressed", String(control.dataset.landmark === selected));
    }
    detail.replaceChildren(node("h3", "", mark.label), node("p", "", mark.observation));
    if (mark.change) detail.append(link(mark.changeLabel, "/changes/" + mark.change));
    history.replaceState(history.state, "", "#" + materialHash(material.id, { view: "bench", benchCase: current.id, landmark: selected }));
    find?.abort();
    if (focusModel) {
      find = new AbortController();
      findWhenMounted(file, `feature: ${data.body}::${selected}\nview: ${data.view}`, find.signal);
    }
  }
  function markButton(mark, i, pin) {
    const button = node("button", pin ? "bench-pin" : "bench-place");
    button.type = "button";
    button.dataset.landmark = mark.feature;
    button.setAttribute("aria-label", `Locate ${mark.label} in photo and model`);
    button.title = mark.label;
    const number = node("span", "bench-number", String(i + 1));
    button.append(number);
    if (pin) {
      button.style.left = mark.point[0] * 100 + "%";
      button.style.top = mark.point[1] * 100 + "%";
    } else button.append(mark.label);
    button.addEventListener("click", () => locate(mark.feature));
    return button;
  }
  function openCase(entry, feature, focusModel = true) {
    current = entry;
    selector.value = entry.id;
    const archived = `${entry.revision}/${entry.folder}/`;
    const repo = "https://github.com/derekbreden/homesodamachine/blob/" + archived;
    const photo = node("img");
    photo.src = "https://raw.githubusercontent.com/derekbreden/homesodamachine/" + archived + entry.photo;
    photo.alt = entry.alt;
    photo.addEventListener("error", () => {
      if (!figure.contains(photo)) return;
      figure.replaceChildren(link("Open the archived bench photograph", repo + entry.photo));
    });
    figure.replaceChildren(photo, ...entry.landmarks.map((mark, i) => markButton(mark, i, true)));
    marks.replaceChildren(...entry.landmarks.map((mark, i) => markButton(mark, i, false)));
    const quote = node("blockquote", "", "“" + entry.quote + "”");
    quote.append(node("cite", "", "Derek, at the bench"));
    date.dateTime = entry.date;
    date.textContent = new Intl.DateTimeFormat("en", { dateStyle: "medium", timeZone: "UTC" }).format(new Date(entry.date + "T12:00:00Z"));
    const sources = node("nav", "bench-sources");
    sources.setAttribute("aria-label", "Print sources");
    sources.append(link("Print job", repo + "print-job.json"), link("Physical record · " + entry.revision.slice(0, 7), repo + entry.record));
    if (entry.guidePage) sources.append(link("Printing the Machine · " + entry.guideTitle,
      "/read/printing-the-machine/printing-the-machine.pdf#page=" + entry.guidePage));
    evidence.replaceChildren(quote, node("p", "bench-setup", entry.setup), sources);
    locate(feature, focusModel);
  }
  function go(options = {}) {
    requested = options;
    if (!data) return;
    const entry = data.cases.find(c => c.id === options.benchCase) || data.cases[0];
    const feature = entry.landmarks.find(m => m.feature === options.landmark)?.feature || entry.landmarks[0].feature;
    if (entry !== current || selected !== feature) openCase(entry, feature);
  }
  selector.addEventListener("change", () => {
    const entry = data.cases.find(c => c.id === selector.value);
    openCase(entry, selected);
  });
  window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, ({ detail: pick }) => {
    if (!data || !pick.feature || pick.file !== file || instanceBody(pick.name) !== data.body) return;
    if (current.landmarks.some(mark => mark.feature === pick.feature)) locate(pick.feature, false);
    else {
      const entry = data.cases.find(c => c.landmarks.some(mark => mark.feature === pick.feature));
      if (entry) openCase(entry, pick.feature, false);
      else hint.textContent = "These prints have no photo marker for that feature.";
    }
  }, { signal: controller.signal });

  async function load() {
    const status = node("p", "bench-loading", "Loading bench photos…");
    status.setAttribute("role", "status");
    pane.replaceChildren(status);
    try {
      const response = await fetch("/print-cases/" + encodeURIComponent(material.print_cases), { signal: controller.signal });
      if (!response.ok) throw new Error("Print cases unavailable");
      const cases = await response.json();
      if (controller.signal.aborted) return;
      data = cases;
      for (const entry of data.cases) selector.add(new Option(entry.title, entry.id));
      pane.replaceChildren(head, figure, marks, detail, pick, hint, evidence);
      go(requested);
    } catch {
      if (controller.signal.aborted) return;
      status.textContent = "The bench photos could not be loaded.";
      const retry = node("button", "", "Try again");
      retry.type = "button";
      retry.addEventListener("click", load, { once: true });
      pane.append(retry);
    }
  }
  load();
  return { go, dispose() {
    controller.abort();
    find?.abort();
    stage.classList.remove("bench-open");
    pane.remove();
    modelLabel.remove();
  } };
}
