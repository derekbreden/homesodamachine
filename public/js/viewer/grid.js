// Card grid for both /3d (parts) and /charts (mermaid). Path drives
// which section renders. Each card lazy-loads its thumbnail via
// IntersectionObserver and opens its detail surface (CAD modal or
// Mermaid modal) on click.

import { state } from "./state.js";
import { openDetail, openDxfDetail } from "./cad-detail.js";
import { openMmdDetail, renderMmdThumbnail } from "./mermaid.js";
import { renderThumbnail } from "./step.js";
import { renderDxfThumbnail } from "./dxf.js";

function shortName(file, ext = ".step") {
  const parts = file.split("/");
  const name = parts.pop().replace(ext, "");
  const dir = parts.join("/");
  return { name, dir };
}

// Subsystem grouping for the Prints and Cuts grids. Files under
// printed-parts/<subsystem>/... or cut-parts/<subsystem>/... bucket by
// <subsystem>; anything else buckets by its top-level path segment
// (e.g. harvested/ STEPs land in their own group). Categories sort
// alphabetically. Within a group the card's `dir` label drops the
// redundant subsystem prefix so the leaf folder reads cleanly under
// the subheader.
function categoryAndPartPath(file) {
  const parts = file.split("/");
  const filename = parts.pop();
  let category, partPath;
  if ((parts[0] === "printed-parts" || parts[0] === "cut-parts") && parts.length > 1) {
    category = parts[1];
    partPath = parts.slice(2).join("/");
  } else {
    category = parts[0] || "";
    partPath = parts.slice(1).join("/");
  }
  return { category, partPath, filename };
}

// Override map for category labels whose folder name reads worse on the
// page than a chosen alternative. The folder stays as-is on disk; only
// the subheader text changes. Add an entry here when the auto-derived
// label is technically right but UX-wise jarring.
const CATEGORY_LABEL_OVERRIDES = {
  harvested: "Reference",
};

function titleCaseCategory(s) {
  if (CATEGORY_LABEL_OVERRIDES[s]) return CATEGORY_LABEL_OVERRIDES[s];
  return s.replace(/[-_]/g, " ")
    .split(" ")
    .map((w) => (w ? w.charAt(0).toUpperCase() + w.slice(1) : ""))
    .join(" ");
}

function groupFilesByCategory(files) {
  const groups = new Map();
  for (const f of files) {
    const { category } = categoryAndPartPath(f);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push(f);
  }
  return new Map([...groups.entries()].sort(([a], [b]) => a.localeCompare(b)));
}

// Append a sequence of [subsection-header, card, card, ...] groups to
// gridEl, one group per category returned by groupFilesByCategory.
// Caller supplies the thumbnail markup (it differs between STEP/DXF
// "loading..." placeholders and the wrapped mmd-thumb structure) plus
// the click handler.
function renderGroupedCards({ files, ext, type, thumbnailHtml, onClick }) {
  for (const [category, group] of groupFilesByCategory(files)) {
    const sub = document.createElement("div");
    sub.className = "subsection-header";
    sub.textContent = titleCaseCategory(category);
    state.gridEl.appendChild(sub);
    for (const file of group) {
      const { partPath, filename } = categoryAndPartPath(file);
      const name = filename.replace(ext, "");
      const card = document.createElement("div");
      card.className = "card";
      card.dataset.file = file;
      card.dataset.type = type;
      card.innerHTML = `${thumbnailHtml(file)}<div class="label"><span class="dir">${partPath}</span>${name}</div>`;
      card.addEventListener("click", () => onClick(file));
      state.gridEl.appendChild(card);
    }
  }
}

// One viewer page area at a time. The path determines which section the
// grid renders.
export function currentSection() {
  const tail = location.pathname.replace(/\/$/, "");
  if (tail === "/charts") return "charts";
  return "parts";
}

