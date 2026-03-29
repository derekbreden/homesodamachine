# Pump Mounting Research

## 1. Mounting Dimensions and Screw Pattern

### Official Datasheet Dimensions (KPHM400 Data Sheet, Kamoer)

The Kamoer KPHM400 straight bracket mounting pattern is defined as follows:

- **Mounting hole pattern:** 4x holes in a square, 50.0mm +/-0.1mm center-to-center on each side
- **Hole diameter:** 4mm (M4 clearance holes)
- **Motor bore circle:** diameter 56mm (the circle cleared by the motor cylinder at the bracket face)
- **Motor cylinder diameter:** 36mm (brushed variant, which is the SW3B25 model used in this project)

### Pump Head Envelope (Straight Bracket)

| Dimension | Value | Notes |
|-----------|-------|-------|
| Front face width | 68.6mm | Bracket face, wider than pump head |
| Pump head width | 62.5mm | The black housing body |
| Pump head height | 62.7mm | Nearly square cross-section |
| Pump head depth (brushed) | 54mm | From front face to bracket face |
| Bracket thickness | ~13mm | Bracket + adapter plate zone |
| Motor length behind bracket | 40.6mm | Motor cylinder body |
| Motor + bracket gap | 8mm | Between bracket and motor body proper |
| Total depth (brushed) | ~115.6mm | Front face to motor end cap |
| Motor shaft nub | ~5mm | Protrudes beyond motor end cap (caliper-verified at 5.05mm) |

### Datasheet vs. Caliper Cross-Reference

The caliper-verified geometry document reports 48mm x 48mm hole spacing with M3 (3.13mm) holes. The official datasheet shows 50mm x 50mm with 4mm holes. The discrepancy is significant:

- **Caliper photo 05** measured 47.88mm edge-to-edge across one pair of holes. If holes are 4mm diameter (per datasheet), center-to-center = 47.88 + 4.0 = 51.88mm -- still not matching 50mm exactly.
- Most likely explanation: the caliper measurement caught the inner edges of holes that are slightly larger than nominal, or the photo was measuring a different feature on the bracket. **The datasheet 50mm +/-0.1mm value should be treated as authoritative for the mounting plate design.**
- **For the cartridge design, use 50mm c-c spacing with 4.2mm through-holes** (M4 + 0.2mm clearance per FDM tolerance guidelines).

### Mounting Approach for the Cartridge

