# Faucet base underside

`faucet_underside.rs` prepares the complete faucet's removable scaffold, sloped roof and sloped skin
as part of the Sculpted and Industrial offline slice. Each style's outline and insert
recesses come from its own mounting face. The editable project and executable archive carry
the actual parts.

- [`filled_base.rs`](../src/filled_base.rs) gives the slicer a temporary solid beneath the seat so it can lay ordinary courses above it.
- [`base_foundation.rs`](../src/base_foundation.rs) lays scaffold, roof and skin, keeps the base's courses above the skin, and lifts travels over the scaffold.
  [`sloped_courses.rs`](../src/sloped_courses.rs) cuts the courses' paths from the mounting face with Clipper2.
  The same stage lays the Sculpted trial's foot for `sculpted-trial foundation`.
- `left-active-height.npz` gives the travel stage the underside of the
  [left-active H2C head reference](../../../../hardware/reference/h2c-toolhead/README.md).
  Its model is a reconstruction from photos. The map's source mesh, settings and generator
  are recorded in [the map's source record](left-active-height.json).
- `left-active-full-height.npz` gives the head replay the whole left-active head: the map above
  with the rest of the head model's bodies folded in by `sculpted-trial head-map`. Its sources are
  in [its record](left-active-full-height.json).

The paths follow the [accepted Sculpted print](https://github.com/derekbreden/homesodamachine/tree/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2).
Its in-hand result covers the Sculpted base. The Industrial preparation uses the same
process on its circular foot.
