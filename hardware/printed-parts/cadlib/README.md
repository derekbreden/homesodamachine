# cadlib

CadQuery library code shared across generators in this repo. Reusable helpers that don't belong inside any one generator's directory.

Read `_world_workplane.md` if your generator uses `xz_plane_y_up` (or any other workplane with a registered non-identity frame transform).

`world_workplane.py` is the world-coordinate interface: CadQuery reads coordinates in a workplane's own local frame, and for half the named planes that frame is not world, so a generator that wants world coordinates goes through here. `snap.py` is the snap-fit vocabulary — bump, notch and the ramps between them, applied to walls a generator already has. `cable_clip.py` is the 9 mm-deep wall-integrated cable-retention profile: its embedment sets its projection, it preserves 3 mm of backing, and its channel ramps to the wall face at both ends.

| clip embedment | minimum host wall | projection from wall |
|---:|---:|---:|
| 0 mm | 3 mm | 9 mm |
| 6 mm | 9 mm | 3 mm |
| 9 mm | 12 mm | 0 mm |

`flute_skin.py` cuts the fluted show surfaces into the mesh a printer reads, and
`flute-evidence/` holds the two full-size photographs its appearance claims are read off.

`plan.py` holds a set of pockets as one figure in the XY plane — union, a closing that fills any gap narrower than a wall, the stock's plan as the edge — and cuts the prism that stands on it, mouths rounded where the figure turns and square where it leaves the stock.

`reeding.py` is the flute vocabulary the texture generators share — fields that read (across, along) in mm ON the surface, so a tile and a standing wall lay down the same texture.
