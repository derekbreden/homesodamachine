# Spatial Resolution: Front Bezel

## 1. System-Level Placement

```
Mechanism: Front Bezel
Parent: Tray assembly (mounts onto the Y = 155 front face of the tray, also interfaces with lid front edge)
Position: front face of the cartridge, protruding forward of the tray's Y = 155 plane
Orientation: bezel XZ plane (outer face) is parallel to the tray XZ plane; bezel is level (no rotation)
```

The front bezel is the only user-facing surface of the cartridge. It covers the tray's open front face (Y = 155 in tray frame), overlaps the tray's side walls and floor by 1.5 mm in a step-lap rabbet joint, and contains finger channels on the left and right sides for the squeeze-release interaction. The bezel is the last part installed and the first removed during service.

---

## 2. Part Reference Frame

```
Part: Front Bezel
  Origin: lower-left corner of the outer face (user-facing side)
  X: width, 0..160 mm (left to right when facing the front, same direction as tray X)
  Z: height, 0..72 mm (bottom to top, same direction as tray Z)
  Y: depth, 0 = outer face (user side), positive toward cartridge interior
  Print orientation: outer face on build plate (Y = 0 face down) for best surface finish
  Installed orientation: outer face points in the +Y tray direction (toward user)
```

The bezel's local frame has the outer face (palm rest surface) on the XZ plane at Y = 0. Y increases toward the cartridge interior. X and Z directions match the tray's X and Z.

---

## 3. Derived Geometry

### 3a. Bezel Outer Envelope

The bezel is a C-channel shell (open at the back and top) that caps the tray's front face. It consists of a front panel spanning the full width and height, with return walls along the left side, right side, and bottom that wrap around the tray's front edges. The top is open (butts against the lid front edge), with a small snap tab for lid retention.

| Parameter | Value (bezel frame) | Tray frame equivalent | Source |
|-----------|--------------------|-----------------------|--------|
| Width (X) | 0 to 160 mm | X = 0 to 160 | Matches tray outer width (Sub-A) |
| Height (Z) | 0 to 72 mm | Z = 0 to 72 | Matches tray wall height (Sub-A) |
| Total depth (Y) at front panel | 0 to 5 mm | Y = 155 to 160 | 5 mm panel thickness |
| Total depth (Y) at return walls | 0 to 8 mm | Y = 152 to 160 | 5 mm panel + 3 mm return wall |
| Outer face plane | Y = 0 | tray Y = 160 | User-facing surface |
| Front panel inner face | Y = 5 | tray Y = 155 | Aligns with tray front face |
| Return wall inner edge | Y = 8 | tray Y = 152 | Provides snap tab engagement depth |

The bezel protrudes 5 mm forward of the tray's front face (tray Y = 155 to Y = 160). Total cartridge depth with bezel installed: 160 mm.

### 3b. Front Panel

The front panel is the main structural and cosmetic surface. It spans the full bezel width and height.

| Parameter | Value (bezel frame) | Notes |
|-----------|---------------------|-------|
| X extent | 0 to 160 mm | Full width |
| Z extent | 0 to 72 mm | Full height |
| Y extent | 0 to 5 mm | 5 mm nominal thickness |
| Outer face | Y = 0 plane | Palm rest surface, printed against build plate for best finish |
| Inner face | Y = 5 plane | Interior of bezel, faces tray cavity |

**Palm contour:** The outer face has a subtle convex crown of 1-2 mm. The crown is centered on the face and its apex is at approximately X = 80, Z = 36 (the center of the outer face). The curvature is gentle enough to be treated as a smooth loft or spline surface rather than a compound curve. In the CadQuery model, this is achieved by offsetting the center of the outer face by 1.5 mm (midpoint of 1-2 mm range) in the -Y direction (toward the user), blending to the flat perimeter edges.

Palm contour profile (XZ cross-sections at selected positions, measured as Y offset from the Y = 0 plane, negative = toward user):

| Position | Y offset at center (mm) | Y offset at edge (mm) |
|----------|------------------------|-----------------------|
| X = 0 (left edge) | 0 | 0 |
| X = 40 | -1.2 | 0 |
| X = 80 (center) | -1.5 | 0 |
| X = 120 | -1.2 | 0 |
| X = 160 (right edge) | 0 | 0 |

