# Fuse clamp

Printed bracket that holds the BOJACK SF76E thermal cutoff's case against the
compressor's power box — the moulded cover over the terminal block and the PTC
start relay ([`reference/compressor`](/hardware/reference/compressor/),
`power_face()`).

A [77](CLAMP_TF) °C cutoff opens on the temperature of **its own case**. Leads
carry no thermal load, and a case laid against a face reads cabinet air until
something presses it on. This is that something.

One part prints here: the **clamp**.

| | clamp |
|---|---|
| type | printed PETG |
| width | [18](CLAMP_PART_X) mm, the whole part |
| head | [18](CLAMP_HEAD_Y) mm tall × [6.7](CLAMP_HEAD_Z) on the seating plane |
| channel | [4.6](CLAMP_CHANNEL_H) × [4.2](CLAMP_CASE_D) mm through it, open both ends |
| neck | [3.5](CLAMP_NECK_Z) mm out of the face |
| leaves | [2.5](CLAMP_LEAF_Y) mm thick, [22](CLAMP_LEAF_REACH) aft, [10](CLAMP_LEAF_SLOT) of slot between |
| volume | [5.56](CLAMP_VOL) cm³ |

## What holds the case

The channel's depth is the case's **own diameter**, so its crown lands on the
outboard generatrix and the pinch is cover — case — crown, with the case's whole
diameter between the two and nothing of the clamp inside it. Its height is one
slip over the case, so the walls fence the case in and never take the load.
`enclosure_assembly.check_cutoff_bedded` is that reading, taken off the placed
solids at every build.

The pocket that leaves is bounded on every side by either the cover itself or by
a head that lies flat on the cover over ~300 mm² — so the case sits in dead air
between surfaces that are at the temperature it is there to read, and the clamp
carries no fin, no boss and no mass out into the bay.

## What holds the clamp

**The case's force is a normal force, and no face of the cover can take one.** A
box has a front, a top, a bottom and two sides, every one of them a plane whose
normal is across that push; a hook over any of them resists nothing pressing
straight out of the front, and no band closes around a box whose aft face is
moulded onto the shell.

The plate's four holes are spoken for — donor grommet and the floor's own
printed post rising through each ([`bom.md`](/hardware/ledger/bom.md) §13,
[`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §5). The
grommet is the isolation element, so anything landing on one of those screws is
fastened to the **cabinet** while the cover it presses rides the can, and every
running hour of the compressor is then relative motion at the case.

What is left is the gap: a slot [15](CLAMP_GAP) mm tall whose two faces — the
box's underside and the plate's crown — **both belong to the compressor**. Two
leaves reach aft into it off the neck, one on each face, chamfered at the tip so
they start in rather than butt the mouth. The clamp therefore rides the
compressor: the vibration is common to the clamp, the cutoff and the face, and
nothing bridges to the cabinet. Nothing is drilled and the cover is not touched.

**Every fit is drawn on the thing it closes on** — the channel's depth is the
case's diameter, the leaves span the gap's height — so the model is the nominal
fit and what makes each of them a press is the print's own tolerance. The leaves
take it up: they are cantilevers [22](CLAMP_LEAF_REACH) mm long and the one
compliant thing in the part, so a [15](CLAMP_GAP) mm gap the donor does not
promise to the tenth is absorbed by bending rather than by crushing a fuse or
losing the contact.

## Service

A thermal fuse is one-shot. The cutoff threads in along the channel from either
end and comes out the same way, so replacing it disturbs neither the clamp nor
the compressor. The clamp itself draws straight forward off the gap when a hand
pulls it.

The channel holds the whole [3](CLAMP_LEAD_STUB) mm of straight the SEFUSE SF/E
datasheet reserves against a bend, and lets the lead go half a millimetre past
it. That leaves [16.5](CLAMP_SPLICE_FREE) mm of the short lead in the open —
against the [12](CLAMP_SPLICE_REACH) mm a crimp splice takes — so no bend and no
splice ever lands inside the [3](CLAMP_LEAD_STUB) mm the part forbids them in.

The case is live at mains potential, and both faces it touches are insulators:
the donor's own moulded cover on one side, this part on the other.

## Frame and print

X is the cutoff's axis, across the cover's [45](CLAMP_FACE_X) mm width. **Z = 0
is the seating plane** — the cover's outboard face, the plane
`compressor.power_face()` states, which is the plate's own front edge as well —
with +Z out of it into the cabinet; only the leaves reach behind it, into the
[15](CLAMP_GAP) mm of air under the box. Y is up, 0 on the face's centre, which
is the case's own axis and the box's mid-height.

It is the **cutoff's own frame**, the one
[`reference/sf76e-thermal-fuse`](/hardware/reference/sf76e-thermal-fuse/) draws
in, so `enclosure_assembly` lays both bodies with one turn on one station and
they cannot land apart.

Every feature is a prism on the part's one [18](CLAMP_PART_X) mm width, so the
whole clamp is a single profile swept across X. It prints on its side, on that
face: every layer is the same silhouette, the channel opens to the outside
rather than bridging, and nothing needs support.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py
```

Controls only, including the two bounds this part states about the donor:

```
tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py selftest
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py`
