# Faucet shell material and printing

The shell base, shell tip, display cover and above-counter plate use PET-GF.
The recorded production material is black Polymaker Fiberon PET-GF15 on the
Bambu H2C with its 0.4 mm tungsten-carbide hotend. The print project preserves
the saved PET-GF profile and 0.24 mm process settings.

White Fiberon PET-GF15 is a listed color in
[Polymaker's range](https://shop.polymaker.com/products/fiberon-pet-gf15).
It is shown for design review; its settings, surface finish and fitted joints
remain to be qualified on these parts.

Functional walls, fastener seats, snap arms, display supports and insert
backing use a 3 mm minimum at the checked sections. The round gooseneck
provides separate 3 mm socket and plug walls at its close-fit curved joint.
The display's cosmetic cover has a nominal 1.30 mm wall, with a 1 mm minimum
for cosmetic sections. The 2 mm TPU countertop gasket is a compressible
sealing component.

The base and tip use build rotations of −35° and −105° about their shared
arc frame. Their CAD print heights are [232.6 mm](BASE_PRINT_HEIGHT) and
[138.8 mm](TIP_PRINT_HEIGHT). The visible swept gooseneck flanks stay within
[35°](MAX_PRINT_OVERHANG) of overhang; the hidden curved plug reaches 49.36°.
Those angles do not describe every face of the lower body or display head.

The separate cover prints with its planar bezel face on the bed.
The plate prints with its gasket face toward the bed. Support contact,
access and removal must be inspected in the production slice and first
physical print, especially inside the donor cavity, around the neck joint
and at the display captures. Preserve the bearing and sliding faces.

The wetted flow remains inside the existing LLDPE tubes and donor metal
body. PET-GF is the structural enclosure around that flow path.

Use the drying and handling procedure recorded in the
[print log](print-log.md) and [tool ledger](/hardware/ledger/tools.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`
