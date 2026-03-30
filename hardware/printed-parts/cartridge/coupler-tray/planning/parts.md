# Coupler Tray — Parts Specification

**Pipeline step:** 4b — Parts Specification
**Input documents:** spatial-resolution.md, synthesis.md, concept.md, john-guest-union/geometry-description.md, requirements.md, vision.md
**Output:** This document — primary input to the CadQuery generation agent (Step 6g)

---

## 1. Part Summary

| Field | Value |
|---|---|
| Part name | Coupler tray |
| Part type | Single printed PETG part |
| Function | Flat plate that captures four John Guest PP0408W union couplers inside the pump cartridge. Each coupler seats in a stepped-bore pocket; the barbell shoulder geometry provides axial retention in both directions. |
| Material | PETG |
| Envelope (W × H × D) | 80.0 mm × 50.0 mm × 15.0 mm |
| Print orientation | Insertion face (large-bore openings, Z = 0) DOWN on build plate. Bore axes run vertically (Z direction, parallel to layer stack). Layer lines parallel to plate face (XY plane). |
| Piece count | 1 |
| Fasteners | None |
| Sub-assemblies | None |

**Coordinate system (part local frame, from spatial-resolution.md Section 2):**

| Axis | Direction | Range |
|---|---|---|
| X | Width, horizontal — positive right when viewed from insertion face | −40 mm → +40 mm |
| Y | Height, vertical — positive up | −25 mm → +25 mm |
| Z | Depth into plate from insertion face — positive toward far face | 0 mm → +15 mm |

Origin: geometric center of the insertion face (the large-bore opening face).
Z = 0 = insertion face (large-bore openings, placed on build plate during printing).
Z = +15 mm = far face (narrow-bore exit openings).

---

## 2. Mechanism Narrative (Rubric A)

### What the assembler sees and touches

The coupler tray is an interior part. The user never sees or touches it in normal operation. The cartridge is a black box to the user; the tray is hidden inside. The assembler encounters it during cartridge build (Vision Section 4, Season 1, Phase 1).

During assembly the assembler holds a flat rectangular PETG plate, 80 mm wide × 50 mm tall × 15 mm thick. One face shows four countersunk openings, each 15.5 mm in diameter, arranged in a 62 mm × 30 mm rectangle centered on the face. That is the insertion face — where the couplers are loaded. The opposite face shows four smaller openings, each 9.5 mm in diameter, at the same four centers. That is the far face.

### What moves

**Moving:** Nothing moves after assembly. The coupler tray is a static structural part. During the assembly step only, each of the four PP0408W couplers translates in the +Z direction (through the insertion face, into and through the stepped bore) until seated.

**Stationary during operation:** The coupler tray plate. All four seated couplers. (The collets at each coupler end move during tube connection/disconnection, but that is coupler-internal mechanism, not tray mechanism.)

### What converts the motion (assembly only)

The assembler pushes a coupler by hand along the Z axis through the insertion face. No mechanical conversion. Direct push force, collinear with the bore axis.

### What constrains the coupler in the seated position

Axial constraint is provided by two bearing surfaces, one for each axial direction:

**Against ejection (−Z direction, pulling coupler back out through insertion face):**
- Feature: narrow bore exit lip at Z = +15 mm (far face).
- The coupler's Shoulder 2 — the annular face between the center body (9.31 mm OD) and body end 2 (15.10 mm OD) — bears against the far face plate material in the annular zone from R = 4.75 mm to R = 7.55 mm (bearing width: 2.80 mm).
- Grounding: body end 2 OD is 15.10 mm; narrow bore exit diameter is 9.5 mm. 15.10 mm > 9.5 mm. The shoulder physically cannot pass back through the narrow bore. The far face at Z = +15 mm is the hard stop.

**Against insertion (pushing coupler further through, +Z direction):**
- Feature: bore shoulder (annular step) at Z = +12.08 mm, inner radius 4.75 mm, outer radius 7.75 mm.
- The coupler's Shoulder 1 — the annular face between body end 1 (15.10 mm OD) and the center body (9.31 mm OD) — bears against this step in the annular zone from R = 4.75 mm to R = 7.55 mm (bearing width: 2.80 mm).
- Grounding: body end 1 OD is 15.10 mm; narrow bore diameter is 9.5 mm. The shoulder cannot pass through the 9.5 mm bore. The annular step at Z = +12.08 mm is the hard stop.

Radial constraint:
- Feature: narrow bore wall, 9.5 mm diameter, Z = +12.08 mm to Z = +15 mm (2.92 mm of engagement depth).
- Center body OD: 9.31 mm. Radial clearance: (9.5 − 9.31) / 2 = 0.095 mm per side.
- The narrow bore supports the coupler radially against gravity (gravity acts in the −Y direction, perpendicular to the bore Z axis). At 5–10 g coupler mass, this clearance is mechanically adequate.

### What provides the return force

Not applicable. There is no return position. The coupler is captured in one position; it does not cycle in and out. This is a static retention, not a spring-loaded mechanism.

### The user's physical interaction (assembly)

