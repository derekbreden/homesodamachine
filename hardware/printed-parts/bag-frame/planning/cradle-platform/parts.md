# Cradle Platform — Parts Specification

**Version:** 1.0
**Date:** 2026-03-29
**Dimensional source:** spatial-resolution.md (sole authoritative source for all coordinates and dimensions)
**FDM constraint source:** hardware/requirements.md
**Assembly authority:** concept.md

---

## 1. Part Identification

| Field | Value |
|-------|-------|
| Part name | Cradle Platform |
| Version | 1.0 |
| Material | PETG |
| Instances | 2 (identical; same file, print twice) |
| Print orientation | On-end — long axis vertical (bag length axis = Z print axis); cap end at Z=0 (build plate face); fold end at Z=287mm (top of print) |
| Print envelope (X × Y × Z) | 204mm × 21.5mm × 287mm |
| Build plate footprint | 204mm (X) × 21.5mm (Y) |
| Print height | 287mm |
| Fits single-nozzle volume | Yes — 204mm ≤ 325mm (X); 21.5mm ≤ 320mm (Y); 287mm ≤ 320mm (Z) |

**Print orientation rationale:** The cradle cannot be printed face-up (concave up) because the ribs on the convex underside would project into the build plate. It cannot be printed face-down (concave down) because the 196mm open concave span exceeds the 15mm maximum bridge span (requirements.md). On-end orientation eliminates all bridging concerns: ribs, lips, snap tabs, and cap-end pocket walls all build as vertical walls in the XY plane. Snap tab flex direction (Y) is parallel to the build plate, satisfying requirements.md layer-strength constraint for snap-fit arms.

---

## 2. Coordinate System

**Origin definition:**

| Axis | Zero point | Positive direction |
|------|------------|--------------------|
| X | Left lip inner face (the face of the left lip wall that faces the bowl center) | Right — toward right lip inner face |
| Y | Bowl deepest point (minimum-Y point of the arc at X=98, the center of the 196mm inner width) | Outward — away from bag, toward convex back face of part |
| Z | Cap-end face (lower terminus of the cradle body; the face from which the Platypus cap exits; the build plate face during printing) | Up — toward fold end; toward enclosure front wall in installed orientation |

**Physical meaning of axes in installed orientation:**
- X spans the cradle width across the enclosure's own width axis (left-right when facing the front of the appliance)
- Y is perpendicular to the bag face (inward toward bag = decreasing Y; outward toward enclosure = increasing Y)
- Z runs along the bag axis at 35° from horizontal (Z=0 is back-bottom of enclosure; Z=287mm is front-top, toward enclosure front wall)

**Part envelope in print frame:**

| Axis | Minimum | Maximum | Span |
|------|---------|---------|------|
| X | −4mm (left lip outer face) | 200mm (right lip outer face) | 204mm |
| Y | 0mm (bowl inner surface center) | 21.5mm (rib tip at center, outboard zones reach 21.5mm at lip Y extent) | 21.5mm |
| Z | 0mm (cap-end face) | 287mm (fold-end face) | 287mm |

**Note on Y envelope:** The part Y maximum of 21.5mm is reached at the lip outer face zone (X=−4 or X=200), where Y spans from Y=3.5mm (lip top) to Y=13.5mm (lip base). The rib tip at Rib 2 center (X=98) reaches Y=8.0mm. The rib tips at Ribs 1 and 3 reach Y=11.3mm. The part envelope maximum in Y is Y=13.5mm (the deepest bowl surface at the lip base / arc tangent point), plus the lip wall material which extends from the arc tangent outward. Because the lip outer face is at X=−4mm (an X-normal face, not a Y face), the Y depth of the part at the outboard face is limited to the lip height range Y=3.5mm to Y=13.5mm — a span of 10mm starting at Y=3.5mm. The overall print envelope Y dimension of 21.5mm is a conservative envelope that encloses all features.

---

## 3. Mechanism Narrative (Rubric A)

The cradle platform is the lower half of a two-part bag-containment sandwich. It supports one Platypus 2L collapsible bag from below, constraining the bag's cross-sectional profile to the designed 27mm lens depth while the bag is held at 35° from horizontal with the cap end toward the back-bottom of the enclosure.

**What holds the cradle:** The cradle is held by its inboard long edge, which carries four snap tabs that engage horizontal slots in the spine. The spine is a single structural element spanning the full enclosure width; both cradle platforms snap to it, one per bag position, stacked vertically. The cradle's outboard long edge rests against a locating ridge on the enclosure inner wall — this ridge prevents lateral rotation about the snap tabs but provides no retention force. The cradle is fully retained by the four inboard snap tabs alone.

**What the cradle holds:** The cradle holds the Platypus 2L bag along the bag's full body zone (Z=50mm to Z=287mm in the cradle's print frame, corresponding to the body and taper zone of the bag). The cap-end pocket (Z=0 to Z=50mm) holds the Platypus cap assembly — a 31mm-diameter, 50mm-deep cylindrical void that captures the cap and spout protruding from the bag's lower seam. The bag cannot slide in the Z direction (along the slope): the cap-end pocket walls prevent cap-end travel and the side lips retain the bag laterally.

**Relationship to the upper cap:** The upper cap is a matching lens-profiled panel that presses onto the bag from above. It snaps to the cradle's side lips via four horizontal snap arms that hook into 1.2mm × 1.2mm rebates cut into the lip outer faces. Once the cap is snapped closed, the bag is fully enclosed between the cradle bowl and the cap face — constrained to the designed 27mm midsection thickness. The cap cannot be removed without tool-level force (90° retention hook geometry). The cradle's lips and rebates are the structural interfaces that make the cap-to-cradle joint work.

**Relationship to the spine:** The cradle's inboard lip (X=−4mm outer face) carries four cantilevered snap tabs that extend 15mm in the −X direction. These tabs click into horizontal slots on the spine face when the cradle is pressed down from above during assembly. The spine determines the installed position and angle of the cradle. All structural load from the bag passes through the cradle floor into the snap tabs and from the tabs into the spine, which transfers load to the enclosure via its own snap posts.

---

## 4. Constraint Chain Diagram (Rubric B)

```
Bag contents (2.05 kg × g = 20.1 N)
         |
         | Normal component (16.5 N perpendicular to cradle face)
         ↓
Cradle bowl surface (R=341mm arc, 190mm chord, 2.0mm floor wall)
         |
         | 3 longitudinal ribs (1.6mm wide, 6mm tall) stiffen floor
         | — floor panels span 47.5mm max transverse; floor 2.0mm thick
         ↓
Cradle floor outer surface → distributed into rib bases
         |
         | Sliding component (11.5 N along incline, toward cap end)
         ↓
Cap-end pocket walls (31mm ID cylinder, 2.0mm wall) — arrest Z-axis sliding
         |
         ↓
4 snap tabs on inboard lip outer face (X=−4mm)
         | Each tab: 8mm wide, 2mm thick, 15mm cantilever
         | Hook: 1.2mm × 90° retention face — permanent engagement
         ↓
Spine horizontal slots (8.2mm wide × 15mm deep)
         |
         ↓
Spine body (single-part, spans full enclosure 220mm width)
         |
         ↓
4 spine snap posts (2 per enclosure half) → enclosure inner walls
         |
         ↓
Enclosure structure (220mm × 300mm × 400mm)

Lateral restraint (anti-rotation):
Cradle outboard face (X=200mm) → Enclosure locating ridge (3mm × 3mm)
```

---

## 5. Feature List

Features are listed in modeling sequence per decomposition.md. Every dimension is extracted directly from spatial-resolution.md. No dimension in this section is derived independently.

---

### Feature 1: Cradle Body — Lens-Profiled Arc Extrusion

**What it does:** The primary structural volume. Defines the bag-contact bowl surface, the floor wall, and the structural base from which all other features derive. This is the base solid from which everything else is added or subtracted.

**Geometry:**

The cross-section profile is a single circular arc (the bowl floor) plus horizontal shelf zones connecting the arc ends to the lip inner faces, bounded by the side lip inner faces.

Arc definition:
- Circle center: (X=98mm, Y=341mm) in part XY frame
- Arc radius: R = 341mm
- Arc spans from (X=3mm, Y=13.5mm) to (X=193mm, Y=13.5mm)
- Arc deepest point: (X=98mm, Y=0mm)