The same profile applies in Z:

| Position | Y offset at center (mm) | Y offset at edge (mm) |
|----------|------------------------|-----------------------|
| Z = 0 (bottom edge) | 0 | 0 |
| Z = 18 | -1.2 | 0 |
| Z = 36 (center) | -1.5 | 0 |
| Z = 54 | -1.2 | 0 |
| Z = 72 (top edge) | 0 | 0 |

The maximum crown apex (1.5 mm proud of the flat plane) occurs at (X = 80, Z = 36) on the outer face. The crown surface is approximately ellipsoidal: Y_offset = -1.5 * (1 - ((X - 80)/80)^2) * (1 - ((Z - 36)/36)^2).

### 3c. Return Walls (Side and Bottom)

The bezel has three return walls that wrap around the tray's front edges, fitting into the Sub-I rabbet.

#### Left Return Wall

| Parameter | Value (bezel frame) | Tray frame equivalent |
|-----------|--------------------|-----------------------|
| X extent (thickness) | 0 to 1.5 mm | tray X = 0 to 1.5 |
| Z extent | 0 to 72 mm | tray Z = 0 to 72 |
| Y extent | 5 to 8 mm | tray Y = 152 to 155 |
| Inner face (toward tray wall) | X = 1.5 plane | tray X = 1.5 (contacts left wall rabbet ledge) |
| Outer face | X = 0 plane | tray X = 0 (flush with tray left wall exterior) |

In the rabbet zone (bezel Y = 6.5 to 8, tray Y = 152 to 153.5 is behind the rabbet, Y = 153.5 to 155 is the rabbet zone), the return wall sits in the 1.5 mm rabbet cut. At bezel Y = 6.5..8 (tray Y = 152..153.5), the wall extends past the rabbet into the tray interior, positioning the snap tabs.

#### Right Return Wall

| Parameter | Value (bezel frame) | Tray frame equivalent |
|-----------|--------------------|-----------------------|
| X extent (thickness) | 158.5 to 160 mm | tray X = 158.5 to 160 |
| Z extent | 0 to 72 mm | tray Z = 0 to 72 |
| Y extent | 5 to 8 mm | tray Y = 152 to 155 |
| Inner face (toward tray wall) | X = 158.5 plane | tray X = 158.5 (contacts right wall rabbet ledge) |
| Outer face | X = 160 plane | tray X = 160 (flush with tray right wall exterior) |

Mirror of left return wall.

#### Bottom Return Wall

| Parameter | Value (bezel frame) | Tray frame equivalent |
|-----------|--------------------|-----------------------|
| X extent | 0 to 160 mm | tray X = 0 to 160 |
| Z extent (thickness) | 0 to 1.5 mm | tray Z = 0 to 1.5 |
| Y extent | 5 to 8 mm | tray Y = 152 to 155 |
| Inner face (toward tray floor) | Z = 1.5 plane | tray Z = 1.5 (contacts floor rabbet ledge) |
| Outer face | Z = 0 plane | tray Z = 0 (flush with tray floor bottom) |

The bottom return wall fills the floor rabbet and extends to Y = 152 (tray frame) for the floor snap tab.

#### No Top Return Wall

The tray is open-top; the lid sits on the tray walls at Z = 72. The bezel's top edge butts against the lid's front edge. A snap tab at the top center engages a pocket in the lid (not the tray). See Section 3g.

### 3d. Finger Channels

Two open vertical channels, one on each side of the bezel, allowing fingers to enter from the side edges and reach the pull-tab paddles. The channels are through-cuts removing material from the return walls, front panel edges, and opening into the tray interior.

#### Left Finger Channel

| Parameter | Value (bezel frame) | Tray frame equivalent | Source |
|-----------|--------------------|-----------------------|--------|
| X extent | 0 to 25 mm | tray X = 0 to 25 | 25 mm deep from left edge (concept Section 4) |
| Z extent | 21 to 51 mm | tray Z = 21 to 51 | 30 mm tall, centered on Z = 36 (tray midheight) |
| Y extent | 0 to 8 mm | tray Y = 152 to 160 | Full bezel depth (through-cut, open at front and back) |
| Opening face (X edge) | X = 0 plane | tray X = 0 | User enters from the left side |
| Opening face (back) | Y = 8 plane | tray Y = 152 | Open into tray interior |

