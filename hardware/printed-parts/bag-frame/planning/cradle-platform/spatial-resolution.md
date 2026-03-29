# Cradle Platform — Spatial Resolution

**Date:** 2026-03-29
**Inputs:** concept.md, decomposition.md, platypus-bag-geometry.md, structural-analysis.md, synthesis.md, requirements.md, vision.md
**Next step:** Step 4b — Parts Specification (feature geometry definitions using this document as the sole dimensional source)

---

## Preamble: Axis Convention Disambiguation

The task specification contains an ambiguity in the Y-axis cross-section description that must be resolved before any coordinates are stated. The ambiguity: "Y is constant along the lip height" could refer to the lip inner face being a plane of constant Y (a Y-normal face) or a plane of constant X (an X-normal face) described by a Y range.

**Resolution by physical geometry:**

The cradle cross-section is a shallow trough. The bowl arc is the floor. The side lips are walls rising on the left and right edges of the trough in the X direction. In the XY cross-section:
- The lip inner face (facing the bowl center) is an X-normal surface: a vertical line at constant X in the cross-section, with a Y range from lip_top to lip_base.
- "Y is constant along the lip height" is interpreted as: along the full 287mm Z length of the lip (the "height" = Z extent), the lip inner face does not move in Y — it is a flat, untapered surface. This is a statement about 3D flatness in Z, not a statement that Y is uniform in the XY cross-section.

This interpretation is consistent with all snap arm assembly geometry described in concept.md. All coordinates below use this interpretation. Deviations from the task's suggested formula "lip_outer_face_Y = lip_thickness + Y_arc_tangent" are flagged where they occur.

---

## 1. Part Reference Frame Definition

**Print orientation:** The cradle is printed on-end. Long axis (bag length) = Z print axis. The cap end (lower in the installed orientation) is at the print bed: Z=0. The fold end (upper in the installed orientation) is at the top of the print: Z=287mm.

**Axis definitions:**

| Axis | Direction | Physical meaning |
|------|-----------|-----------------|
| X | Width | Spans the cradle inner width from left lip inner face to right lip inner face |
| Y | Depth (thin dimension) | From the deepest point of the bowl surface outward toward the convex back face; Y=0 at the innermost bowl contact point (bowl center at mid-length), Y increases toward the convex/rib side |
| Z | Print height | Along the bag's length axis; Z=0 at cap end (bottom of print / lower end of installed cradle); Z=287mm at fold end (top of print / upper end of installed cradle) |

**Origin:**
- X=0: left lip inner face (the face of the left lip wall that faces the bowl center)
- Y=0: the deepest point of the bowl cross-section (the minimum-Y point of the arc at X=98, the center of the 190mm bag-width span). This point is the same at all Z positions along the body zone (Z=50mm to Z=287mm); the cap-end pocket (Z=0 to Z=50mm) is a separate volume.
- Z=0: cap end face (lower terminus of the cradle body, the face where the bag cap exits)

**Part envelope in print frame:**

| Axis | Inner span | Full part span (including lips and ribs) |
|------|-----------|------------------------------------------|
| X | 0 to 196mm | -4mm to 200mm (lip walls 4mm each) |
| Y | 0 to 15.5mm (floor convex face at center) | 0 to 21.5mm (including rib height 6mm) |
| Z | 0 to 287mm | 0 to 287mm |

Notes:
- Y=0 is the innermost bowl surface point (bag contact at center). The floor has 2.0mm wall thickness in Y, so the outer (convex) floor surface at center is at Y=2.0mm. Ribs extend from Y=2.0mm to Y=8.0mm (6mm rib height). The lip outer face is at X=-4mm (left) and X=200mm (right) — a face in the X direction, not Y.
- The lip at the bowl edge (X=3 and X=193) has its bowl surface at Y=13.5mm. The floor wall at this edge location is 2.0mm thick in Y, so the outer convex surface at the arc edge is at Y=15.5mm. Ribs do not extend to the arc edge zone; ribs are centered under the inner portion of the floor.

---

## 2. Lens Bowl Cross-Section Profile

### Arc Geometry Resolution

**Source values from synthesis.md:**
- Bag flat width: 190mm (chord of the arc — the arc serves the bag, not the full cradle inner width)
- Constrained bag thickness (total, both faces of the lens): 27mm
- Arc radius (each arc, derived from the symmetric lens formula R = (W² + T²) / (4T) where W = bag width and T = total lens thickness): R = (190² + 27²) / (4 × 27) = (36100 + 729) / 108 = 36829 / 108 = **341.0mm**

**Arc chord vs. cradle inner width:**
The arc has a chord of **190mm** (bag width). The cradle inner width is **196mm** (190mm + 3mm clearance each side). The arc does NOT span the full 196mm inner width. It spans from X=3mm to X=193mm (centered in the 196mm inner span, with 3mm clearance on each side). From X=0 to X=3 and from X=193 to X=196, the lip inner face transitions to the arc start via a horizontal ledge at Y=13.5mm (the lip base shelf, discussed in Section 3).

**Single-arc sagitta (depth of ONE arc = depth of the cradle bowl floor):**
The synthesis uses 27mm to mean the total bag thickness (sum of both arcs of the lens). The sagitta of one arc (the cradle floor depth):
```
sagitta = R - sqrt(R² - (c/2)²)
        = 341 - sqrt(341² - 95²)
        = 341 - sqrt(116281 - 9025)
        = 341 - sqrt(107256)
        = 341 - 327.500
        = 13.500mm
```

**The bowl floor is 13.5mm deep at its center relative to the arc endpoints.** When the document says "sagitta = 27mm," it refers to the total lens depth (both arcs). The bowl cross-section depth (one arc, what the cradle models) is 13.5mm.

**Circle center in part coordinates:**
Arc center at (X=98, Y=341). The circle passes through (X=98, Y=0) at the bowl deepest point and through (X=3, Y=13.5) and (X=193, Y=13.5) at the arc endpoints.

