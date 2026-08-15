// The CAD modal's bottom-left rail and the three control shapes it holds.
// cad-detail.js builds the rail on open and fills the groups it can fill then;
// scorecard-3d.js reaches the chip row later, once the sidecar it fetched says
// the model carries ports or shape boxes.
//
// Each control here answers `read()` for its own state, so a rail rebuilt for a
// second file shows what that file's tools are actually set to rather than what
// the last one was.

// The rail itself. Controls go in in reading order, top of the column first.
export function makeToolRail() {
  const rail = document.createElement("div");
  rail.className = "tool-rail";
  return rail;
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

// The row of independent switches. `slot` names it for the modules that append
// into it after the rail is already on screen.
export function makeChipRow(slot) {
  const row = document.createElement("div");
  row.className = "tool-chips";
  row.dataset.slot = slot;
  return row;
}

export function chipRow(wrapper, slot) {
  return wrapper ? wrapper.querySelector(`.tool-rail .tool-chips[data-slot="${slot}"]`) : null;
}

// One switch. `read` and `write` are the module's own state accessors, so the
// chip carries no copy of what it is showing.
export function makeToolChip({ className, label, count = null, title, read, write }) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tool-chip" + (className ? " " + className : "");
  if (title) btn.title = title;

  const text = document.createElement("span");
  text.textContent = label;
  btn.appendChild(text);
  if (count != null) {
    const badge = document.createElement("span");
    badge.className = "tool-chip-count";
    badge.textContent = String(count);
    btn.appendChild(badge);
  }

  function refresh() { btn.setAttribute("aria-pressed", read() ? "true" : "false"); }
  btn.addEventListener("click", () => { write(!read()); refresh(); });
  refresh();
  btn.refresh = refresh;
  return btn;
}

// The pick-one control. `options` is `[{id, label, className, title}]`; `sync`
// takes the id that is live now, which lets whatever changed the mode elsewhere
// bring the control with it.
export function makeToolSeg(options, onSelect) {
  const seg = document.createElement("div");
  seg.className = "tool-seg";
  seg.setAttribute("role", "radiogroup");
  for (const o of options) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tool-seg-btn" + (o.className ? " " + o.className : "");
    btn.dataset.mode = o.id;
    btn.textContent = o.label;
    btn.setAttribute("role", "radio");
    if (o.title) btn.title = o.title;
    btn.addEventListener("click", () => onSelect(o.id));
    seg.appendChild(btn);
  }
  seg.sync = (active) => {
    for (const btn of seg.querySelectorAll(".tool-seg-btn")) {
      const on = btn.dataset.mode === active;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-checked", on ? "true" : "false");
    }
  };
  return seg;
}
