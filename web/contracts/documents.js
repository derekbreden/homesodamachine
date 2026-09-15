// The document convention, shared by the server's walker and its file route.
//
// A document is a PDF a person is handed whole — a deck, a drawing set, or a
// customer instruction sheet. The site shows its cover and opens it.
//
// Three files stand together, named off the PDF:
//
//   <name>.pdf         the document
//   <name>.cover.png   its first page, small enough to be a picture on a page
//   <name>.pdf.json    what it is called and how big it is — {title, subtitle,
//                      pages, cover, cover_size}
//
// The sidecar is what makes a PDF a document. A `.pdf` under `hardware/` with
// none — a datasheet a board vendored, a generator's own output — is not in the
// listing and is not reachable through `/docs`. Superseded quick starts are
// excluded even when a scene build restores their PDF and sidecar.
export const DOC_SIDECAR_SUFFIX = ".pdf.json";

const SUPERSEDED_QUICK_STARTS = new Set([
  "quickstart/quick-start.pdf",
  "quickstart-claude/quick-start-claude.pdf",
  "quickstart-codex/edge-study.pdf",
  "quickstart-codex/contour-alternates.pdf",
]);

export function isPublishedDocument(pdfRel) {
  return !SUPERSEDED_QUICK_STARTS.has(pdfRel);
}

// The cover beside a document, as a path relative to the same root. Covers are
// served by the existing `/thumbs/<path>.png` route, which is the one place
// `hardware/`'s PNGs are handed out.
export function coverPathFor(pdfRel, coverName) {
  const slash = pdfRel.lastIndexOf("/");
  const dir = slash < 0 ? "" : pdfRel.slice(0, slash + 1);
  return dir + coverName;
}
