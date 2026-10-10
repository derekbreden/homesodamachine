# Industrial faucet PET-GF print project

The [selected Mark2 print](prints/2026-10-10-shoulders012-wing050-restored-joint-mark2/README.md)
contains all five rigid parts, including the accepted side-down lever replica.
It uses 0.20 mm first bed layers and 0.24 mm layers above them, with 0.12 mm
layers on the base only at print Z13.40–29.00 and Z55.16–68.12 mm. Those bands
cover the two selected annular shoulder faces. Mark2's +0.04 mm requested
trim emits +0.02 mm on Textured PEI. Its native estimate is recorded in the selected job.

The [selection record](selected-print.json) binds the prepared project,
native archive, five source meshes and the complete physical reference.
The base uses one continuous six-wall solid foot and Arachne wall widths;
its native paths are reviewed for repeated starts/stops at the three
screw-host boundaries and all three insert backing regions. Global support
and motion settings match the successful variable-layer reference.
The Industrial cover has 0.50 mm longer wings and matching arch headroom,
with its retaining-lip datum preserved. The shared tip has an unsealed
Ø4 mm overflow drip hole, smooth tangent passage walls around the tubes and
flat ribbon, and 3 mm of local clearance beyond the drain mouth. The curved
joint is at 70°, with a female base and male tip; the tip prints at −105°.
The flavor pair shares a smooth capsule without a central divider or cusp. No intermediate guide
discs, drain bung or insertion tool is fitted. The selected launch receipt
records submission and acceptance separately.

The [physical reference](prints/2026-10-09-two-shoulders008-with-lever-mark2/physical-result/physical-result.json)
records beautiful 0.08 mm shoulder finish and successful removal of its few
thin-layer supports, with exterior lines beside the three screw points.
The 0.12 mm finish, corrected exterior, extended-cover seating and new drip
behavior require physical observation on the complete candidate.

Variable layer height is Derek's accepted shipping compromise. Further
whole-faucet 0.08 mm iteration and research are deferred. The
[tip starting-band result](prints/2026-10-09-tip-root024-mark2/physical-result/physical-result.json)
records tip and wing disruption without establishing its initiating cause.
Physical finish and support cleanup do not establish load capacity or endurance.

The retained four-part 0.24 mm sealed-cavity project and its preparation
workflow are described below. Its exact native archive is not the
current five-part faucet and does not contain its new tip or extended cover.

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the
Industrial shell base, display cover and counter plate with the shared faucet
tip. The [native print archive](../vent-print-readiness/faucet-industrial-black-z018-h2c/faucet-industrial-black-z018-h2c.gcode.3mf)
is prepared for Polymaker PET-GF on H2C's left 0.4 mm nozzle. Black and white
use the same geometry. The matching countertop gasket is on the
[Industrial TPU plate](../asse-vent-seals/vent-bungs-industrial-tpu85a.3mf).

| Position | Part | CAD X rotation |
| --- | --- | ---: |
| Left | Industrial shell base | −15° |
| Right rear | Shared faucet shell tip | −95° |
| Far right rear | Industrial display cover | −50° |
| Right front | Industrial above-counter plate | 0° |

The tip's open 50° neck joint, bottom port and display pocket provide cleanup
access. The cover's visible bezel faces up with an open underside. The plate
rests on its gasket face with pedestals up. The straight neck is 15° from
vertical. Cover preload is 1.25 mm per wing with 1.20 mm groove engagement;
the cover is 29.8 mm wide with 1.25 mm nominal lower side walls.
The [cover reading](display-cover-check.json) checks its geometry against
the shared tip, display and tubes. Physical acceptance remains scoped to the
[identified Sculpted article](../faucet-display-cover/physical-acceptance.json).

The mature PET-GF process uses 0.24 mm layers and a 0.20 mm first layer,
two walls, 15% grid infill, 265/280 °C nozzle temperatures, an 80 °C Textured
PEI plate and 0–70% cooling. The preparation tool uses one continuous foot
modifier with six walls and 100% zigzag infill, while reviewing the three
insert-host/root regions separately. The installed Ø4.6 mm inserts require at least
2 mm of supporting outer stock. The
[native deposition review](faucet-industrial-petgf.insert-beads.json) reads
the actual host slabs and retains missing-area and pore diagnostics.

Tree supports use a 0.45 mm top gap, 0.30 mm bottom gap, 0.40 mm XY gap,
two top interface layers and 0.50 mm interface spacing. H2C's +0.18 mm
0.4 mm trim emits `G29.1 Z0.16` with Textured PEI compensation. The right
nozzle is unused on this plate.

After generating and reviewing the source STLs:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/prepare_vent_prints.py industrial
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_vent_prints.py supports-industrial
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_faucet_inserts.py industrial
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_lower_supports.py industrial
```

Review the lower-support images and record their cleanup access as described in
the [print workflow](../vent-print-readiness/README.md), then finalize:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/finalize_vent_prints.py industrial
```

The [native validation](faucet-industrial-petgf.native-validation.json) records
the source meshes, emitted settings, trim, archive/G-code checksums, estimated
time and profile-density mass. The current slice estimates 4 h 51 min 27 s
and 132.43 g at the saved density. Its complete emitted model/support/brim
envelope retains 25.17 mm usable-bed clearance; separate part toolpaths retain
37.67 mm clearance. The
[readiness record](faucet-industrial-petgf.readiness.json) binds those files
to the final geometry, support review and factory cleanup route. Complete
emitted model/support/brim beads must retain at least 20 mm of usable-bed
clearance. No print is submitted by these tools.

| Part | Support removal |
| --- | --- |
| Base | Cut sacrificial stock into small fragments; remove through the counter-end, common rear tube opening, donor bay and lever opening. Clear the insert pilots and pedestal sockets while retaining their seating faces; the flat ribbon must pass freely behind the F1-D-F2 bundle. |
| Retained sealed-cavity tip | Its saved support review uses the joint, large bottom port and display pocket. That review belongs to the exact archived geometry; the current small-hole tip needs its own native support reading. |
| Cover | Remove supports through the open underside before fitting the display; retain snap wings and lip-bearing faces. |
| Plate | Remove the three screw-counterbore bodies through their screw-head openings while retaining the seats. |

The [support audit](faucet-industrial-petgf.support-audit.json) includes
unlabelled bodies; the [contact reading](faucet-industrial-petgf.support-faces.json)
and [cavity image](../vent-print-readiness/faucet-industrial-black-z018-h2c/native-cavity-supports.png)
locate their paths. The
[lower-guide review](faucet-industrial-petgf.lower-supports.json) and its
[base sections](../vent-print-readiness/faucet-industrial-black-z018-h2c/native-lower-support-sections.png)
locate trees around the shared rear passage and pedestal sockets. Physical release and
deposited finish remain inspection items. The
[complete print set](../vent-print-readiness/README.md) provides
the matching bungs, gasket, insertion tool and
[factory assembly sequence](../asse-vent-seals/README.md).
Record physical support removal, fit and retention in the [print log](print-log.md).
