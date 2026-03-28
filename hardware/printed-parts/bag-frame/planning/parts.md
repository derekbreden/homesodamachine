# Bag Frame -- Parts Specification

Two printed parts per bag (four total for the machine): a lower cradle and an upper cap that snap together permanently around a Platypus 2L bag. No hinge, no latch, no moving parts. Assembled once during build, never opened again.

---

## Coordinate System

Origin: lower-left-front corner of the assembled frame when lying flat on a surface (not tilted at the 35-degree enclosure mount angle).

- **X axis**: width (left to right), 0 at left edge, positive rightward. Total extent: 180 mm.
- **Y axis**: length (front to back), 0 at the uphill/sealed end (front), positive toward the downhill/cap end (back). Total extent: 250 mm.
- **Z axis**: height (bottom to top), 0 at the bottom face of the lower cradle, positive upward. Total extent: 30 mm (assembled).

When mounted in the enclosure at 35 degrees, the Y axis tilts so that Y=250 (cap end) is lower than Y=0 (sealed end). Gravity pulls the bag contents toward +Y.

All dimensions in this document are in the flat/unrotated coordinate system unless explicitly stated otherwise.

---

## Mechanism Narrative

### What the user sees and touches

The bag frame is an internal structural component. The user never sees or touches it during normal operation. It is assembled once during initial build, then sealed permanently inside the enclosure.

During assembly, the user handles two PETG printed parts per bag: a lower cradle (a ribbed tray with perimeter walls) and an upper cap (an open frame with cross-ribs). The user drapes the empty Platypus bag onto the cradle, routes the bag cap and tubing through the open downhill end, places the upper cap on top, and presses down until four clicks confirm the barbs are engaged.

### What moves

**During assembly (one-time):**
- The upper cap translates in -Z (downward) onto the lower cradle.
- Four barb ridges on the upper cap's perimeter rail deflect inward (in the +X direction on the left side, -X on the right side) as they pass the entry ramps on the cradle's rail, then snap outward into the lock ledges.

**During operation (never):**
- Nothing moves. The frame is a rigid, permanently closed structure.

### What converts the motion

During assembly, the user's downward pressing force (-Z) is converted to barb deflection (inward, +/-X) by the 30-degree lead-in ramp on each barb ridge. The ramp acts as a wedge: the vertical force component pushes the barb ridge inward past the cradle wall, and the vertical lock face prevents reverse motion once the barb clears the ledge.

### What constrains each part

**Lower cradle**: constrained by the enclosure rail interface (tongue-and-groove, described below). During assembly on a work surface, it rests flat under gravity.

**Upper cap**: constrained in Z by the four barb engagements with the lower cradle. Constrained in X and Y by the nesting fit of the upper cap's perimeter rail inside the lower cradle's perimeter rail (the upper rail sits inside the lower rail with 0.2 mm clearance per side).

**Bag**: constrained in -Z by the lower cradle's longitudinal ribs. Constrained in +Z by the upper cap's transverse cross-ribs. Constrained in +Y (downhill sliding) by the stop wall at Y=235 mm. Constrained in -Y (uphill) by the clip tab hook at Y=5 mm. Constrained in +/-X loosely by the perimeter rails, though the bag is narrower than the constraint zone width and its heat-sealed edges overhang freely.

### What provides the return force

There is no return force. The barbs engage permanently. Disassembly requires prying with a flat tool, which will deform or break the barb ridges.

### What is the user's physical interaction

1. The user places the lower cradle flat on a work surface.
2. The user drapes the empty Platypus bag onto the cradle, cap hanging off the open downhill end (Y=250 end), sealed end at the uphill end (Y=0 end).
3. The user folds the sealed end of the bag flat and tucks it against the uphill wall of the cradle.
4. The user places the upper cap onto the cradle, aligning the perimeter rails. The upper cap's inner rail dimensions (165.6 mm x 235.6 mm) are smaller than the cradle's inner cavity (166.0 mm x 236.0 mm), providing 0.2 mm clearance per side. This clearance self-centers the cap onto the cradle as it descends.
5. The user presses down firmly. At four points (two per long side), they feel and hear a click as each barb ridge snaps past the lock ledge. The 1.0 mm engagement depth and vertical lock face produce a definitive tactile pop.
6. The user verifies full engagement by pressing down on each barb zone (Y=75 and Y=175, both sides) and confirming no vertical play or rocking. The cap should be rigid with zero give at all four barb points. If the cap rocks or shifts vertically at any point, that barb is not fully engaged -- press harder at that location until it clicks.

---

## Part 1: Lower Cradle

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 180.0 mm |
| Y extent (length) | 250.0 mm |
| Z extent (height) | 15.0 mm |
| Mass (estimated) | ~120 g (PETG, 20% gyroid infill in rails) |

### Perimeter Rail

The perimeter rail is a continuous rectangular wall forming the outer boundary of the cradle.

| Parameter | Value |
|-----------|-------|
| Rail wall thickness | 3.0 mm |
| Rail height (Z) | 15.0 mm |
| Rail outer dimensions (X x Y) | 180.0 mm x 250.0 mm |
| Rail inner dimensions (X x Y) | 174.0 mm x 244.0 mm |
| Rail infill | 20% gyroid |

The perimeter rail is open (no wall) at the downhill end from X=72.5 to X=107.5 (a 35.0 mm wide opening centered on the X midline at X=90.0). This U-shaped opening allows the bag cap and tubing to exit. The opening extends the full height of the rail (0 to 15.0 mm Z).

