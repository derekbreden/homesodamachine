# Cartridge Twist-Release Mechanism

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale. See `research/3d-printed-approach.md` for thread profile research and material analysis.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings. The release plate sits on the dock side of the rear wall (Y > 130).

---

## Mechanism Narrative

The twist-release mechanism converts a half-turn rotation of a wing knob into 3mm of linear plate travel, pushing all four JG collets inward simultaneously to release the dock tubes for cartridge removal.

### What Moves

- The **wing knob** rotates about the Y-axis. It does not translate. Its flat rear face (annular bearing surface, 40mm OD x 12.5mm ID, surrounding the strut bore) bears against the front wall exterior face (Y=0). The front wall prevents the knob from translating in the +Y direction. Thread engagement with the strut prevents the knob from translating in the -Y direction (the knob cannot unscrew past the end of the threaded section).
- The **release plate + integral strut + integral guide pins** translates along the Y-axis. It does not rotate. The two 6mm guide pins sliding in 6.5mm bushings in the rear wall prevent rotation.

### What Is Stationary

- The **cartridge shell** (front wall at Y=0..4, rear wall at Y=126..130) is the ground frame. The front wall provides the axial reaction surface for the knob. The rear wall provides the bushing bores for the guide pins, the through-bore for the strut, and the spring pocket reaction surfaces.

### What Converts the Motion

A **Tr12x3 2-start trapezoidal thread** on the strut front end mates with the internal female thread in the knob. Thread parameters:
- Major diameter: 12.0mm (male), 12.6mm (female, providing 0.3mm radial clearance)
- Pitch: 3.0mm per start
- Lead: 6.0mm (2 starts x 3.0mm pitch)
- Flank angle: 29 degrees (trapezoidal/ACME standard)
- Thread depth: 1.5mm (half of pitch for trapezoidal)
- Engagement length: 20mm (on both knob and strut)

Because the knob is axially constrained by the front wall and can only rotate, turning the knob forces the strut to translate along Y. 180 degrees of rotation produces 3.0mm of travel (6.0mm lead x 0.5 turns).

### What Constrains Each Moving Part

**Knob constraints:**
- Axial (+Y): Front wall exterior face at Y=0. The knob's flat rear annular face (40mm OD x 12.5mm ID) bears against this surface, preventing the knob from being pushed into the cartridge.
- Axial (-Y): Thread engagement with the strut. The knob threads onto a 20mm threaded section; it cannot fly off because the user is holding it during operation and the thread is self-locking at rest.
- Radial: The strut (12.0mm OD) passing through the knob's internal thread bore provides radial centering. The front wall bore (12.5mm) does not constrain the knob radially -- the thread does.
- **DESIGN GAP: Rotation limits.** Nothing currently prevents the knob from rotating more than 180 degrees. Over-rotation would attempt to pull the plate beyond 3mm of travel, which is stopped only by the guide pin bushing engagement length and spring solid height. A positive rotation stop (e.g., a pin on the knob rear face riding in a 180-degree arc slot in the front wall exterior face) is needed to limit rotation to exactly 180 degrees and provide hard endpoints. Without this, the user has no tactile indication of the locked vs. unlocked position boundaries.
- **DESIGN GAP: Tactile feedback at locked/unlocked positions.** The current design provides no detent, click, or snap at the 0-degree (unlocked) or 180-degree (locked) positions. The user in a dark cabinet has no way to know when the knob has reached the correct position. A detent mechanism (e.g., a small spring-loaded ball on the knob engaging notches on the front wall face, or a ramped bump on the rotation stop slot) is needed.

**Plate+strut constraints:**
- Rotation: Two 6mm guide pins (integral to plate, 15mm long) slide in 6.5mm bushings in the rear wall. Pin center-to-center spacing is ~35mm. With 0.25mm radial clearance per pin, maximum angular play is arctan(0.5mm / 35mm) = 0.8 degrees -- negligible.
- Axial (Y): Travel is driven by the thread. In the retracted direction (-Y from rear wall, toward dock), the springs push the plate until the thread engagement stops it (knob bottoms against front wall with strut at maximum extension). In the advanced direction (+Y toward rear wall), the plate can advance until the plate rear face contacts the rear wall dock face (0mm gap), at which point the stepped bores have fully engaged the collets.
- **DESIGN GAP: Over-travel protection.** If the knob rotation limit gap (above) is resolved, the plate travel is inherently limited by the thread geometry. But without a rotation stop, the user could continue turning and either strip the thread or jam the plate against the rear wall under excessive force.

### What Provides the Return Force

Two **metal compression springs** (one on each guide pin, between the rear wall dock face spring pocket and the plate rear face). See the compression springs section below for dimensions and force calculations.