Closed profile for extrusion (the interior bowl surface cross-section, used as the inner wire):
- Left boundary: vertical line at X=0mm, Y from 3.5mm (lip top) to 13.5mm (lip base)
- Left shelf: horizontal line at Y=13.5mm, X from 0mm to 3mm
- Arc: from (X=3, Y=13.5) to (X=193, Y=13.5), following circle center (98, 341), R=341mm
- Right shelf: horizontal line at Y=13.5mm, X from 193mm to 196mm
- Right boundary: vertical line at X=196mm, Y from 13.5mm (lip base) to 3.5mm (lip top)
- Top (bag-side) closure: line at Y=3.5mm from X=196mm to X=0mm (this is the lip top elevation — the profile is the inner face of the trough)

Floor wall thickness: 2.0mm (in Y direction). The outer convex surface of the floor is offset 2.0mm outward (in +Y) from the inner arc surface at every point. At arc center (X=98): inner surface Y=0, outer surface Y=2.0mm. At arc endpoint (X=3 or X=193): inner surface Y=13.5mm, outer surface Y=15.5mm.

Extrusion axis: Z (along bag length)
Extrusion length: Z=0 to Z=287mm (287mm total)

The solid body from this extrusion forms the bowl shell with the floor wall included.

**Profile cross-section values (from spatial-resolution.md Table, Section 2):**

| X (mm) | Bowl inner surface Y (mm) | Outer surface Y (mm) |
|--------|--------------------------|----------------------|
| 0 (lip inner face) | 13.500 | 15.500 |
| 3 (arc left tangent) | 13.500 | 15.500 |
| 10 | 11.548 | 13.548 |
| 20 | 9.040 | 11.040 |
| 30 | 6.852 | 8.852 |
| 40 | 5.117 | 7.117 |
| 50 | 3.396 | 5.396 |
| 60 | 2.177 | 4.177 |
| 70 | 1.149 | 3.149 |
| 80 | 0.482 | 2.482 |
| 90 | 0.094 | 2.094 |
| 98 (center) | 0.000 | 2.000 |
| 110 | 0.208 | 2.208 |
| 120 | 0.710 | 2.710 |
| 130 | 1.503 | 3.503 |
| 140 | 2.598 | 4.598 |
| 150 | 3.993 | 5.993 |
| 160 | 5.682 | 7.682 |
| 170 | 7.687 | 9.687 |
| 180 | 10.006 | 12.006 |
| 190 | 12.647 | 14.647 |
| 193 (arc right tangent) | 13.500 | 15.500 |
| 196 (lip inner face) | 13.500 | 15.500 |

CadQuery formula for any X in [3, 193]: Y_inner = 341 - sqrt(341² − (X−98)²)

**Position:** The extrusion runs the full Z length of the part (Z=0 to Z=287mm). The bowl cross-section is constant along Z throughout the body zone (Z=50mm to Z=287mm). The cap-end pocket (Feature 4) will be subtracted from Z=0 to Z=50mm after the body extrusion is complete.

**Tolerance / fit notes:** The inner bowl surface is a bag-contact surface. No tight tolerance required — the bag film conforms to the surface. Surface quality: smooth (face-up print in this zone is not the print orientation; in on-end print, the bowl inner face is a vertical wall built layer by layer with full perimeter quality). The arc formula is the authoritative shape; CadQuery should use the formula directly, not interpolated points.

---

### Feature 2: Side Lips — Left and Right

**What they do:** The side lips are the vertical walls that rise on both long edges of the cradle trough. They retain the bag laterally, provide the outer face for the snap arm rebate (Feature 9) and the snap tab root (Feature 6), and define the upper boundary of the bag containment zone. Each lip is a rectangular profile extruded the full Z length of the part.

**Left Lip:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Inner face | X=0mm (X-normal plane, facing right toward bowl center) | Part X |
| Outer face | X=−4mm (X-normal plane, facing left toward enclosure side wall) | Part X |
| Lip thickness | 4mm (in X) | Part X |
| Lip top Y | Y=3.5mm | Part Y |
| Lip base Y | Y=13.5mm | Part Y |
| Lip height | 10mm (from Y=13.5mm to Y=3.5mm, in the −Y direction toward the bag) | Part Y |
| Z extent | Z=0 to Z=287mm (full cradle length) | Part Z |
| Top edge fillet | 1.5mm radius at (X=0, Y=3.5mm) and (X=−4mm, Y=3.5mm) inner and outer top corners | — |

The left lip inner face is the surface at X=0mm from Y=3.5mm to Y=13.5mm, running Z=0 to Z=287mm.
The lip base connects to the horizontal shelf at Y=13.5mm (Feature 1, left shelf: Y=13.5mm, X=0 to X=3).

**Right Lip:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Inner face | X=196mm (X-normal plane, facing left toward bowl center) | Part X |
| Outer face | X=200mm (X-normal plane, facing right toward enclosure side wall) | Part X |
| Lip thickness | 4mm (in X) | Part X |
| Lip top Y | Y=3.5mm | Part Y |
| Lip base Y | Y=13.5mm | Part Y |
| Lip height | 10mm | Part Y |
| Z extent | Z=0 to Z=287mm | Part Z |
| Top edge fillet | 1.5mm radius at (X=196, Y=3.5mm) and (X=200mm, Y=3.5mm) inner and outer top corners | — |

**Structural note:** The 4mm lip thickness in X is composed of: 1.2mm rebate cut depth + 2.8mm backing wall. The backing wall of 2.8mm exceeds the 1.2mm structural minimum (requirements.md). The rebate depth of 1.2mm leaves 2.8mm of solid material behind it — adequate per requirements.md for structural wall.

**Tolerance / fit notes:** Lip inner faces (X=0 and X=196) are bag-contact surfaces. No special tolerance. Lip outer faces (X=−4mm and X=200mm) are snap interface surfaces — these are the surfaces that receive the snap arm rebate cut (Feature 9). Dimensional accuracy of X=−4mm and X=200mm is important for consistent snap arm engagement.

---

### Feature 3: Structural Ribs (×3, Convex Underside)

**What they do:** Three longitudinal ribs on the outer (convex) face of the cradle floor stiffen the floor against bending. Without ribs, a 2.0mm PETG floor spanning 47.5mm transversely would deflect acceptably, but the ribs reduce the transverse span from 196mm to 47.5mm cells (structural-analysis.md §2). Ribs run the full Z length.

**Rib cross-section geometry:**

Each rib is a rectangular profile protruding outward (+Y) from the convex floor surface. The rib base is tangent to the convex outer hull of the floor at the rib's X center position.

| Parameter | Value | Frame |
|-----------|-------|-------|
| Rib width | 1.6mm (in X direction) — each rib: center ±0.8mm | Part X |
| Rib height | 6mm (in Y direction, outward from floor outer surface) | Part Y |
| Z extent | Z=0 to Z=287mm (full cradle length) | Part Z |

**Rib positions and Y extents (from spatial-resolution.md §6):**

| Rib | X center | X range | Bowl inner Y at X center | Floor outer Y (rib base) | Rib tip Y |
|-----|----------|---------|--------------------------|--------------------------|-----------|
| 1 | X=50.5mm | X=49.7 to X=51.3mm | Y=3.323mm | Y=5.323mm | Y=11.323mm |
| 2 | X=98mm | X=97.2 to X=98.8mm | Y=0mm | Y=2.0mm | Y=8.0mm |
| 3 | X=145.5mm | X=144.7 to X=146.3mm | Y=3.323mm | Y=5.323mm | Y=11.323mm |

The rib Y base at each rib follows the convex outer surface of the floor. The rib is not a rectangle from a flat datum — it rises from the curved floor surface. In CadQuery, model each rib as a rectangle whose bottom face is the convex outer surface at that X position, extruding outward in +Y by 6mm from the floor outer surface Y value.

Rib spacing center-to-center: 47.5mm (Ribs 1–2 and 2–3). This exceeds the 40mm target in synthesis.md (which was an approximation). See spatial-resolution.md §6 for the structural acceptance flag.

**Flag:** Rib spacing of 47.5mm is marginally above the 40mm span for which the 2.0mm floor thickness was calculated. The safety factor from shell geometry (curved shell stiffness, lip wall contribution) is expected to be adequate. Verify empirically with the first print.

**Tolerance / fit notes:** Ribs are structural, not mating surfaces. No tolerance requirement. Rib wall thickness of 1.6mm exceeds the 1.2mm structural minimum (requirements.md).

