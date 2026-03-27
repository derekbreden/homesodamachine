# Decision: Twist-Release Mechanism Approach

## Summary of Approaches

### All-3D-Printed (Tr12x3 2-Start Trapezoidal)

Prints the release plate with integral strut, knob, and guide pins in PETG. Uses a 2-start trapezoidal thread (Tr12x3, 6mm lead) so a half turn produces 3mm of travel. The 12mm-diameter strut is integral to the release plate -- one continuous printed piece (plate flat on build plate, strut vertical). A wing-style knob with internal female threads mates with the strut front end. Metal compression springs are retained (the one non-printed part).

### Hardware Store Bolt (M6 x 1.0)

Uses a standard M6 x 150mm fully-threaded 304 stainless hex bolt as the strut. The bolt threads into a ruthex M6 brass heat-set insert pressed into a boss on the release plate rear face. Two flanged brass bushings in the front and rear walls support the bolt. A 3D-printed PETG knob with a hex pocket captures the bolt head. Three full turns produce 3mm of plate travel. All metal components are food-safe stainless or brass.

---

## Criterion-by-Criterion Comparison

### 1. User Experience

**Printed: Half turn.** ~1 second. Grab, twist, done. A half-turn twist-to-release is closer to a bayonet mount -- the most intuitive motion for one-handed operation in a dark under-sink cabinet. The transition from "threaded" to "free" is tactilely obvious at 180 degrees.

**Bolt: 3 turns.** ~3 seconds. Clear tactile feedback from steel-on-brass threads. Self-locking feel is crisp. But 3 full turns (1080 degrees) is a lot of wrist rotation for a one-handed operation you cannot see. In a dark cabinet, fumbling through 3 rotations while holding a cartridge with the other hand is a meaningfully worse experience.

**Edge: Printed, decisively.** Half-turn vs 3 turns is not marginal. It is the difference between "twist and pull" and "fumble with 3 rotations in the dark."

### 2. Correct Mechanical Function

**Bolt: Strong.** M6 x 1.0 threads in a brass insert are a proven combination. Self-locking (lead angle 3.4 deg vs friction angle 17 deg). Force analysis shows ~1N fingertip force on a 38mm knob. Zero ambiguity about whether the threads will work.

**Printed: Strong with a caveat.** Tr12x3 2-start is well-suited to FDM -- flat crests/roots, 29-degree flanks, 3mm pitch gives 19-25 layers per pitch at 0.12-0.16mm layer height. The half-turn actuation is mechanically correct. The 2-start geometry's higher lead angle (10.2 degrees) is still below the PETG-on-PETG friction angle (arctan(0.3-0.5) = 17-27 degrees), so it should self-lock. But printed PETG-on-PETG threads have never been tested on this printer with this filament. A 15-minute test print validates this before committing.

**Edge: Bolt.** Zero thread-quality risk. The printed approach is sound in theory but unvalidated.

### 3. Prototypability

**Printed: Testable today, no dependencies.** Everything prints on the H2C. A thread test pair (20mm Tr12x3 2-start bolt + nut) prints in 15 minutes and validates clearance and feel. Full strut prints in ~2 hours. No waiting for deliveries. If the first test fails, iteration is hours, not days.

**Bolt: Testable in 1-2 days with Amazon dependency.** The M6 x 150mm bolt is not available at Home Depot in-store. Amazon Prime delivers in 1-2 days. Ruthex inserts are also Amazon. Flanged brass bushings require McMaster-Carr or can be skipped. Print the knob and plate mods while waiting.

**Edge: Printed.** Zero supply chain dependency. The 15-minute thread test validates the entire approach before printing a full strut.

### 4. Simplicity

**Bolt: 5 unique parts in the mechanism** (bolt, heat-set insert, 2x bushings, knob). Each is off-the-shelf with known dimensions or a simple print. Assembly is linear. If anything breaks, replace the commodity part.

**Printed: 2 unique printed parts** (release plate with integral strut + guide pins, wing knob). Fewer parts, and no joints -- the strut is one continuous piece with the plate. Thread engagement depends on print quality. Clearance tuning adds hidden complexity.

**Edge: Bolt.** More parts, but each is simpler and independently replaceable. The printed approach has fewer parts but more tuning.

### 5. Durability

**Bolt: Essentially infinite at 36 cycles.** Stainless-on-brass threads do not wear measurably at this duty cycle. The heat-set insert is rated for 500N+ pull-out. The only wear point is the PETG knob hex pocket -- negligible over 108 total turns across 3 years.

