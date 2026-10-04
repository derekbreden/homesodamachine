# Cartridge and cap together — Mark2

The [native source](pump-cartridge-cap-pause.3mf) prints the current lower
cartridge cradle upright and its pump cap crown-down on one plate, in black
PET-GF on Mark2's fixed left standard-flow 0.4 mm nozzle. Requested trim is
+0.04 mm; emitted Textured PEI trim is +0.02 mm. Saved process, filament,
tree supports and the cartridge's grip layer bands remain bound to the source.

Native estimate is **15 h 10 min 47 sec**, excluding the operator pause.
The one `M400 U1` pause occurs before layer **344**, cartridge print Z
**31.16 mm**, about **6 h 35 min after starting**. The completed open rim
is **30.92 mm**; first closing beads clear the conservative maximum RC62 by
**0.316 mm**. Insert one labeled, attracting RC62 upright in the lower cradle,
fully below both rims with the tube passages clear. The cap needs no separate
retention magnet. Resume manually after checking insertion and toolhead clearance.

[Preparation](preparation.json) binds both current STEP/STL sources, the two
production orientations, local 100% host/root modifiers, project, native
archive and G-code. The [native check](native-check.json) verifies exact
embedded meshes, modifiers, both initial model layers, cartridge show rounds,
pocket support exclusion and short roof bridges. All 54,070 adjacent infill-row
intervals through the clamp roots and cap pogo hosts have nominal dense deposition
without uncovered material witnesses. General infill remains 15%.

Both objects are emitted inside the shared bed. Their complete toolpaths have
a **30.03 mm minimum bed border** and **28.19 mm separation**. The
[support topology](support-topology.json) retains two cartridge trees and three
cap trees, including every short body. The [removal review](support-lanes.json)
names a lane for every interface before pumps, screws, inserts and connectors
are installed. Physical cleanup effort, fit, magnet exposure, retained force and
joint strength remain unmeasured.

This job is **scheduled and not submitted**. The [launch plan](mark2-launch-plan.json)
targets the October 4, 2026 magnet pause at **12:15 pm local Central time**
(America/Chicago, CDT UTC−05:00), with Mark2 acceptance around **5:40 am**.
The [preflight](mark2-preflight.json) verifies both printers, current source hashes,
the Mark2 Send dialog, external left PET-CF mapping and standing print options.
The operator reports PET-GF loaded in the fixed left 0.4 mm hotend and the
Textured PEI bed clear after task 1307189764.

The [timed launcher](timed_launch.py) opens preparation at 5:30 am, observes
H2C for at least 180 seconds without a new start or resume, then checks both
printers again before its single Send. It records the attempt before pressing
Send and imports a separate copy of the frozen archive. If the native pause
forecast cannot meet **12:50 pm**, it abandons the pending start. Its latest
Send is **6:12:12 am**, allowing three minutes to reach the latest acceptable
6:15:12 am start. Any recorded or ambiguous Send blocks another submission.
Actual transfer, heating and calibration can shift the native timing estimate.

[Queue](../queue.json) authorizes this timed Mark2 trial and retains the separately
prepared H2C front-top without launch authorization. Insert the ring when the
printer pauses, then resume only on a separate request. Both printers must be
read before any separately authorized start or resume, with at least 180 seconds
after the other printer accepts a start or resume.
