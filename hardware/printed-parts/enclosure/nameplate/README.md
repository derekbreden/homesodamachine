# Nameplate

The plate the machine is named and rated on: [104.53 mm](PLATE_W) × [66.07 mm](PLATE_H) ×
[4.5 mm](NAMEPLATE_T), corners r[3 mm](PLATE_CORNER) and its back edge chamfered
[3 mm](PLATE_BEVEL) at 45°, lying flush in a pocket of `enclosure-back-top`'s outer face, in the
field east of the flavour rings. One plate per unit, serialized. Visible after install.

Cut by [`nameplate.py`](nameplate.py) → `nameplate-NNN.step`; the pocket, the plateau the wall
thickens to behind it, the two screw bosses and their heat-set bores are cut by
`enclosure._nameplate` off the same figures.

## What it says

```
     [faucet]  HOME                 ← large mark and three lines of large type
               SODA
               MACHINE

    homesodamachine.com/0001        ← centred below the screw line

            SERIAL  0001           ← all details share one small size, each line centred
         120V 60Hz 5A 600W
           120V 60Hz ONLY
            NOT FOR 240V
  [flame] FLAMMABLE REFRIGERANT
```

The details block starts with the serial and ends with a white flame and `FLAMMABLE REFRIGERANT`.
The [install guide](/hardware/install-guide/README.md) records the refrigerant and charge mass.
Product marking requirements are recorded in
[`/business/regulatory.md`](/business/regulatory.md).

[The household refrigerant marking specification](/hardware/markings/README.md)
provides a separate exterior disposal panel and compressor service/tubing panel. Its
6.5 mm capitals satisfy the incorporated household standard's 6.4 mm warning-letter
target. The small nameplate footer is informational and does not replace those panels.
The separate warnings and an adjacent appliance-rating block preserve space for the
brand, serial and QR. The generated plate's `5A 600W` text is unverified study copy;
the household rating specification calls for established input current in amperes.

The warning offsets the "250V 10A" spec stamp moulded into the C14 inlet standing above it on
the same wall. The link opens the machine overview, included-equipment list, preparation
checklist, and links to the quick start, install guide, and care pages. The routes are described
in [`/future/unit-links.md`](/future/unit-links.md).

Not UL-listed or ETL-listed; the plate carries no UL or ETL mark.

## The type

One face, `bulkhead_ring.WORD_FONT`, in three levels:

- The brand: a [28 mm](LOGO_H) On tap faucet and drop beside `HOME`, `SODA` and `MACHINE` on three lines,
  set at [10.2](TITLE_EM), with caps [7.77 mm](TITLE_CAP) high and [2.8 mm](TITLE_GAP) between lines.
  The complete lockup is [78.63 mm](LOCKUP_W) wide.
- The unit link: [5.5](LINK_EM), caps [4.19 mm](LINK_CAP) high, centred below the screw line.
  Its width is [75.08 mm](LINK_W). Every serial is four digits on one advance, so its width
  holds from unit 0001 to 9999.
- The details: serial, ratings, voltage warnings and refrigerant notice at [2.8](BODY_EM),
  with caps [2.13 mm](BODY_CAP) high, each line centred on the plate with equal line spacing.
  Each letter has [0.1 mm](DETAIL_TRACKING) of extra spacing. The [2.13 mm](FLAME_H) flame and
  refrigerant wording are centred together as the final line, with the flame at cap height.

The detail letter strokes and the plate between adjacent letters are measured against the print
profile's 0.22 mm bead.

The lettering lies in a recess [1 mm](INK_DEPTH) into the plate's face and fills it flush — the
bulkhead ring's construction at another size, printed in a second filament.

The faucet and drop are read directly from [`brand/mark.svg`](/brand/mark.svg), with the
master's proportions and circular arcs. Both print in the white inlay.

## The two screws

| | |
|---|---|
| Head | M3×[8 mm](NAMEPLATE_SCREW_LEN) DIN 912, in a Ø[5.8 mm](CBORE_D) flat counterbore [3 mm](NAMEPLATE_CBORE_DEPTH) deep |
| Land under it | [1.5 mm](NAMEPLATE_LAND), and it is the plate's own section — head plus land is what sets [4.5 mm](NAMEPLATE_T) |
| Seat | Ø[8.8 mm](NAMEPLATE_SEAT_D) of plate round the counterbore, one ligament, and no pad standing off the back |
| Reach | [8 mm](NAMEPLATE_SCREW_REACH) under the head: the land, a ruthex M3 short, and [1.25 mm](BORE_RELIEF) of relief past its tip |
| Boss | [7 mm](BOSS_STEM_D) wide, [5 mm](BOSS_REACH) off the plateau: round above the insert, square below its tangents, and carried to the wall on a full-width 45° corbel. No collar — a collar closes a pad pocket, and there is none |

