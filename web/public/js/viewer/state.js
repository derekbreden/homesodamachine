// Shared mutable state for the viewer modules. One exported object so
// every reader/writer sees the same live binding via property access:
// no per-module sync dance, no getter/setter ceremony, no duplicate
// caches. The shape (the keys present and their meaning) IS the
// contract — every module that reads or writes here treats it like
// the file-scope `let` it replaces.
//
// At most one detail surface is open at a time (parts viewer is modal):
//   currentDetail = { type: "step"|"dxf"|"mmd"|"drawing"|"pcb"|"card", file } | null
//   mountedDetail = { type: "step"|"dxf",       file } | null
// "current" tracks which file the modal is presenting; "mounted" tracks
// which file is actually loaded into the shared Three.js scene (only
// step+dxf use the scene; mmd renders separately via PanZoom). The two
// can briefly disagree during a load — the current file is set first
// so popstate handlers see the new state, then the loader populates
// the scene and updates mounted to match.
export const state = {
  allFiles: [],       // STEP files (paths)
  mmdFiles: [],       // Mermaid files
  dxfFiles: [],       // DXF files
  glbFiles: [],       // GLB assemblies (board 3D models)
  drawingFiles: [],   // Line-art SVG files (drawings/ convention)
  pcbBoards: [],      // PCB boards: {source, name, dir, top, bottom, overlay, inners, picks}
  cards: [],          // Assembly cards, deck-ordered: {path, code, title, subsystem, accent, …} (contracts/api-shapes.js)
  currentDetail: null,
  mountedDetail: null,
  currentMmdContent: null,
  currentMmdWrapper: null,    // host div inside the modal (PanZoom container)
  currentMmdPz: null,         // PanZoom handle for currentMmdWrapper
  currentMmdMinimap: null,    // Minimap handle (pan-zoom-extras.makeMinimap)
  currentDrawingContent: null,
  currentDrawingWrapper: null,// host div inside the modal (PanZoom container)
  currentDrawingPz: null,     // PanZoom handle for currentDrawingWrapper
  currentDrawingMinimap: null,// Minimap handle
  currentCardWrapper: null,   // host div inside the modal (PanZoom container) for an open card
  currentCardPz: null,        // PanZoom handle for currentCardWrapper
  currentCardMinimap: null,   // Minimap handle
  currentPcbSource: null,     // source path of the open board
  currentPcbViews: null,      // {top,bottom,overlay,inner1,…} SVG text for the open board
  currentPcbView: null,       // which view is showing ("top"|"bottom"|"overlay"|"inner1"…)
  currentPcbWrapper: null,    // host div inside the modal (PanZoom container)
  currentPcbToggle: null,     // the view segmented control element (Top/Inner/Bottom/Overlay)
  currentPcbPz: null,         // PanZoom handle for currentPcbWrapper
  currentPcbMinimap: null,    // Minimap handle
  currentPcbPicks: null,      // {pads,unitsPerMm} pad-picker data for the open board
  currentPcbEdit: null,       // {name,components} dev-only editor data for the open board (null in prod)
  currentCadWrapper: null,    // host div inside the modal (parent of canvases)
  currentCadResizeObserver: null,
  currentGroup: null,         // Three.js group currently in scene
  hiddenComponents: new Set(), // component-picker.js: names hidden in the local view (per open file);
                              // repopulated from localStorage on each STEP load, applied to mesh.visible
  thumbnailCache: new Map(),  // STEP file -> dataURL
  mmdThumbCache: new Map(),   // Mermaid file -> svgHTML
  dxfThumbCache: new Map(),   // DXF file -> dataURL
  glbThumbCache: new Map(),   // GLB file -> dataURL
  drawingThumbCache: new Map(),// Drawing file -> svgText (used for both thumbnail and detail)
  pcbThumbCache: new Map(),   // PCB board source -> Top-view svgText (thumbnail)
  stepEtags: new Map(),       // file -> last loaded ETag (for refetch dedupe)
  dxfEtags: new Map(),        // file -> last loaded ETag
  glbEtags: new Map(),        // GLB file -> last loaded ETag
  dxfMeta: new Map(),         // DXF file -> {thickness_mm, material} from sidecar (hardware/README.md)
  gridEl: null,               // set by main.js after DOM ready
  codeVersion: null,          // cache-bust token for re-importing the render modules (loaders.js /
                              // detail-shims.js); null = page-load code is current. Set to the build
                              // commit on a prod deploy (live.js DEPLOY) and to a change nonce on a dev
                              // viewer-source save (live.js CODE_CHANGED), so a code edit is picked up
                              // in place.
  svgIdSeq: 0,                // monotonic token source for pcb.js's per-instance SVG id rewrite; lives
                              // here (not module-local) so it stays unique across a hot re-import of
                              // pcb.js — a reset counter would re-issue "__b1" and collide with a grid
                              // card's ids (the mask-clearance bug pcb.js's uniquifySvgIds guards).
  mmdRenderSeq: 0,            // same, for mermaid.js's transient render ids.
};
