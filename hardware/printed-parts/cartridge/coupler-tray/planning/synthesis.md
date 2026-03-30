# Coupler Tray — Design Synthesis

**Sources synthesized:** hardware/requirements.md, hardware/vision.md, john-guest-union geometry-description.md (caliper-verified), release-plate synthesis.md, pipeline/steps/3-design-decision.md

---

## 1. What This Part Is

The coupler tray is a flat plate that holds four John Guest PP0408W union couplers inside the pump cartridge. It is one of two interior flat plates inside the cartridge (the other is the pump tray). Per Vision Section 4, Season 1, Phase 1, Item 3, this version is:

- A flat plate with pockets for capturing 4 John Guest union couplers
- No strut bores (Phase 4)
- No rail features (Phase 5/9)
- No retention features (Phase 9)
- No split-line geometry, dovetails, or snap detents (Phase 3)

The only geometry beyond a flat plate is what is required to hold the couplers.

---

## 2. Coupler Geometry That Drives the Pocket Design

From the caliper-verified geometry description (all values are measured, HIGH confidence):

| Feature | Value |
|---|---|
| Center body OD | 9.31mm |
| Center body length | 12.16mm |
| Body end OD (each side) | 15.10mm |
| Body end length (each side) | 12.08mm |
| Body without collets (total) | 36.32mm |
| Collet protrusion per side (compressed) | ~1.40mm |
| Collet protrusion per side (extended) | ~2.74mm |
| Total length, collets extended | 41.80mm |
| Total length, collets compressed | 39.13mm |

The fitting is a barbell: two 15.10mm OD ends flanking a 9.31mm OD center. The shoulder at each end-to-center transition is a flat annular ring, 2.90mm wide per side ((15.10 − 9.31) / 2 = 2.895mm).

---

## 3. Pocket Geometry — Reasoning

### 3.1 The constraint

The Phase 1 tray is one piece. The coupler cannot be inserted axially into a pocket that grips the center body on both sides simultaneously — that is exactly the two-piece split problem that Phase 3 solves. For Phase 1 the tray must hold the coupler well enough that it cannot fall out under gravity when the tray is installed vertically (coupler long axis horizontal, perpendicular to gravity).

### 3.2 Candidate: stepped bore

Proposed geometry: a stepped bore on the insertion face. From the insertion face inward:

- **Large bore:** 15.5mm diameter, 12.08mm deep — accepts the insertion-side body end
- **Narrow bore:** 9.5mm diameter, continuing through the remaining plate thickness — accepts only the center body (9.31mm OD)
- **Far face:** Open at 9.5mm — the far body end (15.10mm OD) cannot pass through and bears against the narrow bore exit lip

**Insertion sequence:** The coupler is oriented with one body end facing the tray insertion face. That body end (15.10mm OD, 12.08mm long) slides into the large bore. Once it clears the large-bore shoulder (at 12.08mm depth), the center body (9.31mm OD) enters the narrow bore (9.5mm). The coupler is pushed until the far body end shoulder (the annular face between center body and far body end) seats against the narrow bore exit lip at the far face of the plate.

**Retention check:** With the coupler fully seated:

- Ejection direction (pulling the coupler back out the insertion face): the far body end shoulder (15.10mm OD annular ring) bears against the narrow bore exit lip at the far face. The shoulder cannot pass back through the 9.5mm bore. Axially retained.
- Insertion direction (pushing the coupler further through): the large bore shoulder (the step from 15.5mm to 9.5mm at 12.08mm depth) blocks the insertion-side body end shoulder from advancing. The insertion-side body end shoulder (annular ring, 15.10mm OD) cannot pass through the 9.5mm bore. Axially retained in this direction also.
- Radially: the center body (9.31mm OD) is supported by the 9.5mm narrow bore on all sides. The 0.095mm radial clearance per side (9.5mm bore − 9.31mm body = 0.19mm total, 0.095mm per side) is adequate for gravity support. The coupler cannot rock or drop.

