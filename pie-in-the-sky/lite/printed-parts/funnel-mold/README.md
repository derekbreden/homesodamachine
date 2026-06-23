# Lite hopper-funnel silicone mold

The two-piece printed mold that casts the lite
[hopper funnel](/pie-in-the-sky/lite/printed-parts/funnel/funnel.py) in
food-grade platinum silicone — the **same architecture** as the Kitchen
edition's [hopper-funnel-mold](/hardware/printed-parts/zone-c/hopper-funnel-mold/README.md),
applied to the lite funnel's geometry (narrow-X, deeper drop, centered spout).
The funnel is a hollow [3 mm](SIL_WALL) shell, so the silicone forms in the gap
between an outer **cavity** and an inner **core**.

The mold is a parametric derivative of the lite funnel: `funnel.build_solids()`
returns the exterior + bore solids, and the two halves wrap those — so the mold
tracks the funnel as the lite packing keeps settling.

## The two halves

Both are **relieved shells, not solid blocks**: a registration skin on the
outside, a forming wall around the funnel, and a diagonal X-brace tying the two,
with the dead volume between them hollowed out. The pair is [905 g](PAIR_MASS)
of PETG at 100 % infill — and because the relief leaves the forming faces backed
by solid wall, 100 % infill costs little. The forming-wall overhangs over the
relief are carried by **print supports**, not by PETG structure, so the model
stays minimal.

- **Cavity** ([95.0 × 158.0 × 99.0 mm](CAVITY_DIMS), [606 g](CAVITY_MASS)). The
  funnel exterior carved from a block, opening up; brim recess at the rim,
  spout-pin register hole in the floor. A [5 mm](SKIN_WALL) outer skin carries
  the [10 mm](MOLD_BASE) spout floor and the [8 mm](MOLD_WALL)-nominal block
  footprint the core skirt registers against; a [6 mm](BOWL_WALL) forming wall
  contains the silicone and backs the cast against the vacuum pull. Between skin
  and forming wall the dead solid is relieved out, leaving only a [6 mm](BRACE_WALL)
  diagonal X-brace (corner to corner through the spout boss) to hold the open
  cavity rigid through the pour; the relief vents down to the bed.
- **Core** ([107.0 × 170.0 × 109.0 mm](CORE_DIMS), [299 g](CORE_MASS)). The bore
  as a plug on a [10 mm](PLATE_THK) top plate that forms the brim top and
  registers over the cavity by a skirt; a centered, lead-nosed pin continues the
  [6.35 mm](SPOUT_BORE) spout bore down through the cavity floor, holding the
  thin spout wall concentric. The plug is hollow — a forming-wall shell vented up
  through the plate — so the deep chute is not a solid mass. A [4 mm](FILL_D)
  pour port and [5](N_VENTS) [2.5 mm](VENT_D) vents pass through the plate, over
  the brim flange ring.

Both halves pull straight up (a funnel is its own draft); the forming surfaces
carry no release clearance, so the wall casts at exactly [3 mm](SIL_WALL). One
funnel is about [82 mL](SIL_VOLUME) of silicone.

## Print

Both halves print as drawn — cavity opening up, core clamp-face down with the
plug up. The cavity's forming wall flares out over the relief (steepest on the
deep-Y ramp), so it **prints on supports**: enable them, and they grow in the
relief gaps between the X-brace, not on a forming face. That support sits in
sealed-off internal dead space — not in the silicone path, not on the cast
surface, not in the registration — so it can be left in place; the only check is
that none intrudes into the open bowl, the pin-register hole, or the vents. The
forming wall and registration skin stay fully solid (the relief stops short of
both), so the cast surface and the skirt fit are unaffected by the lightening. As
on the Kitchen mold, smooth the core plug (it forms the funnel's food-contact
inside face); the cavity exterior can stay as-printed.

## Cast + bake

Identical procedure to the Kitchen edition — food-grade platinum silicone (Shore
A 40), vacuum-degas the filled mold, demold the bare funnel, then post-cure bake
and screen per
[wetted-surface-test.md](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md)
before use. Full step-by-step (release/inhibition, pour, clamp, bake, demold):
[hopper-funnel-mold/README.md](/hardware/printed-parts/zone-c/hopper-funnel-mold/README.md).

The cast funnel's silicone, pigment, and release are costed per-unit in the
[lite BOM](/pie-in-the-sky/lite/lite-bom.md) (Flavor subsystem); the mold, vacuum
chamber, pump, and post-cure oven are shared tooling in the ledger §21.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/printed-parts/funnel-mold/funnel_mold.py`
→ `funnel-mold-cavity.step`, `funnel-mold-core.step`, and an exploded
`funnel-mold-assembly.step`.

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/printed-parts/funnel-mold/funnel_mold.py`
