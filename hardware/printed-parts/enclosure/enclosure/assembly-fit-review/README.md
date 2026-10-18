# Prototype assembly clearances

The C14 station has a 28.3 × 19.3 mm cord bore and 0.65 mm per-edge
flange-pocket clearance in X/Z. The 5 mm pocket depth, seating plane and
40 mm screw pitch are fixed. Its nominal pocket spans are 51.07 × 23.47 mm;
the print-down face also has its separate supported-surface allowance.
The cord bore is centered at X=66.9 mm with R1.5 corners. The reported
female-side fit is retained; the external plug-access bore has an independent
3 mm total X allowance for the mating cord body. Physical fit of this wider
access bore remains unmeasured.

The [cord-access measurements](cord-access-measurements.json) read the exported
print mesh at 28.30 mm across, retain the flange-pocket section and measure
3.85 mm nominal stock between the widened bore and the nearest heat-set bore.
The local STEP comparison finds no material change outside the cord opening.

The Mean Well's AC wire entry faces +Y and its DC entry faces −Y. Both
screwdriver axes face the room along −X. The module's aft mounting row is
5 mm forward of the rear corner's mounting limit. Relay #2 stands 4 mm
forward of the module envelope, and the main board 3 mm forward of that
relay. Preform and terminate the fixed solid-wire leads before fastening
the module. The block model is representative; the complete installed
wire bend remains a physical assembly observation.

Two 5 mm full-height webs join the close forward conduit columns while
retaining their 2 mm walls and tube stations.
Passive cold-core tube crossings and cap conduits are Ø7.5 mm for tubing
measured at approximately Ø6.5 mm. Mask the gaps during the foam pour as
specified in [cold-core assembly](../../../../assembly/cold-core.md).
The organizer, faucet, copper-plug seats and PRV tube socket retain their
separately specified fits. The copper crossing datums remain independent
of the passive fluid-passage diameter.

[Native clearance measurements](native-clearance-measurements.json) record
12 clear local wire/tool probes, zero C14-to-shell overlap, one valid
back-top solid and the retained main-board mounting stations. The wire
probes use the selected 2 mm OD stock, a 1 mm straight and R3 fixed bend;
these are nominal access probes, not a qualified installed bend radius.
Run `measure_native.py` manually with the CAD Python to reproduce them.

[Printed C14 measurements](printed-c14-measurements.json) compare the
October 10 Mark1 project's main mesh and the current print STL at the
flange-pocket and cord-bore sections. The fixed exterior planes register
the print object into the machine frame; the measured pocket is not a
registration datum. This is a manual review, invoked by
`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/assembly-fit-review/measure_print.py`.
It is not part of any build or commit check.

[Assembly feedback](assembly-feedback.json) binds the observations to the
identified articles. The latest logged foam-shell success is the May 31
record at source `7cd49702`, whose small passages are Ø6.5 mm. Its saved
project and current design are distinct artifacts; an on-disk modification
time does not establish a later physical print. The October 11 back-top
preparation records `prepared_not_started`.

[Core passage measurements](core-passage-measurements.json) read Ø7.5 mm
cylinder faces from the exported top cap, top lid, both reservoir caps and
foam shell and measure both connecting webs at 5 mm. `measure_core.py` is a
manual B-rep measurement. The [appliance assembly review](../../../../manifold-layout/enclosure-assembly.scorecard.json)
passes its active checks, including pack closure and conduit wall/pair stock.

The [post-publication mesh review](post-publication-review.json) records open
sharp passage-rim findings and the unchanged seam, port and cap-perimeter
regions. Both the preceding and current shell STL report acute curved-passage
entry edges. The Ø7.5 mm clearance review does not qualify their printed
finish. Local chamfer/round candidates did not produce valid solids and are
excluded from the exports. The final cap review reports no short-face
slivers at the 5 mm webs; its ranked perimeter findings remain open. The
listed back-top support faces retain their functional openings and stated
support exits. Live STEP, viewer mesh and STL downloads match their pointer
hashes for all 19 reviewed files.

[Wiring construction](../../../../wiring/ac-wiring-schedule.md#conductor-construction)
names the fixed solid-wire runs, stranded exceptions and Prime stock.
