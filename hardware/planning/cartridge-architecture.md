# Pump Cartridge Architecture

The pump cartridge is the only user-replaceable module in the system. It contains exactly two Kamoer KPHM400 peristaltic pumps -- one per flavor line -- and nothing else. No valves, no motor drivers, no active electronics. The cartridge is a box with two pumps, four fluid ports, and a few passive electrical contact pads. All 10 solenoid valves and both L298N motor drivers live in the main enclosure body. Only 12V motor power crosses the cartridge interface via pogo pins.

---

## 1. Envelope and Pump Layout

| Parameter | Value |
|-----------|-------|
| Envelope | **148W x 130D x 80H mm** |
| Pump count | 2 |
| Pump model | Kamoer KPHM400-SW3B25 (12V DC brushed, 400ml/min) |
| Single pump dimensions | 68.6W x 116.48D x 62.6H mm (caliper-verified; 111.43mm without motor nub) |
| Combined pump width (side-by-side) | ~137.2mm |
| Cartridge mass (estimated) | ~820g (2x 306g pumps + shell) |
| Replacement interval | 18-36 months (pump tube wear) |

The two pumps sit side-by-side with motors facing the same direction (toward the rear). This is the simplest arrangement: symmetric tube routing, both pump heads face forward, electrical leads exit from the same side. The 148mm width accommodates 137.2mm of pumps with ~5.5mm margin per side for shell walls and clearance. The 130mm depth fits the 116.48mm motor axis (caliper-verified, including motor nub) plus mounting hardware and connector protrusion. The 80mm height clears the 62.6mm pumps with room for tubing routing above.

The envelope is constrained by the pumps, not by the available void. The triangular space below the diagonal bags is far larger than needed.

```
TOP VIEW (cartridge, lid removed)

    148mm
  <-------->
  +------------------------------------------+  ---
  |                                          |   ^
  |  +-------------+  +-------------+       |   |
  |  |   PUMP 1    |  |   PUMP 2    |       |   |
  |  |   motor ->  |  |   motor ->  |       |  130mm
  |  | <- tubes    |  | <- tubes    |       |   |
  |  +-------------+  +-------------+       |   |
  |       |                  |               |   |
  |    [tube routing to rear fluid ports]    |   v
  +------------------------------------------+  ---
       FRONT                           REAR
  (pull handle)                  (fluid connections)
```

---

## 2. Dock Position

The cartridge dock occupies the front-bottom of the enclosure, in the triangular void below the diagonal bag slab. The bags run from the top-front (sealed end pinned to back wall near Z=392) to the bottom-back (cap/connector end near the floor). This creates a large trapezoidal region at the front-bottom with over 290mm of height at the front wall and 130mm+ at mid-depth -- far more than the 80mm cartridge needs.

```
SIDE CROSS-SECTION (height vs. depth)

Z(mm)
392 +---------------------------------------------+
    |                          [sealed end pinned] |
    |   [HOPPER]                to back wall       |
    |   [ELECTRONICS]     \\\\\\\\\\\\\\\\\\\\\\\\ |
    |                 \\\\\\\\\\\\\\\\\\\\\\\\\\\\ |
    |            \\\\\\\\ bag slab (2x 2L) \\\\\\\ |
    |         \\\\\\\\ 35 deg diagonal  \\\\\\\\\\ |
    |      \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ |
125 |  cap end \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  |
    |                                              |
 84 |  +----------+ +--------+                     |
    |  |CARTRIDGE | | VALVES |===tubes to bags====>|
    |  |148x130x80| | 2x5    |                     |
    |  +----------+ +--------+      [BACK PANEL]   |
  0 +---------------------------------------------+
    0 (front)      165  240              292 (back)
```

The cartridge slides in along the cabinet floor through a slot at the bottom of the front panel (0-84mm height range). The user crouches, rests the cartridge on the cabinet floor, and pushes it straight in. Gravity assists seating. The valve rack sits directly behind the cartridge dock, using the depth dimension (Y=165-240).

See `research/dock-placement.md` for the full triangle geometry analysis, ergonomic assessment, and tube routing paths.

---

## 3. Fluid Connections — John Guest Push-to-Connect

