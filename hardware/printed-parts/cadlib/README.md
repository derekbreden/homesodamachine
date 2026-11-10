# CAD compatibility helpers

`world_workplane.py` maps world coordinates into the workplanes used by the remaining
CadQuery reference adapters. Read [_world_workplane.md](_world_workplane.md) for its interface.
`_scalar_provider.py` reads native scalar values for those adapters.

The native [fit catalog](/tools/hsm/catalog/src/lib.rs) reads the authored allowances in
[scalars.json](/tools/hsm/shared-data/catalog/scalars.json).
The native enclosure [skin](/hardware/printed-parts/enclosure/enclosure/solid/skin.rs)
defines its show surface. [Flute photographs](flute-evidence/README.md) record the physical appearance.