The channel removes all bezel material in the volume X = 0..25, Z = 21..51, Y = 0..8. This creates:
- An opening in the left side of the front panel (X = 0..25, Z = 21..51, Y = 0..5)
- Complete removal of the left return wall in the channel zone (X = 0..1.5, Z = 21..51, Y = 5..8)
- An open slot visible from the left side edge and from the front face

The channel is open at the back (Y = 8, tray Y = 152), connecting to the tray interior through the tray's open front face. This allows fingers to reach beyond the bezel into the tray cavity to grip the pull-tab paddles.

#### Right Finger Channel

| Parameter | Value (bezel frame) | Tray frame equivalent |
|-----------|--------------------|-----------------------|
| X extent | 135 to 160 mm | tray X = 135 to 160 |
| Z extent | 21 to 51 mm | tray Z = 21 to 51 |
| Y extent | 0 to 8 mm | tray Y = 152 to 160 |
| Opening face (X edge) | X = 160 plane | tray X = 160 |
| Opening face (back) | Y = 8 plane | tray Y = 152 |

Mirror of left finger channel about X = 80.

#### Channel Edge Fillets

Where fingers curl around the channel edges (the front panel edges adjacent to the channel openings), 3 mm fillets are applied per the concept design language (Section 5). These fillets are on the edges where the channel walls meet the outer face:

| Fillet location (bezel frame) | Edge description | Radius |
|-------------------------------|------------------|--------|
| X = 25, Z = 21..51, Y = 0 | Left channel, inner X edge at outer face | 3 mm |
| Z = 21, X = 0..25, Y = 0 | Left channel, bottom Z edge at outer face | 3 mm |
| Z = 51, X = 0..25, Y = 0 | Left channel, top Z edge at outer face | 3 mm |
| X = 135, Z = 21..51, Y = 0 | Right channel, inner X edge at outer face | 3 mm |
| Z = 21, X = 135..160, Y = 0 | Right channel, bottom Z edge at outer face | 3 mm |
| Z = 51, X = 135..160, Y = 0 | Right channel, top Z edge at outer face | 3 mm |

### 3e. Pull-Tab Paddle Positions

The pull-tab paddles are flat surfaces inside the finger channels, connected to the linkage rods. They are the surfaces the user's fingers grip during the squeeze action. The paddles are separate from the bezel (they are attached to the linkage rods, which connect to the release plate).

The paddles sit inside the tray interior, accessible through the finger channels. Their position is determined by the linkage rod path from the Sub-G wall slots to the front of the cartridge.

**Linkage rod path (tray frame):**
- Rod exits release plate at: tray (52.5, 12.0, 36.0) for left rod; tray (107.5, 12.0, 36.0) for right rod
- Rod passes through Sub-G slot: left at tray X = 0..5, Y = 17..23, Z = 35..40; right at tray X = 155..160, Y = 17..23, Z = 35..40
- Rod runs along the exterior of the side wall from the slot toward the front
- Rod terminates at the pull-tab paddle near the front of the cartridge

**Pull-tab paddle positions:**

The paddles must be accessible through the finger channels. The channels open at the side edges of the bezel and into the tray interior. The paddles are at the front end of the linkage rods, positioned to be grippable by fingers entering the channels.

| Parameter | Left paddle | Right paddle | Frame |
|-----------|-------------|--------------|-------|
| X center | 2.5 mm | 157.5 mm | Tray frame: along exterior wall face |
| Z center | 36.0 mm | 36.0 mm | Tray frame: aligned with linkage rod Z |
| Z extent | 21 to 51 mm | 21 to 51 mm | Tray frame: 30 mm tall paddle |
| Y position (paddle face, at rest) | 148 mm | 148 mm | Tray frame: see derivation below |
| Paddle width (Y) | 15 mm | 15 mm | Matches channel Y opening |
| Paddle face plane | XZ plane facing +Y (toward user) | same | Finger contact surface |

