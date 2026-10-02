# Contact-pair coupon

Two small prints that carry the pump cartridge's
[contact pair](../README.md#cartridge-contacts) seats exactly as the production pieces carry them.
[`contact_pair_coupon.py`](contact_pair_coupon.py) builds `enclosure-front-top` and
`enclosure-pump-cap` from the declared enclosure box and keeps one box round each seat;
[`geometry-check.json`](geometry-check.json) records each crop, its print size and the hashes of
the files it was cut from.

| Coupon | Cut from | Prints | Holds |
|---|---|---|---|
| `contact-pair-male-coupon.stl` | front-top's bay bulkhead | +Z up on its cut base, as front-top builds | the male seat's mouth and body, both M1.4 insert bores, the teardrop lead bore through to the aft face, the root of the fore valve tray behind it and the root of the ridge wall on the crown |
| `contact-pair-female-coupon.stl` | the pump clamp | on its crown, as the clamp prints | the female seat's mouth and body, both M1.4 insert bores, the lead slot open through the crown and the start of both crown grooves |

Both STLs stand in their print orientation with the bed at Z = 0. They use the production PET-GF
material and profile. Each seat's roof is a short bridge between the mouth's round ends; a print
that places no support inside either seat or lead passage is the case being tested, so record
any support the slicer puts there.

## What the prints have to show

1. **Each half seats on its datum.** The connector half enters its seat by hand with no force,
   its ear plate lands on the step inside the mouth, and its mating face finishes flush with the
   coupon face within ±0.1 mm across a straightedge. A body that binds, or a face standing
   proud, means the seat's width or the mouth's length is wrong for the delivered part.
2. **The roof did not sag onto the body.** The connector slides out again freely; no witness
   marks on its top or bottom face.
3. **The insert bores take the inserts.** Each M1.4 × 4 × Ø2.3 heat-set presses flush with the
   step, square to the face, and an M1.4 × 5 socket-head screw draws the ear down without lifting
   the connector's face or spinning the insert.
4. **The leads pass.** With 22 AWG leads soldered to each half's four tails, the male half seats
   with its leads drawn back through the teardrop bore, and the female half seats with its leads
   lying in the slot and grooves below the crown face.
5. **The pair mates.** Brought face to face by hand, the halves attract in one orientation and
   seat against each other; each of the four contacts shows continuity across the pair and none
   shows continuity to a neighbour.

Checks 1, 2, 4 and 5 need only the connector pair. Check 3 needs the M1.4 inserts and screws in
[`bom.md`](/hardware/ledger/bom.md) §13.

## Open questions the prints answer

- The ear plate's overall length is read off the listing drawing's scale, not dimensioned on it;
  check 1 settles whether the mouth clears the delivered ears.
- The Ø2.0 bore for the M1.4 insert is a starting size; the listing gives no hole diameter.
  Check 3 settles it.
