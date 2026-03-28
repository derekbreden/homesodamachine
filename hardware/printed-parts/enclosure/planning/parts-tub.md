# Enclosure Tub — Parts Specification

## Coordinate System

- **Origin:** Front-left-bottom corner of the tub exterior.
- **X:** Width, left to right. 0 to 220 mm.
- **Y:** Depth, front to back. 0 to 300 mm.
- **Z:** Height, bottom to top. The tub spans from Z = 0 (bottom face) to Z = 200 mm (top rim / seam plane).
- **Draft convention:** The 3-degree outward draft means the tub is narrowest at the top rim (Z = 200) and widest at the bottom (Z = 0). At Z = 0, the exterior dimensions are 220.0 + 2 * 200 * tan(3 deg) = **241.0 mm** wide and 300.0 + 2 * 200 * tan(3 deg) = **321.0 mm** deep.

**DESIGN GAP (DG-T1): At Z = 0, the drafted footprint is 241.0 x 321.0 mm. The H2C bed is 325 x 320 mm. The 321.0 mm depth exceeds the 320 mm bed dimension by 1 mm. The 5-8 mm brim required for ASA adhesion makes this worse. Resolution options: (a) reduce tub height to ~190 mm so the bottom footprint depth = 300 + 2 * 190 * tan(3) = 319.9 mm (just fits, no brim margin), (b) apply draft only above Z = 10 mm so the base stays at 300 mm and draft expands the top instead, (c) invert the draft direction so the tub is widest at the top rim (220 mm) and narrower at the base. The concept document says "narrower at top" for the assembled enclosure, which means the tub (lower half) should be wider at the bottom and narrower at the top rim -- but this creates the bed-fit conflict. The most consistent interpretation: the tub walls are vertical (no draft on the tub), and the cap provides all the draft (wider at its bottom rim = Z = 200, narrower at its top = Z = 400). This makes the tub a straight-walled box at 220 x 300 mm and the cap tapers inward from 220 x 300 at Z = 200 to ~199 x 279 at Z = 400. This matches the cap specification, which shows the cap is widest at its bottom rim. Alternatively, the draft applies outward going up, so the tub is narrowest at the bottom (220 x 300) and widens toward Z = 200 -- but this contradicts "narrower at top" for the full assembly.**

**Resolution adopted: The tub walls are vertical (zero draft). The exterior is 220 x 300 mm at all Z heights. The 3-degree draft is applied only to the cap (the upper half), which tapers from 220 x 300 at Z = 200 to ~199 x 279 at Z = 400. This is consistent with the cap specification (which defines width/depth at its bottom rim as 220 x 300 and at its top face as 199.1 x 279.1), maintains the "narrower at top" design intent, and avoids the bed-fit conflict. The reveal step (0.8 mm) at the seam plane is created by the cap being inset, not by the tub being wider.**

## Exterior Envelope

| Parameter | Value | Notes |
|-----------|-------|-------|
| Width (X) | 220.0 mm | Constant (vertical walls, no draft) |
| Depth (Y) | 300.0 mm | Constant (vertical walls, no draft) |
| Height (Z span) | 200.0 mm | Z = 0 to Z = 200 |
| Wall thickness | 4.0 mm | Uniform on all four sides |
| Bottom face thickness | 4.0 mm | Flat panel, Z = 0 to Z = 4 interior floor |
| Vertical edge radius | 8.0 mm | All 4 vertical exterior edges |
| Bottom edge radius | 2.0 mm | All 4 bottom exterior edges (firm, grounded per design language) |
| Aperture chamfer | 1.0 mm | All exterior aperture edges (cartridge opening, rear pass-throughs) |

**Interior dimensions:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Interior width (X) | 212.0 mm | 220 - 2 * 4 |
| Interior depth (Y) | 292.0 mm | 300 - 2 * 4 |
| Interior height (Z) | 196.0 mm | 200 - 4 (bottom floor) |
| Interior floor Z | 4.0 mm | Top surface of bottom panel |

**Print orientation:** Open face up (top rim at Z = 200 faces the ceiling). Exterior walls are vertical -- zero overhang on cosmetic surfaces. Interior features (valve cradles, cartridge rails, snap catches) may need tree supports in ASA.

---

## 1. Mechanism Narrative

### What the user sees and touches

The tub is the lower half of a dark charcoal monolithic tower. From the outside, it presents four featureless vertical walls with 8 mm radius vertical edges and 2 mm radius bottom edges. The front face has one aperture: the rectangular pump cartridge opening in the lower center. The back face has pass-through holes for plumbing connections (John Guest tube stubs). The bottom has four rubber foot recesses. The top rim carries the tongue for the permanent solvent-weld joint to the cap.

The user interacts with the tub in one way: sliding the pump cartridge in and out through the front opening. Everything else is permanent and internal.

### What moves during use

The pump cartridge translates along the Y axis (front to back) through the cartridge dock. The cartridge slides in on two rails, seats against four John Guest tube stubs on the dock rear wall, and the collets grip automatically. To remove, the user actuates the cam lever on the cartridge (which retracts the collet rings via the release plate), then slides the cartridge forward and out.

**Stationary parts:** The tub body, valve cradles, all solenoid valves, tube routing channels, John Guest fittings in the rear wall, snap-fit catches, tongue rim -- all permanent.

### What moves during assembly (one-time)

