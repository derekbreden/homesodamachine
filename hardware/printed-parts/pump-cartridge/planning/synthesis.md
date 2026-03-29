# Pump Cartridge Mechanism -- Synthesis

This document combines all technical and UX research into a single execution plan for the pump cartridge. The cartridge executes the interaction described in vision.md Section 3: a palm-up squeeze of two flat surfaces releases four quick connects, allowing the cartridge to slide off its dock rails.

---

## 1. Complete Mechanism Description

### What the user sees

The cartridge is a rectangular block with these external features and nothing else:

- **Front face:** Two flat surfaces separated by a narrow gap. The outer surface (palm side) is the cartridge body. The inner surface (finger side) is the exposed edge of the release plate. Both are flat, both are inset 1-2 mm from the surrounding shell so the user's fingertips and palm naturally find them. The finger surface is visually distinct from the palm surface -- either a different texture (e.g., fine horizontal ribs at 0.8 mm pitch printed into the face-down build plate surface) or a subtle color difference if dual-extrusion is used.
- **Sides:** Inset rail grooves that mate with matching T-profile rails on the enclosure dock. The grooves run the full depth of the cartridge along the insertion axis.
- **Rear face:** Four holes, each barely larger than 1/4" OD tubing (approximately 7.5 mm diameter in the shell), arranged in a compact pattern. These are the only openings into the interior.
- **No visible screws, no seams wider than 0.3 mm, no mechanism components visible from any angle.**

### What is inside

Working from rear to front:

1. **Quick connect fittings (x4).** John Guest PP1208W bulkhead unions (or PP0408W unions press-fit into a printed mounting block) are mounted in a rigid rear bulkhead inside the cartridge. Their collet faces point toward the front of the cartridge (toward the user). The tube stubs from the enclosure dock enter through the rear shell holes and push into these fittings during insertion. The four fittings are arranged in a rectangular pattern at minimum 17 mm center-to-center spacing.

2. **Release plate.** A rigid flat plate with four 7.0-7.5 mm through-holes aligned with the four fittings. The plate sits between the fittings and the user, with its flat face contacting the four collet faces simultaneously. The plate rides on two guide pins (or guide slots in the cartridge shell walls) that constrain it to pure axial translation -- no tilt, no rotation. The guide features maintain perpendicularity to within 0.3 mm across the plate face.

3. **Return springs (x2).** Compression springs sit between the release plate and a forward internal wall, biasing the plate away from the collets (toward the user). When the user is not squeezing, the springs hold the plate clear of the collets, and the collets grip the tubes normally. The springs also provide the rising force profile during squeeze -- force increases as the user compresses them, peaking just before the collets release.

4. **Over-center detent.** A small snap feature (printed cantilever arm with a 1.5 mm bump engaging a matching groove on the release plate travel path) creates a force peak at 60-80% of squeeze travel, followed by a sharp force drop as the detent snaps past. This produces the crisp "click" at the moment the collets fully release. The detent does not latch -- it is a bump the plate passes over in both directions, providing a click on both squeeze and release.

5. **Pump mounting surface.** A rigid internal plate (minimum 1.2 mm wall, structurally 2-3 mm with ribs) spans the cartridge interior. Two Kamoer KPHM400 pumps mount to this plate via their M3 screw patterns (48 mm square, 4 screws each). The plate has two 36.4 mm bore holes for the motor cylinders to pass through. The pumps are oriented with their tube connectors facing forward (toward the fittings) and their motors facing rearward. Short lengths of silicone tubing connect the pump barb connectors to the quick connect fittings.

6. **Electrical connection.** A 2-pin or 4-pin connector (one pair per pump) on the cartridge body mates with a matching connector on the dock. This carries 12V DC at up to 1.4A total. The connector must be a blind-mate type that engages automatically during cartridge insertion. Position: on the rear bulkhead or bottom face, aligned so that rail-guided insertion ensures alignment.

