// Keep Three.js off the catalog's loading path until a model or material opens.
import { isViewerHash, PARTS_PATH } from "/contracts/viewer-links.js";

let viewer;
let requestedLink;

function loadViewer() {
  viewer ??= import("./main.js").then(async module => {
    await module.viewerReady;
    return module;
  });
  return viewer;
}

function reportFailure(error) {
  console.warn("Parts viewer:", error);
  if (document.getElementById("parts-viewer-error")) return;
  const notice = document.createElement("p");
  notice.id = "parts-viewer-error";
  notice.setAttribute("role", "alert");
  notice.textContent = "The parts viewer could not load. Reload the page to try again.";
  document.getElementById("parts-catalog")?.prepend(notice);
}

function openLinkedView() {
  if (viewer) return;
  const query = new URLSearchParams(location.search);
  if (isViewerHash(location.hash) || query.get("file") || query.get("find")) loadViewer().catch(reportFailure);
}

window.addEventListener("popstate", openLinkedView);
window.addEventListener("hashchange", openLinkedView);
openLinkedView();

document.addEventListener("click", event => {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest?.("a[href]");
  if (!link || link.target || link.hasAttribute("download")) return;
  const url = new URL(link.href, location.href);
  if (url.origin !== location.origin || url.pathname !== PARTS_PATH || !isViewerHash(url.hash)) return;
  event.preventDefault();
  const requested = requestedLink = { hash: url.hash, from: location.href };
  loadViewer().then(module => {
    if (requested !== requestedLink || requested.from !== location.href) return;
    return module.openViewerHash(requested.hash, true);
  }).catch(reportFailure);
});
