import express from "express";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const require = createRequire(import.meta.url);
const pdfjsDir = path.dirname(require.resolve("pdfjs-dist/package.json"));
const { version } = JSON.parse(fs.readFileSync(path.join(pdfjsDir, "package.json"), "utf8"));
const pdfjsBase = `/vendor/pdfjs/${version}`;
const escape = (value) => String(value).replace(/[&<>"']/g, ch => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[ch]);

export function mountPdfjsAssets(app) {
  // The library and worker share a versioned URL so an installed PWA cannot
  // pair a cached worker with a different library after a deploy.
  for (const dir of ["legacy/build", "web", "cmaps", "standard_fonts", "wasm"]) {
    app.use(`${pdfjsBase}/${dir}`, express.static(path.join(pdfjsDir, dir), {
      dotfiles: "allow", index: false, maxAge: "1y", immutable: true,
    }));
  }
}

export function renderDocumentReader({ file, title }) {
  const url = `/docs/${file.split("/").map(encodeURIComponent).join("/")}`;
  return renderHead({
    title: `${title} · Home Soda Machine`,
    pageHead: `<link rel="stylesheet" href="${pdfjsBase}/web/pdf_viewer.css">
<link rel="stylesheet" href="/css/document-reader.css">
<script type="module" src="/document-reader.js"></script>`,
  }) + renderNav({ active: "drawings" }) + `
<main class="pdf-reader" data-pdf-url="${escape(url)}?raw=1" data-pdfjs-base="${pdfjsBase}">
  <header class="pdf-heading">
    <a id="pdf-back" href="/drawings">Back</a>
    <h1>${escape(title)}</h1>
    <a href="${escape(url)}?download=1" download>Download PDF</a>
  </header>
  <div class="pdf-toolbar" aria-label="Document controls">
    <div class="pdf-control-group">
      <button id="pdf-prev" type="button" aria-label="Previous page" disabled>←</button>
      <label>Page <input id="pdf-page" type="number" min="1" value="1" inputmode="numeric" disabled></label>
      <span>of <span id="pdf-pages">…</span></span>
      <button id="pdf-next" type="button" aria-label="Next page" disabled>→</button>
    </div>
    <div class="pdf-control-group">
      <button id="pdf-zoom-out" type="button" aria-label="Zoom out" disabled>−</button>
      <button id="pdf-fit" type="button" disabled>Fit width</button>
      <button id="pdf-zoom-in" type="button" aria-label="Zoom in" disabled>+</button>
    </div>
  </div>
  <p id="pdf-status" role="status">Loading document…</p>
  <button id="pdf-retry" type="button" hidden>Try again</button>
  <noscript><p>Enable JavaScript to read this document here, or use Download PDF.</p></noscript>
  <div class="pdf-viewport" tabindex="0" aria-label="Document page">
    <div class="pdf-paper" hidden>
      <canvas id="pdf-canvas" width="0" height="0" aria-hidden="true"></canvas>
      <div id="pdf-text" class="textLayer"></div>
    </div>
  </div>
</main>` + renderFooter();
}
