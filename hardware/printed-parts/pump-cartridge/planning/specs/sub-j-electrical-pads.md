# Parts Specification: Sub-J Electrical Contact Pad Areas

## Coordinate System

Tray reference frame (identical to Sub-A):
- Origin: rear-left-bottom corner
- X: width, 0..160 mm
- Y: depth, 0..155 mm (0 = dock/rear, 155 = user/front)
- Z: height, 0..72 mm
- Print orientation: open-top-up

---

## 1. Mechanism Narrative

### What the user sees and touches

Nothing. Sub-J features are entirely on the rear wall exterior (Y = 0 plane) and on the tray interior floor and walls. The rear wall faces into the dock when the cartridge is inserted. The user never sees, touches, or interacts with these features. The electrical connection is a blind-mate: as the cartridge slides in on its T-rails, female spade terminals on the tray's rear wall engage male blade tabs protruding from the dock, automatically and invisibly.

### What moves

**Moving part:** The entire cartridge translates along the -Y axis during insertion (and +Y during removal). The female spade terminals are fixed within their retention slots on the tray rear wall and move with the cartridge as a rigid body. No part of Sub-J moves independently.

**Stationary parts:** The dock's male blade tabs are fixed to the dock structure. The tray rear wall (host for all Sub-J features) is rigid within the cartridge.

### What converts the motion

No motion conversion. The cartridge's linear translation along Y is the same motion that drives blade engagement. The T-rails (Sub-B) constrain the cartridge to pure Y-axis translation with lateral (X) and vertical (Z) alignment to within 0.3 mm. The 6.3 mm wide blade self-centers within the 7.0 mm blade opening in the retention slot, providing an additional 0.35 mm of lateral tolerance per side. The 4.8 mm blades self-center within the 5.5 mm openings, providing 0.35 mm per side.

### What constrains each part

Each female spade terminal is constrained in its retention slot:
- **+Y direction (pushed inward by blade engagement):** The slot floor at Y = 3.0 mm. The terminal housing bears against this surface when the dock blade pushes into the spade.
- **-Y direction (pulled outward):** The terminal housing shoulders bear against the slot entrance edges at Y = 0.
- **X and Z directions:** The 8.0 mm wide x 8.5 mm tall slot walls (for 6.3 mm terminals) constrain the housing laterally and vertically. The housing has 1.7 mm clearance in X and 2.2 mm in Z (approximate, depends on actual terminal housing dimensions), which is taken up by the blade self-centering force during engagement.
- **The 18.0 mm wide x 7.0 mm tall slot (for the T5 4.8 mm 2-pin terminal)** constrains the dual-pin housing similarly.

Wires are constrained by:
- **Floor channels:** 6.0 mm wide x 2.0 mm deep U-channels cut into the Z = 3 floor surface, running from Y = 124 to Y = 9 along the left side (X = 22..28) and right side (X = 132..138). Wires sit below the floor surface plane at Z = 1..3.
- **Wall pass-throughs:** 3.0 mm diameter holes through the rear wall at each terminal position (W1-W4), allowing wires to pass from the interior to the exterior retention slots.

### What provides the return force

No return force needed. The terminals are press-fit into their retention slots during factory assembly and remain there permanently. The wire crimps and slot geometry hold them in place. There is no moving mechanism within Sub-J.

### What is the user's physical interaction

None. The user's only interaction is sliding the cartridge in and out. The blade engagement and disengagement happens passively during the last ~5 mm of insertion travel and the first ~5 mm of removal travel. The user feels this as a slight increase in insertion resistance (the spring force of the female spade gripping the male blade), but this force (estimated 1-3 N per terminal, 5-15 N total for all 5 positions) is small compared to the spring-detent force at end-of-travel and is not a distinct tactile event.

---

## 2. Constraint Chain

```
[Cartridge translates -Y on T-rails (Sub-B)]
  |
  v  (rigid body motion: tray rear wall carries terminals along Y)
[Female spade terminals in retention slots (Sub-J, Y=0 plane)]
  |
  v  (blade-in-spade linear engagement along Y axis)
[Male blade tabs on dock (fixed, protruding +Y)]
  ^ constrained laterally by: blade opening in slot (7.0 or 5.5 mm) + T-rail alignment (0.3 mm)
  ^ constrained vertically by: blade opening in slot (2.0 or 1.5 mm) + T-rail alignment (0.3 mm)
  ^ engagement force absorbed by: slot floor at Y = 3.0 mm (5.5 mm of wall material behind it)
```

