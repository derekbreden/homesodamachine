# Electrical Mating Approaches for Pump Cartridge Dock

Research document covering connector technologies for a replaceable slide-in pump cartridge. The cartridge needs exactly 3 electrical contacts (ground, motor A 12V, motor B 12V) that mate reliably during insertion into a dock mounted under a kitchen sink.

**Application constraints:**
- 3 contacts only, 12V DC
- Peristaltic pump motors: ~0.3A typical, ~3A max draw, brief stall currents possibly higher
- Moisture-adjacent environment (4 John Guest push-to-connect water fittings on same mating face)
- 3D printed housing for both cartridge and dock
- Straight slide-in insertion, ~100-200mm travel
- Contacts should mate during the last portion of insertion
- Prototype/hobby scale sourcing

---

## 1. Pogo Pins / Spring-Loaded Contacts

### How They Work

A pogo pin (spring-loaded contact) consists of a plunger, a spring, and a barrel. The plunger is pushed inward against the spring when the connector mates, maintaining constant pressure against a flat target pad. The spring provides consistent contact force regardless of minor dimensional variations, making them extremely tolerant of alignment imperfection.

In the typical configuration for this application, the dock side holds the spring-loaded pins (soldered to a PCB or press-fit into a 3D printed housing), and the cartridge side has flat conductive pads (bare copper PCB pads, brass plates, or nickel-plated steel).

### Key Specifications

| Parameter | Typical Range |
|---|---|
| Travel (stroke) | 0.5mm - 3.0mm (rated at mid-stroke) |
| Spring force | 25g - 120g at working travel (model dependent) |
| Contact resistance | < 50 milliohms |
| Current rating (standard) | 2A - 9A per pin |
| Current rating (high-current) | 10A - 30A per pin |
| Cycle life | 100,000 - 1,000,000 insertions |
| Typical diameter | 0.5mm - 4.0mm (larger = higher current) |

Mill-Max is the gold standard for spring-loaded pins. Their catalog includes:
- Standard pins: 2A-9A, various stroke lengths
- High-current pins: up to 13A max (10.4A derated), available in through-hole solder cup
- All ratings specified at mid-stroke compression with 30C temperature rise

### Alignment Tolerance

Pogo pins are very forgiving of misalignment. Because they press vertically against a flat pad, lateral misalignment of 1-2mm is easily tolerated as long as the plunger still contacts some portion of the pad. Making the target pad larger than the pin tip (e.g., 5mm pad for a 2mm pin) provides generous tolerance -- well suited for 3D printed housings with their inherent dimensional variation.

### Self-Cleaning Wipe Action

When a cartridge slides in and the pogo pin first contacts the pad, the continued lateral motion of the cartridge creates a wiping action across the pad surface. This scrapes away oxide films, dust, and light corrosion. For a slide-in cartridge design, this wipe happens naturally -- the pin "drags" across the pad during the last few millimeters of insertion. This is one of the strongest advantages of pogo pins in this application.

### Sourcing at Hobby Scale

**Mill-Max (premium, US-made):**
- Available from DigiKey, Mouser, Newark
- Individual pins $1-5 each depending on model
- Part numbers: 0852 series (9A), 0906 series, 0965 series
- Pre-made connector blocks also available

**Adafruit / SparkFun:**
- Various pogo pin breakout boards and individual pins
- Typically lower current (1-2A), but convenient form factors
- Adafruit sells pogo pins in packs of 10 for ~$8

**Amazon / AliExpress:**
- Generic P75 and P100 series test probes -- very cheap ($5-10 for 100 pieces)
- P75-B1 (pointed tip) or P75-E2 (flat tip) common choices
- Rated 1-3A typically, adequate for this application at 0.3A normal draw
- Quality varies, but at these volumes they're disposable
- Larger diameter pins (2-3mm) available for higher current from Chinese manufacturers

**Chinese manufacturers (Johoty, Promax, Rtench):**
- Custom high-current pogo pins, 5A-30A range
- MOQ varies, some do small batches
- Solder cup termination available

### Advantages

