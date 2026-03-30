# Coupler Tray — Conceptual Architecture

**Phase:** Season 1, Phase 1, Item 3
**Scope:** One-piece flat plate with stepped-bore pockets for 4 John Guest PP0408W union couplers. No strut bores, no rail features, no retention features, no split geometry.

---

## What This Design Is

A rectangular PETG plate, 80mm wide × 50mm tall × 15mm thick, with four stepped-bore pockets. Each pocket accepts one John Guest PP0408W union coupler from the insertion face and retains it by the barbell geometry of the coupler body. The plate sits inside the pump cartridge as one of two interior flat plates. It is a test-fit vehicle and dimensional placeholder for the final two-piece tray that Phase 3 will produce.

---

## 1. Piece Count and Split Strategy

**One piece. No split in Phase 1.**

The synthesis establishes that a stepped bore — large bore accepting the insertion-side body end (15.5mm designed diameter, 12.08mm deep), transitioning to a narrow bore gripping the center body (9.5mm designed diameter, continuing to the far face) — allows coupler insertion and axial capture from a single-piece flat plate. Insertion is one-sided: the user pushes the coupler in through the large-bore face until the far body end shoulder seats against the narrow-bore exit lip.

A split is not needed at this phase because the stepped bore provides sufficient capture for test-fit purposes. The Phase 1 tray is not intended to demonstrate final bilateral shoulder retention — that is Phase 3's task. The vision's statement that the coupler tray must be two pieces refers to the final bilateral-capture design, not to this stepped-bore interim. No conflict exists; the build sequence defers the split intentionally.

---

## 2. Join Methods

Not applicable. This is a single piece. No joining geometry exists in Phase 1.

The couplers seat in the pockets by press-and-snap — pushed in by hand, captured by the pocket geometry. No fasteners, adhesives, or hardware required.

---

## 3. Seam Placement

Not applicable. Single piece; no seams.

---

## 4. User-Facing Surface Composition

The coupler tray is an interior part. The user never sees or touches it in normal use. The assembler encounters it during cartridge build.

**During assembly, the assembler sees:**

- **Insertion face (front):** The large-bore openings of the four pockets. Four 15.5mm diameter counterbores arranged in a 62mm × 30mm rectangle, centered on the plate face. This is the face through which the couplers are loaded. No surface treatment required — it is never user-visible.
- **Far face (back):** Four 9.5mm narrow-bore openings at the far face. The far body end of each seated coupler is flush with or slightly recessed behind this face. This face faces toward the cartridge back wall when installed.
- **Edges:** Four rectangular plate edges. No features. Flat cuts from the print.

There is no user-facing surface on this part. Visual hierarchy is irrelevant. Functional legibility during assembly — which face to load couplers from — is provided by the geometry itself (large bores are obviously the insertion face).

---

## 5. Design Language

The coupler tray is an interior utility part that the user never sees. Matte surface finish from the print is correct and sufficient. No cosmetic treatment, no texturing, no radii at the outer corners.

The part is consistent with how the pump tray will look: a flat plate, rectangular, no exterior detailing. These two interior plates are hidden infrastructure — their design language is functional uniformity, not product aesthetics. A stranger opening the cartridge (which is not a user-accessible action) would see two plain flat plates and four brass-colored couplers. That is the correct appearance for internal structure.

Material is PETG. PETG is dimensionally stable, chemically resistant to flavoring syrup residue, and prints at acceptable accuracy for the tight narrow-bore tolerance (9.5mm designed). Surface finish from standard PETG on the Bambu H2C is adequate for the bore surfaces.

---

## 6. Service Access Strategy

The pump cartridge is replaced as a unit. The user does not service individual interior plates. When the cartridge is retired, the coupler tray goes with it — no disassembly, no part recovery.

This means no service features belong on the coupler tray at any phase. The Phase 3 split design (dovetails and snap detents that lock the halves permanently) is consistent with this: the two halves are assembled once at the factory (or by the builder), never separated again.

No service access features are designed into this part. The cartridge replacement interaction (squeeze the front face, four tubes disengage, slide the cartridge out) provides the only service scenario the vision describes, and it operates at the cartridge level, not the tray level.

---

## 7. Manufacturing Constraints

**Print orientation:** Flat face down on the build plate. The bore axes run vertically (Z direction, parallel to the layer stack). This is the correct orientation because:

- Vertical bores (Z-axis cylinders) print to the tightest diameter tolerances on FDM. The narrow bore (9.5mm designed, gripping a 9.31mm center body with 0.095mm radial clearance per side) requires the best diameter accuracy the printer can produce. Vertical orientation maximizes this.
- The internal shoulder (the annular step from 15.5mm large bore to 9.5mm narrow bore at 12.08mm depth) bridges horizontally across the bore at that depth. Bridge span per side = (15.5 − 9.5) / 2 = 3.0mm. Per requirements.md, minimum unsupported bridge span must remain under 15mm. A 3.0mm bridge is well within limit and prints without support.
- Layer lines run parallel to the plate faces. In-plane loads (coupler weight, assembly handling) act across layers — well within FDM in-plane strength.

**Elephant's foot mitigation:** The bore entrance at the build-plate face will exhibit slight flare from elephant's foot (first 0.2–0.3mm). Add a 0.3mm × 45° chamfer to the bore entrance rim on the bottom face per requirements.md guidance.

**Build volume check:** The plate is 80mm × 50mm × 15mm. The Bambu H2C single-nozzle build volume is 325mm × 320mm × 320mm. The part fits comfortably in any orientation. No constraint.

**Material:** PETG. Single nozzle. No support material required — the bore bridge at 3.0mm prints clean, and there are no other overhangs in the part.

**Minimum wall check:** The annular lip at the narrow bore exit face is (15.5 − 9.5) / 2 = 3.0mm wide. Minimum structural wall per requirements.md is 1.2mm for load-bearing walls, 0.8mm for non-structural. 3.0mm exceeds both. The pocket walls between adjacent bores (minimum edge-to-edge 14.5mm at closest, center-to-center 30mm vertical, 15.5mm diameter bores) present no thin-wall concern.

**FDM hole sizing note (critical):** Per requirements.md, holes print smaller than designed by approximately 0.2mm. The narrow bore (9.5mm designed) may print at 9.3mm — a near-press-fit on the 9.31mm center body. The synthesis flags printing a test coupon at 9.5mm, 9.7mm, and 9.9mm before committing to the pocket diameter. This is the highest manufacturing risk in the part and must be empirically resolved before the final print.

---

## Summary

The Phase 1 coupler tray is a 80mm × 50mm × 15mm PETG rectangular plate with four stepped-bore pockets — one per John Guest PP0408W union coupler. Pockets are arranged in a 62mm × 30mm rectangle centered on the plate, matching the release plate's four fitting positions. Each pocket is a 15.5mm large bore (12.08mm deep) transitioning to a 9.5mm narrow bore through the remaining 2.92mm of plate thickness. Couplers insert large-end-first through the large-bore face and are captured axially by the far narrow-bore exit lip. The plate prints face-down, bore axes vertical, no supports required. No joins, no seams, no user-facing surfaces, no service features.
