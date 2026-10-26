// Card grid for the four viewer pages. Path drives which section renders.
// Model and chart cards lazy-load their thumbnails and open their detail modal.
// Document cards link to PDFs and show committed covers on /drawings.
//
// /3d presents description search, the two product units and their tooling.
// The other three pages group by a path segment.

import { state } from "./state.js";
// Card-click openers come from detail-shims.js so opening a part after a code
// edit runs fresh code; thumbnail renderers stay from the modules (static).
import { openMmdDetail, openPcbDetail } from "./detail-shims.js";
import { buildPartsSection, syncFaucetCard } from "./parts.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { renderMmdThumbnail } from "./mermaid.js";
import { windowContent, markupThumb } from "./lazy.js";
import { renderPcbThumbnail } from "./pcb.js";
import { renderThumbnail, forgetThumbnail } from "./step.js";

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
//
// The card says it is drawing while it draws. Reading a model takes about as long
// as opening one does, and a card that stands empty for that long reads as a card
// with nothing in it rather than one on its way.
export function paintStepThumb(card, { bust = false } = {}) {
  const img = card.querySelector("img");
  if (!img) return;
  const file = card.dataset.file;
  const finish = state.faucetFinish;
  const drawing = (card._drawingSeq || 0) + 1;
  card._drawingSeq = drawing;
  if (bust) forgetThumbnail(file);
  card.dataset.drawing = "1";
  renderThumbnail(file, thumbSize(card), finish, "shelf").then((url) => {
    if (card._drawingSeq !== drawing || card.dataset.file !== file) return;
    if (url) img.src = url;
    delete card.dataset.drawing;
  });
}

window.addEventListener(HSM_EVENTS.FAUCET_OPTIONS, () => {
  state.gridEl?.querySelector(".material-search")?.refresh();
  for (const card of state.gridEl?.querySelectorAll(".card[data-faucet]") || []) {
    const before = `${card.dataset.file}:${card.dataset.finish}`;
    syncFaucetCard(card);
    if (before !== `${card.dataset.file}:${card.dataset.finish}`) card.dataset.faucetDirty = "1";
    // Rebuild the offscreen thumbnail when it is visible again. Finish changes
    // on a large open assembly remain a material swap with no mesh rebuild.
    if (card.dataset.faucetDirty && !state.currentCadWrapper) {
      delete card.dataset.faucetDirty;
      paintStepThumb(card);
    }
  }
});

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
// Caller supplies the thumbnail markup and the click handler.
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
      card.innerHTML = `${thumbnailHtml(file)}<div class="label card-caption">${dir}<span class="name-row"><span class="name">${name}</span></span></div>`;
      card.addEventListener("click", () => onClick(file));
      state.gridEl.appendChild(card);
    }
  }
}

// Documents — the PDFs this site hands over whole (/api/documents,
// web/contracts/documents.js). One card each: the cover, the title, the page
// and byte count, and an href that opens the in-app document reader.
//
// The cover is a committed PNG beside the PDF, served by the same `/thumbs/`
// route every other picture under hardware/ comes through — no thumbnail to
// render, nothing to mount lazily.
function readableBytes(n) {
  return n >= 1024 * 1024 ? `${(n / (1024 * 1024)).toFixed(1)} MB` : `${Math.round(n / 1024)} KB`;
}

