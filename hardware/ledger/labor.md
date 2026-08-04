# Labor — One Consumer Unit

Attended human minutes to build one finished appliance, one row per hand operation, grouped into the nine kinds of work the build actually asks for. Companion to [bom.md](/hardware/ledger/bom.md): that file is what a unit costs in parts, this one is what it costs in time. Both are per finished unit.

**Attended, not elapsed.** A row counts only the minutes a person is *on* the operation. The 30-minute hydro hold, the 15-minute vacuum hold, the silicone cure, the 8-hour burn-in, and the ~200 printer-hours are all real and none of them are in this file — the operator is elsewhere. What is counted is setup, the hands-on pass, the check, the tear-down, and the walk to the next stage.

**Two columns, because both are true.**

- **Groove** — an operator who has done this operation before, with the fixture built, the jig loaded, and a batch of [10](BATCH_SIZE) units in flight, so setup amortizes. This is the number the appliance has to hit to be worth building.
- **Today** — the same operation at the current experience level: reading the procedure between steps, fixtures improvised, and the rework that a first pass earns. Most of the gap is not slower hands. It is a weld that fails PT and gets ground back, a mix ratio missed, a sensor that reads nothing until the loom is re-terminated.

The batch of [10](BATCH_SIZE) is not a hypothetical: it is the size the ledger already buys in — endcap plates 20 at a time (two per vessel), tube 10 at a time, PCBAs at the qty-10 price. An operation whose setup is per-batch rather than per-unit carries a tenth of that setup here.

Cards cite [`assembly/cards/`](/hardware/assembly/cards/README.md); each card's procedure doc is the source of truth for what the operation involves.

## 1. Machining

Drilling, tapping, chamfering, cutting and deburring — all of it on the pressure vessel, all of it before a single weld. The 316L plate work is the slowest metal in the build: four 1/4"-18 NPT ports hand-tapped into 1/4" plate, and a blind register hole that is part of the 90 PSI pressure boundary and must not break through.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Chamfer the four port holes; break both plate edges | PV-01, PV-04 | Countersink inside faces, burr-break only on the outside — that edge is the fillet root | 7 | 40 |
| Tap four 1/4"-18 NPT ports in 1/4" 316L | PV-02 | Hand tap + spring guide + cutting fluid; the production fixture is still an open item, so Today carries improvised work-holding | 18 | 120 |
| Drill the blind rod register, both plates | PV-03 | Drill press at ~740 RPM, depth stop at 0.10", proved on a scrap disc first | 6 | 40 |
| Cut three level rods to length, deburr | PV-05 | 1/8" 316L to 131.1 mm | 5 | 25 |
| Deburr the tube; Scotch-Brite the two fillet bands | PV-07 | ~30 s per joint of prep is what the weld needs; the rest is handling | 9 | 45 |
| **Machining** | | | **[45](LAB_G_SEC1)** | **[270](LAB_T_SEC1)** |

## 2. Welding & brazing

Three laser welds on the vessel and one brazed tie-in on the refrigerant loop. Both are argon-shielded, both are pressure joints, and both are where a first pass is most likely to be a second pass. Today's numbers carry a rework cycle — the closure fillets are the two welds dye-penetrant inspection exists to reject.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Tack the float rod into the bottom-plate register | PV-06 | Same welding session as the plate fillets — heat the welder once | 4 | 30 |
| Weld the bottom-plate corner fillet under argon | PV-08 | ~15" of recessed corner fillet, handheld X1 Pro, keep heat moving | 11 | 130 |
| Close the vessel — top-plate fillet, float captive | PV-09 | Same joint, one shot, nothing comes back out after this | 11 | 130 |
| Cut the loop, tie in the suction line, pinch-swage the capillary | RL-03, RL-04, RL-05 | Brazing the harvested compressor path with argon flowing through the tube | 24 | 210 |
| **Welding & brazing** | | | **[50](LAB_G_SEC2)** | **[500](LAB_T_SEC2)** |

## 3. Pressure testing & leak checks

