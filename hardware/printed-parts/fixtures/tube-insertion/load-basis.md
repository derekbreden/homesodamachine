# Load basis

The tool seats a sleeve-covered 3/8-inch LLDPE tube into the bare Touch-Flo
while its faucet lever is attached, down and unpressed. The existing
[assembly observations](../../faucet/lever-replica/assembly-observations.json)
establish the order and difficult sliding on the tube. They establish no
numerical insertion force. The customer's outcome is controlled coaxial
insertion without a broken tool, a scrunched sleeve or a damaged tube.

Two complete [BESSEY GSCC2.506 clamps](https://www.amazon.com/dp/B000FA0BL8)
supply the actuation and long reaction loops. Each uses its factory spindle,
steel rail and cast-iron jaws. The
[BESSEY product sheet](https://besseytools.com/getmedia/24e6be04-58db-4ea7-b4d7-28083eac8980/BESSEY_Clutch-Style-bar-clamps_EN)
lists 152.4 mm capacity, 63.5 mm throat and 600 lbf (approximately 2669 N)
clamping force per tool. That force does not rate the printed parts, tube,
donor, grip or complete fixture. The screws bear directly against the
collar; both fixed jaws back the donor block at screw height. The printed
base locates the parts, reacts unequal-input yaw and holds the tool on the
bench.

## Sections and load path

The insertion direction is −X. Tube axis is Y8.75, Z30. Both screws are
parallel to X at tube Y±32, Z30; factory contact centres are Y−23.25 and
Y40.75. A 30 mm contact envelope fits uninterrupted front and rear landing
faces. The nearer fixed foot clears the open shank slot by 2.35 mm. These
are fixture stations; proprietary clamp profiles, contact pads, spindle
travel and handle dimensions are not measured CAD. Ordinary unloaded setup
checks actual pad backing and the entire 20 mm screw travel.

The donor's metal base annulus bears against a solid 26 mm thick, 120 mm
wide, 54 mm high block, with the two factory metal fixed jaws immediately behind it
at Z30. The open shank slot has an 11.8 mm diameter; the minimum continuous
bottom-web height is 24.1 mm. The threaded shank, plunger, arches and
attached faucet lever carry no intended axial reaction.

The cradle and clocking pad support the donor from below and are open
above. They provide no positive upward restraint. Off-axis contact during
insertion can therefore lift the donor; the axial and yaw calculations
below do not assess this motion or the required downward counterforce.
The separate [TPU hand pad](donor-hold-down/README.md) bears on the
cylindrical metal body and supplies a flat surface for manual downward
pressure. Its tongue retains the pad in the shank canyon; its press fit
has no assigned hold-down capacity. The tongue joins the solid crown
above the saddle and has 10.25 mm nominal clearance above the threaded
shank, with 8.25 mm of canyon engagement. The pad clears the lower cradle
by 1 mm. Hand-pressure performance
and installed lever clearance remain physically unqualified.

Each rigid collar half is 15 mm high. Its transverse wings have 30.5 mm
axial depth from X8 to X38.5, with screw stations 16 mm beyond the 32 mm
wide core edge. Analysis below assigns an entire station's force to a
single half, rather than assuming that a factory foot shares it equally
between upper and lower halves. The 28 mm preformed TPU liners retain the
Ø7.75 unloaded bore, 3.35 mm front wall and 6.85 mm rear wall. Rigid backing
beneath the pockets is 7 mm; the TPU's minimum backing is 4.125 mm.

The carrier has a 124 mm guide bearing span and a 6 mm thick, 100 mm wide
foot. Its full-width foot starts at X96.5, behind the donor. The forward
38.5 mm shelf is 32 mm wide. Two metal screws couple the lower collar to
the carrier; locating keys assist assembly. The 7 mm high coupling seats
have radius 10 mm, giving 4.9 mm radial stock around the Ø10.2 countersink
and 4.65 mm minimum retained shelf thickness. The lower-jaw square nuts
have 9 mm of floor; the countersunk screw tips have 1.8 mm of relief.
The coupling must remain tightened without slip for the guide-only yaw
calculation to apply.

## Analytical scenarios

The following forces are selected calculation scenarios. They are neither
measured insertion forces nor operating targets, load limits or ratings.
The 2 kN one-station case checks complete unequal loading, including the
short donor block. No load sharing between the two clamps is presumed in
that case.

| Scenario | C1 / C2 input, N | Donor web nominal bending, MPa | One collar half nominal bending, MPa | Guide reaction at each end, N | Tube average axial wall stress, MPa |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 kN balanced | 500 / 500 | 5.9 | 3.4 | 0 | 25.3 |
| 2 kN balanced | 1000 / 1000 | 11.8 | 6.9 | 0 | 50.5 |
| 1 kN at one station | 1000 / 0 | 11.8 | 6.9 | 258 | 25.3 |
| 2 kN at one station | 2000 / 0 | 23.7 | 13.8 | 516 | 50.5 |

For the donor web, use a conservative 24 mm net height and 26 mm axial
thickness: section modulus W=24×26²/6=2704 mm³. Balanced input on a
64 mm span gives M=F×64/4=16F N·mm. Full one-station input uses the
32 mm cantilever-arm scenario, M=32F. This simplified beam model excludes
slot-notch concentration and detailed annular contact redistribution.

For a single collar half, W=15×30.5²/6=2326 mm³ and the station arm is
16 mm. Nominal bending is F_station×16/W. The calculation excludes
pocket/head-hole stress concentration and uneven local contact. The
collar's TPU end-bearing area is approximately 126.4 mm² per pad; if an
entire 1 kN or 2 kN went through one pad, its average end bearing would be
7.9 or 15.8 MPa. This area calculation does not assess wall bending, TPU
shear, slipping or retained squeeze.

Unequal input creates yaw Mz=32×|F_C1−F_C2| N·mm. The 124 mm guide span
reacts R=Mz/124 at its two ends. The whole 100 mm wide, 6 mm thick foot has
an in-plane section modulus of 10000 mm³, giving 6.4 MPa nominal bending
in the 2 kN one-station scenario. Actual corner bearing length is
unmeasured: a 16 mm contact band would have 96 mm² of guide area and 5.4 MPa
average contact stress under 516 N. The 8 mm wide, 6 mm high integral guides
are short local bearings; the calculation does not establish their
printed contact distribution or allowable stress.

The tube wall area is π(9.525²−6.35²)/4=39.59 mm². Thus 1 kN produces
25.3 MPa average axial wall stress before local grip effects. The workpiece,
TPU sleeve and grip can limit operation before the factory metal clamps.
The [John Guest tubing data](https://www.johnguest.com/us/en/lldpe/lldpe-tubing)
give dimensions and pressure/application guidance, with no axial
compression or clamping allowable for this operation.

## Alignment and evidence scope

The 0.1 mm side gaps over a 124 mm guide span give a geometric angular play
bound of 0.2/124 rad. With the collar metal-coupled without slip, worst
nominal port-axis displacement is approximately 0.193 mm at the final
position and 0.225 mm at the initial position. The bare tube's reference
radial port clearance is 0.2375 mm. That comparison is not a measured
working alignment allowance for an interfering TPU sleeve.

With the donor hand pad fitted, one hand applies downward pressure and the
other alternates the screw handles. Advance one screw by one very small
step, then immediately take up the opposite pad gap before another
advance. The common collar stays guided during limited alternation;
continuous two-pad contact and
equal force are not assumed. There is no intentional yaw joint. Spindle
pitch is not documented here, so a turn count is not presented as a
measured advance. A pad gap that cannot be taken up, slipping collar or
binding carrier calls for unloading and correcting alignment before
continuing. Stop at the first of the seating witness or geometric travel
limit, and unload and recheck the setup if they disagree. The travel stops
are geometric overtravel limits, not force-holding reaction surfaces.

The accepted faucet lever has no measured assembled rigid pose. The
full-width guides are rearward and the forward shelf is narrow. Ordinary
unloaded setup confirms that the attached lever stays down at unpressed
rest and remains untouched throughout travel. No fabricated lever transform
or all-angle sphere establishes working clearance.

The [PET-GF15 data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
identifies 100% infill and annealing at 120°C for 16 hours for its mechanical
specimens. Its XY tensile 59.9 MPa and flexural 104.2 MPa, and Z tensile 48.2
MPa and flexural 80.3 MPa, are reference/comparison results with an explicit
warning against using them as design specifications. These unannealed
prints have no established production allowable. The analytical values
above receive no safety factor or load rating from those coupon numbers.
Saved native slicing establishes the prepared process; B-rep review
establishes the stated geometry. Neither supplies physical grip, insertion
force, printed strength or lifetime qualification.
