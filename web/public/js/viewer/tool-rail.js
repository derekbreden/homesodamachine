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
