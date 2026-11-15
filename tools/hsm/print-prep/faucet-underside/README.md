# Faucet base foundation

The faucet plate gives the slicer each style's base with the space under its mounting face filled
to the bed, then lays that space and the base's foot itself ahead of the slicer's layers. The
editable project and the print-only archive carry the actual parts.

- [`filled_base.rs`](../src/filled_base.rs) gives the slicer a temporary solid beneath the seat so it
  lays ordinary courses above it. The fill's rim is the base's own mounting face.
- [`base_foundation.rs`](../src/base_foundation.rs) lays the scaffold, the roof and the foot's courses,
  cut from the base's own sections with a plug in each insert socket and a deck in the bore, keeps the
  base's courses above them, and lifts travels over the scaffold.
  [`sloped_courses.rs`](../src/sloped_courses.rs) cuts the courses' paths with Clipper2.
  `faucet-plate` runs it for each style; `sculpted-trial foundation` runs it alone.
- `left-active-height.npz` gives the travel stage the underside of the
  [left-active H2C head reference](../../../../hardware/reference/h2c-toolhead/README.md).
  Its model is a reconstruction from photos. The map's source mesh, settings and generator
  are recorded in [the map's source record](left-active-height.json).
- `left-active-full-height.npz` gives the head replay the whole left-active head: the map above
  with the rest of the head model's bodies folded in by `sculpted-trial head-map`. Its sources are
  in [its record](left-active-full-height.json).
