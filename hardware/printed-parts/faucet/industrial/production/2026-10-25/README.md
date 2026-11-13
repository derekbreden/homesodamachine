# The approved Industrial faucet print's meshes

The five STLs in this directory are byte-identical copies of the inputs to the
approved physical prints. The [production selection](../../production-selection.json)
names each beside the generated part that prints in its place, with its SHA-256
and its print task. Nothing prints from this directory; a generated part is read
against the mesh here.

The set contains the Industrial base, the lowered shared tip with four foot recesses
and two switch pockets, the extended-front-skirt display cover, the rigid Industrial
above-counter plate and the side-down lever. The cover is task 1374330388; the
remaining four parts are from task 1372253517. The TPU gasket is a separate print.

The [tip STEP](faucet-shell-tip.step) and the
[relaxed cover STEP](sculpted-display-cover-print.step) are the sources of the
approved tip and cover meshes. The
[nominal seated cover STEP](sculpted-display-cover-seated.step) is that cover's
installed shape.

The [physical acceptance and five photographs](../../../faucet-display-cover/prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json)
record working fit and approval. A visible front-corner gap remains and is accepted
as good enough, with no further iteration requested. The selected production
recipe retains **Bambu’s 0.20 mm first bed layer and 0.24 mm later layers**,
with no variable layer bands. Other material, support, seam and calibration settings retain the
accepted recipe.
