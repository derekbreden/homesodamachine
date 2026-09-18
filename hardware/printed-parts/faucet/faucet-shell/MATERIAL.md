# Faucet shell material and printing

The shell base, shell tip, display cover and above-counter plate use PET-GF.
The production material is black Polymaker Fiberon PET-GF15 on Mark2, a
Bambu H2C with its left 0.4 mm diamond PCD hotend. The print project preserves
the saved PET-GF profile and 0.24 mm process settings.

White Fiberon PET-GF15 is a listed color in
[Polymaker's range](https://shop.polymaker.com/products/fiberon-pet-gf15).
It is shown for design review; its settings, surface finish and fitted joints
remain to be qualified on these parts.

Rigid structural walls, fastener seats, display supports and insert
backing use a [2 mm](WALL_MIN) minimum at the checked sections. The round gooseneck
provides [2 mm](SPLIT_SOCKET_WALL) socket and [2 mm](SPLIT_PLUG_WALL) plug walls at its close-fit curved joint.
The display cover flexes around the rigid neck. Its inward-preformed wings
carry broad retaining lips. The nominal skin is 1.30 mm, with a 1 mm minimum
for its thin sections. The [cover geometry](../faucet-display-cover/README.md)
defines the preload and mating grooves. The complete cover's insertion force, retention and resistance
to permanent spreading must be read from the PET-GF fit trial. The 2 mm
TPU countertop gasket is a compressible sealing component.

The base and tip use build rotations of −15° and +40° about their shared
arc frame. The tip stands on its dispense face with the display groove planes
vertical. Their CAD print heights are [244.6 mm](BASE_PRINT_HEIGHT) and
[111.0 mm](TIP_PRINT_HEIGHT). The visible swept gooseneck flanks reach
[70°](MAX_PRINT_OVERHANG) of overhang. Those angles do not describe every face
of the lower body or the hidden curved plug.

The separate cover stands on its front wall, with the inner bezel and retaining
faces vertical.
The plate prints with its gasket face toward the bed. Support contact,
access and removal must be inspected in the production slice and first
physical print, especially inside the donor cavity, around the neck joint
and at the display lips and grooves. Preserve their seating and retaining faces.

Printable meshes use an absolute surface-distance tolerance in millimetres
and an angular tolerance, both set in `piece_mesh`. Meshing uses fresh CAD
copies without cached triangles. The print project embeds those STL surfaces
without reducing them. The geometry audit measures the serialized base STL
against points on its analytic outer loft.

The wetted flow remains inside the existing LLDPE tubes and donor metal
body. PET-GF is the structural enclosure around that flow path.

Use the drying and handling procedure recorded in the
[print log](print-log.md) and [tool ledger](/hardware/ledger/tools.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`
