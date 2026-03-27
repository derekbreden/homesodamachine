# Cartridge Twist-Release Mechanism

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale. See `research/3d-printed-approach.md` for thread profile research and material analysis.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings.

**Critical directional change:** The release plate sits on the DOCK SIDE of the rear wall (outside the cartridge body), not inside. The stepped bores face the dock-side collets. The strut pulls the plate toward the rear wall (toward the cartridge interior) to push dock-side collets inward.

---

## 3D Printed Part: Wing Knob

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** ~40mm diameter body x ~25mm tall
- **Features:**
  - Internal female Tr12x3 2-start trapezoidal thread, ~20mm engagement length
  - 0.3mm radial clearance on thread (female minor diameter = 12.6mm for 12.0mm male major diameter)
  - Wing extensions on left and right sides for grip and pull-handle function
  - Knurled or textured exterior surface for grip (diamond pattern, 0.8-1.0mm deep, ~2mm pitch)
  - Sits against front wall (Y=0 face) with strut threading through
  - Doubles as pull handle for cartridge extraction after collets are released
- **Interfaces:**
  - Threads onto strut front end (male Tr12x3 2-start)
  - Half turn (180 degrees) produces 3mm of plate travel (6mm lead / 2 = 3mm per half turn)
  - Rotates freely against front wall face
- **Quantity:** 1
- **Print orientation:** Upright (open threaded end on build plate for clean internal threads). Wing features extend radially and print without supports if overhang angles stay above 45 degrees.

---

## 3D Printed Part: Guide Pins (integral to release plate)

- **Type:** 3D printed as part of the release plate
- **Material:** PETG
- **Dimensions:** 2x 6mm diameter pins, ~15mm long, extending from rear face of release plate
- **Features:**
  - Slide in 6.5mm bore printed bushings in the rear wall (0.25mm radial clearance)
  - Prevent plate rotation and ensure parallel travel during 3mm stroke
  - Adequate for 3mm travel and ~36 cycles over 3 years
- **Interfaces:**
  - Integral to release plate (no separate fastening)
  - Mate with printed bushings in rear wall
- **Quantity:** 2 (printed as one piece with release plate)

---

## Purchased Parts

### Compression Springs (x2)

- **Specification:** ~5mm OD x 10mm free length, ~0.5 N/mm spring rate
- **Function:** Return release plate to retracted position (collets grip) when knob is loosened
- **Placement:** On guide pins between rear wall and release plate

---

## Modification to Existing Release Plate

The existing release plate (59W x 47H x 6D mm, see `../../cartridge-release-plate/planning/parts.md`) now has the full threaded strut as an integral feature:

- **Integral strut:** The 12mm diameter Tr12x3 2-start trapezoidal strut extends directly from the plate center (29.5, 23.5), replacing the previous press-fit socket. The strut is one continuous printed piece with the plate -- no joint, no epoxy. Total Y extent ~136mm (6mm plate + ~4mm rear wall passage + ~122mm interior span + front thread section).
- **Integral guide pins:** 2x 6mm diameter PETG pins, ~15mm long, extending from the plate rear face. Replace the 3mm steel dowel pin slots with printed pin locations matching the 6.5mm bushings in the rear wall.

The release plate remains on the **dock side** of the rear wall (outside the cartridge body). The stepped bores face the dock-side collets.

---

## Modification to Shell Rear Wall

- **Strut bore:** 12.5mm diameter through-hole at plate center (X=74, Z=40), replacing the existing 6.5mm M6 bolt bore
- **Guide bushings:** 2x 6.5mm bore printed bushings (integral to rear wall or press-fit), replacing the 3.0mm dowel pin press-fit holes

## Modification to Shell Front Wall

- **Strut clearance bore:** 12.5mm diameter through-hole at (X=74, Z=40), replacing the existing 6.5mm M6 bolt bore. The strut passes through but does not engage the front wall -- the knob threads onto the strut end beyond the front wall.

---

## Assembly Sequence

1. **Mount release plate + strut unit through rear wall** -- slide integral guide pins through 6.5mm bushings in rear wall, with compression springs on pins between rear wall and plate. The integral strut feeds through the 12.5mm rear wall bore into the cartridge interior.
2. **Thread wing knob onto strut end at front of cartridge** -- knob threads onto the strut's front-end male thread, seating against the front wall face
5. **Verify operation:**
   - Half turn clockwise draws plate toward rear wall (collets release)
   - Half turn counterclockwise allows springs to push plate back (collets grip)
   - The mechanism is self-locking: lead angle vs. friction angle prevents the plate from back-driving the thread under spring load

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Research -- 3D-printed thread approach:** `research/3d-printed-approach.md`
- **Research -- mechanism decision:** `research/decision.md`
- **Research -- bolt approach (superseded):** `research/hardware-store-bolt.md`
- **Release plate:** `../../cartridge-release-plate/planning/parts.md`
- **Shell:** `../../cartridge-shell/planning/parts.md`
