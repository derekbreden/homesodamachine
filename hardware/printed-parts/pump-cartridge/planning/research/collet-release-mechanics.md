# Collet Release Mechanics — Technical Research

## 1. Collet Release Force and Travel

### How John Guest Collet Release Works

The John Guest PP0408W union has a stainless steel gripper ring (teeth) inside each end that bites into the tube OD when the tube is pulled. The collet (release sleeve) is the white acetal ring visible at each end face. Pushing the collet **inward toward the fitting body center** compresses the gripper teeth radially outward, disengaging them from the tube surface. With the collet held depressed, the tube slides out freely.

This confirms: **pushing the collet toward the fitting body center = release direction.** The release plate in our design moves toward the fittings (toward the user-facing end of the cartridge) and pushes on the dock-facing collets inward.

### Travel Distance

From caliper-verified measurements:
- Collet travel per side: **~1.3 mm** (derived: (41.80 - 39.13) / 2 = 1.335 mm)
- This is the stroke from the collet's default extended position to fully compressed (flush with the body end face)
- Full release likely occurs before maximum compression — a conservative design target is **1.5 mm plate travel** to ensure full engagement with tolerance margin

### Release Force per Collet — Estimated

No manufacturer publishes collet release force for 1/4" John Guest fittings. The following estimation is based on:
- The collet can be depressed by a single fingertip (widely reported by users and in JG's own instructions)
- The PI-TOOL (a small plastic hand tool) is described as making release "easier" but is explicitly not required
- The stainless steel gripper ring is a thin stamped spring element, not a heavy compression spring
- Comparable pneumatic push-in fittings (same mechanism, same size range) are routinely operated by finger pressure

**Estimated release force per collet: 5-15 N (1-3.5 lbf)**

This is based on:
- A fingertip comfortable push force is approximately 5-15 N
- The collet mechanism is specifically designed for tool-free hand operation
- The spring element is a thin stainless steel stamped ring providing just enough grip force to resist tube pullout under rated pressure (150 psi), but designed to yield easily to axial finger pressure on the collet sleeve
- The force is primarily overcoming the spring steel's resistance to radial deflection over a very short travel (1.3 mm)

**For 4 collets simultaneously: 20-60 N (4.5-13.5 lbf) total**

### Failure Modes
- **Misalignment**: If the plate contacts only part of the collet face, localized force could cock the collet rather than depress it evenly. Mitigation: the stepped bore design (inner lip hugging the 9.57 mm collet OD) provides lateral constraint.
- **Incomplete release**: If plate travel is insufficient, the gripper teeth may partially disengage but still snag. Mitigation: design for 1.5 mm travel minimum; the geometry document confirms we have margin.
- **Over-travel**: Pushing beyond 1.3 mm could stress internal components. Mitigation: hard stop built into the cartridge frame limits plate travel to ~1.5 mm.

---

## 2. Release Plate Geometry

### Spatial Layout Recap

The release plate sits between the back wall (dock side) and the fittings. Tubes from the dock pass through clearance holes in the back wall, through clearance holes in the release plate, and into the dock-facing ports of the John Guest fittings. The plate engages the dock-facing collets.

### Stepped Bore Design (per fitting)

Each of the 4 fitting positions on the release plate requires a stepped bore with three concentric diameters:

1. **Tube clearance hole (through-bore):** 6.5 mm diameter
   - Must be larger than tube OD (6.30 mm measured, 6.35 mm nominal) for the tube to pass freely
   - Must be smaller than collet ID (6.69 mm) so the annular face around the bore contacts the collet end face
   - Design window is only 0.39 mm (6.30 to 6.69 mm); a 6.5 mm bore gives 0.1 mm clearance to tube and 0.19 mm engagement lip per side — tight but printable
   - **This annular contact face is what actually pushes the collet inward**

2. **Collet engagement bore (shallow counterbore on fitting-facing side):** 9.8-10.0 mm diameter
   - Just over collet OD (9.57 mm) — provides lateral constraint so the plate engages the collet squarely
   - Depth: ~2 mm (enough to surround the collet protrusion in the extended state)
   - This bore acts as a centering funnel, guiding the plate onto each collet even with slight misalignment

3. **Body end clearance bore (deeper counterbore):** 15.5 mm diameter
   - Clears the 15.10 mm body end OD
   - Depth: sufficient to accommodate the body end protrusion without the plate bottoming out on the body end before the collet is fully depressed
   - This bore does not engage anything — it simply provides clearance

### Plate Layout for 4 Fittings

The 4 fittings are arranged in a rectangular pattern. The minimum center-to-center spacing is constrained by the body end OD (15.10 mm) plus a structural wall between the outer bores:

- Minimum center-to-center: 15.5 mm (bore) + 2.5 mm (wall) + 15.5 mm (bore) / 2 + 15.5 mm / 2 = **18.0 mm minimum** (with just 2.5 mm wall between body end clearance bores)
- Recommended center-to-center: **20.0 mm** (provides 4.5 mm wall between 15.5 mm bores — comfortable for FDM printing in PETG)

Plate overall dimensions depend on the fitting pattern, but a 2x2 grid at 20 mm spacing yields an active area of roughly 40 mm x 40 mm, plus edge material for the guide features.

### Material and Thickness

- **Material:** PETG (strong, slight flex, good layer adhesion)
- **Plate thickness:** 4-5 mm at the collet engagement zone. The stepped bores reduce the effective wall thickness at the tube clearance hole to approximately 2 mm — adequate for the low forces involved (15 N per bore, distributed across the annular face)
- **Print orientation:** Flat (XY plane) so the bore axes are in Z. This gives the strongest geometry for the annular push faces.

---

## 3. Squeeze Ergonomics

### Available Hand Force

The squeeze action uses the palm pushing the cartridge front face forward while the fingers curl around a pull surface connected to the release plate, pulling it toward the user (toward the fittings). This is biomechanically a **power grip squeeze**, similar to operating pliers or a hand brake.

Published ergonomic data:

| Population | Maximum grip force | Recommended sustained/repetitive |
|------------|-------------------|----------------------------------|
| Male 50th percentile | ~450-500 N | ~90-100 N |
| Female 50th percentile | ~250-300 N | ~50-60 N |
| Female 5th percentile | ~150-180 N | ~30-35 N |
| Push button max (auto industry guideline) | — | 13 N (3 lbf) |
| Maximum pinch force (auto industry guideline) | — | 40 N (9 lbf) |

Sources: Ergoweb force guidelines, Cornell DEA3250 hand tool ergonomics, CCOHS hand tool design guidelines.

### Design Target

The release action is **infrequent** (only when replacing the pump cartridge, which may happen once per year or less). It is not repetitive and does not need to be sustained. However, it must be comfortable for the weakest expected user.

- **Total release force (4 collets): 20-60 N estimated**
- **Female 5th percentile squeeze capability: ~150-180 N maximum**
- **Margin: 3x-9x** — well within comfortable one-handed operation even at the high end of the force estimate

For consumer appliance design, the rule of thumb is that required force should be **less than 1/3 of the average maximum** for the target population. For the female 5th percentile (~150 N max), one-third is ~50 N. Our 20-60 N estimate is at or below this threshold.

**Verdict: The squeeze mechanism is ergonomically viable.** Even at the worst case (60 N for 4 collets), the required force is within comfortable one-handed range for nearly all adults. The mechanical advantage of the palm-vs-fingers squeeze geometry (similar to a pair of pliers) further improves the effective force available.

### Grip Span

The distance between the palm surface (front face) and the finger pull surface (release plate linkage) determines the effective grip span. Ergonomic guidelines recommend:

- **Optimal power grip span: 45-55 mm**
- **Maximum comfortable span: 70-90 mm**
- **Minimum functional span: 35-40 mm**

The cartridge geometry should target a **rest-state grip span of 45-55 mm** between the front face and the finger pull surface, closing by ~1.5 mm when fully squeezed (the plate travel distance). This tiny closure ratio means the grip span is essentially constant during the action — the user perceives it as a firm squeeze, not a gradual closing motion.

---

## 4. Plate Travel and Guidance

### Required Travel

- **Collet travel: 1.3 mm** (caliper-verified)
- **Design travel: 1.5 mm** (includes 0.2 mm margin for manufacturing tolerance and incomplete seating)
- **Hard stop at 2.0 mm** (prevents over-travel that could damage internal fitting components)

### Guidance Mechanism Options

The plate must translate linearly along the fitting axis without tilting or binding, over just 1.5 mm of travel. Three options:

#### Option A: Guide Posts and Bores (Recommended)

Two or four smooth cylindrical posts (3-4 mm diameter) printed as part of the cartridge frame, passing through matching bores in the release plate. This is the simplest and most reliable approach for FDM printing.

- **Post diameter:** 3.5 mm
- **Bore diameter:** 3.7-3.8 mm (0.2-0.3 mm clearance for FDM tolerance)
- **Post length:** 8-10 mm (provides sufficient bearing length to prevent plate tilt even with clearance)
- **Placement:** At diagonal corners of the plate, maximizing the moment arm against tilt
- **Advantages:** Simple to print, robust, low friction over 1.5 mm travel, self-aligning
- **Disadvantages:** Requires close tolerance on bore diameter (achievable with 0.1 mm layer height)

#### Option B: Slot Rails

Two parallel rails on the cartridge frame, with matching grooves in the plate edges. The plate slides along the rails.

- **Advantages:** Constrains the plate in both translation axes
- **Disadvantages:** More complex geometry, harder to print cleanly, more friction over short travel, and the short stroke means rail engagement length is minimal

#### Option C: Flexure Guides

The plate is connected to the frame by thin flexure beams that allow ~1.5 mm of axial deflection.

- **Advantages:** No sliding contact, no wear, no clearance issues
- **Disadvantages:** Flexure stress over thousands of cycles (though the cartridge is replaced, not the plate, so cycle count is very low — maybe 1-5 times per cartridge lifetime)

**Recommendation: Option A (guide posts).** The 1.5 mm travel is so short that friction, wear, and alignment are non-issues. Guide posts are the simplest to design and print.

### Tactile Feedback

The user needs to know when the release is complete (all 4 collets fully depressed). Options:

1. **Hard stop with audible click:** A small snap feature on the guide post engages at full travel (1.5 mm). The snap produces a tactile and audible "click." This is the most satisfying feedback mechanism.
   - Implementation: A small bump (0.3 mm) on each guide post at the 1.5 mm position, with a matching detent in the plate bore. The plate snaps over the bump.
   - **Concern:** The snap force must be low enough not to add significantly to the release force, but high enough to be perceptible. A 0.3 mm bump on a 3.5 mm post in PETG should produce ~2-5 N of snap force — perceptible but trivial.

2. **Bottoming out on a hard stop:** The plate contacts a rigid surface at full travel. The user feels the sudden increase in resistance. Less satisfying than a click but simpler.

3. **Visual indicator:** A colored stripe on the guide post becomes visible when the plate reaches full travel. Supplements tactile feedback.

**Recommendation: Hard stop (option 2) as the primary feedback, with a snap feature (option 1) if prototyping confirms it is printable and perceptible.** The 1.5 mm travel is so short that the user will feel the plate bottom out clearly.

---

## 5. Return Mechanism

When the user releases the squeeze, the plate must return to its rest position (not engaging collets) so that:
- The collets can re-grip tubes when the cartridge is re-docked
- The plate doesn't rattle in the rest position
- The mechanism is ready for the next disconnect cycle

### Required Return Force

The return force must overcome:
- Plate weight (negligible — a few grams of PETG)
- Any friction on the guide posts (negligible over 1.5 mm)
- The plate should return positively and not rely on gravity (the cartridge orientation may vary during handling)

A return force of **2-5 N** is sufficient — perceptible to the user as a slight spring-back, but not adding significantly to the squeeze force.

### Option A: Collet Spring-Back (Simplest)

The collets themselves are spring-loaded — they are spring steel elements that naturally return to their extended position when released. This spring-back pushes the release plate back to its rest position.

- **Advantages:** Zero additional parts. The mechanism self-returns using the energy stored in the 4 collet springs.
- **Disadvantages:** The collet spring force may be very low (the same 5-15 N per collet that resists depression, but the return direction is the same spring force). With 4 collets, the return force could be 20-60 N — actually quite strong, and more than sufficient.
- **Concern:** If the plate is not in contact with the collets at rest (there may be a small air gap), collet spring-back would not push the plate at all. The plate must be resting against the collet faces in its default position for this to work.

**Assessment:** This works **only if** the plate rests in contact with the collets at its rest position. Given the tight packaging, this is achievable: the rest position is defined by the plate sitting against the extended collet faces, and the squeeze direction pushes the collets inward. When released, all 4 collet springs push the plate back.

### Option B: Printed Cantilever Springs

Two or four PETG cantilever beams printed as part of the cartridge frame, bearing against the release plate. The beams are pre-deflected ~1.5 mm when the plate is in its travel-end position, providing return force.

- **Cantilever sizing (rule of thumb):** Deflection = beam length / 8 for a safe design. For 1.5 mm deflection: beam length = 12 mm minimum. A 12 mm x 3 mm x 1 mm PETG cantilever deflected 1.5 mm produces approximately 2-4 N of force (varies with print quality and material).
- **Advantages:** Reliable return regardless of collet contact state. Can be tuned by adjusting beam dimensions.
- **Disadvantages:** Adds complexity. Cantilever beams in FDM are sensitive to print orientation and layer adhesion. Fatigue is a non-issue given the very low cycle count (1-5 actuations per cartridge lifetime).

### Option C: Small Compression Spring (Metal)

A standard small compression spring (e.g., 5 mm OD x 10 mm free length, ~0.3 N/mm rate) between the plate and the cartridge frame.

- **Advantages:** Precise and consistent return force. Metal springs do not fatigue at these low cycles and deflections.
- **Disadvantages:** Adds a BOM part. Must be retained during assembly. Spring must be captured (pocket in plate and frame) to prevent displacement.
- **Sourcing:** Widely available as assortment kits on Amazon. A single 5 mm spring with 0.3 N/mm rate compressed 1.5 mm produces 0.45 N — too low. Two springs at 1.0 N/mm rate would produce 3 N total — adequate.

### Option D: Elastomeric Bumper

A small piece of silicone or rubber bonded to the frame, compressed by the plate during actuation.

- **Advantages:** Simple, quiet, provides gentle return and damping.
- **Disadvantages:** Adds a BOM part. Bonding to PETG may be unreliable. Silicone's compression set could reduce return force over time.

### Recommendation

**Primary: Option A (collet spring-back)** — Design the rest position so the plate sits in contact with the collet faces. The collet springs provide a strong, reliable return force with zero additional parts. This is the most elegant solution and aligns with the vision of minimizing BOM.

**Fallback: Option B (printed cantilevers)** — If prototyping reveals that the plate does not maintain reliable contact with the collets at rest (e.g., due to tolerance stack-up creating an air gap), add 2-4 printed cantilever springs. These are zero-BOM and can be integrated into the cartridge frame.

**Not recommended: Options C and D** — Adding metal springs or elastomeric bumpers increases BOM and assembly complexity for a mechanism that actuates only a few times in the cartridge's lifetime. Not justified.

---

## 6. Summary and Design Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Collet travel (per side) | 1.3 mm | Caliper measurement |
| Design plate travel | 1.5 mm | +0.2 mm margin |
| Hard stop | 2.0 mm | Over-travel protection |
| Estimated force per collet | 5-15 N | Engineering estimate (finger-operable mechanism) |
| Total force for 4 collets | 20-60 N | 4x per-collet estimate |
| Female 5th percentile squeeze | ~150 N | Ergonomic literature |
| Ergonomic margin | 3x-9x | Comfortable for nearly all adults |
| Grip span (rest) | 45-55 mm | Ergonomic optimum for power grip |
| Tube clearance bore | 6.5 mm | Between tube OD (6.30) and collet ID (6.69) |
| Collet engagement bore | 9.8-10.0 mm | Just over collet OD (9.57) |
| Body end clearance bore | 15.5 mm | Clears body end OD (15.10) |
| Fitting center-to-center | 20.0 mm recommended | 15.5 mm bore + 4.5 mm wall |
| Guide post diameter | 3.5 mm | FDM-friendly |
| Guide bore diameter | 3.7-3.8 mm | 0.2-0.3 mm clearance |
| Return mechanism | Collet spring-back (primary) | Zero additional parts |
| Plate material | PETG | Strong, slight flex, printable |
| Plate thickness | 4-5 mm | Adequate for 15 N/bore distributed load |

### Key Design Decisions for Next Phase

1. The stepped bore geometry (6.5 / 9.8 / 15.5 mm) is the critical interface — get this right in the first prototype
2. Guide posts at diagonal corners of the plate provide tilt resistance with minimal complexity
3. Collet spring-back as the return mechanism eliminates BOM; verify contact at rest during prototyping
4. A hard stop at 2.0 mm prevents over-travel; consider adding a snap detent for tactile click feedback
5. The 0.39 mm design window on the tube clearance bore (between 6.30 mm tube OD and 6.69 mm collet ID) is the tightest tolerance in the design — FDM at 0.1 mm layers should achieve this, but verify with a test print of just the stepped bore
