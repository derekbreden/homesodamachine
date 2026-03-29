# Sub-F: Tube Routing Channels — Parts Specification

## Coordinate System

Tray reference frame (identical to Sub-F frame — no local transform):
- Origin: rear-left-bottom corner of tray outer envelope
- X: 0..160 mm (width, left to right)
- Y: 0..155 mm (depth, dock/rear to user/front)
- Z: 0..72 mm (height, bottom to top)
- Floor inner surface: Z = 3.00 mm
- Left wall inner face: X = 5.00 mm
- Right wall inner face: X = 155.00 mm
- Rear wall inner face: Y = 8.50 mm

---

## 1. Mechanism Narrative

Sub-F is not a moving mechanism. It is a set of passive printed features — four U-shaped channels on the tray floor with snap-in retention clips — that constrain the routing of four 1/4" OD (6.35 mm) silicone tubes from the pump barb exits to the John Guest fitting ports.

**What the user sees and touches:** Nothing. The tube routing channels are entirely internal to the cartridge, hidden beneath the lid (Sub-A + lid). The user never interacts with these features during normal operation. During Tier 2 service (lid removed for tube re-routing or fitting replacement), the user sees four shallow troughs on the tray floor running from the pump zone toward the rear wall, with tubes pressed into them.

**What is stationary:** Everything. The four U-channels and their snap clips are integral printed features of the tray floor. They do not move.

**What moves (during tube installation only):** The snap clip tabs deflect outward by 0.175 mm per side when the 6.35 mm OD tube is pressed downward into the 6.00 mm snap gap between opposing clip tabs. Once the tube passes the tab edges, the tabs spring back inward, capturing the tube. This is a one-time assembly action (repeated only during service).

**Snap clip deflection mechanism:** Each clip consists of two opposing tabs protruding inward from the top of the channel walls. The tabs are 1.00 mm thick (Z extent) and overhang 2.00 mm into the channel from each side, leaving a 6.00 mm gap between them. The tube OD is 6.35 mm, so each tab must deflect outward 0.175 mm. The tab is cantilevered from the channel wall with a 0.50 mm undercut relief below it (between Z = 9.50 and Z = 10.00), allowing the thin section to flex. PETG at 1.00 mm thickness can elastically deflect 0.175 mm over the 2.00 mm cantilever length without permanent deformation.

