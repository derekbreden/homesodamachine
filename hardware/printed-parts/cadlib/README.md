# cadlib

CadQuery library code shared across generators in this repo. Reusable helpers that don't belong inside any one generator's directory.

Read `_world_workplane.md` if your generator uses `xz_plane_y_up` (or any other workplane with a registered non-identity frame transform).

`perlin.py` is not CadQuery — it is the noise the texture generators bake into geometry, sampled in world space. `snap.py` and `world_workplane.py` are.
