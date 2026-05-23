# cadlib

CadQuery library code shared across generators in this repo. Reusable helpers that don't belong inside any one generator's directory.

Read `_world_workplane.md` first if your generator uses `xz_plane_y_up` (or any other workplane with a registered non-identity frame transform). On `xy_plane_z_up` you don't need it — cadquery's bare `Workplane` works fine there, since world and local 2D coordinates are the same thing.
