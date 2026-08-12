# Labor — One Consumer Unit

Attended human minutes to build one finished appliance, one row per hand operation, grouped into the ten kinds of work the build asks for. Companion to [bom.md](/hardware/ledger/bom.md): that file is what a unit costs in parts, this one is what it costs in time.

**Attended, not elapsed.** A row counts only the minutes a person is *on* the operation. The 30-minute hydro hold, the 15-minute vacuum hold, the silicone cure, the 8-hour burn-in, and the ~100 printer-hours are all real and none of them are in this file — the operator is elsewhere. What is counted is setup, the hands-on pass, the check, the tear-down, and the walk to the next stage. The hours a *machine* is busy are their own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which is what turnaround and throughput are read off.

**An operator who has done the operation before,** with the fixture built, the jig loaded, and a batch of [10](BATCH_SIZE) units in flight, so setup amortizes. That batch is not a hypothetical: it is the size the ledger already buys in — endcap plates 20 at a time (two per vessel), tube 10 at a time, PCBAs at the qty-10 price. An operation whose setup is per-batch rather than per-unit carries a tenth of that setup here.

**The pace is a line's, not a bench's.** Twenty units an hour — three minutes an operation — is a relaxed rate for the repetitive work, so an operation of that shape gets 5 minutes, not 10. A machine screw is seven seconds with a driver; a heat-set insert is fourteen seconds with a hot tip and a jig. Where a row is longer than that it is because the work does not repeat: a weld that has to be right the first time, a hand tap into 1/4" stainless, a foam pour with a cream time.

**Costed at [$100](LABOR_RATE) per hour of attended time.** That rate is what [`/cost`](/cost) prices the labor column with; it reads the number from the marker above, so this file sets it.

**Every estimate lands on one of these increments,** and nothing in between:

`5m · 10m · 15m · 20m · 25m · 30m · 45m · 1h · 1h15 · 1h30 · 1h45 · 2h · 2h30 · 3h · 4h · 6h`

These are the steps a person actually estimates in. "40 minutes" claims a precision no one has for work they have not timed; it means 30 or it means 45, and saying which is the more useful answer. `_labor_totals.py --check` rejects a row that lands anywhere else, so the convention holds as rows get added. Subtotals and the grand total are plain sums of those estimates and land where the arithmetic puts them.

Cards cite [`assembly/cards/`](/hardware/assembly/cards/README.md); each card's procedure doc is the source of truth for what the operation involves.

## 1. Machining

Drilling, tapping, chamfering, cutting and deburring — all of it on the pressure vessel, all of it before a single weld. The 316L plate work is the slowest metal in the build: four 1/4"-18 NPT ports hand-tapped into 1/4" plate, and a blind register hole that is part of the 90 PSI pressure boundary and must not break through.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Chamfer the four port holes; break both plate edges | PV-01, PV-04 | Countersink inside faces, burr-break only on the outside — that edge is the fillet root | 5 |
| Tap four 1/4"-18 NPT ports in 1/4" 316L | PV-02 | Hand tap + spring guide + cutting fluid | 20 |
| Drill the blind rod register, both plates | PV-03 | Drill press at ~740 RPM, depth stop at 0.10", proved on a scrap disc first | 5 |
| Cut three level rods to length, deburr | PV-05 | 1/8" 316L to 131.1 mm | 5 |
| Deburr the tube; Scotch-Brite the two fillet bands | PV-07 | ~30 s per joint of prep is what the weld needs; the rest is handling | 10 |
| **Machining** | | | **[45](LAB_SEC1)** |

## 2. Welding & brazing

Three laser welds on the vessel and one brazed tie-in on the refrigerant loop. Both are argon-shielded, both are pressure joints.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Tack the float rod into the bottom-plate register | PV-06 | Same welding session as the plate fillets — heat the welder once | 5 |
| Weld the bottom-plate corner fillet under argon | PV-08 | ~15" of recessed corner fillet, handheld X1 Pro, keep heat moving | 10 |
| Close the vessel — top-plate fillet, float captive | PV-09 | Same joint, one shot, nothing comes back out after this | 10 |
| Cut the loop, tie in the suction line, pinch-swage the capillary | RL-03, RL-04, RL-05 | Brazing the harvested compressor path with argon flowing through the tube | 25 |
| **Welding & brazing** | | | **[50](LAB_SEC2)** |

