# Pump Mounting Research — Kamoer KPHM400 in 3D Printed Cartridge

## 1. Pump Physical Geometry and Mounting Constraints

### Caliper-Verified Dimensions (from `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`)

| Dimension | Value | Confidence |
|-----------|-------|------------|
| Pump head cross-section | 62.6 x 62.6 mm (nearly square, rounded corners) | HIGH |
| Pump head depth | ~48 mm | HIGH |
| Bracket width (with ears) | ~68.6 mm | HIGH (matches datasheet) |
| Mounting hole diameter | 3.13 mm (M3 clearance) | HIGH |
| Mounting hole center-to-center (X axis) | 49.45 mm | HIGH |
| Motor body diameter | ~35 mm | LOW (needs verification) |
| Total length (with motor nub) | 116.48 mm | HIGH |
| Total length (without motor nub) | 111.43 mm | HIGH |
| Motor shaft nub protrusion | ~5 mm | HIGH |
| Tube connector protrusion from front face | 30-50 mm | MEDIUM |
| Tube connector height span | 82.82 mm total with connectors | MEDIUM |
| Datasheet overall | 68.6W x 115.6D x 62.7H mm | REFERENCE |

### Mounting Bracket Pattern

The bracket is a stamped metal plate sandwiched between the pump head and motor. It extends ~3 mm beyond the pump head on each side to form mounting ears.

**Known:** 2 holes on the X axis, 49.45 mm center-to-center. Each hole is 3.13 mm diameter (accepts M3 screws).

**Unknown:** Whether the bracket has a 1x2 pattern (1 hole per ear, 2 total) or 2x2 pattern (2 holes per ear, 4 total). The caliper photos only measured one axis. The physical part must be inspected to confirm.

**Design implication:** If 1x2 pattern, the pump can rotate around the screw axis unless the bracket is clamped against a flat surface. If 2x2, the screws alone prevent rotation. Design should assume 1x2 (worst case) and provide anti-rotation via bracket clamping.

### Clearance Zones

```
SIDE VIEW (Y axis = depth):

Tube stubs     Pump head        Bracket   Motor body        Nub
  30-50mm    |<-- ~48mm -->|  |<~4mm>| |<--- ~63mm --->|  |5mm|
  =========  |████████████████|========|  ●●●●●●●●●●●●●●  |-|
             |████████████████|========|  ●●●●●●●●●●●●●●  |-|
  =========  |████████████████|========|  ●●●●●●●●●●●●●●  |-|
             |                          |                   |
             Y=0                     Y≈48              Y≈116

TOP VIEW (showing bracket ears):

             |<---------- 68.6mm ---------->|
             |   |<-- 62.6mm -->|           |
             ○   |██████████████|           ○   ← M3 holes
             |   |██████████████|           |
             |<->|              |<->|
             ~3mm               ~3mm
             ◄── 49.45mm c-c ──►
```

### Two Pumps Side by Side

With pump heads at 62.6 mm wide each and brackets at 68.6 mm, placing two pumps side by side requires:

| Arrangement | Width | Notes |
|-------------|-------|-------|
| Bracket-to-bracket touching | 137.2 mm | No gap, no clearance for tools |
| 3 mm gap between brackets | 140.2 mm | Minimal tool access |
| 5 mm gap between brackets | 142.2 mm | Reasonable tool access for M3 screws |

The 220 mm enclosure width (from vision.md) provides ample room for two pumps plus walls and tube routing.

### Depth Budget

From front face to motor nub tip: 116.5 mm. Plus tube stubs in front: ~40 mm typical. Total depth footprint per pump: ~157 mm. The enclosure is 300 mm deep; the cartridge occupies roughly half.

---

## 2. Mounting Strategies for Cylindrical Motors in FDM PETG

### Strategy A: Bracket-Only Mounting (Recommended Primary)

The Kamoer KPHM400 already has a stamped metal bracket with M3 holes. This is the factory-intended mounting method.

**Implementation:**
- Print a flat mounting plate (the "pump tray floor") with bosses for M3 heat-set inserts at 49.45 mm spacing
- Pump bracket sits flat on the tray floor
- M3 x 8 mm socket head cap screws thread into heat-set inserts from above through the bracket holes
- Motor body hangs freely below (if horizontal) or behind (if vertical)

