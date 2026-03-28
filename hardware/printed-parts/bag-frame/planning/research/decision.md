# Bag Frame Design Decision

## Decision Context

The bag frame holds two Platypus 2L bags at 35 degrees inside a permanently sealed enclosure. The critical insight: this mechanism is assembled once during initial build, then never accessed again during normal operation. The enclosure is snapped shut permanently. Bag replacement is a rare service event (years apart, if ever). This is not a daily-access consumer interaction.

This realization eliminates the primary driver behind hinged/latched designs. The frame does not need to open, close, latch, or cycle. It needs to be assembled correctly once.

---

## Candidates Evaluated

### Candidate A: Hinged Flip Lid (3 pieces per bag)

Lower cradle + hinged lid + filament pin. Lid swings open for bag placement, latches closed with cantilever snap. This is the design from the previous concept document.

**Assembly UX:** Good. Gravity holds lid open at 35 degrees, both hands free. Drop bag in, close lid, click. Intuitive single-axis motion.

**Long-term bag behavior:** Good. Continuous lower cradle, cross-rib upper constraint at 27mm gap. Tapered entry/exit prevents kinking.

**Mechanical complexity:** Moderate. Hinge posts, sockets, filament pin, cantilever snap latch. Three pieces per bag, six total. The hinge and latch are permanent moving parts that exist inside a sealed enclosure and will never move again after initial assembly. They are over-designed for the actual use case.

**Failure modes:** The cantilever snap could theoretically creep or relax over years under the modest ~10N bag pressure. Unlikely to fail catastrophically, but it is a moving part solving a problem that does not require movement.

**Print complexity:** Low. No supports needed. ~10-12 hours total print time.

---

### Candidate B: Two-Piece Permanent Cage (2 pieces per bag)

Lower cradle + upper cap that snap together permanently around the bag. No hinge, no latch, no moving parts. The two halves join with permanent snap-fits (ratcheting barbs or through-post captures that click once and do not release).

**Assembly UX:** Excellent for the actual use case. Place bag on lower cradle. Align upper cap. Press down until snaps engage -- a firm, definitive click. Done. No fiddling with hinge pins. No threading filament. No testing whether a latch caught. The single press-to-close motion is the highest-confidence assembly interaction (Pattern F from design-patterns: registration features make alignment automatic).

The bag is limp when empty, so placement on the lower cradle is trivial -- drape it in, route the cap/tubing out the end notch, set the upper piece on top, press. This is the Keurig paradigm: drop, close, done.

**Long-term bag behavior:** Excellent. Identical constraint geometry to Candidate A (continuous lower cradle, cross-rib upper frame, 27mm gap, tapered transitions). The mechanical constraint is the same. The only difference is that the upper half is permanently fixed rather than hinged. This is strictly better for long-term reliability: no latch to relax, no hinge to develop play. The constraint gap is locked at print-time and cannot drift.

**Mechanical complexity:** Minimal. Two pieces, no moving parts, no consumables (filament pin). The permanent snap-fits are simpler than a hinge + latch because they only need to work once. A ratcheting barb (angled lead-in, vertical lock face) is the simplest snap geometry in FDM printing.

**Failure modes:** Essentially none during normal operation. The cage is a rigid, closed structure with no moving parts. The only failure mode is if the permanent snaps are not fully engaged during assembly -- mitigated by designing the snaps to produce an audible/tactile click and by making partial engagement visually obvious (gap between halves).

**Print complexity:** Lower than Candidate A. Two pieces per bag, four total. No hinge posts to get right. Same print orientations. Estimated ~8-10 hours total.

**Service (rare bag replacement):** The permanent snaps must be pried apart or cut. This is acceptable because: (1) bag replacement is expected to happen zero or one times in the product's life, (2) the cage is cheap to reprint if damaged during service, (3) this is the same paradigm as the enclosure itself (snapped shut permanently, pried apart for service). Designing the frame for easy reopening serves a use case that almost never occurs, at the expense of adding moving parts.

---

### Candidate C: Enclosure-Integrated Constraint (0 separate pieces per bag)

The bag constraint surfaces are molded directly into the enclosure interior walls. Horizontal ledges on each enclosure half form the lower cradle and upper constraint when the halves close together. The bag is placed on one enclosure half's ledges, tubing is routed, and closing the enclosure captures the bag.

**Assembly UX:** Mixed. On one hand, zero separate frame pieces to manage -- the bag goes directly onto the enclosure wall features. On the other hand, the assembly sequence becomes rigid: the bag must be placed before the enclosure closes, and the enclosure closure must not pinch, shift, or kink the bag. There is no opportunity to verify bag position and close a local frame before committing to the full enclosure closure. If the bag shifts during enclosure assembly, the entire enclosure must be re-opened.

