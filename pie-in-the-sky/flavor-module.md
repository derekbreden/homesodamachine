# Flavor Module — an external satellite unit

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

A second, smaller appliance that sits alongside the main Kitchen Edition or Shop Edition and adds **four more flavors through its own dedicated faucet**. Self-contained refrigeration, self-contained carbonator, self-contained flavor reservoirs and pumps. Shares only the customer's CO2 tank and water supply via simple tee fittings.

The two units operate as a pair but neither depends on the other for runtime — each one's faucet pours from its own internal cold core. The flavor module is not a "remote reservoir bank" that pipes chilled syrup back into the main unit (that path runs a chilled CO2-pressurized line across the kitchen, picks up heat, demands a second clean cycle architecture, and bottlenecks on the main unit's manifold). It is a **second full machine** with four reservoirs and four flavor lines instead of two, mounted to the same plumbing trunk.

This is the optimistic version of the idea.

## Why this is genuinely good

**The architecture already exists.** Almost everything in the Kitchen / Shop Edition scales to four flavors without redesign:

- Cold core, foam shells, carbonator vessel, refrigeration loop, electronics shelf, power topology — all unchanged. The flavor module *is* a Kitchen-Edition cold core.
- The valve manifold (`hardware/topology/fluid-topology.md`) was sized for two flavors but the underlying truth-table pattern (source-selection valves + return-or-out routing) generalizes to N flavors at the cost of more Beduan solenoids and more Kamoer peristaltic pump cartridges. Going from 2 to 4 is two more pumps and ~6 more valves on the same MCP23017 expander, well within its 16-channel budget.
- The flavor hopper architecture (top-of-enclosure funnel with solenoid-selected route to the right reservoir) handles four flavors the same way it handles two — wider funnel or a 4-way diverter, but no new mechanism.
- Faucet, air switch, display — same parts, same firmware, just configured for four flavors instead of two.

In other words: the flavor module is a Kitchen Edition with twice the flavor count and no countertop faucet. Most of the BOM and most of the assembly procedure transfer directly.

**It solves the genuine "only two flavors" complaint without compromising the main unit.** The two-flavor limit on the main appliance is a real constraint for households that drink Diet Mountain Dew + Diet Pepsi + Pepsi Zero Sugar + a rotating zero-sugar sparkling flavor + the occasional sugar Mountain Dew for guests. The main unit could be widened to 3 or 4 flavors, but it would force a bigger enclosure, more solenoids, a more complex manifold, and a redesigned hopper — pushing complexity into the unit that's already the hard part of the build. A satellite is the cleaner answer: it leaves the main unit exactly as designed, and households who want six flavors just buy both.

**Independent runtime is a feature, not a workaround.** Each unit has its own carbonator, its own refrigeration cycle, its own clean schedule, its own failure domain. If the main unit's compressor fails on a Saturday, the flavor module still pours. The customer's iOS app already individually addresses each appliance over the same Wi-Fi — adding a second device on the same account is straightforward, and the per-unit serial-plus-QR pattern from the Founder Edition nameplate spec scales naturally.

**Plumbing is trivial at install time.** One brass tee on the CO2 line out of the customer's regulator, one tee on the cold water supply. Both units plug into separate outlets. No proprietary inter-unit harness, no chilled syrup runs across the kitchen, no shared firmware contract between the two — they're independent appliances on a shared utility trunk, the same way a dishwasher and an ice maker share the under-sink water tee.

**It opens the household-as-a-bar story.** Once a kitchen has two units side-by-side dispensing six flavors total from two faucets, the product stops looking like "a soda machine" and starts looking like "a beverage installation." That's a different conversation with a different visual surface. For Shop Edition buyers especially — the garage / man-cave audience — adding a second unit to the bar is exactly the move they were going to make anyway. The flavor module is just permission to make it.

## Form factor

Two reasonable variants, both fed by the same architecture:

**Companion under-counter unit.** Same enclosure size, same install pattern, mounted in the adjacent cabinet bay or sharing the under-sink bay with the main unit if there's room. Its own faucet penetrates the countertop next to the main unit's faucet — two faucets at the back of the sink, one with the Kitchen Edition's 2-flavor switch, one with the module's 4-flavor switch. From a guest's vantage this reads as "they have an actual soda bar."

**Companion countertop unit.** Same enclosure size but Shop-Edition-style front face: forward-facing spout, proximity arm, four illuminated flavor-select buttons, drain sump. Sits on a bar shelf next to a Shop Edition main unit. Two front faces of bar equipment, six flavors total. This is the "look at this thing in my garage" version cranked to the appropriate maximum.

Either variant uses the same internal architecture; only the front face and the faucet-or-spout treatment differ. Same fork as Kitchen vs Shop on the main unit.

## Plumbing pattern

```
                       customer's
                       cold water supply
                              │
                              ▼
                        ┌─────┴─────┐
                        │   tee     │
                        └─┬───────┬─┘
                          │       │
                          ▼       ▼
                       MAIN     MODULE

                      customer's
                      CO2 tank + primary regulator
                              │
                              ▼
                        ┌─────┴─────┐
                        │   tee     │
                        └─┬───────┬─┘
                          │       │
                          ▼       ▼
                       MAIN     MODULE
```

Both units carry their own in-appliance WR1110 secondary regulator (each one locks its vessel pressure at 90 PSI independent of the primary setpoint), their own Multiplex 19-0897 backflow preventer on the water inlet (each one is a separate beverage-dispensing-equipment installation per ASSE 1022), their own check valves, their own everything. The shared parts are exactly two: one CO2 tee and one water tee. Neither tee is in either appliance — they live in the customer's plumbing.

CO2 consumption roughly doubles, which is a feature (still months between refills, just less astronomically long). One 5 lb tank still services both units for a long time.

## Customer story

You start with the Kitchen Edition (or Shop Edition). It pours Diet Mountain Dew and Diet Pepsi, which is most of what your household drinks. A year in, you want sparkling water on a third tap because the kids drink LaCroix and you're back to hauling cans for them. You order the flavor module. It arrives, you tee two fittings, plug it in, prime four reservoirs (LaCroix Pamplemousse + LaCroix Cherry Lime + Diet Mountain Dew Code Red + a sugar Pepsi for guests), and now your kitchen has six taps total. The hatred of the cans is now comprehensively answered.

That's an extremely strong upsell path for an existing owner. They're not buying a feature; they're buying *more of the same thing they already love*. The conversion narrative writes itself.

## What's worth doing next on this

The module isn't load-bearing on shipping the first 10 units, and it shouldn't be — the Kitchen Edition is the product. But the design choices made in the main unit's first 10 builds should be made with one eye on the module:

1. **Keep the valve manifold's expansion path obvious.** The current `fluid-topology` is sized for two flavors. Make sure the firmware abstraction over the manifold treats N=2 as a special case of N=N, so that the module can ship as a firmware-flag variant rather than a fork.
2. **Keep the iOS app's device model multi-unit-aware.** If the app assumes one appliance per account, fixing that later is a database migration; doing it from day one is free.
3. **Don't make the Kitchen Edition's BOM dependent on the module ever existing.** If the module ships, great; if it never does, the main unit is still the main unit. No coupling, no shared firmware contract that constrains the main unit's evolution, no "module-ready" wiring that adds cost to every Kitchen Edition.

That third point is the discipline: the flavor module gets to be the cleanest version of itself precisely because it doesn't constrain the main unit while it waits.
