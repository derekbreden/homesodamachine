# Display System and Front Panel Design

**Synthesized:** 2026-03-24
**Sources:** requirements.md, v1-master-spatial-layout.md, gpio-planning.md, commercial retractable cable research, SPI/I2C signal integrity literature

This document covers the detachable display system -- two round screens on retractable cat6 tethers that dock flush to the front panel and pull out for countertop or fridge placement. The retractable tether is a signature UX feature of the product. This research explores whether the concept is mechanically sound, electrically viable, and producible at reasonable cost.

---

## 1. Retractable Cable Mechanism

### 1.1 Cable Dimensions and Spool Geometry

Cat6 cable (unshielded, UTP) has an outer diameter of approximately 5.5-6.5mm depending on jacket thickness. For planning, assume 6mm OD.

One meter of 6mm cable wound on a spool:

```
Cable cross-section area = pi * (3mm)^2 = 28.3 mm^2
1000mm of cable volume   = 28,274 mm^3

For a flat spiral spool (single layer):
  Circumference at radius r = 2 * pi * r
  If the hub radius is 15mm, one wrap = 94mm of cable
  Wraps needed for 1000mm: ~11 wraps
  Outer radius = 15 + (11 * 6mm) = 81mm --> 162mm diameter

That is far too large for the enclosure.
```

A multi-layer spool is required:

```
For a spool with 20mm hub radius, 10mm winding width (stacks ~1.5 layers of 6mm cable):
  Layer 1: hub circumference = 2 * pi * 20 = 126mm per wrap
  Wraps in 10mm width: floor(10 / 6) = 1 wrap per layer
  Actually, with 10mm width and 6mm cable, you get 1 wrap per layer.

Better approach -- a wider spool:

  Hub diameter: 30mm (radius 15mm)
  Spool width (axial): 15mm (allows 2 wraps side by side per layer)
  Layer 1 circumference: 2 * pi * 15 = 94mm; 2 wraps = 188mm of cable
  Layer 2 circumference: 2 * pi * 21 = 132mm; 2 wraps = 264mm
  Layer 3 circumference: 2 * pi * 27 = 170mm; 2 wraps = 340mm
  Layer 4 circumference: 2 * pi * 33 = 207mm; 2 wraps = 414mm
  Running total: 188 + 264 + 340 + 414 = 1,206mm

  Outer diameter: 2 * (33 + 6) = 78mm
  Spool width: 15mm
  Hub depth including spring housing: ~25mm
```

**Summary:** A spool of roughly 80mm diameter and 25mm depth can hold 1 meter of cat6 cable. Two spools require 80mm x 2 = 160mm of width or 80mm of width if stacked vertically. Given the enclosure is 272mm wide internally, side-by-side placement behind the front panel is feasible. Depth behind the panel is 25-30mm per reel, which is within the Y=0-50mm front zone.

### 1.2 Spring Mechanism

Two main options:

**Constant-force spring (clock spring):** A pre-stressed flat spring wound inside the hub. As cable is pulled out, the spring stores energy. When released, the spring retracts the cable. This is the mechanism used in retractable badge holders, vacuum cleaner cords, and retractable ethernet cables.

- Advantages: smooth, consistent retraction force regardless of how much cable is extended.
- Disadvantages: spring fatigue over thousands of cycles, slight manufacturing complexity.

**Spiral torsion spring:** Simpler, cheaper. Retraction force increases as more cable is pulled out (spring winds tighter). Acceptable for 1m travel.

**Recommendation:** Constant-force spring. The retraction force should be in the 0.3-0.5 N range -- enough to wind up slack cable but not enough to drag a 40-gram display module off a countertop. Commercial retractable badge reels operate at roughly 0.2-0.4 N and are a useful reference design.

### 1.3 Locking Mechanism

The cable must stay extended at the user's chosen length, not constantly retract. Three options:

1. **Ratchet/click-stop:** Pull to desired length, a detent locks. Tug sharply to release (like a retractable dog leash). Simple and reliable. Adds ~5mm to spool depth.

2. **Friction brake:** User pulls cable; it stays where released due to friction. A quick tug overcomes static friction and allows retraction. Less precise, depends on cable angle.

3. **Pull-to-lock, pull-to-release:** Pull cable to desired length, give a short extra tug to engage lock. Another short tug releases. This is how most retractable badge reels work. Familiar mechanism.

**Recommendation:** Pull-to-lock, pull-to-release. It is the most common mechanism in retractable reels, well understood, and users already know the interaction from badge holders and retractable USB cables.

### 1.4 Strain Relief

Both ends of the cable need strain relief:

