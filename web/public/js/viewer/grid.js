// Card grid for the four viewer pages. Path drives which section renders. Each
// card lazy-loads its thumbnail via IntersectionObserver and opens its detail
// surface (CAD modal or Mermaid modal) on click. /drawings is the exception —
// its cards are documents, which are files rather than things this page draws,
// so they are anchors with a committed cover and nothing to mount.
//
// /3d's parts stand in the machine's two units — contracts/parts-tree.js states
// the tree, parts.js renders it, and everything below the two is reached by
// opening one of them. The other three pages group by a path segment.

import { state } from "./state.js";
// Card-click openers come from detail-shims.js so opening a part after a code
// edit runs fresh code; thumbnail renderers stay from the modules (static).
import { openMmdDetail, openPcbDetail } from "./detail-shims.js";
import { buildPartsSection } from "./parts.js";
import { renderMmdThumbnail } from "./mermaid.js";
import { windowContent, markupThumb, imageThumb } from "./lazy.js";
import { renderPcbThumbnail } from "./pcb.js";
import { renderThumbnail, forgetThumbnail } from "./step.js";
import { renderDxfThumbnail } from "./dxf.js";
import { renderGlbThumbnail } from "./glb.js";

// A CARD DRAWS THE MODEL IT OPENS. `renderThumbnail` answers off the same mesh
// payload `loadStepFile` does and falls back to the same STEP, so the picture on
// the card and the model behind it are one read of one file. A part cannot look
// like one thing on the grid and another in the modal, and nothing has to be
// regenerated to keep the two alike.
//
// AND IT IS DRAWN AT THE SIZE IT IS SHOWN. The two cards take half the page each,
// so a fixed square meets them stretched — softer still on a dense display. The
// render takes the card's own width in device pixels: floored, so a card measured
// before layout still gets a picture, and capped, so a wide window does not ask
// for detail nobody can see.
const THUMB_MIN = 400;
const THUMB_MAX = 1200;

function thumbSize(card) {
  const css = card.clientWidth || THUMB_MIN;
  const dpr = window.devicePixelRatio || 1;
  return Math.max(THUMB_MIN, Math.min(THUMB_MAX, Math.round(css * dpr)));
}

// `bust` drops the cached picture, so a live reload redraws from the fresh model.
export function paintStepThumb(card, { bust = false } = {}) {
  const img = card.querySelector("img");
  if (!img) return;
  const file = card.dataset.file;
  if (bust) forgetThumbnail(file);
  renderThumbnail(file, thumbSize(card)).then((url) => { if (url) img.src = url; });
}

function shortName(file, ext = ".step") {
  const parts = file.split("/");
  const name = parts.pop().replace(ext, "");
  const dir = parts.join("/");
  return { name, dir };
}

// Subsystem grouping for the charts grid. Files under
// printed-parts/<subsystem>/... or cut-parts/<subsystem>/... bucket by
// <subsystem>; anything else buckets by its top-level path segment
// (charts live in topology/ and wiring/, so those are their groups).
// Categories sort alphabetically. Within a group the card's `dir` label
// drops the redundant subsystem prefix so the leaf folder reads cleanly
// under the subheader.
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

function titleCaseCategory(s) {
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
      const dir = partPath ? `<span class="dir">${partPath}</span>` : "";
      card.innerHTML = `${thumbnailHtml(file)}<div class="label">${dir}<span class="name-row"><span class="name">${name}</span></span></div>`;
      card.addEventListener("click", () => onClick(file));
      state.gridEl.appendChild(card);
    }
  }
}

// Documents — the PDFs this site hands over whole (/api/documents,
// web/contracts/documents.js). One card each: the cover, the title, the page
// and byte count, and an href that opens the PDF in a tab.
//
// The cover is a committed PNG beside the PDF, served by the same `/thumbs/`
// route every other picture under hardware/ comes through — no thumbnail to
// render, nothing to mount lazily.
function readableBytes(n) {
  return n >= 1024 * 1024 ? `${(n / (1024 * 1024)).toFixed(1)} MB` : `${Math.round(n / 1024)} KB`;
}