The assembler holds the tray insertion face up. The assembler picks up one PP0408W coupler and orients it so one body end (either end — the coupler is symmetric) faces the tray. The assembler aligns the 15.10 mm OD body end with one of the 15.5 mm large bore openings and pushes. The body end slides into the large bore (0.4 mm diametric clearance: 15.5 − 15.10 = 0.40 mm). The coupler advances until Shoulder 1 (the annular face at the body end 1 / center body transition) reaches Z = +12.08 mm — the bore step — and stops. At that moment the center body (9.31 mm OD) is aligned with the narrow bore (9.5 mm). The assembler pushes harder; the center body enters the narrow bore and the coupler continues. The coupler is fully seated when Shoulder 2 (the annular face at center body / body end 2 transition, located at Z = +24.24 mm in the tray frame) emerges from the far face and can no longer be pulled back through the narrow bore. The assembler feels resistance increase as Shoulder 2 seats against the far face lip: a tactile click of approximately 2–4 N snap-through as the shoulder clears the 9.5 mm exit diameter. After this point the coupler is captured.

**DESIGN GAP — snap-through tactile force:** The claim of "2–4 N snap-through" is not grounded in a specific geometric feature with calculated force. The retention mechanism is geometric interference (15.10 mm shoulder vs. 9.5 mm bore), not a spring-loaded snap. For Phase 1 test-fit purposes, the coupler is captured once Shoulder 2 clears the far face; the "click" is the shoulder seating against the lip. No spring force calculation is available at this phase. The sensation will be empirically determined from the first print. No design change required; flagging for completeness.

Repeat for the remaining three pockets.

---

## 3. Constraint Chain Diagram (Rubric B)

```
[Assembler hand: +Z push force]
        |
        | Direct push, collinear with bore axis (no mechanical conversion)
        v
[Coupler body end 1: 15.10mm OD body]
        |
        | Slides within large bore (15.5mm ID, 0.40mm diametric clearance)
        | Large bore guides radially during insertion (Z = 0 to Z = +12.08mm)
        v
[Bore shoulder at Z = +12.08mm: annular step, 9.5mm inner / 15.5mm outer]
        |                                               ^
        | Blocks Shoulder 1 from advancing in +Z       | Hard stop in +Z direction
        | (15.10mm OD cannot pass 9.5mm bore)          | (coupler cannot be pushed through)
        v
[Center body: 9.31mm OD enters narrow bore (9.5mm ID, 0.095mm radial clearance/side)]
        |
        | Continues through Z = +12.08mm to Z = +15mm (2.92mm engagement)
        | Narrow bore provides radial constraint (gravity in -Y, perpendicular to Z)
        v
[Far face at Z = +15mm: narrow bore exit lip]
        |                                               ^
        | Shoulder 2 (15.10mm OD) exits far face       | Hard stop in -Z direction
        | Center body exits: 9.24mm of center body     | (coupler cannot be ejected back
        | beyond far face, then Shoulder 2 at +24.24mm | through insertion face)
        v
[Coupler fully captured: zero axial freedom, 0.095mm radial clearance]

Constraints summary:
  - +Z translation: blocked by bore shoulder at Z = +12.08mm (Shoulder 1 bearing)
  - -Z translation: blocked by far face exit lip at Z = +15mm (Shoulder 2 bearing)
  - Radial (X, Y): constrained by narrow bore walls (9.5mm bore, 9.31mm center body)
  - No rotational constraint — bore is circular; coupler rotates freely about Z axis
    (rotation is not a concern; the coupler is symmetric and connects tubes on both ends)
```

---

## 4. Direction Consistency Check (Rubric C)

Coordinate system: X = plate width (±), Y = plate height (±), Z = depth into plate from insertion face.

| Claim | Direction stated | Axis | Verified? | Notes |
|---|---|---|---|---|
| Assembler pushes coupler into insertion face | Into the plate | +Z | Yes | Insertion face at Z = 0; far face at Z = +15mm; +Z is deeper into the plate |
| Large bore receives body end 1 from Z = 0 to Z = +12.08mm | +Z extent | +Z | Yes | Bore starts at insertion face (Z = 0), runs to bore shoulder (Z = +12.08mm) |
| Bore shoulder blocks further +Z travel | Stop in +Z | +Z | Yes | Annular step at Z = +12.08mm; Shoulder 1 cannot advance past this point |
| Center body continues through narrow bore to far face | +Z extent | +Z | Yes | Narrow bore from Z = +12.08mm to Z = +15mm; center body passes through |
| Shoulder 2 exits far face | +Z exit | +Z | Yes | Shoulder 2 at Z = +24.24mm in part frame; plate far face at Z = +15mm; shoulder is 9.24mm beyond far face |
| Far face lip blocks −Z ejection | Stop in −Z | −Z | Yes | Shoulder 2 (15.10mm OD) cannot reenter 9.5mm narrow bore; far face at Z = +15mm is the bearing surface |
| Gravity acts perpendicular to bore axis | −Y | −Y | Yes | Bore axes parallel to Z; gravity is −Y (down when installed); these are orthogonal |
| Narrow bore supports coupler radially against gravity | Radial in XY plane | ±X and ±Y | Yes | Bore axis is Z; radial directions are X and Y; 0.095mm clearance constrains radial displacement |
| Insertion face placed down on build plate | −Z face down | −Z | Yes | Z = 0 face (insertion face) placed on build plate; Z increases upward during printing |
| Elephant's foot chamfer at bore rim, insertion face | At Z = 0, build-plate face | Z = 0 plane | Yes | Bottom of part during printing is insertion face; chamfer on bore rims at Z = 0 |