### The squeeze-release interaction, step by step

**Removal:**
1. User reaches to the front-bottom of the enclosure, wraps one hand around the cartridge front face, palm up. Palm contacts the outer (body) surface; four fingers curl upward and contact the inner (release plate) surface.
2. User squeezes. The release plate translates 4-5 mm toward the collets, compressing the return springs. Force rises smoothly from 0 to approximately 15-20 N.
3. At 3-4 mm of travel, the over-center detent engages: force peaks, then drops sharply with an audible click. At this point the plate has depressed all four collets by 3 mm, fully retracting the stainless steel teeth.
4. With collets released, the user pulls the cartridge forward (toward themselves) along the rails. The four tube stubs slide out of the quick connects with near-zero friction. The cartridge slides off the dock rails and is free.
5. User releases squeeze. Return springs push the release plate back to its rest position. The over-center detent clicks again on the return stroke.

**Insertion:**
1. User aligns cartridge rail grooves with dock rails. Chamfered rail entries (2 mm x 30 degrees on the dock rails) and chamfered tube stub ends (1-2 mm x 30-45 degrees) provide self-centering in the final 5-10 mm of approach.
2. User pushes the cartridge rearward along the rails. The four tube stubs enter the quick connect fittings, passing through the release plate holes, through the collets, past the O-rings, to the tube stops. The collet teeth grip the tubes automatically -- no user action needed.
3. In the last 3-5 mm of insertion travel, a retention latch (spring-loaded printed cantilever on the dock or cartridge side) deflects and then snaps into a notch with an audible click. This click confirms: tubes are fully seated in the fittings AND cartridge is mechanically retained. These two events are synchronized by geometry -- the latch notch position is set so that it engages at the exact insertion depth where tubes reach the tube stops (15-16 mm past the collet face).
4. The cartridge face sits flush with the enclosure dock surface, providing visual confirmation.

---

## 2. Force Budget Resolution

### The question

The user must depress 4 collets simultaneously. Does the user's available squeeze force exceed the required collet release force?

### The numbers

| Parameter | Value | Source |
|-----------|-------|--------|
| Collet release force per fitting (conservative) | 15 N | Quick connect research, worst case |
| Total collet release force (4 fittings) | 60 N | 4 x 15 N |
| With 1.5x aging safety factor | 90 N | Quick connect research |
| Return spring force (2 springs, at full compression) | 5-10 N total | Chosen to provide feel without adding significant load |
| Over-center detent force | 2-3 N peak | Small printed cantilever |
| Total mechanism resistance at peak | 67-103 N | Collets + springs + detent |
| User available squeeze force (5th %ile older female) | 42 N | Squeeze ergonomics research |
| Target user squeeze force (comfortable) | 10-20 N | 20-30% MVC of weakest user |

### The conflict

**There is a direct conflict between the vision and technical feasibility at 1:1 mechanical advantage.** At worst case (90 N mechanism resistance), the weakest target users (42 N capacity) cannot operate the mechanism at all, let alone comfortably. Even at the nominal 60 N, operating at 60 N requires 100% of the weakest user's maximum voluntary contraction -- completely unacceptable for a consumer product.

### Resolution: mechanical advantage from squeeze geometry

The squeeze mechanism inherently provides mechanical advantage because the user's finger travel (squeeze span compression) is greater than the release plate travel (collet depression distance).

**Geometry:**
- Squeeze span at rest: 40-45 mm (distance between palm surface and finger surface)
- Squeeze span at release: 35-40 mm (after 4-5 mm of compression)
- Release plate travel: 3-4 mm (the collet depression distance)
- User finger travel: 4-5 mm (the squeeze compression distance)

At a direct 1:1 linkage (fingers pull the release plate directly), the mechanical advantage is only ~1:1 because finger travel roughly equals plate travel. **This is insufficient.**

