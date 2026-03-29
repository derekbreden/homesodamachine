# Design Decision: Pump Cartridge Mechanism

## Summary

**Recommendation: Rail-guided slide cartridge with squeeze-to-release collet actuation and blind-mate pogo pin electrical contacts.**

The cartridge slides into a dock on parallel T-rails. Insertion seats the fluid connections (4 John Guest fittings push onto tube stubs) and electrical connections (4 pogo pins contact copper pads) automatically. The John Guest collets provide all mechanical retention — the cartridge cannot be pulled out without releasing them. To remove, the user squeezes the front face of the cartridge (palm on the outer shell, fingers pull an inset release panel), which translates a release plate inward against the 4 collets, freeing the tubes. The user then slides the cartridge forward and out.

No lever, no button, no latch. The squeeze gesture is the entire release mechanism. Insertion is push-until-it-clicks. The mechanism is invisible when not in use.

---

## Alternatives Evaluated

### Candidate 1: Rail Slide + Squeeze-to-Release (Recommended)

Pattern A (rail-guided slide) from the design pattern research, with the release mechanism adapted from John Guest collet mechanics and the vision document's squeeze gesture.

**Guidance:** Parallel T-rails on the cartridge sides engage matching channels in the dock walls. The rails are tapered at the leading edge for self-centering. The rail cross-section prevents insertion in any incorrect orientation (keying). The rails handle X and Z alignment; Y is the slide axis (front-to-back).

**Locking:** The 4 John Guest collet grips ARE the lock. When the cartridge is fully seated, each tube stub has passed through a collet and an O-ring inside a JG union fitting. The collet teeth bite the tube. The cartridge physically cannot be removed without depressing all 4 collets. No spring latch, no detent, no secondary lock. The fluid connection IS the mechanical retention. This is the Keurig principle — connection and retention are the same event.

**Release:** The user squeezes the cartridge front face. Their palm pushes against the outer shell (which is rigidly connected to the fittings via the cartridge body). Their fingers pull an inset panel that is connected to the release plate. The release plate translates ~3mm rearward (toward the fittings), pressing on all 4 collet faces simultaneously. This opens the gripper teeth. With the squeeze maintained, the user slides the cartridge forward out of the dock.

**Electrical:** 4 spring-loaded pogo pins mounted on the dock rear wall contact 4 flat copper pads on the cartridge rear face. Connection is automatic at full insertion. No user awareness required.

**Feedback:**
- Tactile: firm resistance as 4 tubes push through collets and O-rings, then a definitive seat when tubes bottom out at the tube stops
- Audible: no click (JG fittings are silent), but the firm-then-done feel is unambiguous
- Visual: cartridge sits flush with the dock opening when properly seated; any protrusion means incomplete insertion
- Electrical: the S3 display shows cartridge state (inserted/locked, unlocked, removed) immediately via pogo pin continuity

### Candidate 2: Rail Slide + Lever-Assisted Seating

Pattern A guidance with a lever (Pattern B element) that provides mechanical advantage for the final seating stroke and cam-actuates the collet release.

**Why rejected:** The lever adds a visible moving part to the front of the device. The vision document is explicit that the mechanism must be hidden — the cartridge is a black box. A lever on the outside of the cartridge or dock violates surface integration. Additionally, the force required to seat 4 quarter-inch JG fittings simultaneously is well within hand-push range (each fitting requires moderate finger pressure; 4 simultaneously requires a firm palm push but nothing uncomfortable). A lever provides mechanical advantage that is not needed and adds complexity that degrades the UX.

**What would change this:** If the total insertion force for 4 simultaneous JG connections proved to be uncomfortably high (above ~80N / 18 lbf), a lever would become necessary. The collet-release research estimates 5-15N per collet for release; insertion force through the O-ring is similar. Four fittings: 20-60N total. This is within comfortable palm-push range. Test empirically.

### Candidate 3: Nest-and-Close with Lever/Cam

Pattern B. The cartridge drops into a cavity and a lever clamps it down.