function buildDocumentsSection() {
  const documents = state.documents || [];
  const node = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  };
  if (!documents.length) {
    state.gridEl.append(node("p", "empty-state", "No documents yet."));
    return;
  }
  const owners = new Map();
  for (const material of state.materialCatalog?.materials || []) for (const doc of material.documents || []) {
    if (doc.kind !== "engineering-drawing") continue;
    if (!owners.has(doc.path)) owners.set(doc.path, []);
    owners.get(doc.path).push(material);
  }
  const params = new URLSearchParams(location.search);
  let active = ["drawing", "guide"].includes(params.get("type")) ? params.get("type") : "all";
  const tools = node("div", "document-tools");
  const search = node("div", "material-search");
  const label = node("label", "", "Find a document");
  const input = node("input"); input.type = "search"; input.autocomplete = "off";
  input.placeholder = "Title, part number or subject…"; input.value = params.get("q") || "";
  input.setAttribute("aria-label", "Find a document");
  label.append(input); search.append(label);
  const filters = node("div", "document-filters"); filters.setAttribute("role", "group");
  filters.setAttribute("aria-label", "Document type");
  const buttons = new Map();
  for (const [kind, name] of [["all", "All"], ["drawing", "Engineering drawings"], ["guide", "Build guides"]]) {
    const button = node("button", "", name); button.type = "button";
    button.addEventListener("click", () => { active = kind; render(); });
    buttons.set(kind, { button, name }); filters.append(button);
  }
  const pickerLabel = node("label", "document-kind-picker", "Show");
  const picker = node("select", "document-kind-select"); picker.setAttribute("aria-label", "Document type");
  for (const [kind, { name }] of buttons) { const option = node("option", "", name); option.value = kind; picker.append(option); }
  picker.addEventListener("change", () => { active = picker.value; render(); });
  pickerLabel.append(picker); filters.append(pickerLabel);
  const status = node("p", "document-search-status"); status.setAttribute("role", "status");
  const searchSlot = document.getElementById("document-search-slot");
  if (searchSlot) searchSlot.replaceChildren(search); else tools.append(search);
  tools.append(filters, status);
  const shelf = node("div", "doc-shelf");
  const cards = documents.map(doc => {
    const material = owners.get(doc.path) || [], kind = material.length ? "drawing" : "guide";
    const card = node("a", "card card-doc"); card.dataset.kind = kind;
    card.href = "/read/" + doc.path.split("/").map(encodeURIComponent).join("/");
    let cover;
    if (doc.cover) {
      cover = node("img", "doc-cover"); cover.src = "/thumbs/" + doc.cover; cover.alt = ""; cover.loading = "lazy";
      if (doc.coverSize) [cover.width, cover.height] = doc.coverSize;
    } else {
      cover = node("div", "doc-cover placeholder", "PDF"); cover.setAttribute("aria-hidden", "true");
    }
    const caption = node("div", "label card-caption");
    const nameRow = node("span", "name-row"); nameRow.append(node("span", "name", doc.title));
    caption.append(node("span", "doc-kind", kind === "drawing" ? "Engineering drawing · " + material.map(m => m.id).join(", ") : "Build guide"),
      nameRow, node("span", "dir", doc.subtitle || ""),
      node("span", "doc-scale", (doc.pages ? doc.pages + (doc.pages === 1 ? " page · " : " pages · ") : "") + readableBytes(doc.bytes)));
    card.append(cover, caption);
    const text = [doc.title, doc.subtitle, ...material.flatMap(m => [m.id, m.description, ...(m.aliases || [])])].join(" ").toLowerCase();
    return { card, kind, text };
  }).sort((a, b) => Number(b.kind === "drawing") - Number(a.kind === "drawing"));
  shelf.append(...cards.map(item => item.card));
  const empty = node("div", "document-empty"); empty.append(node("p", "", "No documents match these filters."));
  const clear = node("button", "", "Clear filters"); clear.type = "button";
  clear.addEventListener("click", () => { input.value = ""; active = "all"; render(); input.focus(); });
  empty.append(clear); state.gridEl.append(tools, shelf, empty);
  function render() {
    const words = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const matches = cards.filter(item => words.every(word => item.text.includes(word)));
    for (const [kind, { button, name }] of buttons) {
      const count = matches.filter(item => kind === "all" || item.kind === kind).length;
      button.textContent = name + " (" + count + ")";
      picker.querySelector('option[value="' + kind + '"]').textContent = ({ all: "All documents", drawing: "Drawings", guide: "Build guides" })[kind] + " (" + count + ")";
      button.setAttribute("aria-pressed", String(active === kind));
    }
    picker.value = active;
    let shown = 0;
    for (const item of cards) {
      item.card.hidden = !matches.includes(item) || (active !== "all" && item.kind !== active);
      if (!item.card.hidden) shown++;
    }
    empty.hidden = shown > 0;
    status.textContent = shown + (shown === 1 ? " document" : " documents");
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set("q", input.value.trim()); else url.searchParams.delete("q");
    if (active !== "all") url.searchParams.set("type", active); else url.searchParams.delete("type");
    if (url.href !== location.href) history.replaceState(history.state, "", url);
  }
  input.addEventListener("input", render);
  input.addEventListener("keydown", event => { if (event.key === "Escape") { input.value = ""; render(); } });
  render();
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
    // parts.js builds the parts section: it seats every CAD file the walkers offer, draws
    // the two roots it seated them into, and leaves the `.card[data-type="step"]
    // [data-file]` shells the window below and live.js select on. The seating that
    // is not those two roots is read by the gate — a directory nothing claims is
    // named above the cards — and is drawn nowhere.
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
        card.innerHTML = `${pcbThumb(board.source)}<div class="label card-caption">${dir}<span class="name-row"><span class="name">${board.name}</span></span></div>`;
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
