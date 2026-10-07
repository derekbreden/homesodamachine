# ASSE drain cavity engineering

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

The white 4 mm drain ends square inside the circular transition at the two-piece
gooseneck connection. Discharge passes around the three continuous drink tubes to
the bottom-center opening. The shared cavity carries no divider. Its end glands
and the shell joint separate this wet transition from the dry shell passages.

## Geometry and calculations

The current generators supply the inputs to [hydraulics.py](hydraulics.py).
[measure_route.py](measure_route.py) binds native full-factory tube lengths and
the documented reference-cabinet elevation to [native-inputs.json](native-inputs.json).
[hydraulic-report.json](hydraulic-report.json) separates analytic geometry from
conditional fluid calculations. It records the nominal installation used for
the rise; it does not infer every customer's cabinet from that reference.
Paired artifact arguments bind the completed appliance STEP and its passed
installed-body clearance audit. Modeled endpoint spans and nominal bore volumes
are distinct from tube cut lengths and measured installed hold-up; barb/socket
engagement is part of actual assembly.

[check_port.py](check_port.py) reads the saved production tip STEP. Its
[native report](port-native-check.json) checks full 2 mm walls around both flange
grooves and body seats, outlet clearance from those seats, a continuous bottom
escape corridor, actual flared torus-face openings and the entire native exterior
opening against the stated sink-position envelope. It records source and STEP
hashes. The wider assembly checks cover tubing, cable, joints and display.

Arc stations are distances along the soda-tube centerline. The circular cavity's
lower wall follows a smaller radius. Port area must therefore be projected onto
that lower wall; multiplying the width and station length overstates the
opening. The rounded rectangular cutter uses a tangent chord of 19.633 mm for
its 22 mm arc-station window. The calculation tests that actual chord geometry
at the minimum 12 mm profile width. It also includes the height increase across the circular
section and along the arch. It clips credited area to the actual planar gland
faces. The downstream keeper undercut, side flare and extra transverse surface
area receive no hydraulic capacity credit. Its assumed discharge coefficient is 0.6,
with 0.4 and 0.8 sensitivity cases. None of these coefficients is a measured
property of the deposited part.

The cavity crosses the arch's gravity crown. The opening spans its complete
lowest floor, so water can leave on either side of the crown. The upstream floor
is the nominal low point; the crown is only about 1 mm higher. A finite flat edge
starts at that low point, and the opening continues through the downstream
keeper before the protected flange groove. The sides flare outward. It has no
internal lip, screen, valve or cap. Nominal free area subtracts S, F1, F2 and the insulated
ribbon from the circular cavity. D terminates at entry and occupies no continuous
lane through this transition.

The water model uses Darcy-Weisbach with smooth-pipe friction. It reports the
pressure required by a full line and a pressure-to-flow sizing envelope that
excludes the device's internal fault opening. An unrestricted-line calculation
uses zero additional fitting loss to give the cavity the larger flow to handle.
The separate K = 5 case illustrates fitting and bend losses; it is not measured.
The report includes 2 C and 20 C water and bore sensitivity. Bore sensitivity is
not a supplier dimensional tolerance.

A water-filled rising line imposes hydrostatic pressure at the device even before
flow starts. A small fault can fill the low parts of the tube before any visible
discharge reaches the sink. The dry CO2 model is an ideal-gas, low-Mach screen;
it does not predict liquid slugs, flashing, high-rate choking or the device's
response to a retained column.

For the reference installation, the small tube is 2106.419 mm long and rises
708.194 mm from the device vent to D's cut end. The nominal bores contain about
10.34 mL in the small tube plus 0.58 mL in the modeled PVC span, using unobstructed
bores and excluding fitting insertion interiors and overlaps. Its
static water column imposes about 1.005 psi at the device. The cavity has
270.61 mm² free cross-section after D ends, and the model credits 224.52 mm² of
projected wet opening. D's lowest bore edge is 13.754 mm above the low floor.

At the nominal 125 psi unrestricted-line sizing envelope, the model predicts
2.606 L/min. With the assumed 0.6 discharge coefficient, cavity head is 6.595 mm
and the bore remains 7.160 mm above water. The independent 3 L/min cavity proof
target predicts 8.315 mm head and 5.439 mm bore clearance. The 200 psi device-rating
sensitivity predicts 3.415 L/min. These are conditional
single-phase calculations. The deliberately conservative area with a 0.4
coefficient leaves only about 0.54 mm at the 125 psi nominal-bore envelope, below
the 2 mm physical proof target. The report exposes that sensitivity rather than
turning an unmeasured coefficient into a qualification result. The report also
shows that shortening the small tube to 1 m can consume the bore-clearance
margin at the same pressure. The supplied factory route is part of the assessed
configuration; a trimmed route needs its own complete-route assessment.

Regenerate the model and saved-part witnesses after generating the production
tip STEP and completing the current appliance STEP and installed-body clearance
audit:

```sh
PYTHONDONTWRITEBYTECODE=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/vent-qualification/measure_route.py \
  --appliance-step hardware/manifold-layout/enclosure-assembly.step \
  --appliance-clearance-report hardware/manifold-layout/drain-clearance-check.json
python3 hardware/printed-parts/faucet/vent-qualification/hydraulics.py \
  --input hardware/printed-parts/faucet/vent-qualification/native-inputs.json \
  --output hardware/printed-parts/faucet/vent-qualification/hydraulic-report.json
PYTHONDONTWRITEBYTECODE=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/vent-qualification/check_port.py \
  --hydraulic-report hardware/printed-parts/faucet/vent-qualification/hydraulic-report.json
```

