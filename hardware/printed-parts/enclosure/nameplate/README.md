# Nameplate

A [104.53 mm](PLATE_W) × [38 mm](PLATE_H) horizontal plate, flush with the rear wall of
`enclosure-back-top`. The face carries the faucet mark, `HOME / SODA / MACHINE` in equal-size
Helvetica Bold, and a unit-specific QR. The three groups have equal 5.1 mm visible gaps.
There is no printed domain, serial, dividing rule or rating footer.

[`nameplate.py`](nameplate.py) generates the two-colour part. [`wordmark.svg`](wordmark.svg)
contains the exact outlined lettering; the faucet comes from [`brand/mark.svg`](/brand/mark.svg).
The face is [2.4 mm](NAMEPLATE_T) thick, with r3 mm corners and a 0.4 mm rear-edge lead-in.
The white inlay is [0.72 mm](INK_DEPTH) deep and flush with the black face.
The STEP and 3MF preserve both colour volumes; the STL represents their combined exterior.

## QR

The unit-0001 payload is `HTTPS://HOSM.US/0001`. Uppercase scheme and host allow the complete
URL to use QR alphanumeric mode: version 1, error correction M, **21 × 21 active modules**.
Each module is 1.1 mm; the active square is 23.1 mm and its four-module quiet zone makes a
31.9 mm square. The quiet zone is part of the black face and contains no other artwork.
Diagonal-only white contacts have 0.02 mm corner joins to keep the CAD interface manifold;
the 1.1 mm module pitch is unchanged. The unit identifier is encoded in the QR. The full-domain address in written instructions is
`homesodamachine.com/0001`; neither address is lettered on this plate.

The separate [appliance marking specification](/hardware/markings/README.md) covers ratings and
refrigerant warnings. The exterior disposal warning is raised into a plain field low on the
rear enclosure.

## Retention

Two straight PET-GF tabs are integral to the plate. Each is 8 mm wide, **1.3 mm thick and
11.3 mm long**, with a 1 mm inner-root radius. A **1.8 mm outward lip** starts 8.5 mm from the
root. The hook has a 1.2 mm tall full-depth land followed by a 1.6 mm lead-in;
its total height is 2.8 mm. Pushing the plate into its pocket bends the
tabs inward; they return behind the enclosure's rigid shoulders. The 0.60 mm shank clearance
leaves 1.2 mm nominal catch engagement. The square retaining face has 0.48 mm axial clearance.

The tabs stand on the plate's horizontal centre line, [82 mm](TAB_PITCH) apart, which leaves
[11.3 mm](TAB_TO_END) from each tab to its end of the plate. One bar behind the pocket receives
both. It spans the two [3 mm](SHOULDER_W) retaining shoulders and runs the full depth from the
wall to [2 mm](SHOULDER_STOCK) inboard of the bearing faces, with [3 mm](BAR_FRAME) of bar above
and below the slots. Each tab passes a straight slot with an inward flex lane, and its lip
catches in a pocket ahead of its shoulder that opens to the bar's inboard face and its end. A
45° corbel carries the bar's print-down face back to the wall. Each catch pocket's floor is
supported by the same body that reaches the pocket's lower rim. The pocket floor retains
[3.6 mm](POCKET_FLOOR) of material outside the two slots. The bar's east end stands clear of the
PSU's AC terminal block (`nameplate-psu-clear`).

The plate is centred on the flavour chips' height, and across the field between the flavour A
pocket and the rear tangent.

The interface is defined once in
[`_nameplate_interface.py`](../enclosure/_nameplate_interface.py); `enclosure._nameplate` cuts
the production pocket and the separately generated `nameplate-receiver.step` fit coupon.
No screws or heat-set inserts are used at this joint.

The [faucet trials](/hardware/printed-parts/faucet/faucet-display-petgf.md) establish the useful
scale of PET-GF features: 1.3 mm cover stock, 3 mm lips and generous receiving clearance.
The nameplate uses this stock in straight tabs with broad bearing faces. Its CAD fit and
swept insertion are checked; force, edge finish and retention are read from a physical
plate-and-receiver print.

