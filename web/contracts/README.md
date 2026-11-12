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
  `web/public/js/viewer/{pcb,pcb-pick}.js`; pinned by `web/tests/picks-schema.test.js`.
- **pcb-out.js** — the board `out/` render layout: view filenames + the `/api/pcb-*` path
  confinement. Produced by `hardware/pcb/pcba/render-board.ts`; read by `web/lib/{walk,viewer-routes}.js`.
- **mesh payloads** — native part arrays and face contributors come from
  `tools/hsm/kernel/src/write.rs`; `tools/hsm/print-payload/` derives viewer surfaces from
  print meshes. `hardware/assembly/scenes/model_export/` writes shared part references and
  placements, and `tools/hsm/build-data/src/payload.rs` reads the flat container for build
  and publication bookkeeping. The browser's `mesh-payload.js` and `shared-scene.js` retain
  those arrays, identities and source records. A `.step` route can name a model whose
  published representation is its `.step.mesh`, with no standalone STEP export.
- **sidecar.js** — `<part>.{step,dxf}.json`: `{thickness_mm, material, process, notes}` authored
  beside a part. Read by `web/lib/viewer-routes.js` (`/api/dxf`) and `web/public/js/viewer/dxf.js`;
  pinned by `web/tests/sidecar.test.js`.
- **documents.js** — a PDF the site hands over whole: the `<name>.pdf.json` sidecar that makes one
  a document and, for a guide, the `<name>.cover.png` beside it. Written by whatever builds the document
  (`hsm-manual-guides` and `hsm-fabrication-guides` for shop books); read by `web/lib/{walk,viewer-routes}.js` and
  `web/public/js/viewer/grid.js`.
- **missing-parts.js** — which runs a machine's published `<model>.facts.json` says the machine
  does not complete, the tubes and fittings each of those lacks, and the scene bodies that stand
  for a run's two ends. The installed machine writes the facts; read by
  `web/lib/viewer-routes.js` (`/api/step-missing`) and
  `web/public/js/viewer/missing-parts.js`, which says them over the model; pinned by
  `web/tests/missing-parts.test.js`.

## The shape of the machine

The tree a page is a browse of. It states the one thing the repository's own files do not — where a
directory stands relative to the others — and reads everything else off disk, so a part added on the
tree needs no edit here.

- **parts-tree.js** — the two units `/3d` browses (the soda machine, which holds the cold core,
  and the faucet and umbilical), the directories each places from, the bought geometry no one of them
  owns, and the tooling a bench works from, including the fixture namespace; plus
  `seatParts`, which walks that nesting and folds a part's `.step` / `.dxf` / `.glb` into one card.
  Read from `/api/{steps,dxf,glbs}` by `web/public/js/viewer/parts.js`; pinned by
  `web/tests/parts-tree.test.js`.
- **component-sources.js** — which file a named solid inside an assembly was modelled in, for the
  ones whose name is not its file's stem; plus `sourceFileFor`, which answers null for the bodies an
  assembly builds and keeps. Read by `web/public/js/viewer/component-picker.js` for the drill-down
  into a selected component; pinned by `web/tests/component-sources.test.js`.
- **part-costs.js** — each part number's cost rolled up through its BOM: its own purchase,
  material, supplies and labor (`costs.direct`, allocated by `web/lib/part-costs.js` from bom.md
  and labor.md and served beside the catalog at `/api/materials`) plus every child's cost times
  its quantity. A labor operation's run (its labor.md Run cell, read the way
  the BOM program reads it) prices it at any batch, and a purchase carries the
  smallest lot batch-forecast.json buys it in. Read by
  `web/public/js/viewer/{material-panel,parts}.js`, `web/lib/{part-cost-view,cost,batch-forecast}.js`.
- **material-quantities.js** — physical contents through assembly levels and supported
  material configurations, shared by `web/lib/{part-costs,material-stock}.js`.
- **material-stock.js** — material demand after completed-stock credits, shared supply
  requirements and build capacity. Reads the catalog and projected stock from
  `web/lib/material-stock.js`; consumed by the material explorer, Build from stock
  and the purchasing forecast.
- **faucet-options.js** — the Sculpted and Industrial faucet assemblies and their part paths,
  plus the Black/White PET-GF finish palette and the exact bodies that take it. Both styles
  use the same assembly frame. Read by the viewer's faucet controls, material builder and
  owner-aware component drilldown; pinned by `web/tests/faucet-options.test.js`.

## Transport & client interface

- **api-shapes.js** — the `/api` endpoints and their responses (PathList, DxfItem, Board, Document). Produced
  by `web/lib/viewer-routes.js`; consumed by `web/public/js/viewer/main.js`.
- **ws-frames.js** — the `/ws` WebSocket frames (hello, ping, files-changed). Produced by
  `web/lib/events.js` and read by `web/public/boot.js`.
- **client-events.js** — the `hsm:*` window CustomEvents. Shared by `web/public/boot.js`
  and `web/public/js/viewer/*.js`.
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
- **explicit build selection** — `web/scripts/build-deps.js` reads native program declarations,
  inputs and outputs from `tools/hsm/build-plan/graph.json` and `tools/hsm/build-plan/inventory.json`.
  It selects producer targets and their dependents for requested builds.
- **importmap** — the three.js bare specifiers resolve through the importmap in the page.
  `web/lib/templates/viewer-body.html`.
- **progressive publication** — `hsm-print-build` carries completed producer outputs and requests
  `hsm-publish` while other producers continue. Shared mesh objects precede the manifests
  that reference them. `tools/hsm/geometry/src/scene.rs` retains identical scene bytes and
  replaces changed manifests atomically.
