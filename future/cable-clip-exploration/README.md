# Bare relay-ribbon clip trial

This coupon holds the **bare 22 AWG 4P J5 RELAYS ribbon** beside a wall, with the
four conductors stacked vertically. The modeled ribbon is 7.25 × 1.70 mm: four
1.70 mm insulated conductors on 1.85 mm pitch. That envelope is a layout value;
the actual complete ribbon section has not been measured.

The one-piece clip has an 8 mm span along the cable, a 2.20 × 7.75 mm seat,
a 1.45 mm entry and a 0.75 mm retaining beak. Its outer post, cap and 45°
corbel use 3 mm stock. The coupon’s host wall is 3 mm thick and 14 mm long.
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
reviewed offline, with an **8 min 36 s** native estimate. It has not been submitted.

The installed-up mouth prints facing the bed because back-top prints ceiling-down.
The coupon uses the same half-turn about X and a +19.70 mm Z translation.
Its host ends at that exact **19.70 mm** height, so both the wall and outer arm
start on the bed. The two bed islands join above the open pocket; a short bridge
closes the 2.20 mm gap at print Z11.50 mm. Tree(auto)/Default supports remain
enabled. The native paths contain no support or brim inside either the cable seat
or entry corridor.

Use the actual bare 4P ribbon to assess insertion, grip, axial slide, release and
layer/root survival. This coupon has no physical fit or retention result and does
not test a braided sleeve or finished crimp inside the clip.

```sh
tools/cad-venv/bin/python future/cable-clip-exploration/relay_ribbon_trial.py
tools/cad-venv/bin/python future/cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon/prepare.py
```
