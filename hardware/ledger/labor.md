# Labor — One Consumer Unit

Attended human minutes to build one finished appliance, grouped into the ten kinds of work the build asks for. Each wiring bench row is one finished harness, including its full sequence of hand operations. Companion to [bom.md](/hardware/ledger/bom.md): that file is what a unit costs in parts, this one is what it costs in time.

**Attended, not elapsed.** A row counts only the minutes a person is *on* the operation. The 30-minute hydro hold, the 15-minute vacuum hold, the silicone cure, the 8-hour burn-in, and the [194.6](LAB_PRINT_H) estimated printer-hours are equipment time. What is counted here is setup, the hands-on pass, the check, the tear-down, and the walk to the next stage. The hours a *machine* is busy are their own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which is what turnaround and throughput are read off.

**Deliberately the ideal, not Derek's actual time.** Derek builds each unit himself, one at a time. These estimates assume practiced hands, the fixture built and the jig loaded, and a batch of [10](BATCH_SIZE) machines built together, the quantity the ledger buys in: endcap plates 20 at a time (two per carbonator), tube 10 at a time, PCBAs at the qty-10 price. Costs, and the price set from them, rest on this ideal picture of labor; paying for Derek's actual hours would take a price of $8,000 or more, which is not the plan.

**Runs.** An operation set up once for many pieces carries a Run cell: `15 m setup a plate of 30 · 30 s a float · 3 a machine`. The setup comes once a run: the plate cleaned and turned, the spool loaded, the welder and argon brought up, the bath mixed. The per-piece time comes with every piece. A run's size is the pieces one setup serves, a plate's or a session's capacity; `a batch` is one setup for every machine built together. The Minutes cell is the arithmetic for a batch of ten: the setups ten machines need, plus every piece's time, divided by ten. The [batch forecast](/hardware/ledger/batch-forecast.md) works the same cells out for 5, 10 and 20 machines. An operation without a Run cell is timed once a machine.

**The maturity benchmark is the 25th unit using the documented method.** A practiced assembler has the maps, material locations, terminal choices and tools ready. Development, lookup and learning are outside the recurring labor estimate. A complete harness remains one bench job, made start to finish by one person; repeat volume does not assume separate stations for mass crimping.

**The pace is a practiced one.** Three minutes an operation is a relaxed rate for repetitive work once it is practiced, so an operation of that shape gets 5 minutes, not 10. A machine screw is seven seconds with a driver; a heat-set insert is fourteen seconds with a hot tip and a jig. Where a row is longer than that it is because the work does not repeat: a weld that has to be right the first time, a hand tap into 1/4" stainless, a foam pour with a cream time.

**Costed at [$100](LABOR_RATE) per hour of attended time.** That rate is what the site's `/cost` page prices the labor column with; it reads the number from the marker above, so this file sets it.

**Every estimate lands on one of these increments,** and nothing in between:

`5m · 10m · 15m · 20m · 25m · 30m · 45m · 1h · 1h15 · 1h30 · 1h45 · 2h · 2h30 · 3h · 4h · 6h`

These are the steps a person actually estimates in. "40 minutes" claims a precision no one has for work they have not timed; it means 30 or it means 45, and saying which is the more useful answer. A run's setup and per-piece time are estimates on the same steps, with seconds and single minutes below them:

`5 s · 10 s · 15 s · 30 s · 45 s · 1 m · 2 m · 3 m`

`_labor_totals.py --check` rejects an estimate that lands anywhere else, so the convention holds as rows get added. A run row's minutes, the subtotals and the grand total are arithmetic and land where it puts them.

The linked fabrication procedures define each operation. [Letter shop guides](/hardware/assembly/guides/README.md) illustrate drilling and cutting, molds, refrigeration and the carbonator weld operation.

## 1. Machining

Drilling, tapping, chamfering, cutting and deburring for the carbonator, its upper float stop and its water-inlet jet. The 316L plate work is the slowest metal in the build: four 1/4"-18 NPT ports hand-tapped into 1/4" plate, and a blind register hole in the carbonator's pressure boundary that must not break through.

