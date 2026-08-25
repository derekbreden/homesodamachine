# Funnel silicone mold

The two-piece printed mold that casts the Zone C [funnel](/hardware/printed-parts/zone-c/funnel/README.md)
in food-grade platinum silicone. The funnel is a hollow [6 mm](SIL_WALL) shell,
so the silicone forms in the gap between an outer **cavity** and an inner
**core** — it is injection-molding geometry, hand-poured. Two printed pieces and
one piece of stock: a [6.35 mm](ROD_D) dowel is the spout's bore.

The mold is a parametric derivative of the funnel: `funnel.build_solids()`
returns the funnel's exterior and bore as separate solids, and the two mold
halves are those Booleaned out of blocks. Change the funnel and the mold follows.

## The two halves

- **Cavity** ([189.0 × 189.0 × 74.6 mm](CAVITY_DIMS)). A block with the funnel exterior
  carved out, opening up. The catch bowl sits in a recess at the top rim. Below the
  spout's own exit face the pocket carries on [12 mm](TIP_BUFFER) further as a
  **blind** drafted bore, stepped [1 mm](TIP_STEP) inside the spout's radius —
  nothing passes the floor. Wall [8 mm](MOLD_WALL) around the part, floor
  [10 mm](MOLD_BASE) under the closed tip.
- **Core** ([201.0 × 201.0 × 50.6 mm](CORE_DIMS)). The funnel interior (the bore) as a plug,
  hanging from a [10 mm](PLATE_THK) top plate that forms the bowl rim's top face and
  registers over the cavity by a skirt that drops over its outside. **The plug stops
  at the ramp tip**: below it the [6.35 mm](SPOUT_BORE) round is the rod's, not the
  print's, and a [28.8 mm](ROD_SOCKET) socket bores up the cone to take it. Nothing
  slender is printed — the core's tallest feature is now the cone itself. A
  [11 mm](FILL_D) pour port and [5](N_VENTS) [2.5 mm](MOLD_VENT_D)
  vents pass through the plate, set over the bowl's rim ring so they open into
  the silicone. The port takes the **whole ring** less a [1 mm](FILL_LAND) land —
  it is not a size but whatever the ring leaves, and it grew when the wall did. A
  [20 mm](FILL_DISH) cone necks down into it from the plate's top face: the dish is
  what the cup is aimed at, and it lives in the plate's own top with no silicone
  under it, so the ring does not hold it.
- **Rod** — a [6.35 mm](ROD_D) × [50.8 mm](ROD_LEN) ground steel dowel (¼" × 2",
  a drawer item). [28.8 mm](ROD_SOCKET) of it lives in the core's socket and
  [22.0 mm](ROD_BELOW) stands in silicone; it **bottoms** in the socket, so the stock
  length sets its own reach and nothing is measured on assembly. It touches no part
  of the mould but that socket, and stops [2 mm](TIP_CAP) short of the pocket's
  blind floor. Slip fit — the core lifts **off** it. Writes no STEP: it is stock,
  billed as a length the way the drain stub is.
  **Buy it ground.** The socket carries [0.1 mm](ROD_FIT) of slip, so the rod's own
  diameter tolerance has to be a fraction of that: ASME-standard ground dowel pins
  hold 0.0025–0.013 mm and any of them will do. Pins sold on a 0.13–0.25 mm band —
  the cheap bearing-steel shelf-peg grade — carry more error than this fit has room
  for, and will either not enter the socket or rattle in it.

## The spout's bore is not printed

**The rod is not fixed to the plate**, so nothing that frees the plug reaches it. That
matters because a Ø6.35 column buried this deep parts at about **34 N** sideways and
takes about **950 N** to pull apart — a 28× asymmetry, and the whole of demold is
keeping on the right side of it. The column is also only **1 %** of the core's contact
with the silicone: it is never what is holding on, only what is in reach while the plug
and the ramp cone are being freed.

Off the plate, it is out of reach. Demold becomes **three independent axial moves** —
core off the rod, funnel out of the cavity, rod out of the cast, each one straight and
each one on its own. Two more things come with the choice: that bore is a **sealing**
bore (the worm clamp closes silicone moulded on this surface onto the drain stub), and
ground stock is rounder and smoother than a printed column of the same nominal; and a
bent rod is replaced from the drawer with the core's own finish untouched.