**Paddle Y position derivation:** The linkage rods run from the Sub-G slots (Y center = 20 in tray frame) toward the front of the cartridge. The rods run along the exterior of the tray side walls. The rod length from slot to paddle determines the paddle Y position. The rods must be long enough to connect the release plate hooks (at the slot Y position) to the paddles. At rest, the paddle face is at approximately tray Y = 148. This places the paddle face 12 mm from the bezel outer face (tray Y = 160), giving a grip span of approximately 12 mm in Y.

**Grip span note:** The concept decision document specifies a 50 mm grip span from the outer face to the pull-tab surface. This referred to the anthropometric hand span during a squeeze grip, measuring from the palm center to the fingertip contact. In the detailed design, the physical Y-distance from the bezel outer face to the pull-tab paddle face is approximately 12 mm. The effective squeeze span experienced by the user is larger because the palm contacts the crown of the front panel (which is wider than the channel zone), and the fingers curl around the side edges and into the channels -- the hand wraps around the bezel rather than squeezing in a pure Y direction. The 1.5 mm plate travel and the force budget (20-60 N total, well within comfortable squeeze) remain valid regardless of the geometric grip span.

**Paddle-to-channel alignment (bezel frame):**

| Parameter | Left paddle | Right paddle |
|-----------|-------------|--------------|
| Within channel X range (0..25)? | X center = 2.5, paddle width negligible in X -- yes | X center = 157.5, within 135..160 -- yes |
| Within channel Z range (21..51)? | Z = 21..51 -- yes | Z = 21..51 -- yes |

The paddles are fully within the channel openings, accessible to fingers entering from the side.

### 3f. Snap Tab Positions

The bezel has six snap tabs that engage six receiving pockets on the tray (Sub-I) and lid. Each tab is a cantilevered hook on the bezel's inner surfaces (return walls and panel edges).

#### Tab positions (bezel frame)

| Tab ID | Location | Center (X, Y, Z) bezel frame | Center (X, Y, Z) tray frame | Mating pocket |
|--------|----------|------------------------------|-----------------------------|----|
| BL1 | Left return wall, lower | (1.5, 6.5, 22.0) | (1.5, 153.5, 22.0) | Sub-I pocket L1 |
| BL2 | Left return wall, upper | (1.5, 6.5, 50.0) | (1.5, 153.5, 50.0) | Sub-I pocket L2 |
| BR1 | Right return wall, lower | (158.5, 6.5, 22.0) | (158.5, 153.5, 22.0) | Sub-I pocket R1 |
| BR2 | Right return wall, upper | (158.5, 6.5, 50.0) | (158.5, 153.5, 50.0) | Sub-I pocket R2 |
| BF1 | Bottom return wall, center | (80.0, 6.5, 1.5) | (80.0, 153.5, 1.5) | Sub-I pocket F1 |
| BT1 | Top edge, center | (80.0, 6.5, 72.0) | (80.0, 153.5, 72.0) | Lid pocket T1 |

All tab centers are at bezel Y = 6.5 (midway through the return wall depth of Y = 5..8), which corresponds to tray Y = 153.5 (midway through the pocket Y range of 152..155).

#### Tab approach directions

| Tab ID | Deflection direction during installation | Springs into pocket direction |
|--------|------------------------------------------|-------------------------------|
| BL1, BL2 | +X (outward, away from tray center) | -X (inward, into tray wall pocket) |
| BR1, BR2 | -X (outward, away from tray center) | +X (inward, into tray wall pocket) |
| BF1 | +Z (upward, away from floor) | -Z (downward, into floor pocket) |
| BT1 | -Z (downward) | +Z (upward, into lid pocket) |

During bezel installation (pushed in the +Y bezel direction, which is -Y tray direction), the tab barbs contact the tray's front edges and deflect. Once past the edges, they spring into the pockets.

#### Tab interference check with finger channels

Snap tab pockets L1/R1 are at Z = 19.5..24.5 and L2/R2 are at Z = 47.5..52.5 (tray frame). The finger channels span Z = 21..51 (tray frame). The pockets L1/R1 overlap the channel zone at Z = 21..24.5 (3.5 mm overlap at the bottom of the channel) and L2/R2 overlap at Z = 47.5..51 (3.5 mm overlap at the top).

