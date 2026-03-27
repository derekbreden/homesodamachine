# Cartridge Twist-Release Mechanism

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale. See `research/3d-printed-approach.md` for thread profile research and material analysis.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings. The release plate sits on the dock side of the rear wall (Y > 130).

---

## Mechanism Narrative

The twist-release mechanism converts a half-turn rotation of a wing knob into 3mm of linear plate travel, pushing all four JG collets inward simultaneously to release the dock tubes for cartridge removal.

**What moves:**
- The **wing knob** rotates about the Y-axis. It does not translate. It sits against the exterior face of the front wall (Y=0) and is trapped axially between the front wall face and the threaded engagement with the strut.
- The **release plate + integral strut + integral guide pins** translates along the Y-axis. It does not rotate. The two guide pins sliding in bushings in the rear wall prevent any rotation. The plate moves between two positions: retracted (3mm away from the rear wall on the dock side, spring-held) and advanced (flush against the rear wall dock face).

**What is stationary:**
- The **cartridge shell** (front wall, rear wall) is the ground frame. The front wall provides the axial reaction surface for the knob. The rear wall provides the bushing bores for the guide pins and the through-bore for the strut.

**What converts the motion:**
- A **Tr12x3 2-start trapezoidal thread** (6mm lead) on the strut mates with the internal female thread in the knob. Because the knob is axially constrained by the front wall and can only rotate, turning the knob forces the strut to translate along Y. Half a turn (180 degrees) produces 3mm of travel (6mm lead / 2).

**What constrains each moving part:**
- The **knob** is constrained axially by the front wall exterior face on one side and by thread engagement on the other. It can only rotate. The front wall prevents the knob from translating inward (+Y). Thread friction under spring preload prevents outward drift (-Y).
- The **plate+strut assembly** is constrained rotationally by the two 6mm guide pins sliding in 6.5mm bushings in the rear wall. It can only translate along Y. Axial travel is limited to 3mm by the spring free length and a physical stop on the strut (thread engagement length limit).

**What provides the return force:**
- Two **metal compression springs** (one on each guide pin, between the rear wall dock face and the plate rear face) push the plate away from the rear wall toward the dock. This is the default "retracted" position where collets grip the tubes. The springs provide approximately 1-2N total return force (2x ~0.5 N/mm springs compressed ~1.5mm at the retracted position, increasing to ~3N at full 3mm stroke).

**How the release works:**
- In the **retracted position** (knob loose, springs extended), the plate is 3mm away from the rear wall on the dock side. The stepped bores clear the JG body ends and collets. Collets grip the tubes naturally via their internal spring-steel teeth. This is the normal operating state.
- To **release** (for cartridge removal), the user twists the knob clockwise (from the front). The thread pulls the strut and plate toward the front wall, which from the dock side means the plate advances toward the rear wall. The stepped bores slide over the JG body ends and the inner lip pushes each collet inward ~1.3mm, releasing all four tubes simultaneously.
- To **retract** (after inserting a new cartridge, or to cancel a release), the user simply lets go of the knob or twists it counterclockwise. The springs push the plate back to the retracted position.

**User's physical interaction:**
- **Release (for removal):** Grip the wing knob wings with thumb and forefinger. Twist clockwise 180 degrees. The motion feels like tightening a wing nut -- smooth thread engagement with increasing spring resistance. At full travel, the thread runs out of engagement and the knob feels "free" (clear tactile endpoint). All four collets release. Pull the cartridge straight out by the knob wings (which double as a pull handle).
- **Insert (new cartridge):** With the knob in the loose/retracted position, slide the cartridge onto the dock tube stubs. The tubes pass through the plate's tube clearance holes and enter the JG fittings -- collets auto-grip. No knob action required. The cartridge is retained by ~20N of collet grip force.

---

## Constraint Chain

```
[User hand]
    │ twist (torque about Y-axis)
    ▼
[Wing knob: ROTATES about Y]
    │ Tr12x3 2-start trapezoidal thread (6mm lead)
    │ half turn (180 deg) → 3mm linear travel
    ▼
[Strut + Release plate: TRANSLATES along Y]
    │ stepped bores contact JG collet end faces
    ▼
[4x JG collets pushed inward → tubes release]

Constraints:
  Wing knob axial:      front wall exterior face (reaction surface, prevents +Y translation)
  Plate+strut rotation: 2x 6mm guide pins in 6.5mm rear wall bushings
  Return force:         2x compression springs on guide pins (rear wall → plate, pushes plate to retracted position)
  Self-locking:         lead angle ~9 deg < PETG-on-PETG friction angle ~17 deg (thread does not back-drive under spring load)
```

---

