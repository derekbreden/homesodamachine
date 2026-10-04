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
| `contact-pair-female-coupon.stl` | [35.7 × 14.5 × 12.1 mm](COUPON_FEMALE_SIZE) | the pump clamp | on its crown, as the clamp prints | the female seat's mouth and body, both M1.4 insert bores, the lead slot open through the crown and the start of both crown grooves |

Both STLs stand in their print orientation with the bed at Z = 0, in the production PET-GF
material and profile. The male coupon's base stands [445](COUPON_BED_LAYERS) layers of
[0.24 mm](COUPON_LAYER) above front-top's own bed, so after the 0.20 mm first layer every layer
boundary falls where front-top lays it. The female coupon's bed is the clamp's own crown. Each
seat's roof is a short bridge between the mouth's round ends; a print with no support inside
either seat or lead passage is the case being tested, so record any support the slicer puts there.

## What the prints have to show

1. **Each half seats on its datum.** The connector half enters its seat by hand with no force,
   its ear plate lands on the step inside the mouth, and its mating face finishes flush with the
   coupon face within [±0.05 mm](COUPON_FLUSH_TOL), measured near both ends. The nominal
   [0.246 mm](COUPON_KISS) frame gap presses a nominal pin
   [0.754 mm](COUPON_PRESS) of its [1.1 mm](COUPON_STROKE) travel. The seller's tip-height and
   body-depth tolerances permit [0.8–1.2 mm](COUPON_PIN_RANGE) protrusion. Including those
   extremes and both face errors gives [0.454–1.054 mm](COUPON_PRESS_RANGE) compression and
   [0.146 mm](COUPON_KISS_MIN) to [0.346 mm](COUPON_KISS_MAX) face gap, at the nominal frame gap.
   Only [0.046 mm](COUPON_STROKE_MARGIN) additional closing error remains before maximum
   stroke. Printed frame position, tilt and lateral alignment require their own installed
   reading; this coupon criterion does not qualify the complete dimensional stack.
2. **The roof did not sag onto the body.** The seat stands [4.55 mm](COUPON_SEAT_HEIGHT) tall
   as drawn, and its roof bridges [23.7 mm](COUPON_ROOF_SPAN) along X between the mouth's round
   ends; the seat's depth is the bridge's width, not its span. At mid-span the seat must still
   measure at least [4.08 mm](COUPON_BODY_MAX), the largest body the drawing's tolerance allows, so
   the roof may sag at most [0.47 mm](COUPON_SAG_LIMIT). The connector slides out again freely,
   with no witness marks on its top or bottom face.
3. **The insert bores take the inserts.** Each M1.4 × 4 × Ø2.3 heat-set passes the Ø2.6 entry
   and seats square with its top 5.00 mm below the mating face, 2.00 mm behind the ear-bearing
   step. The cold depth check and fine-tip procedure are in [enclosure assembly](../../../../assembly/enclosure-mechanical.md). An M1.4 × 8 socket-head screw draws the ear down without lifting
   the connector's face or spinning the insert, with 0.50 mm nominal blind-end clearance.
4. **The leads pass.** With 22 AWG leads soldered to each half's four tails, the male half seats
   with its leads drawn back through the teardrop bore, and the female half seats with its leads
   lying in the slot and grooves below the crown face.
5. **The pair attracts one way and makes all four contacts.** Hold the halves parallel in
   their attracting orientation with two equal, measured nonconductive spacers beside the
   contact row. A 0.25–0.30 mm plastic shim at each end keeps maximum-drawing pins below
   full stroke while all minimum-drawing pins still reach their pads. Keep the pair unpowered.
   Probe the tails: each pin must connect to its corresponding pad and none to a neighbour
   or screw. Mark the attracting ends that will stand at machine −X. Do not let the plastic
   faces snap into zero-gap contact: maximum-drawing protrusion exceeds the stated stroke.
   This local check establishes orientation and continuity, not installed compression,
   holding force or operating contact resistance.

Checks 1, 2, 4 and 5 need only the connector pair. Check 3 needs the M1.4 inserts and screws in
[`bom.md`](/hardware/ledger/bom.md) §13.

## Print record

The H2C trial's slice preparation, support audit, verification and launch record are in
[`h2c-print/`](h2c-print/README.md).

The [mounting audit](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md) states the
current magnet construction, tolerance basis, load path and evidence limits. The
connector magnets are contained in the purchased halves; no magnet goes into a paused
coupon or enclosure print.

## Open questions the prints answer

- The ear plate's overall length is read off the listing drawing's scale, not dimensioned on it;
  check 1 settles whether the mouth clears the delivered ears.
- The Ø2.0 bore for the M1.4 insert is a starting size; the listing gives no hole diameter.
  Check 3 settles it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/contact_pair_coupon.py`