Four JG PP0408W 1/4" push-to-connect union fittings mount in the cartridge rear wall in a 2x2 grid (40mm horizontal x 28mm vertical center-to-center). The dock carries four bare 1/4" OD hard nylon tube stubs (~30mm protrusion) that the cartridge slides onto during insertion. Collets grip automatically on insertion -- no user action needed to connect. The cartridge is the fitting-bearing side; the dock is passive.

Each fitting has a barbell profile (caliper-verified): 15.10mm OD body ends flanking a 9.31mm OD center body (12.16mm long). The center body press-fits into 9.8mm rear wall pockets; the body ends (15.10mm OD, 12.08mm long each) protrude on both sides of the 4mm rear wall. The collet (release sleeve) at each end is 9.57mm OD, 6.69mm ID, with ~1.3mm axial travel per side.

### Twist-Release Mechanism

A twist-release mechanism on the cartridge provides one-motion disconnect of all four fluid lines. The mechanism consists of two printed PETG parts plus two metal compression springs:

| Part | Description |
|------|-------------|
| Release plate (with integral strut + guide pins) | Single PETG piece: 59x47x6mm plate with 4 stepped bores, 12mm-dia Tr12x3 2-start threaded strut (~130mm), 2x 6mm guide pins (15mm) |
| Wing knob | PETG, 40mm body dia, 45mm wingspan, 25mm deep, internal female Tr12x3 2-start thread (20mm engagement) |
| Compression springs (x2) | ~8-9mm OD, 6.5mm ID, 12mm free length, ~0.5 N/mm, stainless steel, on guide pins |

**How it works:** The wing knob sits on the exterior of the front wall (Y=0). Its flat rear annular face (40mm OD x 12.5mm ID) bears against the front wall exterior face, preventing +Y translation. A Tr12x3 2-start trapezoidal threaded strut (12.0mm major diameter, 6.0mm lead) passes through the cartridge interior from the knob to the release plate on the dock side of the rear wall (Y > 130). The strut is integral to the release plate -- one continuous printed PETG piece. Two guide pins (also integral to the plate, 6.0mm dia, 15mm long) slide in 6.5mm bushings in the rear wall (0.25mm radial clearance), preventing rotation and ensuring parallel plate travel. Two compression springs on the guide pins push the plate away from the rear wall.

**Operating state (default, knob loose):** The springs hold the release plate in the retracted position, 3mm from the rear wall dock face. The plate's stepped bores (15.30mm outer bore / 9.70mm inner lip / 6.50mm tube clearance hole) clear the JG body ends and collets. Collets grip the dock tube stubs via their internal spring-steel teeth. The self-locking thread (lead angle 10.3 deg < friction angle 16.7 deg at mu=0.3 for PETG-on-PETG; pitch diameter 10.5mm) prevents the springs (max 4N total) from back-driving the knob.

**Release (for removal):** The user twists the wing knob clockwise (from front) 180 degrees. The 6.0mm thread lead converts 180 degrees to 3.0mm of strut translation toward the front wall (-Y). From the dock side, the plate advances toward the rear wall. The stepped bores slide over all four JG body ends (15.10mm into 15.30mm outer bore, 0.10mm radial clearance) and the inner lips (9.70mm bore, 0.065mm radial clearance to 9.57mm collet OD) push the collets inward ~1.3mm, releasing all four tubes. The user then pulls the cartridge out by the knob wings.

**Constraint chain:**

```
[User hand: twist torque on wing knob, ~22.5mm moment arm]
    | Tr12x3 2-start thread (6.0mm lead, 180 deg -> 3.0mm travel)
    | mechanical advantage: 2*pi*22.5 / 6.0 = 23.6:1
    v
[Wing knob: ROTATES about Y, constrained axially by front wall face (+Y) and thread (-Y)]
    | thread engagement (20mm length, 12.0mm major dia, 0.3mm radial clearance)
    v
[Strut + plate: TRANSLATES along Y, constrained rotationally by 2x 6mm pins in 6.5mm bushings]
    | 4x stepped bores contact collet end faces
    v
[Collets pushed inward ~1.3mm -> tubes release]

Return: 2x compression springs (0.5 N/mm each, 1-4N total over 3mm stroke)
Self-locking: lead angle 10.3 deg < friction angle 16.7 deg (mu=0.3)
```