**Required mechanical advantage:**
- To keep user force at 15 N (comfortable midpoint) while overcoming 60 N of collet resistance plus 8 N of spring/detent resistance = 68 N total:
- Required MA = 68 / 15 = **4.5:1**
- To handle 90 N worst case at 20 N user force:
- Required MA = 90+8 / 20 = **4.9:1**

**Achieving this with a lever mechanism:**

The release plate is not directly connected to the finger surface. Instead, a lever (or pair of levers) pivots inside the cartridge:

- The finger surface is the long arm of the lever, extending 20-25 mm from the pivot.
- The short arm contacts the release plate, extending 4-5 mm from the pivot.
- Lever ratio: 20-25 mm / 4-5 mm = **4:1 to 6.25:1 mechanical advantage.**
- At 5:1 MA, a 15 N finger pull produces 75 N at the release plate -- sufficient for the nominal 60 N case with margin.
- At 5:1 MA, a 20 N finger pull produces 100 N -- sufficient for the 90 N worst case.

**Trade-off:** The lever converts finger travel to plate travel at the inverse ratio. For 3 mm of plate travel at 5:1 MA, the finger surface must travel 15 mm. This is within the 3-6 mm travel recommendation from the design pattern research only if we measure at the release plate, not at the finger. The user's fingers move 15 mm, which is at the upper end of satisfying travel for a squeeze (the design pattern research notes over 8 mm feels laborious for repeated use).

**Minimum modification to the vision:** The vision specifies two flat surfaces that squeeze together. The lever mechanism preserves this -- the finger surface is still flat, the palm surface is still flat, and the lever pivot and short arm are entirely hidden inside the cartridge. The only visible change is that the finger surface travel is 12-15 mm instead of 3-6 mm. This is acceptable because:
1. The cartridge is removed infrequently (pump replacement, perhaps 1-2 times per year at most).
2. A 15 mm travel with a peak-and-drop force profile at a low 15-20 N still feels deliberate and satisfying, not laborious. It is comparable to a robust lever-latch, not a toggle switch.
3. The force is very low throughout, so the longer travel does not cause fatigue.

**If physical testing reveals the collet release force is at the low end of the estimate (5-8 N per fitting, or 20-32 N for four), the lever ratio can be reduced to 2-3:1, bringing finger travel down to 6-9 mm -- right in the sweet spot.** The lever geometry should be adjustable (pivot position set by a pin that can be repositioned in one of 2-3 holes) to allow tuning after measuring actual collet forces.

---

## 3. Critical Dimensions

### Cartridge exterior envelope

| Dimension | Value | Constraint |
|-----------|-------|-----------|
| Width (X) | 150-160 mm | Two pumps side by side at 72-75 mm center-to-center + shell walls (2 x 3 mm) + rail groove depth (2 x 5 mm) |
| Depth (Y, insertion axis) | 160-175 mm | Pump depth (~150-170 mm front of tubes to rear of motor nub) + release plate space (~10 mm) + shell walls |
| Height (Z) | 70-80 mm | Pump head height (62.6 mm) + shell walls (2 x 3 mm) + clearance |
| Weight (pumps alone) | 612 g | Two Kamoer KPHM400 at 306 g each |

The enclosure is 220 mm wide and 300 mm deep. The cartridge at 155 mm wide and 170 mm deep fits comfortably at the front-bottom position.

### Squeeze interface dimensions

| Parameter | Value | Basis |
|-----------|-------|-------|
| Squeeze span (palm to finger surface, at rest) | 40-45 mm | Ergonomics research sweet spot for near-max force generation |
| Finger surface travel | 12-15 mm (adjustable with lever ratio) | 5:1 MA x 3 mm plate travel; reducible to 6-9 mm if collet forces are low |
| Finger surface width | 60-70 mm | 4-finger engagement width from ergonomics research |
| Finger surface depth (exposed edge height) | 12-15 mm | Finger pad depth from ergonomics research |
| Palm surface width | 60-70 mm | Matching finger surface |
| Palm surface height | 40-50 mm | Central palm + thenar eminence coverage |
| Inset depth of squeeze surfaces | 1.5-2 mm | Design pattern research: deep enough to feel, shallow enough to read as part of surface |

