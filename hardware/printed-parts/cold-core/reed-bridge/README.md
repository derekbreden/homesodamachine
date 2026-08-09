# Carbonator reed bridge

The mount for the carbonator vessel's two external level reeds. A printed
PETG interposer that holds each reed against bare 316L on the register
azimuth and stands the evaporator coil off the glass where a wrap crosses
it. One per vessel, plus a reusable setting gauge that places it.

Geometry is owned by [`reed_bridge.py`](reed_bridge.py). The magnet-to-reed
coupling it is sized against is in
[`../reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)
"Magnet–reed signal-path geometry".

## What the reed sits in

The donut is an axially-magnetised ferrite ring. Radially outside it, on
its mid-plane, the field is purely axial — the radial component vanishes by
symmetry on the equatorial plane, the tangential component by axisymmetry.
Both reeds stand with their glass vertical; a reed tilted θ off vertical
couples as sin θ.

The wind's pitch is [12.33 mm](WRAP_PITCH) over [6.35 mm](COPPER_OD) tube,
leaving [5.976 mm](INTER_WRAP_CLEAR) of bare wall between adjacent wraps at
any one azimuth. The glass envelope is [14 mm](REED_GLASS_L), so a reed
standing vertical spans at least one wrap and at most two.

Each reed lies in a pocket cut clear through the bridge to the wall — the
pocket floor is the vessel's steel. The plateau around it stands
[3 mm](POCKET_DEPTH) proud, clearing a ⌀[2.5 mm](REED_GLASS_D) glass
envelope by copper_clearance_over_glass. Nothing sits between the reed and
the wall.

## What holds it

| Stage | Holding it |
|---|---|
| Bench handling, foil skinning | A 3M 425 capture patch over each pocket, then the continuous 3M 425 skin over the whole bridge |
| Coil transfer | Ramps on all four sides — [10 mm](AXIAL_RAMP) axial, [16 mm](ARC_RAMP) circumferential — that each wrap rides up and over |
| Drop into the foam-shell cavity | The coil's hoop tension, clamping the bridge to the wall; the coil envelope stands ~3.4 mm outboard of the plateau |
| Foam pour | Cured closed-cell PU |

## The two heights

Measured up from the tube's **bottom rim** — the face that seats on the
tank support ring.

**The column.** Each end plate is an ID-fit plug recessed 1/4" below its
tube end. The wetted column runs from the bottom plate's inside face at
[12.7 mm](INTERIOR_FLOOR) to the top plate's inside face at
[139.7 mm](INTERIOR_CEILING) — [127 mm](INTERIOR_H) of height in a
[123.7 mm](TUBE_ID_MM) bore, [12.02 mL](ML_PER_MM) per mm,
[1526 mL](INTERIOR_ML) brim-full.

**The serving.** 12 US fl oz of finished soda at the syrup's 1:20 ratio is
[338.1 mL](WATER_PER_SERVING) of carbonated water — [28.13 mm](SERVING_RISE)
of level.

**CHI — pump off** at 65 % of the wetted height: level
[95.25 mm](HIGH_LEVEL). [992 mL](STORED_ML) = [2.93](STORED_SERVINGS)
servings stored above the floor, [534.2 mL](HEADSPACE_ML) of CO2 headspace
(35 %) above it for the sparge column and the level surge.

**CLO — pump on** one serving below: level [67.12 mm](LOW_LEVEL). The
refill increment is one drink. Below CLO, [654 mL](RESERVE_ML) =
[1.93](RESERVE_SERVINGS) servings of reserve.

**Reach.** The donut's magnetic mid-plane travels between
[20.2 mm](MAGNET_LOWEST), sitting on the rod's tack bead, and
[133.7 mm](MAGNET_HIGHEST), against the top plate. Both reed heights fall
inside the wind band, [15 mm](BAND_BOTTOM) … [134.4 mm](BAND_TOP).

**Azimuth.** The rod parks the donut [3 mm](MAGNET_WALL_BIAS) into the bore
wall, so the magnet-to-wall gap is zero on the register line and opens as
the reed walks off it — 0.7 mm at 5 mm of arc, 2.8 mm at 10 mm. The bridge
goes within ±5 mm of arc of the register line.

## The part

Cylindrical shell segment on a 127 mm OD, [3 mm](POCKET_DEPTH) proud at the
plateau, [0.8 mm](SKIRT_T) at the skirt.

- **Extent** — Z [46.12 mm](BRIDGE_Z_BOTTOM) … [116.3 mm](BRIDGE_Z_TOP),
  [70.13 mm](BRIDGE_H) tall × [51.4 mm](BRIDGE_ARC) of arc,
  [6.65 cm³](BRIDGE_VOL) of PETG.
- **Reed pockets** — two, [16 mm](POCKET_L) × [3 mm](POCKET_W), through to
  the wall, centred on the two reed heights. The part is symmetric end for
  end. Lower reed is `CLO`, upper is `CHI`.
- **Lead groove** — [5.6 mm](LEAD_GROOVE_W) × [2.15 mm](LEAD_GROOVE_D),
  offset off the pocket column, carrying `CLO`, `CHI` and the shared common
  out the top edge. A cross-notch at each pocket end brings that reed's
  leads into it.
- **Copper it carries** — [5.69](WRAPS_CARRIED) wraps cross the bridge; at
  full standoff over the plateau and half over the ramps, that is
  [35.4 mm](EFFECTIVE_ARC) of arc each, [201 mm](CARRIED_COPPER) of the
  3.877 m wrap — [5 %](CARRIED_FRACTION).

**Print** — PETG, outer (convex) face down on the plate, no supports.

## Setting gauge

`reed-bridge-setting-gauge.step` — a [60°](GAUGE_ARC_DEG) band that hangs
on the tube's bottom rim by an inward hook. Its top face is at
[46.12 mm](BRIDGE_Z_BOTTOM), the bridge's bottom edge.
[7.68 cm³](GAUGE_VOL) of PETG. Shop tooling, printed once and reused across
vessels like the coil mandrel.

## Bench procedure

1. Solder the two reeds to their three 22 AWG silicone conductors (`CLO`,
   `CHI`, shared common); heat-shrink every joint and every bare lead — the
   3M 425 skin is aluminium. Prove each reed with the donor magnet.
2. Hang the setting gauge on the tube's bottom rim, sight the register line
   90° off the two end-plate ports, mark the bridge's bottom edge.
3. Lay the reeds into the pockets, leads into the groove, a 3M 425 patch
   over each pocket. Prove both reeds through the wall with the donor
   magnet, sliding it along the register line.
4. Seat the bridge on the mark; a wrap of 3M 425 over each ramp end holds
   it. Skin the vessel per [`cold-core.md`](/hardware/assembly/cold-core.md)
   §1 — the foil goes over the bridge, burnished down onto both ramps.
5. Lead the three conductors up the register line, outboard of where the
   coil sits, to the +Z slot.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py`
