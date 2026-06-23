# Lite hopper-funnel silicone mold

The two-piece printed mold that casts the lite
[hopper funnel](/pie-in-the-sky/lite/printed-parts/funnel/funnel.py) in
food-grade platinum silicone — the **same architecture** as the Kitchen
edition's [hopper-funnel-mold](/hardware/printed-parts/zone-c/hopper-funnel-mold/README.md),
applied to the lite funnel's geometry (narrow-X, deeper drop, centered spout).
The funnel is a hollow [3 mm](SIL_WALL) shell, so the silicone forms in the gap
between an outer **cavity** and an inner **core**.

The mold is a parametric derivative of the lite funnel: `funnel.build_solids()`
returns the exterior + bore solids, and the two halves are those Booleaned out of
blocks — so the mold tracks the funnel as the lite packing keeps settling.

## The two halves

- **Cavity** ([93.0 × 164.7 × 99.0 mm](CAVITY_DIMS)). The funnel exterior carved out of a
  block, opening up; brim recess at the rim, spout-pin register hole in the
  floor. Wall [8 mm](MOLD_WALL) around the part, floor [10 mm](MOLD_BASE) under
  the spout.
- **Core** ([105.0 × 176.7 × 109.0 mm](CORE_DIMS)). The bore as a plug on a [10 mm](PLATE_THK)
  top plate that forms the brim top and registers over the cavity by a skirt; a
  centered, lead-nosed pin continues the [6.35 mm](SPOUT_BORE) spout bore down
  through the cavity floor, holding the thin spout wall concentric. A
  [4 mm](FILL_D) pour port and [5](N_VENTS) [2.5 mm](VENT_D) vents pass
  through the plate, over the brim flange ring.

Both halves pull straight up (a funnel is its own draft); the forming surfaces
carry no release clearance, so the wall casts at exactly [3 mm](SIL_WALL). One
funnel is about [84 mL](SIL_VOLUME) of silicone.

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