### Release plate dimensions

| Parameter | Value | Basis |
|-----------|-------|-------|
| Plate travel (axial, toward collets) | 3-4 mm | Collet depression: 2 mm nominal + 1 mm margin |
| Through-hole diameter (x4) | 7.0-7.5 mm | Clears 6.35 mm tube, contacts ~10.5 mm collet face |
| Contact annulus width | ~1.5-1.75 mm radial | (10.5 - 7.0) / 2 = 1.75 mm per side |
| Plate thickness | 3 mm minimum | Rigidity under 60-90 N distributed across 4 points |
| Guide feature clearance | 0.2 mm per side | Sliding fit per FDM constraints |

### Quick connect fitting layout

| Parameter | Value | Basis |
|-----------|-------|-------|
| Fitting type | John Guest PP1208W bulkhead union, 1/4" | Panel-mount, food grade |
| Mounting hole diameter | 17.0 mm | Per JG spec |
| Minimum center-to-center | 17 mm | 11 mm collet contact OD + 6 mm structural wall |
| Pattern | Rectangular, 2x2 | Two pumps, each with inlet and outlet |
| Tube insertion depth | 15-16 mm | Per JG spec for 1/4" OD |
| Collet depression distance | 2-3 mm | JG research; design for 3 mm |
| Collet release force per fitting | 5-15 N (design to 15 N) | JG research, conservative |

### Pump mounting

| Parameter | Value | Basis |
|-----------|-------|-------|
| Pump model | Kamoer KPHM400-SW3B25 | Existing BOM |
| Qty | 2 | One per flavor |
| Mounting screw pattern | 48 mm x 48 mm square, M3 | Caliper-verified |
| Motor bore in mounting plate | 36.4 mm diameter | 35 mm motor + 0.5 mm clearance/side + 0.2 mm FDM comp/side |
| Through-hole diameter for M3 | 3.4 mm | 3.2 mm + 0.2 mm FDM compensation |
| Pump center-to-center (side by side) | 72-75 mm | 68.6 mm bracket width + 3-6 mm gap |
| Clearance forward of pump head | 30 mm minimum | Tube barb connector routing |
| Clearance behind mounting plate | 70 mm | Motor body + shaft nub |

### Rail interface

| Parameter | Value | Basis |
|-----------|-------|-------|
| Rail profile | T-slot or dovetail | Single-axis constraint, no other DOF |
| Rail groove depth in cartridge | 3-5 mm | Sufficient engagement for cartridge weight (~800-900 g total) |
| Rail clearance | 0.2 mm per sliding face | FDM sliding fit tolerance |
| Rail entry chamfer (dock side) | 2 mm x 30 degrees | Self-centering per design pattern guidance |
| Keying | Asymmetric rail position or different left/right groove depth | Prevents wrong-orientation insertion |

---

## 4. UX Specification

These details are drawn from the design pattern research and must be carried through to concept and CAD.

### Feedback cues

| Event | Tactile | Audible | Visual |
|-------|---------|---------|--------|
| Squeeze-to-release | Force rises, peaks at 60-80% travel, drops sharply | Click from over-center detent at release point | -- |
| Cartridge slides free | Smooth, low-friction glide on rails | -- | Cartridge separates from dock |
| Insertion glide | Smooth rail engagement, self-centering in last 5-10 mm | -- | Rails guide alignment |
| Full seating | Force ramp in last 3-5 mm (latch deflection + tube push-in), then snap | Click from retention latch | Cartridge face flush with dock surface |

### Surface treatments