## 3. Pressure testing & leak checks

Every pressure boundary in the unit gets proved before it is buried: the vessel by dye penetrant and hydro before it is foamed in, the refrigerant loop by vacuum decay before charge, the CO2 path by a witnessed hold at working pressure. The holds themselves are unattended — plugging, filling, pumping, reading and draining are not.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Dye-penetrant both closure welds — clean, dwell, develop, read | PV-10 | Solvent-removable visible dye on bare, dry welds | 10 |
| Hydro test to 180 PSI — plug, fill, pump, drain | PV-11 | 2× working pressure; the 30-minute hold is not counted | 15 |
| Citric passivation — load the tub, rinse, dry | PV-12 | Batch soak in the shared tub; the 30–60 minute soak is not counted | 5 |
| Pull vacuum to 500 µm, valve off, read the rise | RL-06 | Two 15-minute holds, neither counted | 10 |
| Mass-metered recharge, run-up and leak check | RL-07, RL-08 | Scale-metered charge, then find the weep if there is one | 10 |
| First CO2 fill to 90 PSI; witness every joint dry | AB-02 | The first time the assembled unit holds gas | 5 |
| **Pressure testing** | | | **[55](LAB_SEC3)** |

## 4. Silicone casting

One cast part per unit: the hopper funnel, ~78 g of 1:1 platinum silicone poured into the two-piece printed mold. The cure and the post-cure bake are oven time, not operator time. What costs is the release film, the degas, and the flash trim.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Release the cavity, release the sealed core, close and clamp | — | Ease Release 200 on both faces every pour | 5 |
| Weigh, pigment, mix and vacuum-degas 78 g of silicone | — | 1:1 by weight, ≤2 % black pigment, chamber until it falls back | 10 |
| Pour through the port, watch the five vents, rack to cure | — | Cure is unattended | 5 |
| Demold, trim the port and vent flash | — | 3 mm wall, 40A — it wants to tear if the release is thin | 5 |
| Post-cure bake — load and unload the oven | — | Bake is unattended | 5 |
| Re-sand, re-seal and re-release the core as the film wears | — | Amortized across the pulls one seal coat survives | 5 |
| **Silicone casting** | | | **[35](LAB_SEC4)** |

## 5. Foam pouring

Three pour-in-place foam operations: both cold-core caps, the body foam around the vessel, and the insulating sleeve on the carbonated-water tube in the umbilical. Same operator motion as the silicone — mix, pour, walk away — but with a shorter cream time and a much bigger mess when a rim overflows.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Mix and pour both cap foams, lids bolted down as the clamp | CC-06 | The cap lids are the pour clamp and stay in the product | 10 |
| Mix and pour the body foam around the vessel | CC-14 | Around seven penetrations and the PRV shroud's protected air cavity | 15 |
| Foam-sleeve the carbonated-water umbilical tube | FU-03 | Only the carbonated line is insulated | 5 |
| Trim the overflow; clean rims, cups and sticks | CC-06, CC-14 | Foam does not wait for you to find a scraper | 5 |
| **Foam pouring** | | | **[35](LAB_SEC5)** |

## 6. Wiring

Twelve harness assemblies off the bench plus the in-cabinet runs — roughly sixty crimped terminations per unit across JST-XH contacts, ferrules, Fastons, forks and rings. The harnesses are built a batch at a time against the schedule, not one loom at a time against the unit in front of you.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Build the twelve harness assemblies — cut, strip, crimp, sleeve, ring out | CA-01, CA-02 | ~60 terminations; batch-built against the harness schedule | 45 |
| AC distribution + ground bus on the shelf; land the pigtails | ES-02, ES-04 | Ferrules into 221s, rings to the ground stud | 10 |
| DC distribution + 12 V branches; land the RELAYS J5 loom | ES-05, ES-06 | | 5 |
| Chassis-ground bonds; C14 to compressor and PSU | WR-01, WR-02 | | 10 |
| Dielectric + continuity check, AC side | ES-07, WR-03 | Pre-power isolation proof — nothing gets energized before it passes | 10 |
| Cabinet 12 V runs and signal looms | WR-04, WR-05 | Label both 7P housings; J4 and J7 share a shell | 10 |
| Bundle, route, strain-relieve | WR-06 | | 5 |
| **Wiring** | | | **[95](LAB_SEC6)** |

