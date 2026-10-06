# PGFUN fixture engineering

The fixture supplies a vertical swivel and a horizontal pivot. Their axes
intersect 145 mm behind the nominal joint, at the joint's 208.05 mm height.
The movements produce orthogonal small arcs at the aiming point. At one
degree the first-order displacement is 2.53 mm; departure from the tangent
is 0.0221 mm. The host uses rotations and measured camera responses.

## Geometry and load paths

The bridge attaches to the stationary rotator's two existing 10 mm holes,
at X=-102/162 and Y=-107. Locating collars register it; M8 anchors retain
it; bench toes support its rear edge. It transfers load into the stationary
base and bench, behind the moving turntable.

The yaw pedestal supports two 6808 bearings through a separate cartridge.
Its journal carries the fork. The pitch journal drives the left cheek through
six M5 bolts; two 6001 bearings support the right cheek's 12 mm axle. The
cheeks and bottom tie support the lined gun cradle from below. Each reducer
is aligned to the bearings before its case bolts are tightened. Its motor
shaft is an input coupling, not a cantilever supporting the gun.

Six printed keys at 20 mm radius transmit torque from each reducer adapter
to its journal. Six M3 bolts retain the faces. Keys have 6 mm depth and
0.05 mm nominal side interference. Journal flanges use six M5 bolts on a
58 mm circle. The opposite axle clamp rotates the bearing support with the
frame; it is not part of the positive pitch stop.

Stops act directly between driven frames and fixed supports. An M6x25
follower in the fork stops yaw; an M6x35 follower in the left cheek's integral
rear arm stops pitch. Each bears against a sector at 70 mm radius. No friction
clamp on a smooth shaft is relied on to stop pitch. Four normally closed
roller switches open before the mechanical stops.

## Load calculation

The measured gun, guide and four-foot cable mass is **1.3118 kg**. The
calculation places that entire mass at the most adverse point of the pinned
exterior reconstruction. It adds gravity moments of moving prints and
**10 N** residual cable force at the maximum exterior radius. This overstates
the distributed gravity load; it does not assume a measured centre of gravity.
The cable post must keep residual force within that allowance. Exact values
and bindings are in [load-screen.json](../printed-parts/fixtures/pgfun-positioner/load-screen.json).

The reducer's advertised continuous output torque is 7 N m. Normal service
must stay within it. An **18 N m structural fault screen** covers nominal
ideal multiplication of the selected motor's holding torque at configured
peak current, with a small allowance. This is not a reducer overload rating
or a calibrated electronic torque limit. A failed limit followed by a powered
stall can damage the reducer; positive stops limit travel with the gun retained.

Screens cover key bearing pressure, net journal torsion, bearing moment couple,
flange fasteners, stop slot pressure, stop-arm bending and an 80 mm net-width
bridge section. Journal torsion subtracts the central bore and six large screw
wells. The 14 mm bearing-centre spacing gives a 500 N couple at 7 N m, below
the bearing seller's 4,180 N static-load figure. That rating does not qualify
printed seats; their average projected contact pressure is screened separately.

PET-CF17 calculations assume **5 MPa allowable stress** and **1,500 MPa
elastic modulus**. These are engineering assumptions for as-printed parts,
not measured properties. Polymaker's published strength values use parts
annealed at 120 C for ten hours; this build does not claim them. Hole stress
concentrations, layer adhesion, creep and contact deformation require the
specified loaded checks. The screens size sections; they do not establish
fatigue life or micron-scale stiffness.

## Useful motion

The controller issues 640,000 counts per output revolution: 200 motor steps,
64 external microsteps and 50:1 reduction. A count at the 145 mm lever is
**1.42 micrometres**. Advertised 20 arcsecond backlash corresponds to
**14.1 micrometres** there. These supplier and command values do not establish
received transmission error or minimum useful movement under load.

Calculated elastic twist at 7 N m is substantially larger than one count.
Static compliance can enter a learned response; changing cable load, heat or
slip cannot be removed by quoting backlash. Camera qualification therefore
checks real dot and wire motion under working mass, routing and temperature,
in all four combinations of approach directions.

Soft travel is +/-1 degree; nominal stops are +/-1.5 degrees. Firmware limits
rate to 1,000 counts/s and acceleration to 4,000 counts/s squared. Maximum
speed is 0.5625 output degrees/s, or 4.69 motor rpm.

The camera measures four coordinates: tangent/normal positions of the dot
and actual wire endpoint relative to the seam. Two axes correct only their
rank-two span. Residual error outside that span rejects the trajectory.
Correct the nominal cradle pose or wire-guide relationship instead. One
camera cannot determine invisible depth or welding focus.

## Verification scope

[clearance-check.json](../printed-parts/fixtures/pgfun-positioner/clearance-check.json)
screens full-precision fixture meshes against pinned gun and rotator CAD at
25 combinations spanning both hard-stop ranges. Intentional key interference
and stop contacts are recorded separately. Real cable shape, switch rollers,
fastener heads and continuous swept volumes require the power-off assembly
sweep. Each printable STL is a closed positive volume within the H2C envelope.

Individual STEP, STL and viewer payload share the print frame. Assembly CAD
uses rotator coordinates. Controller and host profiles bind to the parameter
hash. A parameter change requires new CAD, firmware and affected physical
checks. [Commissioning](commissioning.md) specifies fit, retention, interlocks,
loaded motion and thermal drift. [Observation](observation.md) specifies
camera setup, learning, independent dry validation and replay. Physical results
are recorded only after assembly and measurement.

## Manufacturer references

- [PGFUN reducer and installation video](https://www.amazon.com/dp/B0GF87W2KK): TYXC-0062_17_50 drawing, torque and backlash claims.
- [BIGTREETECH SKR Pico](https://github.com/bigtreetech/SKR-Pico): schematic, board drawing and pin assignments.
- [PET-CF17 technical data](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-CF17_V1.0_EN.pdf): drying, printing and annealed test conditions.
- [Raynox drawing](https://raynoxdirect.securesite.jp/comparison/pdf/DCR150_DCR250_drawings.pdf): lens body, neck and axial dimensions.
- [X1 Pro manual](https://cdn.shopify.com/s/files/1/0973/4353/7468/files/X1_Pro-Manual-EN.pdf?v=1773891208): focus and external interfaces.