- **All external surfaces:** Same material, same finish. Print orientation chosen so user-facing surfaces are build-plate surfaces (smoothest FDM finish).
- **Squeeze finger surface:** Fine texture (horizontal ribs, 0.4-0.8 mm pitch) to differentiate from smooth body. Alternatively, if using ABS or ASA, the finger surface can be vapor-smoothed differently from the body.
- **Squeeze palm surface:** Smooth, matching the rest of the cartridge body.
- **Seam gaps between shell halves:** 0.3 mm maximum. Seams oriented so they run along edges, not across flat faces.
- **No visible fasteners** on any external surface. Shell halves joined by internal snap fits.
- **Rail grooves:** Smooth interior for low friction. Can be lightly lubricated with silicone grease at assembly.

### Tolerance targets

| Interface | Target | Method |
|-----------|--------|--------|
| Shell half seam gap | 0.3 mm max | Snap fit with alignment pins |
| Rail sliding fit | 0.2 mm clearance per face | Calibrate with test prints |
| Release plate guide fit | 0.2 mm clearance per face | Calibrate with test prints |
| Lever pivot | 0.15 mm clearance on pin | Printed pin in printed bore, or metal pin |
| Quick connect hole in rear shell | +0.3 mm over fitting OD | Press fit or light interference for bulkhead union |
| Retention latch engagement | 1.5-2 mm hook depth | Per design pattern research (min 1.5 mm for clear tactile boundary) |

---

## 5. Bill of Materials (Purchased Components Only)

| Component | Specification | Qty | Purpose |
|-----------|--------------|-----|---------|
| John Guest PP1208W bulkhead union, 1/4" | Polypropylene, EPDM O-ring, food grade | 4 | Quick connect fittings in cartridge rear bulkhead |
| M3 x 8 mm socket head cap screw | Stainless steel | 8 | Pump mounting (4 per pump), accessed from motor side |
| M3 nylon-insert lock nut | Stainless steel | 8 | Pump mounting, vibration resistance |
| Compression spring | ~5 mm OD, ~10-15 mm free length, ~1-2 N/mm rate | 2 | Release plate return bias |
| Steel dowel pin | 3 mm diameter, 20-25 mm long | 2 | Release plate guide pins (metal for wear resistance and low friction; alternatively, lever pivot pins) |
| Silicone tubing | 4.8 mm ID / 8 mm OD (matching pump BPT spec), food grade | ~300 mm | Connect pump barb connectors to quick connect fittings inside cartridge |
| 1/4" OD polyethylene tubing | John Guest compatible, food grade | ~100 mm | Short tube stubs in the quick connect fittings if not using the device's continuous tube runs |
| Electrical connector pair | 2-pin or 4-pin, blind-mate, rated 2A at 12V minimum | 1 | Cartridge-to-dock power connection for 2 pump motors |
| Silicone grease (PTFE-free, food grade) | Small quantity | -- | Rail lubrication, release plate guide lubrication |

**Notes on the BOM:**
- The printed cartridge shell (2 halves), release plate, lever arms, internal mounting plate, retention latch, over-center detent, and guide features are all printed parts, not purchased.
- The Kamoer pumps are already in the project BOM (requirements.md) and are not repeated here.
- M3 lock nuts are specified instead of thread locker because the cartridge is designed to be disassemblable (pumps are the replaceable element).

---

## 6. Conflicts Between Vision and Feasibility

### Conflict 1: Squeeze force vs. collet release force (RESOLVED above)

**Vision says:** User squeezes two flat surfaces to release collets.
**Technical finding:** 4 collets at up to 15 N each = 60-90 N required, but comfortable user squeeze is 10-20 N.
**Resolution:** Internal lever mechanism with 4-6:1 mechanical advantage. Both surfaces remain flat. The lever is entirely hidden inside the cartridge. The only user-perceptible change is that finger travel increases from 3-6 mm to 12-15 mm (or less if collet forces measure lower than conservative estimates).

### Conflict 2: Squeeze travel vs. design pattern "sweet spot" (MINOR)

