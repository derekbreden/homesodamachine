// Parts cards load their model thumbnails near the viewport. Guide cards link to documents.

import { state } from "./state.js";
import { buildPartsSection, syncFaucetCard } from "./parts.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { isMounted, windowContent } from "./lazy.js";
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

// A foreground modal owns the browser's rendering time. Keep the thumbnails
// already drawn and resume unfinished or updated cards when the shelf returns.
const pendingStepThumbs = new Set();
let shelfWork = null;

function syncStepThumbnails() {
  if (ContentViewer.isOpen() || state.gridEl.querySelector(":scope > .material-search:focus-within")) {
    shelfWork?.abort();
    shelfWork = null;
  } else if (!shelfWork) {
    shelfWork = new AbortController();
    for (const card of pendingStepThumbs) paintStepThumb(card);
  }
}

export function startStepThumbnails() {
  requestAnimationFrame(() => requestAnimationFrame(() => {
    window.addEventListener(HSM_EVENTS.CONTENT_VIEWER_CHANGED, syncStepThumbnails);
    const search = state.gridEl.querySelector(":scope > .material-search");
    search?.addEventListener("focusin", syncStepThumbnails);
    search?.addEventListener("focusout", () => queueMicrotask(syncStepThumbnails));
    syncStepThumbnails();
  }));
}

// `bust` drops the cached picture, so a live reload redraws from the fresh model.
//
// The card says it is drawing while it draws. Reading a model takes about as long
// as opening one does, and a card that stands empty for that long reads as a card
// with nothing in it rather than one on its way.
export function paintStepThumb(card, { bust = false } = {}) {
  if (bust) forgetThumbnail(card.dataset.file);
  const img = card.querySelector("img");
  if (!img || !card.isConnected || !isMounted(card)) return;
  pendingStepThumbs.add(card);
  if (!shelfWork) return;
  const { signal } = shelfWork;
  const file = card.dataset.file;
  const finish = state.faucetFinish;
  const drawing = (card._drawingSeq || 0) + 1;
  card._drawingSeq = drawing;
  card.dataset.drawing = "1";
  return renderThumbnail(file, thumbSize(card), finish, "shelf", { signal }).then((url) => {
    if (signal.aborted || card._drawingSeq !== drawing || card.dataset.file !== file) return;
    pendingStepThumbs.delete(card);
    if (url && card.isConnected && isMounted(card)) img.src = url;
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

// Guides — the PDFs this site hands over whole (/api/documents,
// web/contracts/documents.js), less the engineering drawings: a drawing is a
// document some material tags `engineering-drawing`, and that material's panel
// shows it. One card each: the cover, the title, the page and byte count, and
// an href that opens the in-app document reader.
//
// The cover is a committed PNG beside the PDF, served by the same `/thumbs/`
// route every other picture under hardware/ comes through — no thumbnail to
// render, nothing to mount lazily.
function readableBytes(n) {
  return n >= 1024 * 1024 ? `${(n / (1024 * 1024)).toFixed(1)} MB` : `${Math.round(n / 1024)} KB`;
}

function buildGuidesSection() {
  const drawings = new Set();
  for (const material of state.materialCatalog?.materials || []) for (const doc of material.documents || []) {
    if (doc.kind === "engineering-drawing") drawings.add(doc.path);
  }
  const guides = (state.documents || []).filter(doc => !drawings.has(doc.path));
  const node = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  };
  if (!guides.length) {
    state.gridEl.append(node("p", "empty-state", "No guides yet."));
    return;
  }
  const search = node("div", "material-search");
  const label = node("label", "", "Find a guide");
  const input = node("input"); input.type = "search"; input.autocomplete = "off";
  input.placeholder = "Title or subject…"; input.value = new URLSearchParams(location.search).get("q") || "";
  input.setAttribute("aria-label", "Find a guide");
  label.append(input); search.append(label);
  const status = node("p", "document-search-status"); status.setAttribute("role", "status");
  document.getElementById("document-search-slot").replaceChildren(search, status);
  const shelf = node("div", "doc-shelf");
  const cards = guides.map(doc => {
    const card = node("a", "card card-doc");
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
    caption.append(nameRow, node("span", "dir", doc.subtitle || ""),
      node("span", "doc-scale", (doc.pages ? doc.pages + (doc.pages === 1 ? " page · " : " pages · ") : "") + readableBytes(doc.bytes)));
    card.append(cover, caption);
    return { card, text: [doc.title, doc.subtitle].join(" ").toLowerCase() };
  });
  shelf.append(...cards.map(item => item.card));
  const empty = node("div", "document-empty"); empty.append(node("p", "", "No guides match this search."));
  const clear = node("button", "", "Clear search"); clear.type = "button";
  clear.addEventListener("click", () => { input.value = ""; render(); input.focus(); });
  empty.append(clear); state.gridEl.append(shelf, empty);
  function render() {
    const words = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const item of cards) {
      item.card.hidden = !words.every(word => item.text.includes(word));
      if (!item.card.hidden) shown++;
    }
    empty.hidden = shown > 0;
    status.textContent = shown + (shown === 1 ? " guide" : " guides");
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set("q", input.value.trim()); else url.searchParams.delete("q");
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
  if (tail === "/guides") return "guides";
  return "parts";
}

export function buildGrid() {
  pendingStepThumbs.clear();
  if (shelfWork) {
    shelfWork.abort();
    shelfWork = new AbortController();
  }
  const search = state.gridEl.querySelector(":scope > .material-search");
  for (const child of [...state.gridEl.children]) if (child !== search) child.remove();
  search?.refresh();
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

  if (section === "guides") {
    buildGuidesSection();
  }

  state.gridWindow?.disconnect();
  state.gridWindow = windowContent({
    elements: state.gridEl.querySelectorAll('.card[data-type="step"]'),
    mount: card => paintStepThumb(card),
    unmount: card => {
      pendingStepThumbs.delete(card);
      card.querySelector("img")?.removeAttribute("src");
    },
  });
}