function buildDocumentsSection() {
  const header = document.createElement("div");
  header.className = "section-header";
  header.textContent = "Documents";
  state.gridEl.appendChild(header);

  if (!state.documents || state.documents.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No documents yet.";
    state.gridEl.appendChild(empty);
    return;
  }

  const shelf = document.createElement("div");
  shelf.className = "doc-shelf";
  state.gridEl.appendChild(shelf);

  for (const doc of state.documents) {
    // An anchor, not a click handler: a document is a file at a URL, so
    // middle-click, cmd-click and "copy link" all mean what they look like.
    const el = document.createElement("a");
    el.className = "card card-doc";
    el.href = `/docs/${doc.path}`;
    el.target = "_blank";
    el.rel = "noopener";
    // The cover's own pixel size, off the sidecar, so the card reserves its box
    // before the picture lands and the shelf does not jump under the reader.
    const size = doc.coverSize ? ` width="${doc.coverSize[0]}" height="${doc.coverSize[1]}"` : "";
    const cover = doc.cover
      ? `<img class="doc-cover" src="/thumbs/${doc.cover}" alt="${doc.title} cover"${size}>`
      : `<div class="doc-cover placeholder">no cover</div>`;
    const scale = doc.pages ? `${doc.pages} pages · ${readableBytes(doc.bytes)}` : readableBytes(doc.bytes);
    el.innerHTML = cover +
      `<div class="label"><span class="name-row"><span class="name">${doc.title}</span></span>` +
      `<span class="dir">${doc.subtitle || ""}</span><span class="doc-scale">${scale}</span></div>`;
    shelf.appendChild(el);
  }
}

// One viewer page area at a time. The path determines which section the
// grid renders.
export function currentSection() {
  const tail = location.pathname.replace(/\/$/, "");
  if (tail === "/charts") return "charts";
  if (tail === "/drawings") return "drawings";
  if (tail === "/pcb") return "pcb";
  return "parts";
}

export function buildGrid() {
  state.gridEl.innerHTML = "";
  const section = currentSection();

  if (section === "parts") {
    // parts.js does the whole build — the seating, the branches, the cards —
    // and leaves the `.card[data-type][data-file]` shells the window below and
    // live.js select on. STEP, DXF and GLB stand together in it, each under the
    // assembly it is a part of.
    if (!state.allFiles.length && !state.dxfFiles.length && !state.glbFiles.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No parts yet.";
      state.gridEl.appendChild(empty);
    } else {
      buildPartsSection(state.gridEl, {
        steps: state.allFiles, dxfs: state.dxfFiles, glbs: state.glbFiles,
      });
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

  if (section === "drawings") {
    buildDocumentsSection();
  }

  if (section === "pcb") {
    // PCB boards: one card per board, thumbnail is the Top copper view. The
    // card opens a modal with the Top / Bottom / Overlay toggle (pcb.js). The
    // dir subline carries the board's folder (minus the leading pcb/).
    const pcbThumb = (source) => `<div class="pcb-thumb" data-file="${source}"><div class="placeholder">loading...</div></div>`;
    const header = document.createElement("div");
    header.className = "section-header";
    header.textContent = "Boards";
    state.gridEl.appendChild(header);
    if (!state.pcbBoards || state.pcbBoards.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No boards yet.";
      state.gridEl.appendChild(empty);
    } else {
      for (const board of state.pcbBoards) {
        const dirLabel = board.dir.replace(/^pcb\//, "");
        const card = document.createElement("div");
        card.className = "card";
        card.dataset.file = board.source;
        card.dataset.type = "pcb";
        // A board whose directory is its own name says it once.
        const dir = dirLabel && dirLabel !== board.name ? `<span class="dir">${dirLabel}</span>` : "";
        card.innerHTML = `${pcbThumb(board.source)}<div class="label">${dir}<span class="name-row"><span class="name">${board.name}</span></span></div>`;
        card.addEventListener("click", () => openPcbDetail(board.source));
        state.gridEl.appendChild(card);
      }
    }
  }

  // Windowed thumbnail content. Every kind mounts as it nears the viewport and
  // releases once it's well past — see lazy.js for why this windows content
  // rather than rows, and for the measurements that motivated it. Each kind
  // supplies only what "mount" and "release" mean for its own thumbnail; the
  // scroll bookkeeping is shared.
  //
  // The handle is kept on `state` so the next buildGrid disconnects these
  // observers before the cards they watch are thrown away.
  state.gridWindow?.disconnect();

  const kinds = {
    // STEP: the model itself, drawn offscreen. Releasing the src is what frees
    // the decoded bitmap; the picture stays in `state.thumbnailCache`, so coming
    // back re-reads that rather than the model.
    step: {
      mount: (card) => paintStepThumb(card),
      unmount: (card) => card.querySelector("img")?.removeAttribute("src"),
    },
    dxf: imageThumb(renderDxfThumbnail),
    glb: imageThumb(renderGlbThumbnail),
    mmd: markupThumb({ hostSelector: ".mmd-thumb", render: renderMmdThumbnail }),
    pcb: markupThumb({ hostSelector: ".pcb-thumb", render: renderPcbThumbnail }),
  };

  const windows = [];
  for (const [type, { mount, unmount }] of Object.entries(kinds)) {
    const elements = state.gridEl.querySelectorAll(`.card[data-type="${type}"]`);
    if (elements.length === 0) continue;
    windows.push(windowContent({ elements, mount, unmount }));
  }
  state.gridWindow = { disconnect: () => windows.forEach((w) => w.disconnect()) };
}
