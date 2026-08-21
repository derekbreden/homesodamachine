// The document convention, shared by the server's walker and its file route.
//
// A DOCUMENT IS A PDF A PERSON IS HANDED WHOLE. The deck a bench builds from,
// the manual that ships in the carton: pages meant to be read in order, on
// paper, off one file. The site does not re-implement a reader for them — it
// shows the cover and opens the PDF.
//
// Three files stand together, named off the PDF:
//
//   <name>.pdf         the document
//   <name>.cover.png   its first page, small enough to be a picture on a page
//   <name>.pdf.json    what it is called and how big it is — {title, subtitle,
//                      pages, cover}
//
// The sidecar is what makes a PDF a document. Every other `.pdf` under
// `hardware/` is a generator's own output — a print sheet, a datasheet a board
// vendored — and stays out of the listing and out of `/docs`.
export const DOC_SIDECAR_SUFFIX = ".pdf.json";

// The cover beside a document, as a path relative to the same root. Covers are
// served by the existing `/thumbs/<path>.png` route, which is the one place
// `hardware/`'s PNGs are handed out.
export function coverPathFor(pdfRel, coverName) {
  const slash = pdfRel.lastIndexOf("/");
  const dir = slash < 0 ? "" : pdfRel.slice(0, slash + 1);
  return dir + coverName;
}
