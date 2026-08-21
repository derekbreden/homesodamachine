# web/

The Node web server for **homesodamachine.com** + the browser-rendered viewer at `/3d` and `/charts`. No bundler. Runs on Render as a single web service, plus a Postgres add-on for the notification inbox and FCM hash tables. The dev story is the same code with a chokidar wrapper.

The hardware/firmware/CAD content the site presents lives in [`hardware/`](/hardware/) at the repo root — that side is its own world (CadQuery, KiCad, ESP-IDF). This document covers the web layer only.

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

`package-lock.json` is tracked, and is what the deployed site installs. `render.yaml` installs it with `npm ci --omit=dev`, which resolves nothing and stops when the lockfile and `package.json` disagree; the pre-commit hook runs that same command with `--dry-run` whenever either file is staged.

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
  + renderNav({surface, active})
  + <body fragment>        // either inline HTML or a template fragment from lib/templates/
  + renderFooter()
)

Browser receives HTML. Inline pre-paint <script> sets dev-mode + notifs-enabled
classes from localStorage. Then deferred /boot.js runs (SW bridge, notifications
state, WebSocket owner, /api/version activation check). Then any page-specific
module (/landing.js, /js/viewer/main.js, etc.).
```

The single shared shell is [`lib/shell.js`](/web/lib/shell.js). Every page goes through `renderHead` + `renderNav` + `renderFooter`. The `surface` arg is `"public"` (hides Parts/Charts unless dev-mode is set in localStorage) or `"dev"` (always shows them).

## Module layout

### `lib/` — server-side

| Module | Mounts | Responsibility |
|---|---|---|
| [`server.js`](/web/server.js) | `/api/version` | Entry; orchestrates the pool, push init, route mounts, WebSocket broadcast diff loop on prod boot. Serves the live build commit at `/api/version` for boot.js's activation check. |
| [`lib/shell.js`](/web/lib/shell.js) | — | `renderHead` / `renderNav` / `renderFooter`. Owns the synchronous pre-paint class flips and the `<script src="/boot.js" defer>` tag. |
| [`lib/landing.js`](/web/lib/landing.js) | `/` | Marketing landing + email signup form. |
| [`lib/viewer-pages.js`](/web/lib/viewer-pages.js) | `/3d`, `/charts`, `/drawings`, `/pcb` | The viewer pages — parts, charts, drawings + the documents shelf, boards. All render [`lib/templates/viewer-body.html`](/web/lib/templates/viewer-body.html). |
| [`lib/viewer-routes.js`](/web/lib/viewer-routes.js) | `/api/{steps,dxf,mermaid,documents}`, `/steps/*`, `/dxfs/*`, `/cards/*`, `/docs/*`, `/api/mermaid-content/*` | API for the viewer's file lists and content. |
| [`lib/settings.js`](/web/lib/settings.js) | `/settings` | Per-user toggles: dev-mode, FCM enable, ratio config. |
| [`lib/events.js`](/web/lib/events.js) | `/ws` | WebSocket channel. One socket per page: deploy hello-handshake + ping heartbeat + `files-changed` broadcasts. |
| [`lib/notifications.js`](/web/lib/notifications.js) | `/api/notifications/*`, `/notifications` | Per-token inbox CRUD + the `/notifications` page. |
| [`lib/push.js`](/web/lib/push.js) | `/api/push/*` | FCM subscriptions + outbound notify; boot-time hash diff against per-kind tables. |
| [`lib/walk.js`](/web/lib/walk.js) | — | Shared `walkFiles(rootDir, exts)` helper, plus the per-kind walkers (`walkPcbBoards`, `walkAssemblyCards`, `walkDocuments`). |
| [`lib/icons.js`](/web/lib/icons.js) | — | Shared SVG glyphs (cube, chart, gear, bell, scissors, clipboard). |

The pattern: `export function mountXxxRoutes(app, { … } = {})`. `server.js` calls each in sequence. To add a new page or API surface, add `lib/foo.js` with `mountFooRoutes`, import and call it from `server.js`.

### `public/` — browser-side

Served flat via `express.static(public/)`.

| File | Loaded on | Role |
|---|---|---|
| [`public/boot.js`](/web/public/boot.js) | every page (`<script defer>`) | SW navigate bridge, notifications state mirror + bell + toast + warm-tap auto-redirect, WebSocket owner, `/api/version` deploy/activation check (reloads the page on a new build unless the viewer claims it via `window.__hsmDeploySoft`). Module-local state — never touches `window.__hsm`. |
| [`public/landing.js`](/web/public/landing.js) | `/` | Glass-animation mount, signup form submit. |
| [`public/settings.js`](/web/public/settings.js) | `/settings` | Dev-mode + notification toggles. |
| [`public/glass-animation.js`](/web/public/glass-animation.js) | `/` | Pours/fizzes the hero animation. |
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
| `dxf.js` | DXF loader, parser, extrusion mesher, thumbnail renderer. |
| `mermaid.js` | Mermaid renderer (lazy-loaded library), thumbnail renderer, modal detail flow with PanZoom. |
| `cad-detail.js` | Shared modal flow for STEP+DXF (`openCadDetail`/`closeCadDetail`); the `CAD_KINDS` table maps type → ext/hashPrefix/loader. |
| `grid.js` | Card grid per page, `IntersectionObserver` for thumbnail lazy-load. `/3d` hands off to `parts.js`; charts and line art group by a path segment (`categoryAndPartPath`, `groupFilesByCategory`). |
| `parts.js` | `/3d`'s tree: the three assemblies as collapsible branches, each holding its own grid, seated by [`contracts/parts-tree.js`](/web/contracts/parts-tree.js). One card per part, its representations folded together. |
| `live.js` | WebSocket-driven refresh — `hsm:files-changed` listener + `refreshXxxCard` per type for per-file updates; `hsm:deploy` listener that wipes caches and refreshes the whole grid + open modal on a new build. Sets `window.__hsmDeploySoft`. |
| `route.js` | popstate + initial-route translation between URL hash/`?file=` and `currentDetail`. |
| `main.js` | Entry. Sets up nav active class + title, calls `fetchFiles`, applies the initial route. |

State sharing pattern is **one shared object** (`state.js`'s exported `state`). Other modules `import { state } from './state.js'` and read/write `state.allFiles` etc. directly. Live binding via the object identity; no per-module proxy or sync ceremony.

The Puppeteer escape hatch `window.__hsm` is set from `main.js` after all modules have loaded; its shape is part of the contract with [`tools/render/render-step*.js`](/tools/render/) (which lives at the repo root and imports `web/server.js`) and must not change without updating those.

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
| Open a CAD detail modal | `openCadDetail("step", file)` or `("dxf", file)` from `cad-detail.js`. Don't write a parallel modal flow. |
| Persist some viewer state across opens | Add to `state.js`'s exported `state` object. Don't introduce a fresh module-scope `let`. |
| Add a live event type | Define on the server in `lib/events.js` + `lib/push.js`, dispatch on the client in `public/boot.js`'s WebSocket message handler. Page modules listen via `window.addEventListener("hsm:foo")`. |
| Wake a user via FCM | `notifyFilesChanged` in `lib/push.js`. The boot-time diff in `server.js` shows the canonical wiring. |

## Things that are NOT here

- No bundler (esbuild/webpack/vite). Browser ES modules + the importmap in `lib/templates/viewer-body.html` is the whole story. If you reach for a bundler, ask why first — most "needs a bundler" arguments here are for problems we don't have.
- No framework (React/Vue/Svelte). The viewer uses Three.js + plain DOM; the rest is server-rendered HTML + small client modules.
- No auth, no sessions, no user accounts. The app identifies a user by their FCM token (when they enable notifications). Settings live in `localStorage`.
- No browser in `npm test`. The suite holds what stays still — the server boots, the public route surface answers, the walkers and the contracts agree — and `.githooks/pre-commit` runs it on every commit that stages under `web/`. `npm run test:browser` is the browser pass, on demand. What the viewer renders moves with the hardware: which assemblies exist, which parts fill a branch, what a readout chip reads. If you reach for an assertion on one of those, ask why first.
