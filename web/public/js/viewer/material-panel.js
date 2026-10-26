import { state } from "./state.js";
import { materialIndex, materialForFile, explodeBom, bomCountText, bomCounts, materialDocuments, materialUses, occurrenceBodies, occurrenceForBody, matchesBody } from "/contracts/materials.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { highlightParts, clearHighlight, scenePartNames } from "./part-highlight.js";
import { openMaterial, materialHash } from "./material-nav.js";
import { makeMaterialSearch } from "./material-search.js";
import { componentLocation, stepLabel, stepLocation } from "/contracts/step-locations.js";
import { mountMaterialDrawing } from "./material-drawing.js";

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const options = () => ({ finish: state.faucetFinish });
const quantity = (q, unit = "ea") => q == null ? "As required" : `${Number(q.toFixed(3))} ${unit}`;
const pathKey = (path) => path.map((item) => `${item.material}:${item.occurrence}`).join("/");
const docHref = (path) => path.endsWith(".pdf") ? "/read/" + path :
  "https://github.com/derekbreden/homesodamachine/blob/main/hardware/" + path;

export function mountMaterialPanel(workspace, { file = null, material = null } = {}) {
  const panel = el("aside", "material-panel");
  panel.setAttribute("aria-label", "Material explorer");
  workspace.append(panel);
  const wrapper = workspace.querySelector(".cad-wrapper");
  const mobile = matchMedia("(max-width: 700px)");
  const toggle = wrapper ? el("button", "materials-toggle", "Materials") : null;
  function setOpen(open) {
    workspace.classList.toggle("materials-open", open);
    toggle?.setAttribute("aria-expanded", String(open));
  }
  if (toggle) {
    toggle.type = "button";
    toggle.addEventListener("click", () => setOpen(!workspace.classList.contains("materials-open")));
    workspace.append(toggle);
    setOpen(false);
  }
  const closeOnMobile = () => { if (mobile.matches) setOpen(false); };
  mobile.addEventListener("change", closeOnMobile);
  const drawingView = wrapper ? mountMaterialDrawing(wrapper, { onShowDrawing: closeOnMobile }) : null;
  let root = material || materialForFile(state.materialCatalog, file)?.id;
  let selected = root, selectedPath = [], tab = "bom";
  let selectedBody = null;
  const expanded = new Set();
  let lastFile = file;
  const scroll = el("div", "material-panel-scroll");
  const headHost = el("div", "material-head-host"), tabsHost = el("div", "material-tabs-host");
  const search = makeMaterialSearch({ compact: true });
  panel.append(search, headHost, tabsHost, scroll);
  let disposed = false;
  let pendingRootFocus = false;
  function contextPath() {
    const parent = materialForFile(state.materialCatalog, lastFile);
    return parent && parent.id !== root ? explodeBom(state.materialCatalog, parent.id, options()).find((r) => r.material.id === root)?.path || [] : [];
  }
  const bindingsFor = (path, names) => occurrenceBodies(state.materialCatalog, [...contextPath(), ...path], names, options());

  function setRoot(id) {
    selectedBody = null;
    root = id; selected = id; selectedPath = []; expanded.clear();
    render();
    const path = contextPath();
    pendingRootFocus = path.length > 0 && state.mountedDetail?.file !== lastFile;
    if (path.length && !pendingRootFocus) highlightParts(occurrenceBodies(state.materialCatalog, path, scenePartNames(), options()));
    else clearHighlight();
  }

  function select(id, path = []) {
    selectedBody = null;
    selected = id; selectedPath = path;
    render();
  }

  function materialLink(m, label = m.description) {
    const link = el("a", "material-link", label);
    link.href = "/3d#" + materialHash(m.id, { panel: "materials" });
    link.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); openMaterial(m.id, true, { panel: "materials" });
    });
    return link;
  }

  function render() {
    const top = scroll.scrollTop;
    scroll.replaceChildren();
    const index = materialIndex(state.materialCatalog), current = index.get(selected), rootMaterial = index.get(root);
    const head = el("div", "material-panel-head");
    const actions = el("div", "material-actions");
    if (rootMaterial && (selected !== root || selectedBody)) {
      const back = el("button", "material-context", "← " + rootMaterial.description);
      back.type = "button"; back.addEventListener("click", () => { clearHighlight(); select(root); }); head.append(back);
    }
    head.append(el("span", "material-eyebrow", current ? `${current.id} · ${current.kind}` : selectedBody ? "Component in assembly" : "CAD model"));
    head.append(el("h2", "", current?.description || (selectedBody || stepLabel(lastFile)).replace(/[-_]/g, " ") || "Material explorer"));
    if (selectedBody) {
      const context = rootMaterial?.bom?.context?.find(item => item.bodies?.some(body => matchesBody(selectedBody, body)));
      head.append(el("p", "material-meta", context?.description || "No material record linked to this component."));
      const open = el("button", "", "Open component"); open.type = "button";
      open.addEventListener("click", async () => {
        const { drillToComponent } = await import("./step-nav.js");
        drillToComponent(componentLocation(lastFile, selectedBody), selectedBody);
      });
      actions.append(open);
    }
    if (current?.manufacturer_number) head.append(el("p", "material-meta", "Manufacturer part: " + current.manufacturer_number));
    if (selectedPath.length) {
      const row = explodeBom(state.materialCatalog, root, options()).find((r) => pathKey(r.path) === pathKey(selectedPath));
      if (row) head.append(el("p", "material-meta", `${quantity(row.quantity, row.item.unit)} in ${rootMaterial.description}`));
    }
    if (current) {
      const permanent = materialLink(current, "Permanent link");
      // A regular anchor supports copying, opening in another tab and bookmarks.
      actions.append(permanent);
      const model = current.models?.find((m) => !m.type || m.type === "step");
      if (model && model.file !== lastFile) {
        const open = el("button", "", "Open 3D"); open.type = "button";
        open.addEventListener("click", async () => {
          if (state.currentCadWrapper) {
            const { drillTo } = await import("./step-nav.js"); drillTo(model.file);
          } else openMaterial(current.id);
        }); actions.prepend(open);
      }
    }
    head.append(actions);
    const drawings = current?.documents?.filter(doc => doc.kind === "engineering-drawing" && doc.path.endsWith(".pdf")) || [];
    drawingView?.setDrawing(drawings[0]);
    for (const drawing of drawings) {
      const featured = el("a", "material-drawing-feature");
      featured.href = docHref(drawing.path);
      featured.setAttribute("aria-label", "View engineering drawing: " + drawing.title);
      featured.append(el("strong", "", "Engineering drawing"), el("span", "", "View finished part →"));
      if (drawingView) featured.addEventListener("click", event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault(); drawingView.showDrawing(drawing);
      });
      head.append(featured);
    }
    headHost.replaceChildren(head);
    const rows = explodeBom(state.materialCatalog, root, options());
    const used = current ? materialUses(state.materialCatalog, current.id, options()) : { assemblies: [], tools: [], equipment: [] };
    const docs = materialDocuments(state.materialCatalog, (current || rootMaterial)?.id, options());
    const counts = { bom: rows.length, used: used.assemblies.length + used.tools.length + used.equipment.length, docs: docs.length };
    const tabs = el("div", "material-tabs"); tabs.setAttribute("role", "tablist"); tabs.setAttribute("aria-label", "Material relationships");
    for (const [key, label] of [["bom", "BOM"], ["used", "Where used"], ["docs", "Documents"]]) {
      const button = el("button", "", `${label} (${counts[key]})`); button.type = "button";
      if (key === "bom" && rootMaterial) button.title = `BOM items in ${rootMaterial.description}, including every nested level`;
      button.setAttribute("role", "tab"); button.setAttribute("aria-selected", String(tab === key));
      button.addEventListener("click", () => { tab = key; render(); }); tabs.append(button);
    }
    tabsHost.replaceChildren(tabs);
    const content = el("div", "material-tab-content"); content.setAttribute("role", "tabpanel");
    content.setAttribute("aria-label", { bom: "Exploded bill of materials", used: "Where used", docs: "Documents" }[tab]);
    scroll.append(content);
    if (tab === "bom") renderBom(content, rootMaterial, index, rows);
    if (tab === "used") renderUsed(content, current, used);
    if (tab === "docs") renderDocs(content, docs);
    scroll.scrollTop = top;
  }

  function renderBom(content, rootMaterial, index, rows) {
    if (!rootMaterial?.bom?.items.length) {
      content.append(el("p", "material-empty", rootMaterial ? "No child materials listed for this part." : "Assembly relationships have not been recorded for this model."));
    } else {
      const summary = el("p", "material-bom-counts", bomCountText({ direct: rows.filter(row => row.depth === 0).length, total: rows.length }));
      summary.title = "One item per BOM row; the total includes every nested level. Quantities appear beside each row.";
      content.append(summary);
      content.append(el("p", "material-scope", rootMaterial.bom.scope));
      const tools = el("div", "bom-tools");
      const all = el("button", "", "Expand all"); all.type = "button";
      const collapse = el("button", "", "Collapse all"); collapse.type = "button";
      all.addEventListener("click", () => { rows.forEach((r) => expanded.add(pathKey(r.path))); render(); });
      collapse.addEventListener("click", () => { expanded.clear(); render(); });
      tools.append(all, collapse, el("span", "", "Quantities per assembly")); content.append(tools);
      const tree = el("div", "bom-tree");
      for (const row of rows) {
        if (row.path.slice(0, -1).some((_, i) => !expanded.has(pathKey(row.path.slice(0, i + 1))))) continue;
        const childCounts = bomCounts(state.materialCatalog, row.material.id, options());
        const key = pathKey(row.path), branch = childCounts.total > 0;
        const line = el("div", "bom-row" + (selectedPath.length && key === pathKey(selectedPath) ? " selected" : ""));
        line.style.setProperty("--depth", row.depth);
        const disclosure = el("button", "bom-disclosure", branch ? (expanded.has(key) ? "−" : "+") : "·");
        disclosure.type = "button"; disclosure.disabled = !branch;
        disclosure.setAttribute("aria-label", `${expanded.has(key) ? "Collapse" : "Expand"} ${row.material.description}`);
        if (branch) disclosure.setAttribute("aria-expanded", String(expanded.has(key)));
        disclosure.addEventListener("click", () => { if (expanded.has(key)) expanded.delete(key); else expanded.add(key); render(); });
        const pick = el("button", "bom-select"); pick.type = "button";
        pick.append(el("span", "bom-description", row.material.description), el("span", "bom-number", row.material.id));
        if (branch) pick.append(el("span", "bom-counts", bomCountText(childCounts)));
        pick.setAttribute("aria-label", `${row.material.description}, ${quantity(row.quantity, row.item.unit)} in this assembly${branch ? ", " + bomCountText(childCounts) : ""}`);
        pick.setAttribute("aria-pressed", String(selectedPath.length > 0 && key === pathKey(selectedPath)));
        pick.addEventListener("click", () => {
          const loading = state.mountedDetail?.file !== lastFile;
          const bodies = loading ? [] : bindingsFor(row.path, scenePartNames());
          select(row.material.id, row.path);
          pendingRootFocus = loading;
          if (bodies.length) highlightParts(bodies); else clearHighlight();
          const note = panel.querySelector(".material-selection-note");
          if (note) note.textContent = loading ? "The model is loading." : bodies.length ? "All visible occurrences highlighted in this model." : "This material has no drawn geometry in the current model.";
        });
        line.append(disclosure, pick, el("span", "bom-quantity", quantity(row.quantity, row.item.unit))); tree.append(line);
      }
      content.append(tree);
      if (selectedPath.length) {
        const note = el("p", "material-selection-note"); note.setAttribute("role", "status");
        content.prepend(note);
      }
      if (rootMaterial.bom.source) {
        const source = el("a", "material-source", "Parts-list source"); source.href = docHref(rootMaterial.bom.source); source.target = "_blank"; source.rel = "noopener"; content.append(source);
      }
    }
    renderRelations(content, index.get(selected) || rootMaterial, index);
  }

  function renderUsed(content, current, used) {
    if (!current) return;
    if (!used.assemblies.length) content.append(el("p", "material-empty", "No containing assemblies recorded."));
    for (const result of used.assemblies) {
      const card = el("div", "material-used");
      card.append(materialLink(result.material), el("span", "material-meta", `${result.direct ? "Direct parent" : "Ancestor"} · ${quantity(result.quantity, result.unit)}`));
      card.append(el("p", "material-path", result.path.map((id) => index.get(id)?.description || id).join(" → "))); content.append(card);
    }
    if (used.tools.length) {
      content.append(el("h3", "", "Tools for this material"));
      used.tools.forEach((m) => content.append(materialLink(m)));
    }
    if (used.equipment.length) {
      content.append(el("h3", "", "Used with")); used.equipment.forEach((m) => content.append(materialLink(m)));
    }
  }

  function renderDocs(content, docs) {
    if (!docs.length) content.append(el("p", "material-empty", "No documents linked to this material or its assemblies."));
    for (const d of docs) {
      const link = el("a", "material-document"); link.href = docHref(d.path); link.target = "_blank"; link.rel = "noopener";
      link.append(el("strong", "", d.title), el("span", "", `${d.path.endsWith(".pdf") ? "PDF" : "Details"}${d.inherited ? " · " + d.owner : ""}`)); content.append(link);
    }
  }

  function renderRelations(content, current, index) {
    const relations = current?.relations || [];
    if (!relations.length) return;
    content.append(el("h3", "", "Connected materials"));
    for (const relation of relations) {
      const m = index.get(relation.material); if (!m) continue;
      const row = el("div", "material-related");
      const label = { "tool-for": "Used to build", "used-with": "Used with", "installation-context": "Installation context", variant: "Alternative style" }[relation.kind] || relation.kind;
      row.append(el("span", "material-meta", label + (relation.quantity ? " · " + quantity(relation.quantity, relation.unit) : "")), materialLink(m)); content.append(row);
    }
  }

  function sync(event) {
    if (disposed) return;
    if (event?.type === HSM_EVENTS.FAUCET_OPTIONS) search.refresh();
    const mountedFile = state.mountedDetail?.file || file;
    if (file && mountedFile !== lastFile) {
      selectedBody = null;
      lastFile = mountedFile; root = materialForFile(state.materialCatalog, mountedFile)?.id; selected = root; selectedPath = []; expanded.clear();
    }
    render();
    if ((pendingRootFocus || (event?.type === HSM_EVENTS.STEP_MOUNTED && contextPath().length)) && state.mountedDetail?.file === lastFile) {
      pendingRootFocus = false;
      highlightParts(selectedPath.length ? bindingsFor(selectedPath, scenePartNames()) :
        occurrenceBodies(state.materialCatalog, contextPath(), scenePartNames(), options()));
    }
  }
  function picked(event) {
    if (event.detail.file !== state.mountedDetail?.file) return;
    clearHighlight();
    const rootMaterial = materialIndex(state.materialCatalog).get(root);
    const names = [...scenePartNames()];
    if (rootMaterial && names.length && names.every(name => matchesBody(name, event.detail.name)) &&
        (!stepLocation(lastFile).component || !explodeBom(state.materialCatalog, root, options()).some(row => row.item.bodies?.length || row.item.prefix) || rootMaterial.models?.some(model => model.file === lastFile))) {
      select(root); return;
    }
    const row = explodeBom(state.materialCatalog, root, options()).filter((r) =>
      bindingsFor(r.path, [event.detail.name]).length).sort((a, b) => b.depth - a.depth)[0];
    if (row) { row.path.forEach((_, i) => expanded.add(pathKey(row.path.slice(0, i + 1)))); select(row.material.id, row.path); }
    else {
      const relation = materialIndex(state.materialCatalog).get(root)?.relations?.find((r) =>
        r.bodies?.some((body) => matchesBody(event.detail.name, body)));
      if (relation) select(relation.material);
      else {
        const parent = materialForFile(state.materialCatalog, lastFile);
        const outside = parent && occurrenceForBody(state.materialCatalog, parent.id, event.detail.name, options());
        if (outside) {
          setRoot(parent.id);
          outside.path.forEach((_, i) => expanded.add(pathKey(outside.path.slice(0, i + 1))));
          select(outside.material.id, outside.path);
        } else {
          selected = null; selectedPath = []; selectedBody = event.detail.name;
          render();
        }
      }
    }
  }
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, sync);
  window.addEventListener(HSM_EVENTS.MATERIAL_PICKED, picked);
  window.addEventListener(HSM_EVENTS.FAUCET_OPTIONS, sync);
  // Visibility belongs to this navigation. Manual toggles last for this view;
  // model links start closed, and material lookups open only on desktop.
  function applyRoute({ panel = null, tab: requestedTab = null } = {}) {
    tab = "bom";
    setOpen(!mobile.matches && (panel === "materials" || requestedTab === "bom"));
    render();
  }
  const handle = { select, setRoot, sync, applyRoute, closeDrawing: () => drawingView?.closeDrawing(), dispose: () => {
    disposed = true;
    drawingView?.dispose();
    mobile.removeEventListener("change", closeOnMobile);
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, sync);
    window.removeEventListener(HSM_EVENTS.MATERIAL_PICKED, picked);
    window.removeEventListener(HSM_EVENTS.FAUCET_OPTIONS, sync);
    if (state.materialPanel === handle) state.materialPanel = null;
  } };
  state.materialPanel = handle;
  render();
  return handle;
}
