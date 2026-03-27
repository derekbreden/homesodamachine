# V1 Back Panel Layout

Research document covering all external connections that enter or exit through the rear of the enclosure. This is the installer-facing surface: a plumber or handy homeowner connects everything here once during installation and never touches it again.

**Enclosure:** 280W x 300D x 400H mm exterior (272 x 292 x 392 interior, 4mm walls).
**Layout:** Diagonal interleave (Vision 1). Bags diagonal top-front to bottom-back, cartridge front-bottom, electronics top-back, hopper top-front.

---

## 1. Connection Inventory

Six connections cross the back panel:

| # | Connection | Fitting Type | Purpose |
|---|-----------|-------------|---------|
| 1 | Tap water inlet | 1/4" push-to-connect bulkhead | Fresh water for automated cleaning/rinsing cycles |
| 2 | Carbonated soda water inlet | 1/4" push-to-connect bulkhead | From carbonation system upstream; feeds flow meter |
| 3 | Carbonated soda water outlet | 1/4" push-to-connect bulkhead | Returns metered soda water to the line downstream |
| 4 | 120V AC power | IEC C14 panel-mount inlet | Mains power to internal PSU |
| 5 | Flavor line 1 exit | Silicone tube pass-through with strain relief | Routes concentrated flavor 1 to faucet |
| 6 | Flavor line 2 exit | Silicone tube pass-through with strain relief | Routes concentrated flavor 2 to faucet |

**Critical design point:** The soda water inlet and outlet exist solely for the flow meter. Soda water enters, passes through the flow meter, and exits. No flavor mixing happens on the soda water line inside the enclosure. The two flavor lines exit separately and route externally to the faucet, where dispensing occurs synchronized with the flow meter reading.

---

## 2. Back Panel Zones

The back panel is 280mm wide x 400mm tall (exterior dimensions). What lives on the inside behind each zone determines what can penetrate the panel at that height.

### Top zone: Z = 310-400mm (top 90mm)

**Interior contents:** Electronics pocket (ESP32, L298N drivers, PSU, RTC, MCP23017, FDC1004). Per the master spatial layout, the electronics pocket occupies X=192-272, Y=222-292 (V1-A) at Z=342-392. The PSU converting 120V AC to 12V DC and 5V logic rails will also live in this zone.

**What goes here:** The 120V AC IEC C14 inlet. Placing power at the top keeps it:
- Adjacent to the PSU on the interior (shortest high-voltage wire run)
- Maximally separated from all water connections (bottom of panel)
- In compliance with standard practice: power above, water below

### Middle zone: Z = 130-310mm (180mm band)

**Interior contents:** The diagonal bag slab passes through this region. At the back wall (Y=292), the lower bag surface is at Z=127mm (V1-A, 1L bags at 35 degrees). The bags slope upward from there toward the front. This zone is mostly occupied by the descending bag slab and the tube channels on the enclosure floor beneath it.

**What goes here:** The two flavor tube exits. Internal routing from the pump cartridge area (front-bottom) to the back panel uses hard PE/PU tubing with John Guest fittings. The transition to silicone tubing happens at or near the back panel PG7/PG9 cable gland, since silicone is only needed for the external cosmetic run to the faucet. Placing the exits in the mid-panel range (around Z=180-220mm) keeps them:
- Clear of the water fittings below
- Clear of the power inlet above
- At a height where they can route upward through the cabinet to the faucet with a gentle bend

### Bottom zone: Z = 0-130mm (bottom 130mm)

**Interior contents:** The back-bottom area is where the bag connector ends sit (the low end of the diagonal at approximately Z=29-127mm at the back wall). Tube routing from bag connectors runs forward along the floor to the valve assembly and cartridge dock. The flow meter sits in this zone, inline with the soda water path.

**What goes here:** The three 1/4" push-to-connect water fittings (tap water inlet, soda inlet, soda outlet). Placing water at the bottom means:
- Any drips or condensation fall downward and away from electronics
- Water supply lines under the sink are typically at or below this height, creating natural tube routing
- The flow meter on the interior is immediately behind the soda inlet and outlet fittings, minimizing internal tube runs

---

## 3. Connection Placement (Detail)