This is acceptable because:
- The pockets are in the tray wall (X = 3.5..5 for left, X = 155..156.5 for right)
- The channels are in the bezel at X = 0..25 (left) and X = 135..160 (right)
- The snap tabs are on the bezel return walls (X = 0..1.5 left, X = 158.5..160 right) -- they are at the extreme X edges, outside the main channel void but within the channel X range
- The tabs are thin features (1.5 mm protrusion) and do not obstruct finger access through the 25 mm deep channel

### 3g. Lid Interface at Top Edge

The bezel's top edge (Z = 72 in bezel frame, tray Z = 72) meets the lid's front edge (lid Y = 155, lid Z = 0..4).

| Parameter | Value (bezel frame) | Tray frame equivalent | Lid frame equivalent |
|-----------|--------------------|-----------------------|---------------------|
| Bezel top edge plane | Z = 72 | tray Z = 72 | lid Z = 0 |
| Bezel top edge Y extent | Y = 0 to 5 | tray Y = 155 to 160 | lid Y = 155 (front face of lid) |
| Contact zone | X = 0..160, Z = 72, Y = 0..5 | -- | -- |

The bezel's top edge butts against the lid's bottom face at the front edge. The bezel does not have a top return wall (the tray is open-top). The constraint at the top is provided by:

1. The lid bearing down on the tray walls at tray Z = 72
2. Snap tab BT1 engaging the lid's T1 pocket

**BT1 tab and lid T1 pocket interface:**

| Parameter | Value (bezel frame) | Tray frame | Lid frame |
|-----------|---------------------|------------|-----------|
| Tab center X | 80.0 | 80.0 | 80.0 |
| Tab center Y | 6.5 | 153.5 | 153.5 |
| Tab center Z | 72.0 (tab extends above) | 72.0 (extends above) | 0 (extends into lid) |
| Pocket cut volume (lid) | -- | X = 77.5..82.5, Y = 152..155, Z = 72..74.5 | X = 77.5..82.5, Y = 152..155, Z = 0..2.5 |
| Tab hooks upward | +Z in bezel frame | +Z in tray frame | +Z in lid frame (into pocket) |

The BT1 tab is a cantilever extending upward from the bezel's top edge at X = 77.5..82.5. It deflects downward (-Z) during installation and springs upward (+Z) into the lid pocket. The pocket is 5 mm wide (X), 3 mm deep (Y, from Y = 152 to 155), and 2.5 mm tall (Z, from lid Z = 0 to 2.5).

### 3h. Step-Lap Rabbet Interface

The bezel's return walls fill the rabbet cuts in the tray's front edges (Sub-I). The interface is a lap joint creating a shadow-line seam.

#### Interface positions (both sides)

| Bezel surface | Bezel frame position | Tray frame position | Mates with |
|---------------|---------------------|---------------------|------------|
| Left inner face | X = 1.5 plane, Y = 5..8, Z = 0..72 | X = 1.5, Y = 152..155, Z = 0..72 | Sub-I left wall rabbet ledge at tray X = 1.5 |
| Right inner face | X = 158.5 plane, Y = 5..8, Z = 0..72 | X = 158.5, Y = 152..155, Z = 0..72 | Sub-I right wall rabbet ledge at tray X = 158.5 |
| Bottom inner face | Z = 1.5 plane, X = 0..160, Y = 5..8 | Z = 1.5, X = 0..160, Y = 152..155 | Sub-I floor rabbet ledge at tray Z = 1.5 |
| Left outer face | X = 0 plane, Y = 5..8, Z = 0..72 | X = 0, Y = 152..155, Z = 0..72 | Flush with tray left wall exterior |
| Right outer face | X = 160 plane, Y = 5..8, Z = 0..72 | X = 160, Y = 152..155, Z = 0..72 | Flush with tray right wall exterior |
| Bottom outer face | Z = 0 plane, X = 0..160, Y = 5..8 | Z = 0, X = 0..160, Y = 152..155 | Flush with tray floor bottom |

