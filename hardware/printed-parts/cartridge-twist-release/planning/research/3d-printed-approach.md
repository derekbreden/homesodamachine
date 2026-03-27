# All-3D-Printed Twist-Release Mechanism: Research

Research for a fully 3D-printed screw/twist release mechanism for the pump cartridge dock. The goal is to eliminate hardware-store fasteners (bolts, nuts, threaded rod) and print the entire mechanism on a Bambu Lab H2C.

## Context Recap

- Release plate: 59W x 47H x 6D mm, 4 stepped bores, 2x2 grid (40mm H x 28mm V spacing)
- Required plate travel: ~3mm
- Threaded strut spans ~122mm through 4mm PETG rear wall
- Cartridge envelope: 148W x 130D x 80H mm
- Knob on front face, plate on dock side of rear wall
- Monthly swap frequency, ~36 cycles over 3 years
- Potable water contact possible (clean cycle); must be food-safe where exposed

---

## 1. Printed Thread Feasibility

### Thread Profile: Trapezoidal/ACME over Metric V-Threads

Standard ISO metric threads have 60-degree V-profiles with sharp crests and roots. These are problematic for FDM because:
- The sharp 60-degree flanks create overhangs that sag or deform layer-by-layer
- Fine pitches (e.g., M10x1.5) push against FDM resolution limits
- Thread crests round off, reducing engagement area

**Trapezoidal (ACME) threads are strongly preferred for FDM.** Their 29-degree flank angle and flat crests/roots produce geometry that is stable during layer-by-layer construction and results in stronger mating surfaces. The flat root and crest also mean more contact area per thread, which distributes load better on soft plastic.

### Minimum Practical Thread Size

For FDM printing, the practical floor depends on nozzle size and layer height:

| Thread Size | Pitch | Printable? | Notes |
|---|---|---|---|
| M8 x 1.25 | 1.25mm | Marginal | Minimum for functional threads on 0.4mm nozzle |
| M10 x 1.5 | 1.5mm | Good | Reliable with 0.2mm layers |
| M12 x 1.75 | 1.75mm | Excellent | Comfortable margin, recommended starting point |
| Tr12x3 (trap.) | 3mm | Excellent | Better profile for FDM than metric |
| Tr16x4 (trap.) | 4mm | Excellent | Very robust, easy to print |

**For this application, Tr12x3 or Tr16x4 trapezoidal threads are recommended.** The strut diameter should be at least 12mm for a 122mm span anyway (see buckling analysis below), so thread size aligns naturally with structural needs.

### Multi-Start Threads

The release only needs ~3mm of linear travel. With a single-start Tr12x3, that is exactly 1 full turn. Options:

| Configuration | Lead | Turns for 3mm | Printability |
|---|---|---|---|
| 1-start, 3mm pitch | 3mm | 1.0 turn | Easy |
| 2-start, 3mm pitch | 6mm | 0.5 turn | Good — half turn to lock |
| 2-start, 4mm pitch | 8mm | 0.375 turn | Good — ~135 degrees |
| 4-start, 3mm pitch | 12mm | 0.25 turn | Marginal — thread depth reduces |

**A 2-start trapezoidal thread with 3mm pitch (6mm lead) is the sweet spot.** Half a turn for full engagement is fast for one-handed operation, and 2-start threads print well because the helix angle is still moderate enough that layer-by-layer buildup remains clean. A 4-start thread reduces per-thread depth excessively at M12 diameters — each thread groove becomes too shallow for reliable engagement in plastic.

### Print Orientation

**Strut (external/male thread):** Must print vertically (standing on end). Vertical orientation keeps the thread profile in the XY plane where the printer has its highest resolution. Threads printed horizontally produce stairstepping on the flanks that prevents smooth engagement. On a 122mm strut, vertical printing is straightforward — well within the H2C's Z height.