## 7. Plumbing

Every wetted and gas joint in the unit: the vessel's four elbow stacks, the seven cold-core penetrations, the CO2 and water paths from rear wall to core, the flavor manifold, and the risers to the umbilical bulkheads. Roughly sixteen taped NPT joints and a larger count of push-to-connect. PTC is fast; NPT into stainless is not.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Install the four elbow stacks, sparge stone, PRV shroud subassembly | PV-13, PV-14 | Nickel-guard tape, SS into SS, every port taped twice across the build | 15 |
| Route the seven cold-core penetrations; stack the copper plugs | CC-12, CC-13 | Done before the body foam locks them in | 10 |
| CO2 path — rear wall to cold core | IP-01 | | 10 |
| Water path — rear wall to cold core | IP-02 | Filter, backflow, pump, top-plate port | 10 |
| Flavor manifold — valves, tees, pumps and channels | IP-03, IP-04 | [10](SOLENOIDS) valves butted collet to collet down the pack's limbs, two peristaltic pumps, two channels | 15 |
| Risers to the umbilical bulkheads | IP-05 | | 5 |
| Witness and tidy every joint | IP-06 | The pass that makes the next leak someone else's fault | 5 |
| **Plumbing** | | | **[70](LAB_SEC7)** |

## 8. Assembly

Everything that is putting parts together with fasteners and hands. Printer tending lives here: ~7.3 kg of filament across the twenty-one §7 lines is ~100 printer-hours per unit ([machine-time.md](/hardware/ledger/machine-time.md)), but the *attended* share is plate changes, spool swaps, part removal and support cleanup. So do the [54](TOTAL_INSERTS) heat-set inserts and the [54](TOTAL_SCREWS) machine screws that close the build — one screw per insert, the whole way through.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Tend the printers — plate changes, spool swaps, part removal, support cleanup | — | ~7.3 kg over ~100 printer-hours; only the load/unload passes are counted | 25 |
| Press the [54](TOTAL_INSERTS) heat-set inserts — shell faces, cap columns, reservoir caps, touch-flo pods, wall bosses, condenser fingers, floor posts | CC-05, ES-01, EN-01 | FX-888D + T18 tip kit, [12](FOAM_CLAMP_INSERTS) of them in the shell faces alone; [50](TOTAL_M3_INSERTS) M3 and the floor's four M5, so the tip changes once | 10 |
| Drive the [54](TOTAL_SCREWS) machine screws that close the build | — | [12](FOAM_SCREWS) foam-cap, [4](PUMP_MOUNT_SCREWS) water-pump, [12](RES_SCREWS) reservoir-cap, [3](TOUCHFLO_SCREWS) touch-flo, [17](SHELF_SCREWS) shelf, [2](COND_SCREWS) condenser, [4](FLOOR_SCREWS) floor | 5 |
| Wind the evaporator coil on the mandrel; transfer it, set the band | CC-01, CC-03 | | 10 |
| Dress the vessel wall — reeds, probe, foil; bond the coil probe | CC-02, CC-04 | | 10 |
| Build the reed columns; seat rods and floats; close the reservoirs | CC-07, CC-08, CC-09, CC-15 | Two reservoirs, gaskets, caps, vent filters | 15 |
| Lower the vessel; seat the reservoirs in their pockets | CC-10, CC-11 | | 5 |
| Press the wall's Wago wells; mount PSU, relays, PCBA | ES-01, ES-03 | Onto `enclosure-back-top`'s [17](SHELF_INSERTS) +X wall bosses | 5 |
| Stage the four printed pieces and the rear wall's bodies; bolt the compressor down to the slab | EN-01, EN-02, EN-03 | Four floor posts, one M5 and a fender washer each, snugged onto the post crowns | 10 |
| Seat the cold core; condenser, power column, close the box, drip tray | EN-04, EN-05, EN-06, EN-07, EN-08 | | 10 |
| Cut, route and sleeve the umbilical; bag the installer kit | FU-01, FU-02, FU-04, FU-05 | Three LLDPE tubes, braid, install-kit bag | 10 |
| Assemble the faucet — three-piece touch-flo shell, plate, gasket, o-ring | — | PET-CF shell, printed TPU seals | 5 |
| **Assembly** | | | **[120](LAB_SEC8)** |