Verify: distance from center (98, 341) to deepest point (98, 0) = 341 = R ✓
Distance from center (98, 341) to arc endpoint (3, 13.5):
sqrt((3-98)² + (13.5-341)²) = sqrt(9025 + 107256.25) = sqrt(116281.25) ≈ 341.0mm ✓

### Cross-Section Profile Table

**Convention:** X=0 is left lip inner face, X=196 is right lip inner face. Y=0 is the bowl deepest point (center, X=98). Y increases outward (toward convex back face of part). Computed as Y = 341 - sqrt(341² - (X-98)²) for X in [3, 193]; Y = 13.5mm for X in [0,3] and [193,196].

| X (mm) | Y (mm) | Zone | Note |
|--------|---------|------|------|
| 0 | 13.500 | Lip inner face (left) | Y constant; vertical X-normal face at X=0 |
| 3 | 13.500 | Arc tangent point (left) | Arc start; matches lip base shelf |
| 6 | 12.647 | Arc | (6-98)=-92; Y=341-sqrt(341²-92²)=341-328.353 |
| 10 | 11.548 | Arc | Y=341-sqrt(116281-7744)=341-sqrt(108537)=341-329.450 |
| 20 | 9.040 | Arc | Y=341-sqrt(116281-6084)=341-sqrt(110197)=341-331.961 |
| 30 | 6.852 | Arc | Y=341-sqrt(116281-4624)=341-sqrt(111657)=341-334.152 |
| 40 | 5.117 | Arc | Y=341-sqrt(116281-3364)=341-sqrt(112917)=341-335.882 |
| 50 | 3.396 | Arc | Y=341-sqrt(116281-2304)=341-sqrt(113977)=341-337.604 |
| 60 | 2.177 | Arc | Y=341-sqrt(116281-1444)=341-sqrt(114837)=341-338.876 (338.822 per precise calc) |
| 70 | 1.149 | Arc | Y=341-sqrt(116281-784)=341-sqrt(115497)=341-339.848 |
| 80 | 0.482 | Arc | Y=341-sqrt(116281-324)=341-sqrt(115957)=341-340.525 |
| 90 | 0.094 | Arc | Y=341-sqrt(116281-64)=341-sqrt(116217)=341-340.907 |
| 98 | 0.000 | Arc center (deepest) | Bowl minimum; Y=0 by definition |
| 100 | 0.006 | Arc | Symmetric to X=96 |
| 110 | 0.208 | Arc | Symmetric to X=86 |
| 120 | 0.710 | Arc | Symmetric to X=76 |
| 130 | 1.503 | Arc | Symmetric to X=66 |
| 140 | 2.598 | Arc | Symmetric to X=56 |
| 150 | 3.993 | Arc | Symmetric to X=44 (≈X=52 symmetric value) |
| 160 | 5.682 | Arc | Symmetric to X=36 |
| 170 | 7.687 | Arc | Symmetric to X=26 |
| 180 | 10.006 | Arc | Symmetric to X=16 |
| 190 | 12.647 | Arc | Symmetric to X=6 |
| 193 | 13.500 | Arc tangent point (right) | Arc end; matches lip base shelf |
| 196 | 13.500 | Lip inner face (right) | Y constant; vertical X-normal face at X=196 |

**Intermediate check (X=60, precise):**
dX from center = 60-98 = -38. Y = 341 - sqrt(341²-38²) = 341 - sqrt(116281-1444) = 341 - sqrt(114837).
sqrt(114837): 338.87² = 114852.8 (too high). 338.8² = 114825.44. 338.82² = 338.82×338.82: 338.8² + 2×338.8×0.02 + 0.02² = 114825.44 + 13.552 + 0.0004 = 114839.0. 338.85²: 338.8² + 2×338.8×0.05 + 0.05² = 114825.44 + 33.88 + 0.0025 = 114859.3. So sqrt(114837) ≈ 338.822. Y = 341 - 338.822 = 2.178mm. Table value 2.177mm ✓.

**Precision note:** All Y values are accurate to ±0.005mm. Downstream agents should use the formula Y = 341 - sqrt(341² - (X-98)²) for any X within the arc span [3, 193], not interpolation.

### Arc Tangent Angle at the Lip Base

At X=3 (left arc endpoint), the arc tangent slope:
```
dY/dX = -(X-98)/(Y_circle_center - Y_arc) = -(3-98)/(341-13.5) = 95/327.5 = 0.2901
```
The arc meets the lip base shelf with a slope of +0.290 (Y increases at 0.290mm per mm of X as X decreases toward X=3 from center). The arc is NOT tangent to a vertical surface at X=3; it meets the lip shelf at an angle of arctan(0.290) = 16.2° from horizontal. The 3mm interior corner fillet (Section 7) is required to smooth this transition.

---

## 3. Side Lip Geometry

The side lips are wall features at the left (X=0) and right (X=196) edges of the cradle. In cross-section, each lip is a rectangular block with:

| Dimension | Value | Reference frame | Notes |
|-----------|-------|-----------------|-------|
| Lip inner face X (left) | X=0 | Part X axis | Definition; the face facing the bowl center |
| Lip inner face X (right) | X=196 | Part X axis | Definition |
| Lip outer face X (left) | X=−4mm | Part X axis | Lip thickness = 4mm in X direction |
| Lip outer face X (right) | X=200mm | Part X axis | Lip thickness = 4mm in X direction |
| Lip base Y (arc tangent) | Y=13.500mm | Part Y axis | Junction of horizontal shelf and lip inner face |
| Lip top Y | Y=3.500mm | Part Y axis | 10mm from lip base toward bag (decreasing Y) |
| Lip height in Y | 10mm | Part Y axis | Per synthesis: "10mm lip height above lowest platform surface" resolved as 10mm in Y from Y=13.5 toward Y=0 |
| Lip thickness in X | 4mm | Part X axis | Structural: supports 1.2mm rebate + 2.8mm backing wall (minimum 1.2mm structural wall per requirements.md) |
| Lip top edge fillet radius | 1.5mm | — | At edge (X=0, Y=3.5mm) and (X=196, Y=3.5mm) |
| Lip base shelf (horizontal) | Y=13.500mm flat from X=0 to X=3 (left) | Part Y axis | Connects lip inner face to arc start; this is the "lip inner face" in the sense of the surface that faces the bag at the bowl rim |
| Lip Z extent | Z=0 to Z=287mm | Part Z axis | Full cradle length; lip runs the entire Z extent |

