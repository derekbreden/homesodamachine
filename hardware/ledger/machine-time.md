# Machine Time — One Consumer Unit

Hours a **machine** is occupied per finished appliance, not hours a person is. The third ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts) and [labor.md](/hardware/ledger/labor.md) (what it costs in attended time). **Nothing here is costed.** It answers two questions money does not:

- **Turnaround** — how long one unit takes end to end, from a cold start.
- **Throughput** — how many the shop can make in a year with the machines it owns.

Where labor.md counts only the minutes a person is *on* an operation, this file counts everything they are *off*: the print, the cure, the bake, the soak, the hold, the burn-in. The two files are complements and share no rows.

**The print rates stand on two slices**, one per bulk configuration, and each one reports its own hours and its own filament off the same plate. A slice is a plate, not a row: the kg beside each is what §7's shell-plus-infill model bills for **the solid that plate was taken from**, so a part that later changes shape moves its own mass without disturbing the rate it is priced at.

- **Cold-core, 0.8 nozzle.** The inner shell sliced at **379.99 m / [14 h 22 m](MT_MEASURED)** on an H2C — 0.4 layer, PETG, 21 mm³/s volumetric cap, 15 % infill ([foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)). That plate bills [1.126](MT_MEASURED_KG) kg on §7's model, so it ran at **[12.8](MT_RATE_BULK_PETG) hours per kg of PETG**.
- **Enclosure exterior, 0.4 nozzle.** The front-top sliced at **213.06 m / [20 h 23 m](MT_MEASURED_EXT)** on an H2C — 0.24 layer, 0.42 mm outer wall, **PET-GF15**, 18 mm³/s, 15 % infill, tree supports ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)). That plate bills [0.653](MT_MEASURED_EXT_KG) kg, so **[31.2](MT_RATE_EXT) hours per kg**. Measured in the stock the exterior ships in, so nothing is carried across a density or a volumetric cap to reach it.

**A rate in hours per kg does not survive a stock change.** A nozzle lays grams at (volumetric cap × density), so hours per kg move by the inverse of that product. The cold core ships in **PET-GF15** ([bom.md](/hardware/ledger/bom.md) §7) and the plate that was timed ran PETG, so the bulk rate is that measurement carried across 18 mm³/s at 1.43 g/cm³ against 21 at 1.27 — [3.6 %](MT_PETGF_CARRY) more hours for every kg, and the kg is itself the bigger one. It is an estimate until a PET-GF plate of the shell is sliced.

The watertight, small-parts, collet-press and ring-and-collar rates below are the **measured plate's own** [12.8](MT_RATE_BULK_PETG) h/kg scaled for a slower configuration — a scaling of the setup and not of the stock, which is why they hang off the measurement rather than off the carried figure. They are estimates and are marked as such. The faucet duration comes directly from its committed [production-profile slice](/hardware/printed-parts/faucet/faucet-petgf.support-audit.json), including supports and brim. Its displayed hours per kg divides that duration by the BOM's estimated part mass; it does not extrapolate the faucet's print time. The ASA Aero floats use their own [v1 native slice](/hardware/printed-parts/cold-core/magnetic-float/all-aero/mark2-print/v1/float-preflight.json), multiplied by the float quantity in BOM §12. That slice estimates the 3.40 mm pocket article; the current 3.60 mm pocket requires a separate v2 slice. Operator wait at each RC62 insertion pause is unmeasured and excluded from these totals.

**A kg here is filament, not geometry.** bom.md §7 bills what a slice of each part lays — the wall loops plus the sparse grid between them, at the settings of the plate that part comes off ([`_bom_masses.py`](/hardware/scripts/_bom_masses.py) `PROFILES`) — and the two rates above are measured against that same figure. What §7 leaves out is the plate's scaffolding: supports, brim and purge are filament, and the front-top's tree supports are about 11 % of its slice. The rate carries them anyway, because it is hours per §7-kg and the hours it was measured over included them.

Eight groups take masses from §7, which is commit-gated, and `_machine_time.py` imports `_bom_masses.GROUP_OF`; `--check` fails if a §7 row is not assigned. The ASA Aero group reads the object-feed mass from the same v1 slice as its time. That feed estimate excludes startup waste and magnet mass and does not establish the finished float's density or buoyancy. The funnel cover takes its duration from its own [unsent native slice](/hardware/printed-parts/zone-c/funnel-cover/native-slice-review.json). All printer, turnaround and throughput figures here are production estimates; the float's v2 slice and manual pauses remain outside the current timing evidence.

## 1. Printing

[2](MT_PRINTERS) × Bambu Lab H2C ([tools.md](/hardware/ledger/tools.md)). The nine groups cover the shipped PET-GF, PETG and ASA Aero parts. A part's rate follows its nozzle, layer height, wall count and material recipe.