The reports record input, source and saved STEP hashes. Nominal geometry passing
does not produce a hydraulic-qualification pass. The native sink check covers a
hole center up to 50.8 mm behind a straight bowl edge with the faucet facing
within 10 degrees of the bowl. The actual installation also has to place the
complete outlet over the bowl width and away from its curved corners.

The native record retains witness-execution hashes and current source bindings.
Its binding audit verifies the same tip STEP, port/gland functions, station
source and seal-wall dimensions. The complete cabinet route is measured and
bound separately to its saved appliance STEP and passed clearance audit.
Factory-tool geometry, the display-cover assembly motion and production-export
locking are outside the recorded consumer port witnesses.

[Postpublication Sculpted mesh review](postpublication-lint.json) and
[Industrial mesh review](postpublication-industrial-lint.json) bind the current
STL hashes and scoped lint answers. [check_base_witnesses.py](check_base_witnesses.py)
records [complete 2 mm inward stock](base-native-lint-witnesses.json) for the
named passage planes, donor/lever roofs and all six annular socket roofs.
[check_lint_supports.py](check_lint_supports.py) reads the retained native G-code;
its [roof support record](lint-support-witnesses.json) projects three actual
support extrusion samples onto each named donor/lever roof. These local witnesses
do not establish global wall thickness, complete support coverage, physical
printing, support removal or part strength.

## Manufacturer evidence

The appliance uses the Multiplex 19-0897 / Anderson Brass ABF-1. Anderson describes
the vent as the exhaust for CO2 and water when its primary check leaks.
[Anderson Brass](https://www.andersonbrass.com/product-page/abf-series-asse-1022-vented-dual-check-backflow)
and the [Multiplex parts catalog, page 25](https://www.multiplexbeverage.com/getmedia/b03506e7-69e1-407f-bd99-f594b8f1ba88/Parts-Book-May-2022.pdf)
do not establish a permitted pressure loss for this reduced, rising discharge
route. The device's working-pressure rating is not a permissible vent
backpressure.

The specified white drain tube is neoFlo LLDPE4M-WHITE. The
[neoFlo manufacturer sheet, metric table](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
specifies 4 mm OD, 2.5 mm ID, 0.75 mm wall and a 25 mm minimum bend radius for
LLDPE-4MM-200M-X; W identifies white. This evidence specifies the tube, not the
ASSE device's performance through it.

## Physical qualification record

No physical discharge or seal result is recorded here. Existing
[mechanical acceptance](../../../mechanical-qualification/README.md) retains its
reported scope. The following procedure defines engineering measurements; it is
not a customer installation step or a request to the founder for a new test.

First qualify the cavity independently of the ASSE device. Use the production
tip, port and glands with actual S/F1/F2 tubing and ribbon. Mount them in the
installed orientation. Feed a square-ended 4 mm tube at the specified cut station
from a controlled bench water source. Collect discharge into a weighed container
to establish actual flow. Use a fixture inspection window or an instrumented
low-floor pressure tap to observe liquid head relative to the native floor
datum; the fixture must preserve the production port, three drink tubes and
gland sealing surfaces. Instrument resolution must distinguish a 2 mm water
column (approximately 20 Pa). Record fixture geometry and instrumentation with
the result.

Run 0.05, 1.0, 2.5 and 3.0 L/min for 60 seconds each, at 2 ± 2 C and 20 ± 2 C.
Record source flow, collected flow, maximum head, escaped water and remaining
water. Repeat the high-flow case with 2 degrees of pitch and roll in each
direction, recording the actual bore and lowest outlet elevations in each pose.
The complete-bottom opening has no closed longitudinal floor hump. This modest
mounting sensitivity does not establish the complete faucet's installation
tolerance or its lateral bowl-position envelope.

Cavity acceptance is discharge through the bottom outlet, dry exterior/dry
shell passages and no immersion of D's cut bore. The target high-flow margin is
2 mm below the bore's lowest edge, one radius of the nominal 4 mm tube. This is
an engineering clearance buffer, not an ASSE backpressure allowance. The report supplies the head datum and
conditional capacity at that margin. Water must leave the gravity low point
after flow stops; a surface film is distinct from a retained bulk sump. Record
any retained volume and its location. The 3 L/min case is a cavity design proof
target chosen above the nominal 125 psi unrestricted-line prediction; it is not
an ASSE standard fault-flow requirement. The device's 200 psi rating appears as
a separate sensitivity envelope and does not define the appliance's operating
or fault limits.

Then assess the complete installed route, including the device, adapters,
bulkhead, full tube length, service-loop orientation, cavity and outlet. In a
rated, isolated fixture, compare the specified device with an open reference
vent and with the appliance route under the device's defined fault procedure.
Measure supply, downstream and vent pressure; liquid and gas flow; protected-side
leakage; dry start; prefilled line; repeated slug clearing; and representative
outlet obstruction. Use device-specific permissible pressure and protected-side
leakage limits as acceptance criteria. Those values and a permitted fault
procedure are not supplied by the public evidence reviewed, so this report
cannot turn that comparison into an ASSE or manufacturer approval.

Record assembly repeatability, clamp position, D cut location, gland seating,
water tightness and outlet inspection separately from nominal CAD checks. A
printed part ready for assembly is not a measured lifetime or discharge result.
