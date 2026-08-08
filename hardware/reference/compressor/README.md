# Compressor — donor primitive

The refrigeration loop's cold end driver: a hermetic reciprocating compressor
harvested from the donor appliance alongside the condenser block, the capillary
tube and the factory drier. NingBo Anuodan / HuaJun **HD48Y11A**, 110-120 V ~
60 Hz 1 PH, ~90-120 W class — nameplate and circuit topology in
[`../ice-maker/README.md`](/hardware/reference/ice-maker/README.md).

There is no vendor solid and no scan. The part was calipered, and
[`compressor.py`](compressor.py) draws the envelope the pack takes of it and the
bolt pattern it stands on. `compressor.step` is that envelope, for the viewer and
for anyone measuring clearance against it.

## Geometry (calipered)

Two bodies. A stamped mounting plate, and an oblong shell standing on it.

| body | size | stands |
|---|---|---|
| plate | [96](BASE_X) × [160](BASE_Y) × [15](BASE_Z) | centered on the origin, underside on the mounting plane |
| shell | [110](SHELL_X) × [125](SHELL_Y) ellipse × [120](SHELL_Z) | centered on X, offset [10](SHELL_OFFSET_Y) on Y, on the plate's crown |

Overall **[110](SHELL_X) × [160](BASE_Y) × [135](OVERALL_H) mm** — and the three
figures come from three different places. The width is the *shell's*, the depth is
the *plate's*, and the height is the two stacked.

The shell is a cylinder pressed slightly oblong: viewed down Z it is an ellipse,
[110](SHELL_X) across the machine and [125](SHELL_Y) along it.

## What the envelope does that a box would not

**The belly overhangs its own plate.** The shell is [110](SHELL_X) across and the
plate only [96](BASE_X), so the widest part of the compressor is
[7](SHELL_OVERHANG_X) mm proud of its footprint on each side — and it starts
[15](BASE_Z) mm up, not at the deck. A wall set to clear the plate does not clear
the shell.

**The shell is off-center on the plate.** The offset leaves
[27.5](PLATE_REACH_LONG) mm of plate reaching past the shell at −Y and
[7.5](PLATE_REACH_SHORT) mm at +Y.

## Mounting

Four Ø[14](MOUNT_D) mm holes through the plate, each inset
[7.5](MOUNT_INSET) mm from both edges it sits in from — center to center
**[81](MOUNT_PITCH_X) × [145](MOUNT_PITCH_Y) mm**, symmetric about the origin.

That inset leaves **[0.5](MOUNT_LIGAMENT) mm of plate** outboard of each hole: the
hole is very nearly tangent to both edges, and on a stamped plate that ligament is
the whole of the bolt's hold in that direction. `mounts_hold()` fails the build if a
figure ever moves far enough to open it into a slot.

## Frame

Z = 0 is the **mounting plane**, the plate's underside. The plate is centered on the
origin, so a floor carrying this bolt pattern carries it about its own center.

Nothing on this envelope tells the two Y ends apart — the suction, discharge and
process stubs, the terminal block and its clip-on PTC start relay / overload module
are **not modeled**. Which end the plate's long reach serves is settled where the
part is placed, and on a symmetric bolt pattern it drops on either way round.

## Holds

`selftest()` reads all three back off the solid:

| hold | what it catches |
|---|---|
| `envelope_hold()` | the six faces the machine clears, and the underside sitting on Z = 0 |
| `shell_hold()` | the shell going round — a cylinder on the larger axis fills the same bounding box and [14](CYL_EXCESS_PCT)% more of it, which only volume sees |
| `mounts_hold()` | a hole opening into the plate's edge, or standing under the belly where no bolt reaches it |

## Where it stands

Which way the compressor faces and what stands beside it is the machine's, not this
module's — [`front_half.py`](/hardware/manifold-layout/front_half.py) and
[`../../printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).
It sits on the enclosure floor slab under the
[compressor shroud](/hardware/cut-parts/compressor-shroud/README.md), which drops
over it from above and clears its feet at the open bottom.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/compressor/compressor.py
```

```
tools/cad-venv/bin/python hardware/reference/compressor/compressor.py selftest
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/reference/compressor/compressor.py`
