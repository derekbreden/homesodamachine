# cadlib

CadQuery library code shared across generators in this repo. Reusable helpers that don't belong inside any one generator's directory.

Read `_world_workplane.md` if your generator uses `xz_plane_y_up` (or any other workplane with a registered non-identity frame transform).

`world_workplane.py` is the world-coordinate interface: CadQuery reads coordinates in a workplane's own local frame, and for half the named planes that frame is not world, so a generator that wants world coordinates goes through here. `snap.py` is the snap-fit vocabulary — bump, notch and the ramps between them, applied to walls a generator already has.

`reeding.py` is the flute vocabulary the texture generators share — fields that read (across, along) in mm ON the surface, so a tile and a standing wall lay down the same texture.
