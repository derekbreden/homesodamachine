# Cartridge and cap together — Mark2

The [native source](pump-cartridge-cap-pause.3mf) prints the current lower
cartridge cradle upright and its pump cap crown-down on one plate, in black
PET-GF on Mark2's fixed left standard-flow 0.4 mm nozzle. Requested trim is
+0.04 mm; emitted Textured PEI trim is +0.02 mm. Saved process, filament,
tree supports and the cartridge's grip layer bands remain bound to the source.

Native estimate is **15 h 10 min 47 sec**, excluding the insertion pause.
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

The [launch record](mark2-launch.json) binds the submitted trial to the
accepted printer job. The [physical result](physical-result.json) records a
sealed-in magnet, reported rattle and uneven initial roof deposition.
The [recorded launcher](https://github.com/derekbreden/homesodamachine/blob/7cf7b55608deefa5f3cae6bb20f83bce14ff706f/hardware/printed-parts/enclosure/enclosure/magnet-retention/v4/timed_launch.py) defines the preparation,
peer-printer observation and single-submission logic for that artifact.
Further physical fit trials are recorded beside the [fit coupons](../fit-coupons/README.md).
