// /changes in the browser: the feed goes on as it scrolls, and a card opens its entry over the
// feed. Every page here works without this — the cards are links to /changes/<id>, the feed
// ends in a link to the next page, and a view's Before/After are radios — so what follows only
// keeps the reader on the feed.

const list = document.getElementById("ch-list");
const more = document.getElementById("ch-more");

// --- more as it scrolls ------------------------------------------------------

if (list && more && "IntersectionObserver" in window) {
  const link = more.querySelector("a");
  let loading = false;
  const near = () => more.isConnected && more.getBoundingClientRect().top < innerHeight + 1200;
  const loadMore = async () => {
    if (loading || !more.dataset.before) return;
    loading = true;
    try {
      const res = await fetch(`/api/changes?before=${encodeURIComponent(more.dataset.before)}&limit=10`);
      if (!res.ok) throw new Error(`${res.status}`);
      const page = await res.json();
      list.insertAdjacentHTML("beforeend", page.html);
      if (page.next) {
        more.dataset.before = page.next;
        if (link) link.href = `/changes?before=${encodeURIComponent(page.next)}`;
      } else {
        observer.disconnect();
        more.remove();
      }
    } catch {
      // The link stays, and is the way on.
      return;
    } finally {
      loading = false;
    }
    // A page that did not fill the screen leaves the sentinel in view, and an observer that
    // already saw it there says nothing more.
    if (near()) loadMore();
  };
  const observer = new IntersectionObserver((seen) => {
    if (seen.some((s) => s.isIntersecting)) loadMore();
  }, { rootMargin: "1200px 0px" });
  observer.observe(more);
}

// --- a view's frame ----------------------------------------------------------

// A tap on the picture flips it, the way a tap on its label does.
document.addEventListener("click", (e) => {
  const frame = e.target.closest?.(".ch-frame");
  if (!frame) return;
  const view = frame.closest(".ch-view");
  const before = view?.querySelector(".ch-r-before");
  const after = view?.querySelector(".ch-r-after");
  if (before && after) (before.checked ? after : before).checked = true;
});

// ← and → choose Before and After for every view of the entry in front — the same keys the
// focused radio answers to, from anywhere on it.
document.addEventListener("keydown", (e) => {
  if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
  if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
  if (e.target.closest?.("input, textarea, select, [contenteditable]")) return;
  const scope = document.querySelector(".cv-dialog .ch-detail") || document.querySelector("main .ch-detail");
  if (!scope) return;
  const side = e.key === "ArrowLeft" ? "before" : "after";
  for (const radio of scope.querySelectorAll(`.ch-r-${side}`)) radio.checked = true;
  e.preventDefault();
});

// --- an entry over the feed ----------------------------------------------------

const ENTRY_PATH = /^\/changes\/([a-z0-9][a-z0-9-]*)\/?$/;
let openId = null;
// Each opening's own number: a close or a fetch that arrives after a newer entry took the
// modal belongs to the old one and does nothing.
let opening = 0;
// Whether this page pushed the entry's URL, and so whether closing it is a step back.
let pushed = false;
// A close the browser's own Back asked for has already moved the URL.
let fromHistory = false;

async function openEntry(id, push) {
  const mine = ++opening;
  const box = document.createElement("div");
  box.className = "ch-modal";
  box.innerHTML = '<p class="ch-loading">Loading…</p>';
  window.ContentViewer.open({
    content: box,
    onClose: () => {
      if (mine !== opening) return;
      const back = pushed && !fromHistory;
      openId = null;
      pushed = false;
      fromHistory = false;
      if (back) history.back();
      else if (ENTRY_PATH.test(location.pathname)) history.replaceState(null, "", "/changes");
    },
  });
  openId = id;
  pushed = false;
  fromHistory = false;
  if (push) {
    history.pushState({ change: id }, "", `/changes/${id}`);
    pushed = true;
  }
  try {
    const res = await fetch(`/changes/${encodeURIComponent(id)}?fragment=1`);
    if (!res.ok) throw new Error(`${res.status}`);
    const html = await res.text();
    if (mine === opening) box.innerHTML = html;
  } catch {
    if (mine === opening) {
      box.innerHTML = `<p class="ch-loading">This change did not load. <a href="/changes/${id}">Open it on its own page</a>.</p>`;
    }
  }
}

if (list && window.ContentViewer) {
  list.addEventListener("click", (e) => {
    const card = e.target.closest("a.ch-card");
    if (!card || e.defaultPrevented || e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    openEntry(card.dataset.change, true);
  });

  window.addEventListener("popstate", () => {
    const m = ENTRY_PATH.exec(location.pathname);
    if (window.ContentViewer.isOpen() && (!m || m[1] !== openId)) {
      fromHistory = true;
      window.ContentViewer.close();
    }
    if (m && !window.ContentViewer.isOpen()) openEntry(m[1], false);
  });
}
