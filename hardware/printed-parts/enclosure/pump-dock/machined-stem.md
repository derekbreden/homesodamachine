# Prepared pump stems

Each replacement pump is supplied with two one-piece machined PP stems
already fitted to its PharMed BPT tube. The customer lowers the prepared
pumps into the existing cartridge and closes its two-screw cap. The fixed
TPU receivers and their interior keepers remain in the appliance.

The [machining STEP](pump-stem-machining.step) contains the complete part,
including the rear hose tail. Its flange center is local Y0. The
[dimension record](pump-stem-machining.json) gives local machining and machine
assembly datums. The installed assembly exposes only the portion beyond the
BPT end; it does not draw an assumed rigid stem through the purchased head.

## Machined component

Use Röchling **Polystone P homopolymer natural extruded PP-H**, PIM-ID 590980,
from traceable stock large enough for the 16 mm flange. A 20 mm rod supplies
machining allowance. The [manufacturer product page](https://www.roechling.com/industrial/materials/thermoplastics/industrial-plastics/pp-h/polystone-p-homopolymer-natural-725241)
links the material's technical data and FDA declaration. Its declaration
identifies 21 CFR 177.1520 on the resin manufacturer's data and assigns
application suitability and finished-part migration/extraction checks to
the fabricator. The stock declaration is not a qualification of the finished
pump joint.

| Feature | Manufacturing definition |
| --- | --- |
| Smooth sealing OD | 6.35 ±0.03 mm; maximum ovality 0.03 mm |
| Through bore | 4.30 mm, continuous |
| Flange | Ø16.00 × 2.50 mm |
| Flange root | R0.40 mm, both sides |
| Forward tip | 0.30 mm long lead; Ø6.05 at its end |
| Working sealing land | Machine Y80.515–86.515 mm; Ra ≤0.8 µm, free of tool marks, burrs and axial scratches |
| Low rear barbs | Two Ø6.90 mm peaks, with R0.10 mm back-edge blends |
| Nominal rear engagement | 12.00 mm behind the prepared BPT end |
| Tip | Machine Y87.015 mm |
| Flange | Machine Y76.25–78.75 mm, center Y77.50 mm |
| Prepared BPT end | Machine Y76.10 mm |
| Factory tie | 2.54 mm wide, centered at Y74.50 mm, head toward +Z |

These are design machining callouts. Supplier stock properties do not
establish the machined finish, the rear-barb fit or the resulting assembled
pressure capacity. The machined part is not an FFF wet component.

## Load path and assembly

The lower cradle carries one half of each Ø22 mm guard. A flange pocket
opens straight upward with 0.15 mm nominal clearance at each flange face and
on its radius. Its fore and aft shoulders carry stem insertion, withdrawal
and hydraulic separation reactions directly into the cradle. The fore
shoulder has 3.00 mm axial stock; the aft shoulder has 3.35 mm to the guard's
end at Y82.25 mm.

The cap carries the guard's upper halves and vertical webs joining its
existing filled body. The cap's flange pockets have 0.35 mm clearance at
each face, so the lower cradle encounters axial travel first. Closing the
cap blocks vertical flange escape without clamping the smooth stem or using
an unsupported thin blade for axial retention. The cap's straight lift path
is cut through the complete modified cartridge exit lane to the cradle's
crown at Z284.174 mm. The integrated feature call supplies
`cap_route_top_z=cap_crown_z(box)`; the guard webs retain their own lower
joining height.

Each moving guard enters a Ø22.5 mm counterbore in the fixed wall, ending
at Y82.50 mm. Its Ø14.3 entrance clears the flexible TPU lip; its Ø12.0
section supports the receiver body through Y82.25 mm. The remaining fixed
wall contains the receiver in X/Z. The cartridge's body stops retain their
existing positions, independent of the machined stem tip and the TPU's
annular stop.

The actual outlet identification distinguishes the local molded casing
from the entire pump head's bounding box. Native scan sections identify an
approximately 4 mm exposed BPT region at world Y72.1–76.1 mm. The factory tie
occupies Y73.23–75.77 mm. Its 12.1 mm circular clearance extends through
Y75.87 mm; the remaining passage is Ø10.1 mm. The tie head uses the relieved
upper channel. Received tube shape, tie-head dimensions, tightening and the
machined tail remain part of the prepared-pump fit observation.

## Force screen

At 80 psi, using the external 6.35 mm seal diameter gives **17.47 N per
stem**. This conservative hydraulic projection is independent of the
smaller internal flow bore. Counting only the lower half of the flange
shoulder gives:

| Screen | Nominal result at 80 psi |
| --- | ---: |
| Aft bearing area, outside the Ø14.3 opening | 20.23 mm² |
| Aft mean bearing stress | 0.864 MPa |
| Fore bearing area backed through the complete 3 mm, outside the Ø12.1 tie passage | 43.04 mm² |
| Fore mean bearing stress | 0.406 MPa |
| Mean flange-root axial shear | 0.350 MPa |
| Radial-strip flange-root bending, load assigned to the lower semicircle | 7.41 MPa |

The bending screen treats the flange as radial strips fixed at the stem,
loaded over its outer bearing annulus. It does not resolve the root fillet,
circumferential plate action, creep, print anisotropy or individual contact
peaks. At 10 psi the nominal aft bearing and strip-bending stresses are
0.108 and 0.926 MPa. These calculations explain the load path and dimensions;
they are not a lifetime, seal or system-pressure rating.

## Factory fixture and review

The [setting fixture](pump-stem-setting-fixture.step) supports the tail and
flange and provides a flat annular tip stop. Its
[STL](pump-stem-setting-fixture.stl) is a bench tool, not a shipped wet part.
No fixture surface touches the working seal land. Measure its actual
tip-to-flange datum before using it to prepare pump units. The finished stem
itself establishes that distance by machining.

The [local native review](stem-native-review.json) checks solid validity, flange-to-guard clearance,
vertical installation of the prepared stems and cap, and the intended
division of load paths: a 0.20 mm stem translation along either Y direction
encounters the lower cradle while remaining clear of the cap; a 0.30 mm
vertical lift encounters the cap. Added guard and web material clears both
purchased pump heads, bosses and motors in their actual assembly pose and
clears the occupied TPU receiver envelopes. The upper webs retreat behind
the broad molded skirts and join the existing cap one millimetre above its
body's lower plane. An exported-cradle native review with the complete
cap-lane cutter checks cap lifts through 110 mm and a continuous conservative
sweep of the new upper guards. It retains all bracket-and-lower stock, the
central screw-pillar envelope and 14.15 mm uninterrupted outboard stock at
the recorded sections. BPT/tie, neighboring plumbing, printed capacity and
lifetime remain outside those geometric results.

Recreate the machining part and bench fixture explicitly:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/stub_grip.py
```
