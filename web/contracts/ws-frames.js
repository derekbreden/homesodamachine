// The WebSocket wire — server -> client push over /ws (web/lib/events.js). The client is
// web/public/boot.js and only receives; it never sends. A reconnecting client catches up via the
// `recent` snapshot on the next hello. Broadcasts follow deploys and artifact adoption.

export const WS = {
  HELLO: "hello",                 // on every connect: { type, commit, time, recent? }
  PING: "ping",                   // 30s heartbeat: { type, t }
  FILES_CHANGED: "files-changed", // { type, commit?, files: string[] } — CAD/board artifact paths
};

/** @typedef {{ type: "hello", commit: string, time: number, recent?: Recent }} Hello */
/** @typedef {{ type: "ping", t: number }} Ping */
/** @typedef {{ type: "files-changed", commit?: string, files: string[] }} FilesChanged */
/** @typedef {{ commit: string, ts: number, files?: string[] }} Recent latest boot-diff, replayed on reconnect */
