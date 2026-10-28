// Client signals shared by boot.js and the viewer. Most are CustomEvents on
// window, with their payload in event.detail. DOCUMENT_* types travel in
// same-origin postMessage data between the embedded reader and its workspace.

export const HSM_EVENTS = {
  FILES_CHANGED: "hsm:files-changed",                 // { files: string[] } — refresh the changed cards
  DEPLOY: "hsm:deploy",                               // { commit, commitChanged, reconnect? } — new build shipped
  CODE_CHANGED: "hsm:code-changed",                   // { version } — a viewer render module moved; re-import the open detail's loader under this token
  NOTIFICATIONS_UPDATED: "hsm:notifications-updated", // inbox state changed (drives bell + toast)
  PCB_TOOL: "hsm:pcb-tool",                           // viewer-internal: pad-picker / editor tool switch
  STEP_TOOL: "hsm:step-tool",                         // viewer-internal: STEP edge-picker / component-picker tool switch
  STEP_MOUNTED: "hsm:step-mounted",                  // { file } — the STEP now drawn in the modal
  MATERIAL_PICKED: "hsm:material-picked",             // { file, name } — component selected in the model; name null when the selection is let go
  DOCUMENT_ESCAPE: "hsm:document-escape",             // embedded document asks to return to its parent view
  DOCUMENT_COMMAND: "hsm:document-command",           // same-origin host → embedded reader: { command, page? }
  DOCUMENT_STATE: "hsm:document-state",               // embedded reader → host: { page, pages, zoom, ready }
  FAUCET_OPTIONS: "hsm:faucet-options",              // viewer-internal: redraw the faucet card from state.faucetStyle / faucetFinish
};

/** @typedef {CustomEvent<{ files: string[] }>} FilesChangedEvent */
/** @typedef {CustomEvent<{ commit: string, commitChanged: boolean, reconnect?: boolean }>} DeployEvent */
/** @typedef {CustomEvent<{ version: string }>} CodeChangedEvent */
