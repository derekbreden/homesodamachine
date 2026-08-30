# Ceiling panel

enclosure-back-top's ceiling, as a part of its own: a [159 mm](PANEL_W) ×
[225 mm](PANEL_D) show skin that grows into an [11 mm](STRUCTURAL_T) structural
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

- **Pack ceiling lane** at z = [352](PANEL_UNDER), with the **show face** at z =
  [355](PANEL_SHOW). The fixed side strips present their own [6 mm](FIXED_T)
  physical interior face at z = [349](FIXED_UNDER), while the removable panel's
  [11 mm](STRUCTURAL_T) structural envelope descends to z =
  [344](STRUCTURAL_UNDER) wherever a purchased body does not need that volume.
  The rear storey's placements still read from the z = [352](PANEL_UNDER) lane:
  `enclosure_assembly.deck_storey` is this less the tap-water chain's crown and
  tie clearance, and the umbilical ports, CO₂ neoFit, C14, DIGITEN axis and tube
  anchors all remain in that one frame. Nothing about the exterior or pack moved
  to pay for either inward-grown section.
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

The load path is a continuous [11 mm](STRUCTURAL_T) plate, not a thin lid with a
single directional brace. Its envelope absorbs the upper roots of the
flow-meter anchors and tube anchors. The existing print profile uses four top
shells, three bottom shells and 15% grid infill, so the CAD envelope is not a
solid 11 mm billet.

There are [9](RELIEF_N) body pockets. Each starts from the purchased solid's
exact intersection with the unrelieved field and rails, adds 2 mm of plan slip
and 1 mm of vertical clearance, and rounds its plan corners to
[3 mm](RELIEF_R). The pocket floor is therefore not a common guessed depth:
shallow bodies leave a thicker roof and tall bodies keep the original ceiling
section over them. They cover the C14, ASSE, CO₂ and water fittings, DIGITEN,
relay, WR1110 and the near-miss gas check valve; the last is deliberately found
by testing the exact body one clearance millimetre upward, so a 0.04 mm miss
cannot silently become an interference in the deeper panel. At the C14 and
relay, that construction locally opens a rail only where the exact placed body
requires it. Every pocket stops at or below the pack lane, leaving at least one
whole [3 mm](PANEL_T) wall of show skin above it, and opens on the interior face,
which is upward on the printer.

Three anchor zip-tie approaches enter the deeper field: the two DIGITEN bands
and the WR1110 barrel's run. Their existing footprints are returned as
[3](TIE_RELIEF_N) local pockets before the anchor furniture is fused, so every
loop can still descend on both sides of its body. `tie-channels` reads all ten
finished tie paths against all enclosure pieces and requires 0% filled; the
panel-section gate separately requires all three approach pockets to leave real
air in the grown field.

The fixed C14 surround reaches into the aft end of the field. It belongs wholly
to back-top; this panel carries a constant-section running pocket open through
its aft edge, so the fixed crown enters that pocket as the panel reaches home.
The RJ11 receptacle stands lower between SODA and FLAVOR-A and does not reach
this panel. `ceiling-panel-slides-in` checks the complete field-and-rail sweep
from the open Y seam to the installed stop rather than checking only the final
pose.

## The rails

What back-top keeps of its ceiling is the two side strips either side of this
panel, [19 mm](RAIL_RUN) wide — the piece's own flank face less the panel's
half-width, and the one figure the whole ceiling is cut to. The dado is cut in
each strip's inboard face and the panel's tongues run in it: a drawer bottom in
a dado.

- **Tongue** [6 mm](TONGUE_T) thick × [6 mm](TONGUE_REACH) reach, a
  [36 mm²](RAIL_AREA) captured rail down each long edge. It fills the grown
  fixed section from z = [346](TONGUE_FLOOR)..[352](TONGUE_ROOF), wholly rooted
  in the structural field and ending on the unchanged pack lane.
  The rails take the part's bounding width to [171 mm](PANEL_BBOX_X), while the
  show face stays [159 mm](PANEL_W) and its seam lines stay on the throat's own
  edges.
