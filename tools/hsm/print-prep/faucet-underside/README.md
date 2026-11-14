# Faucet base underside

`faucet_underside.rs` prepares the complete faucet's removable scaffold, sloped roof and sloped skin
as part of the Sculpted and Industrial offline slice. Each style's outline and insert
recesses come from its own mounting face. The editable project and executable archive carry
the actual parts.

- [fill.py](fill.py) gives the slicer a temporary solid beneath the seat so it can lay ordinary courses above it.
- [courses.py](courses.py) lays scaffold, roof and skin, keeps the base's courses above the skin, and lifts travels over the scaffold.
- `left-active-height.npz` gives the travel stage the underside of the
  [left-active H2C head reference](../../../../hardware/reference/h2c-toolhead/README.md).
  Its model is a reconstruction from photos. The map's source mesh, settings and generator
  are recorded in [the map's source record](left-active-height.json).

The offline slice uses NumPy, Shapely, trimesh and manifold3d in `tools/cad-venv`.
The paths follow the [accepted Sculpted print](https://github.com/derekbreden/homesodamachine/tree/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2).
Its in-hand result covers the Sculpted base. The Industrial preparation uses the same
process on its circular foot.
