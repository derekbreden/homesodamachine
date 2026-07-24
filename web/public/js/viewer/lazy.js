// Windowed thumbnail content for the grid: mount a card's expensive part when
// it comes near the viewport, release it once it's well past.
//
// Every grid kind used to mount on first intersection and then `unobserve`, so
// a scroll to the bottom left the whole list mounted at once. Measured on a
// 390 × 844 viewport, scrolled top to bottom — peak live set, then the same
// scroll with the window below:
//
//   /drawings   88 cards → 86 live iframes (143 documents)  →  13
//   /3d        105 parts → 109 decoded 400 × 400 bitmaps    →  30
//
// Neither is a DOM-size problem — the shells are ~900 nodes on both pages, which
// is nothing. It's the *content*: a card is a live document, and a thumbnail
// that has been fetched is a decoded bitmap (400 × 400 × 4B = 640 KB each,
// which `loading="lazy"` defers the fetch of but never frees). So this windows
// content, not rows: every shell stays in the DOM and keeps its box, and only
// the costly interior comes and goes.
//
// Windowing content rather than virtualizing rows is what keeps this honest.
// Scroll height never changes, so there's no scroll-anchoring jank, no jumping
// scrollbar, and the section headers keep their natural flow — and it works
// because every thumbnail host declares a fixed `aspect-ratio` in viewer.css.
// An empty host occupies exactly the space a full one did, so mounting and
// unmounting can never move anything on screen.
//
// Two observers give the hysteresis. `near` mounts; the wider `far` releases.
// A card that stops right at the boundary can't thrash between the two, because
// leaving requires travelling the whole gap between them.

// Mount when within a screen of the viewport; release once two screens past.
// Expressed in viewport heights so the window scales with the device: a phone
// holds a small working set, a desktop a proportionally larger one.
//
// The near margin buys smoothness — content is ready a full screen before you
// reach it, so nothing pops in. The far margin sets the peak: it's what decides
// how many cards are live at the worst moment, mid-list, with the window
// extending both ways. The one-screen gap between them is the hysteresis; a
// card would have to oscillate by a whole screen height to thrash, and that
// happens two screens off-screen where the work is invisible anyway.
const NEAR_SCREENS = 1;
const FAR_SCREENS = 2;

function screensToPx(n) {
  // innerHeight is 0 in some headless/detached cases; fall back to a sane phone
  // height so the margins never collapse to "mount nothing".
  return `${Math.round((window.innerHeight || 800) * n)}px`;
}

// Whether a grid card's content is currently mounted. Kept as a data attribute
// rather than private bookkeeping because live.js reads it too: a file-changed
// broadcast must not repaint a card that has been released, or the card ends up
// holding content that nothing is tracking and so is never freed. It also means
// the window's state is visible in devtools.
export function isMounted(card) {
  return card.dataset.mounted === "1";
}

// Observe `elements`, calling mount(el) as each nears the viewport and
// unmount(el) once it's far past. Both are called at most once per transition,
// so neither has to be idempotent.
//
// Returns { disconnect } — call it before rebuilding the grid so the observers
// for the old, detached cards go away with them.
export function windowContent({ elements, mount, unmount }) {
  const nearObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting || isMounted(entry.target)) continue;
      entry.target.dataset.mounted = "1";
      mount(entry.target);
    }
  }, { rootMargin: screensToPx(NEAR_SCREENS) });

  const farObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      // Fires on both edges of the far boundary; only the leaving edge matters.
      if (entry.isIntersecting || !isMounted(entry.target)) continue;
      delete entry.target.dataset.mounted;
      unmount(entry.target);
    }
  }, { rootMargin: screensToPx(FAR_SCREENS) });

  for (const el of elements) {
    nearObserver.observe(el);
    farObserver.observe(el);
  }

  return {
    disconnect() {
      nearObserver.disconnect();
      farObserver.disconnect();
    },
  };
}

export const PLACEHOLDER = `<div class="placeholder">loading...</div>`;

// Hosts whose content is an offscreen render handed back as a data URL (DXF
// cuts, GLB assemblies). The host holds either a placeholder or an <img>; both
// declare the same aspect ratio, so swapping between them is invisible. The
// URL stays in its per-kind cache — releasing gives back the decoded bitmap,
// not the render, so returning costs a decode and never a re-render.
export function imageThumb(render) {
  return {
    mount(card) {
      const token = (card._mountToken = (card._mountToken || 0) + 1);
      render(card.dataset.file).then((url) => {
        if (card._mountToken !== token) return;
        const host = card.firstElementChild;
        if (!host) return;
        if (!url) {
          host.innerHTML = "";
          host.className = "placeholder";
          host.textContent = "error";
          return;
        }
        const img = document.createElement("img");
        img.src = url;
        host.replaceWith(img);
      });
    },
    unmount(card) {
      card._mountToken = (card._mountToken || 0) + 1;
      const img = card.querySelector("img");
      if (!img) return;
      const ph = document.createElement("div");
      ph.className = "placeholder";
      ph.dataset.file = card.dataset.file;
      ph.textContent = "loading...";
      img.replaceWith(ph);
    },
  };
}

// Hosts whose content is markup dropped into a wrapper (mermaid, line art, PCB
// views). Releasing means putting the placeholder back — the rendered string
// stays in its per-kind cache, so coming back is a re-parse with no refetch.
//
// Every render is async, so a card can be released (or released and mounted
// again) while its render is still in flight. Each mount takes a token and only
// paints if it's still the current one, which drops both the stale-paint and
// the out-of-order-paint cases.
export function markupThumb({ hostSelector, render }) {
  return {
    mount(card) {
      const host = card.querySelector(hostSelector);
      if (!host) return;
      const token = (host._mountToken = (host._mountToken || 0) + 1);
      render(card.dataset.file).then((markup) => {
        if (host._mountToken !== token) return;
        host.innerHTML = markup || `<div class="placeholder">error</div>`;
      });
    },
    unmount(card) {
      const host = card.querySelector(hostSelector);
      if (!host) return;
      // Bumping the token invalidates any render still in flight for this host.
      host._mountToken = (host._mountToken || 0) + 1;
      host.innerHTML = PLACEHOLDER;
    },
  };
}
