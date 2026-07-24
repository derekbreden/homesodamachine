// Assembly-card module. Owns the card thumbnail, the modal open/close flow, and
// the reload-on-change path for the printable 4×6 deck (hardware/assembly/cards).
//
// Modeled on drawings.js — a 2D artifact opened in ContentViewer under PanZoom,
// so the transform persistence, open/close, and re-render-swap logic mirror it.
// What differs is the artifact: a card is a whole HTML page, not an SVG we can
// adopt into this document. It carries its own stylesheet, its own 1800 × 1200
// canvas, and print colours that must not inherit the viewer's dark theme. So a
// card renders in an <iframe> at its exact canvas size and PanZoom scales it —
// the same document the print pipeline rasterizes, laid out by the same engine,
// never reflowed. What you read here is what comes off the printer.
//
// The iframe is inert: `pointer-events: none` so drag/wheel/pinch reach PanZoom's
// container instead of being swallowed by the nested document. Cards have nothing
// to click, so nothing is lost.

import { state } from "./state.js";
import { makeResetButton, makeMinimap } from "./pan-zoom-extras.js";
import { PLACEHOLDER } from "./lazy.js";
import { CARD_W, CARD_H, cardAssetUrl } from "/contracts/cards.js";

function cardTransformKey(file) { return `card-transform:${file}`; }

export function cardSaveTransform(file, t) {
  try { localStorage.setItem(cardTransformKey(file), JSON.stringify(t)); } catch {}
}
export function cardLoadTransform(file) {
  try {
    const raw = localStorage.getItem(cardTransformKey(file));
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (typeof s.scale !== "number") return null;
    return s;
  } catch { return null; }
}

// A card frame at exact canvas size. `bust` forces past the browser cache after
// a live edit — the card URL is otherwise stable, and no-cache revalidation
// doesn't reach a document already parsed inside a live iframe.
//
// Absolutely positioned at its host's top-left, which is load-bearing rather
// than cosmetic: the frame is 1200 px tall before anything scales it, and in
// normal flow that height pushes its container taller for the one layout pass
// PanZoom measures the viewport in — so the modal fits the card to a viewport
// bigger than the one it ends up in, and the card's footer sits just off the
// bottom edge. Out of flow, the frame can't influence what contains it at any
// scale. Every host below is `position: relative`, so top-left is the same
// origin a static block would have had, and PanZoom's `transform-origin: 0 0`
// math is unchanged.
function makeCardFrame(file, { bust = false } = {}) {
  const frame = document.createElement("iframe");
  frame.className = "card-frame";
  frame.setAttribute("scrolling", "no");
  frame.setAttribute("tabindex", "-1");
  frame.setAttribute("aria-hidden", "true");
  frame.width = CARD_W;
  frame.height = CARD_H;
  frame.style.cssText =
    `position:absolute;top:0;left:0;width:${CARD_W}px;height:${CARD_H}px;` +
    `border:0;display:block;background:#f7f5f0;pointer-events:none;`;
  frame.src = cardAssetUrl(file) + (bust ? `?t=${Date.now()}` : "");
  return frame;
}

// --- Thumbnail ---
// The thumbnail is the card itself: the same iframe, scaled to the host's width
// by transform (not by resizing the frame — the canvas is fixed, so scaling is
// the only faithful reduction). Returns nothing to cache; the host element owns
// the frame. Called by grid.js's IntersectionObserver so an 80-card deck only
// loads the frames actually scrolled into view.
export function mountCardThumbnail(hostEl, file, { bust = false } = {}) {
  if (!hostEl) return;
  // Clear rather than going through unmountCardThumbnail: that restores the
  // placeholder, which the frame would then be appended alongside rather than
  // replacing.
  releaseFrame(hostEl);
  hostEl.innerHTML = "";
  const frame = makeCardFrame(file, { bust });
  frame.style.transformOrigin = "0 0";
  hostEl.appendChild(frame);
  const fit = () => {
    const w = hostEl.clientWidth;
    if (!w) return;
    frame.style.transform = `scale(${w / CARD_W})`;
  };
  fit();
  // The grid reflows on viewport change; re-fit so the scaled card keeps
  // filling its host exactly rather than drifting from the 3:2 thumb box.
  const ro = new ResizeObserver(fit);
  ro.observe(hostEl);
  hostEl._cardResizeObserver = ro;
}

