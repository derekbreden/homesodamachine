# Pump Cartridge Envelope Research

## Question

What is the minimum cartridge envelope needed to house 2 Kamoer KPHM400 pumps, their tubing routing, and their electrical connections, and what are the mounting, vibration, and thermal constraints?

## Source Dimensions

All pump dimensions are caliper-verified from `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`. All John Guest union dimensions are caliper-verified from `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`.

**Pump head cross-section:** 62.6mm x 62.6mm (square, rounded corners)
**Mounting bracket width:** 68.6mm (extends ~3mm per side beyond pump head)
**Total pump length (front face to motor nub):** 116.5mm
**Total pump length (front face to motor end cap):** 111.4mm
**Motor shaft nub protrusion:** 5.0mm
**Motor diameter:** ~35mm
**Mounting hole pattern:** 4x M3 in 48mm x 48mm square on the bracket face (the junction between pump head and motor)
**Tube stubs:** 2 per pump, BPT tubing 4.8mm ID / 8.0mm OD, protruding ~30-50mm from front face
**Motor terminals:** 2 solder tabs at the rear of the motor

**John Guest PP0408W union:** barbell profile, 15.10mm body-end OD, 9.31mm center-body OD, 36.32mm body length, 41.80mm with collets extended
**Collet travel:** ~1.3mm per side


---

## 1. Minimum Dual-Pump Envelope (Width)

### Side-by-Side Arrangement

The pumps are oriented with their long axis (depth) running front-to-rear in the cartridge. The pump heads face the front of the cartridge; the motors face the rear.

**Pump head width:** 62.6mm each.
**Mounting bracket width:** 68.6mm each (the controlling width dimension at the bracket face).

#### Clearances Between Pumps

The space between the two pumps must accommodate:
- **Structural wall between pump bays:** 1.2mm minimum (3 perimeters per FDM constraints for structural walls). Recommend 2.0mm for stiffness.
- **Assembly tolerance:** 0.2mm clearance per side between pump head and cartridge wall (sliding fit per FDM constraints). This means 0.4mm total per pump.
- **Tube routing between pumps:** Not required. The tube stubs exit the front face, not the sides. The inter-pump gap only needs to provide structural separation.

#### Clearances Between Pumps and Outer Walls

Each outer wall must accommodate:
- **Cartridge wall thickness:** 1.6mm minimum (2.0mm recommended for a cartridge that takes insertion/removal forces and rail loads)
- **Clearance to pump head:** 0.2mm per side
- **Clearance to bracket:** The bracket extends 3mm beyond the pump head per side, but the bracket is only at one Y-position (the junction face). The cartridge walls must clear the bracket at that plane. However, if the bracket face seats against a mounting plate (internal partition), then only the pump head width matters for the continuous side walls.

#### Width Calculation

Using the bracket as the controlling dimension (worst case at the junction face):

| Component | Dimension |
|-----------|-----------|
| Left outer wall | 2.0mm |
| Left clearance | 0.2mm |
| Left pump bracket | 68.6mm |
| Center clearance (left) | 0.2mm |
| Center divider wall | 2.0mm |
| Center clearance (right) | 0.2mm |
| Right pump bracket | 68.6mm |
| Right clearance | 0.2mm |
| Right outer wall | 2.0mm |
| **Total width** | **144.0mm** |

However, the bracket is only ~1.5-2mm thick at one Y-position. If the mounting plate has notches/reliefs for the bracket flanges, the continuous cartridge walls only need to clear the 62.6mm pump heads:

| Component | Dimension |
|-----------|-----------|
| Left outer wall | 2.0mm |
| Left clearance | 0.2mm |
| Left pump head | 62.6mm |
| Center clearance (left) | 0.2mm |
| Center divider wall | 2.0mm |
| Center clearance (right) | 0.2mm |
| Right pump head | 62.6mm |
| Right clearance | 0.2mm |
| Right outer wall | 2.0mm |
| **Total width (pump head region)** | **132.2mm** |

**Conclusion:** The minimum cartridge width is 132mm at the pump head region, widening to 144mm at the bracket junction plane (or using local reliefs to avoid the full 144mm). The enclosure width budget is 220mm, so this leaves 76-88mm for the rest of the enclosure width (valves behind, electronics routing, etc). The cartridge itself fits comfortably.

### Height

**Pump head height:** 62.6mm each. In a side-by-side (not stacked) arrangement, the cartridge height equals one pump height plus walls.