The shadow-line seam is the visible line at the junction of the bezel's front panel and the tray's side walls / floor. The seam runs at:
- Left side: X = 0, Y = 5 (bezel frame) = tray Y = 155. The step between the bezel's front panel (protruding to tray Y = 160) and the tray wall (at tray X = 0, Y < 155) creates a 5 mm step with a 1.5 mm overlap shadow line.
- Right side: mirror at X = 160.
- Bottom: Z = 0, same step geometry.

### 3i. External Corner Fillets

Per the concept design language, all external corners on the front bezel have 2 mm fillets, except at the finger channel entries where 3 mm fillets are used (Section 3d).

| Fillet location (bezel frame) | Edges | Radius | Run length |
|-------------------------------|-------|--------|------------|
| Front panel corners (outer face edges) | X = 0, Z = 0..72, Y = 0 (left-bottom vertical) | 2 mm | 72 mm |
| | X = 160, Z = 0..72, Y = 0 (right-bottom vertical) | 2 mm | 72 mm |
| | X = 0..160, Z = 0, Y = 0 (bottom horizontal) | 2 mm | 160 mm |
| | X = 0..160, Z = 72, Y = 0 (top horizontal) | 2 mm | 160 mm |
| Finger channel entries | See Section 3d | 3 mm | Per channel edge |

Note: fillets on the external corners are interrupted at the finger channel zones (X = 0..25 and X = 135..160 at Z = 21..51) where the channel openings cut through the corner edges.

### 3j. Internal Corner Fillets

Internal corners where the return walls meet the front panel inner face have 1 mm fillets for printability and stress relief.

| Junction (bezel frame) | Location | Radius |
|------------------------|----------|--------|
| Left return wall to front panel | X = 1.5, Y = 5, Z = 0..72 | 1.0 mm |
| Right return wall to front panel | X = 158.5, Y = 5, Z = 0..72 | 1.0 mm |
| Bottom return wall to front panel | Z = 1.5, Y = 5, X = 0..160 | 1.0 mm |
| Left return wall to bottom return wall | X = 1.5, Z = 1.5, Y = 5..8 | 1.0 mm |
| Right return wall to bottom return wall | X = 158.5, Z = 1.5, Y = 5..8 | 1.0 mm |

---

## 4. Transform Summary

```
Bezel frame -> Tray frame:
  tray_X = bezel_X       (same direction, same origin)
  tray_Y = 160 - bezel_Y (bezel Y=0 is outer face at tray Y=160; Y inverts)
  tray_Z = bezel_Z       (same direction, same origin)

Tray frame -> Bezel frame:
  bezel_X = tray_X
  bezel_Y = 160 - tray_Y
  bezel_Z = tray_Z
```

### Verification Points

| Point description | Bezel frame (X, Y, Z) | Tray frame (X, Y, Z) | Check |
|-------------------|----------------------|----------------------|-------|
| Origin: lower-left of outer face | (0, 0, 0) | (0, 160, 0) | Outer face at tray Y=160, bottom-left corner |
| Center of outer face | (80, 0, 36) | (80, 160, 36) | Center of the palm rest surface |
| Left rabbet contact (inner face, mid-height) | (1.5, 8, 36) | (1.5, 152, 36) | Bezel inner face sits on rabbet ledge at tray X=1.5, Y=152 |
| Right rabbet contact | (158.5, 8, 36) | (158.5, 152, 36) | Mirror of left |
| Floor rabbet contact (center) | (80, 8, 1.5) | (80, 152, 1.5) | Bezel bottom inner face at tray Z=1.5 |
| Snap tab L1 center | (1.5, 6.5, 22) | (1.5, 153.5, 22) | Matches Sub-I pocket L1 center position |
| Snap tab BT1 center | (80, 6.5, 72) | (80, 153.5, 72) | Matches lid T1 pocket location |
| Left channel opening center | (12.5, 4, 36) | (12.5, 156, 36) | Center of left finger channel void |
| Palm crown apex | (80, -1.5, 36) | (80, 161.5, 36) | Crown protrudes 1.5 mm past Y=0 (toward user) |

### Cross-checks

