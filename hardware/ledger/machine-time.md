# Machine Time — One Consumer Unit

Hours a **machine** is occupied per finished appliance, not hours a person is. The third ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts) and [labor.md](/hardware/ledger/labor.md) (what it costs in attended time). **Nothing here is costed.** It answers two questions money does not:

- **Turnaround** — how long one unit takes end to end, from a cold start.
- **Throughput** — how many the shop can make in a year with the machines it owns.

Where labor.md counts only the minutes a person is *on* an operation, this file counts everything they are *off*: the print, the cure, the bake, the soak, the hold, the burn-in. The two files are complements and share no rows.

**The print rates are measured, not assumed.** Two slices carry the estimate, one per bulk configuration, and each one reports its own hours and its own filament off the same plate.

- **Cold-core, 0.8 nozzle.** The inner shell sliced at **379.99 m / [14 h 22 m](MT_MEASURED)** on an H2C — 0.4 layer, PETG, 21 mm³/s volumetric cap, 15 % infill ([foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)). Against that part's [1.126](MT_MEASURED_KG) kg in [bom.md](/hardware/ledger/bom.md) §7 that is **[12.8](MT_RATE_BULK) hours per kg**.
- **Enclosure exterior, 0.4 nozzle.** The front-top sliced at **213.06 m / [20 h 23 m](MT_MEASURED_EXT)** on an H2C — 0.24 layer, 0.42 mm outer wall, **PET-GF15**, 18 mm³/s, 15 % infill, tree supports ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)). Against that piece's [0.653](MT_MEASURED_EXT_KG) kg in §7 that is **[31.2](MT_RATE_EXT) hours per kg**. Measured in the stock the exterior ships in, so nothing is carried across a density or a volumetric cap to reach it.

The other three rates below are the cold-core rate scaled for a slower configuration; they are estimates and are marked as such.

**A kg here is filament, not geometry.** bom.md §7 bills what a slice of each part lays — the wall loops plus the sparse grid between them, at the settings of the plate that part comes off ([`_bom_masses.py`](/hardware/scripts/_bom_masses.py) `PROFILES`) — and the two rates above are measured against that same figure. What §7 leaves out is the plate's scaffolding: supports, brim and purge are filament, and the front-top's tree supports are about 11 % of its slice. The rate carries them anyway, because it is hours per §7-kg and the hours it was measured over included them.

Masses come from §7, which is commit-gated, so a printed part cannot change shape without moving the figure here. The rate groups are §7's own — `_machine_time.py` imports `_bom_masses.GROUP_OF` rather than keeping a second copy — and `--check` fails if a §7 row is not in it.

## 1. Printing

[2](MT_PRINTERS) × Bambu Lab H2C ([tools.md](/hardware/ledger/tools.md)). The five groups are the five print configurations the build actually uses — a part's rate is set by nozzle, layer height and wall count, not by what it is.

| Group | Parts | Rate | Mass | Hours |
|---|---|---|---:|---:|
| Bulk PETG, 0.8 nozzle | Cold-core shell, four foam-cap pieces | [12.8](MT_RATE_BULK) h/kg — **measured** | [1.706](MT_KG_BULK) kg | [21.8](MT_H_BULK) |
| Enclosure exterior PET-GF, 0.4 TC | The four quadrants, the pump cartridge and its cap, the ceiling panel and the display cover plate — the show surfaces, printed at the finish the box is judged on ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)) | [31.2](MT_RATE_EXT) h/kg — **measured** | [2.946](MT_KG_EXT) kg | [91.9](MT_H_EXT) |
| Watertight translucent PETG, 0.6 nozzle | Both reservoir bodies + caps — 3 mm walls as 5 × 0.60 mm beads, Arachne, for a syrup-tight wall ([watertight-petg.md](/hardware/printed-parts/cold-core/reservoir/watertight-petg.md)); the nozzle is the one all three logged runs were made on ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) | [26](MT_RATE_TIGHT) h/kg — est., ~½ the bulk volumetric rate | [0.880](MT_KG_TIGHT) kg | [22.9](MT_H_TIGHT) |
| Small PETG parts | ASSE drip pan, plug stack, PRV shroud, reed bridge, fuse clamp | [36](MT_RATE_SMALL) h/kg — est., travel and layer-change overhead dominate a small part | [0.107](MT_KG_SMALL) kg | [3.9](MT_H_SMALL) |
| Faucet PET-GF, 0.4 TC | Faucet shell, its display cover plate and the above-counter plate — fine layers, 50 °C chamber, supported the whole height ([faucet-shell/print-log.md](/hardware/printed-parts/faucet/faucet-shell/print-log.md)) | [70](MT_RATE_PETGF) h/kg — est. | [0.204](MT_KG_PETGF) kg | [14.3](MT_H_PETGF) |
| **Printer time per unit** | | | **[5.843](MT_KG)** kg | **[154.8](MT_H_PRINT)** |