**Pros:**
- Uses the manufacturer's mounting interface
- Metal bracket distributes load
- Heat-set inserts provide strong, repeatable M3 threads in PETG (pull-out resistance 200-400 N)
- Simple geometry, easy to print flat

**Cons:**
- If bracket is 1x2 pattern, needs anti-rotation feature
- Motor body unsupported (may matter for vibration)

### Strategy B: Bracket Mounting + Motor Cradle (Recommended)

Combine Strategy A with a semicircular cradle for the motor body.

**Implementation:**
- Same bracket-to-tray-floor mounting as Strategy A
- Add a 180-degree cradle (half-pipe) for the ~35 mm motor body, printed into the tray floor or as a rib rising from it
- Cradle provides lateral support and prevents rotation even with 1x2 bracket
- 0.3-0.5 mm clearance on motor diameter (design for 35.5 mm ID cradle)
- Cradle does NOT need to clamp — gravity and bracket screws hold the pump; cradle just prevents lateral movement

**Pros:**
- Fully constrained in all 6 DOF
- Motor body supported against vibration
- No additional fasteners needed beyond the bracket screws
- Cradle is simple to print (half-pipe with walls)

**Cons:**
- Requires known motor diameter (currently LOW confidence at ~35 mm)
- Must confirm motor flat orientation (anti-rotation flat on motor body)

### Strategy C: Full Clamp (Over-Engineered)

Two-piece clamp around motor body with cap screws.

**Not recommended:** Adds complexity, more fasteners, and more print time for minimal benefit when the factory bracket already provides the primary mounting.

### Strategy D: Interference/Snap-Fit Pocket

Print a tight pocket that the pump head press-fits into.

**Not recommended:** PETG creeps under sustained load, tolerances are tight for FDM (0.1-0.2 mm achievable), and removal for replacement would be difficult. Also prevents using the factory bracket holes.

### Heat-Set Insert Specifications for PETG

| Parameter | Value |
|-----------|-------|
| Insert type | M3 x 5.7 mm brass, knurled OD |
| Pilot hole diameter | 4.0 mm |
| Installation temperature | ~245 C (soldering iron) |
| Minimum wall around insert | 2.0 mm (4.0 + 2x2.0 = 8.0 mm boss OD) |
| Pull-out resistance (PETG) | 200-400 N typical |
| Torque resistance | 1.5-3.0 Nm typical |

**Recommended source:** Prusa M3 heat-set inserts (100 pcs) or CNC Kitchen recommended inserts from Amazon.

---

## 3. Vibration Isolation

### Peristaltic Pump Vibration Characteristics

The Kamoer KPHM400 is a 3-roller peristaltic pump. The rollers compress tubing against the pump housing in sequence, creating pulsating flow. This produces two types of vibration:

1. **Flow pulsation** — pressure waves in the fluid line (3 pulses per revolution)
2. **Mechanical vibration** — reaction forces transmitted through the pump body to the mount

### Is Vibration Damping Needed?

**For flow pulsation:** The BPT tubing inside the pump head and the silicone tubing downstream act as natural dampers. The soft tubing absorbs pulsation. At the flow rates involved (400-500 ml/min max, but actual flavoring delivery is much lower), pulsation is not a functional concern for dispensing into a cup. No pulsation dampener is needed.

**For mechanical vibration:** The Kamoer KPHM400 is a small, low-power pump (10W, 12V). The mechanical vibration is modest. For context:

- The pump weighs 240-306 g depending on motor variant
- Operating noise is less than or equal to 65 dB (manufacturer spec)
- The cartridge is enclosed inside a kitchen appliance with walls on all sides
- The pump runs for seconds at a time during a pour, not continuously

**Assessment: No dedicated vibration isolation is needed.** The combination of:
- PETG's inherent slight flexibility (more compliant than PLA/ABS)
- The BPT tubing's compliance
- Short duty cycles
- Enclosure sound deadening

...makes the vibration acceptable without rubber grommets, damper pads, or isolator mounts.

### If Vibration Becomes a Problem Later

Options in order of simplicity:
1. Add 1-2 mm silicone sheet between bracket and tray floor (trivial retrofit)
2. Use rubber grommets on the M3 mounting screws
3. Add adhesive-backed foam pads to the motor cradle