## Printing and assembly

Print **artwork down**, with the complete black-and-white face on the bed and both tabs
pointing up. Use black and white PET-GF, a hardened 0.4 mm nozzle, a 0.20 mm first layer,
0.24 mm subsequent layers and the faucet's PET-GF material profile. The inlay occupies the first three layers. Each colour is a
separate part of the same object, so both colours print in those layers; this is not a single
filament change above a black slab.

The square lip undersides receive accessible supports with a 0.24 mm top gap; the slicer's
small-overhang support filter is disabled to keep these contacts. Preserve
these bearing faces during removal; a rounded extrusion envelope is not a substitute for
a printed ledge. Supports on the removable plate are accessible from both sides of each tab. Keep the two square catches and their receiving shoulders
clean. The coupon prints in the enclosure orientation in the production material; its receiver
takes support at the pocket's lower rim and each catch pocket's floor.

Scan the finished plate to verify the unit number, then press it straight into the rear
pocket until both clips engage and its face seats. Confirm the plate is retained and that
the QR still scans after installation. The CAD artwork scan is not a physical print test.

## Generation

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 27
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py selftest
```

The first command emits `nameplate-027.step`; the assembly uses `nameplate-001.step`.
Units are restricted to 0001–9999 so every QR stays version 1. The self-test checks solid
validity, receiver clearance, inward seating and outward capture, full face contact on the
print bed, and QR size/quiet-zone geometry.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py`
- `/hardware/printed-parts/enclosure/nameplate/nameplate.py`

## Prepared print project

[`nameplate-001-petgf.3mf`](nameplate-001-petgf.3mf) is an editable two-colour project with
the nameplate artwork-down and the receiver coupon in the back-top print orientation.
Black PET-GF maps to Mark2's left external spool and white PET-GF to its right external
spool. Both use the printer's PET-CF label and hardened 0.4 mm nozzles. The
[material compatibility record](petgf-hotend-compatibility.json) records Polymaker's
H2C PET-GF support for both hotends. The project retains the shared PET-GF temperatures
and flow settings and uses Mark2's requested 0.04 mm bed trim.

The [native print record](mark2-print-readiness.json) identifies the exact archive accepted
by Mark2, its live spool mapping and the right hotend's first use with white PET-GF.
The [physical result](physical-acceptance.json) records Derek's successful print: clear
appearance, reliable QR scanning from 2 feet, intermittent scanning from 3 feet, and working
snaps in the receiver coupon. Both original photographs are retained with the print hashes.
The photographed QR independently decodes to `HTTPS://HOSM.US/0001`.

Derek's preference remains simpler geometry with broad, substantial flexing walls, as in the
faucet display cover. The nameplate's functional result does not remove that complexity concern.

The [native slice reading](mark2-print-readiness.json) records 1.3 mm stem toolpath envelopes
and five consecutive full-depth catch layers. The total catch section is 3.10–3.115 mm:
1.3 mm stem plus 1.8 mm lip. This is commanded extrusion geometry, not measured edge finish.
The first-layer artwork decodes to `HTTPS://HOSM.US/0001`.

The [support audit](nameplate-001-petgf.support-audit.json) records one bed-rooted support
beneath each nameplate catch. Each reaches its labelled interface after 10.32 mm of build-up;
both contacts are exposed beside their tabs. The receiver coupon has one larger support body
serving its ledge, shoulders and rim, plus two small bodies without labelled interfaces near
the pad corners. Those two bodies' contact area and build-up are unmeasured. Support count
is an observation; preserve the working faces when removing them.

The native slice estimates 1 h 23 min and 35.12 g, including the coupon, purge and supports,
using the saved profile's 1.29 g/cm³ density. Its native log notices are retained in the slice
reading. Physical catch finish, insertion force and retention are established with the
included receiver coupon.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/prepare_print.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/verify_mark2_print.py
```
