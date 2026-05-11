# Architecture

This is a **Node web server + browser-rendered SPA-ish UI**, no bundler. It runs on Render as a single web service, plus a Postgres add-on for the notification inbox and FCM hash tables. The dev story is the same code with a chokidar wrapper.

The hardware/firmware/CAD content the site presents lives in [`hardware/`](hardware/) and [`posts/`](posts/) — that side is its own world (CadQuery, KiCad, ESP-IDF). This document covers the web layer only.

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
state, SSE owner). Then any page-specific module (/landing.js, /js/viewer/main.js,
etc.).
```

The single shared shell is [`lib/shell.js`](lib/shell.js). Every page goes through `renderHead` + `renderNav` + `renderFooter`. The `surface` arg is `"public"` (hides Parts/Charts unless dev-mode is set in localStorage) or `"dev"` (always shows them).

## Module layout

### `lib/` — server-side

| Module | Mounts | Responsibility |
|---|---|---|
| [`server.js`](server.js) | — | Entry; orchestrates the pool, push init, route mounts, SSE diff loop on prod boot. |
| [`lib/shell.js`](lib/shell.js) | — | `renderHead` / `renderNav` / `renderFooter`. Owns the synchronous pre-paint class flips and the `<script src="/boot.js" defer>` tag. |
| [`lib/landing.js`](lib/landing.js) | `/` | Marketing landing + email signup form. |
| [`lib/blog.js`](lib/blog.js) | `/blog` | Markdown posts under [`posts/`](posts/), rendered into the one index page. Individual posts are `#post-<slug>` anchors. |
| [`lib/viewer-pages.js`](lib/viewer-pages.js) | `/3d`, `/charts` | The parts/charts viewer pages — both render [`lib/templates/viewer-body.html`](lib/templates/viewer-body.html). |
| [`lib/viewer-routes.js`](lib/viewer-routes.js) | `/api/{steps,dxf,mermaid}`, `/steps/*`, `/dxfs/*`, `/api/mermaid-content/*` | API for the viewer's file lists and content. |
| [`lib/settings.js`](lib/settings.js) | `/settings` | Per-user toggles: dev-mode, FCM enable, ratio config. |
| [`lib/events.js`](lib/events.js) | `/api/events` | SSE channel. One EventSource per page. |
| [`lib/notifications.js`](lib/notifications.js) | `/api/notifications/*`, `/notifications` | Per-token inbox CRUD + the `/notifications` page. |
| [`lib/push.js`](lib/push.js) | `/api/push/*` | FCM subscriptions + outbound notify; boot-time hash diff against per-kind tables. |
| [`lib/walk.js`](lib/walk.js) | — | Shared `walkFiles(rootDir, exts)` helper. |
| [`lib/icons.js`](lib/icons.js) | — | Shared SVG glyphs (cube, chart, gear, bell, scissors, newspaper). |

The pattern: `export function mountXxxRoutes(app, { … } = {})`. `server.js` calls each in sequence. To add a new page or API surface, add `lib/foo.js` with `mountFooRoutes`, import and call it from `server.js`.

### `public/` — browser-side

Served flat via `express.static(public/)`.

| File | Loaded on | Role |
|---|---|---|
| [`public/boot.js`](public/boot.js) | every page (`<script defer>`) | SW navigate bridge, notifications state mirror + bell + toast + warm-tap auto-redirect, SSE owner. Module-local state — never touches `window.__hsm`. |
| [`public/landing.js`](public/landing.js) | `/` | Glass-animation mount, signup form submit. |
| [`public/blog.js`](public/blog.js) | `/blog` | Click-to-open post images via ContentViewer. |
| [`public/settings.js`](public/settings.js) | `/settings` | Dev-mode + notification toggles. |
| [`public/glass-animation.js`](public/glass-animation.js) | `/` | Pours/fizzes the hero animation. |
| [`public/pan-zoom.js`](public/pan-zoom.js) | `/blog`, `/3d`, `/charts` | Generic pan + pinch-zoom + wheel-zoom. |
| [`public/content-viewer.js`](public/content-viewer.js) | `/blog`, `/3d`, `/charts` | Modal singleton: open / close / swipe-down / Esc / X / backdrop. |
| `public/js/viewer/*.js` | `/3d`, `/charts` | The parts/charts viewer modules — see below. |
| `public/css/viewer.css` | `/3d`, `/charts` | Viewer-specific styles. |

### `public/js/viewer/` — the parts viewer modules

`/3d` and `/charts` share one module graph (the entry decides what to show based on `location.pathname`). Each module is a browser-native ES module loaded via the importmap in [`lib/templates/viewer-body.html`](lib/templates/viewer-body.html).

