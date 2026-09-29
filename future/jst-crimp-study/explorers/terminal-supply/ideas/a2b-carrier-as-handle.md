# a2b — The carrier kept as the handle, through inspection and insertion

Branch of [`a2-strip-indexer.md`](a2-strip-indexer.md). **What it changes:** a2
cuts the tab at the station, so the crimped contact leaves bare. a2b cuts the
carrier on either side of the contact instead, and the contact keeps a small
piece of its own carrier: a tag 2.3 mm wide and 3.0 mm deep, with the pilot hole
in it, still joined by the tab. The tag travels with the contact through
inspection and most of the way into the housing and sets the contact's pose. It
does not carry the pull test.

Sketch: [`../sketches/a2b-carrier-as-handle.svg`](../sketches/a2b-carrier-as-handle.svg) (schematic).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §4, §5, §9
[ts §n]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§4, §12 [mtsl §n].

**Related.** [x2](x2-crown-then-sort.md) uses a2b's tag as its sorting handle in
one variant (the tag instead of a post head). The docking comb below pairs with
machine-that-sees-and-learns'
[v2](../../machine-that-sees-and-learns/ideas/v2-arm-taught-by-hand.md) arm.

## Picture it

- **Crimping.** The strip indexer crimps conductor k as in a2.
- **Cutting.** Instead of dropping the tab, a small two-blade shear under the
  carrier cuts the carrier at ±1.15 mm from the pilot hole's centre. Its blades
  go down, away from the wire, like the drop-shear. The contact now hangs from
  its conductor with a 2.3 × 3.0 mm bronze tag behind its insulation barrel. The
  tag lies in the floor plane and has a Ø1.5 hole exactly on the contact's
  centreline.
- **Taking hold at two points.** A gripper of two parts takes the crimp:
  - a pin drops into the tag's hole: position in the plane;
  - two fingers close above and below the crimped insulation barrel: height,
    roll and a second point in the plane.

  The tab neck is compliant (~59 N·mm/rad [mtsl §12]) and is now outside the
  grip's loop. The lower finger passes under the tag and the upper one lands on
  the crimp, so the wire lying over the tag is not in the way.
- **Inspecting.** In that pose the side camera measures bend-up, bend-down and
  twist against the tag's plane; the top camera sees the brush and window; both
  measure the box tip's offset from the hole, which the insertion approach adds.
- **Proof pull, not through the tag.** A slotted plate that passes the barrels
  but not the box slides in behind the box's rear face. The gripper lets go, the
  ribbon carriage pulls the wire to ~20 N against the plate while the camera
  watches the insulation edge for slip, then the gripper takes hold again and
  the camera re-measures the box tip against the hole. Pulling against a tag
  behind the contact would load the tab eccentrically; it yields at 2.5–14 N
  depending on neck width and height [mtsl §4].
- **Inserting.** The same gripper carries the contact to the housing, aligns it
  with cavity k from the hole plus the measured box-tip offset, and pushes while
  the cavity guides the box. Just before the box meets the mouth the camera
  looks at the box tip once more: a conductor's drape of 0.5 N at the box moves
  the tip by the whole cavity window [mtsl §12].
- **Removing the tag.** When the carrier edge nears the rear face, the gripper
  stops, bends the tag down ±90° once or twice against a fulcrum at the
  insulation barrel's rear edge (it breaks in 1–5 cycles [ts §9]), and a fork
  behind the insulation barrel finishes the seat.
- **What the person does.** Nothing beyond a2.

## Why a tag

The hard part of moving a crimped contact is knowing where it is in the
gripper. The Cellios robot cell measures the crimp's position in the gripper
after every handling, because it "changes with every handling operation"
[prior-art §0]; the Sogang ribbon prototype lost most of its trials moving the
floppy cable, not inserting [prior-art, Start here]. A stamped hole on the
contact's centreline, at a fixed distance from its barrels, is a mechanical
datum: a pin in the hole the stamping die already made, plus one measured
correction per contact.

## What locates what, and the force

