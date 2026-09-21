The fixed inner manifold group uses a 9.5 mm drop relative to the outer limbs.
V-A/B, Y-A/B and V-C/D share that datum. The pump stations, carried tees and
outer hairpins keep their existing datums.

The bounded native checks are recorded in [inner-limb-drop-check.json](inner-limb-drop-check.json).

| Interface | Current result |
|---|---|
| V-A/B coils to funnel | 1.216789 / 1.217222 mm native air |
| V-A/B inlet axes | Z269.6750001; X/Y and directions unchanged |
| V-C/D aft tray seat centers | Z190.425; mounting plane Y177.29 |
| V-A/B cap cradle mounting height | 5.225 mm above the lid face |
| Cap cradle socket floor stock | 4.225 mm, with the complete socket and bearing section retained |
| Carrier shelf and backing | Z209.075 / Z182.175; all printed placement dimensions retained |
| C/D underside entry and post insertion | Zero native overlap with the complete carrier |
| Pump cartridge and cap | Zero added or missing native volume against the frozen canonical exports |
| Funnel drain to V-B (`fluid-4`) | R14 throughout; at least 2 mm from unrelated retained neighbors and the complete candidate lid |

The carrier derives each clearance plane as the greater of its existing design
plane and the measured obstacle requirement. A lower valve increases clearance
without changing the structural section. A higher obstacle still produces a
placement mismatch rather than accepting an interference.

The paired [fluid-14 check](../../../../reference/g-ganen-pump/installation/inner-valve-route-check.json)
binds its local valve-side bend to the complete current lid. It retains the
existing cap bearing and records 1.155 mm to V-A, 1.125 mm to V-K and 0.15 mm
intended air over the printed bearing.

These are bounded component and interface checks. The source-derived valve trays,
complete shell, and simultaneous final tube routes require their full build checks.
The archived front-bottom and placed body references are evidence inputs, not
current printable parts. The pump cartridge/cap equality uses the frozen canonical
geometry in `fit-correction-baseline.zip`.

Reproduce without writing production outputs:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python \
  hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/verify_inner_limb_drop.py \
  --output /tmp/inner-limb-drop-check.json
```

The reproducer verifies every input digest in `inner-limb-drop-baseline.zip` and
`fit-correction-baseline.zip` before constructing its local witnesses.
