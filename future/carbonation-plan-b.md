# Carbonation Plan B

The first unit uses the G Ganen B07F35PTFR diaphragm pump, Mean Well
IRM-90-12ST supply, existing enclosure, and the four-port carbonator made with two
identical plates. Water enters through the top Port 2 elbow's
[water-inlet jet](/hardware/assembly/water-inlet-jet.md); CO2 enters through the
plain bottom Port 1 opening. The trial jet is a 1/16-inch (1.5875 mm) bore through
a nominal 2 mm thick 316 cap. Its fit and full root fusion must be qualified by
the fabrication procedure. Carbonation performance is established on the built
machine by [acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md).

These are conditional responses to that final qualification, not additional
parts in the production BOM. Strong carbonation and cold successive glasses
are the required result. A pressure setting or an on-hand component does not
substitute for that result.

## Record the actual operating point

Keep the current refill sequence: dispense first, refill with the faucet closed.
Record the following together for the initial fill, a normal refill, and the
successive-glass sequence. A measurement without its pressure, temperature and
timing context cannot distinguish the failure modes below.

| Measurement | What it separates |
|---|---|
| Static house pressure and flowing pressure at the pump inlet, after the filter, backflow preventer and V-K | Available municipal assistance versus an inlet restriction |
| Pump discharge pressure and carbonator pressure throughout refill; actual switch cut-out and restart | Pump pressure rise, downstream losses and compression of the gas space |
| Starting/ending level, refill volume and elapsed time | Delivered flow at the operating pressure, including a stall or repeated switch cycling |
| Voltage at the pump and supply, pump current and total 12 V load | Hydraulic shortfall versus wiring drop or supply current limit |
| Incoming-water, carbonator-wall and immediate in-glass temperatures; recovery time | Carbonation transfer versus loss of cold water under successive demand |
| Primary regulator setting, gas-feed pressure, initial purge/conditioning, idle time and pour cadence | CO2 partial pressure and contact history; trapped air is not CO2 |
| First-glass and successive-glass carbonation under the same dispense conditions | The product result, preferably with dissolved-CO2 measurement and always against an agreed taste reference |

Use a rated temporary bench fixture at existing line connections for pressure
measurements; record gauge locations and accuracy. Keep the dedicated PRV port
and its vent unobstructed. The fixture is bench tooling, not another carbonator
port. Its connections and instrumentation still need to be specified: the one
owned SENCTRL gauge cannot capture all three pressures at once, so additional
gauges or transducers may be needed. The [purchases ledger](/hardware/ledger/purchases.md) records an acquired
Mean Well LRS-200-12 (12 V, 17 A), available to isolate a supply limitation on the
bench. It is not the production supply. The G Ganen B07F35PTFR from order
112-0884852-3444230 is the selected diaphragm pump; the IEIK B07YXTHNRQ from the
same order is a measurement sample. Begin with the
[received-part dimensional record](/hardware/reference/pump-comparison/README.md).
Both pumps' labels, operating curves, pressure limits and wetted suitability
still require verification; no hydraulic reading of either is recorded.

## Read the pressures correctly

Positive house pressure reduces the pressure rise the pump must produce. For
example, 50 psig at its inlet and 100 psig at its outlet is a 50 psi rise. The
pump's outlet pressure switch still stops it near its outlet setting; a 50 psi
house supply does not raise that setting by 50 psi. Measure the actual cut-out
and restart with the installed inlet pressure. The G Ganen's listing advertises
110 psi and 4.5 L/min. That is not a curve, and not a measured one for this
machine's pressurized inlet, tubing, checks and jet.

