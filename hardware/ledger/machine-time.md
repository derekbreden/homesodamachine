# Machine Time — One Consumer Unit

Hours a **machine** is occupied per finished appliance, not hours a person is. The third ledger beside [bom.md](/hardware/ledger/bom.md) (what a unit costs in parts) and [labor.md](/hardware/ledger/labor.md) (what it costs in attended time). **Nothing here is costed.** It answers two questions money does not:

- **Turnaround** — how long one unit takes end to end, from a cold start.
- **Throughput** — how many the shop can make in a year with the machines it owns.

Where labor.md counts only the minutes a person is *on* an operation, this file counts everything they are *off*: the print, the cure, the bake, the soak, the hold, the burn-in. The two files are complements and share no rows.

**The print rates stand on two slices**, one per bulk configuration, and each one reports its own hours and its own filament off the same plate. A slice is a plate, not a row: the kg beside each is what §7's shell-plus-infill model bills for **the solid that plate was taken from**, so a part that later changes shape moves its own mass without disturbing the rate it is priced at.

- **Cold-core, 0.8 nozzle.** The inner shell sliced at **379.99 m / [14 h 22 m](MT_MEASURED)** on an H2C — 0.4 layer, PETG, 21 mm³/s volumetric cap, 15 % infill ([foam-shell/print-log.md](/hardware/printed-parts/cold-core/foam-shell/print-log.md)). That plate bills [1.126](MT_MEASURED_KG) kg on §7's model, so it ran at **[12.8](MT_RATE_BULK_PETG) hours per kg of PETG**.
- **Enclosure exterior, 0.4 nozzle.** The front-top sliced at **213.06 m / [20 h 23 m](MT_MEASURED_EXT)** on an H2C — 0.24 layer, 0.42 mm outer wall, **PET-GF15**, 18 mm³/s, 15 % infill, tree supports ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)). That plate bills [0.653](MT_MEASURED_EXT_KG) kg, so **[31.2](MT_RATE_EXT) hours per kg**. Measured in the stock the exterior ships in, so nothing is carried across a density or a volumetric cap to reach it.

**A rate in hours per kg does not survive a stock change.** A nozzle lays grams at (volumetric cap × density), so hours per kg move by the inverse of that product. The cold core ships in **PET-GF15** ([bom.md](/hardware/ledger/bom.md) §7) and the plate that was timed ran PETG, so the bulk rate is that measurement carried across 18 mm³/s at 1.43 g/cm³ against 21 at 1.27 — [3.6 %](MT_PETGF_CARRY) more hours for every kg, and the kg is itself the bigger one. This is the historical nozzle/stock reference used for the unsliced small-part estimates. The full shell uses its current production native slice; the cap/lid estimates use that shell's hours per kilogram.

The watertight, small-parts, solid PET-GF and ring-and-collar rates below are the **measured plate's own** [12.8](MT_RATE_BULK_PETG) h/kg scaled for a slower configuration — a scaling of the setup and not of the stock, which is why they hang off the measurement rather than off the carried figure. They are estimates and are marked as such. The shell duration and feed mass come directly from its production native slice. The faucet duration comes directly from its committed [production-profile slice](/hardware/printed-parts/faucet/faucet-petgf.support-audit.json), including supports and brim. Its displayed hours per kg divides that duration by the BOM's estimated part mass; it does not extrapolate the faucet's print time. The ASA Aero floats use their own [v1 native slice](/hardware/printed-parts/cold-core/magnetic-float/all-aero/mark2-print/v1/float-preflight.json), multiplied by the float quantity in BOM §12. That slice estimates the 3.40 mm pocket article; the current 3.60 mm pocket requires a separate v2 slice. Derek's wait at each RC62 insertion pause is unmeasured and excluded from these totals.

**A kg here is filament, not geometry.** bom.md §7 bills what a slice of each part lays — the wall loops plus the sparse grid between them, at the settings of the plate that part comes off ([`_bom_masses.py`](/hardware/scripts/_bom_masses.py) `PROFILES`) — and the two rates above are measured against that same figure. What §7 leaves out is the plate's scaffolding: supports, brim and purge are filament, and the front-top's tree supports are about 11 % of its slice. The rate carries them anyway, because it is hours per §7-kg and the hours it was measured over included them.