No directional contradictions found.

---

## 5. Interface and Path Consistency (Rubric D)

### Part 1 — Interface dimensions

Each of the four pockets is identical. The table below covers one pocket (applies to A, B, C, D).

| Interface | Tray dimension | Coupler dimension | Clearance | Source |
|---|---|---|---|---|
| Large bore (body end 1 seating) | 15.5mm diameter | 15.10mm OD | 0.40mm diametric (0.20mm per side) | Tray: designed CAD value per synthesis.md. Coupler: caliper-verified per geometry-description.md |
| Bore shoulder (Shoulder 1 bearing) | Annular face at Z = +12.08mm, I.R. = 4.75mm, O.R. = 7.75mm | Shoulder 1 annular face, OD = 15.10mm (O.R. = 7.55mm) | Bearing annular width: 7.55 − 4.75 = 2.80mm of contact. No clearance — this is a bearing surface. | Tray: derived from bore diameters. Coupler: caliper-verified. |
| Narrow bore (center body sliding) | 9.5mm diameter | 9.31mm OD | 0.19mm diametric (0.095mm per side) | Tray: designed CAD value per synthesis.md. Coupler: caliper-verified. |
| Narrow bore exit lip (Shoulder 2 bearing) | Annular zone: I.R. = 4.75mm, available O.R. = 7.75mm (3.0mm annular width of material) | Shoulder 2 OD = 15.10mm (O.R. = 7.55mm) | Bearing annular width: 7.55 − 4.75 = 2.80mm of contact (within the 3.0mm annular material zone). | Tray: derived from bore diameters. Coupler: caliper-verified. |

**FDM calibration note (critical):** Per requirements.md, holes print smaller than designed by approximately 0.2mm. If the narrow bore prints at 9.3mm (designed 9.5mm − 0.2mm undersize), the as-printed clearance becomes (9.3 − 9.31) / 2 = −0.005mm per side — a near-press-fit that may resist coupler insertion or crack the bore wall. Print a test coupon with three bore diameters (9.5mm, 9.7mm, 9.9mm designed) before committing to the final pocket diameter. The large bore is less critical (0.40mm designed clearance; even 0.2mm undersize leaves 0.20mm per side clearance). See synthesis.md Open Question 1.

**Interface flag:** The narrow bore designed clearance (0.095mm per side) is below the 0.2mm minimum loose fit guidance in requirements.md. This is intentional — a snug radial fit is desired for gravity support and handling stability. The risk is that as-printed bore undersize converts a snug fit to a press fit. This must be resolved empirically before final print. No design gap, but a manufacturing verification requirement.

### Part 2 — Path continuity (coupler insertion path)

The insertion path is the sequence of geometric zones a coupler body end traverses from Z = 0 to full seating.

| Path | Segment | Z start | Z end | Bore diameter / coupler OD | Connects to next? |
|---|---|---|---|---|---|
| Coupler insertion | Large bore (body end 1) | Z = 0 | Z = +12.08mm | Bore: 15.5mm / Body end 1: 15.10mm | Yes — large bore terminates at bore shoulder |
| Coupler insertion | Bore shoulder transition | Z = +12.08mm | Z = +12.08mm | Annular step: 15.5mm outer → 9.5mm inner | Yes — step is at a single Z plane; narrow bore begins immediately at this Z |
| Coupler insertion | Narrow bore (center body) | Z = +12.08mm | Z = +15mm | Bore: 9.5mm / Center body: 9.31mm | Yes — narrow bore exits at far face (Z = +15mm) |
| Coupler insertion | Beyond far face (center body + Shoulder 2) | Z = +15mm | Z = +24.24mm | Open (no plate material) / Center body then Shoulder 2 | Yes — exits into open space; Shoulder 2 at +24.24mm cannot re-enter |

**Path continuity result:** No gaps. No obstructions. The bore shoulder at Z = +12.08mm creates a step-down in bore diameter from 15.5mm to 9.5mm. Body end 1 (15.10mm OD) cannot pass this step — that is the intentional +Z stop. The center body (9.31mm OD) does pass this step and continues through the narrow bore. The transition is geometrically continuous (no Z-axis gap between large bore end and narrow bore start — both are at exactly Z = +12.08mm).

**Path obstruction check — center body through far face:** The center body (9.31mm OD) must pass through the far face opening (9.5mm narrow bore exit). 9.31mm < 9.5mm. No obstruction. The center body exits the far face freely. Verified.

---

## 6. Assembly Feasibility (Rubric E)

**Can the coupler be physically inserted?**

Yes. The large bore opening (15.5mm) is larger than the body end OD (15.10mm) by 0.40mm diametrically. The assembler can enter body end 1 into the large bore without force-fitting. The coupler is then pushed in the +Z direction (into the plate). The center body (9.31mm OD) is smaller than the narrow bore (9.5mm ID), so it passes through without obstruction. This is confirmed in Rubric D Path Continuity above.

