# Front Bezel -- Parts Specification

The front bezel is a single PETG C-channel shell (160 x 72 x 8 mm) that caps the tray's open front face. It is the only user-facing surface of the cartridge: the flat palm rest, the finger channels for the squeeze-release gesture, and the shadow-line seam where the bezel overlaps the tray. The bezel is the last structural part installed and the first removed during service.

---

## Coordinate System

- **Origin**: lower-left corner of the outer face (the user-facing side), at the bottom-left of the bezel when facing the front of the cartridge.
- **X axis**: width, 0..160 mm (left to right when facing the front, same direction as tray X).
- **Z axis**: height, 0..72 mm (bottom to top, same direction as tray Z).
- **Y axis**: depth, 0 = outer face (user side), positive toward cartridge interior. Y increases away from user.
- **Print orientation**: outer face (Y = 0) on build plate.
- **Installed orientation**: outer face points toward user (tray +Y direction).

**Frame transform**: `tray_X = bezel_X`, `tray_Y = 160 - bezel_Y`, `tray_Z = bezel_Z`. The bezel's Y axis is inverted relative to the tray: bezel Y = 0 (outer face) corresponds to tray Y = 160, and bezel Y = 8 (deepest return wall edge) corresponds to tray Y = 152.

---

## 1. Mechanism Narrative (Rubric A)

### What the user sees and touches

The front bezel is the entire visual and tactile interface of the cartridge. The user sees a smooth, slightly convex rectangular panel (160 mm wide x 72 mm tall) with a subtle ellipsoidal crown (1.5 mm apex at center, blending to flat at the perimeter edges). The panel surface is matte PETG with a slight sheen from build plate contact. All four perimeter edges have 2 mm fillets, giving the panel a finished, rounded feel.

On the left and right edges of the bezel, two open channels (25 mm deep x 30 mm tall) cut into the panel, creating recessed voids. These channels communicate "reach in here" through negative space alone -- there are no labels or icons. The edges where the user's fingers curl around the channel entries have 3 mm fillets for comfort. Inside each channel, the user can see and reach a flat paddle surface (the pull-tab, part of the linkage rod assembly, not part of the bezel itself). The paddles are 30 mm tall and sit approximately 12 mm behind the bezel's outer face.

A thin shadow-line seam runs around the bottom and sides of the bezel where it overlaps the tray walls by 1.5 mm (the step-lap rabbet joint). This is the only visible evidence that the bezel is a separate part from the tray. The seam is intentionally expressed as a 1.5 mm step, not hidden flush, producing a shadow line that reads as a design detail rather than a manufacturing artifact.

### What moves

**During the squeeze-release interaction:** The bezel is stationary. It is the reaction surface for the user's palm. The user's palm pushes against the bezel's outer face, and the reaction force transfers through the bezel's six snap tabs into the tray structure, through the tray to the guide posts and rear wall, holding the cartridge body rigid. The only moving parts during the squeeze are the pull-tab paddles and linkage rods (separate from the bezel), which translate 1.5 mm in the tray +Y direction when the user's fingers pull the paddles toward their palm.

**During bezel installation:** The bezel translates in the -Y bezel direction (pushed toward the cartridge, i.e., tray -Y direction). The bezel's six cantilevered snap tabs deflect as they pass the tray's and lid's front edges, then spring into six receiving pockets (five on the tray via Sub-I, one on the lid via the T1 pocket).

**During bezel removal:** The bezel translates in the +Y bezel direction (pulled away from the cartridge). The user flexes the bezel's side walls inward slightly to release the snap tabs from the side wall pockets, then pulls the bezel forward.

### What converts the motion

**Squeeze-release:** No motion conversion occurs within the bezel. The bezel is purely a stationary reaction surface. The user's finger force on the pull-tab paddles transmits through the linkage rods to the release plate. The bezel transmits the palm's reaction force into the tray via the six snap tab engagements.

**Installation:** The user's push force (bezel -Y) is converted to snap tab deflection by the ramp geometry on the bezel's tab barbs. The angled leading face of each barb (45-degree ramp, 1.0 mm run in the deflection axis) wedges the tab away from the tray wall as it slides past the tray's front edge. Once the barb clears the edge and reaches the pocket, the tab's cantilever spring force drives it into the pocket recess.

### What constrains the bezel (after installation)

| Degree of freedom | Constraint feature | Dimensions |
|---|---|---|
| -Y bezel (toward cartridge, tray -Y) | Six snap tab barbs bear against the rear walls of six pockets at tray Y = 152 (bezel Y = 8). Each barb has a perpendicular lock face that catches the pocket opening edge. | 6 barbs, each 1.5 mm engagement behind pocket edge |
| +Y bezel (away from cartridge, tray +Y) | Barb lock faces catch against pocket opening edges at tray Y = 155 (bezel Y = 5). Barbs cannot back out because the lock faces are perpendicular to Y. | 6 barbs, perpendicular retention faces |
| +/-X (lateral) | Left return wall inner face seats against tray left wall rabbet ledge at tray X = 1.5 (bezel X = 1.5). Right return wall inner face seats against tray right wall rabbet ledge at tray X = 158.5 (bezel X = 158.5). The 157 mm span between ledges matches the bezel's inner return wall spacing. | Return walls 1.5 mm thick, rabbet ledges at X = 1.5 and X = 158.5 |
| -Z (downward) | Bottom return wall inner face seats against tray floor rabbet ledge at tray Z = 1.5 (bezel Z = 1.5). Floor snap tab BF1 hooks downward into pocket F1. | Return wall 1.5 mm thick, rabbet ledge at Z = 1.5 |
| +Z (upward) | Bezel top edge butts against lid bottom face at tray Z = 72 (bezel Z = 72). Snap tab BT1 hooks upward into lid T1 pocket (lid Z = 0 to 2.5). | Lid contact at Z = 72, T1 pocket 2.5 mm deep |

### What provides the return force

There is no return force. The bezel is intended to stay installed. Removal requires the user to deliberately flex the side walls inward (releasing L1, L2, R1, R2 snap tabs from their pockets) while pulling the bezel forward. The cantilever spring force of all six snap tabs holds them in the pockets during normal use, including during the squeeze-release interaction.