The groups take masses from §7 using `_bom_masses.GROUP_OF`. The ASA Aero group reads the object-feed mass from the same v1 slice as its time. That feed estimate excludes startup waste and magnet mass and does not establish the finished float's density or buoyancy. The funnel cover uses the time per kilogram from its identified [unsent native slice](/hardware/printed-parts/zone-c/funnel-cover/native-slice-review.json), with that slice's feed mass normalized from its 1.25 g/cm³ profile density to the BOM's 1.27 g/cm³ PETG density. Current cover geometry is unsliced; its duration is a mass-scaled estimate. All printer, turnaround and throughput figures here are production estimates; physical print yield, plate handling, the float's v2 slice and manual pauses remain outside the current timing evidence.

## 1. Printing

[2](MT_PRINTERS) × Bambu Lab H2C ([tools.md](/hardware/ledger/tools.md)). The timed groups cover the shipped PET-GF, PETG and ASA Aero parts. The small TPU seals have unmeasured durations and remain excluded. A part's rate follows its nozzle, layer height, wall count and material recipe.

| Group | Parts | Rate | Mass | Hours |
|---|---|---|---:|---:|
| Cold-core shell PET-GF, left 0.4 Standard | Full smooth 2.38 mm shell, round copper exits, three Classic loops, A2 scarf and wipe off ([production preparation](/hardware/printed-parts/cold-core/foam-shell/prints/2026-10-26-mark2-round-ports-a2/README.md)) | [21.8](MT_RATE_SHELL) h/kg — native duration; rate shown for comparison | [1.450](MT_KG_SHELL) kg | [31.6](MT_H_SHELL) |
| Cold-core caps/lids PET-GF, left 0.4 Standard | Four smooth foam-cap and lid pieces, three Classic loops and 15% gyroid | [21.8](MT_RATE_BULK) h/kg — estimate from the current shell slice | [0.831](MT_KG_BULK) kg | [18.1](MT_H_BULK) |
| Enclosure exterior PET-GF, 0.4 TC | The four quadrants with front-top's integral upper pump mount, the lower pump retainer, display cover plate, funnel frame and its drain-elbow cradle — the enclosure mechanisms and show surfaces printed at the finish the box is judged on ([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)) | [31.2](MT_RATE_EXT) h/kg — **measured** | [3.472](MT_KG_EXT) kg | [108.3](MT_H_EXT) |
| Watertight translucent PETG, 0.6 nozzle | Both reservoir bodies + caps — 3 mm walls as 5 × 0.60 mm beads, Arachne, for a syrup-tight wall ([watertight-petg.md](/hardware/printed-parts/cold-core/reservoir/watertight-petg.md)); the nozzle is the one all three logged runs were made on ([reservoir/print-log.md](/hardware/printed-parts/cold-core/reservoir/print-log.md)) | [26](MT_RATE_TIGHT) h/kg — est., ~½ the measured plate's volumetric rate | [0.872](MT_KG_TIGHT) kg | [22.7](MT_H_TIGHT) |
| Small PETG parts | Umbilical organizer, PRV shroud, reed bridge and fuse clamp | [36](MT_RATE_SMALL) h/kg — est., travel and layer-change overhead dominate a small part | [0.061](MT_KG_SMALL) kg | [2.2](MT_H_SMALL) |
| Small solid PET-GF parts, 0.4 TC | The install-kit collet press — at least six walls and 100% infill ([collet press](/hardware/printed-parts/collet-press/README.md)) | [36](MT_RATE_TOOL) h/kg — est., the small-part rate until its production slice is logged | [0.017](MT_KG_TOOL) kg | [0.6](MT_H_TOOL) |
| Rings and collars PET-GF, two 0.4 nozzles | Six compact rear labels and six tube collars, each in its station's colour with contrasting lettering; 0.24 mm layers ([rear-identification/README.md](/hardware/printed-parts/enclosure/rear-identification/README.md), [tube-collar/README.md](/hardware/printed-parts/faucet/tube-collar/README.md)) | [36](MT_RATE_RINGS) h/kg — est., the small-part rate; current compact labels unsliced | [0.036](MT_KG_RINGS) kg | [1.3](MT_H_RINGS) |
| Faucet and nameplate PET-GF, 0.4 TC | Faucet shell, lever, display cover, above-counter plate and serial nameplate; 0.24 mm layers, two wall loops and 15 % grid ([faucet-petgf.md](/hardware/printed-parts/faucet/faucet-petgf.md)) | [32.7](MT_RATE_PETGF) h/kg — duration from saved-profile slice | [0.141](MT_KG_PETGF) kg | [4.6](MT_H_PETGF) |
| ASA Aero floats, right 0.4 HS | [3](MT_FLOAT_QTY) one-piece floats, carbonator + two reservoirs; RC62 inserted during printing, 0.20 mm layers and nested perimeters ([float record](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md)) | [88.3](MT_FLOAT_MINUTES) min each — v1 native slice estimate, manual pause excluded; v2 unsliced | [0.042](MT_KG_AERO) kg | [4.4](MT_H_AERO) |
| Funnel cover, black PETG, left 0.4 nozzle | Solid removable plate and locating skirt ([cover recipe](/hardware/printed-parts/zone-c/funnel-cover/README.md)) | [14](MT_RATE_FUNNEL_COVER) h/kg — estimate from the reference native slice; current geometry unsliced | [0.134](MT_KG_FUNNEL_COVER) kg | [1.9](MT_H_FUNNEL_COVER) |
| **Known printer-time subtotal per unit** | | | **[7.056](MT_KG)** kg | **[195.7](MT_H_PRINT)** |

