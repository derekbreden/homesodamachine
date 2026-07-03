// Push + the notifications inbox — how a committed change wakes a device, and the per-token inbox
// behind it. Server: web/lib/push.js (subscriptions, per-kind boot-diff, FCM fan-out) and
// web/lib/notifications.js (inbox CRUD). Client: web/public/boot.js (subscribe, poll, bell + toast)
// and the FCM service worker served by web/server.js. No-ops without DATABASE_URL + FIREBASE_*;
// the boot diff and FCM only run on a real deploy.

// --- Subscription (boot.js -> server) ---
//   POST /api/push/subscribe     body { token, files }   FCM token + the paths it watches
//   POST /api/push/unsubscribe   body { token }
//   GET  /api/push/subscription?token=X   -> the stored subscription, or none

/** @typedef {{ token: string, files: string[] }} PushSubscription */

// --- FCM message (server -> FCM -> device) ---
//   notification: { title, body }          the system banner (iOS / Android / Chrome show it natively)
//   webpush.fcmOptions.link: <url>?n=<id>  deep link to the changed thing; ?n names the inbox row
// One banner per deploy for the file changes (any mix of kinds); posts get their own banner.

// --- Boot-time change detection (web/server.js on prod boot) ---
// Per-kind SHA tables — step_hashes, mermaid_hashes, dxf_hashes, drawing_hashes, pcb_hashes,
// post_hashes — diffed by push.js detect* functions; the changed set drives both the WS
// files-changed / posts-changed broadcast (ws-frames.js) and the FCM fan-out.

// --- Notifications inbox (web/lib/notifications.js) ---
//   GET  /api/notifications?token=X               -> { items: InboxItem[] }   (7-day window)
//   GET  /api/notifications/unread-count?token=X  -> { count }
//   POST /api/notifications/seen                  body { token, ids?, all? }

/** @typedef {{ id: number, kind: string, url: string, title: string, body: string, ts: string, seen: boolean }} InboxItem */