---

### Feature 4: Cap-End Pocket

**What it does:** A cylindrical void at the cap end of the cradle (Z=0 to Z=50mm) that receives the Platypus cap and spout assembly. The pocket is centered on the bag axis. It arrests the bag's Z-axis sliding force (11.5 N) at the cap end by containing the rigid Platypus cap. The pocket wall provides the structural enclosure around the cap assembly and allows the tube exit hole (Feature 5) to pass through.

**Geometry:**

| Parameter | Value | Frame | Derivation |
|-----------|-------|-------|------------|
| Pocket center X | X=98mm | Part X | Inner width midpoint: 196/2 = 98mm |
| Pocket center Y | Y=0mm | Part Y | Bowl center / bag axis at bowl deepest point |
| Pocket inner diameter | 31.0mm | — | Cap OD ~30mm; +0.2mm loose-fit per requirements.md × 2 sides = 30.4mm, rounded up to 31mm |
| Pocket inner radius | 15.5mm | — | 31.0/2 |
| Pocket open face | Z=0 (bottom of print, cap-end face) | Part Z | Cap exits cradle at this face |
| Pocket depth | 50mm | Part Z | Z=0 (open) to Z=50mm (rear wall) |
| Pocket rear wall | Z=50mm | Part Z | Solid wall at Z=50mm, 2.0mm thick (Z=50 to Z=52mm) |
| Pocket wall thickness | 2.0mm minimum | — | Per structural-analysis.md §2 and synthesis.md |

**Modeling operation:** Subtract a cylinder of radius 15.5mm, centered at (X=98, Y=0), from Z=0 through Z=50mm from the body solid. The pocket opens at the Z=0 face (build plate face during printing — builds cavity-upward, no overhang or bridge).

**Elephant's foot chamfer on pocket opening:** Per requirements.md, the bottom face (Z=0) is the build plate face. Elephant's foot flare at the pocket rim will interfere with Platypus cap insertion. Apply a 0.3mm × 45° chamfer on the pocket opening rim (at Z=0, radius transition from 15.5mm). This removes the first ~0.3mm of flared material. CadQuery: fillet or chamfer the edge at (circle r=15.5mm, Z=0) with 0.3mm × 45°.

**Position:** The pocket subtraction removes material from the body solid in the Z=0 to Z=50mm zone. Below Z=50mm (from Z=0), the cross-section at the bag axis is open (the pocket). From Z=50mm upward, the full arc profile of the bowl is present.

**Tolerance / fit notes:** Pocket inner diameter 31.0mm is a loose fit for the Platypus cap (~30mm OD). The +0.2mm per requirements.md is already included in the 31.0mm value. Holes print smaller than designed — add an additional 0.2mm per requirements.md "holes print smaller" note, making the designed pocket diameter 31.2mm to achieve ~31.0mm printed. CadQuery agents: use 31.2mm designed diameter for this pocket.

---

### Feature 5: Tube Exit Hole

**What it does:** A 12mm-diameter clearance hole through the convex outer face of the cradle floor at the cap-end zone. It allows the 1/4" OD hard tubing with John Guest fitting (body OD ~12mm) to exit the pocket and route away from the cap toward the enclosure outlets. The hole is not a sealing surface — it is clearance only.

**Geometry:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Hole diameter | 12.0mm | — |
| Hole center X | X=98mm | Part X |
| Hole center Z | Z=25mm | Part Z |
| Hole axis direction | Y (hole passes through the floor, parallel to the Y axis) | Part Y |
| Hole entry face | Inner arc surface at (X=98, Z=25): Y=0mm (bowl inner surface at center) | Part Y |
| Hole exit face | Convex outer surface at (X=98, Z=25): Y≈2.0mm (floor outer surface at center); exits past rib 2 base at Y=2.0mm | Part Y |

**Modeling operation:** Subtract a cylinder of radius 6.0mm, axis parallel to Y, centered at (X=98, Z=25), passing from the pocket interior outward through the floor (from Y=0 outward through Y=2.0mm and beyond — the hole exits at the convex outer surface). The hole passes through the floor wall (2.0mm) and the rib 2 zone (Y=2.0mm to Y=8.0mm). Rib 2 is centered at X=98mm; the hole at X=98mm passes through the centerline of Rib 2.

**Interaction with Rib 2:** Rib 2 is centered at X=98mm, width 1.6mm (X=97.2 to X=98.8mm). The hole at X=98mm, diameter 12mm (radius 6mm) will cut through Rib 2 from Y=2.0mm to Y=8.0mm. The hole removes the portion of Rib 2 that is within 6mm of (X=98, Z=25) in the XZ plane. The remaining rib material on each side of the hole is adequate — the hole's Z extent in XZ plane is: at Y=8mm (rib tip), the hole radius in Z at X=98 is sqrt(6² − 0²) = 6mm, so the hole cuts 12mm of rib at the rib tip, less elsewhere. Rib 2 spans Z=0 to Z=287mm; losing 12mm of rib height at Z=25mm is acceptable given the ribs' primary function as longitudinal stiffeners.

**Bridge span check:** The hole diameter is 12.0mm. In the on-end print orientation, the hole axis is parallel to Y (horizontal). The hole creates a bridge span of 12.0mm across the hole at the exit point. 12.0mm < 15mm maximum bridge span (requirements.md). No support required.

**Tolerance / fit notes:** Designed as clearance only — no fit tolerance required. The John Guest fitting body passes through; the tube routes away. Holes print smaller: if precise clearance is needed, design at 12.2mm. For this document, use 12.0mm and note for verification.

---

### Feature 6: Snap Tabs (×4, Inboard Edge)

**What they do:** Four cantilevered snap tabs on the inboard lip outer face snap the cradle to the spine. Each tab is a rectangular beam cantilever extending in the −X direction from the left lip outer face (X=−4mm). A hook at the tip engages a mating slot in the spine. The 90° retention face makes this a permanent (non-reversible) joint.

**Inboard edge assignment:** Per spatial-resolution.md §5, the inboard edge is assigned to the X=−4mm face (left lip outer face). Both cradle orientations are valid (the part is symmetric); confirm with spine design which X face is inboard.

**Tab Z positions (from spatial-resolution.md §5):**

| Tab | Z center | Z range (8mm wide) |
|-----|----------|--------------------|
| 1 | Z=97mm | Z=93mm to Z=101mm |
| 2 | Z=145mm | Z=141mm to Z=149mm |
| 3 | Z=192mm | Z=188mm to Z=196mm |
| 4 | Z=240mm | Z=236mm to Z=244mm |

All tabs are outside the pocket zone (Z=0 to Z=50mm). First tab is at Z=93mm (93 − 50 = 43mm clearance from pocket).

**Tab body geometry (from spatial-resolution.md §5):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Tab root X | X=−4mm (lip outer face) | Part X |
| Tab extension direction | −X (outward from cradle, toward spine) | Part X |
| Tab length | 15mm (cantilever) | Part X |
| Tab tip X | X=−19mm | Part X |
| Tab width (Z) | 8mm (±4mm from Z center) | Part Z |
| Tab thickness (Y) | 2mm | Part Y |
| Tab center Y | Y=8.5mm (midpoint of lip Y range: (3.5 + 13.5)/2 = 8.5mm) | Part Y |
| Tab Y range | Y=7.5mm to Y=9.5mm | Part Y |
| Root fillet radius | 1.0mm at the tab root junction with the lip outer face | — |

**Hook geometry (at tab tip, X=−19mm):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Hook protrusion direction | +Y (outward from part, toward spine slot) | Part Y |
| Hook height | 1.2mm | Part Y |
| Hook Y range | Y=9.5mm to Y=10.7mm (tab body top at Y=9.5; hook tip at Y=10.7) | Part Y |
| Hook retention face | 90° perpendicular to Y — the face at Y=9.5mm facing −Y (toward bag face) | — |
| Hook lead-in face | 30° chamfer on the X-facing approach surface — guides hook into slot as tab flexes | — |
| Hook undercut support | 0.2mm interface gap at hook underside (Y=9.5mm face) per requirements.md designed support geometry | — |

**Flex behavior:** The tab flexes in the Y direction. The flex direction is in the XY plane, which is parallel to the build plate (layers stack in Z during printing). This satisfies requirements.md constraint for snap-fit flex direction parallel to build plate.