The two short legs of rail flanking the cap exit opening (X=0 to X=72.5 and X=107.5 to X=180.0 at Y=250.0) are 3.0 mm thick in Y, same as all other rail walls.

### Cradle Floor

The cradle floor is a flat plate at Z=0.0, spanning the full inner area of the perimeter rail.

| Parameter | Value |
|-----------|-------|
| Floor thickness | 1.2 mm (6 layers at 0.2 mm) |
| Floor extent (X) | 174.0 mm (inner rail to inner rail) |
| Floor extent (Y) | 244.0 mm (inner rail to inner rail, minus cap exit opening zone) |

The floor is continuous and flat. It serves as the print bed contact surface and the structural base.

### Longitudinal Ribs

Five longitudinal ribs run parallel to the Y axis, spaced evenly across the floor width. They support the bag's weight and provide anti-adhesion texture.

| Parameter | Value |
|-----------|-------|
| Number of ribs | 5 |
| Rib positions (X, centerline, measured from inner left rail face at X=3.0) | 17.4, 51.8, 86.2 (midline), 120.6, 155.0 mm from origin (X=0) |
| Rib spacing (center-to-center) | 34.4 mm |
| Rib width (X) | 2.0 mm (single extrusion width x2 at 0.4 mm nozzle = 2 perimeters) |
| Rib height above floor (Z) | 5.0 mm (floor at Z=0, rib tops at Z=6.2 including floor thickness) |
| Rib length (Y) | From Y=6.0 (inner face of uphill rail) to Y=235.0 (inner face of stop wall) |
| Rib top edge radius | 0.5 mm radius (chamfered at 45 degrees over 0.5 mm, approximated by 0.2 mm layer stepping) |
| Rib bottom fillets | 1.0 mm radius where rib meets floor |

The rib tops at Z=6.2 are the primary bag contact surface on the lower half. The bag rests on these ribs; air circulates in the 5.0 mm channels between them.

**Anti-adhesion texture on rib tops:** 0.4 mm pitch sawtooth ridges running transverse to the rib (in the X direction), 0.2 mm tall (one layer). These reduce PE film adhesion to the PETG surface.

### Stop Wall

A transverse wall spanning the full inner width at Y=235.0, set back 15.0 mm from the cap exit end. This wall prevents the bag from sliding downhill under the 11 N gravity component.

| Parameter | Value |
|-----------|-------|
| Wall position (Y, inner face) | 235.0 mm |
| Wall thickness (Y) | 3.0 mm (from Y=235.0 to Y=238.0) |
| Wall height (Z) | 15.0 mm (full rail height, from floor to Z=15.0) |
| Wall width (X) | 174.0 mm (full inner width, connects to both side rails) |
| Tubing notch | Semicircular, centered at X=90.0, radius 8.0 mm, cut from the top of the wall (Z=15.0 downward to Z=7.0 at the notch deepest point) |

The tubing notch allows the bag's tubing (6.35 mm / 1/4" OD) to pass through the stop wall without being pinched. The 8.0 mm radius provides 1.65 mm clearance around the tubing on all sides.

### Barb Lock Receivers

Four rectangular slots cut into the inner face of the perimeter rail's long side walls (X=3.0 inner face on left, X=177.0 inner face on right). These receive the barb ridges from the upper cap.

| Parameter | Value |
|-----------|-------|
| Number of receivers | 4 (2 per long side) |
| Receiver positions (Y centerlines) | Y=75.0 and Y=175.0 (symmetric about Y=125.0 midline, 100.0 mm apart) |
| Receiver width (Y) | 12.0 mm |
| Receiver depth into rail wall (+X on left side, -X on right) | 1.5 mm |
| Receiver height (Z) | From Z=7.0 to Z=15.0 (8.0 mm tall, open at the top) |
| Lock ledge position (Z) | Z=8.0 (1.0 mm above the receiver floor at Z=7.0) |
| Lock ledge depth | 1.0 mm (the ledge protrudes 1.0 mm into the receiver from the bottom, creating a shelf the barb ridge locks behind) |

The lock ledge geometry: the receiver is 1.5 mm deep into the rail wall. The bottom 1.0 mm of the receiver (Z=7.0 to Z=8.0) is only 0.5 mm deep (the ledge protrudes 1.0 mm, leaving 0.5 mm of entry space). Above Z=8.0, the full 1.5 mm depth is open. The barb ridge must deflect inward by 1.0 mm to pass the ledge, then springs back outward into the 1.5 mm deep pocket above the ledge.

### Enclosure Rail Tongues

Two outward-facing tongues on the outer faces of the long side rails. These slide into matching grooves in the enclosure side walls.

| Parameter | Value |
|-----------|-------|
| Number of tongues | 2 (one per long side) |
| Tongue position (Y) | Full length of rail, Y=0 to Y=250.0 |
| Tongue position (Z) | Centered at Z=4.0, extending from Z=2.0 to Z=6.0 |
| Tongue height (Z) | 4.0 mm |
| Tongue protrusion from rail outer face (+X on right, -X on left) | 3.0 mm |
| Tongue width (Y along rail) | Continuous, full 250.0 mm |
| Tongue cross-section | Rectangular with 0.5 mm chamfer on leading edges (Y=250 end, where it enters the groove) |

The tongue slides into the enclosure groove from the Y=250 (cap/downhill) end during enclosure assembly. The frame is captured when the enclosure halves close.

### Uphill Wall