**The wall thickens to take it.** A pocket [4.5 mm](NAMEPLATE_T) deep is deeper than this wall's
[3 mm](WALL_T) of stock, so the inner face carries a plateau standing to [6 mm](NAMEPLATE_WALL) —
one wall and one `enclosure.rear_seam_clear`. That second figure is the band the pack already
stands off this face, so the plateau reaches exactly the plane the rear Z seam's lip presents the
cold core and stops there, taking nothing the pack was using. Under the pocket it leaves
[1.5 mm](NAMEPLATE_FLOOR) of floor. Its down-facing edge is struck at 45°: the piece prints with
this wall vertical on the bed, and a plateau's underside is the plate's whole width of ceiling
otherwise.

**The pocket follows the plate's silhouette with 0.15 mm normal clearance.** Its outline
and corner radii expand by [0.15 mm](PLATE_SLIP); its 45° bevel is
[2.938 mm](POCKET_BEVEL), preserving that same clearance along the bevel faces.
The pocket remains [4.5 mm](NAMEPLATE_T) deep, with a flat rim
[1.562 mm](POCKET_RIM) deep and [153.9 mm²](POCKET_SOFFIT) of flat ceiling.
The supported edge receives the enclosure's additional 0.25 mm relief toward print-up.

**Where they stand is the wall's to say.** The cold core's cap crowns at z 253.4 and the
SeaFlo's aft disc comes down to z 266.4, both standing one `enclosure.wall` off this wall. The
plate's horizontal centreline is therefore the lowest line that leaves the corbel one millimetre
over the cap; the pump's rounded aft disc leaves more at the west screw and the PSU leaves more
at the east one. `enclosure_assembly.nameplate_screw_line` is the figure.

**The squared lower half is part of the corbel.** It gives the wedge one full-width face to carry
while the upper half remains the standard M3 boss section around the insert. The two screw
supports are identical.

## Print settings

A separate print from the enclosure, with its own settings.

- **Lettering up, on a solid plane.** The type is 0.2 mm work and wants laying last, on the face
  looking at the nozzle — which puts the plate's inboard face on the bed. Everything the plate
  carries is sunk into the face that looks up, so that bed face is one plane of
  [5902 mm²](BED_AREA) broken only by the two screw shanks: no support, no bridge, no pad to
  stand on. It is what the [4.5 mm](NAMEPLATE_T) section buys.
- **The back edge is chamfered** [3 mm](PLATE_BEVEL) at 45°, so the first layer is inset all
  round and the outline grows out to full size over three millimetres. No elephant's foot on the
  rim the customer can see, and no arris to catch the pocket's inside corner on the way in. At
  [3 mm](PLATE_BEVEL) the corner rounds come to nothing on the bed, so the first layer is a plain
  rectangle. **The pocket is cut to that chamfer too** — see below; it is the wall's relief as
  much as the plate's.
- **Nozzle:** [0.2 mm](NAMEPLATE_NOZZLE_D) (bulk enclosure parts use [0.4 mm](BULK_NOZZLE_D))
- **Layer height:** [0.08](LAYER_H_MIN)–[0.12 mm](LAYER_H_MAX)
- **Two colours:** the plate in PETG Basic Black 30105 and the lettering in White 30106, a
  filament change at the recess floor — [3.5 mm](INK_FLOOR) up, with [1 mm](INK_DEPTH) of type
  over it. No paint; survives kitchen wipe-down.

## Per-unit generation

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 27
```

emits `nameplate-027.step` — the plate and its lettering as two bodies of one part, each in the
filament it comes off. `nameplate-001.step` is the one the assembly stands.

The signature the Founder Edition story asks for is not on the plate. Laser-engraving it onto
the printed plate after the print is the open item, and the decision waits on the first plate
off the bed.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py`
- `/hardware/printed-parts/enclosure/nameplate/nameplate.py`
