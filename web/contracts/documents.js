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
// listing and is not reachable through `/docs`. Retired owner documents are
// excluded even when a scene build restores their PDF and sidecar.
export const DOC_SIDECAR_SUFFIX = ".pdf.json";

// Committed guides are carried by the checkout. CAD publications may still name
// an earlier edition; adopting or retiring those objects must leave the guides in place.
const COMMITTED_DOCUMENT_FILES = new Set([
  "hardware/install-guide/install-guide.pdf",
  "hardware/install-guide/install-guide.cover.png",
  "hardware/install-guide/install-guide.pdf.json",
]);

export function isCommittedDocumentFile(repoRel) {
  return COMMITTED_DOCUMENT_FILES.has(repoRel) || (
    /^hardware\/(?:drill-and-cut-guide|mold-guide|refrigeration-guide|assembly-letter-guide|gun-positioner-guide)\//.test(repoRel)
    && /(?:\.pdf|\.cover\.png|\.pdf\.json)$/.test(repoRel)
  );
}

export function isArchivedDocumentFile(repoRel) {
  return repoRel.startsWith("hardware/assembly/cards/");
}

const RETIRED_OWNER_DOCUMENTS = new Set([
  "quickstart-codex/quick-start-codex.pdf",
  "quickstart/quick-start.pdf",
  "quickstart-claude/quick-start-claude.pdf",
  "quickstart-codex/edge-study.pdf",
  "quickstart-codex/contour-alternates.pdf",
]);

export function isPublishedDocument(pdfRel) {
  return !isArchivedDocumentFile("hardware/" + pdfRel) && !RETIRED_OWNER_DOCUMENTS.has(pdfRel);
}

// The cover beside a document, as a path relative to the same root. Covers are
// served by the existing `/thumbs/<path>.png` route, which is the one place
// `hardware/`'s PNGs are handed out.
export function coverPathFor(pdfRel, coverName) {
  const slash = pdfRel.lastIndexOf("/");
  const dir = slash < 0 ? "" : pdfRel.slice(0, slash + 1);
  return dir + coverName;
}