| Moment | Reference | Located part |
|---|---|---|
| Crimp | a2's pins, fence and anvil block | contact |
| Tag cut | two-blade shear under the carrier, at ±1.15 mm from the hole | tag width |
| Inspection and carry | pin in the hole (in plane) + fingers on the crimped insulation barrel (height, roll) | contact |
| Insertion | the hole plus the measured box-tip offset; then the cavity walls | box tip |
| Seat | fork behind the insulation barrel | contact rear |

**The reference for "fixed"** is a2's anvil block while crimping, then the
gripper's pin and fingers, then the housing nest.

**Force.** The crimp is a2's. The proof pull (~20 N) goes from the carriage
through the wire and crimp into the slotted plate at the box's rear face. The
insertion push goes through the fingers on the crimp; the tab only carries
position. In-plane, the tab neck (0.6–1.0 × 0.2 mm) carries 66–110 N before
yielding; out of plane it yields at ~4–6 N if the resistance acts 0.8–1.2 mm
above the floor plane with nothing else reacting the moment [ts §4].

## The numbers that shape it

- **Width.** A tag wider than 2.5 mm hits the neighbour's at XH pitch. Trimmed
  to 2.3 mm it clears by 0.2 mm; the ligaments beside the hole are 0.4 mm each
  and together carry ~88 N [ts §4].
- **The box tip from the hole.** The tip sits 5.0–6.5 mm ahead of the hole. Each
  degree of bend or twist puts it 0.09–0.11 mm off, against a cavity entry window
  of about ±0.2 mm [mtsl §4]. Dead reckoning holds within ~2°; the per-contact
  correction and the second look cover the rest.
- **Does the carrier edge block the seat?** Taking the housing's front wall as
  0.8–1.0 mm [assumption], JST's 6.1 or 6.5 mm contact and a 0.8–1.15 mm tab, the
  carrier edge ends between 0.05 mm inside and 0.9 mm outside the rear face at
  full seat [ts §4]. In the worst case it stops the contact 0.05 mm short, hence
  the bend-off and fork before the last push.
- **Wire combs.** The tag is 2.3 mm wide; the U-slots of into-the-housing's
  combs (i6, i6b, i3's clamps) are 1.5–1.6 mm. A tagged contact cannot enter
  them, so its rear stands 3.8–4.2 mm ahead of such a comb's face, and a backing
  blade bears on the tag's rear edge (0.46 mm², 54 MPa at 25 N) instead of the
  insulation barrel. In a gang push the tags are either bent off after a partial
  push (two push phases) or used for the sort only and cut before the push.

## The comb (sub-variant)

- **What changes.** Every conductor of a ribbon is laid into consecutive
  contacts while they stay on the strip, 7.1 mm apart, all before any crimp, as
  in ribbon-as-pallet [a2](../../ribbon-as-pallet/ideas/a2-two-pallets-meet.md).
  The strip then indexes each contact to the punch in turn and the ribbon rides
  along. The carrier is cut once, after the last. Because every conductor is
  already in its own contact, none lies on a fresh one.
- **What comes out.** A ribbon end hanging from one rigid carrier segment 3–5
  pitches long, every contact in the same pose and in pin order: a comb.
- **The cost.** At 7.1 mm pitch the conductors fan much wider than a housing
  needs. At a 20° fan the split grows [ts §5]:

  | Ribbon | Split for the comb | Split for XH's 2.5 mm pitch |
  |---|---|---|
  | 3P | ~15 mm | ~2 mm |
  | 4P | ~22 mm | ~3 mm |
  | 5P | ~30 mm | ~4 mm |

  Each also needs the ~6 mm straight run into the contact.
- **What the comb is good for.** Transport as one rigid, keyed object with pin
  order fixed by position; inspection of 3–5 crimp silhouettes in one frame
  along the comb; a pallet with its own datum, docked by two pins in two carrier
  holes plus the carrier edge on a fence, so an arm with 1–2 mm of slop
  (machine-that-sees-and-learns v2) delivers it to a precise station.
- **What it cannot do.** Go into the housing as a comb: contacts 7.1 mm apart in
  one plane collide with the rear face when the first one seats. They leave the
  comb one at a time, each cut to its own tag. A crimp that fails makes the whole
  comb segment scrap.

## Problems and repairs

1. **The wire lies on the tag.** Repair: the two-point grip; the lower finger
   passes under the tag, the upper one lands on the crimped insulation barrel,
   and the pin reaches the hole in the tag's rear half.
2. **A proof pull through the tag bends the tag** [mtsl §4]. Repair: the pull
   goes to the box's rear face through a slotted plate with the grip released,
   and the pose is re-measured afterwards. Whether the box's 0.2 mm walls take
   20 N on a plate edge stays open.
3. **The hole locates the tag, not the box tip** [mtsl §4]. Repair: the
   two-point grip takes the neck out of the loop; one measured correction per
   contact; a last look at the box tip before the mouth.
4. **Tags of neighbouring conductors overlap** near the ribbon end at the web's
   1.7 mm spacing. Repair: on a backlight each unobstructed hole is a bright
   1.5 mm disc, 67 px across at 45 px/mm; a tag lying on top shows its full disc,
   one underneath a crescent or nothing. The picture says which tag is free to
   pick, and a comb finger holds back the rest.
5. **Stub length after bend-off.** A fulcrum edge at the insulation barrel's rear
   should put the break at the neck's contact end, leaving ~0 to a few tenths
   [estimate]. JST faults both no stub and a long stub [xh-facts §1]. Open until
   tried.
6. **Tags cannot enter wire combs.** Repair: two push phases, or cut the tag
   before a gang push (above).

## How it knows it worked

a2's signals through the crimp; then the posed side and top pictures (bend,
twist, brush, window, box-tip offset); the proof-pull trace with the insulation
edge watched for slip; the last look at the box tip before the mouth; the
fork's force trace at the seat (lance event, then wall).

