# Ceiling panel

enclosure-back-top's ceiling, as a part of its own: a [159 mm](PANEL_W) ×
[225 mm](PANEL_D) × [3 mm](PANEL_T) slab that prints flat on the bed, show face
down, and slides into a dado down each side of the piece. Its top face is the
appliance's top surface.

The piece it closes prints MOUTH-DOWN on its seam rim with the build axis +Z and
stands [195 mm](PIECE_H) on that rim, so a ceiling printed in back-top is a roof
laid down the whole of that height over the open service bay. front-top's
ceiling is two corbelled side strips with the hopper throat as the void between
them; back-top has no throat of its own, and this is what fills it.
Box framing: [`../enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md).

## Where it stands

Built in the box's own frame — every plane it stands on is a plane the box
states about itself.

- **Underside** on the interior ceiling, z = [352](PANEL_UNDER), and **show
  face** one wall over it at z = [355](PANEL_SHOW). The panel carries the top
  wall's own section, so the ceiling plane and the exterior top face are both
  continuous across it. That underside is the plane the WHOLE rear storey hangs
  from: `enclosure_assembly.deck_storey` is this less the tap-water chain's
  crown and its tie clearance, and the four umbilical ports, the CO₂ neoFit,
  both C14s, the DIGITEN axis and the three tube anchors are all placed off it.
- **Width** is `hopper_funnel.collar_w`, whole — x ±[79.5](PANEL_HALF_W). The
  throat's opening is that wide and the panel's edges are collinear with it, so
  the ceiling reads as one [159 mm](PANEL_W) channel down the machine, funnel in
  the front of it and panel filling the rest.
- **Fore edge** at y = [236](PANEL_FORE), the collar's own aft edge.
- **Aft edge** at y = [461](PANEL_AFT), back-top's own back-wall face, which is
  the panel's stop. The pack stands hard against the ceiling under that wall —
  the C14's flange, both umbilical unions, the CO₂ neoFit and the tap-water
  chain's crown, all within a millimetre and change of it — so the storey there
  holds nothing a corbelled closure off the wall could descend into, and the
  panel takes the span whole.

## The rails

What back-top keeps of its ceiling is the two side strips either side of this
panel, [22 mm](RAIL_RUN) wide — the piece's own flank face less the panel's
half-width, and the one figure the whole ceiling is cut to. The dado is cut in
each strip's inboard face and the panel's tongues run in it: a drawer bottom in
a dado.

- **Tongue** [1.2 mm](TONGUE_T) thick × [1.2 mm](TONGUE_REACH) reach, one down
  each long edge at the panel's underside, taking the part's bounding width to
  [161.4 mm](PANEL_BBOX_X). The show face stays [159 mm](PANEL_W), so the seam
  line on the appliance's top surface runs on the throat's own edges.
- **Dado** [1.5 mm](DADO_DEPTH) deep with its floor on the ceiling plane and its
  roof struck at z = [353.5](DADO_ROOF) at the blind end — which is where the
  roof is lowest, so that is where the [0.3 mm](DADO_SLIP) of printed-fit
  clearance on each face of the tongue is struck. The panel rests on the dado's
  floor, which is what puts its show face flush.
- **The dado's roof rises to the mouth at [45°](CHAMFER)**, the way every relief
  ceiling on this box does — a roof left flat would hang over the slot in a
  piece that prints mouth-down. At that angle the roof climbs one millimetre of
  section per millimetre of reach, which is what makes the dado exactly as deep
  as the lip over it is thick ([1.5 mm](LIP_T)) and leaves the tongue square: as
  thick as it reaches. The whole joint lives in one wall, because one wall is
  all the rail has at the mouth — the strip's corbel grows below the ceiling
  going outboard and reaches nothing at the panel's edge.

## The brim, and the two screws

The funnel's brim lands ON this panel. The flange overhangs the collar and
covers the first [7 mm](BRIM_SEAT) of show face, inside the
[10 mm](BRIM_MARGIN) of top wall `funnel-brim-margin` asks at that free edge —
which is why the fore edge is load-bearing and why the fore [10 mm](BRIM_MARGIN)
is not a place to put an opening.

Two [M3x10](SCREW_LEN) socket caps pin the fore end against the slide, at x =
±[74.925](SCREW_X), y = [239.5](SCREW_Y) — centred in the brim's landing, so
each head is reached straight down through the throat with the funnel out and
covered by the flange with it in. Aft of them the tongues hold the panel down
and the back wall holds it in; nothing else is fastened.

A 3 mm lid cannot bury a socket cap, so the panel takes the box's own web at
each station: [8 mm](SCREW_PAD_T) of section, the head down in the standard
counterbore with [4 mm](SCREW_LAND) of land under it, and the pad hanging into
the bay for the difference — crown at z = [347](SCREW_SEAT). The screw then
lands exactly: that land and a [5.25 mm](HEATSET) ruthex M3 short together spend
[9.25 mm](SCREW_REACH) of the [M3x10](SCREW_LEN)'s under-head length and the
bore relief takes the rest, so the rail's boss under each station reaches z =
[340.75](SCREW_BORE).

The pad hangs below the ceiling and only the panel's own field has room for it —
outboard of the mouth the rail's corbel is standing in that storey, and a pad
reaching into it could not travel the dado. So each station stands as far
outboard as a full ligament round its counterbore allows, which lands the pad
tangent to the mouth.

## What hangs off it

The ceiling over this field is this part, so every rib rooted on it is this part's
too — the two saddles the DIGITEN flow meter hangs in, and three of the anchors
bored for a round body: `carb-1`, `co2-2` and the WR1110 regulator's barrel. They
were `enclosure-back-top`'s while that piece still printed a ceiling here.
`enclosure.ceiling_stations` is the one call that splits the ceiling's stations
between the two parts, and both read it, so neither can grow a rib the other grew.

Each is built by `enclosure`'s own builder on the box's own frame
(`_digiten_saddles`, `_tube_anchors`), so a saddle here is the same saddle it was
on the piece: a bore concentric with the body it takes, its arc stopped on that
body's own axis plane, and the strap's channel behind it with this panel's
underside as its roof.

The bench sequence follows from it: a seat that hangs off the top wall is an
upward-opening cradle the moment the part is inverted, and this part inverted is a
flat plate.

## Fitting it

1. Slide the panel aft through back-top's Y-seam mouth, tongues in the dados,
   until its aft edge lands on the back wall.
2. Drive the two screws down through the pads into the rails' bosses, reaching
   through the open throat.
3. Turn back-top ceiling-down, lay the meter into its two saddles and each run
   into its rib, and strap them. Then lower the piece onto the machine.
4. Drop the funnel in. Its collar fills the throat immediately ahead of the
   panel and its brim covers the screw heads.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/ceiling-panel/ceiling_panel.py`
→ `ceiling-panel.step`. Prints flat, show face down, on the H2C's
[325 mm](BED_X) × [320 mm](BED_Y) bed.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/ceiling-panel/ceiling_panel.py`
