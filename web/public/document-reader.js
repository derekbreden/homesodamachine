// A single rendered page keeps document reading inside the PWA and bounds
// canvas memory, including on high-density phones and while zoomed in.
const reader = document.querySelector(".pdf-reader");
const viewportEl = reader.querySelector(".pdf-viewport");
const paper = reader.querySelector(".pdf-paper");
const canvas = document.getElementById("pdf-canvas");
const textEl = document.getElementById("pdf-text");
const status = document.getElementById("pdf-status");
const input = document.getElementById("pdf-page");
const prev = document.getElementById("pdf-prev");
const next = document.getElementById("pdf-next");
const zoomIn = document.getElementById("pdf-zoom-in");
const zoomOut = document.getElementById("pdf-zoom-out");
const fit = document.getElementById("pdf-fit");
const retry = document.getElementById("pdf-retry");
const MAX_PIXELS = 4 * 1024 * 1024;
const MAX_DIMENSION = 4096;
let pdfjs, pdf, currentPage = 1, zoom = 1, requested = 0, rendering = false;

function pageFromHash() {
  const value = Number(new URLSearchParams(location.hash.slice(1)).get("page"));
  return Number.isInteger(value) && value > 0 ? value : 1;
}

function updateControls() {
  input.disabled = !pdf;
  input.value = currentPage;
  prev.disabled = !pdf || currentPage <= 1;
  next.disabled = !pdf || currentPage >= pdf.numPages;
  zoomOut.disabled = !pdf || zoom <= 0.5;
  zoomIn.disabled = !pdf || zoom >= 4;
  fit.disabled = !pdf;
}

function showError() {
  status.textContent = "Couldn’t open this page. Try again or download the PDF.";
  retry.hidden = false;
}

async function renderRequestedPage() {
  if (!pdf || rendering) return;
  rendering = true;
  // Serialize canvas use; a newer request replaces the pending one while the
  // current render completes. Cleanup happens only after all page tasks finish.
  while (requested) {
    const revision = requested;
    const pageNumber = currentPage;
    const pageZoom = zoom;
    let page;
    status.textContent = `Loading page ${pageNumber}…`;
    retry.hidden = true;
    paper.hidden = true;
    delete canvas.dataset.page;
    textEl.replaceChildren();
    viewportEl.setAttribute("aria-busy", "true");
    try {
      page = await pdf.getPage(pageNumber);
      const natural = page.getViewport({ scale: 1 });
      const style = getComputedStyle(viewportEl);
      const width = viewportEl.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      const scale = Math.max(1, width) / natural.width * pageZoom;
      const viewport = page.getViewport({ scale });
      const density = Math.min(window.devicePixelRatio || 1, 2,
        Math.sqrt(MAX_PIXELS / (viewport.width * viewport.height)),
        MAX_DIMENSION / viewport.width, MAX_DIMENSION / viewport.height);
      canvas.width = Math.max(1, Math.floor(viewport.width * density));
      canvas.height = Math.max(1, Math.floor(viewport.height * density));
      canvas.style.width = paper.style.width = `${viewport.width}px`;
      canvas.style.height = paper.style.height = `${viewport.height}px`;
      paper.style.setProperty("--scale-factor", scale);
      await page.render({
        canvasContext: canvas.getContext("2d"), viewport,
        transform: [density, 0, 0, density, 0, 0],
      }).promise;
      const textLayer = new pdfjs.TextLayer({
        textContentSource: page.streamTextContent(), container: textEl, viewport,
      });
      await textLayer.render();
      if (revision === requested) {
        paper.hidden = false;
        canvas.dataset.page = pageNumber;
        status.textContent = `Page ${pageNumber} of ${pdf.numPages}`;
        viewportEl.scrollTo(0, 0);
      }
    } catch {
      if (revision === requested) showError();
    } finally {
      page?.cleanup();
      if (revision === requested) requested = 0;
    }
  }
  viewportEl.setAttribute("aria-busy", "false");
  rendering = false;
}

function requestRender() {
  requested++;
  updateControls();
  void renderRequestedPage();
}

function goToPage(value, push = true) {
  if (!pdf) return;
  const number = Number(value);
  if (!Number.isInteger(number)) { input.value = currentPage; return; }
  currentPage = Math.max(1, Math.min(pdf.numPages, number));
  const hash = `#page=${currentPage}`;
  if (location.hash !== hash) {
    history[push ? "pushState" : "replaceState"](null, "", hash);
  }
  requestRender();
}

prev.addEventListener("click", () => goToPage(currentPage - 1));
next.addEventListener("click", () => goToPage(currentPage + 1));
input.addEventListener("change", () => goToPage(input.value));
input.addEventListener("keydown", event => {
  if (event.key === "Enter") { goToPage(input.value); input.blur(); }
});
zoomIn.addEventListener("click", () => { zoom = Math.min(4, zoom * 1.25); requestRender(); });
zoomOut.addEventListener("click", () => { zoom = Math.max(0.5, zoom / 1.25); requestRender(); });
fit.addEventListener("click", () => { zoom = 1; requestRender(); });
retry.addEventListener("click", () => pdf ? requestRender() : location.reload());
window.addEventListener("hashchange", () => goToPage(pageFromHash(), false));
window.addEventListener("popstate", () => goToPage(pageFromHash(), false));
document.addEventListener("keydown", event => {
  if (event.target.closest("input, button, a")) return;
  if (event.key === "ArrowLeft" || event.key === "PageUp") {
    event.preventDefault(); goToPage(currentPage - 1);
  } else if (event.key === "ArrowRight" || event.key === "PageDown") {
    event.preventDefault(); goToPage(currentPage + 1);
  }
});
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(requestRender, 150);
});

try {
  const from = new URL(document.referrer);
  if (from.origin === location.origin && !/^\/(read|docs)\//.test(from.pathname)) {
    document.getElementById("pdf-back").href = from.href;
  }
} catch { /* Direct links return to the document shelf. */ }

try {
  const base = reader.dataset.pdfjsBase;
  // Mozilla's legacy build supplies the polyfills needed by mobile Safari.
  pdfjs = await import(`${base}/legacy/build/pdf.mjs`);
  pdfjs.GlobalWorkerOptions.workerSrc = `${base}/legacy/build/pdf.worker.mjs`;
  pdf = await pdfjs.getDocument({
    url: reader.dataset.pdfUrl,
    cMapUrl: `${base}/cmaps/`, cMapPacked: true,
    standardFontDataUrl: `${base}/standard_fonts/`, wasmUrl: `${base}/wasm/`,
    disableAutoFetch: true, disableStream: true,
    canvasMaxAreaInBytes: MAX_PIXELS * 4,
  }).promise;
  document.getElementById("pdf-pages").textContent = pdf.numPages;
  input.max = pdf.numPages;
  goToPage(pageFromHash(), false);
} catch { showError(); }
