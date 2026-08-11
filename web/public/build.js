// Build-page boot script, loaded as a module from lib/build-tree.js.
//
// The tree's card anchors open the deck's modal in place: viewer/cards.js is
// the same module /drawings opens a card through, so the iframe, the PanZoom
// fit, the minimap, the saved transform and the `#card:` hash are one
// implementation across both pages. A modified click, and a page whose module
// never arrived, follow the anchor's href to the card page.

import { openCardDetail, closeCardDetail, refetchOpenCard } from "/js/viewer/cards.js";
import { state } from "/js/viewer/state.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

const PREFIX = "card:";

// The card the URL names, or null.
function routedCard() {
  const hash = location.hash ? decodeURIComponent(location.hash.slice(1)) : "";
  return hash.startsWith(PREFIX) ? hash.slice(PREFIX.length) : null;
}

// The card the modal is showing, or null.
function openCard() {
  const d = state.currentDetail;
  return d && d.type === "card" ? d.file : null;
}

document.addEventListener("click", (e) => {
  // Every click that means "somewhere else" — new tab, new window, download,
  // middle-click — stays the browser's.
  if (e.defaultPrevented || e.button !== 0) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const a = e.target.closest("a[data-card]");
  if (!a) return;
  e.preventDefault();
  openCardDetail(a.dataset.card);
});

// Back/forward, and ContentViewer's own dismissal, arrive here as the hash the
// URL now carries. Mirrors viewer/route.js for the one kind this page opens.
window.addEventListener("popstate", () => {
  const want = routedCard();
  const open = openCard();
  if (want === open) return;
  if (open) closeCardDetail(false);
  if (want) openCardDetail(want, false);
});

// A `#card:` deep link into the tree. The delay matches route.js: PanZoom fits
// the card against the modal's laid-out size.
const initial = routedCard();
if (initial) setTimeout(() => openCardDetail(initial, false), 100);

// A live edit to the open card re-frames it, the way live.js does on the
// viewer pages. The tree around it is server-rendered and reloads on deploy.
window.addEventListener(HSM_EVENTS.FILES_CHANGED, (e) => {
  const open = openCard();
  if (!open) return;
  const files = (e.detail && e.detail.files) || [];
  if (files.includes(open)) refetchOpenCard(open);
});