**Design pattern research says:** 3-6 mm travel feels deliberate; over 8 mm feels laborious.
**Mechanism requires:** 12-15 mm finger travel at 5:1 lever ratio.
**Assessment:** The 3-6 mm guideline is derived from frequently-used controls (keyboard switches, buttons pressed many times per day). The cartridge release is performed perhaps 1-2 times per year. At 15-20 N force (very light), 15 mm of travel will feel like operating a smooth latch, not a laborious lever. This is a minor concern, not a blocking conflict. If actual collet forces allow a 3:1 lever ratio, travel drops to 9 mm, which is within tolerance.

### No other conflicts identified.

The vision's specified interaction (flat surfaces, hidden mechanism, slide on rails, 4 quick connects inside, palm-up squeeze) is technically achievable with the lever modification described above.

---

## 7. Open Questions

These are technical details the research did not fully resolve. They must be addressed during concept development, prototyping, or physical measurement.

1. **Actual collet release force.** The 5-15 N estimate per fitting is based on inference, not measurement. Before finalizing the lever ratio, measure the actual force on a PP1208W or PP0408W fitting with a spring scale. This single measurement determines whether the lever ratio needs to be 3:1 (low force) or 6:1 (high force), which significantly affects finger travel distance and internal packaging.

2. **Lever pivot packaging.** The lever arms must fit between the release plate and the squeeze surfaces, within the ~40-45 mm squeeze span. The pivot pins, lever arms, and their clearance envelopes need to be laid out in 3D to confirm they fit without conflicting with the pumps, fittings, or tubing. This is a concept-step problem.

3. **Electrical connector type and position.** The blind-mate connector must engage reliably during rail-guided insertion, tolerate the 0.2 mm rail clearance without binding, and carry 1.4A at 12V. Specific connector selection (pogo pins, blade contacts, or a commercial blind-mate connector) is deferred to the concept step.

4. **Over-center detent force tuning.** The printed cantilever that produces the click must be tuned for the right snap force (2-5 N) and feel. This is material-dependent (ABS/ASA will be crisper than PETG) and geometry-dependent (arm length, bump height, arm thickness). Expect 2-3 test-print iterations to get the feel right.

5. **Tube routing inside the cartridge.** Four short silicone tube runs connect the pump barb connectors to the four quick connect fittings. The routing must avoid kinking (minimum bend radius for 4.8 mm ID / 8 mm OD silicone tubing is approximately 15-20 mm) and must not interfere with the release plate travel or lever mechanism. This is a 3D packaging problem for the concept step.

6. **Retention latch synchronization with tube seating.** The retention latch must click at the exact insertion depth where tubes reach the tube stops (15-16 mm past the collet face). This synchronization is set by the latch notch position on the cartridge body relative to the quick connect fitting positions. Tolerance stack-up (fitting position tolerance + tube stop depth tolerance + latch notch position tolerance) must keep the latch engagement within +/- 1 mm of the ideal position. This needs analysis during specification.

7. **Cartridge shell split line.** The shell must split into two halves for assembly, but the seam must not cross any user-facing flat surface (squeeze surfaces, rail grooves). The most likely split is a horizontal plane through the cartridge midline, with the seam running along the side edges. This avoids seams on the top/bottom flat faces but puts them on the sides, which are partially hidden by the dock when inserted. Confirm during concept that this split allows all internal components to be assembled before closing.

8. **Print orientation.** The squeeze surfaces (palm and finger) should be printed face-down for smoothest finish. If the cartridge shell splits horizontally, each half can be printed with its external face on the build plate. Confirm that this orientation satisfies the FDM overhang constraints for all internal features (snap fits, guide slots, lever pivot bosses).

9. **Cartridge weight and center of gravity.** Total cartridge mass will be approximately 800-1000 g (612 g pumps + printed shell + fittings + hardware). The center of gravity is rearward (heavy motors at the back). Confirm the rail engagement is sufficient to prevent the cartridge from sagging or binding during insertion when the user releases their grip.