This is the core UX problem. With a separate frame, the assembler can: (1) load bag into frame, (2) verify position and constraint, (3) close frame, (4) place closed frame into enclosure, (5) close enclosure. Steps are independent and each is verifiable. With integrated constraint, steps 1-3 are entangled with step 5. The assembler cannot verify bag position without also closing the enclosure.

**Long-term bag behavior:** Good, assuming the enclosure halves produce the correct gap geometry when closed. The constraint is as rigid as the enclosure walls.

**Mechanical complexity:** Lowest piece count (zero frame pieces). But the enclosure design becomes significantly more complex: the internal ledge geometry must account for the bag constraint profile, the enclosure halves must align precisely to produce the correct 27mm gap, and the enclosure walls in the bag zone must be thick enough to support the bag weight and pressure.

**Failure modes:** Misalignment of the two enclosure halves produces incorrect bag constraint. Unlike a self-contained frame where the gap is defined by a single print, the gap here is defined by two separate prints that must mate precisely. Any warp, tolerance stack, or assembly error in the enclosure directly affects bag behavior.

**Print complexity:** Reduces total piece count but increases enclosure complexity. The enclosure halves are already the largest, most complex prints. Adding internal constraint geometry (curved cradle surfaces, cross-ribs, tapers) makes them harder to design, harder to iterate, and harder to reprint if only the bag constraint needs adjustment.

---

### Candidate D: Slide-In Channel (2 pieces per bag)

A U-shaped lower channel and a flat upper lid that slides in from one end. The channel has internal tracks/rails; the lid slides along those rails to close. No hinge, no snap, no permanent join -- the lid is captured by the enclosure when it closes.

**Assembly UX:** Moderate. Requires sliding the lid in from one end, which is a linear motion but must be aligned with the rail. If the bag is already in the channel, the lid must slide over the bag without dragging or bunching the film. This is a riskier interaction than the top-down press of Candidate B.

**Long-term bag behavior:** Adequate. Same constraint geometry as other candidates. The lid is held in place by the enclosure walls rather than by its own snaps.

**Mechanical complexity:** Low. Two pieces with simple geometry. But the rail tolerance is critical -- too loose and the lid rattles, too tight and it binds. FDM tolerance on mating rails (typically +/- 0.2mm) makes this interaction less predictable than a snap.

**Failure modes:** Lid could shift within its rails during the enclosure closure step if not fully seated. The enclosure must positively capture the lid.

**Print complexity:** Low. Similar to Candidate B.

---

## Ranking

| Criterion | Weight | A: Hinged Lid | B: Permanent Cage | C: Enclosure-Integrated | D: Slide-In |
|-----------|--------|--------------|-------------------|------------------------|-------------|
| Assembly UX (primary UX) | 1st | Good | Excellent | Poor | Moderate |
| Long-term bag behavior (daily UX) | 1st | Good | Excellent | Good | Adequate |
| Mechanical feasibility | 2nd | Proven | Proven | Feasible but coupled | Feasible |
| Simplicity (print + assemble) | 3rd | Moderate | Simple | Complex (enclosure coupling) | Simple |
| Durability adequacy | 4th | Good | Excellent | Good | Adequate |

**Assembly UX detail:**
- B wins because the interaction is: place bag, place upper half, press until click. One decisive motion confirms completion. No hinge pin to thread, no latch to verify, no sliding to align.
- A is good but has unnecessary assembly steps (thread filament pin, verify latch catch).
- C fails because bag position cannot be verified independently of enclosure closure.
- D is adequate but the slide-over-bag interaction risks film bunching.

**Long-term bag behavior detail:**
- B wins because the constraint gap is permanently fixed at print-time with no moving parts that could relax or develop play.
- A is nearly identical but the hinge and latch are theoretically capable of developing play over years.
- C and D are adequate but the constraint depends on external assemblies (enclosure alignment, rail capture) rather than a self-contained structure.

---

## Recommendation: Candidate B -- Two-Piece Permanent Cage

A lower cradle and an upper cap that snap together permanently around the Platypus 2L bag. No hinge, no latch, no pins, no moving parts. The two halves are pressed together once during assembly and never separated again.

### Design Specifics

**Lower cradle:**
- 250 x 180 x 20 mm footprint
- Continuous smooth concave floor (~3mm sag across 180mm width)
- 8mm side rails along both long edges
- Cap-end wall with notch for tubing pass-through (prevents 11N sliding force from pushing bag downhill)
- Entry/exit tapers: gap widens from 27mm to 45mm over the last 40mm at each end
- 0.4mm-pitch longitudinal anti-adhesion ribs on bag-contact surfaces
- 3mm minimum radius on all bag-contact edges
- 4 snap-fit receptacles (vertical holes or C-shaped sockets) positioned along the side rails, two per side