The pump mounts with its bracket face against a flat surface (the cartridge's internal mounting plate). The mounting plate needs:

1. A central bore hole of at least 37mm diameter (36mm motor + clearance) for the motor cylinder to pass through
2. Four M4 screw holes at 50mm x 50mm square, centered on the bore
3. The pump head protrudes ~54mm forward from the mounting plate
4. The motor protrudes ~49mm rearward (40.6mm body + 8mm gap region), plus 5mm shaft nub = ~54mm total rearward

### Screw Specification

M4 x 10mm or M4 x 12mm socket head cap screws (stainless steel). The screws pass through the mounting plate and thread into the pump's bracket. Bracket thickness is ~1.5-2mm metal, so threads engage the pump head body. Recommended: M4 x 10mm with lock washers or thread-locking adhesive given vibration environment.


## 2. Vibration Characteristics

### Sources of Vibration

The Kamoer KPHM400 generates vibration from two sources:

1. **Motor rotation:** The brushed DC motor at ~280 RPM (full speed, per datasheet test conditions) produces rotational imbalance vibration at the motor frequency = 280/60 = ~4.7 Hz.

2. **Roller pulsation:** The 3-roller peristaltic mechanism creates flow pulsation (and corresponding mechanical pulsation) at 3x the rotation frequency. Pulsation frequency = 3 x 280 / 60 = **14 Hz** at full speed. This is the dominant vibration frequency. Each time a roller occludes and then releases the tubing, there is a discrete mechanical impulse.

### Vibration Amplitude

Kamoer does not publish vibration amplitude data for this pump. However, for small peristaltic pumps in this class (500g, 7-8W):

- Vibration amplitude is low -- these are not industrial pumps with large masses
- The pump weighs ~504g; at 14 Hz the forces are modest
- The 3-roller design inherently produces lower pulsation amplitude than 2-roller designs (more frequent, smaller pulses)
- The primary concern is transmitted vibration causing audible buzz/rattle against the cartridge or enclosure walls, not structural fatigue

### Vibration Isolation Strategy

**Recommendation: Compliant mounting, not rigid.**

The cartridge mounting plate should include vibration isolation between the pump and the cartridge shell. Options in order of preference:

1. **Rubber grommets at each mounting screw (recommended):** Use M4 rubber grommet isolators (barrel type) at each of the 4 mounting points. The screw passes through a rubber bushing that decouples the pump from the plate. This is the standard approach for small motor/pump isolation in consumer appliances.
   - Typical M4 grommet: 10mm OD barrel, 4.2mm ID, 8-10mm long, 40-60 Shore A durometer
   - Available from Amazon in multi-packs for under $10
   - The rubber absorbs vibration across a broad frequency range including the 14 Hz pulsation fundamental

2. **Elastomeric pad between bracket and plate:** A 1-2mm silicone or EPDM pad cut to match the bracket face. Simpler but less effective than grommets because the screw still creates a rigid path.

3. **3D-printed TPU isolator ring:** Print a TPU adapter ring that sits between the pump bracket and the mounting plate, with the four screw holes passing through TPU bushings. The Bambu H2C supports TPU printing.

**The cartridge shell walls should not contact the pump head or motor directly.** Maintain at least 2mm clearance between the pump body and any cartridge wall to prevent contact-transmitted vibration.


## 3. Tubing: Pump to John Guest Quick-Connect Transition

### The Problem

The Kamoer pump uses BPT tubing (4.8mm ID x 8.0mm OD) with barbed connectors on the pump head. The rest of the system uses 1/4" OD (6.35mm) hard tubing with John Guest push-to-connect fittings. The cartridge must transition between these two tubing systems within its interior.

### Transition Approach

The pump's barbed connectors have short BPT tube stubs (~30-50mm) protruding from the pump head front face. The transition path inside the cartridge is:

```
Pump barb → BPT tube stub → Barb-to-barb reducer → Short silicone adapter tube → John Guest union fitting
```

However, this introduces multiple failure points. A simpler approach:

**Recommended: Direct BPT tube into John Guest fitting.**

John Guest push-to-connect fittings grip tubes by their outer diameter. The BPT tube OD is 8.0mm. John Guest makes fittings for metric sizes including 8mm OD tube (their metric range). However, the cartridge design specifies 1/4" (6.35mm) John Guest unions (PP0408W), which accept 1/4" OD tube only.

**Best approach: Use a short piece of 1/4" OD semi-rigid tube as an adapter stub.**

1. The BPT tube stub from the pump barb terminates inside the cartridge
2. A barb-to-barb reducer (8mm to 6mm barb, brass or polypropylene) connects the BPT tube to a short (~30-40mm) piece of 1/4" OD semi-rigid polyethylene tube
3. That 1/4" OD tube stub inserts into the internal port of the John Guest PP0408W union
4. The external port of the John Guest union receives the 1/4" OD tube stub from the enclosure dock

**Alternative (simpler, fewer parts): Use 1/4" OD silicone tubing directly on the pump barbs.**

The pump barbs are designed for 4.8mm ID tubing. 1/4" OD polyethylene tube has ~4.3mm ID (wall ~1mm), which is too small for the barb. However, 1/4" OD silicone tubing has thinner walls and can stretch over a barb. This needs physical testing -- if the barb OD is close to 4.8mm (matching the BPT ID), standard 1/4" OD silicone with ~4mm ID would be too tight.

**Practical recommendation:** Keep the BPT tube stubs as Kamoer ships them. Use brass barb reducers (8mm barb to 1/4" barb, widely available on Amazon) to transition to a short 1/4" OD PE tube segment, which then inserts into the John Guest union. Total transition length: ~50-60mm.


## 4. Minimum Tube Bend Radius

### BPT Tubing (4.8mm ID x 8.0mm OD)

PharMed BPT tubing is relatively stiff compared to silicone. Minimum bend radius for BPT tubing in this size range:

- **Minimum bend radius: ~25-30mm** (approximately 3x the OD)
- Below this radius the tube kinks, reducing or blocking flow
- The tubing routing inside the cartridge from pump barb to the rear-wall John Guest fitting must respect this minimum

### Silicone Tubing (5mm ID x 8.2mm OD, alternate pump tube option)

- **Minimum bend radius: ~20mm** (FDA-rated silicone tubing spec sheets for this size)
- More flexible than BPT, easier to route in tight spaces
- However, shorter pump tube life than BPT

### 1/4" OD Semi-Rigid Polyethylene Tube

- **Minimum bend radius: ~25mm** (John Guest specification for their PE tube)
- Used for the short adapter stub between barb reducer and JG fitting, so bending is not typically needed for this segment

### Design Implication

The cartridge interior must provide at least 25mm of clearance between the pump barb exits (front face of pump) and any 90-degree direction change. With BPT stubs protruding ~30-50mm from the pump face, the tube can make a gradual curve from its forward-pointing exit to a rearward or sideward path toward the John Guest fittings at the rear wall. The total routing space from pump face to cartridge rear wall should be at least 80mm to allow a comfortable bend.


## 5. Electrical Connections

### Motor Wiring (Per Pump)

The brushless DC motor variant (which is the SW3B25 model with 5 wires) has:

| Wire | Color | Function |
|------|-------|----------|
| 1 | Yellow | FG - speed feedback (1 pulse/revolution) |
| 2 | Red | Vcc - positive power supply |
| 3 | White | SP - speed control (PWM 10-30kHz or 0-5V analog) |
| 4 | Black | GND - negative power supply |
| 5 | Green | F/R - forward/reverse (floating = reverse, connect to GND = forward) |

**However:** The project uses the brushed DC motor variant (SW3B25 with "SW" = brushed, 12V, 0.7A). The brushed motor is simpler -- only 2 wires (power + and -), with direction controlled by polarity reversal. The L298N H-bridge motor driver handles speed (PWM) and direction.

**For the brushed motor variant, only 2 electrical connections per pump are needed: motor + and motor -.** Two pumps = 4 total conductors.

### Disconnect Strategy for Replaceable Cartridge

The electrical connection must disconnect cleanly when the cartridge is removed and reconnect reliably when inserted. Options:

#### Option A: Spring-Loaded Pogo Pins (Recommended)

Mount 4 spring-loaded pogo pins (2 per pump) on the enclosure dock, aligned to contact 4 flat copper pads on the rear face of the cartridge. When the cartridge slides into the dock, the pogo pins make contact automatically.

**Advantages:**
- Blind-mate capable -- no alignment precision needed beyond the rail guides
- Self-cleaning contacts (spring-loaded wipe action)
- No user action required beyond sliding cartridge in
- Available as pre-made 4-pin pogo assemblies on Amazon ($5-10)

**Specifications needed:**
- Current rating: 0.7A per pump at 12V = 8.4W. Standard pogo pins rated for 1-2A are sufficient.
- Spring force: 50-100g per pin is standard, providing reliable contact
- Pin travel: 1-2mm, easily accommodated
- Contact pad size on cartridge: 3-4mm diameter copper pads, spaced 2.54mm apart (standard pitch)

**Implementation:** The pogo pin header mounts to the enclosure rear wall of the dock bay. The cartridge rear face has 4 exposed copper pads (small PCB or copper tape). When the cartridge is fully seated on its rails, the pogo pins compress against the pads. The rail guides ensure lateral alignment to within ~1mm, which is sufficient for 3-4mm contact pads.

#### Option B: Magnetic Pogo Pin Connector

Same as Option A but with integrated magnets for self-alignment and retention. Available as 2-pin or 4-pin magnetic pogo connectors.

**Advantages over plain pogo:** Magnetic self-alignment, tactile "click" when connected.
**Disadvantages:** More expensive, magnets may interfere with motor operation if too close, adds a pull-apart force that must not exceed the rail retention force.

#### Option C: Blade Contacts / Wiper Contacts

Flat spring-steel blade contacts on the dock that wipe against flat copper traces on the cartridge. Similar to how a battery compartment works.

**Advantages:** Very simple, no special parts.
**Disadvantages:** Less reliable contact than pogo pins, wear over time, require more precise alignment.

#### Option D: Small Detachable Connector

A standard 4-pin JST or Molex connector with one half permanently wired to the cartridge and the other to the enclosure. The user manually disconnects/reconnects.

**Disadvantages:** Requires user to handle a small connector -- violates the "black box" UX principle. Not blind-mate.

**Recommendation: Option A (pogo pins) is the best fit.** It achieves blind-mate connection, requires no user awareness of electrical connections, and is inexpensive. The pogo pins mount to the enclosure (permanent side), and the cartridge just needs 4 flat contact pads.


## 6. Pump Orientation and Layout

### Constraints

- Cartridge width is constrained by the enclosure width (220mm outer, minus wall thickness ~4mm per side = ~212mm interior)
- Cartridge sits at the front-bottom of the enclosure (per vision.md)
- Each pump is 68.6mm wide (at bracket) x 62.7mm tall x ~116mm deep (plus tube stubs)
- Two pumps must fit side by side or stacked
- 4 John Guest fittings on the rear face (2 inlet, 2 outlet -- one pair per pump)
- User accesses cartridge from the front

### Orientation Options

#### Option 1: Side by Side, Motors Rearward (Recommended)

Both pumps mounted with their motor axis parallel to the depth (Y) axis of the enclosure. Pump heads face forward, motors face rearward. Pumps are side by side along the X axis.

```
TOP VIEW (looking down into cartridge):

        ◄──────── ~160mm ────────►
  ┌──────────────────────────────────────┐
  │  ┌─────────┐    ┌─────────┐         │  ▲
  │  │ Pump 1  │    │ Pump 2  │         │  │
  │  │ Head    │    │ Head    │   JG    │  ~120mm
  │  │  ○Motor │    │  ○Motor │  fittings  │
  │  └─────────┘    └─────────┘    ○○○○ │  ▼
  └──────────────────────────────────────┘
  ◄── FRONT (user side)          REAR ──►
```

**Width calculation:**
- Each pump: 68.6mm (bracket width)
- Gap between pumps: 10-15mm (for tubing routing + vibration isolation)
- Total width: 68.6 + 15 + 68.6 = ~152mm
- Leaves ~30mm on each side for cartridge walls, rail guides, and tubing routing to rear JG fittings

**Depth calculation:**
- Tube stubs in front: ~40mm
- Pump head: ~54mm
- Bracket + motor: ~62mm (including shaft nub clearance)
- Total pump depth: ~156mm
- Add rear wall with JG fittings: ~42mm (fitting length with shoulders)
- Total cartridge depth: ~200mm
- This exceeds the 300mm enclosure depth budget, but the cartridge doesn't use the full depth -- valves sit behind it

**Height:**
- Pump height: 62.7mm
- Mounting plate + grommets: ~5mm below, ~5mm above
- Cartridge shell: ~2mm top, ~2mm bottom
- Total height: ~77mm

**Advantages:**
- Most space-efficient width configuration
- Motors at rear means heat dissipates away from user
- Tube stubs at front are accessible for inspection/replacement
- Gravity-neutral orientation (rollers compress vertically, no gravitational bias on flow)
- JG fittings on rear face align naturally with the enclosure dock tube stubs

**Disadvantages:**
- None significant

#### Option 2: Side by Side, Pumps Rotated 90 Degrees

Pump heads face upward, motors face downward (or vice versa). This reduces depth but increases height.

**Not recommended:** Makes height ~116mm which is excessive for the bottom-front position.

#### Option 3: Stacked (One Above the Other)

**Not recommended:** Total height would be ~140mm+ (two pump heights plus spacing). The cartridge sits below the displays and above the bottom of the enclosure. 140mm is likely too tall for this zone.

### Recommended Layout: Side by Side, Motors Rearward

This is the most natural orientation. The two pumps sit next to each other on a shared mounting plate, which is suspended inside the cartridge shell via the vibration-isolated screw mounts. The BPT tube stubs curve from the pump face rearward and downward (or upward) to reach the John Guest fittings on the cartridge rear wall. The pogo pin contact pads are also on the rear face, below (or beside) the JG fittings.

### Mounting Plate Design

A single flat plate with two sets of 4x M4 holes (50mm square pattern each), two motor bore holes (37mm diameter each), spaced to position the pumps side by side with 10-15mm gap. The plate itself mounts to the cartridge shell via standoffs or integral snap features, with rubber grommets isolating the pump screws from the plate.

Total mounting plate dimensions: approximately 160mm x 62mm (width x height of plate face, perpendicular to motor axes).