| Module | Role |
|---|---|
| `state.js` | Single exported `state` object holding all shared mutable refs (`allFiles`, `currentDetail`, `mountedDetail`, caches, etag maps, `gridEl`). Every other module reads/writes through `state.X`. |
| `scene.js` | Three.js renderer/camera/controls/scene/lighting + ViewCube + animate loop + per-file camera persistence + canvas reparenting (canvases live in `#cad-canvas-host` between opens). |
| `step.js` | STEP loader (occt-import-js), parser, mesher, thumbnail renderer. |
| `dxf.js` | DXF loader, parser, extrusion mesher, thumbnail renderer. |
| `mermaid.js` | Mermaid renderer (lazy-loaded library), thumbnail renderer, modal detail flow with PanZoom. |
| `cad-detail.js` | Shared modal flow for STEP+DXF (`openCadDetail`/`closeCadDetail`); the `CAD_KINDS` table maps type → ext/hashPrefix/loader. |
| `grid.js` | Card grid, subsystem subheaders (`categoryAndPartPath`, `groupFilesByCategory`, `CATEGORY_LABEL_OVERRIDES`), `IntersectionObserver` for thumbnail lazy-load. |
| `live.js` | SSE-driven refresh — `hsm:files-changed` listener, `refreshXxxCard` per type, in-flight detail reload. |
| `route.js` | popstate + initial-route translation between URL hash/`?file=` and `currentDetail`. |
| `main.js` | Entry. Sets up nav active class + title, calls `fetchFiles`, applies the initial route. |

State sharing pattern is **one shared object** (`state.js`'s exported `state`). Other modules `import { state } from './state.js'` and read/write `state.allFiles` etc. directly. Live binding via the object identity; no per-module proxy or sync ceremony.

The Puppeteer escape hatch `window.__hsm` is set from `main.js` after all modules have loaded; its shape is part of the contract with [`tools/render/render-step*.js`](../tools/render/) (which lives at the repo root and imports `web/server.js`) and must not change without updating those.

## Cross-module event flow

```
SSE  /api/events  ────► boot.js                ────► CustomEvent("hsm:files-changed", {files})
                          │                          ────► CustomEvent("hsm:posts-changed", {posts})
                          ▼                          ────► CustomEvent("hsm:deploy")
                     fetchNotifications()           │
                          │                          │
                          ▼                          ▼
                     hsm:notifications-updated     viewer/live.js (per-file refresh)

FCM  → service worker → notification banner
       (tap → on iOS PWA, page focus → boot.js refetch → maybe redirect; on
        Android/Chrome desktop, SW posts {type:"navigate"} which boot.js handles)
```

Three event sources land in the page (SSE, FCM, focus/visibility). All three converge on `fetchNotifications()` which keeps the local state mirror current and dispatches `hsm:notifications-updated` for the toast + bell to react to.

## Dev vs prod

There is **one server core** ([`server.js`](server.js)). The dev wrapper ([`dev-server/server.js`](dev-server/server.js)) imports `start({ dev: true })` and *adds*:

- chokidar watcher on the repo's `hardware/` to re-run `generate_step_cadquery.py` and broadcast `files-changed` over SSE.
- `findScriptsImportingStep` heuristic to also rebuild dependent scripts when a STEP they import changes.
- A Python runner that picks up new `generate_step_*.py` files automatically.

`dev: true` only changes two things in `server.js` itself: the SSE `commit` signal becomes `"dev"` (not the deploy SHA), and the boot-time push diff is skipped. Routes are identical.

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
| Add an SSE event type | Define on the server in `lib/events.js` + `lib/push.js`, dispatch on the client in `public/boot.js`'s SSE handler block. Page modules listen via `window.addEventListener("hsm:foo")`. |
| Wake a user via FCM | `notifyFilesChanged` / `notifyPostsChanged` in `lib/push.js`. The boot-time diff in `server.js` shows the canonical wiring. |

## Things that are NOT here

- No bundler (esbuild/webpack/vite). Browser ES modules + the importmap in `lib/templates/viewer-body.html` is the whole story. If you reach for a bundler, ask why first — most "needs a bundler" arguments here are for problems we don't have.
- No framework (React/Vue/Svelte). The viewer uses Three.js + plain DOM; the rest is server-rendered HTML + small client modules.
- No auth, no sessions, no user accounts. The app identifies a user by their FCM token (when they enable notifications). Settings live in `localStorage`.
- No tests beyond `tests/smoke.test.js`. The smoke test catches the deploy-killer class of bug (module evaluation errors); UI behavior tests would need Puppeteer infrastructure that hasn't paid back yet.