Wire routing constraint chain:
```
[Pump motor solder tabs (Y~124, Z~37)]
  |
  v  (wire drops alongside pump body to floor)
[Floor wire channel (Z = 1..3, 6.0 mm wide)]
  |
  v  (wire runs rearward along floor, Y = 124 to Y = 9)
[Rear wall interior face (Y = 8.5)]
  |
  v  (wire passes through 3.0 mm hole in rear wall)
[Retention slot on rear wall exterior (Y = 0)]
  ^ wire captured by: channel walls (X constraint), channel depth (Z constraint)
  ^ wire exits through: 3.0 mm pass-through hole (W1-W4)
  ^ terminal seated in: retention slot (all 4 sides captured)
```

---

## 3. Feature Specifications

### 3.1 Terminal Retention Slots — 6.3 mm Type (T1, T2, T3, T4)

Four rectangular pockets cut into the rear wall exterior face at Y = 0.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot width (X) | 8.0 mm | Housing clearance for 6.3 mm blade terminal |
| Slot height (Z) | 8.5 mm | Housing clearance for standard flag terminal |
| Slot depth (Y) | 3.0 mm | Cut from Y = 0 inward to Y = 3.0. Leaves 5.5 mm of rear wall behind. |
| Blade opening width (X) | 7.0 mm | Centered in slot (0.5 mm wall each side). Male blade enters here. |
| Blade opening height (Z) | 2.0 mm | Centered vertically in slot. Clears 0.8 mm blade with 0.6 mm margin per side. |
| Blade opening depth (Y) | Full: 0 to 3.0 mm | Open channel from slot floor to exterior face, so blade can enter. |

The blade opening is a rectangular through-slot in the slot floor (at Y = 3.0), centered on the slot center, extending from Y = 0 to Y = 3.0. It allows the dock's male blade to pass through and engage the female spade inside the slot.

**Slot positions (center X, center Z on Y = 0 plane):**

| Slot | X (mm) | Z (mm) | Function |
|------|--------|--------|----------|
| T1 | 25.0 | 18.0 | Pump 1 (+) |
| T2 | 25.0 | 30.0 | Pump 1 (-) |
| T3 | 135.0 | 18.0 | Pump 2 (+) |
| T4 | 135.0 | 34.0 | Pump 2 (-) |

### 3.2 Terminal Retention Slot — 4.8 mm Type (T5)

One rectangular pocket cut into the rear wall exterior face at Y = 0 for the 2-pin cartridge-present jumper.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot width (X) | 18.0 mm | 2-pin housing (2 x 4.8 mm blades at 7.0 mm c-c + housing walls) |
| Slot height (Z) | 7.0 mm | Smaller housing for 4.8 mm terminals |
| Slot depth (Y) | 3.0 mm | Same as motor terminal slots |
| Blade opening width (X) | 5.5 mm each | Two openings, centered at 7.0 mm c-c within the slot |
| Blade opening height (Z) | 1.5 mm | Clears 0.5 mm blade with 0.5 mm margin per side |
| Blade opening depth (Y) | Full: 0 to 3.0 mm | Same through-slot as 6.3 mm type |

**Slot position:** X = 80.0, Z = 8.0 (centered on tray, below fitting exclusion zone).

The two blade openings are at X = 76.5 and X = 83.5 (80.0 +/- 3.5 mm, i.e., 7.0 mm center-to-center).

### 3.3 Wire Pass-Through Holes (W1-W4)

Four cylindrical holes through the rear wall, one per motor terminal.

| Hole | Center X (mm) | Center Z (mm) | Diameter (mm) | Y span |
|------|---------------|---------------|---------------|--------|
| W1 (to T1) | 25.0 | 18.0 | 3.0 | Y = 0 to 8.5 (full wall) |
| W2 (to T2) | 25.0 | 30.0 | 3.0 | Y = 0 to 8.5 |
| W3 (to T3) | 135.0 | 18.0 | 3.0 | Y = 0 to 8.5 |
| W4 (to T4) | 135.0 | 34.0 | 3.0 | Y = 0 to 8.5 |

Each hole is concentric with its corresponding terminal slot center. The wire enters from the interior face (Y = 8.5), passes through the wall, and the crimped spade terminal seats in the retention slot on the exterior face (Y = 0).

The 3.0 mm diameter accommodates 18-22 AWG stranded wire (~1.5 mm OD with insulation) with 0.75 mm clearance per side. The hole is positioned at the center of the retention slot so the wire exits directly behind the seated terminal.

No pass-through hole is needed for T5 because the cartridge-present jumper is a short wire loop (~30 mm) contained entirely within the T5 slot area on the rear wall exterior. Both pins of the 2-pin housing face the dock; the jumper wire connects them on the cartridge side (within the slot depth).

### 3.4 Wire Routing Channels — Floor

Two U-channels cut into the interior floor surface (Z = 3 plane), one per pump.