The stepped bore geometry works. Both axial directions are constrained by the barbell shoulders bearing against the bore step. The coupler is captured.

### 3.3 Is there a simpler option?

A through-hole at 15.5mm (large bore all the way through) would allow the coupler to slide axially and fall out — no retention. A through-hole at 9.5mm (narrow bore all the way through) requires inserting the coupler from one end, which would require pushing the 15.10mm body end through a 9.5mm bore — impossible. The stepped bore is the minimum geometry that provides both insertion access and axial retention from a one-piece flat plate. No simpler option exists.

### 3.4 FDM constraint check

The narrow bore exit lip at the far face: the lip is an annular ring of material between the 9.5mm narrow bore and the outer plate edge. This is a flat surface on the far face of the plate — no overhang, no unsupported geometry. It prints cleanly face-up.

The large-bore-to-narrow-bore shoulder inside the bore: this is a flat annular ring at 12.08mm depth inside the bore, perpendicular to the bore axis. With the bore axis horizontal (perpendicular to the build plate), this shoulder would be an internal overhang. However, the print orientation for this plate is face-up on the build plate (see Section 6), so the bore axis is horizontal — this internal shoulder bridges across the bore diameter (9.5mm to 15.5mm transition). The bridge span is (15.5mm − 9.5mm) / 2 = 3.0mm per side. Per requirements.md: minimum unsupported bridge span < 15mm. A 3.0mm internal shoulder bridge is well within the 15mm bridge limit and prints without support.

### 3.5 Final pocket dimensions

| Feature | Designed dimension | Rationale |
|---|---|---|
| Large bore diameter | 15.5mm | 15.10mm body end OD + 0.4mm FDM clearance allowance |
| Large bore depth | 12.08mm | Exactly the body end length; insertion-side shoulder seated flush at step |
| Narrow bore diameter | 9.5mm | 9.31mm center body OD + 0.19mm total clearance (0.095mm per side, snug sliding fit) |
| Narrow bore depth | plate thickness − 12.08mm (see Section 5) | Exits far face; far body end shoulder bears on exit lip |

**Note on FDM hole sizing:** Per requirements.md, holes print smaller than designed by approximately 0.2mm. The 15.5mm and 9.5mm dimensions are the designed CAD values. If empirical calibration shows the printer is printing holes 0.2mm undersize, adjust to 15.7mm and 9.7mm respectively. The narrow bore tolerance is more critical — if it prints at 9.3mm it will be a press fit on the center body, which may make insertion difficult. Start with 9.5mm; adjust to 9.7mm if needed.

---

## 4. Coupler Positions in the Tray

### 4.1 Source of positions

The release plate synthesis (Section 5) established four fitting positions in the rear wall. The coupler tray holds these same four couplers. The coupler long axes are parallel to the cartridge front-to-back depth axis. The coupler tray is a plate perpendicular to that axis — the four pocket bores are the tray's four coupler positions, and they must match the release plate's bore positions.

### 4.2 Release plate position values

From the release plate synthesis, Section 5:

| Fitting | Pump | Role | X (horizontal) | Z (vertical) |
|---|---|---|---|---|
| A | Pump 1 (left) | Inlet | −31mm | +15mm |
| B | Pump 1 (left) | Outlet | −31mm | −15mm |
| C | Pump 2 (right) | Inlet | +31mm | +15mm |
| D | Pump 2 (right) | Outlet | +31mm | −15mm |

Origin is at the rear wall center. Horizontal center-to-center (A–C or B–D): **62mm**. Vertical center-to-center (A–B or C–D): **30mm**.

### 4.3 Precision of these values

These positions are approximate working assumptions stated in the release plate synthesis. The 62mm horizontal spacing is derived from the Kamoer KPHM400 pump width (62.6mm), with minimal inter-pump clearance — it is geometry-driven and reasonably constrained. The ±15mm vertical spacing (30mm total) is an assumption based on "one above center, one below" for the pump tube connector exit positions; the exact offset has not been caliper-verified (this is flagged as Open Question 3 in the release plate synthesis).