**Known design gaps (see parts.md files for full details):**
- **No rotation limit:** Nothing currently stops the knob from rotating past 180 degrees. A stop pin on the knob rear face riding in a 180-degree arc slot on the front wall face is needed.
- **No tactile detent:** The user has no click or snap at the locked/unlocked positions. A detent mechanism at the arc slot endpoints is needed for dark-cabinet usability.
- **No assembly orientation keying:** The 2-start thread allows two assembly orientations (0 and 180 degrees). If rotation stops are added, the knob must be installed in the correct orientation.

| Aspect | Detail |
|--------|--------|
| Fittings | 4x JG PP0408W 1/4" push-to-connect unions (barbell profile: 15.10mm body ends, 9.31mm center body), cartridge-mounted |
| Fitting grid | 2x2, 40mm horizontal x 28mm vertical center-to-center |
| Release mechanism | 12mm PETG threaded strut (Tr12x3 2-start, 6.0mm lead, integral to release plate) + wing knob + 2x return springs on guide pins |
| Connect UX | Slide cartridge in -- JG collets grip dock tube stubs automatically. No knob action needed. |
| Disconnect UX | Twist knob CW 180 deg to release collets, pull cartridge out by knob wings. **DESIGN GAP: no tactile endpoint at 180 deg yet.** |
| Retention | JG collets provide ~20N grip (4 fittings x ~5N each). Self-locking thread (lead angle 10.3 deg < friction angle 16.7 deg) prevents accidental release. |
| Food safety | NSF 61 (potable water). PETG base resin is FDA-listed; stainless nozzle recommended for food-contact parts. |

**Why drips are not a concern:** The firmware enforces a mandatory clean cycle before the cartridge can be unlocked. After the clean cycle, the fluid lines contain only water or air -- no flavor concentrate remains in the cartridge or dock fittings. A few drops of water on the enclosure floor during a swap is inconsequential.

Research: `research/collet-release.md`, `research/release-plate.md`, `research/release-mechanism-alternatives.md`. Twist-release design: `../printed-parts/cartridge-twist-release/planning/research/decision.md`, `../printed-parts/cartridge-twist-release/planning/research/3d-printed-approach.md`

---

## 4. Electrical Interface

Pogo pins on the dock ceiling press onto flat pads on the cartridge top face. This separation from the fluid connections (rear face) is the primary moisture defense: water drips downward, away from the ceiling-mounted pins.

| Parameter | Value |
|-----------|-------|
| Minimum contacts | 3 (GND, Motor A 12V, Motor B 12V) |
| Optional contacts | Cartridge ID (resistor divider), temp sensor (thermistor) -- up to 6 total |
| Pad size | 8mm x 5mm each, 10mm center-to-center |
| Pad material | Nickel-plated brass (corrosion resistant, adequate conductivity) |
| Pin type | Spring-loaded pogo pins (P75 or P100 series), 2-3mm diameter, 1-2mm stroke |
| Current | ~0.85A per motor typical, ~3A stall transient |
| Wipe action | Natural -- pin tip drags across elongated pad during slide-in insertion |

The guide rails position the cartridge within ~0.5mm lateral tolerance. The oversized pads (8mm target for a 2mm pin tip) tolerate 2-3mm of misalignment, so electrical contact is effectively guaranteed.

Moisture mitigation: a drainage channel molded into the dock ceiling slopes away from pin pockets. Conformal coating protects PCB traces and solder joints on the dock side; contact surfaces remain bare metal.

See `research/electrical-mating.md` for the full connector technology survey, moisture analysis, and implementation sketch.

---

## 5. Guide and Alignment

A three-stage alignment strategy gets the cartridge from blind insertion in a dark cabinet to sub-millimeter precision at the mating face.

**Stage 1 -- Chamfered entrance (coarse capture).** A 5mm chamfer on the slot lip accepts the cartridge even with 10-15mm of initial misalignment. The funnel narrows to the rail clearance over the first 15-20mm.

**Stage 2 -- Floor rails and side guides (guided travel).** Two parallel floor rails (2mm tall, 3mm wide, full slot depth) carry the cartridge weight and provide primary depth guidance. Side wall guides (1.5mm wide rails, 0.3-0.5mm clearance per side) prevent lateral wobble. The cartridge slides ~130mm along these rails.

**Stage 3 -- Last-stage precision.** The final 10-15mm of travel constrains to ~1mm tolerance so the four JG fittings align. Tapered alignment pins at the mating face correct the last 1-2mm of lateral error.

Material: PETG for all sliding surfaces (lower friction than PLA, better layer adhesion, adequate stiffness). Rail clearance: 0.3-0.5mm per side for FDM.