**Does the narrow bore block entry?**

The narrow bore (9.5mm) is at the far end of the large bore (Z = +12.08mm to Z = +15mm). The insertion sequence is: body end 1 enters large bore first. The center body does not encounter the narrow bore until body end 1 has already traveled 12.08mm into the plate. By that point the center body is aligned with the narrow bore and slides through. The narrow bore does not block entry — it only accepts the narrow center body, not the wide body ends. The wide body end 2 (15.10mm OD) is permanently blocked from entering the narrow bore (15.10mm > 9.5mm); this is the intended axial retention.

**Insertion direction:** Unambiguous. Only the stepped bore face (insertion face) accepts the coupler. The narrow bore face cannot accept a body end. The geometry self-documents the correct assembly orientation.

**Assembly sequence:**

1. Hold coupler tray insertion face up (large bore openings facing assembler).
2. Pick up one PP0408W coupler (either end first — symmetric).
3. Align body end with any pocket large bore opening.
4. Push coupler in +Z direction until body end 1 enters the large bore. (No force required — 0.20mm per side clearance.)
5. Continue pushing until center body contacts the narrow bore entry (at Z = +12.08mm). Slight resistance increase as center body enters 0.095mm/side snug fit.
6. Continue pushing until Shoulder 2 clears the far face (Z = +15mm). Coupler is captured. (Test coupon needed to characterize actual insertion force before final print — see Rubric D note.)
7. Repeat for remaining three pockets.

**Trapped parts?** No. The coupler tray is a single plate with no closures. All four pockets are accessible from the insertion face simultaneously throughout the assembly.

**Disassembly:** In Phase 1, the coupler is captured and not intended to be removed from a one-piece tray. Shoulder 2 (15.10mm OD) cannot re-enter the 9.5mm narrow bore. Disassembly of the coupler from a Phase 1 tray requires either destroying the tray or using a tool to push Shoulder 2 back through the narrow bore — this is not physically possible without deforming the coupler or the tray. This is acceptable for Phase 1 (test-fit vehicle, not a serviceable assembly). The Phase 3 two-piece split design will allow coupler insertion and removal from the final tray.

**DESIGN NOTE:** The Phase 1 coupler tray is a one-way assembly. Once a coupler is seated, it cannot be removed without destruction. This is consistent with Phase 1 scope (test fitting) and with the Vision's statement that the Phase 3 two-piece design is the final retention approach.

---

## 7. Part Count Minimization (Rubric F)

**Is this the minimum part count?**

Yes. The coupler tray is one printed part. The four couplers are off-the-shelf parts that seat in the pockets. No fasteners, adhesives, clips, or separate retention features are required for Phase 1.

**Are the couplers permanently joined to the tray?**

No. The couplers are captured by geometry (barbell shoulders bearing against bore features). They are not welded, glued, or press-fitted. They are loose-captured: axially retained by the pocket geometry, free to rotate about their bore axis. This is correct for Phase 1.

**Could the plate and couplers be combined into one printed part?**

No. The PP0408W is a commercial off-the-shelf push-to-connect fitting with an internal collet mechanism. It cannot be printed. It must be a separate part.

**Could any tray features be eliminated?**

The plate body is required (structural, provides material for the bore walls). The four stepped bores are required (physically necessary to capture the couplers — the minimum geometry that provides insertion access and bilateral axial retention from a one-piece plate, per synthesis.md Section 3.3). No features are redundant. Part count is minimized.

**Confirmation: no separate fasteners needed.** The bore shoulder geometry provides +Z stop; the far face exit lip provides −Z stop. No screws, pins, clips, or rings required.

---

## 8. FDM Printability (Rubric G)

### Step 1 — Print orientation

**Orientation: insertion face (Z = 0, large-bore openings) DOWN on the build plate.**

This places the bore axes vertical (parallel to the print Z axis = layer stack direction). The plate face is horizontal on the build plate.

**Why insertion face down (not far face down)?**

Two candidate orientations were considered:

- **Candidate A: Insertion face down (large bores down).** Bore axes vertical. The bore shoulder (annular step at Z = +12.08mm, which is 12.08mm up from the build plate) is a horizontal internal ledge bridging the bore step from R = 4.75mm to R = 7.75mm. Bridge span per side: 7.75 − 4.75 = 3.0mm. This bridges cleanly (3.0mm << 15mm limit). The insertion face bore rims are on the build plate face — elephant's foot mitigation chamfer applies here. This is the orientation stated in spatial-resolution.md and synthesis.md.

- **Candidate B: Far face down (narrow bores down).** Bore axes still vertical (same). The bore shoulder is now 2.92mm from the build plate (at Z = 2.92mm from build plate, measured from far face). The shoulder bridges from R = 4.75mm to R = 7.75mm, same 3.0mm span — same bridge quality. However, the bore entry is now at the top (open, not on the build plate), so elephant's foot does not affect the large bore rims. The far face bore rims (narrow, 9.5mm) are on the build plate — elephant's foot chamfer would apply to those instead.

