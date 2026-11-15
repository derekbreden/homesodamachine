# Small PET-GF parts on Mark2

The [`small-petgf`](../../../trial-preparation/pieces.json) piece puts the machine's small black
PET-GF parts that have no plate of their own on one Mark2 plate:

| Part | Material | Count |
| --- | --- | ---: |
| ASSE 1022 snap cap | HSM-0448 | 1 |
| CO₂ secondary-regulator snap cap | HSM-0449 | 1 |
| Flavor-water regulator snap cap | HSM-0451 | 1 |
| Carbonated-water flow-sensor snap cap | HSM-0450 | 1 |
| G Ganen pump snap cap | HSM-0455 | 1 |
| Machine display cover | HSM-0076 | 1 |
| Lower pump retainer | HSM-0082 | 2 |
| Reservoir B fill bend holder | HSM-0454 | 1 |
| Soda inlet bend holder | HSM-0358 | 1 |
| Flavor-fill funnel drain-elbow cradle | HSM-0073 | 1 |
| Faucet umbilical organizer | HSM-0098 | 1 |

Each part keeps the pose and recipe of the piece that prints it alone, carried as its object
settings, and the regulator cap keeps its nonplanar contact. The umbilical organizer comes from
its part mesh with the shared PET-GF recipe its own record names. Every part lays its walls at
their own speed through the slicer's two shallowest overhang points, as the Sculpted faucet plate
did; the steeper points, bridges and their fan stay as the filament has them.

The ASSE cap prints alone at its top, and the pump cap shares its upper layers with the ASSE cap
only. The single-regulator-cap recipe's smooth timelapse and tower give every layer time away from
the parts, and the slicer takes each snapshot at its safe position. [layer-time.json](layer-time.json)
gives each part's smallest time away beside the 7 November batch's and the single cap's.

The plate prints at Mark2's standing PET-GF trim on textured PEI, every bead well inside the
unseasoned outer plate, with the tower behind the group at the left ([plate](plate.png),
[from above](plate-top.png)). [readings.json](readings.json) holds what the readers found before
the send: each part lays the same beads as it does alone, the bridge-foundation cooling stage is
in the file, and the printer commands are the slicer's own. The only travels under earlier
plastic are the regulator cap's, from its own support to its own support inside its contact band,
and the standing rear-caps plate reads the same. That contact recipe prints for the first time on
this plate.

[launch.json](launch.json) records the accepted Mark2 job, [startup-spacing.json](startup-spacing.json)
Mark1's last start before it, and [first-layer-status.json](first-layer-status.json) the printer's
own report once the first layer was under way. The [sent archive](2026-11-15-small-petgf-mark2-39847f01.gcode.3mf) and
the [editable project](2026-11-15-small-petgf-mark2-39847f01.3mf) are here, with the preparer's
[preparation](preparation.json) and [review](review.json). [Reproduce the plate](REPRODUCE.md).
