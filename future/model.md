# The model

What the machine should do, worked from physics and written down before the test that checks
it. A result inside its band confirms the model; a result outside names the assumption to
change. [`repo-tools model`](/tools/hsm/repo-tools/src/model.rs) computes every figure here from the
inputs below and from the constants the firmware, the faucet and enclosure CAD and the
pressure-vessel and acceptance procedures use. It runs when someone asks, never on a commit or
in the build.

The dispense side comes first. The [Lillium-fed build](/hardware/assembly/lillium-cutover.md)
pours through the appliance's own flavor side, meter, umbilical, faucet and firmware, with the
Lillium where the cold core will stand, so what it measures is the appliance's except for the
carbonator. Each quantity below ends with what carries over.

## The build

The [Lillium](https://liliumfaucet.com/products/under-sink-carbonated-soda-maker-sparkling-water-dispenser-with-3-way-faucet)
chills and carbonates the water, fed CO2 from a 5 lb cylinder through the TAPRITE E-T742
regulator. Blue 1/4" LLDPE carries it to the enclosure's TAP bulkhead, across the deck to the
DIGITEN meter (FL-S402BZJ, [B07QRXLRTH](https://www.amazon.com/dp/B07QRXLRTH)), out the SODA
bulkhead and up the umbilical's blue tube into the Westbrass valve inside the white faucet. The
lever opens its spring poppet, and a 3/8" tube carries the water up the printed gooseneck to the
tip. Two Kamoer KPHM600-SW3B17 pumps in the pump cradle draw each flavor from its reservoir
in the foam shell and push it up the umbilical's flavor runs to the same tip; the two meet in
the glass. The main board drives each pump through a DRV8870 bridge from the Mean Well
IRM-90-12ST, and runs the pour in
[`machine_policy::pourCycleTiming`](/firmware/lib/machine_policy/pour_policy.h): it counts meter
pulses in windows and bursts the pump on a duty set by that count and the
channel's ratio setting.

| Input | Value the model uses | Where it comes from, and how to read it |
|---|---|---|
| CO2 at the regulator | | Lillium's [manual](https://drive.google.com/file/d/1eYFbMV6QgwXx7Ien0929jW30y2Q_zHd5/view) asks 0.45–0.55 MPa at its CO2 inlet. Read the E-T742's low-pressure gauge. |
| Lillium water at rest | | Lillium claims 3–5 °C; its display read 00 °C in the March under-cabinet photo (tag `prototype-doc-last-known`). Read the display. |
| Tap water | | Probe the kitchen cold tap after 30 s of running. |
| Room | | Probe the air beside the faucet. |
| The can's fridge | | Probe a glass of water that spent the night in it. |
| Lillium to the TAP bulkhead | of 1/4" LLDPE, bore, the Lillium's own tube out of its bath included | Tape-measure. The bore is the [scanned sample](/hardware/reference/lldpe-tubes/README.md). |
| TAP to the meter | | Cut on the parts ([cutover](/hardware/assembly/lillium-cutover.md) §3); measure it. |
| Meter to SODA, umbilical, gooseneck | of `carb-2`, the blue tube, of 3/8" tube at | The [assembly facts](/hardware/manifold-layout/enclosure-assembly.facts.json) and the [faucet assembly](/hardware/faucet-layout/faucet_assembly.rs). |
| Water standing ahead of the tip | | Those runs, in the meter and in the Westbrass body. |
| Drinking glass | | Weigh one of the matching glasses. |
| Ratio setting | | The machine display, or `ratio` on the console. |
| Pump | | KPHM600-SW3B17, [BOM](/hardware/ledger/bom.md) §8. |
| Meter | pulses a second per L/min | The listing gives 38; one buyer's calibration found 36. |
| Atmosphere | | Lincoln. |
| Glass of soda | | Twelve ounces, as [acceptance](/hardware/assembly/acceptance-and-burn-in.md) pours. |

A range is this page's assumption until the sink says otherwise. Read the inputs before the
tests and pin each one, `repo-tools model --set regulator_psi=72`
and so on; the page then carries the narrowed prediction, committed before the pour that tests
it. Each figure is the median of the draws with the middle 80 % in brackets.

## 1. Carbonation in the glass

Water holds CO2 in proportion to the CO2 pressure over it, more when colder: Henry's law, here
Weiss's fresh-water solubility with the fugacity correction, the formulation
[pressure vessel](/hardware/assembly/pressure-vessel.md) uses. The CO2 pressure is the
regulator's gauge pressure plus the local atmosphere, less water vapour and the air the
headspace collects. Tap water brings air in and only dissolved air leaves, so an unvented
carbonator's air settles near ([Carbonation Plan B](/future/carbonation-plan-b.md));
the model takes of that level.

A carbonator does not reach equilibrium. A refill takes up part of it as it lands: fountain
carbonators deliver about half, which is what US4745853's numbers imply as Plan B reads them,
and the model assumes. Still water then takes CO2 only through its surface.
CO2-rich water is denser and sinks, and that slow convection is assumed to take
. So a night's idle carbonates the water the first glass draws further
than a refill does, and a run of glasses dilutes the carbonator with fresh refill. The pour
loses CO2 past the poppet seat and in the fall: to a bottle filled at the tip,
a further into a glass and on to a bottle later.

| What is measured | Prediction |
|---|---|
| Equilibrium at the regulator and the Lillium's temperature | |
| A refill as it lands | |
| The carbonator after a night | |
| **First glass of the morning, in the glass** | |
| **Fourth glass of a one-a-minute run, in the glass** | |
| Sixth draw, a bottle filled at the tip | |

The model expects the first glass of the day to hold more CO2 than the
fourth. Lillium's own claim, more than 6.7 g/L or 3.4 volumes in the first cup, sits inside the
first-glass band.

**Carries over:** everything after the carbonator. The appliance pours through this valve, tube
and tip into the same glass, so the tip and glass losses measured here are its losses. Its
carbonator holds the feed, whose equilibrium is in
[pressure vessel](/hardware/assembly/pressure-vessel.md), and its refill transfer is its own
jet's.

## 2. Drink temperature

The carbonator rests at the Lillium's bath temperature. A glass draws from it, and the refill
lands after the glass, because the Lillium's pump refills slower than a pour draws. The refill
is tap water that has lost of its difference from the bath on the way in.
The carbonator is taken as well mixed, (Lillium sells 1 L per draw),
pulled back toward the bath at.

The first glass of a session also carries the water that stood ahead of the tip at room
temperature, and the heat of the of brass in the Westbrass body and its
tube stiffener. Between glasses that standing water warms back toward the room with a
 time constant. A room-temperature glass gives the drink part of its own
heat; after the pour the drink holds of what it would take at
equilibrium.

Plain water, each glass a matching room-temperature glass, read after the lever
closes:

| Glass | Prediction |
|---|---|
| 1, first of the morning |; the stream before the glass, |
| 2, on | |
| 3, on | |
| 4, on | |
| 5, later | |
| A can from the fridge, the same glass, the same reading | |
| Flavor at the predicted ratio adds | |

The model expects the first glass warmer than the second, the third and fourth climbing as
refills dilute the carbonator, and the can colder than every glass unless the Lillium's water
sits near 0 °C. [Acceptance](/hardware/assembly/acceptance-and-burn-in.md) asks for
≤ in the glass.

**Carries over:** the appliance's water stands in its `carb-1` run from the core, the meter,
the umbilical and the gooseneck tube,, and crosses the same
brass. Its first glass carries the same warm term unless the design removes it.

## 3. Syrup ratio

The firmware sets the pump's on and off times from the meter's count per window, clamped at
: at that count and the default ratio.
That is the pump running of the time against the
that count of pulses means, so the shape gives 1:20 for a pump that moves
 while it runs. The KPHM600 is rated, and
three things set what it delivers:

- **The pump's speed.** A brushed motor's speed follows its voltage less the armature's own
  drop. The DRV8870's switches, J13 and the leads take
  at the pump's current, so the motor sees
  and the head turns at of its rated
  speed.
- **Each burst loses its spin-up**, assumed of every on-time.
- **The count is truncated.** Each cycle is timed from the integer average of the last cycle's
  windows, so a flow between counts gets the lower count's duty. Above the clamp the duty stays
  at while the water keeps rising. At full lever this build's flow sits right
  at the clamp, so whether a cycle counts one below it or reaches it moves the dose by.

Back pressure is the rise to the tip and the friction of the umbilical's flavor runs, a few kPa
against a head built for far more; the model allows up to of slip. Diet
concentrate in reservoirs at cabinet temperature is close to water's viscosity and does not
slow the head at these speeds; sugared concentrate in the appliance's chilled reservoirs is
where viscosity would enter. A refractometer reads dissolved solids by mass, so the drink reads
the concentrate's °Brix times the concentrate's mass share of the drink.

| What is measured | Prediction |
|---|---|
| Meter count per window at full lever | |
| Prime: the pump running continuously into a cup | |
| `flow 6` for into a cup, lever closed | |
| `flow 5` for | |
| `flow 3` for | |
| **Full-lever glass, water to concentrate by volume** | |
| Drink °Brix as a share of the concentrate's |; a true reads |
| Lever half open | |

The model expects a full-lever glass near the label and a gentle one well short of it.

**Carries over:** this is the appliance's flavor side, so its ratio follows the same physics.
Its lower feed pours less water, which moves the count per window, and the model puts its
full-lever glass at.

## 4. Seconds to fill a 12 oz glass

The carbonator's pressure, less the rise to the faucet tip, drives the
water through the friction of each run above and the losses of the Lillium's outlet path and
the two bulkhead unions ( velocity heads of the 1/4" tube), the meter
 and the faucet (: the tube stiffener, the poppet seat,
the body's turns, and the bubbles that form past the seat).

| What is measured | Prediction |
|---|---|
| Flow, lever fully open | |
| **12 oz** | |

**Carries over:** at the appliance's feed, through its own runs and
the same losses, the glass fills in.

## The tests

### To buy

Each is an Amazon Prime listing. The Smart Weigh scale, the AstroAI multimeter, the SENCTRL
gauge and the Kill-A-Watt are already in [tools](/hardware/ledger/tools.md); the Rubbermaid
thermometer reads 60–580 °F, too warm for a cold drink.

| Item | Purpose | Price |
|---|---|---:|
| [Lavatools Javelin PRO Classic](https://www.amazon.com/dp/B017NGZIXW) | Probe thermometer, 0.1° display, for the glasses, the can, the tap and the fridge | $42.99 |
| [Flagfront digital Brix refractometer, 0–55 %, ±0.1 %](https://www.amazon.com/dp/B0C49P92J1) | °Brix of the concentrate and of each poured glass | $32.39 |
| [MRbrew spunding valve, ball-lock gas disconnect, 0–60 psi gauge](https://www.amazon.com/dp/B0GTL22HLH) | The carbonation tester's gauge; its pull ring vents the headspace | $26.99 |
| [Ball-lock carbonation caps, 4-pack](https://www.amazon.com/dp/B0DGT98J66) | One per sample bottle, so each sample is capped the moment it is poured | $14.95 |
| [500 mL PET bottles with caps, 24-pack](https://www.amazon.com/dp/B0B28B3C36) | Sample bottles, 28 mm PCO neck, made for carbonated drinks | $36.95 |
| [Diet Mountain Dew, 12 fl oz can](https://www.amazon.com/dp/B01DSYHNDQ) | The reference can; one from any store serves | $12.10 |

### Test 1: the ratio

**What it decides.** Whether the pour shape can keep a fixed pump rate and its truncated pulse
average, or needs each pump's measured rate and an unrounded average. The same code and pumps
pour in the appliance. Acceptance step 6's on the total
cannot see the ratio: 1:20 and 1:10 differ by. The cups and the
refractometer can.

**Setup.** The Lillium-fed build pouring, reservoirs primed. The Smart Weigh, a cup, the phone's
stopwatch, four glasses, the refractometer. The main board's console on USB for step 3, while
it can be reached.

**Procedure and readings.**

1. Read the flavor's ratio setting.
2. Lever closed, hold Prime on the machine display for 10 s by the stopwatch with the tared cup
   under the tip; weigh it. Three times.
3. On the console, lever closed, the tared cup under the tip: `flow 6 20`, `flow 5 20` and
   `flow 3 20`, weighing the cup after each. The firmware runs its pour against each count with
   no water moving.
4. Pour four glasses with the lever fully open, timing each from lever open to close. Weigh each
   glass empty and full.
5. With the refractometer, zeroed on tap water: a drop of neat concentrate, then each glass
   after it has gone flat and warmed past 10 °C, inside the instrument's temperature
   compensation. Then one glass poured with the lever half open, read the same way.

Stop if a reservoir runs low enough for its pump to draw air.

**What would break the model.**

- Prime outside: the pump's speed or its spread.
- Prime inside its band but the `flow` cups outside theirs: the spin-up each burst loses.
- The cups inside but the glasses' °Brix share above or below
 : the meter's count per window, which the console's pour line shows in the
  first cycle's on and off times, or the full-lever flow, which step 4's times and weights give.
- °Brix share disagreeing with what the cups and the flow imply: the refractometer's reading
  below 1 °Brix. A 1:20 mix made by mass on the scale checks it.

### Test 2: the morning run

**What it decides.** Whether the first glass's warm water and brass, which the appliance shares,
need a design answer before the appliance can match the can; whether a run of glasses holds its
carbonation, which sets how much transfer the appliance's jet owes (Plan B's fading and
successive-glass rows); whether the poppet seat loses enough CO2 to need a gentler path;
and what fill time the appliance's lower feed will give.

**Setup, the evening before.**

- Read the regulator, the Lillium's display, the room, the tap, the fridge, and the two runs
  ahead of the meter; weigh a glass; pin them in the model.
- Check the thermometer in stirred ice water: it should read 0.0 °C; note any offset.
- Six matching glasses at room temperature, each weighed empty, with a tape mark at the level
  of water reaches.
- Four sample bottles: each weighed empty with its carbonation cap, then filled to overflowing,
  capped and weighed; the difference is its volume. Emptied and dried.
- Unplug the machine's cord. Its valves are normally closed, so the faucet pours plain Lillium
  water and no concentrate moves.
- No pour for the before the first glass.

**Procedure and readings.** One stopwatch runs from the first glass.

1. At 0 s, glass 1: lever fully open to the tape mark, timed. Probe to mid-depth without
   stirring; read after the lever closes. At pour the glass
   slowly down the inside of a tilted bottle to its shoulder, cap it at once, set it in ice
   water.
2. At and, glasses 2 and 3: pour to the mark, timed; read at
  ; weigh.
3. At, glass 4: as glass 1, into the second bottle.
4. At, glass 5: as glasses 2 and 3. later fill the third bottle
   straight from the tip, tilted so the stream runs down its inside wall, to the shoulder; cap
   it.
5. The can, from the fridge: open, pour down the middle of the sixth glass as the faucet pours,
   read at, into the fourth bottle at.
6. Each bottle, after at least 10 minutes in ice water: weigh it; attach the gauge; shake hard
   30 s and read; pull the ring until the needle drops near zero; shake 30 s and read; pull it
   again; shake until the needle stops rising and read. Take the gauge off, open the cap, probe
   the liquid.
7. `repo-tools model volumes <final psi> <°C> --liquid-g <g>
   --bottle-ml <mL> --snift <first> --snift <second>` gives each sample's volumes.

Fill time is the lever time scaled to by each weighed glass. Keep the
bottles cold: a sample read warm passes the gauge's 60 psi. Stop at any hiss or weep from the
Lillium or its fittings.

**What would break the model.**

- Glass 1 colder than predicted while the rest agree: less warm water or brass than assumed;
  measure the runs.
- Glass 2 well below glass 1 and flat through glass 4: the carbonator does not mix, and refills
  sit on top. Glasses climbing faster than predicted: a smaller carbonator, a weaker bath, or no
  precooling.
- Fill slower than: larger losses than assumed. The SENCTRL on a push-fit tee
  at the SODA bulkhead, read while pouring, splits the runs ahead of it from the umbilical and
  faucet.
- The first and fourth glasses alike: refill transfer is higher, or still-water absorption
  faster, than assumed. The tip bottle far above the fourth glass: the glass loses more than
  assumed, and the can's pour has to match the faucet's for a fair comparison. Every sample low:
  the regulator reading or the headspace's air.

### What to run first

Test 1, as soon as the Lillium-fed build pours. Its prime and console steps need only the scale
and a cup, and the answer feeds the firmware the appliance will run; the refractometer finishes
it. Test 2 needs the thermometer and the carbonation kit.

## Not modelled yet

What else decides whether the appliance pours daily for a month, each with the records and
procedures that already touch it.

| Concern | What the model would predict | Records and procedures |
|---|---|---|
| Pressure safety and burst margin | The welded carbonator's failure pressure and where it fails, predicted and then broken on a sacrificial vessel; the owned BEAMNOVA hydro pump reaches 726 psi | [pressure vessel](/hardware/assembly/pressure-vessel.md) (penetrant, 180 psi × 30 min hydro, SV-125 at 125 psi), [water-inlet jet](/hardware/assembly/water-inlet-jet.md) (root fusion); Lillium's manual gives its own carbonator a 2 MPa test and a 1.1–1.5 MPa valve |
| Leaks and creep over a month | Which joints relax: push-fit O-rings under the CO2 feed, printed reservoir caps on TPU gaskets, pump tubes clamped in their heads | [acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md) (eight-hour burn-in over a towel), [mechanical qualification](/hardware/mechanical-qualification/README.md) "Retained clamping force", concerns "Reservoir watertightness", "Joints buried by the foam", "Water on the cabinet floor", "A leak while nobody is home" |
| Refrigeration pull-down, duty cycle and power | Hours from a warm fill to setpoint, compressor duty at a day's draw, kWh a month | [refrigerant loop](/hardware/assembly/refrigerant-loop.md), acceptance's compressor duty band, the [enclosure](/hardware/printed-parts/enclosure/README.md)'s cabinet heat estimate, [`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h), the Kill-A-Watt, concerns "Cabinet doors shut" |
| Condensation | Where cold surfaces cross the cabinet's dew point and where the water goes | concerns "Condensation" and "Moisture into the foam", [internal plumbing](/hardware/assembly/internal-plumbing.md) (riser insulation), [faucet and umbilical](/hardware/assembly/faucet-and-umbilical.md) (foam ends), mechanical qualification "Insulation thickness"; the Lillium collects its own condensate in its drip tray |
| Insert pull-out and structure | Pull-out and torque-out of the heat-set inserts in PET-GF, and the 4–6 inch drop | mechanical qualification "Screw diameter and insert anchorage", "Short-drop retention", "Infill and deposited structure", [`core-and-faucet-heatsets.json`](/hardware/mechanical-qualification/core-and-faucet-heatsets.json), concerns "Heat-set insert seats", "A 4–6 inch drop splitting the midsection", "Lifting by the handholds" |

## Results

No test has run. Each result lands here with its date, the readings, the inputs pinned for it
and the band it was predicted in.