Spread across [2](MT_PRINTERS) machines that is **[77.4](MT_H_PRINT_WALL) hours** of wall clock, and it is the longest pole in the build by an order of magnitude.

Filament drying is not per-unit: the AMS 2 Pro dries PETG in place and feeds the print from the same unit, so PETG costs no separate cycle. PET-GF15 is dried [10 h at 100 °C](MT_PETGF_DRY) per spool, not per build, and feeds the print from a PolyDryer Box XL ([tools.md](/hardware/ledger/tools.md) "What dries where").

## 2. Curing and baking

| Process | Machine | Notes | Hours |
|---|---|---|---:|
| Silicone funnel — room-temperature cure to demold | The mold | BBDINO 40A, per [funnel-mold](/hardware/printed-parts/zone-c/funnel-mold/README.md) | 5.0 |
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
| [2](MT_PRINTERS) × H2C | [77.4](MT_H_PRINT_WALL) h wall | [113](MT_CEIL_PRINT) | **the bottleneck** |
| Test bench (burn-in + chill) | [9.0](MT_OCC_BENCH) h | [973](MT_CEIL_BENCH) | |
| Funnel mold + oven | [9.0](MT_OCC_MOLD) h | [973](MT_CEIL_MOLD) | |
| Hydro rig, passivation tub, vacuum pump | [2.6](MT_OCC_CARBONATOR) h | [3,369](MT_CEIL_CARBONATOR) | |

At [65 %](MT_DUTY) machine duty — failed prints, plate changes, filament swaps, maintenance, the hours nobody is in the shop to restart a plate — the printers give **[~73](MT_UNITS_YEAR) units a year**. A third H2C moves that to [~110](MT_UNITS_YEAR_3); nothing else bought moves it at all.

## Turnaround — one unit, cold start

What one unit takes end to end if production is unpaused and the shop starts empty. Only work that cannot overlap is on this path; everything else is parallel to it and named below.

| Stage | Hours | |
|---|---:|---|
| Print every part | [77.4](MT_H_PRINT_WALL) | 2 printers, both on this unit |
| Build the cold core; pour the foam and let it cure | 8.0 | carbonator already done, in parallel with the prints |
| Assembly, plumbing, wiring | 8.0 | one working day |
| Power-on and test | 2.0 | |
| First fill and chill-down | 1.0 | |
| Burn-in | 8.0 | |
| Finish and pack | 1.0 | |
| **Turnaround** | **[105.4](MT_H_TURN)** | **[4.4](MT_DAYS_TURN) days** |

Runs in parallel with the print, and so costs no turnaround at all: the whole carbonator chain (machining, welding, PT, hydro, passivation, fittings), the twelve harnesses, the silicone funnel's cure and bake, and the PRV-shroud subassembly with its 24-hour caulk cure. Each of those has to be *started* early enough, which is a scheduling problem, not a duration one.

A second unit behind the first does not cost another [4.4](MT_DAYS_TURN) days — it costs the bottleneck's [77.4](MT_H_PRINT_WALL) hours, since its prints start the moment the first unit's come off the plates.

## Open items

1. **Foam cure time.** [cold-core.md](/hardware/assembly/cold-core.md) open item 2 — mix proportions, pot life, cure time and pour temperature window are all still unread from the datasheet. The 4 h rows in §2 are placeholders; the real figure changes the turnaround, not the throughput.
2. **The three estimated print rates.** The two bulk rates are measured; the watertight, small-parts and faucet rates are not. The reservoir plate has been sliced twice ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) but Bambu Studio wrote no per-plate estimate into either 3MF, so the watertight rate is still inferred. Record the slicer's time on the next slice of each group and these become measurements.
3. **The small-parts group names no nozzle, and two bounds are held to a wall without one.**
   Every other group here names one: cold-core bulk 0.8 (measured,
   [foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)), enclosure
   exterior 0.4 TC (measured,
   [enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)), watertight
   0.6 (measured, three runs), faucet PET-GF 0.4. The small-parts group — ASSE drip pan, plug stack, PRV
   shroud, reed bridge, fuse clamp — has no print log and no chosen nozzle, so a bead width for
   those parts does not exist in this tree. Two constants stand on one anyway:
   `copper_plugs.min_printable_thickness` = 1.0, whose bound is labelled "Every plug leaves a
   **printable** wall standing between its arches", and `_cold_core_interface.port_lane_wall` =
   1.5, whose comment says below it "the wall between two features stops being printable". Neither
   is wrong — both clear one bead on any nozzle this shop runs — but neither is held either, and a
   label that says printable reads as though it were. The figure to copy is
   `faucet_shell.display_line_width` = 0.62, which is its own part's bead on a group that names
   its nozzle.
4. **Print failure rate.** The [65 %](MT_DUTY) duty figure carries it implicitly. A measured scrap rate would separate "the printer was idle" from "the printer printed something that went in the bin".

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_machine_time.py`