Every pressure boundary in the unit gets proved before it is buried: the vessel by dye penetrant and hydro before it is foamed in, the refrigerant loop by vacuum decay before charge, the CO2 path by a witnessed hold at working pressure. The holds themselves are unattended — plugging, filling, pumping, reading and draining are not.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Dye-penetrant both closure welds — clean, dwell, develop, read | PV-10 | Solvent-removable visible dye on bare, dry welds | 12 | 45 |
| Hydro test to 180 PSI — plug, fill, pump, drain | PV-11 | 2× working pressure; the 30-minute hold is not counted | 14 | 60 |
| Citric passivation — load the tub, rinse, dry | PV-12 | Batch soak in the shared tub; the 30–60 minute soak is not counted | 7 | 25 |
| Pull vacuum to 500 µm, valve off, read the rise | RL-06 | Two 15-minute holds, neither counted | 8 | 30 |
| Mass-metered recharge, run-up and leak check | RL-07, RL-08 | Scale-metered charge, then find the weep if there is one | 12 | 90 |
| First CO2 fill to 90 PSI; witness every joint dry | AB-02 | The first time the assembled unit holds gas | 7 | 50 |
| **Pressure testing** | | | **[60](LAB_G_SEC3)** | **[300](LAB_T_SEC3)** |

## 4. Silicone casting

One cast part per unit: the hopper funnel, ~78 g of 1:1 platinum silicone poured into the two-piece printed mold. The cure and the post-cure bake are oven time, not operator time. What costs is the release film, the degas, and the flash trim — and, at this experience level, the pours that come out with a bubble in the rim or tear on demold.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Release the cavity, release the sealed core, close and clamp | — | Ease Release 200 on both faces every pour | 4 | 20 |
| Weigh, pigment, mix and vacuum-degas 78 g of silicone | — | 1:1 by weight, ≤2 % black pigment, chamber until it falls back | 8 | 45 |
| Pour through the port, watch the five vents, rack to cure | — | Cure is unattended | 4 | 25 |
| Demold, trim the port and vent flash | — | 3 mm wall, 40A — it wants to tear if the release is thin | 5 | 55 |
| Post-cure bake — load and unload the oven | — | Bake is unattended | 2 | 15 |
| Re-sand, re-seal and re-release the core as the film wears | — | Amortized across the pulls one seal coat survives | 2 | 40 |
| **Silicone casting** | | | **[25](LAB_G_SEC4)** | **[200](LAB_T_SEC4)** |

## 5. Foam pouring

Three pour-in-place foam operations: both cold-core caps, the body foam around the vessel, and the insulating sleeve on the carbonated-water tube in the umbilical. Same operator motion as the silicone — mix, pour, walk away — but with a shorter cream time and a much bigger mess when a rim overflows.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Mix and pour both cap foams, lids bolted down as the clamp | CC-06 | The cap lids are the pour clamp and stay in the product | 11 | 80 |
| Mix and pour the body foam around the vessel | CC-14 | Around seven penetrations and the PRV shroud's protected air cavity | 13 | 110 |
| Foam-sleeve the carbonated-water umbilical tube | FU-03 | Only the carbonated line is insulated | 5 | 30 |
| Trim the overflow; clean rims, cups and sticks | CC-06, CC-14 | Foam does not wait for you to find a scraper | 6 | 60 |
| **Foam pouring** | | | **[35](LAB_G_SEC5)** | **[280](LAB_T_SEC5)** |

## 6. Wiring

Twelve harness assemblies off the bench plus the in-cabinet runs — roughly sixty crimped terminations per unit across JST-XH contacts, ferrules, Fastons, forks and rings. This is the largest single block of hand labor in the build, and the one that responds best to a crimp jig and a cut list: in a groove the harnesses are built a batch at a time against the schedule, not one loom at a time against the unit in front of you.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Build the twelve harness assemblies — cut, strip, crimp, sleeve, ring out | CA-01, CA-02 | ~60 terminations; batch-built against the harness schedule | 55 | 420 |
| AC distribution + ground bus on the shelf; land the pigtails | ES-02, ES-04 | Ferrules into 221s, rings to the ground stud | 12 | 90 |
| DC distribution + 12 V branches; land the RELAYS J5 loom | ES-05, ES-06 | | 10 | 75 |
| Chassis-ground bonds; C14 to compressor and PSU | WR-01, WR-02 | | 10 | 80 |
| Dielectric + continuity check, AC side | ES-07, WR-03 | Pre-power isolation proof — nothing gets energized before it passes | 8 | 65 |
| Cabinet 12 V runs and signal looms | WR-04, WR-05 | Label both 7P housings; J4 and J7 share a shell | 12 | 70 |
| Bundle, route, strain-relieve | WR-06 | | 8 | 40 |
| **Wiring** | | | **[115](LAB_G_SEC6)** | **[840](LAB_T_SEC6)** |