The socket carries [0.1 mm](ROD_FIT) of slip on diameter — small deliberately, since
it is the one place silicone could wick past the rod, and it will not cross that in a
pot life.

## The tip is cast long and closed, and cut afterwards

The mould does not form the spout's exit face. Forming it is what asked for a
Ø6.35 column driven through a zero-clearance hole in the cavity floor, and a column
loaded sideways on assembly is a column that snaps. Instead the spout casts
[12 mm](TIP_BUFFER) PAST that face into a blind pocket and closes there. Nothing is
pressed into anything; the rod hangs free the whole way down.

The rod runs the full buffer, so the cast tube is **open bore wherever it is cut** —
the cut only has to land in the right place, not make the hole. And the buffer steps
[1 mm](TIP_STEP) in at the exit plane, which leaves an annular shoulder facing down
at exactly the spout length the drain joint is dimensioned to. Lay a razor flat on
that shoulder and sweep: that is the cut, and it is the funnel's real length. It
steps **in** rather than out so every face below the funnel still narrows downward
and the scrap draws up out of its own bore with the part. Everything below the
shoulder is scrap — under a third of a millilitre of it.

Because the part is a funnel — everything narrows downward — both halves pull
straight up; no split halves, no side draft. The forming surfaces carry **no
release clearance**: the mold face *is* the part face, so the wall comes out
exactly [6 mm](SIL_WALL) and the collar still press-fits the Zone C opening
(platinum silicone shrinks ~0.1 %). Release is by silicone flex + a
platinum-compatible release film.

## Print

- **Material:** PETG (the cheap workhorse; the cold-core foam shells print in it
  too). Both halves print flat as drawn — cavity opening up, core plate down. Printed
  that way the core's highest point is the ramp cone, and the socket is a plain
  vertical hole down its axis; there is no slender tower on either half.
- **Food-contact finish:** the core plug forms the funnel's inside (food-contact)
  surface, so its texture telegraphs into the silicone. Smooth + seal the plug —
  light sand, then a hard **gloss clear-acrylic** seal coat (not a matte
  filler-primer, which is micro-porous and grips/tears soft silicone; not enamel,
  which can inhibit the cure). PETG can't be vapor-smoothed, and a rough inner
  surface both traps concentrate and outgasses under vacuum. The cavity (outside)
  face can stay as-printed. Full procedure — seal, release, coupon-test — under
  "Finish the core" below.
- **Open the socket before the first pour.** It models at
  [6.45 mm](ROD_SOCKET_D) and printed PETG holes come out under it. Test-fit the rod
  dry; if it does not drop in under its own weight, run a **1/4" bit** down the
  socket — in PETG that leaves ~6.4–6.5 mm, which is the fit as drawn. Do this
  *before* the core is sealed and released, so the swarf goes with the sanding.
- **Critical bridge:** printed opening-up, the cavity's flange-seat ledge (the
  downward-facing shelf where the bowl recess meets the throat) is a short bridge
  that forms the bowl-rim seal — verify it prints clean.
- No supports needed; the pour port and vents are vertical through-holes, and the
  pour dish is a cone that only ever widens toward the plate's top — printed plate
  down, every layer of it is larger than the one under it.

## Finish the core

The core plug forms the funnel's **wetted inside face**, so its surface
telegraphs into the silicone and sets how the cast releases. The two halves get
different finishes:

- **Cavity (cosmetic outside):** leave as-printed; mist Mann Ease Release 200
  ([§21](/hardware/ledger/purchases.md)) every pour.
- **Core (food-contact inside):** **seal** it with a hard clear acrylic and run a
  light release on it too — *not* a filler-primer, and *not* release-free.

Why not a filler-primer: sanded back it cures matte and micro-porous, which a soft
40A silicone keys into and tears against on demold (a grip surface, not a release
surface), and enamel-class primers can inhibit the cure. Why not release-free: a
cured film alone does not reliably release soft silicone over many pulls — it
grips and can delaminate. Sealing and releasing are two separate jobs; do both.