### Self-Locking Analysis

The thread must not back-drive under spring return force. Self-locking condition: lead angle < friction angle.

- Lead angle: arctan(lead / (pi x pitch diameter)) = arctan(6.0 / (pi x 10.5)) = arctan(0.182) = **10.3 degrees**
  - Pitch diameter = major diameter - thread depth = 12.0 - 1.5 = 10.5mm
- Friction angle for PETG-on-PETG: arctan(mu) where mu = 0.3-0.5 (published range for PETG sliding friction)
  - At mu=0.3 (worst case): arctan(0.3) = **16.7 degrees**
  - At mu=0.5 (typical): arctan(0.5) = **26.6 degrees**
- Margin: 16.7 - 10.3 = **6.4 degrees minimum** (at worst-case friction)

The thread is self-locking with margin. The springs (max ~4N total at full stroke) cannot back-drive the knob. If silicone grease is applied to threads, friction coefficient may drop to ~0.15-0.20; at mu=0.15, friction angle = 8.5 degrees, which is LESS than the 10.3-degree lead angle -- the thread would no longer self-lock. **Grease must not be applied to threads if self-locking is required at all positions.** Alternatively, the rotation stop detent (see design gap above) would provide positive locking independent of thread friction.

### User's Physical Interaction

- **Release (for removal):** Grip the wing knob wings (45mm wingspan, 10mm wing depth provides ~22.5mm moment arm) with thumb and forefinger. Twist clockwise (from front) 180 degrees. The thread converts rotation to -Y strut translation (toward front wall), which from the dock side advances the plate toward the rear wall. Spring resistance increases from ~1N to ~4N total over the stroke. **DESIGN GAP: No tactile endpoint.** The user currently has no distinct feel at 180 degrees (see rotation limit gap above). Once the rotation stop is implemented, the hard stop provides the endpoint feel. After release, pull cartridge out by knob wings.
- **Insert (new cartridge):** Knob in loose/unlocked position (springs hold plate retracted). Slide cartridge onto dock tubes. Collets auto-grip. No knob action needed.

---

## Constraint Chain

```
[User hand: twist torque about Y-axis, ~22.5mm moment arm on wing]
    | force transmission: wing knob rotates about Y
    v
[Wing knob: ROTATES about Y-axis]
    | constrained axially by: front wall face at Y=0 (+Y) and thread engagement (-Y)
    | constrained radially by: thread engagement with strut (12.0mm)
    | DESIGN GAP: no rotation limit (need 180-deg arc stop)
    | DESIGN GAP: no detent at locked/unlocked positions
    |
    | force conversion: Tr12x3 2-start trapezoidal thread
    |   180 deg rotation -> 3.0mm linear travel along Y
    |   mechanical advantage: 2*pi*22.5mm / 6.0mm = 23.6:1 (wing tip to thread)
    v
[Strut + Release plate: TRANSLATES along -Y (toward front wall)]
    | constrained rotationally by: 2x 6mm guide pins in 6.5mm bushings (0.25mm radial clearance)
    | constrained axially by: thread engagement (retract limit) and rear wall face (advance limit)
    | return force: 2x compression springs (~1-4N total over stroke)
    |
    | force transmission: 4x stepped bores on plate contact JG collet end faces
    v
[4x JG collets pushed inward ~1.3mm -> tubes release]

Self-locking: lead angle 10.3 deg < friction angle 16.7 deg (at mu=0.3 worst case)
    Thread does not back-drive under spring load (max 4N).
```

---

## 3D Printed Part: Wing Knob