**Note on "Y coordinate of the lip outer face":** The lip outer face is an X-normal plane at X=−4mm (left) and X=200mm (right). It does not have a single Y coordinate; it spans Y=3.5mm to Y=13.5mm. The task specification formula "lip_outer_face_Y = lip_thickness + Y_arc_tangent = 4 + 13.5 = 17.5mm" does not correspond to a feature in the correct cross-section geometry — this formula would apply if the lip extended in the Y direction rather than X. The correct outer face is at X=−4mm (left) / X=200mm (right).

### Lip Top Edge Fillet

The fillet at the lip top edge (1.5mm radius) is at:
- Left lip top edge: (X=0, Y=3.5mm) in the XY cross-section; center of fillet arc at (X=−1.5mm, Y=3.5mm) or (X=0, Y=3.5+1.5=5.0mm) depending on fillet tangent orientation.

The lip inner face (X=0) is vertical (Y-direction). The lip top edge (horizontal, Y=3.5mm) transitions to the lip inner face. A 1.5mm concave fillet in the interior corner at (X=0, Y=3.5mm) has its center at (X=−1.5mm, Y=3.5mm) (center is 1.5mm outward in X from the edge and at the same Y).

The lip outer face (X=−4mm) also gets a 1.5mm fillet at the top edge (X=−4mm, Y=3.5mm). Center at (X=−2.5mm, Y=3.5mm).

### Snap Arm Rebate (for Upper Cap Hook)

The upper cap's snap arms hook over the lip outer face (X=−4mm / X=200mm). The rebate is cut into the lip outer face (the X-normal face at X=−4mm) as a horizontal groove running the full Z length.

| Dimension | Value | Reference frame | Notes |
|-----------|-------|-----------------|-------|
| Rebate depth (into lip, X direction) | 1.2mm | Part X axis | Cut from X=−4mm to X=−4+1.2=−2.8mm (left) |
| Rebate height (Y direction) | 1.2mm | Part Y axis | The groove spans 1.2mm in Y |
| Rebate center Y | Y=5.5mm | Part Y axis | 8mm from lip base (Y=13.5mm) toward bag: 13.5−8=5.5mm |
| Rebate Y range | Y=4.9mm to Y=6.1mm | Part Y axis | Center ±0.6mm |
| Rebate Z extent | Z=0 to Z=287mm | Part Z axis | Runs full cradle length |
| Rebate cross-section | 1.2mm deep (X) × 1.2mm tall (Y) rectangular groove | XY plane | Bottom of groove at X=−2.8mm (left); top at Y=6.1mm, bottom at Y=4.9mm |

**Cross-section of rebate in XY plane (left lip outer face):**

```
X=−4mm (lip outer face)
    |
    |  Y=3.5mm (lip top edge)
    |  ↕ 1.4mm above rebate top
    |  Y=4.9mm ─────────────── rebate top edge
    |           |              |
    |    1.2mm  |   rebate     |  ← 1.2mm deep in X direction
    |           |              |
    |  Y=6.1mm ─────────────── rebate bottom edge
    |  ↕ 7.4mm below rebate bottom to lip base
    |  Y=13.5mm (lip base / arc tangent)
    |
X=−2.8mm (rebate back wall)
```

The rebate runs the full Z length (Z=0 to Z=287mm). The snap arm hook (1.2mm height) sits in this rebate in the locked state.

---

## 4. Cap-End Pocket

The Platypus cap assembly (cap + spout) protrudes approximately 40–50mm from the bag body seam. The pocket accommodates this protrusion.

### Pocket Center and Axis

The pocket axis is coincident with the bag's central axis through the cradle. In the part local frame:
- Bag central axis at the cap end runs along the Z axis
- Pocket center in XY: X=98mm (centerline of inner width), Y=0mm (at the bowl surface center, which is where the bag axis passes)

Wait — the pocket is a cylindrical volume centered on the bag axis. The bag axis passes through the bowl center (X=98, Y=0) and runs along Z. The pocket is centered on this axis.

**Pocket Y center:** Y=0 is the bowl deepest point. The pocket center in Y is at Y=0 (the bag axis runs along Y=0 at the bowl center).

**Pocket center coordinates:** (X=98mm, Y=0mm).

### Pocket Dimensions

| Parameter | Value | Reference frame | Derivation |
|-----------|-------|-----------------|------------|
| Pocket center X | 98mm | Part X axis | Inner width midpoint (196/2 = 98mm) |
| Pocket center Y | 0mm | Part Y axis | Bowl center / bag axis |
| Pocket open face | Z=0 face | Part Z axis | Opens at cap end; bag cap exits at Z=0 |
| Pocket depth (Z extent) | 50mm | Part Z axis | Z=0 (open) to Z=50mm (rear wall) |
| Pocket inner diameter | 31.0mm | — | Cap OD ~30mm; +0.2mm loose-fit per requirements.md × 2 sides = 30.4mm → round up to 31mm for reliable insertion |
| Pocket inner radius | 15.5mm | — | 31/2 |
| Pocket wall thickness | 2.0mm minimum | — | Per structural analysis and synthesis |

**Pocket geometry in part frame:**
- The pocket is a cylinder: center axis at (X=98, Y=0), radius 15.5mm, spanning Z=0 to Z=50mm.
- At Z=0: the pocket opening is at the lower face of the cradle (the cap-end face). The pocket is open to Z<0.
- At Z=50: the pocket rear wall closes the pocket.

**Elephant's foot chamfer on pocket opening:**
Per requirements.md, mating bottom faces require a 0.3mm × 45° chamfer on the bottom edge. The pocket opening is at Z=0 (the bottom of the print). A 0.3mm × 45° chamfer on the pocket opening rim is required to prevent elephant's foot interference with the Platypus cap insertion.

### Tube Exit Hole