**Knob (internal/female thread):** Also print vertically (knob face down or up). The internal thread is formed by the perimeter walls in each layer. With trapezoidal threads at 3mm pitch and 0.12-0.16mm layer height, each pitch spans 19-25 layers — more than enough resolution to capture the profile.

### Tolerance and Clearance

For printed male-female thread pairs, radial clearance is critical:

- **Minimum radial clearance: 0.2mm per side (0.4mm on diameter)**
- **Recommended: 0.3mm per side (0.6mm on diameter)** for smooth operation without post-processing
- This means: if the male thread major diameter is 12.0mm, model the female thread minor diameter at 12.6mm

Additional recommendations:
- Print a test nut-and-bolt pair first (5-minute print) to dial in clearance for your specific filament and profile
- Apply a thin coat of food-safe silicone grease on threads for smoother operation and reduced wear
- Layer height of 0.12-0.16mm for thread sections (can use variable layer height — coarse for smooth shaft sections, fine for threads)

### Layer Adhesion and Thread Shear Resistance

On a vertically printed thread, the shear force from tightening acts across layers. This is the weakest axis for FDM parts. Mitigation:

- Use 4+ perimeters (walls) — perimeters are the structural backbone of threads, far more important than infill
- Trapezoidal threads distribute load over wider flanks than V-threads
- PETG and PA-CF have better interlayer adhesion than PLA
- The loads here are very low: the plate only needs to move 3mm against light spring pressure (~2-5N total), so thread shear stress is negligible

---

## 2. Material Selection

### Material Comparison for This Application

| Property | PETG | PETG-CF | PA-CF | ASA |
|---|---|---|---|---|
| Food safety | Good (base resin FDA listed) | Uncertain (CF additive) | Poor (moisture absorbs, additives) | Poor (styrene) |
| Layer adhesion | Very good | Good | Excellent | Good |
| Thread wear resistance | Moderate | Good | Excellent | Moderate |
| Moisture sensitivity | Low | Low | High | Low |
| Print difficulty | Easy | Moderate (hardened nozzle) | Hard (dry box, hardened nozzle, enclosure) | Moderate (enclosure) |
| Stiffness | Moderate | High | Very high | Moderate |
| Cost | Low | Moderate | High | Low |

### Recommended Material Strategy

**Primary recommendation: All PETG.** Rationale:
- Food-safe where it matters (the strut passes through the water-contact zone during clean cycles)
- 36 cycles over 3 years is low enough that PETG thread wear is not a concern
- Simplifies printing (single material, no dry box, no hardened nozzle)
- PETG's slight flexibility actually helps threads self-align and resist cracking

**If thread wear becomes a problem:** Upgrade the strut to PETG-CF for better surface hardness and stiffness, keeping the knob in PETG. The softer knob threads will wear preferentially, and the knob is the easier part to reprint. This is the classic "sacrificial soft nut on hard screw" pattern.

**PA-CF is overkill** for this application. Its superior wear resistance is designed for hundreds or thousands of cycles. At 36 cycles, the moisture sensitivity and printing difficulty are not worth the marginal benefit. PA-CF also raises food-safety questions — nylon absorbs water and the carbon fiber additive composition varies by manufacturer.

**ASA is ruled out** for any water-contact surfaces due to styrene content.

### Food Safety Notes

FDM prints have inherent food-safety limitations regardless of material:
- Layer lines create microscopic crevices that harbor bacteria
- Brass nozzles may contain trace lead (use a stainless steel nozzle for food-contact parts)
- Additives in filament (colorants, UV stabilizers, flow modifiers) may not be FDA-listed

For this application, the risk is low: water contact is minimal (clean cycle only), the mechanism is not in the continuous flow path, and a food-safe epoxy or polyurethane coating on water-contact surfaces can seal the layer lines. A stainless steel nozzle is recommended for printing the strut.

---

## 3. Strut Design

### The 122mm Span Problem

