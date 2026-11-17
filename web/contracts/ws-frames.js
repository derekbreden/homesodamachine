// WebSocket frames for deploy detection and live viewer updates.

export const WS = {
  HELLO: "hello",                 // on every connect: { type, commit, time, recent? }
  PING: "ping",                   // 30s heartbeat: { type, t }
  FILES_CHANGED: "files-changed", // { type, commit?, files: string[] } — CAD/board artifact paths
};

/** @typedef {{ type: "hello", commit: string, time: number, recent?: Recent }} Hello */
/** @typedef {{ type: "ping", t: number }} Ping */
/** @typedef {{ type: "files-changed", commit?: string, files: string[] }} FilesChanged */
/** @typedef {{ commit: string, ts: number, files: string[] }} Recent latest publication, replayed on reconnect */
