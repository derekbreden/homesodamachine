# Current measured-branch front-top fixture

This is the native front-top from the measured tee branch dimensions and the
SeaFlo-sized Box `b48ba9046c15391e5e9be3c64eda68ae89f41e4fc0b6b62a2b12dfb05c248804`.
It is a separate qualification fixture. The production shell files are not its
outputs, and the selected G Ganen pump is not integrated into this Box.

[The fixture record](fixture.json) freezes 35 loaded Python sources and the Box.
The STEP is one valid solid, with a relative native round-trip volume difference
of 3.85e-9 and maximum bound difference of 0.0000006 mm. The smooth STL is one
closed, consistently oriented volume with zero non-manifold edges. Its ordinary
enclosure tessellation and float32/Manifold reconciliation remove zero-area
facets without changing the bounds or volume. The fixture STL has no production
show flutes and is not a released print file.

The STEP SHA256 is
`0fbd43ae69417c0e6072827216ea8f530b5256491a54c39aeebbf46bc8ba24f6`.

| Native reading | Result |
| --- | --- |
| Full backing above all four tee troughs | 5.504166 mm retained; zero missing probe stock |
| Spring seat, guide, service land and roof alignment/stock | 26 readings pass |
| Positive X-rotation restraint at the three working stations | 12 contact probes pass |
| Full release-face annuli and straight empty-bay extraction lanes | 8 readings pass |
| Both carrier halves and eight tie-head envelopes at release, connected and aft limit | 30 readings pass |

[The backing audit](upper-backing-check.json) uses the existing production
verifier with only report destinations redirected here. Production carrier
reports are unchanged. Connected-state fixed-center first contact is about
2.10–2.13 degrees; endpoint readings couple to the travel stops. These are rigid
geometric contact readings, not free-body backlash, material stiffness or
measured deflection. No spring guide or tee contact supplies the guide restraint.

The body-bending comparison in [the audit](readiness-audit.json) excludes the
central joint, contact compliance, torsion, shear and printed material structure.
Its body-only spring-return gain is 1.57 at equal material modulus, with the
specified load pattern. That result does not establish greater assembled
rigidity or qualify the replacement carrier design.

[The interface audit](native-interface-check.json) reads the complete flat
release annulus from R4.26 to R5.00 mm and a straight Ø8.48 mm fore extraction
corridor through each Ø8.5 mm opening. The plate neck is 3.175 mm long and prints
with +Z upward. Supports can be approached through the empty cartridge bay;
the actual connected support bodies, their removal and the physical terminal
ring's bearing remain unqualified. Tie-head envelopes clear the actual wall;
this does not qualify threading or tightening every installed tie.

Complete carrier insertion is not qualified. The separate simple-carrier study
finds interference between an outer tee and the unchanged handhold-bar corner
during the inboard entry motion. Clear discrete working stations do not resolve
that installation conflict. Spring capture, the final centre connection,
physical stiffness, complete routes and a production support review remain
separate requirements. The canonical Box also retains the water-split flank
conflict recorded in [its generation evidence](../box-generation.json).

Reproduce against the exact named Box:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/branch-propagation/front-top/build_fixture.py --box-sha256 b48ba9046c15391e5e9be3c64eda68ae89f41e4fc0b6b62a2b12dfb05c248804
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/branch-propagation/front-top/check_upper_backing.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/branch-propagation/front-top/check_interfaces.py
```
