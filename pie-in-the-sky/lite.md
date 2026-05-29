# Lite Edition — flavor companion to a Lillium-class carbonator

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A small companion appliance that pairs with a Lillium-class under-sink carbonator (Lillium, Brio, or equivalent) to add flavor injection through a real faucet. The Lite Edition does not refrigerate. It does not carbonate. It does not store water. It is a flavor-injection module — two reservoirs, two peristaltic pumps, a manifold, a faucet, the dispense controls, and a small enclosure to wrap them — and the paired carbonator is the source of cold carbonated water.

## What the customer buys

Two appliances. We offer both — the Lillium as a reseller (it stays a Lillium product, with Lillium quality, warranty, and service relationship intact), the Lite Edition as our own product:

1. A Lillium (or Brio, or equivalent) — an under-sink carbonator that plumbs to the customer's cold water line and pressurizes from a CO2 tank. These run roughly $1,000 retail and produce ~4 °C carbonated water at up to ~70 PSI. Customers who already own a compatible unit skip this line item.
2. The Lite Edition — our own product, our manufacture. ~$1,500.

Bundle total: ~$2,500. Lite alone: ~$1,500. The bundle is the easier path for a new customer — one purchase, one shipment, one install consult covering both appliances. Lite-alone serves the customer who already has a working carbonator and just wants the flavor companion.

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

At a Founder Edition target around $1,500 the margin structure mirrors the main appliance's at lower absolute numbers. The bundled Lillium passes through at near-zero margin to us — we're not in the business of making money on someone else's appliance, we're in the business of removing a sourcing step for the customer.

## What it would take to ship the Lite Edition

The Lite Edition is approximately the prototype that already exists on the founder's counter, with a consumer-grade printed cabinet around it and a tightened-up firmware build. The hard subsystems of the main appliance (carbonator vessel fabrication, hydro-test, refrigerant-loop teardown and recharge, foam-pour cold-core assembly, hydrocarbon-refrigerant safety architecture) are absent. The remaining work is enclosure design, the faucet-inlet stub that accepts a Lillium output line, install documentation that explains the Lillium pairing, and ten units' worth of assembly time.

## Minimum set of printed parts

A walk through [`hardware/printed-parts/`](/hardware/printed-parts/) filtered for what the Lite Edition needs — what the existing prototype already uses, plus what would be added for the consumer-grade cabinet. The cold-core stack (foam shells, foam caps, copper plugs, coil mandrel, PRV shroud) is absent because the Lite Edition has no carbonator and no refrigeration.

For the prototype's last-known state before its narrative doc was retired, see git tags `prototype-doc-last-known` and `prototype-bom-last-known`.

### Existing iteration in flight

**Faucet stack** — [`hardware/printed-parts/faucet/`](/hardware/printed-parts/faucet/)

- [`touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) — PET-CF, 3-piece split shell, 0.6 mm DUROZZLE TC nozzle, same-material supports. Joint-clearance arc closed at attempt 14 ("Pretty good. Or good enough at least for now" per [`print-log.md`](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md)); current iteration is on tube-bore clearances and scarf-seam handling, both in recording-only posture. Assembly procedure in [`ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md).
- [`touch-flo-mounting-plate/`](/hardware/printed-parts/faucet/touch-flo-mounting-plate/) — paired with shell on the current 3-piece plate.
- [`touch-flo-mounting-gasket/`](/hardware/printed-parts/faucet/touch-flo-mounting-gasket/) — TPU gasket between mounting plate and countertop.
- [`touch-flo-tpu-o-ring/`](/hardware/printed-parts/faucet/touch-flo-tpu-o-ring/) — TPU o-ring at the body-to-shell interface.

