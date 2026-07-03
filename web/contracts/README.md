# contracts

The definitions that cross between the builders, the server, and the browser viewer — the shapes,
tags, and file conventions each side has to agree on. Homed here so a change to one sits beside its
siblings. Each entry names its producer and consumers; a definition is written in the language its
code imports (`.ts` where the tscircuit builders share it, `.js` everywhere else). The `.js`
definitions are served to the browser at `/contracts` (`web/server.js`), so the viewer imports the
same file the server does — Node by path, the browser by URL, one source either way.

## Builder → viewer data

- **picks-schema.ts** — `out/<board>.picks.json`: pads/vias/traces the pad picker hit-tests, plus
  the board readout (size) and checks (clearance floor + tight pairs, DRC errors, cap-decoupling
  audit). Produced by `hardware/pcb/pcba/pick-data.ts`; read by
  `web/public/js/viewer/{pcb,pcb-pick,pcb-edit}.js`; pinned by `web/tests/picks-schema.test.js`.
- **pcb-out.js** — the board `out/` render layout: view filenames + the `/api/pcb-*` path
  confinement. Produced by `hardware/pcb/pcba/render-board.ts`; read by `web/lib/{walk,viewer-routes}.js`.
- **sidecar.js** — `<part>.{step,dxf}.json`: `{thickness_mm, material, process, notes}` authored
  beside a part. Read by `web/lib/viewer-routes.js` (`/api/dxf`) and `web/public/js/viewer/dxf.js`;
  pinned by `web/tests/sidecar.test.js`.

## Transport & client interface

- **api-shapes.js** — the `/api` endpoints and their responses (PathList, DxfItem, Board). Produced
  by `web/lib/viewer-routes.js`; consumed by `web/public/js/viewer/main.js`.
- **ws-frames.js** — the `/ws` WebSocket frames (hello, ping, files-changed, posts-changed). Produced
  by `web/lib/events.js` (broadcasters `web/server.js`, `web/dev-server/server.js`); read by `web/public/boot.js`.
- **client-events.js** — the `hsm:*` window CustomEvents. Dispatched by `web/public/boot.js` (pcb-tool
  by the viewer itself); listened for by `web/public/js/viewer/*.js`.
- **hsm-globals.js** — `window.__hsm`, the headless-render escape hatch. Set by
  `web/public/js/viewer/main.js`; read by `tools/render/*.js`.
- **push-notify.js** — the wake-on-commit path: `/api/push/*` + `/api/notifications/*`, the FCM
  message, the boot-diff hash tables. Produced by `web/lib/{push,notifications}.js`; consumed by
  `web/public/boot.js` and the FCM service worker.

## Lives with its code

- **pick-format.js** (`web/public/js/viewer/pick-format.js`) — the clipboard grammar the pickers emit
  and an agent pastes back. Viewer logic (a parser + geometry matcher), not just a shape, so it lives
  with the viewer rather than here; imported by both the browser and its Node test,
  `web/tests/pick-format.test.js`.

## Conventions (enforced in code, no shared module)

- **edition cookie** `hsmEdition` — picks the content root (kitchen / lite). `web/lib/viewer-routes.js`
  reads it; `web/lib/shell.js` mirrors the localStorage choice into it.
- **legacy redirects** `/dev`, `/dev/diagrams`, `/dev/mermaid`, `/dev/settings` → 301. `web/lib/viewer-pages.js`.
- **generator detection** — a `.py` is a live-rebuild generator when it calls
  `export_step` / `export_assembly` / `export_dxf` (from `_cadq_export`); STEP-load edges follow
  `importStep` / `_load`. `web/dev-server/deps.js`.
- **drawings/ convention** — a line-art `.svg` counts only inside a `drawings/` directory.
  `web/lib/walk.js` (`walkFilesUnderDir`), served via `/api/drawing-content`.
- **importmap** — the three.js bare specifiers resolve through the importmap in the page.
  `web/lib/templates/viewer-body.html`.
- **deterministic export** — generators write `.step` / `.dxf` atomically and byte-stable, so a no-op
  edit produces no write and the watcher stays quiet. `hardware/scripts/_cadq_export.py`.
