# Bag Frame Design Decision

## Candidates Evaluated

Five frame architectures were considered for constraining each Platypus 2L bag at 35 degrees inside the 220x300x400mm enclosure.

### Candidate 1: Hinged Clamshell

Two lens-profiled halves connected by a living hinge along one long edge. The user opens the clamshell like a book, lays the bag in the lower half, and closes it. Snap latches along the opposite long edge hold it shut. The assembled clamshell mounts to the enclosure via snap rails on the enclosure interior walls.

**Hand motion:** One hand holds the clamshell open, the other lays the bag flat, then press closed. Single-axis closing motion.

**Design pattern alignment:** Strong. The clamshell hides the bag completely once closed (Pattern B -- compression between two surfaces). The closing action is a single-axis motion (Key Observation 5). The rigid shell becomes the object the user handles (Pattern A -- rigid shell as shape proxy). The snap closure provides tactile confirmation (breast pump adapter pattern).

**Mechanical feasibility:** The living hinge must survive repeated open/close cycles. In PETG, a living hinge with 0.3-0.4mm thickness at the fold survives hundreds of cycles. The hinge runs along the 250mm constraint zone length -- printable on the Bambu H2C without issue. The clamshell halves are each approximately 190mm wide x 250mm long x 15mm deep -- well within print volume.

**Simplicity:** Two parts if the hinge is integral (printed-in-place). Three parts if the hinge is a separate pin/rod. Snap latches are integral to the print. No purchased hardware.

**Drawback:** The hinge axis must be accessible to the user, which constrains enclosure mounting orientation. If the clamshell is mounted flush against a wall on its hinge side, the user cannot open it. Requires clearance on the hinge side equal to the full width of the open lid.

### Candidate 2: Tray + Separate Lid

A lower cradle (tray) that the bag sits in, plus a separate upper constraint (lid) that drops on top and locks down with snap tabs. The tray has integrated rails or posts that guide the lid into alignment. The tray mounts to the enclosure; the lid is a loose piece the user handles.

**Hand motion:** Pull lid off (lift straight up), lay bag in tray, place lid back on (drop straight down), press until snaps engage.

**Design pattern alignment:** Moderate. The drop-in motion matches Boxxle (open, drop, close) and Keurig (drop pod into cradle). But the loose lid is a separate piece the user must store or hold -- it is not attached to the tray. This is the "cardboard box" level of integration (Pattern A without the product unity of Keurig). The two pieces do not feel like a single mechanism.

**Mechanical feasibility:** Straightforward. The tray and lid are simple flat-ish shapes with snap features. No hinges, no moving parts. The snap tabs must be robust enough to resist the bag's internal pressure pushing the lid upward (~10N distributed).

**Simplicity:** Two completely separate prints. Both are flat and easy to print. Snap alignment posts/tabs are standard FDM features.

**Drawback:** The loose lid is a UX liability. Where does the user put it while handling the bag? It will be set on the counter, dropped, or lost. Every bag change requires two hands: one for the lid, one for the bag. It does not feel like a single product -- it feels like parts.

### Candidate 3: Slide-In Tray with Captive Lid

A lower cradle permanently mounted in the enclosure, plus an upper constraint lid that is captive -- it slides along rails integrated into the cradle or enclosure walls. The lid cannot be fully removed; it slides open (toward the user) to expose the bag, and slides closed to constrain it. A detent or snap at the closed position locks it.

**Hand motion:** Slide the lid toward you (one hand, one finger), lay the bag in with the other hand, slide the lid back until it clicks shut.

**Design pattern alignment:** Strong. The slide-open/slide-closed motion is a single-axis interaction. The lid is captive, so there is no loose piece. The closed state hides the bag completely. The click at the closed position provides tactile confirmation. This is closest to Pattern C (rigid backer with shaped sleeve) -- the lid slides along a defined path like a drawer. The enclosure interior becomes the "product surface" and the slide mechanism is integrated into it.

**Mechanical feasibility:** The slide rails must be precise enough for smooth travel but loose enough to not bind with thermal expansion or print tolerance. Rail length is approximately 250mm. PLA/PETG rail-in-groove tolerances of 0.3-0.4mm clearance are well-established for FDM. The rails could be on the enclosure interior walls (integral to the enclosure halves) rather than on the cradle itself, distributing the alignment function across parts that are already being printed.