- Excellent alignment tolerance -- ideal for 3D printed housings
- Natural wipe action during slide-in insertion
- Constant spring pressure maintains reliable contact
- Very high cycle life (100K+ insertions far exceeds cartridge replacement frequency)
- Simple target pad on cartridge side (just a flat conductive surface)
- Wide current range available; even cheap P75 probes handle 1-3A

### Disadvantages

- Higher cost per contact than blade/tab connectors
- Spring fatigue possible over very long periods, though rated life far exceeds this application's needs
- Exposed spring mechanism can trap moisture if not sealed
- Vertical press direction means contact force is perpendicular to mating face -- fine for slide-in with mechanical stop

---

## 2. Blade / Tab Connectors (FASTON-Style)

### How They Work

A flat metal blade (tab) on one side slides into a spring-clip receptacle on the other side. The receptacle's internal spring fingers grip the blade, creating a gas-tight contact. This is the same technology used in automotive wiring, appliance connections, and household electronics.

The FASTON connector family (TE Connectivity) is the industry standard, with the ".250" designation referring to the 0.250-inch (6.35mm) blade width.

### Key Specifications

| Parameter | FASTON .250 | FASTON .187 | Automotive (MX150) |
|---|---|---|---|
| Tab width | 6.35mm (0.250") | 4.75mm (0.187") | Various |
| Tab thickness | 0.8mm (0.032") | 0.5mm (0.020") | Various |
| Current rating | 7A continuous | 5A continuous | Up to 22A |
| Voltage rating | 250V typical | 250V typical | 60V |
| Cycle life | 500+ insertions | 500+ insertions | Thousands |
| Contact resistance | < 5 milliohms | < 5 milliohms | Low |

### Self-Wiping Action

Blade connectors inherently provide self-wiping action. As the blade slides into the receptacle, the spring fingers scrape along both surfaces of the blade, removing oxide layers and contaminants. TE Connectivity's AMPLIVAR serrations on some FASTON models enhance this effect with textured contact surfaces that are particularly aggressive at breaking through oxide films.

### Slide-In Mating Compatibility

Blade connectors can absolutely mate as part of a slide-in motion, but the insertion axis must be aligned with the blade direction. For a cartridge that slides horizontally into a dock:
- Blades on the cartridge aligned parallel to the insertion direction
- Receptacles in the dock, open end facing the insertion path
- The blade naturally slides into the receptacle during the last portion of insertion

This is mechanically straightforward. The challenge is alignment precision -- the blade must enter the receptacle opening, which requires tighter lateral tolerance than pogo pins. A tapered lead-in (funnel shape) on the receptacle or in the 3D printed housing helps, but you're still talking about +/- 1mm tolerance at best without guide features.

### Sourcing

- TE Connectivity FASTON terminals: widely available from DigiKey, Mouser, Amazon
- Extremely cheap: $0.05-0.20 per terminal
- Available in bare, insulated, and PCB-mount versions
- Tab terminals can be soldered to wire or crimped
- Also available as PCB-mount right-angle headers

### Advantages

- Extremely cheap and widely available
- Excellent self-wiping action
- High current capacity relative to size
- Very low contact resistance (gas-tight joint)
- Well-proven in automotive/appliance environments
- Can handle vibration well due to positive spring grip

### Disadvantages