| Component | Dimension |
|-----------|-----------|
| Bottom wall | 2.0mm |
| Bottom clearance | 0.2mm |
| Pump head height | 62.6mm |
| Top clearance | 0.2mm |
| Top wall | 2.0mm |
| **Total height** | **67.0mm** |

The tube stubs protrude from the front face. Photo 17 shows 82.82mm from the bottom of the pump to the top of the tube connectors, meaning the tube connectors extend ~20mm above the pump head square profile. This does NOT affect cartridge height if the tubes route forward and then bend downward/sideways rather than straight up. Inside the cartridge, the tubes will be routed in a controlled path (see Section 2).

**Conclusion:** Minimum cartridge height is 67mm.


---

## 2. Tubing Routing Constraints

### The Routing Problem

Each pump has 2 BPT tube stubs exiting its front face, for a total of 4 tubes. The vision specifies that 4 John Guest quick connects are at the **rear** of the cartridge (the motor end). The tube stubs exit the **front** (the pump head face). The tubes must route from the front face, around or alongside the pump body, to quick connects at the rear.

### BPT Tube Bend Radius

BPT tubing (4.8mm ID / 8.0mm OD) is highly flexible -- comparable to silicone tubing. The general rule for flexible tubing is a minimum bend radius of 2x the OD, giving **16mm minimum bend radius** for 8mm OD tubing. In practice, BPT tubing can be bent tighter without kinking (down to ~10-12mm radius), but 16mm is the safe design value that avoids flow restriction and tube fatigue.

### Routing Path Options

**Option A: Tubes route along the outside of the pump body.** The tube stubs exit the front face, bend 180 degrees alongside the pump head and motor, and reach the quick connects at the rear. This requires clearance alongside the pump for the tube + bend radius. A 180-degree bend at 16mm radius plus the 8mm tube OD adds approximately 40mm to the depth at the front, and the tubes run in the clearance space alongside or beneath the pumps.

**Option B: Tubes route through channels in the cartridge floor/ceiling.** Dedicated channels molded into the cartridge walls guide the tubes from front to rear. The tubes exit the front face, enter channels that run along the bottom or top of the pump bays, and emerge at the rear wall where the quick connects are mounted.

**Option C: Tubes route through the center divider.** The 4 tubes (2 per pump) pass through channels in the center divider wall between the two pump bays, running from front to rear. This uses otherwise dead space.

**Recommended approach:** Option B (floor/ceiling channels). This keeps tubes protected, maintains the clean cartridge exterior the vision demands, and uses the vertical space beneath or above the pump head (the pump head is 62.6mm tall but the motor is only ~35mm diameter -- there is ~14mm of unused space above and below the motor cylinder). The tubes can run in this dead space alongside the motor without increasing the cartridge width.

### Depth Budget for Tubing Routing

The critical depth constraint is at the **rear wall** where the John Guest unions are mounted. The rear wall must accommodate:

| Component | Dimension (from rear face inward) |
|-----------|-----------|
| John Guest union body-end (outside cartridge, connects to enclosure tubes) | 12.08mm (external, not part of cartridge depth) |
| Rear wall thickness around center body press-fit | 3.0mm minimum (the wall grips the 9.31mm center body) |
| John Guest union body-end (inside cartridge) | 12.08mm |
| Collet protrusion (extended) | ~2.7mm |
| Tube insertion depth into union | ~16mm |
| Tube bend from axial to lateral routing | 16mm radius bend = ~24mm in the depth direction (for a 90-degree bend from the union port inward to running alongside the pump) |
| **Rear wall + union + tube transition zone** | **~58mm** from the rear face of the cartridge to where the tubes are running parallel alongside the pumps |

At the **front** of the cartridge, the tube stubs protrude 30-50mm from the pump head face. These stubs need to:
- Exit the pump face
- Bend ~90 degrees to enter the routing channels
- The 90-degree bend takes ~24mm (16mm radius + 8mm tube diameter)

| Component | Dimension (from pump front face forward) |
|-----------|-----------|
| Tube stub protrusion | 30-50mm (use 40mm nominal) |
| 90-degree bend clearance | 24mm |
| Front wall thickness | 2.0mm |
| **Front clearance zone** | **~66mm** from the pump front face to the front of the cartridge |

Wait -- this cannot be right. The tube stubs protrude forward, and the routing needs to turn them rearward. The entire depth budget would be enormous. Let me reconsider.

### Revised Routing Analysis

