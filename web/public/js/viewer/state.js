// Shared mutable state for the viewer modules. One exported object so
// every reader/writer sees the same live binding via property access:
// no per-module sync dance, no getter/setter ceremony, no duplicate
// caches. The shape (the keys present and their meaning) IS the
// contract — every module that reads or writes here treats it like
// the file-scope `let` it replaces.
//
// At most one detail surface is open at a time (parts viewer is modal):
//   currentDetail = { type: "step"|"dxf"|"glb"|"material", file } | null
//   mountedDetail = { type: "step"|"dxf",       file } | null
// "current" tracks which file the modal is presenting; "mounted" tracks
// which file is actually loaded into the shared Three.js scene. The two
// can briefly disagree during a load — the current file is set first
// so popstate handlers see the new state, then the loader populates
// the scene and updates mounted to match.
export const state = {
  materialCatalog: null,    // permanent materials, authored BOMs and typed relationships
  materialCatalogTag: null, // the existing HTTP version keeps record views stable during mesh updates
  materialPanel: null,      // active companion panel's select / sync / dispose handle
  dismissViewerRoute: false, // the next history pop ends a dismissed viewer walk
  allFiles: [],       // STEP files (paths)
  documents: [],      // PDFs the site hands over whole: {path, title, subtitle, pages, cover, bytes} (contracts/documents.js)
  currentDetail: null,
  mountedDetail: null,
  currentCadWrapper: null,    // host div inside the modal (parent of canvases)
  currentCadResizeObserver: null,
  currentGroup: null,         // Three.js group currently in scene
  faucetStyle: "sculpted",   // shared by the faucet assembly and its related models
  faucetFinish: "black",     // shared by the faucet assembly and its PET-GF part drilldowns
  stepLoadSeq: 0,            // only the most recent asynchronous CAD request can mount
  cadLoadAbort: null,         // active CAD transfer; shared across hot loader imports
  hiddenComponents: new Set(), // component-picker.js: names hidden in the local view (per open file);
                              // repopulated from localStorage on each STEP load, applied to mesh.visible
  autoHiddenComponents: new Set(), // obstructions hidden around the current selection
  autoHiddenFile: null,
  thumbnailCache: new Map(),  // "<STEP file>@<square px>[@<faucet finish>]" -> dataURL
  memberUrls: new Map(),      // file -> the store's URL for its bytes (/api/objects), when there is one
  memberLoaded: new Map(),    // file -> the store URL last loaded, which is the hash of what is on screen
  stepEtags: new Map(),       // file -> last loaded ETag (for refetch dedupe)
  dxfEtags: new Map(),        // file -> last loaded ETag
  glbEtags: new Map(),        // GLB file -> last loaded ETag
  dxfMeta: new Map(),         // DXF file -> {thickness_mm, material} from sidecar (hardware/README.md)
  gridEl: null,               // guide shelf, when present
  codeVersion: null,          // Deploy commit used to re-import the detail loaders.
};
