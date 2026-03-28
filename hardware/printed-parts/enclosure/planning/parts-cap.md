# Enclosure Cap — Parts Specification

## Coordinate System

- **Origin:** Front-left-bottom corner of the enclosure exterior (shared with tub).
- **X:** Width, left to right. 0 to 220 mm.
- **Y:** Depth, front to back. 0 to 300 mm.
- **Z:** Height, bottom to top. The cap spans from Z ~200 mm (seam plane) to Z ~400 mm (top face).
- **Draft convention:** The 3-degree inward draft means the cap is widest at its bottom rim (Z = 200) and narrowest at the top (Z = 400). Similarly for depth. All X/Y dimensions given below are at the **bottom rim** (Z = 200) unless stated otherwise.

## Exterior Envelope

| Parameter | Value | Notes |
|-----------|-------|-------|
| Width at bottom rim (X) | 220.0 mm | Matches tub top rim |
| Depth at bottom rim (Y) | 300.0 mm | Matches tub top rim |
| Height (Z span) | 200.0 mm | Z = 200 to Z = 400 |
| Width at top face (X) | 220.0 - 2 * 200 * tan(3 deg) = **199.1 mm** | 3-degree draft per side |
| Depth at top face (Y) | 300.0 - 2 * 200 * tan(3 deg) = **279.1 mm** | 3-degree draft per side |
| Wall thickness | 4.0 mm | Uniform on all four sides and top face |
| Vertical edge radius | 8.0 mm | All 4 vertical exterior edges |
| Top-face-to-side radius | 5.0 mm | All 4 top edges |
| Aperture chamfer | 1.0 mm | All exterior aperture edges |

**Print orientation:** Open face up (bottom rim faces ceiling). The cap prints inverted -- the top face (Z = 400 in assembly) is on the build plate, and the bottom rim (Z = 200 in assembly) is the last layer printed. This means the interior faces upward during printing, and all interior features build from the top face down toward the open bottom rim.

---

## 1. Mechanism Narrative

### What the user sees and touches

The cap is the upper half of a dark charcoal monolithic tower. Its exterior presents four featureless drafted side walls (3-degree taper, narrower at top), a flat top face with one aperture (the funnel opening), and a front face with three flush-mounted circular elements (two displays and the air switch). The user touches the cap in three ways: pouring liquid into the funnel on top, pressing the air switch on the front face, and optionally snapping out the displays or air switch for external mounting.

The bottom rim of the cap carries the mating geometry for the permanent joint to the tub. Once assembled and solvent-welded, the cap never separates from the tub. The 0.8 mm reveal step at the seam is the only visible evidence of the two-piece construction.

### What moves during assembly (one-time)

During the single assembly event, the cap translates downward (-Z) onto the tub. The tongue-and-groove joint self-aligns the two halves. Eight snap-fit catches on the tub's inner walls engage eight ledges on the cap's inner walls -- each catch deflects outward during insertion then springs back to lock behind the ledge. This is a permanent, destructive-to-separate engagement.

### What moves during use

