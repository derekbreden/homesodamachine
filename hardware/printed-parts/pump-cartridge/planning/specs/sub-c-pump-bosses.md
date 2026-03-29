# Sub-C: Pump Mounting Bosses — Parts Specification

## Reference Frame

All coordinates are in the tray reference frame:
- Origin: rear-left-bottom corner of tray outer envelope
- X: 0..160 (width, left to right)
- Y: 0..155 (depth, dock/rear to user/front)
- Z: 0..72 (height, bottom to top)
- Floor inner surface: Z = 3.00
- Left wall inner face: X = 5.00
- Right wall inner face: X = 155.00
- Rear wall inner face: Y = 8.50

Material: PETG (per conceptual architecture).

---

## 1. Mechanism Narrative

Sub-C contains no moving parts. It is a set of six static structural features — four mounting bosses and two motor cradles — printed integral with the tray floor (Sub-A). Their sole purpose is to hold two Kamoer KPHM400 peristaltic pumps rigidly in position during operation.

**What the user sees and touches:** Nothing. Sub-C is entirely internal to the cartridge, hidden beneath the lid and behind the front bezel. The user never contacts these features. The only interaction is during pump replacement (Tier 3 service): after removing the lid, the user unscrews 2x M3 SHCS per pump from the boss top faces using a 2.5 mm hex key, lifts the pump out, drops a replacement in, and re-fastens.

**What is stationary:** Everything. The four bosses are fixed columns rising from the tray floor. The two cradles are fixed semicircular ribs rising from the tray floor. The pumps, once fastened, are stationary during all normal operation (dispensing, priming, cleaning).

**How the pumps are held:**

Each pump has a stamped-metal mounting bracket at the junction between the pump head and motor body. The bracket has two ears extending beyond the pump head width, each with a 3.13 mm through-hole (M3 clearance). Two bosses per pump rise from the tray floor to meet these ears. Each boss has an M3 x 5.7 mm brass heat-set insert embedded in its top face. An M3 x 8 mm SHCS passes through the bracket ear and threads into the insert, clamping the bracket ear against the boss top face.

The pump head (62.6 x 62.6 mm cross-section) rests directly on the tray floor at Z = 3.00. The bracket ears are at the pump center axis height, Z = 34.30 (half of 62.6 mm above the floor). Therefore each boss must rise 31.30 mm from the floor to meet the bracket.

Behind each pump head, the DC motor body (~35 mm diameter cylinder) extends rearward. A semicircular cradle at Y = 116.50 supports the motor from below, preventing the cantilevered motor weight from applying a bending moment to the bracket screws. The cradle does not clamp the motor — it is open at the top so the pump can be lifted straight up during service.

**Vibration and load path:** During operation, the peristaltic roller mechanism generates cyclic radial loads. The M3 screw clamping force (bracket ear compressed against boss top face) resists lateral loads through friction. The pump head bottom resting on the floor resists downward loads through direct bearing. The motor cradle resists the motor's gravitational cantilever moment. No adhesive or secondary retention is used.

---

## 2. Constraint Chain Diagram

```
[Pump head bottom face] -> [Floor surface Z=3.00: direct bearing] -> [Tray structure]
  ^ resists: -Z (gravity on pump head)

[Bracket ear] -> [M3 SHCS clamping] -> [Boss top face Z=34.30] -> [Boss column] -> [Floor Z=3.00] -> [Tray structure]
  ^ resists: +X/-X, +Y/-Y (lateral loads via friction under clamp force)
  ^ resists: +Z (tensile via screw)

[Motor body underside] -> [Cradle semicircular surface] -> [Cradle rib] -> [Floor Z=3.00] -> [Tray structure]
  ^ resists: -Z (gravity on cantilevered motor)
  ^ resists: +X/-X (lateral motor movement via arc contact)
```

Every arrow names a force path. Every part lists its constraints. No unlabeled arrows.

---

## 3. Feature Specifications

### 3a. Mounting Bosses (4x)

Each boss is a cylindrical column with triangular reinforcement ribs, rising from the tray floor.

**Positions (center of boss at top face):**

| Boss ID | X (mm) | Y (mm) | Z top face (mm) |
|---------|--------|--------|-----------------|
| P1-L | 18.48 | 83.00 | 34.30 |
| P1-R | 67.93 | 83.00 | 34.30 |
| P2-L | 92.08 | 83.00 | 34.30 |
| P2-R | 141.53 | 83.00 | 34.30 |