| Group | Parts | Rate | Mass | Hours |
|---|---|---|---:|---:|
| Cold-core PET-GF, 0.8 TC | Cold-core shell, four foam-cap pieces — the stack the box's own fluted skin is carried onto, printed on the big nozzle rather than the exterior's fine one ([foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)) | [13.3](MT_RATE_BULK) h/kg — est., the [12.8](MT_RATE_BULK_PETG) measured plate carried across the stock | [2.493](MT_KG_BULK) kg | [33.2](MT_H_BULK) |
| Enclosure exterior PET-GF, 0.4 TC | The four quadrants, the lower pump cradle and its top clamp, display cover plate, funnel frame and its drain-elbow cradle — the enclosure mechanisms and show surfaces printed at the finish the box is judged on ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)) | [31.2](MT_RATE_EXT) h/kg — **measured** | [3.478](MT_KG_EXT) kg | [108.5](MT_H_EXT) |
| Watertight translucent PETG, 0.6 nozzle | Both reservoir bodies + caps — 3 mm walls as 5 × 0.60 mm beads, Arachne, for a syrup-tight wall ([watertight-petg.md](/hardware/printed-parts/cold-core/reservoir/watertight-petg.md)); the nozzle is the one all three logged runs were made on ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) | [26](MT_RATE_TIGHT) h/kg — est., ~½ the measured plate's volumetric rate | [0.890](MT_KG_TIGHT) kg | [23.1](MT_H_TIGHT) |
| Small PETG parts | ASSE drip pan, plug stack, PRV shroud, reed bridge, fuse clamp — one plate holds them all, and the three cold-core ones are the parts the PET-GF stack closes over | [36](MT_RATE_SMALL) h/kg — est., travel and layer-change overhead dominate a small part | [0.052](MT_KG_SMALL) kg | [1.9](MT_H_SMALL) |
| Collet press PET-GF, 0.4 TC | The supportless install-kit tool — 0.24 mm layers, at least six walls and a solid dense core ([collet-press/README.md](/hardware/printed-parts/collet-press/README.md)) | [36](MT_RATE_TOOL) h/kg — est., the small-part rate until its first slice is logged | [0.017](MT_KG_TOOL) kg | [0.6](MT_H_TOOL) |
| Rings and collars PET-GF, two 0.4 nozzles | Five bulkhead rings and five tube collars, each in its station's colour with its word off the black or the white spool — two colours to a plate, the rings face up on the nameplate's 0.24 mm profile ([bulkhead-ring/README.md](/hardware/printed-parts/enclosure/bulkhead-ring/README.md), [tube-collar/README.md](/hardware/printed-parts/faucet/tube-collar/README.md)) | [36](MT_RATE_RINGS) h/kg — est., the small-part rate until a plate of all ten is sliced | [0.034](MT_KG_RINGS) kg | [1.2](MT_H_RINGS) |
| Faucet PET-GF, 0.4 TC | Faucet shell, its display cover plate and the above-counter plate — four pieces on one plate, 0.24 mm layers, two wall loops and 15 % grid ([faucet-petgf.md](/hardware/printed-parts/faucet/faucet-petgf.md)) | [32.7](MT_RATE_PETGF) h/kg — duration from saved-profile slice | [0.138](MT_KG_PETGF) kg | [4.5](MT_H_PETGF) |
| ASA Aero floats, right 0.4 HS | [3](MT_FLOAT_QTY) one-piece floats, carbonator + two reservoirs; RC62 inserted during printing, 0.20 mm layers and nested perimeters ([float record](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md)) | [88.3](MT_FLOAT_MINUTES) min each — v1 native slice estimate, manual pause excluded; v2 unsliced | [0.042](MT_KG_AERO) kg | [4.4](MT_H_AERO) |
| Funnel cover, black PETG, left 0.4 nozzle | Solid removable plate and locating skirt ([cover recipe](/hardware/printed-parts/zone-c/funnel-cover/README.md)) | [14.6](MT_RATE_FUNNEL_COVER) h/kg — duration from the unsent native slice | [0.103](MT_KG_FUNNEL_COVER) kg | [1.5](MT_H_FUNNEL_COVER) |
| **Printer time per unit** | | | **[7.247](MT_KG)** kg | **[178.9](MT_H_PRINT)** |

Spread across [2](MT_PRINTERS) machines that is **[89.5](MT_H_PRINT_WALL) hours** of wall clock, and it is the longest pole in the build by an order of magnitude.

Filament drying is per spool: the AMS 2 Pro dries and feeds the [1.04](MT_KG_PETG_UNIT) kg PETG allocation. PET-GF15 is dried [10 h at 100 °C](MT_PETGF_DRY) and feeds from a PolyDryer Box XL ([tools.md](/hardware/ledger/tools.md) "What dries where"). ASA Aero uses its own drying cycle and the sealed external drybox route recorded in the [float recipe](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md).

## 2. Curing and baking

| Process | Machine | Notes | Hours |
|---|---|---|---:|
| Silicone funnel — room-temperature cure to demold | The mold | BBDINO 40A: the maker's 5 h to demold at 23 °C, per [silicone.md](/hardware/printed-parts/zone-c/funnel-mold/silicone.md). Full use at 24 h; a cool shop lengthens both | 5.0 |
| Silicone funnel — food-contact post-cure bake | Oven at ~200 °C | The drive-off bake is the food-contact acceptance gate, not the room-temp cure. **The maker states no post-cure schedule** ([silicone.md](/hardware/printed-parts/zone-c/funnel-mold/silicone.md)); 4 h at ~200 °C is a placeholder, under the cured material's 230 °C ceiling, until the trial is run | 4.0 |
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

