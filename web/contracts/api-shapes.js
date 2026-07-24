// The /api surface the viewer fetches — mounted by web/lib/viewer-routes.js, consumed by
// web/public/js/viewer/main.js (fetchFiles) and the per-type modules. List endpoints return
// root-relative paths under the active content root (the edition cookie picks which root).

/** @typedef {string[]} PathList  /api/steps, /api/mermaid, /api/drawings — file paths, sorted client-side */
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
 * @typedef {Object} Card  one /api/cards entry (walkAssemblyCards in web/lib/walk.js), deck-ordered
 * @property {string} path            assembly/cards/<file>.html, root-relative — the card's id everywhere
 * @property {string} file            bare filename
 * @property {string|null} code       the printed code chip, e.g. "PV-05"
 * @property {string} title           the printed title (filename-derived if the card has none)
 * @property {string|null} deckpos    the printed deck position, e.g. "Pressure vessel · 05/14"
 * @property {string|null} subsystem  two-letter body class, e.g. "pv"; null on the cover
 * @property {string} subsystemLabel  display name from the deck's style.css, or "Deck"
 * @property {string|null} accent     the subsystem's accent colour from style.css
 */

// Endpoints:
//   GET /api/steps      -> PathList
//   GET /api/mermaid    -> PathList
//   GET /api/drawings   -> PathList
//   GET /api/dxf        -> DxfItem[]
//   GET /api/pcb        -> Board[]
//   GET /api/cards      -> Card[]
//   GET /api/mermaid-content/<path>  -> text/plain (raw .mmd)
//   GET /api/drawing-content/<path>  -> image/svg+xml
//   GET /api/pcb-content/<path>      -> image/svg+xml   (confined by pcb-out.js VIEW_REQUEST_RE)
//   GET /api/pcb-picks/<path>        -> PicksFile        (picks-schema.ts; confined by PICKS_REQUEST_RE)
//   GET /steps/<path>  /dxfs/<path>  -> file bytes
//   GET /thumbs/<path>               -> image/png        (server-rendered STEP thumbnail)
//   GET /cards/<path>                -> card page / stylesheet / embedded render (confined by cards.js)
//   GET /api/version                 -> { commit }       (deploy/activation check; boot.js polls it)
