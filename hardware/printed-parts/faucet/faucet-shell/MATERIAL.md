# Faucet shell material and printing

The shell base, shell tip, display cover and above-counter plate use PET-GF.
Use the selected style's reviewed printer, left 0.4 mm nozzle and saved
Polymaker Fiberon PET-GF15 material settings. Ordinary model layers are
 above the 0.20 mm first bed layer. The
[complete Industrial recipe](../industrial/faucet-industrial-petgf.md) uses
0.12 mm on its two selected base shoulder bands.

Rigid structural walls, fastener seats, display supports and insert
backing use a minimum at the checked sections. The round gooseneck
provides socket and plug walls at its close-fit curved joint.
The display cover flexes around the rigid neck. Its inward-preformed wings
carry broad retaining lips. The nominal skin is 1.30 mm, with a 1 mm minimum
for its thin sections. The [cover geometry](../faucet-display-cover/README.md)
defines the preload and mating grooves. Firm snap seating and retention are
reported for the identified complete covers in the [physical trial](https://github.com/derekbreden/homesodamachine/blob/archive-finished-trials/hardware/printed-parts/fixtures/faucet-display-snap/print-log.md).
The current 27 mm neck and matching cover require their own fit reading;
the [acceptance record](../faucet-display-cover/physical-acceptance.json) preserves
the scope of the accepted article. Repeated cycling and resistance to permanent
spreading remain physical readings. The 2 mm TPU countertop gasket and
[donor-port thimble](../tpu-o-ring/README.md) have their own material recipes.

The base and tip use build rotations of −15° and −105° about the CAD X axis.
The tip's build direction is at the angular midpoint of its gooseneck sweep,
with the joint end toward the bed and the crown raised. Their print heights are
 and. The visible swept gooseneck flanks reach
 of overhang. Those angles do not describe every face
of the lower body or the hidden curved plug.

The separate cover prints bezel up at −50° about the CAD X axis. Its lower
skirt and lip seating lands face the bed; its upper retaining lands face up.
The inner bezel receives support accessible through the open underside.
The plate prints with its gasket face toward the bed. Support contact,
access and removal must be inspected in the production slice and first
physical print, especially inside the donor cavity, around the neck joint
and at the display lips and grooves. Preserve their seating and retaining faces.

Printable meshes are the kernel's own triangles (`faucet_shell.rs`): every
curve is cut by the chord and angle in `tools/hsm/kernel/src/rule.rs`, and
the STL keeps each triangle as cut. The print project embeds those STL
surfaces without reducing them. The geometry audit measures the serialized
base STL against points on its analytic outer loft.

The drinking flow remains inside the existing LLDPE tubes and donor metal
body. The white drain ends square inside the smooth shared passage, with
3 mm of mouth clearance and an unsealed Ø4 mm underside warning hole. No
drain bung or sealed chamber is fitted. Incidental escape into the housing
during a major fault is accepted; the complete faucet requires replacement
after that event. Physical threading, cleanup and fault discharge remain
unmeasured.

The [print readiness record](../vent-print-readiness/README.md) links the exact
editable projects and native print archives for the selected rigid set.
The countertop gasket and donor thimble are separate TPU prints.

Use the drying and handling procedure recorded in the
[print log](print-log.md) and [tool ledger](/hardware/ledger/tools.md).
