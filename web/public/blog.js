// Blog-page boot script loaded via <script src="/blog.js" defer> from
// lib/blog.js. Two jobs:
//
//   1. Tap-to-zoom — wire bare <img> in post bodies into a pan-zoom
//      ContentViewer. Re-run as new posts stream in.
//
//   2. Infinite scroll — the server renders the newest page of posts plus a
//      #blog-sentinel; as the sentinel nears the viewport we fetch the next
//      page from /blog/posts and append it. Deep links to /blog#post-<slug>
//      (notification taps, bookmarks) may target a post on a later page, so
//      we keep paging until that post exists, then scroll to it.

(function () {
  // Wire any not-yet-wired post images for tap-to-zoom. Idempotent via the
  // data-zoom-wired marker so it's safe to call after each page append.
  function wireZoom() {
    for (const img of document.querySelectorAll(".post-body img:not([data-zoom-wired])")) {
      img.setAttribute("data-zoom-wired", "");
      // An image wrapped in <a> (markdown's [![alt](src)](url) form) is an
      // explicit link and must follow its href — the link is the author's
      // declared intent and overrides the lightbox. Bare images only.
      if (img.closest("a")) continue;
      img.style.cursor = "zoom-in";
      img.addEventListener("click", function () {
        const cloned = img.cloneNode(true);
        cloned.style.maxWidth = "none";
        cloned.style.maxHeight = "none";
        cloned.style.width = "auto";
        cloned.style.height = "auto";
        cloned.style.display = "block";
        cloned.style.margin = "0";
        cloned.style.borderRadius = "0";
        cloned.removeAttribute("loading"); // already loaded; show immediately
        cloned.draggable = false;
        const wrapper = document.createElement("div");
        wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
        wrapper.appendChild(cloned);
        // The fit clears the modal's own chrome, so the whole photo is on
        // screen rather than running under the filename pill and the close X.
        const obstacles = [];
        const pz = PanZoom.wrap(cloned, {
          container: wrapper,
          initialFit: true,
          fitObstacles: obstacles,
        });
        const refit = function () {
          const rects = PanZoom.measureObstacles(wrapper, ContentViewer.CHROME);
          obstacles.length = 0;
          obstacles.push.apply(obstacles, rects);
          pz.fit();
        };
        ContentViewer.open({
          content: wrapper,
          filename: img.alt || undefined,
          onOpen: function () { refit(); requestAnimationFrame(refit); },
          onClose: function () { pz.destroy(); },
        });
      });
    }
  }

  wireZoom();

  const sentinel = document.getElementById("blog-sentinel");
  if (!sentinel) return; // first page is the whole feed; nothing to page in

  let nextOffset = parseInt(sentinel.getAttribute("data-next-offset"), 10) || 0;
  let hasMore = true;
  let loading = false;
  let sentinelVisible = false;

  // Single-flight loader: appends the next page before the sentinel. The
  // `loading` guard means overlapping triggers (observer + deep-link loop)
  // collapse into one in-flight request.
  async function loadNextPage() {
    if (loading || !hasMore) return;
    loading = true;
    sentinel.classList.add("loading");
    let ok = false;
    try {
      const res = await fetch("/blog/posts?offset=" + nextOffset, {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error("status " + res.status);
      const data = await res.json();
      if (data.html) sentinel.insertAdjacentHTML("beforebegin", data.html);
      nextOffset = data.nextOffset;
      hasMore = data.hasMore;
      wireZoom();
      ok = true;
    } catch (err) {
      // Leave hasMore alone so a later scroll can retry this offset.
      console.error("blog: failed to load more posts", err);
    } finally {
      loading = false;
      sentinel.classList.remove("loading");
    }
    if (!ok) return;
    if (!hasMore) {
      observer.disconnect();
      sentinel.remove();
      return;
    }
    // If the page just added was shorter than the viewport, the sentinel may
    // still be on screen and the observer won't re-fire — keep pulling.
    if (sentinelVisible) loadNextPage();
  }

  // rootMargin pre-loads the next page ~one screen before the sentinel is
  // actually visible, so scrolling stays smooth.
  const observer = new IntersectionObserver(
    function (entries) {
      sentinelVisible = entries[0].isIntersecting;
      if (sentinelVisible) loadNextPage();
    },
    { rootMargin: "800px 0px" },
  );
  observer.observe(sentinel);

  // Deep link: /blog#post-<slug> can point at a post not yet in the DOM.
  // Page in until it appears (or we run out), then scroll to it — the
  // browser's own on-load anchor jump already handled first-page targets.
  async function loadUntilHash() {
    if (!/^#post-[\w-]+$/.test(location.hash)) return;
    const id = location.hash.slice(1);
    let target = document.getElementById(id);
    while (!target && hasMore) {
      await loadNextPage();
      target = document.getElementById(id);
    }
    if (target) target.scrollIntoView();
  }

  loadUntilHash();
  window.addEventListener("hashchange", loadUntilHash);
})();
