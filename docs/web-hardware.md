# web-hardware

This is the scope for moving part of [`web/`](/web/) into a standalone package, `web-hardware`: the viewers for the design files (STEP, DXF, PCB, mermaid, print sheets), the picker, editor, live reload, and phone-push it has today. Point the package at a directory of files, hand it an HTML shell, and those come up. Branding, routes, and content layout stay behind in the shell and a config the package takes; it carries none of them. Anyone can run it against their own hardware project.

`web/` runs on this package and keeps every behavior it has now.

## Parity

The behaviors are mapped in [`web/README.md`](/web/README.md) and checked by [`smoke.test.js`](/web/tests/smoke.test.js), [`deps.test.js`](/web/tests/deps.test.js), [`pick-format.test.js`](/web/tests/pick-format.test.js), [`pcb-editor.test.js`](/web/tests/pcb-editor.test.js). The README, a green `cd web && npm test`, and the running site are the parity surface. [`browser/viewer.browser.js`](/web/tests/browser/viewer.browser.js) is the browser pass, run by `npm run test:browser`.

The threads below reach past that surface — couplings that live outside `web/`, or that the tests don't exercise.

## Threads outside web/

- **Headless render reads the viewer's globals.** `window.__hsm` is set in [`main.js`](/web/public/js/viewer/main.js) and read by [`render-step.js`](/tools/render/render-step.js), [`render-dxf.js`](/tools/render/render-dxf.js), [`render-thumbnails.js`](/tools/render/render-thumbnails.js), [`render-step-side-by-side.js`](/tools/render/render-step-side-by-side.js), [`render-step-posed.js`](/tools/render/render-step-posed.js), [`render-view.js`](/tools/render/render-view.js).

- **What the viewer keeps between mounts is what a many-picture render has to put back.** [`render-step-posed.js --jobs`](/tools/render/render-step-posed.js) draws N pictures on one page, so anything a viewer module carries from one mounted model to the next lands in the next picture. Three did, and each was found as a byte difference against the same picture drawn on its own page: [`scene.js`](/web/public/js/viewer/scene.js)'s `animate` loop refits `scene.fog` to wherever the camera is standing when a frame happens to run, so the tool calls `resetCamera` itself and spends every `await` before it touches the frame; [`xray.js`](/web/public/js/viewer/xray.js) sizes its feature-edge materials in pixels of whatever buffer that loop last measured, so the tool sizes them to the buffer it is about to draw into; and [`step.js`](/web/public/js/viewer/step.js) shares shading materials across mounts by colour, which sets the order three.js draws the opaque solids in — `forgetMaterials` / `forgetEdgeMaterials` drop them so each subject is drawn in its own order. A fourth module doing the same would show up the same way: `HSM_POSE_DEBUG=1` prints what each frame was composed against.

- **A frame is read back in the task that drew it.** [`scene.js`](/web/public/js/viewer/scene.js)'s renderer is built without `preserveDrawingBuffer`, so a capture that goes through the page gets an arbitrary frame and no wait can fix it. Every renderer above ends its `page.evaluate` with `renderer.render(...)` and `toDataURL` on adjacent lines and passes the result to `frameBuffer` — [`browser.js`](/tools/render/browser.js) carries the whole reason. A new renderer that calls `page.screenshot` on the viewer is nondeterministic even though it will look fine the first few runs. The picture being the canvas is also why none of these hide the viewer's nav, gizmo or buttons.

- **Live reload runs the hardware build tools.** CadQuery scripts run under `tools/cad-venv/bin/python`; boards run `bun render-board.ts`. [`dev-server/server.js`](/web/dev-server/server.js), [`dev-server/deps.js`](/web/dev-server/deps.js). Generators write `.step`/`.dxf` beside their `.py`; [`hardware/scripts/_cadq_export.py`](/hardware/scripts/_cadq_export.py) writes them atomically and byte-stable.

- **Board output is a shape the viewer reads.** [`render-board.ts`](/hardware/pcb/pcba/render-board.ts) writes `out/<name>.{top,bottom,overlay,inner N}.svg` and `<name>.picks.json` ([`pick-data.ts`](/hardware/pcb/pcba/pick-data.ts)); read by [`viewer-routes.js`](/web/lib/viewer-routes.js), [`pcb.js`](/web/public/js/viewer/pcb.js), [`pcb-pick.js`](/web/public/js/viewer/pcb-pick.js). The `RENDER_PHASE=placement` line drives the preview.

- **`files-changed` paths match what the viewer fetched** — each broadcast relative to the content root the file was listed under. [`dev-server/server.js`](/web/dev-server/server.js), [`live.js`](/web/public/js/viewer/live.js).

- **Clipboard pick text round-trips.** [`pick-format.js`](/web/public/js/viewer/pick-format.js), [`pick-format.test.js`](/web/tests/pick-format.test.js).

- **Phone push wakes on a commit.** [`push.js`](/web/lib/push.js), [`notifications.js`](/web/lib/notifications.js), [`boot.js`](/web/public/boot.js). Runs with `DATABASE_URL` + `FIREBASE_*`, no-ops without; the boot diff and FCM paths show on a real deploy. Verify on a device.

- **Content root.** `hardware/`. [`server.js`](/web/server.js), [`viewer-routes.js`](/web/lib/viewer-routes.js).

- **Old deep links resolve.** `/dev`, `/dev/diagrams`, `/dev/mermaid`, `/dev/settings`. [`viewer-pages.js`](/web/lib/viewer-pages.js).

- **dev and prod differ in two places.** The commit signal, and the skipped boot push diff. Routes match. [`server.js`](/web/server.js), [`smoke.test.js`](/web/tests/smoke.test.js).