The tube stubs are **flexible BPT tubing**, not rigid pipes. They can be bent immediately at exit from the pump head. The stubs protrude 30-50mm, but this is the free length of tubing -- not a rigid standoff. The actual clearance needed in front of the pump head is only enough for the tube to make a gentle bend:

**Front clearance needed:** The tube exits the pump face and needs to turn 90 degrees (or 180 degrees if routing backward). With a 16mm bend radius on 8mm OD tubing:
- For a 90-degree bend down into a floor channel: ~24mm forward of the pump face
- For a U-turn (180-degree bend) to route backward: ~40mm forward of the pump face

**Practical minimum front clearance:** 25mm forward of the pump front face allows a 90-degree bend into floor/ceiling routing channels. The excess tube stub length (the remaining 15-25mm) runs along the channel.

### Total Cartridge Depth

| Component | Dimension |
|-----------|-----------|
| Front wall | 2.0mm |
| Front tube routing clearance | 25mm |
| Pump head depth | 48mm |
| Bracket/adapter | ~4mm |
| Motor body | ~63mm |
| Motor nub | 5mm |
| Motor terminal clearance | 5mm |
| Rear electrical connector zone | 10mm (see Section 3) |
| Rear wall with John Guest union pocket | 15mm (center body press-fit zone + wall structure) |
| **Total cartridge depth** | **~177mm** |

But the enclosure is only 300mm deep. The cartridge sits at the front and bottom, so 177mm of depth is significant. However, this includes everything from the front face (which the user grasps) to the rear face (which has the quick connects that dock with the enclosure tubes).

**Conclusion:** The minimum cartridge depth is approximately 175-180mm. This is within the 300mm enclosure depth budget, leaving ~120mm behind the cartridge for valve manifold, tubing, and electronics routing.

### Quick Connect Arrangement at Rear

The 4 John Guest unions at the rear wall should be arranged in a 2x2 pattern (2 per pump, left-right mirroring the pump positions). Each union occupies a 15.10mm diameter footprint on the wall face. With 5mm clearance between unions, the 4 unions span approximately 35mm x 35mm, well within the 132mm cartridge width.

**The release plate mechanism** is inside the cartridge, between the rear wall and the motor terminals. The plate must slide ~3mm toward the rear wall to push the collets. This zone overlaps with the electrical connector zone (Section 3), and both must be designed as an integrated assembly at the rear of the cartridge.


---

## 3. Electrical Connection

### Requirements

- 2 pumps, each with 2 motor terminals (DC brushed motor) = 4 electrical contacts total
- The cartridge must make/break these connections during insertion/removal
- Blind-mate alignment (the user pushes the cartridge in; contacts mate without visual alignment)
- The pumps draw modest current: 12V DC brushed motor, estimated 0.3-0.5A per pump at operating load (based on Kamoer KPHM400 datasheet listing 0.3A for the stepper variant; brushed DC variant is comparable)
- Power: ~4-6W per pump maximum

### Connector Options

#### Option A: Magnetic Pogo Pins (Recommended)

Spring-loaded pogo pin connectors with magnetic alignment are purpose-built for blind-mate cartridge applications.

**Specifications (typical 2-pin magnetic pogo connector):**
- Pitch: 2.5mm between pins
- Current rating: 1-3A per pin (adequate for 0.5A pump load)
- Voltage rating: 12V+ (typical rating is 36V)
- Contact force: ~60g per pin at working height (spring-loaded)
- Misalignment tolerance: up to 1-2mm lateral
- Cycle life: 10,000-50,000 cycles (far exceeds the pump replacement lifetime)
- Total footprint for a 2-pin connector: ~8mm x 5mm
- Working height (compressed travel): 1.0-1.5mm

For 2 pumps, two 2-pin magnetic pogo connectors would be used. The cartridge side has flat contact pads; the enclosure dock side has the spring-loaded pogo pins.

**Advantages:** Self-aligning via magnets, zero insertion force, very high cycle life, compact, no exposed blade contacts that could short.
**Disadvantages:** More expensive than blade terminals (~$2-5 per connector pair). Magnets may attract metal debris.

**Space requirement:** 2 connectors x ~8mm x 5mm footprint = negligible. Mount them on the enclosure dock rear wall, mating with contact pads on the cartridge rear face adjacent to the quick connects. Total space: ~10mm depth for the pogo pin housings on the dock side.

#### Option B: Blade / Spade Terminals

Standard automotive 6.3mm blade terminals (male on cartridge, female on dock).