During the single assembly event, the cap translates downward (-Z) onto the tub. The tub's tongue enters the cap's groove. Eight snap-fit catches on the tub's inner walls are pushed outward (back toward their respective wall) by the descending cap's ledges, then spring back inward to their rest position, locking behind the ledges on the cap's inner walls. Acetone solvent is applied to the tongue and groove surfaces before pressing, creating a permanent molecular weld.

### Retention mechanisms

- **Pump cartridge in dock:** Retained axially by John Guest collet grip on four tube stubs. The collets automatically grip 1/4" OD tubes pressed into them. Lateral and vertical position maintained by the two guide rails and dock floor. No snap latch -- the cartridge is held purely by the collet grip and rail constraint.
- **Solenoid valves in cradles:** Each valve sits in a U-shaped channel (cradling the white valve body from below and sides). A snap-over retention bar across the top of the white valve body prevents the valve from lifting out. The retention bar is a 1.5 mm thick cantilever beam that deflects upward during valve insertion and snaps over the top of the white body.
- **John Guest fittings in rear wall:** Press-fit into pocket bores in the dock rear wall. The fitting's 9.31 mm OD center body presses into a 9.1 mm bore (0.21 mm interference). The 15.10 mm OD body-end shoulders seat against the rear wall face on the dock side, preventing the fitting from pushing through.

### Constraint chain (Rubric B)

```
CARTRIDGE INSERTION:
[User hand] -> [Cartridge: translates -Y into dock]
    -> [Guide rails: constrain X and Z, allow Y translation]
    -> [Dock floor: supports Z from below]
    -> [4x JG tube stubs on rear wall: cartridge 4x JG fittings seat onto stubs, collets grip automatically]
    -> [Output: cartridge locked in position, fluid paths connected]
        ^ X constrained by: 2 guide rails (left and right inner walls of dock)
        ^ Z constrained by: dock floor (below) and rail top edges (above)
        ^ Y constrained by: JG collet grip (rear) and cartridge front face flush with tub front face (front)

CARTRIDGE REMOVAL:
[User hand rotates cam lever on cartridge] -> [Cam converts rotation to +Y plate translation]
    -> [Release plate pushes JG collets inward, releasing tube grip]
    -> [User hand pulls cartridge +Y (forward, out of dock)]
    -> [Output: cartridge free, fluid paths disconnected]
        ^ Cam lever is part of the cartridge, not the tub. The tub provides only the static dock.

CAP-TO-TUB ASSEMBLY:
[Assembly hand] -> [Cap: translates -Z onto tub]
    -> [Tongue enters groove: self-alignment in X and Y]
    -> [8 snap catches deflect outward (toward walls) as cap ledges pass, spring back inward behind ledges]
    -> [Acetone solvent weld on tongue/groove: permanent molecular bond]
    -> [Output: permanent, non-separable enclosure]
        ^ X/Y constrained by: tongue-and-groove interlock
        ^ Z constrained by: snap catches (mechanical) + solvent weld (chemical)
```

---

## 2. Top Rim — Cap Interface

The top rim is the mating surface where the tub joins the cap. It runs the full perimeter at Z = 200 mm.

### 2.1 Tongue (mates with cap groove)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Tongue width | 1.5 mm | Fits into cap's 1.7 mm wide groove with 0.1 mm clearance per side |
| Tongue height (Z protrusion above rim face) | 3.0 mm | Fits into cap's 3.2 mm deep groove with 0.2 mm clearance at top |
| Tongue position | Centered in the 4.0 mm wall thickness | 1.25 mm from outer face, 1.25 mm from inner face |
| Tongue profile | Rectangular, protruding upward from top face of rim | Runs continuous around full perimeter |

The tongue runs continuously around all four sides, following the 8 mm corner radii at the vertical edges. The tongue surfaces are raw (unsmoothed) ASA for optimal solvent weld adhesion -- the tub prints with the top rim as the last layers, so the tongue is formed by the slicer without supports.

### 2.2 Rim Face

The top face of the rim (Z = 200 mm, excluding the tongue) is the seam plane. The rim is 4.0 mm wide (wall thickness). The tongue occupies the center 1.5 mm. The remaining rim surface on either side of the tongue (1.25 mm outer, 1.25 mm inner) provides a flat landing for the cap's bottom rim face, transferring compressive loads during assembly.

### 2.3 Snap-Fit Catches (8 total)

The tub carries 8 cantilever snap catches on its inner walls, near the top rim. These mate with 8 ledges on the cap's inner walls. The catches are on the tub; the ledges are on the cap.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Catch count | 8 | 2 per side (front, back, left, right) |
| Catch form | Cantilever beam protruding inward from inner wall, with 90-degree hook at tip | Hook catches behind cap ledge |
| Catch beam length (Z, measured downward from root) | 15.0 mm | Root at Z = 200 (rim), tip at Z = 185 |
| Catch beam width (along wall) | 15.0 mm | Matches cap ledge width |
| Catch beam thickness (protrusion from wall) | 2.5 mm | At root; tapers to 2.0 mm at hook |
| Hook depth (overhang beyond beam face) | 2.0 mm | Engages 2.0 mm deep cap ledge |
| Hook height (Z) | 2.0 mm | Vertical face of the 90-degree catch |
| Hook tip Z position | Z = 185 mm | Bottom of cantilever beam |
| Engagement Z | Z = 205 mm (cap ledge bottom face) | Cap ledge is at Z = 205 per cap spec; the hook springs outward to engage behind it during -Z cap insertion |
| Deflection during assembly | 2.0 mm inward toward wall | Hook must deflect 2.0 mm to pass the cap ledge, then springs back |
| Beam material strain | 2.0 / 15.0 = 13.3% at tip | **DESIGN GAP (DG-T2): ASA strain tolerance is 2-4%. A 13.3% deflection strain will permanently deform or break the cantilever. The beam length must be increased. For 3% strain at 2.0 mm deflection: L = sqrt(2.0 * 2.5 / (0.03 * 1.5)) = approx 33 mm minimum (using cantilever deflection formula delta = F*L^3 / 3EI with strain = 3*delta*t / 2L^2). A 35 mm beam from Z = 200 down to Z = 165 would be sufficient. This changes the hook tip Z to 165. Adopted below.** |