A 122mm printed threaded rod is long but feasible. Key considerations:

**Buckling:** For a 12mm diameter PETG rod under compression (which occurs when tightening the knob to pull the plate), Euler buckling is not a concern. The critical buckling load for a 12mm solid PETG cylinder at 122mm length is on the order of hundreds of Newtons — far exceeding the few Newtons of spring return force. Even with a generous safety factor, 12mm diameter is sufficient.

**Print quality over length:** Vertical printing of a 122mm rod is well within capabilities. The H2C's CoreXY kinematics minimize vibration that could affect thread quality at height. However, long thin vertical prints can develop resonance or wobble. Recommendations:
- Print with a brim for bed adhesion
- Use modest speeds (40-60mm/s for thread sections)
- Ensure the rod is truly vertical in CAD (no draft angle)

### Design Options

**Option A: Fully threaded strut**
- Entire 122mm length is threaded
- Simplest design, but unnecessary — only the ends need threads
- More print time, more material, threads in the middle serve no purpose
- Thread-on-thread sliding for 122mm of travel during cartridge insertion/removal would wear faster

**Option B: Smooth rod with threaded ends (recommended)**
- 15-20mm of thread on each end
- Smooth 10-12mm shaft in the middle section
- The plate end has male thread that screws into the plate (or is integral — see below)
- The knob end has male thread that engages the knob's female thread
- Lighter, faster to print, less wear surface

**Option C: Integral strut + plate (one piece)**
- The strut is printed as part of the release plate
- Eliminates one joint and one thread pair
- The strut grows straight out of the plate's back face
- Challenge: print orientation conflict — the plate wants to print flat (XY plane) but the strut wants to print vertically (Z axis)
- Solution: print the plate on its edge so the strut extends vertically, but this puts the plate's stepped bores on their sides (may need supports)
- **Viable but adds print complexity.** Recommended only after validating that the two-piece version works.

### Strut-to-Plate Attachment

If not integral, the strut attaches to the plate center. Options:
- **Threaded into plate:** Male thread on strut end mates with a threaded boss on the plate. Allows disassembly but adds a failure point.
- **Press-fit + adhesive:** Smooth stub on strut press-fits into a hole in the plate, secured with cyanoacrylate or epoxy. Simple, strong, permanent.
- **Printed snap ring:** Strut passes through plate hole, a printed retaining collar snaps on. Allows disassembly without threads.

**Recommended: press-fit with adhesive.** There is no reason to disassemble the strut from the plate after initial assembly. A dab of epoxy on a press-fit joint is stronger than any printed thread at this scale.

---

## 4. Printed Guide Pins

The current design uses 2x steel dowel pins to guide the release plate's linear travel. Can these be printed?

### Printed Pin Feasibility

A guide pin for 3mm of travel needs:
- Straightness over ~15-20mm of engagement length
- Low friction in the bushing/hole
- Resistance to bending under the off-axis loads from spring return

**Printed pins are feasible for this application.** The loads are very low (spring return force distributed across 2 pins), travel is only 3mm, and cycle count is low.

### Design Recommendations

**Pin material:** PETG-CF or plain PETG. The carbon fiber filler improves surface hardness and reduces the coefficient of friction slightly. A solid 6mm diameter printed pin has more than enough strength.

**Bushing approach:** Rather than pin-in-hole, use a printed pin sliding in a printed bushing:
- Pin: 6mm diameter, PETG-CF, printed vertically for best roundness
- Bushing: 6.5mm bore (0.25mm radial clearance), PETG, press-fit into the rear wall
- The different materials (CF pin in plain PETG bushing) reduce galling compared to same-material sliding pairs

**Clearance:** 0.2-0.3mm radial clearance for a sliding fit. With only 3mm of travel and monthly use, a slightly loose fit is acceptable and preferred over binding.