- **Candidate C: Plate on edge (bore axes horizontal).** Bores become horizontal. The bore shoulder is now a vertical internal ledge — a 3.0mm wide annular overhang inside the bore. With horizontal bores, the top half of each bore shoulder is an unsupported overhang (material bridging across 9.5mm to 15.5mm, spanning the full bore diameter horizontally). Maximum unsupported span = bore diameter = 15.5mm at the large bore entrance and 9.5mm at the shoulder top. Per requirements.md: minimum unsupported bridge span < 15mm. The large bore horizontal span (15.5mm) exceeds the 15mm limit. Additionally, horizontal bores print with worse diameter accuracy than vertical bores (layer-stair-stepping on bore walls), which is problematic for the critical 9.5mm narrow bore. Candidate C is rejected: it violates the bridge span requirement and produces inferior bore geometry.

**Decision: Candidate A (insertion face down).** This is the orientation from the planning documents and is correct. The bore shoulder bridges cleanly at 3.0mm. Bore axes are vertical, producing the best diameter accuracy for the critical narrow bore. The only difference from Candidate B is that Candidate A puts elephant's foot risk at the large bore rims (where 0.40mm designed clearance provides margin) rather than the narrow bore rims (where 0.095mm/side clearance provides no margin). Insertion face down is therefore the safer choice: elephant's foot at the large bore is tolerable; elephant's foot at the narrow bore is not.

**Elephant's foot chamfer decision:** The insertion face (Z = 0) IS the build plate face. Per requirements.md: "If the bottom face is a mating surface, add a 0.3mm × 45° chamfer to the bottom edge." The insertion face is not a precision mating surface against another part (it is an open face — the coupler enters from this side). However, the bore rim at Z = 0 is the entry guide for the coupler body end during insertion. Elephant's foot at these rims would reduce the effective bore diameter for the first 0.2–0.3mm of Z, making the coupler harder to start. The 0.3mm × 45° chamfer is applied to the bore rim at Z = 0 on the insertion face. This is specified in spatial-resolution.md Section 3.5 and Section 3.6. Decision: **chamfer applies. Applied to all four large bore rims at Z = 0.**

### Step 2 — Overhang audit

Print orientation: insertion face (Z = 0) down. Layer stack runs in +Z direction (upward during print).

| Surface / Feature | Angle from horizontal in print orientation | Printable? | Resolution |
|---|---|---|---|
| Plate bottom face (insertion face, Z = 0) | 0° — horizontal, on build plate | OK — build plate contact |
| Plate top face (far face, Z = +15mm) | 0° — horizontal, fully supported from below | OK |
| Plate side walls (±X and ±Y faces, 80mm × 15mm and 50mm × 15mm) | 90° — vertical | OK — no overhang |
| Large bore walls (15.5mm cylinder, Z = 0 to Z = +12.08mm) | 90° — vertical cylinder walls | OK — vertical cylinder, no overhang |
| Bore shoulder (annular step at Z = +12.08mm, inner R = 4.75mm, outer R = 7.75mm) | 0° — horizontal annular surface, faces upward (+Z) | Bridge: span = 3.0mm per side (from narrow bore wall to large bore wall). 3.0mm << 15mm limit. | OK — bridge span within FDM limit |
| Narrow bore walls (9.5mm cylinder, Z = +12.08mm to Z = +15mm) | 90° — vertical cylinder walls | OK — vertical cylinder, no overhang |
| Bore rim chamfers (0.3mm × 45° at Z = 0) | 45° — exactly at the printable limit | OK — 45° chamfer is at the FDM overhang limit; printable |

**Overhang audit result: No problematic overhangs. The only non-trivial print feature is the bore shoulder bridge (annular horizontal ledge inside the bore). At 3.0mm span, it is well within the 15mm bridge limit and will print without support. No support material is required for any feature in this part.**

### Step 3 — Wall thickness check

| Location | Measured wall thickness | Minimum required (requirements.md) | Status |
|---|---|---|---|
| Large bore to plate edge, horizontal (X direction) | 1.25mm | 1.2mm structural | Marginal pass (+0.05mm) |
| Large bore to plate edge, vertical (Y direction) | 2.25mm | 1.2mm structural | Pass |
| Between vertical adjacent bores (A–B or C–D pair, Y direction) | 14.5mm | 1.2mm structural | Pass |
| Between horizontal adjacent bores (A–C or B–D pair, X direction) | 46.5mm | 1.2mm structural | Pass |
| Narrow bore exit lip annular width (far face, R = 4.75mm to R = 7.75mm) | 3.0mm | 1.2mm structural | Pass |
| Bore shoulder annular width (at Z = +12.08mm, same radial zone) | 3.0mm | 1.2mm structural | Pass |

**Wall thickness warning:** The 1.25mm wall at the large bore horizontal edge is a marginal pass (0.05mm above the 1.2mm minimum). If Phase 5 rail geometry requires reducing the plate width (currently 80mm), verify this wall does not drop below 1.2mm before any width change is made. The wall is 3 perimeters (0.4mm nozzle × 3 = 1.2mm) at the absolute minimum. No design change required at this phase; the warning is flagged for Phase 5.