**Revised catch dimensions (addressing DG-T2):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Catch beam length (Z) | 35.0 mm | Root at Z = 200, tip at Z = 165 |
| Catch beam thickness | 2.5 mm at root, 2.0 mm at hook | Taper reduces stress concentration |
| Hook tip Z | Z = 165 mm | |
| Deflection strain | 2.0 * 2.5 / (2 * 35^2) * 3 = **~3.1%** | Within ASA's 2-4% range (tight end) |

**Catch placement around perimeter (X, Y coordinates of catch center, at inner wall — matching cap ledge positions):**

- Front wall (Y = 4.0 mm inner face): X = 60.0 mm, X = 160.0 mm
- Back wall (Y = 296.0 mm inner face): X = 60.0 mm, X = 160.0 mm
- Left wall (X = 4.0 mm inner face): Y = 100.0 mm, Y = 200.0 mm
- Right wall (X = 216.0 mm inner face): Y = 100.0 mm, Y = 200.0 mm

---

## 3. Pump Cartridge Dock

The dock occupies the front-lower zone of the tub interior. The cartridge slides in from the front face along the Y axis.

### 3.1 Dock Envelope

| Parameter | Value | Notes |
|-----------|-------|-------|
| Dock floor Z (top surface) | 20.0 mm | 16 mm above interior floor (Z = 4), provides space for cable routing and rubber feet below |
| Dock floor thickness | 4.0 mm | Z = 16 to Z = 20 |
| Dock ceiling Z | 95.0 mm | 75 mm above dock floor — clears pump height (62.6 mm) + rail height (see below) |
| Dock width (X, interior) | 160.0 mm | Two pumps at 68.6 mm each (bracket width) + 10 mm center divider + 2 * 6.2 mm side clearance |
| Dock depth (Y, interior) | 130.0 mm | Pump total length 116.5 mm + 10 mm tube stub clearance in front + ~3.5 mm rear margin |
| Dock X position | Centered: X = 30 to X = 190 mm (inner face) | 26 mm margin to each side wall inner face |
| Dock Y span | Y = 4 mm (front inner wall) to Y = 134 mm | Open at front (cartridge opening), closed at rear (dock rear wall) |

### 3.2 Guide Rails (2)

Two rails run along the dock floor, parallel to Y, guiding the cartridge in and out.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Rail count | 2 | Left and right |
| Rail form | Rectangular rib protruding upward from dock floor | Cartridge has matching grooves on its underside |
| Rail height (Z, above dock floor) | 5.0 mm | Provides Z and X constraint for the cartridge |
| Rail width (X) | 4.0 mm | |
| Rail length (Y) | 126.0 mm | From Y = 4 mm (front wall) to Y = 130 mm (4 mm before dock rear wall) |
| Left rail X position (center) | X = 50 mm | Inner edge at X = 48, outer edge at X = 52 |
| Right rail X position (center) | X = 170 mm | Inner edge at X = 168, outer edge at X = 172 |
| Rail-to-rail inner span | 116.0 mm | X = 52 to X = 168; cartridge body fits between |
| Rail surface finish | Raw ASA (unsmoothed) | Provides controlled friction for cartridge sliding |

The rail top edges also provide an upper Z constraint: the cartridge sits on the dock floor and is prevented from lifting by the rail top edges engaging the cartridge's groove lips. The groove in the cartridge is 5.5 mm deep x 4.5 mm wide (0.5 mm Z clearance, 0.25 mm X clearance per side).

### 3.3 Dock Rear Wall

The rear wall of the dock carries the four John Guest tube stubs that mate with the cartridge's four fittings.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Rear wall Y position | Y = 134 mm (front face of wall) | |
| Rear wall thickness (Y) | 6.0 mm | Thicker than exterior walls to accommodate JG press-fit pocket depth |
| Rear wall Z span | Z = 16 mm (dock floor bottom) to Z = 95 mm (dock ceiling) | |
| Rear wall X span | X = 30 to X = 190 mm | Matches dock width |

### 3.4 John Guest Tube Stub Pockets (4)

Each pocket holds one John Guest PP0408W union fitting. The fitting's barbell profile (15.10 mm body-end OD, 9.31 mm center-body OD, 15.10 mm body-end OD) requires a stepped pocket.

**Pocket design:** The fitting's center body (9.31 mm OD, 12.16 mm long) press-fits into the dock rear wall. One body-end section (15.10 mm OD) protrudes into the dock interior (facing the cartridge). The other body-end section protrudes behind the rear wall (facing the valve block zone).

| Parameter | Value | Notes |
|-----------|-------|-------|
| Press-fit bore diameter | 9.1 mm | 0.21 mm interference on 9.31 mm center body; light press-fit in ASA |
| Press-fit bore depth (Y, through wall) | 6.0 mm | Matches rear wall thickness; bore goes fully through |
| Counterbore diameter (dock side) | 15.5 mm | Clears 15.10 mm body-end OD with 0.2 mm radial clearance |
| Counterbore depth (dock side) | 0 mm | No counterbore needed on dock side; the body-end simply protrudes into the dock space |
| Counterbore diameter (valve side) | 15.5 mm | Clears 15.10 mm body-end OD |
| Counterbore depth (valve side) | 0 mm | Body-end protrudes freely into valve zone |