| Operation | Procedure | Notes | Run | Minutes |
|---|---|---|---|---:|
| Chamfer the four port holes; break both plate edges | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Countersink inside faces, burr-break only on the outside — that edge is the fillet root | | 5 <!--parts HSM-000009--> |
| Tap four 1/4"-18 NPT ports in 1/4" 316L | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Hand tap + spring guide + cutting fluid | | 20 <!--parts HSM-000009--> |
| Drill the blind rod register, both plates | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Drill press at ~740 RPM; the setup is the depth stop at 0.10", proved on a scrap disc | 10 m setup a batch · 2 m a plate · 2 a machine | 5 <!--parts HSM-000009--> |
| Cut three level rods to length, deburr | [reservoir rods](/hardware/assembly/handwork.md#cut--seat-the-reservoir-float-rods), [pressure-vessel](/hardware/assembly/pressure-vessel.md) | 1/8" 316: one at 5.110 ±0.005 in and two at 203.8 mm; the setup is a stop set and proved for each length | 20 m setup a batch · 1 m a rod · 3 a machine | 5 <!--parts HSM-000336 HSM-000339--> |
| Deburr the tube; Scotch-Brite the two fillet bands | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | ~30 s per joint of prep is what the weld needs; the rest is handling | | 10 <!--parts HSM-000008--> |
| Drill the jet handling blank, cut the cap, deburr and clean | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured attended-time estimate; the drilling fixture, already made, is set up once a batch | 20 m setup a batch · 3 m a cap · 1 a machine | 5 <!--parts HSM-000011--> |
| Bore, cut, deburr and clean the upper float stop | [pressure-vessel](/hardware/assembly/pressure-vessel.md#upper-float-stop) | Provisional, unmeasured allowance: clamp the stainless handling blank, bore Ø9/64 inch before the 4 mm cutoff, deburr both mouths and inspect length | 20 m setup a batch · 3 m a stop · 1 a machine | 5 <!--parts HSM-000004--> |
| **Machining** | | | | **[55](LAB_SEC1)** |

## 2. Welding & brazing

Five laser operations serve the carbonator: the float-rod tack, upper float-stop tack, two closure welds and the water-inlet jet cap weld. The refrigerant loop has one brazed tie-in. Argon shielding and the jet's internal purge are included in their attended setup allowances.

| Operation | Procedure | Notes | Run | Minutes |
|---|---|---|---|---:|
| Tack the float rod into the bottom register and the upper stop over the top register | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Provisional, unmeasured allowance for both loose-cap tacks; welder, argon and fixture are set up once for the session the plate fillets share | 20 m setup a session of 10 · 5 m a vessel · 1 a machine | 7 <!--parts HSM-000004--> |
| Weld the bottom-plate corner fillet under argon | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | ~15" of recessed corner fillet, handheld X1 Pro, keep heat moving | | 10 <!--parts HSM-000004--> |
| Close the carbonator — top-plate fillet, float captive | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Same joint, one shot, nothing comes back out after this | | 10 <!--parts HSM-000004--> |
| Fixture, purge and weld the water-inlet jet cap | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured estimate for a qualified, repeatable process; destructive development coupons are excluded | | 10 <!--parts HSM-000338--> |
| Cut the loop, tie in the suction line, pinch-swage the capillary | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Brazing the harvested compressor path with argon flowing through the tube | | 25 <!--parts HSM-000001--> |
| **Welding & brazing** | | | | **[62](LAB_SEC2)** |

## 3. Pressure, leak & flow checks

The carbonator receives dye penetrant and hydro before foaming, the refrigerant loop a vacuum-decay check before charge, and the CO2 path a witnessed hold at measured operating pressure. The jet elbow receives its own production inspection and timed flow check. The holds themselves are unattended — plugging, filling, pumping, reading and draining are not. These checks do not replace the weld-process qualification.

| Operation | Procedure | Notes | Run | Minutes |
|---|---|---|---|---:|
| Dye-penetrant both closure welds — clean, dwell, develop, read | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Solvent-removable visible dye on bare, dry welds | | 10 <!--parts HSM-000004--> |
| Hydro test to 180 PSI — plug, fill, pump, drain | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | 1.44× the SV-125's set pressure; the 30-minute hold is not counted | | 15 <!--parts HSM-000004--> |
| Citric passivation — load the tub, rinse, dry | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | Clean carbonator and jet elbow; the setup is the citric bath mixed in the shared tub, the 30–60 minute soak not counted | 20 m setup a batch · 3 m a vessel · 1 a machine | 5 <!--parts HSM-000004:4 HSM-000338:1--> |
| Inspect the jet elbow, flow-check and record the result | [Jet procedure](/hardware/assembly/water-inlet-jet.md) | Provisional, unmeasured estimate; accepted geometry and flow band must be established by qualification | | 5 <!--parts HSM-000338--> |
| Pull vacuum to 500 µm, valve off, read the rise | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Two 15-minute holds, neither counted | | 10 <!--parts HSM-000001--> |
| Mass-metered recharge, run-up and leak check | [refrigerant-loop](/hardware/assembly/refrigerant-loop.md) | Scale-metered charge, then find the weep if there is one | | 10 <!--parts HSM-000001--> |
| First CO2 fill at the selected setting; measure pressure and witness every joint dry | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | Record actual carbonator pressure; the nominal regulator setting is not a reading | | 5 <!--parts HSM-000001--> |
| **Pressure, leak & flow checks** | | | | **[60](LAB_SEC3)** |

## 4. Silicone casting

One cast part per unit: the funnel, [331.0](FUNNEL_VOLUME_ML) mL of finished CAD volume, estimated at [374](FUNNEL_FINISHED_G) g using an assumed [1.13](FUNNEL_DENSITY_G_ML) g/mL density. The batch allocation is [411](FUNNEL_MIXED_G) g of 1:1 platinum silicone, including a provisional [10%](FUNNEL_MIX_ALLOWANCE) mixing and port-flash allowance. Two printed mold shells and a straight 6 × 25 mm steel rod form the complete funnel and its cylindrical bore for the drain tube. Room-temperature cure and the post-cure bake are equipment time; the attended work is preparation, pouring, release and flash trim. Casting yield, finishing compatibility and these handwork allowances remain unmeasured.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Release both forming faces and the steel rod; drop it in the lower seat and clamp the shells | — | Compatible finishing/release stack, rod resting on the lower floor, bare mold lands closed; [mold procedure](/hardware/printed-parts/zone-c/funnel-mold/README.md) | 5 <!--parts HSM-000070--> |
| Weigh, pigment, mix and vacuum-degas [411](FUNNEL_MIXED_G) g of silicone | — | 1:1 by weight, ≤2 % black pigment, chamber until it falls back | 10 <!--parts HSM-000070--> |
| Pour the open cavity, lower the core, vacuum and top up, rack to cure | — | The cure and the vacuum hold are unattended | 5 <!--parts HSM-000070--> |
| Demold, pull the straight rod and trim outlet, port and vent flash | — | Peel the brim first to admit air; pull the rod through the bowl, then trim flash flush | 5 <!--parts HSM-000070--> |
| Post-cure bake — load and unload the oven | — | Bake is unattended | 5 <!--parts HSM-000070--> |
| Maintain the shell forming faces and clean the steel rod | — | Amortized across casting pulls; preserve the shell finish and smooth cylindrical rod | 5 <!--parts HSM-000070--> |
| **Silicone casting** | | | **[35](LAB_SEC4)** |

## 5. Foam pouring

Three pour-in-place foam operations: both cold-core caps, the body foam around the carbonator, and the insulating sleeve on the soda umbilical tube. Same motion as the silicone — mix, pour, walk away — but with a shorter cream time and a much bigger mess when a rim overflows.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Mix and pour both cap foams, lids bolted down as the clamp | [cold-core](/hardware/assembly/cold-core.md) | The cap lids are the pour clamp and stay in the product | 10 <!--parts HSM-000003--> |
| Mix and pour the body foam around the carbonator | [cold-core](/hardware/assembly/cold-core.md) | Around seven penetrations and the PRV shroud's protected air cavity | 15 <!--parts HSM-000003--> |
| Foam-sleeve the carbonated-water umbilical tube | [faucet-and-umbilical](/hardware/assembly/faucet-and-umbilical.md) | Only the carbonated line is insulated | 5 <!--parts HSM-000002 HSM-000007--> |
| Trim the overflow; clean rims, cups and sticks | [cold-core](/hardware/assembly/cold-core.md) | Foam does not wait for you to find a scraper | 5 <!--parts HSM-000003--> |
| **Foam pouring** | | | **[35](LAB_SEC5)** |

## 6. Wiring

**One complete bench job per harness, at unit 25.** One practiced person cuts,
marks, strips, terminates, dresses, tests and labels each finished piece before
starting another. The map, cut lengths, tools and materials are ready; shared
setup is amortized, with no separate mass-crimping station. These are
theoretical attended-time estimates, not timed production readings. Development,
lookup, learning and final cabinet fitting are outside the bench cycles.
J13's XHP-4 end is made on the bench; its free end passes through front-top's
lead bore into the bay before its four Fastons are crimped. Landing them on the
motor tabs and final routing retain their separate assembly allowances.

The [J2](https://homesodamachine.com/cost#j2-harness) and
[J13](https://homesodamachine.com/cost#j13-harness) visual guides
are the corresponding rows below and are included in the unit total. J2's
10-minute estimate allows about 5–6 minutes for its 18 crimps and 4–5 minutes
for preparation, dressing, Wago assembly, continuity and labeling; allow up to
15 minutes for planning. J13's five minutes covers four JST crimps, four
Faston crimps and its end-to-end check; allow up to ten.
The other estimates use the same practiced method: five minutes for a simple
four-conductor cable, ten for a smaller fan-out, and fifteen for the larger
valve or reed assembly. All remain unmeasured.

### Finished bench harnesses

Eleven pieces: ten JST-ended looms and the ferruled J10 supply lead. Reed
soldering and insulation belong to J6/J7; mounting the finished columns
belongs to Assembly. The separate faucet umbilical is included in that
subassembly's Assembly allowance. J8 is the unused I2C expansion header, with
no production loom in the cable schedule; the reserved J4 IO23/IO27 positions
are also unpopulated. Neither adds a moisture-sensor harness.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| J1 · Manifold A → eight valves | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Nine JST contacts; eight switched returns, eight positive branches and the 221-420 COM fan-out; terminate, dress and ring out the whole assembly | 15 <!--parts HSM-000343--> |
| J2 · Manifold B → V-I, V-J, fan and V-K | [J2 bench guide](/hardware/assembly/harnesses/j2.md) | Five JST contacts in the 6P housing, four positive branches, five ferrules, eight far-end terminations and the 221-415; complete dressed and tested harness | 10 <!--parts HSM-000344--> |
| J3 · Faucet → rear-wall keystone | [cable-assemblies](/hardware/assembly/cable-assemblies.md#faucet-display-sig-6) | Four JST contacts, four 110 IDC landings, dressing, label and end-to-end check; inboard cable only | 5 <!--parts HSM-000345--> |
| J4 · Sensors → temperature bus and flow meter | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Five populated JST positions, temperature-bus connections, flow-meter branch and shared-ground 221-415; terminate, dress and test; IO23/IO27 empty | 10 <!--parts HSM-000346--> |
| J5 · Relays → both relay modules | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, relay-end ferrules and shared V5/GND branches, dressing, label and test | 5 <!--parts HSM-000347--> |
| J6 · Reeds A → four reservoir reeds | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Five JST contacts, four reed pairs soldered and insulated, shared-ground 221-415, lacing and magnet/continuity check; excludes installing the finished column | 10 <!--parts HSM-000348--> |
| J7 · Reeds B → four reservoir and two carbonator reeds | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Seven JST contacts, six reed pairs soldered and insulated, shared-ground 221-420, dressing and magnet/continuity check; excludes mounting reeds or column | 15 <!--parts HSM-000349--> |
| J9 · Display → enclosure LCD | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, four ferruled display-terminal ends, dressing, label and test | 5 <!--parts HSM-000350--> |
| J11 · Gas → MQ-6 sensor | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Four JST contacts, four sensor-end connections, dressing, label and test | 5 <!--parts HSM-000352--> |
| J13 · Pumps → both motors | [J13 bench guide](/hardware/assembly/harnesses/j13.md) | 4P ribbon, four JST contacts in the XHP-4, free motor-lead pairs through the shared rear passage and motor wells before four motor Fastons, +X leads to pump A and −X leads to pump B; label and test; excludes landing on the motor tabs | 5 <!--parts HSM-000353--> |
| J10 · 12 V distribution → board input | [cable-assemblies](/hardware/assembly/cable-assemblies.md) | Two 16 AWG leads, four ferrules, label and test; excludes landing the finished lead in the cabinet | 5 <!--parts HSM-000351--> |

### Installation and AC checks

These operations begin with the finished bench harnesses. Their recurring
work is cabinet power distribution, mounting connections, routing and installed
checks; no JST crimping, reed soldering or J13 Faston crimping is counted again.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| AC distribution + ground bus on the shelf; land the pigtails |  | Ferrules into 221s, rings to the ground stud | 10 <!--parts HSM-000001--> |
| DC distribution + 12 V branches; land J10 and RELAYS J5 |  | Cabinet distribution connections and completed loom landings; J10/J5 cable fabrication is counted above | 5 <!--parts HSM-000001--> |
| Chassis-ground bonds; C14 to compressor and PSU | [wiring](/hardware/assembly/wiring.md) | | 10 <!--parts HSM-000001--> |
| Dielectric + continuity check, AC side | [wiring](/hardware/assembly/wiring.md) | Pre-power isolation proof — nothing gets energized before it passes | 10 <!--parts HSM-000001--> |
| Cabinet 12 V runs and signal looms | [wiring](/hardware/assembly/wiring.md) | Land the labeled 7P J4/J7 housings at their own wafers. With front-top loose, feed DC-5’s bare pump end through the common rear mouth and motor wells to the open underside; keep its XHP-4 aft. Crimp and ring out the four Fastons, connect the accessible motor tabs, then raise the prepared pumps and retainer motor-first while drawing slack aft. Seat both retainer snap hooks; seat J13 through the funnel opening after closure. With AC unplugged, check all four J13 channels point to point and for neighbor isolation | 10 <!--parts HSM-000001:9 HSM-000161:1--> |
| Bundle, route, strain-relieve | [wiring](/hardware/assembly/wiring.md) | | 5 <!--parts HSM-000001--> |
| **Wiring** | | | **[140](LAB_SEC6)** |

## 7. Plumbing

Every wetted and gas joint in the unit: the carbonator's four port elbows, the seven cold-core penetrations, the CO2 and water paths from the +Y wall of back-top to the core, the flavor manifold, and the risers to the umbilical bulkheads. Roughly fourteen taped NPT joints and a larger count of push-to-connect. PTC is fast; NPT into stainless is not.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Install the four port elbows, qualified jet elbow and PRV shroud | [pressure-vessel](/hardware/assembly/pressure-vessel.md) | One outside elbow per port, the bottom two aimed at their lines; recurring jet work is counted in §§1–3 | 15 <!--parts HSM-000004:4 HSM-000003:1--> |
| Route the cold-core passages; form and seal the copper exits | [cold-core](/hardware/assembly/cold-core.md) | Done before the body foam locks them in | 10 <!--parts HSM-000003--> |
| CO2 path — +Y wall of back-top to cold core | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | | 10 <!--parts HSM-000001--> |
| Water path — +Y wall of back-top to cold core | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | Filter, backflow, pump, top-plate port | 10 <!--parts HSM-000001--> |
| Flavor manifold — fixed valves, pump tees, upper tubes and lower returns, prepared pumps and channels | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | [10](SOLENOIDS) fixed valves total. Stage both pumps in the loose retainer, fit their LLDPE tubes, set the tips with the tube setting jig and remove the jig. With the motor leads landed, raise this prepared group motor-first into loose front-top and seat both retainer snap hooks. Fit each pump tee, its upper tube and its fore valve as a group, sliding the tee forward over its fixed pump tube to the insertion stop with its branch in the tee-wall bore. Fit all four fore groups before seating the rear valves; cut eight stem elbows' stems, push them up into the tees and rear valves, and fit the four straight return tubes. This assembly time is an unmeasured allowance | 15 <!--parts HSM-000001:4 HSM-000161:1--> |
| Risers to the umbilical bulkheads | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | | 5 <!--parts HSM-000001--> |
| Witness and tidy every joint | [internal-plumbing](/hardware/assembly/internal-plumbing.md) | The pass that makes the next leak someone else's fault | 5 <!--parts HSM-000001--> |
| **Plumbing** | | | **[70](LAB_SEC7)** |

## 8. Assembly

Everything that is taking the printed parts off the printers and putting parts together with fasteners and hands. Assembly includes the [68](TOTAL_INSERTS) M3/M5 heat-set inserts and [68](TOTAL_SCREWS) matching screws.

### Printed parts

The print model allocates [7.033](LAB_PRINT_KG) kg of filament and [194.6](LAB_PRINT_H) printer-hours per unit, including the three ASA Aero floats ([machine-time.md](/hardware/ledger/machine-time.md)); those hours are the printers'. A plate's setup is its turn: the finished plate pulled and its parts released, the plate cleaned, glued and seated, the next job started, the spool changed when it runs out. A piece's own time is its brim and supports off and a look over it, and for a float the RC62 seated at its pause. A large part fills a plate by itself; the small ones go a batch's worth to a plate. Plate capacities follow the recorded slicer layouts where there is one and are provisional elsewhere, as are the times. The small TPU seals' printing is unmeasured and not counted. On the ledger's batch the printed parts take [1 h 18 m](LAB_HM_PRINTED) a machine.

| Operation | Procedure | Notes | Run | Minutes |
|---|---|---|---|---:|
| Print the cold-core insulation shell | [preparation](/hardware/printed-parts/cold-core/foam-shell/prints/2026-10-26-mark2-round-ports-a2/README.md) | One shell to a plate; no generated supports | 3 m setup a plate of 1 · 1 m a shell · 1 a machine | 4 <!--parts HSM-000018--> |
| Print the four cold-core caps and lids | — | One piece to a plate | 3 m setup a plate of 1 · 30 s a piece · 4 a machine | 14 <!--parts HSM-000019 HSM-000020 HSM-000021 HSM-000022--> |
| Print the four enclosure quadrants | [print log](/hardware/printed-parts/enclosure/enclosure/print-log.md) | One quadrant to a plate; tree supports and a 5 mm brim | 3 m setup a plate of 1 · 2 m a quadrant · 4 a machine | 20 <!--parts HSM-000078 HSM-000079 HSM-000080 HSM-000081--> |
| Print the funnel frame, lower pump retainer, display cover and drain-elbow cradle | — | Two to a plate; tree supports | 3 m setup a plate of 2 · 1 m a piece · 4 a machine | 10 <!--parts HSM-000072 HSM-000082 HSM-000076 HSM-000073--> |
| Print the two flavor reservoirs and their caps | [print log](/hardware/printed-parts/cold-core/reservoir/print-log.md) | A reservoir and its cap to a plate | 3 m setup a plate of 2 · 1 m a piece · 4 a machine | 10 <!--parts HSM-000025 HSM-000026 HSM-000027 HSM-000028--> |
| Print the funnel cover | [recipe](/hardware/printed-parts/zone-c/funnel-cover/README.md) | Black PETG, one to a plate | 3 m setup a plate of 1 · 30 s a cover · 1 a machine | 3.5 <!--parts HSM-000071--> |
| Print the faucet shell base and tip, display cover and above-counter plate | [faucet-petgf](/hardware/printed-parts/faucet/faucet-petgf.md) | The four share one plate in the production slice | 3 m setup a plate of 4 · 1 m a piece · 4 a machine | 7 <!--parts HSM-000094 HSM-000095 HSM-000096 HSM-000092 HSM-000113 HSM-000114 HSM-000111--> |
| Print the PRV shroud, reed bridge and thermal-cutoff clamp | — | PETG, a batch's worth to a plate | 3 m setup a plate of 30 · 15 s a piece · 3 a machine | 1.1 <!--parts HSM-000024 HSM-000029 HSM-000041--> |
| Print the umbilical organizer, soda bend holder, collet press, lever and nameplate | — | PET-GF, a batch's worth to a plate; each nameplate carries its unit's serial | 3 m setup a plate of 50 · 15 s a piece · 5 a machine | 1.6 <!--parts HSM-000098 HSM-000358 HSM-000372 HSM-000268 HSM-000069--> |
| Print the port identification plates and tube collars | [rear identification](/hardware/printed-parts/enclosure/rear-identification/README.md), [tube collar](/hardware/printed-parts/faucet/tube-collar/README.md) | Each in its station's colour with contrasting lettering, a batch's worth to a plate | 3 m setup a plate of 130 · 15 s a piece · 13 a machine | 3.6 <!--parts HSM-000062 HSM-000063 HSM-000064 HSM-000065 HSM-000066 HSM-000067 HSM-000068 HSM-000272 HSM-000099 HSM-000100 HSM-000101 HSM-000102 HSM-000273--> |
| Print the three level floats; seat an RC62 in each at the pause | [float record](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md) | ASA Aero from the drybox on the glued Engineering plate; one pause a plate seats every float's magnet; the elapsed pause is unmeasured | 15 m setup a plate of 30 · 30 s a float · 3 a machine | 3 <!--parts HSM-000033--> |

### Fitting it together

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Press the [68](TOTAL_INSERTS) M3/M5 heat-set inserts | [cold-core](/hardware/assembly/cold-core.md), [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | Shell faces, cap columns, reservoir caps, touch-flo pods, wall bosses, condenser fingers, the integral front-top pump mount, funnel-frame ledges, [4](SEAM_INSERTS) enclosure Y-seam anchors and floor posts. FX-888D + T18 tips for [60](TOTAL_M3_INSERTS) M3 and [8](TOTAL_M5_INSERTS) M5 | 10 <!--parts HSM-000003:41 HSM-000001:24 HSM-000002:3 HSM-000007:3--> |
| Drive the [68](TOTAL_SCREWS) M3/M5 build screws | — | [20](FOAM_SCREWS) foam-cap, [4](PUMP_MOUNT_SCREWS) water-pump, [12](RES_SCREWS) reservoir-cap, [3](TOUCHFLO_SCREWS) faucet base, [13](SHELF_SCREWS) electronics, [2](COND_SCREWS) condenser, [4](ROOF_CLOSURE_SCREWS) funnel-frame, [0](DISPLAY_COVER_SCREWS) display plate, [0](NAMEPLATE_SCREWS) nameplate, [4](SEAM_RODS) M5 enclosure Y-seam screws, two upward through the handholds and two downward through the roof, each with one flat washer, [4](FLOOR_SCREWS) floor, [2](C14_SCREWS) C14 inlet | 5 <!--parts HSM-000003:32 HSM-000001:32 HSM-000051:1 HSM-000002:3 HSM-000007:3--> |
| Wind the evaporator coil on the mandrel; transfer it, set the band | [cold-core](/hardware/assembly/cold-core.md) | | 10 <!--parts HSM-000015--> |
| Dress the carbonator wall — reeds, probe, foil; bond the coil probe | [cold-core](/hardware/assembly/cold-core.md) | | 10 <!--parts HSM-000003--> |
| Fit the finished reed columns; seat rods and floats; close the reservoirs | [cold-core](/hardware/assembly/cold-core.md) | Two reservoirs, gaskets, caps, vent filters; J6/J7 soldering and insulation are counted in Wiring | 15 <!--parts HSM-000003--> |
| Lower the carbonator; seat the reservoirs in their pockets | [cold-core](/hardware/assembly/cold-core.md) | | 5 <!--parts HSM-000003--> |
| Populate the WAGO wells; mount PSU, relays, PCB and earth stack | [electronics-bay](/hardware/assembly/electronics-bay.md) | The PCB uses the core's full-length cap inserts. The PSU's four west-sidewall hosts and the core earth boss use [5](SHELF_INSERTS) short inserts, and each relay fastens at two diagonal short inserts | 5 <!--parts HSM-000001:4 HSM-000051:1--> |
| Stage the printed enclosure and dock parts and the +Y wall's seven bodies; bolt the compressor down to the slab | [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | Four quadrants, lower pump retainer and four pump tees; rear-wall set includes the RJ11 keystone. Four floor posts, one M5 and a fender washer each, snugged onto the post crowns | 10 <!--parts HSM-000001--> |
| Seat the cold core; condenser, electronics bay, close the box | [enclosure-mechanical](/hardware/assembly/enclosure-mechanical.md) | | 10 <!--parts HSM-000001--> |
| Cut, route and sleeve the umbilical; bag it with the under-counter plate | [faucet-and-umbilical](/hardware/assembly/faucet-and-umbilical.md) | Three LLDPE tubes, braid, the bag | 10 <!--parts HSM-000002 HSM-000007--> |
| Assemble the faucet — two-piece shell, display cover, plate, gasket and o-ring | — | Route tubes and ribbon before closing the plate; PET-GF prints, TPU seals | 5 <!--parts HSM-000002 HSM-000007--> |
| **Assembly** | | | **[172.8](LAB_SEC8)** |

## 9. Power-on & testing

The unit is fully built. Now it gets plugged in for the first time: load the firmware, walk every sensor and every actuator, dispense from it, and leave it running overnight. The 8-hour burn-in is not counted — firmware logs it and Derek checks in three times.

| Operation | Procedure | Notes | Run | Minutes |
|---|---|---|---|---:|
| Check the wiring is right; first DC power-on | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | | | 5 <!--parts HSM-000001--> |
| Load the firmware onto the three ESP32s | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | Base, enclosure display, faucet display; the setup is the release built and the flashing station cabled | 20 m setup a batch · 1 m a board · 3 a machine | 5 <!--parts HSM-000001:2 HSM-000002:1 HSM-000007:1--> |
| Read every sensor and confirm it reports | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | Both DS18x20s, flow, reeds, gas | | 10 <!--parts HSM-000001--> |
| Fire every valve and pump; run the compressor and set its setpoints | [firmware-and-commissioning](/hardware/assembly/firmware-and-commissioning.md) | | | 10 <!--parts HSM-000001--> |
| First dispenses — water, flavor A, flavor B | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | | | 5 <!--parts HSM-000001--> |
| Clean cycle, air purge, level-sensing transitions | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | | | 10 <!--parts HSM-000001--> |
| Burn-in check-ins at 1 h, 4 h and 8 h | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | The 8-hour window itself is not counted | | 10 <!--parts HSM-000001--> |
| **Power-on & testing** | | | | **[55](LAB_SEC9)** |

## 10. Finishing & packing

The unit passed. Empty it, clean it up, name it, box it.

| Operation | Procedure | Notes | Minutes |
|---|---|---|---:|
| Drain and air-purge for transit | [acceptance-and-burn-in](/hardware/assembly/acceptance-and-burn-in.md) | Nothing wet ships | 5 <!--parts HSM-000001--> |
| Wipe down + final inspection | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 <!--parts HSM-000001--> |
| Scan the nameplate QR and snap its horizontal wings into the back-top receiver | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | Match the four-digit unit number to the order and per-unit archive; confirm full seating and retention per [finish procedure](/hardware/assembly/finish-pack-ship.md#3-apply-the-per-unit-nameplate) | 5 <!--parts HSM-000001--> |
| Cap the inlets + photograph | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 <!--parts HSM-000001--> |
| Make up the customer's runs; pack the install kit, the cold kit and the carton | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 10 <!--parts HSM-000341:5 HSM-000342:1 HSM-000340:4--> |
| Weigh, label, hand off | [finish-pack-ship](/hardware/assembly/finish-pack-ship.md) | | 5 <!--parts HSM-000340--> |
| **Finishing & packing** | | | **[35](LAB_SEC10)** |

## Totals

| Section | Time | At [$100](LABOR_RATE)/h |
|---|---:|---:|
| 1. Machining | [55 m](LAB_HM1) | [$91.67](LAB_USD1) |
| 2. Welding & brazing | [1 h 2 m](LAB_HM2) | [$103.33](LAB_USD2) |
| 3. Pressure, leak & flow checks | [1 h](LAB_HM3) | [$100.00](LAB_USD3) |
| 4. Silicone casting | [35 m](LAB_HM4) | [$58.33](LAB_USD4) |
| 5. Foam pouring | [35 m](LAB_HM5) | [$58.33](LAB_USD5) |
| 6. Wiring | [2 h 20 m](LAB_HM6) | [$233.33](LAB_USD6) |
| 7. Plumbing | [1 h 10 m](LAB_HM7) | [$116.67](LAB_USD7) |
| 8. Assembly | [2 h 53 m](LAB_HM8) | [$288.00](LAB_USD8) |
| 9. Power-on & testing | [55 m](LAB_HM9) | [$91.67](LAB_USD9) |
| 10. Finishing & packing | [35 m](LAB_HM10) | [$58.33](LAB_USD10) |
| **Per-unit total** | **[12 h](LAB_HM)** | **[$1,199.67](LAB_USD)** |

The target is 10 hours attended per unit. The current estimate is [12 h](LAB_HM), including 20 minutes of unmeasured recurring jet work. The largest attended-time categories are:

- **Assembly** ([2 h 53 m](LAB_HM8), the largest category) — [1 h 18 m](LAB_HM_PRINTED) of it is the printed parts, most of that the plate turns of the large parts that fill a plate each. More printers shorten the print, not the plate turns.
- **Wiring** ([2 h 20 m](LAB_HM6)) — 90 minutes for eleven finished bench harnesses and 50 minutes for installation and AC checks. Ready maps, a cut list and staged crimping and soldering tools support the practiced unit-25 estimates.
- **Machining** — the four hand-tapped NPT ports are the slowest five minutes each in the build.

## Not counted here

- **Pump-dock manufacturing allowance** — the pump tube preparation is a required production operation. Its attended time is unmeasured and excluded from these totals.
- **Unattended process time** — every hour a machine is busy and nobody is on it. That is its own ledger: [machine-time.md](/hardware/ledger/machine-time.md), which holds the print, the cures and bakes, the hydro and vacuum holds, the passivation soak, the chill-down and the burn-in, and derives turnaround and throughput from them. Nothing there is costed.
- **Shipping and receiving** — unpacking orders, kitting, inventory.
- **Design, CAD, firmware and documentation** — this file costs building a unit, not developing one.
- **Initial jet-process qualification** — destructive weld coupons, fixture development, purge qualification and setting the production flow band are development work. Recurring drilling, welding, cleaning and inspection remain in the per-unit rows above.
- **Contract labor already capitalized in dollars** — JLCPCB assembly of the main board, SendCutSend's cutting. Those arrive as parts and are priced in [bom.md](/hardware/ledger/bom.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_bom_sync.py`
- `/hardware/scripts/_labor_totals.py`

Every operation also carries a hidden `<!--parts …-->` tag after its minutes, naming the part numbers the work makes or puts together; [`materials.md`](/hardware/ledger/materials.md#costs) says how its minutes are divided among them.