Nothing on the cap moves during normal use except the removable funnel insert, which lifts straight up (+Z) out of the funnel opening for cleaning. The displays and air switch can be snapped out of their apertures (pulled forward, -Y direction from the rear retention clips, which is +Y from the user's perspective outside the front face) for external mounting, but this is a one-time configuration choice, not a regular operation.

### Retention mechanisms

- **Funnel insert:** Sits in a stepped recess by gravity. A 2.0 mm lip around the top of the recess prevents lateral movement. The insert's flange rests on the lip. No snap retention -- the insert must be freely removable for dishwasher cleaning.
- **Displays and air switch:** Each sits in a stepped circular pocket in the front wall. From behind, two diametrically opposed cantilever snap tabs (integral to the cap's inner wall) engage a shoulder on the component body. To remove: the user pushes the component from behind (if access exists before assembly) or pulls firmly from the front, deflecting the snap tabs inward until they release. After enclosure assembly, the snap tabs are accessible only through the aperture itself -- the user pulls the component forward and the tabs deflect.

---

## 2. Bottom Rim — Tub Interface

The bottom rim is the mating surface where the cap joins the tub. It runs the full perimeter at Z = 200 mm.

### 2.1 Groove (mates with tub tongue)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Groove width | 1.7 mm | Accepts 1.5 mm tongue with 0.1 mm clearance per side |
| Groove depth | 3.2 mm | Accepts 3.0 mm tall tongue with 0.2 mm clearance at bottom |
| Groove position | Centered in the 4.0 mm wall thickness | 1.15 mm from outer face, 1.15 mm from inner face |
| Groove profile | Rectangular, open at bottom face of rim | Runs continuous around full perimeter |

The groove is machined into the bottom face of the cap's rim. It runs continuously around all four sides, following the 8 mm corner radii at the vertical edges. The groove walls are raw (unsmoothed) ASA for optimal solvent weld adhesion -- the cap prints with the bottom rim at the top of the print, so the groove is formed naturally by the slicer without supports.

### 2.2 Reveal Step

| Parameter | Value | Notes |
|-----------|-------|-------|
| Step depth (inset) | 0.8 mm | Cap outer surface is 0.8 mm inward from tub outer surface |
| Step height | Flush with seam plane | The cap's outer wall begins 0.8 mm inward from the tub's outer wall at Z = 200 |

The reveal is created by making the cap's exterior footprint 0.8 mm smaller per side than the tub's exterior at the seam plane. The cap's outer wall at Z = 200 is at X = 0.8 and X = 219.2 (left/right), and Y = 0.8 and Y = 299.2 (front/back). The tub's outer wall at Z = 200 is at X = 0 and X = 220, Y = 0 and Y = 300. This creates a continuous 0.8 mm shadow gap around the perimeter.

### 2.3 Snap-Fit Ledges (8 total)

The cap carries 8 ledges on its inner walls, near the bottom rim. These mate with 8 cantilever snap catches printed into the tub's inner walls. The catches are on the tub; the ledges are on the cap.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Ledge count | 8 | 2 per side (front, back, left, right) |
| Ledge form | Horizontal shelf protruding inward from inner wall | 90-degree catch angle (permanent) |
| Ledge width (along wall) | 15.0 mm | Per ledge |
| Ledge depth (protrusion from inner wall) | 2.0 mm | Into interior volume |
| Ledge thickness (Z) | 2.0 mm | Vertical thickness of the shelf |
| Ledge Z position | Bottom face of ledge at Z = 205.0 mm | 5.0 mm above seam plane, providing clearance for the tongue-and-groove below |
| Catch engagement depth | 2.0 mm | The tub's catch hook must deflect 2.0 mm outward to pass the ledge, then springs back behind it |

**Ledge placement around perimeter (X, Y coordinates of ledge center, at inner wall):**

- Front wall (Y = 4.0 mm inner face): X = 60.0 mm, X = 160.0 mm
- Back wall (Y = 296.0 mm inner face): X = 60.0 mm, X = 160.0 mm
- Left wall (X = 4.0 mm inner face): Y = 100.0 mm, Y = 200.0 mm
- Right wall (X = 216.0 mm inner face): Y = 100.0 mm, Y = 200.0 mm

The ledges are placed to avoid interference with internal features (bag cradles, electronics shelf, display pockets, tube routing channels).

---

## 3. Bag Cradles

Two Platypus 2L bag cradles occupy the primary interior volume of the cap. Each bag is mounted diagonally per the vision document: bag cap (outlet) at back-bottom, bag top pinned to the front wall.

### 3.1 Platypus 2L Bag — Filled Dimensions (reference)

| Parameter | Value | Source |
|-----------|-------|--------|
| Filled length | ~330 mm | Requirements doc |
| Filled width | ~180 mm | Requirements doc |
| Filled thickness | ~80 mm | Requirements doc |

**DESIGN GAP: Platypus 2L bag dimensions are approximate ("~330 mm long x 180 mm wide x 80 mm thick" from the concept document). No caliper-verified measurements exist. The cradle dimensions below are derived from these approximate values. Caliper verification of a filled bag is needed before finalizing cradle geometry.**

### 3.2 Diagonal Mounting Geometry

Each bag is tilted at approximately 45 degrees from horizontal. In this orientation:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Bag length projection onto Y (depth) | 330 * cos(45 deg) = **233.3 mm** | Fits within 292 mm interior depth (300 - 2*4) |
| Bag length projection onto Z (height) | 330 * sin(45 deg) = **233.3 mm** | Exceeds 192 mm interior height (200 - 4 top wall - 4 reserved) |

**DESIGN GAP: At 45 degrees, the bag's Z-projection (233 mm) exceeds the cap's interior height (192 mm). The bags must be tilted at a shallower angle. At 35 degrees from horizontal: Z-projection = 330 * sin(35) = 189 mm, Y-projection = 330 * cos(35) = 270 mm. A 35-degree tilt fits the height. The concept document says "roughly 45 degrees" which should be interpreted as the approximate range, not a hard constraint. This specification uses 35 degrees.**

**Revised diagonal geometry at 35 degrees:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Tilt angle from horizontal | 35 degrees | Bag cap at back-bottom, bag top at front-top |
| Bag Z-projection | 330 * sin(35 deg) = **189.3 mm** | Fits within 192 mm interior height |
| Bag Y-projection | 330 * cos(35 deg) = **270.3 mm** | Fits within 292 mm interior depth |
| Bag width (X) | ~180 mm | Two bags cannot be side-by-side (2*180 = 360 > 212 mm interior width) |

The two bags are stacked vertically (one above the other), not side by side, because the interior width (212 mm) cannot hold two bags at 180 mm each. Each bag occupies nearly the full interior width.

### 3.3 Bag Stacking Arrangement

| Parameter | Value | Notes |
|-----------|-------|-------|
| Lower bag center Z | ~250 mm | Centered in lower portion of cap |
| Upper bag center Z | ~340 mm | Centered in upper portion of cap |
| Vertical spacing between bag centers | ~90 mm | 80 mm bag thickness + 10 mm clearance for cradle walls |
| Lower bag outlet (cap end) position | Back-bottom of cap, near Y = 280 mm, Z = 210 mm | Just above seam plane, tube routes down through rim |
| Upper bag outlet (cap end) position | Back of cap, near Y = 280 mm, Z = 300 mm | Tube routes down behind lower bag to seam plane |

### 3.4 Cradle Construction

Each cradle is a lens-shaped half-shell printed integrally with the cap's side walls. The cradle supports the bag's natural filled elliptical cross-section from below and the sides. Living-hinge retention clips at the top of each cradle fold over to loosely contain the bag.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cradle shell thickness | 2.0 mm | Structural support for filled bag (~2 kg water weight) |
| Cradle interior width (X) | 184.0 mm | 180 mm bag + 2 mm clearance per side |
| Cradle interior depth profile | Lens-shaped, matching bag's natural filled cross-section | Elliptical: ~80 mm thick at center, tapering to edges |
| Living-hinge clips | 2 per cradle, spaced at 1/3 and 2/3 along bag length | 1.0 mm thick at hinge, 8.0 mm wide, 15.0 mm long arm |
| Clip engagement | Clips fold over the top of the bag, resting against upper surface | No snap -- just gravity and light elastic preload |

**Cradle attachment to cap walls:** Each cradle is connected to the left and right inner walls of the cap via 3 printed ribs per side (6 ribs total per cradle). Each rib is 3.0 mm thick (Y) x 2.0 mm wide (X) and spans from the inner wall to the cradle shell. The ribs are angled at 35 degrees (matching the bag tilt) and carry the bag's weight to the enclosure walls.

### 3.5 Bag Outlet Tube Routing

Each bag's outlet (at the cap end of the Platypus bottle) connects to 1/4" OD silicone tubing that must route downward through the cap's bottom rim into the tub's valve block.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Tube OD | 6.35 mm (1/4") | Standard throughout system |
| Tube routing channel | Printed half-round channel (4.0 mm radius) in rear inner wall | Routes from bag outlet position downward to seam plane |
| Tube pass-through at bottom rim | 8.0 mm diameter hole through bottom rim | 2 holes, one per bag, in rear wall at Y = 280 mm |
| Pass-through positions (X) | X = 70 mm (bag 1), X = 150 mm (bag 2) | Spaced to align with valve block in tub |
| Pass-through Z | Z = 200 mm | Through the seam plane rim |

The channels have snap-over clips every 40 mm to retain the tubing. Each clip is a 1.0 mm thick cantilever arm, 6 mm wide, that snaps over the tube with 0.5 mm interference.

---

## 4. Electronics Shelf

The electronics shelf sits at the upper rear of the cap interior, above and behind the upper bag cradle. It holds the ESP32, three L298N motor drivers, and the DS3231 RTC module.

### 4.1 Component Dimensions (reference)

| Component | Dimensions (L x W x H) | Source |
|-----------|------------------------|--------|
| ESP32-DevKitC-32E | ~55 x 28 x 13 mm | Datasheet typical |
| L298N driver board | ~43 x 43 x 27 mm | Datasheet typical |
| DS3231 RTC module | ~38 x 22 x 14 mm | Datasheet typical |

**DESIGN GAP: ESP32, L298N, and DS3231 dimensions are from datasheets and typical measurements, not caliper-verified. These should be measured before finalizing pocket dimensions.**

### 4.2 Shelf Geometry

| Parameter | Value | Notes |
|-----------|-------|-------|
| Shelf Z position (top surface) | Z = 380 mm | 20 mm below top interior face (Z = 400 - 4 wall - 16 clearance) |
| Shelf Y span | Y = 220 mm to Y = 292 mm | 72 mm deep, against rear wall |
| Shelf X span | X = 8 mm to X = 211 mm | 203 mm wide, nearly full interior width |
| Shelf thickness | 3.0 mm | Printed integral with rear and side walls |
| Shelf support | 3 ribs underneath, 3 mm thick x 20 mm tall, at X = 50, 110, 170 mm | Ribs connect shelf to rear wall |

### 4.3 Component Pockets

Each component sits in a recessed pocket with snap tabs for retention. Pockets are shallow depressions (1.5 mm deep) in the shelf surface, with 2 snap tabs per component.

**Layout on shelf (X positions, all at shelf Z = 380):**

| Component | X center | Y center | Pocket size (X x Y) | Notes |
|-----------|----------|----------|---------------------|-------|
| ESP32 | 35 mm | 256 mm | 58 x 31 mm | 1.5 mm clearance per side |
| L298N #1 | 100 mm | 256 mm | 46 x 46 mm | 1.5 mm clearance per side |
| L298N #2 | 150 mm | 256 mm | 46 x 46 mm | 1.5 mm clearance per side |
| L298N #3 | 100 mm | 235 mm | 46 x 46 mm | Forward of #1, staggered |
| DS3231 RTC | 170 mm | 235 mm | 41 x 25 mm | 1.5 mm clearance per side |

**DESIGN GAP: The three L298N boards at 46 mm each may not all fit in the 72 mm shelf depth. Two in a row (Y = 256 center, spanning Y = 233 to Y = 279) fit. The third, staggered forward (Y = 235 center, spanning Y = 212 to Y = 258), overlaps with the upper bag cradle zone. This layout needs validation against the actual bag cradle envelope. The electronics shelf may need to extend further forward or the upper bag may need to be positioned lower.**

Snap tabs: Each pocket has 2 cantilever snap tabs on opposite long sides.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Tab length | 8.0 mm | Cantilever length from pocket wall |
| Tab width | 3.0 mm | Along pocket edge |
| Tab thickness | 1.0 mm | At root |
| Tab overhang | 1.5 mm | Engages top of PCB |
| Tab deflection for insertion | 1.5 mm | Component presses tabs outward during insertion |

### 4.4 Wire Routing

A 10 mm wide x 8 mm deep channel runs along the front edge of the shelf (Y = 220 mm) for the wiring harness. This channel routes wires from the electronics shelf downward along the side walls to the seam plane, where they pass into the tub through designated wire pass-throughs.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Wire channel width | 10.0 mm | Along shelf front edge |
| Wire channel depth | 8.0 mm | Below shelf surface |
| Wire pass-throughs at bottom rim | 2 rectangular slots, 12 x 6 mm each | In rear wall at Y = 290 mm, X = 40 mm and X = 180 mm |

---

## 5. Funnel/Hopper Opening

The funnel opening is on the top face of the cap, positioned as far forward as possible (per requirements: "as close to the front as possible").

### 5.1 Opening Geometry

| Parameter | Value | Notes |
|-----------|-------|-------|
| Shape | Rectangular with 5.0 mm corner radius | Matches top-face design language |
| Opening X span | X = 60 mm to X = 139 mm | 79 mm wide, centered at X = 99.6 mm (center of top face) |
| Opening Y span | Y = 20 mm to Y = 90 mm | 70 mm deep, forward-biased |
| Opening size | 79 x 70 mm | Large enough for pouring from a SodaStream bottle |
| Lip height | 2.0 mm | Raised lip around opening on top face, contains drips |
| Lip width | 3.0 mm | Annular flat surface for funnel insert flange to rest on |
| Chamfer | 1.0 mm | On outer edge of opening, per design language |

**Note:** The top face at the opening location is at approximately Z = 396 mm (Z = 400 minus 4 mm wall thickness). The top face exterior is at Z = 400, and the 2.0 mm lip raises the rim to Z = 402 locally.

**Correction:** The lip is a 2.0 mm tall raised rim on the top exterior surface. The exterior top face is at Z = 400; the lip outer edge is at Z = 402. The lip inner edge (where the funnel insert flange sits) is at Z = 400 (flush with the general top face). The lip is formed by a 2.0 mm tall, 3.0 mm wide rectangular ring on the exterior surface surrounding the opening.

### 5.2 Funnel Insert Recess

The removable funnel insert sits in a stepped recess inside the opening.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Recess step depth (below top face) | 4.0 mm | Matches wall thickness -- the insert flange sits on the inner surface of the top wall |
| Recess step width | 3.0 mm | Annular ledge inside the opening for insert flange |
| Insert flange OD | Rectangular, 78 x 69 mm with 5 mm radius corners | 0.5 mm clearance per side in 79 x 70 mm opening |
| Insert flange thickness | 2.0 mm | Sits on the recess ledge |
| Keying | None | Rectangular shape prevents rotation; insert drops in any of 2 orientations (180-degree symmetry) |

### 5.3 Funnel Throat Routing

Below the funnel insert, a printed tube-guide channel routes the funnel's outlet downward and rearward to the bag fill line.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Throat position | Center of funnel opening, descending from Z = 396 mm | Printed channel integral with cap interior |
| Throat ID | 12.0 mm | Accepts funnel insert's outlet tube |
| Routing path | Descends from Z = 396 at Y = 55 mm to Z = 210 at Y = 270 mm | Curves rearward behind the bag cradles |
| Channel form | Half-round printed trough on inner rear wall | Open on one side for tube insertion during assembly |

---

## 6. Front Face Apertures

Three circular apertures on the cap's front face (Y = 0 exterior surface) for the RP2040 display, S3 display, and KRAUS air switch. These sit in the lower portion of the cap's front face, between the bag cradle zone above and the seam line below.

### 6.1 Aperture Zone

The front face of the cap spans from Z = 200 (seam) to Z = 400 (top). The bag cradles begin at approximately Z = 220 and occupy most of the interior. The aperture zone for displays and air switch is:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Aperture zone Z range | Z = 210 to Z = 280 | Between seam plane and bag cradles |
| Aperture zone X range | Full front face width | Components centered or distributed across width |
| Front wall thickness at apertures | 4.0 mm | Standard wall thickness |

### 6.2 RP2040 Display (Waveshare 0.99" Round LCD)

| Parameter | Value | Source |
|-----------|-------|--------|
| Display active area diameter | 25.15 mm (0.99") | Waveshare datasheet |
| PCB diameter | ~33.0 mm | Waveshare datasheet (round PCB) |
| PCB thickness | ~1.6 mm | Standard |

**DESIGN GAP: RP2040 round display PCB dimensions are from datasheet, not caliper-verified. The PCB diameter, total thickness including components on the back, and the exact bezel/active area relationship need caliper verification.**

**Aperture specification:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Aperture shape | Circular | Flush-mount round display |
| Aperture diameter (exterior) | 26.0 mm | Clears 25.15 mm active area + 0.4 mm margin per side; 1.0 mm chamfer on outer edge |
| Stepped pocket diameter (interior) | 34.0 mm | Accepts 33.0 mm PCB with 0.5 mm clearance |
| Pocket depth from exterior surface | 2.5 mm | Display glass sits flush with exterior; PCB recesses into pocket |
| Aperture center position | X = 110 mm, Z = 245 mm | Centered on front face (see Section 6.5 revised layout) |
| Snap retention tabs | 2 tabs, diametrically opposed (top and bottom) | Cantilever snaps engaging PCB shoulder from behind |

Snap tab dimensions:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Tab length | 6.0 mm | Cantilever from pocket wall |
| Tab width | 4.0 mm | Arc segment |
| Tab thickness | 1.2 mm | At root |
| Tab overhang | 1.0 mm | Engages behind PCB edge |

### 6.3 S3 Display (Meshnology ESP32-S3 1.28" Round Rotary)

| Parameter | Value | Source |
|-----------|-------|--------|
| Display active area diameter | 32.51 mm (1.28") | Meshnology listing |
| Total module diameter (with rotary knob ring) | ~42.0 mm | Estimated from listing photos |
| Knob ring protrusion beyond display face | ~5.0 mm | Estimated |

**DESIGN GAP: S3 rotary display dimensions are estimated from product listing photos, not caliper-verified. The knob ring outer diameter, total depth, and mounting shoulder dimensions are unknown. Caliper verification is required.**

**Aperture specification:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Aperture shape | Circular | Flush-mount round display with rotary knob |
| Aperture diameter (exterior) | 43.0 mm | Clears estimated 42.0 mm knob ring + 0.5 mm margin; 1.0 mm chamfer on outer edge |
| Stepped pocket diameter (interior) | 46.0 mm | Accepts module body behind the knob ring |
| Pocket depth from exterior surface | 3.0 mm | Knob ring face sits flush with exterior |
| Aperture center position | X = 170 mm, Z = 245 mm | Right on front face (see Section 6.5 revised layout) |
| Snap retention tabs | 2 tabs, diametrically opposed (left and right) | Same cantilever design as RP2040 |

Snap tab dimensions: Same as RP2040 (Section 6.2).

### 6.4 KRAUS Air Switch

| Parameter | Value | Source |
|-----------|-------|--------|
| Button diameter (visible face) | ~32.0 mm | Estimated from product photos |
| Body diameter (below flange) | ~28.0 mm | Estimated |
| Flange diameter | ~38.0 mm | Estimated |
| Body depth behind flange | ~25.0 mm | Estimated; includes pneumatic tube connector |

**DESIGN GAP: KRAUS air switch dimensions are estimated from product photos, not caliper-verified. The button face diameter, body diameter, flange dimensions, and total depth are all unknown. Caliper verification is required before finalizing this aperture.**

**Aperture specification:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Aperture shape | Circular | Flush-mount button |
| Aperture diameter (exterior) | 33.0 mm | Clears estimated 32.0 mm button face + 0.5 mm margin; 1.0 mm chamfer |
| Stepped pocket diameter (interior) | 39.0 mm | Accepts estimated 38.0 mm flange |
| Pocket depth from exterior surface | 2.0 mm | Button face sits flush with exterior |
| Aperture center position | X = 50 mm, Z = 225 mm | Far left on front face (see Section 6.5 revised layout) |
| Snap retention tabs | 2 tabs, diametrically opposed | Same cantilever design as displays |

Snap tab dimensions: Same as RP2040 (Section 6.2).

### 6.5 Aperture Layout Summary (Front Face)

```
Front face of cap, viewed from outside (Y = 0 plane, looking in +Y direction):

     X = 0                     X = 110                    X = 220
     |                           |                           |
Z=280 ............................................................
     .                                                        .
     .                                                        .
     .         [RP2040]             [S3 Display]              .
Z=245 .      X=70,Z=245            X=130,Z=245               .
     .        dia 26                 dia 43                   .
     .                                                        .
     .                [Air Switch]                            .
Z=218 .              X=110,Z=218                              .
     .                 dia 33                                 .
Z=210 ............................................................
     .                  (seam at Z=200)                       .
```

**Minimum clearance between apertures:**
- RP2040 edge to S3 edge: (130 - 70) - (26/2 + 43/2) = 60 - 34.5 = **25.5 mm** (adequate)
- S3 edge to air switch edge: sqrt((130-110)^2 + (245-218)^2) - (43/2 + 33/2) = sqrt(400+729) - 38 = 33.6 - 38 = **-4.4 mm (OVERLAP)**

**DESIGN GAP: The S3 display (center X=130, Z=245, dia 43) overlaps with the air switch (center X=110, Z=218, dia 33). The edge-to-edge distance is negative. Resolution options: (a) move the air switch lower (Z = 210 minimum, but this approaches the seam), (b) move the air switch further left or right, (c) move the S3 display higher. Recommended: move air switch to X = 110, Z = 210, which gives edge-to-edge = sqrt((130-110)^2 + (245-210)^2) - 38 = sqrt(400+1225) - 38 = 40.3 - 38 = 2.3 mm. Tight but feasible. Alternatively, lower the air switch center to Z = 208 for 4.6 mm clearance, but this places part of the aperture below the seam plane, which is not possible. The air switch must move laterally: X = 150, Z = 218 gives sqrt((130-150)^2 + (245-218)^2) - 38 = 33.6 - 38 = -4.4 mm -- same problem (symmetric). The fundamental issue is that 43 mm + 33 mm = 76 mm combined diameter across only 27 mm of Z separation. Moving the air switch to Z = 206 (just above seam) gives sqrt(20^2 + 39^2) - 38 = 43.8 - 38 = 5.8 mm clearance. This places the air switch center at Z = 206, with the aperture bottom edge at Z = 206 - 33/2 = 189.5, which is below the seam plane (Z = 200). Not feasible.**

**Revised layout after gap analysis:** Move the air switch to a separate X position to achieve adequate clearance.

- Air switch center: **X = 50 mm, Z = 225 mm** (far left, slightly higher)
- RP2040 center: **X = 110 mm, Z = 245 mm** (centered)
- S3 center: **X = 170 mm, Z = 245 mm** (right)

Clearance check:
- Air switch to RP2040: sqrt((110-50)^2 + (245-225)^2) - (26/2 + 33/2) = sqrt(3600+400) - 29.5 = 63.2 - 29.5 = **33.7 mm** (adequate)
- RP2040 to S3: (170 - 110) - (26/2 + 43/2) = 60 - 34.5 = **25.5 mm** (adequate)
- Air switch to S3: sqrt((170-50)^2 + (245-225)^2) - (43/2 + 33/2) = sqrt(14400+400) - 38 = 121.7 - 38 = **83.7 mm** (adequate)

**Updated aperture centers (replacing values in Sections 6.2, 6.3, 6.4 above):**

| Component | X center | Z center | Aperture dia |
|-----------|----------|----------|-------------|
| Air switch | 50 mm | 225 mm | 33.0 mm |
| RP2040 display | 110 mm | 245 mm | 26.0 mm |
| S3 display | 170 mm | 245 mm | 43.0 mm |

---

## 7. Top Face

The top face is a flat 4.0 mm thick panel spanning the top of the cap. At Z = 400 exterior, Z = 396 interior.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Exterior surface Z | 400.0 mm | Flat top |
| Interior surface Z | 396.0 mm | 4.0 mm wall |
| Top face exterior dimensions | 199.1 x 279.1 mm | After 3-degree draft at Z = 400 |
| Features | Funnel opening only (see Section 5) | Rest is featureless flat panel |
| Edge treatment | 5.0 mm radius on all 4 top-face-to-side transitions | Per design language |

---

## 8. Back Face Features

The cap's rear wall carries tube routing channels and wire pass-throughs. The John Guest bulkhead fittings for plumbing connections are in the tub's rear wall (below the seam plane), not in the cap.

### 8.1 Bag Fill Line Entry

The funnel/hopper system requires a fill line from the funnel throat to the bags. This line routes internally within the cap (Section 5.3) and does not penetrate the back wall.

### 8.2 Tube Pass-Throughs at Bottom Rim

See Section 3.5 -- two 8.0 mm diameter holes for bag outlet tubes passing through the bottom rim into the tub.

### 8.3 Wire Pass-Throughs at Bottom Rim

See Section 4.4 -- two 12 x 6 mm rectangular slots for wiring harness passing through the bottom rim into the tub.

---

## 9. Interior Clearances

### 9.1 Cross-Section at Z = 250 (mid-height, through bag zone)

```
Looking down (-Z), cross-section at Z = 250:

Y=0 (front)
|
|  4mm wall
|  ┌──────────────────────────────────────────────────────┐
|  │  [Air switch pocket]  [RP2040 pocket] [S3 pocket]   │ front wall
|  │                                                       │
|  │  ┌─────────────────────────────────────────────────┐ │
|  │  │              BAG CRADLE (lower)                  │ │
|  │  │         180 mm wide bag in 184 mm cradle         │ │
|  │  └─────────────────────────────────────────────────┘ │
|  │                                                       │
|  │       tube channels on rear wall                      │
|  └──────────────────────────────────────────────────────┘
|                                                     4mm wall
Y=300 (rear)

X=0 ◄────────────────── 220 mm ──────────────────► X=220
```

### 9.2 Minimum Interior Clearances

| Zone | Available (mm) | Used (mm) | Clearance (mm) | Notes |
|------|---------------|-----------|----------------|-------|
| Interior width (X) | 212 | 184 (cradle) | 14 per side | Cradle ribs attach to walls in this gap |
| Interior depth (Y) at Z=250 | 292 | 270 (bag Y-projection) | 22 total | Front wall pockets consume ~30 mm, leaving rear for tube routing |
| Interior height (Z) | 192 | 189 (bag Z-projection) + shelf | **Tight** | See Design Gap in Section 3.2 |

---

## 10. Print Considerations

### 10.1 Orientation (inverted)

The cap prints open-face-up: the top face (Z = 400) is on the build plate, and the bottom rim (Z = 200) is the last printed layer. In print coordinates:

| Assembly feature | Print Z | Notes |
|-----------------|---------|-------|
| Top face exterior | Print Z = 0 | On build plate |
| Interior top face | Print Z = 4 mm | First interior layer |
| Electronics shelf | Print Z = 20 mm | Early in print |
| Bag cradle ribs | Print Z = 20-180 mm | Throughout print |
| Funnel opening | Through-hole in top face | Forms at print Z = 0-4 mm |
| Display apertures | Through-holes in front wall | Vertical walls, no supports |
| Bottom rim groove | Print Z = 196-200 mm | Last layers; groove is open at top in print orientation |
| Snap-fit ledges | Print Z = 191-195 mm | Near top of print; undersides need support |

### 10.2 Support Requirements

| Feature | Support needed? | Type | Notes |
|---------|----------------|------|-------|
| Exterior walls | No | N/A | 3-degree draft, well within overhang limits |
| Display apertures | No | N/A | Through-holes with vertical walls |
| Snap-fit ledge undersides | Yes | Tree supports (ASA) | 8 ledges, each 15 x 2 mm underside |
| Electronics shelf | Yes | Tree supports (ASA) | Horizontal surface at print Z = 20 mm |
| Bag cradle shells | Yes | Tree supports (ASA) | Curved surfaces with some overhang |
| Living-hinge clips | No | N/A | Small, thin features that print vertically |
| Funnel lip | No | N/A | 2 mm tall ring on the build plate surface |

### 10.3 Bed Fit Verification

| Dimension | Cap value | H2C limit | Margin |
|-----------|-----------|-----------|--------|
| X (width) | 220 mm | 325 mm | 105 mm |
| Y (depth) | 300 mm | 320 mm | 20 mm |
| Z (height) | 200 mm | 320 mm | 120 mm |

All dimensions within bed limits. The 20 mm Y margin is the tightest constraint; a 5-8 mm brim on Y edges reduces available margin to 12-15 mm, which is still adequate.

---

## 11. Summary of Design Gaps

| ID | Gap | Impact | Resolution needed |
|----|-----|--------|-------------------|
| DG-1 | Platypus 2L bag filled dimensions are approximate (~330 x 180 x 80 mm), not caliper-verified | Cradle dimensions may not match actual bag shape | Caliper-verify a filled bag |
| DG-2 | Bag tilt angle adjusted from concept's "roughly 45 degrees" to 35 degrees to fit 192 mm interior height | Changes from concept, needs product owner confirmation | Confirm 35-degree tilt is acceptable |
| DG-3 | ESP32, L298N, DS3231 dimensions from datasheets, not caliper-verified | Pocket dimensions may be wrong | Caliper-verify all PCBs |
| DG-4 | L298N #3 and DS3231 pocket positions may conflict with upper bag cradle envelope | Electronics may not fit in allocated space | Validate layout against bag cradle 3D envelope |
| DG-5 | RP2040 display PCB dimensions not caliper-verified | Aperture and pocket may be wrong size | Caliper-verify |
| DG-6 | S3 rotary display dimensions estimated from photos, not caliper-verified | Aperture may be wrong size; knob ring clearance unknown | Caliper-verify |
| DG-7 | KRAUS air switch dimensions estimated from photos, not caliper-verified | Aperture may be wrong size | Caliper-verify |
| DG-8 | Original front face layout had S3/air-switch overlap; revised to spread components across full width | Layout changed from initial centered grouping | Confirm visual balance is acceptable |
| DG-9 | Interior height is tight: 189 mm bag Z-projection in 192 mm available | Only 3 mm total clearance for bag + cradle wall thickness | May need to reduce tilt angle further or accept minor bag compression |

---

## 12. Interface Summary

All interfaces between the cap and other parts/components:

| Interface | Cap feature | Mating feature | Dimensions |
|-----------|------------|----------------|------------|
| Cap-to-tub groove | 1.7 mm wide x 3.2 mm deep groove in bottom rim | 1.5 mm wide x 3.0 mm tall tongue on tub top rim | 0.1 mm side clearance, 0.2 mm depth clearance |
| Cap-to-tub snaps | 8 ledges (15 x 2 x 2 mm) on inner walls at Z = 205 | 8 cantilever catches on tub inner walls | 2.0 mm engagement depth, 90-degree catch |
| Cap-to-tub reveal | 0.8 mm inset on all 4 sides | Tub outer wall flush at seam | 0.8 mm step, full perimeter |
| Bag outlet pass-throughs | 2x 8.0 mm holes in bottom rim at Y = 280, X = 70/150 | Tube routing in tub valve block zone | 6.35 mm tube in 8.0 mm hole (0.83 mm radial clearance) |
| Wire pass-throughs | 2x 12 x 6 mm slots in bottom rim at Y = 290, X = 40/180 | Wiring from tub | Sized for wire bundle |
| RP2040 aperture | 26 mm dia exterior, 34 mm dia pocket | RP2040 round PCB (~33 mm dia) | 0.5 mm radial clearance in pocket |
| S3 aperture | 43 mm dia exterior, 46 mm dia pocket | S3 module (~42 mm dia with knob) | 0.5 mm clearance exterior, 2.0 mm pocket |
| Air switch aperture | 33 mm dia exterior, 39 mm dia pocket | KRAUS air switch (~32 mm button, ~38 mm flange) | 0.5 mm clearance |
| Funnel insert recess | 79 x 70 mm opening with 3 mm ledge at -4 mm depth | Funnel insert flange (78 x 69 x 2 mm) | 0.5 mm clearance per side, gravity retention, no snap |
| Funnel throat | 12 mm ID channel | Funnel insert outlet tube | Sliding fit |