### What is the user's physical interaction

**During cartridge removal (squeeze-release):**

1. **Grip:** The user wraps one hand around the front bezel. Their palm contacts the ellipsoidal crown surface centered at (X = 80, Z = 36), which is 1.5 mm proud of the flat perimeter. The crown shape distributes palm pressure across a broad contact area (approximately 100 x 50 mm central zone where the crown height exceeds 0.5 mm). The crown's curvature is gentle enough (1.5 mm over 72 mm half-width) to feel flat to the palm.
2. **Fingers enter channel:** The user's four fingers on one hand curl around one side edge (left or right), entering the 25 mm deep x 30 mm tall finger channel. The 3 mm fillets at the channel edges (at bezel X = 25 or X = 135, spanning Z = 21 to 51 on the outer face) provide a smooth radius for the fingers to curl around. The fingertips contact the pull-tab paddle face approximately 12 mm behind the outer face (paddle at tray Y = 148, outer face at tray Y = 160).
3. **Squeeze:** The user squeezes their fingers toward their palm. The palm reaction force holds the bezel (and cartridge) stationary. The fingers pull the paddle 1.5 mm toward the palm. The linkage rods transmit this to the release plate, which compresses all four collets.
4. **Tactile endpoint:** At approximately 1.3 mm of paddle travel, the collets bottom out internally. The user feels a sudden increase in resistance -- the mechanism has reached its hard stop. The force required is 20-60 N total (4 collets at 5-15 N each), well within the 150 N capability of a 5th-percentile female. The 3-9x margin means the squeeze feels firm but effortless.
5. **Slide out:** While maintaining the squeeze (holding the collets released), the user slides the cartridge forward along the dock T-rails. The tube stubs withdraw from the John Guest fittings. A 5-10 N spring detent on the dock rails provides a small resistance that confirms disengagement.

**During bezel installation:**

1. **Align:** The builder positions the bezel against the tray's front face, with the return walls oriented to wrap around the tray's front edges. The step-lap rabbet self-centers the bezel laterally (X) and vertically (Z) via the 1.5 mm rabbet ledges.
2. **Push:** The builder pushes the bezel firmly toward the cartridge (bezel -Y). Six snap tabs deflect and latch into six pockets in a single push.
3. **Confirm:** The builder pulls the bezel forward. It does not move. All six tabs are captured.

---

## 2. Constraint Chain Diagram (Rubric B)

```
[User palm on bezel outer face]
    -> [Bezel: stationary reaction surface]
    -> [6 snap tabs transfer reaction into tray body / lid]
         ^ BL1, BL2 hook into Sub-I pockets L1, L2 at tray (3.5..5, 152..155, 19.5..24.5/47.5..52.5)
         ^ BR1, BR2 hook into Sub-I pockets R1, R2 at tray (155..156.5, 152..155, 19.5..24.5/47.5..52.5)
         ^ BF1 hooks into Sub-I pocket F1 at tray (77.5..82.5, 152..155, 1.5..3)
         ^ BT1 hooks into lid T1 pocket at lid (77.5..82.5, 152..155, 0..2.5)
    -> [Tray body -> guide posts -> rear wall: rigid reaction path]
    -> [Fittings held rigid while collets are compressed]

[User fingers on pull-tab paddles]
    -> [Pull-tab paddles: translate +Y tray (1.5 mm)] -- NOT part of bezel
    -> [Linkage rods: rigid, translate +Y through Sub-G wall slots] -- NOT part of bezel
    -> [Release plate: translates +Y, compresses collets] -- NOT part of bezel

Bezel installation:
[User hand: pushes bezel -Y (bezel frame)] -> [Bezel translates toward tray]
    -> [Tab barb ramps: wedge tabs away from tray walls (45-deg, 1.0 mm deflection)]
    -> [Tabs spring into 6 pockets]
         ^ captured by: pocket rear walls at tray Y = 152 (bezel Y = 8)
         ^ retained by: barb lock faces perpendicular to Y

Bezel lateral/vertical registration:
    -> [Left return wall inner face X = 1.5] + [Right return wall inner face X = 158.5]
         ^ constrain +/-X
    -> [Bottom return wall inner face Z = 1.5]
         ^ constrains -Z
    -> [Lid bottom face at Z = 72] + [BT1 in T1 pocket]
         ^ constrains +Z
```

Every arrow names the force transmission mechanism. Every constraint names a geometric feature with dimensions.

---

## 3. Feature Specification

### 3a. Shell Body (C-Channel)

The base solid is a C-channel shell: a front panel spanning the full width and height, with three return walls (left, right, bottom) wrapping around the tray's front edges. The top is open (interfaces with the lid).

| Parameter | Value (bezel frame) | Tray frame equivalent | Source |
|-----------|--------------------|-----------------------|--------|
| Width (X) | 0 to 160 mm | X = 0 to 160 | Tray outer width, spatial 3a |
| Height (Z) | 0 to 72 mm | Z = 0 to 72 | Tray wall height, spatial 3a |
| Front panel thickness (Y) | 0 to 5 mm | Y = 155 to 160 | Spatial 3b |
| Return wall depth (Y) | 5 to 8 mm | Y = 152 to 155 | Spatial 3c; 3 mm return wall |
| Left return wall thickness (X) | 0 to 1.5 mm | X = 0 to 1.5 | Spatial 3c |
| Right return wall thickness (X) | 158.5 to 160 mm | X = 158.5 to 160 | Spatial 3c |
| Bottom return wall thickness (Z) | 0 to 1.5 mm | Z = 0 to 1.5 | Spatial 3c |
| Material | PETG | -- | Concept Sec. 5/7 |

The return walls are 1.5 mm thick and 3 mm deep (bezel Y = 5 to 8). They fill the 1.5 mm step-lap rabbet cut into the tray's front edges (Sub-I), making the bezel's outer surfaces flush with the tray's outer walls and floor.

