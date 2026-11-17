# lib/

Server-side modules for the Node web app. Each `.js` here exports a `mountXxxRoutes(app, …)` function that attaches Express handlers; [`server.js`](/web/server.js) calls them in order at boot. See [`web/README.md`](/web/README.md) for the full picture of how request → server.js → lib → response works, and the dev-vs-prod story.

## The mount-routes contract

```js
// lib/foo.js
export function mountFooRoutes(app, { someOption } = {}) {
  app.get("/foo", (req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.send(
      renderHead({ title: "Foo · Home Soda Machine", pageStyles: "..." })
      + renderNav({ active: "foo" })
      + `<main>...</main>`
      + renderFooter()
    );
  });
}
```

Then in `server.js`:
```js
import { mountFooRoutes } from "./lib/foo.js";
…
mountFooRoutes(app, { /* options */ });
```

That's it. There is no central router config, no decorator metadata, no plugin registration — `server.js` is the orchestration script you can read top-to-bottom in two minutes to know every route the app serves.

## Files

| Module | Mounts | Notes |
|---|---|---|
| [`shell.js`](/web/lib/shell.js) | — | Shared `<head>` + nav + footer. Owns the synchronous pre-paint class flips and the `<script src="/boot.js" defer>` tag that every page loads. |
| [`landing.js`](/web/lib/landing.js) | `/` | Marketing landing + signup form. Inline JS extracted to [`public/landing.js`](/web/public/landing.js). |
| [`unit.js`](/web/lib/unit.js) | `/0001`, `/0001/get-started`, `/0001/guides` | Registered unit pages with the shared head and their own owner navigation. Equipment, preparation, and links to the printed guides. |
| [`viewer-pages.js`](/web/lib/viewer-pages.js) | `/3d`, `/guides` | Parts and guides share [`templates/viewer-body.html`](/web/lib/templates/viewer-body.html). |
| [`viewer-routes.js`](/web/lib/viewer-routes.js) | Viewer API | Lists and serves models, board views and published documents. Walks `hardware/` via [`walk.js`](/web/lib/walk.js). |
| [`events.js`](/web/lib/events.js) | `/ws` | WebSocket channel — one socket per page, owned by [`public/boot.js`](/web/public/boot.js). |
| [`notifications.js`](/web/lib/notifications.js) | `/api/notifications/*`, `/notifications` | Per-token inbox CRUD + the page. Routes only mount if `pool` is non-null (i.e. DATABASE_URL is set). |
| [`push.js`](/web/lib/push.js) | `/api/push/*` | FCM subscriptions and notifications. File changes are read from `step_hashes`, `dxf_hashes`, `document_hashes` and `pcb_hashes`. |
| [`walk.js`](/web/lib/walk.js) | — | `walkFiles(rootDir, exts)` and the per-kind walkers (`walkFilesUnderDir`, `walkPcbBoards`, `walkDocuments`) — shared between `viewer-routes.js` and `push.js`. Every one of them skips a retired tree. |
| [`retired.js`](/web/lib/retired.js) | — | The `.retired` marker: a directory holding that file, and everything under it, is source kept for reading. Read by `walk.js` (what the site browses) and [`scripts/build-deps.js`](/web/scripts/build-deps.js) (what the build rebuilds), from here so the two cannot disagree. |
| [`icons.js`](/web/lib/icons.js) | — | Shared SVG glyphs for navigation and notification rows. |
| [`templates/`](/web/lib/templates/) | — | HTML fragments included by the page-render modules above. Currently just `viewer-body.html`. |

## Conventions

- **Module-load side effects are minimal.** Imports may register module-level constants, but no module starts a server, opens a connection, or schedules a timer at import time. Wiring happens inside the exported `mountXxxRoutes` so server boot order is deterministic.
- **DB optionality.** Modules that touch Postgres check `if (!pool) return [...empty...]` at the call boundary, so a troubleshooting run or smoke test can start without a database.
- **`window.__hsm` is reserved** for the `/3d` viewer's Puppeteer escape hatch (see [`web/contracts/hsm-globals.js`](/web/contracts/hsm-globals.js)). Don't write to it from server-side modules or `boot.js`.
- **Inline JS in lib/ is a smell.** If a page needs more than ~10 lines of client-side code, extract to `public/<page>.js` linked via `<script src="..." defer>`. The exception is the synchronous pre-paint class flips in `shell.js` HEAD_TAGS, which must run during head parse to avoid FOUC.
