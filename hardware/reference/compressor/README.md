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

Two bodies. A stamped base plate, and an oblong shell standing on it.

| body | size | stands |
|---|---|---|
| plate | × × | centered on the origin, underside on the mounting plane |
| shell | × ellipse × | centered on X, offset on Y, on the plate's crown |
| power box | × × | centered on X, filling the plate's long reach at −Y, hanging off the shell with its underside at |

Overall ** × × mm** — and the three
figures come from three different places. The width is the *shell's*, the depth is
the *plate's*, and the height is the two stacked.

The shell is a cylinder pressed slightly oblong: viewed down Z it is an ellipse,
 across the machine and along it.

## Overhang and offset

**The belly overhangs its own plate.** The shell is across and the
plate only, so the widest part of the compressor is
 mm proud of its footprint on each side — and it starts
 mm up, not at the deck. A wall set to clear the plate does not clear
the shell.

**The shell is off-center on the plate.** The offset leaves
 mm of plate reaching past the shell at −Y and
 mm at +Y. The **power box** stands in that long reach —
 mm deep, the reach exactly, its aft face on the shell's own tangent
plane at y =. It hangs off the shell, not off the plate:
underside at z =, crown at z =, with air between it and the
plate's crown. The box carries the compressor's terminal block
and clip-on PTC start relay under the donor's own moulded cover, and it is the one feature
that tells the two ends apart: **−Y is the power end.**

## Mounting

Four Ø mm holes through the plate, each inset
 mm from both edges it sits in from — center to center
** × mm**, symmetric about the origin.

That inset leaves ** mm of plate** outboard of each hole — the
ligament the plate keeps between a hole and the edge it is inset from. `mounts_hold()`
raises in `selftest()` if a figure ever moves far enough to close it and open the hole into a slot.

## Frame

Z = 0 is the **mounting plane**, the plate's underside. The plate is centered on the
origin, so a floor carrying this bolt pattern carries it about its own center.

The bolt pattern is symmetric about that origin; the power box is not. **−Y is the
power end** — that is what orients the part. The suction, discharge and process stubs
are **not modeled**; all three are stations instead, so a line brazed into one and a
valve clamped on one both answer to the can.

## The process tube

The third stub, and the only one not in the loop: a short copper tube pinched and brazed
shut at the factory ([`../ice-maker/README.md`](/hardware/reference/ice-maker/README.md)
"Process tube"). It leaves the −X tangent — the same flank the suction leaves by — at
z =, mm above the suction's own station, so
the saddle and the suction leg share one lane down the machine's west side.

`process_tube()` reads mm out along that stub, where the Supco
BPV31's saddle bands it. The valve goes on once and stays for the life of the appliance —
[`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

## Holds

`selftest()` runs:

| hold | what it catches |
|---|---|
| `power_hold()` | the box coming off the reach it fills, sitting down on the plate, or covering a mount |
| `mounts_hold()` | a hole opening into the plate's edge, or standing under the belly where no bolt reaches it |
| `stations_hold()` | a loop stub standing outside the shell's standing height |

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
