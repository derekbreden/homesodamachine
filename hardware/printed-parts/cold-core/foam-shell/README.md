# Cold-core shell

The PET-GF shell carries the carbonator and evaporator coil, the two flavor
reservoirs, their dry reed channels and the surrounding pour-in-place foam.
The casing has three pieces: this shell, a uniform top equipment lid and an
open-topped bottom cap. A separate small R14 holder locates the B-fill tube bend.

## Dimensions and datums

The smooth rounded footprint is 282.4 × 180.4 mm, with 11.7 mm outside corner
radii, 2.38 mm standing walls and a 2 mm structural floor. The printed shell is
225.85 mm high. The internal vessel, reservoir and coil layout uses its fixed
213.4 mm upper datum; extending the casing does not change those stations.

In the appliance the shell's base is Z20 mm, its rim Z245.85 mm, and the top
lid underside Z246 mm. The 7.4 mm lid presents its equipment face at Z253.4 mm.
The bottom cap stands on Z0 and seats 0.15 mm below the shell base. The complete
casing therefore remains 253.4 mm high.

The main body's mouth is open for lowering the finished vessels, routing tubes
and pouring foam. The straight fill, draw and air tubes are installed in their
reservoir grips before the body pour, with their upper ends located on the lid-hole axes. After
cure these ends pass through the lid; the dip sections remain free inside the
closed reservoirs. The B-fill
R14 guide is installed with its tube after the vessels are seated.

## Vessel supports and pockets

The carbonator support ring and both reservoir pockets retain their native
positions. The ring supports the carbonator rim and leaves its bottom fittings
in open space. Reservoir pockets retain their 0.25 mm clearance to the bodies.
Before the body pour, bridge each closed reservoir cap's perimeter to its pocket
rim with burnished 3M 425 foil tape. This closes the 0.25 mm running gap and keeps
foam out of the pocket clearance and reed sensing windows. Leave tube lumens and
reed-channel entry mouths open. The syrup-wetted bodies and lids are PETG
Translucent; the surrounding shell is PET-GF. The coil's 7 mm radial envelope, vessel ports, copper tails, and all
reservoir wet interfaces belong to their respective native generators.

The two dry reservoir reed channels continue to the raised rim. Their sensing
windows keep their full opening to the internal body datum, then peak
across their 8 mm width over an 8 mm rise, with 4.45 mm of header stock.
Backing above those windows keeps pour
foam out of the channels. Reservoir A's leads leave through the lid bore;
Reservoir B's leads use the fore side window below the rim. Its peaked roof
rises 8 mm above the straight cable opening and retains 4.2 mm of header stock.
Mask the channels
for the pour and install the proved reed columns before closing the lid.

## M5 closure stations

Each face takes ten M5 × 100 fully threaded socket-head screws in RX-M5×9.5
inserts. Shell-native stations are X±135.4 at Y−60/0/+60, and X45/110 at Y±84.4 mm.
They clamp the short ends and aft long flanks while clearing the tube lanes,
PCB inserts, and copper exits. The spun top lid carries the inverse pattern;
the bottom cap uses the shell pattern directly.

Each Ø6.4 × 10.5 mm insert pilot has 2.6 mm radial stock in an Ø11.6 host
joined to the outer wall. The same section runs between both insert faces,
leaving 3.2 mm around the Ø5.2 screw-tail passages. Each tail has 2.5 mm of
full-bore nominal tip air. Bottom-facing pilot transitions and blind ends
narrow by 0.5 mm per millimetre of build rise, above their complete cylindrical
clearance depths. The casing wall remains continuous behind the host webs.

The upper screws reach 97.6 mm past their mouths; lower screws reach 85.4 mm.
Both take the same acquired M5 × 100 stock as the enclosure's seam screws.
Heads are Ø8.5 × 5 mm, with 4 mm hex sockets, seated in Ø9 outward-open pockets.
Exterior foil bands cover the dry pocket mouths and perimeter joints.

## Plumbing and cable passages