**Surface finish:** Light sanding of the printed pins with 400+ grit sandpaper dramatically improves sliding feel. A wipe of silicone grease eliminates any remaining friction.

### Versus Steel Dowel Pins

| Aspect | Steel Dowel | Printed Pin |
|---|---|---|
| Straightness | Excellent (ground) | Good (depends on print quality) |
| Wear | Essentially zero | Negligible at 36 cycles |
| Cost | ~$2 for a pair | ~$0.05 in filament |
| Availability | Hardware store trip | Print on demand |
| Integration | Separate part | Can be integral with plate |

**Verdict:** Printed pins are adequate. Steel dowels are objectively better but unnecessary for this load and cycle count. If the plate is printed with integral pins extending from its back face, the guide pins come "free" as part of the plate print.

---

## 5. Knob Design

### Thread Engagement

The knob contains the female thread that mates with the strut's male thread. For a 2-start Tr12x3:
- Minimum engagement length: 1.5x major diameter = 18mm
- This ensures at least 3 full thread pitches are engaged at any position
- Knob depth (along the strut axis): 20-25mm provides comfortable engagement plus room for the thread entry chamfer

### Ergonomics

For one-handed operation in a dark under-sink cabinet:
- **Diameter: 40-50mm.** Large enough to grip firmly with one hand, small enough to not interfere with the cartridge envelope (148mm wide).
- **Knurled grip:** Diamond knurl pattern on the outer surface. FDM prints knurling well — it is just a series of small pyramids or ridges on the perimeter. A 1mm-deep knurl pattern with 2mm spacing prints cleanly at 0.2mm layer height.
- **Flared or flanged base:** A slight flare at the base of the knob provides a natural finger stop and prevents the hand from slipping off.

### Pull-Handle Hybrid

Since the cartridge must be pulled out of the dock after releasing, the knob could double as a pull handle:
- **T-handle design:** A horizontal bar across the top of the knob, like a cork pull. Grip the bar, twist to release, then pull to extract.
- **Wing knob:** Two lobes extending from the sides, like a wing nut. Easy to grip and twist with one hand, and the lobes provide purchase for pulling.
- **Recommendation: wing knob.** It is the simplest to print (no overhangs if oriented correctly), provides good torque leverage, and doubles as a pull handle naturally.

### Print Orientation

Print the knob upright with the open (threaded) end facing up. This puts the internal thread walls in the XY plane for best resolution. The wing features extend radially and print without supports as long as any overhang angle stays above 45 degrees.

---

## 6. Spring Alternatives

The release plate needs a return force of ~2-5N to push it back to the "released" position when the knob is loosened.

### Option A: Printed TPU Compression Springs

TPU springs are viable for low-force, low-deflection applications:
- Design: helical coil, 8-10mm OD, 3-4mm wire diameter, 10-15mm free length
- Print with 95A TPU at 100% infill, 0.1-0.15mm layer height
- Expected force at 3mm compression: 1-3N per spring (highly dependent on geometry and TPU durometer)
- **Concern:** TPU springs lose force over time (stress relaxation/creep). Over months of being compressed, a TPU spring will weaken. Since the plate stays compressed between monthly swaps, this is a real issue.

### Option B: Printed Leaf Springs

A thin PETG or PETG-CF leaf spring integrated into the plate or rear wall:
- Design: cantilever beam, 2mm thick, 10mm wide, 20mm long, deflecting 3mm
- Produces reliable force and does not suffer from creep the way TPU does
- Can be printed as part of the rear wall (integral)
- **Concern:** Fatigue. PETG leaf springs at 3mm deflection over 20mm length are near the elastic limit. Over 36 cycles they may survive, but there is little safety margin.

### Option C: Printed Flexure Integrated into Plate

A compliant mechanism built into the plate itself:
- Living hinges or serpentine flexures around the plate perimeter
- The plate "bows" inward under knob tension and springs back when released
- Eliminates separate spring parts entirely
- **Concern:** Adds complexity to the plate geometry and may interfere with the collet bores.

