# Enclosure Decomposition Analysis

**Date:** 2026-03-29
**Status:** Architecture Decision Complete
**Review:** Concept.md analyzed against step-generation.md, design-patterns.md, and snap-fit-design.md

---

## Decision: Pass Through (No Decomposition)

**Recommendation:** Both enclosure halves should be modeled and 3D-printed as **monolithic solid pieces**. No decomposition into sub-components is required or beneficial.

---

## Rationale

### Top Half (220 × 300 × 200 mm)

**Features (from concept.md):**
1. Exterior shell with 2-3 mm edge fillets
2. Horizontal seam recess (0.5-1.0 mm inset, continuous around perimeter)
3. 10 snap hook engagement points on seam face (cantilever beams, 20 mm length, 1.2 mm base tapered to 0.8 mm, 2.5 mm overhang, 0.8 mm fillet radius)
4. Bag cradle support geometry (internal platform for 2L bags at 35° diagonal orientation)
5. Bag constraint ribs (internal vertical ribs preventing bag movement)
6. Electronics mounting frame (back-top interior, 4-corner snap anchors)
7. Display mounting surfaces (front-interior with snap anchors for flush-mounted screens)
8. Air switch mounting surfaces (front-interior with snap anchors)
9. Internal structural ribs (wall deflection support, component mounting)
10. Funnel geometry (centered at front edge, top surface)

**Geometric paradigm:** **Single, unified extrude-and-cut paradigm**
- Base geometry: rectangular box (extrude 220 × 300 × 200 mm)
- All features are variations of extrude (add material) and cut (remove material)
- Snap geometry: cantilever beams are extruded from the seam face, then tapered; undercuts are pocketed cavities
- Mounting surfaces: all pockets and recesses created via cut operations
- Ribs: extruded from interior walls
- No revolves, sweeps, lofts, or helical features

**Feature interdependencies:** All features share the same origin, coordinate system, and reference planes. Snap hooks must align with the seam plane at Z=200 mm. Bag cradle must align with funnel centerline on the top surface. Mounting anchors must align with internal rib geometry. Moving any feature requires updating others — they cannot be modeled independently.

**Can a single CadQuery agent handle this?** YES
- Extrude the base box
- Apply fillets to all external edges (2-3 mm radius, including seam corners at 3-4 mm)
- Cut the horizontal seam recess (0.5-1.0 mm inset) as a continuous channel around the perimeter
- Create snap hook geometry: extrude cantilever beams from seam face, taper (1.2 mm to 0.8 mm), add fillet at base
- Cut mounting pockets for electronics, displays, air switch
- Add internal ribs via cut-and-extrude patterns
- Create bag cradle geometry via pocketed and extruded features
- Add funnel geometry (likely a depression or small boss with internal lip)

All these operations are standard CadQuery extrude/cut patterns. No advanced techniques required beyond what step-generation.md specifies for complex parts.

**Would decomposition help?**
- NO. The part is monolithic by design (concept.md Section 2 explicitly states "monolithic halves"). Splitting it would create:
  - Internal joins requiring alignment tolerance
  - Additional composition logic to reassemble sub-components
  - Loss of structural rigidity (internal ribs in one sub-component might not align with snap geometry in another)
  - More validation steps (interface boundaries, fit checks)

---

### Bottom Half (220 × 300 × 200 mm)

