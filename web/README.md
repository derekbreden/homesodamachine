# web/

The Node web server for **homesodamachine.com** + the browser-rendered viewer at `/3d` and `/charts`. No bundler. Runs on Render as a single web service, plus a Postgres add-on for the notification inbox and FCM hash tables. The dev story is the same code with a chokidar wrapper.

The hardware/firmware/CAD content the site presents lives in [`hardware/`](/hardware/) at the repo root — that side is its own world (CadQuery, KiCad, ESP-IDF). This document covers the web layer only.

## Website style reference

The [website style guide](https://homesodamachine.com/style-guide) is a small working example page for agents and contributors. Read it when adding or changing a web surface. It shows text and color roles, links, buttons, search, selected material rows, tabs and an expandable cost panel, with usage notes, copyable markup and production source links.

The home page sets the visual language: Montserrat, cobalt introductions, pale content surfaces, navy text and orange accents. [`public/css/site.css`](public/css/site.css) shares its 84rem outer width, responsive gutters, type scale and navigation alignment. Interior pages use `renderPageHeader`, a `site-content` main and `renderFooter({ siteFooter: true })` from [`lib/shell.js`](lib/shell.js). Text articles keep a narrower reading column inside those proportions. Immersive CAD tools retain their dark work surfaces; the model shelf uses pale backgrounds and separately rendered thumbnails. Owner pages and the document reader share the typeface and surface colors with layouts suited to setup and reading.

[`lib/style-guide.js`](/web/lib/style-guide.js) uses the shared shell, the exported cost and landing-button CSS, and [`public/css/materials.css`](/web/public/css/materials.css) directly. [`public/css/style-guide.css`](/web/public/css/style-guide.css) supplies documentation layout; [`public/style-guide.js`](/web/public/style-guide.js) supplies local demonstrations and reads displayed font sizes and colors from the browser. Match an existing pattern by its role and importance. Add examples when another reusable pattern needs a reference; correct existing pages where a specific problem is identified.

## Home page audience

The home page is for someone who knows little more than "soda machine" and has no earlier context. Its main job is to explain the equipment under the kitchen counter, the dedicated faucet above it, and cold, carbonated soda poured into a glass. The integrated appliance is presented as under development. The one-time availability notification signup is a small secondary feature after the explanation. The [home page audience brief](/marketing/lincoln/working-materials.md#home-page-audience-brief) sets the priorities for [`lib/landing.js`](/web/lib/landing.js).

## Running it

```bash
cd web
npm ci             # installs package-lock.json exactly — what Render runs
npm start          # production server (port 3001 by default; PORT env overrides)
npm run dev        # dev wrapper: chokidar + Python runner + WebSocket hot reload (port 3000)
npm run dev -- --no-watch  # same server, no watchers: nothing rebuilds on save
npm test           # route mount, walkers, contracts — no browser, no DB
npm run test:browser # the browser pass (tests/browser/), on demand
npm run build      # rebuild every CAD generator + PCB board, producers first (minutes)
npm run build:check # same, then exit 1 if a rebuild moved anything — the fix is left in the tree
npm run subscribers # the signup list; DATABASE_URL comes from Render's dashboard
```

`npm start` boots `server.js` directly — what Render runs in production. `npm run dev` adds the file watcher that re-runs CadQuery generator scripts when a CAD source changes and pushes file-change events over the WebSocket so an open `/3d` page hot-reloads its thumbnails. A "generator" is any part-named `.py` under `hardware/` that calls `export_step` / `export_assembly` / `export_dxf` from `_cadq_export`; the watcher detects them by content, not filename. `--no-watch` serves the same site with no chokidar at all — no generator runs, no board renders, no thumbnails, no hot-reload broadcast — so an edit anywhere in the tree costs nothing and the viewer shows what is on disk until you reload it. Set `DATABASE_URL` to enable the notification inbox + FCM push paths; both no-op without a DB so dev works fine without one.

## Dependencies

The Wiring section of `/cost` contains the `/cost#j2-harness` and
`/cost#j13-harness` assembly guides. Their connections, materials and estimates
come from `hardware/assembly/harnesses/j2.json` and `j13.json`;
`lib/harness-guide.js` renders each workbench and its text fallback.
`public/js/harness/main.js` lazily initializes each Three.js model as its guide
approaches the viewport. Clicking a conductor highlights it; the separate
**Open conductor** action opens its end-to-end view. The Build and Parts panels
keep the assembly sequence and components beside the model.

On phone and tablet widths, each guide is a tappable 3D preview. Opening it
uses the full viewport width, with the inspector beneath the model and a
Close button above it. Desktop Expand uses the same dialog. Pinching zooms
the model, and multi-touch gestures do not select conductors.

The harnesses and CAD viewer share `public/js/viewer/navigation.js`: free
Trackball rotation, right-drag and two-finger pan, surface-aware zoom,
ViewCube snaps and camera persistence. Rotate, Pan and Zoom choose the
one-finger or left-drag action. Reset view preserves the assembly state.
`axis-rulers.js` and `xray-render.js` provide the same instance-owned rulers
and x-ray rendering to both viewers. Harness rulers switch to the native
PCB view, where the geometry has a physical millimeter scale. Find searches
conductors, endpoints and parts; selections can be hidden and restored.

Both guides include a crop of the native PCB geometry and its printed labels,
with crop assets and provenance in `public/harness/`. Cable reach is compressed
for the bench view; it does not specify installed routing. The labor ledger
includes J2's ten minutes and J13's five minutes once within
Wiring, with the other harnesses listed as individual estimates and
installation counted separately. These are theoretical, unmeasured unit-25
estimates for practiced hands with the map, tools and materials ready;
development and lookup time are excluded.

Regenerate the native PCB crops on demand with
`tools/cad-venv/bin/python tools/harness/extract-j2-board.py J2 J13` from the
repository root. The producer clips the published PCB and embeds its original
fabrication pixels; the provenance records its source hashes and bench pose.

`package-lock.json` is tracked, and is what the deployed site installs. `render.yaml` installs it with `npm ci --omit=dev`, which resolves nothing and stops when the lockfile and `package.json` disagree.

`overrides` pins `uuid` to `^11.1.1`. Below that it misses a buffer bounds check in its v3/v5/v6 generators. It arrives four levels down — `firebase-admin` → `@google-cloud/storage` → `retry-request`/`teeny-request` → `uuid` — and again through `gaxios`.

Node 22 is the floor, in `engines` and in `.node-version`: `firebase-admin` 14 declares `>=22`, and Render reads `.node-version` from the service's root directory. `npm run audit` reads the production half of the tree.

## Page request lifecycle

```
HTTP GET /<path>
   │
   ▼
server.js  ── start({ dev }) ──┬─ pg.Pool from DATABASE_URL (null if missing)
   │                            ├─ initPush(serviceAccountJson)
   │                            └─ for each lib/<name>.js:
   │                                  mountXxxRoutes(app, …)        // attaches GET handlers
   │
   ▼  (route handler in lib/<name>.js)
res.send(
  renderHead({…})          // <head>: meta, fonts, /css/site.css, HEAD_TAGS, page styles
  + renderNav({active})
  + <body fragment>        // either inline HTML or a template fragment from lib/templates/
  + renderFooter()
)

Browser receives HTML. Inline pre-paint <script> sets the notifs-enabled
class from localStorage. Then deferred /boot.js runs (SW bridge, notifications
state, WebSocket owner, /api/version activation check). Then any page-specific
module (/landing.js, /js/viewer/main.js, etc.).
```

The single shared shell is [`lib/shell.js`](/web/lib/shell.js). Every page uses `renderHead` and `renderFooter`. Public and engineering pages use `renderNav`, which draws the same icons everywhere: Home, Latest, Parts, Charts, Drawings, Boards and Cost, then the bell and the gear. Latest opens the `/latest` hub, where Changes and Updates both begin, and stands lit anywhere in either feed. Unit pages have their own named navigation: Your machine, Get started, and Guides.

## Module layout

### `lib/` — server-side

| Module | Mounts | Responsibility |
|---|---|---|
| [`server.js`](/web/server.js) | `/api/version` | Entry; orchestrates the pool, push init, route mounts, WebSocket broadcast diff loop on prod boot. Serves the live build commit at `/api/version` for boot.js's activation check. |
| [`lib/shell.js`](/web/lib/shell.js) | — | `renderHead` / `renderNav` / `renderFooter`. Owns the synchronous pre-paint class flips and the `<script src="/boot.js" defer>` tag. |
| [`lib/landing.js`](/web/lib/landing.js) | `/` | Appliance overview with CAD-based kitchen and detail illustrations. [`lib/landing-support.js`](/web/lib/landing-support.js) supplies the optional film, supplier acknowledgements and secondary availability signup. |
| [`lib/unit.js`](/web/lib/unit.js) | `/0001`, `/0001/get-started`, `/0001/guides` | Machine overview, included equipment, preparation checklist, and owner documents. Only serials registered in this module resolve. |
| [`lib/cost.js`](/web/lib/cost.js) | `/cost` | Parts, planned batch labor, sale price, investment recovery and remaining-purchase forecasts for the first 5/10/20 machines. Reads the parts, labor, machine-time, purchase and batch-forecast ledgers. [`lib/batch-forecast.js`](/web/lib/batch-forecast.js) deducts dated stock and already-ordered quantities before comparing whole purchase lots. [`lib/batch-forecast-view.js`](/web/lib/batch-forecast-view.js) renders ranked purchase bars and collapsible stock, supply and cash-budget details; [`lib/cost-categories.js`](/web/lib/cost-categories.js) shares the BOM category names between both cost views. |
| [`lib/viewer-pages.js`](/web/lib/viewer-pages.js) | `/3d`, `/charts`, `/drawings`, `/pcb` | The viewer pages — parts, charts, the documents shelf, boards. All render [`lib/templates/viewer-body.html`](/web/lib/templates/viewer-body.html). |
| [`lib/weld-position.js`](/web/lib/weld-position.js) | `/weld-position` | Tube, recessed endcap and gun orientation; grip, hole and vertical rotations about the laser dot. |
| [`lib/viewer-routes.js`](/web/lib/viewer-routes.js) | `/api/{steps,dxf,mermaid,documents}`, `/steps/*`, `/dxfs/*`, `/read/*`, `/docs/*`, `/api/mermaid-content/*` | API for the viewer's file lists and content, plus document publication gates. |
| [`lib/document-reader.js`](/web/lib/document-reader.js) | `/vendor/pdfjs/<version>/*` | Document reader HTML and the installed PDF.js assets. `/read/*` renders one page at a time through `public/document-reader.js`, with page links, history, selectable text and zoom. `/docs/*?raw=1` supplies range-capable PDF bytes; `?download=1` supplies an attachment. HTML navigations to saved `/docs/*` links redirect to the reader. |
| [`lib/changes.js`](/web/lib/changes.js) | `/changes`, `/changes/<id>`, `/changes/<id>/<file>`, `/api/changes` | Before-and-after feed of recorded changes, newest first. Reads `changes/<id>/entry.md` (frontmatter + the Updates markdown subset) and `views.json` (each view's Before and After images, pixel size and marks); [`changes/README.md`](/changes/README.md) is how an entry is made. Serves the cards, `/api/changes?before=<id>` pages for the infinite scroll, the entry page and its `?fragment=1` modal body, and only the images a view names. Entries do not deploy: on the deployed container it carries those committed since its clone from GitHub when the feed is asked for — main's root tree, then the `changes/` subtree only when it moved, at most once a minute, standing down below 20 calls left in the shared hour. |
| [`lib/latest.js`](/web/lib/latest.js) | `/latest` | The hub the nav's Latest item opens. Changes, then Updates: each section's name, a line on what it is, its newest items as thumbnails and a link into the whole feed. A change's thumbnail is its first view cut down the middle, the Before's left half against the After's right; a post's is its `image`, else its `image_fig`; an item with neither carries its words in the same frame. Each thumbnail opens its item at `/changes/<id>` or `/updates/<slug>`. The entries come through the reader `mountChangesRoutes` hands back, and the page waits on the same carry. |
| [`lib/settings.js`](/web/lib/settings.js) | `/settings` | Per-user toggles: FCM enable, live-reload debug. |
| [`lib/style-guide.js`](/web/lib/style-guide.js) | `/style-guide` | Production-style examples, usage notes, markup and source links. Sample material names and quantities come from the catalog. |
| [`lib/events.js`](/web/lib/events.js) | `/ws` | WebSocket channel. One socket per page: deploy hello-handshake + ping heartbeat + `files-changed` broadcasts. |
| [`lib/notifications.js`](/web/lib/notifications.js) | `/api/notifications/*`, `/notifications` | Per-token inbox CRUD + the `/notifications` page. |
| [`lib/push.js`](/web/lib/push.js) | `/api/push/*` | FCM subscriptions + outbound notify; boot-time hash diff against per-kind tables. |
| [`lib/walk.js`](/web/lib/walk.js) | — | Shared `walkFiles(rootDir, exts)` helper, plus the per-kind walkers (`walkPcbBoards`, `walkDocuments`). |
| [`lib/icons.js`](/web/lib/icons.js) | — | Shared SVG glyphs (cube, chart, gear, bell, scissors, clipboard). |

The pattern: `export function mountXxxRoutes(app, { … } = {})`. `server.js` calls each in sequence. To add a new page or API surface, add `lib/foo.js` with `mountFooRoutes`, import and call it from `server.js`.

### `public/` — browser-side

Served flat via `express.static(public/)`.

| File | Loaded on | Role |
|---|---|---|
| [`public/boot.js`](/web/public/boot.js) | every page (`<script defer>`) | SW navigate bridge, notifications state mirror + bell + toast + warm-tap auto-redirect, WebSocket owner, `/api/version` deploy/activation check (reloads the page on a new build unless the viewer claims it via `window.__hsmDeploySoft`). Module-local state — never touches `window.__hsm`. |
| [`public/landing.js`](/web/public/landing.js) | `/` | Loads the film player when its local poster is activated; handles availability signup and feedback. The poster links to YouTube without JavaScript. |
| [`public/landing/`](/web/public/landing/) | `/` | Kitchen and component illustrations rendered from the current CAD meshes by [`../tools/render/render-kitchen-scene.py`](../tools/render/render-kitchen-scene.py), plus the film poster. The scene renderer is run on demand. |
| [`public/suppliers/`](/web/public/suppliers/) | `/` | White logos for the landing page's suppliers section, each from the supplier's own site. Fresh Water Systems: its white footer logo. JLCPCB: its header logo, the `logo` glyph (U+E6CC) of its icon font, written as a path. SendCutSend: the approved white logo from its [brand assets](https://sendcutsend.com/brand-assets/) page, its canvas trimmed to the artwork; the approved colors are black, red and white, and only its approved logos may be used. Lulu: its site logo, filled white. |
| [`public/cost.js`](/web/public/cost.js) | `/cost` | Cost overview navigation and sales scenario controls. Three accordion cards show per-unit cost, investment recovery and the 5/10/20 forecast in that order, with headline totals visible while collapsed. Jump links and direct section links reveal the relevant card; recovery controls update its summary. `cost-recovery.js` shares recovery math and the SVG chart with the server. `batch-forecast.js` selects the 5/10/20 plan, defaults to Parts category, and filters suppliers and stock-covered parts. Compact purchase lists scroll; each item expands for source, lots and stock evidence. The overview, category grouping and all three batch disclosures work without JavaScript. |
| [`public/unit.js`](/web/public/unit.js) | Unit pages | Opens the included-equipment disclosure from its link and saves preparation checkmarks in this browser, keyed by serial. Navigation and documents are server-rendered links. |
| [`public/changes.js`](/web/public/changes.js) | `/changes` | Loads more cards as the feed scrolls and opens a card's entry in ContentViewer with its `/changes/<id>` URL pushed, so Back closes it. A tap on a picture, or ← and →, flips each view between Before and After; without it the cards are links, the feed ends in a link to older entries, and the views are radios. |
| [`public/settings.js`](/web/public/settings.js) | `/settings` | Notification + live-reload debug toggles. |
| [`public/style-guide.js`](/web/public/style-guide.js) | `/style-guide` | Local sample search, tabs, row selection, copy markup and computed style readouts. |
| [`public/brand/mark.svg`](/web/public/brand/mark.svg) | every page | The faucet mark in the Home link and landing hero. Generated from [`../brand/mark.svg`](../brand/mark.svg) by [`../tools/build_brand_assets.py`](../tools/build_brand_assets.py). |
| [`public/pan-zoom.js`](/web/public/pan-zoom.js) | `/3d`, `/charts` | Generic pan + pinch-zoom + wheel-zoom. |
| [`public/content-viewer.js`](/web/public/content-viewer.js) | `/3d`, `/charts` | Modal singleton: open / close / swipe-down / Esc / X / backdrop. |
| `public/js/viewer/*.js` | `/3d`, `/charts` | The parts/charts viewer modules — see below. |
| `public/css/viewer.css` | `/3d`, `/charts` | Viewer-specific styles. |

### `public/js/viewer/` — the parts viewer modules

`/3d` and `/charts` share one module graph (the entry decides what to show based on `location.pathname`). Each module is a browser-native ES module loaded via the importmap in [`lib/templates/viewer-body.html`](/web/lib/templates/viewer-body.html).

| Module | Role |
|---|---|
| `state.js` | Single exported `state` object holding all shared mutable refs (`allFiles`, `currentDetail`, `mountedDetail`, caches, etag maps, `gridEl`). Every other module reads/writes through `state.X`. |
| `scene.js` | Three.js renderer/camera/controls/scene/lighting + ViewCube + animate loop + per-file camera persistence + canvas reparenting (canvases live in `#cad-canvas-host` between opens). |
| `step.js` | STEP loader (occt-import-js), parser, mesher, thumbnail renderer. |
| `faucet-options.js` | The faucet's Sculpted/Industrial style and Black/White finish controls. Style swaps actual assembly payloads in the same view; finish recolors the printed exterior, lever, above-counter gasket, soda faucet tube, including their direct part views. The continuous black 4 mm flavor tubes retain their stock color in both finishes. On narrow screens the choices expand from a compact summary. |
| `xray.js` | The X-ray toggle. Every model, and every card's picture, draws solid until x-ray is turned on; the choice is kept in this browser under `step-xray` and applies to every model. |
| `dxf.js` | DXF loader, parser and extrusion mesher. No page draws a card for a cut, so a `.dxf` is reached by opening it. |
| `mermaid.js` | Mermaid renderer (lazy-loaded library), thumbnail renderer, modal detail flow with PanZoom. |
| `cad-detail.js` | Shared modal flow for STEP+DXF (`openCadDetail`/`closeCadDetail`); the `CAD_KINDS` table maps type → ext/hashPrefix/loader. |
| `grid.js` | Card grid per page, `IntersectionObserver` for thumbnail lazy-load. `/3d` hands off to `parts.js`; charts and line art group by a path segment (`categoryAndPartPath`, `groupFilesByCategory`). |
| `parts.js` | `/3d`'s description lookup and cards for the two product units and build tools. Each card draws the model it opens, at the card's own size. The material catalog supplies identities and engineering relationships; uncataloged CAD models remain searchable. |
| `material-search.js` | Description, permanent number, alias and manufacturer-number lookup on the grid and in the model companion. |
| `material-panel.js` | Expandable BOM with quantities through assembly levels, geometry selection, reverse ancestry and linked documents. Context representations inspect a named assembly inside an enclosing model while retaining its own BOM. |
| `material-nav.js` | Permanent `/3d#material:HSM-000001` links and material records with or without geometry. Model drill-downs retain the STEP navigation trail. |
| `live.js` | WebSocket-driven refresh — `hsm:files-changed` listener + `refreshXxxCard` per type for per-file updates; `hsm:deploy` listener that wipes caches and refreshes the whole grid + open modal on a new build. Sets `window.__hsmDeploySoft`. |
| `route.js` | popstate + initial-route translation between URL hash/`?file=` and `currentDetail`. |
| `main.js` | Entry. Sets up nav active class + title, calls `fetchFiles`, applies the initial route. |

State sharing pattern is **one shared object** (`state.js`'s exported `state`). Other modules `import { state } from './state.js'` and read/write `state.allFiles` etc. directly. Live binding via the object identity; no per-module proxy or sync ceremony.

`GET /api/materials` reads [`hardware/ledger/materials.json`](/hardware/ledger/materials.json) through `lib/material-catalog.js`, resolving authored part-list imports such as the insertion fixture's `parts.json`. `contracts/materials.js` traverses quantities, ancestry and model bindings in the browser and Node. [`hardware/ledger/materials.md`](/hardware/ledger/materials.md) describes the catalog's identity and authoring rules. The financial BOM remains [`hardware/ledger/bom.md`](/hardware/ledger/bom.md).

3D thumbnails and plain model or material links start with the material companion collapsed. Search results carry `?panel=materials` and open it on desktop, including in new tabs and browser Back/Forward. Every navigation starts collapsed on narrow screens and touch devices without hover, including landscape phones. The **Materials** button opens a sidebar on desktop and a panel covering the viewer on phones; that manual choice applies to the current view. Entering the phone layout closes the pane. Component selection updates the material record while preserving whether the panel is open or closed. Closing the panel restores the model; material records without geometry open directly as a full panel. `material-panel.js` owns pane visibility and its button state; navigation applies the destination's intent through `applyRoute`.

A material's own engineering drawing is featured above its relationship tabs.
The **3D / Drawing** switch shows it in the model area using the embedded PDF
reader, preserving the model's camera and selection. On phones, opening the
drawing closes the materials pane to reveal the page. The reader retains zoom,
page controls, a full-page link and PDF download; Escape returns to 3D.

Assembly cards, search results and expandable BOM rows show direct and total BOM-item counts. Direct counts cover immediate rows; totals follow every nested assembly path. Each row counts once regardless of its quantity. Faucet counts use the selected style and finish. On desktop, the card's underlined count link opens the Materials pane on its BOM tab; `#material:HSM-000001?tab=bom` preserves that intent in bookmarks and new tabs. On phones the tab is ready when **Materials** is opened. The model link opens with the pane collapsed. The Materials tabs count the displayed BOM's items, recorded uses (containing assembly paths and associated tools/equipment), and distinct linked documents, including documents inherited from containing assemblies.

Every selected component offers **Open component** or its canonical part model. Source lookup uses the material catalog before name aliases. Components without a standalone STEP use a `?component=` view of the owning model's named body or branch, preserving the STEP breadcrumb and browser Back/Forward behavior. The loader reads the owning file and filters its geometry; the view creates no second CAD file or material identity. Picks continue to name the owning geometry file. Cataloged assemblies include numbered records for their fitted tube runs, context geometry and tooling workpieces.

The Puppeteer escape hatch `window.__hsm` is set from `main.js` after all modules have loaded; its shape is part of the contract with [`tools/render/render-step*.js`](/tools/render/) (which lives at the repo root and imports `web/server.js`) and must not change without updating those.

## Unit pages

`/0001` presents the soda machine, faucet, and install kit. Its Get started page links the
seven installation steps to the matching pages of the install guide; Guides opens the quick
start, full booklet, and care pages. The cobalt layout is in `public/css/unit.css`. The common
head supplies boot behavior, icons, and metadata, with IBM Plex Sans and the unit page's theme
color. The pages work without JavaScript; the disclosure's direct link and saved checkmarks
are progressive enhancements.

`public/unit/faucet.webp` is the optimized copy of the install guide's committed
`hardware/install-guide/assets/steps/pour-base.png`. Regenerate it with
`node web/scripts/build-unit-assets.mjs`, using the Sharp dependency in `tools/render/`.

## Tube shape review

Open **Soda machine** at `/3d`, then turn on **Tubes** in the Show tools. Choose an
LLDPE run and use **Show run** to frame it. The cyan dashed line is the CAD route; the coloured
line is an assumed relaxed shape. Fitting exits and actual ties are marked. **Temporarily omit
a hold** recalculates the shape without that restraint; **Reset assumptions** restores every
hold. Selecting a hold, unsupported span or reported contact focuses that location.

The calculation keeps the exposed developed length, fitting exit directions and finite anchor
seats. CAD corner points are free to move. The stock can be assumed straight or curved in either
sense of a selected coil plane, with an adjustable assumed radius. These choices are scenarios,
not measured material memory or bounds on the installed shape. The unloaded, uniform-stiffness
centreline model minimizes bending energy subject to length constraints; it does not model
gravity, pressure, friction, torsion or the stiffness added by insulation. Convergence describes
a local numerical solution. A tightened tie fixes its place along the tube; axial slip through
the tie is not modeled. The stock's bend floor is a reported diagnostic, not an enforced
material law. An unfinished solve remains visibly marked and cannot establish an anchor need.

Capsules around each candidate centreline are screened against the displayed assembly's triangle
surfaces, including hidden parts and other tubes. Sleeves contribute their radius only along
their recorded lengths. The selected tube's own CAD body and co-moving sleeves are excluded;
fitting and anchor contacts are exempted only over their recorded interface intervals. The panel
compares contacts with the CAD route and identifies new locations. Contact is reported, not
resolved: a candidate passing through a part is not a feasible installed shape. Surface screening
does not detect self-contact or a span wholly enclosed inside a solid.

`tube-overlay-host.js` mounts the optional tool; `tube-overlay.js` owns its controls and scene
sibling. The canonical CAD group and its pick geometry are unchanged. A module worker runs
`tube-relaxation.js` and `tube-contacts.js`; mesh bounds and triangle trees are reused between
assumptions. The worker is created on demand and stopped when the tool closes.

The route sidecar is `public/tube-routes.json`, generated by
`hardware/scripts/tube_routes.py` with the CadQuery venv. `/api/tube-routes/manifold-layout/enclosure-assembly.step`
checks the assembly STEP, complete viewer payload and routing input digests before returning it.
The panel refuses stale data. Opening the tool never starts a CAD build.
The current run and hold readings are in
[`hardware/manifold-layout/tube-shapes.md`](/hardware/manifold-layout/tube-shapes.md).

## Cross-module event flow

```
WS  /ws  ─────────────► boot.js                ────► CustomEvent("hsm:files-changed", {files})
                          │                          ────► CustomEvent("hsm:deploy", {commitChanged})
                          ▼                          │
                     fetchNotifications()           │
                          │                          │
focus/visibility/pageshow │                          ▼
   ├─► fetchNotifications()│                     viewer/live.js  → __hsmDeploySoft set: refresh
   └─► GET /api/version ───┘                     grid + open modal in place
        (commit changed? ──► hsm:deploy)         other pages → boot.js reloads on hsm:deploy

FCM  → service worker → notification banner
       (tap → on iOS PWA, page focus → boot.js refetch → maybe redirect; on
        Android/Chrome desktop, SW posts {type:"navigate"} which boot.js handles)
```

Three signals drive the page: the WebSocket push, FCM, and activation (focus/visibility/pageshow). Activation does double duty — it refetches notifications AND polls `/api/version`, so a deploy that the socket missed (suspended PWA, lost `recent` race) still reloads the page the next time it's foregrounded. The notification signals all converge on `fetchNotifications()`, which keeps the local state mirror current and dispatches `hsm:notifications-updated` for the toast + bell.

## Dev vs prod

There is **one server core** ([`server.js`](/web/server.js)). The dev wrapper ([`dev-server/server.js`](/web/dev-server/server.js)) imports `start({ dev: true })` and *adds*:

- chokidar watcher on the repo's `hardware/` to re-run CadQuery generator scripts and broadcast `files-changed` over the `/ws` WebSocket.
- `findScriptsImportingStep` heuristic to also rebuild dependent scripts when a STEP they import changes.
- A Python runner that picks up any new part-named generator script (detected by `export_step` / `export_assembly` / `export_dxf` calls) automatically.

`dev: true` only changes two things in `server.js` itself: the `commit` signal — sent in the WebSocket hello and served at `/api/version` — becomes `"dev"` instead of the deploy SHA, and the boot-time push diff is skipped. Routes are identical.

To verify dev/prod parity, the test in `tests/smoke.test.js` boots `start({ dev: false })` against an ephemeral port. If module evaluation or any default route 5xx's, it fails before any UI test runs.

## Where things go (cheat sheet)

| You want to… | Touch |
|---|---|
| Add a new page at `/foo` | `lib/foo.js` (new) with `mountFooRoutes`, `import + mountFooRoutes(app)` in `server.js`. Add to `tests/smoke.test.js`. |
| Add per-page client JS | `public/foo.js`, link from `lib/foo.js`'s body via `<script src="/foo.js" defer>`. |
| Change something on the viewer | The relevant `public/js/viewer/<module>.js`. Don't put viewer-only things in `public/boot.js` — that loads on every page. |
| Add a new feather glyph | `lib/icons.js`, then import and use in the consumer. Don't inline SVG strings elsewhere. |
| Walk a directory by extension | `import { walkFiles } from "./walk.js"` (server-side). |
| Open a CAD detail modal | `openDetail(file)`, `openDxfDetail(file)` or `openGlbDetail(file)` from `cad-detail.js` — one name per kind, which is what `route.js`'s `OPENERS` tables. They are the whole of `openCadDetail(type, …)`; don't write a parallel modal flow. |
| Persist some viewer state across opens | Add to `state.js`'s exported `state` object. Don't introduce a fresh module-scope `let`. |
| Add a live event type | Define on the server in `lib/events.js` + `lib/push.js`, dispatch on the client in `public/boot.js`'s WebSocket message handler. Page modules listen via `window.addEventListener("hsm:foo")`. |
| Wake a user via FCM | `notifyFilesChanged` in `lib/push.js`. The boot-time diff in `server.js` shows the canonical wiring. |

## Things that are NOT here

- No bundler (esbuild/webpack/vite). Browser ES modules + the importmap in `lib/templates/viewer-body.html` is the whole story. If you reach for a bundler, ask why first — most "needs a bundler" arguments here are for problems we don't have.
- No framework (React/Vue/Svelte). The viewer uses Three.js + plain DOM; the rest is server-rendered HTML + small client modules.
- No auth, no sessions, no user accounts. The app identifies a user by their FCM token (when they enable notifications). Settings live in `localStorage`.
- No browser in `npm test`. The suite holds what stays still — the server boots, the public route surface answers, the walkers and the contracts agree. `npm run test:browser` is the browser pass, on demand. What the viewer renders moves with the hardware: which assemblies exist, which parts fill a branch, what a readout chip reads. If you reach for an assertion on one of those, ask why first.
