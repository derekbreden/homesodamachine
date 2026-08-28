# Ceiling panel

enclosure-back-top's ceiling, as a part of its own: a [159 mm](PANEL_W) ×
[225 mm](PANEL_D) show skin that grows into an [8 mm](STRUCTURAL_T) structural
field on the interior side. It prints flat on the bed, show face down, and slides
into a dado down each side of the piece. Its top face is the appliance's top
surface; all structural pockets open upward during printing.

The piece it closes prints MOUTH-DOWN on its seam rim with the build axis +Z and
stands [195 mm](PIECE_H) on that rim, so a ceiling printed in back-top is a roof
laid down the whole of that height over the open service bay. front-top's
ceiling is two corbelled side strips with the funnel's throat as the void between
them; back-top has no throat of its own, and this is what fills it.
Box framing: [`../enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md).

## Where it stands

Built in the box's own frame — every plane it stands on is a plane the box
states about itself.

- **Ceiling datum** at z = [352](PANEL_UNDER), with the **show face** one wall
  over it at z = [355](PANEL_SHOW). The [8 mm](STRUCTURAL_T) field descends to
  z = [347](STRUCTURAL_UNDER) wherever a purchased body does not need that
  volume. The rear storey's placements still read from the z =
  [352](PANEL_UNDER) datum: `enclosure_assembly.deck_storey` is this less the
  tap-water chain's crown and tie clearance, and the umbilical ports, CO₂
  neoFit, C14, DIGITEN axis and tube anchors all remain in that one frame.
- **Width** is `funnel.collar_w`, whole — x ±[79.5](PANEL_HALF_W). The
  throat's opening is that wide and the panel's edges are collinear with it, so
  the ceiling reads as one [159 mm](PANEL_W) channel down the machine, funnel in
  the front of it and panel filling the rest.
- **Fore edge** at y = [236](PANEL_FORE), the collar's own aft edge.
- **Aft edge** at y = [461](PANEL_AFT), back-top's own back-wall face, which is
  the panel's stop. Rounded reliefs rise locally over the C14, both upper
  umbilical unions, the CO₂ neoFit and the tap-water chain; the material between
  those pockets remains one broad field to the stop.

## The structural field

The load path is a continuous [8 mm](STRUCTURAL_T) plate, not a thin lid with a
single directional brace. Its envelope absorbs all but 1.25 mm of the two
retention-insert sockets and the upper roots of the flow-meter anchors and tube
anchors. The existing print profile uses four top shells, three bottom shells
and 15% grid infill, so the CAD envelope is not a solid 8 mm billet.

There are [7](RELIEF_N) body pockets. Each starts from the purchased solid's
exact intersection with the unrelieved field and rails, adds 2 mm of plan slip
and 1 mm of vertical clearance, and rounds its plan corners to
[3 mm](RELIEF_R). The pocket floor is therefore not a common guessed depth:
shallow bodies leave a thicker roof and tall bodies keep the original ceiling
section over them. At the C14, that same construction locally opens the lower
face of the +X rail while its captured upper section continues to the back
stop. Every pocket is open on the interior face, which is upward on the printer.

One anchor's zip tie approach enters the new field. Its whole existing footprint
is returned as the single [1](TIE_RELIEF_N) zip tie pocket, so the loop still
descends on both sides of the WR1110 barrel. The other anchor channels and both
meter channels remain open while their solid roots merge into the plate.

The C14 tunnel reaches into the aft end of the field. Its intersecting upper cap
belongs to this panel and travels with it; the rest stays on back-top and gives
up the +X rail's clearance. The two screw piers likewise keep their structural
section below the rail while leaving its dado open above. The union in the
installed machine is the same tunnel, while neither it nor a pier blocks the
panel's slide. `ceiling-panel-slides-in` checks the complete field-and-rail sweep
from the open Y seam to the installed stop rather than checking only the final
pose.

## The rails

What back-top keeps of its ceiling is the two side strips either side of this
panel, [22 mm](RAIL_RUN) wide — the piece's own flank face less the panel's
half-width, and the one figure the whole ceiling is cut to. The dado is cut in
each strip's inboard face and the panel's tongues run in it: a drawer bottom in
a dado.

- **Tongue** [3 mm](TONGUE_T) thick × [3 mm](TONGUE_REACH) reach, a
  [9 mm²](RAIL_AREA) captured rail down each long edge. It is centred on the
  interior ceiling datum, z = [350.5](TONGUE_FLOOR)..[353.5](TONGUE_ROOF), so
  half its root merges into the structural field and half into the show skin.
  The rails take the part's bounding width to [165 mm](PANEL_BBOX_X), while the
  show face stays [159 mm](PANEL_W) and its seam lines stay on the throat's own
  edges.
- **Dado** [3.15 mm](DADO_DEPTH) deep, from z = [350.35](DADO_FLOOR) to
  [353.65](DADO_ROOF) at the blind end. That end carries the
  [0.15 mm](DADO_SLIP) printed-fit clearance on every face and leaves
  [1.5 mm](DADO_LOWER_LIGAMENT) of the fixed corbel below the groove plus a
  [1.35 mm](LIP_T) show-skin lip above it. Those are the two ligaments that
  capture the rail and hold the panel on the ceiling datum.
- **The dado's roof rises to the mouth at [45°](CHAMFER)**, the way every relief
  ceiling on this box does — a roof left flat would hang over the slot in a
  piece that prints mouth-down. The roof climbs one millimetre per millimetre of
  run and clears the show face at the open mouth; the corbel grows downward in
  the other direction, providing the lower capture section at the blind end.

## The brim, and the two screws

The funnel's brim lands ON this panel. The flange overhangs the collar and
covers the first [7 mm](BRIM_SEAT) of show face, inside the
[10 mm](BRIM_MARGIN) of top wall `funnel-brim-margin` asks at that free edge —
which is why the fore edge is load-bearing and why the fore [10 mm](BRIM_MARGIN)
is not a place to put an opening.

Two [M3x10](SCREW_LEN) socket caps pin the fore end against the slide, at x =
±[74.925](SCREW_X), y = [239.5](SCREW_Y). **Each screw is inserted from the Z−
direction and travels +Z.** Its head is in a downward-open counterbore in
back-top's fixed boss; its thread lands in a heat-set inserted upward into this
panel from the same Z− face. Nothing pierces or counterbores the appliance's
show face. Aft of them the tongues hold the panel down and the +Y wall holds
it in; nothing else is fastened.

The fixed boss presents [4 mm](SCREW_LAND) of land from the head's bearing face
at z = [341.75](SCREW_HEAD_SEAT) to the panel socket at z =
[345.75](SCREW_INSERT_OPEN). Its recessed head face is flush at z =
[337.75](SCREW_HEAD_FACE). The panel socket is [9.25 mm](SCREW_SOCKET_T) from
its downward mouth to the show face: a [5.25 mm](HEATSET) ruthex M3 short ends
at z = [351](SCREW_INSERT_END), the bore continues to z =
[352](SCREW_INSERT_BORE_END), and a whole 3 mm wall caps it under the show
surface. Land and insert spend [9.25 mm](SCREW_REACH) of the
[M3x10](SCREW_LEN)'s under-head length, leaving [0.25 mm](SCREW_TIP_AIR) beyond
the tip before the blind end.

Each station stands as far outboard as a full ligament round its counterbore
allows, tangent to the mouth and inside the panel's moving field.

## What hangs off it

The ceiling over this field is this part, so every rib rooted on it is this part's
too — the two anchors the DIGITEN flow meter hangs in, and three anchors bored
for a round body: `carb-1`, `co2-2` and the WR1110 regulator's barrel.
`enclosure.ceiling_stations` is the one call that assigns the ceiling's stations,
so each one is grown by exactly one part.

Each is built by `enclosure`'s own builder (`_flow_meter_anchors`, `_tube_anchors`):
a bore concentric with the body it takes, its arc stopped on that body's own axis
plane, and the zip tie's channel behind it. The stations are struck in the box's
frame, because that is the frame the bodies are in; the z = [352](PANEL_UNDER)
datum remains the plane each rib is constructed toward. The structural field
then merges with the solid portions of those roots while leaving every zip tie
channel open.

The bench sequence follows from it: a seat that hangs off the top wall is an
upward-opening cradle the moment the part is inverted, and this part inverted is a
flat plate.

## Fitting it

1. Set the panel show-face down and install both heat-sets upward from its Z−
   face until each is flush in its downward-open socket.
2. Slide the panel aft through back-top's Y-seam mouth, tongues in the dados,
   until its aft edge lands on the +Y wall.
3. Keep back-top ceiling-down, with its Z− face upward. Insert both screws from
   that face through the fixed bosses and drive them upward into the panel's
   heat-sets.
4. Lay the meter into its two anchors and each run into its rib, and zip tie them.
   Then lower the populated piece onto the machine.
5. Drop the funnel in. Its collar fills the throat immediately ahead of the
   panel; the panel's show face remains uninterrupted behind it.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/ceiling-panel/ceiling_panel.py`
→ `ceiling-panel.step`. Prints flat, show face down, on the H2C's
[325 mm](BED_X) × [320 mm](BED_Y) bed.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/ceiling-panel/ceiling_panel.py`
