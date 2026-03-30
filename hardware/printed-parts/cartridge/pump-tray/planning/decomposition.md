# Pump-Tray Decomposition

**Decision: Pass-through. This part is a single geometric paradigm. No decomposition needed.**

---

## Decomposition Criteria Assessment

### Criterion 1: Does the part combine features from fundamentally different geometric paradigms?

No.

Every feature on the pump-tray belongs to a single paradigm: prismatic operations (extrude and cut) on a flat plate. The complete feature inventory:

- Base plate body — box
- Mounting pad zones — coplanar with base plate surface, no step operation needed beyond the 0.5mm field zone recess
- Field zone step — 0.5mm recess, extrude-and-cut into base plate face
- Motor bores (2×) — cylindrical through-cut, vertical axis
- M3 clearance holes (8×) — cylindrical through-cut, vertical axis
- Boss cylinders (8×) — cylindrical extrusion from front face, vertical axis
- Boss cavities (8×) — cylindrical blind bore, vertical axis into boss top
- Cross rib — rectangular extrusion from front face, vertical axis
- Bore-to-boss radiating ribs (8×) — short rectangular extrusions from front face, vertical axis
- Wiring channels (2×) — rectangular pocket cuts into rear face, vertical axis (into the face that is the top surface when printing)
- Wiring channel strain-relief bumps (6×) — small rounded extrusions from channel floors, vertical axis
- Snap notches (2×) — rectangular relief cuts into rear lateral edges
- Perimeter chamfers — 45° chamfer on top and lateral edges
- Elephant's foot chamfer — 0.3mm × 45° chamfer on bottom edge
- Rear bore edge chamfers (2×) — 0.5mm × 45° chamfer on rear face bore entries

All of these are: box, cut box, extrude cylinder, cut cylinder, chamfer edge. There is no swept profile, no loft, no helix, no revolve of a complex axial profile. The motor bores are straight cylindrical through-holes — not stepped bores with multiple diameters. The boss cavities are simple blind cylindrical bores. CadQuery's `extrude()`, `cut()`, `chamfer()`, and `fillet()` cover the complete feature set.

**This criterion does not apply.**

### Criterion 2: Would a single CadQuery agent need to use multiple advanced techniques?

No.

The most complex single operation in this part is the bore-to-boss radiating ribs, which are short rectangular extrusions positioned between a boss OD and a bore edge. This is a box extrusion with a positional offset — no advanced technique. The wiring channels with strain-relief bumps are rectangular pockets with small rounded protrusions — still box operations. Nothing in this part requires a sweep, loft, revolve of a multi-point axial profile, or helix.

The CadQuery script for this part is: build plate box, union bosses and ribs, cut bores and holes and channels, add chamfers and fillets. Every line of that script uses the same workplane and the same operation types. A single agent handles this without technique diversity.

**This criterion does not apply.**

### Criterion 3: Do features in different regions have no geometric dependencies on each other?

No — features are tightly coupled to a shared reference geometry.

The two mounting pad zones are symmetrically placed about the plate centerline. Boss positions are defined relative to bore centers, not independently. Rib positions are defined by boss ODs and bore edges — the rib geometry cannot be specified without knowing both. The snap notches are positioned at the rear lateral edges of the plate, which is defined by the plate's own dimensions. The wiring channels originate at the motor bore edges. Every feature references the plate origin, the bore centers, or both. There is no region of this part whose features are geometrically independent of the rest.

**This criterion does not apply.**

---

## Pass-Through Definition

### Reference Frame

```
Origin:   Front-face bottom-left corner of tray (build plate face corner)
X:        Tray width, left to right — range [0, 144mm]
Y:        Tray thickness, front face to rear face — range [0, 5mm]
          Y=0 is front face (pump-bracket side, printed face-down on build plate)
          Y=5 is rear face (motor/service side, top surface when printing)
Z:        Tray height, bottom to top — range [0, ~80mm]
          Z=0 is build plate face (bottom edge)
          Z=~80 is top edge (pump-tube clearance edge)
Envelope: 144mm W × 5mm D × ~80mm H → X:[0,144] Y:[0,5] Z:[0,80]
```

Note on Z: the exact height (80mm vs. 85mm) depends on OQ-3/OQ-4 resolution (tube stub positions). The specification step must pin this dimension before CAD generation.

Plate center in X: X = 72mm. Bore centers are at X = 72 ± (bore_spacing/2), Z = plate_Z_center. Exact bore center positions are derived from pump mounting geometry per `../off-the-shelf-parts/kamoer/extracted-results/geometry-description.md`.

### Geometric Paradigm

Single paradigm: **extrude-and-cut on a flat plate.**

