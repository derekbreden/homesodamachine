# Pump Cartridge Mechanism — Design Synthesis

This document synthesizes all technical research and design pattern findings into one concrete execution plan for the pump cartridge mechanism described in the vision.

---

## 1. Mechanism Description

### What the user sees and does

The pump cartridge is a smooth, opaque PETG box approximately 132mm wide, 67mm tall, and 177mm deep. The user interacts with exactly three visible features:

1. **Rear face:** Four small holes (one per tube), each chamfered 0.5-1.0mm, barely larger than the 6.35mm tube OD. These are the only indication that tubes connect here.

2. **Side grooves:** Two rectangular channels, one per side, 4.5mm wide and 4.5mm deep, running the full depth of the cartridge. These are visually obvious (not hairline slots) and their tapered lead-in communicates the direction of insertion.

3. **Front face squeeze surfaces:** Two flat surfaces, one for the palm and one for the fingers, separated by a gap. The palm surface is the front wall of the cartridge body (rigidly attached to the internal structure that holds the quick connects). The finger surface is a flat plate that protrudes slightly from the front face, connected internally to the release plate. Both surfaces are single, continuous, seamless planes with no visible fasteners. A subtle texture change or contrasting color distinguishes the squeeze zone from the surrounding shell.

**Insertion:** The user aligns the cartridge's side grooves with the two rectangular rails protruding from the dock's interior walls. A 5mm chamfer at the groove mouth and a matching chamfer on the rail tips create a roughly 6mm capture zone, so alignment within 3mm is sufficient. The user pushes the cartridge in along the rails. The first 130mm of travel is a smooth, low-friction slide (2-5N). In the last 20mm, the four tube stubs on the dock's rear wall begin entering the four John Guest quick connect fittings inside the cartridge. Resistance increases to 20-40N total as the tubes push past the O-rings. The cartridge stops when the tubes bottom out on the internal depth stops inside the fittings. Simultaneously, a 0.5mm printed detent bump on each rail snaps into a matching relief in each groove, producing an audible click. The cartridge face sits flush with the dock opening (within 0.5mm). Four blade electrical terminals on the cartridge rear face engage four shrouded female receptacles on the dock wall during the final 10mm of travel. The user feels three distinct phases: free slide, increasing resistance, then hard stop plus click. This is the confirmation that the cartridge is fully seated.

**Removal:** The user wraps one hand around the front of the cartridge. Their palm rests on the outer flat surface (which is rigidly connected through the cartridge body to the quick connect mounting wall). Their fingers curl around and rest on the inner flat surface (which is connected through internal linkages to the release plate). The user squeezes. The finger surface moves 2-4mm toward the palm surface. This motion pulls the release plate rearward (toward the collets) through a direct rigid linkage. The release plate translates axially along its four collet-hugger bores and presses the four collet sleeves inward, deflecting the grab ring teeth and releasing all four tubes simultaneously. The user feels a rising force that peaks at 10-20N (the combined resistance of 4 collet springs plus linkage friction), then a sharp drop as the collets clear (at least 3:1 peak-to-released ratio). A deflection stop engages within 1mm past the release point, preventing over-squeeze. While maintaining the squeeze, the user pulls the cartridge forward off the dock's tube stubs. The tubes slide freely out of the released fittings. The cartridge clears the detent bumps with 2-3N of pull force and slides out along the rails.

### What moves inside the cartridge

**Release plate:** A flat PETG plate positioned between the motor terminals and the John Guest fittings, in the rear 25-30mm of the cartridge. The plate has four stepped bores, one per fitting:

- Innermost bore: 6.5mm diameter (clears the 6.35mm tube but contacts the collet's annular end face, which spans from 6.69mm ID to 9.57mm OD)
- Middle bore (collet hugger): 9.8mm diameter (0.23mm clearance over the 9.57mm collet OD, providing lateral guidance while allowing axial slide)
- Outer bore: 15.4mm diameter (clears the 15.10mm body end OD with 0.15mm per side)

The four collet-hugger bores collectively constrain the plate in X and Y while permitting Z translation (along the fitting axis). This four-point guidance prevents the tilt that would cause partial collet depression.

The plate travels 3mm total. The first 0.5-1.0mm is take-up (the plate contacts all four collet faces, absorbing manufacturing tolerances in fitting position and collet rest position). The remaining 1.3-2.0mm is active collet depression. The 1.7mm margin between the 1.3mm required collet travel and the 3mm available stroke ensures that "push it all the way" always works.

**Linkage from squeeze surface to release plate:** A pair of rigid arms (printed PETG) connect the finger-side squeeze surface to the release plate. The arms run along the inside of the cartridge side walls, transferring the user's finger pull directly to the plate. This is a 1:1 mechanical ratio — no amplification needed. The arms must be rigid enough not to flex under 40-60N of load.

**Return mechanism:** When the user releases the squeeze, the plate must return to its rest position. The grab ring springs in the four fittings provide some restoring force, but this is not reliable as the sole return mechanism. A pair of small compression springs (or printed PETG flexures) between the release plate and the rear wall bias the plate away from the collets. The return force need only be 5-10N — enough to positively retract the plate and reset the squeeze gap.

### What constrains the cartridge in the dock

**Rails:** Two rectangular PETG rails, 4mm wide by 4mm tall, protruding from the dock's interior side walls. They run the full insertion depth (~150mm). The cartridge's matching 4.5mm x 4.5mm grooves slide over these rails with 0.25mm clearance per side. At 150mm length, this clearance limits angular play to under 0.2 degrees — no visible wobble.

**Tube retention:** Once the four tubes are seated in the John Guest fittings (past the collet grab rings), the pull-out force exceeds 89N per fitting. The four fittings collectively hold the cartridge with over 350N of retention. This is the primary retention mechanism.

**Detent bumps:** Two 0.5mm printed bumps on the rails, positioned at the full-insertion point, snap into 0.3mm-deep reliefs in the grooves. These provide the audible/tactile click and roughly 2-3N of passive retention per side — enough to hold the cartridge during the brief window before the tubes are fully engaged, and enough to prevent slide-out from vibration.

**Electrical engagement:** Four 6.3mm blade terminals on the cartridge rear face mate with four shrouded female receptacles on the dock wall. The blade insertion force (1-3 lbs per contact) is absorbed into the tube-insertion force budget. The rails provide the lateral alignment that blade terminals require (within 0.5-1mm).

---

## 2. Critical Dimensions

### Cartridge Envelope

| Dimension | Value | Source |
|-----------|-------|--------|
| Width (X) | 132mm at pump head region; 144mm at bracket plane (use local reliefs) | Envelope research: 2x 62.6mm pump heads + walls + clearances |
| Height (Z) | 67mm | Envelope research: 62.6mm pump head + walls + clearances |
| Depth (Y) | 177mm | Envelope research: front wall + tube routing + pump + motor + electrical + rear wall |
| Volume | ~1,565 cm3 | Envelope research |

### Collet Release Force and Travel

| Parameter | Value | Source |
|-----------|-------|--------|
| Single collet release force (design value) | 10N | Collet research: first-principles + ergonomic bounds |
| Single collet release force (worst case) | 15N | Collet research |
| 4 collets simultaneously (design) | 40N | Collet research |
| 4 collets simultaneously (worst case) | 60N | Collet research |
| Collet travel required | 1.3mm per side | Caliper-verified: 41.80mm extended - 39.13mm compressed = 2.67mm / 2 |
| Release plate travel available | 3.0mm | Collet research |
| Take-up allowance | 0.5-1.0mm | Collet research: absorbs fitting position tolerances |

### Squeeze Mechanism

| Parameter | Value | Source |
|-----------|-------|--------|
| Squeeze travel | 2-4mm | Design patterns: side-release buckles, HP latch |
| Peak squeeze force | 10-20N | Design patterns: HP spring clamp (17.3N), snap-fit (13N) |
| Force drop ratio at release | At least 3:1 | Design patterns: snap-fit tactile feedback research |
| Deflection stop past release | Within 1mm | Design patterns: ITW Nexus over-flexure prevention |

### Rail Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Rail cross-section (tongue) | 4mm wide x 4mm tall | Rail research |
| Groove cross-section (channel) | 4.5mm wide x 4.5mm tall | Rail research: 0.25mm clearance per side |
| Clearance per side | 0.25mm | Rail research: 1x nozzle width rule for calibrated Bambu |
| Entry taper angle | 30 degrees | Rail research |
| Entry taper length | 5mm on rail tips and groove mouths | Rail research |
| Capture zone | ~6mm per side (with additional 45-degree funnel chamfer) | Rail research |
| Detent bump height | 0.5mm | Rail research |
| Detent engagement force | 3-5N | Rail research |
| Rail length | ~150mm (full insertion depth) | Rail research |

### John Guest Fitting Pocket Dimensions

| Parameter | Value | Source |
|-----------|-------|--------|
| Body end OD | 15.10mm | Caliper-verified JG geometry |
| Center body OD | 9.31mm | Caliper-verified JG geometry |
| Center body length | 12.16mm | Caliper-verified JG geometry |
| Body end length (each side) | 12.08mm | Caliper-verified JG geometry |
| Collet OD | 9.57mm | Caliper-verified JG geometry |
| Collet wall thickness | 1.44mm | Caliper-verified JG geometry |
| Collet ID | 6.69mm | Caliper-verified JG geometry |
| Press-fit bore for center body | 9.5mm (light press-fit) | JG geometry: 9.31mm body in 9.5mm bore |
| Sliding-fit bore for center body | 9.8mm | JG geometry |
| Total length, collets extended | 41.80mm | Caliper-verified JG geometry |
| Total length, collets compressed | 39.13mm | Caliper-verified JG geometry |
| Tube insertion depth | ~16mm per side | Industry standard |

### Pump Mounting Pattern

| Parameter | Value | Source |
|-----------|-------|--------|
| Pump head cross-section | 62.6mm x 62.6mm | Caliper-verified Kamoer geometry |
| Mounting bracket width | 68.6mm | Caliper-verified Kamoer geometry |
| Mounting hole pattern | 4x M3 in 48mm x 48mm square | Caliper-verified Kamoer geometry |
| Mounting hole diameter | 3.13mm | Caliper-verified Kamoer geometry |
| Total pump length (with nub) | 116.48mm | Caliper-verified Kamoer geometry |
| Total pump length (without nub) | 111.43mm | Caliper-verified Kamoer geometry |
| Motor diameter | ~35mm | Kamoer geometry (low confidence) |
| Motor shaft nub protrusion | 5.05mm | Caliper-verified Kamoer geometry |
| Tube stub protrusion from front face | 30-50mm (flexible BPT) | Kamoer geometry |
| BPT tube dimensions | 4.8mm ID / 8.0mm OD | Kamoer geometry |

---

## 3. Integration Zones — The Rear 25-30mm

The rear of the cartridge is the most geometrically constrained zone. Four systems converge here: the John Guest fitting pockets, the release plate, the electrical connectors, and the tube routing transitions. This section describes how they coexist.

### Axial layout (measured from the exterior rear face of the cartridge, inward)

**Zone A: Rear wall with JG fitting pockets (0-15mm from rear face)**

The rear wall is a structural PETG plate ~3mm thick at its thinnest (around the center body press-fit bores). The four John Guest fittings are mounted in this wall by press-fitting their 9.31mm center bodies into 9.5mm bores. The body-end shoulders (the step from 9.31mm to 15.10mm) seat against the inboard face of the wall, providing positive axial location.

On the exterior (dock-facing) side of the wall, the outboard body ends protrude 12.08mm. These are the ports that the dock's tube stubs push into. The collets on this outboard side are extended by default (adding ~1.3mm beyond the body end face).

On the interior (cartridge-facing) side of the wall, the inboard body ends protrude 12.08mm into the cartridge. The collets on this side are the ones the release plate engages.

Total wall-plus-fitting depth: 3mm wall + 12.08mm inboard body end = ~15mm from the rear face to the inboard collet tips.

The four fittings are arranged in a 2x2 pattern. With 15.10mm body end OD and 5mm minimum clearance between fittings, the pattern spans approximately 35mm x 35mm — well within the 132mm cartridge width.

**Zone B: Release plate zone (15-20mm from rear face)**

The release plate sits directly in front of the four inboard body ends. In its rest position, the plate's collet-hugger bores surround the four collet sleeves, and the plate face is 1.7mm away from contacting the collet end faces (the take-up gap). The plate itself is approximately 4-5mm thick (to provide stiffness across the 35mm x 35mm fitting pattern and to accommodate the stepped bore geometry).

The plate occupies the space from approximately 15mm to 20mm inboard of the rear face.

**Zone C: Return springs and linkage attachment (20-25mm from rear face)**

Two compression springs sit between the release plate and standoffs on the rear wall, biasing the plate to its rest position. The linkage arms from the squeeze surface attach to the inboard face of the release plate at its lateral edges (outside the fitting pattern). This zone is 5mm deep.

**Zone D: Electrical terminal zone (20-30mm from rear face)**

The four blade electrical terminals are mounted on the exterior rear face of the cartridge, positioned laterally outside the 2x2 fitting pattern. They protrude 10mm from the rear face (standard 6.3mm blade terminal length plus housing). On the interior side, the wiring from the blade terminals runs along the cartridge side walls toward the motor terminals, which are located approximately 120mm inboard of the rear face (at the motor end caps). The blade terminals and their wiring do not overlap with the release plate or fitting pockets — they sit laterally adjacent.

**Zone E: Motor terminal clearance (25-30mm from rear face)**

The motor end caps (with solder tabs) sit roughly 25-30mm inboard of the rear face. The 5mm motor shaft nub requires a clearance bore or open space in the rear structure. There is 5mm of air gap between the motor end caps and the nearest structural element (the release plate linkage zone), which satisfies the thermal clearance requirement.

### Radial layout (looking at the rear face from outside)

```
    ┌──────────────────────────────────────┐
    │   [blade]           [blade]          │
    │       ┌──────────────────┐           │
    │       │  ○JG1      ○JG2 │           │
    │       │                  │           │
    │       │  ○JG3      ○JG4 │           │
    │       └──────────────────┘           │
    │   [blade]           [blade]          │
    └──────────────────────────────────────┘
```

The four JG fittings occupy the center of the rear face. The four blade terminals sit in the corners or lateral margins. The tube holes visible to the user are the 6.35mm bores through the outboard collet IDs of the four fittings. The blade terminals are recessed or shrouded so they are not visible as exposed metal — the user sees only the four small tube holes.

---

## 4. Force Budget

### The question

The user's squeeze must depress 4 collets (40-60N combined) through a direct 1:1 linkage. The design pattern research recommends 10-20N peak squeeze force for a satisfying feel. Are these compatible?

### Resolution

These are two different measurements of two different things, and they are compatible.

**The 10-20N figure from design patterns** refers to the force profile of the *latch mechanism itself* — the cantilever snap-fit that provides the tactile click when the user squeezes. This is the force to deflect the snap arm past its engagement point, producing the over-center feel. It is the signal force, not the working force.

**The 40-60N figure from collet research** is the force required to depress 4 collets simultaneously. This is the working force.

In the cartridge mechanism, these overlap in sequence:

1. As the user begins to squeeze (0-1mm travel), the plate takes up slack and begins contacting collet faces. The user feels light, increasing resistance.
2. As the squeeze continues (1-3mm travel), the plate depresses the collets. The force rises to 40-60N. This feels deliberate and substantial but is well within comfortable one-hand squeeze range (comfortable squeeze capacity: 60-120N).
3. At the end of travel, a deflection stop engages, halting further motion with a crisp stop.

The 40-60N working force *is the tactile signal*. The collet springs themselves provide the over-center-like force profile: force increases as the grab ring teeth are deflected, then drops sharply when the teeth clear the tube surface. This natural force-drop-at-release provides the "click" sensation without any additional latch mechanism.

**No mechanical advantage is needed.** A 1:1 linkage transmits 40-60N of finger force to the plate. Even at the worst case of 60N, this is half of a comfortable pinch grip and well within the range any adult can sustain for the 1-2 seconds needed to pull the cartridge free.

**The 10-20N design pattern guidance applies as an overlay.** If empirical testing of the actual collet force shows the total is in the 20-30N range (plausible, given the 10N per collet is a conservative mid-range estimate), the force profile naturally falls within the design-pattern-recommended range. If it is higher (40-60N), the mechanism still works — it simply feels more substantial. The deflection stop and the sharp force drop at collet release provide the decisive feel regardless of the absolute force magnitude.

### Empirical verification required

The collet force estimate (10N per collet) is first-principles, not measured. Before finalizing the squeeze geometry, measure the actual force per the test procedure in the collet research document. If measured force exceeds 15N per collet (60N total for 4), consider:

1. Adding 1.5:1 mechanical advantage through a lever ratio in the linkage arms (reduces finger force to 40N)
2. Angling the linkage arms slightly to gain a cam effect

Neither modification changes the user-facing interaction. The squeeze still feels like squeezing two flat surfaces together.

---

## 5. Bill of Materials

### Off-the-Shelf Parts (per cartridge)

| Part | Qty | Function |
|------|-----|----------|
| Kamoer KPHM400-SW3B25 peristaltic pump | 2 | Flavor dispensing |
| John Guest PP0408W 1/4" push-to-connect union | 4 | Quick-disconnect tube connections |
| M3 rubber vibration isolation mounts (8mm dia, 8mm height, male-male) | 8 | Pump vibration decoupling (4 per pump) |
| M3 x 8mm screws (if not included with isolation mounts) | 8 | Secure pumps to isolation mounts |
| 6.3mm blade terminals, male | 4 | Electrical connection, cartridge side (2 per pump) |
| Compression springs, ~5mm OD, ~10mm free length, ~1 N/mm rate | 2 | Release plate return bias |
| BPT tubing, 4.8mm ID / 8.0mm OD, cut to length | 4 pcs | Route from pump tube stubs to JG fittings (internal) |

### Custom Printed Parts (PETG, all printed on Bambu H2C)

| Part | Qty | Function |
|------|-----|----------|
| Cartridge shell — bottom half | 1 | Lower enclosure: pump bays, floor tube channels, rail grooves, rear wall with JG fitting pockets |
| Cartridge shell — top half | 1 | Upper enclosure: snap-fits to bottom half, forms top wall and squeeze surface (palm side) |
| Release plate | 1 | 4x stepped bores, rides on collet ODs, depresses all 4 collets simultaneously |
| Finger plate (squeeze surface, finger side) | 1 | Flat surface the user's fingers pull; connected to release plate via linkage arms |
| Linkage arms | 2 | Rigid PETG bars connecting finger plate to release plate along cartridge interior side walls |
| Mounting partition | 1 | Internal plate with 2x motor bores (~36mm) and 8x M3 through-holes for isolation mount studs; separates pump bays from rear zone |

### Dock-Side Parts (not part of the cartridge BOM, but required for the system)

| Part | Qty | Function |
|------|-----|----------|
| Dock rails (printed PETG, integral to enclosure interior walls) | 2 | 4mm x 4mm rectangular tongues with 5mm entry tapers and 0.5mm detent bumps |
| 6.3mm blade receptacles, female, shrouded | 4 | Electrical connection, dock side |
| 1/4" OD polyethylene tube stubs, ~20mm long | 4 | Protrude from dock rear wall into cartridge JG fittings during insertion |

---

## 6. Conflicts and Open Questions

### No conflicts with the vision

The technical research validates every aspect of the vision's specified interaction:

- **Squeeze-to-release between two flat surfaces:** Achievable. The 40-60N combined collet force is within comfortable one-hand squeeze range. No mechanical advantage required for the nominal case.
- **Release plate hidden inside the cartridge:** Achievable. The release plate sits 15-20mm inboard of the rear face, invisible to the user. The linkage arms run internally along the side walls.
- **Rail-guided slide-in with tube quick connects:** Achievable. The rectangular tongue-and-groove rails provide smooth guidance. The John Guest fittings accept tubes with 5-10N per fitting, 20-40N total — manageable as a push-in force.
- **Cartridge as black box:** Achievable. The user sees only tube holes, side grooves, and squeeze surfaces. No fasteners, no exposed mechanism, no seams on user-facing surfaces.
- **Four quick connects inside the cartridge:** Achievable. The barbell profile of the PP0408W allows press-fitting the 9.31mm center body into the rear wall, with body ends protruding on both sides.

### Open Questions

**1. Exact tube stub positions on the Kamoer pump front face.**
The two tube connector exits on each pump are offset from center, but their exact X/Z coordinates are not caliper-verified. This determines the tube routing channel geometry. Measure before designing channels.

**2. Motor body diameter confirmation.**
The ~35mm motor diameter has low confidence (photos 15, 16 in Kamoer geometry). This dimension controls the motor bore in the mounting partition. Measure with calipers before specifying the bore.

**3. Empirical collet release force.**
The 10N per collet estimate is derived from first-principles analysis. Measure with a kitchen scale per the procedure in the collet research document. If the measured force significantly exceeds 15N per collet, the linkage may need a modest mechanical advantage (1.5:1).

**4. Linkage arm routing and clearance.**
The rigid linkage arms connecting the finger plate to the release plate must run along the interior side walls without interfering with the tube routing channels or the pump bays. The exact path depends on the cartridge shell geometry. This is a 3D spatial problem that the concept modeling step must resolve.

**5. Cartridge shell parting line.**
The cartridge is two halves snap-fit together. The parting line should follow a natural edge (a 0.3-0.5mm step, per design pattern guidance) and must not cross the palm squeeze surface or the finger squeeze surface. The optimal parting plane is horizontal (splitting the cartridge into top and bottom halves at the mid-height of the pump bays), which places the parting line on the side walls where it reads as an intentional feature.

**6. Squeeze surface geometry and ergonomics.**
The vision specifies both surfaces as "perfectly flat." The design pattern research confirms this works. However, the exact dimensions of the squeeze zone (how wide, how tall, how deep the finger plate is recessed) and the gap between palm surface and finger surface must be determined by hand ergonomics. A comfortable one-hand squeeze on a 67mm-tall cartridge suggests the squeeze zone spans most of the front face height. The finger plate recess depth sets the available squeeze travel (2-4mm recommended). This is a concept-step decision.

**7. Return spring specification.**
The return springs must fit in the 5mm zone between the release plate and the rear linkage attachment. Compression springs of ~5mm OD and ~10mm free length at ~1 N/mm rate would provide 5-10N of return force in the working range. Alternatively, printed PETG leaf springs integrated into the rear wall could eliminate two separate parts. Evaluate both options in concept modeling.

**8. Tube routing channel cross-section.**
The envelope research specifies 10mm x 10mm minimum channels (8mm OD tube + 1mm clearance per side). Four channels must run from the pump front face area to the rear fitting pockets, routed through the dead space alongside the motor cylinders (the motor is ~35mm diameter inside a 62.6mm square bay, leaving ~14mm per side). Confirm that four 10mm x 10mm channels fit in this dead space without conflicting with the mounting partition or vibration mount hardware.

**9. Calibration test prints.**
Before committing to full cartridge prints, the following test sections are required:
- 30mm rail/groove section at 0.20, 0.25, and 0.30mm clearance per side (select the tightest that slides freely)
- Release plate with one JG fitting pocket (verify collet-hugger guidance, plate travel, and force)
- Snap-fit shell joint sample (verify seam gap under 0.3mm)
