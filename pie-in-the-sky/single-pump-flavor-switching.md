# Single-pump flavor switching — one pump, one line, N flavors

*Pie-in-the-sky, not roadmap. Captured 2026-08-07.*

*Volumes, rates, and film thicknesses in this doc are first-pass calculations intended to size the idea, not specifications.*

One peristaltic pump serves every flavor. One flavor line runs up the umbilical to the faucet at any N. Selecting a flavor is a cycle, not a valve state: the pump reverses and draws the standing syrup back into its own reservoir, the line is flushed and re-primed with the new flavor, and capacitive sensing confirms each transition. Between switches the faucet is primed and pours instantly. Switching costs time.

[`flavor-module.md`](/pie-in-the-sky/flavor-module.md) reaches the same flavor count through a second appliance with its own faucet and a four-line nozzle.

## Sensing points

Three, on one line.

- **Pump outlet**, in the dry cabinet — reads air when the line is fully evacuated, which is the condition for switching reservoir valves without stranding old syrup downstream.
- **Faucet body** and **faucet tip** — read liquid as the new flavor arrives, and confirm it reached the point of dispense.

A peristaltic head is positive-displacement, so each stage of the cycle is a counted volume with a sensor at its end.

## Line volume

The flavor path is 1/4" OD LLDPE end to end. The umbilical run is **1548 mm** installed — the 1186 mm drop plus the 362 mm the flavor tubes climb inside the faucet past where the carbonated-water tube lands, per [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §1. In-cabinet, the pump outlet reaches the rear-wall bulkhead through a junction and the nozzle gate — another 400–600 mm.

At a nominal 4.3 mm bore, **~30 mL of standing syrup**. A 12 oz pour at 1:20 draws about 17 mL.

## The cycle

| Step | mL | Where it goes |
|---|---:|---|
| Reverse — draw standing syrup back | 30 | its own reservoir; film stays on the wall |
| Flush — tap water forward, out the tip | ~45 | the sink, carrying the film |
| Prime — new syrup forward, water expelled ahead of it | 30 | line ends full of new flavor; the interface is lost |

A parked KPHM400 head passes flow both ways ([`fluid-topology.md`](/hardware/topology/fluid-topology.md)), and the manifold already runs tap pressure across an idle pump in its clean-fill modes. Tap pressure at the nozzle gate moves the flush in about a second. The reverse and the prime — 60 mL — are pump work.

## Film

A receding meniscus leaves a coating on the tube wall, thickening with speed: `h/R ≈ 1.34·Ca^(2/3)`, saturating near `h/R ≈ 0.3`. At purge rates of 100–400 mL/min through a 2.15 mm radius, `h` runs 0.18–0.33 mm — **5–9 mL of the old flavor** over a 2 m line, against a 17 mL dose.

Both ends of that range assume a syrup viscosity near 10 cP and surface tension near 50 mN/m. Neither is measured.

## Pump

Sixty millilitres of pump work in ten seconds is **~360 mL/min**, three to four times a KPHM400.

**Dispense duty.** At 360–500 mL/min, 17 mL over a pour lands near 14–19% duty; each 50 ms injection is 0.3–0.4 mL, forty-odd of them into a 355 mL glass, above the `PUMP_ON_MIN_MS` floor in [`/firmware/src/main.cpp`](/firmware/src/main.cpp). A 1:6 bag-in-box ratio lands near 40–55%.

**Head duty.** One head carries both flavors' dispensing and 60 mL per switch. Four switches a day is ~240 mL/day of purge against perhaps 100 mL of dispensing, on a single silicone tube. A larger head at lower rpm delivers the same flow.

**Drive.** The dispense-to-purge range is 25:1. A stepper head crosses it with torque at the bottom and makes each revolution a known volume. The board carries two DRV8870 brushed H-bridges ([`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)); this is one pump on a DRV8825/TMC2209-class driver.

## Sensing hardware

The machine carries no liquid-in-line sensing today. What this design wants is a printed clamshell holding two copper foil rings against a 1/4" LLDPE tube, read by a charge-transfer controller — an MPR121 at 0x5A takes twelve electrodes behind one address — on the existing I2C bus with no ESP32 GPIO. The J8 header ([`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)) is where it would land, so the board needs no change. The pump-outlet sensor is that same part in a different position on the same tube size in the same dry cabinet.

The faucet pair would sit in a PET-CF gooseneck with carbonated water and condensation inches away and a hand on the capacitive LCD during selection. The faucet carries its own ESP32-S3 with an I2C bus and a UART link home over SIG-6, so a controller there adds no umbilical conductors.

Prime is a counted volume with or without the faucet electrodes reporting. Without them, the cycle loses its read on empty reservoir, blockage, and pump slip.

## What changes

**Direction.** [`fluid-topology.md`](/hardware/topology/fluid-topology.md) states flow inlet-to-outlet only and pumps forward only, and the truth table is built on it. Direct-acting solenoids pass reverse flow; pilot-operated ones do not. Which the Beduan valves are decides whether the rest of this doc has a subject.

**Suction at the tip.** Air enters the flavor path at the hopper funnel today — dry, open, unfiltered — and leaves at the tip; every mode in the truth table runs forward, and each dispense path carries a gate at both ends of its pump so a standing column cannot drain back through a parked head. Reversing makes an open tip in a wet dispense head, beside the carbonated-water stream, into the air inlet. A PTFE-membrane vent in the gooseneck above the tip takes the make-up air instead, the same part family as the reservoir vented caps in [`cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/).

**Or nothing.** The cycle runs forward out of modes already in the table — tap pressure across the idle head to the nozzle gate, hopper air through the pump to the nozzle gate, then Dispense verbatim. The upstream sensor reads air at the end of the dry step, the tip sensor reads liquid at the end of the prime, and pump work stays 60 mL. The 30 mL goes out the tip rather than back to its reservoir — 1.8 doses per switch.

**Manifold.** Per reservoir, a draw valve and a return valve. Shared, the tap inlet, the hopper gate, and the nozzle gate. **2N + 3.**

## Counts

| | Valves | Pumps | Tubes up the counter | Nozzle ports |
|---|---:|---:|---:|---:|
| Two flavors, as built | 10 | 2 | 2 | 2 |
| Two flavors, single-pump | 7 | 1 | 1 | 1 |
| Four flavors, single-pump | 11 | 1 | 1 | 1 |
| Six flavors, single-pump | 15 | 1 | 1 | 1 |

A flavor is two solenoids and a reservoir. The faucet, the umbilical, and the nozzle are the same part at every N.

The line takes a water flush on every switch. Reverting to the household default in the background after a non-default pour leaves it standing primed with the common flavor.

## Open questions

1. **Are the manifold solenoids bidirectional?** Direct-acting passes reverse flow; pilot-operated does not.
2. **The 1/4" LLDPE bore is not recorded anywhere in the repo.** Every volume here assumes 4.3 mm, and scales as its square. Measure the neoFlo spool.
3. **KPHM400 delivered flow is unspecified.** The 3–4× figure is relative to an assumed 100 mL/min. Measure the pumps.
4. **What does 30 mL of aerated syrup do inside the reservoir?** The vented cap passes the air. Foam riding the magnet float reaches the reed column in [`level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md).
5. **Does a capacitive electrode read through PET-CF at the tip**, with condensation on the gooseneck and a hand on the LCD?
6. **Syrup viscosity and surface tension.** The film range and the flush volume rest on assumed values.
