// Blog-page boot script loaded via <script src="/blog.js" defer> from
// lib/blog.js. Wires bare <img> elements inside post bodies into a
// pan-zoom ContentViewer for tap-to-zoom.

(function () {
  // Tap-to-zoom: bare <img> inside .post-body opens in ContentViewer with
  // pan + pinch-zoom. An image wrapped in <a> (markdown's
  // [![alt](src)](url) form) is an explicit link and must follow its
  // href — the link is the author's declared intent and overrides the
  // lightbox affordance. The clone-into-modal pattern below applies only
  // to bare images.
  for (const img of document.querySelectorAll(".post-body img")) {
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
      cloned.draggable = false;
      const wrapper = document.createElement("div");
      wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
      wrapper.appendChild(cloned);
      const pz = PanZoom.wrap(cloned, { container: wrapper, initialFit: true });
      ContentViewer.open({
        content: wrapper,
        filename: img.alt || undefined,
        onClose: function () { pz.destroy(); },
      });
    });
  }
})();
