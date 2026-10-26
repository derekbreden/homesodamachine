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

export function renderDocumentReader({ file, title, embedded = false, hostControls = false }) {
  hostControls = embedded && hostControls;
  const url = `/docs/${file.split("/").map(encodeURIComponent).join("/")}`;
  const readUrl = `/read/${file.split("/").map(encodeURIComponent).join("/")}`;
  return renderHead({
    title: `${title} · Home Soda Machine`,
    pageClass: "site-interior" + (embedded ? " pdf-embedded" : "") + (hostControls ? " pdf-host-controls" : ""),
    pageHead: `<link rel="stylesheet" href="${pdfjsBase}/web/pdf_viewer.css">
<link rel="stylesheet" href="/css/workspace.css">
<link rel="stylesheet" href="/css/document-reader.css">
<script type="module" src="/document-reader.js"></script>`,
  }) + (embedded ? "" : renderNav({ active: "drawings" })) + `
<main class="pdf-reader site-light" data-pdf-url="${escape(url)}?raw=1" data-pdfjs-base="${pdfjsBase}" data-embedded="${embedded}" data-host-controls="${hostControls}">
  <header class="pdf-heading">
    <div class="pdf-identity">
      ${embedded ? `<a class="pdf-back" href="${escape(readUrl)}" target="_blank" rel="noopener">Open full drawing</a>` : '<a id="pdf-back" class="pdf-back" href="/drawings" aria-label="Back"><span aria-hidden="true">←</span><span class="pdf-back-word">Back</span></a>'}
      <h1 title="${escape(title)}">${escape(title)}</h1>
    </div>
    <div class="pdf-toolbar" aria-label="Document controls">
      <div id="pdf-pagination" class="pdf-control-group" role="group" aria-label="Page navigation" hidden>
        <button id="pdf-prev" type="button" aria-label="Previous page" disabled>←</button>
        <label><span class="pdf-page-word">Page</span><input id="pdf-page" type="number" min="1" value="1" inputmode="numeric" disabled></label>
        <span class="pdf-total">/ <span id="pdf-pages">…</span></span>
        <button id="pdf-next" type="button" aria-label="Next page" disabled>→</button>
      </div>
      <div class="pdf-control-group pdf-zoom" role="group" aria-label="Zoom and page fit">
        <button id="pdf-zoom-out" class="pdf-zoom-step" type="button" aria-label="Zoom out" disabled>−</button>
        <select id="pdf-fit" aria-label="Page fit" disabled><option value="page">Fit page</option><option value="width">Fit width</option><option value="custom" disabled hidden>Zoomed</option></select>
        <button id="pdf-zoom-in" class="pdf-zoom-step" type="button" aria-label="Zoom in" disabled>+</button>
      </div>
    </div>
    <details class="workspace-menu pdf-actions">
      <summary aria-label="Document actions" title="Document actions">⋯</summary>
      <div class="workspace-menu-body">
        <p class="pdf-document-title">${escape(title)}</p>
        <div class="pdf-menu-zoom"><span>Zoom</span><button type="button" data-pdf-zoom="out" aria-label="Zoom out" disabled>−</button><button type="button" data-pdf-zoom="in" aria-label="Zoom in" disabled>+</button></div>
        <a href="${escape(url)}?download=1" download>Download PDF</a>
      </div>
    </details>
  </header>
  <p id="pdf-status" role="status">Loading document…</p>
  <button id="pdf-retry" type="button" hidden>Try again</button>
  <noscript><p>Enable JavaScript to read this document here, or use Download PDF.</p></noscript>
  <div class="pdf-viewport" tabindex="0" aria-label="Document page">
    <div class="pdf-paper" hidden>
      <canvas id="pdf-canvas" width="0" height="0" aria-hidden="true"></canvas>
      <div id="pdf-text" class="textLayer"></div>
    </div>
  </div>
</main>` + (embedded ? "</body></html>" : renderFooter());
}
