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
      + renderNav({ surface: "public", active: "foo" })
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
| [`blog.js`](/web/lib/blog.js) | `/blog` | Markdown posts from [`posts/`](/posts/), rendered into the index page (individual posts are `#post-<slug>` anchors). Inline JS in [`public/blog.js`](/web/public/blog.js). |
| [`viewer-pages.js`](/web/lib/viewer-pages.js) | `/3d`, `/charts` | Both pages render [`templates/viewer-body.html`](/web/lib/templates/viewer-body.html), which loads `public/js/viewer/main.js`. The decision of "show parts vs charts" is made client-side by `currentSection()`. |
| [`viewer-routes.js`](/web/lib/viewer-routes.js) | API surface for the viewer | `/api/{steps,dxf,mermaid}` (file lists), `/steps/*`, `/dxfs/*`, `/api/mermaid-content/*` (file passthroughs). Walks `hardware/` via [`walk.js`](/web/lib/walk.js). |
| [`settings.js`](/web/lib/settings.js) | `/settings` | Per-user toggles. Inline JS in [`public/settings.js`](/web/public/settings.js). |
| [`events.js`](/web/lib/events.js) | `/ws` | WebSocket channel — one socket per page, owned by [`public/boot.js`](/web/public/boot.js). |
| [`notifications.js`](/web/lib/notifications.js) | `/api/notifications/*`, `/notifications` | Per-token inbox CRUD + the page. Routes only mount if `pool` is non-null (i.e. DATABASE_URL is set). |
| [`push.js`](/web/lib/push.js) | `/api/push/*` | FCM subscriptions + outbound notify. Boot-time hash diff against per-kind tables (`step_hashes`, `dxf_hashes`, `mermaid_hashes`, `post_hashes`). |
| [`walk.js`](/web/lib/walk.js) | — | `walkFiles(rootDir, exts)` — shared between `viewer-routes.js` and `push.js`. |
| [`icons.js`](/web/lib/icons.js) | — | Shared SVG glyphs (cube, chart, gear, bell, scissors, newspaper, file). One source of truth for both nav and notification rows. |
| [`templates/`](/web/lib/templates/) | — | HTML fragments included by the page-render modules above. Currently just `viewer-body.html`. |

## Conventions

- **Module-load side effects are minimal.** Imports may register module-level constants (`marked.use(...)` in `blog.js` is the one notable exception), but no module starts a server, opens a connection, or schedules a timer at import time. Wiring happens inside the exported `mountXxxRoutes` so server boot order is deterministic.
- **DB optionality.** Modules that touch Postgres check `if (!pool) return [...empty...]` at the call boundary, so the dev server (no DATABASE_URL) and the smoke tests both work without a database.
- **`window.__hsm` is reserved** for the `/3d` viewer's Puppeteer escape hatch (see [`tools/render/render-step.js`](/tools/render/render-step.js)). Don't write to it from server-side modules or `boot.js`.
- **Inline JS in lib/ is a smell.** If a page needs more than ~10 lines of client-side code, extract to `public/<page>.js` linked via `<script src="..." defer>`. The exception is the synchronous pre-paint class flips in `shell.js` HEAD_TAGS, which must run during head parse to avoid FOUC.