## Steps covered, and what it hands back

- **Covers:** everything a2 covers, plus posing the crimp for inspection, a proof
  pull, and carrying the contact to and into the housing up to the last ~1 mm.
- **Hands back:** splay and strip; the final seat by a fork (which can be a
  separate station); the housing's own nesting and indexing.

## Printed and bought

As a2, plus: a second small two-blade drop-shear (steel, bought or ground from
flat stock); a two-point gripper (a 1.448 mm pin gauge in a printed body, and two
fingers of 1095 shim — Precision Brand assortment, Prime, $53.39
[sourcing/amazon-prime.md] — on an MG90S servo); a slotted pull plate (stencil
steel) and the ribbon carriage's pull; a steel bend-off fulcrum; a fork with
steel shim tines.

## Contribution

A datum carried with the part from reel to housing: a stamped hole on the
contact's centreline, which sets the pose for inspection and insertion. Held
together with the crimped insulation barrel, it keeps the compliant neck out of
the loop.

## Major unresolved problems

- **Whether the two-point grip fits between neighbours** at the housing at
  2.5 mm pitch.
- **Stub quality from a bend-off done beside a housing.**
- **Whether the box walls take a 20 N proof pull** on a plate edge.
- **Carrier edge versus rear face at full seat,** −0.05 to +0.9 mm, with the
  front-wall thickness assumed. One kit housing with one contact settles it.
- **Tags against wire combs** in any gang push: two push phases, or no tag.
- **The comb's long split,** and whether more free length at each loom end
  matters for dressing and strain relief (Derek's question).

## What each conclusion rests on

- **Facts [mfr, source]:** carrier and tab geometry from clone drawings; JST's
  stub faults [xh-facts §1]; prior-art on gripper uncertainty.
- **Calculations [calc]:** tag width, ligaments and neck strength [ts §4]; comb
  split [ts §5]; bend-off cycles [ts §9]; tab yield and box-tip sensitivity
  [mtsl §4, §12].
- **Estimates:** tab neck width 0.6–1.0 mm (read from clone drawings); C5191
  yield 550 MPa; insertion force 3–20 N; stub after bend-off.
- **Assumptions:** the housing's front-wall thickness (0.8–1.0 mm).