### Option D: Just Use Metal Springs (Recommended)

Two small compression springs (6mm OD x 10mm length, ~1N/mm rate) cost under $1 total and will outlast the entire mechanism by orders of magnitude. They do not creep, do not fatigue at 36 cycles, and are trivially sourced.

**Verdict:** Metal springs are the right choice here. This is the one place where the "all-printed" aspiration should yield to practicality. Printed springs are possible but introduce reliability concerns (creep, fatigue) that are completely unnecessary given how cheap and reliable metal springs are.

If the goal is truly zero hardware-store parts, TPU compression springs in an oversized design (compensating for creep by starting with 2-3x the required force) are the fallback. Replace them annually.

---

## 7. Assembly and Part Count

### Minimum Part Count: All-Printed

| Part | Material | Print Orientation | Notes |
|---|---|---|---|
| Release plate with integral guide pins | PETG | On edge (pins vertical) | Pins extend from back face |
| Strut | PETG | Vertical | Threaded ends, smooth middle |
| Knob (wing style) | PETG | Upright | Internal thread |
| Springs (if printed) | TPU 95A | Vertical | 2x, replace annually |

**Total: 3 printed parts** (+ 2 springs, printed or metal)

Assembly: press-fit strut into plate center hole (epoxy), slide strut through rear wall, thread knob onto strut from front face. Guide pins slide into bushings in rear wall (bushings can be printed as part of the rear wall).

### Could Anything Be One Piece?

- **Plate + strut:** Possible but forces awkward print orientation (see Section 3, Option C)
- **Plate + guide pins:** Natural fit — pins are just cylinders extending from the plate back face
- **Strut + knob:** Not possible — the knob must thread onto the strut for the mechanism to function
- **All-in-one print-in-place:** Theoretically possible with dissolvable supports (PVA for the thread gap), but unnecessarily complex for 3 simple parts

---

## 8. Durability Analysis

### Thread Wear Over 36 Cycles

Each cycle involves:
1. Unscrew knob (~180 degrees for 2-start thread) — 1 wear event
2. Remove cartridge (strut slides through rear wall — no thread contact)
3. Insert new cartridge
4. Screw knob (~180 degrees) — 1 wear event

Total thread engagements: ~72 half-turns over 3 years.

For PETG-on-PETG threads with 0.3mm clearance and food-safe silicone grease:
- Wear is negligible at this cycle count. PETG is soft compared to metal but has enough wear resistance for dozens of cycles.
- The primary failure mode is not wear but cross-threading or overtightening, which can strip the printed threads. A physical stop (shoulder on the strut that bottoms out at full engagement) prevents overtightening.

### Creep Under Sustained Load

The knob keeps the plate pulled against the rear wall for weeks at a time. At room temperature, PETG creep under the low loads involved (a few Newtons of spring preload) is minimal. The threads are in compression along their flanks — PETG handles sustained compressive loads much better than tensile loads.

### Environmental Factors

- Under-sink environment: moderate temperature (15-30C), moderate humidity
- No UV exposure (enclosed cabinet)
- No thermal cycling beyond seasonal indoor temperature variation
- PETG is stable under all these conditions

### Expected Lifetime

**Conservative estimate: 100+ cycles before thread slop becomes noticeable.** At 36 cycles over 3 years, the mechanism should be well within its useful life. If the knob threads do wear, reprinting the knob takes 30 minutes and costs pennies.

---

## 9. Comparison: All-Printed vs. Hardware-Store Bolt

