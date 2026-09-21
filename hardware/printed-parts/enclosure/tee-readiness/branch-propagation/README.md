# Measured tee branch integration

The nominal branch face is 22.35 mm from the run axis when extended and 20.85 mm
when pressed. Those stations use Derek's 30.5 / 29.0 mm outside-width readings and
the nominal 8.15 mm back-collar radius. Branch travel is 1.50 mm; run-sleeve travel
is independently 1.65 mm. The terminal ring's exact OD/seam and physical release
bearing remain unqualified.

The production source places the inner/outer tee axes at X ±22.35 / ±82.10 mm and
the Kamoer centers at ±52.225 mm. The named 5.476 mm pump-to-release span preserves
the release plane at Y82.690 mm and the cap/cartridge aft face at Y79.269 mm. The
complete 3 mm skirt band and 0.246 mm plate air remain present. Connected carrier
travel is 2.00 mm; the mechanical aft limit is 4.50 mm.

The Ø8.5 mm circular release opening retains a complete flat annulus. A Ø6.35 mm
tube has 1.075 mm radial air. [The source check](release-bore-check.json) reads an
annulus from R4.26 to R5.00 mm; that geometric probe is not a qualification of the
physical terminal ring's minimum size. Front-top prints in +Z, so this short
horizontal opening may require crown support. Its two mouths remain accessible
before hardware installation; actual support bodies require a current slice.

The carrier retains R8.75 mm troughs and 5.504166 mm of upper backing. Its outside
tie slots stand at X ±90.00 mm, behind the collar tangent and inboard of the complete
handhold backing. Tie locks face the open inter-tee gaps. The source and native checks
retain the full bar root, finger backing, collar running air and declared lock envelopes.
These lap-joint halves are a dimensional baseline; the final simple carrier remains a
separate design and qualification task.

The fixed spring floors are at Y90.040 mm and the moving floors at Y109.390 mm
plus carrier travel, on X ±97.535 and Z211.209 mm. Bearing lengths are 19.35 mm at
release, 21.35 mm connected and 23.85 mm at the aft limit. This geometry does not
provide qualified positive spring capture or assembled stiffness.

Two cold-core lid cradles follow the valve placement: cap-frame A=(89.790,24.770)
and B=(89.790,-22.350) mm. The fluid-14 anchor stands at (65.000,43.500) mm on the
same tube axis and height, retaining 1.365 mm clearance to the A plinth. The
fluid-2 approach retains R14 mm bends and 1.413 mm native pump clearance.

[The canonical Box reading](box-generation.json) records one failed enclosure
bound: the water split enters the back-top flank by 1.10 mm. A separate native
reading finds 4.182 mm³ interference between fluid-14 and V-A. Both remain open
complete-enclosure issues. The three cartridge-local Box bounds pass; the
cartridge/cap bench-fit scope does not qualify either route or the selected
G Ganen integration.

[The coupled native-region check](../tee-integration.json) identifies exact sources,
native inputs, tube axes and working-state readings. The [front-top fixture](front-top/)
holds its own Box digest and source closure when generation has completed. The
[archived baseline](../current-front-top/) is not the measured-branch fixture; its
interrupted full motion operation supplies no pass/fail result.

No report in this directory releases the complete enclosure or establishes physical
fit, snap retention, material stiffness or support-removal effort.
