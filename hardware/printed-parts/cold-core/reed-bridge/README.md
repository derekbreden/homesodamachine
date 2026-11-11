# Carbonator reed bridge

The mount for the carbonator's two external level reeds, installed on the
foam shell's −Y azimuth opposite both reservoirs' +Y sensing stations. A printed
PETG interposer that holds each reed against bare 316L on the register
azimuth and stands the evaporator coil off the glass where a wrap crosses
it. One per carbonator, plus a reusable setting gauge that places it.

[`numbers.rs`](numbers.rs) holds the bridge's dimensions and profiles, and
[`reed_bridge.rs`](reed_bridge.rs), the build step, writes the bridge and setting
gauge as STEP, f64 models, STL and viewer payloads from them. The magnet-to-reed
coupling it is sized against is in
[`../reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)
"Magnet–reed signal-path geometry".

## What the reed sits in

The inserted magnet is an axially magnetised RC62 N42 ring. Radially outside it, on
its mid-plane, the field is purely axial — the radial component vanishes by
symmetry on the equatorial plane, the tangential component by axisymmetry.
Both reeds stand with their glass vertical; a reed tilted θ off vertical
has a smaller axial projection as it tilts.

The wind's pitch is over tube,
leaving of bare wall between adjacent wraps at
any one azimuth. The mounting envelope is, so a reed
standing vertical spans at least one wrap and at most two.

Each reed lies in a pocket cut clear through the bridge to the wall — the
pocket floor is the carbonator's steel. The plateau around it stands
 proud, clearing a ⌀ capture
envelope by copper_clearance_over_glass. Nothing sits between the reed and
the wall.

## What holds it

| Stage | Holding it |
|---|---|
| Bench handling, foil skinning | A 3M 425 capture patch over each pocket, then the continuous 3M 425 skin over the whole bridge |
| Coil transfer | Ramps on all four sides — axial, circumferential — that each wrap rides up and over |
| Drop into the foam-shell cavity | The coil's hoop tension clamps the bridge to the wall |
| Foam pour | Cured closed-cell PU |

## The two heights

Measured up from the tube's **bottom rim** — the face that seats on the
carbonator support ring.

**The column.** Each end plate is an ID-fit plug recessed 1/4" below its
tube end. The wetted column runs from the bottom plate's inside face at
 to the top plate's inside face at
 — of height in a
 bore, per mm,
 brim-full.

**The serving.** 12 US fl oz of finished soda at the syrup's 1:20 ratio is
 of carbonated water —
of level.

**CHI — pump off** at 65 % of the wetted height: level
. =
servings stored above the floor, of CO2 headspace
(35 %) above it for the inlet jet and the level surge.

**CLO — pump on** one serving below: level. The
refill increment is one drink. Below CLO, =
 servings of reserve.

**Reach.** The Aero float's magnetic midplane travels between
, sitting on the rod's tack bead, and
, against the 4 mm stainless stop below the top plate. Both reed heights fall
inside the wind band, ….

**Reed centres and calibration.** The geometric seed centres are
CLO and CHI, above the tube bottom rim.
The 28 mm float's magnet is relative to the waterline
at the assumed 0.65 g/cm³ foam density. These seed centres align magnet and
reed; they do not predict the rising/falling contact thresholds. Measure the
finished float in water through the actual stainless wall before printing a
final bridge or bonding it in place. [Calibration and datums](../magnetic-float/all-aero/installation.md).

**Azimuth.** The rod axis is 20 mm inside the wet wall. The float has
 nominal body clearance and ±0.8125 mm radial guide
motion. The conservative nearest RC62-edge to reed-centre distance is at most
14.189 mm on this azimuth. Keep the reeds vertical. The mount retains a
14 × 2.5 mm envelope for the smaller MDSR-7-10-15 glass and capture tape.

Stored liquid and headspace estimates include the assumed immersed float
volume and the guide rod. They require a dry, undeformed float; pressure,
wetting and actual density can change them.

## The part

Cylindrical shell segment on a 127 mm OD, proud at the
plateau, at the skirt.

- **Extent** — Z …,
  tall × of arc,
  of PETG.
- **Reed pockets** — two, ×, through to
  the wall, centred on the two reed heights. The part is symmetric end for
  end. Lower reed is `CLO`, upper is `CHI`.
- **Lead groove** — ×,
  offset off the pocket column, carrying `CLO`, `CHI` and the shared common
  out the top edge. A cross-notch at each pocket end brings that reed's
  leads into it.
- **Copper it carries** — wraps cross the bridge; at
  full standoff over the plateau and half over the ramps, that is
  of arc each, of the
  3.877 m wrap —.

**Print** — PETG, outer (convex) face down on the plate, supports off. The lead-groove floor
bridges above the bed; its retained strands have a 0.25 mm allowance in the
groove depth. The outer plateau supplies that room, preserving the full
0.8 mm skirt backing, tube seat, and reed-glass bearing plane. The glass
pockets pass completely through the bridge.

## Setting gauge

`reed-bridge-setting-gauge.step` — a band that hangs
on the tube's bottom rim by an inward hook. Its top face is at
, the bridge's bottom edge.
 of PETG. Shop tooling, printed once and reused across
carbonators like the coil mandrel.

## Bench procedure

Complete the [finished-float calibration](../magnetic-float/all-aero/installation.md#reed-calibration)
before printing the bridge/setting gauge or fixing the reed heights.

1. Solder the two reeds to their three 22 AWG silicone conductors (`CLO`,
   `CHI`, shared common); heat-shrink every joint and every bare lead — the
   3M 425 skin is aluminium. Prove each reed with the printed RC62 float.
2. Hang the setting gauge on the tube's bottom rim, sight the register line
   beyond the negative port on the port diameter, mark the bridge's bottom edge.
3. Lay the reeds into the pockets, leads into the groove, a 3M 425 patch
   over each pocket. Prove both reeds through the wall with the RC62 in the
   finished ASA Aero float, sliding it along the register line.
4. Seat the bridge on the mark; a wrap of 3M 425 over each ramp end holds
   it. Skin the carbonator per [`cold-core.md`](/hardware/assembly/cold-core.md)
   §1 — the foil goes over the bridge, burnished down onto both ramps.
5. Keep the reed bridge at its register azimuth. Lead CLO, CHI and their
   continuous common up outside the coil, then transfer them over the open
   vessel head at enclosure Z225/Y352 before the body foam pour. Join the
   shared west-side seven-core loom at X−48/Y347; its other cores are the
   three temperature-bus leads and green 16 AWG carbonator earth lead. The
   loom follows an R5.5 transition to the Ø7.5 mm equipment-lid opening at
   X−78/Y320/Z253.4. Lay it before the pour; foam locates it below the lid.
   Thread the free ends through the lid before fitting outside terminations,
   then dress the three reed ends to J7 and the existing reed-common WAGO.