export function buildGrid() {
  state.gridEl.innerHTML = "";
  const section = currentSection();

  if (section === "parts") {
    // Two subsections: Prints (STEP, 3D-printable) then Cuts (DXF, laser-
    // cut sheet). Within each, cards are further grouped under subsystem
    // subheaders (Cold Core, Flavor, Faucet, ...) derived from the folder
    // structure in hardware/printed-parts/ and hardware/cut-parts/. The
    // section headers always render so the structure is explicit even
    // when a subsection is empty; the empty-state replaces the would-be
    // card grid for that subsection.
    const stepThumb = (file) => `<div class="placeholder" data-file="${file}">loading...</div>`;

    const printsHeader = document.createElement("div");
    printsHeader.className = "section-header";
    printsHeader.textContent = "Prints";
    state.gridEl.appendChild(printsHeader);
    if (state.allFiles.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No prints yet.";
      state.gridEl.appendChild(empty);
    } else {
      renderGroupedCards({ files: state.allFiles, ext: ".step", type: "step", thumbnailHtml: stepThumb, onClick: openDetail });
    }

    const cutsHeader = document.createElement("div");
    cutsHeader.className = "section-header";
    cutsHeader.textContent = "Cuts";
    state.gridEl.appendChild(cutsHeader);
    if (state.dxfFiles.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No cuts yet.";
      state.gridEl.appendChild(empty);
    } else {
      renderGroupedCards({ files: state.dxfFiles, ext: ".dxf", type: "dxf", thumbnailHtml: stepThumb, onClick: openDxfDetail });
    }
  }

  if (section === "charts") {
    // Same subsystem grouping as Prints/Cuts, applied to mermaid files.
    // Charts live in hardware/topology/ and hardware/wiring/ rather than
    // under printed-parts/cut-parts, so categoryAndPartPath buckets them
    // by their top-level segment ("topology", "wiring", ...).
    const mmdThumb = (file) => `<div class="mmd-thumb" data-file="${file}"><div class="placeholder">loading...</div></div>`;
    if (state.mmdFiles.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No charts yet.";
      state.gridEl.appendChild(empty);
    } else {
      renderGroupedCards({ files: state.mmdFiles, ext: ".mmd", type: "mmd", thumbnailHtml: mmdThumb, onClick: openMmdDetail });
    }
  }

  // Lazy-load STEP thumbnails
  const stepObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      stepObserver.unobserve(entry.target);
      const file = entry.target.dataset.file;
      renderThumbnail(file).then((url) => {
        if (!url) {
          entry.target.querySelector(".placeholder").textContent = "error";
          return;
        }
        const img = document.createElement("img");
        img.src = url;
        const placeholder = entry.target.querySelector(".placeholder");
        if (placeholder) placeholder.replaceWith(img);
      });
    }
  }, { rootMargin: "200px" });

  for (const card of state.gridEl.querySelectorAll('.card[data-type="step"]')) {
    stepObserver.observe(card);
  }

  // Lazy-load DXF thumbnails (top-down render of the line geometry).
  const dxfObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      dxfObserver.unobserve(entry.target);
      const file = entry.target.dataset.file;
      renderDxfThumbnail(file).then((url) => {
        if (!url) {
          entry.target.querySelector(".placeholder").textContent = "error";
          return;
        }
        const img = document.createElement("img");
        img.src = url;
        const placeholder = entry.target.querySelector(".placeholder");
        if (placeholder) placeholder.replaceWith(img);
      });
    }
  }, { rootMargin: "200px" });

  for (const card of state.gridEl.querySelectorAll('.card[data-type="dxf"]')) {
    dxfObserver.observe(card);
  }

  // Lazy-load Mermaid thumbnails
  const mmdObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      mmdObserver.unobserve(entry.target);
      const file = entry.target.dataset.file;
      renderMmdThumbnail(file).then((svg) => {
        const thumbEl = entry.target.querySelector(".mmd-thumb");
        if (!thumbEl) return;
        if (!svg) { thumbEl.innerHTML = `<div class="placeholder">error</div>`; return; }
        thumbEl.innerHTML = svg;
      });
    }
  }, { rootMargin: "200px" });

  for (const card of state.gridEl.querySelectorAll('.card[data-type="mmd"]')) {
    mmdObserver.observe(card);
  }
}