See `research/guide-alignment.md` for the full mechanism family survey, tolerance analysis, 3D printing clearances, and consumer product prior art.

---

## 6. Insertion and Removal Sequence

### Insertion

1. User opens the front panel (or accesses the slot directly if no panel door).
2. User rests the cartridge on the cabinet floor, roughly aimed at the slot. The twist-release knob is in the loose/unlocked position (default). The springs (2x 0.5 N/mm, compressed ~1mm) hold the release plate retracted 3mm from the rear wall dock face. The plate's stepped bores clear the JG body ends and collets.
3. The 5mm x 45-degree chamfered entrance on the shell's four front edges captures the cartridge and funnels it onto the floor rails even with 10-15mm of initial misalignment.
4. The cartridge slides ~130mm along the floor rails (2mm tall x 3mm wide). Side guides (1.5mm wide, 0.3-0.5mm clearance per side) prevent lateral wobble.
5. At full insertion depth, the dock's bare 1/4" OD tube stubs pass through the release plate's 6.50mm tube clearance holes (0.20mm diametral clearance to 6.30mm tubes) and enter the cartridge's four JG fittings. Collets grip automatically via spring-steel teeth -- no user action needed. The ~20N total collet retention force (4 fittings x ~5N each) secures the cartridge.
6. Pogo pins (P75/P100 series, 1-2mm stroke) on the dock ceiling make contact with 8x5mm nickel-plated brass pads on the cartridge top face. Wipe action from the slide-in motion cleans the contact surfaces.
7. Done. No knob action required for insertion. The JG collets provide all retention.

### Removal

**Prerequisite:** Firmware enforces a mandatory clean cycle before the cartridge can be removed. After the clean cycle, all fluid lines contain only water or air.

1. User grips the wing knob wings (45mm wingspan) with thumb and forefinger and twists clockwise (from front) 180 degrees. The Tr12x3 2-start thread (6.0mm lead) converts the half turn into 3.0mm of plate travel toward the rear wall. The plate's stepped bores (15.30mm outer, 9.70mm inner lip) slide over all four JG body ends and push collets inward ~1.3mm, releasing the dock tube stubs. Spring resistance increases from ~1N to ~4N total over the stroke, providing progressive tactile feedback. **DESIGN GAP: No hard stop or detent at 180 degrees yet -- the user currently has no distinct tactile endpoint (see section 3 design gaps).**
2. User pulls the cartridge forward by the knob wings (which double as a pull handle), sliding it along the rails and out of the slot. The ~4N spring force plus friction provides slight resistance to accidental extraction before full collet release.
3. Pogo pins retract into the dock ceiling (1-2mm spring stroke) as the cartridge withdraws.
4. Once the cartridge is free, the user can release the knob. The springs push the plate back to the retracted position (3mm from rear wall), ready for the next insertion. The self-locking thread (lead angle 10.3 deg < friction angle 16.7 deg) keeps the knob in whatever position the user leaves it.

Total swap time target: under 60 seconds, one-handed, in a dark cabinet.

---

## 7. Cartridge Body Construction

The recommended construction is a tray + shell assembly (from `research/pump-mounting.md`):

- **Pump tray:** Flat PETG plate (138 x 120 x 6mm) with heat-set M3 insert bosses for the two pump brackets. Includes printed C-clips for tubing strain relief and a wire routing channel. Prints flat for maximum screw boss strength.
- **Outer shell:** Rectangular PETG box (148 x 130 x 80mm exterior, 4mm solid walls, 140 x 122 x 72mm interior) with slide rails on the exterior, JG fitting pockets on the rear wall, 12.5mm bore in the front wall for the threaded strut, and a recess for the pogo target PCB on the top face. The tray drops in and screws to the shell ledges.
- **Lid:** Flat plate closing the open top, secured with screws or snap clips. Provides assembly access.

Pump mounting uses the Kamoer bracket (2-4x M3 holes, exact pattern to be measured from the physical pumps). Optional rubber grommet isolators on mount screws reduce vibration transmission. Internal tubing transitions from BPT pump tubes (4.8mm ID x 8.0mm OD) to 1/4" OD hard tubing via brass barb fittings.

---

## 8. Open Questions and Design Gaps

### Design Gaps (from twist-release mechanism)