**Why rejected:** The cartridge has 4 rear-facing fluid connections that must engage tube stubs in the dock. A nest-and-close (drop-in) pattern places the module perpendicular to the connection axis — the tubes would need to be on the bottom face, pointing downward. This constrains the plumbing layout severely and means the cartridge must be lowered vertically, which conflicts with the vision of a front-accessible cartridge at the bottom of the enclosure. The slide axis (front-to-back) naturally aligns the tube connections with the dock stubs.

### Candidate 4: Quarter-Turn Bayonet

Pattern D. Push in, rotate 90 degrees to lock.

**Why rejected:** The cartridge contains 4 fluid connections and 2 pumps. Rotating the entire assembly after insertion would torque the tubes. The JG fittings are inline unions — the tube stubs from the dock would need to accommodate rotation, requiring flexible loops. This adds complexity, potential failure points, and makes the tubes the weak link. The straight push-and-done gesture is superior for this geometry.

### Candidate 5: Magnetic Alignment

Pattern E. Magnets pull the cartridge into final position.

**Why rejected:** The cartridge weighs approximately 1.2 kg (two 504g pumps plus housing). Magnets strong enough to seat and retain a 1.2 kg module against tube insertion friction would be large and expensive. More critically, the magnets must not interfere with the DC motor operation. The magnetic field from retention magnets near two brushed DC motors is a reliability risk. Magnetic retention does not provide the positive lock that JG collets provide — a bump or vibration could unseat the cartridge. This is a fluid system under pressure; breakaway is a bug, not a feature.

---

## Detailed Mechanism Design

### Rail System

**Geometry:** Two T-shaped rails, one on each side of the cartridge, running the full depth of the cartridge body. The T-profile prevents separation in all directions except the slide axis (Y). The rail head (the crossbar of the T) faces inward on each side.

**Dimensions:**
- Rail width (crossbar of T): 8mm
- Rail stem height: 4mm
- Rail stem width: 4mm
- Clearance between rail and channel: 0.2mm per side (sliding fit per FDM tolerance guidelines)
- Rail length: full cartridge depth, ~160mm

**Lead-in:** The front 15mm of each rail tapers from 6mm to 8mm width (the crossbar narrows toward the front edge). The corresponding dock channel has a matching flared entry. This creates a funnel that guides the cartridge onto the rails even with 2-3mm of lateral misalignment. The taper also serves as the keying geometry — the cartridge cannot be inserted upside down because the T-rail profile is asymmetric top-to-bottom.

**Material:** Printed in PETG for the cartridge rails (good wear resistance, low friction). The dock channels are part of the enclosure interior and can be PLA or PETG.

**Surface integration:** The rails are inset grooves on the cartridge sides (per the vision document). From the outside, the cartridge appears as a simple rectangular box with two subtle grooves. The dock channel openings are inside the enclosure, not visible to the user.

### Fluid Connections — John Guest Union Fittings

**Configuration:** 4x PP0408W 1/4" union fittings mounted in the cartridge rear wall. Each fitting is press-fit by its 9.31mm center body into a 9.5mm bore in the rear wall. The 15.10mm body-end shoulders seat against the wall faces on each side, providing axial location. The fitting's barbell profile makes it self-locating: once pressed into the bore, it cannot translate axially.

**Layout (viewed from rear):**

```
    Cartridge rear face (user cannot see this)

    ┌──────────────────────────────────┐
    │                                  │
    │     ○ JG1-in      ○ JG2-in      │
    │                                  │
    │     ○ JG1-out     ○ JG2-out     │
    │                                  │
    │       [pogo]  [pogo]             │
    │       [pads]  [pads]             │
    └──────────────────────────────────┘
```

Each pump has one inlet fitting and one outlet fitting. The fittings are arranged in a 2x2 grid, centered on the rear wall, with ~25mm center-to-center spacing (sufficient for the 15.10mm body-end OD plus clearance plus release plate bore spacing).

