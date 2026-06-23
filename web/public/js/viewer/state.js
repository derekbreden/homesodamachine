// Shared mutable state for the viewer modules. One exported object so
// every reader/writer sees the same live binding via property access:
// no per-module sync dance, no getter/setter ceremony, no duplicate
// caches. The shape (the keys present and their meaning) IS the
// contract — every module that reads or writes here treats it like
// the file-scope `let` it replaces.
//
// At most one detail surface is open at a time (parts viewer is modal):
//   currentDetail = { type: "step"|"dxf"|"mmd", file } | null
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
  drawingFiles: [],   // Line-art SVG files (drawings/ convention)
  pcbBoards: [],      // PCB boards: {source, name, dir, top, bottom, overlay}
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
  currentPcbSource: null,     // source path of the open board
  currentPcbViews: null,      // {top,bottom,overlay} SVG text for the open board
  currentPcbView: null,       // which view is showing ("top"|"bottom"|"overlay")
  currentPcbWrapper: null,    // host div inside the modal (PanZoom container)
  currentPcbToggle: null,     // the Top/Bottom/Overlay segmented control element
  currentPcbPz: null,         // PanZoom handle for currentPcbWrapper
  currentPcbMinimap: null,    // Minimap handle
  currentCadWrapper: null,    // host div inside the modal (parent of canvases)
  currentCadResizeObserver: null,
  currentGroup: null,         // Three.js group currently in scene
  thumbnailCache: new Map(),  // STEP file -> dataURL
  mmdThumbCache: new Map(),   // Mermaid file -> svgHTML
  dxfThumbCache: new Map(),   // DXF file -> dataURL
  drawingThumbCache: new Map(),// Drawing file -> svgText (used for both thumbnail and detail)
  pcbThumbCache: new Map(),   // PCB board source -> Top-view svgText (thumbnail)
  stepEtags: new Map(),       // file -> last loaded ETag (for refetch dedupe)
  dxfEtags: new Map(),        // file -> last loaded ETag
  dxfMeta: new Map(),         // DXF file -> {thickness_mm, material} from sidecar (hardware/README.md)
  gridEl: null,               // set by main.js after DOM ready
};
