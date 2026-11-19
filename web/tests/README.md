# tests/

The `*.test.js` files here run under `node --test`, as `tests/**/*.test.js`. The bar is that
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
  08b908b), `npm test` fails immediately.
- **Route surface.** The public pages, model and document lists, app icons, and browser modules have smoke coverage.
  The retired push worker URLs return the script that removes existing browser registrations.
- **Legacy redirects.** `/dev`, `/drawings` and `/pcb` return redirects.
- **WebSocket.** `/ws` accepts a connection and receives a `hello`
  frame carrying a `commit` field on connect.
- **File passthroughs.** `/steps/*` and `/dxfs/*`
  each probe one real file from the tree (skipped if the tree happens
  to be empty for that extension).
- **Contracts.** `picks-schema`, `sidecar`, `scorecard-sidecar`,
  `component-sources`, `cards` and `contracts-browser` hold each contract
  under `web/contracts/` against the artifacts and the browser code that
  read it.
- **Walkers and seating.** `walk` checks how a PCB board is discovered.
  `parts-tree` checks how model paths are assigned and that the website's
  artifact pointers include a model for each assembly. `deps` checks the
  rebuild ordering used by `build-all`.
- **Text-only readers.** `updates` parses the feed's frontmatter and order,
  `pick-format` the edge-picker's copy blobs.

## What it does not hold

- **The machine's shape.** The Parts workspace reads the published models.
- **Signup storage.** The suite runs without a database and does not write subscriber rows.
- **UI behavior.** The browser suite covers catalog links and modal interactions.
- **Error paths.** Bad-input 400s on `/steps/../etc/passwd` and friends
  are exercised by the dev viewer in normal use.

A route in `lib/*.js` that answers without a database belongs in
`smoke.test.js`'s route table. One that needs a fixture is named in the
deliberately-not-tested comment at the bottom of that file.
