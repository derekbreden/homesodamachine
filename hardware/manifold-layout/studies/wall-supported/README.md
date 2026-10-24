# Wall-supported arrangement

The C14 is horizontal in the upper dry rear corner, with 5.15 mm to the left
interior wall and 4.94 mm to the ordinary roof. Its flange origin is
`(-68.5, 471.3, 330)` mm. The rear wall carries its flange pocket and two
40.21 mm-pitch mounting holes. The opening clears the scanned rim; the face
is exposed without a deep cord tunnel.

The RJ11 face is at `(-30, 471.3, 274.376)` mm, beside the bottom umbilical row.
Its receptacle includes the existing 3 mm lip, insertion ease and snap catches.
A broad 0.7 mm extension behind the 9 mm rear wall carries the required
9.7 mm capture depth. The jack's estimated body clears the pump by 5.02 mm,
the supply by 6.75 mm and the pump slider by 3.26 mm. The ground stud and WAGO
junctions are deferred until the primary parts and full wire routes are placed.

Both Teyleten relays mount directly on the dry sidewall, above the flat Mean
Well. Their boards face inward, their contact terminals point aft, and their
control headers point fore. Their PCB underside centers are
`(-94.5, 398, 303)` and `(-94.5, 398, 328)` mm. Four integral Ø8 mm bosses per
board project 4 mm, leaving 2 mm behind the modeled pin tails. Ø4 mm,
7.5 mm-deep blind pilots accept RX-M3×5.7 inserts and leave 5.5 mm to the outer
wall. M3×8 screws through the 1.5 mm boards have 1 mm nominal tip reserve.
The [existing insert specification](../../../printed-parts/enclosure/enclosure/heat-set-review/README.md)
provides the supplier pilot and stock requirements. No additional PSU shell
is included.

V-K and V-A each sit on one broad raised plate fused to their nearest sidewall.
The plates use the existing four-post pattern, V69 sockets, bearing plane and
port channel from the [valve seat](../../../printed-parts/valve-seat/README.md).
Their 9.2 mm depth includes 3 mm behind the blind socket floors. The space
under each plate remains open; each lower fitting clears its plate by about
2.68 mm. There is no floor-height crosswall or separate support piece.

The [native build](build.py) exports each complete wall as one valid solid.
Highlight meshes duplicate only the added features for the transparent-wall
viewer; they are not separate printable pieces. The [selected mesh query](study.json)
reports no unrelated body or local-connection interference. The
[40 mm screwdriver probes](access-audit.json) clear the retained fixed parts;
these shafts do not establish hand or full-length driver clearance. Use a
compact/right-angle driver for the inward-facing relay terminals, or wire
before final mounting. Fit the relay
mounting screws before landing COM; its straight local lead crosses one
mounting-screw tool path on each board.

The selected water group, PCB, folded CO₂ path and roof pockets retain their
co2-fold poses. Production shell migration, complete tube/wire routes, the
proposed core gas guide, PSU/PCB retention and final valve retention remain
outside this arrangement. The V69 fit acceptance and the earlier RJ11 print
fit retain their identified article/orientation scope. These native seats do
not establish installed fit or load capacity in the new shell.

```sh
PYTHONPATH=. tmp/takeover/cadq "Wall-supported layout" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/wall-supported/build.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/wall-supported/study.py --check
tools/cad-venv/bin/python hardware/manifold-layout/studies/wall-supported/access.py
```
