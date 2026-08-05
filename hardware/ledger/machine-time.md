# Machine Time — One Consumer Unit

Hours a **machine** is occupied per finished appliance, not hours a person is. The third ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts) and [labor.md](/hardware/ledger/labor.md) (what it costs in attended time). **Nothing here is costed.** It answers two questions money does not:

- **Turnaround** — how long one unit takes end to end, from a cold start.
- **Throughput** — how many the shop can make in a year with the machines it owns.

Where labor.md counts only the minutes a person is *on* an operation, this file counts everything they are *off*: the print, the cure, the bake, the soak, the hold, the burn-in. The two files are complements and share no rows.

**The print rate is measured, not assumed.** The cold-core inner shell sliced at **1142.47 g / [14 h 22 m](MT_MEASURED)** on an H2C — 0.8 nozzle, 0.4 layer, PETG, 21 mm³/s volumetric cap, 15 % infill ([foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)). Against that part's [1.325](MT_MEASURED_KG) kg geometry mass in [bom.md](/hardware/ledger/bom.md) §7 that is **[10.8](MT_RATE_BULK) hours per geometry-kg**, and it is the one hard number the whole print estimate stands on. The other three rates below are that rate scaled for a slower configuration; they are estimates and are marked as such.

Masses come from bom.md §7, which is geometry-derived and commit-gated, so a printed part cannot change shape without moving the figure here. `_machine_time.py --check` fails if a §7 row is not assigned to a rate group.

## 1. Printing

[2](MT_PRINTERS) × Bambu Lab H2C ([tools.md](/hardware/ledger/tools.md)). The four groups are the four print configurations the build actually uses — a part's rate is set by nozzle, layer height and wall count, not by what it is.

| Group | Parts | Rate | Mass | Hours |
|---|---|---|---:|---:|
| Bulk PETG, 0.8 nozzle | Cold-core shell, both enclosure sets, four foam-cap pieces | [10.8](MT_RATE_BULK) h/kg — **measured** | [6.021](MT_KG_BULK) kg | [65.0](MT_H_BULK) |
| Watertight translucent PETG | Both reservoir bodies + caps — 3 mm walls, Arachne, fine nozzle for a syrup-tight wall ([watertight-petg.md](/hardware/printed-parts/cold-core/reservoir/watertight-petg.md)) | [22](MT_RATE_TIGHT) h/kg — est., ~½ the bulk volumetric rate | [0.880](MT_KG_TIGHT) kg | [19.4](MT_H_TIGHT) |
| Small PETG parts | Valve trays, drip pan, plug stack, PRV shroud, AC hub plate, reed bridge | [30](MT_RATE_SMALL) h/kg — est., travel and layer-change overhead dominate a small part | [0.230](MT_KG_SMALL) kg | [6.9](MT_H_SMALL) |
| PET-CF, 0.4 nozzle | Faucet touch-flo shell + mounting plate — fine layers, 50 °C chamber, hardened nozzle | [60](MT_RATE_PETCF) h/kg — est. | [0.163](MT_KG_PETCF) kg | [9.8](MT_H_PETCF) |
| **Printer time per unit** | | | **[7.294](MT_KG)** kg | **[101.1](MT_H_PRINT)** |

Spread across [2](MT_PRINTERS) machines that is **[50.5](MT_H_PRINT_WALL) hours** of wall clock, and it is the longest pole in the build by an order of magnitude.

Filament drying is not per-unit: the AMS 2 Pro dries PETG in place and feeds the print from the same unit, so PETG costs no separate cycle. PET-CF is dried [12 h at 85 °C](MT_PETCF_DRY) per spool, not per build.

## 2. Curing and baking

| Process | Machine | Notes | Hours |
|---|---|---|---:|
| Silicone funnel — room-temperature cure to demold | The mold | BBDINO 40A, per [hopper-funnel-mold](/hardware/printed-parts/zone-c/hopper-funnel-mold/README.md) | 5.0 |
| Silicone funnel — food-contact post-cure bake | Oven at ~200 °C | The drive-off bake is the food-contact acceptance gate, not the room-temp cure | 4.0 |
| Body foam — pour to trimmable | In the part | Cure time is an **open item** in [cold-core.md](/hardware/assembly/cold-core.md); 4 h is a placeholder for a 2 lb pour foam, not a datasheet figure | 4.0 |
| Cap foams — pour to trimmable, both caps | In the part | Same open item; the two caps pour together | 4.0 |
| PRV-shroud caulk — full cure | Bench shelf | ≥24 h for 100 % RTV, but the subassembly is built ahead and shelves indefinitely — off the critical path | 24.0 |
| **Curing and baking** | | | **[41.0](MT_H_CURE)** |

