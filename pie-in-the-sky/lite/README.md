# Lite Edition — flavor companion to a Lillium-class carbonator

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A small companion appliance that pairs with a Lillium-class under-sink carbonator (Lillium, Brio, or equivalent) to add flavor injection through a real faucet. The Lite Edition does not refrigerate. It does not carbonate. It does not store water. It is a flavor-injection module — two collapsible flavor bags, two peristaltic pumps, a manifold, a faucet, the dispense controls, and a small enclosure to wrap them — and the paired carbonator is the source of cold carbonated water.

## What the customer buys

Two appliances. We offer both — the Lillium as a reseller (it stays a Lillium product, with Lillium quality, warranty, and service relationship intact), the Lite Edition as our own product:

1. A Lillium (or Brio, or equivalent) — an under-sink carbonator that plumbs to the customer's cold water line and pressurizes from a CO2 tank. These run roughly $1,000 retail and produce ~4 °C carbonated water at up to ~70 PSI. Customers who already own a compatible unit skip this line item.
2. The Lite Edition — our own product, our manufacture. ~$1,500.

Bundle total: ~$2,500. Lite alone: ~$1,500. The bundle is the easier path for a new customer — one purchase, one shipment, one install consult covering both appliances. Lite-alone serves the customer who already has a working carbonator and just wants the flavor companion.

## What the Lite Edition is

A transparent consumer-grade enclosure wrapping the flavor-injection half of the main appliance, with no refrigeration subsystem and no carbonation subsystem. Specifically:

- **Two collapsible flavor bags** (Platypus-class, food-grade), ~1 L each, spout-down in a cradle. Liquid funnels to the low port; the bag collapses as it empties, visible through the transparent enclosure. The bag-in-box pattern. Filled through a top hopper routed to the bag's port through the manifold. A swappable consumable. **Not refrigerated** — bags sit at room temperature.
- **Two peristaltic pumps** (Kamoer KPHM400), valve-locked between dispenses so each flavor holds prime between pours for instant injection.
- **A valve manifold** with the same source-selection / output-routing pattern as the main appliance. Hopper input, bag output to faucet, clean-cycle paths. Lite divergences — BiB dispenses direct with no chilled pre-load, clean water comes from the Lillium, and the runs the user sees through the enclosure go clear — in [`fluid-topology-manifold.mmd`](/pie-in-the-sky/lite/fluid-topology-manifold.mmd).
- **A faucet** — Westbrass Touch-Flo or equivalent through-counter dispense — with the carbonated water line entering its inlet from the customer's Lillium output, and the two flavor lines injecting at the nozzle alongside the carbonated water.
- **A flavor-select air switch** (KRAUS or equivalent), through-counter.
- **A config display** — the same Waveshare ESP32-S3-Touch-LCD-4.3B as the main appliance, set into a 45° facet at the top-front-left of the enclosure (angled up to the user), showing the active flavor by default and reaching settings on touch. Same front display as the Kitchen edition.
- **Electronics shelf** — ESP32, MCP23017 expander, ULN2803A drivers, motor driver, 12 V supply. Same parts family as the main appliance.
- **A transparent PETG enclosure** sized for under-sink placement. The same split-half (front + back) cross-pinned shell as the main appliance, with the display facet and a drop-in hopper opening — but no refrigeration loop, so no compressor, condenser, fan, foam shell, or hydrocarbon-refrigerant shroud; the reservoir-pockets bag box is the heavy back-bottom anchor instead of the cold core, and the cabinet is meaningfully smaller than the main appliance's.

## What the Lite Edition does not contain

