// Guide cards link to documents and use their published covers.

import { state } from "./state.js";

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

export function buildGrid() {
  state.gridEl.replaceChildren();
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
