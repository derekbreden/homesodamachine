# Faucet shell material and printing

The shell base, shell tip, display cover and above-counter plate use PET-GF.
The Sculpted faucet uses black Polymaker Fiberon PET-GF15 on the
Bambu H2C with its left 0.4 mm diamond PCD hotend. The print project uses
[0.24 mm](PRINT_LAYER) layers with the saved PET-GF material settings.

Rigid structural walls, fastener seats, display supports and insert
backing use a [2 mm](WALL_MIN) minimum at the checked sections. The round gooseneck
provides [2 mm](SPLIT_SOCKET_WALL) socket and [2 mm](SPLIT_PLUG_WALL) plug walls at its close-fit curved joint.
The display cover flexes around the rigid neck. Its inward-preformed wings
carry broad retaining lips. The nominal skin is 1.30 mm, with a 1 mm minimum
for its thin sections. The [cover geometry](../faucet-display-cover/README.md)
defines the preload and mating grooves. Firm snap seating and retention are
reported for the identified complete covers in the [physical trial](../../fixtures/faucet-display-snap/print-log.md).
The current 27 mm neck and matching cover require their own fit reading;
the [acceptance record](../faucet-display-cover/physical-acceptance.json) preserves
the scope of the accepted article. Repeated cycling and resistance to permanent
spreading remain physical readings. The 2 mm TPU countertop gasket and two
[85A TPU vent bungs](../asse-vent-seals/README.md) are compressible sealing components.

The base and tip use build rotations of −15° and −95° about the CAD X axis.
The tip's build direction is at the angular midpoint of its gooseneck sweep,
with the joint end toward the bed and the crown raised. Their print heights are
[220.1 mm](BASE_PRINT_HEIGHT) and [158.9 mm](TIP_PRINT_HEIGHT). The visible swept gooseneck flanks reach
[45°](MAX_PRINT_OVERHANG) of overhang. Those angles do not describe every face
of the lower body or the hidden curved plug.

The separate cover prints bezel up at −50° about the CAD X axis. Its lower
skirt and lip seating lands face the bed; its upper retaining lands face up.
The inner bezel receives support accessible through the open underside.
The plate prints with its gasket face toward the bed. Support contact,
access and removal must be inspected in the production slice and first
physical print, especially inside the donor cavity, around the neck joint
and at the display lips and grooves. Preserve their seating and retaining faces.

Printable meshes use an absolute surface-distance tolerance in millimetres
and an angular tolerance, both set in `piece_mesh`. Meshing uses fresh CAD
copies without cached triangles. The print project embeds those STL surfaces
without reducing them. The geometry audit measures the serialized base STL
against points on its analytic outer loft.

The drinking flow remains inside the existing LLDPE tubes and donor metal
body. Fault discharge enters the PET-GF chamber between the two TPU bungs and
leaves through its open underside outlet. The chamber is isolated from the
display and dry passages. It requires printed-surface cleanup and a liquid
containment check; the native CAD and toolpaths do not establish that seal.

The [print readiness record](../vent-print-readiness/README.md) links the exact
editable projects and native print archives for the rigid pieces, bungs,
countertop gasket and perimeter insertion tool.

Use the drying and handling procedure recorded in the
[print log](print-log.md) and [tool ledger](/hardware/ledger/tools.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`