**For this synthesis:** Use 62mm horizontal spacing and 30mm vertical spacing as the nominal coupler positions in the tray. These are the same values as the release plate. If the pump tube connector exit positions are subsequently measured and differ from ±15mm, both the release plate and the coupler tray will need to be updated together. The coupler tray's pocket positions are always locked to the release plate's bore positions — they are the same four points.

### 4.4 Explicit pocket center positions

Using the same coordinate convention as the release plate (origin at plate center, X horizontal, Z vertical, viewed from the front):

| Pocket | X | Z |
|---|---|---|
| A (Pump 1 Inlet) | −31mm | +15mm |
| B (Pump 1 Outlet) | −31mm | −15mm |
| C (Pump 2 Inlet) | +31mm | +15mm |
| D (Pump 2 Outlet) | +31mm | −15mm |

### 4.5 Edge clearance check

Large bore diameter: 15.5mm. Nearest edges:

- Horizontal (A–C): 62mm center-to-center. Edge-to-edge = 62mm − 15.5mm = 46.5mm. No interference.
- Vertical (A–B): 30mm center-to-center. Edge-to-edge = 30mm − 15.5mm = 14.5mm. No interference.
- Plate outer edge to nearest bore center: the plate outer edge must be at least 7.75mm (large bore radius) + 1.2mm (minimum structural wall per requirements.md) = 8.95mm from each bore center. The plate extends ±31mm horizontally from center + 8.95mm minimum = minimum half-width 39.95mm, so minimum total width ~80mm. Vertically: ±15mm + 8.95mm = minimum half-height 23.95mm, so minimum total height ~48mm.

---

## 5. Plate Dimensions

### 5.1 Thickness

The minimum plate thickness is set by the large bore depth requirement:

- Large bore depth: 12.08mm (body end length, exactly)
- Minimum narrow bore retention lip: any positive thickness exits the far face. Minimum structurally sound wall is 0.8mm (2 perimeters per requirements.md).
- Minimum plate thickness: 12.08mm + 0.8mm = **12.88mm**

A 12.88mm plate is technically functional but leaves only 0.8mm of narrow bore engagement. For robust retention of the far body end shoulder, a minimum of 2.0mm of narrow bore depth is preferable (enough for the shoulder to seat firmly against the lip under gravity and light handling loads, with the 1.2mm structural wall minimum applying to the lip annular ring).

**Designed plate thickness: 15mm**

This provides:
- Large bore depth: 12.08mm (body end, full length)
- Narrow bore depth: 15mm − 12.08mm = **2.92mm** (far shoulder seated against a 2.92mm deep lip)
- The narrow bore exit lip annular ring: (15.5mm − 9.5mm) / 2 = 3.0mm wide. At 2.92mm depth, the annular lip presents ample bearing surface for the far body end shoulder.

**Justification for 15mm vs. minimum 12.88mm:** The additional 2.12mm of narrow bore depth increases the bearing surface for the far body end shoulder from 0.8mm to 2.92mm. The shoulder load under gravity is trivial (coupler weighs a few grams), but 2.92mm provides robust handling retention — the coupler will not disengage when the tray is handled during assembly. The added material (2.12mm extra thickness) has no functional cost.

### 5.2 Width and height

Minimum outer plate dimensions from bore positions and minimum wall requirements:

- Width: 2 × (31mm + 7.75mm + 1.2mm) = 2 × 39.95mm ≈ **80mm minimum**
- Height: 2 × (15mm + 7.75mm + 1.2mm) = 2 × 23.95mm ≈ **48mm minimum**

**Designed plate dimensions: 80mm wide × 50mm tall × 15mm thick**

The 50mm height provides 2mm of additional margin over the 48mm minimum at the top and bottom bore edges. The 80mm width is the minimum. Both are preliminary nominal values — the final dimensions will be updated when the coupler tray slides into side-wall rails (Phase 5) and when the pump tray and side-wall geometry is finalized.

