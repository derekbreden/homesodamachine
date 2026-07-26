# AC hub

The H / N / G mains distribution block: three [Wago 221-413](/hardware/reference/wago-221-413/)
lever nuts on one printed plate, in the strip between the controller board and
the PSU on the cold core's top foam cap.

```
   ┌─────────────────────────────────────────┐
   │ ○      ▭▭▭    ▭▭▭    ▭▭▭             ○  │
   │        H      N      G                  │
   └─────────────────────────────────────────┘
     ○ = clearance hole over a cap column
     ▭ = butt-end pocket; the wire half hangs past the plate (+Y)
```

## What mounts here

Three Wago 221-413 lever nuts, one per pole. Each drops into a pocket that wraps
its butt half on five faces — both X, both Z, and the −Y end — at one 0.15 mm
press clearance, open toward +Y. All three face the same way; the wire half of
each lug sits past the plate's edge, and the levers work from above, under the
bay's own opening.

Everything else on this shelf bolts to a deck-mount column of the cap with
nothing printed beneath it — the controller PCBA, the Mean Well PSU, Teyleten
relay #1, and the ground ring-terminal stack
([`_cold_core_interface.deck_mounts`](/hardware/printed-parts/cold-core/_cold_core_interface.py)).

## Mounting

Two clearance holes, one at each end of the row, over the cap's two `ac-hub`
columns; the plate spans the foam-cap lid's pour hole between them. M3 × 8 SHCS
down through each, into a ruthex short in the column's top bore. The hole spacing
is read from `deck_mount_xy("ac-hub")`, so the plate and the columns carry one
number.

The plate is 3 mm PETG, reaching the pockets and both hold-down pads and ending
where the buried butts do.

`ac_hub.py` → `ac-hub.step`; `ac_hub_assembly.py` → `ac-hub-assembly.step` (plate
+ three seated lugs, which is what the enclosure pack places). Regenerate with
`tools/cad-venv/bin/python <script>`.
