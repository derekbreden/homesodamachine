# Cold core layout

The cold core with everything inside it, in one frame: the carbonator vessel, the coil wound on
it, both flavour reservoirs, every fitting made up on every port, and the lines drawn among
them. Built by [`cold_core_assembly.py`](cold_core_assembly.py) →
`cold-core-assembly.step`, with the `.scorecard.json` beside it that the 3D viewer's bottom bar
reads at [`/3d`](https://homesodamachine.com/3d).

[`printed-parts/cold-core/foam-assembly`](/hardware/printed-parts/cold-core/foam-assembly/) is
the same stack one frame out — five printed pieces, the faces the enclosure loads and stands
its own bodies off. `enclosure_assembly` places THAT, as one solid with a port table.

## Frame

The foam shell's own. Z up, the shell floor's outer face at z = 0, the shell's open top at
[213.4](SHELL_TOP). ±Y is the vessel's port axis; +X is the register azimuth, which the float
rod and the reed bridge share. `foam_assembly.stack_floor_z` and `.cap_face_z` are the two
planes the appliance reads off the stack.

## What is here

| | |
|---|---|
| foam stack | shell, both caps, both lids — loaded from `foam-assembly` |
| vessel | 5" × 0.065" 316 tube, two 1/4" endcap plates recessed one thickness in, the 1/8" 316L float rod between their blind registers |
| vessel fittings | four TAISHER street elbows, one per tapped port; the SV-125 and its shroud on port 4 |
| pockets | both reservoirs and their caps |
| wall | the three copper plugs, in their own slots |
| lines | the seven `_internal_routes` centrelines, each drawn at the arc its corridor leaves |

## The card

Reporting, not gating — a finding lands in the card and on the terminal and the STEP still
writes. `bodies-clear` is the axis the work is on.

```
tools/cad-venv/bin/python hardware/cold-core-layout/cold_core_assembly.py
```

## Where a fitting's figures come from

[`_fittings.py`](_fittings.py) builds each purchased body to its catalog envelope; each figure
carries its source. Two of them are struck off parts this repo owns rather than off a catalog:
the elbow hex is sized by the ⌀19 bore `prv-shroud` presents to it, and the male leg's standoff
is `hole_shift_from_edge + plate_recess`, which is where the shell's own storeys put the band
each line crosses on.