**Note:** The release plate synthesis gives an approximate plate dimension of 75mm wide × 65mm tall for the release plate, which must span the same 62mm × 30mm fitting rectangle plus guide pin bosses at the corners. The coupler tray does not have guide pin bosses, so it does not need the extra height the release plate requires for pin placement. The coupler tray is a smaller plate.

### 5.3 Plate outer profile

Rectangular. No chamfers, no fillets, no rounded corners in this phase. A flat rectangle is the simplest shape and there is no physics-driven reason to add edge features in Phase 1.

---

## 6. Print Orientation

**Print orientation: flat face down on the build plate (large bore face up or down, bore axes horizontal, parallel to the build plate).**

Wait — the bore axes are the coupler long axes, which are horizontal (front-to-back in the cartridge). The plate face is perpendicular to those axes. If the plate face is down on the build plate, the bore axes are vertical (pointing up from the build plate). That means the bores print as vertical cylinders — clean, accurate, no bridging issues. The internal shoulder (large-bore-to-narrow-bore step) is a horizontal ledge inside a vertical bore, which is a simple overhang requiring bridging across the bore diameter.

**Revised:** With bores vertical (Z-axis, parallel to print layers), the internal shoulder is a horizontal surface bridging the bore step. The bridge is the annular ring from 9.5mm to 15.5mm in diameter — the unsupported span is (15.5 − 9.5)/2 = 3.0mm per side. Per requirements.md, minimum unsupported bridge span < 15mm. 3.0mm is well within limit. The shoulder prints cleanly as a bridge.

**Print orientation: flat face (large bore insertion face) pointing up or down. Bore axes vertical (Z direction). Layer lines parallel to plate face.**

This orientation is correct for:
- Bore accuracy (vertical cylinders print to tightest diameter tolerances)
- The internal shoulder bridge (3.0mm, within FDM bridge limit)
- Layer lines parallel to plate face, meaning the plate resists in-plane loads (from coupler weight and handling) across layers — these loads are perpendicular to the bore axes and are well within FDM in-plane strength

**Elephant's foot note:** If the insertion face is placed down on the build plate, the first 0.2–0.3mm of the large bore entrance will flare slightly. Per requirements.md, add a 0.3mm × 45° chamfer to the bottom edge of the bore entrance to mitigate elephant's foot on the bore rim. If the insertion face is up (far face down), no chamfer is needed at the bore entrance but a chamfer at the far face bore edge is appropriate for the same reason.

---

## 7. Conflicts with the Vision

### Conflict 1: Vision describes a two-piece tray; Phase 1 specifies one piece

**Vision Section 3:** "The coupler tray is two separate pieces (flat surfaces) that lock permanently together via tapered dovetails and snap detents. The geometry of the John Guest union couplers requires this — the couplers cannot be inserted into a one-piece tray."

**Phase 1 scope (Vision Section 4, Season 1, Phase 1, Item 3):** "Coupler tray — flat plate with holes/pockets for capturing 4 John Guest union couplers. No strut bores — those come in Phase 4." The two-piece split is explicitly deferred to Phase 3 (steps 8–11).

**Resolution:** This is not a conflict between the vision and physics — it is the intentional phased build sequence. Phase 1 uses a stepped bore pocket that allows coupler insertion from one side (insertion-side body end enters the large bore, center body passes into the narrow bore, far body end cannot exit). This one-piece geometry physically captures the coupler. It does not provide the bilateral shoulder retention of the final two-piece design (in Phase 1, one shoulder — the large-bore step — is accessible during insertion and does not capture by itself; the far exit lip provides the final retention). The Phase 1 tray is a test-fit vehicle, not the final retention design.

**No modification needed.** Phase 1 proceeds as scoped. The vision's two-piece description applies to the final design, which is Phase 3.

### Conflict 2: One-piece stepped bore vs. vision's claim that "couplers cannot be inserted into a one-piece tray"

**Vision states:** "the couplers cannot be inserted into a one-piece tray."