These are all field-retrofittable without redesigning the cartridge.

---

## 4. Electrical Connections

The cartridge needs 2 DC motor connections (12V, ~1A each). The connections must survive repeated insertion/removal (target: 500+ cycles over product lifetime).

### Option A: Blade/Spade Connectors (Recommended)

Standard 6.3 mm (1/4 inch) blade terminals, the same type used in automotive and appliance wiring.

**Implementation:**
- Male blade tabs mounted on the dock (fixed side), wired to motor drivers
- Female spade terminals on the cartridge pump wires
- 2 blades per pump (+ and -), 4 total
- Blades oriented parallel to insertion direction so they engage during cartridge insertion

**Pros:**
- Extremely proven technology (billions in service)
- Rated for 10-15A at 12V (far exceeds ~1A pump draw)
- Self-wiping contacts (wipe clean on every insertion)
- Cycle life: 10,000+ insertion/removal cycles typical
- Cheap: less than $0.10 per terminal
- Available with locking tabs for secure connection
- Tolerant of slight misalignment (blade guides itself into spade)
- Available at Home Depot, Amazon, any auto parts store

**Cons:**
- Requires ~5 mm of insertion travel for full engagement
- Exposed metal contacts (moisture concern mitigated by indoor kitchen use)
- Polarity must be enforced by mechanical keying (asymmetric blade spacing or housing)

**Specific parts:**
- Male: 6.3 mm blade terminal, solder or crimp
- Female: 6.3 mm fully insulated female spade terminal (flag or inline)
- Housing: Molex-style 2-pin blade connector housing (optional but recommended for polarity)

### Option B: Pogo Pins

Spring-loaded pins on the dock, flat contact pads on the cartridge.

**Pros:**
- True blind-mate capability
- Zero insertion force
- 20,000+ cycle life
- Compact footprint

**Cons:**
- Expensive ($2-5 per pin, $8-20 for a 4-pin assembly)
- Spring pins can stick or corrode in humid kitchen environment
- Need flat, clean contact pads (PCB or plated surface on cartridge)
- Current rating per pin typically 1-3A — adequate but less margin
- More complex to integrate (requires precise alignment)

### Option C: Anderson Powerpole Connectors

Genderless DC power connectors used in ham radio and robotics.

**Pros:**
- Genderless (same connector on both sides)
- 15-45A rating
- Color-coded for polarity
- Snap together, pull apart

**Cons:**
- Bulky (each housing is ~16 x 8 x 16 mm)
- Not designed for blind mating
- Require manual alignment during cartridge insertion

### Recommendation: Blade Connectors (Option A)

Blade connectors are the clear winner for this application. They are cheap, proven, high-cycle, self-wiping, and naturally engage during a linear cartridge insertion. The 6.3 mm width provides easy alignment, and a keyed housing prevents reverse polarity.

**Polarity enforcement:** Use a 2x2 blade housing with asymmetric pin spacing, or simply use different-width blades (6.3 mm for positive, 4.8 mm for negative). The cartridge physically cannot be inserted with reversed polarity.

**Moisture:** Indoor kitchen environment, cartridge is inside an enclosed appliance. Not a concern. If needed later, gold-plated blade terminals are available.

### Continuity Detection

Per the cartridge state detection design (from memory), one additional contact pair can serve as a "cartridge present" signal — a simple continuity loop. This can be a 3rd blade pair or a microswitch actuated by cartridge insertion.

---

## 5. Tube Routing

### Minimum Bend Radius for 1/4 inch Silicone Tubing

The general rule for silicone tubing bend radius is 3-4x the outer diameter.

| Tubing | ID | OD | Min Bend Radius |
|--------|----|----|-----------------|
| 1/4" silicone (typical) | 6.35 mm (1/4") | 9.5 mm (3/8") | 28-38 mm (1.1-1.5") |
| Kamoer BPT tubing | 4.8 mm | 8.0 mm | 24-32 mm |

**Practical minimum:** 25 mm (1 inch) radius for 1/4" silicone tubing without kinking. This is conservative; softer durometer silicone can go tighter. But designing for 25 mm minimum avoids any risk of flow restriction.

### Routing Within the Cartridge

Each pump has 2 barbed tube connectors (inlet and outlet) protruding from the front face. These need to connect to 4 John Guest quick-connect fittings at the rear of the cartridge (the dock interface).