**Simplicity:** Two printed parts (cradle + sliding lid), but the rails add geometric complexity to either the cradle or the enclosure walls. The rail geometry must be designed into the enclosure halves, coupling the bag frame design to the enclosure design.

**Drawback:** Slide travel distance must be long enough to fully expose the bag for insertion/removal. At 35 degrees inside a 220mm-wide enclosure, the available slide distance may be limited by the enclosure walls. If the lid cannot slide far enough, the user is reaching into a partially-covered slot to place the bag -- poor UX.

### Candidate 4: Fixed Lower Cradle + Hinged Upper (Top-Hinged Flip Lid)

A lower cradle permanently mounted in the enclosure. An upper constraint plate hinged at the uphill (sealed) end of the bag, so it flips open toward the front/top of the enclosure. The hinge is at the high end; the latch is at the low (cap) end. The user flips the lid up, lays the bag in, and flips it down until the latch engages.

**Hand motion:** Flip lid up (one finger, it stays open by gravity since the hinge is at the high end of the 35-degree tilt), lay bag in with both hands free, flip lid down, press latch at the bottom edge.

**Design pattern alignment:** Very strong. This is the Boxxle pattern (open lid, drop in, close lid) adapted to a tilted geometry. The hinge at the uphill end means the lid naturally stays open during bag placement -- gravity holds it. The user never holds the lid while placing the bag. Both hands are free for bag handling. The latch at the low end is at the front of the enclosure (most accessible point). The closed state fully constrains the bag. The lid is captive (hinged, cannot be lost). The interaction reads as: flip, place, close -- three steps, all single-axis, all one-handed except placing the bag.

**Mechanical feasibility:** The hinge can be a pin-in-socket (two printed posts on the cradle + holes in the lid, with a printed or wire pin). At 35 degrees, the lid's center of gravity is behind the hinge when open, so it stays propped open without a detent. The latch at the low end can be a cantilever snap. The lid is approximately 180mm wide x 200-250mm long -- a flat plate with cross-ribs. The cradle is a continuous surface with side rails and a cap-end stop.

The hinge must be accessible inside the enclosure. Since the hinge is at the uphill (sealed) end of the bag, which faces the front/top of the enclosure per the vision, the hinge is near the front panel. The lid opens toward the user, which is the natural direction.

**Simplicity:** Two printed parts (cradle + lid) plus a hinge pin (could be a short length of 1.75mm filament or a printed pin). The cradle mounts to enclosure snap points. The hinge geometry is simple: two posts with holes.

**Drawback:** The hinge adds a failure point. If the pin breaks, the lid becomes a loose piece (falls back to Candidate 2). The hinge posts must be robust enough for repeated use. PETG pin-in-socket joints at this scale (3-4mm pin diameter) are durable but not indestructible.

### Candidate 5: Integrated Cage (Single Print)

A single-piece cage with an opening large enough to slide the bag in from one end. The cage is a skeleton: two lens-profiled rings connected by longitudinal ribs, with one end open for bag insertion. The bag slides in lengthwise through the open end.

**Hand motion:** Thread the bag into the cage lengthwise, cap-end first, pushing it through until the cap protrudes from the far end.

**Design pattern alignment:** Weak. Threading a floppy filled bag through a cage is the worst-case interaction -- the user is "stuffing a floppy bag into a hole" (Key Observation 3). There is no datum surface guiding insertion. The motion is not single-axis in practice because the bag must be wiggled and coaxed through the opening. No tactile confirmation of correct seating.

**Mechanical feasibility:** The cage must have an opening larger than the bag's filled cross-section (~190mm x 30mm lenticular). Longitudinal ribs connecting the rings must span 200-250mm without sagging. Printable but structurally marginal for thin ribs.

**Simplicity:** Single print, no assembly. But the geometry is complex (skeletal frame with tight tolerances on the internal profile).

**Drawback:** The insertion experience is fundamentally poor. A filled 2L bag weighing 2kg, flexible and slippery, does not thread through a skeleton cage gracefully. This approach fails the primary design criterion.

---

## UX Ranking