- No carbonator. No pressure vessel. No 90 PSI service. No hydro-test. No sparge stone. No level reeds. No PRV. No WR1110 regulator. No ASSE 1022 backflow preventer in the carbonator path — the customer's Lillium handles its own inlet protection.
- No refrigeration loop. No harvested ice-maker compressor. No condenser, no fan, no cap-tube, no drier. No R-600a. No UL 60335-2-89 fire-enclosure shroud. No flame-symbol marking. No SNAP-approved end-use considerations.
- No diaphragm pump. No water-side check valves. No backflow telltale moisture sensor.
- No reed level sensing on the flavor bags. No PTFE vent membrane. No reservoir caps, gaskets, retaining rings, or bulkhead seals.
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

## Setup, priming, and refill

Manual and watched at every step — no level sensors, no automated prime. The customer does by hand and eye what the main appliance's sensors and firmware do on their own. Factory setup procedure:

1. Hold PRIME. Watch the bags. Keep holding until they appear flat and no air pulses at the faucet.
2. Pour one bottle of concentrate into the hopper. Watch the bag fill.
3. Pour a second bottle. Watch the bag fill again.
4. Stop pouring.
5. Hold PRIME again until flavoring reaches the faucet.
6. Done — until a bag runs low.

Refill: top a bag up before it empties, watching through the enclosure to catch it in time. Let one run dry and air gets back into the line; the next fill starts over at step 1's hold-and-watch purge.

Clean cycle: the customer starts it, watches Lillium water run out through the flavor lines, and judges when it's finished. No unattended sequence, no sensor calling it done.

## BOM sketch

| Section | Rough $ |
|---|---:|
| Controllers + electronics | $110 |
| Flavor subsystem (2 collapsible bags, 2 Kamoer pumps, manifold solenoids, hopper, fittings) | $260 |
| Faucet + under-counter plate | $40 |
| User interface (air switch + display + buzzer) | $80 |
| Wiring + fasteners | $25 |
| Printed mechanical parts (transparent enclosure, hopper, bag cradles, pump cartridge) | $50 |
| Mechanical attach hardware + bag port fittings | $10 |
| **Total** | **~$575** |

At a Founder Edition target around $1,500 the margin structure mirrors the main appliance's at lower absolute numbers. The bundled Lillium passes through at near-zero margin to us — we're not in the business of making money on someone else's appliance, we're in the business of removing a sourcing step for the customer.

## What it would take to ship the Lite Edition

The Lite Edition is approximately the prototype that already exists on the founder's counter, with a transparent printed cabinet around it and a tightened-up firmware build. The hard subsystems of the main appliance (carbonator vessel fabrication, hydro-test, refrigerant-loop teardown and recharge, foam-pour cold-core assembly, hydrocarbon-refrigerant safety architecture) are absent. The remaining work: the transparent enclosure, the faucet-inlet stub that accepts a Lillium output line, the bag cradle and bag-port fitting, install documentation for the Lillium pairing and the priming procedure, and per-unit [assembly](/pie-in-the-sky/lite/assembly.md).

## Minimum set of printed parts

A walk through [`hardware/printed-parts/`](/hardware/printed-parts/) filtered for what the Lite Edition needs — what the existing prototype already uses, plus what would be added for the transparent cabinet. The cold-core stack (foam shells, foam caps, copper plugs, coil mandrel, PRV shroud) is absent because the Lite Edition has no carbonator and no refrigeration.

For the prototype's last-known state before its narrative doc was retired, see git tags `prototype-doc-last-known` and `prototype-bom-last-known`.

Reservoirs are off-the-shelf collapsible bags, not printed (see "What the Lite Edition is"). The Kitchen Edition's printed reservoir stack — `reservoir-*.step`, the PTFE-membrane caps in [`vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md), the reed column in [`level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) — is not part of the Lite. The only printed part on the bag side is the cradle, under "Not designed" below.

### Existing iteration in flight

**Faucet stack** — [`hardware/printed-parts/faucet/`](/hardware/printed-parts/faucet/)

