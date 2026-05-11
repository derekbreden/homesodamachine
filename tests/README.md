# tests/

Smoke tests for the Node web server. The bar is "the server boots and the
public route surface answers."

## Run

    npm test

Uses `node --test` (Node 20 stdlib runner), no extra deps. No DB or FCM
credentials required.

## What's covered

- **Boot-time evaluation.** `import { start } from "../server.js"` at the
  top of `smoke.test.js` is the most valuable assertion in the suite. If
  any module under `lib/` throws while loading (the way a stray
  `VIEWER_DEFAULTS` ReferenceError took down a deploy before commit
  8611dfa), `npm test` fails immediately.
- **Route surface.** Every GET that doesn't require a database — landing,
  /3d, /charts, /blog, /settings, the JSON APIs (`/api/steps`,
  `/api/dxf`, `/api/mermaid`, `/api/firebase-config`), the three service
  worker URLs, the favicons + apple-touch-icon, and every static JS file
  imported by an HTML surface. Status code + Content-Type prefix.
- **Legacy redirects.** `/dev`, `/dev/diagrams`, `/dev/mermaid`,
  `/dev/settings` still 301 to their new homes.
- **SSE.** `/api/events` opens, sends a `hello` frame with a `commit`
  field, then is aborted.
- **File passthroughs.** `/steps/*`, `/dxfs/*`, `/api/mermaid-content/*`
  each probe one real file from the tree (skipped if the tree happens
  to be empty for that extension).

## What's NOT covered

- **Anything that requires Postgres.** `/api/subscribe`,
  `/api/push/subscribe`, `/api/push/unsubscribe`,
  `/api/push/subscription`, `/notifications`, and the
  `/api/notifications/*` endpoints all bail out without a DB and aren't
  exercised here. They need a database fixture (integration test, not
  smoke).
- **Real FCM.** Push delivery, token registration, notification banner
  rendering — needs Firebase credentials and a real device. Not in
  scope.
- **UI behavior.** The viewer's grid rendering, modal interactions, glass
  animation physics — all client-side, all behind JS. A puppeteer pass
  would catch some of this; the route smoke is the priority deliverable.
- **Error paths.** Bad-input 400s on `/steps/../etc/passwd` and friends
  are exercised by the dev viewer in normal use; not pinned here.

If a route appears in `lib/*.js` that doesn't appear in
`smoke.test.js`'s route table, decide whether it's "boots without a DB" —
add it — or "needs a fixture" — leave it for a future integration suite
and document why in the deliberately-not-tested comment at the bottom of
`smoke.test.js`.