### Step 4 — Bridge span check

| Bridge feature | Span | Limit | Status |
|---|---|---|---|
| Bore shoulder at Z = +12.08mm (annular horizontal ledge inside bore) | 3.0mm per side (from narrow bore wall to large bore wall, radially) | 15mm | Pass — 3.0mm is 20% of the 15mm limit |

No other horizontal unsupported spans exist in the part.

### Step 5 — Layer strength check

The coupler tray experiences no cyclic or high-stress loads during operation. Forces on the part are:

- Gravity on each seated coupler: approximately 5–10 g per coupler, acting in −Y direction. This is a radial load on the narrow bore walls (Y direction load on a Z-axis bore). The bore walls are layer lines in the XY plane — this load acts across layer lines, which is the weak direction for FDM. However, at 5–10 g per coupler and 3.0mm of narrow bore wall depth, the shear stress on the layer interfaces is negligible. No concern.
- Axial coupler retention forces (Z direction): act in the Z direction, parallel to the layer stack. Layer lines resist compression and tension along Z well (in-plane inter-layer bond is the strong direction for tensile loads). The bore shoulder must resist Shoulder 1 bearing force and the far face lip must resist Shoulder 2 bearing force. Both are compression loads on horizontal (XY-plane) surfaces — these are in the print plane, the strongest direction. No concern.

No snap-fit arms or flexing features exist in this part. Layer strength check is satisfactory for all features in the stated print orientation.

---

## 9. Feature List

Every feature described with: name, operation type (Add = material added to blank, Remove = material removed), exact dimensions, position in part local frame, and justification.

### Feature 1 — Plate Body

| Field | Value |
|---|---|
| Operation | Add (base body) |
| Shape | Rectangular prism |
| Width (X) | 80.0 mm (X: −40mm to +40mm) |
| Height (Y) | 50.0 mm (Y: −25mm to +25mm) |
| Depth (Z) | 15.0 mm (Z: 0 to +15mm) |
| Position | Origin at geometric center of insertion face; fills entire part envelope as stated |
| Justification | Physical necessity (structural): provides the plate body material for bore walls, shoulder bearing surfaces, and far face exit lips. Width 80.0mm and height 50.0mm are the minimum dimensions that maintain ≥ 1.2mm structural wall at all bore edges (see spatial-resolution.md Section 3.4). Depth 15.0mm provides 12.08mm of large bore depth (full body end length) plus 2.92mm of narrow bore depth (robust shoulder bearing with 2.80mm annular contact zone). |

### Feature 2 — Stepped Bore, Pocket A (Pump 1 Inlet)

| Field | Value |
|---|---|
| Operation | Remove (two-diameter stepped bore from Z = 0 to Z = +15mm) |
| Bore center (X, Y) | X = −31mm, Y = +15mm |
| Bore axis | Parallel to Z axis, through-bore from Z = 0 to Z = +15mm |
| Stage 1 — Large bore | Diameter: 15.5mm; Z extent: Z = 0 to Z = +12.08mm; depth: 12.08mm |
| Stage 2 — Narrow bore | Diameter: 9.5mm; Z extent: Z = +12.08mm to Z = +15mm; depth: 2.92mm |
| Bore shoulder | Annular step at Z = +12.08mm; inner radius 4.75mm; outer radius 7.75mm; annular width 3.0mm; face normal in −Z direction (faces insertion face) |
| Entry chamfer | 0.3mm × 45° at large bore rim, Z = 0 plane (insertion face / build plate face) |
| Justification | Physical necessity (structural + assembly): stepped bore geometry is the minimum feature set that allows coupler insertion from the insertion face and provides axial retention in both directions. See synthesis.md Section 3.3 for proof that no simpler geometry exists. Vision Section 4, Season 1, Phase 1, Item 3: "flat plate with holes/pockets for capturing 4 John Guest union couplers." |

### Feature 3 — Stepped Bore, Pocket B (Pump 1 Outlet)

| Field | Value |
|---|---|
| Operation | Remove (two-diameter stepped bore, identical profile to Feature 2) |
| Bore center (X, Y) | X = −31mm, Y = −15mm |
| Bore axis | Parallel to Z axis, through-bore from Z = 0 to Z = +15mm |
| All bore dimensions | Identical to Feature 2 (15.5mm large bore, 9.5mm narrow bore, 12.08mm / 2.92mm depths, bore shoulder at Z = +12.08mm, 0.3mm × 45° entry chamfer) |
| Justification | Physical necessity (assembly): one pocket per coupler. Pump 1 has two tube connections (inlet and outlet); two couplers required. |

### Feature 4 — Stepped Bore, Pocket C (Pump 2 Inlet)

| Field | Value |
|---|---|
| Operation | Remove (two-diameter stepped bore, identical profile to Feature 2) |
| Bore center (X, Y) | X = +31mm, Y = +15mm |
| Bore axis | Parallel to Z axis, through-bore from Z = 0 to Z = +15mm |
| All bore dimensions | Identical to Feature 2 |
| Justification | Physical necessity (assembly): one pocket per coupler. Pump 2 inlet connection. |