- Rabbet contact at bezel Y=8 -> tray Y=152: Sub-I pocket rear walls are at tray Y=152. Consistent.
- Bezel outer face at tray Y=160: protrudes 5mm past tray front face (Y=155). The 5mm panel thickness provides the palm rest body.
- Snap tab centers at bezel Y=6.5 -> tray Y=153.5: matches Sub-I pocket center Y=153.5. Consistent.
- Bezel return wall inner face at X=1.5 (left): contacts Sub-I rabbet ledge at tray X=1.5. Consistent.
- Bezel bottom inner face at Z=1.5: contacts Sub-I floor rabbet ledge at tray Z=1.5. Consistent.
- Finger channel Z range (21..51 in bezel frame = 21..51 in tray frame): snap tab pockets L1/R1 at tray Z=19.5..24.5 and L2/R2 at Z=47.5..52.5 bracket the channel from below and above. The pocket Z centers (22 and 50) are at the edges of the channel, with the pockets partially inside the channel Z range. This matches Sub-I's finger channel clearance analysis.
- Left paddle X center (2.5 in tray frame): within the left channel X extent (0..25 in bezel frame = 0..25 in tray frame). Accessible.
- Paddle Z extent (21..51 in tray frame): matches channel Z extent (21..51). Fully visible through the channel.

### Bezel frame -> Lid frame cross-reference

```
Lid frame -> Tray frame:  lid_Z = 0 -> tray_Z = 72;  lid_X = tray_X;  lid_Y = tray_Y
Bezel top edge:  bezel_Z = 72 -> tray_Z = 72 -> lid_Z = 0

At the BT1 tab location:
  bezel (80, 6.5, 72) -> tray (80, 153.5, 72) -> lid (80, 153.5, 0)
  Lid T1 pocket: lid X = 77.5..82.5, Y = 152..155, Z = 0..2.5
  BT1 at lid (80, 153.5, 0) is centered in the pocket X and Y ranges. Tab extends into +Z (lid frame), into pocket depth. Consistent.
```

---

## 5. Linkage Rod Path Through Bezel Zone

The linkage rods pass through the tray wall slots (Sub-G) and run along the tray wall exteriors to the pull-tab paddles near the front. The bezel's finger channels provide access to these paddles.

**Rod path (tray frame, left rod):**

| Waypoint | Tray (X, Y, Z) | Description |
|----------|----------------|-------------|
| Release plate hook | (52.5, 12.0, 36.0) | Rod attaches at plate left edge, mid-thickness, plate center Z |
| Rod bends to run along wall | (~5, ~15, ~37) | Rod transitions from interior to the wall slot zone |
| Wall slot entry | (5, 20, 37.5) | Rod center enters left wall slot at mid-slot position |
| Wall slot exit | (0, 20, 37.5) | Rod exits slot on tray exterior |
| Rod runs forward along exterior | (0..2, 20..148, 37.5) | Rod runs in +Y along the left wall exterior |
| Pull-tab paddle | (2.5, 148, 36) | Paddle face at tray Y = 148, centered in channel |

The rod runs along the tray exterior wall face, through the zone that will be covered by the bezel's left return wall and finger channel. In the channel zone (X = 0..25, Z = 21..51), the rod and paddle are exposed and accessible. Outside the channel zone, the rod is hidden behind the bezel's return wall.

**Right rod:** Mirror about tray X = 80.

---

## 6. Print Orientation and Build Plate Contact

```
Print orientation: outer face (Y = 0) on build plate
Build plate contact surface: the palm contour outer face (Y = 0 plane, with 1.5 mm crown)
Layer direction: Y axis (each layer adds to bezel depth)
```

The outer face contacts the PEI build plate for the best surface finish (smooth, slight sheen). The palm crown (1.5 mm) means the build plate contact is not perfectly flat -- the crown creates a slight dome. For printing, the crown may need to be flattened to the Y = 0 plane (first layer flat), with the crown shape built up in subsequent layers. Alternatively, print with the outer face up (Y max on build plate) and accept visible layer lines on the cosmetic surface. The parts specification step will determine the final print orientation.

The finger channels are open voids that may require supports when printed with the outer face down (the channel ceilings at Z = 51 would be overhangs). Printing with the bezel standing upright (Z axis vertical) eliminates channel supports but puts layer lines on the palm surface. This trade-off is resolved in the parts specification.