**Tube installation sequence:**
1. Route the silicone tube from the pump barb, letting it drop to the floor level.
2. Lay the tube into the open-top U-channel from above.
3. Press the tube downward at the clip location. The tube crown (at Z = 11.35 in the channel, computed as Z = 3.00 floor + 10.00/2 channel half-depth + 6.35/2 tube half-OD = 11.18, rounding to the spatial doc's ~8.18 centerline + 3.18 radius = 11.36) pushes the clip tabs outward.
4. The tube snaps past the tabs and seats in the channel. The tabs return to their rest position, trapping the tube below them.
5. Repeat for all four tubes.

**Tube retention force:** The 0.175 mm interference per side provides a light retention. The tube can be pulled upward out of the clip with moderate finger force (~2-5 N estimated) by deflecting the tabs outward again. This is intentional — tubes must be removable during service without tools.

**No return force is needed.** The clips are a static detent, not a spring-loaded mechanism. Gravity and the tube's own stiffness keep it seated.

---

## 2. Constraint Chain Diagram

```
[Assembler hand] -> [presses tube downward into U-channel]
                         |
                         v
[Tube (6.35mm OD)] -> [contacts snap clip tabs] -> [tabs deflect outward 0.175mm]
                                                         ^ cantilever: 1.00mm thick, 2.00mm overhang, 0.50mm undercut
                                                         |
                         v (tube passes tab edges)       |
[Tube seated in channel] <- [tabs spring back to rest position]
                         |
                         ^ constrained laterally by: channel walls (10.00mm apart, 10.00mm tall, Z = 3 to Z = 13)
                         ^ constrained vertically (down) by: channel floor (Z = 3.00, tray floor surface)
                         ^ constrained vertically (up) by: snap clip tabs (Z = 10.00 to Z = 13.00, 6.00mm gap)
                         ^ constrained along channel path by: friction + tube stiffness (no mechanical stop)
```

**Force path for tube retention:**
- Gravity pulls tube downward -> channel floor (Z = 3.00) reacts.
- Any upward pull on tube -> snap clip tabs (overhanging at Z = 10.00 to Z = 13.00) resist until deflection force exceeds elastic limit of 1.00mm PETG tab.
- Lateral forces on tube -> channel side walls (2.00 mm thick, 10.00 mm tall) resist.
- Axial forces along tube path -> no printed constraint (friction only). The tube is held at a single clip point per channel; the rest of its length is free to slide axially within the channel. This is acceptable because the tube is connected at both ends (barb and fitting) and has no tendency to translate axially.

---

## 3. Channel Features

### 3a. Cross-Section (all 4 channels identical)

```
Looking along channel centerline:

         10.00mm
    |<-------------->|
    +---+--------+---+  Z = 13.00
    |2mm|        |2mm|
    |   | 10.00  |   |
    |   |  gap   |   |  Channel depth: 10.00mm
    |   |        |   |
    |   |  (tube)|   |
    +---+--------+---+  Z = 3.00 (floor)
```

| Parameter | Value (mm) | Source |
|-----------|------------|--------|
| Channel width (inner gap) | 10.00 | Spatial doc 3e: 6.35 tube OD + 3.65 clearance |
| Channel depth | 10.00 | Spatial doc 3e |
| Channel wall thickness | 2.00 | Spatial doc 3e: minimum printable PETG wall |
| Wall height | 10.00 | From Z = 3.00 (floor) to Z = 13.00 |
| Floor surface | Z = 3.00 | Sub-A floor inner surface |
| Wall tops | Z = 13.00 | Z = 3.00 + 10.00 |

**Implementation:** Raised walls (UNION) extruded upward from the tray floor. Each channel is a U-trough formed by two parallel walls separated by a 10.00 mm gap. Adjacent channels within a pump pair share a single 2.00 mm wall.

### 3b. Channel Paths

Each channel follows a smooth arc (R = 30.00 mm, above the 25.00 mm minimum bend radius for 1/4" silicone tubing) from its entry point near the pump barb drop zone to its exit point near the fitting column. The channel wall centerlines (i.e., the tube centerline positions) are sampled below at 5 mm Y intervals.

**Tube A channel (P1-lower to F-LL):**

| Y (mm) | X centerline (mm) |
|---------|-------------------|
| 33.0 | 37.2 |
| 28.0 | 42.5 |
| 23.0 | 50.0 |
| 18.0 | 57.5 |
| 16.0 | 64.0 |

**Tube B channel (P1-upper to F-UL), parallel to A, +12.00 mm X offset:**

| Y (mm) | X centerline (mm) |
|---------|-------------------|
| 33.0 | 49.2 |
| 28.0 | 54.5 |
| 23.0 | 62.0 |
| 18.0 | 69.5 |
| 16.0 | 76.0 |

**Tube C channel (P2-lower to F-LR), mirror of A about X = 80:**

| Y (mm) | X centerline (mm) |
|---------|-------------------|
| 33.0 | 122.8 |
| 28.0 | 117.5 |
| 23.0 | 110.0 |
| 18.0 | 102.5 |
| 16.0 | 96.0 |

**Tube D channel (P2-upper to F-UR), mirror of B about X = 80:**

| Y (mm) | X centerline (mm) |
|---------|-------------------|
| 33.0 | 110.8 |
| 28.0 | 105.5 |
| 23.0 | 98.0 |
| 18.0 | 90.5 |
| 16.0 | 84.0 |

**Arc radius:** 30.00 mm throughout all four channels. The spatial resolution document verified that a 30 mm radius arc fits the available chord length (~31.7 mm) and produces a 33.3 mm arc length.

**Channel pair spacing:** Within each pump pair, channels are 12.00 mm center-to-center (10.00 mm channel width + 2.00 mm shared wall). At the fitting end (Y = 16), the two pairs share a common 2.00 mm wall at the tray centerline X = 80.

### 3c. Channel Wall Geometry — Full Footprint

Each channel has an inner wall and an outer wall, each 2.00 mm thick, offset 5.00 mm from the channel centerline on each side.

**Pump 1 pair wall X positions at entry (Y = 33.0):**
- Tube A outer wall: X = 32.20 to 34.20
- Tube A inner wall / Tube B outer wall (shared): X = 42.20 to 44.20
- Tube B inner wall: X = 54.20 to 56.20 (note: this is offset; at the shared wall for adjacent channels the wall is shared, reducing to one 2mm wall — see note below)

Correction per spatial doc 3i: Tube A and B share one wall between them. At Y = 33.0:
- A left wall: X = 32.20 to 34.20
- Shared A-B wall: X = 42.20 to 44.20
- B right wall: X = 52.20 to 54.20

Wait — let me be precise. Channel A centerline at Y=33 is X = 37.2. The channel gap is 10.00mm, so walls are at X = 37.2 - 5.0 = 32.2 (left edge of left wall) to 37.2 + 5.0 = 42.2 (right edge of right wall). But the wall is 2mm thick, so: left wall spans X = 32.2 to 34.2, right wall spans X = 40.2 to 42.2. Channel B centerline at Y=33 is X = 49.2. Left wall: X = 44.2 to 46.2. Right wall: X = 52.2 to 54.2. The gap between A's right wall (ending at 42.2) and B's left wall (starting at 44.2) is 2.0 mm. Per the spatial doc, this gap is exactly the "shared wall" — the 12mm center-to-center spacing was chosen so the adjacent walls merge into a single 2mm wall.

**Clarification on "shared wall":** The spatial doc states 12.00 mm center-to-center within a pair (10 mm channel + 2 mm wall). This means the right wall of the inner channel and the left wall of the outer channel ARE a single merged 2.00 mm wall. The two walls do not exist separately with a gap — they are one printed feature spanning 2.00 mm. At Y = 33.0 for the Pump 1 pair:
- A left wall: X = 32.20 to 34.20
- Shared A-B wall: X = 42.20 to 44.20
- B right wall: X = 52.20 to 54.20
- Total pair width: 54.20 - 32.20 = 22.00 mm (two 10mm channels + three 2mm walls, but the outer two walls are 2mm each and the shared wall is 2mm = 6mm walls + 20mm channels... no.)

Let me recalculate cleanly. Center-to-center is 12.00. Channel A center = 37.2, Channel B center = 49.2. Difference = 12.0. Correct. Each channel is 10mm wide (inner gap). Wall is 2mm thick.

Channel A: left wall left edge = 37.2 - 5.0 - 2.0 = 30.2? No. The channel walls define the U-trough. The inner gap is 10mm. The wall material is on either side of that gap. So:
- Channel A inner gap: X = 32.2 to 42.2 (centered on 37.2, width 10.0)
- Channel A left wall: X = 30.2 to 32.2 (2mm thick, to the left of the gap)
- Channel A right wall: X = 42.2 to 44.2 (2mm thick, to the right of the gap)
- Channel B inner gap: X = 44.2 to 54.2 (centered on 49.2, width 10.0)
- Channel B left wall: X = 42.2 to 44.2 (2mm thick — same as A's right wall!)
- Channel B right wall: X = 54.2 to 56.2

So A's right wall and B's left wall are the same physical wall: X = 42.2 to 44.2. This is the "shared wall." The spatial doc's envelope (32.2 to 54.2) is confirmed.

**Pump 1 pair (A+B) wall summary at Y = 33.0:**

| Wall | X range (mm) | Thickness (mm) |
|------|-------------|----------------|
| A left (outer) | 30.20 to 32.20 | 2.00 |
| A-B shared (center) | 42.20 to 44.20 | 2.00 |
| B right (outer) | 54.20 to 56.20 | 2.00 |

Hmm, but the spatial doc says "A outer wall: X = 37.2 - 5 = 32.2 to X = 37.2 + 5 = 42.2." That's describing the channel extent from wall-inner-face to wall-inner-face. And the wall thickness is outside that. Let me re-read spatial doc section 3i more carefully.

The spatial doc says: "Channel walls at widest point (Y=33): A outer wall: X = 37.2 - 5 = 32.2 to X = 37.2 + 5 = 42.2." This is ambiguous — it could mean the channel extends from 32.2 to 42.2 (the inner faces of the walls). But then: "Shared wall between A and B: X = 42.2 to X = 44.2 (2mm wall)." So the shared wall occupies 42.2 to 44.2. And "B outer wall: X = 49.2 - 5 = 44.2 to X = 49.2 + 5 = 54.2." So channel B gap extends from 44.2 to 54.2.

This means the wall is INCLUDED in the "outer wall" extent. The spatial doc is using "outer wall" to mean "the full extent of this channel including its walls." So:
- Channel A occupies X = 32.2 to 42.2 (this includes the left wall and the channel gap — the gap starts at 32.2 + 2 = 34.2 and ends at 42.2 - 0 = 42.2? No, that gives an 8mm gap.)

Actually, re-reading: the spatial doc states the overall extents as "A outer wall: X = 32.2 to 42.2" and "B outer wall: X = 44.2 to 54.2" with "shared wall: 42.2 to 44.2." The total Pump 1 pair extent is 32.2 to 54.2. That's 22mm for two channels + walls. If we have: 2mm wall + 10mm gap + 2mm shared wall + 10mm gap = 24mm. But 54.2 - 32.2 = 22mm. So the outer walls must only be on the shared side, not on the outside edges. Let me reconsider.

If the design is: gap-A (10mm) | shared-wall (2mm) | gap-B (10mm) = 22mm, and center-to-center = 12mm, then:
- Channel A gap: 32.2 to 42.2 (10mm)
- Shared wall: 42.2 to 44.2 (2mm)
- Channel B gap: 44.2 to 54.2 (10mm)
- No outer walls on the outside edges of A and B.

But that's not a U-channel — a U-channel needs walls on BOTH sides. A wall-less outer edge would mean the tube can fall out sideways.

I think the spatial doc's description is the WALL extents, not the gap extents. Let me re-read one more time. "Channel cross-section: 10.00mm [width label], channel depth 10.00mm." The 10mm is the channel width (gap). "Wall thickness between adjacent channels: 2.00." And "Channel width: 10.00 — 6.35mm tube OD + 3.65mm clearance."

The spatial doc's floor plan shows "X:35 47 47 59" for the A-B pair at the entry. That's: 35 to 47 = 12mm for A, 47 to 59 = 12mm for B. Each channel occupies 12mm of X space (10mm gap + one 2mm wall). The pair shares boundaries: 47 is both A's right edge and B's left edge.

So the correct interpretation: each channel is a 10mm gap with 2mm walls on EACH side = 14mm total per channel. But when two channels are adjacent, they share the wall between them, so the pair = 14 + 14 - 2 = 26mm. But 59 - 35 = 24mm = 47-35=12 + 59-47=12.

The spatial doc's numbers (35, 47, 59) don't match the centerlines (37.2, 49.2) offset by 5mm for the gap half-width. 37.2 - 5 = 32.2, not 35. There's a discrepancy. The floor plan appears to be approximate/schematic.

I'll use the analytically correct values derived from the stated centerlines and dimensions:

**Each channel structure:** 2mm outer wall + 10mm gap + 2mm outer wall = 14mm per isolated channel. When paired with 12mm c-c spacing, the inner walls merge:
- Channel A left wall: CL_A - 5.0 - 2.0 to CL_A - 5.0 = 30.20 to 32.20
- Channel A gap: 32.20 to 42.20
- Shared wall: 42.20 to 44.20
- Channel B gap: 44.20 to 54.20
- Channel B right wall: 54.20 to 56.20
- Total pair: 30.20 to 56.20 = 26.00mm at Y = 33.0

Wait — but the spatial doc explicitly says "Pump 1 pair X range at entry: 32.2 to 54.2" in the dimensional summary table. That's 22mm, not 26mm. This suggests the outer walls are NOT present — the channels are just raised walls between them and the pair has open outer edges.

I think the intended design is:
- Three walls for each pair: outer-left, shared-center, outer-right
- Pair extent includes walls: 32.2 to 54.2 = 22mm
- Wall breakdown: wall (2mm) at 32.2-34.2, gap-A (8mm) at 34.2-42.2, wall (2mm) at 42.2-44.2, gap-B (8mm) at 44.2-52.2, wall (2mm) at 52.2-54.2
- That gives 8mm gaps, not 10mm.

OR: the pair extent is measured from the inner face of the outermost wall to the inner face of the other outermost wall. Then: inner-face-left = 32.2, inner-face-right = 54.2. Gap-A = 32.2 to 42.2 = 10mm. Shared wall = 42.2 to 44.2 = 2mm. Gap-B = 44.2 to 54.2 = 10mm. The outer walls extend BEYOND this range: left wall = 30.2 to 32.2, right wall = 54.2 to 56.2.

This interpretation gives the correct 10mm gaps. The spatial doc's "X range" appears to be the channel-gap extent (inner wall faces), not the total solid extent including outer walls. I'll use this interpretation.

OK, I've spent too long on this ambiguity. Let me just specify the design clearly and move on.

### 3d. Wall Positions — Complete Specification

All walls are 2.00 mm thick, 10.00 mm tall (Z = 3.00 to Z = 13.00). Positions given at the channel entry (Y = 33.0) and exit (Y = 16.0); intermediate positions follow the smooth arc interpolation from Section 3b.

**Pump 1 pair (channels A + B):**

| Wall ID | Y = 33.0 X range | Y = 16.0 X range | Description |
|---------|-------------------|-------------------|-------------|
| W1-L | 30.20 to 32.20 | 57.00 to 59.00 | A outer-left wall |
| W1-C | 42.20 to 44.20 | 69.00 to 71.00 | A-B shared center wall |
| W1-R | 54.20 to 56.20 | 81.00 to 83.00 | B outer-right wall |

Derivation at Y = 33.0: A centerline 37.2 - 5.0 (half gap) - 2.0 (wall) = 30.2 for W1-L left edge. A centerline + 5.0 = 42.2 for W1-C left edge. B centerline + 5.0 = 54.2 for W1-R left edge.

Derivation at Y = 16.0: A centerline 64.0 - 5.0 - 2.0 = 57.0 for W1-L left edge. A centerline + 5.0 = 69.0 for W1-C left edge. B centerline + 5.0 = 81.0 for W1-R left edge.

**Pump 2 pair (channels C + D):**

| Wall ID | Y = 33.0 X range | Y = 16.0 X range | Description |
|---------|-------------------|-------------------|-------------|
| W2-L | 103.80 to 105.80 | 77.00 to 79.00 | D outer-left wall |
| W2-C | 115.80 to 117.80 | 89.00 to 91.00 | D-C shared center wall |
| W2-R | 125.80 to 127.80 | 101.00 to 103.00 | C outer-right wall |

Derivation at Y = 33.0: D centerline 110.8 - 5.0 - 2.0 = 103.8 for W2-L left edge. D centerline + 5.0 = 115.8 for W2-C left edge. C centerline + 5.0 = 127.8 for W2-R left edge.

Derivation at Y = 16.0: D centerline 84.0 - 5.0 - 2.0 = 77.0 for W2-L left edge. D centerline + 5.0 = 89.0 for W2-C left edge. C centerline + 5.0 = 101.0 for W2-R left edge.

**Cross-pair shared wall at fitting end (Y = 16.0):** W1-R right edge at Y=16 = 83.0. W2-L left edge at Y=16 = 77.0. These overlap from 77.0 to 83.0 — a 6mm overlap. This means the two pairs' outer walls merge at the fitting end. The physical wall between channel B (gap ending at 81.0) and channel D (gap starting at 79.0) occupies X = 79.0 to 81.0, a 2mm wall. This is consistent with the spatial doc section 3i stating "the inner walls of the two pairs meet at X ~ 80, which is acceptable — they share a single 2mm wall at the tray centerline."

**DESIGN GAP: The outer walls of the two pairs (W1-R and W2-L) converge and overlap between Y ~ 23 and Y = 16. The exact merge geometry (where three separate walls become one shared wall) needs to be resolved in the CadQuery script as a smooth wall-merge operation. This specification defines the wall positions at the entry and exit; the CAD implementation must produce a valid solid at intermediate positions where walls converge.**

### 3e. Snap Clip Features

One snap clip per channel, positioned at the midpoint of each channel's floor run. All clips are geometrically identical.

**Clip positions:**

| Channel | Clip center X (mm) | Clip center Y (mm) | Source |
|---------|-------------------|-------------------|--------|
| A | 50.0 | 23.0 | Spatial doc 3h |
| B | 62.0 | 23.0 | Spatial doc 3h |
| C | 110.0 | 23.0 | Spatial doc 3h |
| D | 98.0 | 23.0 | Spatial doc 3h |

**Clip geometry:**

```
Cross-section at clip location (looking along channel):

    |<--2mm-->|<---6.00mm gap--->|<--2mm-->|
    +---+     +-----+-----+     +---+
    |   |     |/tab/| |/tab/|     |   |  Z = 13.00 (wall top / tab top)
    |   |     +-----+ +-----+     |   |  Z = 10.00 (tab bottom)
    |   |     :                   |   |  Z = 9.50  (undercut bottom)
    |   |                         |   |
    |   |       (tube 6.35mm)     |   |
    |   |                         |   |
    +---+-------------------------+---+  Z = 3.00 (floor)
```

| Parameter | Value (mm) | Source |
|-----------|------------|--------|
| Tab length along channel (Y extent) | 5.00 | Spatial doc 3h |
| Tab overhang into channel from each wall | 2.00 | Spatial doc 3h |
| Remaining gap between opposing tabs | 6.00 | 10.00 - 2*2.00 |
| Tab thickness (Z extent) | 3.00 | Z = 10.00 to Z = 13.00 (spatial doc 3h) |
| Undercut relief below tab (Z extent) | 0.50 | Z = 9.50 to Z = 10.00 (spatial doc 3h) |
| Undercut depth into wall (X extent) | 0.50 | Allows tab to flex outward |
| Snap interference per side | 0.175 | (6.35 - 6.00) / 2 |

**Tab detail:** Each tab is a rectangular block protruding from the inner face of the channel wall at the top of the wall. It spans from Z = 10.00 to Z = 13.00 (3.00 mm tall) and overhangs 2.00 mm into the channel. Below the tab, a 0.50 mm tall by 0.50 mm deep rectangular undercut (Z = 9.50 to Z = 10.00, extending 0.50 mm into the wall from the inner face) creates a thin hinge section that allows the tab to flex outward when the tube is pressed in.

**DESIGN NOTE (tab thickness clarification):** The spatial doc section 3h states "Tab thickness: 1.00" and "Tab height (Z position): Z = 10 to Z = 13." These are contradictory — the Z range is 3.00mm, not 1.00mm. The 1.00mm figure likely refers to the effective flexing section height (the portion above the undercut that acts as the cantilever hinge), while the full tab body is 3.00mm tall to provide a solid ramp surface for the tube to press against. The flexing behavior comes from the 0.50mm undercut, not the full tab height. The tab body itself is rigid; only the thin section at Z = 9.50 to Z = 10.00 (where the undercut reduces the wall cross-section) flexes.

### 3f. Channel Openings

All four channels have open ends at both the pump side (Y = 33.0) and the fitting side (Y = 16.0). The walls simply terminate — no printed caps, ramps, or funnels. The tube enters and exits the channel freely at each open end.

**Pump-side openings (Y = 33.0):** The tube descends from the pump barb (at Y = 35.0, Z = ~25 or ~44) and enters the open channel end. The vertical drop is unconstrained — the flexible silicone tube bends naturally.

**Fitting-side openings (Y = 16.0):** The tube exits the channel and curves upward and rearward in a 3D arc to reach the fitting port face (at Y = 22.41, Z = 26 or 46). This transition is also unconstrained — no printed guide is needed because the tube lengths are short (20-39 mm free span) and the silicone is self-supporting.

**Optional: 2mm chamfer on wall tops at channel entries/exits** — a 45-degree chamfer on the top edges of the channel walls at Y = 33.0 and Y = 16.0 would ease tube insertion. This is a nice-to-have for prototyping; omit from the first print and add if tube installation proves finicky.

---

## 4. Vertical Transition Zones

These zones are NOT printed features. They are descriptions of the free tube paths outside the channels, documented here for completeness and to confirm that no additional printed guides are needed.

**Pump-side drops:**

| Tube | From (barb) | To (channel entry) | Drop (mm) | Confidence |
|------|-------------|--------------------|-----------:|------------|
| A | (~43.2, 35.0, ~25) | (37.2, 33.0, ~8) | ~17 | LOW (barb Z) |
| B | (~43.2, 35.0, ~44) | (49.2, 33.0, ~8) | ~36 | LOW (barb Z) |
| C | (~116.8, 35.0, ~25) | (122.8, 33.0, ~8) | ~17 | LOW (barb Z) |
| D | (~116.8, 35.0, ~44) | (110.8, 33.0, ~8) | ~36 | LOW (barb Z) |

**Fitting-side rises:**

| Tube | From (channel exit) | To (fitting port) | 3D distance (mm) |
|------|--------------------|--------------------|------------------:|
| A | (64.0, 16.0, ~8) | (70.0, 22.41, 26.0) | 20.0 |
| B | (76.0, 16.0, ~8) | (70.0, 22.41, 46.0) | 39.0 |
| C | (96.0, 16.0, ~8) | (90.0, 22.41, 26.0) | 20.0 |
| D | (84.0, 16.0, ~8) | (90.0, 22.41, 46.0) | 39.0 |

All distances are within the silicone tube's self-supporting bend capability at 25mm minimum radius.

---

## 5. Interface Dimensions

### 5a. Channel-to-Floor (Sub-A)

All channel walls bond directly to the tray floor inner surface at Z = 3.00. This is a monolithic UNION — the walls are part of the same printed solid as the floor. No separate interface, no clearance, no fasteners.

### 5b. Channel entries to pump zone (Sub-C)

No physical interface. The tube is the flexible link between the pump barb and the channel. The channel entries (Y = 33.0) are positioned 2.0 mm behind the barb face (Y = 35.0) to allow the tube's vertical-to-horizontal bend.

### 5c. Channel exits to fitting zone (Sub-D)

No physical interface. The tube is the flexible link between the channel exit and the fitting port. The channel exits (Y = 16.0) are positioned 6.41 mm in front of the fitting port faces (Y = 22.41) to allow the tube's horizontal-to-angled-rise transition.

### 5d. Interference clearances

| Potential conflict | Channel zone | Other feature zone | Clearance | Status |
|-------------------|-------------|-------------------|-----------|--------|
| Sub-C pump bosses | Y = 16..33 | Y ~ 83 | 50 mm | No interference |
| Sub-C motor cradles | Y = 16..33 | Y = 109..124 | 76 mm | No interference |
| Sub-E guide posts | Y = 16..33 near X = 80 | Rear wall face Y = 8.5 | Guide posts at Y < 16 | No interference |
| Sub-D fitting bores | Floor zone Z = 3..13 | Rear wall Y = 0..8.5 | Channels end at Y = 16 | No interference |

---

## 6. Material and Print Orientation

**Material:** PETG (per requirements.md and concept architecture).

**Print orientation:** Sub-F features are integral to the tray, which prints open-top facing up. The channel walls extrude upward from the floor (along +Z), which is the print direction. No overhangs on the channel walls. The snap clip tabs overhang 2.00 mm into the channel, which is printable at 45 degrees or with minimal support. The 0.50 mm undercut below each tab may require support material or can be printed bridging across the 0.50 mm gap.

**Layer height consideration:** Standard 0.2 mm layers are sufficient for channel walls. The snap clip tabs and undercuts are small features; 0.15 mm layers in that zone would improve tab edge quality but are not required for function.

---

## 7. Part Count

Sub-F adds zero additional parts. All features (channel walls, snap clips) are integral to the tray (Sub-A). The channels are UNION operations on the tray solid. The only non-printed component is the silicone tubing itself, which is a purchased item (1/4" OD silicone tubing, already in BOM).

---

## 8. Design Gaps

1. **DESIGN GAP: Wall merge geometry at fitting end.** Where the Pump 1 pair outer-right wall (W1-R) and Pump 2 pair outer-left wall (W2-L) converge between Y ~ 23 and Y = 16, the separate walls must merge into a single 2mm wall at the tray centerline. The exact Y position where the merge occurs and the wall shape during the transition needs to be resolved in CAD. A smooth taper/fillet where the walls meet is the expected solution.

2. **DESIGN GAP: Snap clip tab "thickness" ambiguity.** The spatial doc states both "tab thickness: 1.00mm" and "tab Z range: 10 to 13" (3.00mm). This specification uses the 3.00mm body with a 0.50mm undercut hinge as the functional interpretation. The first prototype should validate that the undercut hinge provides adequate flex for 0.175mm deflection without permanent deformation. If the tab is too stiff, the undercut depth can be increased from 0.50mm to 1.00mm.

3. **DESIGN GAP: Tube axial retention.** No feature prevents the tube from sliding axially within the channel. The tube endpoints (barb press-fit and JG fitting grip) provide the actual axial constraint. If tubes tend to bow upward out of the channels during operation (due to thermal expansion or pump pulsation), additional clips may be needed. One clip per channel is a starting point for prototyping.
