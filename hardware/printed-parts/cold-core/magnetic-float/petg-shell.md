# PETG shell: recipe and thickness

The bench float has a **3 mm outer wall, 1.8 mm bore lining, 3 mm floor and
3.06 mm roof**, printed in **Bambu PETG Translucent Clear 32101**, the reservoir
filament, using the researched 0.6 mm sealing process. Its 36 × 60.06 mm envelope has 4.96 g of reserve lift at
0.55 g/cm³ Aero density. This is the specified first pressure-test article.

[petg-translucent-recipe.json](petg-translucent-recipe.json) records material
GFG01, transparent color `#00000000`, the current reservoir project's identity,
the native Translucent preset and the material-specific limits. The print uses
the successful PETG Basic recipe's sealing controls with Translucent's
1.25 g/cm³ density and 16 mm³/s volumetric ceiling.

## Physical evidence in this repository

The [reservoir print log, attempt 3](../reservoir/print-log.md)
records hours of water retention with the gaskets installed. The exact printed
project is at [f25975cd045cc835eccf1a207cb12fe48dc63ada](https://github.com/derekbreden/homesodamachine/blob/f25975cd045cc835eccf1a207cb12fe48dc63ada/hardware/printed-parts/cold-core/reservoir/reservoir.3mf).
Its active PETG is **GFG00, PETG Basic**, custom-named `Bambu PETG Water`.
[petg-water-recipe.json](petg-water-recipe.json) extracts the active left-nozzle
settings and records the source file's SHA-256. Later Translucent reservoir
projects have different settings and no success result recorded in that log.

The [archived water-test cup log](https://github.com/derekbreden/homesodamachine/blob/archive-water-test-cup/hardware/reference/water-test-cup/print-log.md)
records a successful first water-holding print with the same PETG Water recipe
and 3 mm walls/floor. The reservoir's current
[watertight PETG guide](../reservoir/watertight-petg.md) explains sealing paths,
cooling, floor fill and seam treatment.

The sphere pressure test is recorded in
[commit b7dc4d576](https://github.com/derekbreden/homesodamachine/commit/b7dc4d576e9dc38794d190f31473f31d71aa4aa1):
its printed NPT port wept at **5 psi or less**. The
[archived sphere generator](https://github.com/derekbreden/homesodamachine/blob/archive-plan-b/hardware/printed-parts/plan-b/carbonator-tank-sphere/generate_step_cadquery.py)
has 5 mm walls. The recovered sphere test history is incomplete. This commit
records one threaded-port leak; it does not describe the outcomes of the other
sphere trials. Their pressures, hold times and leak locations remain missing
from the recovered evidence. This fragment establishes no pressure limit for
the unpierced PETG wall.
The [commit map](/tools/git-history/README.md) resolves older transcript SHAs.

## Published pressure evidence

The [pressure-printing review](pressure-printing-research.md), checked through
September 2026, documents uncoated PETG fittings holding substantial internal
water pressure, a heat-treated PETG system's 24-hour operating result, and
controlled studies of flow, layer height and pause bonding. It includes an
audit of the fitting authors' actual projects and G-code, including discrepancies
with their paper. Those findings establish pressure-sealing feasibility and
support the process choices here; they do not assign this float an external
collapse pressure or a service life.

## Printing recipe

| Parameter | Float setting | Basis |
| --- | --- | --- |
| Left nozzle | 0.6 mm standard flow | Successful reservoir |
| PETG temperature, first / subsequent | 255 / 260 °C | Successful reservoir |
| Flow | 1.02 | Successful PETG Basic reservoir sealing recipe |
| Maximum volumetric speed | 16 mm³/s | Native PETG Translucent preset |
| Textured bed | 70 °C | Successful reservoir |
| Layer, first / subsequent | 0.30 / 0.18 mm | Successful reservoir |
| Lines / requested walls | 0.60 mm / six, Arachne | Successful reservoir |
| Solid fill | 100% zig-zag, 15% wall overlap | Successful reservoir |
| Floor/top surface | Zig-zag, top ironing 10%, 0.15 mm spacing | Successful reservoir |
| Wall order | Inner then outer | Successful reservoir |
| Seam | Random, scarf all walls, 10% start height | Successful reservoir |
| Part cooling | 10–20%, first three layers off, auxiliary off | Successful reservoir |
| Scarf condition / seam gap | Unconditional / 0% | Continuous circular sealing walls |
| Outer / inner / solid / top speeds | 40 / 60 / 60 / 30 mm/s | Small sealing article |
| Bridge / internal bridge flow | 1.0 / 1.0 | Roof rests on the Aero insert |
| Bridge speed / overhang fan | 20 mm/s / 20% | Roof rests on the Aero insert |
| Floor / roof layers | 16 / 17 | 3.00 / 3.06 mm solid thickness |

The 255/260 °C nozzle targets are within Bambu's Translucent recommendation of
230–260 °C. Unconditional scarf, zero seam gap, the slower speeds, bridge controls and
floor/roof layer counts are float-specific adaptations. This material/process combination has no
separate physical float result yet. Six requested walls is a slicer limit;
actual thickness is the CAD dimension, covered by variable-width bead paths.
The [verification](verification.json) checks the emitted paths, including
nominal wall coverage along twelve radial samples at mid-height.

The 1.02 flow is 5.15% above the source material's 0.97 stock baseline.
Published extrusion multipliers depend on material, printer and slicer.
The [mass sensitivities](pressure-printing-research.md#flow-thickness-and-buoyancy-together)
show why copying a higher multiplier indiscriminately consumes useful lift.

The Aero parts print separately on the right 0.4 mm nozzle at their own
270 °C / 90 °C bed / 60 °C chamber recipe. The PETG shell contains no
PETG-to-ASA material changes. Its pause is after Z57.00; its first roof layer
is Z57.18. A fully seated foam insert backs that layer across the annulus.
Seat the RC62 in the cooled core on the bench and set out the insert and tools
before the shell print. Keep the bed at 70 °C, lower the prepared core and
insert chamfered ends first, press the insert level with the rim, close the
enclosure and resume promptly. The resumed interface has no measured PETG
bond-strength result.

## Thickness and pressure loads

The outer cylinder is loaded in compression and can ovalize under external
pressure. The bore lining sees water on its inside and is loaded in hoop
tension. They do not have the same required thickness. The bore's 1.8 mm wall
provides approximately three 0.6 mm paths while leaving foam between PETG and
the RC62. The 4.8 mm bore clears the 3.175 mm rod by 0.8125 mm radially.

The outer wall and end caps have the 3 mm material depth demonstrated by the
water-holding parts. The floor is one 0.30 mm layer plus fifteen 0.18 mm layers.
The roof is seventeen 0.18 mm layers. A 54 mm interior height accommodates
44 mm and 10 mm Aero pieces printed in complete 0.20 mm layers. Their upper
and lower faces seat directly together; the tall core rests on the PETG floor
and the insert covers the complete roof annulus. The 0.5 mm lower-edge lead-ins
and magnet-pocket clearance account for 0.124 cm³ of intentional internal
relief. The outer wall, bore lining and PETG end caps remain continuous.

The buoyancy calculation includes the RC62's 5.09 g mass, PETG at 1.25 g/cm³,
and foam at 0.55 g/cm³:

| Envelope with the specified thick shell | Reserve lift |
| --- | --- |
| 28 × 50 mm, 3 mm outer/end walls and 1.8 mm bore lining | −2.12 g |
| 36 × 60.06 mm, specified shell | +4.96 g |

At the same 36 × 60.06 mm envelope, increasing only the outer wall to 3.6 mm
reduces this estimate to 2.87 g; 4 mm reduces it to 1.52 g. Additional PETG
replaces Aero within the fixed exterior volume. The specified 3 mm wall
preserves useful lift while providing material depth and ovalization resistance.
The [research calculation](pressure-printing-sources.json) records this tradeoff.

[pressure_analysis.py](pressure_analysis.py) produces the independent annulus
calculation and the pressure/stiffness sensitivity in
[pressure-analysis.json](pressure-analysis.json). With full pressure differential
and no structural credit for the foam, Lamé thick-cylinder equations give:

| External pressure | Outer-wall hoop compression | Bore-wall hoop tension | Annular end load |
| --- | --- | --- | --- |
| 90 psi | 4.06 MPa | 1.22 MPa | 620 N |
| 125 psi | 5.64 MPa | 1.70 MPa | 862 N |
| 180 psi | 8.12 MPa | 2.44 MPa | 1,241 N |

These are loads/stresses away from the end junctions, not allowable stresses.
The published PETG Translucent XY Young's modulus is 1,420 ± 160 MPa in
[Bambu's material data](https://cdn.shopify.com/s/files/1/0574/3116/2995/files/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf?v=1704680051).
Those specimens were conditioned at 65 °C for eight hours; the mean is a
material-screen input, not the assembled shell's measured modulus.
The simple homogeneous ovalization screen
`p = E × (t/r_mean)^3 / [4(1−ν²)]` follows equation 27 in
[NASA SP-8007 Rev 2](https://ntrs.nasa.gov/citations/20205011530).
At an assumed Poisson ratio of 0.38, the 3 mm wall gives 362 psi ideal pressure;
50% of that is 181 psi. At an assumed reduced modulus of 1,000 MPa, those values
are 255 and 127 psi. The 50% factor is a sensitivity assumption, not an FDM
knockdown factor. The cube dependence makes wall thickness important even when
simple compressive stress is modest.

That screen does not rate this short, relatively thick, anisotropic printed
shell. It does not qualify end-cap bending, seam porosity, pause-layer bonding,
creep or foam crushing. The intact foam provides contact support, but Bambu
publishes no applicable 270 °C-printed ASA Aero hydrostatic/compressive endurance
value. A 180 psi external test corresponds to a possible 1.24 MPa contact load
on that foam. The source evidence and calculations support this first article;
its measured pressure endurance remains the result of the assembled float's
pressure test.
