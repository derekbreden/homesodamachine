// The /3d grid: the machine's three assemblies, and the shelf of what none of
// them places.
//
// contracts/parts-tree.js states the tree — imported here over the URL the server
// serves it at and by path on the Node side, one file either way. Each assembly is
// one card, and the card opens the assembly in the detail modal; a part inside it
// is reached from there, by arming Select → Component and taking the file the
// panel offers. The shelf renders as a <details> holding its own grid, and whether
// it stands open is in localStorage.
//
// A CARD IS A PART, NOT A FILE. `seatParts` folds the `.step` and the `.dxf` of
// one cut part into a single part; the card opens the richer of them and carries
// a chip for the other. `data-file` and `data-type` are what grid.js's lazy
// window and live.js's repaint select on.
//
// THIS RUNS AHEAD OF EVERY CAD RENDER IN THE REPOSITORY. `main.js` calls
// `applyInitialRoute` after `buildGrid`, and the render family in tools/render/
// opens `/3d?file=…` and waits on `__hsm.mountedStepFile` — so a throw here is
// not a broken page, it is a scene that never mounts. contracts/parts-tree.js
// names them.

import { openDetail, openDxfDetail, openGlbDetail } from "./cad-detail.js";
import { seatParts } from "/contracts/parts-tree.js";
import { iconSvg } from "/contracts/icons.js";

const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail };

// Whether the shelf stands open. Absent: closed — the page opens as the three
// assemblies, and the shelf is opened by asking for it.
const OPEN_KEY = "parts-open";

function readOpen() {
  try {
    const raw = localStorage.getItem(OPEN_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* unreadable or unparseable: fall through to the default */ }
  return null;
}

function writeOpen(el) {
  const open = [...el.querySelectorAll("details.branch[open]")].map((d) => d.dataset.branch);
  try { localStorage.setItem(OPEN_KEY, JSON.stringify(open)); } catch {}
}

// Segments that name where a build put a file rather than what the part is:
// `pcb/pcba/out/pcba.glb` is a pcba, `assembly/scenes/glb/cold-core.glb` a scene.
const BUILD_DIRS = new Set(["out", "glb"]);

function dirLabel(part) {
  const segs = part.dir.split("/").filter((s) => !BUILD_DIRS.has(s));
  const leaf = segs[segs.length - 1] || "";
  // `drip-pan/drip-pan` reads as one name, not two.
  return leaf === part.name ? "" : leaf;
}

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// The representations that get a chip: every one the card does not open, plus a
// primary that is not a STEP. A STEP-only part carries none.
function chipsFor(part) {
  return part.kinds.filter((k) => k !== part.primary || k.type !== "step");
}

function thumbHtml(part) {
  return part.primary.type === "step"
    ? `<img loading="lazy" alt="">`
    : `<div class="placeholder" data-file="${esc(part.primary.file)}">loading...</div>`;
}

function renderPart(part) {
  const card = document.createElement("div");
  card.className = "card";
  card.dataset.file = part.primary.file;
  card.dataset.type = part.primary.type;

  const dir = dirLabel(part);
  const chips = chipsFor(part)
    .map((k) => `<button class="kind" type="button" data-open="${esc(k.file)}" ` +
                `data-kind="${k.type}">${k.type}</button>`)
    .join("");
  card.innerHTML = thumbHtml(part) +
    `<div class="label">${dir ? `<span class="dir">${esc(dir)}</span>` : ""}` +
    `<span class="name-row"><span class="name">${esc(part.name)}</span>` +
    `${chips ? `<span class="kinds">${chips}</span>` : ""}</span></div>`;

  card.addEventListener("click", (e) => {
    // A chip opens its own representation; the card opens the primary.
    const chip = e.target.closest(".kind");
    if (chip) {
      e.stopPropagation();
      OPENERS[chip.dataset.kind](chip.dataset.open);
      return;
    }
    OPENERS[part.primary.type](part.primary.file);
  });
  return card;
}

// An assembly: its render, the name the machine's docs call it by, and what it
// holds. The click opens the assembly, which is where its own parts are reached.
function renderAssembly(assembly) {
  const card = document.createElement("div");
  card.className = "card card-assembly";
  card.dataset.file = assembly.model.primary.file;
  card.dataset.type = assembly.model.primary.type;
  card.innerHTML = thumbHtml(assembly.model) +
    `<div class="label"><span class="name-row">` +
    `<span class="name">${esc(assembly.label)}</span></span>` +
    `<span class="assembly-note">${esc(assembly.note)}</span></div>`;
  card.addEventListener("click", () => {
    OPENERS[assembly.model.primary.type](assembly.model.primary.file);
  });
  return card;
}

function renderShelf({ id, label, note, parts }, isOpen) {
  const details = document.createElement("details");
  details.className = "branch";
  details.dataset.branch = id;
  details.open = isOpen;
  // On the branch, not on the grid: buildGrid runs again on every live reload
  // and throws these away, so the listener goes with the element it watches.
  details.addEventListener("toggle", () => writeOpen(details.parentNode));

  const summary = document.createElement("summary");
  summary.className = "branch-head";
  summary.innerHTML = `<div class="branch-text">` +
    `<span class="branch-title">${iconSvg("chevron", "branch-caret")}${esc(label)}</span>` +
    `<span class="branch-count">${parts.length} part${parts.length === 1 ? "" : "s"}</span>` +
    `<span class="branch-note">${esc(note)}</span></div>`;
  details.appendChild(summary);

  const body = document.createElement("div");
  body.className = "branch-body";
  for (const part of parts) body.appendChild(renderPart(part));
  details.appendChild(body);

  return details;
}

// Open the shelf when a deep link names a file standing on it, so it is behind
// the modal that link opened.
function revealLinked(gridEl) {
  const file = new URLSearchParams(location.search).get("file") ||
    (location.hash ? decodeURIComponent(location.hash.slice(1)).replace(/^\w+:/, "") : "");
  if (!file) return;
  const card = gridEl.querySelector(`.card[data-file="${CSS.escape(file)}"]`);
  card?.closest("details.branch")?.setAttribute("open", "");
}

export function buildPartsSection(gridEl, { steps, dxfs, glbs }) {
  const tree = seatParts({ steps, dxfs, glbs });

  // The directories holding files nothing claimed.
  if (tree.unseated.length) {
    const warn = document.createElement("div");
    warn.className = "grid-warn";
    warn.innerHTML = `<b>Not seated:</b><ul>` +
      tree.unseated.map((d) => `<li><code>${esc(d)}</code> stands in no assembly — ` +
        `place it in <code>contracts/parts-tree.js</code></li>`).join("") + `</ul>`;
    gridEl.appendChild(warn);
  }

  const row = document.createElement("div");
  row.className = "assembly-row";
  for (const assembly of tree.assemblies) {
    if (assembly.model) row.appendChild(renderAssembly(assembly));
  }
  gridEl.appendChild(row);

  if (tree.loose.parts.length) {
    const open = readOpen();
    gridEl.appendChild(renderShelf(tree.loose, open ? open.has(tree.loose.id) : false));
  }
  revealLinked(gridEl);
}
