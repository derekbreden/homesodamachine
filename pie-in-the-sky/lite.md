# Lite Edition — flavor companion to a customer-supplied carbonator

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

A small companion appliance that pairs with a customer-supplied countertop carbonator (Lillium, Brio, or equivalent) to add flavor injection through a real faucet. The Lite Edition does not refrigerate. It does not carbonate. It does not store water. It is a flavor-injection module — two reservoirs, two peristaltic pumps, a manifold, a faucet, the dispense controls, and a small enclosure to wrap them — and the customer's existing or newly-purchased carbonator is the source of cold carbonated water.

## What the customer buys

Two appliances, sourced separately:

1. A Lillium (or Brio, or equivalent) — a countertop carbonator the customer plumbs to their cold water line and pressurizes from a CO2 tank. These run roughly $2,500 retail and produce ~4 °C carbonated water at up to ~70 PSI. The customer buys this themselves from the original manufacturer; the Lite Edition does not include it.
2. The Lite Edition — flavor companion, sourced from us. Price target around $1,500.

The customer's total spend across both appliances is approximately $4,000.

## What the Lite Edition is

A consumer-grade enclosure wrapping the flavor-injection half of the main appliance, with no refrigeration subsystem and no carbonation subsystem. Specifically:

- **Two flavor reservoirs**, 1 L each. Same printed hard reservoir architecture as the main appliance, vented through PTFE membrane caps. Filled through a top hopper. **Not refrigerated.** Reservoirs sit at room temperature.
- **Two peristaltic pumps** (Kamoer KPHM400), valve-locked between dispenses so each flavor primes once at install and stays primed for instant injection thereafter.
- **A valve manifold** with the same source-selection / output-routing pattern as the main appliance. Hopper input, reservoir output to faucet, clean-cycle paths.
- **A faucet** — Westbrass Touch-Flo or equivalent through-counter dispense — with the carbonated water line entering its inlet from the customer's Lillium output, and the two flavor lines injecting at the nozzle alongside the carbonated water.
- **A flavor-select air switch** (KRAUS or equivalent), through-counter.
- **An RP2040 round display** through-counter, showing the active flavor's logo.
- **Electronics shelf** — ESP32, MCP23017 expander, ULN2803A drivers, motor driver, 12 V supply. Same parts family as the main appliance.
- **A small enclosure** sized for under-sink placement. No refrigeration loop means no compressor, no condenser, no fan, no foam shell, no hydrocarbon-refrigerant shroud — the cabinet is meaningfully smaller than the main appliance's.

## What the Lite Edition does not contain

- No carbonator. No pressure vessel. No 90 PSI service. No hydro-test. No sparge stone. No level reeds. No PRV. No WR1110 regulator. No ASSE 1022 backflow preventer in the carbonator path — the customer's Lillium handles its own inlet protection.
- No refrigeration loop. No harvested ice-maker compressor. No condenser, no fan, no cap-tube, no drier. No R-600a. No UL 60335-2-89 fire-enclosure shroud. No flame-symbol marking. No SNAP-approved end-use considerations.
- No diaphragm pump. No water-side check valves. No backflow telltale moisture sensor.
- No insulated dispense path. No cold core. No foam-pour assembly.

Roughly half of `hardware/future.md` simply does not apply.

## Plumbing pattern

```
   customer's cold water ──► Lillium ──► cold carbonated water (~4°C, ≤70 PSI)
                            ▲                          │
                            │                          ▼
                customer's CO2 tank             Lite faucet inlet ◄── flavor concentrate ◄── Lite Edition pumps
```

Two cords (Lillium's, Lite's) into two outlets. One 1/4" line from the Lillium's carbonated-water output up to the back of the Lite Edition's faucet. The Lite Edition does not touch the customer's water line, does not touch their CO2 tank, and does not see pressurized water inside its own enclosure beyond the faucet inlet stub.

## What the customer's daily experience is

Lever opens — soda pours. The mechanical interaction is the same as the main appliance: pull a faucet lever, get a glass of soda with flavor injected at the nozzle.

The qualitative experience differs in three ways the customer will notice:

- **Temperature.** Lillium-class carbonators output water at roughly 4 °C at best. The main appliance targets ~2 °C and holds it in a passively-stabilized vessel; the Lite Edition has no equivalent thermal buffering and is at the mercy of the upstream carbonator's instantaneous output. After a long pour, the next pour can be noticeably warmer until the Lillium catches up.
- **Carbonation level.** Lillium-class carbonators run at roughly 70 PSI working pressure. The main appliance carbonates at 90 PSI. The difference is perceptible — sharper bite, more retained fizz in the glass — and the Lite Edition cannot make it up downstream.
- **Flavor reservoir temperature.** Syrup is dispensed at room temperature, mixing with cold carbonated water at the nozzle. The main appliance pre-chills syrup passively in the cold core; the Lite Edition does not. In practice this is a small effect at typical 1:20 syrup-to-water ratio, but it is real.

For a customer who wants faucet soda and does not have an option to install the main appliance, this is a genuine version of the experience.

## BOM sketch

| Section | Rough $ |
|---|---:|
| Controllers + electronics | $110 |
| Flavor subsystem (2 reservoirs, 2 Kamoer pumps, manifold solenoids, hopper, fittings) | $260 |
| Faucet + under-counter plate | $40 |
| User interface (air switch + display + buzzer) | $80 |
| Wiring + fasteners | $25 |
| Printed mechanical parts (smaller enclosure, hopper, pump cartridge) | $50 |
| Mechanical attach hardware + reservoir caps + membranes | $10 |
| **Total** | **~$575** |

At a Founder Edition target around $1,500 the margin structure mirrors the main appliance's at lower absolute numbers.

## What it would take to ship the Lite Edition

The Lite Edition is approximately the prototype that already exists on the founder's counter, with a consumer-grade printed cabinet around it and a tightened-up firmware build. The hard subsystems of the main appliance (carbonator vessel fabrication, hydro-test, refrigerant-loop teardown and recharge, foam-pour cold-core assembly, hydrocarbon-refrigerant safety architecture) are absent. The remaining work is enclosure design, the faucet-inlet stub that accepts a customer's Lillium output line, install documentation that explains the Lillium pairing, and ten units' worth of assembly time.

Time-to-first-unit at solo build cadence is short — weeks rather than the months the main appliance requires.

## Form factor

Under-counter, in the kitchen cabinet beneath the sink, alongside the customer's Lillium (which sits on the countertop above as it does in any home Lillium install). The Lite Edition's enclosure is smaller than the main appliance's because it contains no cold core and no refrigeration; it could fit a corner of the cabinet without disrupting other under-sink contents.