**Technical finding:** The stepped bore geometry described in Section 3 allows coupler insertion into a one-piece tray. Insertion is possible because the large bore accepts the insertion-side body end, and only the far body end is blocked. The vision's statement is accurate for a symmetrically-bored one-piece tray (where the center bore is too small for the body ends and there is no room to insert from either side), but a stepped bore provides one-sided insertion access.

**Resolution:** No conflict with the build sequence — the Phase 1 stepped bore is an interim design that allows test fitting. The final two-piece design (Phase 3) will provide full bilateral shoulder retention. The vision's statement describes why a symmetric one-piece tray fails; it does not preclude a stepped-bore one-piece tray as an interim. Flag this for the Phase 3 agent: when designing the split, note that the Phase 1 stepped bore tray does physically capture the coupler (with one accessible shoulder), and the Phase 3 design improves on this with bilateral capture.

---

## 8. Bill of Materials

### 3D-printed parts

| Part | Material | Qty |
|---|---|---|
| Coupler tray | PETG | 1 |

### Off-the-shelf parts seated in this tray

| Part | Specification | Qty |
|---|---|---|
| John Guest PP0408W 1/4" union coupler | White acetal copolymer, 1/4" OD, straight union, barbell profile | 4 |

No fasteners, adhesives, or additional hardware are required for Phase 1. The couplers are retained by the pocket geometry alone.

---

## 9. Open Questions

1. **Pocket diameter empirical calibration.** The narrow bore (9.5mm designed) must be verified on the actual printer. If it prints undersize by 0.2mm (per requirements.md guidance), the as-printed diameter is 9.3mm — this would be a press fit on the 9.31mm center body and may make coupler insertion difficult or crack the bore walls. Print a test bore at 9.5mm, 9.7mm, and 9.9mm before committing to the final pocket diameter.

2. **Large bore depth tolerance.** The large bore depth is designed to 12.08mm, exactly the body end length. If the printer overshoots depth by 0.2mm (12.28mm depth), the insertion-side shoulder no longer seats flush at the bore step — there is a 0.2mm gap. This does not affect retention (the far exit lip still captures the coupler) but may allow 0.2mm of axial play. A large bore depth of 12.08mm is the correct design value; verify empirically.

3. **Fitting position precision.** The ±15mm vertical fitting offset (30mm vertical spacing) is an assumption from the release plate synthesis, not a caliper-verified value. The actual Kamoer KPHM400 tube connector exit positions must be measured before these positions are treated as final. If the actual vertical offset differs from ±15mm, both the release plate and coupler tray pocket positions must be updated together to maintain alignment. This is the highest-priority open question for the coupler tray.

4. **Coupler retention under vibration and handling.** Phase 1 retention relies on the narrow bore exit lip bearing against the far body end shoulder. Under gravity this is stable. Under handling (tilting, inverting the tray), the coupler may slide axially if the fit has significant play. The 9.5mm bore on a 9.31mm center body gives 0.095mm radial clearance per side — tight enough that the coupler is radially snug. Axial play: with the coupler fully seated, axial freedom is zero (the large-bore shoulder and narrow-bore exit lip both bearing against respective shoulders). If there is any dimensional gap from print variation, the coupler may rattle. Acceptable for Phase 1 test fitting; addressed in Phase 3.

5. **Plate outer dimensions finalization.** The 80mm × 50mm nominal outer dimensions will be superseded when the side-wall rail geometry is designed in Phase 5. The coupler tray must slide into protruding rails on the left and right side walls. The plate width (80mm) and height (50mm) are the minimum bounding rectangle; the final values depend on cartridge interior width and the rail engagement length required. This is a Phase 5 dependency.

6. **Relationship to pump tray.** The pump tray and coupler tray are both interior plates in the cartridge. Their relative Z (vertical) positions — which plate is higher, what gap exists between them — determine the tubing routing from pump head to coupler. This spatial relationship is not yet defined and will need to be coordinated once both plates are modeled.
