// The WebSocket wire — server -> client push over /ws (web/lib/events.js). The client is
// web/public/boot.js and only receives; it never sends. A reconnecting client catches up via the
// `recent` snapshot on the next hello. Broadcasts originate in web/server.js (boot-time hash diff)
// and web/dev-server/server.js (chokidar file-change). The client matches on the exact type tags.

export const WS = {
  HELLO: "hello",                 // on every connect: { type, commit, time, recent? }
  PING: "ping",                   // 30s heartbeat: { type, t }
  FILES_CHANGED: "files-changed", // { type, commit?, files: string[] } — CAD/board artifact paths
  POSTS_CHANGED: "posts-changed", // { type, commit?, posts: object[] } — blog entries
  CODE_CHANGED: "code-changed",   // { type, version } — dev-only: a viewer render module was edited (web/dev-server watches web/public/js/viewer); version is the cache-bust token the client re-imports the leaf loader under
};

/** @typedef {{ type: "hello", commit: string, time: number, recent?: Recent }} Hello */
/** @typedef {{ type: "ping", t: number }} Ping */
/** @typedef {{ type: "files-changed", commit?: string, files: string[] }} FilesChanged */
/** @typedef {{ type: "posts-changed", commit?: string, posts: object[] }} PostsChanged post item shape: describeChangedPosts in web/lib/push.js */
/** @typedef {{ type: "code-changed", version: string }} CodeChanged dev viewer-source hot-reload signal */
/** @typedef {{ commit: string, ts: number, files?: string[], posts?: object[] }} Recent latest boot-diff, replayed on reconnect */