Operation sequence:
1. Box — base plate body, 144 × 5 × 80mm with 3mm outer corner radii (plan view)
2. Cut — 0.5mm field zone recess into front face (Y=0), outside the two mounting pad zones and cross rib; 45° chamfer at step transition
3. Union — 8 boss cylinders (9mm OD, 5mm tall) from front face (Y=0)
4. Union — cross rib (6mm wide, 5mm tall) between two mounting pad zones along plate X midline
5. Union — 8 radiating ribs (4mm wide, 5mm tall, variable length) from boss ODs toward bore edges
6. Cut — 2 motor bores (37.2mm diameter, through-plate, vertical axis in Y) with 0.5mm × 45° chamfer on rear face entry
7. Cut — 8 M3 clearance holes (3.6mm diameter, through-plate, vertical axis in Y)
8. Cut — 8 boss cavities (4.7mm diameter, 4.5mm deep blind bore from boss top, vertical axis in Y)
9. Cut — 2 wiring channels (6mm wide, 4mm deep, rectangular pocket into rear face Y=5), routing path from bore edge to tray lateral edge, then longitudinally toward front
10. Union — 6 strain-relief bumps (1.5mm tall × 2mm wide, rounded, 3 per channel) from channel floors
11. Cut — 2 snap notches (1.5mm deep × 3mm wide relief) into rear lateral edges of tray (top or bottom edge per concept.md Section 2)
12. Chamfer — 1.5mm × 45° on top face (Z=80) perimeter edge and lateral edges (X=0, X=144), full plate height
13. Chamfer — 0.3mm × 45° on bottom edge (Z=0, elephant's foot edge, per requirements.md)
14. Fillet — 1.5mm radius at boss base where cylinder meets plate face
15. Fillet — 2.0mm radius at rib base where rib meets plate face
16. Fillet — 1.5mm radius at wiring channel interior corners (wall meets channel floor)

All operations share the same coordinate origin. No coordinate frame change is needed within the script.

### Interface Boundaries

**Tray-to-shell channel interface:**
- Tray lateral edges (X=0 plane and X=144mm plane), full plate height and thickness
- Engaging surface: 5.0mm tray thickness (Y dimension), sliding into a 5.2mm shell channel
- Snap notch: 1.5mm deep × 3mm wide rectangular relief in each lateral edge, positioned at rear edge of tray. Exact Z position (along the tray height) must be specified in the shell concept step; the tray notch is a passive rectangular cut that the shell latch hooks into
- The tray contributes flat sliding surfaces and a passive notch. All snap spring geometry is on the shell.

**Pump bracket mating faces:**
- Two mounting pad zones on front face (Y=0), each centered on a motor bore
- Mounting pad zone footprint: approximately 74mm × 74mm (per concept.md Section 5) centered on each bore center
- Mating surface: flat, at Y=0 (front face at full plate height)
- Boss tops: coplanar at Y = −5mm (5mm proud of front face, or equivalently Z=+5mm above front face surface in the front-face workplane)
- 8 boss cavities open at boss top faces: 4.7mm CAD diameter, 4.5mm deep, receive M3 heat-set inserts
- Boss OD: 9mm
- Motor bore: 37.2mm diameter through-hole; motor cylinder passes through this bore from front face

**Motor bore geometry:**
- Diameter: 37.2mm (37mm motor body + 0.2mm loose fit clearance per requirements.md)
- Axis: Y-axis (through plate thickness)
- Position: derived from Kamoer pump geometry description (caliper-verified bore center X and Z coordinates)
- Rear face entry chamfer: 0.5mm × 45° for finished appearance and slight clearance on bore arc top
- Motor cylinder protrudes through bore from front face; bore is a clearance hole, not a bearing surface — no surface contact between bore wall and motor body is expected

**JG fitting pocket faces:**
- The pump-tray does NOT carry JG fitting pockets. This is an explicit decision in concept.md Section 2.
- The JG fittings belong to the cartridge rear wall (a separate shell panel, OQ-5 from synthesis.md).
- The tray's rear face (Y=5mm) is a flat utility surface; it presents no fitting pocket geometry and no interface to JG components.
- The tray's rear edge (top of Z range) faces the JG fitting zone but carries no features for it; tube stubs from the pump heads pass through or alongside the tray edge into the rear wall zone.
- When the JG fitting pocket specification is written (per OQ-7), there is no tray interface to resolve — the rear wall carries all JG geometry independently.

---

## Open Questions Blocking CAD Start

The following OQs from concept.md must be resolved before the specification step can produce final dimensions for the generation script:

- **OQ-1:** Screw hole depth in pump head body → determines M3 screw length (12mm vs. 14–15mm). Does not affect tray CAD, but affects BOM.
- **OQ-2:** Motor body diameter → confirms 37.2mm bore or requires adjustment.
- **OQ-3 / OQ-4:** Tube stub Z and X positions on pump face → determines final tray height (80mm vs. 85mm) and bore center Z position.
- **OQ-6:** Shell harness connector location → determines wiring channel routing path (lateral-then-longitudinal vs. diagonal). Affects only the channel path; all other tray features are independent of this.

OQ-1 and OQ-6 do not block CAD start. OQ-2, OQ-3, OQ-4 must be resolved before the bore diameter and tray height are finalized. The specification step for the tray should be gated on OQ-2/3/4 resolution.

---

## Summary

The pump-tray passes through decomposition as a single part. It is a flat PETG plate with extrude-and-cut features only. No decomposition criterion applies. One CadQuery agent, one coordinate frame, one operation sequence, one STEP file.
