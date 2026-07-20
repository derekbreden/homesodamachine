// Client-side CustomEvents on window — the viewer's in-page signal bus. web/public/boot.js turns
// WebSocket frames (web/contracts/ws-frames.js) and notification state into these; the viewer
// modules (web/public/js/viewer/*.js) listen. Names are the exact strings passed to
// CustomEvent / addEventListener; detail rides on event.detail.

export const HSM_EVENTS = {
  FILES_CHANGED: "hsm:files-changed",                 // { files: string[] } — refresh the changed cards
  POSTS_CHANGED: "hsm:posts-changed",                 // { posts: object[] } — refresh the blog
  DEPLOY: "hsm:deploy",                               // { commit, commitChanged, reconnect? } — new build shipped
  CODE_CHANGED: "hsm:code-changed",                   // { version } — a viewer render module moved; re-import the open detail's loader under this token
  NOTIFICATIONS_UPDATED: "hsm:notifications-updated", // inbox state changed (drives bell + toast)
  PCB_TOOL: "hsm:pcb-tool",                           // viewer-internal: pad-picker / editor tool switch
  STEP_TOOL: "hsm:step-tool",                         // viewer-internal: STEP edge-picker / component-picker tool switch
};

/** @typedef {CustomEvent<{ files: string[] }>} FilesChangedEvent */
/** @typedef {CustomEvent<{ posts: object[] }>} PostsChangedEvent */
/** @typedef {CustomEvent<{ commit: string, commitChanged: boolean, reconnect?: boolean }>} DeployEvent */
/** @typedef {CustomEvent<{ version: string }>} CodeChangedEvent */
