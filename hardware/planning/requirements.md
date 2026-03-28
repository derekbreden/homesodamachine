# Hardware Requirements

This document is the foundational input to the hardware design pipeline. Every agent in every step reads this document first. It contains facts that no agent can discover on its own — they come from the product owner and are verified before any design work begins.

If this document does not exist or has not been verified by the product owner, no design work may proceed.

---

## 1. Product Vision

We are building a soda flavor injection appliance. It sits under a kitchen counter, connected to a soda water line, and injects flavor concentrate into the soda stream on demand. It contains:

- An ESP32 main controller, an RP2040 round display, and an ESP32-S3 rotary config display
- Two peristaltic pumps in a removable cartridge
- Solenoid valves (up to 10) for flow routing
- Two 2L Platypus bags holding flavor concentrate
- A hopper/funnel system for refilling bags by pouring
- A DS3231 RTC module
- A 12V power supply
- All connected by 1/4" OD hard tubing with John Guest push-to-connect fittings

The product is controlled via an iOS app over BLE and via the on-device displays/controls.

---

## 2. Product Values

These values are absolute and apply to every decision at every level:

1. **This is a high-end consumer product.** Not a prototype, not a maker project, not a proof of concept. The standard is: what would Apple build if they were making a soda machine, but restricted to this specific 3D printer and components available from Amazon?

2. **User experience is paramount in all things.** Above durability, above simplicity, above prototypability, above cost. One-handed operation, intuitive feel, speed, dark-cabinet usability. If a design choice improves UX at the expense of everything else, it is the right choice.

3. **Cost is not a factor.** Never use cost as a reason to choose or reject any approach. Any filament, any fastener, any component that is available can be purchased. The budget is unlimited for the purpose of all design decisions.

4. **Design a product, not an assembly of parts.** The finished product must look like it was always meant to be this way — as if every surface, every transition, every interaction point was designed together as a single coherent object. Nothing should look added on, bolted to, or improvised. A stranger encountering the product for the first time should see a product, not a collection of components.

5. **Nothing needs to come apart.** The only serviceable component is the pump cartridge, which slides in and out. Everything else is permanent. If the enclosure cannot be disassembled once assembled, that is a feature, not a flaw. Glue it, weld it, press-fit it — whatever makes the product feel most solid and unified. There are no "service panels" for electronics, no "access hatches" for wiring. If something breaks, the whole unit is replaced. Design for a consumer appliance lifecycle, not for repairability.

6. **The deliverable is always the final artifact.** A STEP generation script that was never run is not a deliverable. A parts.md that contradicts the research is not a deliverable. The thing that matters is the physical object.

---

## 3. Manufacturing Equipment

### 3D Printer

**Bambu Lab H2C**

The exact specifications of this printer are documented in `manufacturing-environment.md`, which is produced by Step 0 of the design pipeline by looking up the manufacturer's published specifications. No agent may assume printer capabilities — they must read the verified spec document.

### Materials

Any filament that is compatible with the Bambu Lab H2C is available. This includes but is not limited to: PLA, PETG, PETG-CF, ABS, ASA, PA (nylon), PA-CF, PC, TPU, PVA (support), and any specialty filaments Bambu Lab sells or that third parties produce for this printer class.

Material selection for each part is a design decision made during the pipeline, not a constraint. Agents should choose the material that best serves the product values above, not the cheapest or most common material.

### Components

All off-the-shelf components (fasteners, magnets, springs, heat-set inserts, bearings, etc.) are sourced from Amazon Prime. Any component that is available on Amazon can be used. Cost is not a factor.

### Tools

The product owner has standard maker tools available (screwdrivers, hex keys, soldering iron for heat-set inserts, CA glue, sandpaper, etc.). No specialized tooling (CNC, injection molding, etc.) is available — all custom parts are 3D printed on the H2C.

---

## 4. Existing Hardware (already purchased/built)

The following components are already in the system and are constraints on the design (the design must accommodate them, not replace them):

- **ESP32 dev board** — main controller
- **Waveshare 0.99" round LCD with RP2040** — flavor display
- **ESP32-S3 with Meshnology rotary encoder display** — config interface
- **DS3231 RTC module** (I2C, CR2032 backup)
- **Peristaltic pumps** (2x, in removable cartridge)
- **Beduan 12V solenoid valves** (up to 10)
- **2L Platypus bags** (2x, 190W x 350L mm, lens-shaped cross-section)
- **John Guest 1/4" push-to-connect fittings** (various types: straights, elbows, tees)
- **1/4" OD hard PE/PU tubing**
- **L298N motor drivers** (for pump control)
- **MCP23017 I/O expander** (for valve control)
- **6x3mm neodymium disc magnets** (for display docking and panel retention)
- **M3 fasteners and heat-set inserts**

---

## 5. What This Document Does NOT Contain

- **Specific dimensions, geometry, or architecture** — those are outputs of the design pipeline, not inputs
- **Material choices for specific parts** — those are design decisions
- **Printer specifications** — those belong in `manufacturing-environment.md`, produced by Step 0
- **Mechanism designs** — those emerge from the pipeline's research and architecture steps

This document contains only the facts that a design agent cannot discover on its own and that must be true before any design work makes sense.