**Correction:** Since the bore goes fully through and is only 6 mm long, while the center body is 12.16 mm, the center body is longer than the wall. The press-fit must engage a portion of the center body. With 6 mm of wall and 12.16 mm of center body, 6.16 mm of the center body protrudes on each side beyond the bore (3.08 mm per side of un-engaged center body), plus a body-end section (12.08 mm) protrudes on each side.

**Revised pocket design:** The 9.1 mm press-fit bore extends the full 6.0 mm wall thickness. The fitting is centered in the bore so that approximately equal lengths of center body protrude on each side. With 12.16 mm center body and 6.0 mm bore, 3.08 mm of center body protrudes on each side before the shoulder transition to the 15.10 mm body-end. The body-end sections (12.08 mm long, 15.10 mm OD) protrude freely on both sides.

**Tube stub protrusion into dock (toward cartridge):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Center body protrusion (dock side) | 3.08 mm | 9.31 mm OD cylinder |
| Body-end protrusion (dock side) | 12.08 mm | 15.10 mm OD section, carries the collet |
| Total protrusion into dock | 15.16 mm | From rear wall face to fitting end |
| Tube inserted into fitting end | ~16 mm | 1/4" OD tube from cartridge inserts into the collet |

**Tube stub positions (center of each pocket bore, on dock rear wall face Y = 134 mm):**

The four stubs correspond to: Pump 1 inlet, Pump 1 outlet, Pump 2 inlet, Pump 2 outlet.

| Stub | X position | Z position | Notes |
|------|-----------|-----------|-------|
| Pump 1 inlet | 75.0 mm | 55.0 mm | Left pump, lower |
| Pump 1 outlet | 75.0 mm | 75.0 mm | Left pump, upper |
| Pump 2 inlet | 145.0 mm | 55.0 mm | Right pump, lower |
| Pump 2 outlet | 145.0 mm | 75.0 mm | Right pump, upper |

**Stub spacing:** 70 mm between pump pairs (X), 20 mm between inlet/outlet of same pump (Z). The X spacing centers each pair of stubs within its half of the dock (pump 1 centered at X = 75 in the X = 30-110 half; pump 2 centered at X = 145 in the X = 110-190 half).

### 3.5 Cartridge Opening (Front Face)

The cartridge opening is a rectangular aperture in the front face of the tub.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Opening width (X) | 152.0 mm | Dock width (160 mm) minus 4 mm per side for the rail-to-wall attachment |
| Opening height (Z) | 75.0 mm | From dock floor (Z = 20) to Z = 95 (dock ceiling), which is the pump height (62.6 mm) + rail height (5 mm) + 7.4 mm clearance |
| Opening X position | X = 34 to X = 186 mm | Centered |
| Opening Z position | Z = 20 to Z = 95 mm | |
| Chamfer | 1.0 mm | All 4 edges of opening, exterior side |
| Finger scoop | Shallow concave recess in bottom edge of opening, 40 mm wide x 5 mm deep x 3 mm tall | Centered at X = 110, Z = 20; allows user to grip the cartridge front face |

The cartridge front face sits flush with the tub's front exterior surface (Y = 0 plane) when fully inserted. The cartridge face is 152 x 75 mm, matching the opening.

---

## 4. Valve Cradles

The valve block sits behind and above the pump dock, occupying the upper-rear zone of the tub interior. Up to 10 Beduan solenoid valves are arranged in two rows of 5.

### 4.1 Valve Arrangement

| Parameter | Value | Notes |
|-----------|-------|-------|
| Valve count | 10 (maximum) | Two rows of 5 |
| Valve orientation | Solenoid coil pointing upward (+Z), tube ports along Y axis | White body horizontal, metal coil vertical |
| Row direction | Along X axis | 5 valves per row |

**Row positions:**

| Row | Z center of white valve body | Y center | Notes |
|-----|------------------------------|----------|-------|
| Lower row | Z = 110.0 mm | Y = 220.0 mm | Above dock ceiling (Z = 95), 15 mm clearance for wiring |
| Upper row | Z = 170.0 mm | Y = 220.0 mm | 60 mm above lower row (56 mm valve height + 4 mm gap) |

**Valve X positions within each row (center of each valve slot):**

| Slot | X center | Notes |
|------|----------|-------|
| 1 | 22.0 mm | Left-most; 22 - 32.71/2 = 5.6 mm from left inner wall (X = 4) |
| 2 | 58.0 mm | 36 mm pitch |
| 3 | 94.0 mm | 36 mm pitch |
| 4 | 130.0 mm | 36 mm pitch |
| 5 | 166.0 mm | 36 mm pitch; 166 + 32.71/2 = 182.4 mm, 29.6 mm from right inner wall (X = 212) |

**Pitch justification:** 36 mm pitch for 32.71 mm wide valves = 3.3 mm gap between adjacent valve bodies. This provides clearance for the snap-over retention bars and wiring access to spade connectors.

**Total X span:** Slot 1 left edge (X = 5.6) to Slot 5 right edge (X = 182.4) = 176.8 mm, within 212 mm interior width.

### 4.2 Valve Cradle Geometry