Spread across [2](MT_PRINTERS) machines, the known subtotal is **[97.9](MT_H_PRINT_WALL) hours** of estimated wall clock.

Filament drying is per spool: the AMS 2 Pro dries and feeds the [1.07](MT_KG_PETG_UNIT) kg PETG allocation. PET-GF15 is dried [10 h at 100 °C](MT_PETGF_DRY) and feeds from a PolyDryer Box XL ([tools.md](/hardware/ledger/tools.md) "What dries where"). ASA Aero uses its own drying cycle and the sealed external drybox route recorded in the [float recipe](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md).

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
| Burn-in | Test bench | The ≥8-hour window, one metered dispense every 75 minutes; firmware logs it and Derek checks in three times | 8.0 |
| **Running** | | | **[9.0](MT_H_RUN)** |

## Throughput

The printers are the constraint in this estimate. Per unit, before unmeasured RC62-pause delays:

| Machine | Occupied per unit | Units/year at 100 % | |
|---|---:|---:|---|
| [2](MT_PRINTERS) × H2C | [97.9](MT_H_PRINT_WALL) h wall | [90](MT_CEIL_PRINT) | **the bottleneck** |
| Test bench (burn-in + chill) | [9.0](MT_OCC_BENCH) h | [973](MT_CEIL_BENCH) | |
| Funnel mold + oven | [9.0](MT_OCC_MOLD) h | [973](MT_CEIL_MOLD) | |
| Hydro rig, passivation tub, vacuum pump | [2.6](MT_OCC_CARBONATOR) h | [3,369](MT_CEIL_CARBONATOR) | |

At [65 %](MT_DUTY) assumed machine duty — failed prints, plate changes, filament swaps, maintenance, the hours nobody is in the shop to restart a plate — the modeled output is **[~58](MT_UNITS_YEAR) units a year**. A third H2C gives [~87](MT_UNITS_YEAR_3) on the same rates and allocation assumptions. This is an estimate until the selected recipes have physical production results and plate handling, small TPU seals, pump tube preparation and pause handling have production timings.

## Turnaround — one unit, cold start

What one unit takes end to end if production is unpaused and the shop starts empty. Only work that cannot overlap is on this path; everything else is parallel to it and named below.

| Stage | Hours | |
|---|---:|---|
| Print the timed parts | [97.9](MT_H_PRINT_WALL) | 2 printers, both on this unit |
| Build the cold core; pour the foam and let it cure | 8.0 | carbonator already done, in parallel with the prints |
| Assembly, plumbing, wiring | 8.0 | one working day |
| Power-on and test | 2.0 | |
| First fill and chill-down | 1.0 | |
| Burn-in | 8.0 | |
| Finish and pack | 1.0 | |
| **Turnaround** | **[125.9](MT_H_TURN)** | **[5.2](MT_DAYS_TURN) days** |

Pump tube preparation and the small TPU seals have unmeasured production durations; plate handling and physical print yield remain unmeasured.

Runs in parallel with the print when started early enough: the whole carbonator chain (machining, welding, PT, hydro, passivation, fittings), the eleven bench harnesses, the silicone funnel's cure and bake, and the PRV-shroud subassembly with its 24-hour caulk cure. Each of those has to be *started* early enough, which is a scheduling problem, not a duration one.

A second unit behind the first does not cost another [5.2](MT_DAYS_TURN) days — it costs the bottleneck's [97.9](MT_H_PRINT_WALL) hours, since its prints start the moment the first unit's come off the plates.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_machine_time.py`
