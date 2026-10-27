# Bare relay-ribbon clip trial

This coupon holds the **bare 22 AWG 4P J5 RELAYS ribbon** beside a wall, with the
four conductors stacked vertically. The modeled ribbon is 7.25 × 1.70 mm: four
1.70 mm insulated conductors on 1.85 mm pitch. That envelope is a layout value;
the actual complete ribbon section has not been measured.

The one-piece clip has an 8 mm span along the cable, a 2.20 × 7.75 mm seat,
a 1.45 mm entry and a 0.75 mm retaining beak. Its outer post, cap and 45°
corbel use 3 mm stock. The coupon’s host wall is 3 mm thick, 24 mm long and
extends 6 mm below the hook. It stands on one 72 mm² wall-edge footprint.
The [geometry report](geometry-report.json) binds the
[generator](relay_ribbon_trial.py), installed and print-oriented native parts,
modeled conductor clearance and source hashes. It records 0.25 mm seated
clearance around the modeled strands.

## Proposed J5 site

The [site reading](proposed-site-review.json) places the guide on back-top’s west
inside face, **X−98.5**, across **Y324–332 mm**. The local frame begins at
**(−98.5, 328, 275.925) mm** and the ribbon centre is
**(−97.4, 328, 288) mm**. The installed mouth faces +Z; the cable runs along Y.

This proposal requires dressing the J5 conductors **2.4 mm toward the wall**,
with an **8 mm straight bare window before the relay fan-out**. The ¼-inch PET
braid ends before the clip. It does not represent the current route unchanged
or remove a counted tie. The closest tested native body is V-A, with
**0.846 mm** clip clearance and **4.096 mm** clearance to the loading envelope.
The checked fixtures have no native overlap. Connecting curves, braid transition,
complete quadrant assembly and service remain outside that local reading.
The guide and redressing are a site proposal, not production integration.

## Print preparation

The [Mark2 job](prints/2026-10-26-mark2-relay-ribbon/README.md) is prepared and
reviewed with a **10 min 1 s** native estimate. It is running on Mark2 as
**task 1379210744**, accepted **October 26 at 11:11 p.m. CDT**. The
[launch receipt](prints/2026-10-26-mark2-relay-ribbon/launch.json) binds the
reviewed archive to the active printer task.

The coupon prints in its **installed orientation, entry up**, translated 6 mm
upward to put the host wall's bottom on the bed. Its total height is **25.70 mm**.
The 45° hook corbel grows out of the wall beginning at print Z6 mm.
The larger wall footprint supplies its bed attachment; the recipe requests no
brim. Tree(auto)/Default supports remain enabled, and the emitted native slice
has no support. The cable seat and entry corridor are clear. This fit coupon's
orientation does not define the proposed enclosure quadrant's print pose.

Use the actual bare 4P ribbon to assess insertion, grip, axial slide, release and
layer/root survival. This coupon has no physical fit or retention result and does
not test a braided sleeve or finished crimp inside the clip.

```sh
tools/cad-venv/bin/python future/cable-clip-exploration/relay_ribbon_trial.py
tools/cad-venv/bin/python future/cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon/prepare.py
```