**Route:** Pump barbs (front) --> silicone tubing --> 180-degree turn --> John Guest fittings (rear)

```
TOP VIEW OF CARTRIDGE:

  FRONT (user-facing)                              REAR (dock interface)
  ┌─────────────────────────────────────────────────────┐
  │  ╔═══╗        ╔═══╗                                 │
  │  ║ P1 ║        ║ P2 ║     ← pump heads              │
  │  ╚═══╝        ╚═══╝                                 │
  │    │├──out──────────────────────────────────►JG1     │
  │    │└──in───────────────────────────────────►JG2     │
  │              │├──out────────────────────────►JG3     │
  │              │└──in─────────────────────────►JG4     │
  └─────────────────────────────────────────────────────┘
```

**Key constraints:**
- Tube stubs protrude ~30-50 mm from pump face; tubing pushes onto barbs
- 180-degree reversal from front-facing barbs to rear-facing John Guest fittings
- Each 180-degree turn needs ~50 mm depth (25 mm radius x 2)
- 4 tubes must not cross or interfere
- Tubes must be secured (printed clips or channels) to prevent shifting during cartridge handling

### Tube Retention

Printed channel guides molded into the cartridge tray floor and walls:
- Open-top channels (U-shaped, 10 mm wide x 10 mm deep for 1/4" OD tubing with silicone)
- Snap-over clips at 30-50 mm intervals to hold tubing in channels
- Channels route tubes along the cartridge walls, keeping the center clear

### John Guest Fitting Mounting

The 4 John Guest fittings at the rear of the cartridge are the fluid interface to the dock. They must be rigidly mounted and precisely positioned to align with the 4 tube stubs in the dock.

**Approach:** Print a fitting plate at the rear of the cartridge with 4 holes sized for John Guest collet bodies. Collets can be pressed into the printed holes with an interference fit, or retained with printed snap features.

---

## 6. Failure Modes and Concerns

| Concern | Risk | Mitigation |
|---------|------|------------|
| Motor diameter uncertainty (~35 mm, LOW confidence) | Cradle too tight or too loose | Measure motor with calipers before finalizing cradle ID. Design cradle with 0.5 mm clearance. |
| Bracket hole pattern unknown (1x2 vs 2x2) | If 1x2, pump can rotate on screws | Cradle provides anti-rotation regardless. Inspect bracket before CAD. |
| Heat-set insert pull-out during cartridge removal | User yanks cartridge, screws resist | Not a concern — screws hold pump to tray, tray travels with cartridge. No pull-out force on inserts during normal use. |
| Blade connector misalignment | Blades miss spades during insertion | Guide rails on cartridge/dock ensure alignment within 2 mm; blade width (6.3 mm) tolerates this. |
| Tube kinking during cartridge insertion/removal | Crimped tube restricts flow | Route tubes along walls, secure with clips, use 25 mm minimum bend radius everywhere. |
| PETG creep under sustained pump weight | Cradle/mount deforms over months | Pump weighs 240-306 g; PETG creep at this load is negligible. Not a concern. |
| Pump vibration loosening M3 screws | Screws back out over time | Use M3 nyloc nuts or thread-locking compound (blue Loctite 242). Or rely on heat-set insert friction. |

---

## 7. Summary of Recommendations

1. **Mounting method:** Bracket-to-tray-floor with M3 heat-set inserts (Strategy B: bracket + motor cradle)
2. **Vibration isolation:** Not needed. Retrofit with silicone sheet if it becomes a problem.
3. **Electrical connections:** 6.3 mm blade/spade connectors, 4 total (2 per pump), keyed housing for polarity
4. **Tube routing:** 25 mm minimum bend radius, printed channel guides, snap clips for retention
5. **Before CAD:** Must verify motor body diameter (calipers) and bracket hole count (visual inspection of bracket)

## 8. Open Questions Requiring Physical Verification

1. Is the mounting bracket 1x2 or 2x2 hole pattern?
2. Exact motor body diameter (current data is ~35 mm with LOW confidence)
3. Exact tube connector exit positions on the pump front face (X/Z offsets from center)
4. Can the bracket be separated from the pump head for measurement?
5. Motor flat orientation relative to bracket ears