| Aspect | All-Printed | M8/M10 SS Bolt + Nut |
|---|---|---|
| Thread precision | Good (0.3mm clearance, trapezoidal) | Excellent (machined, tight tolerance) |
| Thread durability | Good for 36 cycles | Essentially infinite |
| Food safety | PETG: good with coating | Stainless steel: excellent |
| Cost per unit | ~$0.50 in filament | ~$3-5 for bolt + nut + knob |
| Lead time | 2-3 hours print time | Hardware store trip |
| Customization | Unlimited (any diameter, pitch, lead) | Fixed to standard sizes |
| Multi-start thread | Easy — just model it | Not available off the shelf |
| Weight | Very light | Heavier (not relevant here) |
| Repairability | Reprint any part | Replace standard part |
| Feel/smoothness | Adequate with grease | Superior |
| One-handed speed | Better (2-start = half turn) | Worse (fine pitch = many turns) |
| Overtightening risk | Higher (can strip plastic) | Lower (metal is forgiving) |

### Where All-Printed Clearly Loses

- **Thread feel:** A machined bolt in a machined nut will always feel smoother and more precise than printed threads. Users accustomed to metal fasteners will notice the difference.
- **Overtightening tolerance:** Printed threads strip if forced. Metal threads handle abuse better.
- **Long-term reliability certainty:** Metal is a known quantity. Printed threads at low cycle counts should be fine, but there is less real-world data.

### Where All-Printed Surprisingly Wins

- **Multi-start / quick-release:** A 2-start trapezoidal thread gives half-turn engagement. You cannot buy this off the shelf for a few dollars. This is the single biggest functional advantage — one-handed operation in a dark cabinet is dramatically easier with half a turn instead of 6+ turns on a fine-pitch bolt.
- **Integration:** The strut, plate, and guide pins can be optimized as a system. No compromising the design to accommodate standard bolt head sizes or thread pitches.
- **Iteration speed:** If the first version is too tight/loose/short/long, adjust the CAD and reprint in 2 hours. No waiting for a different bolt to arrive.
- **Zero-hardware-store-trip appeal:** For a maker project, self-sufficiency has real value.

---

## 10. Recommendations and Next Steps

### Recommended Configuration

1. **Thread:** 2-start trapezoidal, 12mm major diameter, 3mm pitch (6mm lead), 0.3mm radial clearance
2. **Material:** PETG for all parts (upgrade strut to PETG-CF only if wear is observed)
3. **Strut:** 12mm diameter, 122mm long, smooth shaft with 20mm threaded sections at each end, press-fit into plate with epoxy
4. **Knob:** Wing-style, 45mm wingspan, 25mm deep, internal 2-start trapezoidal thread
5. **Plate:** PETG, integral guide pins (6mm diameter, 15mm long)
6. **Guide bushings:** Printed into rear wall, 6.5mm bore
7. **Springs:** Metal compression springs (the one non-printed part worth keeping)
8. **Print settings:** 0.12-0.16mm layer height for threaded sections, 4+ walls, 30%+ infill, stainless steel nozzle

### Validation Steps

1. **Print a thread test pair first.** A 20mm long Tr12x3 2-start bolt and nut. Test fit, adjust clearance, validate feel. This is a 15-minute print.
2. **Print the strut at full length.** Verify straightness, thread quality at the top (furthest from bed).
3. **Print the knob.** Test thread engagement with the strut. Verify one-handed twist operation.
4. **Assemble the full mechanism.** Validate 3mm travel, spring return, guide pin sliding.
5. **Cycle test.** Run 50 insert/remove cycles (exceeding the 36-cycle lifetime) and inspect threads for wear.

### Risk Mitigations

| Risk | Mitigation |
|---|---|
| Threads too tight | Start with 0.4mm radial clearance, tighten if needed |
| Threads strip on overtightening | Add a physical stop (shoulder) on the strut |
| Strut prints crooked | Use brim, reduce speed, check belt tension |
| Guide pins bind | Increase clearance to 0.3mm radial, sand pins, apply grease |
| TPU springs creep (if used) | Oversize by 2-3x, replace annually, or just use metal |
| PETG thread wear at year 3 | Reprint the knob (30 min, $0.10) |
