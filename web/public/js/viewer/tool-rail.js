// The CAD modal's chrome: the bottom-left rail and the three control shapes it
// holds, plus the collapse the readout panels share. cad-detail.js builds the
// rail on open, with the controls the open file carries.
//
// Each control here answers `read()` for its own state, so a rail rebuilt for a
// second file shows what that file's tools are actually set to rather than what
// the last one was.

import { iconSvg } from "/contracts/icons.js";

// The glyph beside a control's label, from the table the shell nav draws from
// (contracts/icons.js). The markup is this repository's own constant, never
// anything read off the wire.
function prependIcon(el, key) {
  if (key) el.insertAdjacentHTML("afterbegin", iconSvg(key, "tool-icon"));
}

// The rail itself. Controls go in in reading order, top of the column first.
export function makeToolRail() {
  const rail = document.createElement("div");
  rail.className = "tool-rail";
  return rail;
}

// Compact views keep their tools in a disclosure; wide mouse-driven views
// keep the same controls open. The selected mode stays visible on the summary.
export function mountToolDrawer(rail) {
  const drawer = document.createElement("details");
  drawer.className = "tool-drawer";
  const summary = document.createElement("summary");
  summary.className = "tool-btn";
  const label = document.createElement("span");
  label.textContent = "Tools";
  summary.appendChild(label);
  drawer.appendChild(summary);
  const body = document.createElement("div");
  body.className = "tool-drawer-body";
  while (rail.firstChild) body.appendChild(rail.firstChild);
  drawer.appendChild(body);
  rail.appendChild(drawer);

  const compactViewport = matchMedia("(max-width: 900px), (pointer: coarse)");
  const fit = () => {
    drawer.classList.toggle("compact", compactViewport.matches);
    drawer.open = !compactViewport.matches;
  };
  compactViewport.addEventListener("change", fit);
  fit();

  let previousMode;
  const sync = () => {
    const selected = body.querySelector('.tool-seg-btn[aria-checked="true"]');
    const mode = selected?.dataset.mode || "off";
    if (mode === previousMode) return;
    previousMode = mode;
    summary.querySelector(".tool-icon")?.remove();
    const hasSelection = mode !== "off";
    summary.classList.toggle("has-selection", hasSelection);
    if (hasSelection) summary.appendChild(selected.querySelector(".tool-icon").cloneNode(true));
    else summary.insertAdjacentHTML("beforeend", iconSvg("chevron", "tool-icon"));
    const selection = selected?.querySelector(".tool-label").textContent || "Off";
    summary.title = `Viewer tools · Select: ${selection}`;
    summary.setAttribute("aria-label", hasSelection ? `Tools: ${selection} selection enabled` : "Tools");
  };
  const observer = new MutationObserver(sync);
  observer.observe(body, { subtree: true, childList: true, attributes: true, attributeFilter: ["aria-checked"] });
  sync();
  body.addEventListener("click", (e) => {
    if (e.target.closest(".tool-seg-btn, .pick-find-toggle, .tube-toggle")) {
      closeToolDrawer(rail.closest(".cad-wrapper"), !!e.target.closest(".tool-seg-btn"));
    }
  });
  return () => {
    compactViewport.removeEventListener("change", fit);
    observer.disconnect();
  };
}

export function closeToolDrawer(wrapper, focus = false) {
  const drawer = wrapper?.querySelector(".tool-drawer.compact[open]");
  if (!drawer) return false;
  drawer.open = false;
  if (focus) drawer.querySelector("summary").focus();
  return true;
}

// An action pill: a label, its glyph, and a click.
export function makeToolButton({ className, label, icon, title, onClick }) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tool-btn" + (className ? " " + className : "");
  if (title) btn.title = title;
  const text = document.createElement("span");
  text.className = "tool-label";
  text.textContent = label;
  btn.appendChild(text);
  prependIcon(btn, icon);
  btn.addEventListener("click", onClick);
  return btn;
}

// A captioned block. The caption names what the controls under it have in
// common; the block hides itself when nothing lands in `body`.
export function makeToolGroup(label, body) {
  const group = document.createElement("div");
  group.className = "tool-group";
  const caption = document.createElement("span");
  caption.className = "tool-group-label";
  caption.textContent = label;
  group.appendChild(caption);
  group.appendChild(body);
  return group;
}

// The row of independent switches.
export function makeChipRow() {
  const row = document.createElement("div");
  row.className = "tool-chips";
  return row;
}

// One switch. `read` and `write` are the module's own state accessors, so the
// chip carries no copy of what it is showing.
export function makeToolChip({ className, label, icon, title, read, write }) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tool-chip" + (className ? " " + className : "");
  if (title) btn.title = title;

  const text = document.createElement("span");
  text.className = "tool-label";
  text.textContent = label;
  btn.appendChild(text);
  prependIcon(btn, icon);

  function refresh() { btn.setAttribute("aria-pressed", read() ? "true" : "false"); }
  btn.addEventListener("click", () => { write(!read()); refresh(); });
  refresh();
  btn.refresh = refresh;
  return btn;
}

// The collapse for a readout panel (.edge-panel and the component panel that
// wears its chrome). Collapsed, the panel keeps its head — the title and the
// name of what is selected — and drops everything under it, so the reader can
// hold a selection without the panel standing over the model it names. The
// choice is per-browser, because a panel collapsed for being in the way is in
// the way again on the next load.
export function makePanelCollapse(panel, lsKey) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "edge-panel-collapse";
  // A chevron, turned by CSS off the aria-expanded this button already carries.
  prependIcon(btn, "chevron");
  let collapsed = false;
  try { collapsed = localStorage.getItem(lsKey) === "1"; } catch {}

  function apply() {
    panel.classList.toggle("collapsed", collapsed);
    btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
    btn.title = collapsed ? "Expand" : "Collapse";
  }
  btn.addEventListener("click", () => {
    collapsed = !collapsed;
    try { localStorage.setItem(lsKey, collapsed ? "1" : "0"); } catch {}
    apply();
  });
  apply();
  return btn;
}

// The pick-one control. `options` is `[{id, label, className, title}]`; `sync`
// takes the id that is live now, which lets whatever changed the mode elsewhere
// bring the control with it.
export function makeToolSeg(options, onSelect) {
  const seg = document.createElement("div");
  seg.className = "tool-seg";
  seg.setAttribute("role", "radiogroup");
  // A segment can arrive after the control is on screen — the editor's does,
  // once its API answers for the open file (pick-mode.js).
  seg.addOption = (o, onClick) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tool-seg-btn" + (o.className ? " " + o.className : "");
    btn.dataset.mode = o.id;
    const text = document.createElement("span");
    text.className = "tool-label";
    text.textContent = o.label;
    btn.appendChild(text);
    prependIcon(btn, o.icon);
    btn.setAttribute("role", "radio");
    if (o.title) btn.title = o.title;
    btn.addEventListener("click", onClick || (() => onSelect(o.id)));
    seg.appendChild(btn);
    return btn;
  };
  for (const o of options) seg.addOption(o);
  seg.sync = (active) => {
    for (const btn of seg.querySelectorAll(".tool-seg-btn")) {
      const on = btn.dataset.mode === active;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-checked", on ? "true" : "false");
    }
  };
  return seg;
}