Each cradle is a U-shaped channel that supports the white valve body from below and on two sides. The metal solenoid coil protrudes upward above the cradle. Each cradle is printed integrally with the tub's interior structure.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cradle interior width (X) | 34.0 mm | 32.71 mm valve body + 0.65 mm clearance per side |
| Cradle interior depth (Y) | 54.0 mm | ~50.84 mm valve depth + 1.6 mm clearance per side |
| Cradle interior height (Z, from floor to top of sidewall) | 20.0 mm | Supports ~19.4 mm tall white valve body (slightly proud) |
| Cradle wall thickness | 2.0 mm | All three walls (bottom, left, right) of the U-channel |
| Cradle bottom surface | Flat | Supports valve body underside |
| Solenoid coil clearance above cradle | 40.0 mm minimum | 36.63 mm coil + connectors + wiring clearance |

### 4.3 Snap-Over Retention Bars

Each cradle has one retention bar spanning across the top of the valve body, preventing the valve from lifting out of the cradle.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Bar form | Cantilever beam extending from one cradle sidewall across the valve body opening | Hinged on one side, free end snaps over opposite sidewall |
| Bar length (X) | 38.0 mm | Spans 34 mm cradle opening + 2 mm engagement on each side |
| Bar width (Y) | 8.0 mm | Centered along the valve body length |
| Bar thickness (Z) | 1.5 mm | Thin enough to deflect for valve insertion |
| Bar position (Y) | Centered in cradle Y span | At the midpoint of the valve body |
| Retention method | The bar's free end has a 1.5 mm hook that catches behind a 1.5 mm ledge on the opposite cradle sidewall | Snap engagement; can be pried open with a tool for valve removal during assembly |
| Deflection for insertion | ~3 mm upward (+Z) | Bar flexes as the solenoid coil housing passes through; springs back once the coil clears |

### 4.4 Valve Block Zone Envelope

| Parameter | Value | Notes |
|-----------|-------|-------|
| Zone X span | X = 4 to X = 212 mm | Full interior width |
| Zone Y span | Y = 140 to Y = 292 mm | From dock rear wall back face (Y = 140) to rear inner wall |
| Zone Z span | Z = 95 to Z = 200 mm | From dock ceiling to top rim |
| Available height | 105 mm | Two rows of 56 mm valves + 4 mm gap = 116 mm — exceeds 105 mm |

**DESIGN GAP (DG-T3): Two rows of valves at 56 mm height each with a 4 mm gap require 116 mm of Z span. The available Z from dock ceiling (Z = 95) to top rim (Z = 200) is only 105 mm. Resolution: Lower the dock ceiling from Z = 95 to Z = 84 by reducing clearance above the pumps. Pump height is 62.6 mm. Dock floor is at Z = 20. Pump top is at Z = 82.6. With dock ceiling at Z = 84, clearance above pump is 1.4 mm — too tight for the cartridge rail top edge. Alternative: raise the top rim is not possible (fixed at Z = 200). Alternative: overlap the lower valve row with the dock zone by placing valves beside the dock rather than above it. The dock width is only 160 mm in a 212 mm interior, leaving 26 mm on each side -- not enough for 50.84 mm deep valves. Alternative: stack the two rows with reduced gap: lower row center Z = 104.5 (white body bottom at Z = 95, top at Z = 114.5, coil top at Z = 151), upper row center Z = 160 (white body bottom at Z = 150.5, top at Z = 170, coil top at Z = 207). The upper coil extends to Z = 207, above the rim (Z = 200). This does not work either. Alternative: reduce row count to 1 row of 5 (only 5 valves) plus a second row of 5 shifted to Y positions flanking the dock. Or accept that 10 valves cannot fit in the tub at these dimensions.**

**Revised valve arrangement (addressing DG-T3): Use a staggered layout. The lower row of 5 sits immediately above the dock ceiling with the bottom of the white valve bodies resting at Z = 95 (white body top at Z = 114.4, coil top at Z = 151). The upper row of 5 sits with white body bottoms at Z = 141 (4 mm gap above lower row solenoid tops is insufficient since lower coil tops are at Z = 151). Re-computing: lower row white body bottom Z = 95, white body top Z = 114.4, metal coil bottom Z = 114.4, spade connector top Z = 151. Upper row needs white body bottom at Z = 155 minimum (4 mm above lower connector tops). Upper row white body top Z = 174.4, coil top Z = 211 -- still above Z = 200.**

**DESIGN GAP (DG-T3, unresolved): 10 Beduan solenoid valves in two rows cannot fit vertically between Z = 95 and Z = 200 (105 mm available, ~116 mm needed including spade connectors of the upper row extending above Z = 200). The spade connectors of the upper row extend 11 mm above the rim. Options: (a) accept that the upper row's spade connectors protrude into the cap's interior volume (the cap has space at Z = 200-210 before bag cradle structures begin), (b) tilt the upper row valves, (c) reduce valve count. Option (a) is adopted: the spade connectors are flexible wire terminals that can angle/bend slightly, and the cap's interior at Z = 200-210 is clear of structures at the Y = 220 zone. The valve cradle tops remain below Z = 200. Only the spade connector tips of the upper row extend above.**

**Final valve Z positions (adopted):**

| Row | White body bottom Z | White body top Z | Spade connector top Z | Notes |
|-----|---------------------|------------------|-----------------------|-------|
| Lower | 95.0 mm | 114.4 mm | 151.0 mm | Fits within tub |
| Upper | 155.0 mm | 174.4 mm | 211.0 mm | Connectors extend 11 mm into cap volume |

