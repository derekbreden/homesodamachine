# Display cover plate

The printed border that fills the display inset in the enclosure's 45° facet, laps
the Waveshare 4.3B's cover glass on all four sides, and closes that face flat. What a
hand meets on the top-front arris is one unbroken 45° plane with a border let into
it: the plate's top face lies in the plane, and both screws are countersunk into
their own lands, so nothing stands proud of the face anywhere.

The plate is also what fastens the display. The glass sits in the bezel counterbore
of `enclosure-front-top`; this border stands over it and is drawn down into that same
piece by two screws, so the display is captured between the two printed parts.

## Frame

`enclosure.display_plane`'s own — +X the box's lateral axis, +Y up the 45° slope, +Z
out of the face at the user, origin on the glass's centre in the 45° plane. The
plate's top face lies on Z = 0 and the whole body hangs below it, so every figure
here is a depth below the face and reads directly against the depths
`enclosure._display_cuts` cuts the facet to.

## Outline

- Outer [152.9 mm](COVER_X) lateral × [82.4 mm](COVER_SLOPE) up the slope,
  corners r[2.2 mm](COVER_CORNER_R). That is the inset less
  [0.3 mm](COVER_SLIP) per side, corner radius included, so the plate's round and
  the inset's stay concentric and the fit is one figure the whole way round.
- [2 mm](COVER_T) thick — the inset's own depth, which is what puts the top face in
  the 45° plane.
- Window [107.5 mm](WINDOW_X) × [71 mm](WINDOW_SLOPE), corners
  r[2.5 mm](WINDOW_CORNER_R) — the glass less [3 mm](INSET_LAP) of lap per side.
  The corners carry the glass's own radius, since a constant lap round a corner
  needs both outlines to share it.
- Border [22.7 mm](BORDER_X) either side laterally, [5.7 mm](BORDER_SLOPE) top and
  bottom. The lateral land is wide because the inset reaches past the glass for the
  two screws to stand in; up the slope the border is the lap twice over.

## Screws

One at each of x = ±[66.75 mm](PAD_X), y = 0 — the middle of the lateral land, the
widest material the plate has.

- **Pad** — ⌀[12 mm](COVER_PAD_D) standing [3.2 mm](COVER_PAD_DEPTH) below the plate's underside,
  into the pocket `enclosure._display_cuts` sinks in the inset floor for it. The
  plate is [5.2 mm](PAD_SEAT) thick under each screw where the bare border is
  [2 mm](COVER_T).
- **Head seat** — a flat-bottomed ⌀[6.15 mm](CBORE_D) counterbore struck
  [3.2 mm](COVER_CBORE_DEPTH) down from the top face over a ⌀[3.9 mm](SHANK_D) shank
  clearance, the same seat the foam cap's lids take. The head lands
  [0.2 mm](SEAT_RECESS) under the 45° face and the plane closes over it. Under the
  head is [2 mm](COVER_LAND) of land — the bare border's own section, which is what the pad
  exists to leave there.
- **Fastener** — M3 × [8 mm](COVER_SCREW_LEN) DIN 912 socket head cap, into a ruthex M3
  short in the [5.25 mm](HEATSET_DEPTH) bore under each pocket, [5.25 mm](THREAD_ENGAGED)
  of it in thread. DIN 912 states a length under the head, and what it has to stand in
  is [8.25 mm](COVER_SCREW_REACH): the land, the insert, and the relief the box bores under
  the insert so a tip that runs past it finds air rather than a floor.

## The lap

The plate's underside sits [2 mm](COVER_T) below the 45° face and the glass's front
face [3 mm](GLASS_FACE_DEPTH) below it, so [1 mm](GLASS_LAP_AIR) of air runs under
the border all the way round. The border stands over the glass; it does not bear on
it.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-cover/display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/display_cover.py`