**Specifications:**
- Current rating: up to 21A (vastly over-specified for 0.5A)
- Insertion force: 1-3 lbs per contact (higher than pogo pins)
- Cycle life: 1,000-5,000 cycles (lower than pogo pins, but still adequate -- a pump cartridge might be replaced 5-20 times over the product lifetime)
- Footprint per terminal: ~8mm x 6.3mm blade width
- Requires precise lateral alignment (~1mm tolerance)

**Advantages:** Extremely cheap (<$0.10 per terminal), robust, well-understood.
**Disadvantages:** Higher insertion force, less forgiving of misalignment, exposed blades could short against each other or the cartridge structure if not properly shrouded. Requires alignment guides on the cartridge rails.

**Space requirement:** Similar to pogo pins. 4 blade terminals arranged in a row: ~32mm x 8mm footprint.

#### Option C: Spring Contacts (Leaf Springs)

Custom stamped spring contacts on the dock side that press against flat pads on the cartridge.

**Specifications:**
- Current rating: depends on material and contact area; 1-5A typical
- Contact force: 50-200g per contact
- Cycle life: 10,000+ cycles
- Requires tight vertical alignment (spring contacts press perpendicular to insertion direction)

**Advantages:** Simple, cheap, reliable. Common in battery compartments and cartridge mechanisms.
**Disadvantages:** Requires the cartridge to be pressed firmly against the contacts (the rail mechanism provides this). Contact pads on the cartridge must be precisely positioned.

**Space requirement:** 4 contacts x ~5mm x 5mm each = ~20mm x 10mm total.

### Recommendation

**Blade terminals (Option B)** are the best fit for this application. Reasons:
- The cartridge slides in on rails, which provides the precise linear alignment that blade terminals need. The user is not plugging in blindly -- the rails guide the cartridge to the exact mating position.
- The insertion force of blade terminals is trivial relative to the force already needed to push tubing into the John Guest quick connects.
- Cost is negligible.
- Automotive-grade reliability in a food-adjacent environment.
- Shrouded female blade receptacles on the dock side prevent accidental shorts.

Mount 4 blade terminals (2 per pump) on the cartridge rear face, positioned between or alongside the 4 quick connects. The mating female receptacles are on the enclosure dock wall. As the cartridge slides to its final position on the rails, the blade terminals engage the receptacles simultaneously with the tubes entering the quick connects.

**Electrical zone depth:** 10mm behind the motor terminals for blade terminal length and wiring clearance.

### Failure Modes

- **Corrosion:** In a kitchen environment with occasional humidity. Blade terminals with tin or nickel plating resist corrosion adequately. Gold-plated pogo pins would be more resistant but unnecessary at this current level.
- **Misalignment:** Blade terminals tolerate ~0.5-1mm lateral misalignment. The rail system must achieve this. If alignment proves difficult in testing, fall back to pogo pins (Option A) which tolerate 1-2mm.
- **Partial insertion:** If the cartridge is not fully seated, blade terminals may make intermittent contact. The rail mechanism should include a positive detent or latch at the fully-inserted position.


---

## 4. Vibration

### The Vibration Problem

Peristaltic pumps produce pulsatile flow by compressing tubing with rotating rollers. The Kamoer KPHM400 uses a 3-roller mechanism, which means the flow (and the mechanical impulse) pulses 3 times per revolution. At the rated speed of ~200-400 RPM, this produces vibration at 10-20 Hz -- well within the range that transmits audibly through rigid structures.

### Vibration Transmission Path

Pump motor/rollers --> pump housing --> mounting screws --> mounting plate --> cartridge walls --> rails --> enclosure

Every rigid junction in this path transmits vibration efficiently.

### Mounting Approaches

#### Approach A: Rigid Mounting (Baseline)

Pump bracket bolted directly to a rigid mounting plate with M3 screws. All vibration transmits directly to the cartridge and enclosure.

**Pros:** Simplest, cheapest, most dimensionally stable.
**Cons:** Maximum noise transmission. The enclosure becomes a sounding board.

#### Approach B: Rubber Grommet Isolation (Recommended)

Replace the 4 rigid M3 mounting screws with M3 rubber vibration isolation mounts (cylindrical rubber bobbins with M3 threaded studs on each end). These are standard catalog parts from BelMetric, JW Winco, and others.

**Typical specifications (M3 rubber isolation mount):**
- Diameter: 8-10mm
- Height: 8-10mm
- Thread: M3 x 0.5 on both ends
- Material: Natural rubber (NR), 40-55 Shore A durometer
- Load capacity: 0.5-2 kg per mount (4 mounts share the ~200-300g pump weight, well within capacity)
- Vibration reduction: 60-80% amplitude reduction at frequencies above the mount's natural frequency (~15-25 Hz for small rubber mounts)