All wet paths are continuous tubes or their specified fittings. The main foam
closes on their outside surfaces. The lid's quarter-inch passages are Ø7.5 mm;
reservoir air-tube passages are Ø5.2 mm for separate 4 mm tubes. B-fill uses the
accepted Ø6.8 teardrop-channel R14 holder, with a plain lid clearance window.
The PCB's four full-length M3 inserts belong to the lid, above its flat bed face.

The water line keeps R14 turns in the west lane. Its two opposed turns pass
inboard of the M5 host before reaching the outer lane and fixed lid guide.
The CO2 descent stands 2.5 mm inboard of the copper lane and retains R14 turns
and the complete support-ring slot crossing. The soda and gas lines,
PRV vent, reservoir tubes and carbonator sensor/earth loom retain their endpoints.
## Copper feed-throughs

The two copper feed-throughs are round Ø7.5 mm holes at native Y±77.5,
Z28.425 mm, pointing out of the −X face. The nominal Ø6.35 copper has 0.575 mm
radial clearance. Feed the bare tails during the carbonator's descent, then form
the final bends and close each annulus with burnished 3M 425 collars per the
[assembly procedure](../../../assembly/cold-core.md#5-body-side-install).

## Seam channel

The +Y casing seam channel is 9.5 mm wide and 1.5 mm deep. Its folded inner face
retains the 2.38 mm wall section to the full raised rim. The PRV's vent chase
retains its separate open discharge route.

## Bottom foam and open-body pour

The bottom cap is a single open-topped tray. Its 2 mm floor and 19.85 mm total
height leave 17.85 mm of central foam below the shell's fixed base. Four Ø30 mm
ports at native X±75/Y±40 distribute the charge directly across its four quarters.
Two Ø6 air vents remain. Foam reaching a vent is not the fill criterion.

Attach the bottom cap to the empty shell with its ten screws, mask the dry seam
and head pockets, and invert the empty shell onto its upper rim. Distribute the
measured charge through the four underside ports within the manufacturer's working
time. Cure, trim and foil-patch the ports and seam. Return the casing upright
before installing the vessels. The top body pour is made with the equipment lid off.

The foil allowance is 0.30 mm per casing face, containing at most two 0.12 mm
3M 425 layers. Tape sits on the smooth exterior and stays off bearing/seating faces.
Perimeter bands, underside port patches and the dry guide-window boundary form the
specified casing closures. Fluid lumens, reservoir air tubes and the PRV discharge
remain open. Complete-appliance readiness is recorded in
[print readiness](../../enclosure/print-readiness.md).

## Print settings

Print the shell floor-down on the configured Mark2 left 0.4 mm hardened Standard-flow nozzle.
Use the saved PET-GF recipe, three Classic walls and 15% gyroid. The current
casing's [kernel print review](kernel-print-review.json) binds the exact Rust
STL, full-bead bed margin, local solid deposition and support bodies. The
[native print review](printability-review.json) supplies its comparison slice.
The [local solid regions](../foam-cap/fore-snap-print-regions.json) fill all ten
M5 hosts and their wall roots at 100%; the surrounding casing keeps its bulk recipe.
The top lid prints on its uniform flat underside; the bottom cap prints on its
outside floor. Print the R14 holder flat on its D back. Its teardrop channel
prints without trapped tunnel supports. Follow the repository's Tree(auto)/Default
policy for other accessible supports; no new support override is prescribed here.

Use the smooth `.stl` print export. The kernel writes the STEP and the full-precision
`.step.npz` model beside it; `.step.mesh` is the viewer surface cut from the STL.
Native assembly callers retain the shell's construction builder.

Assembly sequence: [cold-core assembly](../../../assembly/cold-core.md).
Component geometry: [cold-core layout](../../../cold-core-layout/README.md).
Top and bottom details: [closure reference](../foam-cap/README.md).

## Sources

[Python datums](foam_shell.py), [kernel geometry](foam_shell.rs), and
[native construction builder](../_foam_shell.py).
