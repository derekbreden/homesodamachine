# web-hardware

This is the scope for moving part of [`web/`](/web/) into a standalone package, `web-hardware`: the viewers for the design files (STEP, DXF, PCB, mermaid, line-art), the picker, editor, live reload, and phone-push it has today. Point the package at a directory of files, hand it an HTML shell, and those come up. Branding, routes, and content layout stay behind in the shell and a config the package takes; it carries none of them. Anyone can run it against their own hardware project.

`web/` runs on this package and keeps every behavior it has now.

## Parity

The behaviors are mapped in [`web/README.md`](/web/README.md) and checked by [`smoke.test.js`](/web/tests/smoke.test.js), [`deps.test.js`](/web/tests/deps.test.js), [`viewer.test.js`](/web/tests/viewer.test.js), [`pick-format.test.js`](/web/tests/pick-format.test.js), [`pcb-editor.test.js`](/web/tests/pcb-editor.test.js). The README, a green `cd web && npm test`, and the running site are the parity surface.

The threads below reach past that surface — couplings that live outside `web/`, or that the tests don't exercise.

## Threads outside web/

- **Headless render reads the viewer's globals.** `window.__hsm` is set in [`main.js`](/web/public/js/viewer/main.js) and read by [`render-step.js`](/tools/render/render-step.js), [`render-dxf.js`](/tools/render/render-dxf.js), [`render-thumbnails.js`](/tools/render/render-thumbnails.js), [`render-step-side-by-side.js`](/tools/render/render-step-side-by-side.js).

- **Live reload runs the hardware build tools.** CadQuery scripts run under `tools/cad-venv/bin/python`; boards run `bun render-board.ts`. [`dev-server/server.js`](/web/dev-server/server.js), [`dev-server/deps.js`](/web/dev-server/deps.js). Generators write `.step`/`.dxf` beside their `.py`; [`hardware/scripts/_cadq_export.py`](/hardware/scripts/_cadq_export.py) writes them atomically and byte-stable.

- **Board output is a shape the viewer reads.** [`render-board.ts`](/hardware/pcb/pcba/render-board.ts) writes `out/<name>.{top,bottom,overlay,inner N}.svg` and `<name>.picks.json` ([`pick-data.ts`](/hardware/pcb/pcba/pick-data.ts)); read by [`viewer-routes.js`](/web/lib/viewer-routes.js), [`pcb.js`](/web/public/js/viewer/pcb.js), [`pcb-pick.js`](/web/public/js/viewer/pcb-pick.js). The `RENDER_PHASE=placement` line drives the preview.

- **`files-changed` paths match what the viewer fetched** — each broadcast relative to the content root the file was listed under. [`dev-server/server.js`](/web/dev-server/server.js), [`live.js`](/web/public/js/viewer/live.js).

- **Clipboard pick text round-trips.** [`pick-format.js`](/web/public/js/viewer/pick-format.js), [`pick-format.test.js`](/web/tests/pick-format.test.js).

- **Phone push wakes on a commit.** [`push.js`](/web/lib/push.js), [`notifications.js`](/web/lib/notifications.js), [`boot.js`](/web/public/boot.js). Runs with `DATABASE_URL` + `FIREBASE_*`, no-ops without; the boot diff and FCM paths show on a real deploy. Verify on a device.

- **Content roots.** `hardware/` and `thin/hardware/` behind the edition toggle, [`posts/`](/posts/) for the blog. [`server.js`](/web/server.js), [`viewer-routes.js`](/web/lib/viewer-routes.js).

- **Old deep links resolve.** `/dev`, `/dev/diagrams`, `/dev/mermaid`, `/dev/settings`. [`viewer-pages.js`](/web/lib/viewer-pages.js).

- **dev and prod differ in two places.** The commit signal, and the skipped boot push diff. Routes match. [`server.js`](/web/server.js), [`smoke.test.js`](/web/tests/smoke.test.js).