## 3. Soaking and holding

| Process | Machine | Notes | Hours |
|---|---|---|---:|
| Dye-penetrant dwell + develop-and-read | Bench | ~10 min dwell, read within ~10 min | 0.3 |
| Hydro test — 180 PSI hold | Hydro rig | The 30-minute minimum; the SENCTRL gauge supports hour-scale soaks beyond it | 0.5 |
| Citric passivation soak | Polycarbonate tub | 30–60 min; batched across vessels | 1.0 |
| Refrigerant vacuum — pump-down + two 15-minute holds | Vacuum pump | Pull to 500 µm, valve off, read the rise, repeat | 0.8 |
| **Soaking and holding** | | | **[2.6](MT_H_SOAK)** |

## 4. Running

| Process | Machine | Notes | Hours |
|---|---|---|---:|
| First chill-down — tap water to service temperature | The unit | Tens of minutes to first compressor-off, longer than the steady-state cycle that follows | 1.0 |
| Burn-in | Test bench | The ≥8-hour window, one metered dispense every 75 minutes; firmware logs it and the operator checks in three times | 8.0 |
| **Running** | | | **[9.0](MT_H_RUN)** |

## Throughput

The printers are the constraint and nothing else is close. Per unit:

| Machine | Occupied per unit | Units/year at 100 % | |
|---|---:|---:|---|
| [2](MT_PRINTERS) × H2C | [50.5](MT_H_PRINT_WALL) h wall | [173](MT_CEIL_PRINT) | **the bottleneck** |
| Test bench (burn-in + chill) | [9.0](MT_OCC_BENCH) h | [973](MT_CEIL_BENCH) | |
| Funnel mold + oven | [9.0](MT_OCC_MOLD) h | [973](MT_CEIL_MOLD) | |
| Hydro rig, passivation tub, vacuum pump | [2.6](MT_OCC_VESSEL) h | [3,369](MT_CEIL_VESSEL) | |

At [65 %](MT_DUTY) machine duty — failed prints, plate changes, filament swaps, maintenance, the hours nobody is in the shop to restart a plate — the printers give **[~112](MT_UNITS_YEAR) units a year**. A third H2C moves that to [~169](MT_UNITS_YEAR_3); nothing else bought moves it at all.

## Turnaround — one unit, cold start

What one unit takes end to end if production is unpaused and the shop starts empty. Only work that cannot overlap is on this path; everything else is parallel to it and named below.

| Stage | Hours | |
|---|---:|---|
| Print every part | [50.5](MT_H_PRINT_WALL) | 2 printers, both on this unit |
| Build the cold core; pour the foam and let it cure | 8.0 | vessel already done, in parallel with the prints |
| Assembly, plumbing, wiring | 8.0 | one working day |
| Power-on and test | 2.0 | |
| First fill and chill-down | 1.0 | |
| Burn-in | 8.0 | |
| Finish and pack | 1.0 | |
| **Turnaround** | **[78.5](MT_H_TURN)** | **[3.3](MT_DAYS_TURN) days** |

Runs in parallel with the print, and so costs no turnaround at all: the whole pressure-vessel chain (machining, welding, PT, hydro, passivation, fittings), the twelve harnesses, the silicone funnel's cure and bake, and the PRV-shroud subassembly with its 24-hour caulk cure. Each of those has to be *started* early enough, which is a scheduling problem, not a duration one.

A second unit behind the first does not cost another [3.3](MT_DAYS_TURN) days — it costs the bottleneck's [50.5](MT_H_PRINT_WALL) hours, since its prints start the moment the first unit's come off the plates.

## Open items

1. **Foam cure time.** [cold-core.md](/hardware/assembly/cold-core.md) open item 2 — mix proportions, pot life, cure time and pour temperature window are all still unread from the datasheet. The 4 h rows in §2 are placeholders; the real figure changes the turnaround, not the throughput.
2. **The three estimated print rates.** Only the bulk-PETG rate is measured. The reservoir plate has been sliced twice ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) but Bambu Studio wrote no per-plate estimate into either 3MF, so the watertight rate is still inferred. Record the slicer's time on the next slice of each group and these become measurements.
3. **Print failure rate.** The [65 %](MT_DUTY) duty figure carries it implicitly. A measured scrap rate would separate "the printer was idle" from "the printer printed something that went in the bin".

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_machine_time.py`