**Features (from concept.md):**
1. Exterior shell with 2-3 mm edge fillets
2. Horizontal seam recess (0.5-1.0 mm inset, continuous around perimeter)
3. 10 snap undercut cavities on seam face (female geometry to receive hooks from top half, 2.8 mm depth, accommodating 2.5 mm overhang + 0.3 mm tolerance)
4. Pump cartridge dock (snap-fitted mounting frame integral to bottom-half interior, 4 corner snaps anchoring the frame, 4 tube stub ports at correct spacing for quick-connects)
5. Valve manifold mounting frame (internal vertical ribs with 6-8 distributed snap anchors for valve assembly)
6. Port penetrations (back face: cold water inlet/outlet, tap water inlet, flavor outlets; 1/4" quick-connect recesses, 5-10 mm inset)
7. Internal structural ribs (support long wall spans, prevent bulging between snap points)
8. Bottom surface mounting feet or leveling pads (if required)

**Geometric paradigm:** **Single, unified extrude-and-cut paradigm**
- Base geometry: rectangular box (extrude 220 × 300 × 200 mm)
- All features are variations of extrude (add material) and cut (remove material)
- Snap undercuts: pocketed cavities in the seam face
- Pump cartridge dock: internal frame created via extrude/cut patterns, with snap anchors integral to the geometry
- Port penetrations: cylindrical bores (drilled/cut perpendicular to back face)
- Valve mounting frame: extruded ribs with snap anchor details
- Mounting feet: small protrusions on bottom surface (extrude or boss operations)
- No revolves, sweeps, lofts, or complex curves

**Feature interdependencies:** Identical to top half. All features share origin, coordinate system, and reference planes. Snap undercuts must align with snap hooks from top half (shared seam plane). Pump cartridge dock must align with valve mounting frame internally. Port penetrations must align with internal tubing stubs. These features cannot be modeled in isolation.

**Can a single CadQuery agent handle this?** YES
- Extrude the base box
- Apply fillets to all external edges (2-3 mm radius, including seam corners at 3-4 mm)
- Cut the horizontal seam recess (0.5-1.0 mm inset) as a continuous channel around the perimeter
- Create snap undercut cavities: pocketed into seam face, 2.8 mm depth, with lead-in angle for hook engagement
- Cut port penetrations: cylindrical bores (1/4" recessed 5-10 mm) on back face, with internal stubs for quick-connects
- Create pump cartridge dock: extrude internal frame with 4 corner snap anchors (integral geometry)
- Add valve manifold mounting frame: extrude ribs with 6-8 snap anchor details
- Add internal structural ribs: extruded bosses supporting wall deflection
- Create mounting feet: small protrusions on bottom surface

All standard CadQuery extrude/cut operations. No advanced techniques.

**Would decomposition help?**
- NO. Same reasoning as top half. The bottom half is also monolithic by design. Splitting would introduce alignment problems and overhead without benefit.

---

## Paradigm Classification Summary

| Aspect | Top Half | Bottom Half |
|--------|----------|-------------|
| **Primary paradigm** | Extrude-and-cut | Extrude-and-cut |
| **Advanced techniques** | None | None |
| **Revolved features** | None | None |
| **Swept features** | None | None |
| **Lofted features** | None | None |
| **Features share origin?** | YES | YES |
| **Features interdependent?** | YES | YES |
| **Monolithic by design?** | YES (concept.md) | YES (concept.md) |

---

## Composition Specification (Not Required, but Documented)

**If this decision is revisited:** The only plausible decomposition would be based on **functional regions** rather than geometric paradigms:

### Hypothetical Top Half Sub-Components (Not Recommended)
1. **Main structural shell:** Rectangular box + edge fillets + seam recess
2. **Snap engagement surface:** 10 snap hooks with beam geometry
3. **Bag cradle assembly:** Support platform + constraint ribs + funnel
4. **Electronics mounting frame:** Rear-top mounting points

**Problem:** Sub-components would require:
- Internal join interfaces (seam between shell and snap surface)
- Alignment tolerance between snap geometry and snap face
- Separate validation that sub-components assemble correctly
- More CAD assembly steps than the monolithic approach

**Conclusion:** Monolithic approach is simpler and more reliable.

---

## CadQuery Agent Capability Analysis

Per step-generation.md Section 6 (CadQuery Techniques), a single agent can handle:

✓ **Geometry this part uses:**
- Box creation with `centered=False` positioning
- Extrude operations with `extrude(positive)` and `extrude(negative)`
- Cut operations via `cut()` Boolean
- Fillet operations via `fillet(radius)`
- Chamfer operations via `chamfer(length, angle)`
- Pocket creation via workplane shifts and negative extrusions
- Boss creation via positive extrusions
- Rib patterns via workplane translation and extrude

✗ **Advanced geometry this part does NOT require:**
- Revolves (no rotational symmetry features)
- Sweeps (no paths along curves)
- Lofts (no blended surfaces)
- Helical features (no threads or spirals)

**Verdict:** A single CadQuery agent working with extrude-and-cut can model either enclosure half without hesitation.

---

## Manufacturing and Assembly Implications

**Monolithic approach (recommended):**
- ✓ Single print job per half (no secondary assembly)
- ✓ No internal joints or interfaces
- ✓ Structural integrity guaranteed (no split points)
- ✓ Simplified snap-fit validation (entire snap geometry is one solid)
- ✓ Simpler tolerance stack (no cumulative errors from sub-assembly)

**Decomposed approach (not recommended, documented for reference):**
- ✗ Multiple print jobs per half (additional prints, waste)
- ✗ Requires sub-assembly before final enclosure closure
- ✗ Internal joints add potential failure points
- ✗ Snap geometry split across multiple pieces (harder to validate)
- ✗ Tolerance stack becomes cumulative (sub-component alignment + final assembly)

---

## Design Consistency Verification

This decomposition analysis is consistent with:

1. **Concept.md Section 1 (Decomposition Rationale):** "Monolithic halves, not sub-components... Each half is a single rigid shell with no internal joins."

2. **Concept.md Section 2 (Snap-fit Efficiency):** "All interior components snap to the **inner surfaces** of the two halves. No internal sub-components require snaps to the walls."

3. **Concept.md Section 4 (Service Access):** "Pump cartridge dock (snap-fitted mounting frame integral to the bottom-half interior)." → Integral means monolithic.

4. **Snap-fit-design.md Section 11.1:** Treats each half as a single solid with snap geometry integral to the part.

5. **Step-generation.md:** Assumes parts can be modeled as single CadQuery solids with all features in one script.

6. **Requirements.md (FDM Constraints):** No mention of assembling sub-components; assumes monolithic printing.

---

## Unknowns and Dependencies for Downstream Steps

**For Step 4 (CAD Implementation):**

1. **Snap hook orientation:** Concept.md specifies snap arms must print parallel to the XY-plane for strength. The CAD model must ensure snap geometry is oriented this way when the half is placed on the print bed with seam face horizontal.

2. **Internal rib placement:** The bag cradle ribs and valve mounting ribs must be positioned to avoid interfering with other mounting points. This requires careful spatial planning during CAD (not a decomposition issue, but important for the agent).

3. **Port penetration tubing stubs:** The quick-connect stubs on the bottom-half interior must be designed to align with pump cartridge quick-connect ports (spacing and orientation). Reference geometry from the pump cartridge CAD is required.

4. **Seam face flatness:** The snap hooks and undercuts must have perfectly aligned seam faces (within ±0.1 mm tolerance, per snap-fit-design.md) so the two halves mate flush. The CAD model must ensure this flatness is built into the base geometry.

5. **Support geometry for snap hooks:** Per requirements.md, snap hook undercuts require intentional support ribs (0.3 × 0.8 mm, 0.2 mm interface gap). The CAD model should include these supports as part of the design, or the slicer will auto-generate them (with risk of poor removal).

**For Step 4b (Test Prints):**

1. **Snap geometry validation:** Print individual snap hook test specimens to confirm assembly force (40-50 N per snap) and seating resistance (>80 N per snap post-assembly).

2. **Seam gap tolerance:** After first half-assembly test, measure snap undercut depth and adjust ±0.1-0.2 mm if needed to achieve 1.2 mm ±0.1-0.2 mm nominal seam gap.

3. **Rib strength:** Verify internal ribs support wall spans without visible deflection under component mounting loads.

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Decompose Top Half?** | NO |
| **Decompose Bottom Half?** | NO |
| **Geometric paradigm** | Single: Extrude-and-cut (both halves) |
| **Feature interdependencies** | High (all features share origin and reference planes) |
| **CadQuery capability** | Sufficient (no advanced techniques required) |
| **Decomposition overhead** | Would exceed benefit (internal joins, alignment, tolerance stack) |
| **Design vision alignment** | Monolithic by design (concept.md explicit) |
| **Manufacturing simplicity** | Single print per half; no sub-assembly |

---

## Next Step

Proceed directly to Step 4 (CAD Implementation) with both halves as monolithic CadQuery models. Each half will be a single STEP file generated by a single CadQuery script.

---

**Document Status:** Complete
**Review:** Verified against concept.md, snap-fit-design.md, step-generation.md, design-patterns.md, requirements.md, and vision.md
**No conflicts identified.**