**Implementation:** One M3 rubber mount at each of the 4 mounting hole positions. The stud threads into the pump bracket on one side and into the cartridge mounting plate on the other. The rubber body decouples the pump from the cartridge structure.

**Space impact:** Each rubber mount adds ~8-10mm to the mounting plate thickness (or equivalently, the pump floats ~8-10mm away from the plate surface). This is absorbed into the existing depth budget -- the mounting plate sits at the bracket junction, and the motor cylinder protrudes behind it anyway.

**Pros:** Dramatic noise reduction. Standard off-the-shelf parts. M3 threading matches the existing pump bracket holes.
**Cons:** Adds ~8mm to the effective mounting depth. Rubber can degrade over years (but NR is highly durable). The pump has slight freedom to oscillate, which means tube connections must tolerate ~0.5mm of relative movement (BPT tubing is flexible, so this is fine).

#### Approach C: Compliant Mounting Plate (Alternative)

Print the mounting plate from TPU (flexible filament) instead of rigid PLA/PETG. The flex in the plate absorbs vibration.

**Pros:** No additional parts needed. Can be printed on the Bambu H2C (TPU is listed as a supported material).
**Cons:** Less predictable vibration characteristics than purpose-built rubber mounts. TPU is harder to print precisely. May creep under sustained load.

### Recommendation

**Approach B (rubber grommet isolation)** is the clear winner. The M3 rubber vibration isolation mounts are cheap (~$0.50-1.00 each), widely available (BelMetric, Amazon, McMaster-Carr), and directly compatible with the pump's existing M3 mounting holes. They add minimal space to the design.

Additionally, the cartridge rails themselves should include a thin (1-2mm) rubber or silicone gasket strip where the cartridge contacts the enclosure dock. This provides a second isolation stage and prevents the cartridge from buzzing against the dock.

### Failure Modes

- **Rubber aging:** NR rubber grommets may harden over 5-10 years, reducing isolation effectiveness. Not a concern for a consumer appliance with a ~5-year practical lifetime.
- **Resonance:** If the pump's operating frequency matches the natural frequency of the rubber mount system, vibration could amplify rather than attenuate. The pump's pulsation frequency (10-20 Hz) is near the typical natural frequency of small rubber mounts (15-25 Hz). If resonance is observed in testing, stiffer mounts (higher Shore A) raise the natural frequency above the excitation range.
- **Pump walking:** The compliant mounts allow small oscillatory movement. The 4-mount pattern constrains all 6 degrees of freedom. BPT tube connections tolerate this movement without issue.


---

## 5. Thermal

### Heat Generation

The Kamoer KPHM400-SW3B25 uses a 12V DC brushed motor. Based on the Kamoer datasheet and Amazon listing:
- Voltage: 12V DC
- Current: ~0.3A (stepper variant spec; brushed DC variant is similar or slightly higher under load)
- Power input: ~3.6W per pump, ~7.2W total for both pumps
- Motor efficiency (small brushed DC): typically 50-70%
- Heat dissipation per pump: ~1-2W (the remaining 1.6-2.6W becomes mechanical work)
- **Total heat from both pumps: ~2-4W**

### Duty Cycle

These pumps run only during dispensing -- typically 5-15 seconds per glass. Even at heavy use (20 glasses per day), total run time is 100-300 seconds per day. The duty cycle is well under 1%. The pumps are effectively cold between dispensing events.

### Thermal Environment

The cartridge is enclosed in the lower front of a 220mm x 300mm x 400mm plastic enclosure. The cartridge walls are printed plastic (PLA, PETG, or ABS), which are thermal insulators.

### Thermal Analysis

At 2-4W of continuous heat generation (worst case -- sustained dispensing), the temperature rise in an enclosed plastic box depends on surface area and ventilation:
- Cartridge surface area: approximately 2 x (132 x 177) + 2 x (67 x 177) + 2 x (132 x 67) = ~88,000 mm2 = 0.088 m2
- Natural convection from a plastic surface: ~5-10 W/(m2*K)
- Temperature rise at 4W: T_rise = 4W / (7.5 W/(m2*K) x 0.088 m2) = ~6 degrees C

A 6 degree C rise above ambient is negligible. Even in a worst-case enclosed scenario with poor convection, the temperature would not exceed ambient + 15 degrees C.

