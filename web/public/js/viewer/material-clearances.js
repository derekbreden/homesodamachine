// The material's clearance view pairs the actual mating surfaces with the chosen and default CAD numbers.
import { materialIndex } from "/contracts/materials.js";
import { inspectionMeshes } from "./step.js";
import { fitSide, nominalTube } from "./clearance-surfaces.js";
import { clearanceScene } from "./clearance-scene.js";

const el = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};
const mm = (value, places = 2) => Number(value.toFixed(places)).toLocaleString("en-US", {
  minimumFractionDigits: 2, maximumFractionDigits: places,
}).replace(/^-/, "−");

function readings(dim, fit, allowance) {
  const gap = allowance[fit.motion] * (dim.faces ?? 2) + allowance.supported * (dim.supported || 0);
  const standard = dim.nominal == null ? gap : dim.nominal + (dim.external ? -gap : gap);
  return [dim.chosen, standard].map(n => mm(n, dim.places));
}
function button(label) {
  const control = el("button", "", label);
  control.type = "button";
  return control;
}
function selector(label) {
  const field = el("label", "fit-field", label);
  const input = el("select");
  field.append(input);
  return { field, input };
}

export function mountClearances(wrapper, material, records, catalog) {
  const index = materialIndex(catalog), allowance = catalog.fittedClearances.allowance;
  const host = el("section", "material-clearance-view");
  host.setAttribute("aria-label", "Fitted clearances");
  const header = el("header", "fit-head");
  header.append(el("h2", "", material.description));
  const fitField = selector("Fitted to"), siteField = selector("Location");
  header.append(fitField.field, siteField.field);
  const diagram = el("div", "fit-diagram"), plot = el("div", "fit-plot");
  const panel = el("div", "fit-readings"), table = el("table", "fit-values");
  table.setAttribute("aria-label", "Chosen and default CAD dimensions in millimetres");
  const headRow = table.createTHead().insertRow();
  for (const text of ["mm", "Chosen", "Default"]) {
    const th = el("th", "", text); th.scope = "col"; headRow.append(th);
  }
  const body = table.createTBody();
  const sideTabs = el("div", "fit-sides");
  sideTabs.setAttribute("role", "group"); sideTabs.setAttribute("aria-label", "Label surfaces");
  const sideButtons = {};
  for (const side of ["host", "mate"]) {
    const control = button(""); control.dataset.side = side;
    control.addEventListener("click", () => { activeSide = side; renderReadings(); });
    sideTabs.append(control); sideButtons[side] = control;
  }
  panel.append(sideTabs, table);
  const tools = el("div", "fit-tools");
  const pose = el("div", "fit-pose");
  pose.setAttribute("role", "group"); pose.setAttribute("aria-label", "Part position");
  const seated = button("Seated"), apart = button("Apart"), reset = button("Reset view");
  pose.append(seated, apart); tools.append(pose, reset);
  const status = el("div", "fit-status"); status.setAttribute("role", "status");
  plot.append(tools, status); diagram.append(plot, panel); host.append(header, diagram); wrapper.append(host);
  let visual;
  try { visual = clearanceScene(diagram, plot); }
  catch (error) { host.remove(); throw error; }
  let fit, hostSite, pair, controller, activeSide, separated = false;
  let locked = null;
  const cache = new Map();

  function other(record) { return index.get(record.host === material.id ? record.mate : record.host); }
  function optionLabel(record) {
    const mate = other(record);
    return records.some(r => r !== record && other(r).id === mate.id)
      ? mate.description + " · " + record.title : mate.description;
  }
  for (const record of records) fitField.input.add(new Option(optionLabel(record)));
  if (records.length === 1) fitField.input.replaceWith(el("span", "fit-part-name", optionLabel(records[0])));

  function renderReadings() {
    locked = null; body.replaceChildren();
    const rows = [], marks = pair?.[activeSide].marks || [];
    for (const [side, control] of Object.entries(sideButtons)) {
      control.setAttribute("aria-pressed", String(side === activeSide));
    }
    function addRow(label, numbers, anchors = []) {
      const row = body.insertRow(), title = el("th"); title.scope = "row"; row.append(title);
      if (anchors.length) {
        const key = rows.length, control = button(label);
        const badge = el("span", "fit-key", String.fromCharCode(65 + key));
        badge.setAttribute("aria-hidden", "true"); control.prepend(badge); title.append(control);
        row.dataset.side = activeSide; rows.push({ element: row, marks: anchors, label, values: numbers ? readings(numbers, fit, allowance) : null });
        const highlight = n => {
          visual.select(n);
          rows.forEach(({ element }, i) => element.classList.toggle("fit-selected", i === n));
        };
        control.addEventListener("click", () => { locked = locked === key ? null : key; highlight(locked); });
        control.addEventListener("focus", () => highlight(key));
        control.addEventListener("blur", () => highlight(locked));
        row.addEventListener("pointerenter", event => { if (event.pointerType === "mouse") highlight(key); });
        row.addEventListener("pointerleave", () => highlight(locked));
      } else title.textContent = label;
      if (numbers) for (const n of readings(numbers, fit, allowance)) row.insertCell().textContent = n;
      else title.colSpan = 3;
      return row;
    }
    const gaps = activeSide === "host" ? fit.hostGaps : hostSite.mateGaps;
    const singleGap = fit.dimensions.length === 1 && fit.dimensions[0].nominal == null && marks.length === 1;
    const grouped = new Map();
    marks.forEach((mark, i) => {
      const gap = gaps ? fit.faceGaps[gaps[i]] : singleGap ? fit.dimensions[0] : null;
      const key = mark.name + "/" + (gap?.label || "");
      if (!grouped.has(key)) grouped.set(key, { name: mark.name, gap, marks: [] });
      grouped.get(key).marks.push(mark);
    });
    for (const group of grouped.values()) {
      let label = group.name;
      if (label === "Cheek" && group.marks.length > 1) label = "Each cheek";
      if (label === "Housing side" && group.gap) label += group.gap === fit.faceGaps[1] ? " at floor" : " at roof";
      addRow(label, group.gap, group.marks);
    }
    if (!singleGap) fit.dimensions.forEach((dim, i) => {
      const row = addRow(dim.label, dim);
      if (!i && marks.length) row.classList.add("fit-opening");
      if (dim.clearanceLabel) addRow(dim.clearanceLabel, { ...dim, nominal: null,
        chosen: (dim.chosen - dim.nominal) * (dim.external ? -1 : 1) });
    });
    if ([...body.rows].some(row => row.cells[1]?.textContent.startsWith("−"))) {
      const caption = table.createCaption(); caption.textContent = "Negative values indicate interference";
    } else table.deleteCaption();
    visual.setLabels(activeSide, rows);
  }
  function showPose(next) {
    separated = next;
    seated.setAttribute("aria-pressed", String(!next)); apart.setAttribute("aria-pressed", String(next));
    if (pair) visual.separate(next);
  }
  seated.addEventListener("click", () => showPose(false)); apart.addEventListener("click", () => showPose(true));
  reset.addEventListener("click", () => visual.reset());

  async function showSite() {
    controller?.abort(); controller = new AbortController();
    const { signal } = controller;
    pair = null; visual.clear();
    const station = Math.max(0, siteField.input.selectedIndex);
    hostSite = fit.hostSites[station] || fit.hostSites[0];
    const mateSite = fit.mateSites[station] || fit.mateSites[0];
    const file = (site, id) => site.file || index.get(id).models[0].file;
    const hostFile = file(hostSite, fit.host), mateFile = mateSite && file(mateSite, fit.mate);
    for (const key of cache.keys()) if (key !== hostFile && key !== mateFile) cache.delete(key);
    async function read(file) {
      if (cache.has(file)) return cache.get(file);
      const meshes = await inspectionMeshes(file, signal);
      signal.throwIfAborted(); cache.set(file, meshes); return meshes;
    }
    host.dataset.ready = "false"; status.textContent = "Loading fitted surfaces…";
    renderReadings();
    try {
      const [hostMeshes, mateMeshes] = await Promise.all([read(hostFile), mateSite ? read(mateFile) : null]);
      signal.throwIfAborted();
      const hostSide = fitSide(hostMeshes, hostSite, "host", fit);
      const mateSide = mateSite ? fitSide(mateMeshes, mateSite, "mate", fit) : nominalTube(fit);
      visual.setPair(hostSide, mateSide, fit, hostSite, separated);
      pair = { host: hostSide, mate: mateSide };
      renderReadings();
      status.replaceChildren(); host.dataset.ready = "true";
    } catch (error) {
      if (signal.aborted) return;
      console.warn("Fitted surfaces:", error);
      const retry = button("Retry"); retry.addEventListener("click", showSite);
      status.replaceChildren("Couldn’t load the fitted surfaces. ", retry);
    }
  }
  function chooseFit() {
    fit = records[Math.max(0, fitField.input.selectedIndex)];
    activeSide = material.id === fit.host ? "mate" : "host";
    sideButtons.host.textContent = fit.hostSurface;
    sideButtons.mate.textContent = fit.tubeSection ? "Nominal tube OD" : fit.mateSurface;
    siteField.input.replaceChildren();
    const sites = fit.hostSites.length >= fit.mateSites.length ? fit.hostSites : fit.mateSites;
    for (const [i, site] of sites.entries()) siteField.input.add(new Option(site.label || String(i + 1)));
    siteField.field.hidden = sites.length < 2;
    showSite();
  }
  fitField.input.addEventListener("change", chooseFit);
  siteField.input.addEventListener("change", showSite);
  showPose(false); chooseFit();
  return { dispose() { controller?.abort(); cache.clear(); visual.dispose(); host.remove(); } };
}
