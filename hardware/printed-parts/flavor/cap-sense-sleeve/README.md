# Cap-sense sleeve

Printed clamshell that wraps a 1/4" OD ([6.35 mm](TUBE_OD)) LLDPE
flavor tube and seats two copper-foil ring electrodes against the
tube wall. Pairs with an MPR121 capacitive touch controller on the
existing I2C bus to sense liquid presence inside the tube (segment 4,
hopper feed in the manifold; can also live on the BiB-feed segments).
The MPR121 reads capacitance between the two foil rings; water in the
tube (~80 dielectric) gives a much larger reading than air (~1).

## Wiring

The MPR121 mounts off-board next to the sleeves at the manifold (short
electrode leads keep the reading clean) and plugs into the pcba's **J8
I2C header** — GND / 3V3 / SDA / SCL, all plane nets, so it rides the
existing bus at address 0x5A with **no ESP32 GPIO**. Each sleeve's two
foil rings wire to a pair of the MPR121's 12 electrode inputs; poll it,
or route its IRQ to a spare pin for event-driven reads. J8 is on the
board's south edge — see the I2C bus in
[`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd).

## Clamshell architecture

Two-piece clamshell, split at y=0 along the tube axis. Joined by
friction-fit dowel pins at the cut plane.

- **+y half** — foil grooves (180° arcs on the inner bore) and wire
  exit slots (radial through-wall, +x side, one per groove). Receives
  dowel holes.
- **−y half** — plain inner bore. Carries integrated dowel pins that
  protrude into the +y half.

The foil rings install on +y before assembly. The 180° foil strips
produce a field spanning the tube interior.

## Geometry

| Dimension | Value |
|---|---|
| Tube OD (reference) | **[6.35 mm](TUBE_OD)** |
| Inner bore radius | **[3.225 mm](BORE_R)** |
| Wall thickness | **[3 mm](CSENSE_WALL_T)** |
| Outer radius | **[6.225 mm](OUTER_R)** |
| Sleeve length | **[17 mm](SLEEVE_L)** |
| Foil groove width (axial) | **[3 mm](GROOVE_W)** |
| Foil groove pitch (center-to-center) | **[5 mm](GROOVE_PITCH)** |
| Foil groove depth | **[0.1 mm](LAYER_H)** |
| Groove outer radius | **[3.325 mm](GROOVE_OUTER_R)** |
| Wire exit slot Y width | **[2 mm](SLOT_W_Y)** |
| Wire exit slot Z padding | **[0.5 mm](SLOT_Z_PAD)** |
| Dowel radius | **[1 mm](DOWEL_R)** |
| Dowel protrusion | **[2.5 mm](DOWEL_L)** |
| Dowel X offset | **[4.725 mm](DOWEL_X)** |
| Dowel Z inset | **[2 mm](DOWEL_Z_INSET)** |

## Print orientation

Each STEP exports in part coordinates with the cut face at y=0. In
the slicer, rotate −90° about world X to set the cut face on the
build plate; the tube axis runs along the print's Y axis and the
foil grooves face up.

## Foil install (the +y half, before clamshell mating)

Two copper-foil strips, each [3 mm](GROOVE_W) wide, are pressed into
the +y half's two foil grooves with the adhesive backing facing the
groove floor. The wires solder onto the foil at the +x edge of each
ring and exit through the wire-exit slot. The −y half then mates
against the cut face, dowel-pinned, and the two halves close around
the LLDPE tube.

## Regenerate

```
tools/cad-venv/bin/python cap_sense_sleeve.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/flavor/cap-sense-sleeve/cap_sense_sleeve.py`