## 3D Printed Part: Wing Knob

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** ~40mm diameter body x ~25mm deep (Y-axis)
- **Features:**
  - Internal female Tr12x3 2-start trapezoidal thread, ~20mm engagement length
  - 0.3mm radial clearance on thread (female minor diameter = 12.6mm for 12.0mm male major diameter)
  - Two wing extensions (left and right) for grip and pull-handle function, ~45mm total wingspan
  - Knurled or textured exterior surface for grip (diamond pattern, 0.8-1.0mm deep, ~2mm pitch)
  - Flat rear face bears against front wall exterior face (Y=0), providing the axial reaction surface
  - Doubles as pull handle for cartridge extraction after collets are released
- **Interfaces:**
  - Threads onto strut front end (male Tr12x3 2-start, 12.0mm major diameter)
  - Knob rear face bears against front wall exterior face at Y=0 (axial constraint, prevents knob from translating +Y)
  - Half turn (180 degrees) produces 3mm of plate travel (6mm lead / 2 = 3mm per half turn)
  - Strut passes through front wall 12.5mm bore with 0.25mm radial clearance (no thread engagement with wall)
- **Quantity:** 1
- **Print orientation:** Upright, open threaded end facing up on build plate. Wing features extend radially and print without supports if overhang angles stay above 45 degrees. 0.12-0.16mm layer height for thread sections, 4+ perimeter walls.

---

## Purchased Parts

### Compression Springs (x2)

- **Specification:** ~8-9mm OD, ~6.5mm ID (must clear 6mm guide pin), 12mm free length, ~0.5 N/mm spring rate, stainless steel
- **Function:** Return release plate to retracted position (collets grip) when knob is loosened. Springs must be preloaded (compressed even at retracted position) to provide nonzero return force.
- **Placement:** On guide pins, seated in ~8mm deep counterbored spring pockets in the rear wall dock face (~10mm dia pocket, centered on each guide pin axis). Spring rear end seats against pocket floor; spring front end bears against plate rear face.
- **Geometry at retracted (operating) position:** Plate is 3mm from rear wall dock face. Spring space = 3mm gap + 8mm pocket = 11mm. A 12mm free-length spring is compressed 1mm. Return force: ~0.5N per spring, ~1N total. Sufficient to hold plate in retracted position.
- **Geometry at advanced (release) position:** Plate is flush with rear wall dock face. Spring space = 0mm gap + 8mm pocket = 8mm. Spring compressed 4mm. Return force: ~2N per spring, ~4N total.
- **Rear wall modification:** The spring pockets are counterbores in the rear wall dock face, coaxial with the guide pin bushings. Pocket diameter ~10mm, depth ~8mm. The 6.5mm bushing bore continues through the wall behind the pocket.

---

## Modification to Shell Rear Wall

- **Strut bore:** 12.5mm diameter through-hole at plate center (X=74, Z=40). The strut (12mm OD smooth shaft) passes through with 0.25mm radial clearance. No thread engagement at this bore.
- **Guide bushings:** 2x 6.5mm bore printed bushings (integral to rear wall or press-fit), 0.25mm radial clearance for 6mm guide pins. Positioned symmetrically about the strut bore.

## Modification to Shell Front Wall

- **Strut clearance bore:** 12.5mm diameter through-hole at (X=74, Z=40). The strut smooth shaft section passes through this bore. The knob threads onto the strut end that protrudes beyond the front wall exterior face.
- **Knob reaction surface:** The front wall exterior face (Y=0) provides the axial constraint for the knob. The knob's flat rear face bears against this surface. No additional features needed -- the wall face itself is the bearing surface.

---

## Assembly Sequence

1. **Slide springs onto guide pins** -- place one compression spring on each of the two integral guide pins on the release plate rear face.
2. **Insert plate+strut assembly through rear wall from dock side** -- feed the strut through the 12.5mm rear wall bore and slide the guide pins (with springs) into the 6.5mm rear wall bushings. The springs compress between the rear wall dock face and the plate.
3. **Feed strut through front wall** -- the strut passes through the cartridge interior and exits through the 12.5mm front wall bore.
4. **Thread wing knob onto strut front end** -- screw the knob onto the protruding strut end until the knob rear face contacts the front wall exterior face.
5. **Verify operation:**
   - Twist knob clockwise (from front): plate advances toward rear wall, compressing springs. At 180 degrees, plate is flush with rear wall dock face (collets would be released).
   - Release or twist counterclockwise: springs push plate back to retracted position (3mm from rear wall).
   - Confirm self-locking: springs alone do not back-drive the thread (plate stays at whatever position the knob sets).

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Research -- 3D-printed thread approach:** `research/3d-printed-approach.md`
- **Research -- mechanism decision:** `research/decision.md`
- **Release plate:** `../../cartridge-release-plate/planning/parts.md`
- **Shell:** `../../cartridge-shell/planning/parts.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