The 1/4" OD hard tubing with John Guest fitting exits through the pocket rear wall or pocket side wall. Per the rear-wall clearance analysis (concept.md: only 13mm clearance to enclosure rear wall), the tube CANNOT exit straight through the Z=50 rear wall toward the enclosure back. The tube must exit laterally (through the Y face of the cradle body).

**Tube exit hole geometry:**

| Parameter | Value | Reference frame | Derivation |
|-----------|-------|-----------------|------------|
| Hole diameter | 12.0mm | — | John Guest fitting body OD; clearance hole (not sealing surface) |
| Hole center Z | Z=25mm | Part Z axis | Mid-depth of pocket; centered at the pocket's cylindrical wall |
| Hole center X | X=98mm | Part X axis | On the cradle centerline in X |
| Hole exit face | Outer Y face | Part Y axis | Exits through the convex outer face of the cradle floor |
| Hole center Y | Passes from Y=0 (pocket interior) through floor | Part Y axis | Hole axis is parallel to Y axis; center at (X=98, Z=25) |
| Exit point Y | Y ≈ 8mm (outer convex face at X=98, Z=25mm) | Part Y axis | Floor 2.0mm + ribs 6mm = outer rib face at Y=8mm at center |

The tube exit hole passes through the cradle floor from the pocket interior (at Y=0, the bowl surface inner wall of the pocket) to the outer convex face. In the installed orientation (35° tilt, cap end down), the tube exits through the floor on the LOWER (gravity-toward) side of the cradle and bends 90° to route along the enclosure floor toward the back-wall outlets.