## 7. Plumbing

Every wetted and gas joint in the unit: the vessel's four elbow stacks, the seven cold-core penetrations, the CO2 and water paths from panel to core, the flavor manifold, and the risers to the umbilical bulkheads. Roughly sixteen taped NPT joints and a larger count of push-to-connect. PTC is fast; NPT into stainless is not.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Install the four elbow stacks, sparge stone, PRV shroud subassembly | PV-13, PV-14 | Nickel-guard tape, SS into SS, every port taped twice across the build | 14 | 90 |
| Route the seven cold-core penetrations; stack the copper plugs | CC-12, CC-13 | Done before the body foam locks them in | 10 | 70 |
| CO2 path — front panel to cold core | IP-01 | | 9 | 60 |
| Water path — rear panel to cold core | IP-02 | Filter, backflow, pump, top-plate port | 9 | 60 |
| Flavor manifold — valves, tees, pumps and channels | IP-03, IP-04 | Six valve trays, two peristaltic pumps, two channels | 16 | 110 |
| Risers to the umbilical bulkheads | IP-05 | | 6 | 40 |
| Witness and tidy every joint | IP-06 | The pass that makes the next leak someone else's fault | 6 | 60 |
| **Plumbing** | | | **[70](LAB_G_SEC7)** | **[490](LAB_T_SEC7)** |

## 8. Assembly

Everything that is putting parts together with fasteners and hands. Printer tending lives here: ~7.3 kg of filament across the twenty-one §7 lines is on the order of 200 printer-hours per unit, but the *attended* share is plate changes, spool swaps, part removal and support cleanup. So do the 42 heat-set inserts and the 42 machine screws that close the build.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Tend the printers — plate changes, spool swaps, part removal, support cleanup | — | ~7.3 kg over ~200 printer-hours; only the load/unload passes are counted | 40 | 150 |
| Press 42 heat-set inserts — foam caps, reservoir caps, touch-flo pods | CC-05 | FX-888D + T18 tip kit, twelve of them in the shell faces alone | 14 | 70 |
| Drive the 42 machine screws that close the build | — | 12 foam-cap, 12 reservoir-cap, 3 touch-flo, 15 shelf | 12 | 45 |
| Wind the evaporator coil on the mandrel; transfer it, set the band | CC-01, CC-03 | | 12 | 90 |
| Dress the vessel wall — reeds, probe, foil; bond the coil probe | CC-02, CC-04 | | 12 | 90 |
| Build the reed columns; seat rods and floats; close the reservoirs | CC-07, CC-08, CC-09, CC-15 | Two reservoirs, gaskets, caps, vent filters | 18 | 130 |
| Lower the vessel; seat the reservoirs in their pockets | CC-10, CC-11 | | 8 | 60 |
| Prepare the shelf trays; mount PSU, relays, PCBA | ES-01, ES-03 | Onto the top cap's fifteen deck-mount columns | 10 | 70 |
| Stage shell and back panel; compressor shroud, condenser and fan | EN-01, EN-02, EN-03 | | 14 | 110 |
| Seat the cold core; drip pan, hopper, back panel, electronics shelf | EN-04, EN-05, EN-06, EN-07, EN-08 | | 16 | 120 |
| Cut, route and sleeve the umbilical; bag the installer kit | FU-01, FU-02, FU-04, FU-05 | Three LLDPE tubes, braid, install-kit bag | 12 | 80 |
| Assemble the faucet — three-piece touch-flo shell, plate, gasket, o-ring | — | PET-CF shell, printed TPU seals | 8 | 45 |
| **Assembly** | | | **[176](LAB_G_SEC8)** | **[1,060](LAB_T_SEC8)** |

## 9. Commissioning & pack