## 9. Power-on & testing

The unit is fully built. Now it gets plugged in for the first time: load the firmware, walk every sensor and every actuator, dispense from it, and leave it running overnight. The 8-hour burn-in is not counted — firmware logs it and the operator checks in three times.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Check the wiring is right; first DC power-on | FC-01 | | 5 |
| Load the firmware onto the three ESP32s | FC-02 | Base, config display, faucet display | 5 |
| Read every sensor and confirm it reports | FC-03 | Both DS18x20s, flow, moisture, reeds, gas | 10 |
| Fire every valve and pump; run the compressor and set its setpoints | FC-04, FC-05 | | 10 |
| First dispenses — water, flavor A, flavor B | AB-03 | | 5 |
| Clean cycle, air purge, level-sensing transitions | AB-04, AB-05 | | 10 |
| Burn-in check-ins at 1 h, 4 h and 8 h | AB-06 | The 8-hour window itself is not counted | 10 |
| **Power-on & testing** | | | **[55](LAB_SEC9)** |

## 10. Finishing & packing

The unit passed. Empty it, clean it up, name it, box it.

| Operation | Cards | Notes | Minutes |
|---|---|---|---:|
| Drain and air-purge for transit | AB-07 | Nothing wet ships | 5 |
| Wipe down + final inspection | FS-01 | | 5 |
| Drain dry, nameplate, sign the plaque | FS-02 | Pigment ink in the recess, then let it set | 5 |
| Cap the inlets + photograph | FS-03 | | 5 |
| Pack the install kit and carton | FS-04 | | 10 |
| Weigh, label, hand off | FS-05 | | 5 |
| **Finishing & packing** | | | **[35](LAB_SEC10)** |

## Totals

| Section | Time | At [$100](LABOR_RATE)/h |
|---|---:|---:|
| 1. Machining | [45 m](LAB_HM1) | [$75.00](LAB_USD1) |
| 2. Welding & brazing | [50 m](LAB_HM2) | [$83.33](LAB_USD2) |
| 3. Pressure testing & leak checks | [55 m](LAB_HM3) | [$91.67](LAB_USD3) |
| 4. Silicone casting | [35 m](LAB_HM4) | [$58.33](LAB_USD4) |
| 5. Foam pouring | [35 m](LAB_HM5) | [$58.33](LAB_USD5) |
| 6. Wiring | [1 h 35 m](LAB_HM6) | [$158.33](LAB_USD6) |
| 7. Plumbing | [1 h 10 m](LAB_HM7) | [$116.67](LAB_USD7) |
| 8. Assembly | [2 h](LAB_HM8) | [$200.00](LAB_USD8) |
| 9. Power-on & testing | [55 m](LAB_HM9) | [$91.67](LAB_USD9) |
| 10. Finishing & packing | [35 m](LAB_HM10) | [$58.33](LAB_USD10) |
| **Per-unit total** | **[9 h 55 m](LAB_HM)** | **[$991.67](LAB_USD)** |

The target is 10 hours attended per unit. Bottom-up this says [9 h 55 m](LAB_HM). Where the remaining time sits:

- **Assembly** ([2 h](LAB_HM8), the largest category) — over a third of it is tending printers, which is setup, not work: a second printer takes it straight out of the unit.
- **Wiring** ([1 h 35 m](LAB_HM6)) — three quarters of it is the twelve harnesses. A crimp jig and a batch cut list against the harness schedule move that number; nothing else in the section will.
- **Machining** — the four hand-tapped NPT ports are the slowest five minutes each in the build, and the production tapping fixture is still an open item in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md).

## Not counted here

- **Unattended process time** — every hour a machine is busy and nobody is on it. That is its own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which holds the print, the cures and bakes, the hydro and vacuum holds, the passivation soak, the chill-down and the burn-in, and derives turnaround and throughput from them. Nothing there is costed.
- **Shipping and receiving** — unpacking orders, kitting, inventory.
- **Design, CAD, firmware and documentation** — this file costs building a unit, not developing one.
- **Contract labor already capitalized in dollars** — JLCPCB assembly of the controller board, SendCutSend's cutting. Those arrive as parts and are priced in [bom.md](/hardware/ledger/bom.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_bom_sync.py`
- `/hardware/scripts/_labor_totals.py`