**Frangible bridge at hook underside:** The 90° hook retention face at Y=9.5mm faces downward (toward build plate during printing — it faces in the +Z direction when the part is installed, but in the on-end print orientation the Y direction is horizontal and the hook's 90° undercut face is horizontal). In on-end print orientation, Y is the print bed's depth direction (not Z), so the hook underside is not a downward-facing overhang — it is a horizontal surface in the Y-axis direction printed as a wall in the XZ cross-section. The 90° retention face is a vertical surface in the on-end print frame (it faces in the −Y direction). No support needed for the retention face itself.

The hook profile: at the tab tip (X=−19mm), the tab body spans Y=7.5 to Y=9.5mm. The hook adds material from Y=9.5 to Y=10.7mm on the outer side (the side facing the spine). The lead-in face is a 30° chamfer on the X=−19mm face of the hook, cutting from the hook tip toward the tab body. In the on-end print orientation, this chamfer is a sloped wall in the XY plane — its overhang angle depends on how it faces relative to the print Y-axis. The 30° lead-in means the face is 30° from perpendicular to the tab axis — this face is printed as a wall angled at 30° off vertical in XY. At 30° from the hook face direction, this is not a downward overhang and requires no support.

**Mating note:** The mating slot in the spine is 8.2mm wide (Z) × 15mm deep (X), open at top for assembly from above (assembly direction: cradle presses down in −Z/installed-down direction). The 8.2mm slot width accommodates the 8mm tab with 0.2mm sliding clearance per requirements.md.

---

### Feature 7: Interior Corner Fillet (3mm radius)

**What it does:** Smooth concave fillets at all floor-to-lip inner transitions on the bag-contact face. These fillets prevent stress concentration on the Platypus bag film seams at the cradle perimeter. They also smooth the visual transition between bowl and lip in a way consistent with the design language (concept.md §5).

**Fillet locations (from spatial-resolution.md §7):**

**Left side — arc-to-shelf corner:**
- Position: (X=3mm, Y=13.5mm) in XY — the junction of the arc endpoint and the left horizontal shelf
- Fillet radius: 3mm
- Fillet center: approximately (X=3.8mm, Y=16.4mm) (from spatial-resolution.md §7)
- Applied to the concave corner between the arc end surface and the horizontal shelf at Y=13.5mm

**Left side — shelf-to-lip-wall corner:**
- Position: (X=0mm, Y=13.5mm) in XY — the junction of the horizontal shelf and the left lip inner face
- Fillet radius: 3mm
- Fillet center: (X=−3mm, Y=16.5mm) (from spatial-resolution.md §7)
- Applied to the 90° concave corner between the horizontal shelf (Y=13.5mm surface) and the left lip inner face (X=0 surface)
- Note: fillet center at X=−3mm is inside the lip wall material (lip extends from X=−4mm to X=0mm); fillet is geometrically achievable

**Right side (symmetric):**
- Arc-to-shelf corner: (X=193mm, Y=13.5mm); fillet center ≈ (X=192.2mm, Y=16.4mm)
- Shelf-to-lip-wall corner: (X=196mm, Y=13.5mm); fillet center ≈ (X=199mm, Y=16.5mm)

All four fillet edges run the full Z length (Z=0 to Z=287mm).

**Tolerance / fit notes:** These are bag-contact fillets. Radius must not be less than 3mm (risk of seam stress concentration if tighter). No upper tolerance limit for functional purposes; 3mm is the design target.

---

### Feature 8: Lip Top Edge Fillet (1.5mm radius)

**What it does:** A convex fillet on the top edge of both side lips (the Y=3.5mm edge visible along both long edges of the assembled cradle). This fillet provides a finished edge treatment consistent with the design language (concept.md §5: "The lip top edge is a prominent visual feature — 1.5mm radius reads as a finished edge rather than a printed edge").

**Fillet locations (from spatial-resolution.md §3):**

**Left lip inner top edge:**
- Position: (X=0mm, Y=3.5mm) in XY cross-section
- Fillet radius: 1.5mm
- Fillet center (per spatial-resolution.md): at (X=−1.5mm, Y=3.5mm) — 1.5mm outward in X from the inner face corner

**Left lip outer top edge:**
- Position: (X=−4mm, Y=3.5mm) in XY cross-section
- Fillet radius: 1.5mm
- Fillet center: at (X=−2.5mm, Y=3.5mm)

**Right lip inner and outer top edges:** symmetric at X=196mm and X=200mm respectively.

All fillet edges run the full Z length (Z=0 to Z=287mm).

**Tolerance / fit notes:** These are visual/ergonomic features. No fit tolerance. The upper cap's perimeter edge rests ~1.5mm above these edges when locked (concept.md §3 seam treatment), so the lip top edge is visible in the assembled state from above.

---

### Feature 9: Snap Arm Rebate (×2, both lip outer faces)

**What it does:** A horizontal groove running the full Z length of each lip outer face. The upper cap's snap arms hook into this groove when the cap is pressed down. The 1.2mm × 1.2mm groove profile matches the 1.2mm hook height of the snap arms. The groove provides the 90° retention surface that holds the cap closed.

**Rebate geometry (from spatial-resolution.md §3):**

**Left lip outer face rebate (at X=−4mm):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Rebate location face | X=−4mm (left lip outer face, X-normal plane) | Part X |
| Rebate depth (cut into lip, −X direction) | 1.2mm — from X=−4mm to X=−2.8mm | Part X |
| Rebate height (Y extent) | 1.2mm | Part Y |
| Rebate center Y | Y=5.5mm | Part Y |
| Rebate Y range | Y=4.9mm to Y=6.1mm (center ±0.6mm) | Part Y |
| Rebate Z extent | Z=0 to Z=287mm (full cradle length) | Part Z |
| Cross-section | Rectangular groove: 1.2mm deep (X) × 1.2mm tall (Y) | XY plane |

Cross-section view at the left outer face:
```
X=−4mm (lip outer face)
    |
    |  Y=3.5mm (lip top edge)
    |  ↕ 1.4mm gap above rebate top
    |  Y=4.9mm ─────── rebate top
    |           | 1.2mm deep in X
    |           |────── rebate back wall at X=−2.8mm
    |           | 1.2mm tall in Y
    |  Y=6.1mm ─────── rebate bottom
    |  ↕ 7.4mm gap below rebate bottom
    |  Y=13.5mm (lip base)
```

**Right lip outer face rebate (at X=200mm):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Rebate location face | X=200mm (right lip outer face, X-normal plane) | Part X |
| Rebate depth (cut into lip, +X direction) | 1.2mm — from X=200mm to X=198.8mm | Part X |
| Rebate height (Y extent) | 1.2mm | Part Y |
| Rebate center Y | Y=5.5mm | Part Y |
| Rebate Y range | Y=4.9mm to Y=6.1mm | Part Y |
| Rebate Z extent | Z=0 to Z=287mm | Part Z |

**Tolerance / fit notes:** The rebate receives the 1.2mm hook of the snap arm. Per requirements.md, mating clearance for snug fit is 0.1mm. The rebate should be designed at 1.3mm deep (1.2 + 0.1mm) and 1.3mm tall to ensure the hook seats without force fit. Both lips should be designed consistently. The Y=5.5mm center position is the primary mating constraint — the cap snap arm must engage at this position.

**Structural check:** Backing wall behind rebate: X=−4mm outer face, rebate cuts to X=−2.8mm. Wall from X=−2.8mm to X=0 (lip inner face) = 2.8mm. This exceeds the 1.2mm structural minimum (requirements.md). Adequate.

---

### Feature 10: Cap-End Solid Terminus (Z=0 Face)

**What it does:** The closed bottom face of the cradle. In the print frame this is the build plate face. In the installed orientation this is the lower face of the cradle (cap end, back-bottom of enclosure). The pocket opening is in this face. The face is closed everywhere outside the pocket and its tube exit.

**Geometry:**

The Z=0 face is defined by the outer profile of the part at Z=0:
- X extent: X=−4mm to X=200mm (full lip-to-lip width)
- Y extent: Y=3.5mm to Y=15.5mm (lip top edge to outer convex floor surface at arc endpoint)
- Pocket opening: circle of diameter 31.0mm centered at (X=98, Y=0) — this is the only opening in the Z=0 face within the bowl zone

This face is solid PETG except at the pocket opening. The cap-end face is the primary structural terminus that transmits the bag's Z-sliding force (11.5 N) from the pocket walls into the cradle body.

**Elephant's foot treatment:** The Z=0 face is the build plate face. Per requirements.md: add a 0.3mm × 45° chamfer to all bottom edges at Z=0 that are mating surfaces. The pocket opening rim at Z=0 receives the 0.3mm × 45° chamfer (specified in Feature 4). The outer perimeter of the part at Z=0 is not a mating surface (it does not contact the spine or enclosure in assembled position), so no chamfer is required there. Only the pocket opening chamfer is mandatory.

---

### Feature 11: Fold-End Open Face (Z=287mm) and Lead-In Chamfer

**What it does:** The open upper face of the cradle at Z=287mm. The bag fold end (a flat heat-sealed strip, 190mm wide, 3–8mm thick) exits the cradle through this opening and enters the spine's fold-end slot. The lead-in chamfer guides the fold strip into the spine slot during assembly.

**Geometry:**

The Z=287mm face is fully open — there is no material closing the trough at this end. The trough profile at Z=287mm is identical to the body zone cross-section.

**Lead-in chamfer (from spatial-resolution.md §9):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Location | Inner bowl surface at Z=287mm (all sides of the bowl opening) | Part Z |
| Chamfer depth | 3mm in Z (from Z=284mm to Z=287mm) | Part Z |
| Chamfer width | 3mm in Y (expands bowl opening by 3mm toward bag in this zone) | Part Y |
| Direction | 45°; the bowl opening at Z=287mm is chamfered on the inner face — both sides of arc, both lip inner faces | — |

The chamfer creates a widening lead-in bevel at the top of the cradle that guides the bag's fold end into the spine slot during assembly step 4 (per concept.md assembly sequence). Applied to the arc surface and lip inner faces at Z=287mm.

---

## 6. Interface Table (Rubric D)

Every mating surface — every point where this part contacts another part or component.

| Interface | Cradle feature | Mating part / feature | Contact type | Key dimension | Tolerance |
|-----------|---------------|----------------------|--------------|---------------|-----------|
| Cradle to spine — snap engagement | Snap tabs (×4): 8mm wide, 2mm thick, 15mm cantilever, hook 1.2mm at Y=9.5–10.7mm; root at X=−4mm | Spine horizontal slots: 8.2mm wide (Z), 15mm deep (X), open at top | Permanent snap — 90° retention face | Tab width 8mm, slot width 8.2mm (0.2mm sliding clearance per requirements.md) | ±0.1mm on tab width; ±0.1mm on hook height |
| Cradle to upper cap — snap rebate | Rebate: 1.2mm deep × 1.2mm tall, Y center 5.5mm, on both lip outer faces | Cap snap arm hooks: 1.2mm height, 90° retention face | Permanent snap — hook into groove | Rebate designed 1.3mm × 1.3mm (0.1mm snug fit clearance per requirements.md) | ±0.1mm rebate height; Y position ±0.1mm |
| Cradle to enclosure — outboard locating ledge | Outboard lip outer face: X=200mm, Y=3.5mm to Y=13.5mm, Z=0 to Z=287mm | Enclosure inner wall locating ridge: 3mm × 3mm | Contact locator (no snap) — prevents lateral rotation | Full face contact along Z; ridge at X=203mm (3mm from cradle outer face) | Clearance fit; no precision required |
| Cap-end pocket to Platypus cap | Pocket: 31.0mm ID (designed 31.2mm), 50mm deep, center at (X=98, Y=0), open at Z=0 | Platypus 2L cap assembly: ~30mm OD, 40–50mm protrusion from bag seam | Clearance fit — pocket captures cap, not a sealing surface | Designed ID 31.2mm → ~31.0mm printed (holes shrink per requirements.md) | Loose fit; verify with physical cap |
| Tube exit hole to John Guest fitting | Hole: 12.0mm diameter, center at (X=98, Z=25mm), axis in Y direction | John Guest fitting body: ~12mm OD, 1/4" OD hard tubing | Clearance fit — not a sealing surface | 12.0mm hole; fitting body passes through | Clearance; verify with fitting |
| Cradle bowl surface to Platypus bag film | Inner bowl surface: R=341mm arc, X=3 to X=193, full Z length | Bag film (nylon/PE laminate, ~0.2mm thick) | Conforming contact — bag film drapes against bowl | No tolerance constraint — bag conforms to surface | N/A (bag conforms) |
| Cradle upper lip edge to upper cap perimeter | Lip top edges: Y=3.5mm, X=0 and X=196, full Z length (1.5mm fillet applied) | Cap perimeter edge | Non-contact — 1.5mm reveal gap (cap sits 1.5mm proud of lip top edge per concept.md §3) | 1.5mm reveal when cap is locked | Visual check |

---

## 7. FDM Printability (Rubric G)

Print orientation: on-end — long axis vertical (Z=bag axis, Z=0 at build plate, Z=287mm at top). Layer planes are XY. Every surface is evaluated against requirements.md constraints.

### Overhang Table

| Feature / Surface | Orientation in print frame | Overhang angle | Pass/Fail | Notes |
|-------------------|---------------------------|----------------|-----------|-------|
| Bowl inner surface (arc) | Vertical wall — builds as XY cross-section layers stacking in Z | 0° overhang (walls, not horizontal faces) | Pass | Full perimeter quality; no overhang |
| Left and right lip inner faces | Vertical walls at X=0 and X=196 | 0° overhang | Pass | |
| Lip top edges (Y=3.5mm) | Horizontal surface at the top of the lip wall | Top face of a vertical wall — prints as a cap layer, not an overhang | Pass | Top-facing surface; no overhang issue |
| Convex outer floor surface | Vertical curved surface in Y (the outer hull of the arc profile) | 0° — this is the exterior of a convex curved wall | Pass | Builds layer by layer |
| Structural ribs 1–3 | Vertical walls in XZ cross-section | 0° overhang — ribs are walls extruded in Z | Pass | 1.6mm width exceeds 0.8mm minimum wall (requirements.md) |
| Snap tabs — body | Horizontal cantilever extending in −X from the lip outer face at X=−4mm | The tab body projects in −X (horizontal in installed orientation; in on-end print frame, X is a horizontal axis). The tab is at Y=7.5–9.5mm; the tab extends in −X as a horizontal projection from the lip face | The tab in the on-end print frame: layers stack in Z. The tab is a wall in the XZ plane extending −X. The tab body (2mm thick in Y) is a wall, not a horizontal plate — it is 2mm wide in Y and 8mm wide in Z, extending 15mm in −X. From the print's perspective this is a wall extending horizontally from the lip outer face. **The underside of the tab** (at Y=7.5mm) is a horizontal surface that overhangs in the −X direction from the lip wall. This is an overhang at 0° (fully horizontal). | **Fail — requires designed support** | The tab underside at Y=7.5mm is a horizontal overhang 15mm long (−X from root to tip). This exceeds the 15mm bridge limit at maximum. See resolution below. |
| Snap tab hook — lead-in face (30°) | 30° chamfer on the hook approach face (the face at X=−19mm, angled at 30° from the hook face) | 30° from vertical = 60° from horizontal. The overhang limit is 45° from horizontal (walls must be within 45° of vertical). 60° > 45°: this face is printable without support. | Pass | 30° lead-in is within printable range |
| Snap tab hook — retention face (90°) | Flat face at Y=9.5mm, facing −Y (toward bag face), perpendicular to Y axis | In the on-end print frame, the retention face is a horizontal surface facing in the −Y direction. The hook tip protrudes +Y from the tab body. The retention face is the underside of the hook step — a horizontal undercut. | **Fail — requires designed support** | Use 0.2mm interface gap per requirements.md. See resolution below. |
| Cap-end pocket opening (Z=0 face) | Bottom face — build plate face | Build plate: no overhang | Pass | Elephant's foot chamfer applied |
| Cap-end pocket cylindrical wall | Vertical cylinder wall building from Z=0 upward | 0° overhang — cylinder builds as a series of closed loops | Pass | |
| Cap-end pocket rear wall (Z=50mm) | This is a horizontal bridge/cap at Z=50mm spanning across the 31mm pocket opening | The pocket rear wall spans 31mm at Z=50mm — a bridge of 31mm. **31mm > 15mm maximum bridge span (requirements.md).** | **Fail — requires designed support** | See resolution below. |
| Tube exit hole | 12mm-diameter circle, axis in Y direction; hole is horizontal in print frame | The hole top (Y maximum of the hole circle) creates a 12mm bridge span in the XZ plane. 12mm < 15mm maximum. | Pass | 12.0mm < 15mm limit |
| Snap arm rebate (groove on lip outer face) | Horizontal groove on a vertical face (the lip outer face is a vertical wall in the print frame; the rebate is a horizontal slot into it) | The rebate ceiling (top face at Y=4.9mm) is a horizontal overhang into the groove, but the groove depth is 1.2mm — this is a very short horizontal overhang of 1.2mm. | Pass | 1.2mm groove ceiling overhang << 15mm bridge limit |
| Fold-end chamfer (Z=287mm) | 45° chamfer on inner face at top of print | 45° from horizontal — exactly at the printable limit per requirements.md | Pass (boundary) | Exactly 45°; acceptable per requirements.md |
| Interior corner fillets (3mm) | Concave fillets on the inner bowl surface corners; in print frame these are concave transitions on vertical walls | No overhang — concave transitions between walls | Pass | |
| Lip top edge fillets (1.5mm) | Convex fillets on lip top edges — small convex transitions at the top of a wall | No overhang concern | Pass | |

### Overhang Resolutions for Fail Items

**Snap tab body underside (horizontal overhang 15mm in −X):**

The tab body (Y=7.5mm to Y=9.5mm) extends 15mm in −X from the lip outer face. The underside at Y=7.5mm is a horizontal face that overhangs the space below. At exactly 15mm, this is at the absolute limit of the bridge span — sag is expected at 15mm per requirements.md ("will sag visibly").

Resolution: Apply a 45° chamfer on the underside leading edge of the tab at the root (at X=−4mm, Y=7.5mm). The chamfer transitions the underside from the lip outer face, removing the sharp root overhang and reducing effective bridge length. The chamfer is 2mm × 45° (removing 2mm of the 15mm span from the root), leaving a 13mm span. 13mm < 15mm. The chamfer is on the bottom (non-functional) face of the tab; it does not affect tab width, thickness, or hook geometry.

Alternatively: increase tab thickness from 2mm to 2.5mm to reduce the visual sag impact. The 2mm thickness is driven by the strain analysis in structural-analysis.md (verified adequate). The 0.5mm addition would place the tab further inside the printable zone. Either the chamfer or the thickness increase is acceptable; the chamfer is preferred as it does not change the tab mechanical properties.

**Snap tab hook retention face (90° undercut):**

Resolution: Per requirements.md and concept.md, use a 0.2mm interface gap at the hook retention face. The hook tip (Y=10.7mm) is connected to the tab body at Y=9.5mm by a 0.2mm-gapped frangible bridge. In the on-end print orientation, the retention face faces −Y; the 0.2mm gap creates a thin, fragile bridge that prints and breaks cleanly on first assembly deflection. This is the explicit designed support geometry approach from requirements.md.

CadQuery instruction: At the hook retention face (the face at Y=9.5mm on the hook, facing −Y), offset the hook geometry 0.2mm outward (in +Y) from the tab body surface at Y=9.5mm, leaving a 0.2mm gap. The hook top geometry at Y=9.5mm to Y=10.7mm is fully connected to the tab body at the sides and tip; only the underside face has the 0.2mm gap.

**Cap-end pocket rear wall (31mm bridge span at Z=50mm):**

The pocket rear wall is a horizontal disc of 31mm diameter (plus surrounding floor material) at Z=50mm. This creates a 31mm bridge across the pocket opening — exceeding the 15mm maximum.

Resolution: The rear wall at Z=50mm is 2.0mm thick (per spatial-resolution.md §4: "Z=50 to Z=52mm"). In the on-end print orientation, this wall builds at Z=50mm as a horizontal surface. However, the pocket is a cylindrical void below it — the "bridge" is the rear wall spanning the 31mm pocket. 31mm >> 15mm limit.

Designed support: Add a 1.5mm-thick cross-rib inside the pocket at Z=50mm that bridges the 31mm span in two 15mm half-spans. The cross-rib runs from one pocket wall to the other, passing through (X=98, Y=0) at Z=50mm, oriented in the X direction (Y=0, spanning X=98−15.5mm to X=98+15.5mm = X=82.5mm to X=113.5mm). The cross-rib is 1.5mm wide in Y and serves as the designed support for the pocket rear wall.

The cross-rib uses the requirements.md approach: 0.2mm interface gap between rib top face and pocket rear wall underside. The rib breaks away cleanly after printing; the gap leaves the pocket rear wall surface intact. Rib width: 1.5mm in Y (above 0.8mm minimum). Rib span: 31mm total, split into two 15.5mm half-spans by the rib center at X=98mm. Each half-span is 15.5mm — marginally over the 15mm limit by 0.5mm. If 15.5mm shows sag, reduce the pocket diameter (31.2mm designed) by 0.5mm to 30.7mm to bring each half-span to 15.25mm; this still provides adequate loose fit for the ~30mm cap OD.

Alternative resolution: Print the pocket rear wall with a 30° chamfer on its inner face at the transition from cylindrical wall to flat rear wall (a 30° cone chamfer). This converts the 31mm bridge into a progressive chamfer that builds without bridge support. The chamfer removes 2mm of axial depth from the pocket interior at the rear wall; adjust pocket depth from 50mm to 52mm (moving open face to Z=0, rear wall still at Z=50mm inner face, outer face at Z=52mm). This is the cleaner resolution — no support, no rib to remove.

**Recommendation:** Use the 30° chamfer on the pocket rear wall inner face. This eliminates the bridging problem entirely, requires no support, and leaves the pocket interior clean. CadQuery instruction: at the pocket rear wall, apply a 30° chamfer (measured from the cylinder axis) on the inner face of the rear wall — a conical transition from the cylinder bore to the flat rear wall. This chamfer should span from the pocket inner radius (15.5mm) to the pocket inner radius reduced by the chamfer depth; use a 2mm axial depth (from Z=50mm to Z=48mm on the inner face), which gives a chamfer width in radius of 2mm × tan(30°) = 1.15mm. The pocket inner diameter at the chamfer entry is 31mm; at the rear wall face it narrows to 31mm − 2×1.15mm = 28.7mm — still adequate clearance for the 28mm cap thread OD.

### Wall Thickness Table

| Feature | Wall thickness | Requirements.md minimum | Pass/Fail |
|---------|---------------|------------------------|-----------|
| Cradle floor (bowl shell) | 2.0mm (in Y) | 1.2mm structural | Pass |
| Side lip walls | 4.0mm (in X) | 1.2mm structural | Pass — 3.3× minimum |
| Rebate backing wall (behind rebate) | 2.8mm (X=−2.8 to X=0) | 1.2mm structural | Pass |
| Structural ribs | 1.6mm (in X) | 1.2mm structural | Pass |
| Snap tab body | 2.0mm (in Y) | 1.2mm structural | Pass |
| Pocket wall | 2.0mm minimum | 1.2mm structural | Pass |
| Pocket rear wall | 2.0mm (in Z, Z=50 to Z=52mm) | 1.2mm structural (note: this wall has bridge-resolution applied) | Pass (with chamfer resolution) |

### Bridge Span Table

| Feature | Bridge span | Requirements.md maximum | Pass/Fail |
|---------|------------|------------------------|-----------|
| Tube exit hole | 12.0mm | 15mm | Pass |
| Pocket rear wall | 31mm (designed with chamfer resolution) | 15mm — exceeds; chamfer resolution applied | Pass (with resolution) |
| Snap tab body underside | 15mm (at limit; chamfer resolution applied) | 15mm | Pass (with resolution) |
| Rebate groove ceiling | 1.2mm | 15mm | Pass |

### Layer Strength Table (Snap-Fit Features)

| Feature | Flex direction | Layer orientation | Load direction vs. layer planes | Pass/Fail |
|---------|---------------|-------------------|---------------------------------|-----------|
| Snap tabs | Flex in Y direction | Layer planes are XY (on-end print) | Y flex is in-plane with XY layers — tabs flex across layer boundaries in the plane direction, not across layer bonds | Pass — satisfies requirements.md snap-fit flex constraint |
| Cap rebate engagement | Upper cap arms hook in Y direction | Layer planes are XY (on-end print for cradle) | The rebate is a groove in a wall; the constraint force is in Y — in-plane | Pass |

---

## 8. Feature Traceability (Rubric H)

Every feature traced to a vision line or physical necessity. Categories: V = vision requirement, S = structural necessity, M = manufacturing constraint, A = assembly requirement, R = routing necessity.

| Feature | Traces to | Rationale |
|---------|-----------|-----------|
| Cradle body — arc extrusion (R=341mm, 190mm chord, 287mm long) | V: "bags are each supported by their own lens shaped platform that fits their natural liquid filled shape" (vision.md §2); V: "constrained from above... remain at 25–30mm consistently" — cradle provides the lower half of the 27mm lens constraint | The lens arc profile is derived from the Platypus bag geometry (190mm flat width, 27mm constrained depth). The 287mm Z length is the horizontal projection of the 350mm bag at 35° (concept.md). No geometry is arbitrary. |
| Side lips — 10mm height, 4mm thick | S: retains bag laterally and supports the snap arm rebate and snap tab features; V: "constrained from above" implies containment walls are needed | 10mm lip height per synthesis.md structural review. 4mm thickness is structural minimum plus rebate geometry (1.2mm rebate + 2.8mm backing wall). |
| Cap-end solid terminus (Z=0 face) | S: pocket walls must close at Z=50mm to provide axial stop for the bag cap; A: pocket opens at Z=0 to allow cap insertion from the cap end during assembly | Physical necessity of the pocket geometry. |
| Fold-end open face (Z=287mm) | A: the bag fold end must exit the cradle at the top to enter the spine fold-end slot (concept.md §2 assembly step 5); V: "top of each bag is pinned flat against the front wall" — the fold end must emerge from the cradle | Open face at Z=287mm is the only way to allow the fold end to pass through. |
| Fold-end lead-in chamfer (3mm × 45°) | A: guides the bag fold end into the spine slot during assembly; reduces assembly force | Assembly requirement. Chamfer at fold end ensures the fold strip enters the spine slot without snagging on the edge. |
| Structural ribs ×3 (1.6mm × 6mm) | S: floor thickness 2.0mm alone is inadequate for the 196mm transverse span — ribs reduce effective span to 47.5mm cells (structural-analysis.md §2); V: "structural ribs visible on the underside of a bracket are an established appliance interior language" (concept.md §4) | Structural necessity. Rib cross-section and position derived from span analysis in structural-analysis.md. |
| Cap-end pocket (31mm ID, 50mm deep) | S: the Platypus cap + spout assembly protrudes 40–50mm from the bag seam; the pocket must capture this protrusion to prevent cap-end drift; S: cap-end pocket walls transmit the 11.5 N sliding force from the bag | Physical necessity: without this pocket, the bag would slide along the cradle axis under gravity. |
| Elephant's foot chamfer on pocket opening | M: requirements.md §FDM "Elephant's foot: first 0.2–0.3mm flares outward... add 0.3mm × 45° chamfer to bottom edge if mating surface" — pocket opening is at Z=0 (build plate face) and mates with the Platypus cap | Manufacturing constraint per requirements.md. |
| Tube exit hole (12mm, Y axis, at Z=25mm) | R: the 1/4" OD hard tubing with John Guest fitting must exit the pocket to route toward enclosure outlets; the rear wall clearance is only 13mm (concept.md) — tube cannot exit straight back; exits laterally through Y face | Routing necessity. Concept.md explicitly states: "tube must make a 90° bend within the cap pocket and exit laterally." |
| Snap tabs ×4 (8mm × 2mm × 15mm, 1.2mm hook, 90° retention) | A: the cradle must snap to the spine from above during assembly and remain permanently retained (concept.md §2, join methods); V: "Every single interior piece has specific snap connecting points" (vision.md §2) | Assembly requirement. Tab dimensions from structural-analysis.md and concept.md. 90° retention is per vision's permanent-assembly architecture. |
| Root fillet on snap tabs (1mm) | M: requirements.md §FDM: fillets at snap tab roots prevent stress concentration at the root, which is the highest-stress point during flex. Concept.md §2 specifies 1.0mm root fillet. | Manufacturing/structural constraint. |
| Interior corner fillet (3mm) | V: "contact surfaces should be smoothly radiused at the bag perimeter (no sharp edges that would concentrate stress on the side seams)" (platypus-bag-geometry.md §6); M: fillet radius chosen per concept.md §5 design language (3mm = midpoint of 2–4mm range) | Vision requirement for bag seam protection. Physical necessity: sharp corners at floor-to-lip transitions would stress bag film seams. |
| Lip top edge fillet (1.5mm) | V: concept.md §5: "1.5mm radius reads as a finished edge rather than a printed edge" — vision requires appliance-quality interior surfaces | Vision requirement for surface language. |
| Snap arm rebate (1.2mm × 1.2mm, full Z length) | A: upper cap snap arms require a mating groove to hook into; without the rebate, the cap cannot be snapped closed (concept.md §2, upper cap join method) | Assembly requirement. Rebate dimensions match the 1.2mm hook geometry of the cap snap arms (concept.md §2). |
| Reveal ledge (1.5mm) at inboard edge | V: concept.md §3: "1.5mm reveal — the cradle inboard wall stops 1.5mm short of flush with the spine face... seam reads as 'cradle seated in spine recess'" | Vision requirement for seam treatment. The 1.5mm reveal is a deliberate shadow line at the spine-to-cradle seam. |
| Pocket rear wall chamfer (30° at Z=50mm) | M: requirements.md §FDM: bridge span maximum 15mm; the 31mm pocket diameter exceeds this without the chamfer; chamfer converts the bridge into a printable transition | Manufacturing constraint. Added to satisfy requirements.md bridge limit. |
| Snap tab body underside chamfer (2mm × 45°) | M: requirements.md §FDM: bridge span maximum 15mm; tab body underside at 15mm is at the limit and requires the chamfer to stay within the printable range | Manufacturing constraint. Added to satisfy requirements.md bridge limit. |
| Pocket rear wall frangible support rib | M: requirements.md §FDM: where bridges are unavoidable, "designed support geometry must not be a solid union with the main body; include a 0.2mm interface gap" (alternative to chamfer resolution — see Feature 4 for both resolutions) | Manufacturing constraint per requirements.md. Primary resolution is the chamfer (Feature 4). |

---

## Rubric C — Design Principles (Completeness Check)

Every behavioral claim in this document resolves to a named geometric feature with dimensions:

| Behavioral claim | Resolving feature | Dimensions |
|-----------------|-------------------|------------|
| "Constrains bag to 27mm midsection" | Cradle body arc profile | R=341mm, sagitta=13.5mm (one arc), total two-arc depth=27mm |
| "Retains bag laterally" | Side lips | 4mm thick, 10mm tall, X=−4 to X=0 (left), X=196 to X=200 (right) |
| "Captures Platypus cap, prevents Z sliding" | Cap-end pocket | 31.0mm ID, 50mm deep, Z=0 to Z=50mm |
| "Allows tube routing" | Tube exit hole | 12mm diameter, Y axis, at (X=98, Z=25mm) |
| "Snaps permanently to spine" | Snap tabs ×4 | 8mm × 2mm × 15mm, 1.2mm hook, 90° retention face, Z=97/145/192/240mm |
| "Cap snaps closed" | Snap arm rebate | 1.2mm × 1.2mm groove, Y=4.9 to Y=6.1mm, on both lip outer faces, full Z length |
| "Finished edge appearance" | Lip top edge fillet | R=1.5mm at Y=3.5mm, both lips, full Z length |
| "No stress concentration on bag seams" | Interior corner fillet | R=3mm at arc-to-shelf and shelf-to-lip corners, full Z length |
| "Fold end guided into spine slot" | Fold-end lead-in chamfer | 3mm × 45°, inner face at Z=284–287mm |
| "Stiff floor, no visible deflection" | Structural ribs ×3 | 1.6mm × 6mm, at X=50.5/98/145.5mm, Z=0 to Z=287mm |

No ungrounded behavioral claims are present. Every claim in sections 3–5 resolves to a feature in this list.

---

## Rubric E — Completeness Verification

Feature inventory from decomposition.md, verified:

| # | Feature (decomposition.md) | Specified in this document | Feature number |
|---|---------------------------|---------------------------|----------------|
| 1 | Lens-shaped bowl body | Yes | Features 1, 10, 11 |
| 2 | Side lips (both long edges) | Yes | Feature 2 |
| 3 | Structural ribs ×3 (underside) | Yes | Feature 3 |
| 4 | Cap-end pocket | Yes | Feature 4 |
| 5 | Tube exit hole | Yes | Feature 5 |
| 6 | Snap tabs ×4 | Yes | Feature 6 |
| 7 | Floor-to-lip interior fillet (3mm) | Yes | Feature 7 |
| 8 | Lip top edge fillet (1.5mm) | Yes | Feature 8 |
| 9 | Outer lip rebate (1.2mm × 1.2mm) | Yes | Feature 9 |

All 9 features accounted for. No orphaned features. No features added beyond those in decomposition.md except the fold-end lead-in chamfer (spatial-resolution.md §9) and the pocket rear wall chamfer (FDM resolution — manufacturing constraint, not a design feature in its own right).

---

## Rubric F — Dimensional Completeness

Every dimension that a CadQuery agent requires to model this part, with source citation:

| Dimension | Value | Source |
|-----------|-------|--------|
| Arc radius | 341mm | spatial-resolution.md §2 |
| Arc circle center | (X=98, Y=341) | spatial-resolution.md §2 |
| Arc chord | 190mm (X=3 to X=193) | spatial-resolution.md §2 |
| Single-arc sagitta | 13.5mm | spatial-resolution.md §2 |
| Bowl deepest point | (X=98, Y=0) | spatial-resolution.md §1 |
| Part Z length | 287mm | spatial-resolution.md §1 |
| Left lip inner face | X=0mm | spatial-resolution.md §3 |
| Right lip inner face | X=196mm | spatial-resolution.md §3 |
| Left lip outer face | X=−4mm | spatial-resolution.md §3 |
| Right lip outer face | X=200mm | spatial-resolution.md §3 |
| Lip height | 10mm (Y=13.5 to Y=3.5mm) | spatial-resolution.md §3 |
| Lip top edge Y | Y=3.5mm | spatial-resolution.md §3 |
| Lip base Y | Y=13.5mm | spatial-resolution.md §3 |
| Lip thickness | 4mm in X | spatial-resolution.md §3 |
| Floor wall thickness | 2.0mm in Y | spatial-resolution.md §6 |
| Rib 1 center X | X=50.5mm | spatial-resolution.md §6 |
| Rib 2 center X | X=98mm | spatial-resolution.md §6 |
| Rib 3 center X | X=145.5mm | spatial-resolution.md §6 |
| Rib width | 1.6mm | spatial-resolution.md §6 |
| Rib height | 6mm | spatial-resolution.md §6 |
| Rib base Y (Ribs 1 and 3) | Y=5.323mm | spatial-resolution.md §6 |
| Rib base Y (Rib 2) | Y=2.0mm | spatial-resolution.md §6 |
| Rib tip Y (Ribs 1 and 3) | Y=11.323mm | spatial-resolution.md §6 |
| Rib tip Y (Rib 2) | Y=8.0mm | spatial-resolution.md §6 |
| Pocket center X | X=98mm | spatial-resolution.md §4 |
| Pocket center Y | Y=0mm | spatial-resolution.md §4 |
| Pocket inner diameter (designed) | 31.2mm (for ~31.0mm printed; see requirements.md hole shrinkage note) | spatial-resolution.md §4 + requirements.md |
| Pocket depth | 50mm (Z=0 to Z=50mm) | spatial-resolution.md §4 |
| Pocket rear wall | Z=50 to Z=52mm (2.0mm thick in Z) | spatial-resolution.md §4 |
| Pocket opening elephant's foot chamfer | 0.3mm × 45° at Z=0 pocket rim | requirements.md + spatial-resolution.md §4 |
| Tube exit hole diameter | 12.0mm | spatial-resolution.md §4 |
| Tube exit hole center X | X=98mm | spatial-resolution.md §4 |
| Tube exit hole center Z | Z=25mm | spatial-resolution.md §4 |
| Tube exit hole axis | Y direction | spatial-resolution.md §4 |
| Snap tab root X | X=−4mm | spatial-resolution.md §5 |
| Snap tab tip X | X=−19mm | spatial-resolution.md §5 |
| Snap tab Z centers | Z=97, 145, 192, 240mm | spatial-resolution.md §5 |
| Snap tab width (Z) | 8mm | spatial-resolution.md §5 |
| Snap tab thickness (Y) | 2mm | spatial-resolution.md §5 |
| Snap tab center Y | Y=8.5mm | spatial-resolution.md §5 |
| Snap tab Y range | Y=7.5 to Y=9.5mm | spatial-resolution.md §5 |
| Snap tab hook protrusion | 1.2mm in +Y (Y=9.5 to Y=10.7mm) | spatial-resolution.md §5 |
| Snap tab hook lead-in | 30° chamfer on approach face | spatial-resolution.md §5 / concept.md §2 |
| Snap tab hook retention face | 90° perpendicular to Y at Y=9.5mm | spatial-resolution.md §5 / concept.md §2 |
| Snap tab root fillet | 1.0mm | concept.md §2 |
| Snap tab frangible bridge | 0.2mm gap at hook retention face | requirements.md |
| Rebate depth (X) | 1.2mm (designed 1.3mm for fit) | spatial-resolution.md §3 |
| Rebate height (Y) | 1.2mm (designed 1.3mm for fit) | spatial-resolution.md §3 |
| Rebate center Y | Y=5.5mm | spatial-resolution.md §3 |
| Rebate Y range | Y=4.9 to Y=6.1mm (designed Y=4.85 to Y=6.15mm) | spatial-resolution.md §3 |
| Rebate Z extent | Z=0 to Z=287mm | spatial-resolution.md §3 |
| Interior fillet radius | 3mm | spatial-resolution.md §7 |
| Left arc-to-shelf fillet center | (X=3.8mm, Y=16.4mm) | spatial-resolution.md §7 |
| Left shelf-to-lip fillet center | (X=−3mm, Y=16.5mm) | spatial-resolution.md §7 |
| Lip top edge fillet radius | 1.5mm | spatial-resolution.md §3 |
| Fold-end chamfer | 3mm × 45° on inner face at Z=284 to Z=287mm | spatial-resolution.md §9 |
| Pocket rear wall chamfer | 30° at Z=50mm inner face, 2mm axial depth | Rubric G FDM resolution — requirements.md bridge limit |
| Tab underside chamfer | 2mm × 45° at root on underside (Y=7.5mm face) | Rubric G FDM resolution — requirements.md bridge limit |

---

## Design Gaps and Flags

The following items are flagged for resolution before or after first print. None are unresolvable blockers; all are empirical verification points.

1. **Rib spacing at 47.5mm vs. 40mm design target:** The floor thickness of 2.0mm is marginally under the calculated requirement for a 47.5mm span (calculated 2.52mm for a flat plate). The curved shell geometry and lip wall contribution provide additional stiffness not captured in the 2D beam model. Accept for first print; verify empirically by pressing the floor at mid-span. If visible flex, increase floor thickness to 2.5mm in a revised version.

2. **Pocket diameter empirical verification needed:** The Platypus cap OD is inferred at ~30mm from the manufacturer's 1.17 in dimension. If the actual cap OD differs, the designed pocket diameter of 31.2mm may need adjustment. Measure the physical cap before committing the STEP file.

3. **Pocket rear wall chamfer vs. support rib:** Two resolutions are provided for the pocket rear wall bridge issue (30° chamfer and cross-rib with 0.2mm gap). The chamfer is preferred. The CadQuery agent should implement the chamfer; if the chamfer causes a modeling difficulty, fall back to the cross-rib support.

4. **Inboard edge assignment (X=−4mm vs. X=200mm):** The part is symmetric. The inboard edge (snap tab side) is arbitrarily assigned to X=−4mm. The spine design must confirm which physical side of each cradle faces the spine. If both bags are on the same spine face, both cradles are oriented identically (both with X=−4mm facing the spine). If they face each other, one cradle must be printed mirrored. Confirm with spine design before fabrication.

5. **Constrained midsection 27mm:** The arc radius R=341mm is derived from the 27mm constrained thickness. This value has not been empirically confirmed against the actual bag. If the constrained thickness is measured at 25mm, R changes to ~412mm (shallower bowl, less sagitta). If 30mm, R changes to ~278mm (deeper). The arc profile in this specification must be revised after bag measurement.
