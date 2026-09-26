# Water-inlet jet

The water-inlet jet is a drilled 316 stainless cap welded onto the male tip of
the TAISHER 1/4-inch NPT street elbow at carbonator Port 2. The elbow enters the
top plate from outside; the cap discharges into the CO2 headspace. The plate is
one of the identical purchased SendCutSend blanks. The other top port carries
the PRV, and the bottom ports carry plain CO2 and soda-water elbows.

**Status: fabrication trial, unqualified.** The cap dimensions below describe
the first fit and welding trial. The actual elbow bore and tip, completed NPT
engagement, weld root, hydraulic performance and carbonation performance have
no measurements recorded here. The G Ganen B07F35PTFR diaphragm pump, Mean Well
supply and enclosure are the baseline. The conditional pump arrangement is in
[`carbonation-plan-b.md`](/future/carbonation-plan-b.md).

## Parts and tools

Purchase status and receipts are in [`purchases.md`](/hardware/ledger/purchases.md).
The jet cap is per-unit material; its clamping and purge fixtures are shop tools.

| Part or tool | Use |
|---|---|
| TAISHER 316L 1/4-inch MNPT × FNPT street elbow, [B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1) | One of the four production port elbows. The additional two-pack supplies a destructive trial and a spare; the four earlier elbows are allocated to one machine. |
| Hosifiy 316 round rod, nominal 3/8 inch / 9.5 mm × 400 mm, [B0FYCJJXCS](https://www.amazon.com/dp/B0FYCJJXCS) | Candidate cap stock. Measure its actual OD; its listing is 316, not a claim of 316L. |
| 1/16-inch stub cobalt drill, [B00FX9PNYQ](https://www.amazon.com/dp/B00FX9PNYQ) | Drills the axial jet hole while the cap is still part of a longer handling blank. |
| WEN 4208T drill press; Tap Magic EP-Xtra | The trial begins at the press's 1100 rpm belt setting. |
| WEN BA4555 bandsaw; Imachinist 24 TPI M42 blade | Cuts handling blanks and cap slices. |
| Owned printers and filament, fixture plywood/MDF, four C-clamps | Print and set up the [two-piece drilling fixture](/hardware/printed-parts/fixtures/water-inlet-jet/README.md); STL, STEP and source are provided. Physical grip and clamp clearance are untested. |
| NEIKO caliper, magnifier, stainless-only brush and Scotch-Brite | Fit measurements, burr inspection and surface preparation. |
| XLaserlab X1 Pro, ER316L .030 wire, C110 copper stock, argon | Small-joint weld trial and fixturing. Power, pulse, wobble, travel and filler settings are unqualified. |
| HARFINGTON 6 mm push-fit × 1/4-inch MNPT branch tee, [B0F1FDG9SC](https://www.amazon.com/dp/B0F1FDG9SC) | Splits the regulated argon hose between the welder and the purge branch. |
| LTWFITTING 316 1/4-inch FNPT full coupling, [B01ABDD8FY](https://www.amazon.com/dp/B01ABDD8FY) | Joins the tee's male branch to the first compression adapter. One coupling belongs to this shop fixture. |
| Two owned VALVENTO 1/4-inch OD compression × 1/4-inch MNPT adapters, [B0DXZZBK7D](https://www.amazon.com/dp/B0DXZZBK7D) | One after the coupling, one in the trial elbow's female port. |
| Owned VALVENTO 1/4-inch OD 316 tube, [B0F6SYFK48](https://www.amazon.com/dp/B0F6SYFK48) | Two straight purge links, cut to suit the bench layout. |
| Owned TAISHER TC025 304 compression needle valve, 1/4-inch OD both ends, [B0CLXHZZCW](https://www.amazon.com/dp/B0CLXHZZCW) | Throttles purge flow independently of torch shielding. |
| Owned Mudder hose cutter, argon cylinder and RX Weld regulator/flowmeter | Cuts the existing 6 mm OD supply hose square and feeds both branches. The RHP400 is an alternate regulator, not a second simultaneous supply. |

## Candidate dimensions and measured fit

| Feature | Trial specification |
|---|---|
| Cap OD | [9.5 mm](CAP_OD), subject to measured elbow land and port clearance |
| Finished cap thickness | [2 mm](CAP_THICKNESS), initial cutting target ±0.2 mm |
| Axial hole | [1/16 inch / 1.5875 mm](JET_BORE) |
| Passage length / diameter | [1.26](JET_LD), from the nominal thickness and bore |
| Nominal passage area | [1.979 mm²](JET_AREA), not a measured flow coefficient |

Before cutting the batch, record the following on an actual elbow and a loose
tapped plate:

1. Male-end bore diameter, tip diameter, flat annular land and any chamfer.
   The layout CAD's elbow bore is a stand-in, not a caliper reading.
2. Actual rod OD and the overlap it makes on that land. The cap must cover
   the bore, sit flat and leave a weld path that can fuse to the bore-side
   root. A wide unfused lap is not an acceptable seating feature.
3. Minimum clear opening through the tapped plate, cap OD and the maximum
   welded OD. The nominal tap-pilot size does not establish this clearance.
4. Made-up elbow depth, clocking and cap projection relative to the plate's
   inside face. The completed jet exit must reach the headspace with a clear
   downward path and without changing the elbow's external stack height.
5. Thread condition after welding and repeat fit on the same plate. The weld
   must not obstruct or distort the sealing threads.

The 9.5 mm rod is a candidate, not permission to force the cap through the
plate or deepen the NPT tap to accommodate it. A failed reading returns the
cap diameter or joint detail to design; it does not authorize a new plate
pattern, port position or foam-cap height. Record the accepted dimensions
before updating the nominal CAD.

## 1. Drill the handling blank, then cut the cap

Cut a manageable 50–60 mm handling blank from the rod with the bandsaw;
the 400 mm stock is not the upright drill-press workpiece. Print the fixed
base/jaw and loose jaw from the
[drilling-fixture files](/hardware/printed-parts/fixtures/water-inlet-jet/README.md).
They provide 30 mm of rod support and a solid floor. Two C-clamps close the
jaws horizontally; two secure the base flanges, wood backer and drill table.
Follow the fixture's stopped-spindle setup and grip trial before making caps.
Its nominal groove is adjustable in source if the measured stock or print
does not grip correctly. Do not drill a rod that can turn or rock in the jaws.

1. Seat the rod vertically with a flat, clean end under the drill. Align the
   stopped drill tip with the rod axis and check that the chuck grips the
   1/16-inch shank concentrically.
2. Set the WEN 4208T to **[1100 rpm](DRILL_RPM)**, approximately
   [18.0 surface feet/minute](DRILL_SFM) at this diameter. This is a trial
   starting point, not a validated feed/speed recipe. Apply Tap Magic and
   feed positively enough to cut chips. Retract to clear chips and renew
   fluid; do not dwell with the bit rubbing. Stop for squealing, stalled
   cutting, excessive heat or a wandering bit and correct the setup.
3. Drill approximately 3–4 mm deep. That leaves the full-diameter part of
   the hole beyond the proposed cap's back face. Do not drill the entire
   handling length.
4. Put the rod in the bandsaw vise, set the cut square and begin the 24 TPI
   blade trial at the saw's low speed. Set a nominal [2 mm](CAP_THICKNESS)
   slice from the drilled end, accounting for which side of the blade the
   stop references. Clamp the retained rod; keep the cutoff free to fall
   into a tray, without a stop trapping it against the moving blade.
5. Measure the slice. Inspect the hole from both faces under the magnifier.
   Remove loose saw/drill burrs and clean both faces while they are
   accessible. A light hand turn of a larger owned drill can remove a hole
   edge burr; do not power-countersink a thin cap or enlarge the jet. Keep
   the exit edge consistent and reject a visibly distorted hole.
6. Wash away cutting fluid and particles, rinse and dry. Check the cap sits
   flat on the elbow tip without rocking. Reject a wedge-shaped or damaged
   slice rather than hiding its gap under filler. Repeat from the newly cut
   rod end for the next cap, reseating and realigning it in the clean jaws.
   Retire the handling blank before it is shorter than 40 mm, or earlier if
   the actual chuck clearance requires it.

The cap is drilled before welding so both sides of its bore remain accessible
for deburring. The finished hole is inspected and flow-checked after welding;
an unrecorded drill-through repair is not the same geometry.

[Norseman's drilling guidance](https://www.norsemandrill.com/feeds-speeds-drill.php)
gives material-dependent speed and feed ranges and notes that conditions
require adjustment. The trial record carries the setting that actually cuts
this stock with this fixture.

## 2. Assemble the argon purge branch

Close the cylinder and depressurize the line before cutting or disconnecting
it. The tee goes in the **regulated 6 mm OD argon hose**, with its straight
run continuing to the welder. Its 1/4-inch male branch feeds this chain:

**Tee → FNPT coupling → compression adapter → 1/4-inch OD stainless tube →
TC025 needle valve → stainless tube → second compression adapter → elbow's
female port → drilled jet hole.**

Cut the 6 mm hose square with the Mudder cutter. Seat both hose ends fully
in the tee and tug-test them. Cut, deburr and clean the stainless tube links;
fit the compression joints to their maker's instructions. Use the owned NPT
seal tape on the threaded connections, keeping tape out of the gas passage.
The last adapter is temporary shop tooling and is removed from the finished
jet elbow before washing and installation.

The tee's stated maximum working pressure is 1 MPa / 145 PSI; it belongs only
downstream of regulation. The
[X1 Pro setup guide](https://eu.xlaserlab.com/blogs/academy/x1pro-laser-welder-unboxing-installation)
specifies a 6 mm OD protective-gas hose, inlet pressure above 0.2 MPa and
gas flow above 15 L/min. Confirm the installed hose and regulator match that
connection before cutting, and keep the complete regulated line within the
lowest component rating.

Start with the needle valve closed. Restore argon, check the new joints for
leaks, then crack the needle valve to a gentle purge through the elbow.
Keep the jet hole open as the vent. Purge must not lift the cap or disturb
the weld pool. Check torch shielding with the purge flowing: the upstream
flowmeter reads both branches together, not torch flow alone. Record the
torch-flow check, purge setting and root condition during qualification;
no numerical purge-flow setting is established here. Water-only PP
push-connect fittings are not part of this gas fixture.

## 3. Qualify the small weld on a spare elbow

Use the same elbow, rod material, cap dimensions and surface preparation as
the production assembly. Remove cutting fluid, dirt and loose oxides before
welding. Keep NPT tape, polymer purge fittings and the printed drilling
fixture away from the weld zone; hold the bare elbow on a metal fixture.

Set the elbow with its male tip facing up and the cap seated flat and
concentric. Establish the gentle internal purge and torch shielding, then
tack opposite sides and check seating. Close the circumference with the
small-joint trial settings, keeping the jet clear. Record power, pulse mode,
wobble, travel, filler use, shielding/purge, tack order and restart treatment.
There is no approved numerical laser recipe for this joint. The carbonator's
large closure-weld settings are not its recipe.

The required result is fusion through the cap-to-tip interface to the
bore-side root, with no wetted lap crevice, loose metal, crack or black root
scale. An attractive bead on the outer rim does not demonstrate that result.
The [X1 Pro specification](https://www.xlaserlab.com/products/xlaserlab-x1-pro-laser-welder-cleaner-cutter)
includes pulse/spot operation and thin stainless work; it does not qualify
this particular joint.

Check the completed thread fit and cap projection first. Then section the
trial elbow/cap through the jet axis, with a second section at a different
azimuth to sample the tack/restart region. Hold the elbow body securely in
the bandsaw vise. Dress the cut faces with the owned fine abrasive stock on
a flat support, then inspect and photograph the cap, fusion region and root
under the magnifier. Retain the sections and settings record. A section whose
root cannot be read is an unresolved qualification, not a pass; metallographic
preparation or additional examination may be needed to resolve it.

Reject a visible unbonded interface open to the bore, cracks, root scale,
cap movement, damaged threads or a changed/obstructed jet passage. Sectioning
samples the joint and does not inspect every point around it; repeatability,
inspection coverage and the production acceptance record remain part of the
qualification. Pressure retention and a good-looking jet do not replace this
root inspection. [Nickel Institute's stainless fabrication guidance](https://www.nickelinstitute.org/media/1677/fabricatingstainlesssteelsforthewaterindustry_guidelinesforachievingtopperformance_11026_.pdf)
addresses full penetration, clean welds and inert-gas protection of the root.

## 4. Make, clean and flow-check the production elbow

Use the accepted dimensions, fixture and weld settings to make the production
elbow. Inspect its cap, jet passage and accessible weld surfaces, repeat the
loose-plate fit, and record its identity against the qualification coupon.
Remove the temporary purge adapter. Flush the elbow in both directions until
no loose particles emerge; inspect the passage under magnification. Define
and demonstrate the fluid/residue cleaning method on the qualification part
before applying it to the batch.

The jet elbow enters the citric bath clean, with acceptable root condition
and weld oxide already addressed, under
[`pressure-vessel.md` step 8](/hardware/assembly/pressure-vessel.md#8-citric-acid-passivation).
Rinse through the female port and the jet passage, drain and dry. Citric
passivation does not remove an unfused crevice or establish removal of weld
heat tint. [BSSA passivation guidance](https://bssa.org.uk/bssa_articles/passivation-of-stainless-steels/)
requires a clean surface before treatment.

On the bench, support the elbow and aim the jet into a catch container.
Use the baseline water supply and pump within their ratings. At a recorded
inlet pressure, collect and weigh or measure water over a timed interval.
Record water temperature, duration and collected mass/volume, inspect for
flow emerging anywhere except the drilled hole, and repeat to check
consistency. A second stream from the cap perimeter is a reject. No numerical
production flow band is established until the qualified geometry has been
measured.

An open-air flow check gives the pressure difference to atmosphere; it is
not a measurement of refill into the pressurized carbonator. The integrated
run records carbonator pressure and delivered refill volume/time, using the
actual supply path, and evaluates the drink after refill and idle per
[`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md).
The pump's advertised pressure alone establishes neither that flow nor the
carbonation result. A plain jet is not a measured spray pattern.

Install the accepted elbow at Port 2 after the bare carbonator passes hydro
and passivation, per
[`pressure-vessel.md` step 9](/hardware/assembly/pressure-vessel.md#9-install-elbows-and-prv).
Confirm its clocking and projection against the loose-plate fit record before
the cold-core pour.

## Qualification record still required

| Record | Current state |
|---|---|
| Actual rod OD; elbow bore, end land and tip | Unmeasured |
| Cap OD/thickness, thread fit and headspace projection | Candidate dimensions only |
| Printed rod-clamping fixture and drilling/cut repeatability | Not built or demonstrated |
| Purge-hose fit, gas-tight joints and torch-flow check | Not demonstrated |
| Small-weld recipe and sectioned root | Unqualified |
| Root/oxide cleaning, residue removal and passivation acceptance | Unqualified |
| Per-part inspection and flow acceptance band | Undefined pending qualification |
| Integrated G Ganen refill, idle behaviour and in-glass carbonation | Unmeasured |

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_water_inlet_jet_sync.py`
