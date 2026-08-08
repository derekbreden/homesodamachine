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
| power box | [45](POWER_X) × [27.5](POWER_Y) × [45](POWER_Z) | centered on X, filling the plate's long reach at −Y, hanging off the shell with its underside at [30](POWER_Z0) |

Overall **[110](SHELL_X) × [160](BASE_Y) × [135](OVERALL_H) mm** — and the three
figures come from three different places. The width is the *shell's*, the depth is
the *plate's*, and the height is the two stacked.

The shell is a cylinder pressed slightly oblong: viewed down Z it is an ellipse,
[110](SHELL_X) across the machine and [125](SHELL_Y) along it.

## Overhang and offset

**The belly overhangs its own plate.** The shell is [110](SHELL_X) across and the
plate only [96](BASE_X), so the widest part of the compressor is
[7](SHELL_OVERHANG_X) mm proud of its footprint on each side — and it starts
[15](BASE_Z) mm up, not at the deck. A wall set to clear the plate does not clear
the shell.

**The shell is off-center on the plate.** The offset leaves
[27.5](PLATE_REACH_LONG) mm of plate reaching past the shell at −Y and
[7.5](PLATE_REACH_SHORT) mm at +Y. The **power box** stands in that long reach —
[27.5](POWER_Y) mm deep, the reach exactly, its aft face on the shell's own tangent
plane at y = [-52.5](SHELL_TANGENT_Y). It hangs off the shell, not off the plate:
underside at z = [30](POWER_Z0), crown at z = [75](POWER_Z1), with air between it and the
plate's crown. The box carries the compressor's terminal block
and clip-on PTC start relay under the donor's own moulded cover, and it is the one feature
that tells the two ends apart: **−Y is the power end.**

## Mounting

Four Ø[14](MOUNT_D) mm holes through the plate, each inset
[14.5](MOUNT_INSET) mm from both edges it sits in from — center to center
**[67](MOUNT_PITCH_X) × [131](MOUNT_PITCH_Y) mm**, symmetric about the origin.

That inset leaves **[7.5](MOUNT_LIGAMENT) mm of plate** outboard of each hole — the
ligament the plate keeps between a hole and the edge it is inset from. `mounts_hold()`
raises in `selftest()` if a figure ever moves far enough to close it and open the hole into a slot.

## Frame

Z = 0 is the **mounting plane**, the plate's underside. The plate is centered on the
origin, so a floor carrying this bolt pattern carries it about its own center.

The bolt pattern is symmetric about that origin; the power box is not. **−Y is the
power end** — that is what orients the part. The suction, discharge and process stubs
are **not modeled**.

## Holds

`selftest()` reads all three back off the solid:

| hold | what it catches |
|---|---|
| `envelope_hold()` | the six faces the machine clears, and the underside sitting on Z = 0 |
| `shell_hold()` | the shell going round — a cylinder on the larger axis fills the same bounding box and [14](CYL_EXCESS_PCT)% more of it |
| `power_hold()` | the box coming off the reach it fills, hanging off the plate's X, sitting down on the plate or climbing past the shell's crown, or covering a mount |
| `mounts_hold()` | a hole opening into the plate's edge, or standing under the belly where no bolt reaches it |

## Where it stands

Which way the compressor faces and what stands beside it is the machine's, not this
module's — [`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) and
[`../../printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).
It sits on the enclosure floor slab and is bolted down to it: `enclosure._floor_bosses`
stands a post under each of the four plate holes, and each rises *through* its hole to
the plate's crown, so the posts locate the part as well as fasten it.

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