### Feature 5 — Stepped Bore, Pocket D (Pump 2 Outlet)

| Field | Value |
|---|---|
| Operation | Remove (two-diameter stepped bore, identical profile to Feature 2) |
| Bore center (X, Y) | X = +31mm, Y = −15mm |
| Bore axis | Parallel to Z axis, through-bore from Z = 0 to Z = +15mm |
| All bore dimensions | Identical to Feature 2 |
| Justification | Physical necessity (assembly): one pocket per coupler. Pump 2 outlet connection. |

---

## 10. Feature Traceability (Rubric H)

| Feature | Justification source | Specific reference |
|---|---|---|
| Plate body (Feature 1) | Physical necessity — structural | Load path: bore walls must have sufficient material to carry coupler weight and assembly push forces. Minimum wall 1.2mm at all bore edges per requirements.md Section 6. Plate thickness 15mm set by synthesis.md Section 5.1: 12.08mm (full body end seating) + 2.92mm (robust shoulder bearing lip). |
| Plate width 80mm | Physical necessity — structural | Minimum width to maintain 1.25mm wall at horizontal bore edge (bore center at ±31mm, bore radius 7.75mm, plate edge at ±40mm). Derivation in spatial-resolution.md Section 3.4. |
| Plate height 50mm | Physical necessity — structural | Minimum height to maintain 2.25mm wall at vertical bore edge (bore center at ±15mm, bore radius 7.75mm, plate edge at ±25mm). Derivation in spatial-resolution.md Section 3.4. |
| Plate depth 15mm | Physical necessity — structural | Large bore depth 12.08mm required to fully seat body end 1. Narrow bore minimum 0.8mm per requirements.md Section 6. 15mm chosen to give 2.92mm of narrow bore depth for robust Shoulder 2 retention. Synthesis.md Section 5.1. |
| Four stepped bores (Features 2–5) | Vision + physical necessity | Vision Section 4, Season 1, Phase 1, Item 3: "flat plate with holes/pockets for capturing 4 John Guest union couplers." Physical necessity (assembly): stepped bore is the minimum geometry that provides both insertion access and bilateral axial capture from a one-piece plate. See synthesis.md Section 3.3. |
| Large bore diameter 15.5mm | Physical necessity — assembly | 15.10mm coupler body end OD (caliper-verified) + 0.40mm diametric clearance for sliding fit per synthesis.md Section 3.5. Requirements.md Section 6: "Add 0.2mm to hole diameters for loose fit." 15.10 + 0.40 = 15.50mm. |
| Large bore depth 12.08mm | Physical necessity — assembly | Exactly the coupler body end length (caliper-verified: 12.08mm). Full body end seating ensures Shoulder 1 aligns with and bears against the bore shoulder. Synthesis.md Section 3.5. |
| Narrow bore diameter 9.5mm | Physical necessity — assembly | 9.31mm center body OD (caliper-verified) + 0.19mm diametric clearance (0.095mm per side) for snug sliding fit. Tight enough to support coupler radially under gravity; loose enough to allow coupler insertion. Synthesis.md Section 3.5. |
| Narrow bore depth 2.92mm | Physical necessity — assembly | Plate thickness (15mm) − large bore depth (12.08mm) = 2.92mm. Provides 2.80mm annular bearing zone for Shoulder 2 at far face. Synthesis.md Section 5.1. |
| Bore shoulder at Z = +12.08mm | Physical necessity — assembly | Hard stop for Shoulder 1 of coupler in +Z direction. Without this feature, the coupler slides fully through the plate (no +Z retention). The step (15.5mm → 9.5mm) is the minimum geometry that stops the 15.10mm OD Shoulder 1. |
| Entry chamfer 0.3mm × 45° at bore rim, Z = 0 | Physical necessity — manufacturing | Requirements.md Section 6: "If the bottom face is a mating surface, add a 0.3mm × 45° chamfer to the bottom edge." The insertion face is the build plate face. The bore rim at Z = 0 is on the build plate face. Elephant's foot would reduce the bore entrance diameter and obstruct coupler insertion. Chamfer mitigates this. |
| Bore center positions: (±31mm X, ±15mm Y) | Physical necessity — assembly | Locked to release plate fitting positions (spatial-resolution.md Section 3.1). Must align with the four PP0408W coupler positions in the assembled cartridge so the release plate collet contact faces and coupler tray bore axes are co-axial. If positions differ, the release mechanism cannot engage the collets. |
| Rectangular outer profile, no corner radii or edge features | Physical necessity — manufacturing | Phase 1 scope: simplest shape that occupies the correct space. Vision Section 2: "Internal components that the user never sees or touches should be the simplest geometry that works." No edge features are required by any functional or assembly constraint in Phase 1. Rail geometry (Phase 5) will add features when that constraint is known. |

**No unjustified features found.** All features trace to a specific vision line or a named physical necessity category.

---

## 11. Complete Dimension Reference

All dimensions in coupler tray local frame. Values from spatial-resolution.md Section 6.

**Plate body:**

| Dimension | Value |
|---|---|
| Width (X extent) | 80mm (−40mm to +40mm) |
| Height (Y extent) | 50mm (−25mm to +25mm) |
| Depth / thickness (Z extent) | 15mm (Z = 0 to Z = +15mm) |