**Boss column geometry:**
- Outer diameter: 8.00 mm
- Height above floor: 31.30 mm (from Z = 3.00 to Z = 34.30)
- Base: bonded to floor inner surface at Z = 3.00, printed integral with Sub-A

**Heat-set insert pocket (bored into boss top face):**
- Pilot hole diameter: 4.00 mm
- Pilot hole depth: 7.00 mm (from top face, extending downward into the boss)
- Insert: M3 x 5.7 mm brass heat-set insert (standard knurled OD for PETG, pressed in with soldering iron)
- The 7.00 mm pocket depth provides 1.30 mm of clearance below the 5.7 mm insert, ensuring the insert seats fully without bottoming out

**Reinforcement ribs:**
At 31.30 mm tall with only 8.00 mm OD, each boss is a slender column (aspect ratio 7.8:1). Four triangular gusset ribs per boss provide stiffness and print stability.

- Rib count per boss: 4, arranged at 0/90/180/270 degrees around the boss circumference
- Rib profile: right triangle, 2.00 mm thick (circumferential), extending 4.00 mm radially from the boss outer surface
- Rib height: full boss height, 31.30 mm (floor to top face)
- Rib top: flush with boss top face at Z = 34.30 (does not protrude above the bracket bearing surface)
- Rib bottom: bonded to floor at Z = 3.00

**Rib orientation per boss:**
- The four ribs point along +X, -X, +Y, -Y from each boss center
- This produces a cross-shaped footprint at the floor: 8.00 mm circle with four 4.00 mm radial fins
- Total footprint per boss: 16.00 mm diameter bounding circle (8.00 + 2x4.00)

**Rib clearance check:**
- Adjacent boss pair closest approach (P1-R to P2-L): 92.08 - 67.93 = 24.15 mm center-to-center. With ribs extending 4.00 mm from each boss surface: rib tip at 67.93 + 4.00 + 4.00 = 75.93 (P1-R, +X rib) and 92.08 - 4.00 - 4.00 = 84.08 (P2-L, -X rib). Gap between rib tips: 84.08 - 75.93 = 8.15 mm. Clear.
- Boss to wall closest approach (P1-L -X rib tip): 18.48 - 4.00 - 4.00 = 10.48. Left wall at X = 5.00. Gap: 10.48 - 5.00 = 5.48 mm. Clear.
- Boss to wall closest approach (P2-R +X rib tip): 141.53 + 4.00 + 4.00 = 149.53. Right wall at X = 155.00. Gap: 155.00 - 149.53 = 5.47 mm. Clear.

**Boss top face (bracket bearing surface):**
- Flat annular ring: 8.00 mm OD, 4.00 mm ID (pilot hole)
- Surface area per boss: pi/4 * (8.00^2 - 4.00^2) = 37.7 mm^2
- This surface bears the clamping load from the M3 SHCS head (5.5 mm diameter) through the bracket ear

**Fastener specification:**
- Screw: M3 x 8 mm Socket Head Cap Screw (SHCS), stainless steel
- Screw head diameter: 5.50 mm, head height: 3.00 mm
- Thread engagement into insert: ~5.0 mm (8.0 mm screw length minus ~1.5 mm bracket thickness minus ~1.5 mm head seating)
- Tool: 2.5 mm hex key

### 3b. Motor Cradles (2x)

Each cradle is a semicircular rib rising from the tray floor, cradling the motor body from below.

**Positions (cradle center):**

| Cradle | Center X (mm) | Y midplane (mm) | Arc center Z (mm) |
|--------|--------------|-----------------|-------------------|
| Cradle 1 (Pump 1) | 43.20 | 116.50 | 34.30 |
| Cradle 2 (Pump 2) | 116.80 | 116.50 | 34.30 |

**Cradle cross-section (XZ plane at Y = 116.50):**
- Inner radius: 17.75 mm (35.50 mm ID, providing 0.25 mm diametral clearance on ~35 mm motor body)
- Wall thickness: 3.00 mm
- Outer radius: 20.75 mm
- Arc: 180 degrees, bottom half (from 9 o'clock to 3 o'clock, open at top)
- Arc lowest inner point: Z = 34.30 - 17.75 = 16.55
- Arc highest inner point (arm tips): Z = 34.30 + 17.75 = 52.05
- Arc highest outer point (arm tips): Z = 34.30 + 20.75 = 55.05

