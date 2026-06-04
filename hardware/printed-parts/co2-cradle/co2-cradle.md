# CO2 cradle — instrumented cylinder platform

A free-standing platform the customer's CO2 cylinder stands in, inside the under-sink cabinet, so the appliance can read remaining CO2 by weight. It is two printed parts plus one off-the-shelf load cell: a grounded **base** on three feet, a floating **well** the cylinder drops into, and a single-point load cell that is the only structural bridge between them. The appliance reads the cell through an HX711 24-bit ADC on a spare ESP32 ADC channel; firmware turns grams-remaining into the depletion gauge and the dispense lockout.

The platform stands beside the enclosure in the cabinet side-gap, on the cabinet floor, and connects to the appliance only by the load-cell signal cable — nothing on the appliance touches the cylinder. That isolation is the whole measurement: the only load path from cylinder to cabinet floor runs cylinder → well → load cell → base → feet, so a cylinder leaning on the well wall, or the CO2 tether tugging the regulator, adds a lateral force the cell does not see.

## World frame

`+Z` up; the cylinder axis runs up `+Z` at the origin `(x, y) = (0, 0)`; `z = 0` is the foot-contact plane (cabinet floor). The load cell bar lies along world `X`, its fixed end toward `−X` and its free (load) end toward `+X`. The regulator/tether notch in the well rim faces `+Y`, toward the front-panel CO2 inlet.

## Well — the floating cup

The well is an open-top cup the cylinder drops into. It accepts a [127 mm](CYL_D) ⌀ 5 lb aluminum CGA-320 cylinder with a [4 mm](SEAT_CLEAR) radial drop-in clearance, so the bore is ⌀[135 mm](WELL_ID) and the outer wall ⌀[142 mm](WELL_OD) at a [3.5 mm](WALL_T) wall. The floor is [6 mm](FLOOR_T) thick — it carries the full cylinder weight into the free-end riser beneath it. The wall rises [110 mm](WELL_WALL_H) above the interior floor: tall enough to capture a roughly 18-inch cylinder against leaning, short enough to drop the cylinder in without lifting it over a tall collar. The wall captures the cylinder laterally only; it bears no vertical load.

A notch [46 mm](NOTCH_W) wide × [45 mm](NOTCH_DEPTH) deep is cut into the `+Y` rim for the regulator body and the CO2 tether to exit, doubling as the orientation index so the cylinder seats the same way every time. Three drain holes through the floor (clear of the cell footprint below) let water out — under-sink is a wet zone, and the floor must never hold a puddle around the cylinder base.

On its underside the well carries the **free-end riser**: a boss that hangs down to the load cell's free (`+X`) end and bolts to it. This is the single point at which the well's weight — cylinder included — is delivered to the cell.

## Base — the grounded reference

The base is a ⌀[158 mm](BASE_OD) disc on **three feet** at 120°. Three points seat flat on any cabinet floor with no rock — a four-foot base rocks on a bowed particleboard floor, which both noises up the reading and wobbles a tall cylinder. The feet lift the plate [10 mm](FOOT_H) off the floor for drainage and leveling clearance.

On top of the base: a **fixed-end pedestal** that the load cell's `−X` end bolts down to, and two **travel-stop pads** flanking the cell in `±Y`. The cell mounts in the classic single-point couple — fixed end anchored low to the base, free end carrying the well high — with [8 mm](CELL_AIR_GAP) of air under the free end and over the fixed end so the bar can bend. The travel-stop pads rise to within [2 mm](TRAVEL_GAP) of the well underside: under an overload (a cylinder dropped into the well, someone leaning on it), the well floor lands on the pads before the bar deflects past its rating. Impact force is several times static weight, so the stop is not optional.

## Load cell

A single-point / platform "bar" load cell — long axis along world `X`, modelled here at the [80 mm](CELL_L) × [12.7 mm](CELL_W) × [12.7 mm](CELL_H) envelope of a 20 kg Geekstory cell ([B079FQNJJH](https://www.amazon.com/dp/B079FQNJJH), HX711 included). Single-point cells read accurately regardless of where on the platform the load sits, which is what lets the cylinder be off-center in the well without skewing the reading. The 20 kg capacity sits at ~30 % of rating under a full 5 lb cylinder (~6 kg gross); the travel-stop guards the drop-in impact case. The HX711 amplifier pairs to a spare ESP32 ADC channel.

## What this gives the appliance

A smooth, continuous "grams remaining" signal — not the binary cliff a supply-pressure transducer would give — and it is temperature-independent (cylinder warming from the condenser side does not move a mass reading). A mass step-up of ~2.3 kg is an unambiguous cylinder-swap event the firmware detects on its own, so the customer never resets anything: they set the new cylinder in the well and reconnect, exactly the gesture they already make.

## Open items

- [ ] **Load-cell envelope + bolt pattern confirm-against-part.** `CELL_L/W/H`, the end-bolt pitch, and the M5 fastener (heat-set insert vs. direct-tapped PETG) are modelled to a generic 20 kg single-point cell. Measure the actual Geekstory cell and pin the riser/pedestal hole pattern to it.
- [ ] **HX711 + cable mount.** The electronics mount, conformal-coat/sealing against the under-sink wet zone, the strain-relieved 4-wire lead, and the keyed appliance-panel connector are not yet placed on the base. The cable run must reach either cabinet side (cylinder parks on the condenser-intake side by preference — cooler, less cell drift).
- [ ] **Drainage detailing.** Floor drain holes pass water onto the base; whether the base needs its own sloped drainage or the three-foot stand simply drips to the cabinet floor (as any leak would) is unsettled. Keep the HX711 out of the drip path.
- [ ] **Factory calibration.** The cell is calibrated once at burn-in with known weights, stored as per-unit cal data — no customer calibration. Calibration procedure + storage location TBD; ties into the burn-in flow.
- [ ] **Anti-tip.** An optional upper strap to the appliance for earthquake/bump security must engage with clearance only — a load-bearing strap would short the measurement. Geometry deferred to the side-face exterior surface doc.
- [ ] **10 lb cylinder.** This part is sized for 5 lb only. A 10 lb cylinder (~7.25" ⌀) needs a larger well + likely a 50 kg cell; out of scope here.
- [ ] **Single-point moment / platform-size rating.** A tall cylinder cantilevered off one free-end mount loads the cell in a way bounded by its rated platform size. Confirm the ⌀[142 mm](WELL_OD) well is within the chosen cell's rating, or step to a 50 kg cell.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/co2-cradle/co2_cradle.py`