- Requires tighter alignment than pogo pins (~1mm vs ~2-3mm)
- Higher insertion force than pogo pins (spring grip is firm)
- Less tolerant of angular misalignment
- Receptacle is an enclosed pocket that can trap moisture
- 500-cycle rated life is lower than pogo pins (though still adequate -- a cartridge replaced weekly = 10 years)
- Tab must be oriented correctly (can't mate at an angle)

---

## 3. Edge Connectors (PCB-Based)

### How They Work

A PCB with gold-plated edge contacts (gold fingers) slides into a card-edge socket. This is how PCIe cards, RAM modules, ISA cards, and similar expansion cards connect. The socket contains spring-loaded contacts on both sides that grip the PCB edge.

For this application: a small PCB mounted to the cartridge edge, with 3 gold finger traces, mating into a card-edge socket mounted in the dock.

### Key Specifications

| Parameter | Value |
|---|---|
| Contact pitch | 0.050" - 0.200" (1.27mm - 5.08mm) |
| Current per contact (standard) | 1A typical for signal-grade |
| Current per contact (power) | 3A for industrial grade |
| Current per contact (high-power) | Up to 43A (TE Multi-Beam power edge) |
| PCB gold thickness | 30 microinches minimum (hard gold, ENIG not sufficient) |
| Cycle life | 500 - 10,000 insertions depending on socket quality |
| Contact resistance | 10-30 milliohms |

### Current Limitations

Standard card-edge connectors are designed for signal-level currents (1A per contact). The gold finger traces on the PCB are typically thin copper (1oz or 2oz, 35-70 microns) with limited cross-section. For 3A, you'd need:
- Wide traces (5mm+ per contact)
- Heavy copper PCB (2oz minimum)
- Power-rated card-edge socket (not a standard PCIe/ISA socket)

TE Connectivity makes dedicated power card-edge connectors rated at 43A per terminal, but these are industrial components with different form factors than standard card-edge sockets.

### Practicality at Prototype Scale

**PCB side (cartridge):**
- PCBWay, JLCPCB, and others offer gold finger PCBs
- Must specify hard gold plating (not ENIG) -- adds cost
- A simple 3-contact gold finger PCB would cost ~$5-15 for 5 pieces
- Beveled edge recommended for smooth insertion

**Socket side (dock):**
- Standard card-edge sockets from DigiKey/Mouser
- A 6-position edge socket (using 3 of 6 contacts) would cost $1-3
- Must match PCB thickness (typically 1.6mm)

### Self-Wiping Action

Card-edge connectors provide excellent wipe action -- the entire length of the gold finger is wiped by the socket contacts during insertion. This is one reason they're reliable in computing applications despite infrequent mating.

### Advantages

- Excellent self-wiping action
- Proven technology with high reliability
- Cartridge-side contact is just a PCB edge -- very flat, easy to integrate
- Good alignment tolerance along the insertion axis (socket guides the PCB)

### Disadvantages

- Standard contacts limited to 1-3A (adequate for this application, but no margin)
- Requires gold-plated PCB (adds cost and lead time vs. simpler options)
- PCB thickness must match socket precisely (1.6mm standard)
- Socket is enclosed and can trap moisture
- More complex integration into 3D printed housing than pogo pins or blade connectors
- PCB edge is fragile if cartridge is 3D printed around it -- mounting matters
- Overkill for 3 contacts (these systems are designed for dozens/hundreds of contacts)

---

## 4. Magnetic Connectors (MagSafe-Style)

### How They Work

Magnetic connectors combine permanent magnets for alignment/retention with spring-loaded pogo pins for electrical contact. The magnets pull the two halves together and hold them in alignment while the pogo pins make contact. This is the technology behind Apple's MagSafe, many laptop/tablet charging connectors, and various wearable device chargers.

### Key Specifications (Hobby-Grade)

**Adafruit DIY Magnetic Connectors (Product 5358/5359/5360):**

| Parameter | Value |
|---|---|
| Pin count | 3, 4, or 5 contact versions |
| Pin pitch | 2.54mm (0.1") |
| Current rating | 2A max per pin |
| Contact type | Spring-loaded pogo pins |
| Alignment | Embedded magnets, self-aligning |
| Mounting | Right-angle PCB solder |
| Price | ~$4-5 per mated pair |

**Professional/Custom Options:**
- 5A-8A for consumer device charging
- 10A-30A for industrial applications (custom manufacturing)
- IP67/IP68 waterproof versions available from specialized manufacturers

### Suitability for Slide-In Application

Magnetic connectors are fundamentally designed for a **drop-on or snap-on** mating action, not a slide-in. The magnets attract the two halves together perpendicular to the contact face. In a slide-in cartridge:

- The magnets would fight the slide motion (attracting laterally before alignment)
- The snap-on retention force competes with the mechanical slide-in lock
- If the cartridge slides past the magnetic connector, the magnets provide no benefit

Magnetic connectors make much more sense for a **drop-in** dock design where the cartridge lowers vertically onto the dock. For a straight slide-in with 100-200mm travel, magnets add complexity without clear benefit.

### Advantages

- Self-aligning (magnets guide contacts into position)
- Clean break on removal (MagSafe safety feature)
- Available as ready-made hobby modules from Adafruit
- Compact form factor

### Disadvantages

- Designed for snap-on, not slide-in -- poor fit for this insertion motion
- 2A current limit on hobby-grade modules (marginal for 3A motor peaks)
- Magnets attract ferrous debris (metal shavings, screws, tools under a sink)
- More expensive than blade connectors or bare pogo pins
- Magnetic retention may not be strong enough for reliable contact under vibration
- Magnets and water: corrosion risk if magnets aren't fully sealed

---

## 5. Bare Contact Pads + Spring Pressure

### How They Work

The simplest approach: exposed conductive pads on the cartridge pressed against spring contacts in the dock. This is exactly how battery compartments work in flashlights, remote controls, toys, and portable electronics. A coil spring or leaf spring in the dock pushes against a flat metal pad on the cartridge.

### Contact Materials and Surface Finish

| Material | Conductivity | Corrosion Resistance | Cost | Notes |
|---|---|---|---|---|
| Nickel-plated steel | Good | Good | Low | Standard battery contact material |
| Nickel-plated brass | Better | Good | Low | Better conductivity than steel |
| Gold-plated copper | Excellent | Excellent | Medium | Best for low-resistance contacts |
| Tin-plated brass | Good | Moderate | Low | Good weldability |
| Stainless steel | Moderate | Excellent | Low | Higher contact resistance |
| Beryllium copper (BeCu) | Excellent | Good | Medium | Best spring material, 98% Cu / 2% Be |

For this moisture-adjacent application, nickel-plated brass is the sweet spot: good conductivity, corrosion resistance, low cost. Gold plating over nickel is the premium option for lowest contact resistance and best corrosion resistance.

### Battery Contact Design Patterns

**Coil spring (negative terminal style):**
- Simple compression spring soldered to a PCB pad or crimped to a wire
- Provides 2-5mm of travel
- Current capacity depends on wire gauge of spring: 18 AWG spring wire handles 5A+
- Very cheap, available everywhere

**Leaf spring / finger contact (positive terminal style):**
- Flat spring steel or BeCu strip bent into a curved contact
- Provides 1-3mm of travel with wiping action as cartridge slides
- Multiple fingers can share current load
- This is how most battery compartment positive contacts work

**Dome/button contact:**
- Stamped metal dome that flexes under pressure
- Less travel than coil spring, but flatter profile
- Common in coin cell holders

### Current Handling

Battery contacts routinely handle 1-5A in consumer devices. Larger spring contacts (like those in power tool battery packs) handle 20A+. For the 0.3A typical / 3A peak of this application, even the cheapest battery spring contacts are more than adequate.

### Sourcing

- Amazon: battery spring contacts, various sizes, $5-10 for packs of 20-50
- Keystone Electronics: professional battery contacts available from DigiKey/Mouser
- Leaf springs / finger contacts: available as individual components or can be fabricated from phosphor bronze strip

### Advantages

- Cheapest option by far
- Simplest to integrate into 3D printed housing
- Proven in billions of consumer devices
- Easy to replace if worn
- Handles adequate current for this application

### Disadvantages

- No inherent self-wiping action for direct-press contacts (coil spring type)
- Leaf spring contacts DO provide wipe if oriented for slide-in
- Open contacts are fully exposed to moisture
- Contact resistance higher than pogo pins or blade connectors
- Spring force can vary with fatigue
- Less precise alignment than purpose-built connectors
- Corrosion of bare metal surfaces in humid environment requires appropriate plating

---

## 6. Moisture Considerations

All contacts are on the same mating face as 4 John Guest 1/4" push-to-connect water line fittings. This is the most critical design challenge.

### What Happens If Water Contacts the Electrical Connections

At 12V DC:
- **Short circuit between contacts:** Motor driver sees a short, potentially damaging the L298N H-bridge. A fuse or current-limiting on the motor driver is essential regardless of connector choice.
- **Electrolysis/corrosion:** DC voltage across wet contacts accelerates galvanic corrosion. The anode contact will corrode rapidly. Even intermittent moisture accelerates this.
- **Leakage current:** Water between contacts creates a resistive path. At 12V with tap water (~500 ohm/cm conductivity), leakage current through a water bridge could be tens of milliamps -- enough to cause slow corrosion but unlikely to damage the motor driver.

### Contact Material Choices for Moisture Resistance

- **Gold plating:** Best corrosion resistance, prevents oxide formation entirely. Even a thin flash of gold (5 microinches) helps; 30+ microinches for reliable long-term performance.
- **Nickel plating:** Good barrier against oxidation, standard for moisture-exposed contacts.
- **Stainless steel:** Inherently corrosion resistant but higher contact resistance.
- **Avoid:** Bare copper (oxidizes rapidly in humidity), bare brass (dezincification in wet conditions), tin (whisker growth in humid environments).

### Conformal Coating

Conformal coating (silicone, acrylic, or urethane) can protect PCB traces and solder joints near the contacts, but the contact surfaces themselves cannot be coated -- they must remain bare metal for electrical contact.

### Physical Separation Strategies

**Minimum separation distance:**
- IPC-2221 standard recommends minimum 0.6mm clearance between conductors at 12V in a contaminated environment. Between electrical contacts and water fittings, 10-20mm minimum separation is prudent.
- More is better. If the mating face allows it, 25-50mm separation provides meaningful splash protection.

**Drainage channels:**
- Molded channels in the 3D printed dock face between the water fittings and electrical contacts
- Water flows downward (gravity) rather than laterally toward contacts
- A raised ridge or wall between water and electrical zones acts as a dam

**Splash guards:**
- A raised lip or overhang above the electrical contacts prevents drips from above
- Since this is under a sink, gravity pulls water downward -- contacts placed ABOVE the water fittings (or to the side with a dam) are safer

**Recessed contacts:**
- Electrical contacts recessed into a pocket in the dock face
- The pocket acts as a physical barrier to splashed water
- Must include drain holes so trapped water can escape (avoid creating a pool)

### Should Electrical Contacts Be on a Different Face?

**Strong argument for YES:**
- Water fittings have O-ring seals but can weep during connection/disconnection
- Separating the failure domains (water vs. electrical) is sound engineering
- A cartridge has 6 faces; using one for water and another for electrical is trivial

**Argument for keeping them together:**
- Single mating action (one slide connects everything)
- Fewer alignment constraints
- Simpler dock geometry

**Recommendation:** If the cartridge design allows it, placing electrical contacts on the TOP face of the cartridge and water fittings on the FRONT face (or vice versa) provides the best moisture isolation. If they must share a face, place electrical contacts above the water fittings (water drips down, not up) with a raised dam between them.

---

## 7. Self-Cleaning / Wipe Action

### Why Wipe Matters

Over time, contact surfaces develop:
- Oxide films (even gold-plated contacts develop contaminant films)
- Dust and debris accumulation
- Mineral deposits (especially in a moisture-adjacent environment)
- Corrosion products

A wiping action -- where one contact slides laterally across the other during mating -- physically scrapes away these non-conductive layers, exposing fresh metal underneath. Without wipe, contacts rely solely on contact pressure to break through surface films, which becomes less reliable over time.

### How Much Wipe is Needed

Industry guidelines (per Samtec engineering and general connector design practice):
- **Minimum effective wipe:** 0.5mm (0.020")
- **Typical wipe in production connectors:** 1-3mm
- **Card-edge connectors (PCIe, etc.):** 3-6mm of wipe (the full gold finger length)
- **Blade/tab connectors:** 5-15mm of wipe (full insertion depth)

For this application, even 1-2mm of wipe during the final portion of cartridge insertion is sufficient to maintain reliable contact.

### Which Connector Types Provide Inherent Wipe

| Connector Type | Wipe Action | Wipe Distance | Notes |
|---|---|---|---|
| Pogo pin (slide-in) | Yes | Depends on pad length and insertion geometry | Pin drags across pad during slide |
| Blade / tab | Yes | Full insertion depth (5-15mm) | Excellent natural wipe |
| Card-edge | Yes | Full finger length (3-6mm) | Designed for wipe |
| Magnetic (snap-on) | Minimal | < 0.5mm | Straight-on press, minimal lateral motion |
| Battery spring (coil) | No | 0mm | Pure vertical compression |
| Battery spring (leaf) | Yes | 1-3mm | Leaf flexes and wipes during slide |

### Designing for Wipe in This Application

Since the cartridge slides ~100-200mm into the dock, any contact that engages during the last portion of insertion automatically gets wipe action. The key design choices:

1. **Contact pad on cartridge should be elongated in the insertion direction** (e.g., 10mm long x 5mm wide pad for a 2mm pogo pin tip). The pin contacts the leading edge of the pad and wipes across it as insertion completes.

2. **Pogo pins or leaf springs in the dock should be oriented so the cartridge motion creates lateral wipe**, not just vertical compression.

3. **Blade connectors inherently align with the insertion axis**, so wipe is automatic.

---

## 8. Practical Evaluation for This Application

### Requirements Summary

- 3 contacts: GND, Motor A (12V), Motor B (12V)
- Current: 0.3A typical, 3A peak, brief stall transients
- Environment: moisture-adjacent (under kitchen sink, near water fittings)
- Housing: 3D printed (PLA/PETG, ~0.2mm dimensional tolerance)
- Insertion: straight slide, 100-200mm travel, contacts mate at end
- Scale: prototype, 1-5 units
- Replacement frequency: infrequent (weeks to months between cartridge swaps)

### Option Comparison

| Criteria | Pogo Pins | Blade/Tab | Card-Edge | Magnetic | Bare Spring |
|---|---|---|---|---|---|
| Current handling | A+ | A+ | B | B- | A |
| Alignment tolerance | A+ | B | B+ | A+ | A |
| Self-wipe (slide-in) | A | A+ | A+ | D | B (leaf) |
| Moisture resistance | B | B- | B- | C | B- |
| 3D print integration | A | B+ | B- | B | A+ |
| Cost (3 contacts) | B | A+ | B | B- | A+ |
| Sourcing ease | A | A+ | B+ | A | A+ |
| Complexity | B+ | A | B- | C | A+ |

### Recommended Approach: Pogo Pins (Dock) + Flat Pads (Cartridge)

**Why pogo pins win for this application:**

1. **Alignment tolerance is the decisive factor.** With 3D printed housings at ~0.2mm tolerance over a 100-200mm slide path, the contacts at the end of travel could easily be off by 1-2mm. Pogo pins with oversized target pads (e.g., 8mm pads for 2mm pins) handle this effortlessly. Blade connectors would need precision guide features.

2. **Natural wipe action during slide-in.** The pogo pin tip drags across the flat pad during the final millimeters of insertion, providing self-cleaning without any additional mechanism.

3. **Moisture tolerance.** The contact surface on the cartridge is a flat pad -- no pocket to trap water. The pogo pin barrel can be conformal-coated below the plunger. If water does get on the pad, the spring force and wipe action push through it.

4. **Simple cartridge design.** The cartridge side is just 3 flat metal pads -- can be brass plates press-fit or epoxied into a 3D printed surface, or a small PCB with copper pads.

5. **Current capacity.** Even cheap P75 test probes handle 1-3A. For the typical 0.3A load with 3A peaks, standard pogo pins are adequate. For extra margin, Mill-Max 0852 series (9A rated) pins are available for ~$3 each.

### Specific Implementation Sketch

**Dock side:**
- 3x spring-loaded pogo pins (P100-series or Mill-Max, 2-3mm diameter, 1-2mm stroke)
- Mounted in a 3D printed pocket at the back of the dock slot
- Pins face the incoming cartridge face
- Connected to motor driver via wire (solder cup) or small PCB (through-hole)

**Cartridge side:**
- 3x nickel-plated brass pads (8mm x 5mm each), press-fit into 3D printed cartridge face
- Pads slightly recessed (0.5mm) to prevent accidental shorts during handling
- Pads spaced 10mm center-to-center (well within 3D print tolerance)
- Connected to pump motor leads via solder or crimp

**Moisture mitigation:**
- Electrical contacts on TOP of cartridge/dock mating face
- Water fittings on BOTTOM of mating face
- 3D printed dam/ridge between electrical and fluid zones
- Drain channel below water fittings
- Nickel or gold plating on pads for corrosion resistance

### Budget Estimate (3 contacts, 1 unit)

| Component | Source | Approximate Cost |
|---|---|---|
| 3x pogo pins (P75 or P100) | Amazon/AliExpress pack | $2-5 (from 100-pack) |
| 3x brass pads (or small PCB) | Amazon brass strip / JLCPCB | $1-5 |
| Wire, solder, heatshrink | Stock | $1 |
| **Total** | | **$4-11** |

For higher quality Mill-Max pins: add $5-15 for 3 pins from DigiKey.

### Fallback Option: Blade / Tab Connectors

If alignment proves better than expected (tight 3D print tolerances, good guide rails), FASTON .250 blade connectors are the cheapest and simplest option:
- 3x tab terminals on cartridge: $0.30
- 3x receptacle terminals in dock: $0.30
- Total: under $1 for all contacts
- 7A rating provides generous margin
- Excellent wipe action

The risk is alignment: if the 3D printed guide rails don't hold the cartridge precisely enough, the blade may miss the receptacle opening. A tapered funnel lead-in on the receptacle pocket can help, but this requires more precise 3D printed geometry than the pogo pin approach.

### What to Prototype First

1. **Start with pogo pins + brass pads.** Order a pack of P75 or P100 pogo pins from Amazon (~$8 for 100 pieces). Cut 3 small brass pads from hobby brass sheet. Mount in 3D printed test pieces and verify contact reliability across multiple insertions with deliberate misalignment.

2. **Measure actual alignment tolerance** of the 3D printed slide mechanism. If it's consistently within +/- 0.5mm, blade connectors become viable and cheaper.

3. **Test moisture resistance** by misting the contacts with water and verifying the motor still runs correctly. Check for corrosion after a week of under-sink installation.

---

## Sources

- [Mill-Max Spring Loaded Pogo Pins & Connectors](https://www.mill-max.com/engineering-notebooks/spring-loaded-pogo-pins-connectors)
- [Mill-Max High Current Spring-Loaded Pins](https://www.mill-max.com/products/new/rugged-high-current-spring-loaded-pogo-pins)
- [Mill-Max Pogo Pin FAQs](https://www.mill-max.com/engineering-notebooks/spring-loaded-pogo-pins-connectors/faqs)
- [Same Sky Pogo Pins 101](https://www.sameskydevices.com/blog/pogo-pins-101)
- [CFECON 30A High Current Pogo Pins](https://cfeconn.com/connector/30a-high-current-pogo-pins-spring-loaded-contacts/)
- [TE Connectivity FASTON Terminals](https://www.te.com/en/products/brands/faston.html)
- [FASTON Terminal Quick Reference Guide (Mouser PDF)](https://www.mouser.com/pdfdocs/TEConnectivityFASTONQuickReferenceGuide.PDF)
- [FASTON Terminal - Wikipedia](https://en.wikipedia.org/wiki/FASTON_terminal)
- [What Are Blade Connectors - Connector Supplier](https://connectorsupplier.com/what-are-blade-connectors/)
- [TE Connectivity Card Edge Power Connectors](https://www.te.com/en/products/connectors/pcb-connectors/card-edge-connectors/card-edge-power-connectors.html)
- [PCBWay Gold Fingers](https://www.pcbway.com/pcb_prototype/PCB_Gold_fingers.html)
- [Adafruit DIY Magnetic Connector - 3 Pin (Product 5360)](https://www.adafruit.com/product/5360)
- [SUNMON Magnetic Pogo Pin Connector Design Guide](https://smeconn.com/magnetic-pogo-pin-connector-design-guide/)
- [Waterproof Pogo Pin Connectors - Promax](https://promaxpogopin.com/manufacturer/pogo-pin/connector/waterproof/)
- [IP67 Waterproof Pogo Pin Connector - Johoty](https://www.johotypro.com/ip67-waterproof-pogo-pin-connector/)
- [Samtec Blog: Is Contact Wipe Important?](https://blog.samtec.com/post/is-contact-wipe-important/)
- [Adafruit 12V Peristaltic Pump (Product 1150)](https://www.adafruit.com/product/1150)
- [Lee Spring - Battery Springs](https://www.leespring.com/learn-about-battery-springs/)
- [Newcomb Spring - Battery Contacts](https://www.newcombspring.com/products/battery-contacts-springs)