**Support rib below arc:**
- From Z = 3.00 (floor) to Z = 16.55 (bottom of arc), a solid rectangular rib fills the space below the semicircle
- Rib width: matches cradle outer diameter = 41.50 mm (2 x 20.75)
- Rib height: 16.55 - 3.00 = 13.55 mm

**Cradle depth (Y extent):**
- 15.00 mm, centered at Y = 116.50
- Y range: 109.00 to 124.00

**Cradle X extents:**

| Cradle | X min (outer) | X max (outer) |
|--------|--------------|--------------|
| Cradle 1 | 22.45 | 63.95 |
| Cradle 2 | 96.05 | 137.55 |

**Clearances:**
- Cradle 1 left edge to left wall: 22.45 - 5.00 = 17.45 mm
- Cradle 2 right edge to right wall: 155.00 - 137.55 = 17.45 mm
- Inter-cradle gap: 96.05 - 63.95 = 32.10 mm
- Cradle arm tips at Z = 55.05, pump head top at Z = 65.60: 10.55 mm below pump head top. The cradle arms do not interfere with the pump head volume because the cradle is at Y = 116.50 (motor zone) while the pump head ends at approximately Y = 83 (bracket plane).

**Motor retention:** The cradle does not clamp the motor. It is open at the top. The motor rests in the cradle under gravity. The M3 bracket screws at Y = 83.00 are the primary retention. The cradle prevents the motor from sagging downward or shifting laterally, but the pump can be lifted straight up (+Z) during service without removing the cradle.

---

## 4. Interface Specifications

### 4a. Bosses to Floor (Sub-A)

Each boss base circle (8.00 mm OD) plus four ribs (16.00 mm bounding circle) bonds to the interior floor surface at Z = 3.00. Printed as a single continuous extrusion — no separate attachment. The boss and rib geometry is part of the tray solid.

### 4b. Cradles to Floor (Sub-A)

Each cradle base rib bonds to the floor at Z = 3.00 across a 41.50 x 15.00 mm rectangular footprint. Printed integral with the tray.

### 4c. Bosses to Pump Bracket (off-the-shelf)

| Parameter | Boss (Sub-C) | Bracket (Kamoer) | Clearance / Fit |
|-----------|-------------|-------------------|----------------|
| Hole center spacing | 49.45 mm (P1-L to P1-R, P2-L to P2-R) | 49.45 mm (caliper-verified) | Matched |
| Boss top face Z | 34.30 mm | Bracket ear at pump center axis | Matched (pump head bottom at Z=3.00, center at Z=34.30) |
| Pilot hole diameter | 4.00 mm | N/A (insert receives M3 screw) | N/A |
| Screw through-hole (bracket) | N/A | 3.13 mm (caliper-verified) | M3 screw (3.00 mm) passes through 3.13 mm hole: 0.13 mm clearance |
| Insert OD | ~4.0 mm knurled (press into 4.0 mm pilot) | N/A | Interference press-fit (heat-set) |
| Boss OD vs bracket ear width | 8.00 mm | Ear ~3 mm overhang per side from pump head (bracket total 68.6 mm, head 62.6 mm, so ear width ~3 mm per side, hole centered on ear) | Boss OD (8.00 mm) exceeds ear width (~6 mm per ear from head edge to bracket edge). The boss supports beyond the bracket ear footprint — this is acceptable as the bracket simply rests on the boss face. |

### 4d. Cradles to Motor Body (off-the-shelf)

| Parameter | Cradle (Sub-C) | Motor (Kamoer) | Clearance |
|-----------|---------------|----------------|-----------|
| Cradle ID | 35.50 mm | ~35 mm OD (LOW confidence, photos 15/16) | ~0.50 mm diametral (0.25 mm per side) |
| Arc center Z | 34.30 mm | Motor coaxial with pump center axis at Z = 34.30 | Matched |
| Arc center X | 43.20 / 116.80 | Pump centerlines | Matched |

**DESIGN GAP: Motor body diameter is LOW confidence (~34.54 to ~35.13 mm from caliper photos). The 35.50 mm cradle ID provides 0.25-0.48 mm clearance per side across the measurement range. If the motor is actually larger than 35.0 mm, clearance drops below 0.25 mm per side. Caliper re-verification of motor diameter is needed before final print.**

### 4e. Sub-C to Sub-F (tube routing channels)

Tube barb exits at approximately Y = 35.00, near pump centerlines X = 43.20 and 116.80. Tube routing channels (Sub-F) must route around boss positions at Y = 83.00. The boss footprints (16.00 mm bounding circles centered at the four boss X positions) constrain the lateral routing of tube channels through the bracket plane zone. Specific routing is Sub-F's responsibility.