1. **Rotation limit** — nothing currently stops the knob from rotating past 180 degrees. Need a stop pin on the knob rear face riding in a 180-degree arc slot on the front wall face. Without this, the user has no hard endpoints and risks over-rotation (thread stripping or plate jamming).
2. **Tactile detent at locked/unlocked positions** — the user in a dark cabinet has no click or snap to confirm mechanism state. Need a detent (spring-loaded ball, ramped bump) at the arc slot endpoints.
3. **Assembly orientation keying** — the 2-start thread allows two assembly orientations (0 or 180 degrees). If rotation stops are added, the knob must be installed correctly. Need a visual alignment mark or asymmetric feature.
4. **Wing knob grip extent** — the wings extend only 2.5mm beyond the 40mm body, providing minimal grip advantage. Consider increasing wingspan to 55-60mm or reducing body diameter.
5. **Grease vs. self-locking** — silicone grease on threads would defeat self-locking (lead angle 10.3 deg exceeds friction angle at mu<0.18). Do not grease threads unless a positive rotation stop provides independent locking.
6. **Bushing engagement length** — rear wall is only 4mm thick, providing short bearing length for guide pins. Extending bushings as bosses through the spring pockets would provide 10-12mm of bearing.

### Validation Open Questions

7. **Exact pump mounting hole pattern** — must be measured from the physical KPHM400 pumps with calipers, or obtained from a GrabCAD STEP model.
8. **Print orientation strategy** — shell and tray print orientation need prototyping (wall thickness is 4mm solid, no ribs).
9. **Cartridge ID pin** — whether firmware will support identifying cartridge type/revision via a resistor divider on a 4th pogo contact. Not needed for MVP.
10. **Vibration isolation** — rigid mount first; add rubber grommets if noise is objectionable in practice.
11. **Thread clearance validation** — print a Tr12x3 2-start test pair (20mm bolt + nut, 15-minute print) to dial in radial clearance for the specific PETG filament and profile. Start with 0.3mm radial clearance (0.6mm on diameter).
12. **Integral strut print quality** — the release plate + integral strut prints as one piece (plate flat on build plate, strut vertical). Validate that the strut prints straight and threads engage cleanly.
13. **Printed guide pin wear** — 6mm PETG guide pins sliding in 6.5mm PETG bushings. Monitor for slop or binding over cycle testing. Sand pins with 400+ grit and apply silicone grease to pins (not threads) if needed.
14. **Stepped bore engagement timing** — the exact JG body end protrusion from the rear wall dock face depends on fitting seating depth. Must verify with physical fitting that the outer bore engages the body end within the 3mm plate travel.

---

## 9. Research Index

| File | Description |
|------|-------------|
| `research/collet-release.md` | JG collet behavior, release force, stepped bore geometry. Only relevant if JG fittings are chosen. |
| `research/dock-placement.md` | Front-bottom triangular void geometry, envelope optimization, ergonomics, tube routing for the diagonal interleave layout. |
| `research/electrical-mating.md` | Pogo pins vs blade vs edge connector vs magnetic -- full technology survey. Recommends pogo pins + flat pads. |
| `research/fitting-alternatives.md` | Survey of JG, barb, Luer, bayonet, magnetic, and press-fit fitting options. JG push-to-connect is the chosen approach. |
| `research/guide-alignment.md` | Rail, dovetail, funnel, tapered pin, and kinematic coupling survey. Recommends three-stage: chamfer + rails + fine alignment. |
| `research/pump-mounting.md` | Kamoer pump mounting features, vibration isolation, screw boss design for 3D printing, tray + shell construction, tube strain relief, wire routing. |
| `research/release-mechanism-alternatives.md` | Alternative release strategies beyond the cam lever. Only relevant if JG fittings are chosen. |
| `research/release-plate.md` | Stepped bore geometry and hole arrangement for the JG collet release plate. Only relevant if JG fittings are chosen. |
| `../printed-parts/cartridge-twist-release/planning/research/decision.md` | Decision analysis: hardware-store bolt vs all-printed twist-release mechanism. Recommends 3D-printed approach (Tr12x3 2-start trapezoidal, PETG). |
| `../printed-parts/cartridge-twist-release/planning/research/3d-printed-approach.md` | All-printed twist-release: Tr12x3 2-start trapezoidal thread, PETG material, strut design, guide pins, knob, spring options, durability analysis. |
