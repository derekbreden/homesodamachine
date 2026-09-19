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

Two straight PET-GF tabs are integral to the plate. Each is 8 mm wide, 0.8 mm thick and 9 mm
long, with a 0.6 mm inner-root radius. A 0.6 mm outward lip starts 7.5 mm from the root and
runs into a tapered insertion nose. Pushing the plate straight into its pocket bends the tabs
inward; they return behind the enclosure's rigid shoulders. The 0.15 mm side clearance leaves
0.45 mm nominal catch engagement. The square retaining face has 0.48 mm axial clearance.

The shoulders have straight slots, an inward flex lane, and open rear relief. Their supported
ends receive the enclosure's 0.25 mm print-direction allowance. The pocket floor is continuous
except at the two slots and retains 3.6 mm of material. The water pump's full-width rear bearing
ledge remains at its assembly datum. The plate centre is 9.5 mm above the cold-core cap.

The interface is defined once in
[`_nameplate_interface.py`](../enclosure/_nameplate_interface.py); `enclosure._nameplate` cuts
the production pocket and the separately generated `nameplate-receiver.step` fit coupon.
No screws or heat-set inserts are used at this joint.

The [faucet trials](/hardware/printed-parts/faucet/faucet-display-petgf.md) establish PET-GF
flexure and the value of generous receiving clearance on that cover. This nameplate's tab
length, lip and lower insertion travel are specific to this much lighter part. Its fit has
been checked in CAD; insertion force and retention await a physical plate-and-receiver print.

## Printing and assembly

Print **artwork down**, with the complete black-and-white face on the bed and both tabs
pointing up. Use black and white PET-GF, a hardened 0.4 mm nozzle, a 0.20 mm first layer,
0.24 mm subsequent layers and the faucet's PET-GF material profile. The inlay occupies the first three layers. Each colour is a
separate part of the same object, so both colours print in those layers; this is not a single
filament change above a black slab.

The 0.6 mm lips have exposed undersides. Any small support under a lip is rooted on the
plate's back and fully accessible from either side of its tab; there are no enclosed support
channels on the removable plate. Keep the two square catches, their receiving shoulders and
the pocket's lower rim clean. The coupon can be printed in the enclosure orientation to check
those supported receiver faces with the production material.

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
Both PET-GF colours map to the profile-compatible extruder. The local Bambu Studio slice
estimates 1 h 20 min and 33.89 g for the plate, coupon, purge and supports using its saved
1.29 g/cm³ density. It has not been submitted to a printer.

The [slice reading](nameplate-001-petgf.print.json) records the emitted temperatures, material
mapping and Bambu's profile-lookup/special-tool-command notices. The rendered first-layer
extrusions decode to `HTTPS://HOSM.US/0001`. The actual filament assignment and two-colour
purge remain setup items before sending this editable project to a printer.

The [support audit](nameplate-001-petgf.support-audit.json) finds **no slicer supports on the
nameplate**, including its two lip undersides. The coupon has two bed-rooted support bodies:
one reaches the pump ledge with 18.48 mm build-up; the other reaches the pocket's lower rim
with 41.28 mm build-up. Both contact regions remain open for removal. These are slice readings;
physical catch finish and retention have not been measured.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/prepare_print.py
```
