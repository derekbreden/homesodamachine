# Front-top integration repair

The source uses rear inner Y468.3, with the cold core at Y182.3..465.3.
The complete aft valve tray remains at Y172.09..181.29 with its 9.2 mm section,
blind socket floors, fitted post pattern and 1.01 mm air to the core. The manifold,
collet plate, cartridge, pump seats and moving carrier keep their positions.

[The bounded native repair reading](front-top-repair.json) passes 27 checks.
It uses the exact exported parts from the failed assembly as a frozen regression
fixture. It does **not** qualify a newly generated whole shell or revised routes.

| Interface | Current source and bounded result |
|---|---|
| Cold core / valve tray | Core shifts 4.3 mm aft with the rear boundary. Native intersection is zero; tray air is 1.01 mm. |
| Outer valve coils / front flanks | Actual near-wall coil surfaces define shallow pockets with 45-degree print-up roofs. Each coil has 1 mm air. Remaining flank stock is 7.65 mm, including 6.45 mm behind maximum exterior fluting. |
| Flank cable clips / fluid-18 | Complete clip profiles are embedded 1.2 mm, retaining their 3 mm arms, S-channel and end ramps. The frozen fluid-18 has 1.05 mm minimum air at the aft clip. The revised route needs its own completed-shell reading. |
| Fixed spring cups / outer wells | Full native cup stock is present. Passage volume outside the declared cups is clear. Actual tee, carrier and pusher paths remain separate checks. |
| Inner aft coil entry / carrier | Both full continuous native rises have zero intersection. Each includes 54 boundary-face witnesses; the forward metal ends 0.25 mm below the broad backing. The gate resolves touching bounding boxes with these native sweeps. |
| Cartridge and raised cap | Current builders with the extended rear boundary produce exactly the retained native parts: zero extra or missing volume in both directions. [Native equality](pump-rear-boundary-equivalence.json) binds their unchanged STEP/STL hashes. |

The core's front corner stops move from Y190 to Y194.3. They are integral to
front-bottom, so that piece requires regeneration despite its unchanged Y200
seam, Z160 split, collet and rail datums. The cap's V-A/B cradle X coordinate is
94.090 in the cap frame to keep their fixed world Y229.710 mounting centres.
V-K follows the core-mounted suction chain. Remaining cap, rear-shell and route
changes belong to the coordinated complete assembly build.

The [baseline manifest](fit-correction-baseline.json) authenticates a compact
[native archive](fit-correction-baseline.zip), including the failed scorecard and
the initial interference/alternative-placement readings. That archive contains
historical regression inputs and is not production print geometry. Its native
coil shapes match the completed assembly exactly; the coil entry-box failures
fill the open yoke region, and the outer well-box failures consist entirely of
the declared fixed spring cups.

Reproduce the local reading with the project CadQuery environment:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/verify_front_top_repair.py --output /tmp/hsm-front-top-repair.json
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/verify_pump_rear_boundary_equivalence.py --output /tmp/hsm-pump-rear-boundary.json
```

Both scripts read the archived native fixture and current source. They write
reports only; they do not export production geometry. The complete current Box,
shells and aggregate still need their coordinated checks. Physical spring feel,
retention and rigidity are evaluated in the full printed enclosure.
