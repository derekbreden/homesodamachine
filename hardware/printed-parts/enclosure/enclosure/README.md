# Enclosure

A PETG box, 3 mm walls, sized live to the bounding box of the contents placed
by [`../enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py),
**split into four printable pieces** — front/back × bottom/top, every piece
inside the H2C bed — that telescope and screw together. The Y seam sits as
close to the box's midpoint as the cold core allows, and each column takes its
bottom↔top seam at its own height (the seams stagger like a brick bond): the
back-bottom piece houses the cold core, the back-top carries the Zone-B trays
and every rear- and side-panel port; the front column splits at its waist over
the condenser — refrigeration below, pumps + electronics stack + funnel +
display above.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`) plus
`enclosure.step` — the four as separate solids in assembled position, seams
intact (mirrors `faucet/touch-flo-shell`). It also exports two test-print
coupons over the shared Y-seam mating geometry: `enclosure-front-coupon.step`,
a reduced-size front (~156 × 101 × 116 mm) carrying every feature at full size
(the display housing, the telescoping lip, the corner bosses, the ribs), and
`enclosure-back-coupon.step`, the matching back (~156 × 40 × 116 mm) — its
mouth, plugs, and screw bores aligned to the front coupon's lip and sockets.

## Seams + bosses

Three seams, one joint idiom. Front↔back: the front pieces' full-wall rear lip
telescopes into the back pieces; one cross-pin per side wall per level — the
lower pair tucked just under the front Z seam (so it pins the two bottom
pieces), the upper pair under the ceiling — fastens the columns with M3 screws
driven from the ±X exterior. Bottom↔top, per column: the same joint rotated
90°, at `z_joint_front` (the front stack's waist, above the condenser) and
`z_joint_back` (the one back-wall band left open between the cold core's
foam-cap top and the rear bulkhead field) — the bottom pieces carry a 3-sided
lip + socket pods, the top pieces carry the D-pins and the braces that back
them, four more X-axis screws crossing each seam. The front pair joins, the
back pair joins, then the front assembly telescopes into the back as one.
Each cross-pin mates the walls of its overlap (the
pin's mouth-side face on the receiving mouth, the socket pod's rim-side face
on the lip rim) and the two are coaxial by construction, so the **overlap
depth is derived from those matings**, not chosen — it works out to
(plug + bore)/2 + one wall.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then the pin body (the screw spans
the head seat to the heat-set, so the body is screw length − heat-set long), then
the heat-set, then a one-wall cap.

- **Receiving piece = D-pin** (the back pieces on the Y seam, the top pieces on
  the Z seam): a Ø9.9 mm cylinder (the shank + one wall each side, *not* the
  head — the head sits in the wall counterbore) from the exterior to the
  heat-set, registering in the socket bore, fused to a flat tab that runs to
  the lip rim where a brace backs it.
- **Lip piece = socket** (the front pieces / the bottom pieces): a pod bored
  Ø10.3 mm to take the round pin as a slide fit, with the ruthex M3 heat-set
  (Ø4.0 × 5.25) capped at its deep inboard end and a channel the pin's tab
  slides through as the lip telescopes home.

The cold core rides in the back-bottom piece, verified clear of every boss at
build time. Each printed piece fits the H2C left-nozzle build envelope
(325 × 320 × 320 mm) even though the whole enclosure does not — that is the
point of the split.

Every piece's vertical (print-axis Y) corners are rounded for print-bed
anti-warp relief, matching the foam shell's 12 mm outer radius — concentric
inner one wall in, so the wall is preserved. The back pieces also carry
braces — ribs from the lip rim toward the rear wall (the lower pair stopping
ahead of the cold core), sized to the pin they back and butting its flat tab
at the rim — anchoring the walls against peeling and supporting the X-axis
pins; the top pieces carry the matching braces above their Z-seam pins.

## Display housing

A flat 45° facet is chamfered into the top-front-left corner for the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/),
facing up-and-forward (−Y front / +Z up) toward the standing user, flush to the
−X (left) edge so the whole top-front-left corner comes off. The facet surface
is sized to the bezel + a 3 mm buffer all around — [119.5 mm](DISPLAY_FACET_X)
(X, lateral) × [83 mm](DISPLAY_FACET_SLOPE) (along the 45° slope).

The facet is thickened into an 18 mm housing (the display's overall depth) with
the display let in. The glass is the datum: a shallow 1 mm bezel counterbore,
centered on the facet (corners rounded 2.5 mm to match the glass), recesses the
glass with the 3 mm buffer uniform all around. The glass overhangs the body
unevenly (further up-and-left), so the 106 × 69 mm PCB through-hole sits offset
the opposite way; where the corner pod sits behind the facet, the hole takes it
clean through.
The recessed panel is sealed from the cavity at both lateral edges: the −X edge
by the left exterior wall, the +X edge by a one-wall gusset spanning the full
housing depth (inner front wall, inner top wall, housing back plane), continuous
with the slab. The display reference is seated in the housing in
`../enclosure-assembly/`.

## Hopper opening

A rectangular opening is punched through the top wall to the right of the display
housing and flush to the front, where the removable silicone hopper funnel
([`../../zone-c/hopper-funnel/`](/hardware/printed-parts/zone-c/hopper-funnel/))
drops in — its brim resting on the top, its collar press-fitting the opening. The
opening is sized to the room right of the display; its +X edge is clamped clear of
the top-right corner pod. The funnel derives its collar from the same rectangle
(`_hopper_hole`), so the two always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, each
piece's envelope vs. the H2C bed, every piece-pair's slip fit, and the
cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