- **Panel exit:** Rubber grommet or molded strain relief where cable exits the front panel. Must allow the cable to pivot at least 45 degrees in any direction without kinking. A ball-and-socket strain relief (like on laptop charger cables) is ideal.
- **Display connector:** Same ball-and-socket or flexible boot where the cable enters the display module's RJ45 jack. This end sees the most flexing.
- **Bend radius:** Cat6 minimum bend radius is 4x outer diameter = 24mm. The spool hub (15mm radius = 30mm diameter) is above this minimum, so winding onto the spool does not violate bend radius.

### 1.5 Commercial Retractable Cat6 Products

Retractable cat6 cables do exist as travel accessories (Monoprice, Cable Matters, and generic brands sell them for laptop use). These typically:

- Contain 1-1.5m of flat cat6 cable (thinner than round, ~3mm thick)
- Use a central spool mechanism with dual retraction (cable exits both sides)
- Are rated for hundreds of extend/retract cycles

**Key insight:** Flat cat6 cable (3mm thick vs. 6mm round) would halve the spool diameter. A flat cat6 cable on a spool could fit in roughly 50-55mm diameter. This is a significant improvement and worth specifying.

**Flat cat6 spool estimate:**

```
Flat cat6: ~7mm wide x 3mm thick
Hub radius: 12mm
Spool width: 10mm (allows ~1.4 wraps side by side, effectively 1)
Layer 1: 2 * pi * 12 = 75mm per wrap
Layer 2: 2 * pi * 15 = 94mm
...continuing...
~12-13 layers to reach 1000mm
Outer radius: 12 + (13 * 3) = 51mm --> ~102mm diameter

With 2 wraps per layer (14mm spool width):
Layer 1: 150mm, Layer 2: 188mm, Layer 3: 226mm, Layer 4: 264mm,
Layer 5: 302mm = total 1,130mm in 5 layers
Outer radius: 12 + (5 * 3) = 27mm --> 54mm diameter
Spool width: 14mm + spring housing: ~22mm total depth
```

**Revised recommendation:** Use flat cat6 cable. Spool diameter drops to approximately 55mm, spool depth to approximately 22mm. Two spools side-by-side require 110mm of width (well within 272mm interior). Depth behind the front panel is only 22mm.

---

## 2. Cat6 Pinout for Power and Data

### 2.1 Available Conductors

Standard cat6 has 8 conductors arranged in 4 twisted pairs:

| Pair | Pin A | Pin B | T-568B Color |
|------|-------|-------|-------------|
| 1 | Pin 4 | Pin 5 | Blue / Blue-White |
| 2 | Pin 1 | Pin 2 | Orange-White / Orange |
| 3 | Pin 3 | Pin 6 | Green-White / Green |
| 4 | Pin 7 | Pin 8 | Brown-White / Brown |

### 2.2 Display Communication Protocol

From the GPIO planning document, both displays communicate via **UART**:

- Display 1 (RP2040): ESP32 GPIO 32 (TX) and GPIO 35 (RX) -- Serial2
- Display 2 (ESP32-S3): ESP32 GPIO 15 (TX) and GPIO 34 (RX) -- Serial1

This is significant. The existing firmware architecture uses UART, not SPI, to talk to the displays. UART requires only 2 signal lines (TX, RX) and is far more tolerant of cable length than SPI. UART at 115200 baud over 1 meter of cat6 is electrically trivial.

### 2.3 Proposed Pinout

| RJ45 Pin | Cat6 Pair | Function | Notes |
|----------|-----------|----------|-------|
| 1 | Pair 2A | UART TX (from main board) | Data to display controller |
| 2 | Pair 2B | UART RX (to main board) | Data from display controller |
| 3 | Pair 3A | RESET (active low) | Optional; allows main board to reset display |
| 4 | Pair 1A | VCC (+5V) | Power for display module |
| 5 | Pair 1B | VCC (+5V) | Doubled for current capacity |
| 6 | Pair 3B | Backlight PWM | Optional; or tie to VCC on the display module |
| 7 | Pair 4A | GND | Power return |
| 8 | Pair 4B | GND | Doubled for current capacity |

**Why 5V, not 3.3V:** See Section 7 (power budget). Voltage drop over 1m of thin cat6 conductor at 100mA makes 3.3V delivery unreliable. Sending 5V and regulating to 3.3V locally on the display module with an LDO is far more robust.

**Why UART pairs are split across different twisted pairs:** The TX and RX signals are on pins 1 and 2 (a twisted pair in T-568B), which gives good common-mode noise rejection. The two power pins (4, 5) share a pair, as do the two ground pins (7, 8). This keeps power delivery balanced across pairs.

