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
        HOME SODA MACHINE          ← the glass mark and the name, one lockup
          SERIAL  0001
       120V 60Hz 5A 600W
        120V 60Hz ONLY
         NOT FOR 240V
   homesodamachine.com/u/0001      ← as wide as the lockup, and it sets that way at every unit
```

The warning offsets the "250V 10A" spec stamp moulded into the C14 inlet standing above it on
the same wall. The link is where everything beyond the printed quick start lives — warranty,
RMA, troubleshooting, BOM, support contact and ongoing care — per
[`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

Not UL-listed or ETL-listed; the plate carries no UL or ETL mark.

## The type

One face, `bulkhead_ring.WORD_FONT`, in two registers. The name and the block are set at
[6.5](TITLE_EM) — `bulkhead_ring.WORD_SIZE`, the em the bulkhead rings beside this plate are
lettered at. The link is set at [6.05](LINK_EM): the em that brings it out at
[88.8 mm](LOCKUP_W), the lockup's own width, so the plate is bracketed top and bottom by two
marks that measure the same. Every serial is four digits and this face sets figures on one
advance, so that holds from unit 0001 to 9999.

The lettering lies in a recess [1 mm](INK_DEPTH) into the plate's face and fills it flush — the
bulkhead ring's construction at another size, printed in a second filament.

## The two screws

| | |
|---|---|
| Head | M3×[8 mm](NAMEPLATE_SCREW_LEN) DIN 912, in a Ø[6.15 mm](CBORE_D) flat counterbore [3 mm](NAMEPLATE_CBORE_DEPTH) deep |
| Land under it | [1.5 mm](NAMEPLATE_LAND), and it is the plate's own section — head plus land is what sets [4.5 mm](NAMEPLATE_T) |
| Seat | Ø[9.15 mm](NAMEPLATE_SEAT_D) of plate round the counterbore, one ligament, and no pad standing off the back |
| Reach | [8 mm](NAMEPLATE_SCREW_REACH) under the head: the land, a ruthex M3 short, and [1.25 mm](BORE_RELIEF) of relief past its tip |
| Boss | Ø[10 mm](BOSS_STEM_D) round the insert, [5 mm](BOSS_REACH) off the plateau. No collar — a collar closes a pad pocket, and there is none |

**The wall thickens to take it.** A pocket [4.5 mm](NAMEPLATE_T) deep is deeper than this wall's
[3 mm](WALL_T) of stock, so the inner face carries a plateau standing to [6 mm](NAMEPLATE_WALL) —
one wall and one `enclosure.rear_seam_clear`. That second figure is the band the pack already
stands off this face, so the plateau reaches exactly the plane the rear Z seam's lip presents the
cold core and stops there, taking nothing the pack was using. Under the pocket it leaves
[1.5 mm](NAMEPLATE_FLOOR) of floor. Its down-facing edge is struck at 45°: the piece prints with
this wall vertical on the bed, and a plateau's underside is the plate's whole width of ceiling
otherwise.

**And the pocket is cut to the plate's whole silhouette, chamfer included** — its floor
[3 mm](PLATE_BEVEL) in from the outline all round, opening out to full size at 45°. This is the
same wall standing vertical on the bed, so the pocket's own head is a down-facing ceiling: cut
square it hangs the pocket's whole [4.5 mm](NAMEPLATE_T) depth, which measures
[443.4 mm²](POCKET_SOFFIT_SQUARE) of flat. Ramped it hangs [1.5 mm](POCKET_RIM), or
[147.8 mm²](POCKET_SOFFIT) — less than the [2 mm](RING_T) pocket hung before the plate ever
thickened. The last [1.5 mm](POCKET_RIM) stays square deliberately: 45° carried out to the face
would read as a V-groove round the plate instead of a flush inlay. The angle is
`enclosure.relief_chamfer`, what every relief ceiling on this box rises at.

**Where they stand is the wall's to say.** The cold core's cap crowns at z 253.4 and the
SeaFlo's aft disc comes down to z 266.4, both standing one `enclosure.wall` off this wall — so
a boss anywhere else on this field is a boss in the core or in the pump. Between them the room
is open from x −28 to 85, and the plate's own horizontal centreline stands on that line. That
is what puts a screw at each end at mid-height. `enclosure_assembly.nameplate_screw_line` is
the figure; `nameplate-field` on the build card is the reading.

## Print settings

A separate print from the enclosure, with its own settings.

- **Lettering up, on a solid plane.** The type is 0.2 mm work and wants laying last, on the face
  looking at the nozzle — which puts the plate's inboard face on the bed. Everything the plate
  carries is sunk into the face that looks up, so that bed face is one plane of
  [5895 mm²](BED_AREA) broken only by the two screw shanks: no support, no bridge, no pad to
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
