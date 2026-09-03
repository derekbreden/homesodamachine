# Display cover plate

The printed border that fills the display inset in the enclosure's 45° facet, laps
the Waveshare 4.3B's cover glass on all four sides, and closes that face flat. What a
hand meets on the top-front arris is one unbroken 45° plane with a border let into
it: the plate's top face lies in the plane, and both screws are counterbored into
their own lands, so nothing stands proud of the face anywhere.

The plate is also what fastens the display. The glass sits in the bezel counterbore
of `enclosure-front-top`; this border laps it all round and two screws draw the plate
down into that same piece, closing on the glass through the TPU ring between them, so
the display is captured between the two printed parts.

## Frame

`enclosure.display_plane`'s own — +X the box's lateral axis, +Y up the 45° slope, +Z
out of the face at the user, origin on the glass's centre in the 45° plane. The
plate's top face lies on Z = 0 and the whole body hangs below it, so every figure
here is a depth below the face and reads directly against the depths
`enclosure._display_cuts` cuts the facet to.

## Outline

- Outer [153.2 mm](COVER_X) lateral × [82.7 mm](COVER_SLOPE) up the slope,
  corners r[2.35 mm](COVER_CORNER_R). That is the inset less
  [0.15 mm](COVER_SLIP) per side, corner radius included, so the plate's round and
  the inset's stay concentric and the fit is one figure the whole way round.
- [2 mm](COVER_T) thick **where it laps the glass** — the inset's own depth, which is
  what puts the top face in the 45° plane. Everywhere else it is [5.2 mm](COVER_SEAT);
  see *Two sections* below.
- Window [107.5 mm](WINDOW_X) × [71 mm](WINDOW_SLOPE), corners
  r[2.5 mm](WINDOW_CORNER_R) — the glass less [3 mm](INSET_LAP) of lap per side.
  The corners carry the glass's own radius, since a constant lap round a corner
  needs both outlines to share it.
- Border [22.85 mm](BORDER_X) either side laterally, [5.85 mm](BORDER_SLOPE) top and
  bottom. The lateral land is wide because the inset reaches past the glass for the
  two screws to stand in; up the slope the border is the lap twice over.

## Screws

One at each of x = ±[66.75 mm](PAD_X), y = 0 — the middle of the lateral land, the
widest material the plate has.

- **Seat** — no pad. The plate is already [5.2 mm](COVER_SEAT) thick everywhere the
  glass is not under it, so a head's counterbore is sunk into the plate's own
  section and nothing stands off its back.
- **Head seat** — a flat-bottomed ⌀[6.15 mm](CBORE_D) counterbore struck
  [3.2 mm](COVER_CBORE_DEPTH) down from the top face over a ⌀[3.9 mm](SHANK_D) shank
  clearance, the same seat the foam cap's lids take. The head lands
  [0.2 mm](SEAT_RECESS) under the 45° face and the plane closes over it. Under the
  head is [2 mm](COVER_LAND) of land — the lap's own section. Counterbore plus land is
  what *sets* the [5.2 mm](COVER_SEAT) seat; the plate is not thickened to some figure
  and then bored, it is exactly as thick as a buried M3 needs.
- **Fastener** — M3 × [8 mm](COVER_SCREW_LEN) DIN 912 socket head cap, into a ruthex M3
  short in the [5.25 mm](HEATSET_DEPTH) bore under each seat, [5.25 mm](THREAD_ENGAGED)
  of it in thread. DIN 912 states a length under the head, and what it has to stand in
  is [8.25 mm](COVER_SCREW_REACH): the land, the insert, and the relief the box bores under
  the insert so a tip that runs past it finds air rather than a floor.

## Two sections

Over the glass the plate is [2 mm](COVER_T) and can be nothing else — what stands in
that step is the gasket, and under it the cover glass. Everywhere else it is
[5.2 mm](COVER_SEAT), and `enclosure._display_cuts` sinks the inset's land to meet it.
The two meet on the **bezel's own outline one slip out**,
[113.8 mm](SEAT_INNER_X) × [77.3 mm](SEAT_INNER_SLOPE) with corners
r[2.65 mm](SEAT_INNER_R), so the deeper section drops past the bezel counterbore's wall
on the same figure the plate's edge takes at the outline.

| | |
|---|---|
| Seat band, laterally | [19.7 mm](SEAT_BAND_X) each side — the whole land the inset reaches out for the screws |
| Seat band, up the slope | [2.7 mm](SEAT_BAND_SLOPE) each side — there the border is nearly all lap |
| Lap that stays thin | [3.15 mm](LAP_BAND) from the window out: the gasket's own footprint and one slip more |

**What it buys.** The plate used to stand two ⌀12 circles off an otherwise flat back
and rest on them, with the whole of its area [3.2 mm](COVER_CBORE_DEPTH) in the air.
Now the back is one plane either side of a single step. Across the lateral land — the
span the two screws bridge, and the only place this plate is asked to be stiff — the
section goes 2 mm → 5.2 mm, which is [17.6×](SEAT_STIFFNESS) the bending stiffness,
since that goes as the cube of the section.

**It prints face down.** The top face has to come out flat and lie in the 45° plane,
and a face printed against the bed is flat because the bed is. It is also what makes
the step free: build upward from that face and every step in the back faces *up* — the
lap stops at its own depth, the seat carries on, and nothing hangs. The bed takes
[4978 mm²](BED_AREA) of top face in one plane. The only feature on the whole plate that
hangs is the annular ledge at each counterbore, [1.125 mm](CBORE_LEDGE) wide.

## The lap

The plate's underside sits [2 mm](COVER_T) below the 45° face and the glass's front
face [3 mm](GLASS_FACE_DEPTH) below it. What stands in that step all the way round is
the display gasket
([`display-gasket/`](/hardware/printed-parts/enclosure/display-gasket/README.md)) — a
TPU 90A ring cut to the glass's own outline outside and to this plate's window inside,
so it lands under the border and nowhere else, and its thickness is the step itself.
The border bears on the glass through that ring, which is what makes the two screws
hold the display rather than the plate alone.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-cover/display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/display_cover.py`
