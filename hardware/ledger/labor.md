# Labor — One Consumer Unit

Attended human minutes to build one finished appliance, grouped into the ten kinds of work the build asks for. Each wiring bench row is one finished harness, including its full sequence of hand operations. Companion to [bom.md](/hardware/ledger/bom.md): that file is what a unit costs in parts, this one is what it costs in time.

**Attended, not elapsed.** A row counts only the minutes a person is *on* the operation. The 30-minute hydro hold, the 15-minute vacuum hold, the silicone cure, the 8-hour burn-in, and the [185.2](LAB_PRINT_H) estimated printer-hours are equipment time. What is counted here is setup, the hands-on pass, the check, the tear-down, and the walk to the next stage. The hours a *machine* is busy are their own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which is what turnaround and throughput are read off.

**Deliberately the ideal, not Derek's actual time.** Derek builds each unit himself, one at a time. These estimates assume practiced hands, the fixture built and the jig loaded, and per-batch setup shared across [10](BATCH_SIZE) units, the quantity the ledger buys in: endcap plates 20 at a time (two per carbonator), tube 10 at a time, PCBAs at the qty-10 price. An operation whose setup is per-batch rather than per-unit carries a tenth of that setup here. Costs, and the price set from them, rest on this ideal picture of labor; paying for Derek's actual hours would take a price of $8,000 or more, which is not the plan.

**The maturity benchmark is the 25th unit using the documented method.** A practiced assembler has the maps, material locations, terminal choices and tools ready. Development, lookup and learning are outside the recurring labor estimate. A complete harness remains one bench job, made start to finish by one person; repeat volume does not assume separate stations for mass crimping.

**The pace is a practiced one.** Three minutes an operation is a relaxed rate for repetitive work once it is practiced, so an operation of that shape gets 5 minutes, not 10. A machine screw is seven seconds with a driver; a heat-set insert is fourteen seconds with a hot tip and a jig. Where a row is longer than that it is because the work does not repeat: a weld that has to be right the first time, a hand tap into 1/4" stainless, a foam pour with a cream time.

**Costed at [$100](LABOR_RATE) per hour of attended time.** That rate is what the site's `/cost` page prices the labor column with; it reads the number from the marker above, so this file sets it.

**Every estimate lands on one of these increments,** and nothing in between:

`5m · 10m · 15m · 20m · 25m · 30m · 45m · 1h · 1h15 · 1h30 · 1h45 · 2h · 2h30 · 3h · 4h · 6h`

These are the steps a person actually estimates in. "40 minutes" claims a precision no one has for work they have not timed; it means 30 or it means 45, and saying which is the more useful answer. `_labor_totals.py --check` rejects a row that lands anywhere else, so the convention holds as rows get added. Subtotals and the grand total are plain sums of those estimates and land where the arithmetic puts them.

The linked fabrication procedures define each operation. [Letter shop guides](/hardware/assembly/guides/README.md) illustrate drilling and cutting, molds, refrigeration and the carbonator weld operation.

## 1. Machining