**Dock side:** 4 tube stubs (1/4" OD PE tubing, ~20mm long) protrude from the dock rear wall, aligned with the 4 JG fittings. When the cartridge slides to full depth, each tube stub enters the outer port of its corresponding JG fitting, passes through the collet and O-ring, and bottoms out at the tube stop. The tube stubs are permanently installed in the dock — they never move.

**Alignment tolerance:** The rail system aligns the cartridge to within ~0.4mm laterally (0.2mm clearance per side). The JG fitting bore (6.69mm collet ID) accepts a 6.30mm tube with 0.39mm clearance. The rail alignment tolerance is within the fitting's acceptance window. No additional funnel geometry is needed at the fittings themselves, though a 1mm chamfer on each fitting pocket in the dock wall provides a visual guide for the tube stubs during assembly.

### Release Plate

**Function:** A flat plate inside the cartridge, positioned between the user-facing front wall and the JG fittings on the rear wall. The plate has 4 stepped bores aligned with the 4 fittings. When the plate translates rearward (toward the fittings), the bore faces contact the collet annular faces and push them inward, releasing the gripper teeth.

**Bore geometry (per fitting):**
- Innermost bore: 6.5mm diameter (between tube OD 6.30mm and collet ID 6.69mm) — this annular face contacts the collet end face
- Middle bore: 9.8mm diameter — hugs the collet OD (9.57mm) for lateral alignment, preventing off-axis push
- Outer bore: 15.5mm diameter — clears the body end OD (15.10mm)

**Stroke:** 3mm total travel. The collet requires ~1.3mm of compression to release. The 1.7mm margin accommodates manufacturing variation across the 4 fittings.

**Guide:** The release plate slides on 2 guide pins (smooth steel dowel pins, 3mm diameter) that pass through clearance holes in the plate and are press-fit into the cartridge rear wall. The pins keep the plate parallel to the rear wall throughout its stroke. Compression springs on the guide pins return the plate to its forward (non-releasing) position when the user lets go.

**Connection to user:** The release plate is connected to the inset front panel (the finger-pull surface) via 2 rigid links (printed rods or standoffs) that pass through clearance slots in the internal mounting plate. The user's fingers pull the front panel; the links pull the release plate rearward.

### Squeeze Gesture — The User Interaction

The front face of the cartridge has two surfaces:

1. **Outer shell face (palm surface):** The main front wall of the cartridge box. Rigid, flush with the dock opening. This is what the user's palm pushes against. It is connected to the cartridge body, which is connected to the JG fittings via the rear wall.

2. **Inset release panel (finger surface):** A recessed panel within the outer shell face, set back ~5mm from the outer surface. This panel is connected to the release plate via internal links. The recess provides a natural finger grip — the user's fingers curl into the recess and pull the panel toward them.

**Geometry of the inset panel:**
- Width: ~80mm (enough for 3-4 fingers of each hand)
- Height: ~30mm
- Recess depth: 5mm behind the outer shell face
- Travel: 3mm toward the user (pulling the release plate 3mm rearward)
- The panel edges have a 1mm radius for comfort

**The gesture:** The user wraps their hand around the cartridge front face. Palm on the outer shell. Fingers curled into the inset recess. Squeeze. The inset panel moves 3mm toward their palm. The release plate pushes the collets. The user then slides the cartridge forward out of the dock while maintaining the squeeze.

**For re-insertion:** The user simply slides the cartridge into the dock until it seats firmly. The tube stubs push into the JG fittings regardless of collet/release plate position. No squeeze needed. Insertion is always easier than removal (design principle 1 from the pattern research).

**Force budget:**
- 4 collets at 5-15N each = 20-60N total release force
- The squeeze gesture uses finger flexor muscles (grip strength), which can comfortably produce 100-200N
- The force is well within the comfortable range even for users with lower grip strength

### Electrical Connections

**Dock side:** A 4-pin spring-loaded pogo pin header mounted on the dock rear wall (or a small PCB attached to the dock wall). The pins are oriented along the Y axis (the slide direction), pointing forward toward where the cartridge rear face will be.

**Cartridge side:** 4 flat copper contact pads on the cartridge rear face. Each pad is ~4mm diameter, on 5.08mm (2x standard 2.54mm) pitch. The pads can be implemented as:
- A small PCB fragment (FR4 with exposed copper pads) epoxied into a pocket in the rear wall
- Copper tape squares applied to the rear wall surface
- Conductive paint dots (less reliable, not recommended)

**Pin assignment:**
- Pin 1: Pump 1 motor +
- Pin 2: Pump 1 motor -
- Pin 3: Pump 2 motor +
- Pin 4: Pump 2 motor -

**Contact reliability:** The pogo pins have 1-2mm of spring travel. The rail system positions the cartridge rear face within 0.4mm of nominal. The springs ensure solid contact across this tolerance range. The pogo pin wipe action (the pin tip slides slightly across the pad during the last mm of insertion) self-cleans oxidation.

**State detection:** The ESP32 can detect cartridge presence by measuring continuity or resistance across each motor pair. An open circuit means cartridge removed or not seated. This eliminates the need for a separate presence switch.

### Internal Tubing Routing

Inside the cartridge, each pump's tube stubs (BPT tubing from the barbed connectors) must route to the JG union fittings on the rear wall.

**Path:** Pump barbs face forward (toward the user). BPT tube stubs exit forward ~40mm, then curve rearward in a U-bend (minimum 25mm bend radius) and route along the cartridge side walls toward the rear. At the rear, each BPT stub connects via a brass barb reducer (8mm barb to 1/4" barb) to a short (~35mm) piece of 1/4" OD PE tube, which inserts into the internal port of the corresponding JG union fitting.

**Space budget:** The cartridge interior depth (pump face to rear wall) must be at least 80mm to accommodate the U-bend. With pumps ~48mm deep (head only, bracket at rear) and the pump head face ~40mm from the front wall (tube stub clearance), the total cartridge depth is approximately:
- Front wall: 3mm
- Tube stub zone + U-bend: 80mm
- Pump head depth: 48mm
- Bracket zone: 15mm
- Motor body: 63mm (behind bracket, protruding rearward)
- Rear wall with JG fittings: 20mm (wall + fitting protrusion)

Wait — the motors extend rearward from the bracket. The JG fittings are on the rear wall. The motors must not collide with the fittings or the release plate.

**Revised layout:** The pumps mount on an internal plate with pump heads forward and motors rearward. The mounting plate sits roughly at the cartridge's midpoint. The motor cylinders extend rearward and must clear the release plate and the JG fittings.

- Motor length behind bracket: ~63mm (including shaft nub)
- Release plate: ~5mm thick, positioned ~10mm in front of the JG fittings
- JG fitting internal protrusion from rear wall: ~20mm (half the fitting body)

The motor ends and the JG fittings/release plate occupy different lateral zones. The 4 JG fittings are clustered at center-bottom of the rear wall. The 2 motors are at center-left and center-right. With 48mm hole spacing on each pump and pumps side-by-side, the motors are laterally offset from the center JG cluster. This works if the JG fittings are positioned between and below the two motor cylinders.

**Total cartridge exterior dimensions (estimated):**
- Width: ~165mm (two 62.6mm pump heads + 15mm gap + 2x 12mm walls/rails)
- Height: ~80mm (62.6mm pump + 5mm grommets + 2x 5mm shell walls)
- Depth: ~200mm (front wall + tube zone + pumps + motors + rear wall)

These fit within the 220mm x 300mm x 400mm enclosure with room for the valves behind the cartridge dock.

### State Feedback Summary

| Event | Tactile | Audible | Visual |
|-------|---------|---------|--------|
| Cartridge slides onto rails | Smooth, guided motion | Quiet sliding | Cartridge aligns with dock opening |
| Tubes engage JG fittings | Firm, increasing resistance through 4 collets + O-rings | Faint friction sound | Cartridge approaching flush |
| Full seat | Resistance drops (past O-rings, at tube stops) | Silence | Cartridge flush with dock face |
| S3 display update | — | — | S3 shows "Cartridge OK" or pump icons |
| Squeeze to release | Firm spring resistance in the inset panel | Quiet | Inset panel moves 3mm |
| Cartridge slides out | Smooth, free motion (collets released) | Quiet sliding | Cartridge emerging from dock |

The dominant feedback is tactile: the firm-then-done feel of 4 JG connections seating simultaneously. This is not a click (JG fittings are silent), but it is unambiguous. The S3 display provides electronic confirmation.

---

## Bill of Materials (Per Cartridge)

| Part | Qty | Purpose |
|------|----:|---------|
| Kamoer KPHM400-SW3B25 peristaltic pump | 2 | The pumps being replaced |
| John Guest PP0408W 1/4" union fitting | 4 | Fluid connections (2 per pump: inlet + outlet) |
| M3 x 10mm socket head cap screw, stainless | 8 | Pump mounting (4 per pump) |
| M4 rubber grommet isolator (barrel type, 40-60 Shore A) | 8 | Vibration isolation at pump mounts |
| Brass barb reducer, 8mm barb to 1/4" barb | 4 | BPT-to-PE tube transition |
| 1/4" OD semi-rigid PE tube, cut to ~35mm | 4 | Adapter stubs into JG fittings |
| 3mm x 40mm steel dowel pin | 2 | Release plate guide pins |
| Compression spring, 3mm ID x 8mm free length | 2 | Release plate return springs |
| Small PCB or copper tape pads (4x 4mm pads) | 1 | Electrical contact surface |
| 22 AWG wire, ~150mm lengths | 4 | Internal motor wiring to contact pads |

**Dock-side (installed once, not replaced with cartridge):**

| Part | Qty | Purpose |
|------|----:|---------|
| 4-pin spring-loaded pogo pin header | 1 | Electrical connection to cartridge |
| 1/4" OD PE tube stubs, ~20mm, permanently installed | 4 | Tube stubs that mate with JG fittings |

**Printed parts (PETG):**

| Part | Qty | Purpose |
|------|----:|---------|
| Cartridge shell (2-piece, top + bottom) | 1 set | Outer housing, rail features, front face with inset recess |
| Internal mounting plate | 1 | Pump mount surface with grommet bores |
| Release plate | 1 | 4x stepped bores, guide pin holes, link attachment |
| Inset release panel | 1 | Finger-pull surface, connected to release plate via links |
| Release plate links (2x rigid standoffs) | 2 | Connect inset panel to release plate |
| Dock rail channels (integrated into enclosure) | 2 | Receive cartridge rails |
| Dock rear wall / pogo pin mount | 1 | Tube stubs + pogo pin header mount |

---

## What Would Change This Recommendation

1. **Insertion force too high.** If empirical testing shows that pushing 4 JG fittings onto tube stubs simultaneously requires more than ~80N (uncomfortable palm push), add a cam lever to the dock that provides mechanical advantage for the final 15mm of travel. This would shift the design toward the server drive bay pattern (Candidate 2) without changing the rail guidance or collet release. Test with a bathroom scale: push the cartridge against the scale to measure seating force.

2. **Collet release force too high or uneven.** If one or more collets require significantly more force than others (manufacturing variation), the release plate may tilt on its guide pins, releasing some collets but not all. Mitigation: add a third guide pin for over-constrained parallelism, or use a thicker (stiffer) release plate. Test by depressing all 4 collets with a flat plate in a bench vise.

3. **Tube alignment fails.** If the 0.39mm clearance between tube OD and collet ID is insufficient given rail tolerance stack-up, the tubes will not enter the fittings during insertion. Mitigation: add small funnel cones (printed, 2mm lead-in taper) to the cartridge rear wall around each fitting port, effectively increasing the acceptance window. Test by attempting insertion with the cartridge deliberately offset to one side of the rail clearance.

4. **Pogo pin contact unreliable.** If vibration during pump operation causes intermittent pogo pin contact (motor stutter), switch to blade/wiper contacts which have higher contact area and friction-based retention. Alternatively, add a very small magnetic element near the pogo pins (away from the motors) to increase contact force.

5. **Cartridge weight makes squeeze-while-sliding awkward.** If users find it difficult to maintain the squeeze grip while simultaneously sliding a 1.2kg cartridge forward, add a spring-assist ejector (a small compression spring at the dock rear wall that pushes the cartridge forward ~10mm once the collets are released, so the user only needs to squeeze and the cartridge pops out enough to grab).

6. **Mounting hole spacing.** The pump-mounting research notes a discrepancy: the Kamoer datasheet says 50mm center-to-center while caliper measurements suggest 48mm. The caliper-verified geometry document uses 48mm (user-verified). The internal mounting plate should be designed with slotted holes (48-50mm range) until this is resolved with a definitive measurement, or simply test-print a plate at 48mm first.