- [`touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) — PET-CF, 3-piece split shell, 0.6 mm DUROZZLE TC nozzle, same-material supports. Joint-clearance arc closed at attempt 14 ("Pretty good. Or good enough at least for now" per [`print-log.md`](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md)); current iteration is on tube-bore clearances and scarf-seam handling, both in recording-only posture. Assembly procedure in [`ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md).
- [`touch-flo-mounting-plate/`](/hardware/printed-parts/faucet/touch-flo-mounting-plate/) — paired with shell on the current 3-piece plate.
- [`touch-flo-mounting-gasket/`](/hardware/printed-parts/faucet/touch-flo-mounting-gasket/) — TPU gasket between mounting plate and countertop.
- [`touch-flo-tpu-o-ring/`](/hardware/printed-parts/faucet/touch-flo-tpu-o-ring/) — TPU o-ring at the body-to-shell interface.

### Exists, no documented iteration

**Flavor pump stack** — [`hardware/printed-parts/flavor/`](/hardware/printed-parts/flavor/)

- [`pump-case/`](/hardware/printed-parts/flavor/pump-case/) — base + cap STEPs generated. No print-log or README on file.
- [`peristaltic-tube/`](/hardware/printed-parts/flavor/peristaltic-tube/) — STEP generated. No print-log or README.
- [`cap-sense-sleeve/`](/hardware/printed-parts/flavor/cap-sense-sleeve/) — +Y and -Y STEPs generated. No print-log or README.
- [`buckle/`](/hardware/printed-parts/flavor/buckle/) — only `discussion.md` on file; no STEP, no cadquery. Not designed yet.

### Added scope for the Lite Edition — what is now designed, what is not

The existing prototype lives ad-hoc on the counter; the Lite Edition wraps it in a consumer form. The pieces the prototype does without:

- **Enclosure shell — designed.** [`enclosure/`](/pie-in-the-sky/lite/enclosure/) — the same split-half (front + back) cross-pinned shell as the Kitchen edition, sized live to the contents, with the 45° display facet at the top-front-left and a drop-in hopper opening to its right. The reservoir-pockets box is the heavy back-bottom anchor (doorway facing the cabinet back), where the Kitchen has its cold core. The Kitchen's `back-panel/` / `front-panel/` / `nameplate/` subfolders are sized for the integrated appliance (side-to-side condenser airflow, rear-panel CO2 / water inlets, compressor compartment) — none of that applies, so the Lite has no equivalents. Still open within the shell: mounting feet, a pump-access provision, and the rear faucet-inlet stub for the Lillium hose.
- **Bag cradle — designed.** [`reservoir-pockets/`](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/) — two pockets holding each bag spout-down, with a rod-hang channel and low ⌀6.5 mm spout exits.
- **Hopper — designed.** [`funnel/`](/pie-in-the-sky/lite/printed-parts/funnel/) — a drop-in pour-through funnel whose collar is derived from the enclosure's hopper opening (the Kitchen `zone-c` idiom), seated right of the display.
- **Electronics-shelf housing — not designed.** Cold-core has an electronics shelf at the top-back. Lite-side, the electronics take a smaller home — represented as a placeholder box in the dead +X channel beside the reservoir until a discrete printed part is drawn.

### Open questions that surface from this walk

- What fitting mates to the Platypus bag's port, and does one low port serve both fill (from the hopper through the manifold) and draw (to the pump), or does the bag need a second port?
- Is `flavor/buckle` load-bearing for the prototype, or just an idea captured in `discussion.md`?
- Are `flavor/pump-case` + `peristaltic-tube` + `cap-sense-sleeve` the same iteration the prototype is using, or is the prototype on earlier / different versions?
- Is `touch-flo-shell` at attempt 14/15 the version that would ship, or is more iteration expected — the scarf-seam recording-only posture suggests Derek is still tuning.

## Form factor

Under-counter, in the kitchen cabinet beneath the sink, alongside the customer's Lillium (also a plumbed under-sink appliance). The Lite Edition's enclosure is smaller than the main appliance's because it contains no cold core and no refrigeration; it could fit a corner of the cabinet without disrupting other under-sink contents.
