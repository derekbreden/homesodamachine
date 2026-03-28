# Bag Frame -- Conceptual Architecture

## Critical Realization: Access Frequency

The vision states the enclosure is "snapped together permanently" and "the user never opens the enclosure." The requirements state bags are "permanent fixture the same as all other internal plumbing." This means the bag frame is assembled once during initial build, then sealed inside the enclosure for the product's lifetime. The flip lid is an assembly and service mechanism, not a daily consumer interaction. This fundamentally shapes every design choice below.

The hinge concept from the decision document remains correct -- it makes initial assembly clean (gravity holds lid open, both hands free for bag placement) and preserves serviceability if a bag ever needs replacement. But the mechanism does not need to survive thousands of cycles, be accessible from the enclosure exterior, or feel like a consumer touchpoint.

---

## 1. Piece Count and Split Strategy

**3 pieces per bag frame, 6 total for both bags.**

| Piece | Function | Approximate Size |
|-------|----------|-----------------|
| Lower cradle | Supports bag weight, mounts to enclosure walls, provides hinge posts | 250 x 180 x 20 mm |
| Flip lid | Upper constraint (cross-rib frame), hinge sockets, latch tab | 250 x 180 x 15 mm |
| Hinge pin | Connects lid to cradle | 170 mm x 1.75 mm dia (filament segment) |

**Why not fewer pieces?** The cradle and lid must be separate to allow bag insertion -- a single cage with an end-opening was rejected in the decision (poor insertion UX). The hinge pin could be eliminated with a snap-in knuckle hinge (integral cylinders on the lid that snap into C-shaped sockets on the cradle), but a filament pin is simpler, more reliable, and trivial to replace.

**Why not more pieces?** There is no reason to split the cradle or lid. Both fit the Bambu H2C print bed (325 x 320 mm) with generous margin. The cradle prints flat, face-down. The lid prints flat, ribs-up.

**Mounting to the enclosure:** The cradle does not snap to the enclosure walls directly. Instead, the enclosure interior has two pairs of horizontal ledges (molded into each enclosure half) that the cradle rests on. The ledges define the 35-degree angle and the vertical stacking position. The cradle has downward-facing tabs that drop into slots on the ledges, preventing lateral and longitudinal shift. This is not a snap-fit -- it is a gravity-seated registration. The enclosure halves, when joined, capture the cradles from both sides.

**Why gravity-seated instead of snap-fit?** Because the enclosure halves are assembled around the cradles. The assembly sequence is: (1) install cradles with bags onto one enclosure half, (2) close the other half over. Snap-fits on the enclosure interior would require reaching inside to engage them, which is awkward. Gravity-seated registration with capture-on-close is the right pattern for a clam-shell enclosure.

---

## 2. Join Methods

| Joint | Method | Rationale |
|-------|--------|-----------|
| Lid to cradle | Filament hinge pin through post-and-socket | Simple, replaceable, low cycle count needed |
| Lid closed position | Cantilever snap latch at cap (downhill) end | Tactile click confirms closure; one-finger release |
| Cradle to enclosure | Gravity-seated tabs in ledge slots, captured by enclosure closure | No reaching inside; assembly-friendly |
| Upper cradle to lower cradle | No direct connection; both independently seated on enclosure ledges | Stacking is defined by the enclosure geometry, not by the frames themselves |

**Hinge detail:** Two cylindrical posts (4 mm OD, 6 mm tall) on the cradle's uphill end, spaced 160 mm apart. The lid has matching holes (4.2 mm ID). A 170 mm length of 1.75 mm PETG filament threads through all four features. The filament is retained by friction or small printed end-caps. At 35 degrees, the open lid's center of gravity falls behind the hinge axis, so the lid stays open without a detent.

**Latch detail:** A single cantilever tab on the lid's downhill edge hooks under a catch on the cradle's cap-end wall. The tab is 3 mm wide, 15 mm long, with 0.8 mm of engagement. Deflection to release: ~2 mm. This is a standard FDM cantilever snap -- printable in PETG without issue. One latch is sufficient because the bag's internal pressure is modest (~10 N total upward force, distributed) and the lid's own weight at 35 degrees biases it toward closed.

---

## 3. Seam Placement

The bag frame has two seams: the hinge line and the latch line. Both are internal to the enclosure and invisible to the user.

- **Hinge seam** runs across the uphill (front/top) end of the frame. It is the visual boundary between the cradle and the lid when closed. Since the frame is inside a sealed enclosure, seam treatment is purely functional -- no aesthetic gap control needed. A 0.5 mm gap at the hinge line is acceptable.
- **Latch seam** is at the downhill (back/bottom) end. The lid's edge sits on top of the cradle's cap-end wall with the snap tab below. Gap: 0-0.5 mm when latched.
- **Side seams** between the lid perimeter rail and the cradle side rails. These are open gaps (~2 mm) that allow the bag's heat-sealed edges to protrude slightly without pinching. This is functional, not a cosmetic seam.

**No user-visible seams.** The bag frame is entirely enclosed. The only enclosure seams the user sees are on the outer shell, which is a separate design problem.

---

## 4. User-Facing Surface Composition

The bag frame has no user-facing surfaces. It is permanently enclosed.

The surfaces that matter are **bag-facing**: the cradle floor and the lid cross-ribs that contact the Platypus film.

