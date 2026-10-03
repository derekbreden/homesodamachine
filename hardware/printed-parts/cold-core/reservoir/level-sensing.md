# Flavor reservoir level sensing

Each flavor reservoir carries one **ASA Aero float with an RC62 magnet** on
a 1/8 in 316 SS rod. Four **Littelfuse MDSR-7-10-15** reeds stand outside the
reservoir in the foam-shell channel. The float and installation datums are in
[the shared float interface](../magnetic-float/all-aero/installation.md).

## Guide and float

The rod axis is `(x = ±[106.25](ROD_POSITION_X), y = +[32.5](ROD_POSITION_Y))`
in the assembled cold-core frame. It is **[20 mm](ROD_WALL_DISTANCE)** inward
from the wet far wall at `x = ±[126.25](CAVITY_FAR_WALL_X)`. The float is
**[36 × 28 mm](FLOAT_SIZE)** with a 4.8 mm through bore, sliding on the
**[3.175 mm](ROD_DIAMETER)** rod. Its magnet center is 14 mm above its bottom.
This leaves 2 mm nominal wall clearance, with 1.1875 mm minimum under upright
radial guide motion. Finished foam expansion and free travel need physical checks.

Cut each rod to **[176.5 mm (6.95 in)](RESERVOIR_ROD_LEN)**. The lower end seats
in a blind bore in a standing boss on the body's wet slope. The upper end enters
the matching cap boss. The bosses share the same XY axis and are wider than the
float bore, so they define its travel stops. The wet slope remains uncut beneath
the lower rod seat. Rod end clearance is [0.15 mm](ROD_END_CLEARANCE); the cap must seat on its gasket.

The magnet-center travel is **[52.48–188.15 mm](FLOAT_TRAVEL)** in the assembled
frame. Four provisional reed centers are **[52.82, 97.82, 142.82, 187.82](REED_CENTRES)
mm**, at 45 mm pitch. These accessible CAD stations are seeds for calibration,
not quarter-volume measurements or final full/empty control thresholds.

## Reed channel and wiring

Each column has **[4](REEDS_PER_RES)** vertical reeds, four signal conductors and
one common return in BNTECHGO 22 AWG black silicone 5P ribbon. Solder and lace
the column after [liquid calibration](../magnetic-float/all-aero/installation.md#reed-calibration)
sets its positions. The 14 × 2.5 mm CAD capture envelope includes glass, tape
and lead room; it is not a claim about the MDSR-7's glass dimensions.

The foam shell's channel is a three-sided box projecting outward from the
reservoir's far wall, centered on the same +Y rod/reed plane. It is open at the
top and has a bottom shelf. The column drops into this dry channel after the
foam pour has cured; it is mechanically captured by the shelf, sides and cap.
It is not embedded in foam. The cable rises directly through the cap's
**[6.8 mm](CONDUIT_BORE_D)** conduit at
[reed-cable-a (134.5, 31), reed-cable-b (-134.5, 31)](REED_CONDUIT_XY).
The −X face stays flat against the refrigeration base. The fluid draw exits
through each pocket's −Y wall at x = [±97](FLAVOR_HOLE_X).

The greatest float-edge-to-reed-center distance is **11.063 mm**, including
upright bore play; the corresponding RC62-edge distance is 19.538 mm. The
initial design maximum is **18 mm from float edge to reed center**, based on
the [printed-float report](../magnetic-float/README.md#reed-reach) of a usable
20 mm limit. The 20 mm rod-to-inside-wall datum supplies running room. Actual
installed directional crossings and all-reed acceptance remain unmeasured.

Reservoir A's four signals use MCP23017 0x20 PB[0:3]; reservoir B's use 0x21
PB[0:3]. They reach the main board on the J6/J7 looms; there is no expander
inside the cold core. [Wiring map](/hardware/wiring/valve-control.mmd) and
[cable assemblies](/hardware/assembly/cable-assemblies.md) define terminations.

## Level interpretation and calibration

One moving magnet closes a reed as it passes. The firmware tracks the last
crossing and whether the machine is filling or drawing; the highest active reed
wins if windows overlap. It retains the level between sensors. It does not
interpret all reeds below the water surface as closed.

The display has five states from empty through full. Locate the end thresholds
at reachable liquid crossings, then place the two intermediate reeds at measured
volume fractions. Equal height spacing is an initial layout, not proof of equal
volume or servings. The float's immersed volume and the reservoir's shaped
floor matter at the bottom of its travel. The finished-float
[calibration procedure](../magnetic-float/all-aero/installation.md#reed-calibration)
gives the tools, direction-dependent measurements and placement criteria.

## Parts and service

Each build uses three printed ASA Aero floats and three RC62 rings, including
the carbonator, and ten MDSR-7-10-15 reeds. Rods, silicone ribbon and those
purchased parts are in [BOM §12](/hardware/ledger/bom.md).

Removing the cap releases the rod's upper register. Lift the rod and float out
of the lower boss, or leave the rod standing and lift the float off it. The
reed column can be withdrawn through its open channel after the cap is lifted.
Confirm the 6 × 8 mm channel and cable exit pass the soldered/laced column
before fixing its final wire layout. Reservoir leak acceptance applies to the
reservoir prints that were tested; it does not establish foam-float immersion,
pressure life or flavor compatibility.

## Sources

[value](NAME) figures are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
- `/hardware/assembly/_cold_core_sync.py`

Reed evidence and calibration are kept beside the [float](../magnetic-float/README.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py`
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