### 2.4 Signal Integrity: UART over 1 Meter

UART at 115200 baud has a bit period of ~8.7 microseconds. The rise time of a 3.3V CMOS output is typically 5-10 ns. Over 1 meter of cat6, propagation delay is approximately 5 ns. Cable capacitance is roughly 50-55 pF/m for cat6.

At these frequencies and distances, signal integrity is a non-issue. Cat6 is rated for 250 MHz operation over 100 meters. Running 115200 baud UART over 1 meter is using approximately 0.0005% of the cable's bandwidth capacity.

Even at 921600 baud (the highest common UART rate), signal integrity over 1m of cat6 remains trivial.

**Comparison to SPI (if it were needed):** SPI at 10 MHz over 1m would be marginal -- reflections, crosstalk, and capacitive loading become real concerns without termination resistors. SPI at 40 MHz over 1m would be unreliable without careful impedance matching. The UART architecture completely sidesteps these issues.

### 2.5 EMI Considerations

The enclosure contains solenoid valves (8 total, driven at 12V with inductive kick-back) and motor drivers (L298N H-bridges with PWM). These generate broadband EMI during switching.

Mitigations for the cat6 display cable:

1. **Twisted pairs provide inherent noise rejection.** Common-mode noise from nearby solenoids couples equally into both conductors of a pair and cancels at the receiver.
2. **Short cable run (1m max).** EMI pickup is proportional to cable length.
3. **Low data rate.** UART at 115200 baud has massive noise margin. A spike would need to last ~4 microseconds to corrupt a bit.
4. **Physical separation.** The cable exits the front panel and routes away from the enclosure interior where solenoids and motors live. The most vulnerable segment is the 20-25mm behind the front panel where the cable runs from the spool to the enclosure interior. Route this segment away from motor driver wires.

**Shielded cat6 (STP):** Not necessary for this application. The cost and stiffness increase of STP cable would make the retraction mechanism harder (stiffer cable = stronger spring needed = higher retraction force = display gets yanked around). Stick with UTP.

---

## 3. Display Module Design

### 3.1 Display Selection

The GC9A01 1.28-inch round TFT is the most common round display in the embedded space. Key specs:

| Parameter | Value |
|-----------|-------|
| Diagonal | 1.28 inches (32.4mm active area diameter) |
| Resolution | 240 x 240 pixels |
| Interface | SPI (to the local controller: RP2040 or ESP32-S3) |
| Backlight | LED, ~20-40mA at 3.3V |
| Viewing angle | IPS, ~170 degrees |
| Module dimensions | ~37mm diameter PCB, ~4mm thick |

Larger alternative: 1.69-inch round TFT (also GC9A01-based, 240x240). Active area ~38mm diameter, module ~43mm diameter. Slightly more readable but the 1.28-inch is more common and cheaper.

