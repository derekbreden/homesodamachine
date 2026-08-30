# Faucet display cover plate

The printed face plate over the faucet display, and the only thing holding the
device in. A hand meets its outer face as the top of the cradle, unbroken from
the collar below it but for one seam and one screw head. It laps the device's
face on all four edges, comes down over its housing, threads a single M3 into
the shell above the device's north edge, and hooks under the shell's south wall
at the other end.

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

**A butt, the whole way round.** The plate sits on the shell's land and nothing
crosses the line but the hook. The tip end face keeps the one horizontal line
across it that the parting gives it.

## The hook

The screw is at the far end of the plate, so on its own it would leave the
bezel's grip on the device's bottom edge hanging off 50 mm of cantilever. The
wall between the device and the dispense end carries the other end instead.

That wall's inner face is [5.3 mm](CRADLE_WALL_H) tall, and it divides:

| from | to | | whose |
|---|---|---|---|
| [11.9](FLOOR_N) | [12.4](HOOK_N0) | [0.5 mm](HOOK_RELIEF) air | void |
| [12.4](HOOK_N0) | [14.65](HOOK_N_TOP) | [2.25 mm](HOOK_T) tongue | plate |
| [14.65](HOOK_N_TOP) | [14.8](HOOK_N1) | [0.15 mm](HOOK_GAP) clearance | void |
| [14.8](HOOK_N1) | [17.2 mm](PLATE_N_BOTTOM) | [2.4 mm](ROOF_T) roof | shell |

The top band stands [1.86 mm](HOOK_LAP) further up-gooseneck than the wall under
it, cantilevered off the end-face skin, and the plate's tongue goes under it: a
riser down the notch and a toe reaching back beneath the roof. The tongue is
[13 mm](HOOK_X) wide — the flat of the cavity's rounded end — and full-height
wall is left standing either side of the notch, which is what still stops the
device.

**It goes in by sliding.** The plate is set down
[2.01 mm](HOOK_TRAVEL) up-gooseneck of home, where the toe clears the roof and
the notch takes it straight down, then pushed toward the spout until the riser
stops against the roof's face. Then the screw, which is what keeps it there.

**What it costs.** The wall it needs is a skin to carry the roof, the roof's own
reach, the riser, and the travel — [7.59 mm](S_BOTTOM) of it, against the
[1.86 mm](COVER_WALL) a plain wall would have been. That is why the device sits
that far up the tip, and why the plate's chin below the window is
[9.84 mm](CHIN) rather than 4.11.

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

One, on the centreline at s = [56.45 mm](SCREW_S) — north of the device, in the
head wall the cradle already had.

- **Seat** — ⌀[3.9 mm](SHANK_DIA) shank clear through, ⌀[6.15 mm](CBORE_DIA)
  counterbore [3.2 mm](CBORE_DEPTH) deep, leaving
  [3.81 mm](LAND_UNDER_HEAD) of land under the head.
- **Fastener** — M3 × [8 mm](SCREW_LEN) DIN 912 socket head cap, black oxide,
  into a ruthex M3 short set into the shell from the land. It reaches
  [4.19 mm](THREAD_REACH) past the plate: the insert's whole 4 mm of body, with
  the rest in the bore's relief.
- **Why one.** The hook holds the other end, so the screw has only to pull the
  plate down onto the shell's land and keep it from sliding back off the hook.
  The skirt bottoms on the land before the bezel touches the device.

## It prints standing on the tip end

The tip-end face is the bed — [201 mm²](BED_AREA) over one face — and the outer
face rises from it as a [905 mm²](SHOW_AREA) wall, so the show surface carries
no support scars, and the counterbore's ledge and the bezel's underside stand
as walls beside it. Every face that hangs looks down the gooseneck:

| s | face | support |
|---|---|---|
| [52.59 mm](POCKET_S_TOP) | the pocket's north ceiling | the one tall tower the print needs |
| [50.34 mm](WINDOW_S_NORTH) | the window's north wall | the window slot's own |
| [3.72 mm](STEM_S0) | the riser's south face | filmed by the pocket tower it adjoins |
| [2.01 mm](HOOK_S0) | the toe's south face | the same tower's foot |

The two short faces would read as defects by the enclosure's support numbers —
under 5 mm, in the hook's crevice — and cost nothing here: their films grow
from the same connected void as the pocket's tower, and one pull on the tower
takes them out with it. The toe's top face stays flat rather than ramped — a
ramp there would let the hook cam out under the screw's own shank clearance.
The shell pays nothing for the matching face: the roof's underside looks straight
down the cradle's normal, which in the tip's print orientation is
[35°](MAX_PRINT_OVERHANG), the same its swept flanks carry.
`faucet_display_cover.py selftest` measures the show face and the bed face off
the built solid rather than arguing from these figures.

Same spool as the shell it sits on — Polymaker Fiberon PET-GF15 black
([bom.md §7](/hardware/ledger/bom.md)).

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
