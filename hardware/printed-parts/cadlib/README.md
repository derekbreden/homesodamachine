# cadlib

CadQuery library code shared across generators in this repo. Reusable helpers that don't belong inside any one generator's directory.

If your code crosses workplanes — anywhere geometry sits on `xz_plane_y_up` or any other non-identity frame — read `_world_workplane.md` first. Generators that stay on `xy_plane_z_up` and only need bare cadquery don't need this directory.
