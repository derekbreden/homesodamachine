# Cartridge Twist-Release Mechanism

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale. See `research/3d-printed-approach.md` for thread profile research and material analysis.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings.

**Critical directional change:** The release plate sits on the DOCK SIDE of the rear wall (outside the cartridge body), not inside. The stepped bores face the dock-side collets. The strut pulls the plate toward the rear wall (toward the cartridge interior) to push dock-side collets inward.

---

## 3D Printed Part: Threaded Strut

- **Type:** 3D printed
- **Material:** PETG
- **Dimensions:** 12mm OD, ~126mm total length (4mm rear wall thickness + 122mm interior span)
- **Features:**
  - Tr12x3 2-start trapezoidal thread on BOTH ends, ~20mm threaded sections each
  - Middle section: smooth 12mm cylinder (no threads, reduces print time and wear surface)
  - Rear end: press-fits into 12mm ID socket in release plate, secured with epoxy
  - Front end: male thread engages wing knob's internal female thread
  - Passes through rear wall via 12.5mm bore (0.25mm clearance per side)
- **Interfaces:**
  - Rear end permanently bonded to release plate (press-fit + epoxy)
  - Front end threads into wing knob (half turn = 3mm plate travel)
  - Slides freely through rear wall bore during plate travel
- **Quantity:** 1
- **Print orientation:** Vertical (standing on end, thread axis = Z on print bed). Vertical orientation keeps the thread profile in the XY plane for best resolution. Print with brim for bed adhesion, 40-60mm/s for threaded sections, 0.12-0.16mm layer height on threaded sections, 4+ perimeter walls.

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

### Epoxy

- **Specification:** Two-part epoxy (e.g., JB Weld or similar)
- **Function:** Secures strut rear end into release plate socket (permanent bond)
- **Application:** Apply to strut end and socket interior before press-fit assembly

---

## Modification to Existing Release Plate

The existing release plate (59W x 47H x 6D mm, see `../../cartridge-release-plate/planning/parts.md`) needs these changes:

- **Replace center boss with strut socket:** Remove the existing 8mm diameter x 1mm push rod boss at plate center (29.5, 23.5). Replace with a 12mm ID socket, ~10mm deep, for press-fit + epoxy attachment of the strut rear end.
- **Add integral guide pins:** 2x 6mm diameter PETG pins, ~15mm long, extending from the plate rear face. Replace the 3mm steel dowel pin slots with printed pin locations matching the 6.5mm bushings in the rear wall.

The release plate remains on the **dock side** of the rear wall (outside the cartridge body). The stepped bores face the dock-side collets.

---

## Modification to Shell Rear Wall

- **Strut bore:** 12.5mm diameter through-hole at plate center (X=74, Z=40), replacing the existing 6.5mm M6 bolt bore
- **Guide bushings:** 2x 6.5mm bore printed bushings (integral to rear wall or press-fit), replacing the 3.0mm dowel pin press-fit holes

## Modification to Shell Front Wall

- **Strut clearance bore:** 12.5mm diameter through-hole at (X=74, Z=40), replacing the existing 6.5mm M6 bolt bore. The strut passes through but does not engage the front wall -- the knob threads onto the strut end beyond the front wall.

---

## Assembly Sequence

1. **Press-fit and epoxy strut into release plate socket** -- apply epoxy to strut rear end and socket interior, press strut fully into 12mm ID socket, allow to cure
2. **Mount release plate on guide pins through rear wall bushings** -- slide integral guide pins through 6.5mm bushings in rear wall, with compression springs on pins between rear wall and plate
3. **Pass strut through rear wall bore from dock side** -- strut feeds through 12.5mm bore into cartridge interior
4. **Thread wing knob onto strut end at front of cartridge** -- knob threads onto the strut's front-end male thread, seating against the front wall face
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
