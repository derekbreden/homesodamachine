# tests/

Seventeen files over `node --test`, run as `tests/**/*.test.js`. The bar is that
the server boots, the public route surface answers, and the contracts under
`web/contracts/` agree with the tree they describe.

## Run

    npm test              # this directory, no browser, no DB
    npm run test:browser  # tests/browser/, a Chromium launch

Node's stdlib runner (`>=22`, per `package.json`), no extra deps.

## What's covered

- **Boot-time evaluation.** `import { start } from "../server.js"` at the
  top of `smoke.test.js` is the most valuable assertion in the suite. If
  any module under `lib/` throws while loading (the way a stray
  `VIEWER_DEFAULTS` ReferenceError took down a deploy before commit
  8611dfa), `npm test` fails immediately.
- **Route surface.** Every GET that doesn't require a database — landing,
  /3d, /charts, /settings, the JSON APIs (`/api/steps`,
  `/api/dxf`, `/api/mermaid`, `/api/firebase-config`), the three service
  worker URLs, the favicons + apple-touch-icon, and every static JS file
  imported by an HTML surface. Status code + Content-Type prefix.
- **Legacy redirects.** `/dev`, `/dev/diagrams`, `/dev/mermaid`,
  `/dev/settings` still 301 to their new homes.
- **WebSocket.** `/ws` accepts a connection and receives a `hello`
  frame carrying a `commit` field on connect.
- **File passthroughs.** `/steps/*`, `/dxfs/*`, `/api/mermaid-content/*`
  each probe one real file from the tree (skipped if the tree happens
  to be empty for that extension).
- **Contracts.** `picks-schema`, `sidecar`, `scorecard-sidecar`,
  `component-sources`, `cards` and `contracts-browser` hold each contract
  under `web/contracts/` against the artifacts and the browser code that
  read it.
- **Walkers and seating.** `walk` pins how a PCB board is discovered;
  `parts-tree` pins that every file the walkers offer is claimed — by an
  assembly's model, by the shelf under them, or by a directory an assembly
  places from; `deps` pins the rebuild ordering the dev-server and
  `build-all` walk.
- **Text-only readers.** `updates` parses the feed's frontmatter and order,
  `pick-format` the edge-picker's copy blobs.
- **Dev-only editors.** `step-editor` and `pcb-editor` gate the write-back
  routes that only exist under `npm run dev`.

## What it does not hold

- **The machine's shape.** Which assemblies exist, which parts fill a
  branch, what a readout chip reads, which order a grid lays out. Those
  move with the hardware, and `/3d` and `/pcb` render them from the tree at
  request time.
- **Anything that requires Postgres.** `/api/subscribe`,
  `/api/push/subscribe`, `/api/push/unsubscribe`,
  `/api/push/subscription`, `/notifications`, and the
  `/api/notifications/*` endpoints bail out without a DB, and nothing here
  stands one up.
- **Real FCM.** Push delivery, token registration, notification banner
  rendering. Firebase credentials and a real device.
- **UI behavior.** Grid rendering, modal interactions, glass animation
  physics — client-side, behind JS. `lazy.js` is held at source level here;
  the window itself is a browser's answer.
- **Error paths.** Bad-input 400s on `/steps/../etc/passwd` and friends
  are exercised by the dev viewer in normal use.

A route in `lib/*.js` that answers without a database belongs in
`smoke.test.js`'s route table. One that needs a fixture is named in the
deliberately-not-tested comment at the bottom of that file.