The perimeter rail at Y=0 serves as the uphill wall. No special features beyond the standard 3.0 mm thick, 15.0 mm tall rail wall. The inner face at Y=3.0 is where the folded sealed end of the bag rests.

### Entry/Exit Tapers

The longitudinal ribs taper in height near both ends of the constraint zone to prevent kinking the bag film at the constraint boundary.

**Uphill taper (sealed end):**
- From Y=6.0 to Y=46.0 (40.0 mm taper zone), rib height increases linearly from 0.0 mm to 5.0 mm.
- At Y=6.0 (inner face of uphill rail), the ribs are flush with the floor (no protrusion).
- At Y=46.0, the ribs reach full height (5.0 mm above floor, Z=6.2).

**Downhill taper (cap end):**
- From Y=195.0 to Y=235.0 (40.0 mm taper zone), rib height decreases linearly from 5.0 mm to 0.0 mm.
- At Y=195.0, the ribs are at full height (Z=6.2).
- At Y=235.0 (stop wall), the ribs are flush with the floor.

The full-height constraint zone spans Y=46.0 to Y=195.0: 149.0 mm of constant 5.0 mm rib height.

---

## Part 2: Upper Cap

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 174.0 mm (fits inside the lower cradle's perimeter rail) |
| Y extent (length) | 244.0 mm (fits inside the lower cradle's perimeter rail, with 20 mm clip tab extension at uphill end) |
| Z extent (height) | 15.0 mm (from Z=15.0 to Z=30.0 in assembled position) |
| Mass (estimated) | ~80 g (PETG, 20% gyroid infill in rail) |

### Perimeter Rail

The upper cap has its own perimeter rail that nests inside the lower cradle's rail.

| Parameter | Value |
|-----------|-------|
| Rail wall thickness | 2.0 mm |
| Rail height (Z, in assembled position) | 8.0 mm (from Z=15.0 to Z=23.0 in assembled coordinates; the lower 8.0 mm of the cap nests inside the cradle rail, the upper 7.0 mm protrudes above) |
| Rail outer dimensions (X x Y) | 173.6 mm x 243.6 mm |
| Rail inner dimensions (X x Y) | 169.6 mm x 239.6 mm |

**DESIGN NOTE:** The upper cap rail outer dimension (173.6 mm) plus 0.2 mm clearance per side = 174.0 mm, which equals the cradle inner width. Similarly, 243.6 + 0.2 + 0.2 = 244.0 mm = cradle inner length. The 0.2 mm per side clearance allows the cap to self-center when placed on the cradle.

The upper cap perimeter rail is open at the downhill end (Y=244.0 end of the cap, corresponding to Y=247.0 in cradle coordinates) from X=71.3 to X=102.3 (31.0 mm wide, centered on X=86.8 cap midline). This aligns with the cradle's cap exit opening, allowing tubing to pass through.

**Assembled Z positions:**
- The cap rail bottom sits at Z=15.0 (resting on the top of the cradle rail).
- When fully engaged, the cap rail bottom sits at Z=15.0 with zero gap between the two rail tops. The barb engagement at Z=8.0 (cradle coordinates) means the cap rail extends 7.0 mm below the cradle rail top (from Z=15.0 down to Z=8.0 is inside the cradle). Wait -- let me reconsider this.

**CORRECTION -- Assembled nesting geometry:**

The upper cap rail descends into the cradle. The cradle's inner dimensions are 174.0 mm x 244.0 mm and the rail height is 15.0 mm. The cap rail outer dimensions are 173.6 mm x 243.6 mm (0.2 mm clearance per side). The cap rail is 8.0 mm tall.

When assembled:
- The cap rail descends inside the cradle rail.
- The cap rail bottom edge sits at Z=7.0 (inside the cradle).
- The cap rail top edge sits at Z=15.0 (flush with the cradle rail top).
- Zero visible gap between cap rail top and cradle rail top when fully engaged.

This means the cap's features (cross-ribs, top plate) sit above Z=15.0. The cap rail provides the 8.0 mm of nesting depth needed for the barb engagement.

### Top Plate

A flat plate at the top of the cap, connecting the perimeter rail and cross-ribs.

| Parameter | Value |
|-----------|-------|
| Top plate position (Z, assembled) | Z=30.0 (top face), Z=28.8 (bottom face) |
| Top plate thickness | 1.2 mm (6 layers at 0.2 mm) |
| Top plate extent (X) | 169.6 mm (inner rail to inner rail) |
| Top plate extent (Y) | 239.6 mm (inner rail to inner rail) |

### Transverse Cross-Ribs

Four transverse ribs hang downward from the top plate into the bag constraint zone. These limit the bag's maximum upward bulge.

| Parameter | Value |
|-----------|-------|
| Number of ribs | 4 |
| Rib positions (Y, centerline, in cap-local coordinates from cap Y=0) | 49.9, 99.9, 149.9, 199.9 mm (50.0 mm spacing) |
| Equivalent positions in cradle/assembled coordinates (Y) | 52.9, 102.9, 152.9, 202.9 mm |
| Rib width (Y) | 3.0 mm |
| Rib depth below top plate (Z, downward from Z=28.8) | Variable -- defines the constraint gap |
| Rib undersurface Z position (assembled) | Z=20.7 in the full-height constraint zone |
| Rib extent (X) | 169.6 mm (inner rail to inner rail), continuous |
| Rib bottom edge radius | 3.0 mm radius on all bag-contact edges |

**Constraint gap calculation:**
- Lower cradle rib tops at Z=6.2 (floor 1.2 mm + rib 5.0 mm).
- Upper cap rib undersurface at Z=20.7.
- Gap = 20.7 - 6.2 = 14.5 mm between opposing rib surfaces.

**DESIGN GAP: The 14.5 mm gap between opposing rib surfaces does not match the 27 mm center gap specified in the concept.** The concept defines the center gap as "cradle floor to cap rib underside." Re-interpreting: if the 27 mm gap is measured from the cradle floor (Z=1.2, top of floor plate) to the cap rib underside, then cap rib underside = Z=1.2 + 27.0 = Z=28.2. This means the cross-ribs barely protrude below the top plate (28.8 - 28.2 = 0.6 mm). That provides no meaningful constraint.

**Resolution:** The 27 mm gap is measured from the cradle rib tops (Z=6.2) to the cap rib undersurface. Therefore: cap rib undersurface Z = 6.2 + 27.0 = Z=33.2. But the assembled frame height is only 30.0 mm (Z=0 to Z=30). This means either the frame must be taller, or the gap is measured from the floor.

**Revised frame height:** The total assembled frame height must accommodate:
- Floor: 1.2 mm (Z=0 to Z=1.2)
- Cradle ribs above floor: 5.0 mm (Z=1.2 to Z=6.2)
- 27.0 mm center gap (Z=6.2 to Z=33.2)
- Cap cross-rib thickness: 3.0 mm (Z=33.2 to Z=36.2, the rib body above the undersurface)
- Cap top plate: 1.2 mm (Z=36.2 to Z=37.4)

**Revised total assembled height: 37.4 mm.**

This changes the overall envelope. Let me revise all Z dimensions accordingly.

---

## REVISED Dimensions (incorporating 27 mm gap)

### Revised Overall Envelopes

**Lower Cradle:**

| Parameter | Value |
|-----------|-------|
| X extent | 180.0 mm |
| Y extent | 250.0 mm |
| Z extent | 18.0 mm |

The cradle rail height increases from 15.0 to 18.0 mm to provide sufficient nesting depth for the cap rail while maintaining the 27 mm internal gap.

**Upper Cap:**

| Parameter | Value |
|-----------|-------|
| X extent | 173.6 mm (rail outer) |
| Y extent | 243.6 mm (rail outer, plus 20 mm clip tab extension) |
| Z extent | 19.4 mm |

**Assembled frame:**

| Parameter | Value |
|-----------|-------|
| Total height (Z) | 37.4 mm |
| Cap rail nesting depth | 8.0 mm (cap rail descends inside cradle rail) |
| Overlap zone | Z=10.0 to Z=18.0 (cap rail inside cradle rail) |
| Visible height above cradle rail | 19.4 mm (Z=18.0 to Z=37.4) |

### Revised Z Stack (bottom to top, assembled)

| Feature | Z bottom | Z top | Thickness |
|---------|----------|-------|-----------|
| Cradle floor plate | 0.0 | 1.2 | 1.2 mm |
| Cradle longitudinal ribs (above floor) | 1.2 | 6.2 | 5.0 mm |
| **Center gap** | **6.2** | **33.2** | **27.0 mm** |
| Cap cross-rib body | 30.2 | 33.2 | 3.0 mm |
| Cap top plate | 36.2 | 37.4 | 1.2 mm |
| Cap rail (inside cradle) | 10.0 | 18.0 | 8.0 mm |
| Cap open zone (rib to top plate) | 33.2 | 36.2 | 3.0 mm (empty space, structure only at rail perimeter) |

Wait -- the cross-rib undersurface is at Z=33.2 and the top plate bottom is at Z=36.2. The cross-ribs hang from the top plate. Let me re-stack:

| Feature | Z bottom | Z top | Notes |
|---------|----------|-------|-------|
| Cradle floor plate | 0.0 | 1.2 | 1.2 mm thick |
| Cradle longitudinal rib zone | 1.2 | 6.2 | 5.0 mm rib height |
| **Center gap (bag zone)** | **6.2** | **33.2** | **27.0 mm** |
| Cap cross-rib undersurface | 33.2 | -- | Bag contact surface |
| Cap cross-rib body | 33.2 | 36.2 | 3.0 mm tall ribs hanging down from top plate |
| Cap top plate | 36.2 | 37.4 | 1.2 mm thick |

The cap rail needs to bridge from Z=10.0 (inside cradle) to Z=37.4 (top of cap), so the cap rail total height = 27.4 mm. The nesting depth inside the cradle is 8.0 mm (Z=10.0 to Z=18.0). The portion above the cradle rail top is 19.4 mm (Z=18.0 to Z=37.4).

**Revised cradle rail height:** 18.0 mm (Z=0 to Z=18.0).

**Revised cap rail height:** 27.4 mm (Z=10.0 to Z=37.4 in assembled coordinates; printed height = 27.4 mm).

### Revised Barb Lock Geometry

| Parameter | Value |
|-----------|-------|
| Receiver positions in cradle rail (Z) | Z=10.0 to Z=18.0 (the top 8.0 mm of the cradle rail, where the cap rail nests) |
| Lock ledge Z position | Z=11.0 (1.0 mm above the receiver floor at Z=10.0) |
| Barb ridges on cap rail outer face | Located at the bottom 8.0 mm of the cap rail, corresponding to the nesting zone |
| Barb ridge Z position (cap-local, measured from cap rail bottom) | Ridge peak at 1.0 mm from cap rail bottom (Z=11.0 assembled) |
| Barb ridge geometry | 30-degree lead-in ramp from cap rail bottom edge upward 1.0 mm, then vertical lock face |
| Barb ridge protrusion (outward from cap rail face) | 1.0 mm |

When the cap is pressed down, the barb ridges slide past the cradle rail inner face. At the receiver slot locations, the barb ridge enters the 1.5 mm deep receiver. The 30-degree ramp on the barb pushes the cap rail inward (deflecting the 2.0 mm thick cap rail wall). Once the ridge clears the lock ledge (Z=11.0 assembled), the cap rail springs back outward and the ridge locks behind the ledge.

**Cap rail deflection during assembly:** The cap rail wall (2.0 mm thick PETG) must deflect inward by 1.0 mm at the barb ridge to pass the lock ledge. For a 2.0 mm wall with 27.4 mm unsupported height, the cantilever deflection of 1.0 mm is well within PETG's elastic range. The cross-ribs connecting the two long rails act as stiffeners, so the deflection is localized to the 12.0 mm barb zone between stiffening points.

---

## Part 1: Lower Cradle (REVISED)

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 180.0 mm |
| Y extent (length) | 250.0 mm |
| Z extent (height) | 18.0 mm |
| Material | PETG |
| Estimated mass | ~130 g |
| Estimated print time | 2.5-3.0 hours |

### Perimeter Rail

| Parameter | Value |
|-----------|-------|
| Rail wall thickness | 3.0 mm |
| Rail height (Z) | 18.0 mm (Z=0 to Z=18.0) |
| Rail outer dimensions (X x Y) | 180.0 mm x 250.0 mm |
| Rail inner dimensions (X x Y) | 174.0 mm x 244.0 mm |
| Infill | 20% gyroid |

**Cap exit opening:** The downhill end (Y=247.0 to Y=250.0) has no wall from X=72.5 to X=107.5 (35.0 mm wide, centered on X=90.0). This U-shaped opening runs the full rail height (Z=0 to Z=18.0).

### Cradle Floor

| Parameter | Value |
|-----------|-------|
| Z position | Z=0.0 (bottom) to Z=1.2 (top) |
| Thickness | 1.2 mm |
| Extent (X x Y) | 174.0 mm x 244.0 mm (inner rail area) |

### Longitudinal Ribs

| Parameter | Value |
|-----------|-------|
| Count | 5 |
| Rib X positions (centerlines) | 17.4, 51.8, 86.2, 120.6, 155.0 mm (measured from X=0; 34.4 mm spacing within the 174.0 mm inner width, first rib at 14.4 mm from inner rail face, last rib at 14.4 mm from opposite inner rail face) |
| Rib width (X) | 2.0 mm |
| Rib height above floor | 5.0 mm (rib top at Z=6.2) |
| Rib Y extent | Y=6.0 to Y=235.0 (between uphill rail inner face and stop wall inner face) |
| Full-height zone | Y=46.0 to Y=195.0 (149.0 mm) |
| Uphill taper | Y=6.0 to Y=46.0, height ramps linearly from 0.0 to 5.0 mm |
| Downhill taper | Y=195.0 to Y=235.0, height ramps linearly from 5.0 to 0.0 mm |
| Anti-adhesion texture | 0.4 mm pitch sawtooth, 0.2 mm tall, transverse (X direction) on rib tops, full-height zone only |
| Rib top edge | 0.5 mm 45-degree chamfer (both X edges of each rib top) |
| Rib base fillets | 1.0 mm radius where rib meets floor |

### Stop Wall

| Parameter | Value |
|-----------|-------|
| Y position (inner face) | Y=235.0 |
| Y thickness | 3.0 mm (Y=235.0 to Y=238.0) |
| Z height | 18.0 mm (full rail height) |
| X extent | 174.0 mm (full inner width, connects to both side rails) |
| Tubing notch shape | Semicircular |
| Tubing notch center | X=90.0, Z=18.0 (open at top) |
| Tubing notch radius | 8.0 mm |
| Tubing notch depth (from Z=18.0 downward) | 8.0 mm (notch floor at Z=10.0) |

### Barb Lock Receivers

| Parameter | Value |
|-----------|-------|
| Count | 4 (2 per long side wall) |
| Y positions (centerlines) | Y=75.0 and Y=175.0 |
| Receiver width (Y) | 12.0 mm |
| Receiver depth into rail inner face | 1.5 mm |
| Receiver Z extent | Z=10.0 to Z=18.0 (8.0 mm, open at top) |
| Lock ledge Z position | Z=11.0 |
| Lock ledge protrusion | 1.0 mm (ledge extends inward from receiver back wall, reducing the receiver depth from 1.5 mm to 0.5 mm in the Z=10.0 to Z=11.0 zone) |

### Enclosure Rail Tongues

| Parameter | Value |
|-----------|-------|
| Count | 2 (one per long side, on rail outer face) |
| Tongue Y extent | Y=0 to Y=250.0 (full length) |
| Tongue Z position | Z=5.0 to Z=9.0 (centered at Z=7.0) |
| Tongue height (Z) | 4.0 mm |
| Tongue protrusion | 3.0 mm outward from rail outer face |
| Tongue cross-section | Rectangular, 0.5 mm chamfer on all four long edges |
| Leading edge chamfer | 1.0 mm x 45 degrees at Y=250 end (entry end for enclosure groove) |

### Bag-Contact Edge Radii

All edges that may contact the bag film have a minimum 3.0 mm radius:
- Top edges of the perimeter rail inner face (Z=18.0, inner corners): 3.0 mm radius
- Stop wall inner face top edge: 3.0 mm radius
- Uphill wall inner face top edge: 3.0 mm radius
- Rib top edges: 0.5 mm chamfer (ribs are too narrow for 3.0 mm radius; the 2.0 mm width with 0.5 mm chamfers on both sides leaves a 1.0 mm flat top, which is acceptable since the bag rests on the flat top, not the edge)

---

## Part 2: Upper Cap (REVISED)

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width, rail outer) | 173.6 mm |
| Y extent (length, rail outer, excluding clip tab) | 243.6 mm |
| Y extent (length, including clip tab) | 263.6 mm (clip tab extends 20.0 mm past the uphill end) |
| Z extent (height, printed) | 27.4 mm |
| Z extent (assembled, from Z=10.0 to Z=37.4) | 27.4 mm |
| Material | PETG |
| Estimated mass | ~90 g |
| Estimated print time | 1.5-2.0 hours |

### Perimeter Rail

| Parameter | Value |
|-----------|-------|
| Rail wall thickness | 2.0 mm |
| Rail total height | 27.4 mm |
| Rail nesting depth (inside cradle) | 8.0 mm |
| Rail outer dimensions (X x Y) | 173.6 mm x 243.6 mm |
| Rail inner dimensions (X x Y) | 169.6 mm x 239.6 mm |
| Assembled Z positions | Bottom of rail: Z=10.0; Top of rail: Z=37.4 |
| Infill | 20% gyroid |

**Cap exit opening:** Downhill end, from X=71.3 to X=102.3 (31.0 mm wide, centered on X=86.8). Full rail height. This aligns with the cradle cap exit opening (the cap opening is slightly narrower since it sits inside the cradle rail).

**DESIGN NOTE on cap exit alignment:** The cradle cap exit is 35.0 mm wide centered at X=90.0 (from X=72.5 to X=107.5). The cap sits inside the cradle with 0.2 mm clearance on the left side, so the cap's X=0 aligns with cradle X=3.2. The cap exit should be centered at cap X=86.8 (= cradle X=90.0). Cap exit from X=71.3 to X=102.3 in cap coordinates = cradle X=74.5 to X=105.5. This is 31.0 mm wide and fits inside the cradle's 35.0 mm opening with 2.0 mm margin on each side.

### Top Plate

| Parameter | Value |
|-----------|-------|
| Z position (assembled) | Z=36.2 (bottom face) to Z=37.4 (top face) |
| Thickness | 1.2 mm |
| Extent | 169.6 mm x 239.6 mm (inner rail dimensions) |

### Transverse Cross-Ribs

| Parameter | Value |
|-----------|-------|
| Count | 4 |
| Y positions (cap-local centerlines) | 46.9, 96.9, 146.9, 196.9 mm |
| Y positions (assembled/cradle coordinates) | 50.1, 100.1, 150.1, 200.1 mm |
| Rib width (Y) | 3.0 mm |
| Rib depth below top plate bottom face | 3.0 mm |
| Rib undersurface Z (assembled) | Z=33.2 |
| Rib X extent | 169.6 mm (full inner width) |
| Rib bottom edge radius | 3.0 mm (on both Y-facing edges of each rib bottom) |
| Anti-adhesion texture | 0.4 mm pitch sawtooth, 0.2 mm tall, longitudinal (Y direction) on rib undersurfaces |

**Constraint gap verification:**
- Cradle rib tops: Z=6.2
- Cap cross-rib undersurface: Z=33.2
- Gap: 33.2 - 6.2 = 27.0 mm. Confirmed.

**Entry/exit taper on upper constraint:** The two outermost cross-ribs (at Y=50.1 and Y=200.1 assembled) are within the taper zones of the lower cradle ribs. At Y=50.1, the cradle ribs are at approximately 4.1 mm height (50.1 is partway through the Y=46.0-to-Y=6.0 taper zone... wait, the taper goes from Y=46.0 toward Y=6.0 with decreasing height). At Y=50.1, the cradle rib is nearly at full height (50.1 > 46.0, so it is past the taper zone, fully at 5.0 mm). The gap at the first cross-rib is 27.0 mm.

The tapered gap at the ends is achieved by the lower cradle rib height tapering, not by the upper cap ribs changing position. Since there are no upper cap ribs in the taper zones (the outermost ribs at Y=50.1 and Y=200.1 are just outside the taper boundaries), the bag is unconstrained from above in the taper zones. The bag can bulge upward freely there, which is the intended behavior: the taper zones allow the bag to transition from constrained (27 mm) to unconstrained smoothly.

### Barb Ridges

| Parameter | Value |
|-----------|-------|
| Count | 4 (2 per long side, on rail outer face) |
| Y positions (cap-local centerlines) | Y=71.8 and Y=171.8 |
| Equivalent assembled Y positions | Y=75.0 and Y=175.0 (matching cradle receivers) |
| Ridge width (Y) | 10.0 mm (narrower than the 12.0 mm receiver, 1.0 mm clearance each side) |
| Ridge protrusion from rail outer face | 1.0 mm |
| Ridge Z position (cap-local, from cap rail bottom) | Ramp starts at cap rail bottom (Z=0 cap-local = Z=10.0 assembled), ramp peak at 1.0 mm above bottom (Z=11.0 assembled) |
| Lead-in ramp angle | 30 degrees from vertical (the ramp face is 30 degrees off the Z axis) |
| Lock face | Vertical (parallel to Z axis), 1.0 mm tall |
| Ramp height (Z) | 1.73 mm (1.0 mm / tan(30 deg)) |

The barb ridge cross-section (viewed from above looking down the Y axis):
- Starting from the cap rail outer face, the ridge protrudes 1.0 mm outward.
- The bottom of the ridge (facing downhill during assembly) has a 30-degree ramp: it starts flush with the rail face at the cap rail bottom edge and ramps outward to 1.0 mm protrusion over 1.73 mm of Z height.
- The top of the ridge (facing uphill once locked) is a vertical face: 1.0 mm tall, perpendicular to the rail face.
- Total ridge Z height: 1.73 + 1.0 = 2.73 mm.

### Clip Tab

A flat tab extending from the uphill end of the upper cap, past the cradle's uphill wall, with a downward hook that pins the folded sealed end of the bag.

| Parameter | Value |
|-----------|-------|
| Tab Y extent (cap-local) | From Y=0 (uphill end of cap rail) extending 20.0 mm in the -Y direction (past the cradle uphill wall) |
| Tab width (X) | 80.0 mm (centered on cap X midline at X=86.8, from X=46.8 to X=126.8) |
| Tab thickness (Z) | 2.0 mm |
| Tab Z position (assembled) | Top face at Z=37.4 (flush with cap top plate), bottom face at Z=35.4 |
| Hook at tab end | Downward-facing hook at the -Y end of the tab |
| Hook depth (Z, downward from tab bottom) | 5.0 mm |
| Hook inner radius | 3.0 mm (to avoid creasing the bag film) |
| Hook throat opening (Z) | 8.0 mm (distance from hook tip to tab underside, measured at the entry point) |
| Hook tip thickness | 2.0 mm |

The hook captures the folded bag film: the sealed end of the bag is folded over the cradle's uphill wall (Y=0 to Y=3.0) and the hook clamps the fold against the outer face of the cradle's uphill wall. The hook tip points in the +Y direction (toward the bag), curving from the tab downward and back toward the cradle.

**Assembly sequence for clip tab:** The upper cap is placed so the clip tab overhangs the cradle's uphill wall. As the cap is pressed down, the hook descends alongside the outer face of the cradle's uphill wall. The folded bag film is sandwiched between the hook's inner curve and the cradle wall outer face.

### Bag-Contact Edge Radii

All edges that may contact the bag film have a minimum 3.0 mm radius:
- Cross-rib bottom edges (both Y-facing edges): 3.0 mm radius
- Rail inner face bottom edges (Z=10.0, inner corners in assembled position): 3.0 mm radius
- Clip tab hook inner curve: 3.0 mm radius

### Print Orientation

The upper cap prints with the top plate on the print bed (face down) and the ribs/rail pointing upward.
- The top plate bottom face (Z=36.2 assembled) is the first layer against the bed: smooth finish.
- The cross-ribs point upward: the bag-contact undersurfaces of the ribs are actually the top surfaces during printing, which are well-controlled at 0.2 mm layer height.
- The perimeter rail extends upward from the top plate: prints vertically with good layer adhesion.
- The barb ridges are on the rail outer face: the 30-degree ramp and vertical lock face are parallel to layer lines, maximizing shear strength.
- The clip tab and hook extend from one end: the hook's downward curve requires no support since it is less than 45 degrees from vertical.

**DESIGN NOTE:** With the cap printed upside-down, the "top plate" is the build plate surface (smoothest), the cross-rib bag-contact surfaces are the last layers printed (adequate smoothness at 0.2 mm), and the barb ridge lock faces have layer lines parallel to the shear plane (strongest orientation). No supports required.

---

## Interface Specifications

### Interface 1: Cradle-to-Cap Perimeter Rail Nesting

| Parameter | Cradle (receiver) | Cap (insert) | Clearance |
|-----------|-------------------|--------------|-----------|
| Inner width (X) | 174.0 mm | 173.6 mm (outer) | 0.2 mm per side |
| Inner length (Y) | 244.0 mm | 243.6 mm (outer) | 0.2 mm per side |
| Nesting depth (Z) | 8.0 mm (Z=10.0 to Z=18.0) | 8.0 mm (bottom of cap rail) | N/A |

### Interface 2: Barb Ridge to Receiver

| Parameter | Cradle receiver | Cap barb ridge | Clearance |
|-----------|----------------|----------------|-----------|
| Width (Y) | 12.0 mm | 10.0 mm | 1.0 mm per side |
| Depth (into wall) | 1.5 mm | 1.0 mm protrusion | 0.5 mm behind barb when locked |
| Lock engagement (Z) | 1.0 mm ledge | 1.0 mm vertical lock face | Matched |
| Y positions | 75.0, 175.0 mm | 75.0, 175.0 mm (assembled) | Aligned |

### Interface 3: Enclosure Rail Tongue-to-Groove

| Parameter | Cradle tongue | Enclosure groove (specified here for interface consistency) |
|-----------|--------------|-------------------------------------------------------------|
| Tongue height (Z) | 4.0 mm | Groove height: 4.4 mm (0.2 mm clearance top and bottom) |
| Tongue protrusion | 3.0 mm | Groove depth: 3.4 mm (0.2 mm clearance at back, 0.2 mm at entry) |
| Tongue Y extent | 250.0 mm | Groove Y extent: 250.0 mm minimum |
| Angle | Mounted at 35 degrees from horizontal | Groove cut at 35 degrees in enclosure side wall |

### Interface 4: Clip Tab Hook to Cradle Uphill Wall

| Parameter | Value |
|-----------|-------|
| Cradle uphill wall outer face Y position | Y=0.0 |
| Hook inner face Y position (at hook tip) | Y=-2.0 (2.0 mm past cradle outer face) |
| Gap between hook inner face and cradle wall outer face | 3.0 mm (the hook inner radius creates a curved gap, minimum 3.0 mm, to accommodate folded bag film which is ~0.3 mm thick but may bunch up to 2 mm when folded) |

---

## Entry/Exit Taper Summary

| Zone | Y range | Cradle rib height | Cap cross-rib | Effective gap |
|------|---------|-------------------|---------------|---------------|
| Uphill unconstrained | Y=0 to Y=6.0 | No ribs (inside uphill wall) | No ribs | Unconstrained |
| Uphill taper | Y=6.0 to Y=46.0 | 0 to 5.0 mm (linearly increasing) | No ribs | Taper from unconstrained to 27 mm |
| Full constraint zone | Y=46.0 to Y=195.0 | 5.0 mm (constant) | 4 ribs at Y=50.1, 100.1, 150.1, 200.1 | 27.0 mm |
| Downhill taper | Y=195.0 to Y=235.0 | 5.0 to 0 mm (linearly decreasing) | No ribs | Taper from 27 mm to unconstrained |
| Downhill unconstrained | Y=235.0 to Y=250.0 | No ribs (stop wall zone + cap exit) | No ribs | Unconstrained |

---

## Print Specifications

| Parameter | Lower Cradle | Upper Cap |
|-----------|-------------|-----------|
| Material | PETG | PETG |
| Layer height | 0.2 mm | 0.2 mm |
| Nozzle | 0.4 mm | 0.4 mm |
| Infill (rails/walls) | 20% gyroid | 20% gyroid |
| Supports | None | None |
| Print orientation | Flat, floor on bed, ribs up | Flat, top plate on bed (upside-down), ribs/rail up |
| Bed dimensions required | 180 x 250 mm (fits H2C 325 x 320 mm bed) | 174 x 264 mm including clip tab (fits H2C bed) |
| Estimated print time | 2.5-3.0 hr | 1.5-2.0 hr |
| Estimated mass | ~130 g | ~90 g |

---

## Assembly Sequence

1. Place lower cradle flat on work surface, cap exit opening (Y=250 end) facing away from you.
2. Drape empty Platypus bag onto cradle. Orient with cap/spout hanging off the open end (Y=250) and sealed end at the uphill end (Y=0).
3. Fold the sealed end of the bag over the cradle's uphill wall (Y=0 to Y=3.0 rail). The fold tucks against the outer face of the uphill wall.
4. Confirm the bag film lies flat on the longitudinal ribs, with heat-sealed side edges overhanging freely past the inner rail faces.
5. Place the upper cap onto the cradle. The cap's perimeter rail nests inside the cradle's perimeter rail (0.2 mm clearance self-centers). The clip tab overhangs past the cradle's uphill wall, with the hook descending along the outer face and capturing the folded bag film.
6. Press the upper cap down firmly and evenly. Four clicks (two per long side) confirm all barb ridges have engaged past the lock ledges. Each click is a definitive tactile pop from the 1.0 mm barb clearing the lock ledge.
7. Verify: press down on each barb zone (Y=75 and Y=175 on both sides) and confirm zero vertical play. The cap must be rigid at all four points. Any rocking or give indicates incomplete barb engagement -- press harder at that location until it clicks.
8. Route bag tubing through the stop wall's tubing notch (semicircular, 8.0 mm radius at Y=235, X=90) and out the cap exit opening.
9. Repeat steps 1-8 for the second bag.
10. Slide each assembled frame into the enclosure rail grooves (tongue enters from the cap/downhill end).
11. Route tubing to pumps and valves.
12. Close enclosure.

---

## BOM (per bag frame)

| Part | Qty | Material | Source |
|------|-----|----------|--------|
| Lower cradle | 1 | PETG | Printed |
| Upper cap | 1 | PETG | Printed |

**Total for both bags: 4 printed parts. No purchased hardware. No fasteners. No consumables.**

---

## Key Dimensions Summary

| Parameter | Value |
|-----------|-------|
| Assembled frame dimensions (X x Y x Z) | 180.0 x 250.0 x 37.4 mm |
| Constraint zone Y extent | Y=46.0 to Y=195.0 (149.0 mm) |
| Constraint zone X extent | 169.6 mm (cap inner width; bag heat-sealed edges overhang freely) |
| Center gap (cradle rib top to cap rib underside) | 27.0 mm |
| Entry/exit taper length | 40.0 mm each end |
| Cradle rib height | 5.0 mm above 1.2 mm floor |
| Cap cross-rib depth | 3.0 mm below 1.2 mm top plate |
| Perimeter rail nesting clearance | 0.2 mm per side |
| Barb engagement depth | 1.0 mm, 4 points |
| Barb lead-in angle | 30 degrees |
| Cap exit opening width | 35.0 mm (cradle), 31.0 mm (cap) |
| Tubing notch radius | 8.0 mm |
| Enclosure tongue protrusion | 3.0 mm |
| Enclosure rail angle | 35 degrees from horizontal |
| Minimum bag-contact edge radius | 3.0 mm (0.5 mm on narrow rib tops) |