Power-on through hand-off. The 8-hour burn-in is not counted — firmware logs it and the operator checks in three times. What is counted is the walkthrough that finds the fault, and on a first unit that walkthrough *is* the debugging: a sensor that reads nothing, a valve that clicks on the wrong channel, a setpoint that never settles.

| Operation | Cards | Notes | Groove | Today |
|---|---|---|---:|---:|
| Verify wiring-out; first DC power-on | FC-01 | | 6 | 90 |
| Flash the three ESP32s | FC-02 | Base, config display, faucet display | 6 | 45 |
| Sensor health walkthrough | FC-03 | Both DS18x20s, flow, moisture, reeds, cap-sense, gas | 8 | 120 |
| Valve + pump self-test; compressor smoke test and setpoints | FC-04, FC-05 | | 10 | 180 |
| First dispenses — water, flavor A, flavor B | AB-03 | | 8 | 90 |
| Clean cycle, air purge, level-sensing transitions | AB-04, AB-05 | | 8 | 70 |
| Burn-in check-ins at 1 h, 4 h and 8 h | AB-06 | The 8-hour window itself is not counted | 12 | 40 |
| Drain and air-purge for transit | AB-07 | | 5 | 25 |
| Wipe down, nameplate, sign the plaque, photograph | FS-01, FS-02, FS-03 | Pigment ink in the recess, then let it set | 12 | 45 |
| Pack the install kit and carton; weigh, label, hand off | FS-04, FS-05 | | 10 | 35 |
| **Commissioning & pack** | | | **[85](LAB_G_SEC9)** | **[740](LAB_T_SEC9)** |

## Totals

| Section | Groove | Today |
|---|---:|---:|
| 1. Machining | [45](LAB_G_SEC1) | [270](LAB_T_SEC1) |
| 2. Welding & brazing | [50](LAB_G_SEC2) | [500](LAB_T_SEC2) |
| 3. Pressure testing & leak checks | [60](LAB_G_SEC3) | [300](LAB_T_SEC3) |
| 4. Silicone casting | [25](LAB_G_SEC4) | [200](LAB_T_SEC4) |
| 5. Foam pouring | [35](LAB_G_SEC5) | [280](LAB_T_SEC5) |
| 6. Wiring | [115](LAB_G_SEC6) | [840](LAB_T_SEC6) |
| 7. Plumbing | [70](LAB_G_SEC7) | [490](LAB_T_SEC7) |
| 8. Assembly | [176](LAB_G_SEC8) | [1,060](LAB_T_SEC8) |
| 9. Commissioning & pack | [85](LAB_G_SEC9) | [740](LAB_T_SEC9) |
| **Total, minutes** | **[661](LAB_G_GRAND)** | **[4,680](LAB_T_GRAND)** |
| **Total, hours** | **[11.0](LAB_G_HOURS)** | **[78.0](LAB_T_HOURS)** |

The target is 10 hours attended per unit. Bottom-up, the groove column says [11.0](LAB_G_HOURS) — the gap is one wiring block wide, which is where the next jig pays for itself. Today's column says [78.0](LAB_T_HOURS), a factor of [7.1](LAB_RATIO) on the same operations; the whole factor is fixtures, procedure fluency, and rework.

Where the 10-hour target is actually won:

- **Wiring** ([115](LAB_G_SEC6) min groove, the largest block) — a crimp jig and a batch cut list against the harness schedule, not a loom at a time.
- **Assembly** ([176](LAB_G_SEC8) min groove, the largest category) — printer tending and heat-sets are both pure setup work; a second printer and an insert fixture take the setup out of the unit.
- **Machining** — the production tapping fixture is still an open item in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). It is the single biggest gap between the two columns per minute of groove time.

## Not counted here

- **Unattended process time** — the 30-minute hydro hold, the two 15-minute vacuum holds, the 30–60 minute passivation soak, the silicone cure and post-cure bake, the foam rise, the ~200 printer-hours, the 8-hour burn-in, and the first chill-down from tap temperature to service temperature.
- **Shipping and receiving** — unpacking orders, kitting, inventory.
- **Design, CAD, firmware and documentation** — this file costs building a unit, not developing one.
- **Contract labor already capitalized in dollars** — JLCPCB assembly of the controller board, SendCutSend's cutting. Those arrive as parts and are priced in [bom.md](/hardware/ledger/bom.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_labor_totals.py`