**Shell interior:** The interior of the C-channel (the volume bounded by the front panel inner face at bezel Y = 5 and the return wall inner faces at X = 1.5, X = 158.5, Z = 1.5, extending to Y = 8) is open and hollow. This void interfaces with the tray's interior cavity when the bezel is installed.

### 3b. Palm Contour (Outer Face Crown)

The outer face (nominally at bezel Y = 0) has a subtle convex ellipsoidal crown. The crown provides a comfortable palm rest surface and communicates "push here" through its gentle curvature.

| Parameter | Value | Source |
|-----------|-------|--------|
| Crown apex position | (X = 80, Z = 36) on the Y = 0 plane | Spatial 3b; center of outer face |
| Crown apex height | 1.5 mm proud of the Y = 0 plane (toward user, Y = -1.5) | Spatial 3b; midpoint of 1-2 mm concept range |
| Crown profile equation | Y_offset = -1.5 * (1 - ((X - 80)/80)^2) * (1 - ((Z - 36)/36)^2) | Spatial 3b |
| Perimeter edge offset | 0 mm (crown blends to flat at all four edges) | Spatial 3b |

The crown is modeled as an ellipsoidal surface. At the apex (X = 80, Z = 36), the surface protrudes 1.5 mm toward the user. At the edges (X = 0 or 160, Z = 0 or 72), the surface is flush with the Y = 0 plane. The curvature is gentle: 1.5 mm over 80 mm half-width (X direction) and 1.5 mm over 36 mm half-height (Z direction). The user's palm perceives this as a nearly flat surface with a slight warmth of curvature.

**Print orientation note:** The crown means the build plate contact surface (Y = 0 face) is not perfectly flat -- the apex protrudes 1.5 mm. For printing, the first layer contacts the build plate at the perimeter edges (where Y_offset = 0), and the crown is built up in subsequent layers. The PEI build plate contact produces a smooth finish on the perimeter ring, and the crown's gentle slope (maximum 1.5 mm rise over 36 mm run = 2.4 degrees from horizontal) prints cleanly without any overhang concerns.

### 3c. Finger Channels (2 channels)

Two open rectangular voids, one on each side of the bezel, that allow the user's fingers to reach the pull-tab paddles inside the cartridge. Each channel is a through-cut removing material from the front panel, the adjacent return wall, and opening into the tray interior.

#### Left Finger Channel

| Parameter | Value (bezel frame) | Tray frame equivalent | Source |
|-----------|--------------------|-----------------------|--------|
| X extent | 0 to 25 mm | X = 0 to 25 | Spatial 3d; 25 mm deep from left edge |
| Z extent | 21 to 51 mm | Z = 21 to 51 | Spatial 3d; 30 mm tall, centered on Z = 36 |
| Y extent | 0 to 8 mm | Y = 152 to 160 | Full bezel depth (through-cut) |
| Channel width (X) | 25 mm | -- | Concept Sec. 4 |
| Channel height (Z) | 30 mm | -- | Concept Sec. 4 |
| Side opening | X = 0 plane | -- | User enters from the left side |
| Back opening | Y = 8 plane | Y = 152 | Open into tray interior |

The channel removes all bezel material in the volume X = 0..25, Z = 21..51, Y = 0..8. This creates an opening visible from both the left side and the front face. The channel is open at the back, connecting to the tray interior so fingers can reach the pull-tab paddle (positioned at tray Y = 148, approximately 12 mm behind the outer face).

#### Right Finger Channel

Mirror of the left channel about X = 80.

| Parameter | Value (bezel frame) | Tray frame equivalent |
|-----------|--------------------|-----------------------|
| X extent | 135 to 160 mm | X = 135 to 160 |
| Z extent | 21 to 51 mm | Z = 21 to 51 |
| Y extent | 0 to 8 mm | Y = 152 to 160 |
| Side opening | X = 160 plane | User enters from the right side |
| Back opening | Y = 8 plane | Y = 152 |

### 3d. Snap Tabs (6 tabs)

Six cantilevered snap tabs on the bezel's inner surfaces (return walls and edges) engage six receiving pockets on the tray (Sub-I: L1, L2, R1, R2, F1) and the lid (T1). Each tab is a flexible cantilever beam with a barb at its tip.

#### Common Tab Dimensions

| Parameter | Value | Source |
|-----------|-------|--------|
| Tab barb protrusion | 1.5 mm into host wall (engagement depth into pocket) | Sub-I pocket depth 1.5 mm into wall body |
| Tab barb length (along deflection axis) | 1.5 mm | Matches pocket height 1.5 mm |
| Tab width (along host wall, tangent to deflection axis) | 4.5 mm | Fits inside 5.0 mm pocket width with 0.25 mm clearance per side |
| Cantilever beam length | 8.0 mm | Stress analysis below |
| Cantilever beam thickness | 1.0 mm | Stress analysis below |
| Barb ramp angle | 45 degrees | Leading face ramp for insertion deflection |
| Barb lock face | Perpendicular to Y (90 degrees) | Prevents pull-out in +Y bezel direction |

#### Tab Cantilever Deflection Analysis

Each tab must deflect 1.5 mm (the barb protrusion distance) during insertion, then spring back to seat in the pocket.

| Parameter | Value |
|-----------|-------|
| Material | PETG (tensile yield ~50 MPa, flexural modulus ~2100 MPa) |
| Effective cantilever length (L) | 8.0 mm |
| Beam thickness (t) | 1.0 mm |
| Beam width (w) | 4.5 mm |
| Required deflection (delta) | 1.5 mm |
| Max bending stress | sigma = (3 * E * t * delta) / (2 * L^2) = (3 * 2100 * 1.0 * 1.5) / (2 * 64) = 73.8 MPa |

At 73.8 MPa, this exceeds PETG yield (~50 MPa) by approximately 48%. This is the same stress regime as the lid tabs (which also operate at ~49 MPa with 1.0 mm deflection). The bezel tabs require 1.5 mm deflection rather than 1.0 mm, producing higher stress.

