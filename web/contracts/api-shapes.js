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
 * @property {string|null} picks  out/<name>.picks.json when present (picks-schema.ts), else null
 */

// Endpoints:
//   GET /api/steps      -> PathList
//   GET /api/mermaid    -> PathList
//   GET /api/drawings   -> PathList
//   GET /api/dxf        -> DxfItem[]
//   GET /api/pcb        -> Board[]
//   GET /api/mermaid-content/<path>  -> text/plain (raw .mmd)
//   GET /api/drawing-content/<path>  -> image/svg+xml
//   GET /api/pcb-content/<path>      -> image/svg+xml   (confined by pcb-out.js VIEW_REQUEST_RE)
//   GET /api/pcb-picks/<path>        -> PicksFile        (picks-schema.ts; confined by PICKS_REQUEST_RE)
//   GET /steps/<path>  /dxfs/<path>  -> file bytes
//   GET /thumbs/<path>               -> image/png        (server-rendered STEP thumbnail)
//   GET /api/version                 -> { commit }       (deploy/activation check; boot.js polls it)