- **Cradle floor:** Continuous smooth surface with 0.4 mm-pitch longitudinal ribs (parallel to bag long axis). The ribs prevent PE film adhesion to PETG. The surface is gently concave -- not a precise lens-profile arc, but a shallow dish (~3 mm of sag across 180 mm width) that guides the bag toward center. All edges contacting the bag have 3 mm minimum radius.
- **Lid cross-ribs:** 4 ribs spanning the 180 mm width, spaced 50 mm apart. Each rib is 3 mm wide x 12 mm tall with a gently curved underside matching the upper half of the 27 mm constraint gap. Rib undersurfaces have 0.4 mm-pitch transverse texture (perpendicular to bag axis) to prevent adhesion. 3 mm edge radii.
- **Cradle side rails:** 8 mm tall along both long edges. They prevent lateral bag shift but do not compress the bag -- the bag's heat-sealed perimeter overhangs the rails freely.
- **Cap-end wall:** A lip at the downhill end with a notch for the cap/tubing to pass through. Prevents the bag from sliding down the 35-degree incline (resists the 11 N sliding force).
- **Entry/exit tapers:** Over the last 40 mm at each end of the constraint zone, the gap widens from 27 mm to 45 mm via gentle ramps on both cradle and lid. This prevents kinking at the constraint boundary.

---

## 5. Design Language

**Internal-functional, not consumer-aesthetic.** Since the bag frame is never seen or touched by the user, it does not need the surface finish, corner radii, or visual polish of the enclosure exterior. It needs to be mechanically correct.

- **Material:** PETG. Chosen for chemical resistance (contact with food-grade syrup residue on bag exterior), temperature stability (under-sink environment), and hinge/snap durability. Not PLA (too brittle for snap features over time). Not ABS (unnecessary and harder to print).
- **Surface finish:** Standard FDM layer lines are acceptable on all surfaces. Bag-contact surfaces get the anti-adhesion rib texture described above. No sanding, painting, or post-processing.
- **Corner treatment:** 3 mm radii on all edges that contact the bag (safety/film protection). Other edges can be sharp or lightly chamfered (0.5 mm) for print quality -- no aesthetic requirement.
- **Color:** Any. It is invisible. Recommend natural/translucent PETG so that during assembly, the bag's fill level and position are visible through the frame. This is a build-verification aid, not an aesthetic choice.
- **Visual distinction from enclosure parts:** None needed. The bag frame is a utilitarian internal structure. It should look like what it is -- a functional cradle.

---

## 6. Service Access Strategy

**Tier 1 -- Never (normal operation):** The bag frame is sealed inside the enclosure. No access needed. Filling is via the funnel. Cleaning is automated. Dispensing is via tubing. The user never interacts with the bag frame.

**Tier 2 -- Rare (bag replacement due to failure):** If a Platypus bag develops a leak or needs replacement after years of use, the enclosure must be opened. The enclosure halves are snapped together permanently per the vision, so this is a destructive-ish operation (prying apart snap tabs). Once open, the bag frame's flip lid unlatches and hinges open, the old bag is removed, the new bag is placed, the lid is closed. The hinge and latch are designed to survive this -- they are not single-use.

**Tier 3 -- Assembly (initial build):** The bag frame is assembled and loaded with bags before the enclosure is closed. Sequence:
1. Mount cradles (with bags and closed lids) onto one enclosure half's internal ledges.
2. Route tubing from bag caps to valves/pumps.
3. Close the second enclosure half, capturing the cradles.

The gravity-seated mounting means the cradles simply drop into position. No tools, no snap engagement to fumble with inside a half-closed enclosure.

---

## 7. Manufacturing Constraints

| Constraint | Value | Source |
|------------|-------|--------|
| Print bed (single nozzle) | 325 x 320 x 320 mm | requirements.md |
| Cradle footprint | 250 x 180 mm | Fits bed with 75+ mm margin each axis |
| Lid footprint | 250 x 180 mm | Same |
| Print orientation -- cradle | Flat, concave face up | No supports needed; bag-contact surface is top layer (smoothest) |
| Print orientation -- lid | Flat, ribs pointing up | Ribs print vertically (strong layer orientation); no supports |
| Layer height | 0.2 mm | Standard for structural parts; 0.1 mm unnecessary for non-visible parts |
| Material | PETG | Chemical resistance + snap durability |
| Hinge pin | 1.75 mm PETG filament, cut to 170 mm | Zero print time; uses waste filament |
| Wall thickness minimum | 1.5 mm | Standard FDM minimum for PETG |
| Snap tab minimum width | 3 mm | Ensures adequate flex life in PETG |
| Anti-adhesion ribs | 0.4 mm pitch, 0.2 mm tall | Achievable at 0.2 mm layer height with 0.4 mm nozzle |

**No supports required for any piece.** The cradle is a shallow dish -- prints flat. The lid is an open frame with vertical ribs -- prints flat with ribs pointing up. Both are straightforward single-material PETG prints.

**No multi-material printing needed.** Both pieces are uniform PETG.

**Print time estimate:** Cradle ~3-4 hours, lid ~1.5-2 hours at 0.2 mm layers. Total for all 6 parts (2 cradles + 2 lids): ~10-12 hours, excluding hinge pins (not printed).

---

## Concept Summary

Two identical bag frames, each consisting of a lower cradle and a hinged flip lid, gravity-seated on ledges molded into the enclosure interior. The frames are assembled with bags during initial build, then sealed inside the permanently-closed enclosure. The user never sees or touches them.

The cradle provides a smooth, textured, gently concave surface that supports the bag and prevents lateral/longitudinal shift. The lid provides cross-rib constraint that limits midsection thickness to 27 mm. The hinge at the uphill end uses a filament pin and allows the lid to stay open via gravity during assembly. A single cantilever snap at the downhill end latches the lid closed.

No purchased hardware. No tools. No post-processing. Six PETG prints and two filament offcuts per machine, assembled by hand in under five minutes.
