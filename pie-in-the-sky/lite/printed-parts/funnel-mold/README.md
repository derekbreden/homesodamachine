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

Neither is a solid block. Each is the bare structure the mold needs and nothing
more — a forming wall around the funnel, a registration band at the top, and a
minimal brace — with everything else open. The pair is [502 g](PAIR_MASS) of PETG
at 100 % infill; the forming-wall overhangs are held during printing by
sacrificial **supports**, not by PETG that stays in the part.

- **Cavity** ([95.0 × 158.0 × 99.0 mm](CAVITY_DIMS), [262 g](CAVITY_MASS)). The
  funnel exterior carved from a block, opening up; brim recess at the rim,
  spout-pin register hole in the floor. The mold is a [4 mm](BOWL_WALL) forming
  wall around the funnel (the cavity that holds the silicone) standing on a
  [10 mm](MOLD_BASE) spout floor. The only other solid is a [13 mm](COLLAR_H)
  registration collar at the top — the [8 mm](MOLD_WALL)-wide band the core skirt
  drops over — and a low [4 mm](BRACE_WALL) diagonal X-brace, corner to corner
  through the spout boss, that stands the necking funnel on a wide foot through
  the pour. Below the collar there is no outer skin; the chute forming wall is its
  own stiff tube.
- **Core** ([107.0 × 170.0 × 109.0 mm](CORE_DIMS), [241 g](CORE_MASS)). The bore
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
plug up. The cavity's forming wall flares out over open space (steepest on the
deep-Y ramp), so it **prints on supports**: enable them and they fill the open
relief, landing on the bed and the X-brace, never on the forming face. That
support is in open space off the part — not in the silicone path, not on the cast
surface, not in the registration — so it can be left in; the only check is that
none intrudes into the bowl, the pin-register hole, or the vents. The forming
wall, the collar, and the spout floor stay fully solid, so the cast surface and
the skirt fit are unaffected by the lightening. As on the Kitchen mold, smooth
the core plug (it forms the funnel's food-contact inside face); the cavity
exterior can stay as-printed.

Per-attempt slice records: [`print-log.md`](print-log.md).

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