| Rank | Candidate | Key UX Strengths | Key UX Weaknesses |
|------|-----------|-------------------|---------------------|
| 1 | **4: Fixed Cradle + Hinged Flip Lid** | Both hands free for bag placement; lid stays open via gravity; one-finger open/close; captive lid; latch at front (most accessible); Boxxle-level interaction | Hinge is a mechanical dependency |
| 2 | 1: Hinged Clamshell | Single-axis open/close; bag fully hidden; tactile snap | One hand occupied holding it open; requires clearance on hinge side; entire assembly removed from enclosure for bag change |
| 3 | 3: Slide-In Tray + Captive Lid | Captive lid; single-axis slide; click confirmation | May not slide far enough to fully expose bag; reaching into slot |
| 4 | 2: Tray + Separate Lid | Simple drop-in motion | Loose lid (lost, dropped, requires two-hand coordination) |
| 5 | 5: Integrated Cage | Single piece, no assembly | Threading a filled bag through a skeleton; no tactile confirmation; worst insertion experience |

---

## Recommendation: Candidate 4 -- Fixed Lower Cradle + Top-Hinged Flip Lid

### Why This Wins

The top-hinged flip lid at 35 degrees is the only candidate where gravity works in favor of the UX. When the user flips the lid up, it stays open on its own -- the 35-degree tilt means the lid's weight holds it past vertical against the hinge. Both hands are free to place the bag. This is a meaningful advantage over every other candidate, where at least one hand is occupied holding something open or managing a loose piece.

The interaction sequence:

1. **Flip lid up** (one finger on the latch at the front/bottom of the enclosure). The lid swings open and stays open.
2. **Lay bag in cradle** (both hands). The cradle's side rails and cap-end stop guide placement. The bag drops into a lens-profiled trough -- self-aligning, like a Keurig pod dropping into its holder (Pattern F).
3. **Flip lid down** (one hand). It swings closed under its own weight once past the balance point.
4. **Press latch** (one finger, same spot as step 1). Click. Done.

This matches the Boxxle pattern (open, drop, close) and adds the gravity-assisted lid hold that Boxxle achieves with a spring but which the 35-degree angle provides for free.

### Against the Design Patterns

| Pattern | Alignment |
|---------|-----------|
| A: Rigid shell as shape proxy | Yes. The cradle + lid form a rigid shell that defines the bag's shape. The user handles rigid surfaces, not the bag. |
| B: Compression between two surfaces | Yes. The bag is sandwiched between the cradle (below) and the lid (above). The constraint is passive -- no springs or actuators needed because the bag's internal pressure is modest. |
| C: Rigid backer with shaped sleeve | Partial. The cradle acts as the rigid datum surface. The lid is not a sleeve but provides the same function (predictable insertion path). |
| E: Gravity angle + atmospheric collapse | Yes. The 35-degree mount is integral. Cap-down orientation drains toward the outlet. |
| F: Registration at transfer point | Yes. The cap protrudes through the downhill end of the cradle, aligning with the tubing connection below. |
| Key Observation 1 (hide the bag) | Yes. Lid closed = bag invisible. |
| Key Observation 3 (rigid datum) | Yes. The cradle is the datum surface. |
| Key Observation 5 (single-axis motion) | Yes. Flip up, drop in, flip down. All single-axis. |
| Key Observation 6 (continuous compression) | Partial. The lid maintains constraint at full and partial fill. At low fill, the upper portion of the bag collapses away from the lid, but the lower portion remains constrained. This is acceptable because the 35-degree angle concentrates liquid at the cap end where constraint matters most. |

### Product-Surface Integration

The cradle mounts to snap points on the enclosure interior walls. The hinge posts are part of the cradle. The lid is part of the bag frame assembly, not a separate enclosure feature. The latch at the front edge can be designed to sit flush with the enclosure front panel opening -- so the latch click-point is a small, deliberate feature on the product's exterior surface, not an afterthought.

This is product-surface integration: the user touches a latch on the enclosure surface and the internal mechanism responds. The bag, cradle, hinge, and lid are all invisible behind the enclosure panel.

### Detailed Component Design