The printers are the constraint in this estimate. Per unit, before unmeasured magnet-pause delays:

| Machine | Occupied per unit | Units/year at 100 % | |
|---|---:|---:|---|
| [2](MT_PRINTERS) × H2C | [89.5](MT_H_PRINT_WALL) h wall | [98](MT_CEIL_PRINT) | **the bottleneck** |
| Test bench (burn-in + chill) | [9.0](MT_OCC_BENCH) h | [973](MT_CEIL_BENCH) | |
| Funnel mold + oven | [9.0](MT_OCC_MOLD) h | [973](MT_CEIL_MOLD) | |
| Hydro rig, passivation tub, vacuum pump | [2.6](MT_OCC_CARBONATOR) h | [3,369](MT_CEIL_CARBONATOR) | |

At [65 %](MT_DUTY) assumed machine duty — failed prints, plate changes, filament swaps, maintenance, the hours nobody is in the shop to restart a plate — the modeled output is **[~64](MT_UNITS_YEAR) units a year**. A third H2C gives [~95](MT_UNITS_YEAR_3) on the same rates and allocation assumptions. This is an estimate until the selected recipes and pause handling have production timings.

## Turnaround — one unit, cold start

What one unit takes end to end if production is unpaused and the shop starts empty. Only work that cannot overlap is on this path; everything else is parallel to it and named below.

| Stage | Hours | |
|---|---:|---|
| Print every part | [89.5](MT_H_PRINT_WALL) | 2 printers, both on this unit |
| Build the cold core; pour the foam and let it cure | 8.0 | carbonator already done, in parallel with the prints |
| Assembly, plumbing, wiring | 8.0 | one working day |
| Power-on and test | 2.0 | |
| First fill and chill-down | 1.0 | |
| Burn-in | 8.0 | |
| Finish and pack | 1.0 | |
| **Turnaround** | **[117.5](MT_H_TURN)** | **[4.9](MT_DAYS_TURN) days** |

Runs in parallel with the print, and so costs no turnaround at all: the whole carbonator chain (machining, welding, PT, hydro, passivation, fittings), the twelve harnesses, the silicone funnel's cure and bake, and the PRV-shroud subassembly with its 24-hour caulk cure. Each of those has to be *started* early enough, which is a scheduling problem, not a duration one.

A second unit behind the first does not cost another [4.9](MT_DAYS_TURN) days — it costs the bottleneck's [89.5](MT_H_PRINT_WALL) hours, since its prints start the moment the first unit's come off the plates.

## Open items

1. **Foam cure time.** [cold-core.md](/hardware/assembly/cold-core.md) open item 2 — mix proportions, pot life, cure time and pour temperature window are all still unread from the datasheet. The 4 h rows in §2 are placeholders; the real figure changes the turnaround, not the throughput.
2. **The four scaled print rates.** Watertight, small-parts, collet-press and ring-and-collar rates remain estimates. The faucet uses its own saved-profile slice duration; the cold-core PET-GF rate is carried from its PETG measurement. The reservoir plate has been sliced twice ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) but Bambu Studio wrote no per-plate estimate into either 3MF, so the watertight rate is still inferred. Record the slicer's time on the next slice of each group and these become measurements.
3. **The small-parts group names no nozzle, and two bounds are held to a wall without one.**
   Every other group here names one: cold-core bulk 0.8 (measured,
   [foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)), enclosure
   exterior 0.4 TC (measured,
   [enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)), watertight
   0.6 (measured, three runs), collet press PET-GF 0.4, rings and collars PET-GF 0.4, faucet PET-GF 0.4. The small-parts group — ASSE drip pan, plug stack, PRV
   shroud, reed bridge, fuse clamp — has no print log and no chosen nozzle, so a bead width for
   those parts does not exist in this tree. Two constants stand on one anyway:
   `copper_plugs.min_printable_thickness` = 1.0, whose bound is labelled "Every plug leaves a
   **printable** wall standing between its arches", and `_cold_core_interface.port_lane_wall` =
   1.5, whose comment says below it "the wall between two features stops being printable". Neither
   is wrong — both clear one bead on any nozzle this shop runs — but neither is held either, and a
   label that says printable reads as though it were. The faucet's saved [print project](/hardware/printed-parts/faucet/faucet-petgf.md) names
   its 0.4 mm nozzle, 0.42 mm outer wall and 0.45 mm inner wall lines.
4. **Print failure rate.** The [65 %](MT_DUTY) duty figure carries it implicitly. A measured scrap rate would separate "the printer was idle" from "the printer printed something that went in the bin".
5. **ASA Aero production duration.** The current float has 0.20 mm more upper pocket clearance than the identified v1 slice. Its native v2 duration and the elapsed pause for each of the [3](MT_FLOAT_QTY) inserted magnets are unmeasured. The v1 contribution is a provisional allowance, not an accepted production recipe or a completed-job timing.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_machine_time.py`