All positions described as viewed from behind the unit (installer's perspective). X=0 is the left edge of the back panel, X=280 is the right edge. Z=0 is the bottom, Z=400 is the top.

### 3a. 120V AC Power Inlet (IEC C14)

**Position:** X=210, Z=370 (upper-right quadrant).

**Fitting:** IEC 60320 C14 panel-mount inlet, 10A 250VAC rated. Screw-mount type with solder or quick-connect tabs on the interior.

**Panel cutout:** 27.4 x 19.8mm rectangular. Two M3 mounting screws at 40mm center-to-center pitch (horizontal).

**Interior clearance:** 25mm behind the panel surface for the terminal tabs. The PSU mounts within 50mm of this inlet on the electronics shelf.

**Why this position:**
- Upper-right places it directly behind the electronics pocket (X=192-272, Z=342-392 interior)
- Maximum vertical separation from water fittings (250mm above the water zone)
- The right side of the panel has no fluid connections, creating a dry column
- Standard IEC C13 power cord plugs in horizontally; the cord drops straight down and exits the cabinet

**Safety notes:**
- The C14 inlet should include an integrated fuse holder (common in combo C14+fuse modules). A 3A slow-blow fuse protects the internal PSU.
- Under UL/CSA requirements for under-sink appliances, the power cord must be suitable for wet/damp locations. The C14 approach allows the user to use a GFCI-protected outlet (required under NEC 210.8 for under-sink receptacles) with a standard C13 power cord.
- International variant: swap C14 for C14 with different fuse rating. The C13/C14 connector system is universal at 250VAC, so the same inlet works for 120V and 240V markets. Only the PSU and fuse change internally.

### 3b. Tap Water Inlet

**Position:** X=50, Z=50 (lower-left).

**Fitting:** John Guest PP1208W 1/4" bulkhead union. The bulkhead body passes through a 15.9mm (5/8") hole in the panel. A hex nut clamps against the exterior surface. On the exterior, a 90-degree elbow (John Guest PP0308W) directs the incoming tube downward parallel to the panel, preventing kinking against the cabinet wall.

**Interior clearance:** 30mm behind the panel for the fitting body plus the internal tube stub. The internal tube routes forward approximately 150mm to the clean water tee (T-CLEAN), which splits supply to both clean solenoid circuits.

