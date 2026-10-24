# V-A feed and west-packed PCB

V-A supplies clean water to **Y-A port1**, the flavor manifold's shared-source
tee. That junction connects the water and funnel gates to the two channel
selects. Its retained production mouth is `(22.35,166.24,270.675)` mm, facing
upward. The arriving tube turns downward into that mouth.

The V-A outlet stem elbow points east. One continuous 1/4-inch tube sweeps
around the pump's fore side with a 79.704 mm horizontal centerline radius,
then rises toward Y-A through a short inclined run and two R14 turns. No
additional fitting is included. The source elbow's 16.891 mm insertion and
the JG tee's nominal 15.7 mm insertion are included in the [route](route.json).

The PCB is flat at underside Z257, with its long dimension across X. Its
footprint is X−93..−2.184 and Y182..254.800 mm. J10 faces east. The local mating
connectors and lead envelopes remain in the manual clearance query; harness
drawings are omitted from the view. The selected mesh query finds no
unrelated intersections. The tube clears the pump by 12.02 mm, the board by
10.12 mm and the funnel frame by 12.05 mm. The carried connector/lead envelope
stays 5.32 mm inside the ideal west wall.

Only Y-A is added as destination context. Its mesh is the existing frozen
Y-B tee mirrored about X0, with reversed winding, using the manifold's
symmetry. The mouth datum comes from `manifold_layout.port('Y-A','front')`
carried into the enclosure frame. `fluid-topology.md` segment3 defines the
V-A-O → Y-A1 connection. V-B and reservoir routes remain deferred. The
selected water group, valve seats, relays, rear fittings and gas path retain
their wall-supported poses.

## Water regulator candidate

The [EcoReg239KS1245 reference](../../../reference/ecoreg-regulator/README.md)
contains a 52 × Ø34 mm inline water-regulator body with two nominal JG
adapters, giving an estimated 89 mm tube-mouth span. It has a fixed 45 psi
preset. EPS listed six at $48, usually shipping within 24 hours, checked
2026-10-23. Manufacturer instructions cover drinking water and permit any
mounting orientation; the water inlet maximum is 145 psi.

The available straight distance from the selected tee to the V-A elbow is
74.5 mm. The EcoReg candidate therefore requires an arrangement change; it
does not replace the selected Yetaha in this study. `comparison()` places
both complete envelopes in free space. Source drawings, the nominal thread
take-up and current stock evidence are beside the reference. The candidate
has no purchase or production-selection status.

The production pack and remaining equipment retention are outside this
arrangement. Regenerate the study and its manual fit query with:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/east-feed/study.py --check
```
