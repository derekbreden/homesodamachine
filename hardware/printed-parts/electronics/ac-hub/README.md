# AC hub

The H / N / G mains distribution block: three [Wago 221-413](/hardware/reference/wago-221-413/)
lever nuts on one printed plate, in the strip between the controller board and
the PSU on the cold core's top foam cap.

```
   plan                              section (looking along the row, +X)

   ┌───────────────────────────┐          ║ wires up
   │ ○   ▭▭   ▭▭   ▭▭       ○  │        ┌─╨─┐
   │     H    N    G           │     ◄──┤   │  levers out −Y
   └───────────────────────────┘        ┌┤   ├┐
     ○ = clearance hole over a cap      ││   ││ well wall
         column                       ──┴┴───┴┴──  floor
     ▭ = butt-end well; the lug
         stands in it, ports up
```

## What mounts here

Three Wago 221-413 lever nuts, one per pole, each standing on its butt end. A lug
drops into a well that wraps its lower half on four faces — both X and both Y —
at one 0.15 mm press clearance, open at the top. All three face the same way,
so their wire ports look straight up under the bay's own opening and their wires
leave vertically, as the board's JST headers beside them do. The levers lie on
the −Y face, clear above the wall, and swing out toward the board — the side the
row has room on.

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

The plate is 3 mm PETG, reaching the wells and both hold-down pads and ending
where the wells do.

`ac_hub.py` → `ac-hub.step`; `ac_hub_assembly.py` → `ac-hub-assembly.step` (plate
+ three standing lugs, which is what the enclosure pack places). Regenerate with
`tools/cad-venv/bin/python <script>`.
