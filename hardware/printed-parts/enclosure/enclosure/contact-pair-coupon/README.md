# Contact-pair coupon

Two small prints that carry the pump cartridge's
[contact pair](../README.md#cartridge-contacts) seats exactly as the production pieces carry them.
[`contact_pair_coupon.py`](contact_pair_coupon.py) builds `enclosure-front-top` and
`enclosure-pump-cap` from the declared enclosure box and keeps one box round each seat;
[`geometry-check.json`](geometry-check.json) records each crop, each coupon's machine-to-bed
transform, the bed position of every seat feature a slice review looks for, and the hashes of the
files it was cut from.

| Coupon | Size | Cut from | Prints | Holds |
|---|---|---|---|---|
| `contact-pair-male-coupon.stl` | [35.7 × 16.3 × 18.6 mm](COUPON_MALE_SIZE) | front-top's bay bulkhead | +Z up on its cut base, as front-top builds | the male seat's mouth and body, both M1.4 insert bores, the teardrop lead bore through to the aft face, the root of the fore valve tray behind it and the root of the ridge wall on the crown |
| `contact-pair-female-coupon.stl` | [35.7 × 12.0 × 12.1 mm](COUPON_FEMALE_SIZE) | the pump clamp | on its crown, as the clamp prints | the female seat's mouth and body, both M1.4 insert bores, the lead slot open through the crown and the start of both crown grooves |

Both STLs stand in their print orientation with the bed at Z = 0, in the production PET-GF
material and profile. The male coupon's base stands [445](COUPON_BED_LAYERS) layers of
[0.24 mm](COUPON_LAYER) above front-top's own bed, so after the 0.20 mm first layer every layer
boundary falls where front-top lays it. The female coupon's bed is the clamp's own crown. Each
seat's roof is a short bridge between the mouth's round ends; a print with no support inside
either seat or lead passage is the case being tested, so record any support the slicer puts there.

## What the prints have to show

1. **Each half seats on its datum.** The connector half enters its seat by hand with no force,
   its ear plate lands on the step inside the mouth, and its mating face finishes flush with the
   coupon face within [±0.1 mm](COUPON_FLUSH_TOL) across a straightedge. That tolerance is the
   installed press's: the [0.246 mm](COUPON_KISS) kiss leaves each pin pressed
   [0.754 mm](COUPON_PRESS) of its [1.1 mm](COUPON_STROKE) travel, both halves off by the full
   tolerance in either direction still press it [0.554–0.954 mm](COUPON_PRESS_RANGE), and the two
   faces keep at least [0.046 mm](COUPON_KISS_MIN) between them.
2. **The roof did not sag onto the body.** The seat stands [4.55 mm](COUPON_SEAT_HEIGHT) tall
   as drawn, and its roof bridges [23.7 mm](COUPON_ROOF_SPAN) along X between the mouth's round
   ends; the seat's depth is the bridge's width, not its span. At mid-span the seat must still
   measure at least [4.08 mm](COUPON_BODY_MAX), the largest body the drawing's tolerance allows, so
   the roof may sag at most [0.47 mm](COUPON_SAG_LIMIT). The connector slides out again freely,
   with no witness marks on its top or bottom face.
3. **The insert bores take the inserts.** Each M1.4 × 4 × Ø2.3 heat-set presses flush with the
   step, square to the face, and an M1.4 × 5 socket-head screw draws the ear down without lifting
   the connector's face or spinning the insert.
4. **The leads pass.** With 22 AWG leads soldered to each half's four tails, the male half seats
   with its leads drawn back through the teardrop bore, and the female half seats with its leads
   lying in the slot and grooves below the crown face.
5. **The pair attracts one way and makes all four contacts.** Brought face to face by hand, the
   halves attract in one orientation only, and each of the four contacts shows continuity across
   the pair and none to a neighbour. Faces held together press the pins their full
   [1 mm](COUPON_FULL_PRESS) working height, not the installed press of check 1, so this check
   proves polarity and continuity and nothing about the installed compression.

Checks 1, 2, 4 and 5 need only the connector pair. Check 3 needs the M1.4 inserts and screws in
[`bom.md`](/hardware/ledger/bom.md) §13.

## Print record

The H2C trial's slice preparation, support audit, verification and launch record are in
[`h2c-print/`](h2c-print/README.md).

## Open questions the prints answer

- The ear plate's overall length is read off the listing drawing's scale, not dimensioned on it;
  check 1 settles whether the mouth clears the delivered ears.
- The Ø2.0 bore for the M1.4 insert is a starting size; the listing gives no hole diameter.
  Check 3 settles it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/contact_pair_coupon.py`
