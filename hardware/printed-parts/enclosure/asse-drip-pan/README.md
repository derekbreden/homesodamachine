# ASSE drip pan

One PETG pan catches the ASSE 1022 atmospheric vent's drips. The Shutao moisture
plate lies loose on its floor and trips the alarm when water pools there. The pan
has no drain or cable opening; it draws out through the −X wall for emptying.

| | Pan |
| --- | --- |
| Basin outside | [51](PAN_LEN) × [76](PAN_DEPTH) × [15](PAN_HEIGHT) mm |
| Walls and floor | [2.5](PAN_WALL) and [3](PAN_FLOOR) mm |
| Capacity to rim | [39.2](PAN_CAPACITY) mL |
| Pull face | [5.95](PULL_FACE_DEPTH) mm proud of the enclosure; [4](PULL_FACE_Y_OVERHANG) mm wider than the basin on each Y side |

The basin is one rectangular box with a matching hollow and r[2](PAN_COVE_R)
floor coves. Its square outside corners meet the slot floor and roof across
the wall's full thickness. The pull face is fused to its west end. Its four
[2.5](PULL_FACE_CHAMFER) mm 45° corners leave a full-height section across the
wall slot, and its inner face rests against the enclosure's exterior wall to
stop insertion. The printed pan is one watertight solid.

The back-top's 9 mm west flank has one rectangular through-slot.
It follows the basin's [76](PAN_DEPTH) × [15](PAN_HEIGHT) mm YZ section with
0.25 mm running room on both Y sides and above. Back-top prints ceiling-down;
its 0.25 mm supported-face allowance gives the bottom the same running room.
The pan's floor bears on the slot floor and its two end-wall rims bear on the
slot roof. Those surfaces hold the pan horizontal through the wall's full
9 mm thickness. The pull face spans the slot's Y edges and stops on the
outside face. No printed material projects into the enclosure around the pan.

The open rim stands [4](PAN_VENT_GAP) mm below the ASSE chain's underside.
The pan is 8.25 mm clear of the pump casting at its east end.
Its forward edge stands beyond the pump's discharge root. The vent drips into
the pan's flat floor inside its coves.

The moisture plate is [54](PLATE_LEN) × [40](PLATE_DEPTH) mm. It lies with its
long axis along the pan's Y, on the 42 × 67 mm flat floor inside the coves,
with [1](PLATE_SLIP_MM) mm of room on each side. Its continuous lead rises out
of the open mouth to the cable clip on the dry flank below the slot. Draw the
pan west until the plate is reachable, lift the plate from the pan, then draw
the pan the rest of the way out.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/asse-drip-pan/asse_drip_pan.py
```

This writes the STEP solid and printable STL.

## Sources

[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/asse-drip-pan/asse_drip_pan.py`