| Parameter | Left Channel (Pump 1) | Right Channel (Pump 2) |
|-----------|----------------------|----------------------|
| X range | 22..28 mm | 132..138 mm |
| Y range | 9..124 mm | 9..124 mm |
| Z range | 1..3 mm (2 mm deep cut into 3 mm floor) | 1..3 mm |
| Channel width (X) | 6.0 mm | 6.0 mm |
| Channel depth (Z) | 2.0 mm | 2.0 mm |
| Channel length (Y) | 115 mm | 115 mm |
| Material below channel | 1.0 mm (Z = 0 to Z = 1) | 1.0 mm |

Each channel carries 2 wires (18-22 AWG, ~1.5 mm OD each). The 6.0 mm width accommodates 2 wires side-by-side (2 x 1.5 mm = 3.0 mm) with 3.0 mm total clearance. Wires sit below the Z = 3 floor surface plane, avoiding interference with tube routing channels (Sub-F) which run at the Z = 3 surface level.

The channels run parallel to and inboard of the tube routing channels (Sub-F). The left wire channel (X = 22..28) is inboard of the left tray wall (X = 0..5), and the right wire channel (X = 132..138) is inboard of the right tray wall (X = 155..160).

### 3.5 Keying Strategy

Cross-mating is prevented by three independent mechanisms:

1. **Pair spacing difference:** Pump 1 blades are 12.0 mm apart (Z center-to-center). Pump 2 blades are 16.0 mm apart. A female spade pair crimped at 12.0 mm spacing cannot seat on blade tabs at 16.0 mm spacing (4.0 mm mismatch), and vice versa.

2. **Lateral separation:** Pump 1 terminals are at X = 25.0. Pump 2 terminals are at X = 135.0. The 110 mm separation means no accidental cross-connection is geometrically possible — the connectors cannot physically reach.

3. **Blade width differentiation:** Motor terminals use 6.3 mm blades. The cartridge-present terminal uses 4.8 mm blades. A 6.3 mm female spade cannot seat on a 4.8 mm blade (too loose for reliable contact), and a 4.8 mm spade will not accept a 6.3 mm blade (too wide to enter).

---

## 4. Interface Specifications

### 4.1 Sub-J to Sub-A (Rear Wall Exterior)

Five retention slot cuts and four wire pass-through holes, all within the rear wall body (X = 0..160, Y = 0..8.5, Z = 0..72). The rear wall is 8.5 mm thick. Slot depth is 3.0 mm, leaving 5.5 mm of intact wall behind each slot. Pass-through holes span the full 8.5 mm wall thickness.

### 4.2 Sub-J to Sub-A (Interior Floor)

Two wire routing channels cut into the Z = 3 floor surface to a depth of 2.0 mm (down to Z = 1). The floor is 3.0 mm thick (Z = 0 to Z = 3), so 1.0 mm remains below each channel. Channels are at X = 22..28 and X = 132..138, running Y = 9..124.

### 4.3 Sub-J to Sub-D (Fitting Bores, Clearance)

All terminal slots and wire holes are outside the fitting bore exclusion envelope (X = 54.3..105.8, Z = 11.8..63.3).

| Feature | Nearest exclusion edge | Clearance |
|---------|----------------------|-----------|
| T1 (X=25, Z=18) | X = 54.3 | 29.3 mm in X |
| T2 (X=25, Z=30) | X = 54.3 | 29.3 mm in X |
| T3 (X=135, Z=18) | X = 105.8 | 29.2 mm in X |
| T4 (X=135, Z=34) | X = 105.8 | 29.2 mm in X |
| T5 (X=80, Z=8) | Z = 11.8 (nearest funnel edge) | See below |

T5 clearance detail: T5 is at (X=80, Z=8). The T5 slot extends from Z = 4.5 to Z = 11.5 (center Z=8, height 7.0 mm). The nearest fitting funnel is at (X=70, Z=27.5) with a 15.5 mm diameter countersink, giving a lower funnel edge at Z = 27.5 - 7.75 = 19.75. Distance from T5 slot top (Z=11.5) to funnel lower edge (Z=19.75) = 8.25 mm. No volumetric interference.

### 4.4 Sub-J to Sub-F (Tube Routing Channels, Clearance)

Wire channels (Z = 1..3, below floor surface) and tube channels (at Z = 3 surface level and above) occupy different Z ranges. The wire channels at X = 22..28 and X = 132..138 are laterally separated from the tube channels which route between pump barbs and fittings through the center of the tray floor. No interference.

### 4.5 Sub-J to Dock (Mating Interface)

The dock provides 5 male blade positions matching (X, Z) coordinates of T1-T5. Dock blades protrude in the +Y direction, length ~8-10 mm. Engagement begins approximately 5 mm before end-of-travel (blade tip enters spade opening through the blade opening slot). Full seating occurs at end-of-travel when the spring detent clicks.

---

## 5. Assembly Sequence (Sub-J features within the tray)

Sub-J features are cuts into the tray (Sub-A) solid and are created during manufacturing (printing), not during assembly. However, the wiring and terminal installation is part of the cartridge assembly:

1. **Crimp female spade terminals** onto the 4 pump motor wires (2 per pump, 18-22 AWG stranded).
2. **Route Pump 1 wires** down alongside the pump body to the floor, into the left floor channel (X = 22..28), rearward along the floor to Y = 9, then thread each wire through its pass-through hole (W1 at Z=18, W2 at Z=30).
3. **Seat Pump 1 spade terminals** into retention slots T1 and T2 on the rear wall exterior (Y = 0 plane). Push each terminal into its 3.0 mm deep slot until the housing shoulders bear against the slot walls.
4. **Route Pump 2 wires** identically: down to floor, into right channel (X = 132..138), rearward, through W3 and W4.
5. **Seat Pump 2 spade terminals** into T3 and T4.
6. **Assemble cartridge-present jumper:** crimp two 4.8 mm female spade terminals onto a short (~30 mm) wire loop. Insert both terminals into the T5 dual-pin housing slot on the rear wall exterior.

**This wiring step occurs after pump mounting (so wires can be routed from motor terminals) and before lid installation (wires need to be laid into floor channels from above).**

### Disassembly for Service

To replace a pump motor wire or terminal:
1. Remove lid (snap-fit, tool-free).
2. Pull the spade terminal out of its retention slot from the exterior face.
3. Pull wire back through the pass-through hole.
4. Lift wire out of the floor channel.
5. Reverse to install new wire.

The retention slots do not have mechanical latches — terminals are held by friction fit of the housing against the slot walls. They can be pulled out with fingers or needle-nose pliers from the Y = 0 face.

---

## 6. Material and Manufacturing Notes

**Material:** PETG (same as entire tray, printed as one piece).

**Print orientation:** The tray prints open-top-up. The retention slots on the rear wall exterior (Y = 0 plane) are vertical features in the print — slot walls are printed in the XZ plane, slot depth runs along Y. The 3.0 mm slot depth and 8.0/18.0 mm slot widths are well within FDM capability without supports.

**Wire pass-through holes (3.0 mm diameter)** run horizontally through the rear wall along the Y axis. These are printed as horizontal holes and will exhibit the typical FDM bridging artifact on the top of the hole interior. At 3.0 mm diameter this is minimal and does not affect wire passage.

**Floor channels** are simple rectangular cuts in the floor surface, oriented along Y. No overhangs, no supports needed.

**Minimum wall thickness check:**
- Behind retention slots: 8.5 - 3.0 = 5.5 mm. Well above the 1.2 mm minimum for PETG walls.
- Slot walls between blade opening and slot edge: (8.0 - 7.0) / 2 = 0.5 mm per side. This is thin but structurally adequate because these walls only need to prevent the terminal housing from shifting laterally; the primary engagement force is along Y, absorbed by the 5.5 mm wall behind the slot.
- Floor below wire channels: 3.0 - 2.0 = 1.0 mm. Thin but acceptable — this is a non-structural surface carrying no load.
- T5 slot walls between blade openings: The two 5.5 mm blade openings at 7.0 mm c-c leave (7.0 - 5.5) = 1.5 mm between openings. The wall between the slot edge and the nearest blade opening: (18.0 - (2 x 5.5) - (7.0 - 5.5)) / 2 = (18.0 - 11.0 - 1.5) / 2 = 2.75 mm per side. Adequate.

**DESIGN GAP: Slot wall between blade opening edge and slot edge for 6.3 mm terminals is 0.5 mm per side. This is below the typical 0.8 mm minimum feature size for FDM at 0.2 mm layer height. This wall may not print reliably.** Options: (a) accept it as a cosmetic wall that may partially fuse or deform — it is not load-bearing; (b) widen the slot to 8.5 mm or narrow the blade opening to 6.5 mm to increase this wall to 0.75-1.0 mm; (c) verify with a test print. The current spec retains the 8.0 mm / 7.0 mm dimensions from the spatial resolution; this gap should be resolved during prototyping.

---

## 7. Parts List (Sub-J Specific Off-the-Shelf Components)

| Part | Qty | Notes |
|------|-----|-------|
| 6.3 mm female fully-insulated spade terminal (for 18-22 AWG) | 4 | Crimped onto pump motor wires, seated in T1-T4 |
| 4.8 mm female fully-insulated spade terminal (for 18-22 AWG) | 2 | Crimped onto jumper wire, seated in T5 |
| 22 AWG stranded wire | ~30 mm | Cartridge-present jumper loop for T5 |
| 18-22 AWG stranded wire (pump motor leads) | 4x ~350 mm | From motor solder tabs to rear wall terminals. Routed through floor channels. |

Note: The 6.3 mm male blade terminals and 4.8 mm male blade terminals are mounted on the dock, not on the cartridge. They are not part of Sub-J.