- **Type:** 3D printed
- **Material:** PETG
- **Body envelope:** 40mm diameter cylindrical body x 25mm deep (Y-axis)
- **Features:**
  - **Internal female Tr12x3 2-start trapezoidal thread:**
    - Minor diameter (bore): 12.6mm (= 12.0mm male major + 0.6mm diametral clearance)
    - Major diameter (root of female thread): 12.0mm + 2 x 1.5mm thread depth + 0.6mm clearance = 15.6mm
    - Engagement length: 20mm
    - 0.3mm radial clearance on thread flanks
  - **Two wing extensions** for grip and pull-handle function:
    - Total wingspan: 45mm (tip to tip, measured across the knob center)
    - Wing width (radial extent beyond body): (45 - 40) / 2 = 2.5mm beyond the 40mm body on each side
    - **DESIGN GAP: Wing radial extent.** At only 2.5mm beyond the body, the wings provide minimal additional grip leverage. Either the wingspan should be increased (e.g., 55-60mm) or the body diameter reduced (e.g., 30mm body with 45mm wings = 7.5mm wing extent per side). The current 45mm wingspan on a 40mm body is effectively just a slightly non-circular cylinder, not a true wing knob.
    - Wing thickness: 10mm (Y-axis depth, same plane as knob body)
    - Wing profile: rounded rectangular lobes, overhang angles >45 degrees for support-free printing
  - **Knurled exterior surface:** Diamond pattern, 0.8-1.0mm depth, ~2mm pitch, on the cylindrical body OD
  - **Flat rear annular face:** Bears against front wall exterior face (Y=0). Annular contact area: 40mm OD to 12.5mm ID (matching front wall strut bore). This face provides the axial reaction that prevents knob +Y translation.
  - **DESIGN GAP: Rotation stop feature.** A pin, tab, or lug on the knob rear face is needed to ride in a matching 180-degree arc slot on the front wall exterior face. This feature limits rotation to exactly 180 degrees and provides hard tactile endpoints. Pin dimensions and slot geometry TBD.
  - **DESIGN GAP: Assembly orientation keying.** The 2-start thread has two possible assembly orientations (0 and 180 degrees offset). If the rotation stop is implemented, the knob must be threaded onto the strut in the correct orientation so that the stop pin aligns with the slot endpoints at the locked and unlocked positions. A visual alignment mark (flat, dot, or color) on both the knob and strut is needed, OR the stop pin must be positioned so that both 180-degree orientations produce valid locked/unlocked positions (which is only possible if the slot is symmetric about the thread start positions).
- **Interfaces:**
  - Threads onto strut front end (male Tr12x3 2-start, 12.0mm major diameter)
  - Knob rear face bears against front wall exterior face at Y=0
  - Strut passes through front wall 12.5mm bore (0.25mm radial clearance to 12.0mm strut OD)
  - Half turn (180 degrees) produces 3.0mm plate travel (6.0mm lead / 2)
- **Quantity:** 1
- **Print orientation:** Upright, open threaded end facing up. Wing features extend radially and print without supports if overhang angles stay above 45 degrees. 0.12-0.16mm layer height for thread sections, 4+ perimeter walls, 30%+ infill.

---

## Purchased Parts

### Compression Springs (x2)

- **Specification:** ~8-9mm OD, ~6.5mm ID (must clear 6mm guide pin with 0.25mm radial gap), 12mm free length, ~0.5 N/mm spring rate, stainless steel
- **Function:** Return release plate to retracted position when knob is loosened.
- **Placement:** On guide pins, seated in ~8mm deep counterbored spring pockets in the rear wall dock face (~10mm diameter pocket, centered on each guide pin axis). Spring rear end seats against pocket floor; spring front end bears against plate rear face.
- **Force at retracted (operating) position:**
  - Plate is 3mm from rear wall dock face. Available spring space = 3mm gap + 8mm pocket depth = 11mm. A 12mm free-length spring is compressed 1mm.
  - Force per spring: 0.5 N/mm x 1mm = 0.5N. Total return force: ~1.0N.
  - This is sufficient to hold the plate retracted but provides minimal tactile feel for the user. The user would feel almost no spring resistance when starting to twist.
- **Force at advanced (release) position:**
  - Plate is flush with rear wall dock face. Available spring space = 0mm gap + 8mm pocket depth = 8mm. Spring compressed 4mm.
  - Force per spring: 0.5 N/mm x 4mm = 2.0N. Total: ~4.0N.
  - Thread mechanical advantage (23.6:1 from wing tip) reduces required fingertip force to ~0.17N -- imperceptible.
- **Spring solid height check:** A typical 12mm free-length spring with 0.5 N/mm rate and ~8-9mm OD has approximately 6-7mm solid height. At maximum compression (4mm deflection, 8mm compressed length), the spring is not at solid height. Adequate.
- **Rear wall modification:** The spring pockets are counterbores in the rear wall dock face, coaxial with the guide pin bushings. Pocket diameter ~10mm, depth ~8mm. The 6.5mm bushing bore continues through the wall behind the pocket.

---

## Modification to Shell Rear Wall

- **Strut bore:** 12.5mm diameter through-hole at plate center (X=74, Z=40 in shell coordinates). The strut smooth shaft section (12.0mm OD) passes through with 0.25mm radial clearance. No thread engagement at this bore -- the strut is smooth through this section.
- **Guide bushings:** 2x 6.5mm bore printed bushings (integral to rear wall or press-fit), 0.25mm radial clearance for 6.0mm guide pins. Positioned symmetrically about the strut bore at shell coordinates (X=57, Z=40) and (X=91, Z=40), giving 34mm center-to-center spacing.
  - Bushing engagement length: at least 10mm (the full rear wall thickness of 4mm plus any boss extension into the dock-side cavity). The 4mm wall thickness alone provides only 4mm of bearing length for the guide pins, which is short for a 6mm pin. **DESIGN GAP: Bushing engagement length.** 4mm of bearing length on a 6mm pin with 0.25mm clearance allows ~3.6 degrees of angular play per pin. With two pins 34mm apart this is acceptable (the second pin constrains the other end), but extending the bushings as bosses 6-8mm into the dock-side cavity would improve guidance. The spring pockets (8mm deep, 10mm dia) are coaxial with the bushings, so the bushing bore could continue through the spring pocket wall, providing up to 12mm of total bearing length.