Finishing the core (owned = already in the ledger):

1. **Light-sand** the core with the Shineboc wet/dry sponges (owned,
   [B0D8ZC6HKY](https://www.amazon.com/dp/B0D8ZC6HKY)), ~320 → 600 grit; wipe with
   99.9 % IPA (owned, [B0BZ21DBJ6](https://www.amazon.com/dp/B0BZ21DBJ6)) and let it
   flash off.
2. **Seal** with 2–3 thin coats of **gloss clear acrylic** — Krylon K01303 Crystal
   Clear Acrylic ([B00023JE7K](https://www.amazon.com/dp/B00023JE7K)). A hard,
   glossy, low-surface-energy film: it seals the print porosity (no outgassing
   through the face under vacuum), is amine/sulfur/tin-free so it does not inhibit
   the cure, and bonds to PETG. *Not* a high-build filler — at 0.08 mm the texture
   is shallow.
   - **Only if the 0.08 mm texture still telegraphs through:** one thin
     self-leveling epoxy base coat — Smooth-On XTC-3D
     ([B01BKSLI9M](https://www.amazon.com/dp/B01BKSLI9M)) — *under* the acrylic to
     fill it glassy. The acrylic still goes on top as the release skin; epoxy alone
     is not a release face and must be fully cured.
3. **Let it fully gas off before casting** — solvent (or, for the epoxy base,
   uncured resin) left in the film inhibits platinum cure. Wait until there is no
   solvent smell.
4. **Release the core too:** a light mist of Mann Ease Release 200 on the cured
   acrylic. It is an addition-cure-compatible *film*, not a silicone-fluid release
   (which would prime the silicone to bond), so it does not add the D4/D5/D6
   siloxane the screen is chasing — and the funnel's ~200 °C post-cure bake +
   [wetted-surface screen](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md)
   is the food-contact gate that clears any trace. Keep silicone-fluid "food-grade"
   releases off it.
5. **Coupon-test the exact stack, on every re-coat:** cast a BBDINO 40A pad on a
   scrap carrying the *same* sand → acrylic → release finish, room-temp cure, and
   check both that it cures firm (no tacky face) **and** peels clean — then peel it
   a few more times on the same coupon, since grip/fusing shows up over repeated
   demolds, not the first.

Re-coat the acrylic when it dulls or bald-spots; it is the wear surface that gates
how many funnels the mold yields. If PETG + acrylic can't pass the coupon, the
fallback is a natively smooth SLA-printed core (fully UV-cured + IPA-washed +
sealed the same way — resin is the worst cure inhibitor, so the wash discipline
and coupon test are mandatory).

## Cast

1. **Silicone.** Food-grade platinum-cure, **Shore A 40** (the BBDINO 40A kit in
   [purchases.md §21](/hardware/ledger/purchases.md)). Soft is right here: it
   peels off the rigid core without tearing the 2 mm spout, conforms and seals at
   the press-fit collar, and flexes to clean — and the funnel never has to be
   self-supporting, since the rigid opening cradles it during a pour. Select for
   **high tear-strength / elongation**; the 2 mm spout wall is the weak link on
   demold. One funnel is about [135 mL](SIL_VOLUME) of silicone. BBDINO rates it
   food-contact safe for **fat-free foods** — fine here: the concentrate is a
   sugar/sucralose syrup with no fat.
2. **Release + inhibition.** Platinum silicone is cure-poisoned by sulfur, tin,
   amines, and many release agents — a bad release leaves an uncured, tacky layer
   on the food face. Use a **platinum-compatible (addition-cure) release**, or
   none if a test shows bare PETG demolds clean. **Patch-test the actual silicone
   *and* release on a PETG coupon first** (not just bare PETG). Keep latex gloves
   and sulfur-bearing clay/tape away from the mold.
3. **Degas + pour.** With a chamber, pour degassed silicone into the **open
   cavity** and pull vacuum on it — the spout fills bottom-up and air rises out —
   then lower the core slowly so it displaces silicone up and out the top vents.
   Keep the mold slightly **under-filled / degas the open cavity before seating the
   core** so the ~3× vacuum rise doesn't overflow and starve the part.
   Without a chamber, seat the core and pour through the port: it is
   [11 mm](FILL_D) into a [20 mm](FILL_DISH) dish, which is a pour and not a
   trickle, and the vents weep when the mould is full. What that path risks is voids
   in the deep spout — and the **bottom [12 mm](TIP_BUFFER) of that spout is
   scrap**, cut off at the shoulder, so the deepest and most void-prone part of the
   pocket is not part of the funnel. Inspect the cut face; a void above the shoulder
   is a re-pour.
4. **Clamp.** Hold the plate down with clamps or weight through the plate while it
   cures; a loosely-held plate flashes a soft fill at the rim parting line.
5. **Cure, then demold — in three pulls, every one of them straight.** BBDINO 40A
   cures at room temperature, ~5 h to demold; respect the full time before pulling
   the spout. Then, in order:
   - **The core off the rod.** Lift the plate evenly. The skirt holds the core square
     on the cavity for the first [10 mm](LIP_H); past that keep it level by hand —
     never rock it. The rod stays behind, standing in the cast.
   - **The funnel out of the cavity.** Grip the brim and lift; the scrap tip is
     drafted and breaks its own seal at once.
   - **The rod out of the funnel.** [22.0 mm](ROD_BELOW) of it stands proud below the
     ramp tip: grip that with pliers and draw it straight out. It is stock, it is
     ground round, and it is not attached to anything that could lever it.

   Wicking a little IPA into the annulus as the rod starts to move kills the
   adhesion; the blind tip's vacuum is about 3 N and is not worth designing around.
6. **Trim — the tip, then the sprue.** The part comes out of the mould with growths
   on it, and one pass with a fresh razor takes them all.
   - **The tip.** The spout casts long and closed. Lay the blade flat against the
     shoulder [1 mm](TIP_STEP) below the spout's outer face and sweep it round — the
     cut lands on the funnel's real spout length and opens a bore the rod already
     formed. Discard the [12 mm](TIP_BUFFER) below it. **The funnel is not a funnel
     until this cut is made**; `reference/funnel-drain-stub` takes the whole of that
     spout as the clamp land, so a tip left on is a spout that will not meet the
     union's collet face.
   - **The sprue and the vent pips.** The port and the vents leave columns standing
     on the brim's TOP face. That face is flat and it is its own jig: lay the blade
     on it and take them flush. It shows above the top wall, so the
     [11 mm](FILL_D) sprue scar is the one cosmetic mark the pour leaves — on black
     silicone a flush cut reads as matte against gloss and nothing more.
7. **Post-cure bake — the funnel alone, out of the mould.** For food contact, add a
   drive-off **bake of ~4 h at ~200 °C (392 °F)** (industry norm 160–200 °C, 2–6 h):
   the high-temp soak clears residual platinum + cyclic siloxanes (D4/D5/D6) and
   improves compression set so the collar holds; a filament dryer (≤110 °C) is far
   too cool. Cured BBDINO 40A is rated to **230 °C / 446 °F**, so the funnel sits
   well within its limit — **the PETG mould does not.** PETG goes soft around 80 °C
   and this bake would slump both halves, so the mould never sees the oven, which is
   why the demold above comes first. Stand the funnel **inverted** on the rack, brim
   down and spout up: the brim is a flat [173 mm](BRIM_SQ) square and carries it, where
   the right way up stands the whole part on a freshly cut spout. That is why the trim
   comes first — with the sprue and the vent pips still standing, the brim is not flat
   and the funnel bakes rocking on six little columns. One per bake — two
   abreast leaves no gap for the convection. This bake — not BBDINO's room-temp cure —
   is the food-contact acceptance gate — see
   [wetted-surface-test.md](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md).
8. **Reuse.** Reapply release every pour and inspect/clean the PETG faces between
   cycles — a reused mold accumulates cured film and bald spots.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py`
→ `funnel-mold-cavity.step`, `funnel-mold-core.step`, and an
exploded `funnel-mold-assembly.step`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py`