The WR1105 holds incoming CO2 at nominally 43.5 psig, its etched 3 bar. It
does not hold the carbonator there while water compresses the sealed gas space.
At the current level stations, a nominal 338 mL refill reduces headspace from
about 872 to 534 mL; if the incoming water absorbed none of the trapped gas,
the fill would end near 80 psig, under the pump's nominal 100 psi switch. How
far pressure actually rises depends on CO2 uptake during the fill as well as
temperature. Gas admission pauses when its forward pressure difference
disappears; the plain inlet is not a continuous bubbler. A pump cutting out
before CHI is a real pressure-margin failure even when water flowed briskly at
the start. A relief-valve event requires finding the pressure source; it does
not identify a regulator fault by itself.

Most house supplies stand above the 43.5 psig feed. Tap pressure alone then
drives water through the idle pump and jet whenever V-K opens, and V-K's seat
is all that holds it out between refills. A leaking V-K fills the carbonator
past CHI until the headspace reaches house pressure, and the drink goes flat.

The headspace is not all CO2. Air dissolved in the tap water comes out into it
and leaves only dissolved in the water dispensed, so it builds until the
outgoing water carries what the incoming water brings: about 11 psi of air with
air-saturated 15 °C water and a 2 °C carbonator, more with colder or
supersaturated supply, most of the way there within the first hundred litres.
That air displaces CO2 the feed would otherwise deliver
([pressure vessel](/hardware/assembly/pressure-vessel.md#co2-supply-and-pressure-protection)).
Coca-Cola measured unvented fountain carbonators at up to 30 % air and put a
20–25 % level at 1.0–1.5 volumes of lost carbonation
([US4745853](https://patents.google.com/patent/US4745853A/en)). A carbonator
measured before and after that build-up has been measured at two operating
points.

Qualify at the nominal 43.5 psig feed with the primary in its band. A trial at
a lower feed sets the primary below the preset. A trial above it seats the
owned WR1110, the same body preset at 6 bar, in the regulator cradle and sets
the primary to the trial pressure. A setting other than the nominal is valid
only if the first and successive glasses meet the same carbonation target. Gas
pressure, gas-transfer rate and the carbonation retained in the glass are
separate measurements.

## Change the part that the measurements identify

| Observed failure | Next action | Conditional change if that action does not resolve it |
|---|---|---|
| Nominal 9.5 mm cap does not fit the actual elbow/plate, or welding cannot produce inspectable bore-side root fusion | Do not install that trial part. Record the measured elbow tip, bore, thread engagement, cap clearance and failed joint section under the water-inlet-jet procedure. | Redesign the cap/joint to the measured elbow, or qualify a replaceable purpose-made stainless jet in an existing threaded port. Source the actual candidate and study its made-up stack height and outlet position before adoption. Keep the identical plates; purchased rod does not qualify a joint or select a production part. |
| Refill cannot reach CHI, stalls, or cannot restart after a dispense | Verify flowing inlet pressure, V-K opening, level sensing, jet bore, check direction, voltage and actual switch behavior. Separate jet pressure loss from rising carbonator pressure. | Compare jet bores or outlet geometry on bench fixtures, then pump samples at the measured inlet and outlet pressures. Select another pump only from demonstrated pressure/flow/current and verified material and installation limits. Retain the required carbonation target in that comparison. |
| Refill completes and the water is cold, but carbonation is weak after idle or in successive glasses | Verify CO2 charging/air removal, actual gas pressure and dispense losses. Confirm the jet leaves the final elbow passage into headspace and strikes the water without an intervening turn or obstruction. Record mixing and the time available for absorption. | Compare a revised jet at the same temperature and pressure. If adequate jet mixing still fails the target, evaluate a documented food-contact 316 diffuser as a separate trial, including its cleaning, fouling and permanent-immersion requirements. A brewing-stone listing alone does not qualify a lifetime component. |
| Carbonation that met the target at first fades over the first weeks of use | Record the headspace's air against the CO2 the feed should deliver: carbonator pressure, temperature and dissolved CO2 after the same idle, early and late. | Remove the air: a timed headspace vent, as US4745853 fits, needs a top-plate path that the four existing ports do not offer. Otherwise trial a higher fixed preset against the same first- and successive-glass target. |
| The carbonator fills past CHI with the pump off | Verify V-K closes and seals against the measured house pressure, and that firmware ends every refill at CHI. | Hold house pressure below the gas feed with a water-inlet pressure-limiting valve. Zip HydroTap fits one at 50 psi ahead of a 39–44 psi carbonator ([specification](https://us.zipwater.com/wp-content/uploads/2026/06/HydroTap-R290-CS-120V-Command-Center-Only-Spec-Sheet-with-Small-CO2_01048500.pdf)); a limit under 43.5 psi keeps tap pressure from driving water through the idle pump. |
| Voltage falls or the 12 V supply limits during refill | Measure at both supply and pump, including other active loads; check connections and wire loss. Repeat the same hydraulic point with the acquired LRS-200-12 bench supply. | Revise supply capacity or load sequencing only if the isolated comparison establishes the shortfall. Account for electrical integration, heat and fit before changing the production supply; the current dispense-then-refill policy remains the baseline. |
| The first glass meets the target but following glasses warm up or lose fizz | Record actual pour cadence, refill timing, incoming temperature, immediate in-glass temperature and recovery. Check coil contact, refrigerant charge, sensor contact and dispense-line insulation against their procedures. | Change refill batching or cadence only after separating thermal and pressure effects; moving CLO alone does not shorten a refill that waits for a full pour to finish. Consider incoming-water prechill, more cold storage or refrigeration capacity only if the remaining measured heat load requires it. |

A nominal 338 mL refill from 20 °C into 654 mL at 2 °C would mix to about
8.1 °C before refrigeration removes heat. That simple energy balance explains
why a cold wall reading and a good first glass do not establish repeated-glass
performance. Smaller batches spread the load over time; they do not remove
the total heat arriving with the water.

## Concrete pump path if refill requires more pressure

First measure the G Ganen at the operating point: verify its permitted inlet
pressure and electrical and wetted limits, then record its actual pressure,
flow, switch behavior and current. If it fails the refill requirement, measure
the IEIK sample the same way at the same operating point. A suitable 12 V pump
keeps the simpler electrical architecture; the IEIK is not selected by its
advertised pressure or size.

If none of those 12 V pumps meets the requirement, the researched higher-head
candidate is the
[Aquatec 8852-2P01-V421](https://www.freshwatersystems.com/products/aquatec-cdp-8800-pressure-boost-pump-8852-2p01-v421-160-psi-bypass-3-8-jg-24-vac),
with a separate
[TACS114-48 120 V-to-24 VAC, 2 A transformer](https://wateranywhere.com/products/aquatec-8800-series-transformer-power-supply-for-high-flow-booster-pump-120v-24vac-usa).
September 16, 2026 listing prices are $104.02 + $36.37 = **$140.39** before tax,
shipping, adapters and integration. This is a researched candidate, not an
approved replacement or a delivery quote: the pump page currently renders
“Unavailable,” so its delivery date needs verification when this branch is needed.

The pump listing calls the bypass 160 psi but also describes a 125 psi outlet
limit. Aquatec's
[8800 installation instructions](https://aquatec.com/documents/downloads/IMI-102_F.pdf)
state a 125 psi maximum, while the
[manufacturer's published series curve](https://www.aquatec.com/documents/downloads/8800%20Series%2024VAC%202.6%20LPM.pdf)
is for a different part-number family and gives a 60 psi inlet limit. Obtain
the exact V421 pressure/current curve and manufacturer resolution of those
limits before selection. The 160 psi title does not authorize that pressure
in the carbonator or its nominally 150 psi plumbing. A 24 VAC pump also needs
its own supply, switching, mounting and verified pressure protection; it is
not a drop-in replacement for the G Ganen/IRM-90 pair.

Close qualification by recording the chosen jet, pressure setting, actual
refill and restart envelope, supply margin, first-glass result, successive-glass
result and recovery time. Carry those measured limits into the acceptance
procedure. An alternative becomes the build only when it resolves a recorded
failure and its integration is complete.