// Stop re-fitting a host's frame. Separate from the DOM teardown because mount
// and unmount leave the host in different states — empty vs. placeholder — but
// both have to drop the observer, which would otherwise outlive its frame.
function releaseFrame(hostEl) {
  hostEl._cardResizeObserver?.disconnect();
  hostEl._cardResizeObserver = null;
}

// Release a card thumbnail: drop the iframe's document and the observer that
// was re-fitting it. This is the one kind where releasing really matters — a
// mounted card is a live document with its own stylesheet, layout, and embedded
// renders, and a deck this size will hold ~90 of them at once if nothing ever
// lets go. The host keeps its 3:2 box (viewer.css), so nothing moves.
export function unmountCardThumbnail(hostEl) {
  if (!hostEl) return;
  releaseFrame(hostEl);
  hostEl.innerHTML = PLACEHOLDER;
}

// --- Detail ---

// Swap the card inside the open modal without disturbing PanZoom's state — used
// by the live-edit path so pan/zoom survives a re-save. Minimap + reset button
// get rebuilt against the new frame, matching the drawing path.
function reRenderOpenCard(file) {
  if (!state.currentCardWrapper || !state.currentCardPz) return;
  const prev = state.currentCardPz.getTransform();
  state.currentCardPz.destroy();
  try { state.currentCardMinimap?.destroy(); } catch {}
  const frame = makeCardFrame(file, { bust: true });
  state.currentCardWrapper.innerHTML = "";
  state.currentCardWrapper.appendChild(frame);
  const minimap = makeMinimap(frame, state.currentCardWrapper);
  state.currentCardPz = PanZoom.wrap(frame, {
    container: state.currentCardWrapper,
    initialFit: false,
    onTransformChange: (t) => cardSaveTransform(file, t),
    onTransformLive: (t) => minimap.update(t),
  });
  state.currentCardWrapper.appendChild(minimap.el);
  state.currentCardWrapper.appendChild(makeResetButton(state.currentCardPz, {
    transformKey: cardTransformKey(file),
  }));
  state.currentCardMinimap = minimap;
  state.currentCardPz.setTransform(prev);
}

function shortName(file) {
  return file.split("/").pop().replace(/\.html$/, "");
}

export async function openCardDetail(file, pushHistory = true) {
  // Set currentDetail BEFORE touching location.hash — some configurations
  // (Puppeteer) fire popstate synchronously and the handler dispatches on it.
  state.currentDetail = { type: "card", file };
  if (pushHistory) location.hash = "card:" + encodeURIComponent(file);

  const wrapper = document.createElement("div");
  wrapper.className = "card-wrapper";
  wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
  const frame = makeCardFrame(file);
  wrapper.appendChild(frame);

  const minimap = makeMinimap(frame, wrapper);
  const pz = PanZoom.wrap(frame, {
    container: wrapper,
    initialFit: true,
    onTransformChange: (t) => cardSaveTransform(file, t),
    onTransformLive: (t) => minimap.update(t),
  });
  wrapper.appendChild(minimap.el);
  wrapper.appendChild(makeResetButton(pz, { transformKey: cardTransformKey(file) }));

  state.currentCardWrapper = wrapper;
  state.currentCardPz = pz;
  state.currentCardMinimap = minimap;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(file),
    onOpen: () => {
      pz.fit();
      const saved = cardLoadTransform(file);
      if (saved) pz.setTransform(saved);
      minimap.update();
    },
    onClose: () => {
      try { pz.destroy(); } catch {}
      try { minimap.destroy(); } catch {}
      state.currentDetail = null;
      state.currentCardWrapper = null;
      state.currentCardPz = null;
      state.currentCardMinimap = null;
      if (location.hash) history.back();
    },
  });
}

export function closeCardDetail(pushHistory = true) {
  if (!ContentViewer.isOpen()) {
    state.currentDetail = null;
    state.currentCardWrapper = null;
    state.currentCardPz = null;
    return;
  }
  if (!pushHistory) {
    const pz = state.currentCardPz;
    state.currentDetail = null;
    state.currentCardWrapper = null;
    state.currentCardPz = null;
    try { pz?.destroy(); } catch {}
    ContentViewer.close();
    return;
  }
  ContentViewer.close();
}

// Live-edit / deploy refresh for the open card. Unlike the fetch-and-compare
// kinds, the card's bytes live inside the iframe's own document — we can't
// diff them from here, so an edit to the open card always re-frames it. The
// cost is one cheap document load; the pan/zoom is preserved either way.
export async function refetchOpenCard(file) {
  reRenderOpenCard(file);
}