Drilling, tapping, chamfering, cutting and deburring for the carbonator and its water-inlet jet. The 316L plate work is the slowest metal in the build: four 1/4"-18 NPT ports hand-tapped into 1/4" plate, and a blind register hole in the carbonator's pressure boundary that must not break through.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Chamfer the four port holes; break both plate edges | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Countersink inside faces, burr-break only on the outside — that edge is the fillet root | 5 |
| Tap four 1/4"-18 NPT ports in 1/4" 316L | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Hand tap + spring guide + cutting fluid | 20 |
| Drill the blind rod register, both plates | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Drill press at ~740 RPM, depth stop at 0.10", proved on a scrap disc first | 5 |
| Cut three level rods to length, deburr | [reservoir rods](/hardware/assembly/handwork.md#cut--seat-the-reservoir-float-rods), [pressure-vessel](/hardware/assembly/pressure-vessel.md) | 1/8" 316L: one at 131.1 mm and two at 176.5 mm | 5 |
| Deburr the tube; Scotch-Brite the two fillet bands | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | ~30 s per joint of prep is what the weld needs; the rest is handling | 10 |
| Drill the jet handling blank, cut the cap, deburr and clean | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured attended-time estimate; batch setup amortized, drilling fixture already made | 5 |
| **Machining** | | | **[50](LAB_SEC1)** |

## 2. Welding & brazing

Four laser operations serve the carbonator: the float-rod tack, two closure welds and the water-inlet jet cap weld. The refrigerant loop has one brazed tie-in. Argon shielding and the jet's internal purge are included in their attended setup allowances.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Tack the float rod into the bottom-plate register | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Same welding session as the plate fillets — heat the welder once | 5 |
| Weld the bottom-plate corner fillet under argon | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | ~15" of recessed corner fillet, handheld X1 Pro, keep heat moving | 10 |
| Close the carbonator — top-plate fillet, float captive | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Same joint, one shot, nothing comes back out after this | 10 |
| Fixture, purge and weld the water-inlet jet cap | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured estimate for a qualified, repeatable process; destructive development coupons are excluded | 10 |
| Cut the loop, tie in the suction line, pinch-swage the capillary | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Brazing the harvested compressor path with argon flowing through the tube | 25 |
| **Welding & brazing** | | | **[60](LAB_SEC2)** |

## 3. Pressure, leak & flow checks

The carbonator receives dye penetrant and hydro before foaming, the refrigerant loop a vacuum-decay check before charge, and the CO2 path a witnessed hold at measured operating pressure. The jet elbow receives its own production inspection and timed flow check. The holds themselves are unattended — plugging, filling, pumping, reading and draining are not. These checks do not replace the weld-process qualification.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Dye-penetrant both closure welds — clean, dwell, develop, read | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Solvent-removable visible dye on bare, dry welds | 10 |
| Hydro test to 180 PSI — plug, fill, pump, drain | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | 1.44× the SV-125's set pressure; the 30-minute hold is not counted | 15 |
| Citric passivation — load the tub, rinse, dry | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Clean carbonator and jet elbow; batch soak in the shared tub, 30–60 minute soak not counted | 5 |
| Inspect the jet elbow, flow-check and record the result | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured estimate; accepted geometry and flow band must be established by qualification | 5 |
| Pull vacuum to 500 µm, valve off, read the rise | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Two 15-minute holds, neither counted | 10 |
| Mass-metered recharge, run-up and leak check | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Scale-metered charge, then find the weep if there is one | 10 |
| First CO2 fill at the selected setting; measure pressure and witness every joint dry | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | Record actual carbonator pressure; the nominal regulator setting is not a reading | 5 |
| **Pressure, leak & flow checks** | | | **[60](LAB_SEC3)** |

## 4. Silicone casting

One cast part per unit: the funnel, [219.4](FUNNEL_VOLUME_ML) mL of finished CAD volume, estimated at [248](FUNNEL_FINISHED_G) g using an assumed [1.13](FUNNEL_DENSITY_G_ML) g/mL density. The batch allocation is [273](FUNNEL_MIXED_G) g of 1:1 platinum silicone, including a provisional [10%](FUNNEL_MIX_ALLOWANCE) mixing and port-flash allowance. Two printed mold shells and a straight 6 × 25 mm steel rod form the complete funnel and its cylindrical bore for the drain tube. Room-temperature cure and the post-cure bake are equipment time; the attended work is preparation, pouring, release and flash trim. Casting yield, finishing compatibility and these handwork allowances remain unmeasured.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Release both forming faces and the steel rod; drop it in the lower seat and clamp the shells | — | Compatible finishing/release stack, rod resting on the lower floor, bare mold lands closed; [mold procedure](/hardware/printed-parts/zone-c/funnel-mold/README.md) | 5 |
| Weigh, pigment, mix and vacuum-degas [273](FUNNEL_MIXED_G) g of silicone | — | 1:1 by weight, ≤2 % black pigment, chamber until it falls back | 10 |
| Pour the open cavity, lower the core, vacuum and top up, rack to cure | — | The cure and the vacuum hold are unattended | 5 |
| Demold, pull the straight rod and trim outlet, port and vent flash | — | Peel the brim first to admit air; pull the rod through the bowl, then trim flash flush | 5 |
| Post-cure bake — load and unload the oven | — | Bake is unattended | 5 |
| Maintain the shell forming faces and clean the steel rod | — | Amortized across casting pulls; preserve the shell finish and smooth cylindrical rod | 5 |
| **Silicone casting** | | | **[35](LAB_SEC4)** |

## 5. Foam pouring

Three pour-in-place foam operations: both cold-core caps, the body foam around the carbonator, and the insulating sleeve on the soda umbilical tube. Same motion as the silicone — mix, pour, walk away — but with a shorter cream time and a much bigger mess when a rim overflows.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Mix and pour both cap foams, lids bolted down as the clamp | [cold-core](/hardware/assembly/cold-core.md) | The cap lids are the pour clamp and stay in the product | 10 |
| Mix and pour the body foam around the carbonator | [cold-core](/hardware/assembly/cold-core.md) | Around seven penetrations and the PRV shroud's protected air cavity | 15 |
| Foam-sleeve the carbonated-water umbilical tube | [faucet-and-umbilical](/hardware/assembly/faucet-and-umbilical.md) | Only the carbonated line is insulated | 5 |
| Trim the overflow; clean rims, cups and sticks | [cold-core](/hardware/assembly/cold-core.md) | Foam does not wait for you to find a scraper | 5 |
| **Foam pouring** | | | **[35](LAB_SEC5)** |

## 6. Wiring

**One complete bench job per harness, at unit 25.** One practiced person cuts,
marks, strips, terminates, dresses, tests and labels each finished piece before
starting another. The map, cut lengths, tools and materials are ready; shared
setup is amortized, with no separate mass-crimping station. These are
theoretical attended-time estimates, not timed production readings. Development,
lookup, learning and final cabinet fitting are outside the bench cycles.
J13 is finished with front-top loose on the bench: its free cable end passes
through the empty bulkhead bore before the pogo tails are soldered. Connector
mounting and final routing retain their separate assembly allowances.

The [J2](https://homesodamachine.com/cost#j2-harness) and
[J13 fixed-half](https://homesodamachine.com/cost#j13-harness) visual guides
are the corresponding rows below and are included in the unit total. J2's
10-minute estimate allows about 5–6 minutes for its 18 crimps and 4–5 minutes
for preparation, dressing, Wago assembly, continuity and labeling; allow up to
15 minutes for planning. J13's five minutes covers four JST crimps, four
individually insulated solder tails and its end-to-end check; allow up to ten.
The other estimates use the same practiced method: five minutes for a simple
four-conductor cable, ten for a smaller fan-out, and fifteen for the larger
valve or reed assembly. All remain unmeasured.

### Finished bench harnesses

Twelve pieces: ten JST-ended looms, the separate cartridge contact cable and
the ferruled J10 supply lead. Reed soldering and insulation belong to J6/J7;
mounting the finished columns belongs to Assembly. The separate faucet
umbilical is included in that subassembly's Assembly allowance. J8 is the
unused I2C expansion header, with no production loom in the cable schedule;
the reserved J4 IO23/IO27 positions are also unpopulated. Neither adds a
moisture-sensor harness.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| J1 · Manifold A → eight valves | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Nine JST contacts; eight switched returns, eight positive branches and the 221-420 COM fan-out; terminate, dress and ring out the whole assembly | 15 |
| J2 · Manifold B → V-I, V-J, fan and V-K | [J2 bench guide](/hardware/assembly/harnesses/j2.md) | Five JST contacts in the 6P housing, four positive branches, five ferrules, eight far-end terminations and the 221-415; complete dressed and tested harness | 10 |
| J3 · Faucet → rear-wall keystone | [cable-assemblies](/hardware/assembly/cable-assemblies.md#faucet-display-sig-6) | Four JST contacts, four 110 IDC landings, dressing, label and end-to-end check; inboard cable only | 5 |
| J4 · Sensors → temperature bus and flow meter | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Five populated JST positions, temperature-bus connections, flow-meter branch and shared-ground 221-415; terminate, dress and test; IO23/IO27 empty | 10 |
| J5 · Relays → both relay modules | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, relay-end ferrules and shared V5/GND branches, dressing, label and test | 5 |
| J6 · Reeds A → four reservoir reeds | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Five JST contacts, four reed pairs soldered and insulated, shared-ground 221-415, lacing and magnet/continuity check; excludes installing the finished column | 10 |
| J7 · Reeds B → four reservoir and two carbonator reeds | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Seven JST contacts, six reed pairs soldered and insulated, shared-ground 221-420, dressing and magnet/continuity check; excludes mounting reeds or column | 15 |
| J9 · Display → enclosure LCD | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, four ferruled display-terminal ends, dressing, label and test | 5 |
| J11 · Gas → MQ-6 sensor | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, four sensor-end connections, dressing, label and test | 5 |
| J13 · Pumps → fixed pogo half | [J13 bench guide](/hardware/assembly/harnesses/j13.md) | With front-top loose and ready: 350 mm 4P ribbon, four JST contacts, free end through the empty bore before four individually heat-shrunk male-half solder tails; identify attracting orientation, label and test; excludes bulkhead mounting | 5 |
| Pump cartridge · pogo half → both motors | [cable-assemblies](/hardware/assembly/cable-assemblies.md#contact-pair--dc-5) | Four 100 mm leads, four individually heat-shrunk female-half solder tails and four motor Fastons; identify attracting orientation and test; excludes clamp mounting | 5 |
| J10 · 12 V distribution → board input | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Two 16 AWG leads, four ferrules, label and test; excludes landing the finished lead in the cabinet | 5 |

### Installation and AC checks

These operations begin with the finished bench harnesses. Their recurring
work is cabinet power distribution, mounting connections, routing and installed
checks; no JST crimping, reed soldering or pogo-tail fabrication is counted again.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| AC distribution + ground bus on the shelf; land the pigtails |  | Ferrules into 221s, rings to the ground stud | 10 |
| DC distribution + 12 V branches; land J10 and RELAYS J5 |  | Cabinet distribution connections and completed loom landings; J10/J5 cable fabrication is counted above | 5 |
| Chassis-ground bonds; C14 to compressor and PSU | [wiring](/hardware/assembly/wiring.md) | | 10 |
| Dielectric + continuity check, AC side | [wiring](/hardware/assembly/wiring.md) | Pre-power isolation proof — nothing gets energized before it passes | 10 |
| Cabinet 12 V runs and signal looms | [wiring](/hardware/assembly/wiring.md) | Land the labeled 7P J4/J7 housings at their own wafers. Route the finished fixed cable along the ridge clip and +X wall, and the cartridge leads in its grooves; the bulkhead bore was threaded before soldering. With AC unplugged, check all four channels point to point and for neighbor isolation with the cartridge out and seated | 10 |
| Bundle, route, strain-relieve | [wiring](/hardware/assembly/wiring.md) | | 5 |
| **Wiring** | | | **[145](LAB_SEC6)** |

## 7. Plumbing

Every wetted and gas joint in the unit: the carbonator's four elbow stacks, the seven cold-core penetrations, the CO2 and water paths from the +Y wall of back-top to the core, the flavor manifold, and the risers to the umbilical bulkheads. Roughly sixteen taped NPT joints and a larger count of push-to-connect. PTC is fast; NPT into stainless is not.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Install four elbow stacks, qualified jet elbow and PRV shroud | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | One outside elbow per port; recurring jet work is counted in §§1–3 | 15 |
| Route the seven cold-core penetrations; stack the copper plugs | [cold-core](/hardware/assembly/cold-core.md) | Done before the body foam locks them in | 10 |
| CO2 path — +Y wall of back-top to cold core | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | | 10 |
| Water path — +Y wall of back-top to cold core | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | Filter, backflow, pump, top-plate port | 10 |
| Flavor manifold — fixed valves and tees, permanent receivers, prepared pumps and channels | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | [10](SOLENOIDS) fixed valves total. Install four TPU receivers, flat keepers and the rear support; connect the straight permanent tails and tie the fixed tees into their saddles. Install aft valves from the open underside, then fore valves and stationary links. Fit the prepared pump stems into their cradle captures. This assembly time is an unmeasured allowance | 15 |
| Risers to the umbilical bulkheads | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | | 5 |
| Witness and tidy every joint | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | The pass that makes the next leak someone else's fault | 5 |
| **Plumbing** | | | **[70](LAB_SEC7)** |

## 8. Assembly

Everything that is putting parts together with fasteners and hands. The print model allocates [7.386](LAB_PRINT_KG) kg of filament and [185.2](LAB_PRINT_H) printer-hours per unit, including the three ASA Aero floats and the four-receiver TPU plate ([machine-time.md](/hardware/ledger/machine-time.md)). The attended share is plate changes, spool swaps, part removal, support cleanup and the three RC62 insertions at their print pauses. That tending allowance is provisional. Assembly includes the [76](TOTAL_INSERTS) M3/M5 heat-set inserts and [76](TOTAL_SCREWS) matching screws, plus four M1.4 inserts and four M1.4 × 8 screws mounting the pogo halves.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Tend the printers — plate changes, spool swaps, part removal, support cleanup and float-magnet insertion | — | [7.386](LAB_PRINT_KG) kg over [185.2](LAB_PRINT_H) estimated printer-hours; includes three RC62 insertion/resume passes. Provisional attended allowance; the v2 float slice and elapsed manual pauses are unmeasured | 25 |
| Press the [76](TOTAL_INSERTS) M3/M5 heat-set inserts and four M1.4 pogo inserts | [cold-core](/hardware/assembly/cold-core.md), [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | Shell faces, cap columns, reservoir caps, touch-flo pods, wall bosses, condenser fingers, six pump-dock lock hosts, [4](SEAM_INSERTS) enclosure Y-seam anchors and floor posts. FX-888D + T18 tips for [68](TOTAL_M3_INSERTS) M3 and [8](TOTAL_M5_INSERTS) M5; use an on-hand VECO-T T18 I/LB fine tip with the recessed-seat cold reach/depth check for the four M1.4 × 4 × Ø2.3 pogo inserts ([enclosure assembly](/hardware/assembly/enclosure-mechanical.md)) | 10 |
| Drive the [76](TOTAL_SCREWS) M3/M5 build screws and four M1.4 × 8 pogo screws | — | [20](FOAM_SCREWS) foam-cap, [4](PUMP_MOUNT_SCREWS) water-pump, [12](RES_SCREWS) reservoir-cap, [3](TOUCHFLO_SCREWS) faucet base, [17](SHELF_SCREWS) shelf, [2](COND_SCREWS) condenser, [0](DISPLAY_COVER_SCREWS) display plate, [0](NAMEPLATE_SCREWS) nameplate, [4](SEAM_RODS) M5 enclosure Y-seam screws, two upward through the handholds and two downward through the roof, each with one flat washer, [4](FLOOR_SCREWS) floor, [2](PUMP_CAP_SCREWS) pump clamp, [2](C14_SCREWS) C14 inlet and [6](DOCK_LOCKS) permanent receiver keeper/rear-support locks, each with a Ø7 × 0.5 mm DIN 125A washer; two M1.4 × 8 screws per pogo half, seated with a hand-operated 1.3 mm hex driver | 5 |
| Wind the evaporator coil on the mandrel; transfer it, set the band | [cold-core](/hardware/assembly/cold-core.md) | | 10 |
| Dress the carbonator wall — reeds, probe, foil; bond the coil probe | [cold-core](/hardware/assembly/cold-core.md) | | 10 |
| Fit the finished reed columns; seat rods and floats; close the reservoirs | [cold-core](/hardware/assembly/cold-core.md) | Two reservoirs, gaskets, caps, vent filters; J6/J7 soldering and insulation are counted in Wiring | 15 |
| Lower the carbonator; seat the reservoirs in their pockets | [cold-core](/hardware/assembly/cold-core.md) | | 5 |
| Press the wall's Wago wells; mount PSU, relays, PCBA |  | Onto `enclosure-back-top`'s [17](SHELF_INSERTS) +X wall bosses | 5 |
| Stage the printed enclosure and dock parts and the +Y wall's seven bodies; bolt the compressor down to the slab | [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | Four quadrants, cartridge, pump clamp, four TPU receivers, four keepers and one rear support; rear-wall set includes the RJ11 keystone. Four floor posts, one M5 and a fender washer each, snugged onto the post crowns | 10 |
| Seat the cold core; condenser, electronics bay, close the box, ASSE drip pan | [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | | 10 |
| Cut, route and sleeve the umbilical; bag it with the under-counter plate | [faucet-and-umbilical](/hardware/assembly/faucet-and-umbilical.md) | Three LLDPE tubes, braid, the bag | 10 |
| Assemble the faucet — two-piece shell, display cover, plate, gasket and o-ring | — | Route tubes and ribbon before closing the plate; PET-GF prints, TPU seals | 5 |
| **Assembly** | | | **[120](LAB_SEC8)** |

## 9. Power-on & testing

The unit is fully built. Now it gets plugged in for the first time: load the firmware, walk every sensor and every actuator, dispense from it, and leave it running overnight. The 8-hour burn-in is not counted — firmware logs it and Derek checks in three times.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Check the wiring is right; first DC power-on | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | | 5 |
| Load the firmware onto the three ESP32s | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | Base, enclosure display, faucet display | 5 |
| Read every sensor and confirm it reports | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | Both DS18x20s, flow, moisture, reeds, gas | 10 |
| Fire every valve and pump; run the compressor and set its setpoints | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | | 10 |
| First dispenses — water, flavor A, flavor B | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | | 5 |
| Clean cycle, air purge, level-sensing transitions | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | | 10 |
| Burn-in check-ins at 1 h, 4 h and 8 h | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | The 8-hour window itself is not counted | 10 |
| **Power-on & testing** | | | **[55](LAB_SEC9)** |

## 10. Finishing & packing

The unit passed. Empty it, clean it up, name it, box it.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Drain and air-purge for transit | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | Nothing wet ships | 5 |
| Wipe down + final inspection | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 |
| Scan the nameplate QR and snap its horizontal wings into the back-top receiver | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | Match the four-digit unit number to the order and per-unit archive; confirm full seating and retention per [finish procedure](/hardware/assembly/finish-pack-ship.md#3-apply-the-per-unit-nameplate) | 5 |
| Cap the inlets + photograph | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 |
| Make up the customer's runs; pack the install kit, the cold kit and the carton | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 10 |
| Weigh, label, hand off | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 |
| **Finishing & packing** | | | **[35](LAB_SEC10)** |

## Totals

| Section | Time | At [$100](LABOR_RATE)/h |
|---|---:|---:|
| 1. Machining | [50 m](LAB_HM1) | [$83.33](LAB_USD1) |
| 2. Welding & brazing | [1 h](LAB_HM2) | [$100.00](LAB_USD2) |
| 3. Pressure, leak & flow checks | [1 h](LAB_HM3) | [$100.00](LAB_USD3) |
| 4. Silicone casting | [35 m](LAB_HM4) | [$58.33](LAB_USD4) |
| 5. Foam pouring | [35 m](LAB_HM5) | [$58.33](LAB_USD5) |
| 6. Wiring | [2 h 25 m](LAB_HM6) | [$241.67](LAB_USD6) |
| 7. Plumbing | [1 h 10 m](LAB_HM7) | [$116.67](LAB_USD7) |
| 8. Assembly | [2 h](LAB_HM8) | [$200.00](LAB_USD8) |
| 9. Power-on & testing | [55 m](LAB_HM9) | [$91.67](LAB_USD9) |
| 10. Finishing & packing | [35 m](LAB_HM10) | [$58.33](LAB_USD10) |
| **Per-unit total** | **[11 h 5 m](LAB_HM)** | **[$1,108.33](LAB_USD)** |

The target is 10 hours attended per unit. The current estimate is [11 h 5 m](LAB_HM), including 20 minutes of unmeasured recurring jet work. The largest attended-time categories are:

- **Wiring** ([2 h 25 m](LAB_HM6), the largest category) — 95 minutes for twelve finished bench harnesses and 50 minutes for installation and AC checks. Ready maps, a cut list and staged crimping and soldering tools support the practiced unit-25 estimates.
- **Assembly** ([2 h](LAB_HM8)) — includes 25 minutes of provisional printer tending. Additional printer capacity changes elapsed print time; plate handling and magnet insertion still require attended work.
- **Machining** — the four hand-tapped NPT ports are the slowest five minutes each in the build, and the production tapping fixture is still an open item in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md).

## Not counted here

- **Pump-dock manufacturing allowances** — the machined PP stems and gauged DP420 magnet bedding are required production operations. Their supplier pricing and attended preparation time are unmeasured and excluded from these totals. The fixed and moving adhesive mounts each require a 24-hour unattended cure at 23 °C, in sequence; the ≥48-hour fixture window belongs in the production schedule.
- **Unattended process time** — every hour a machine is busy and nobody is on it. That is its own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which holds the print, the cures and bakes, the hydro and vacuum holds, the passivation soak, the chill-down and the burn-in, and derives turnaround and throughput from them. Nothing there is costed.
- **Shipping and receiving** — unpacking orders, kitting, inventory.
- **Design, CAD, firmware and documentation** — this file costs building a unit, not developing one.
- **Initial jet-process qualification** — destructive weld coupons, fixture development, purge qualification and setting the production flow band are development work. Recurring drilling, welding, cleaning and inspection remain in the per-unit rows above.
- **Contract labor already capitalized in dollars** — JLCPCB assembly of the main board, SendCutSend's cutting. Those arrive as parts and are priced in [bom.md](/hardware/ledger/bom.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_bom_sync.py`
- `/hardware/scripts/_labor_totals.py`
