# Cap-sense sleeve

Printed clamshell that wraps a 1/4" OD ([6.35 mm](TUBE_OD)) LLDPE
flavor tube and seats two copper-foil ring electrodes against the
tube wall. Pairs with an MPR121 capacitive touch controller on the
existing I2C bus to sense liquid presence inside the tube (segment 4,
hopper feed in the manifold; can also live on the BiB-feed segments).
The MPR121 reads capacitance between the two foil rings; water in the
tube (~80 dielectric) gives a much larger reading than air (~1).

## Clamshell architecture

Two-piece clamshell, split at y=0 along the tube axis. Same pattern
as `../touch-flo-shell/` tube halves: each half has its cut face on
the build plate, so each half prints support-free with the tube axis
lying horizontal. Joined by friction-fit dowel pins at the cut plane.

Asymmetric features:

- **+y half** — foil grooves (180° arcs on the inner bore) and wire
  exit slots (radial through-wall, +x side, one per groove). The
  functional half. Receives dowel HOLES.
- **−y half** — plain inner bore. The structural cap. Carries
  integrated dowel PINS that protrude into the +y half.

The foil rings install on +y before assembly; -y stays a plain print
with no fiddly inner features. The 180° foil strips still produce a
field spanning the whole tube interior — a full 360° ring isn't
needed for sensing.

## Geometry

| Dimension | Value | Rationale |
|---|---|---|
| Tube OD (reference) | **[6.35 mm](TUBE_OD)** | 1/4" OD LLDPE flavor tubing |
| Inner bore radius | **[3.225 mm](BORE_R)** | tube OD + slip-fit clearance per side; the sleeve sits over the tube without pinching |
| Wall thickness | **[3 mm](WALL_T)** | Solid clamshell shell around the bore — rigid enough that grooves and wire-exit slots don't deform under hand pressure |
| Outer radius | **[6.225 mm](OUTER_R)** | bore + wall |
| Sleeve length | **[17 mm](SLEEVE_L)** | See *Length budget* below |
| Foil groove width (axial) | **[3 mm](GROOVE_W)** | Adequate axial contact area for the foil ring; not so wide that it weakens the bore wall |
| Foil groove pitch (center-to-center) | **[5 mm](GROOVE_PITCH)** | [2 mm](GROOVE_GAP) of full-thickness bore between the two grooves — enough material to keep the inner bore stiff between the two foil rings |
| Foil groove depth | **[0.1 mm](LAYER_H)** | One layer at the project's standard 0.1 mm layer height. Foil tape (~[0.05 mm](FOIL_T) thick) sits in the groove with ~[0.05 mm](FOIL_ADHESIVE_ROOM) of adhesive headroom |
| Groove outer radius | **[3.325 mm](GROOVE_OUTER_R)** | bore + groove depth |
| Wire exit slot Y width | **[2 mm](SLOT_W_Y)** | Wire needs room to bend from circumferential (in the groove) to radial (out of the slot) without stressing the solder joint |
| Wire exit slot Z padding | **[0.5 mm](SLOT_Z_PAD)** | Per side, beyond the groove width — keeps the wire's entry/exit edges off the groove's z corner |
| Dowel radius | **[1 mm](DOWEL_R)** | Same cylinder geometry defines pin and hole; friction fit tuned by trial |
| Dowel protrusion | **[2.5 mm](DOWEL_L)** | Past the cut plane on the bearing half; matching hole is slightly longer so dowels never bottom out before the cut faces seat |
| Dowel X offset | **[4.725 mm](DOWEL_X)** | Mid-wall: (bore_radius + outer_radius) / 2 |
| Dowel Z inset | **[2 mm](DOWEL_Z_INSET)** | From each rim — one dowel near each end on each x side, four per half |

### Length budget

```
[17 mm](SLEEVE_L) sleeve = end zone + groove zone + end zone
                = [4.5 mm](END_ZONE_Z) + [8 mm](GROOVES_TOTAL_Z) + [4.5 mm](END_ZONE_Z)
```

The [8 mm](GROOVES_TOTAL_Z) groove zone is two [3 mm](GROOVE_W) grooves
separated by [2 mm](GROOVE_GAP) of un-grooved bore.

Each end zone is laid out as:

```
rim ── [1 mm](RIM_MARGIN) rim margin ── dowel ([2 mm](DOWEL_D) dia.) ── [1.5 mm](DOWEL_TO_GROOVE) clearance ── groove edge
```

i.e. the [4.5 mm](END_ZONE_Z) end zone = rim margin + dowel diameter + dowel-to-groove clearance.

## Print orientation

Each STEP exports in part coordinates with the cut face at y=0. In
the slicer, rotate −90° about world X to set the cut face on the
build plate; the tube axis then runs along the print's Y axis and
the foil grooves face up. No supports — the inner bore's top half
bridges naturally at this OD.

## Foil install (the +y half, before clamshell mating)

Two copper-foil strips, each [3 mm](GROOVE_W) wide (matching
groove width), are pressed into the +y half's two foil grooves with
the adhesive backing facing the groove floor. The wires solder onto
the foil at the +x edge of each ring and exit through the wire-exit
slot. The −y half then mates against the cut face, dowel-pinned, and
the two halves close around the LLDPE tube.

At coarser layer heights the grooves resolve only marginally; the
fallback is to stick the foil flush against the un-grooved bore.

## Regenerate

```
tools/cad-venv/bin/python cap_sense_sleeve.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/flavor/cap-sense-sleeve/cap_sense_sleeve.py`
