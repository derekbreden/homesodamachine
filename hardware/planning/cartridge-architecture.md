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

Four JG PP0408W 1/4" push-to-connect union fittings mount in the cartridge rear wall in a 2x2 grid (40mm horizontal x 28mm vertical center-to-center). The dock carries four bare 1/4" OD hard nylon tube stubs (~30mm protrusion) that the cartridge slides onto during insertion. Collets grip automatically on insertion — no user action needed to connect. The cartridge is the fitting-bearing side; the dock is passive.

**Disconnect uses a twist-release mechanism.** A twist-release knob on the cartridge front face threads onto a 12mm PETG threaded strut with Tr12x3 2-start trapezoidal thread that passes through the cartridge body to a release plate on the dock side of the rear wall. The strut is integral to the release plate -- one continuous printed piece, no joint. The release plate has four stepped bores (15.30mm outer / 9.70mm inner lip / 6.50mm tube clearance, caliper-verified) that engage all four JG body ends simultaneously. Half a turn (180 degrees) of the knob produces 3mm of plate travel (6mm lead from the 2-start thread). When the user unscrews the knob half a turn, return springs on the guide pins retract the plate, all four collets release at once, and the user pulls the cartridge out by the knob (which doubles as the pull handle).

| Aspect | Detail |
|--------|--------|
| Fittings | 4x JG PP0408W 1/4" push-to-connect unions, cartridge-mounted, ~$8 total |
| Fitting grid | 2x2, 40mm horizontal x 28mm vertical center-to-center |
| Release mechanism | 12mm PETG threaded strut (Tr12x3 2-start trapezoidal, integral to release plate) + wing knob + return springs |
| Connect UX | Slide in — cartridge fittings grip dock tube stubs automatically, thread knob half turn to lock |
| Disconnect UX | Unscrew knob half turn, pull out by knob |
| Retention | JG collets provide ~20N grip (4 fittings). Self-locking thread (lead angle ~9 deg < friction angle ~17 deg for PETG-on-PETG) prevents accidental release. |
| Food safety | NSF 61 (potable water). PETG base resin is FDA-listed; stainless nozzle recommended for food-contact parts. |

**Why drips are not a concern:** The firmware enforces a mandatory clean cycle before the cartridge can be unlocked. After the clean cycle, the fluid lines contain only water or air — no flavor concentrate remains in the cartridge or dock fittings. A few drops of water on the enclosure floor during a swap is inconsequential.

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
2. User rests the cartridge on the cabinet floor, roughly aimed at the slot.
3. The chamfered entrance captures the cartridge and funnels it onto the floor rails.
4. The cartridge slides ~130mm along the rails. Side guides prevent lateral wobble.
5. At full insertion depth, the cartridge's four JG fittings slide onto the dock's bare tube stubs. Collets grip automatically — no user action needed.
6. Pogo pins on the dock ceiling make contact with pads on the cartridge top face. Wipe action cleans the contact surfaces.
7. The user threads the twist-release knob clockwise half a turn (180 degrees). The 2-start trapezoidal thread engages rapidly, pulling the release plate snug against the rear wall. Clear tactile stop when fully tightened.

### Removal

**Prerequisite:** Firmware enforces a mandatory clean cycle before the cartridge lock disengages. After the clean cycle, all fluid lines contain only water or air.

1. User unscrews the twist-release knob half a turn (180 degrees) counterclockwise. The strut disengages from the release plate; return springs retract the plate, releasing all 4 JG collets simultaneously.
2. User pulls the cartridge forward by the knob (which doubles as the pull handle), sliding it along the rails and out of the slot.
3. Pogo pins retract into the dock ceiling as the cartridge withdraws.
4. New cartridge slides in (reverse of above).

Total swap time target: under 60 seconds, one-handed, in a dark cabinet.

---

## 7. Cartridge Body Construction

The recommended construction is a tray + shell assembly (from `research/pump-mounting.md`):

- **Pump tray:** Flat PETG plate (138 x 120 x 6mm) with heat-set M3 insert bosses for the two pump brackets. Includes printed C-clips for tubing strain relief and a wire routing channel. Prints flat for maximum screw boss strength.
- **Outer shell:** Rectangular PETG box (148 x 130 x 80mm exterior, 4mm solid walls, 140 x 122 x 72mm interior) with slide rails on the exterior, JG fitting pockets on the rear wall, 12.5mm bore in the front wall for the threaded strut, and a recess for the pogo target PCB on the top face. The tray drops in and screws to the shell ledges.
- **Lid:** Flat plate closing the open top, secured with screws or snap clips. Provides assembly access.

Pump mounting uses the Kamoer bracket (2-4x M3 holes, exact pattern to be measured from the physical pumps). Optional rubber grommet isolators on mount screws reduce vibration transmission. Internal tubing transitions from BPT pump tubes (4.8mm ID x 8.0mm OD) to 1/4" OD hard tubing via brass barb fittings.

---

## 8. Open Questions

1. **Exact pump mounting hole pattern** — must be measured from the physical KPHM400 pumps with calipers, or obtained from a GrabCAD STEP model.
2. **Print orientation strategy** — shell and tray print orientation need prototyping (wall thickness is 4mm solid, no ribs).
3. **Cartridge ID pin** — whether firmware will support identifying cartridge type/revision via a resistor divider on a 4th pogo contact. Not needed for MVP.
4. **Vibration isolation** — rigid mount first; add rubber grommets if noise is objectionable in practice.
5. **Thread clearance validation** — print a Tr12x3 2-start test pair (20mm bolt + nut, 15-minute print) to dial in radial clearance for the specific PETG filament and profile. Start with 0.3mm radial clearance (0.6mm on diameter).
6. **Integral strut print quality** — the release plate + integral strut prints as one piece (plate flat on build plate, strut vertical). Validate that the strut prints straight and threads engage cleanly. The 15-minute Tr12x3 test print validates thread quality before committing to the full part.
7. **Printed guide pin wear** — 6mm PETG guide pins sliding in 6.5mm PETG bushings. Monitor for slop or binding over cycle testing. Sand pins with 400+ grit and apply silicone grease if needed.

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