**Printed: Adequate with margin.** PETG threads estimated at 100+ cycles before noticeable slop. 36 cycles needed gives ~3x safety margin. The knob is the sacrificial wear part and reprints in 30 minutes. A physical stop on the strut prevents overtightening (the primary failure mode for printed threads).

**Edge: Bolt.** Both pass the 36-cycle requirement. The bolt has orders of magnitude more margin. But the printed approach has enough margin (3x) for a mechanism whose wear part reprints in 30 minutes.

### 6. Cost

**Bolt:** ~$15 total (bolt pack, heat-set inserts, bushings, washers).

**Printed:** ~$0.50 in filament + metal springs (~$2).

**Edge: Irrelevant.** Cost is not a factor in this decision. Both approaches are cheap. Never use cost as a deciding criterion for this project.

---

## Recommendation: All-3D-Printed (Tr12x3 2-Start Trapezoidal)

**Use the printed approach.** UX is the primary design concern, and the printed approach wins it decisively.

Half-turn vs 3 turns is not a marginal difference. It is the difference between "twist and pull" and "fumble with 3 rotations in the dark." This mechanism lives in a dark under-sink cabinet where one-handed operation matters. A bayonet-style half-turn release is dramatically better UX than threading and unthreading a bolt.

The durability concern is real but manageable. 100+ estimated cycles against 36 needed is a ~3x safety margin. The wear part (the knob) reprints in 30 minutes. Overtightening is prevented by a physical stop on the strut. And if threads ever do wear prematurely, the knob is the only part that needs replacing.

The mechanical uncertainty is addressed by a 15-minute test print. Print a 20mm Tr12x3 2-start bolt-and-nut pair, test the feel, adjust clearance if needed. This validates the approach before printing the full strut. If the test print feels good, proceed. If it does not, iterate clearance (0.3mm to 0.4mm radial) and retest -- each iteration is 15 minutes.

The bolt approach remains a proven fallback if printed threads turn out to be mechanically infeasible after testing. But the test print is the gate, not a preemptive retreat to bolts.

---

## Fallback

**Switch to the bolt approach ONLY if:** printed Tr12x3 2-start threads prove mechanically infeasible after testing -- threads do not engage reliably, thread feel is unacceptable after clearance tuning, or the strut prints too crooked for thread alignment. This is a fallback for mechanical infeasibility, not a fallback for "it takes an extra iteration."

---

## Hybrid Option (Future Consideration)

Use the bolt for the strut (proven, stiff, food-safe stainless) but print a 2-start trapezoidal knob-to-wall interface at the front face. This gets the half-turn UX at the user-facing end while keeping a reliable bolt-to-insert connection at the plate end. The knob's female thread only needs to be ~20mm long and is easy to reprint if wear occurs. Not recommended now -- validate the all-printed approach first.

---

## Bill of Materials (Printed Approach)

### 3D Printed Parts (Bambu H2C, PETG)

| Qty | Part | Specification | Notes |
|---|---|---|---|
| 1 | Release plate with integral strut + guide pins | 59x47mm PETG plate with 12mm dia Tr12x3 2-start strut extending from center, ~136mm total Y extent, 2x 6mm guide pins on rear face | Print plate-down, strut vertical, 0.12-0.16mm layer height for thread sections, 4+ walls |
| 1 | Wing knob | PETG, ~45mm wingspan, 25mm deep, internal female Tr12x3 2-start thread, knurled grip | Print upright, open end facing up |

### Metal Components

| Qty | Item | Specification | Notes |
|---|---|---|---|
| 2 | Compression springs | ~5-6mm OD x 10mm, ~0.5-1.0 N/mm, stainless steel | Retained from existing design |

### Optional

| Qty | Item | Specification | Notes |
|---|---|---|---|
| 1 | Food-grade silicone grease | Super Lube 92003 (NSF H1) | For thread lubrication if desired |

### Print Settings

| Parameter | Value |
|---|---|
| Layer height (thread sections) | 0.12-0.16mm |
| Layer height (smooth shaft) | 0.20mm (variable layer height) |
| Walls/perimeters | 4+ |
| Infill | 30%+ |
| Nozzle | Stainless steel (food safety) |
| Thread clearance | 0.3mm radial (0.6mm on diameter), adjust from 15-min test print |