**Upper cap:**
- 250 x 180 x 15 mm footprint
- Open frame with 4 cross-ribs spanning 180mm width, spaced 50mm apart
- Each rib: 3mm wide x 12mm tall, gently curved underside matching upper half of 27mm gap
- Perimeter rail connecting the ribs
- 0.4mm-pitch transverse anti-adhesion texture on rib undersurfaces
- 3mm minimum radius on all bag-contact edges
- 4 ratcheting barb posts extending downward from the perimeter rail, mating with the cradle receptacles

**Snap-fit detail:**
- Ratcheting barb geometry: angled lead-in (30-degree ramp) for easy insertion, vertical lock face for permanent retention
- Barb engagement: 1.0mm (sufficient for permanent hold in PETG, impossible to accidentally disengage)
- Post diameter: 4mm; receptacle ID: 4.2mm (0.2mm clearance for FDM tolerance)
- Designed to produce a tactile and audible click at full engagement
- Partial engagement is visually obvious: a 1-2mm gap between cradle rail and cap rail indicates incomplete closure

**Constraint zone:**
- Center gap: 27mm (midpoint of 25-30mm target)
- Constraint zone length: 200-250mm centered on bag midsection
- Constraint zone width: 170-180mm (narrower than 190mm bag width, heat-sealed edges overhang freely)
- Side edge gap: 5mm minimum to avoid pinching perimeter seals

**Mounting to enclosure:** Identical to the concept document's approach. The enclosure interior has horizontal ledges. The cradle has downward-facing tabs that drop into ledge slots. Gravity-seated, captured when enclosure halves close. The bag frame is a self-contained module that is assembled and verified before going into the enclosure.

### Assembly Sequence

1. Lay lower cradle on work surface
2. Drape empty Platypus bag onto cradle, cap hanging off the downhill end through the notch
3. Fill bag partially (~500mL) to give it enough body to sit correctly in the cradle (optional but recommended -- gives visual confirmation of position)
4. Place upper cap onto cradle, aligning the 4 snap posts with receptacles
5. Press down firmly until all 4 snaps click -- the bag is now permanently caged
6. Verify: no visible gap between cradle rail and cap rail at any of the 4 snap points
7. Repeat for second bag
8. Mount both caged bags onto enclosure half ledges
9. Route tubing
10. Close enclosure

### BOM (per bag frame -- multiply by 2 for complete machine)

| Part | Qty | Source | Notes |
|------|-----|--------|-------|
| Lower cradle (PETG print) | 1 | Printed | ~250 x 180 x 20 mm, ~3-4 hr print |
| Upper cap (PETG print) | 1 | Printed | ~250 x 180 x 15 mm, ~1.5-2 hr print |

**Total for both bags: 4 printed parts. No purchased hardware. No consumables.**

### Print Specifications

| Parameter | Value |
|-----------|-------|
| Material | PETG |
| Layer height | 0.2mm |
| Nozzle | 0.4mm |
| Infill | 20-30% (structural, not visible) |
| Supports | None required |
| Cradle orientation | Flat, concave face up (bag-contact surface is top/smoothest layer) |
| Cap orientation | Flat, ribs pointing up (ribs print vertically for strength) |
| Estimated total print time | ~8-10 hours for all 4 pieces |

---

## What Would Change This Recommendation

1. **If bag replacement became a routine operation** (e.g., bags wear out every 6 months instead of lasting years): The permanent cage becomes a liability because it must be destroyed and reprinted for each replacement. In that case, Candidate A (hinged flip lid) would be the right choice. The threshold is roughly: if bag replacement happens more than once per year, switch to a hinged design.

2. **If the bags were pre-filled at the factory** (user receives a sealed machine with bags already installed): The frame would never need to be assembled by a human at all. In that case, Candidate C (enclosure-integrated) becomes viable because the manufacturer controls alignment precision and can verify bag position on an assembly line.

3. **If the constraint gap needed to be adjustable** (e.g., different bag brands with different thicknesses): A permanent cage locks the gap at print-time. An adjustable design (threaded spacers, shim plates) would be needed. This does not currently apply -- the Platypus 2L is the specified bag.

4. **If the enclosure interior geometry changed** so that the bag frame could not be assembled as a module outside the enclosure (e.g., the bag zone is only accessible from inside): The modular pre-assembly advantage of Candidates A and B is lost, and the slide-in approach (D) or enclosure-integrated approach (C) would need reconsideration.
