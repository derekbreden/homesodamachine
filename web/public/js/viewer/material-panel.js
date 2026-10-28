import { state } from "./state.js";
import { materialIndex, materialForFile, explodeBom, bomItems, bomCountText, bomCounts, materialDocuments, materialUses, occurrenceBodies, occurrenceForBody, matchesBody } from "/contracts/materials.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { highlightParts, clearHighlight, leaveHighlight, scenePartNames } from "./part-highlight.js";
import { clearComponentSelection } from "./component-picker.js";
import { standsIn } from "/contracts/body-path.js";
import { openMaterial, materialHash } from "./material-nav.js";
import { makeMaterialSearch } from "./material-search.js";
import { componentLocation, stepLabel, stepLocation } from "/contracts/step-locations.js";
import { mountMaterialDrawing } from "./material-drawing.js";
import { rollupCost, directCost, laborUsd, money, duration, runText, COST_KINDS } from "/contracts/part-costs.js";

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const options = () => ({ finish: state.faucetFinish });
const quantity = (q, unit = "ea") => q == null ? "As required" : `${Number(q.toFixed(3))} ${unit}`;
const pathKey = (path) => path.map((item) => `${item.material}:${item.occurrence}`).join("/");
const docHref = (path) => "/read/" + path;
// Costs appear for the finished unit and everything in it; tooling and
// references have no per-unit cost.
const costedIds = () => new Set(state.materialCatalog?.costs?.costed || []);
const percent = (part, whole) => whole > 0 ? `${Math.max(0, Math.min(100, part / whole * 100)).toFixed(2)}%` : "0%";

// Parts and labor as one bar: orange for what is bought, cut, printed or used up,
// blue for attended time — the split the cost page draws for the whole unit.
function costBar(cost, scale = cost.usd) {
  const bar = el("span", "cost-split");
  bar.setAttribute("aria-hidden", "true");
  const parts = el("i", "p"), labor = el("i", "l");
  parts.style.width = percent(cost.parts, scale); labor.style.width = percent(cost.labor, scale);
  bar.append(parts, labor);
  return bar;
}
const costKey = (kind, text) => {
  const item = el("span", "material-cost-key");
  item.append(el("i", kind === "labor" ? "cost-key l" : "cost-key"), text);
  return item;
};

