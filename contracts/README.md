# contracts

The shapes that cross between the builders and the web viewer — a builder produces data, the
viewer reads it, and the shape they agree on is defined here.

- **picks-schema.ts** — `out/<board>.picks.json`: the pads/vias/traces the pad picker hit-tests,
  plus the board readout (size) and checks (clearance floor + tight pairs, DRC errors, the
  cap-decoupling audit). Produced by `hardware/pcb/pcba/pick-data.ts`; read by
  `web/public/js/viewer/{pcb,pcb-pick,pcb-edit}.js`; pinned by `web/tests/picks-schema.test.js`.
- **pcb-out.js** — the board `out/` render layout: the view filenames and the `/api/pcb-*` path
  confinement. Produced by `hardware/pcb/pcba/render-board.ts`; read by
  `web/lib/{walk,viewer-routes}.js`.

A sibling that lives with the viewer because the browser loads it at runtime:
`web/public/js/viewer/pick-format.js` — the clipboard grammar the pickers emit and parse back
(pinned by `web/tests/pick-format.test.js`).

A definition is written in the language its code imports: `.ts` where the tscircuit builders
share it, `.js` where the node/browser web layer does.