- **Dado** [6.15 mm](DADO_DEPTH) deep, from z = [345.85](DADO_FLOOR) to
  [352.15](DADO_ROOF) at the blind end. That end carries the
  [0.15 mm](DADO_SLIP) printed-fit clearance on every face and leaves
  [3 mm](DADO_LOWER_LIGAMENT) of the fixed corbel below the groove plus a
  [2.85 mm](LIP_T) show-skin lip above it. Those are the two ligaments that
  capture the rail and hold the panel on the ceiling datum.
- **The dado's roof rises to the mouth at [45°](CHAMFER)**, the way every relief
  ceiling on this box does — a roof left flat would hang over the slot in a
  piece that prints mouth-down. The roof climbs one millimetre per millimetre of
  run and clears the show face at the open mouth; the corbel grows downward in
  the other direction, providing the lower capture section at the blind end.

The rail is locally pocketed only where a placed body already occupies its lower
section: the long ASSE crown on −X and the relay on +X. The opposite spans remain
the full 6 × 6 mm section, and each side keeps a complete body-free capture band.
`ceiling-rail-capture` reads those two bands from the finished solids: zero home
clash, fixed contact after one clearance-plus-0.25 mm displacement outboard,
upward or downward, and the complete 3.00/2.85 mm blind-end ligaments. A pocket
therefore cannot turn either whole dado into an uncaptured channel.

## The brim, and the two keepers

The funnel's brim lands ON this panel. The flange overhangs the collar and
covers the first [7 mm](BRIM_SEAT) of show face, inside the
[10 mm](BRIM_MARGIN) of top wall `funnel-brim-margin` asks at that free edge —
which is why the fore edge is load-bearing and why the fore [10 mm](BRIM_MARGIN)
is not a place to put an opening.

The long dados already constrain X and Z, and the +Y wall is the panel's home
stop. The only unrestrained motion is back toward the open Y− mouth. Two
[M3x12](RETAINER_LEN) headless socket set screws block that motion directly:
one crosses each empty dado at y = [234.35](RETAINER_Y), z =
[351.5](RETAINER_Z), immediately ahead of the tongue's fore face.

The panel reaches the rear stop before either keeper exists. Each screw is then
driven outboard from the empty field into a [5.25 mm](HEATSET) ruthex M3 short
buried horizontally in back-top's existing corbel. Its socket end remains in
the rail lane and crosses [5.6 mm](RETAINER_OVERLAP) of the
[6 mm](TONGUE_T) tongue in X and 2 mm of it in Z; its
aft crown leaves the same [0.15 mm](RETAINER_AIR) fore air as the dado's printed
slide fit. The insert runs x = ±[86.65](RETAINER_INSERT_FACE)..±[91.9](RETAINER_INSERT_END),
reached through a [4.3 mm](RETAINER_APPROACH_D) guide beginning at the proven
x = ±[82.65](RETAINER_GUIDE_FACE) face. The deeper dado's blind wall lies farther
outboard; retaining this inboard guide face clears the new roof wedge without
moving the insert, screw end or keeper axis.
The Ø4 bore continues [1 mm](RETAINER_TIP_AIR) past the insert, so the cup point
cannot bottom on PET-GF and jack the pin back into the field. The fixed strip
carries the standard radial ligament around the insert's lower bearing land without
any added boss. The guide and insert socket retain their complete nominal round
passages and open only above them into the enclosure's 36° tangent teardrop roof,
with at least three 0.24 mm production layers of fixed PET-GF required over the apex.

The panel carries no insert, socket, counterbore or local pad. When it tries to
move fore, each tongue bears on a steel cross-pin and each pin bears directly in
the fixed strip. `ceiling-dado-mouth-keepers` checks both sides independently:
clear at home, caught after the stated fore air, empty socket, complete insert
lower land, printable roof and the exact established world coordinates.

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

1. Feed a ruthex M3 short through each dado-mouth guide and heat-set it outboard
   into the horizontal socket in back-top's fixed corbel.
2. Slide the panel aft through back-top's Y-seam mouth, tongues in the dados,
   until its aft edge lands on the +Y wall.
3. From the still-empty field, drive one [M3x12](RETAINER_LEN) headless keeper
   outboard into each insert until its socket end reaches the stated rail-lane
   depth. The screw crosses the dado ahead of the tongue; it does not enter the
   panel.
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