**Resolution:** Increase the cantilever length to 10 mm. This requires routing the cantilever beam along the return wall interior (running in the Y direction from the return wall tip at Y = 8 back toward Y = 5, then curving to run along the front panel inner face). With L = 10 mm:

| Parameter | Revised value |
|-----------|---------------|
| Effective cantilever length (L) | 10.0 mm |
| Beam thickness (t) | 1.0 mm |
| Required deflection (delta) | 1.5 mm |
| Max bending stress (revised) | sigma = (3 * 2100 * 1.0 * 1.5) / (2 * 100) = 47.3 MPa |

At 47.3 MPa vs ~50 MPa yield, this is within the PETG yield limit. Acceptable given the infrequent deflection cycles (bezel installed/removed rarely) and PETG's slight ductility.

The 1.0 mm beam thickness is 2.5 perimeters at 0.4 mm nozzle width -- printable but should be verified with a test print.

#### Tab Positions

| Tab ID | Location | Center (X, Y, Z) bezel frame | Center (X, Y, Z) tray frame | Deflection direction | Pocket |
|--------|----------|------------------------------|-----------------------------|----|---|
| BL1 | Left return wall, lower | (1.5, 6.5, 22.0) | (1.5, 153.5, 22.0) | +X during install, springs -X into pocket | Sub-I L1 |
| BL2 | Left return wall, upper | (1.5, 6.5, 50.0) | (1.5, 153.5, 50.0) | +X during install, springs -X into pocket | Sub-I L2 |
| BR1 | Right return wall, lower | (158.5, 6.5, 22.0) | (158.5, 153.5, 22.0) | -X during install, springs +X into pocket | Sub-I R1 |
| BR2 | Right return wall, upper | (158.5, 6.5, 50.0) | (158.5, 153.5, 50.0) | -X during install, springs +X into pocket | Sub-I R2 |
| BF1 | Bottom return wall, center | (80.0, 6.5, 1.5) | (80.0, 153.5, 1.5) | +Z during install, springs -Z into pocket | Sub-I F1 |
| BT1 | Top edge, center | (80.0, 6.5, 72.0) | (80.0, 153.5, 72.0) | -Z during install, springs +Z into pocket | Lid T1 |

#### Tab-to-Channel Interference Check

Tabs BL1/BL2 are at Z = 22.0 and Z = 50.0 on the left return wall (X = 0..1.5). The left finger channel removes material at X = 0..25, Z = 21..51. The tab cantilever roots are at X = 0..1.5, which is within the channel X range but at the extreme outer edge. The tabs are thin features (1.0 mm beam, 1.5 mm barb protrusion) along the X = 0..1.5 return wall zone. In the channel zone (Z = 21..51), the return wall is removed. The tab cantilevers must therefore be positioned outside the channel Z range or must be routed through the front panel body (Y = 0..5) rather than the return wall.

**Resolution for BL1, BL2, BR1, BR2:** These four tabs are routed as cantilever beams extending from the front panel's inner face (Y = 5 plane) at the left and right edges. The beam runs along the Y axis from Y = 5 toward Y = 8 (return wall depth), and the barb protrudes in the +/-X direction into the pocket. The cantilever root is embedded in the front panel body at the junction of the front panel and where the return wall would be. The beam extends 10 mm along a path from the panel body through the return wall zone. Since the return wall is 1.5 mm thick (X) x 3 mm deep (Y), and exists above and below the channel zone (Z = 0..21 and Z = 51..72), the tabs outside the channel are on intact return wall material. The tabs at Z = 22 and Z = 50 straddle the channel boundary -- their 4.5 mm width spans from Z = 19.75 to Z = 24.25 (BL1/BR1) and Z = 47.75 to Z = 52.25 (BL2/BR2), partially inside and partially outside the channel. The portion inside the channel (Z = 21..24.25 for BL1, Z = 47.75..51 for BL2) has no return wall to root into.

**Final resolution:** The tab cantilevers root into the front panel body (5 mm thick PETG) at the left and right edges. The beam runs from the front panel inner face (Y = 5) in the +Y direction (toward Y = 8), extending as a free cantilever that protrudes past the return wall zone. The barb at the beam tip hooks into the tray pocket. The tab does not depend on return wall material; it is integral to the front panel. The 5 mm front panel thickness provides adequate root material for a 1.0 mm thick cantilever.

#### BT1 Tab (Top Edge) Detail

BT1 is a cantilever extending upward from the bezel's top edge at X = 77.5..82.0 (4.5 mm wide, centered on X = 80), at Y = 5..8 (return wall depth zone). The beam extends upward in the +Z direction, past the bezel top edge at Z = 72, and the barb hooks in the +Z direction into the lid T1 pocket (lid Z = 0 to 2.5, or tray Z = 72 to 74.5).

| Parameter | Value | Source |
|-----------|-------|--------|
| Tab center X | 80.0 mm | Spatial 3g; centered on bezel |
| Tab X extent | 77.75 to 82.25 mm (4.5 mm wide) | 0.25 mm clearance per side in 5.0 mm pocket |
| Tab Y extent | 5 to 8 mm (3 mm deep) | Return wall depth zone |
| Tab Z root | 72 - 10 = 62 mm (root embedded in front panel body) | 10 mm effective cantilever length |
| Tab Z barb tip | 72 + 1.5 = 73.5 mm | Barb protrudes 1.5 mm above bezel top edge into lid pocket |
| Barb engagement in lid pocket | 1.5 mm above Z = 72, within lid pocket Z = 0..2.5 (tray Z = 72..74.5) | Lid spec Sec. 3c |
| Lid pocket rear wall | Y = 152 tray (bezel Y = 8) | Captures barb in -Y bezel direction |

During installation, BT1 deflects in the -Z direction (downward) as the bezel is pushed onto the tray. Once the barb clears the lid's front edge, the cantilever springs it upward (+Z) into the T1 pocket.

### 3e. Step-Lap Rabbet Interface

The bezel's three return walls (left, right, bottom) fill the rabbet cuts in the tray's front edges (Sub-I). This creates the shadow-line seam.