**Recommendation:** Start with the 1.28-inch GC9A01. If user testing reveals readability issues (these displays will be viewed from arm's length on a countertop), upgrade to 1.69-inch. The display module housing should accommodate either size with a different bezel insert.

### 3.2 Module Form Factor

The detachable display module is a self-contained puck:

```
        ┌───────────────────┐
        │   protective lens │  ~1.5mm polycarbonate or glass
        ├───────────────────┤
        │   round TFT       │  ~4mm (display + PCB)
        ├───────────────────┤
        │   controller PCB  │  ~3mm (RP2040/ESP32-S3 + passives)
        │   (behind display)│
        ├───────────────────┤
        │   housing base    │  ~3mm (RJ45 jack, magnets, flat base)
        └────────┬──────────┘
                 │ RJ45 jack (recessed)
                 │ cable exits downward or rearward
```

**Overall dimensions:**
- Diameter: 50mm (allows ~6mm bezel around a 38mm display area, accommodates either 1.28" or 1.69" TFTs)
- Thickness: 12-15mm
- Weight: 25-40 grams (PCB + display + housing + magnets)

### 3.3 Mounting Options for the Detached Display

When pulled out of the enclosure, the display needs to be placed somewhere stable:

1. **Flat on countertop:** The flat base with a slight rubber ring for grip. Display faces up. Good for glancing down at. Cable coils loosely beside it.

2. **Angled stand (built-in kickstand):** A small fold-out leg on the back tilts the display 30-45 degrees toward the user. Similar to a phone kickstand. Adds ~2mm to thickness when folded.

3. **Magnetic mount:** 2-3 small neodymium disc magnets (6mm dia x 2mm thick) embedded in the base. Total pull force ~1-2 kg, enough to hold on a fridge or steel cabinet. The display module weighs <40g, so even modest magnets are overkill.

4. **Adhesive mount:** A 3M Command strip slot on the back. User can stick the display to a cabinet face. Removable.

5. **Clip mount:** Spring clip for attaching to a shelf edge. Adds bulk; probably overkill for V1.

**Recommendation:** Include magnets (always available, zero-effort) and a fold-out kickstand. These cover the two most likely placements: fridge door and countertop. Adhesive mounts can be included as an accessory.

### 3.4 Kitchen Environment Considerations

The display module lives in a kitchen:

- **Splashes:** The module needs at minimum IPX2 (drip-proof) rating. Seal the front lens to the housing with a silicone gasket. The RJ45 jack on the back is the vulnerability -- a rubber flap or recessed port with downward orientation helps.
- **Grease/steam:** The lens needs to be wipeable. Polycarbonate with an oleophobic coating, or tempered glass with anti-fingerprint treatment.
- **Cleaning:** Users will wipe with a damp cloth. No exposed PCB edges or unsealed seams.
- **Heat:** Kitchen countertop temperatures are benign (15-35C). Under-sink is similarly mild.

### 3.5 Displayed Information

Each display serves a different role:

**Display 1 (ESP32-S3 driven):** The "configuration" display. Since the ESP32-S3 handles WiFi/BLE configuration, this display likely shows:
- WiFi status and setup info
- System configuration (dose calibration, flavor names)
- Firmware update status
- Diagnostic/error codes

**Display 2 (RP2040 driven):** The "operational" display. The RP2040 receives UART commands from the main ESP32 about system state:
- Current flavor selection (color-coded)
- Bag fill levels (percentage bars or animated liquid levels)
- Pour count / volume dispensed today
- Cartridge health / replacement reminder
- Active pour animation

Both displays are 240x240 round, which works well for radial gauge-style UIs: circular progress bars, central icons, ring indicators.

---

## 4. Front Panel Layout

### 4.1 Zone Allocation

The front panel is 280mm wide (exterior) x 400mm tall (exterior). Interior face is 272mm wide x 392mm tall.

From the master spatial layout, the existing component positions on the front panel are:
- Display 1: X=40-80, Z=280-320 (left side, mid-height)
- Display 2: X=192-232, Z=280-320 (right side, mid-height)
- Hopper funnel: X=86-186, Z=322-392 (centered, top)
- Cartridge slot: X=61-211, Z=0-80 (centered, bottom)

The clearance analysis flagged that displays (Z=280-320) are only 2mm below the hopper (Z=322). The recommendation was to lower displays to Z=250-290 or raise the hopper to Z=330. This layout adopts **Z=250-290 for displays**.

### 4.2 Revised Front Panel Zones

| Zone | X Range (mm) | Z Range (mm) | Height | Purpose |
|------|-------------|-------------|--------|---------|
| Hopper access | 86-186 | 330-392 | 62mm | Funnel opening with flip-up lid |
| Display zone | 20-260 | 240-300 | 60mm | Two display docking points |
| Transition | 0-272 | 100-240 | 140mm | Blank panel (behind: bag slab) |
| Cartridge slot | 61-211 | 0-95 | 95mm | Cartridge opening + status LED ring |

### 4.3 ASCII Front Panel Diagram

```
             280mm (exterior width)
    ├──────────────────────────────────────┤

    ┌──────────────────────────────────────┐ ─── 400mm (top)
    │                                      │
    │         ┌──────────────────┐         │
    │         │  HOPPER ACCESS   │         │ Z=392
    │         │   flip-up lid    │         │
    │         │  100mm dia hole  │         │
    │         └──────────────────┘         │ Z=330
    │                                      │
    │   ┌────────┐          ┌────────┐     │ Z=300
    │   │ DISPLAY│          │ DISPLAY│     │
    │   │ DOCK 1 │          │ DOCK 2 │     │
    │   │  (D1)  │          │  (D2)  │     │
    │   │ 50mm   │          │ 50mm   │     │
    │   └────────┘          └────────┘     │ Z=250
    │     X:30-80            X:192-242     │
    │                                      │
    │   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │
    │     (blank panel -- bags behind)     │
    │                                      │
    │                                      │
    │                                      │
    │   ┌──────────────────────────────┐   │ Z=95
    │   │                              │   │
    │   │      CARTRIDGE SLOT          │   │
    │   │     150mm wide opening       │   │
    │   │                              │   │
    │   │    ○ status LED (amber/grn)  │   │ Z=40 (LED at side)
    │   │                              │   │
    │   └──────────────────────────────┘   │ Z=0
    └──────────────────────────────────────┘ ─── 0mm (bottom)

    Left side view (depth cross-section at display dock):

    FRONT PANEL (4mm)    SPOOL ZONE (25mm)    INTERIOR
    │                │                     │
    │  ┌──────────┐  │   ┌─────────────┐   │
    │  │ display  │  │   │ retractable │   │
    │  │ puck     │──┼───│ spool       │   │
    │  │ (12mm)   │  │   │ (55mm dia)  │   │
    │  └──────────┘  │   └─────────────┘   │
    │                │                     │
    ← Y=0           Y=4                  Y=29
```

### 4.4 Hopper Access Design

The user needs to pour syrup into the hopper funnel from the front/top. Options:

1. **Flip-up hinged lid:** A spring-loaded lid on the front panel that flips upward to expose the funnel opening. Hinge at the top edge of the hole. Pros: one-handed operation, stays open while pouring. Cons: hinge adds mechanical complexity, lid protrudes when open.

2. **Removable cap:** A silicone or plastic plug that pulls straight out. Pros: simple, no hinge. Cons: user needs to set it down somewhere, two-handed operation.

3. **Twist-lock cap:** Quarter-turn to unlock, pull to remove. Prevents accidental opening. Better for households with children.

**Recommendation:** Twist-lock cap for production. Removable silicone plug for prototype. The hopper funnel itself is already specified as removable for cleaning; the front panel cap is just the access point.

### 4.5 Cartridge Slot Design

The cartridge (150W x 130D x 80H mm) slides in from the front. The front panel opening needs:

- **Width:** 155mm (150mm cartridge + 5mm total clearance for guide rails)
- **Height:** 85mm (80mm cartridge + 5mm clearance for the lever mechanism above)
- **Guide rails:** Molded into the enclosure side walls at X=61 and X=211, running from Y=0 to Y=130
- **Visual indicator:** A single bicolor LED (green = locked and running, amber = unlocked or missing) mounted at the edge of the cartridge slot opening, driven from MCP23017 pins GPA4/GPA5 as already planned in the GPIO map
- **Door/flap:** Not recommended. The cartridge face itself acts as the "door" when fully inserted. When the cartridge is removed, the slot is open -- this is fine because the enclosure lives under a sink where appearance is not critical.

---

## 5. Display Docking Mechanism

### 5.1 Docked State (Retracted)

When the display is retracted, it sits in a shallow pocket on the front panel:

- **Pocket depth:** 6-8mm recessed into the front panel surface. The display puck is 12-15mm thick, so it protrudes 4-9mm from the panel. A fully flush mount would require a 12-15mm pocket, which eats into the spool zone depth. A semi-flush design (protruding 5mm) is the practical compromise.
- **Pocket shape:** Circular, 52mm diameter (50mm puck + 2mm clearance).
- **Retention:** Two small neodymium magnets (3mm dia x 2mm thick) embedded in the panel pocket, attracted to matching magnets in the display base. Pull force of ~0.5 N total -- enough to hold the display against the panel but easy to pull free by hand.
- **Alignment:** A small notch or D-flat on the pocket and puck prevents the display from rotating. This ensures the cable exit point always aligns with the panel cable hole.

### 5.2 Visual and Tactile Cue for Detaching

The user needs to discover that the displays can be pulled out:

- **Physical:** The 5mm protrusion means the puck has a graspable edge. A textured ring around the puck circumference invites fingers.
- **Software:** On first boot or when the display is newly docked, display a brief animation ("pull to detach" with a directional arrow).
- **Material contrast:** The display puck is a different material/color than the front panel. If the panel is matte grey, the puck is gloss black or white.

### 5.3 Extended State

When pulled out:

- Cable extends from the panel through the ball-and-socket strain relief.
- The pull-to-lock mechanism engages when the user stops pulling, keeping the cable at the desired length.
- Excess cable between the lock point and the spool stays wound inside.
- The cable hangs loosely from the display module to the panel. At full 1m extension, the display can reach a countertop above a typical 36-inch (914mm) counter from a base cabinet interior (~600mm below counter). The vertical distance is roughly 300-400mm, so 1m of cable is generous and allows horizontal placement as well.

### 5.4 Re-docking

User places the display puck back onto the front panel pocket:

1. Magnets pull the puck into alignment as it approaches within ~10mm.
2. The puck seats into the pocket.
3. User gives a short tug on the cable (or just pushes the display gently) to disengage the pull-to-lock mechanism.
4. The spool retracts the slack cable.
5. The display is docked.

This interaction takes 2-3 seconds and requires no precision from the user. The magnets do the alignment work.

---

## 6. Alternatives to Cat6

### 6.1 Comparison Matrix

| Option | Conductors | Retractable? | Durability | Connector | Cost | Verdict |
|--------|-----------|-------------|-----------|-----------|------|---------|
| **Cat6 UTP (flat)** | 8 | Yes (proven spools exist) | Good (rated for flex) | RJ45 (robust, latching) | Low ($2-4/cable) | **Baseline choice** |
| **Cat6 UTP (round)** | 8 | Yes (larger spool) | Good | RJ45 | Low | Spool too large |
| **USB-C** | 4-24 (complex) | Possible but fragile | Poor (connector wear is a known issue) | USB-C | Medium | Overkill; connector fragility is a dealbreaker for daily dock/undock |
| **FFC/FPC ribbon** | 4-40 | No (cannot spool; fold fatigue) | Poor (tears after ~1000 flex cycles) | ZIF connector | Very low | Not viable for retractable use |
| **Custom 4-pin cable** | 4 | Yes (thinner = smaller spool) | Good if using quality cable | Custom or JST-SM | Medium (tooling) | Viable; smaller spool but no standard connector |
| **Wireless (BLE)** | 0 | N/A | N/A | None | High ($5-8 BLE module + battery) | Eliminates tether but adds battery maintenance and latency |
| **Magnetic pogo pins** | 4-8 | N/A (dock only) | Good (no insertion wear) | Magnetic pogo | Medium | Great for docking but does not solve the tether |

### 6.2 Analysis of Top Contenders

**Flat cat6 UTP** is the best option for the retractable tether because:
- 8 conductors provide headroom (only 4-5 are needed for UART + power)
- RJ45 connectors are mechanically robust -- rated for thousands of insertion cycles
- The latching tab on RJ45 provides a positive connection that does not work loose from cable retraction tension
- Commercial retractable cat6 cables exist, proving the spool concept works
- Cable is cheap, commodity, and replaceable
- Flat form factor keeps spool diameter manageable

**Custom 4-pin cable** is the most interesting alternative. With only UART TX, UART RX, 5V, and GND needed, a 4-conductor cable (like a telephone handset cord) with JST-SM connectors would produce a spool roughly 35-40mm in diameter. However, the JST-SM connector lacks a latching mechanism suitable for the retraction tension. A custom magnetic breakaway connector (see below) could solve this, but adds design cost.

**Wireless (BLE):** Eliminating the cable entirely is appealing but introduces three problems:
1. The display module now needs a battery (LiPo, ~150-300mAh). Batteries in a kitchen appliance add safety certification complexity and charging circuitry.
2. BLE display updates add 20-50ms latency. For a pour animation that should feel responsive, this matters.
3. Two BLE connections (one per display) plus the main ESP32's WiFi all sharing the 2.4 GHz radio creates congestion. The ESP32-S3 could handle this, but the RP2040 has no wireless capability -- it would need an added BLE module.

**Wireless is a viable V2 upgrade path** if the display modules are designed with a battery compartment from the start. For V1, the tethered approach is simpler and cheaper.

### 6.3 Magnetic Pogo-Pin Dock Connector (Hybrid Approach)

Instead of an RJ45 jack on the display module, consider:

- The **docking pocket** on the front panel has spring-loaded pogo pins (4-8 pins in a circular pattern).
- The **display module base** has flat contact pads aligned with the pogo pins.
- **Magnets** hold the display against the pogo pins for reliable contact.

When docked, the display communicates and receives power through the pogo pins -- no cable involved. When pulled away, the pogo pins disconnect cleanly (magnetic breakaway) and the retractable cat6 cable takes over for communication and power.

This hybrid means:
- The RJ45 jack and plug are fully enclosed within the enclosure (spool to panel-mounted RJ45 to pogo pin PCB). No external RJ45 connectors exposed to kitchen splashes.
- The display module has no exposed port -- just flat contact pads recessed into the base. Much better for kitchen environment sealing.
- The cable is only exposed when the display is pulled out, and the display-end terminates at the pogo pad PCB behind the docking pocket, not at the display itself.

**Wait -- this breaks the retractable cable concept.** If the cable terminates at the panel, not the display, then pulling the display out disconnects it. The cable needs to reach the display.

**Revised hybrid:** The retractable cable connects the enclosure to the display module. The display-end connector could be:
- A small magnetic pogo connector (4-pin) on the bottom of the display puck. When docked, the pogo pins on the panel provide a secondary power path. When undocked, the retractable cable (terminating in a small magnetic pogo plug) stays connected to the display.
- The magnetic breakaway at the display end means if the cable snags, it disconnects cleanly rather than pulling the display off a surface.

This is a nice UX refinement but adds connector design cost. **Flag for V2.** For V1, a recessed RJ45 with a rubber flap is sufficient.

---

## 7. Power Budget Per Display

### 7.1 Component Power Draw

| Component | Current (mA) | Voltage | Power (mW) |
|-----------|-------------|---------|-----------|
| GC9A01 TFT backlight | 20-40 | 3.3V | 66-132 |
| GC9A01 driver IC | 5-10 | 3.3V | 17-33 |
| RP2040 (Display 2) | 25-50 | 3.3V | 83-165 |
| ESP32-S3 (Display 1) | 40-100 | 3.3V | 132-330 |
| Passive components | ~5 | 3.3V | ~17 |
| **Total per display (RP2040)** | **~55-105** | **3.3V** | **~180-350** |
| **Total per display (ESP32-S3)** | **~70-155** | **3.3V** | **~230-660** |

**Worst case:** The ESP32-S3 display draws ~155mA at 3.3V (with WiFi active). The RP2040 display draws ~105mA at 3.3V.

### 7.2 Voltage Drop Over 1m of Cat6

Cat6 conductors are typically 23-24 AWG solid copper. At 24 AWG:

```
Resistance per meter: ~84 milliohms (24 AWG copper at 20C)
Two conductors for VCC (pins 4+5), two for GND (pins 7+8):
  Each path: 84 mohm per conductor, two in parallel = 42 mohm per path
  Total loop resistance: 42 + 42 = 84 mohm

Voltage drop at 155mA: 0.084 ohm * 0.155A = 0.013V

Voltage drop at 105mA: 0.084 ohm * 0.105A = 0.009V
```

At these currents, voltage drop over 1m is negligible -- about 13mV worst case with doubled conductors. Even with a single conductor pair:

```
Single conductor per rail: 84 mohm each
Total loop: 168 mohm
Drop at 155mA: 0.168 * 0.155 = 0.026V (26mV)
```

Still negligible.

### 7.3 3.3V vs. 5V Delivery

**3.3V direct delivery** is actually viable given the tiny voltage drops calculated above. However, 5V with a local LDO is still recommended because:

1. The ESP32-S3 and RP2040 both accept 5V on their USB/VIN pins and have onboard regulators. Sending 3.3V requires bypassing the onboard regulator and feeding the 3.3V rail directly, which is less robust.
2. A 5V rail provides headroom for future additions to the display module (brighter backlight, buzzer, ambient light sensor).
3. The main enclosure PSU already provides both 5V and 12V rails. Tapping 5V is trivial.

**Recommendation:** Send 5V over the cat6 cable. Use the RP2040/ESP32-S3 module's onboard regulator to step down to 3.3V locally. Total power delivery per cable: ~0.8W worst case (155mA x 5V). This is well within cat6 conductor ratings.

---

## 8. Prior Art and Reference Products

### 8.1 Detachable Tethered Displays

Products with a display that detaches from a base unit on a cable are rare in the consumer space, which makes this a genuine differentiator. The closest examples:

**Wireless meat thermometers (e.g., ThermoWorks Signals, Meater Block):** These have a base station that stays near the grill and a separate display/receiver that the user carries or places on a countertop. The connection is wireless (RF or BLE), not tethered. The user experience of "leave the base unit in an awkward spot, carry the display to where you can see it" is exactly the UX model for this product.

**Baby monitors (e.g., Infant Optics DXR-8, Eufy SpaceView):** Camera unit stays in the nursery; parent unit is a portable display. Connected wirelessly. Same concept: sensor/actuator in an inaccessible location, display wherever the user is.

**Smart home hubs (e.g., old-gen Wink Hub with detachable tablet, Brilliant switch panels):** Some early smart home products had detachable or repositionable displays. The Brilliant smart switch has a fixed display but the concept of a control surface on a wall or counter is relevant.

**Retractable conference phones (e.g., Polycom satellite microphones):** Conference phones with satellite microphone pods on retractable cables. The pods detach and retract back to the base. The retractable cable UX (pull out, place on table, retract when done) is directly applicable.

### 8.2 Retractable Cable Products

**Retractable badge reels:** The most common consumer reference for pull-to-lock retractable cables. Users intuitively understand the pull/tug/retract interaction from badge reels. This familiarity is a UX advantage.

**Retractable USB/ethernet cables for travel:** Monoprice and others sell retractable cat5e/cat6 cables in compact spools for laptop bags. These prove the spool mechanism works for ethernet cable. The spool diameter is typically 65-75mm for 1m of cable.

**Retractable vacuum cleaner cords:** Larger scale (5-10m of heavy cable) but the constant-force spring mechanism is identical to what is needed here, just miniaturized.

### 8.3 UX Lessons from Prior Art

1. **Make detachment obvious.** Baby monitors ship with the parent unit already detached. If the display always starts docked, some users may never discover it detaches. The first-boot setup should instruct the user to pull the display out.
2. **Retraction force must be gentle.** Badge reels that snap back aggressively are universally hated. The spring tension should allow the cable to retract under its own pull but not yank the display out of the user's hand.
3. **Wireless is the V2 play.** Every tethered product category (baby monitors, thermometers, game controllers) eventually went wireless. Design the display module with a battery compartment and BLE antenna pad even if V1 does not populate them.
4. **The cable should be a feature, not a compromise.** If the cable is visible (e.g., display on the countertop with cable running down to under the sink), it needs to look intentional -- a braided fabric-jacketed flat cable reads as premium; a bare white cat6 cable reads as jury-rigged.

---

## 9. Open Questions and Risks

### 9.1 Dealbreaker Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Spool mechanism too large to fit behind front panel | Medium | Flat cat6 reduces spool to ~55mm dia. Two spools fit in the 272mm width with room to spare. Depth of 22-25mm is within the Y=0-30mm front zone. **Not a dealbreaker.** |
| Cat6 too stiff for smooth retraction | Medium | Flat cat6 is more flexible than round. Test with commercial retractable cat6 product to validate. Spring force may need tuning. **Needs physical prototype.** |
| RJ45 connector too bulky for 50mm display puck | Low | A slimline RJ45 jack (low-profile, 13mm wide x 11mm tall) fits within the 50mm puck footprint. The jack can be mounted on the bottom edge with the cable exiting downward. **Manageable.** |
| User never discovers the display detaches | Medium | Software prompt on first boot. Physical design cues (textured grab ring, contrasting material). Include in product quick-start guide. **Solvable.** |
| Cable routing from under-sink to countertop looks messy | Low-Medium | Offer cable management accessories (adhesive cable clips). Use fabric-jacketed flat cable for a finished look. Cable is only ~4mm thick when flat. **Acceptable.** |
| Moisture ingress at RJ45 connector in kitchen | Medium | Recessed jack with downward orientation. Rubber port flap when undocked. When docked, the panel pocket seals around the puck. **Needs validation.** |

### 9.2 Prototype Milestones

1. **Spool proof-of-concept:** Acquire a commercial retractable cat6 cable (travel type). Measure spool dimensions. Test retraction smoothness and force. Determine if the internal mechanism can be re-housed in a custom enclosure behind the front panel.
2. **UART over cat6 validation:** Wire a 1m cat6 patch cable between an ESP32 and RP2040. Run UART at 115200 and 921600 baud. Verify zero bit errors over 1 million characters. Test with solenoid valves firing nearby.
3. **Display puck mockup:** 3D print a 50mm x 15mm puck. Embed magnets. Test docking feel on a flat panel with matching magnets. Evaluate pull-away force, re-docking alignment, and retention strength.
4. **Front panel mockup:** Laser-cut or 3D print the front panel with hopper hole, two display pockets, and cartridge slot. Validate ergonomics: can a user pour syrup into the hopper, pull a display out, and slide a cartridge in without conflict?

---

## 10. Summary and Recommendations

**The retractable cat6 display concept is viable.** No dealbreakers were identified. The hardest part is the spool mechanism, and commercial retractable cat6 products prove it works at the required scale.

Key decisions:

| Decision | Recommendation | Confidence |
|----------|---------------|-----------|
| Cable type | Flat cat6 UTP | High |
| Communication protocol | UART (already in firmware) | High |
| Power delivery | 5V over cat6, local LDO to 3.3V | High |
| Spool mechanism | Constant-force spring, pull-to-lock | Medium (needs prototype) |
| Display size | 1.28" GC9A01 round TFT (upgradeable to 1.69") | Medium |
| Puck diameter | 50mm | Medium |
| Docking retention | Neodymium magnets | High |
| Connector type | RJ45 (recessed, rubber-flapped) | Medium |
| Wireless option | Design for V2 (reserve battery compartment) | High |
| Cable jacket | Fabric-braided flat cable for premium feel | Medium |

The display tether system uses only 4 of the 8 cat6 conductors for V1 (TX, RX, 5V, GND). The remaining 4 conductors are available for future use: additional data channels, dedicated backlight PWM, I2C for an ambient light sensor on the display, or a hardware interrupt line from a touch sensor on the puck.
