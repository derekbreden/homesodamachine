# Hopper-funnel silicone mold

The two-piece printed mold that casts the Zone C [hopper funnel](/hardware/printed-parts/zone-c/hopper-funnel/README.md)
in food-grade platinum silicone. The funnel is a hollow [3 mm](SIL_WALL) shell,
so the silicone forms in the gap between an outer **cavity** and an inner
**core** — it is injection-molding geometry, hand-poured.

The mold is a parametric derivative of the funnel: `hopper_funnel.build_solids()`
returns the funnel's exterior and bore as separate solids, and the two mold
halves are those Booleaned out of blocks. Change the funnel and the mold follows.

## The two halves

- **Cavity** ([170.5 × 102.0 × 86.0 mm](CAVITY_DIMS)). A block with the funnel exterior
  carved out, opening up. The brim sits in a recess at the top rim; the spout
  pokes down through a register hole in the floor. Wall [8 mm](MOLD_WALL) around
  the part, floor [10 mm](MOLD_BASE) under the spout.
- **Core** ([182.5 × 114.0 × 96.0 mm](CORE_DIMS)). The funnel interior (the bore) as a plug,
  hanging from a [10 mm](PLATE_THK) top plate that forms the brim's top face and
  registers over the cavity by a skirt that drops over its outside. A pin —
  tapered at the tip so it self-centers — continues the [6.35 mm](SPOUT_BORE)
  spout bore down through the cavity floor, holding the thin spout wall
  concentric. A [4 mm](FILL_D) pour port and [5](N_VENTS) [2.5 mm](VENT_D)
  vents pass through the plate, set over the brim flange ring so they open into
  the silicone.

Because the part is a funnel — everything narrows downward — both halves pull
straight up; no split halves, no side draft. The forming surfaces carry **no
release clearance**: the mold face *is* the part face, so the wall comes out
exactly [3 mm](SIL_WALL) and the collar still press-fits the Zone C opening
(platinum silicone shrinks ~0.1 %). Release is by silicone flex + a
platinum-compatible release film.

## Print

- **Material:** PETG (the cheap workhorse; the cold-core foam shells print in it
  too). Both halves print flat as drawn — cavity opening up, core plate down.
- **Food-contact finish:** the core plug forms the funnel's inside (food-contact)
  surface, so its layer lines telegraph into the silicone. Smooth the plug —
  sand + filler-primer, or print the core on resin/SLA — since PETG can't be
  vapor-smoothed and a layer-lined inner surface traps sticky concentrate. The
  cavity (outside) face can stay as-printed.
- **Critical bridge:** printed opening-up, the cavity's flange-seat ledge (the
  downward-facing shelf where the brim recess meets the chute) is a short bridge
  that forms the brim seal — verify it prints clean.
- No supports needed; the pour port and vents are vertical through-holes.

## Cast

1. **Silicone.** Food-grade platinum-cure, target **Shore A ~50** — stiff enough
   to hold the rectangular brim shape and press-fit the collar, soft enough to
   peel off the core. Select for **high tear-strength / elongation**: the 2 mm
   spout wall is the weak link on demold. One funnel is about
   [69 mL](SIL_VOLUME) of silicone.
2. **Release + inhibition.** Platinum silicone is cure-poisoned by sulfur, tin,
   amines, and many release agents — a bad release leaves an uncured, tacky layer
   on the food face. Use a **platinum-compatible (addition-cure) release**, or
   none if a test shows bare PETG demolds clean. **Patch-test the actual silicone
   *and* release on a PETG coupon first** (not just bare PETG). Keep latex gloves
   and sulfur-bearing clay/tape away from the mold.
3. **Degas + pour — vacuum is the primary path, not optional.** The deep 2 mm
   spout is a void trap, so clear it first: pour degassed silicone into the
   **open cavity** and pull vacuum on it — the spout fills bottom-up and air rises
   out. Then lower the core slowly so it displaces silicone up and out the top
   vents. Keep the mold slightly **under-filled / degas the open cavity before
   seating the core** so the ~3× vacuum rise doesn't overflow and starve the part.
   (Fallback: seat the core and pour through the fill port — but the deep spout
   casts voids this way; use only with no chamber.)
4. **Clamp.** Hold the plate down with clamps or weight through the plate while it
   cures; a loosely-held plate flashes a soft fill at the brim parting line.
5. **Cure, then post-cure bake.** After primary cure, **bake per the silicone's
   TDS** — typically **~4 h at ~200 °C (392 °F)** (industry norm 160–200 °C for
   2–6 h). The high-temp soak is what drives off residual platinum and cyclic
   siloxanes (D4/D5/D6) and improves compression set so the collar holds; a
   filament dryer (≤110 °C) is far too cool. It is the food-contact acceptance
   gate — see
   [wetted-surface-test.md](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md).
6. **Demold.** Respect the full demold time before pulling the thin spout; lift
   the core out (it peels off the plug), then pop the funnel from the cavity.
7. **Reuse.** Reapply release every pour and inspect/clean the PETG faces between
   cycles — a reused mold accumulates cured film and bald spots.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel-mold/hopper_funnel_mold.py`
→ `hopper-funnel-mold-cavity.step`, `hopper-funnel-mold-core.step`, and an
exploded `hopper-funnel-mold-assembly.step`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel-mold/hopper_funnel_mold.py`