| Bezel surface | Bezel frame position | Tray frame position | Mates with |
|---------------|---------------------|---------------------|------------|
| Left return wall inner face | X = 1.5, Y = 5..8, Z = 0..72 | X = 1.5, Y = 152..155, Z = 0..72 | Sub-I left wall rabbet ledge at tray X = 1.5 |
| Right return wall inner face | X = 158.5, Y = 5..8, Z = 0..72 | X = 158.5, Y = 152..155, Z = 0..72 | Sub-I right wall rabbet ledge at tray X = 158.5 |
| Bottom return wall inner face | Z = 1.5, X = 0..160, Y = 5..8 | Z = 1.5, X = 0..160, Y = 152..155 | Sub-I floor rabbet ledge at tray Z = 1.5 |
| Left return wall outer face | X = 0, Y = 5..8, Z = 0..72 | X = 0, Y = 152..155 | Flush with tray left wall exterior |
| Right return wall outer face | X = 160, Y = 5..8, Z = 0..72 | X = 160, Y = 152..155 | Flush with tray right wall exterior |
| Bottom return wall outer face | Z = 0, X = 0..160, Y = 5..8 | Z = 0, X = 0..160, Y = 152..155 | Flush with tray floor bottom |

The shadow-line seam is the visible step at the junction of the bezel's 5 mm front panel and the tray's side walls/floor. The step is 5 mm deep (tray Y = 155 to 160) with the 1.5 mm overlap filling the rabbet. The visible step reads as a deliberate shadow line.

### 3f. Internal Fillets

Internal corners where the return walls meet the front panel inner face receive 1.0 mm fillets for printability and stress relief.

| Junction (bezel frame) | Location | Radius |
|------------------------|----------|--------|
| Left return wall to front panel | X = 1.5, Y = 5, Z = 0..72 | 1.0 mm |
| Right return wall to front panel | X = 158.5, Y = 5, Z = 0..72 | 1.0 mm |
| Bottom return wall to front panel | Z = 1.5, Y = 5, X = 0..160 | 1.0 mm |
| Left return wall to bottom return wall | X = 1.5, Z = 1.5, Y = 5..8 | 1.0 mm |
| Right return wall to bottom return wall | X = 158.5, Z = 1.5, Y = 5..8 | 1.0 mm |

### 3g. External Fillets

All external corners on the outer face have 2 mm fillets. Finger channel entries have 3 mm fillets.

| Fillet location (bezel frame) | Edge description | Radius |
|-------------------------------|------------------|--------|
| X = 0, Z = 0..21, Y = 0 | Left-bottom vertical edge, below channel | 2 mm |
| X = 0, Z = 51..72, Y = 0 | Left-bottom vertical edge, above channel | 2 mm |
| X = 160, Z = 0..21, Y = 0 | Right-bottom vertical edge, below channel | 2 mm |
| X = 160, Z = 51..72, Y = 0 | Right-bottom vertical edge, above channel | 2 mm |
| X = 0..160, Z = 0, Y = 0 | Bottom horizontal edge | 2 mm |
| X = 0..160, Z = 72, Y = 0 | Top horizontal edge | 2 mm |
| X = 25, Z = 21..51, Y = 0 | Left channel, inner vertical edge at outer face | 3 mm |
| Z = 21, X = 0..25, Y = 0 | Left channel, bottom horizontal edge at outer face | 3 mm |
| Z = 51, X = 0..25, Y = 0 | Left channel, top horizontal edge at outer face | 3 mm |
| X = 135, Z = 21..51, Y = 0 | Right channel, inner vertical edge at outer face | 3 mm |
| Z = 21, X = 135..160, Y = 0 | Right channel, bottom horizontal edge at outer face | 3 mm |
| Z = 51, X = 135..160, Y = 0 | Right channel, top horizontal edge at outer face | 3 mm |

The 2 mm fillets are interrupted at the finger channel zones where the channel openings cut through the corner edges.

---

## 4. Direction Consistency Check (Rubric C)

| # | Claim | Direction | Axis (bezel frame) | Axis (tray frame) | Verified? | Notes |
|---|-------|-----------|--------------------|--------------------|-----------|-------|
| 1 | "Bezel is pushed toward cartridge during installation" | -Y bezel, toward interior | -Y bezel = tray -Y | tray -Y | Yes | User pushes from front, bezel moves toward dock |
| 2 | "Left tabs deflect outward (+X) during install" | +X (away from tray center) | +X bezel = +X tray | +X | Yes | Tab barb contacts tray left wall edge, ramp pushes tab in +X |
| 3 | "Left tabs spring inward (-X) into pocket" | -X (toward tray center) | -X bezel = -X tray | -X | Yes | Cantilever restores tab, barb enters pocket in -X direction |
| 4 | "Right tabs deflect outward (-X) during install" | -X (away from tray center) | -X bezel = -X tray | -X | Yes | Mirror of left |
| 5 | "Right tabs spring inward (+X) into pocket" | +X (toward tray center) | +X bezel = +X tray | +X | Yes | Mirror of left |
| 6 | "BF1 deflects upward (+Z) during install" | +Z | +Z bezel = +Z tray | +Z | Yes | Floor tab pushed up by tray floor front edge |
| 7 | "BF1 springs downward (-Z) into pocket" | -Z | -Z bezel = -Z tray | -Z | Yes | Cantilever restores tab into floor pocket |
| 8 | "BT1 deflects downward (-Z) during install" | -Z | -Z bezel = -Z tray | -Z | Yes | Top tab pushed down by lid front edge |
| 9 | "BT1 springs upward (+Z) into lid pocket" | +Z | +Z bezel = +Z tray | +Z | Yes | Cantilever restores tab upward into lid T1 pocket |
| 10 | "Palm pushes bezel away during squeeze" | Bezel reaction is stationary | N/A | N/A | Yes | Bezel is rigid, not translating; palm force path goes through snap tabs into tray |
| 11 | "User fingers pull paddles toward palm" | +Y tray (toward user/front) | -Y bezel (but paddles are not bezel parts) | +Y tray | Yes | Paddles are linkage rod parts, move in tray +Y direction |
| 12 | "Release plate moves toward fittings" | +Y tray (toward front/user) | N/A (plate is internal) | +Y tray | Yes | Per release plate spec: plate translates +Y tray when squeezed |
| 13 | "Bezel outer face at tray Y = 160" | Bezel Y = 0 = tray 160 | Verified via transform | tray Y = 160 | Yes | 160 - 0 = 160 |
| 14 | "Return wall inner edge at tray Y = 152" | Bezel Y = 8 = tray 152 | Verified via transform | tray Y = 152 | Yes | 160 - 8 = 152 |