export function mountMaterialPanel(workspace, { file = null, material = null } = {}) {
  const panel = el("aside", "material-panel");
  panel.setAttribute("aria-label", "Material explorer");
  workspace.append(panel);
  const wrapper = workspace.querySelector(".cad-wrapper");
  const mobile = matchMedia("(max-width: 700px), (hover: none) and (pointer: coarse)");
  const toggle = wrapper ? el("button", "materials-toggle", "Materials") : null;
  function setOpen(open) {
    workspace.classList.toggle("materials-open", open);
    toggle?.setAttribute("aria-expanded", String(open));
  }
  if (toggle) {
    toggle.type = "button";
    toggle.addEventListener("click", () => setOpen(!workspace.classList.contains("materials-open")));
    workspace.querySelector(".cad-header-actions").append(toggle);
    setOpen(false);
  }
  const closeOnMobile = () => { if (mobile.matches) setOpen(false); };
  mobile.addEventListener("change", closeOnMobile);
  const drawingView = wrapper ? mountMaterialDrawing(wrapper, { onShowDrawing: closeOnMobile }) : null;
  let root = material || materialForFile(state.materialCatalog, file)?.id;
  let selected = root, selectedPath = [], tab = null;
  let selectedBody = null;
  let sortByCost = false;
  const expanded = new Set();
  let lastFile = file;
  const scroll = el("div", "material-panel-scroll");
  const headHost = el("div", "material-head-host"), tabsHost = el("div", "material-tabs-host");
  const search = makeMaterialSearch({ compact: true });
  panel.append(search, headHost, tabsHost, scroll);
  let disposed = false;
  // A selection made while its model is still loading waits here for STEP_MOUNTED.
  let pending = null;
  let status = "";
  function contextPath() {
    const parent = materialForFile(state.materialCatalog, lastFile);
    return parent && parent.id !== root ? explodeBom(state.materialCatalog, parent.id, options()).find((r) => r.material.id === root)?.path || [] : [];
  }
  const bindingsFor = (path, names) => occurrenceBodies(state.materialCatalog, [...contextPath(), ...path], names, options());

  // THE PANEL'S SELECTION IS THE MODEL'S. What the model picks out: the selected BOM item, a
  // related material's bodies, a picked body with no record, or this material where it stands
  // in the larger model it was opened in. The model's own material picks nothing out, so the
  // model opens whole and unfaded.
  function hasSubject() {
    return Boolean(selectedBody || selectedPath.length || selected !== root || contextPath().length);
  }
  function subjectNames(names) {
    if (selectedBody) return [...names].filter((name) => standsIn(name, selectedBody));
    if (selectedPath.length) return bindingsFor(selectedPath, names);
    if (selected !== root) {
      const relation = materialIndex(state.materialCatalog).get(root)?.relations?.find((r) => r.material === selected && r.bodies?.length);
      return relation ? [...names].filter((name) => relation.bodies.some((body) => matchesBody(name, body))) : [];
    }
    return occurrenceBodies(state.materialCatalog, contextPath(), names, options());
  }

  // Bring the model into line with the panel. `fly` frames a new selection, or flies back out
  // to the view from before one that ended; a pick made in the model keeps the camera where
  // the reader has it.
  function show({ fly = true } = {}) {
    if (disposed || !lastFile) return;
    if (state.mountedDetail?.file !== lastFile) {
      pending = { fly };
      setStatus(hasSubject() ? "The model is loading." : "");
      return;
    }
    pending = null;
    if (!hasSubject()) {
      setStatus("");
      if (fly) leaveHighlight({ owner: "materials" });
      else clearHighlight({ owner: "materials" });
      return;
    }
    const names = subjectNames(scenePartNames());
    highlightParts(names, {
      owner: "materials", onRelease: released, fly,
      onDraw: (drawn) => setStatus(!names.length ? "This material has no drawn geometry in the current model."
        : drawn.shown ? "All visible occurrences highlighted in this model."
        : drawn.hidden ? "Hidden in this view." : ""),
    });
  }

  function setStatus(text) {
    status = text;
    let note = panel.querySelector(".material-selection-note");
    if (!text) { note?.remove(); return; }
    const tree = tab === "bom" && scroll.querySelector(".bom-tree");
    if (!note && tree) {
      note = el("p", "material-selection-note"); note.setAttribute("role", "status");
      tree.parentElement.prepend(note);
    }
    if (note) note.textContent = text;
  }

  // The material this panel is open on. A material shown inside a larger model gives way to
  // that model's own; the URL follows, so a reload opens what is shown.
  function reroot(id) {
    const open = workspace.classList.contains("materials-open");
    history.replaceState(history.state, "", "#" + materialHash(id, { panel: open ? "materials" : null }));
    root = id; selected = id; selectedPath = []; selectedBody = null; expanded.clear(); tab = null;
  }

  function setRoot(id) {
    clearComponentSelection();
    root = id; selected = id; selectedPath = []; selectedBody = null; expanded.clear(); tab = null;
    render();
    show();
  }

  // `fromModel`: the reader picked it in the model, so the camera stays and the picker keeps
  // its own mark on the body clicked.
  function select(id, path = [], { fromModel = false } = {}) {
    if (!fromModel) clearComponentSelection();
    selectedBody = null;
    selected = id; selectedPath = path;
    render();
    scroll.querySelector(".bom-row.selected")?.scrollIntoView({ block: "nearest" });
    show({ fly: !fromModel });
  }

  // One level up from the selection: the BOM item holding it, then the material this panel is
  // open on, then — for a material shown inside a larger model — that model's own material.
  function parentOfSelection() {
    const index = materialIndex(state.materialCatalog);
    if (selectedPath.length > 1) {
      const path = selectedPath.slice(0, -1);
      const material = index.get(path.at(-1).material);
      return material ? { material, path } : null;
    }
    if (selectedBody || selected !== root) return index.has(root) ? { material: index.get(root), path: [] } : null;
    const model = contextPath().length ? materialForFile(state.materialCatalog, lastFile) : null;
    return model ? { material: model, path: [], reroot: true } : null;
  }
  function up() {
    const parent = parentOfSelection();
    if (!parent) return;
    if (parent.reroot) reroot(parent.material.id);
    select(parent.material.id, parent.path);
  }

  // Let go of the selection altogether: back to the model's own material with nothing picked
  // out, flying back to the view from before it unless the reader let go in the model.
  // Answers whether there was a selection to let go of.
  function leave({ fromModel = false } = {}) {
    const marked = !fromModel && clearComponentSelection();
    if (!hasSubject()) return marked;
    const model = contextPath().length ? materialForFile(state.materialCatalog, lastFile) : null;
    if (model) reroot(model.id);
    selectedBody = null; selected = root; selectedPath = [];
    render();
    show({ fly: !fromModel });
    return true;
  }

  // Another surface took the model's selection, or it was cleared from outside (Reset view,
  // the checks): the panel lets go of its own without touching the model.
  function released() {
    if (disposed || !hasSubject()) return;
    clearComponentSelection();
    const model = contextPath().length ? materialForFile(state.materialCatalog, lastFile) : null;
    if (model) reroot(model.id);
    selectedBody = null; selected = root; selectedPath = []; status = "";
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
    const identity = el("div", "material-identity");
    const parent = parentOfSelection();
    if (parent) {
      const back = el("button", "material-context", "← " + parent.material.description);
      back.type = "button"; back.addEventListener("click", up); head.append(back);
    }
    identity.append(el("span", "material-eyebrow", current ? `${current.id} · ${current.kind}` : selectedBody ? "Component in assembly" : "CAD model"));
    identity.append(el("h2", "", current?.description || (selectedBody || stepLabel(lastFile)).replace(/[-_]/g, " ") || "Material explorer"));
    head.append(identity);
    if (selectedBody) {
      const context = rootMaterial?.bom?.context?.find(item => item.bodies?.some(body => matchesBody(selectedBody, body)));
      identity.append(el("p", "material-meta", context?.description || "No material record linked to this component."));
      const open = el("button", "", "Open component"); open.type = "button";
      open.addEventListener("click", async () => {
        const { drillToComponent } = await import("./step-nav.js");
        drillToComponent(componentLocation(lastFile, selectedBody), selectedBody);
      });
      actions.append(open);
    }
    if (current?.manufacturer_number) identity.append(el("p", "material-meta", "Manufacturer part: " + current.manufacturer_number));
    const costed = costedIds(), memo = new Map();
    const costOf = (id) => rollupCost(state.materialCatalog, id, options(), memo);
    const costedRoot = Boolean(rootMaterial && costed.has(rootMaterial.id));
    const costedCurrent = Boolean(current && costed.has(current.id));
    if (selectedPath.length) {
      const row = explodeBom(state.materialCatalog, root, options()).find((r) => pathKey(r.path) === pathKey(selectedPath));
      const cost = costedCurrent && row?.quantity != null && costOf(current.id);
      if (row) identity.append(el("p", "material-meta", `${quantity(row.quantity, row.item.unit)} in ${rootMaterial.description}` +
        (cost?.costed && row.quantity !== 1 ? ` · ${money(row.quantity * cost.usd)}` : "")));
    }
    if (costedCurrent) identity.append(costSummary(current, costOf(current.id)));
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
    if (actions.childElementCount) {
      const menu = el("details", "workspace-menu material-record-menu");
      const summary = el("summary", "", "⋯"); summary.setAttribute("aria-label", "Material actions"); summary.title = "Material actions";
      actions.classList.add("workspace-menu-body"); menu.append(summary, actions); head.append(menu);
    }
    const drawings = current?.documents?.filter(doc => doc.kind === "engineering-drawing" && doc.path.endsWith(".pdf")) || [];
    const activeDrawing = drawings.find(doc => doc.path === drawingView?.drawingPath()) || drawings[0];
    drawingView?.setDrawing(activeDrawing ? { ...activeDrawing, subject: selected !== root ? current.description : null } : null);
    headHost.replaceChildren(head);
    const rows = explodeBom(state.materialCatalog, root, options());
    const used = current ? materialUses(state.materialCatalog, current.id, options()) : { assemblies: [], tools: [], equipment: [] };
    const docs = materialDocuments(state.materialCatalog, (current || rootMaterial)?.id, options());
    const counts = { bom: rows.length, cost: Number(costedCurrent), used: used.assemblies.length + used.tools.length + used.equipment.length, docs: docs.length };
    if (!tab) tab = counts.bom ? "bom" : counts.docs ? "docs" : counts.cost ? "cost" : counts.used ? "used" : "bom";
    const tabs = el("div", "material-tabs"); tabs.setAttribute("role", "tablist"); tabs.setAttribute("aria-label", "Material relationships");
    for (const [key, label] of [["bom", "BOM"], ["cost", "Cost"], ["docs", "Documents"], ["used", "Where used"]]) {
      if (!counts[key] && tab !== key) continue;
      const button = el("button", "", key === "cost" ? label : `${label} (${counts[key]})`); button.type = "button";
      if (key === "bom" && rootMaterial) button.title = `BOM items in ${rootMaterial.description}, including every nested level`;
      button.setAttribute("role", "tab"); button.setAttribute("aria-selected", String(tab === key));
      button.addEventListener("click", () => { tab = key; render(); }); tabs.append(button);
    }
    tabsHost.replaceChildren(tabs);
    const content = el("div", "material-tab-content"); content.setAttribute("role", "tabpanel");
    content.setAttribute("aria-label", { bom: "Exploded bill of materials", cost: "Cost breakdown", used: "Where used", docs: "Documents" }[tab]);
    scroll.append(content);
    if (tab === "bom") renderBom(content, rootMaterial, index, rows, costedRoot ? costOf : null);
    if (tab === "cost") renderCost(content, current, index, costedCurrent ? costOf : null);
    if (tab === "used") renderUsed(content, current, used, index);
    if (tab === "docs") renderDocs(content, docs);
    scroll.scrollTop = top;
  }

  function costSummary(material, cost) {
    const box = el("div", "material-cost");
    if (!cost.costed) {
      box.append(el("p", "material-cost-none", "No per-unit cost is recorded for this material."));
      return box;
    }
    const total = el("p", "material-cost-total");
    total.append(el("strong", "", money(cost.usd)), el("span", "", material.id === state.materialCatalog.costs.root ? "per finished unit" : "each"));
    const legend = el("p", "material-cost-legend");
    legend.append(costKey("parts", `Parts ${money(cost.parts)}`));
    if (cost.minutes) legend.append(costKey("labor", `Labor ${money(cost.labor)} · ${duration(cost.minutes)}`));
    box.append(total, costBar(cost), legend);
    return box;
  }

  // A material's own cost, one row per kind, under its contents in the tree: the
  // work of putting it together and what it consumes, so an expanded assembly
  // visibly adds up to the total on its own row.
  function ownCostRows(id, depth, pieces, path, total) {
    const own = directCost(state.materialCatalog, id);
    if (!own || !bomItems(materialIndex(state.materialCatalog).get(id), options()).length) return [];
    const groups = new Map();
    for (const element of own.elements) {
      const group = groups.get(element.kind) || { parts: 0, labor: 0, minutes: 0, items: [] };
      group.parts += element.usd || 0;
      group.labor += laborUsd(state.materialCatalog, element.minutes || 0);
      group.minutes += element.minutes || 0;
      group.items.push(element);
      groups.set(element.kind, group);
    }
    return COST_KINDS.filter((kind) => groups.has(kind.id)).map((kind) => {
      const group = groups.get(kind.id), usd = group.parts + group.labor;
      const line = el("div", `bom-row bom-own bom-own-${kind.id}`);
      line.style.setProperty("--depth", depth);
      const pick = el("button", "bom-select"); pick.type = "button";
      const detail = kind.id === "labor" ? `${group.items.length} operation${group.items.length === 1 ? "" : "s"} · ${duration(group.minutes * pieces)}`
        : group.items.map((item) => item.label).slice(0, 2).join(" · ") + (group.items.length > 2 ? ` · ${group.items.length - 2} more` : "")
          + (group.minutes ? ` · ${duration(group.minutes * pieces)}` : "");
      pick.append(el("span", "bom-description", kind.id === "labor" ? "Labor on this assembly" : kind.id === "unallocated" ? kind.label : `${kind.label} for this assembly`),
        el("span", "bom-counts", detail));
      pick.setAttribute("aria-label", `${kind.label}: ${money(usd * pieces)}, open the cost breakdown`);
      pick.addEventListener("click", () => { tab = "cost"; select(id, path); });
      const amount = el("span", "bom-amount");
      amount.append(el("span", "bom-cost", money(usd * pieces)));
      const share = el("span", "bom-share");
      share.append(costBar({ parts: group.parts * pieces, labor: group.labor * pieces }, total));
      line.append(el("span", "bom-own-mark", kind.id === "labor" ? "◷" : "·"), pick, amount, share);
      return line;
    });
  }

  function renderBom(content, rootMaterial, index, rows, costOf) {
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
      tools.append(all, collapse);
      if (costOf) {
        const order = el("div", "bom-order"); order.setAttribute("role", "group"); order.setAttribute("aria-label", "Order");
        for (const [byCost, label] of [[false, "BOM order"], [true, "By cost"]]) {
          const button = el("button", "", label); button.type = "button";
          button.setAttribute("aria-pressed", String(sortByCost === byCost));
          button.addEventListener("click", () => { sortByCost = byCost; render(); });
          order.append(button);
        }
        tools.append(order);
      }
      content.append(tools);
      const columns = el("div", "bom-columns");
      columns.append(el("span", "", "Item"), el("span", "", costOf ? "Qty · cost in this assembly" : "Qty in this assembly"));
      content.append(columns);
      const tree = el("div", "bom-tree");
      const total = costOf ? costOf(rootMaterial.id).usd : 0;
      const extended = (row) => costOf && row.quantity != null ? row.quantity * costOf(row.material.id).usd : 0;
      const children = new Map();
      for (const row of rows) {
        const parent = pathKey(row.path.slice(0, -1));
        if (!children.has(parent)) children.set(parent, []);
        children.get(parent).push(row);
      }
      const emit = (parentKey, ownerId, depth, pieces, ownerPath) => {
        const list = children.get(parentKey) || [];
        for (const row of costOf && sortByCost ? [...list].sort((a, b) => extended(b) - extended(a)) : list) {
          tree.append(bomRow(row, costOf, total, extended(row)));
          const key = pathKey(row.path);
          if (expanded.has(key)) emit(key, row.material.id, depth + 1, row.quantity ?? 1, row.path);
        }
        if (costOf) tree.append(...ownCostRows(ownerId, depth, pieces, ownerPath, total));
      };
      emit("", rootMaterial.id, 0, 1, []);
      content.append(tree);
      if (status) {
        const note = el("p", "material-selection-note", status); note.setAttribute("role", "status");
        content.prepend(note);
      }
    }
    renderRelations(content, index.get(selected) || rootMaterial, index);
  }

  function bomRow(row, costOf, total, extendedUsd) {
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
    const cost = costOf ? costOf(row.material.id) : null;
    const costText = cost ? (cost.costed ? money(extendedUsd) : "—") : null;
    pick.setAttribute("aria-label", `${row.material.description}, ${quantity(row.quantity, row.item.unit)} in this assembly${costText ? ", " + (cost.costed ? costText : "no recorded cost") : ""}${branch ? ", " + bomCountText(childCounts) : ""}`);
    pick.setAttribute("aria-pressed", String(selectedPath.length > 0 && key === pathKey(selectedPath)));
    pick.addEventListener("click", () => select(row.material.id, row.path));
    const amount = el("span", "bom-amount");
    amount.append(el("span", "bom-quantity", quantity(row.quantity, row.item.unit)));
    if (costText) {
      const value = el("span", "bom-cost" + (cost.costed ? "" : " bom-cost-none"), costText);
      if (!cost.costed) value.title = "No per-unit cost is recorded for this material";
      amount.append(value);
    }
    line.append(disclosure, pick, amount);
    if (cost?.costed) {
      const share = el("span", "bom-share");
      const pieces = row.quantity ?? 0;
      share.append(costBar({ parts: pieces * cost.parts, labor: pieces * cost.labor, usd: extendedUsd }, total));
      line.append(share);
    }
    return line;
  }

  function renderCost(content, current, index, costOf) {
    if (!current || !costOf) {
      content.append(el("p", "material-empty", "No per-unit cost is recorded for this material. Costs cover the finished unit and every part in it."));
      return;
    }
    const cost = costOf(current.id);
    const own = directCost(state.materialCatalog, current.id);
    const rate = state.materialCatalog.costs.rate;
    const section = (title, amount) => {
      const head = el("div", "material-cost-head");
      head.append(el("h3", "", title), el("span", "", amount));
      content.append(head);
    };
    const contents = bomItems(current, options()).filter((item) => typeof item.quantity === "number")
      .map((item) => ({ item, material: index.get(item.material), cost: costOf(item.material) }))
      .filter((entry) => entry.material && entry.cost.costed)
      .map((entry) => ({ ...entry, usd: entry.item.quantity * entry.cost.usd }))
      .sort((a, b) => b.usd - a.usd);
    if (contents.length) {
      const subtotal = contents.reduce((sum, entry) => sum + entry.usd, 0);
      section("Contents", money(subtotal));
      const list = el("div", "material-cost-lines");
      for (const entry of contents) {
        const line = el("button", "material-cost-line material-cost-link"); line.type = "button";
        const name = el("span", "material-cost-name");
        name.append(el("span", "", entry.material.description), el("span", "material-cost-meta", `${entry.material.id} · ${quantity(entry.item.quantity, entry.item.unit)}`));
        line.append(name, el("span", "material-cost-value", money(entry.usd)));
        line.append(costBar({ parts: entry.item.quantity * entry.cost.parts, labor: entry.item.quantity * entry.cost.labor, usd: entry.usd }, cost.usd));
        line.addEventListener("click", () => {
          const path = [...selectedPath];
          const row = explodeBom(state.materialCatalog, root, options()).find((r) =>
            r.material.id === entry.material.id && pathKey(r.path.slice(0, -1)) === pathKey(path));
          select(entry.material.id, row ? row.path : []);
        });
        list.append(line);
      }
      content.append(list);
    }
    for (const kind of COST_KINDS) {
      const elements = (own?.elements || []).filter((element) => element.kind === kind.id);
      if (!elements.length) continue;
      const minutes = elements.reduce((sum, element) => sum + (element.minutes || 0), 0);
      const usd = elements.reduce((sum, element) => sum + (element.usd || 0), 0) + laborUsd(state.materialCatalog, minutes);
      section(kind.label, minutes ? `${duration(minutes)} · ${money(usd)}` : money(usd));
      const list = el("div", "material-cost-lines");
      for (const element of elements.sort((a, b) => (b.usd || b.minutes || 0) - (a.usd || a.minutes || 0))) {
        const line = el("div", "material-cost-line");
        const name = el("span", "material-cost-name");
        const label = element.href ? el("a", "", element.label) : el("span", "", element.label);
        if (element.href) { label.href = element.href; label.target = "_blank"; label.rel = "noopener"; }
        const meta = [];
        if (element.measure) meta.push(`${+element.measure.value.toFixed(element.measure.value < 1 ? 3 : 2)} ${element.measure.unit}`);
        if (kind.id === "labor" && element.of && Math.abs(element.of - element.minutes) > 0.01) meta.push(`share of ${duration(element.of)}`);
        if (kind.id !== "labor" && kind.id !== "price" && element.of && Math.abs(element.of - element.usd) > 0.005) meta.push(`share of ${money(element.of)}`);
        if (element.section) meta.push(element.section.replace(/^\d+\.\s*/, ""));
        name.append(label);
        if (meta.length) name.append(el("span", "material-cost-meta", meta.join(" · ")));
        const run = element.run ? runText(element.run, state.materialCatalog.costs.batch) : element.lot ? `Lot: ${element.lot.label}` : "";
        if (run) name.append(el("span", "material-cost-run", run));
        const value = element.minutes ? `${duration(element.minutes)} · ${money(element.minutes * rate / 60)}` : money(element.usd);
        line.append(name, el("span", "material-cost-value", value));
        list.append(line);
      }
      content.append(list);
    }
    const batch = state.materialCatalog.costs.batch;
    content.append(el("p", "material-scope", `Per piece. Purchases, stock and supplies carry their delivered cost from the per-unit cost ledger; labor is attended time at ${money(rate, { cents: false })} an hour. Bulk stock and shared operations are divided across the pieces of a finished unit${batch ? `, and a run's setup across a batch of ${batch} machines` : ""}.`));
  }

  function renderUsed(content, current, used, index) {
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
    const ownDrawing = d => !d.inherited && d.kind === "engineering-drawing";
    for (const d of [...docs].sort((a, b) => Number(ownDrawing(b)) - Number(ownDrawing(a)))) {
      const link = el("a", "material-document" + (ownDrawing(d) ? " material-drawing-feature" : ""));
      link.href = docHref(d.path); link.target = "_blank"; link.rel = "noopener";
      if (ownDrawing(d)) {
        link.setAttribute("aria-label", "View engineering drawing: " + d.title);
        link.append(el("span", "material-document-kind", "Engineering drawing"));
        if (drawingView) link.addEventListener("click", event => {
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault(); drawingView.showDrawing({ ...d, subject: selected !== root ? d.owner : null });
        });
      }
      link.append(el("strong", "", d.title), el("span", "", ownDrawing(d) ? "Open in Drawing →" : "PDF" + (d.inherited ? " · " + d.owner : ""))); content.append(link);
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
      // Another model: its own material, nothing selected, under the camera it opened with.
      drawingView?.closeDrawing();
      selectedBody = null; pending = null; status = "";
      lastFile = mountedFile; root = materialForFile(state.materialCatalog, mountedFile)?.id; selected = root; selectedPath = []; expanded.clear(); tab = null;
      render();
      show({ fly: false });
      return;
    }
    render();
    if (state.mountedDetail?.file !== lastFile) return;
    // A selection waiting on the model frames it once the opener has set the camera.
    const waiting = pending;
    if (waiting) requestAnimationFrame(() => { if (pending === waiting) show(waiting); });
    else show({ fly: false });
  }
  // A click in the model (Component mode) selects what it hit; a click on empty space,
  // or the Component panel's ×, lets go.
  function picked(event) {
    if (event.detail.file !== state.mountedDetail?.file) return;
    if (!event.detail.name) { leave({ fromModel: true }); return; }
    const pick = { fromModel: true };
    const rootMaterial = materialIndex(state.materialCatalog).get(root);
    const names = [...scenePartNames()];
    if (rootMaterial && names.length && names.every(name => matchesBody(name, event.detail.name)) &&
        (!stepLocation(lastFile).component || !explodeBom(state.materialCatalog, root, options()).some(row => row.item.bodies?.length || row.item.prefix) || rootMaterial.models?.some(model => model.file === lastFile))) {
      select(root, [], pick); return;
    }
    const row = explodeBom(state.materialCatalog, root, options()).filter((r) =>
      bindingsFor(r.path, [event.detail.name]).length).sort((a, b) => b.depth - a.depth)[0];
    if (row) { row.path.forEach((_, i) => expanded.add(pathKey(row.path.slice(0, i + 1)))); select(row.material.id, row.path, pick); }
    else {
      const relation = materialIndex(state.materialCatalog).get(root)?.relations?.find((r) =>
        r.bodies?.some((body) => matchesBody(event.detail.name, body)));
      if (relation) select(relation.material, [], pick);
      else {
        const parent = materialForFile(state.materialCatalog, lastFile);
        const outside = parent && occurrenceForBody(state.materialCatalog, parent.id, event.detail.name, options());
        if (outside) {
          reroot(parent.id);
          outside.path.forEach((_, i) => expanded.add(pathKey(outside.path.slice(0, i + 1))));
          select(outside.material.id, outside.path, pick);
        } else {
          selected = null; selectedPath = []; selectedBody = event.detail.name;
          render();
          show({ fly: false });
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
    tab = requestedTab === "bom" ? "bom" : null;
    setOpen(!mobile.matches && (panel === "materials" || requestedTab === "bom"));
    render();
  }
  const handle = { select, setRoot, sync, applyRoute, leave, closeDrawing: () => drawingView?.closeDrawing(), dispose: () => {
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
