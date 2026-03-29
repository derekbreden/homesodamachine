# Cradle Platform — Decomposition Decision

**Date:** 2026-03-29
**Input:** `hardware/printed-parts/bag-frame/planning/concept.md` (Sections 1, 7)
**Decision:** Pass through as a single part. No decomposition.

---

## Feature Inventory

Every feature from the concept description, accounted for:

| # | Feature | Geometric operation | Paradigm |
|---|---|---|---|
| 1 | Lens-shaped bowl body | Arc profile extruded along 287 mm bag axis | Prismatic sweep (2.5D) |
| 2 | Side lips (both long edges) | Rectangular profile extruded along same 287 mm axis | Prismatic sweep (2.5D) |
| 3 | Structural ribs × 3 (underside) | Rectangular profile extruded along same 287 mm axis | Prismatic sweep (2.5D) |
| 4 | Cap-end pocket (~38 mm ID × ~50 mm deep) | Circle subtracted along pocket axis at the cap end of the body | Cylindrical cut (2.5D subtract) |
| 5 | Tube exit hole (10–12 mm) | Circle subtracted through pocket rear wall | Cylindrical cut (2.5D subtract) |
| 6 | Snap tabs × 4 (inboard long edge) | Rectangular arm extruded perpendicular to lip face; hook profile cut on tip | Prismatic extrude + cut (2.5D) |
| 7 | Floor-to-lip interior fillet (3 mm) | Edge treatment on interior concave corners | Fillet operation |
| 8 | Lip top edge fillet (1.5 mm) | Edge treatment on lip top edge perimeter | Fillet operation |
| 9 | Outer lip rebate for cap snap arms (1.2 mm × 1.2 mm) | Rectangular channel subtracted along the lip outer face | Prismatic cut (2.5D) |

All 9 features accounted for. All appear in this single part. No feature is orphaned.

---

## Paradigm Analysis

**The question:** Does the cradle platform combine features from fundamentally different geometric paradigms?

**The answer:** No. Every feature is prismatic — it is produced by sketching a profile on a plane and extruding or subtracting along a single axis.

- Features 1–3 share the same sweep axis (the 287 mm bag axis, Z when printing on-end). They are all longitudinal extrusions and form the core body in one modeling pass.
- Features 4 and 5 are cylindrical subtracts. A cylinder in CadQuery is a circle extruded along a perpendicular axis — this is a standard 2.5D operation, not a rotational/revolved paradigm. The cap-end pocket is no different from drilling a hole in a plate: one workplane, one sketch, one extrude-cut. It does not introduce a lathe-turned solid or a surface-of-revolution into the model.
- Feature 6 (snap tabs) is a prismatic cantilever arm — an extruded rectangle with a small hook cut at the tip. The flex direction being in the X/Y plane (satisfied by the on-end print orientation) is a constraint on orientation, not a change in geometric paradigm.
- Features 7–9 are edge treatments and a shallow channel cut — all standard operations in the same paradigm.

No feature requires a helical sweep, a complex surface of revolution, a lofted transition between dissimilar profiles, or any geometry outside the extrude-and-cut toolset. The step generation document defines "2.5D" as the ability to derive a feature by sketching a profile and sweeping it along a straight path. Every feature on this part fits that definition.

---

## Interdependence Analysis

The features are not merely co-paradigm — they are geometrically continuous with each other. The body (Feature 1), the lips (Feature 2), and the ribs (Feature 3) all share the same extrusion axis and are generated in a single sweep pass or as immediate additions to the same base body. The cap-end pocket (Feature 4) is a void carved into the lower terminus of that continuous body — it is not a separate cylinder attached to a plate, it is a removal from the bowl that is already there. Separating the pocket from the bowl body would require an arbitrary transverse split plane cutting through a continuous curved surface, producing a seam with no geometric motivation.

The snap tabs (Feature 6) are integral to the inboard lip (Feature 2). Their flexure depends on their connection to the lip wall. Splitting them into a separate sub-component would require defining an interface at a structural root, which is the worst possible place to introduce a joint.

The outer lip rebate (Feature 9) is a cut into the lip face — it cannot be assigned to a separate part without assigning the lip to that part as well, which is the bowl body itself.

**There are no natural geometric boundaries within this part.** Every feature is attached to a feature that is attached to the core body. The topology forms a single connected tree rooted at the bowl extrusion.

---

## Print Orientation Compatibility

The on-end print orientation (287 mm = Z, cap pocket at bottom) allows all features to build without support:

- Longitudinal ribs, lips, and snap tabs are vertical walls in X/Y.
- The cap-end pocket opens downward from the bottom face — built cavity-upward as the print progresses from the pocket bottom toward the open top.
- The tube exit hole (10–12 mm circle through the pocket rear wall) bridges horizontally across the pocket wall. At 10–12 mm diameter, this is within the 15 mm bridge limit from requirements.md and requires no support.

No feature in this part requires a different print orientation from any other feature. The entire part is coherent in a single print setup.

---

## Decision

**Pass through as a single part.**

The cradle platform is a single-paradigm part (extrude-and-cut throughout). Its features are geometrically continuous and structurally interdependent. No natural boundary exists that would motivate a split. Decomposing it would create artificial interfaces inside continuous geometry, orphan structurally critical features across a seam, and add assembly complexity without mechanical benefit.

A single CadQuery generation agent receives this part as its input and produces one STEP file. The modeling sequence follows directly from the feature inventory:

1. Extrude the arc (lens) profile along the 287 mm bag axis → base bowl body
2. Add side lips along both long edges (same sweep axis)
3. Add three longitudinal ribs on the convex underside (same sweep axis)
4. Subtract the cylindrical cap-end pocket at the lower terminus
5. Subtract the tube exit hole through the pocket rear wall
6. Add four snap tab cantilever arms to the inboard lip face
7. Subtract the hook profiles at snap tab tips (or add via frangible bridge geometry per requirements.md)
8. Subtract the outer lip rebate along both lip outer faces
9. Apply 3 mm interior fillets at floor-to-lip corners
10. Apply 1.5 mm fillets to lip top edges

This is a linear, single-agent modeling sequence. No handoff. No sub-component interface. No composition step needed.