No contradictions found. All directional claims are consistent with the coordinate systems.

---

## 5. Interface Dimensional Consistency (Rubric D)

| Interface | Part A dimension | Part B dimension | Clearance | Source |
|-----------|-----------------|------------------|-----------|--------|
| Left return wall inner face (X = 1.5) to Sub-I left rabbet ledge (tray X = 1.5) | 1.5 mm wall thickness | 1.5 mm rabbet depth | 0.0 mm nominal (sliding fit during install, seated contact after) | Spatial 3c; Sub-I left rabbet |
| Right return wall inner face (X = 158.5) to Sub-I right rabbet ledge (tray X = 158.5) | 1.5 mm wall thickness | 1.5 mm rabbet depth | 0.0 mm nominal | Mirror of left |
| Bottom return wall inner face (Z = 1.5) to Sub-I floor rabbet ledge (tray Z = 1.5) | 1.5 mm wall thickness | 1.5 mm rabbet depth | 0.0 mm nominal | Spatial 3c; Sub-I floor rabbet |
| Bezel inner width (X = 1.5 to 158.5 = 157 mm) to tray rabbet span (X = 1.5 to 158.5 = 157 mm) | 157 mm | 157 mm | 0.2 mm per side built into bezel (bezel inner width printed at 157.4 mm to provide 0.2 mm clearance per side) | Sub-I narrative; requirements.md 0.2 mm sliding fit |
| BL1 tab width 4.5 mm to L1 pocket width 5.0 mm | 4.5 mm | 5.0 mm | 0.25 mm per side | Spatial 3f; Sub-I L1 |
| BL1 tab barb depth 1.5 mm to L1 pocket depth into wall 1.5 mm | 1.5 mm | 1.5 mm | 0.0 mm nominal (barb fills pocket depth) | Sub-I L1 |
| BL1 tab Y range to L1 pocket Y range 152..155 (3 mm) | Tab at bezel Y = 5..8 = tray Y = 152..155 | Pocket Y = 152..155 | Aligned (3 mm range matches) | Spatial 3f; Sub-I |
| BT1 tab width 4.5 mm to T1 pocket width 5.0 mm | 4.5 mm | 5.0 mm | 0.25 mm per side | Lid spec Sec. 3c |
| BT1 tab barb height 1.5 mm to T1 pocket height 2.5 mm | 1.5 mm barb extends into 2.5 mm pocket | 2.5 mm | 1.0 mm clearance above barb tip | Lid spec Sec. 3c |
| BT1 tab Y range to T1 pocket Y range 152..155 | Tab at bezel Y = 5..8 = tray Y = 152..155 | Pocket Y = 152..155 | Aligned | Lid spec Sec. 3c |

**Note on zero-clearance rabbet interfaces:** The return wall to rabbet ledge interfaces are 0.0 mm nominal. In practice, FDM tolerances produce a small gap. The bezel's inner width is specified at 157 mm nominal with 0.2 mm clearance per side (built into the bezel's return wall inner face positions). The floor return wall similarly has 0.2 mm clearance. These clearances are implemented by making the bezel's return wall inner faces at X = 1.7 (rather than 1.5) and X = 158.3 (rather than 158.5), and Z = 1.7 (rather than 1.5). This is a CadQuery-level adjustment, not a change to the nominal geometry. The nominal positions stated throughout this document (X = 1.5, X = 158.5, Z = 1.5) represent the tray's ledge positions; the bezel's mating faces are offset by 0.2 mm.

---

## 6. Assembly Feasibility (Rubric E)

### Assembly Sequence

The bezel is Step 10 in the cartridge assembly (concept Section 12), the last structural part installed.

