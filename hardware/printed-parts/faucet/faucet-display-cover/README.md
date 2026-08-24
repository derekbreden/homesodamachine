# Faucet display cover plate

The printed face plate over the faucet display, and the only thing holding the
device in. A hand meets its outer face as the top of the cradle, unbroken from
the collar below it but for one seam and one screw head. It laps the device's
face on all four edges, comes down over its housing, and threads a single M3
into the shell above the device's north edge.

## Frame

The shell's own tip frame, off
[`faucet_shell._tip_frame`](/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py):
`s` is distance up-gooseneck from the tip end along the tip axis, `n` is
distance from the water-tube centreline along the tip's top normal, `x` is world
X. Every figure below is read against the shell's own cuts, and
`faucet_assembly` stands the plate on the faucet without moving it — it builds
where it sits.

## The seam

**The cradle parts at the device's own step.** The shell stops at
[17.2 mm](PLATE_N_BOTTOM) — the step the device's board makes under its housing
— and this plate is everything above it. So the line a hand finds around the
cradle is a step the device already has, not a height chosen for it, and the
plan outline carries across unchanged: [28.72 mm](PLATE_X) wide on both sides of
it, so the outside reads as one surface.

**A tongue, not a butt.** The shell's wall tops are rebated on their inner
[0.62 mm](TONGUE_W) — one extrusion of the three the wall is — for
[1.24 mm](LAP_DEPTH) of depth, and the plate hangs a matching tongue down to
[15.96 mm](TONGUE_N_BOTTOM). That joint is what locates the plate across the tip
and along it, and what puts the seam's own tolerance below the surface instead
of on it. The groove carries the slip; the tongue is nominal.

## Outline

- Outer face at [24.21 mm](PLATE_N_TOP), [7.01 mm](PLATE_THICKNESS) of plate
  under it at the screw.
- Skirt inner faces on the cavity's own outline, [12.5 mm](SKIRT_HALF_X) each
  side of centre, coming [5.15 mm](SKIRT_DEPTH) down over the device's housing.
- Bezel [1.86 mm](BEZEL_THICKNESS) thick, its underside at
  [22.35 mm](BEZEL_N_BOTTOM) — [0.1 mm](COVER_OVER_FACE) over the device's face,
  so the plate captures the device rather than clamping it through its housing.
- Window [20.5 mm](WINDOW_X) × [40.5 mm](WINDOW_S), r[3.75 mm](WINDOW_CORNER_R).
  The bezel laps the face by [2 mm](COVER_LAP) on every edge, which stops
  [1.375 mm](WINDOW_SIDE_MARGIN) short of the glass on the sides and
  [3.785 mm](WINDOW_END_MARGIN) short on the ends.
- North end cut to the cradle's own back ramp, so the plate's slope continues
  the shell's across the seam instead of stepping off it.

## The screw

One, on the centreline at s = [50.72 mm](SCREW_S) — north of the device, in the
head wall the cradle already had.

- **Seat** — ⌀[3.9 mm](SHANK_DIA) shank clear through, ⌀[6.15 mm](CBORE_DIA)
  counterbore [3.2 mm](CBORE_DEPTH) deep, leaving
  [3.81 mm](LAND_UNDER_HEAD) of land under the head.
- **Fastener** — M3 × [8 mm](SCREW_LEN) DIN 912 socket head cap, black oxide,
  into a ruthex M3 short set into the shell from the land. It reaches
  [4.19 mm](THREAD_REACH) past the plate: the insert's whole 4 mm of body, with
  the rest in the bore's relief.
- **Why one.** The tongue takes both lateral axes the whole way round, so the
  screw has only to pull the plate down onto the shell's land. The skirt bottoms
  there before the bezel touches the device.

## It prints face down

The outer face lies on the bed and every step in the body faces up from there —
the skirt, the tongue, the bezel's underside. The only hanging feature is the
annular ledge at the counterbore, [1.125 mm](CBORE_LEDGE) wide, which bridges.
Bed face: [740 mm²](BED_AREA) over one face, which
`faucet_display_cover.py selftest` checks by measuring the built solid rather
than arguing from these figures.

Same spool as the shell it sits on — Polymaker Fiberon PET-GF15 black
([bom.md §7](/hardware/ledger/bom.md)).

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