**Reservoir stack** — [`hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) (directory lives under cold-core for historical reasons; the reservoir parts themselves don't depend on the rest of the cold core)

- `reservoir-left.step` + `reservoir-right.step` — bodies. SunTop food-contact-compliant PETG, 0.8 mm high-flow nozzle. First print at this material + geometry combination ran 2026-05-22 per [`print-log.md`](/hardware/printed-parts/cold-core/reservoir/print-log.md).
- `reservoir-cap-left.step` + `reservoir-cap-right.step` — caps with PTFE membrane vent pockets per [`vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md).
- `reservoir-gasket.step` — TPU sandwich between cap and body around the M3 × 12 screw circle.
- `reservoir-bulkhead-seal.step` — PETG seal at the bottom outlet bulkhead.
- `reservoir-retaining-ring.step` — TPU ring holding the ø13 mm PTFE membrane filter in the cap.

### Exists, no documented iteration

**Flavor pump stack** — [`hardware/printed-parts/flavor/`](/hardware/printed-parts/flavor/)

- [`pump-case/`](/hardware/printed-parts/flavor/pump-case/) — base + cap STEPs generated. No print-log or README on file.
- [`peristaltic-tube/`](/hardware/printed-parts/flavor/peristaltic-tube/) — STEP generated. No print-log or README.
- [`cap-sense-sleeve/`](/hardware/printed-parts/flavor/cap-sense-sleeve/) — +Y and -Y STEPs generated. No print-log or README.
- [`buckle/`](/hardware/printed-parts/flavor/buckle/) — only `discussion.md` on file; no STEP, no cadquery. Not designed yet.

### Not designed — added scope for the Lite Edition

The existing prototype lives ad-hoc on the counter; the Lite Edition wraps it in a consumer form. Parts that don't exist yet because the prototype does without them:

- **Enclosure shell.** The cold-core enclosure docs ([`back-panel/`](/hardware/printed-parts/enclosure/back-panel/), [`front-panel/`](/hardware/printed-parts/enclosure/front-panel/), [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/)) are sized and oriented for the integrated appliance — side-to-side condenser airflow, rear-panel CO2 / water inlets, compressor compartment, foam-shell back wall. None of that applies. A separate, smaller enclosure design is its own pass: footprint, panel layout, faucet pass-through, hopper opening, pump-cartridge access door, electronics mount, mounting feet, rear inlet for the Lillium carbonated-water hose.
- **Reservoir mounting outside the foam shell.** Current reservoir bodies are dimensioned to nest in foam-shell pockets. The reservoir itself (body + cap + bulkhead outlet + vent) is self-contained, but the way it's held inside the enclosure is new — either brackets integral to the enclosure shell or separate cradles.
- **Level-sensing column mount.** Per [`level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md), the reed column lives in a channel cut into the foam shell — *"The foam shell carries the channel that holds the column — no separate printed reed-holder part."* Without a foam shell, the Lite Edition gets either a new printed reed-holder part attached to the reservoir or the enclosure, or ships without level sensing (the prototype on the counter may already do without).
- **Hopper.** Cold-core docs reference an enclosure-integrated hopper for top-fill. Lite-side, the hopper is either part of the new enclosure shell or a separate part that mounts to it.
- **Electronics-shelf housing.** Cold-core has an electronics shelf at the top-back. Lite-side, the electronics take a smaller home — either a discrete printed part or a feature of the new enclosure shell.

### Open questions that surface from this walk

- Does the prototype currently include level sensing? If yes, how is the reed column mounted today? If no, the Lite Edition's level-sensing question collapses to "does it need one at all."
- Is `flavor/buckle` load-bearing for the prototype, or just an idea captured in `discussion.md`?
- Are `flavor/pump-case` + `peristaltic-tube` + `cap-sense-sleeve` the same iteration the prototype is using, or is the prototype on earlier / different versions?
- Is `touch-flo-shell` at attempt 14/15 the version that would ship, or is more iteration expected — the scarf-seam recording-only posture suggests Derek is still tuning.

## Form factor

Under-counter, in the kitchen cabinet beneath the sink, alongside the customer's Lillium (also a plumbed under-sink appliance). The Lite Edition's enclosure is smaller than the main appliance's because it contains no cold core and no refrigeration; it could fit a corner of the cabinet without disrupting other under-sink contents.
