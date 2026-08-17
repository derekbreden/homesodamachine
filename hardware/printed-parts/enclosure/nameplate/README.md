# Rear-Wall Nameplate

The plate the machine is named and rated on: [104.53 mm](PLATE_W) × [66.07 mm](PLATE_H) ×
[2 mm](PLATE_T), lying flush in a pocket of `enclosure-back-top`'s outer face, in the field
east of the flavour chips. One plate per unit, serialized. Visible after install.

Cut by [`nameplate.py`](nameplate.py) → `nameplate-NNN.step`; the pocket, the two screw bosses
and their heat-set bores are cut by `enclosure._nameplate` off the same figures.

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
the same wall. The link is where everything not on the printed quick-start sheet lives —
warranty, RMA, troubleshooting, BOM, support contact, ongoing care — per
[`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

Not UL-listed or ETL-listed; the plate carries no UL or ETL mark.

## The type

One face, `port_ring.WORD_FONT`, in two registers. The name and the block are set at
[6.5](TITLE_EM) — `port_ring.WORD_SIZE`, the em the bulkhead chips beside this plate are
lettered at. The link is set at [6.05](LINK_EM): the em that brings it out at
[88.8 mm](LOCKUP_W), the lockup's own width, so the plate is bracketed top and bottom by two
marks that measure the same. Every serial is four digits and this face sets figures on one
advance, so that holds from unit 0001 to 9999.

The lettering lies in a recess [1 mm](INK_DEPTH) into the plate's face and fills it flush — the
port chip's construction at another size, printed in a second filament.

## The two screws

| | |
|---|---|
| Head | M3×[8 mm](SCREW_LEN) DIN 912, in a Ø[6.15 mm](CBORE_D) flat counterbore [3 mm](CBORE_DEPTH) deep |
| Land under it | [1.5 mm](LAND) — the plate thickens by [2.5 mm](PAD_DEPTH) over a Ø[9.15 mm](PAD_D) pad, and the wall is pocketed to take it |
| Reach | [8 mm](SCREW_REACH) under the head: the land, a ruthex M3 short, and [1.25 mm](BORE_RELIEF) of relief past its tip |
| Boss | [8 mm](BOSS_REACH) inboard of the wall's inner face — Ø[14.75 mm](BOSS_COLLAR_D) round the pad's pocket, Ø[10 mm](BOSS_STEM_D) round the insert |

**Where they stand is the wall's to say.** The cold core's cap crowns at z 253.4 and the
SeaFlo's aft disc comes down to z 266.4, both standing one `enclosure.wall` off this wall — so
a boss anywhere else on this field is a boss in the core or in the pump. Between them the room
is open from x −28 to 85, and the plate's own horizontal centreline stands on that line. That
is what puts a screw at each end at mid-height. `enclosure_assembly.nameplate_screw_line` is
the figure; `nameplate-field` on the build card is the reading.

## Print settings

A separate print from the enclosure, with its own settings.

- **Nozzle:** [0.2 mm](NAMEPLATE_NOZZLE_D) (bulk enclosure parts use [0.4 mm](BULK_NOZZLE_D))
- **Layer height:** [0.08](LAYER_H_MIN)–[0.12 mm](LAYER_H_MAX)
- **Two colours:** the plate in PETG Basic Black 30105 and the lettering in White 30106, a
  filament change at the recess floor. No paint; survives kitchen wipe-down.

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