**Bore center positions (at insertion face, Z = 0):**

| Pocket | X | Y | Function |
|---|---|---|---|
| A | −31mm | +15mm | Pump 1 Inlet |
| B | −31mm | −15mm | Pump 1 Outlet |
| C | +31mm | +15mm | Pump 2 Inlet |
| D | +31mm | −15mm | Pump 2 Outlet |

**Bore stage dimensions (identical for all four pockets):**

| Feature | Designed diameter | Z start | Z end | Depth |
|---|---|---|---|---|
| Large bore | 15.5mm | Z = 0 | Z = +12.08mm | 12.08mm |
| Bore shoulder (annular step) | Inner: 9.5mm / Outer: 15.5mm | Z = +12.08mm | — | — |
| Narrow bore | 9.5mm | Z = +12.08mm | Z = +15mm | 2.92mm |

**Entry chamfer (elephant's foot mitigation):**

| Feature | Dimension | Z position |
|---|---|---|
| Bore rim chamfer | 0.3mm × 45° | At Z = 0, bore rim on insertion face (build plate face) |

**Bore shoulder annular geometry:**

| Feature | Value |
|---|---|
| Inner radius | 4.75mm (half of 9.5mm narrow bore) |
| Outer radius | 7.75mm (half of 15.5mm large bore) |
| Annular width | 3.0mm |
| Face normal | −Z (faces toward insertion face) |

**Wall thicknesses at tightest points:**

| Location | Thickness | Minimum required | Status |
|---|---|---|---|
| Large bore to plate edge (X direction) | 1.25mm | 1.2mm | Marginal pass |
| Large bore to plate edge (Y direction) | 2.25mm | 1.2mm | Pass |
| Between vertical adjacent bores (Y direction) | 14.5mm | 1.2mm | Pass |
| Narrow bore exit lip (annular, far face) | 3.0mm width | 1.2mm | Pass |

---

## 12. Bill of Materials

### 3D-printed parts

| Part | Material | Qty |
|---|---|---|
| Coupler tray | PETG | 1 |

### Off-the-shelf parts seated in this tray

| Part | Specification | Qty |
|---|---|---|
| John Guest PP0408W 1/4" union coupler | White acetal copolymer, 1/4" OD, straight union, barbell profile | 4 |

No fasteners, adhesives, or additional hardware are required.

---

## 13. Open Questions and Design Gaps

**Open Question 1 (CRITICAL — from synthesis.md):** Narrow bore diameter empirical calibration. The 9.5mm designed narrow bore may print at 9.3mm (per requirements.md FDM undersize guidance), which would be a near-press-fit on the 9.31mm center body. Print test coupon with three bore diameters (9.5mm, 9.7mm, 9.9mm designed values) before committing to final pocket diameter. Resolve before printing the coupler tray.

**Open Question 2 (from synthesis.md):** Large bore depth tolerance. 12.08mm designed depth. Printer overshoot (12.28mm) would leave a 0.2mm axial gap — Shoulder 1 would not seat flush against the bore shoulder. This would not affect ejection retention (far face exit lip still captures Shoulder 2) but could allow 0.2mm of axial play. Acceptable for Phase 1.

**Open Question 3 (from synthesis.md):** Fitting position precision. The ±15mm vertical bore spacing (30mm total) is a working assumption from the release plate synthesis, not a caliper-verified measurement of the actual Kamoer KPHM400 tube connector exit positions. If the measured positions differ, both the release plate and the coupler tray must be updated together.

**DESIGN GAP noted in Rubric A:** Snap-through insertion force is not analytically characterized. The coupler must deform slightly (or the bore wall must flex) for Shoulder 2 to clear the 9.5mm exit bore (Shoulder 2 is 15.10mm OD — it cannot pass through a rigid 9.5mm bore unless the bore or shoulder deforms). Re-examination: Shoulder 2 emerges from the far face — it exits into open air, not through the bore. The narrow bore exit diameter is 9.5mm; the center body (9.31mm OD) passes through during insertion; Shoulder 2 (15.10mm OD) exits into free space on the far side. The shoulder does NOT need to pass back through the bore for capture — it is already on the far side once the coupler is seated. There is no snap-through. The coupler seats by pushing until Shoulder 2 clears Z = +15mm (far face). The insertion force is simply the friction of the center body (9.31mm OD) sliding through the narrow bore (9.5mm, 2.92mm deep) plus the resistance at the bore shoulder where Shoulder 1 contacts the step. No deformation required. **DESIGN GAP retracted — no gap. The assembly sequence is: push until Shoulder 2 emerges from far face. After that point, Shoulder 2 cannot re-enter the narrow bore and the coupler is captured.**

**Phase 3 note:** The Phase 1 one-piece stepped bore tray provides one-sided insertion and axial capture. Phase 3 will split the tray to allow bilateral shoulder retention (both shoulders accessible for final seated position). The Phase 3 agent should note that Phase 1 does physically capture the couplers with Shoulder 2 retention; the Phase 3 improvement is bilateral capture and the ability to remove and reinsert couplers for serviceability.