### 4.5 Valve Block Support Structure

The valve cradles cannot float -- they must be connected to the tub walls.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Lower row support | Cradle floors rest on the dock rear wall top edge (Z = 95) and on 2 mm thick ribs spanning from left to right inner walls | 3 ribs at Y = 200, 220, 240 mm, each 2 mm thick (Y), spanning full interior width |
| Upper row support | Cradle floors rest on ribs spanning side walls, positioned at Z = 155 | Same 3 ribs, with a shelf at Z = 155 |
| Rib depth (Y) | 2.0 mm each | Thin to minimize tube routing obstruction |
| Rib height (Z span) | From dock ceiling (Z = 95) to Z = 200 (rim) | Full remaining height, providing structural rigidity |

---

## 5. Tube Routing Channels

Tubes connect the valve block to the rear bulkhead fittings and to the cartridge dock. Channels are half-round troughs printed into the tub's inner walls and floor, with snap-over clips for tube retention.

### 5.1 Channel Profile

| Parameter | Value | Notes |
|-----------|-------|-------|
| Channel cross-section | Half-round, 4.0 mm radius | Accepts 6.35 mm (1/4") OD tube with 0.83 mm radial clearance |
| Channel wall thickness | 2.0 mm | Printed integral with tub wall |
| Snap-over clips | Every 40 mm along channel length | 1.0 mm thick cantilever arms, 6 mm wide, 0.5 mm interference on tube |

### 5.2 Channel Routes

**Valve-to-rear-bulkhead routes:** Each valve's outlet port connects to a John Guest fitting on the tub's rear wall. Tubes route along the rear inner wall (Y = 296 mm face) in a organized bundle, descending or ascending as needed to reach their respective bulkhead fitting positions.

**Valve-to-dock routes:** Tubes from the 4 cartridge-facing valves (pump inlet/outlet pairs) route from the valve block zone downward and forward to the John Guest stubs on the dock rear wall. These channels run along the left and right inner walls to avoid blocking the dock interior.

**Cap-to-valve routes:** Two tubes from the cap's bag outlets (passing through the seam plane at Y = 280, X = 70 and X = 150) route from the bottom rim downward into the valve block zone. Channels for these are on the rear inner wall.

### 5.3 Routing Channel Positions

**DESIGN GAP (DG-T4): Exact tube routing paths depend on the specific valve-to-fitting assignments, which are determined by the plumbing schematic (which valve connects to which fitting). The channels documented here are the structural provision (half-round troughs with clips). Exact positions require the plumbing schematic to be finalized. The rear wall and left/right walls each have space for 3-4 parallel channels at 10 mm pitch.**

---

## 6. Rear Wall Pass-Throughs

The tub's rear wall (Y = 300 exterior, Y = 296 inner face) carries all external plumbing connections. Each connection is a John Guest PP0408W union fitting press-fit into a pocket bore, with one end protruding outside the enclosure and the other inside.

### 6.1 Rear Bulkhead Fitting Positions

| Fitting | Function | X position | Z position | Notes |
|---------|----------|-----------|-----------|-------|
| RB-1 | Carbonated water inlet | 40.0 mm | 120.0 mm | Left side |
| RB-2 | Carbonated water outlet | 40.0 mm | 150.0 mm | Left side, above inlet |
| RB-3 | Tap water inlet (clean cycle) | 110.0 mm | 120.0 mm | Center |
| RB-4 | Flavor 1 dispensing outlet | 150.0 mm | 120.0 mm | Right-of-center |
| RB-5 | Flavor 2 dispensing outlet | 180.0 mm | 120.0 mm | Right side |

**DESIGN GAP (DG-T5): The concept document mentions "two outlets for each flavoring dispense" and "inlet and outlet for the refrigerated carbonated water" and "inlet for tap water" = 6 rear fittings minimum. However, the plumbing schematic may require additional pass-throughs (e.g., bag fill lines from the tap water system). 5 fittings are specified above; a 6th position is reserved at X = 180, Z = 150 for future use. The exact count depends on the final plumbing schematic.**

### 6.2 Rear Bulkhead Pocket Design

Each bulkhead pocket is identical to the dock rear wall pockets (Section 3.4), adapted for the 4.0 mm thick exterior rear wall.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Press-fit bore diameter | 9.1 mm | 0.21 mm interference on 9.31 mm JG center body |
| Wall thickness at pocket | 6.0 mm | Locally thickened from 4 mm to accommodate press-fit depth |
| Local thickening | 2.0 mm boss protruding inward from rear wall inner face | 6 mm total pocket depth |
| Counterbore (exterior side) | None | Body-end (15.10 mm OD) protrudes freely; the shoulder seats against the exterior wall face |
| Counterbore (interior side) | None | Body-end protrudes freely into interior |
| Chamfer (exterior) | 1.0 mm | Around each pocket bore on the exterior face, per design language |

### 6.3 Debossed Icons

Each rear bulkhead fitting has a debossed languageless icon adjacent to it (per vision document: no text, no logos on user-facing surfaces; rear face uses debossed icons only).

| Parameter | Value | Notes |
|-----------|-------|-------|
| Icon size | 10 x 10 mm | Square icon field |
| Icon depth (deboss) | 0.4 mm | Shallow deboss, visible under raking light |
| Icon position | 5 mm above each fitting center | Centered on fitting X, Z + 20 mm |
| Icon content | Languageless symbols: water drop (inlet), arrow-out (outlet), wrench (clean), cup (flavor) | Specific icon designs TBD |

### 6.4 Wire Pass-Through (Rear Wall)

One pass-through for the power cable on the rear wall.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Shape | Rectangular with 2 mm corner radius | |
| Size | 12 x 8 mm | Accommodates barrel jack or USB cable |
| Position | X = 110 mm (centered), Z = 30 mm | Low on rear wall, below valve zone |
| Chamfer | 1.0 mm | Exterior edge |

### 6.5 Cap Interface Pass-Throughs (Top Rim)

The tub's top rim has pass-throughs that align with the cap's bottom rim pass-throughs for tubes and wires crossing the seam plane.

| Pass-through | Shape | Size | Position | Matches cap feature |
|--------------|-------|------|----------|-------------------|
| Bag 1 tube | Circular | 8.0 mm dia | X = 70, Y = 280, Z = 200 | Cap Section 3.5 |
| Bag 2 tube | Circular | 8.0 mm dia | X = 150, Y = 280, Z = 200 | Cap Section 3.5 |
| Wire harness 1 | Rectangular | 12 x 6 mm | X = 40, Y = 290, Z = 200 | Cap Section 4.4 |
| Wire harness 2 | Rectangular | 12 x 6 mm | X = 180, Y = 290, Z = 200 | Cap Section 4.4 |

These are notches in the top rim, open at the top face (Z = 200). They align with matching notches in the cap's bottom rim to form complete pass-through holes when the two halves are assembled. The tongue is interrupted at each pass-through location.

---

## 7. Rubber Foot Recesses

Four recesses on the bottom face (Z = 0 exterior) accept press-fit silicone rubber feet.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Foot count | 4 | One near each corner |
| Recess shape | Circular | |
| Recess diameter | 15.0 mm | Accepts standard 12-14 mm OD adhesive rubber feet with clearance |
| Recess depth | 1.5 mm | Feet protrude below the bottom face by ~2-3 mm (foot thickness minus recess depth) |
| Recess positions (X, Y on bottom face) | (30, 30), (190, 30), (30, 270), (190, 270) | 30 mm inset from each corner |

**DESIGN GAP (DG-T6): Rubber foot dimensions are assumed (12-14 mm OD, 3.5-4.5 mm thick). No specific part has been selected or caliper-verified. The recess diameter (15 mm) and depth (1.5 mm) are based on common adhesive-backed silicone feet available from Amazon.**

---

## 8. Cartridge Opening Detail

The cartridge opening is the primary user-facing aperture on the tub. It is specified in Section 3.5 above. Additional detail on the exterior presentation:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Exterior surface presentation | Rectangular aperture with 1 mm chamfer on all 4 edges | Flush cartridge front face when docked |
| Reveal around cartridge | 0.5 mm gap between cartridge front face and opening perimeter | Uniform gap; cartridge face is 151 x 74 mm, opening is 152 x 75 mm |
| Cartridge face material | Same ASA, same finish | Appears as part of the front surface when docked |

---

## 9. Below-Dock Zone (Z = 4 to Z = 20)

The space between the interior floor (Z = 4) and the dock floor (Z = 20) is reserved for cable routing and structural support.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Zone height | 16.0 mm | Z = 4 to Z = 20 |
| Zone use | Wire harness routing from rear wall power pass-through to valve zone | Wires run along the interior floor beneath the dock |
| Dock floor support | The dock floor (Z = 16-20) is supported by 4 ribs running front-to-back (Y direction) at X = 50, 90, 130, 170 mm | Each rib is 2 mm thick (X) x 16 mm tall (Z = 4 to Z = 20) |

---

## 10. Print Considerations

### 10.1 Orientation

The tub prints upright, open face up. The bottom face (Z = 0) is on the build plate. The top rim (Z = 200) is the last layer.

| Assembly feature | Print Z | Notes |
|-----------------|---------|-------|
| Bottom face exterior | Print Z = 0 | On build plate |
| Interior floor | Print Z = 4 mm | |
| Rubber foot recesses | Z = 0 to Z = 1.5 mm | Formed as shallow pockets on build plate |
| Below-dock ribs | Z = 4 to Z = 20 | Vertical ribs, no supports |
| Dock floor | Z = 16 to Z = 20 | Horizontal surface; needs support beneath |
| Guide rails | Z = 20 to Z = 25 | Built on top of dock floor |
| Cartridge opening | Through-hole in front wall, Z = 20 to Z = 95 | Vertical walls, no supports |
| Valve cradles | Z = 95 to Z = 175 | U-channels, some interior supports needed |
| Snap-fit catches | Z = 165 to Z = 200 | Cantilever beams protruding inward; hook undersides need support |
| Tongue | Z = 200 to Z = 203 | Last printed layers; no support needed |

### 10.2 Support Requirements

| Feature | Support needed? | Type | Notes |
|---------|----------------|------|-------|
| Exterior walls | No | N/A | Vertical, no overhang |
| Cartridge opening | No | N/A | Through-hole with vertical walls |
| Dock floor underside | Yes | Tree supports (ASA) | Horizontal surface at Z = 16-20, spanning 160 mm |
| Valve cradle retention bars | Yes | Tree supports (ASA) | Small horizontal beams |
| Snap-fit catch hook undersides | Yes | Tree supports (ASA) | 8 hooks at Z = 165, small area each |
| Valve block support ribs | No | N/A | Vertical ribs |
| Tongue | No | N/A | Small protrusion on top rim, last layers |

### 10.3 Bed Fit Verification

| Dimension | Tub value | H2C limit | Margin |
|-----------|-----------|-----------|--------|
| X (width) | 220 mm | 325 mm | 105 mm |
| Y (depth) | 300 mm | 320 mm | 20 mm |
| Z (height) | 203 mm (including tongue) | 320 mm | 117 mm |

All dimensions within bed limits. The 20 mm Y margin is the tightest constraint; a 5-8 mm brim reduces available margin to 12-15 mm, adequate.

---

## 11. Summary of Design Gaps

| ID | Gap | Impact | Resolution needed |
|----|-----|--------|-------------------|
| DG-T1 | Draft direction resolved: tub walls are vertical (no draft), cap provides all taper | Departs from concept's "3-degree draft on side walls" for the full enclosure -- only the cap has drafted walls | Confirm with product owner that a vertical-walled tub with a drafted cap is acceptable |
| DG-T2 | Snap-fit catch beams lengthened from 15 mm to 35 mm to stay within ASA strain limits | Catches extend deeper into tub interior (down to Z = 165) | Verify no interference with valve block at those X/Y positions |
| DG-T3 | Upper valve row spade connectors extend 11 mm above tub rim (to Z = 211) | Connectors protrude into cap interior volume | Verify cap interior is clear at Z = 200-211 in the Y = 220 zone (per cap spec, bag cradles begin at ~Z = 220; this zone should be clear) |
| DG-T4 | Exact tube routing channel positions not specified | Cannot generate drawing without plumbing schematic | Finalize plumbing schematic, then specify exact channel positions |
| DG-T5 | Rear bulkhead fitting count may be 5, 6, or more depending on plumbing schematic | Fitting positions are provisional | Finalize plumbing schematic |
| DG-T6 | Rubber foot dimensions assumed, not caliper-verified | Recess dimensions may not match selected feet | Select specific rubber feet and caliper-verify |
| DG-T7 | Dock tube stub Z positions (55 and 75 mm) assume the cartridge's JG fitting positions, which depend on the cartridge design | Mismatch would prevent cartridge docking | Cross-reference with cartridge parts specification when available |
| DG-T8 | Valve cradle Y position (Y = 220 center) and depth (54 mm) must clear the dock rear wall back face (Y = 140) | Lower row cradle front face at Y = 220 - 27 = 193 mm; clears dock rear wall at Y = 140 | Confirmed clear, but tube routing between dock and valves must fit in the Y = 140-193 gap |

---

## 12. Interface Summary

All interfaces between the tub and other parts/components:

| Interface | Tub feature | Mating feature | Dimensions |
|-----------|------------|----------------|------------|
| Tub-to-cap tongue | 1.5 mm wide x 3.0 mm tall tongue on top rim | 1.7 mm wide x 3.2 mm deep groove on cap bottom rim | 0.1 mm side clearance, 0.2 mm depth clearance |
| Tub-to-cap snaps | 8 cantilever catches (35 mm beam, 2.0 mm hook) on inner walls at Z = 165-200 | 8 ledges (15 x 2 x 2 mm) on cap inner walls at Z = 205 | 2.0 mm engagement depth, 90-degree catch |
| Tub-to-cap reveal | Tub outer wall flush at seam (X = 0 to 220, Y = 0 to 300 at Z = 200) | Cap outer wall inset 0.8 mm per side at Z = 200 | 0.8 mm reveal step |
| Bag tube pass-throughs | 2x 8.0 mm holes at X = 70/150, Y = 280, Z = 200 | Matching holes in cap bottom rim | 6.35 mm tube in 8.0 mm hole |
| Wire pass-throughs | 2x 12 x 6 mm slots at X = 40/180, Y = 290, Z = 200 | Matching slots in cap bottom rim | Sized for wire bundle |
| Cartridge-to-dock rails | 2 rails (4 mm wide x 5 mm tall) at X = 50/170 | Cartridge underside grooves (4.5 mm wide x 5.5 mm deep) | 0.25 mm X clearance, 0.5 mm Z clearance |
| Cartridge-to-dock JG stubs | 4x JG PP0408W press-fit in dock rear wall at X = 75/145, Z = 55/75 | 4x JG PP0408W on cartridge rear face | Collet grip on 1/4" OD tube; tube insertion ~16 mm |
| JG fitting-to-dock wall press-fit | 9.1 mm bore in 6 mm wall | 9.31 mm OD JG center body | 0.21 mm interference (press-fit) |
| JG body-end-to-wall clearance | 15.10 mm OD body-end protrudes freely on both sides of wall | No bore constraint | Shoulder seats against wall face |
| Valve-to-cradle | U-channel: 34 mm wide x 54 mm deep x 20 mm tall | Beduan valve: 32.71 mm wide x 50.84 mm deep x 19.4 mm white body height | 0.65 mm X clearance/side, 1.6 mm Y clearance/side, 0.6 mm Z clearance |
| Valve retention bar | 1.5 mm thick bar spanning 38 mm across cradle top | Top of white valve body (~19.4 mm tall) | Bar snaps over body; 1.5 mm hook engagement |
| Rear bulkhead JG fittings | 9.1 mm bore in locally thickened (6 mm) rear wall | 9.31 mm OD JG center body | 0.21 mm interference (press-fit) |
| Rubber feet-to-recess | 15 mm dia x 1.5 mm deep circular recess | ~12-14 mm OD rubber foot | ~0.5-1.5 mm radial clearance |
| Power cable pass-through | 12 x 8 mm rectangular hole in rear wall at X = 110, Z = 30 | Barrel jack or USB cable | Sized for cable passage |
