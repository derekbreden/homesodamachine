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
| Forward tip | 0.30 ±0.03 mm axial lead; Ø6.05 ±0.03 mm at its end |
| Working sealing land | Machine Y83.515–89.515 mm; Ra ≤0.8 µm, free of tool marks, burrs and axial scratches |
| Low rear barbs | Two Ø6.90 mm peaks, with R0.10 mm back-edge blends |
| Nominal rear engagement | 12.00 mm behind the prepared BPT end |
| Tip | Machine Y90.015 mm |
| Flange | Machine Y76.25–78.75 mm, center Y77.50 mm |
| Prepared BPT end | Machine Y76.10 mm |
| Factory tie | 2.54 mm wide, centered at Y74.50 mm, head toward +Z |

These are design machining callouts. Supplier stock properties do not
establish the machined finish, the rear-barb fit or the resulting assembled
pressure capacity. The machined part is not an FFF wet component.

The 12 mm rear engagement ends at machine Y64.10 mm. The retained pump
reference and scan review cover external fit and exclude hidden tube bends
and roller clearances. No internal straight-tail record establishes that
engagement. Prepared-pump BPT fit, free rotation and pumping behavior with
the machined tail remain unqualified.

## Load path and assembly

The lower cradle carries one half of each Ø22.30 mm guard. A flange pocket
opens straight upward with 0.15 mm nominal clearance at each flange face and
on its radius. The guard's diameter includes that radial fit allowance and
retains 3.00 mm radial stock around the Ø16.30 mm pocket. Its fore and aft shoulders carry stem insertion, withdrawal
and hydraulic separation reactions directly into the cradle. The fore
shoulder starts on the retained head-well aft plane, Y72.887 mm, and has
3.213 mm axial stock to its pocket. The integrated caller supplies that
plane from `cy + pump_tray.skirt_body_open_y_bounds[1]`. The aft shoulder
has 3.365 mm to the cartridge's aft plane at Y82.265 mm. A straight Ø7.75 mm
dry passage clears the stem and its R0.40 flange root between that pocket
and the cartridge back. Its radius includes the full root radius, the
0.15 mm pocket-center float and another 0.15 mm radial air, so the broad
flat flange face supplies the first axial reaction after the 0.15 mm pocket
clearance.

The cap carries rear upper arches and straight, 5.996 mm-deep webs joining its
existing filled body. Every arch and web starts at Y76.269 mm, 0.300 mm
behind the actual reference head's Y75.969 mm aft extent, so they clear the
seated heads throughout a straight cap lift. This named case clearance has
no printed fit result. The arches have open fore faces and 0.35 mm aft
clearance to the stem flanges; the lower cradle encounters axial travel first.
The webs finish within the cap body's own X planes. The two outer webs
are 11.175 mm wide, and the two inner webs are 12.100 mm wide; each keeps
the complete 5.996 mm Y section into the cap body.
Closing the cap blocks vertical flange escape without clamping the smooth
stem. Both capture halves end flush at the cartridge back. The cap's straight lift path
is cut through the complete modified cartridge exit lane to the cradle's
crown at Z284.174 mm. The integrated feature call supplies
`cap_route_top_z=cap_crown_z(box)`; the guard webs retain their own lower
joining height.

The permanent wall starts at Y82.515 mm, 0.250 mm behind the cartridge
back, and supports the TPU directly around its funnel and sealing body.
Its closed bore locates the receiver in X/Z; the flat interior keeper
blocks its Y assembly route. The four outboard body stops set cartridge
insertion independently of the stem tip and the TPU's internal stop.

The actual outlet identification distinguishes the local molded casing
from the entire pump head's bounding box. Native scan sections identify an
approximately 4 mm exposed BPT region at world Y72.1–76.1 mm. The factory tie
occupies Y73.23–75.77 mm. Its Ø12.1 mm circular clearance continues through
the complete fore shoulder to the flange pocket at Y76.10 mm. The tie head uses the relieved
upper channel. The modeled tie-head relief ends at Y76.07 mm, ahead of the
rear arch's Y76.269 mm fore face. The delivered head's Y width has no
measurement or applicable drawing. Received tube shape, tie-head dimensions, tightening and the
machined tail remain part of the prepared-pump fit observation.

## Force screen

At 80 psi, using the external 6.35 mm seal diameter gives **17.47 N per
stem**. This conservative hydraulic projection is independent of the
smaller internal flow bore. Counting only the lower half of the flange
shoulder gives:

| Screen | Nominal result at 80 psi |
| --- | ---: |
| Aft bearing area, outside the Ø7.75 passage | 76.94 mm² |
| Aft mean bearing stress | 0.227 MPa |
| Fore bearing area backed through 3.213 mm, outside the Ø12.1 tie passage | 43.04 mm² |
| Fore mean bearing stress | 0.406 MPa |
| Mean flange-root axial shear | 0.350 MPa |
| Radial-strip flange-root bending, load assigned to the lower semicircle | 5.05 MPa |

The bending screen treats the flange as radial strips fixed at the stem,
loaded over its outer bearing annulus. It does not resolve the root fillet,
circumferential plate action, creep, print anisotropy or individual contact
peaks. The table uses centered nominal geometry; the native fit review
separately bounds the full 0.15 mm pocket float and first flat-face contact.
At 10 psi the nominal aft bearing and strip-bending stresses are
0.0284 and 0.631 MPa. These calculations explain the load path and dimensions;
they are not a lifetime, seal or system-pressure rating.

## Factory fixture and review

The [setting fixture](pump-stem-setting-fixture.step) supports the plain rear
shank and flange of the bare machined stem, before fitting the BPT tubing,
and provides a flat annular tip stop. Its
[STL](pump-stem-setting-fixture.stl) is a bench tool, not a shipped wet part.
The fork spans the full 24 mm base width and has 3 mm fore and aft cheeks.
Its fore cheek supports the plain shank beyond the last barb; the aft cheek's
Ø8.65 mm opening clears the working sealing surface. The Ø16.30 mm flange
pocket is at Y76.15–78.85 mm and the tip stop at Y90.015 mm. Measure
the actual tip-to-flange datum before using the fixture to prepare pump
units. The finished stem itself establishes that distance by machining.

The [local native review](stem-native-review.json) checks solid validity, flange-to-guard clearance,
vertical installation of the prepared stems and cap, and the intended
division of load paths: a 0.20 mm stem translation along either Y direction
encounters the lower cradle while remaining clear of the cap; a 0.30 mm
vertical lift encounters the cap. Guard and web material clears both
retained native pump-reference heads, bosses and motors in their assembly pose and
clears the occupied TPU receiver envelopes. The upper arches and webs remain
behind the complete reference heads and join the existing cap one millimetre above its
body's lower plane. An exported-cradle native review with the complete
cap-lane cutter checks cap lifts through 110 mm and a continuous conservative
sweep of the upper guards. The recorded sections keep 14.00 mm
uninterrupted outboard stock beside the cap lanes. BPT/tie, neighboring plumbing, printed capacity and
lifetime remain outside those geometric results.

Recreate the machining part and bench fixture explicitly:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-dock/stub_grip.py
```

The producer reads the current declared Box for the prepared tip and capture
datums. Materialize that declaration before recreating these factory files.
