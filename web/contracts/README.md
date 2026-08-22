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
- **cards.js** — the assembly deck: where cards live (`assembly/cards/<code>-<slug>.html`), the
  1800 × 1200 canvas they're authored against, and which of the deck's files `/cards/*` will serve.
  Authored in `hardware/assembly/cards/`; read by `web/lib/{walk,viewer-routes,push}.js`
  and `web/dev-server/server.js`; pinned by `web/tests/cards.test.js`.
- **documents.js** — a PDF the site hands over whole: the `<name>.pdf.json` sidecar that makes one
  a document and the `<name>.cover.png` beside it. Written by whatever builds the document
  (`hardware/assembly/cards/_build.py`); read by `web/lib/{walk,viewer-routes}.js` and
  `web/public/js/viewer/grid.js`.

## The shape of the machine

The tree a page is a browse of. It states the one thing the repository's own files do not — where a
directory stands relative to the others — and reads everything else off disk, so a part added on the
tree appears with no edit here and anything unseated is reported on the page.

- **parts-tree.js** — the three assemblies `/3d` browses (enclosure assembly, cold core, faucet), the
  shelf of what none of them hands over, and the directories they place from; plus `seatParts`, which
  folds a part's `.step` / `.dxf` / `.glb` into one card. Read from `/api/{steps,dxf,glbs}` by
  `web/public/js/viewer/parts.js`; pinned by `web/tests/parts-tree.test.js`.
- **component-sources.js** — which file a named solid inside an assembly was modelled in, for the
  ones whose name is not its file's stem; plus `sourceFileFor`, which answers null for the bodies an
  assembly builds and keeps. Read by `web/public/js/viewer/component-picker.js` for the drill-down
  into a selected component; pinned by `web/tests/component-sources.test.js`.

## Transport & client interface

- **api-shapes.js** — the `/api` endpoints and their responses (PathList, DxfItem, Board, Card). Produced
  by `web/lib/viewer-routes.js`; consumed by `web/public/js/viewer/main.js`.
- **ws-frames.js** — the `/ws` WebSocket frames (hello, ping, files-changed, code-changed). Produced
  by `web/lib/events.js` (broadcasters `web/server.js`, `web/dev-server/server.js`); read by `web/public/boot.js`.
- **client-events.js** — the `hsm:*` window CustomEvents. Dispatched by `web/public/boot.js` (pcb-tool
  by the viewer itself); listened for by `web/public/js/viewer/*.js`.
- **icons.js** — the Feather glyph table and its `<svg>` attributes. Drawn by `web/lib/icons.js`
  into the shell nav and the notification rows, and by
  `web/public/js/viewer/tool-rail.js` into the 3D viewer's tool rail.
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

- **legacy redirects** `/dev`, `/dev/diagrams`, `/dev/mermaid`, `/dev/settings` → 301. `web/lib/viewer-pages.js`.
- **generator detection** — a `.py` is a live-rebuild generator when it calls
  `export_step` / `export_assembly` / `export_dxf` (from `_cadq_export`); STEP-load edges follow
  `importStep` / `_load`. `web/dev-server/deps.js`.
- **deck subsystem order** — the card deck's subsystems, their display names, and their build order
  are read from the `body.xx { --accent }` block in `hardware/assembly/cards/style.css`, the same
  declaration the printed cards colour themselves from. `web/lib/walk.js` (`walkAssemblyCards`).
- **importmap** — the three.js bare specifiers resolve through the importmap in the page.
  `web/lib/templates/viewer-body.html`.
- **deterministic export** — generators write `.step` / `.dxf` atomically and byte-stable, so a no-op
  edit produces no write and the watcher stays quiet. `hardware/scripts/_cadq_export.py`.