- **Spring pockets:** 2x counterbores in rear wall dock face, 10mm diameter, 8mm deep, coaxial with guide pin bushings. The 6.5mm bushing bore runs through the center of each pocket.

## Modification to Shell Front Wall

- **Strut clearance bore:** 12.5mm diameter through-hole at (X=74, Z=40 in shell coordinates). The strut smooth shaft section passes through. The knob threads onto the strut end that protrudes beyond the front wall exterior face.
- **Knob reaction surface:** The front wall exterior face (Y=0) is the axial constraint for the knob. The knob's flat rear annular face bears against this surface. No additional features needed beyond the flat wall face.
- **DESIGN GAP: Rotation stop slot.** If a rotation-limiting feature is added to the knob (see knob design gaps), a corresponding 180-degree arc slot must be machined or printed into the front wall exterior face, centered on the strut bore, at a radius matching the knob's stop pin. Slot width ~3mm, depth ~2mm, arc from 0 to 180 degrees. The slot endpoints provide the hard stops for locked and unlocked positions.

---

## Assembly Sequence

1. **Slide springs onto guide pins** -- place one compression spring on each of the two integral guide pins on the release plate rear face (the dock-facing side of the plate). The springs slide over the 6mm pins; the ~6.5mm spring ID clears the pins.
2. **Insert plate+strut assembly through rear wall from dock side** -- feed the strut (12.0mm OD smooth section) through the 12.5mm rear wall bore and slide the guide pins (with springs) into the 6.5mm rear wall bushings. The springs seat in the 8mm deep spring pockets and compress between the pocket floor and the plate rear face.
3. **Feed strut through front wall** -- the strut passes through the cartridge interior and exits through the 12.5mm front wall bore. The threaded section (20mm long, Tr12x3 2-start) protrudes beyond the front wall exterior face.
4. **Thread wing knob onto strut front end** -- screw the knob onto the protruding strut threaded end. The 2-start thread has two possible orientations (0 or 180 degrees offset). **DESIGN GAP: No keying ensures correct orientation.** If a rotation stop is implemented, the knob must be installed in the correct rotational orientation relative to the stop slot. See knob design gap above.
5. **Verify operation:**
   - Twist knob clockwise (from front): plate advances toward rear wall, compressing springs. At 180 degrees, plate should be flush with rear wall dock face.
   - Release or twist counterclockwise: springs push plate back to retracted position (3mm from rear wall).
   - Confirm self-locking: springs alone do not back-drive the thread.

---

## Design Gap Summary

| ID | Gap | Impact | Suggested Resolution |
|----|-----|--------|---------------------|
| DG-1 | No rotation limit -- nothing stops over-rotation past 180 degrees | User cannot feel locked/unlocked endpoints; risk of thread stripping or plate jamming | Add a pin on knob rear face riding in a 180-degree arc slot on front wall face |
| DG-2 | No tactile detent at locked and unlocked positions | User in dark cabinet cannot confirm mechanism state by feel | Add spring-loaded ball detent or ramped bump at slot endpoints |
| DG-3 | No assembly orientation keying for 2-start thread | Knob may be installed 180 degrees wrong, misaligning rotation stops | Add visual mark or asymmetric feature; or design stop geometry to work in both orientations |
| DG-4 | Wing radial extent only 2.5mm beyond body | Minimal grip improvement over a plain cylinder | Increase wingspan to 55-60mm or reduce body to 30mm |
| DG-5 | Bushing engagement length only 4mm (rear wall thickness) | Short bearing length may allow guide pin angular play | Extend bushings as bosses through spring pocket walls for 10-12mm total bearing length |
| DG-6 | Silicone grease on threads may defeat self-locking | Lead angle (10.3 deg) exceeds friction angle at mu<0.18 | Do not grease threads, or implement positive locking via rotation stop detent |

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Research -- 3D-printed thread approach:** `research/3d-printed-approach.md`
- **Research -- mechanism decision:** `research/decision.md`
- **Release plate:** `../../cartridge-release-plate/planning/parts.md`
- **Shell:** `../../cartridge-shell/planning/parts.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