### Do the Motors Need Ventilation?

**No.** At this power level and duty cycle, active ventilation is unnecessary. The motor's own metal housing conducts heat to the surrounding air, and even with plastic cartridge walls, the thermal load is trivial.

However, the motor end cap should not be pressed against a solid wall with zero air gap. A **minimum 5mm air gap** between the motor end cap and any surrounding surface allows basic convective cooling and prevents heat from concentrating at the motor-wall interface.

### Clearance Requirements

- **Motor nub:** 5mm protrusion from the motor end cap. The cartridge rear structure must not contact this nub. Provide a clearance bore or open space behind the motor.
- **Motor body radial clearance:** The motor is ~35mm diameter inside a ~62.6mm square pump head bay. There is ~14mm of clearance on each side of the motor. This is more than adequate for air circulation.
- **Ventilation holes:** Not required for thermal reasons, but small holes (3-5mm) in the cartridge walls near the motor zone could be added for marginal improvement if testing shows any concern. These also provide drainage in case of a leak.

### Kamoer Thermal Specifications

Kamoer's published working temperature range is 0-40 degrees C ambient, with humidity below 80%. No specific motor derating curve or maximum case temperature is published. Given the low power and short duty cycle, the motor will always operate well within this range in a kitchen environment.

### Failure Modes

- **Stalled motor:** If a pump stalls (e.g., kinked tube, debris), the motor draws maximum current and generates maximum heat. At 12V, a stalled small DC motor might draw 1-2A, generating 12-24W of heat. Firmware must detect stall conditions (via current sensing or back-EMF monitoring) and shut down the motor within seconds. This is a firmware safety requirement, not a thermal design requirement -- no amount of ventilation prevents damage from an undetected stall.
- **Ambient temperature:** In an under-sink cabinet on a hot summer day, ambient could reach 35-40 degrees C. The 6 degree C rise from motor heat stays well within the 40 degree C working temperature limit. No concern.


---

## 6. Summary: Minimum Cartridge Envelope

### Dimensions

| Axis | Dimension | What Determines It |
|------|-----------|-------------------|
| **Width (X)** | **132mm** minimum (pump head region); 144mm at bracket plane | Two 62.6mm pump heads + 2.0mm center wall + 2x 2.0mm outer walls + clearances |
| **Height (Z)** | **67mm** minimum | One 62.6mm pump head height + 2x 2.0mm walls + clearances |
| **Depth (Y)** | **177mm** minimum | Front wall + tube routing (25mm) + pump head (48mm) + bracket/adapter (4mm) + motor (63mm) + nub (5mm) + terminal clearance (5mm) + electrical connector zone (10mm) + rear wall with JG union pockets (15mm) |

### Volume

132mm x 67mm x 177mm = **1,565 cm3** (~1.57 liters)

### Fits Within Enclosure?

The enclosure is 220mm wide x 300mm deep x 400mm tall. The cartridge at 132mm x 177mm x 67mm occupies:
- 60% of enclosure width
- 59% of enclosure depth (from the front)
- 17% of enclosure height (at the bottom)

This fits. The cartridge leaves room beside it for valve manifold routing, behind it for plumbing and electronics, and above it for the display/switch zone and bag frames.

### Key Constraints Carried Forward to Design

1. **Width is driven by pump head width (62.6mm), not bracket width (68.6mm).** Use local reliefs at the bracket plane to avoid widening the entire cartridge to 144mm.
2. **Depth is driven primarily by the pump length (116.5mm) plus tube routing at the front (25mm) and the JG union + electrical zone at the rear (25mm).** Reducing tube routing clearance (tighter bends) is the main lever to reduce depth.
3. **The release plate mechanism, electrical connectors, and JG unions all share the rear 25-30mm of the cartridge.** This zone requires careful integrated design.
4. **Rubber grommet vibration mounts (M3, 8mm diameter, 8mm height)** add ~8mm to the effective mounting depth but are absorbed into the motor-zone clearance.
5. **No active ventilation required.** Maintain a 5mm minimum air gap behind the motor end cap.
6. **Blade terminals are the recommended electrical connector.** 4 terminals (2 per pump) on the cartridge rear face, mating with shrouded receptacles on the dock wall.
7. **Tube routing channels** in the cartridge floor or ceiling carry the BPT tubes from the pump head face to the JG unions at the rear. Minimum channel cross-section: 10mm x 10mm (8mm OD tube + 1mm clearance per side).