**Why this position:**
- Lower-left groups it with the other water fittings but separates it from the soda water pair
- The tap water supply under most sinks is a cold water shutoff valve on the left side (when facing the cabinet). A T-splitter (ice maker style, 1/4" saddle valve or 3/8" to 1/4" adapter tee) connects to the cold supply, and the tube routes directly to this lower-left fitting
- Separated from soda water fittings by 90mm horizontally, making it impossible to cross-connect during installation

**Color coding:** Blue ring, embossed label "TAP IN". Blue tube convention matches ice maker kits.

### 3c. Carbonated Soda Water Inlet

**Position:** X=140, Z=50 (lower-center).

**Fitting:** John Guest PP1208W 1/4" bulkhead union with exterior 90-degree elbow. Same 15.9mm panel hole, same hex nut mounting.

**Interior clearance:** 30mm for fitting body. Internal tube routes approximately 80mm to the flow meter inlet. The flow meter sits directly behind this fitting, mounted to the enclosure floor or back wall interior.

**Why this position:**
- Centered horizontally, paired with the soda outlet to its right
- The soda inlet and outlet are a matched pair (the carbonation system's output connects to the inlet, and the outlet returns to the soda dispensing line). Placing them adjacent makes the installation logic obvious: soda comes in on the left of the pair, goes out on the right
- Interior routing to the flow meter is minimal (80mm straight shot)

**Color coding:** Green ring, embossed label "SODA IN". The incoming soda water line from the carbonation system is typically clear tubing.

### 3d. Carbonated Soda Water Outlet

**Position:** X=200, Z=50 (lower-right of water group).

**Fitting:** John Guest PP1208W 1/4" bulkhead union with exterior 90-degree elbow. Same specification as the inlet.

**Interior clearance:** 30mm for fitting body. Internal tube routes approximately 80mm from the flow meter outlet back to this fitting.

**Why this position:**
- Paired with the soda inlet, 60mm to its right (center-to-center)
- The tube from here routes externally to the faucet soda supply line
- Placed to the right of the inlet, following the left-to-right "flow direction" convention

**Color coding:** White ring, embossed label "SODA OUT" or "TO FAUCET".

### 3e. Flavor Line 1 Exit

**Position:** X=80, Z=200 (mid-panel, left side).

**Fitting:** A PG7 or PG9 cable gland (nylon, IP68) repurposed as a tube pass-through. The gland body threads into a 12.5mm (PG7) or 15.2mm (PG9) hole. The compression seal clamps around the silicone tube, providing both strain relief and a sealed pass-through. No push-to-connect fitting needed here since this is a continuous silicone tube from the pump outlet to the faucet dispenser.

**Tube spec:** Food-grade platinum-cured silicone, 1/4" OD (6.35mm) x 1/8" ID (3.18mm). The narrow ID reduces dead volume in the long external run to the faucet.

**Interior clearance:** 15mm for the gland body. The silicone tube routes from the dispensing solenoid SV-D1 (located at approximately X=0-60, Y=100-160, Z=0-35 interior) rearward along the enclosure floor, then upward to this exit point.

**Why this position:**
- Mid-height placement allows a gentle upward curve as the tube exits and routes up through the cabinet
- Left side corresponds to flavor line 1 (left-right matches the two-flavor layout inside)
- Vertically separated from water fittings (150mm above) and power (170mm below)

**Labeling:** Embossed "FLAVOR 1" with a colored ring or band matching the flavor line's identity (user-assignable; e.g., orange for citrus, purple for grape). The tube itself can be marked with heat-shrink labels at both ends.

### 3f. Flavor Line 2 Exit

**Position:** X=200, Z=200 (mid-panel, right side).

**Fitting:** Same PG7/PG9 cable gland as flavor line 1.

**Why this position:**
- Mirrors flavor line 1 on the opposite side
- The 120mm horizontal separation between the two flavor exits prevents tangling during the external run to the faucet
- Right side corresponds to flavor line 2

**Labeling:** Embossed "FLAVOR 2" with a different colored ring.

---

## 4. Flow Meter Integration

### 4a. Purpose

The flow meter measures the volume of carbonated soda water passing through the system in real time. The ESP32 uses this measurement to synchronize flavor pump activation: when the user pours soda water, the flow meter detects flow, and the firmware activates the appropriate peristaltic pump to inject flavor at the faucet in proportion to the soda water volume.

### 4b. Flow Meter Options

#### Option A: Hall-Effect Turbine Flow Meter (Recommended)

**DIGITEN 1/4" Quick Connect Flow Sensor**
- Dimensions: 63.5 x 30.5 x 38.1mm (L x W x H)
- Flow range: 0.3-10 L/min
- Frequency output: F = 36 x Q (L/min), approximately 36 pulses per liter at 1 L/min
- Working voltage: DC 3-24V (compatible with ESP32 3.3V logic via GPIO 23)
- Max current draw: 1.5mA at 5V
- Fittings: 1/4" push-to-connect on both ends
- Wetted materials: food-grade POM (polyoxymethylene) body
- Cost: approximately $8-12 USD
- Accuracy: +/- 2%

**GREDIA 1/4" Food-Grade Flow Sensor**
- Dimensions: 58 x 34 x 26mm (L x W x H) -- slightly more compact
- Flow range: 0.3-6 L/min
- Working voltage: DC 5-24V
- Wetted materials: food-grade plastic (ROHS compliant)
- Cost: approximately $8-10 USD
- G1/4" male thread connections (would need thread-to-push-connect adapters)

Both of these are turbine-style: a small impeller spins inside the flow path, and a Hall-effect sensor counts rotations. They are proven in coffee machines, water dispensers, and RO filter systems.

**Downsides of turbine type:**
- The impeller contacts the fluid. For carbonated water, CO2 bubbles passing through the turbine can cause erratic readings at very low flow rates.
- Moving parts wear over time, though at typical soda dispensing volumes (a few liters per day), lifespan is measured in years.
- The impeller and housing must be food-grade. The DIGITEN and GREDIA models claim food-grade POM, which is FDA-compliant for food contact.

#### Option B: Ultrasonic Clip-On Flow Meter (No Fluid Contact)

**Sonotec SONOFLOW CO.55**
- Clamps onto the outside of a plastic or silicone tube
- No fluid contact whatsoever -- ideal for hygiene
- Measures flow via transit-time ultrasonic principle
- Works with rigid and flexible tubing from approximately 2mm to 25mm OD
- Accuracy: 1-2%

**Downsides:**
- Cost: industrial ultrasonic clip-on meters start at $200-500+ for a single sensor. The Sonotec CO.55 is a commercial/industrial product priced accordingly.
- Size: the clamp-on sensor head is typically 30-50mm long and 20-30mm in diameter, similar to the hall-effect options in footprint but with an external clamp mechanism.
- Signal interface: many output 4-20mA or RS-485, requiring additional circuitry to interface with the ESP32. Some newer models offer pulse output.
- Overkill for this application. The soda water line is a simple, clean fluid at low flow rates. The cost premium of ultrasonic is justified in sterile or corrosive applications, not here.

#### Option C: Paddlewheel or Gear Flow Meter

- Gear-type meters (like the GREDIA oil/fuel models) are more common for viscous liquids
- Paddlewheel meters are bulkier (typically 1/2" or larger fittings)
- Neither is well-suited for 1/4" low-flow carbonated water

### 4c. Recommendation

**Use the DIGITEN 1/4" Quick Connect Hall-Effect Flow Sensor.** It has integrated 1/4" push-to-connect fittings (no adapters needed), is compact, food-grade, cheap, and outputs a pulse signal directly compatible with ESP32 GPIO 23 (already assigned for flow in firmware).

### 4d. Flow Meter Placement

The flow meter sits inline between the soda water inlet bulkhead and the soda water outlet bulkhead. Both bulkheads are on the back panel at Z=50mm. The flow meter mounts on the enclosure interior, as close to the back panel as possible.

**Interior position:** Approximately X=120-185, Y=262-292 (against the back wall), Z=15-55.

**Mounting:** The DIGITEN sensor has a flat bottom surface. Mount it to the enclosure floor using a simple printed clip or bracket (two screws into heat-set inserts). Orient the sensor so its 1/4" push-connect ports face left and right (toward the inlet and outlet bulkheads). The signal cable (15cm, 3-wire: VCC red, GND black, signal yellow) routes upward along the back wall interior to the electronics shelf at Z=342+.

**Internal tube routing:**
- Soda inlet bulkhead (X=140, Z=50 on panel) -> 80mm of 1/4" hard tube -> flow meter inlet port
- Flow meter outlet port -> 80mm of 1/4" hard tube -> soda outlet bulkhead (X=200, Z=50 on panel)
- Total internal soda water path: approximately 160mm of tube + 60mm through the meter body = 220mm

**Signal wire routing:** The flow meter's 15cm signal cable runs upward along the back wall interior (Y=292, from Z=50 to Z=342) to reach the ESP32 on the electronics shelf. This is approximately 290mm of vertical run. The factory 15cm cable is too short. Options:
- Extend with 22AWG stranded wire (solder + heat shrink, 3 conductors)
- Use a JST connector pair at the meter end for clean disconnection during service

The signal wire (GPIO 23, interrupt-driven pulse counting) should be routed away from the L298N motor power wires. Running it along the back wall while motor power runs along the side walls provides natural separation.

---

## 5. Flavor Tube Exits

### 5a. What These Tubes Carry

Each flavor line carries concentrated syrup under peristaltic pump pressure (approximately 0.1-0.3 bar, very low). The syrup flows from the bag -> through the pump cartridge -> through the dispensing solenoid -> out through the back panel -> externally up through the cabinet -> through or alongside the faucet supply lines -> to a dispenser nozzle at the faucet.

### 5b. Tube Specification

- Material: Platinum-cured food-grade silicone (FDA 21 CFR 177.2600 compliant)
- OD: 1/4" (6.35mm)
- ID: 1/8" (3.18mm) or 3/16" (4.76mm)
- Wall thickness: 1/16" (1.59mm)
- The narrow bore is intentional: it minimizes dead volume in the 600-900mm external run

### 5c. Back Panel Pass-Through

**Recommended: PG7 nylon cable gland (IP68 rated).**

A cable gland is the right tool here. It threads into the panel from the inside, a locknut secures it on the outside, and the internal compression ring seals tightly around the silicone tube. This provides:
- Strain relief: the tube cannot pull through the fitting
- Sealing: prevents insects, moisture, and debris from entering the enclosure through the hole
- Clean appearance: the nylon gland body looks professional
- Easy installation: push the tube through the gland before tightening, then snug the compression nut

**PG7 gland specs:**
- Thread OD: 12.5mm
- Panel hole: 12.5mm
- Clamping range: 3-6.5mm (perfect for 6.35mm OD silicone tube)
- Cost: under $0.50 each

**Alternative: Bulkhead fitting with barb.** A 1/4" barb-to-bulkhead fitting would also work but is more expensive, more complex, and creates a disconnect point where there should not be one. The silicone tube should be continuous from the dispensing solenoid to the faucet nozzle -- no joints in the external run means no leak points and no dead volume pockets.

### 5d. External Routing

From the back panel, each flavor tube routes:
1. Upward along the cabinet back wall (~300mm vertical rise)
2. Through the cabinet top or alongside the faucet supply risers (~200mm)
3. Through a countertop hole or alongside the faucet mounting hardware (~50mm)
4. To a dispenser nozzle at the faucet (~100mm to reach the spout area)

**Total external run: approximately 600-900mm** depending on cabinet height and faucet position. A standard under-sink cabinet has about 600mm from the enclosure back panel to the countertop surface. Add 150-300mm for routing to the faucet location.

### 5e. Dead Volume Concern

Dead volume is the syrup sitting stagnant in the tube between pours. With 1/8" ID (3.18mm) tubing at 900mm length:

    Dead volume = pi * (1.59mm)^2 * 900mm = 7,148 mm^3 = 7.1 ml per line

At 3/16" ID (4.76mm):

    Dead volume = pi * (2.38mm)^2 * 900mm = 16,009 mm^3 = 16.0 ml per line

The 1/8" ID option keeps dead volume to about 7ml per line. At typical syrup-to-water ratios (1:5 to 1:10), 7ml of syrup flavors 35-70ml of water. After a long idle period (overnight), the first pour flushes this stale syrup. Mitigation strategies:

- **Firmware pre-purge:** Before the first pour of the day, the pump runs briefly to push stale syrup through. The purge volume equals the dead volume (7ml). This can be triggered automatically at a scheduled time or on the first flow meter detection.
- **Refrigerated syrup:** If the syrup is kept cool (under-sink is typically 15-20C), bacterial growth in the dead volume is slow.
- **Narrow bore:** Using 1/8" ID instead of 3/16" ID cuts dead volume by more than half.

**Recommendation: Use 1/4" OD x 1/8" ID silicone tubing for the external flavor runs.** The higher flow resistance of the narrow bore is irrelevant because the peristaltic pump generates sufficient pressure, and the flow rates are low (10-50 ml/min of concentrated syrup).

---

## 6. Tap Water Inlet

### 6a. Purpose

The tap water inlet supplies fresh water for automated cleaning and rinsing cycles. It does not carry drinking water to the faucet. It is used to:
- Flush the hopper funnel and fill tubes after a flavor refill (removing residual syrup)
- Rinse the bag interiors during a periodic deep clean cycle
- Push clean water through the dispensing path to flush stale syrup

### 6b. Connection to Home Plumbing

The tap water inlet connects to the home's cold water supply via a T-splitter or saddle valve, exactly like an ice maker or under-sink RO system. Common connection methods:
- **1/4" saddle valve** clamped onto the cold water supply line (simplest, cheapest, but can leak over time)
- **3/8" compression tee** on the cold water shutoff valve, with a 3/8" to 1/4" adapter (more reliable, standard for RO systems)
- **1/2" to 1/4" push-to-connect adapter tee** (John Guest, SharkBite) on the cold water riser

The installation kit should include the appropriate adapter tee and 5 feet of 1/4" PE tubing to reach from the cold water supply to the enclosure back panel.

### 6c. Internal Routing

From the back panel bulkhead, the tap water routes approximately 150mm to a tee fitting (T-CLEAN) that splits the supply to both flavor channels. Each branch passes through a needle valve (flow restriction to prevent over-pressurizing the bags) and a normally-closed solenoid valve (SV-C1, SV-C2) before reaching the flavor line tees (T1, T2).

**Usage frequency:** Cleaning cycles are automated by firmware. Typical schedule:
- After each hopper refill: brief flush of the hopper line (30 seconds, ~200ml of water)
- Weekly: full rinse cycle of both flavor paths (2-3 minutes, ~500ml of water per line)
- The tap water line is idle most of the time; the solenoid valves are normally closed

### 6d. Pressure Considerations

Municipal tap water pressure is typically 40-80 PSI (2.8-5.5 bar). The needle valve (NV) downstream of T-CLEAN restricts flow to prevent this full pressure from reaching the bags (which are rated for low pressure only). The needle valve should be pre-set during manufacturing and not user-adjustable.

---

## 7. Power Inlet

### 7a. IEC C14 vs. Hardwired Cord

| Factor | IEC C14 (Detachable) | Hardwired Cord |
|--------|---------------------|----------------|
| User experience | Familiar (same as PC, monitor, printer) | Permanently attached; no accidental disconnection |
| Installation | Plug in a standard C13 cord (included in box) | Thread cord through cabinet; strain relief at panel |
| Cord replacement | User swaps cord (any C13 cord works) | Requires opening enclosure or cutting/splicing |
| Safety certification | C14 inlets are UL/CSA recognized components | Hardwired requires strain relief grommet meeting UL standards |
| Under-sink context | Cord unplugs cleanly for slide-out tray servicing | Must have enough slack for tray travel |
| International variants | Same C14 inlet worldwide; only the plug end of the C13 cord changes | Different cord molded for each market |

**Recommendation: IEC C14 inlet.** The detachable cord makes installation and servicing easier. The user plugs a C13 cord into the back of the enclosure and the other end into a GFCI-protected outlet under the sink. When sliding the enclosure out on its tray, the C13 cord unplugs or has enough slack (it is a standard 6-foot cord, plenty of slack).

### 7b. Internal PSU

The IEC C14 inlet connects to a compact enclosed AC-DC power supply module on the electronics shelf. The PSU converts:
- 120V AC (or 240V AC for international) to 12V DC for pump motors and solenoid valves
- 12V DC steps down via a buck converter to 5V and 3.3V for logic (ESP32, displays, sensors)

**PSU specification:**
- Input: 100-240V AC, 50/60Hz (universal input, works worldwide)
- Output: 12V DC, 3A (36W) -- covers worst-case draw of ~24W with headroom
- Form factor: enclosed module (like a Meanwell IRM-45-12 or similar), approximately 80 x 52 x 29mm
- Mounting: screw-mount to the electronics shelf

The PSU should be placed within 50mm of the C14 inlet to keep the 120V AC wire run as short as possible inside the enclosure. All 120V wiring inside the enclosure must be insulated, routed away from fluid paths, and secured with cable ties.

### 7c. GFCI Considerations

Under NEC 210.8(A)(7) and 210.8(D), receptacles under kitchen sinks must be GFCI-protected. The enclosure does not need to contain its own GFCI device as long as it plugs into a GFCI-protected outlet (which is code-required in this location). The installation instructions should state: "Connect only to a GFCI-protected outlet."

### 7d. Safety Separation

The power inlet is at Z=370 (top of panel). The nearest water fitting is at Z=50 (bottom). This provides 320mm of vertical separation between mains power and water connections. On the interior, the electronics shelf at Z=342 creates a physical barrier between the power/electronics zone (above Z=342) and the fluid zone (below Z=310).

---

## 8. Cable and Tube Management

### 8a. The Problem

Six things exit the back panel: three water tubes, two flavor tubes, and one power cord. Under a dark cabinet with limited reach, this can become a tangled mess. The installer needs a foolproof system.

### 8b. Grouping Strategy

Organize connections into three distinct groups with physical separation on the panel:

| Group | Connections | Panel Zone | Color Theme |
|-------|-----------|------------|-------------|
| Water | Tap in, Soda in, Soda out | Bottom (Z=30-70) | Blue/Green/White rings |
| Flavor | Flavor 1, Flavor 2 | Middle (Z=180-220) | Colored bands (user-assignable) |
| Power | IEC C14 | Top (Z=350-390) | Black (standard power cord color) |

### 8b. Labeling System

Stickers peel off in humid under-sink environments. All labeling must be permanent:

- **Embossed text** on the 3D-printed (prototype) or injection-molded (production) back panel, directly adjacent to each fitting. Raised letters can be felt by touch in the dark.
- **Color-coded snap-on rings** around each bulkhead fitting nut. Print in colored PETG or silicone-overmold in production.
- **Matching tags** at the far end of each tube (at the carbonation system, at the faucet, at the cold water supply). The installer can verify connections by matching tags without tracing tubes.
- **Molded arrows** showing flow direction next to the soda inlet and outlet.

### 8c. Quick-Install Connection Order

Print this sequence on a label inside the enclosure lid or on a separate quick-start card:

1. **Power first.** Plug the C13 power cord into the top of the back panel. Plug the other end into a GFCI outlet. The unit powers on and runs a self-test.
2. **Soda water pair.** Connect the soda inlet (green, "SODA IN") to the carbonation system output. Connect the soda outlet (white, "SODA OUT") to the faucet soda supply line.
3. **Tap water.** Connect the tap water inlet (blue, "TAP IN") to the cold water T-splitter.
4. **Flavor lines.** Route the two silicone flavor tubes from the mid-panel exits up through the cabinet to the faucet dispenser. Secure with cable clips every 150mm.
5. **Test.** Run a glass of soda water through the faucet. The enclosure display should show flow detected. Trigger a test dispense from the display menu.

### 8d. Strain Relief

| Connection | Strain Relief Method |
|-----------|---------------------|
| Water fittings (x3) | 90-degree elbows (John Guest PP0308W) on the exterior of each bulkhead. Tubes exit parallel to the panel, never perpendicular. |
| Flavor tubes (x2) | PG7 cable glands with compression seal. The gland locks the tube in place. |
| Power cord | The IEC C14 connector itself provides mechanical retention (the C13 plug clicks into the C14 inlet). A printed cord clip on the panel below the inlet prevents the cord from pulling sideways. |

---

## 9. Installation Considerations

### 9a. Cabinet Wall Clearance

The back panel faces the cabinet back wall. Push-to-connect bulkhead fittings protrude approximately 30-40mm from the panel surface. With 90-degree elbows added to the exterior, total protrusion is approximately 50-55mm, but tubes exit parallel to the panel (not perpendicular), so the enclosure can sit as close as 60mm (2.4 inches) from the cabinet wall.

The IEC C14 inlet protrudes approximately 35-40mm when a C13 plug is inserted. The plug exits perpendicular to the panel but the cord is flexible and bends easily.

**Minimum clearance between back panel and cabinet wall: 75mm (3 inches).** This provides room for:
- Fitting protrusion (55mm)
- Tube bends (20mm minimum bend radius)
- Fingers during installation (pushing tubes into fittings requires 50mm of finger access above each fitting)

At 300mm enclosure depth + 75mm rear clearance = 375mm total depth consumed. Under-sink cabinet usable depth is 480-510mm, leaving 105-135mm of front clearance for the slide-out tray overhang and cabinet door clearance.

### 9b. Slide-Out Tray and Connection Slack

The enclosure sits on a slide-out tray that travels approximately 150-200mm forward for hopper refill and cartridge access. All connections at the back panel must have enough slack to accommodate this travel without pulling, kinking, or disconnecting.

**Slack requirements:**

| Connection | Required Slack | How Achieved |
|-----------|---------------|--------------|
| Water tubes (x3) | 200mm of slack in each tube behind the panel | The 90-degree elbows direct tubes downward. Tubes make a gentle U-bend loop below the fittings before routing to their destinations (carbonator, cold water supply, faucet line). The U-bend absorbs travel. |
| Flavor tubes (x2) | 200mm of slack | Silicone tubing is inherently flexible. The external run to the faucet is 600-900mm long. The first 200mm hangs in a service loop behind the enclosure. |
| Power cord | 200mm of slack | A standard 6-foot (1.8m) C13 cord provides ample slack. The cord coils loosely behind the enclosure. |

**Critical: push-to-connect fittings do not disconnect under tension** as long as the tube is fully inserted (the collet grips the tube with approximately 15-25 lbs of pull-out force). The 200mm of slack prevents any tension from reaching the fittings during normal tray travel. The tray should have a travel stop that prevents pulling beyond the designed 200mm.

### 9c. One-Time Installation

All back panel connections are made once during initial installation. After that:
- Hopper refills (weekly) happen from the top -- no back panel access needed
- Cartridge swaps (every 18-36 months) happen from the front -- no back panel access needed
- The back panel connections are "set and forget"

The only reason to access the back panel after installation is to disconnect the enclosure entirely (moving, replacing, or major repair). Even then, push-to-connect fittings release easily by pressing the collet.

---

## 10. ASCII Layout Diagram

Viewed from behind the enclosure (installer's perspective). The left/right orientation is mirrored from the interior view.

```
                         280mm
    ├──────────────────────────────────────────┤

    ┌──────────────────────────────────────────┐ ─┬─
    │                                          │  │
    │                                          │  │
    │                                          │  │  Z=400
    │                          ┌─────────┐     │  │
    │                          │  120V   │     │  │  Z=370 (center)
    │                          │  IEC    │     │  │
    │                          │  C14    │     │  │
    │                          └─────────┘     │  │
    │                            X=210         │  │
    │                                          │  │
    │                                          │  │  Z=310
    │──────────────────────────────────────────│  │  (electronics zone
    │                                          │  │   boundary, interior)
    │                                          │  │
    │                                          │  │
    │                                          │  │
    │    (FLAVOR 1)              (FLAVOR 2)    │  │
    │       ◎                       ◎          │  │  Z=200 (center)
    │     X=80                    X=200        │  │
    │    PG7 gland               PG7 gland     │  │
    │                                          │  │
    │                                          │  │
    │                                          │  │  Z=130
    │── ── ── ── ── ── ── ── ── ── ── ── ── ──│  │  (bag connector zone
    │                                          │  │   boundary, interior)
    │                                          │  │
    │                                          │  │
    │   ●           ●           ●              │  │  Z=50 (center)
    │  TAP IN     SODA IN    SODA OUT          │  │
    │  (blue)     (green)    (white)           │  │
    │  X=50       X=140      X=200             │  │
    │   1/4"PTC    1/4"PTC    1/4"PTC          │  │
    │                                          │  │
    └──────────────────────────────────────────┘ ─┴─ Z=0

    ├──────────────────────────────────────────┤
                         280mm

    PTC = push-to-connect bulkhead (John Guest PP1208W)
    ◎   = cable gland tube pass-through (PG7)
    ●   = bulkhead fitting (15.9mm hole)
```

### Dimensioned Detail of Water Zone (Bottom 70mm)

```
    ┌──────────────────────────────────────────┐
    │                                          │ Z=70
    │                                          │
    │   ●──40mm──●──60mm──●                    │ Z=50
    │  TAP       SODA     SODA                 │
    │  IN        IN       OUT                  │
    │  X=50      X=140    X=200                │
    │                                          │ Z=30
    └──────────────────────────────────────────┘ Z=0

    All fittings have 90-degree elbows on the exterior
    directing tubes downward (parallel to panel).
    Interior: flow meter sits between SODA IN and SODA OUT.
```

### Interior View: Flow Meter Position (Top-Down, Back Wall Slice)

```
    ┌──────────────── 272mm interior ─────────────────┐
    │                                                  │
    │  [TAP IN]                                        │
    │   bulkhead        ┌───────────────┐              │
    │   X=46          │ FLOW METER    │              │
    │                   │ (DIGITEN)    │              │
    │                   │ 63 x 30 x 38│              │
    │  [SODA IN]──tube──│→  IN    OUT →│──tube──[SODA OUT]
    │   bulkhead        └───────────────┘      bulkhead│
    │   X=136              X=116-180          X=196    │
    │                                                  │
    │               signal wire ↑                      │
    │               routes up to                       │
    │               electronics shelf                  │
    └──────────────────────────────────────────────────┘
      (all X values are interior coordinates = exterior minus 4mm)
```

---

## 11. Panel Construction

### 11a. Removable Back Panel

The back panel should be a separate piece that screws onto the enclosure body. This allows:
- Pre-installation of all bulkhead fittings and glands before attaching the panel to the enclosure
- Internal plumbing access by removing 4-6 screws (M3 into heat-set inserts)
- Replacement if a fitting hole wears out (cheap, small print)
- Better 3D print quality (a flat panel prints cleaner than an integrated wall on a large box)

### 11b. Panel Thickness

4mm, matching the enclosure wall thickness. The John Guest bulkhead hex nut clamps against this thickness. The IEC C14 inlet is designed for 1-3mm panels; a 4mm panel may require a slightly recessed mounting area or a spacer on the interior side.

### 11c. Drip Dam

A 2mm raised ridge molded into the exterior face of the panel, running horizontally at Z=120mm (between the water zone and flavor zone). Any condensation or minor drip from the water fittings below pools against this ridge and drains off the panel edges rather than wicking upward toward the flavor exits or power inlet.

### 11d. Sealing

The enclosure is not waterproof (it has ventilation for the PSU and electronics). No gasket is needed between the back panel and the enclosure body. The bulkhead fittings and cable glands provide their own seals at each penetration point.

---

## 12. Bill of Materials (Back Panel)

| Item | Specification | Qty | Est. Cost |
|------|--------------|-----|-----------|
| Back panel (3D printed, PETG) | 280 x 400 x 4mm with mounting holes, fitting holes, embossed labels | 1 | ~$3 material |
| John Guest PP1208W bulkhead union | 1/4" x 1/4" push-to-connect | 3 | ~$4 each = $12 |
| John Guest PP0308W 90-degree elbow | 1/4" push-to-connect | 3 | ~$1.50 each = $4.50 |
| IEC C14 panel-mount inlet with fuse holder | 10A 250VAC, screw mount, integrated 5x20mm fuse | 1 | ~$3 |
| PG7 nylon cable gland | 3-6.5mm clamping range, IP68 | 2 | ~$0.50 each = $1 |
| M3 x 8mm screws | Panel mounting (into heat-set inserts in enclosure body) | 6 | ~$0.50 total |
| M3 heat-set inserts | Brass, press-in | 6 | ~$1 total |
| DIGITEN 1/4" flow meter | Hall-effect, 0.3-10 L/min, food-grade | 1 | ~$10 |
| **Total** | | | **~$35** |

---

## 13. Open Questions and Next Steps

| Question | Impact | Resolution Path |
|----------|--------|----------------|
| Does the DIGITEN flow meter read accurately with carbonated (CO2-dissolved) water? | If bubbles disrupt the turbine, readings will be erratic. The soda water should be fully dissolved CO2, not visibly bubbly, which helps. | Bench test: run carbonated water through the meter and compare pulse count to measured volume. |
| Is 1/4" OD x 1/8" ID silicone tube too restrictive for the peristaltic pump? | The pump must overcome friction in 900mm of narrow-bore tubing. | Bench test: measure flow rate and pump stall pressure with 1m of 1/8" ID silicone. If too restrictive, switch to 3/16" ID (acceptable dead volume increase from 7ml to 16ml). |
| Should the power inlet include an on/off switch? | A combined C14 inlet + rocker switch + fuse module is available (common in PC PSUs). It lets the user power-cycle the unit without unplugging. | Decide during electronics integration. The switch adds ~10mm to the panel footprint. |
| How to route flavor tubes through the countertop? | The tubes need to reach the faucet area. Options: through the existing faucet mounting hole, through a separate 1/2" hole, or alongside the faucet supply risers if the hole is large enough. | Research faucet-side integration separately. This is outside the scope of the back panel but affects the flavor tube length spec. |
| Does the slide-out tray need a drip tray extension behind the enclosure? | When the enclosure slides forward, the area behind it is exposed. Any drip from fittings lands on the bare cabinet floor. | Consider a rear drip lip on the slide-out tray that extends 50mm behind the enclosure back panel. |

---

## References

- [v1-master-spatial-layout.md](v1-master-spatial-layout.md) -- component positions, coordinates, clearance analysis
- [back-panel-and-routing.md](back-panel-and-routing.md) -- earlier zone-era research on panel layout and internal routing (different connection inventory but useful fitting and strain relief details)
- [requirements.md](../requirements.md) -- enclosure functional requirements, connection inventory
- [gpio-planning.md](../../../gpio-planning.md) -- ESP32 GPIO 23 assigned to flow meter pulse input, signal routing notes
