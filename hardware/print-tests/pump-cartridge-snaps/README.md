# Cartridge snaps and pointed-tip comparison

The production Kamoer pump retainer prints on its Y-minus end. Its 2.0 mm leaves
have 22.25 mm from root to catch, a 1.5 mm inside root blend, 2.6 mm seated catch
overlap and 0.4 mm static catch clearance. Both full-length wings, fitted pump
wells and skirt-bearing lands are included. Front-top's matching receivers keep
6.4 mm nominal pocket backing, 3 mm nominally behind each centered 5 mm tool opening and their
production seam-plane print orientation.

[Normal integration](normal-integration.json) identifies the active published
normal-build artifacts. The snap source definitions match exactly; sampled
surface deviation in the spring bands is below 0.004 mm, and seated overlap
is zero. The prepared trial surfaces and slices retain their recorded hashes.

[Assembly integration](assembly-integration.json) binds the scoped full appliance and
enclosure STEP, fine meshes and viewer payloads. The installed retainer uses its
seated pose; the standalone print uses its relaxed pose. Unrelated native and
viewer bodies retain their arrays. [Installation scenes](installation-scenes.json)
identify the front-top and pump-mount GLBs made by the production scene writer.
The physical scene also carries the earlier ASSE, PISCO and meter revisions; its
cached scalar checks retain their stale source stamps and are not new checks.

[Geometry](geometry.json) binds the test pieces. The cartridge receiver sample
is cropped from the actual production front-top STL, with both complete receivers,
their end shoulders, release openings and surrounding front/side/tee-wall stock.
Its top ends one nominal wall above the pump skirt bearing. The upper motor and
display rooms are outside this sample. The retainer is the complete production
STL, so the span, root constraints and two-pump skirt capture are represented.

The compact cartridge comparison adds a 3 mm insertion ramp to the lower hook,
keeping its 1.6 mm nose, root and catch datums. Both full-Y wing samples use
the same production receiver; the candidate has zero seated overlap.

The PISCO comparison uses the production station and cap functions with a
3 mm ramp rise and pointed tip. The extra 2 mm lead length and matching pocket
ceiling are experimental. Both caps retain the same measured hardware bearings,
2 mm leaves, 22.25 mm length, 1.5 mm root blend, 2.6 mm catch, 1.6 mm nose and
centered pry entry. The complete candidate parent is generated before cropping
its receiver, including the snug rear bore and both axial shoulders. The regular
cap and pointed cap use the same receiver for the comparison. The published
rear equipment retains the regular tips while their fitted bearings are tested.

## Prepared plates

[Print jobs](print-jobs.json) identifies each native project and sliced archive,
its input and G-code hashes, printer-specific trim, emitted bead margin and review.
No plate has been submitted. Material is black PET-GF15 on the left hardened
0.4 mm Standard-flow nozzle, with a 0.20 mm first layer, 0.24 mm ordinary layers,
three Classic walls, local solid snap hosts and solid small caps. Tree(auto)/Default
and localized cooling retain the shared recipe.

| Plate | Printer | Parts and purpose |
| --- | --- | --- |
| Pointed tips and ASSE · 2 h 53 min, 91.02 g | Mark1 | One complete PISCO receiver, regular and pointed caps, and the backed ASSE replacement cap for the current trial receiver. |
| Cartridge ramp comparison · 2 h 15 min, 73.93 g | Mark2 | One complete full-Y wing with its receiver and a second wing carrying a 3 mm insertion ramp. This screens bending and release on the actual spring span. |
| Full cartridge fit · 496.29 g | Mark2 | Complete pump retainer and cropped production front-top receiver, including both full-length wings and both pump skirt bearings. This 17 h 24 min fixture is retained for the complete two-pump check. |

Start with the pointed-tip comparison and the compact cartridge ramp comparison
when the current trials have finished and their beds are clear. The compact
cartridge samples retain the complete Y span, both axial shoulders, complete
Z hook/root interface and production outer wall. A 3 mm strip of the carrier
remains inboard of the spring corridor; this sample does not reproduce the
whole carrier’s stiffness or capture two pumps. Use the full fixture for those
checks. The cartridge’s trailing lower hook uses a longer ramp into the same
leaf; it does not use the rear cap’s leading pointed free end.

Finish and inspect the running ASSE/PISCO and meter trials first. The cartridge
interface is independent of those bearing results. Use the PISCO comparison once
its fitted hardware bearings are accepted; a further bearing revision requires
fresh caps and a matched receiver. The backed ASSE cap addresses its separately
recorded window backing and mates with the running trial's receiver.

## Bench checks

1. Remove supports before seating hardware. Use a tiny flathead that fits each
   cavity; retain accessible automatic supports under functional ceilings. Verify
   removal access on the cartridge sample itself. The rear-cavity result does not
   qualify a different support topology.
2. Seat both Kamoer pumps in the retainer and raise them motor-first into the
   sample. Inspect both hooks along their complete Y span. Check lateral and
   vertical play and the fitted skirt capture. The missing upper motor room and
   plumbing do not qualify the complete installation path.
3. Watch the whole spring wall during insertion. Record whether bending spreads
   through the wall or concentrates at the corner, and whether either root marks
   or cracks. Record insertion effort and both hooks' seating.
4. Support the cartridge, release each hook through its centered screwdriver
   opening and lower it. Verify that a center push releases the complete broad
   wing, including its ends. Record the blade used and any damage or difficulty.
5. Fit the same PISCO hardware and regular cap in the comparison receiver, then
   repeat with the pointed cap. Compare insertion effort, distributed bending,
   full catch engagement, centered tool removal and hardware play in X, Y and Z.
   Confirm the longer point does not bottom against the pocket roof.
6. Repeat seating and release and record the count, whitening, cracks, permanent
   set and change in force. A short bench sequence establishes only those uses;
   vibration, load capacity, creep and lifetime still need their own evidence.

The above-core G-Ganen pump's accepted fit is a separate interface. Its fitted
motor rails and stops are preserved. The pointed-tip comparison establishes a
candidate ramp, not acceptance of that ramp in every pump lid or enclosure.
