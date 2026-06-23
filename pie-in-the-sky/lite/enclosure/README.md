# Lite enclosure shell

A transparent PETG box, 3 mm walls, sized live to the bounding box of the
contents placed by
[`../enclosure-assembly/_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py),
**split into two printable halves** — `enclosure-front` and `enclosure-back` —
that telescope and screw together. The back half houses the reservoir-pockets
box; the front half's rear wall inserts into it.

The same architecture as the [Kitchen edition enclosure](/hardware/printed-parts/enclosure/enclosure/),
adapted to the Lite contents — no cold core, compressor, or condenser, so the
reservoir-pockets box is the heavy back-bottom anchor the box is sized around.

`enclosure.py` exports the two printable halves (`enclosure-front.step`,
`enclosure-back.step`) plus `enclosure.step` — the two halves as separate solids
in assembled position, seams intact (mirrors `faucet/touch-flo-shell`). (The Lite
carries no test-print coupons; the [Kitchen edition coupons](/hardware/printed-parts/enclosure/enclosure/)
cover the shared split/boss mating geometry.)

## Frame

The contents' frame carries through: +X right, +Y back (depth), +Z up, floor on
z=0. The −Y wall is the enclosure front (carrying the display facet and, below
it, the front tray stack and pumps); +Y is the cabinet back (where the
reservoir's bag-load doorway faces); the lid plane is the box top.

## Split + bosses

The front half's full-wall rear lip telescopes into the back half; four corner
cross-pins — one at each top/bottom corner of the ±X side walls — fasten the
halves with M3 screws driven from the ±X exterior. Each cross-pin mates the
walls of the overlap (the back plug's −Y face on the back mouth, the front
socket pod's +Y face on the lip rim) and the two are coaxial by construction, so
the **overlap depth is derived from those matings**, not chosen — it works out
to (plug + bore)/2 + one wall.

Reading an M3×10 screw outboard→inboard from the ±X exterior: a Ø6.15 mm head
counterbore, then the pin body, then the heat-set, then a one-wall cap.

- **Back half = D-pin**: a Ø9.9 mm cylinder (the shank + one wall each side) from
  the exterior to the heat-set, registering in the socket bore, fused to a flat
  tab that runs to the lip rim where the corner brace backs it.
- **Front lip = socket**: a corner pod, integral with the top/bottom wall, bored
  Ø10.3 mm to take the round pin as a slide fit, with the ruthex M3 heat-set
  capped at its deep inboard end and a +Y channel the pin's tab slides through as
  the lip telescopes home.

The back half is sized so the reservoir seats behind the bosses (verified clear
at build time). Each printed half fits the H2C left-nozzle build envelope
(325 × 320 × 320 mm) even though the whole enclosure does not — that is the
point of the split.

Both halves' vertical (print-axis Y) corners are rounded 12 mm for print-bed
anti-warp relief, concentric inner one wall in so the wall is preserved. The
back half also carries four corner braces — ribs from the lip rim to the rear
wall — anchoring the corners against peeling and supporting the X-axis pin in Y.

## Display housing

A flat 45° facet is chamfered into the top-front-left corner for the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/),
facing up-and-forward (−Y front / +Z up) toward the standing user, flush to the
−X (left) edge so the whole top-front-left corner comes off. The facet surface
is sized to the bezel + a 3 mm buffer all around — [119.5 mm](DISPLAY_FACET_X)
(X, lateral) × [83 mm](DISPLAY_FACET_SLOPE) (along the 45° slope).

The facet is thickened into a 19 mm housing (the display's overall depth) with
the display let in: a shallow 1 mm bezel counterbore, centered on the facet
(corners rounded 2.5 mm), recessing the glass, and a 106 × 69 mm PCB
through-hole offset behind it. The recessed panel is sealed from the cavity at
both lateral edges: the −X edge by the left exterior wall, the +X edge by a
one-wall gusset. The display reference is seated in the housing in
`../enclosure-assembly/`.

This is the same front display as the Kitchen edition, top-left of the front
face, angled up to the user — replacing the round RP2040 display the Lite
originally sketched.

## Hopper opening

A **narrow-X, deep-Y slot** is punched through the top wall to the right of the
display housing, where the removable hopper
[funnel](/pie-in-the-sky/lite/printed-parts/funnel/) drops in — its brim resting
on the top, its collar press-fitting the opening. Both side edges run flush to
their neighbours with no dead strip of wall: the −X edge against the display
gusset, the +X edge against the top-right corner pod; the slot reaches the full
front-half depth back to the seam lip. Only the short bib/nozzle stack sits
beneath the slot — the tall back trays end short of its −X edge — so the deep
slot has a tall clear chute for a big pour buffer (verified in `funnel.py` against
the real solids). The funnel derives its collar from the same rectangle
(`_hopper_hole`), so the two always match.

## Dimensions

Outer envelope [211.5 mm](LITE_OUTER_X) × [301.5 mm](LITE_OUTER_Y) × [301 mm](LITE_OUTER_Z)
(X × Y × Z) — smaller than the Kitchen edition (289 × 342 × 310) in all three
axes: with no cold core, compressor, or condenser, the trays and pumps pack into a
tight front zone ahead of the reservoir, and the contents sit flush against the
flat front/back walls (only the ±X/±Z walls keep a thin margin off the rounded
print-corners). Read live from the contents placed by
`../enclosure-assembly/_contents.py`, so any move in the contents propagates.

## Regenerate

The enclosure sizes itself from the contents bbox:

`tools/cad-venv/bin/python pie-in-the-sky/lite/enclosure/enclosure.py`
→ `enclosure-front.step`, `enclosure-back.step`, `enclosure.step`. Wall, split,
boss, and facet constants are at the top of `enclosure.py`. Prints the facet size,
each half's envelope vs. the H2C bed, and the reservoir/boss clearance.

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/enclosure/enclosure.py`
