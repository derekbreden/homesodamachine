# AC hub — RETIRED as a printed part

**Nothing prints this any more.** The five 221-413 lever nuts it used to carry — three
mains poles and the two 12 V rails — press straight into wells printed on the
enclosure's own +X wall (`enclosure._east_wells`), so there is no plate, no hold-down
bosses and no screws. It is off [`bom.md`](/hardware/ledger/bom.md) §7, off the
print-time table, and off the scorecard's mount list.

`ac_hub.py` survives for one consumer:
[`mains-assembly/_mains_interface.py`](/hardware/printed-parts/electronics/mains-assembly/_mains_interface.py)
still derives the mains block's splice band from this module's frame. Repointing that
model at the wall's own well constants is the last step of the retirement and has not
been done — until it is, treat the geometry below as the mains model's, not as a part.

The H / N / G mains distribution block: three [Wago 221-413](/hardware/reference/wago-221-413/)
lever nuts on one printed plate, on the crown of the machine's power column
against the enclosure's +X wall.

```
   plan                              section (looking along the row, +X)

   ┌───────────────────────────┐          ║ wires up
   │ ○   ▭▭   ▭▭   ▭▭       ○  │        ┌─╨─┐
   │     H    N    G           │     ◄──┤   │  levers out −Y
   └───────────────────────────┘        ┌┤   ├┐
     ○ = clearance hole over a wall     ││   ││ well wall
         boss                         ──┴┴───┴┴──  floor
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

## Mounting

Two clearance holes, one at each end of the row, on the row's own centre line.
M3 SHCS down through each, into a ruthex short in the boss standing under it. In
the appliance those bosses are the enclosure's own — the hub joins the power
column on the +X wall, and
[`enclosure._east_bosses`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)
prints one per hole, reaching in off the wall to the plate's underside.

The spacing is the row's: each bore sits at the middle of the pad its end of the
plate grows into, so a lug added to the row carries the pair outward with it and
the plate and its bosses cannot end up on two different numbers.

The plate is 3 mm PETG, reaching the wells across the row and one hold-down pad
past it at each end.

`ac_hub.py` → `ac-hub.step`; `ac_hub_assembly.py` → `ac-hub-assembly.step` (plate
+ three standing lugs, which is what the enclosure pack places). Regenerate with
`tools/cad-venv/bin/python <script>`.
