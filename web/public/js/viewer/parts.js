// The /3d grid: the machine's three assemblies, drilled down.
//
// Which assembly a directory stands in, and in what order a branch reads, is
// contracts/parts-tree.js — imported here over the URL the server serves it at
// and by path on the Node side, one file either way. A branch renders as a
// <details> holding its own grid, and the set left open is in localStorage.
//
// A CARD IS A PART, NOT A FILE. `seatParts` folds the `.step` and the `.dxf` of
// one cut part into a single part; the card opens the richer of them and carries
// a chip for the other. `data-file` and `data-type` are what grid.js's lazy
// window and live.js's repaint select on.

import { openDetail, openDxfDetail, openGlbDetail } from "./cad-detail.js";
import { seatParts } from "/contracts/parts-tree.js";

const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail };

// Which branches stand open. Absent: the three assemblies open, the reference
// shelf shut.
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

function renderPart(part, { hero = false } = {}) {
  const card = document.createElement("div");
  card.className = hero ? "card card-hero" : "card";
  card.dataset.file = part.primary.file;
  card.dataset.type = part.primary.type;

  const dir = dirLabel(part);
  const chips = chipsFor(part)
    .map((k) => `<button class="kind" type="button" data-open="${esc(k.file)}" ` +
                `data-kind="${k.type}">${k.type}</button>`)
    .join("");
  card.innerHTML = thumbHtml(part) +
    `<div class="label">${dir ? `<span class="dir">${esc(dir)}</span>` : ""}` +
    `${esc(part.name)}${chips ? `<span class="kinds">${chips}</span>` : ""}</div>`;

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

function renderGroup(group, body) {
  const head = document.createElement("div");
  head.className = "subsection-header";
  head.innerHTML = `${esc(group.label)}` +
    (group.note ? `<span class="group-note">${esc(group.note)}</span>` : "");
  body.appendChild(head);

  if (!group.parts.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state empty-group";
    empty.textContent = "Nothing exported yet.";
    body.appendChild(empty);
    return;
  }
  for (const part of group.parts) body.appendChild(renderPart(part));
}

function renderBranch({ id, label, note, hero, groups, parts }, isOpen) {
  const details = document.createElement("details");
  details.className = "branch";
  details.dataset.branch = id;
  details.open = isOpen;
  // On the branch, not on the grid: buildGrid runs again on every live reload
  // and throws these away, so the listener goes with the element it watches.
  details.addEventListener("toggle", () => writeOpen(details.parentNode));

  const count = (groups || []).reduce((n, g) => n + g.parts.length, 0) +
    (parts ? parts.length : 0) + (hero ? 1 : 0);

  const summary = document.createElement("summary");
  summary.className = "branch-head";
  summary.innerHTML = `<div class="branch-text">` +
    `<span class="branch-title">${esc(label)}</span>` +
    `<span class="branch-count">${count} part${count === 1 ? "" : "s"}</span>` +
    `<span class="branch-note">${esc(note)}</span></div>`;

  // The branch's assembly rides in the header, so a collapsed branch still shows
  // what it is. A click on it opens the model instead of toggling the branch.
  if (hero) {
    const card = renderPart(hero, { hero: true });
    card.addEventListener("click", (e) => e.preventDefault());
    summary.appendChild(card);
  }
  details.appendChild(summary);

  const body = document.createElement("div");
  body.className = "branch-body";
  details.appendChild(body);

  for (const group of groups || []) renderGroup(group, body);
  for (const part of parts || []) body.appendChild(renderPart(part));

  return details;
}

// Open the branch holding the file a deep link names, so it stands behind the
// modal that link opened.
function revealLinked(gridEl) {
  const file = new URLSearchParams(location.search).get("file") ||
    (location.hash ? decodeURIComponent(location.hash.slice(1)).replace(/^\w+:/, "") : "");
  if (!file) return;
  const card = gridEl.querySelector(`.card[data-file="${CSS.escape(file)}"]`);
  card?.closest("details.branch")?.setAttribute("open", "");
}

export function buildPartsSection(gridEl, { steps, dxfs, glbs }) {
  const tree = seatParts({ steps, dxfs, glbs });

  // The directories holding files no group claimed.
  if (tree.unseated.length) {
    const warn = document.createElement("div");
    warn.className = "grid-warn";
    warn.innerHTML = `<b>Not seated:</b><ul>` +
      tree.unseated.map((d) => `<li><code>${esc(d)}</code> stands in no assembly — ` +
        `give it a group in <code>contracts/parts-tree.js</code></li>`).join("") + `</ul>`;
    gridEl.appendChild(warn);
  }

  const open = readOpen();
  const isOpen = (id) => (open ? open.has(id) : id !== tree.reference.id);
  for (const branch of tree.branches) {
    gridEl.appendChild(renderBranch(branch, isOpen(branch.id)));
  }
  gridEl.appendChild(renderBranch(tree.reference, isOpen(tree.reference.id)));
  revealLinked(gridEl);
}