**Lower cradle:**
- Continuous smooth surface, gently concave (lens-profile matching half of a 27mm-gap lenticular cross-section)
- Width: 180mm (narrower than the 190mm bag to avoid pinching the heat-sealed edges)
- Length: 250mm (midsection constraint zone, leaving 50mm unconstrained at each end)
- Side rails: 8mm tall along both long edges, preventing lateral shift
- Cap-end stop: a lip or wall at the downhill end, with a notch for the cap/tubing to pass through
- Sealed-end taper: over the last 40mm, the side rails flare outward and the cradle floor ramps down, creating a gradual transition from constrained to unconstrained
- Cap-end taper: similar 40mm ramp at the downhill end
- Surface texture: 0.4mm-pitch longitudinal ribs (parallel to the bag's long axis) to prevent PE film adhesion
- Hinge posts: two cylindrical posts (4mm OD, 6mm tall) at the uphill (sealed) end, spaced 160mm apart
- Enclosure mounting: snap tabs on the underside of the cradle engage rails or posts on the enclosure interior walls
- Edge radii: 3mm minimum on all edges contacting the bag

**Flip lid (upper constraint):**
- Open frame with 4 cross-ribs spanning the 180mm width, spaced 50mm apart along the 250mm length
- Each cross-rib: 3mm wide x 12mm tall, with the bag-contact edge gently curved (matching the upper half of the 27mm lenticular profile)
- Perimeter rail connects the cross-ribs into a rigid frame
- Hinge sockets: two holes (4.2mm ID) at the uphill end, mating with the cradle's hinge posts
- Latch tab: a cantilever snap at the downhill end, engaging a catch on the cradle's cap-end wall
- Bag-contact surfaces on cross-ribs: 0.4mm-pitch transverse ribs (perpendicular to bag long axis) to prevent adhesion
- Edge radii: 3mm minimum on all cross-rib edges contacting the bag

**Hinge pin:**
- 1.75mm filament segment or a printed PETG pin, 170mm long, threaded through the hinge post holes and lid socket holes
- Retained by friction fit or small printed caps on each end
- Alternative: print the hinge as a pin-in-socket with 0.3mm clearance -- the pin is integral to the lid, the socket is integral to the cradle. This eliminates the loose pin but requires more careful print orientation.

**Constraint gap geometry:**
- Center gap between cradle floor and lid cross-rib undersurface: 27mm
- Side gap at 180mm width edges: 5mm minimum (the side rails are shorter than the cross-ribs)
- Entry taper (both ends): gap widens from 27mm to 45mm over 40mm of length
- The cap-end notch in the cradle allows the bag cap to protrude downhill and below the cradle floor, connecting to tubing underneath

### Bill of Materials

| Part | Qty | Material | Approx Print Mass | Notes |
|------|-----|----------|-------------------|-------|
| Lower cradle | 2 | PETG | ~80g each | One per bag. Prints flat, no supports needed. |
| Flip lid | 2 | PETG | ~35g each | One per bag. Open-frame design, minimal material. |
| Hinge pin | 2 | PETG filament or printed | <1g each | 170mm length of 1.75mm filament, or printed-in-place. |
| **Total per bag** | **3 parts** | | **~116g** | |
| **Total for 2 bags** | **6 parts** | | **~232g** | |

No purchased components. No screws, no springs, no metal hardware. All PETG, all snap-fit or press-fit.

### What Would Change This Recommendation

1. **If the enclosure interior cannot provide clearance for the lid to flip open.** The lid, when open, sweeps an arc approximately 250mm long. At 35 degrees, the uphill end of the lid rises about 200mm above the cradle. If the enclosure ceiling or the bag above prevents this, the lid cannot open fully. Mitigation: the lid could be split into two shorter halves, each with its own hinge, reducing the sweep arc. This adds parts but preserves the interaction model.

2. **If the bags need to be removed frequently (daily or more).** The flip-lid-and-lay-in interaction is optimized for monthly or weekly bag changes. If bags are swapped daily, a slide-in mechanism (Candidate 3) might be faster despite its UX compromises, because it does not require reaching into the enclosure cavity.

3. **If the hinge proves unreliable in testing.** If the pin-in-socket hinge breaks or binds after repeated use, the fallback is Candidate 1 (clamshell with living hinge). A PETG living hinge at 0.3mm is more durable in flex cycles than a pin joint, though it requires the entire assembly to be removable from the enclosure for bag changes.

4. **If the Platypus bag is replaced with a gusseted or box-shaped bag.** The lens-profiled cradle and cross-rib lid are optimized for the Platypus's lenticular cross-section. A bag with flat faces and gusseted sides (like a BIB bladder) would need flat constraint surfaces instead of curved ones. The frame architecture (hinged lid, fixed cradle) would remain the same; only the surface profiles would change.

5. **If active compression is needed for complete drainage.** The current design is passive -- the bag drains by gravity at 35 degrees, and atmospheric collapse helps. If testing reveals that the bag retains significant liquid in internal folds, a spring-loaded element in the lid (pressing the bag toward the cradle as it empties) would improve drainage. This would add a compression spring and change the lid from an open frame to a more solid platen. The Boxxle pattern explicitly solves this with a spring platform.