1. **Prerequisites complete:** Tray fully loaded (pumps, tubes, fittings, release plate, linkage rods threaded through Sub-G slots). Lid snapped onto tray (Step 9). Linkage rod exterior ends with pull-tab paddles positioned near the tray front face.
2. **Hook linkage rods to paddles:** If the paddles are separate from the rods (printed hooks), the builder connects the rod exterior ends to the paddles before installing the bezel. The paddles sit loosely in the intended channel zone positions.
3. **Align bezel:** Builder holds the bezel with its open back facing the tray front face. The return walls are oriented to wrap around the tray/lid front edges. The rabbet ledges self-center the bezel in X and Z.
4. **Push bezel onto tray:** Builder pushes firmly in the -Y bezel direction. All six snap tabs deflect and latch into pockets in a single push. The pull-tab paddles are now captured inside the finger channels (the bezel's C-channel shell prevents the paddles from withdrawing).
5. **Verify:** Builder pulls the bezel in the +Y direction. It does not move. All six tabs are engaged.

### Assembly Check

| Step | Check | Result |
|------|-------|--------|
| Align bezel | Can the bezel physically slide over the tray front edges? | Yes. The C-channel opening (157 mm inner width) slides over the tray front face (155 mm inner width between 5 mm walls, with 1.5 mm rabbet step reducing the front edge to 3.5 mm per wall). The 0.2 mm clearance per side allows smooth sliding. |
| Push bezel | Can the builder's hand reach the full front face to push evenly? | Yes. The 160 x 72 mm face is smaller than a palm span. |
| Paddles captured | After bezel installation, are the pull-tab paddles retained? | Yes. The paddles sit inside the finger channels. The channel back is open to the tray interior, but the paddles are connected to the linkage rods which pass through the Sub-G wall slots. The bezel prevents the paddles from moving in the +Y bezel direction (away from cartridge) past the bezel front panel. |
| Trapped parts | Are any parts trapped by the bezel that need service access? | No. The bezel is the first part removed during service. Once removed, the lid can be popped off, giving access to all internals. The linkage rod hook connections are accessible through the open finger channel zones after bezel removal. |

### Disassembly Sequence

1. Flex bezel side walls inward slightly (compresses BL1/BL2 and BR1/BR2 tabs out of their pockets).
2. Pull bezel forward (+Y bezel direction). BF1 and BT1 release as the bezel lifts away.
3. The pull-tab paddles are now exposed. Unhook from linkage rod ends if service is needed.

No tools required. Deliberate flex force is needed to compress all four side tabs simultaneously. The bezel cannot accidentally pop off during the squeeze-release interaction because the squeeze force is directed along the Y axis (perpendicular to the tab deflection axis) and does not produce the inward-flex motion needed to release the tabs.

---

## 7. Part Count (Rubric F)

| Pair | Permanently joined? | Move relative to each other? | Same material, printable as one? | Assessment |
|------|---------------------|------------------------------|----------------------------------|------------|
| Bezel + tray | No (snap-fit, removable) | Yes (bezel installs/removes) | Yes (PETG) | Correct: must be separate. Bezel is the first part removed for service; separate printing allows cosmetic reprints. |
| Bezel + lid | No (butt joint at top edge) | Yes (both install/remove independently) | Yes (PETG) | Correct: must be separate. Lid installs before bezel and is removed after bezel. |
| Bezel + pull-tab paddles | No (not connected) | Yes (paddles translate 1.5 mm during squeeze) | Yes (PETG) | Correct: must be separate. Paddles move; bezel is stationary. |
| Bezel shell + snap tabs | Yes (integral, printed as one) | No | Yes (PETG) | Correct: one printed part. Tabs are cantilevers integral to the shell body. |
| Bezel shell + palm contour | Yes (integral, outer face shape) | No | Yes (PETG) | Correct: one printed part. The crown is a surface feature of the shell. |

**Part count: 1 printed part.** No fasteners. No hardware. The bezel is a single monolithic PETG print with integral snap tabs, return walls, finger channel voids, and palm contour surface.

---

## 8. FDM Printability (Rubric G)

### Step 1 -- Print Orientation

**Intended orientation:** Outer face (Y = 0, the palm contour surface) on the build plate, with the bezel Y axis pointing upward (away from the build plate). Layers stack in the Y direction.

**Rationale:** The outer face is the only user-visible surface and benefits from the smooth PEI build plate finish. This orientation places the cosmetic surface on the build plate for best quality.

**Constraint:** The palm contour crown (1.5 mm apex) means the build plate contact is not perfectly flat. The perimeter edges of the outer face (where the crown height is 0) contact the build plate, and the crown protrudes 1.5 mm above the flat plane. The first layer prints on the perimeter ring; subsequent layers build up the crown. The crown's maximum slope is 2.4 degrees from horizontal (1.5 mm / 36 mm), which is negligible for layer stacking.

**Alternative considered:** Printing upright (Z axis vertical, bezel standing on its bottom edge). This eliminates finger channel overhang issues but places visible layer lines on the palm surface. Rejected because cosmetic surface quality is paramount (vision.md: "user experience is paramount").

### Step 2 -- Overhang Audit

In the stated print orientation (outer face down, Y axis up), layers are XZ planes stacked in Y:

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|---|---|---|
| Outer face (Y = 0 plane) | 0 degrees (on build plate) | OK | Build plate contact surface |
| Front panel inner face (Y = 5 plane) | 0 degrees (horizontal, parallel to build plate, at top of 5 mm panel section) | OK | Flat horizontal surface, printed as top layer of panel zone |
| Left return wall inner face (X = 1.5 plane) | 90 degrees (vertical) | OK | Vertical wall, no overhang |
| Right return wall inner face (X = 158.5 plane) | 90 degrees (vertical) | OK | Vertical wall |
| Bottom return wall inner face (Z = 1.5 plane) | 90 degrees in print frame (vertical, since Z is horizontal in print) | OK | Printed as vertical wall |
| Return wall top edges (Y = 8 plane) | 0 degrees (horizontal, topmost layer) | OK | Flat top surface |
| Finger channel ceiling (Z = 51 plane, spanning X = 0..25, Y = 0..8) | This is a horizontal surface in the print frame, but it spans 8 mm in the Y (print Z) direction. The channel ceiling is the surface at Z = 51 that bridges across the channel void from Y = 0 to Y = 8. In print orientation, Z is horizontal, so this surface is vertical. | OK | The channel "ceiling" (Z = 51 face) is a vertical wall in print orientation. No overhang. |
| Finger channel inner wall (X = 25 plane, Z = 21..51, Y = 0..8) | 90 degrees (vertical in print frame, since X is horizontal) | OK | Vertical wall |
| Snap tab cantilevers | Tab beams are 1.0 mm thick features extending 10 mm. In print orientation, they build up in the Y (print Z) direction. The barb overhang (45-degree ramp + perpendicular lock face) requires intentional support. | Needs resolution | See below |
| Palm contour crown surface | Maximum 2.4 degrees from build plate plane | OK | Negligible slope, prints as gradual layer offsets |
| 2 mm external fillets on outer face edges | Fillet radius 2 mm, spanning from build plate (Y = 0) upward | OK | Fillets are convex features; the outer edges curve away from the build plate at 90 degrees initially |
| 3 mm finger channel entry fillets | Similar convex curvature | OK | Convex, no overhang |

**Snap tab barb overhang resolution:** Each tab barb has a perpendicular lock face (90-degree overhang from the barb tip). In the print orientation, the barbs are small features (1.5 mm protrusion, 1.5 mm tall) at the Y = 8 end of the bezel (topmost layers in print). The lock face creates a 90-degree overhang over a 1.5 mm span. Resolution: add a 45-degree chamfer on the underside of each barb lock face, reducing the unsupported overhang to 0 degrees. The chamfer removes 1.5 mm of the lock face height at 45 degrees, leaving the perpendicular portion intact above the chamfer. The chamfer does not affect tab retention because the barb still has a perpendicular face above the chamfer that catches behind the pocket edge. The effective retention depth is reduced from 1.5 mm to approximately 0.75 mm, which is sufficient for the low retention forces involved (the bezel is enclosed in the dock during normal operation and only needs to resist handling forces).

### Step 3 -- Wall Thickness Check

| Feature | Thickness | Minimum required | Pass? |
|---------|-----------|-----------------|-------|
| Front panel | 5.0 mm | 1.2 mm (structural) | Yes |
| Left return wall | 1.5 mm | 0.8 mm (standard) | Yes. Not load-bearing; serves as rabbet fill and snap tab root. |
| Right return wall | 1.5 mm | 0.8 mm | Yes |
| Bottom return wall | 1.5 mm | 0.8 mm | Yes |
| Snap tab cantilever beam | 1.0 mm | 0.8 mm (standard) | Yes. 2.5 perimeters at 0.4 mm nozzle. |
| Snap tab barb | 1.5 mm protrusion | 0.8 mm | Yes |
| Front panel at channel zone (X = 0..25, Z = 21..51) | No material (channel is through-cut) | N/A | N/A -- channel removes all material in this zone |
| Front panel between channels (X = 25..135, Z = 21..51) | 5.0 mm | 1.2 mm | Yes |

### Step 4 -- Bridge Span Check

| Span location | Direction | Length | Under 15 mm? | Resolution |
|---------------|-----------|--------|---------------|------------|
| Finger channel ceiling (Z = 51 face across Y = 0..8) | In print orientation, this is a vertical surface, not a bridge | 8 mm | N/A | Not a bridge in this print orientation |
| Front panel inner face (Y = 5) spanning X = 0..160 | In print orientation (Y up), this is the top surface of the front panel section. Each layer is a full 160 mm XZ perimeter. The inner face is the last layer printed before the return walls begin. | N/A | N/A | Not a bridge; solid infill supports it |
| Return wall top surfaces (Y = 8, spanning short runs) | Top surface of 1.5 mm thin walls, 3 mm tall in print direction | N/A | N/A | Not a bridge; each return wall is a solid thin wall |

No unsupported bridge spans exceed 15 mm. All horizontal surfaces in print orientation are either on the build plate or are supported by infill below.

### Step 5 -- Layer Strength Check

| Feature | Load direction | Layer orientation (print Y up) | Layers parallel to load? | Notes |
|---------|---------------|-------------------------------|-------------------------|-------|
| Snap tab cantilevers (BL1/BL2/BR1/BR2) | Deflect in +/-X during install | Layers stack in Y (perpendicular to X deflection) | No -- layers are perpendicular to the deflection direction | This is a concern. The cantilever beams flex in X, and the layers stack in Y. Delamination between layers could cause tab failure during deflection. |
| Snap tab BF1 | Deflects in +Z during install | Layers stack in Y (perpendicular to Z deflection) | No -- same concern | |
| Snap tab BT1 | Deflects in -Z during install | Layers stack in Y (perpendicular to Z deflection) | No -- same concern | |
| Front panel under palm load | Compression in Y (palm pushes) | Layers stack in Y (compression along layer stack) | Yes -- compression along layer stack is the strongest orientation | No concern |

**Layer strength resolution for snap tabs:** In this print orientation (Y up), all six snap tabs flex perpendicular to the layer lines. This is the weakest orientation for flexing features. However, the tabs flex infrequently (only during bezel installation/removal, not during normal squeeze-release operation), and the deflection is small (1.5 mm over 10 mm length). The 1.0 mm beam thickness at 0.4 mm nozzle means each layer is two perimeter walls (0.8 mm) with 0.2 mm gap or slight overlap. PETG has good interlayer adhesion compared to PLA.

**Mitigation:** Print at 0.15 mm layer height for the snap tab zones to maximize interlayer bond area. Alternatively, if tabs fail in testing, print the bezel upright (bottom edge on build plate, Z vertical) which aligns layers parallel to the X-deflection axis for the side tabs. This trades cosmetic surface finish for tab strength. Decision deferred to prototyping.

**Priority tradeoff:** The outer face cosmetic finish (build plate contact) is prioritized over snap tab layer orientation. The tabs are low-cycle features and PETG's interlayer adhesion is expected to be adequate. If testing reveals tab breakage, the print orientation will be changed to upright and the outer face will receive post-processing (light sanding).

---

## 9. Design Gaps

1. **Snap tab layer orientation vs. cosmetic surface.** The preferred print orientation (outer face on build plate) places layer lines perpendicular to the snap tab deflection direction. PETG interlayer adhesion is expected to be adequate for the low cycle count, but this must be verified with a test print of a representative tab geometry. If tabs delaminate during installation, the print orientation must change to upright (sacrificing outer face finish) or tab geometry must be redesigned (thicker beams, shorter deflection).

2. **Palm crown first-layer contact.** The 1.5 mm ellipsoidal crown means the first layer does not fully contact the build plate across the entire outer face. The perimeter edges contact the plate; the center floats 1.5 mm above. The first few layers print as rings that gradually fill inward as the crown builds up. If this causes adhesion issues or first-layer quality problems, the crown may need to be reduced to 1.0 mm or the print orientation changed.

3. **Return wall clearance for bezel installation.** The 0.2 mm per side clearance between bezel return wall inner faces and tray rabbet ledges is at the minimum for sliding fits (per requirements.md). If FDM tolerance on the bezel or tray produces a tighter fit, installation may require excessive force. Verify with test print of the rabbet joint.

---

## 10. Summary

The front bezel is a single PETG print: a C-channel shell with a 5 mm front panel, 1.5 mm return walls, two 25 x 30 mm finger channels, six integral snap tabs, a 1.5 mm ellipsoidal palm contour crown, 2 mm external fillets, 3 mm finger channel entry fillets, and 1 mm internal fillets. It mates to the tray (Sub-I rabbet and 5 pockets) and lid (T1 pocket) with zero fasteners. Total part count for the bezel: 1 printed part, 0 hardware.
