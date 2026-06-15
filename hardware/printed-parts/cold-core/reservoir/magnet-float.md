# Magnet Float

Companion to `magnet_float.py`. A purpose-printed buoyant float for the flavor-reservoir level sensing in [`level-sensing.md`](level-sensing.md), replacing the harvested DEVMO donut with an embedded neodymium ring magnet so the external wall reeds trip with the magnet held off the wall — no scrape fit.

## Donor magnet

An axially-magnetized **N52 sintered-NdFeB ring**, AplysiaTech [B0GD15CWCL](https://www.amazon.com/dp/B0GD15CWCL): [25.4 mm](MAGNET_OD) OD × [12.7 mm](MAGNET_ID) ID × [3.18 mm](MAGNET_T) thick, ≈ [9.1 g](MAGNET_MASS). Br ≈ 1.3 T — roughly 4× the ferrite donut's field at equal size, which is the whole reason to carry the buoyancy penalty below.

## Geometry

Axisymmetric PETG puck, **[30 mm](FLOAT_OD) OD × [29.14 mm](FLOAT_H) tall**, sliding on the 1/8" 316 SS rod through a [3.775 mm](BORE_D) center bore (rod + free-slide clearance). The ring sits concentric at the bottom of an internal annular cavity, located radially by its OD against the pocket wall; the buoyancy void fills the cavity above it. Floor, side wall, bridged roof, and the central bore tube fully encase the magnet — the only wetted material is PETG, the only wetted metal stays the rod.

## Buoyancy

Neodymium is dense and PETG itself sinks in the syrup, so every gram of lift comes from a sealed air void. Sized for the ≈ [9.1 g](MAGNET_MASS) magnet at a design syrup density of [1.10 g/cm³](SYRUP_RHO) (Pepsi-made sucralose 1:20 concentrate — near water, no sugar; designed at the low end so it floats if the syrup runs denser), the void is **[21.46 mm](VOID_H) tall** and the assembled float carries **[1.15×](RESERVE) reserve buoyancy**. The magnet at the bottom puts the center of mass low, so the float rides upright.

`magnet_float.py` solves the void height from these densities; change `syrup_density`, the magnet dimensions, or `reserve_buoyancy` and the float re-sizes.

## Print-pause embed

Print mouth-up. Pause when the print reaches **Z = [5.18 mm](PAUSE_Z)** (floor + magnet thickness) — the magnet pocket is then open and exactly ring-deep. Drop the ring over the bore tube onto the floor, resume, and the walls continue up to form the void before the roof bridges it closed.

The resume pass lays the void walls directly beside the ring, not over it; the nozzle only crosses the magnet later when the roof bridges, several layers above. Capture the ring (snug pocket + a dab of CA) so it can't jump to the nozzle, and run the first post-resume layers slow.

## Watertightness

Carry the reservoir's watertight PETG recipe ([`watertight-petg.md`](watertight-petg.md)): arachne walls, 100% infill, ironing. The one new risk is the roof — a bridge across the full radial span of the cavity top; it gets the extra thickness and ironing so it seals. Fill-and-hold a printed float before trusting it.

## Cavity fit

At [30 mm](FLOAT_OD) OD the float is wider than the 27.75 mm donut it replaces, so it sits tighter against the −Y/far-corner screw boss — already the tightest clearance in the cavity. Two levers: the N52 field headroom means the rod no longer has to ride the wall, so `ROD_POSITION_X` can move back toward center to recover boss clearance; or a smaller/lighter magnet shrinks the float (the script re-sizes). Re-check the donut sweep against that boss before committing.

## Calibration coupon

Before the full float, a flat coupon prints the reservoir wall thickness in PETG with a reed slot on one face and stepped magnet seats at 1–6 mm gaps on the other, to measure reed pull-in vs. magnet-to-reed distance with this exact ring — fixing how far off the wall the float can ride.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/magnet_float.py`