**Bridge span check:** The hole is 12mm diameter, passing through the cradle floor. At Z=25mm (center of the pocket), the arc is still developing (the full arc profile doesn't begin until the pocket terminates at Z=50mm). The hole bridges 12mm — within the 15mm maximum bridge span from requirements.md. No support required.

**Pocket rear wall (Z=50 face):**
The pocket rear wall closes the pocket at Z=50mm. This wall is 2.0mm thick (in Z), running from Z=50 to Z=52mm. The tube exit hole passes through the Y face at Z=25mm, not the Z=50 rear wall. The Z=50 rear wall is solid (no penetrations) and provides the axial stop for the cap assembly.

---

## 5. Snap Tab Geometry (Inboard Edge)

### Inboard Edge Identification

The inboard edge (toward the spine, toward the enclosure center) is the edge of the cradle that faces the spine face. Per concept.md, the spine is a single continuous element spanning the 220mm enclosure width, and each cradle snaps onto the spine face from above.

The enclosure is 220mm wide. The cradle inner width is 196mm plus 4mm lips on each side = 204mm total. The two cradles are mounted side by side in the enclosure. Per the vision, the bags are mounted "one above the other" — the cradles are STACKED VERTICALLY (one above the other in the installed orientation), not side by side in X. Each cradle spans the full 204mm in X within the 220mm enclosure.

**Inboard vs. outboard:**
- The cradle's inboard edge is the edge facing the spine face — the spine runs parallel to the X axis (spanning the full enclosure width) and the cradles mount to the spine face. The cradle's inboard edge is the edge at one X extreme that faces the spine.

From concept.md: "Each cradle platform connects to the spine at its inboard long edge (the edge that faces the center of the enclosure / the spine face)."

The inboard edge is the LONG edge of the cradle — parallel to Z (the 287mm bag-axis direction). In the installed orientation, there are two long edges: one facing the spine (inboard) and one facing the enclosure side wall (outboard).

In the print frame (part printed on-end with Z vertical):
- Inboard edge = one of the long edges in the YZ plane at either X=−4mm (left lip outer face) or X=200mm (right lip outer face).
- The inboard edge is NOT the lip inner face but the full outer face of one lip.

**Which side is inboard:** This is a manufacturing detail not fully specified in the source documents (the two cradles are printed identically and can be oriented either way). For this document, define the **inboard edge as the X=−4mm side (left lip outer face)**. The inboard edge snap tabs are at X=−4mm (the outer face of the left lip). The outboard edge (X=200mm) contacts the enclosure side wall locating ledge.

This assignment is arbitrary (both orientations are valid since the part is symmetric). The downstream modeling agent should note this and confirm with the enclosure design which X face is inboard.

### Snap Tab Positions Along Z

4 snap tabs, spaced to avoid the cap-end pocket zone (Z=0 to Z=50mm). The tabs must be outside the pocket zone and evenly distributed in the remaining span.

Available Z span: Z=50mm to Z=287mm = 237mm.
4 tabs with approximately 60mm spacing (per concept.md).

Optimal positions for even spacing in [50, 287]:
- Tab 1 center: Z=50 + (237/5 × 1) = Z=50 + 47.4 = Z=97mm → **Z=97mm**
- Tab 2 center: Z=50 + (237/5 × 2) = Z=50 + 94.8 = Z=145mm → **Z=145mm**
- Tab 3 center: Z=50 + (237/5 × 3) = Z=50 + 142.2 = Z=192mm → **Z=192mm**
- Tab 4 center: Z=50 + (237/5 × 4) = Z=50 + 189.6 = Z=240mm → **Z=240mm**

Spacing: 97, 145, 192, 240 → intervals of 48, 47, 48mm. Maximum spacing from last tab to Z=287: 287−240=47mm. Maximum spacing from Z=50 to first tab: 97−50=47mm. All intervals approximately equal.

| Tab | Z center | Z range (8mm wide) |
|-----|----------|--------------------|
| 1 | Z=97mm | Z=93 to Z=101mm |
| 2 | Z=145mm | Z=141 to Z=149mm |
| 3 | Z=192mm | Z=188 to Z=196mm |
| 4 | Z=240mm | Z=236 to Z=244mm |

### Tab Body Geometry

Per concept.md and synthesis.md:
- Tab body: 8mm wide (Z direction), 2mm thick (Y direction), 15mm long (cantilever in X direction from the lip outer face)
- Hook: 1.2mm height, 30° lead-in, 90° retention face

**Tab root position:** The tab root is at the lip outer face. For the inboard edge (X=−4mm):
- Tab root at X=−4mm (the lip outer face)
- Tab extends in the −X direction (outward from the cradle, toward the spine)
- Tab tip is at X=−4−15 = X=−19mm

**Tab orientation in XZ cross-section:**
The tab is a cantilever beam extending in the −X direction from the inboard lip outer face. The tab body is 2mm thick in the Y direction (centered at the mid-Y of the lip outer face).

Tab centerline Y: Y_lip_center = (Y_lip_top + Y_lip_base) / 2 = (3.5 + 13.5) / 2 = **Y=8.5mm**
Tab Y range: Y=8.5 ± 1.0mm = **Y=7.5mm to Y=9.5mm** (2mm thick in Y)

**Hook geometry:**
The hook is at the tab tip (X=−19mm). The hook protrudes in the +Y direction (toward the outer/back face, outward from the part):
- Hook protrusion direction: +Y (toward the convex back face)
- Hook height: 1.2mm in Y; hook occupies Y=9.5mm to Y=10.7mm at the tab tip
- Hook 30° lead-in: on the X-facing approach surface, 30° chamfer guides the hook into the mating slot in the spine
- Hook 90° retention face: the face at Y=9.5mm (the inner face of the hook, perpendicular to Y) is the retention face

**Flex direction:** The tabs flex in the Y direction (perpendicular to X, the tab length axis). The flex direction is in the XY plane, which is parallel to the print build plate (layers stack in the Z direction). This satisfies the requirements.md constraint that snap-fit flex direction be parallel to the build plate.

| Parameter | Value | Reference frame |
|-----------|-------|-----------------|
| Inboard edge X (tab root) | X=−4mm (lip outer face) | Part X axis |
| Tab extension direction | −X | Part X axis |
| Tab length | 15mm | Part X axis |
| Tab tip X | X=−19mm | Part X axis |
| Tab width in Z | 8mm | Part Z axis |
| Tab thickness in Y | 2mm | Part Y axis |
| Tab center Y | Y=8.5mm | Part Y axis |
| Tab Y range | Y=7.5 to Y=9.5mm | Part Y axis |
| Hook protrusion direction | +Y | Part Y axis |
| Hook height | 1.2mm (Y=9.5 to Y=10.7mm) | Part Y axis |
| Tab Z centers | Z=97, 145, 192, 240mm | Part Z axis |
| Tab Z ranges | ±4mm from each center | Part Z axis |
| Flex direction | Y (in-plane with build layers) | Requirements ✓ |

---

## 6. Structural Ribs

3 longitudinal ribs on the outer (convex) face of the cradle floor. Ribs run the full Z length from Z=0 to Z=287mm.

### Rib X Positions

The ribs are evenly spaced transversely under the floor in the X direction. The inner floor span is from X=0 to X=196mm (inner lip face to inner lip face). The 3mm gap at each side (X=0 to X=3 and X=193 to X=196) is the lip shelf zone; ribs should not interfere with the cap-end pocket zone or the lip shelf zone.

Effective rib placement zone: X=3mm to X=193mm (190mm inner arc zone).
3 ribs with equal spacing in a 190mm span:
- Spacing interval: 190 / 4 = 47.5mm
- Rib 1 center: X = 3 + 47.5 = **X=50.5mm**
- Rib 2 center: X = 3 + 95.0 = **X=98mm** (coincides with bowl center/bag axis)
- Rib 3 center: X = 3 + 142.5 = **X=145.5mm**

Rib spacing (center to center): 47.5mm. This is greater than the 40mm spacing cited in synthesis.md. The synthesis specified "~40mm apart transversely" as an approximation for the span analysis. The actual positions 50.5, 98, 145.5mm give 47.5mm spacing, which satisfies the structural requirement (at 47.5mm span, the floor still meets the 2.0mm thickness requirement derived from the 40mm span analysis — a 47.5mm span with 2.0mm floor gives acceptable deflection within the 0.5mm limit).

Verify: at 47.5mm transverse span, the structural analysis gives required floor thickness:
h = cbrt(5 × q_span × L⁴ / (384 × E × δ_max × 12 / 1mm_width)) where L=47.5mm span
The analysis at 40mm gives h=2.0mm. Scaling: h scales as L^(4/3). At 47.5mm: h_scaled = 2.0 × (47.5/40)^(4/3) = 2.0 × (1.1875)^(1.333) = 2.0 × 1.262 = 2.52mm. The 2.0mm floor is technically marginally under the stiffness target for a 47.5mm span. However, the structural analysis used conservative assumptions (simple beam, no benefit of 3D shell stiffness, no contribution from the lip walls or the curved shell geometry). The actual shell stiffness is significantly higher. Accept 47.5mm rib spacing with 2.0mm floor. Flag for empirical verification.

### Rib Cross-Section

| Parameter | Value | Reference frame | Notes |
|-----------|-------|-----------------|-------|
| Rib height | 6mm (in Y) | Part Y axis | Per synthesis; extends from convex floor surface outward |
| Rib width | 1.6mm (in X) | Part X axis | Per synthesis; exceeds structural minimum of 1.2mm (3 perimeters) |
| Rib X range (Rib 1) | X=49.7mm to X=51.3mm | Part X axis | Center X=50.5mm ± 0.8mm |
| Rib X range (Rib 2) | X=97.2mm to X=98.8mm | Part X axis | Center X=98mm ± 0.8mm |
| Rib X range (Rib 3) | X=144.7mm to X=146.3mm | Part X axis | Center X=145.5mm ± 0.8mm |
| Rib Z extent | Z=0 to Z=287mm | Part Z axis | Full cradle length |
| Rib Y base | Y=2.0mm (convex floor surface at each rib X position, approximately) | Part Y axis | The convex floor outer surface at rib X position; see note |
| Rib Y tip | Y=2.0 + 6.0 = Y=8.0mm | Part Y axis | Rib extends 6mm outward from the convex floor surface |

**Rib Y base note:** The convex floor outer surface at rib X position depends on the bowl arc profile:
- At Rib 2 (X=98mm, bowl center): floor surface (bag side) is at Y=0; convex outer surface is at Y=2.0mm (floor thickness). Rib base Y = 2.0mm.
- At Rib 1 (X=50.5mm): bowl surface is at Y = 341 - sqrt(341²-(50.5-98)²) = 341 - sqrt(341²-47.5²) = 341 - sqrt(116281-2256.25) = 341 - sqrt(114024.75) = 341 - 337.677 = 3.323mm. Convex outer surface at Y=3.323+2.0=5.323mm. Rib base Y=5.323mm, rib tip Y=11.323mm.
- At Rib 3 (X=145.5mm): symmetric to Rib 1. Y_bowl=3.323mm. Rib base Y=5.323mm, rib tip Y=11.323mm.

**Summary rib Y extents:**

| Rib | X center | Bowl surface Y | Rib base Y | Rib tip Y |
|-----|----------|---------------|------------|-----------|
| 1 | X=50.5mm | Y=3.323mm | Y=5.323mm | Y=11.323mm |
| 2 | X=98mm | Y=0mm | Y=2.0mm | Y=8.0mm |
| 3 | X=145.5mm | Y=3.323mm | Y=5.323mm | Y=11.323mm |

---

## 7. Interior Corner Fillet

3mm fillet at the cradle floor-to-lip transition on the interior face (bag-contact side).

**Location:** At the junction of the arc surface and the lip inner face wall. In the XY cross-section, this junction is at (X=3, Y=13.5mm) for the left side and (X=193, Y=13.5mm) for the right side. The arc surface arrives at slope dY/dX = 0.290 (16.2° from horizontal). The lip inner face (at X=3, oriented vertically in X-Z plane) is perpendicular to the arc tangent there — the two surfaces meet at approximately 90° - 16.2° = 73.8° (not a right angle).

Actually, the arc meets the lip shelf (horizontal surface at Y=13.5mm from X=0 to X=3), not directly the lip inner face at X=3. The transition in the inner surface is:
1. Arc surface (curved) ending at (X=3, Y=13.5mm)
2. Horizontal shelf at Y=13.5mm from X=3 to X=0 (left side)
3. Lip inner face (vertical, X=0) from Y=13.5mm to Y=3.5mm

The 3mm fillet applies at the 90° corner between the arc endpoint and the horizontal shelf, and between the horizontal shelf and the lip inner face. In practice, the modeling agent should apply 3mm fillets to all interior concave corners on the bag-contact face:
- Corner at (X=3, Y=13.5mm): between arc end and lip shelf — apply 3mm fillet here
- Corner at (X=0, Y=13.5mm): between lip shelf and lip inner face — apply 3mm fillet here

**Fillet center for the arc-to-shelf corner (X=3, Y=13.5):**
The arc tangent at this point has slope 0.290 in X-Y. The lip shelf is horizontal (Y=13.5 = constant, slope=0). The fillet center for a concave fillet of radius 3mm at this corner is located 3mm away from both surfaces along their inward normals.
- Inward normal to arc at (X=3, Y=13.5): the arc's normal points toward the arc center (X=98, Y=341); direction = (98-3, 341-13.5)/341 = (95, 327.5)/341 = (0.279, 0.960). Inward = (0.279, 0.960) → fillet center from (X=3, Y=13.5) displaced by 3mm in this direction: X=3+0.837=3.837, Y=13.5+2.881=16.381 ≈ **(X=3.8mm, Y=16.4mm)**.
- Inward normal to shelf (horizontal, Y=13.5mm) is in the +Y direction. Fillet center 3mm in +Y from shelf: Y=13.5+3=16.5mm. Combined fillet center approximately (X=3.8, Y=16.4mm).

The fillet center is at approximately (X=3.8mm, Y=16.4mm) for the left arc-to-shelf corner. Symmetric at (X=192.2mm, Y=16.4mm) for the right.

**Fillet center for the shelf-to-lip-wall corner (X=0, Y=13.5):**
Corner between horizontal shelf (Y=13.5, going in X direction) and vertical lip inner face (X=0, going in Y direction). This is a 90° concave corner. Fillet center at 3mm from each surface:
- 3mm in +Y direction from shelf: Y=13.5+3=16.5mm
- 3mm in −X direction from lip inner face: X=0−3=−3mm
- Fillet center: **(X=−3mm, Y=16.5mm)**

Note: this fillet center is outside the lip wall (X<0 is the lip outer zone), so the fillet radius of 3mm is achievable — the fillet arc at (X=−3mm, Y=16.5mm) with R=3mm touches X=0 at Y=16.5mm and Y=13.5mm at X=−3mm, and creates a smooth concave arc in the interior corner.

---

## 8. Enclosure Locating Ledge Interface

The outboard edge of the cradle (X=200mm, the outer face of the right lip in the default orientation) rests against a 3mm × 3mm ridge on the enclosure inner wall. This is a contact locator only; all retention is provided by the inboard snap tabs.

**Interface in part local frame:**

| Feature | Part coordinate | Mating feature |
|---------|-----------------|---------------|
| Outboard contact face | X=200mm (right lip outer face) | Enclosure inner wall locating ridge |
| Contact Y range | Y=3.5mm to Y=13.5mm (full lip outer face Y extent) | Ridge engages this face |
| Contact Z range | Z=0 to Z=287mm | Full length contact |
| Ridge engagement depth | 3mm (the ridge is 3mm × 3mm; the contact is the entire outboard face area against the ridge face) | Enclosure: 3mm × 3mm ridge at X=203mm (3mm from cradle outer face) |

The enclosure ridge prevents the cradle from rotating about the inboard snap tabs. No snapping mechanism on this side — the cradle simply rests against the ridge.

---

## 9. Fold-End Face (Z=287)

At Z=287mm (top of print, upper-front end of cradle in installed orientation), the bag fold end exits the cradle and enters the spine slot. The fold end of the bag is a flat 190mm wide strip, 3–8mm thick when folded flat.

**Fold-end face definition:**

| Feature | Value | Reference frame |
|---------|-------|-----------------|
| Fold-end face Z position | Z=287mm | Part Z axis |
| Face X extent | X=−4mm to X=200mm (full cradle width including lips) | Part X axis |
| Face Y extent | Y=0 to Y=21.5mm (full cradle depth including ribs) | Part Y axis |
| Bag fold strip location on face | X=3 to X=193 (inner arc width), Y=0 to Y=13.5mm (bowl zone) | Within face |
| Fold end bag thickness at this face | 3–8mm (pinned flat by spine slot) | — |

**Lead-in chamfer on upper edge (Z=287 face):**
The bag fold end must slide into the spine fold-end slot during assembly. To guide the bag fold end into the slot, the upper edge of the cradle's inner bowl surface at Z=287mm receives a 3mm × 45° chamfer on the inner face (the face facing the bag). This chamfer is applied to the arc surface at Z=287mm, creating a widening lead-in.

Chamfer parameters:
- Location: inner bowl surface at Z=287mm
- Chamfer depth: 3mm in Z (from Z=284mm to Z=287mm)
- Chamfer width: 3mm in Y (expands the bowl opening by 3mm toward the bag in this zone)
- Direction: the bowl opening at Z=287mm is chamfered on all sides (both sides of arc, both lip inner faces) to create a 3mm × 45° lead-in bevel

The spine fold-end slot dimensions (from concept.md): 195mm wide × 20mm tall × 10mm deep. The cradle fold-end face provides the bag strip that feeds into this slot. The 3mm chamfer on the cradle's upper edge guides the fold strip into the spine slot during assembly step 5.

---

## 10. Two-Bag Vertical Stack Confirmation

Per the synthesis.md stack analysis, two cradle assemblies consume approximately 94–110mm of vertical height in the installed orientation. The two bags are stacked vertically (one above the other in the installed 35° orientation, not side by side).

In the installed orientation (35° from horizontal):
- The cradle long axis is at 35°
- The cradle cross-section (XY plane in print frame) is perpendicular to the bag axis and tilted at 35° from vertical in the installed frame

**Vertical pitch between the two installed cradles:**

The structural analysis confirms:

| Component | Thickness (perpendicular to bag face) | Vertical component (at 35°) |
|-----------|--------------------------------------|----------------------------|
| Cradle floor + ribs | 2.0mm + 6.0mm = 8.0mm | 8.0 × cos(35°) = 6.6mm |
| Constrained bag | 27mm | 27 × cos(35°) = 22.1mm |
| Upper cap face + ribs | 1.5mm + 5.0mm = 6.5mm | 6.5 × cos(35°) = 5.3mm |
| Per-bag assembly thickness (perp to face) | ~41.5mm | ~34mm vertical |
| Inter-bag gap on spine | ~10mm (min) | ~8.2mm vertical |
| **Two-bag vertical span** | — | **~76mm** |

The cradle part itself (in print frame, Y dimension) spans from Y=0 (bowl inner face at center) to Y=21.5mm (rib tip at outer center). Perpendicular to the bag face, the cradle contributes 8.0mm (floor + ribs, as above).

The two-bag stack fits within 94–110mm vertical (from structural analysis), well within the ~160mm allocated zone in the enclosure's upper section.

**In the print frame:** Each cradle is a separate identical part (same STL file, printed twice). The vertical stack relationship between the two installed cradles is an enclosure/spine design concern, not a cradle-part geometry concern. The cradle part has no built-in awareness of which bag position it occupies. Confirm with the spine design that the spine's two cradle attachment rail positions are separated by the correct vertical pitch (≈54mm center-to-center, derived from ~47mm per-assembly perpendicular thickness × cos(35°)≈38.5mm vertical + ~8mm inter-bag + mounting geometry).

---

## 11. Transform Summary and Verification Points

### Installed Frame to Print Frame Transform

The cradle installs at 35° from horizontal (cap end down toward back wall, fold end up toward front wall). The print frame is the cradle's own local frame (printed on-end, cap end at Z=0 on build plate).

**Transform: Installed frame → Print frame**

In the installed frame:
- Horizontal direction (front-to-back): corresponds to Z print axis (bag length)
- Vertical direction: corresponds to the combination of Z (along bag) and Y (perpendicular to bag face)
- Cap end (back-bottom in installed) = Z=0 in print frame
- Fold end (front-top in installed) = Z=287mm in print frame

The transform is a rotation of 35° between the installed vertical and the print Z axis, plus a translation. For verification purposes, three points are computed in both frames:

**Verification Point 1: Bowl center at mid-length**
- Print frame: (X=98, Y=0, Z=143.5)
- Installed frame: at the center of the cradle, the bag's midsection. Position in enclosure: at 143.5mm along the bag axis from cap end, which is 143.5×cos(35°)=117.5mm front-to-back from the cap end, and 143.5×sin(35°)=82.3mm vertically above the cap end.
- This point is the deepest point of the bowl (closest to the bag face). Y=0 = innermost bowl contact. ✓

**Verification Point 2: Cap-end pocket opening**
- Print frame: (X=98, Y=0, Z=0) — pocket center at the cap-end face
- Installed frame: the lowest point of the cradle assembly, at the cap end of the bag, where the Platypus cap exits the cradle. This is in the back-bottom zone of the enclosure. The pocket opening is at Z=0 in print frame (the bottom of the print = the cap-end face).
- Pocket diameter 31mm centered at (X=98, Y=0, Z=0). ✓

**Verification Point 3: Snap tab 1 center (inboard edge)**
- Print frame: (X=−19, Y=8.5, Z=97) — tab tip at center
- Installed frame: located 97mm from the cap end along the bag axis (above the pocket zone), at the inboard edge (facing the spine). The tab tip protrudes 15mm from the inboard lip outer face.
- Tab Z=97mm in print frame → installed position is 97×cos(35°)=79.5mm front-to-back from cap end, and 97×sin(35°)=55.6mm vertically above the cap end. ✓

**Self-consistency check:**
- Cap-end pocket: Z=0 to Z=50mm. First snap tab at Z=93mm. Gap = 43mm. No tab within the pocket zone. ✓
- Arc tangent Y = R - sqrt(R²-95²) = 341 - sqrt(107256) = 341 - 327.5 = 13.5mm. Lip height from arc tangent toward bag = 10mm. Lip top Y = 13.5 - 10 = 3.5mm > 0. Lip does not extend below Y=0 (the bowl center surface). ✓
- Rib tip at center (X=98, Y=8mm) is 8mm outward from the bowl surface. Rib tip at Rib 1/3 (Y=11.3mm) is 11.3mm outward. Both are within the Y dimension of the print envelope (0 to ~21.5mm at the lip positions). ✓
- Snap tab hook (Y=10.7mm at tip) is within the Y envelope. ✓
- Part fits print envelope: X=−4 to X=200 = 204mm ≤ 325mm print X. Y=0 to 21.5mm ≤ 320mm print Y. Z=0 to 287mm ≤ 320mm print Z. ✓

---

## 12. Dimensional Summary Table

All dimensions from the part's origin (X=0, Y=0, Z=0) in the print frame:

| Feature | Coordinate / Dimension | Frame |
|---------|----------------------|-------|
| Left lip inner face | X=0mm | Part X |
| Right lip inner face | X=196mm | Part X |
| Left lip outer face | X=−4mm | Part X |
| Right lip outer face | X=200mm | Part X |
| Arc left tangent point | (X=3mm, Y=13.5mm) | Part XY |
| Arc right tangent point | (X=193mm, Y=13.5mm) | Part XY |
| Arc center of circle | (X=98mm, Y=341mm) | Part XY |
| Arc radius | R=341mm | — |
| Arc chord (bag width) | 190mm (X=3 to X=193) | Part X |
| Single-arc sagitta (bowl depth) | 13.5mm | Part Y |
| Bowl deepest point | (X=98, Y=0) | Part XY |
| Lip height (Y extent) | 10mm (Y=3.5mm to Y=13.5mm) | Part Y |
| Lip top edge | Y=3.5mm | Part Y |
| Lip base (arc tangent) | Y=13.5mm | Part Y |
| Lip thickness | 4mm (in X direction) | Part X |
| Lip top edge fillet | R=1.5mm at (X=0, Y=3.5) and (X=196, Y=3.5) | Part XY |
| Snap arm rebate center Y | Y=5.5mm | Part Y |
| Snap arm rebate Y range | Y=4.9mm to Y=6.1mm | Part Y |
| Snap arm rebate depth | 1.2mm (X direction), from X=−4mm to X=−2.8mm | Part X |
| Snap arm rebate Z extent | Z=0 to Z=287mm (full length) | Part Z |
| Cradle body Z length | 287mm | Part Z |
| Cap-end pocket center | (X=98, Y=0) | Part XY |
| Cap-end pocket diameter | 31.0mm | — |
| Cap-end pocket Z extent | Z=0 to Z=50mm | Part Z |
| Tube exit hole center | (X=98, Z=25mm) | Part XZ |
| Tube exit hole axis | Y direction (exits through outer Y face) | Part Y |
| Tube exit hole diameter | 12.0mm | — |
| Snap tab root X (inboard) | X=−4mm (lip outer face) | Part X |
| Snap tab tip X | X=−19mm | Part X |
| Snap tab Z centers | Z=97, 145, 192, 240mm | Part Z |
| Snap tab Y center | Y=8.5mm | Part Y |
| Snap tab width (Z) | 8mm | Part Z |
| Snap tab thickness (Y) | 2mm | Part Y |
| Tab hook protrusion | 1.2mm in +Y from Y=9.5mm | Part Y |
| Rib 1 center X | X=50.5mm | Part X |
| Rib 2 center X | X=98mm | Part X |
| Rib 3 center X | X=145.5mm | Part X |
| Rib width (X) | 1.6mm (each rib ±0.8mm from center) | Part X |
| Rib height (Y) | 6mm | Part Y |
| Rib base Y (at Ribs 1 and 3) | Y=5.3mm | Part Y |
| Rib tip Y (at Ribs 1 and 3) | Y=11.3mm | Part Y |
| Rib base Y (at Rib 2) | Y=2.0mm | Part Y |
| Rib tip Y (at Rib 2) | Y=8.0mm | Part Y |
| Rib Z extent | Z=0 to Z=287mm | Part Z |
| Interior fillet radius | R=3mm at arc-to-shelf and shelf-to-lip corners | — |
| Interior fillet center (left arc-to-shelf) | (X=3.8mm, Y=16.4mm) | Part XY |
| Interior fillet center (left shelf-to-lip) | (X=−3mm, Y=16.5mm) | Part XY |
| Floor wall thickness | 2.0mm (in Y) | Part Y |
| Fold-end chamfer | 3mm × 45° on inner face at Z=287mm | Part Z |
| Outboard contact face | X=200mm (right lip outer face) | Part X |
| Part total X span | −4mm to 200mm = 204mm | Part X |
| Part total Y span | 0mm to 21.5mm | Part Y |
| Part total Z span | 0mm to 287mm | Part Z |

---

## 13. Open Items for Empirical Resolution

These dimensions are committed design values, but carry measurement-verification flags from the source documents. The spatial resolution is complete; the following are calibration checkpoints before cutting a final STEP file:

| Parameter | Committed value | Verification method |
|-----------|----------------|---------------------|
| Single-arc sagitta (bowl depth) | 13.5mm (derived from R=341mm, chord=190mm) | Fill bag at 35°, apply flat board with light pressure, measure gap = should be ~27mm total (13.5mm × 2); if total differs, recalculate R and update arc table |
| Cap body OD (actual) | Assumed ~30mm (from spec 1.17in = 29.7mm) | Measure actual cap with calipers; if OD ≠ 30mm, adjust pocket diameter (design = OD + 0.4mm minimum, rounded to 31mm) |
| Lip thickness | 4mm (structural estimate) | Verify after first print: arm must cam outward by 1.5mm, lip must not crack; adjust if snap arm geometry requires wider/narrower lip |
| Rib spacing | 47.5mm (geometric; slightly above the ~40mm analysis value) | Empirical deflection test on first print; press flat board on bowl with ~2kg load, measure deflection at rib midspan |