---

## 5. Assembly Sequence

1. **Install heat-set inserts:** Press four M3 x 5.7 mm brass heat-set inserts into the four boss pilot holes using a soldering iron with a tapered tip. Insert seats flush with or 0.5 mm below the boss top face. This is done once during cartridge manufacturing, before any pumps are installed.

2. **Place Pump 1:** Lower Pump 1 into the tray from above (+Z direction), pump head first, with tube barbs facing toward the rear wall (-Y). The pump head bottom rests on the floor at Z = 3.00. Align bracket ear holes over bosses P1-L and P1-R. The motor slides into Cradle 1.

3. **Fasten Pump 1:** Insert two M3 x 8 mm SHCS through the bracket ears into bosses P1-L and P1-R. Tighten with 2.5 mm hex key. Access from above is unobstructed (no lid yet).

4. **Place Pump 2:** Same procedure, into bosses P2-L/P2-R and Cradle 2.

5. **Fasten Pump 2:** Same as step 3.

6. **Route tubes, install lid, bezel** (subsequent sub-components, not Sub-C scope).

**Disassembly (pump replacement):**
1. Remove front bezel (snap-fit, tool-free).
2. Remove lid (snap-fit, tool-free).
3. Unscrew two M3 SHCS from the target pump's bosses (2.5 mm hex key).
4. Lift pump straight up out of the tray. Motor clears the cradle (open top). Pump head clears the boss tops (boss OD 8.00 mm is smaller than pump head 62.6 mm).
5. Drop replacement pump in, reverse steps 3-1.

---

## 6. Print Orientation and Manufacturing Notes

Sub-C features are printed integral with the tray. The tray prints with the open top facing up (Z axis = print Z axis). All Sub-C features are extrusions along the print Z axis:

- **Bosses:** Cylindrical columns extruding upward from the floor. No overhangs. No supports needed.
- **Reinforcement ribs:** Vertical fins. No overhangs. No supports needed.
- **Cradle support ribs:** Solid rectangular blocks extruding upward from floor. No overhangs.
- **Cradle semicircular arcs:** The inner surface of the semicircle is a 180-degree overhang from Z = 16.55 to Z = 52.05. The lowest point of the arc (Z = 16.55) transitions from vertical walls to the curved underside. Overhangs beyond 45 degrees begin at approximately Z = 19.2 (where the arc tangent exceeds 45 degrees from vertical). **Supports are needed on the underside of the cradle arc from approximately Z = 19.2 to the midpoint at Z = 34.30.** The 3.00 mm wall thickness is sufficient to bridge the supported region. Alternatively, the cradle can be redesigned with a V-shaped or trapezoidal profile instead of a semicircle to eliminate supports entirely — this is a manufacturing tradeoff, not a functional requirement.

**Layer height:** Standard 0.2 mm layers are adequate for all Sub-C features. The boss pilot holes (4.00 mm diameter) achieve sufficient circularity at 0.2 mm layers for heat-set insert installation.

---

## 7. Design Gaps

1. **Motor diameter uncertainty:** The cradle ID of 35.50 mm is based on LOW confidence caliper readings (~35 mm). If the actual motor diameter exceeds 35.00 mm, clearance is tighter than intended. **Action: re-verify motor body diameter with calipers before final print.**

2. **Bracket ear thickness:** Estimated at ~1.5 mm based on photos. This affects screw engagement calculation (8.0 mm screw length minus bracket thickness minus head seating = thread engagement in insert). If bracket is thicker than 2.0 mm, the M3 x 8 mm SHCS may not provide adequate thread engagement. **Action: measure bracket ear thickness with calipers.**

3. **Cradle arc overhang:** The semicircular cradle profile requires support material on its underside during printing. If support removal is difficult inside the tray (limited access at Y = 116.50), consider a V-cradle or trapezoidal profile that stays within 45-degree overhang limits. Functional requirement (support motor from below) is met by either profile.

4. **Motor flat:** The motor body has a flat on one side (anti-rotation feature). The semicircular cradle ignores this flat — the cradle is a simple half-pipe. If the flat faces downward, there will be a small gap between the motor and cradle at the flat. This does not affect function (the cradle is a gravity rest, not a clamp) but could allow slight lateral play. **Not critical — the bracket screws are the primary retention.**
