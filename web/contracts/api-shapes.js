// The /api surface the viewer fetches — mounted by web/lib/viewer-routes.js, consumed by
// web/public/js/viewer/main.js (fetchFiles) and the per-type modules. List endpoints return
// paths relative to the content root, hardware/.

/** @typedef {string[]} PathList  /api/steps, /api/mermaid — file paths, sorted client-side */
/** @typedef {{ path: string, thickness_mm: number|null, material: string|null }} DxfItem  one /api/dxf entry (sidecar.js) */
/**
 * @typedef {Object} Board  one /api/pcb entry (walkPcbBoards in web/lib/walk.js)
 * @property {string} source   pcb/<dir>/<name>.tsx, root-relative
 * @property {string} name
 * @property {string} dir      root-relative board directory
 * @property {string} top      out/<name>.top.svg
 * @property {string} bottom
 * @property {string} overlay
 * @property {string[]} inners inner-plane view paths, stack order (pcb-out.js)
 * @property {string|null} topmask     out/<name>.topmask.svg (exposed-copper map, front) when rendered, else null
 * @property {string|null} bottommask  out/<name>.bottommask.svg (exposed-copper map, back) when rendered, else null
 * @property {string|null} picks  out/<name>.picks.json when present (picks-schema.ts), else null
 */
/**
 * @typedef {Object} Card  one walkAssemblyCards entry (web/lib/walk.js), deck-ordered — what
 *                          /build lays out against the procedure steps its cards render
 * @property {string} path            assembly/cards/<file>.html, root-relative — the card's id everywhere
 * @property {string} file            bare filename
 * @property {string|null} code       the printed code chip, e.g. "PV-05"
 * @property {string} title           the printed title (filename-derived if the card has none)
 * @property {string|null} deckpos    the printed deck position, e.g. "Pressure vessel · 05/14"
 * @property {string|null} subsystem  two-letter body class, e.g. "pv"; null on the cover
 * @property {string} subsystemLabel  display name from the deck's style.css, or "Deck"
 * @property {string|null} accent     the subsystem's accent colour from style.css
 */
/**
 * @typedef {Object} Document  one /api/documents entry (walkDocuments in web/lib/walk.js)
 * @property {string} path      <dir>/<name>.pdf, root-relative — served at /docs/<path>
 * @property {string} title     from the <name>.pdf.json sidecar (contracts/documents.js)
 * @property {string} subtitle  what it is and what it prints on, from the same sidecar
 * @property {number} pages     page count, from the same sidecar
 * @property {string|null} cover  <dir>/<name>.cover.png, root-relative — served at /thumbs/<cover>
 * @property {number} bytes     the PDF's size on this disk
 */

// Endpoints:
//   GET /api/steps      -> PathList
//   GET /api/mermaid    -> PathList
//   GET /api/dxf        -> DxfItem[]
//   GET /api/pcb        -> Board[]
//   GET /api/documents  -> Document[]
//   GET /api/mermaid-content/<path>  -> text/plain (raw .mmd)
//   GET /api/pcb-content/<path>      -> image/svg+xml   (confined by pcb-out.js VIEW_REQUEST_RE)
//   GET /api/pcb-picks/<path>        -> PicksFile        (picks-schema.ts; confined by PICKS_REQUEST_RE)
//   GET /steps/<path>  /dxfs/<path>  -> file bytes
//   GET /thumbs/<path>               -> image/png        (server-rendered STEP thumbnail)
//   GET /cards/<path>                -> card page / stylesheet / embedded render / the bound deck (cards.js)
//   GET /docs/<path>                 -> application/pdf   (confined by documents.js — a sidecar makes it a document)
//   GET /api/version                 -> { commit }       (deploy/activation check; boot.js polls it)
