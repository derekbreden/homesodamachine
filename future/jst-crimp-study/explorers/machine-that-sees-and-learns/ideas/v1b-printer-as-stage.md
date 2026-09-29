# v1b — Branch of v1: a cheap printer's three axes become the stage

Explorer: machine-that-sees-and-learns. Parent: [`v1-watched-nest.md`](v1-watched-nest.md).

Sketch: [`../sketches/w3-v1b-axes.svg`](../sketches/w3-v1b-axes.svg)
(schematic: four ways to give the pallet its axes).
Numbers: [`../calc/cycle_and_cost.out.txt`](../calc/cycle_and_cost.out.txt) §1;
this view's [`wave2.out.txt`](../calc/wave2.out.txt) (**[calc: wave2 §n]**) and
[`w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt)
(**[calc: w3htp §n]**); borrowed-machines'
[`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt)
(**[bm W §n]**); ribbon-as-pallet's
[`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt)
(**[rap P §n]**). **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28. Controllers and software: [`v7-the-run.md`](v7-the-run.md).

## Picture it

**Where things start.**
- An **Ender-3-class bed-slinger** stands on the bench with its hot end
  removed. The Creality Ender 3 V3 SE is on Prime at $219.00 (2,112 ratings,
  500+ bought in the past month) or $186.14 (791 ratings, 200+ a month)
  [Prime]. The two Bambu H2Cs are not used: they are busy printing the
  appliance [repo: tools.md] and are not an open G-code port.
- On a bed-slinger the bed moves front to back, the carriage moves side to
  side, and the gantry moves up and down. A thing on the bed has one axis; a
  thing on the carriage has two.
- v1 wants three things from the stage, per conductor: **across** (key to
  key), **along the wire** (the insulation edge into the window, read per
  conductor because strip scatter uses 20–120 % of it [calc: wave2 §2], and
  the ~20 N proof pull), and **height** (set once per ribbon end; the key, not
  the stage, drops each conductor).

**Four ways to hand out those axes.** Which one fits depends on what the
crimp host weighs and whether it can move.

| | What rides where | Along the wire comes from | Fits |
|---|---|---|---|
| **A. The press rides the bed** | A small self-contained press or tack station bolted to a stiffened bed plate; the fan block hangs from the carriage where the hot end was | The bed | A tack station ([v8](v8-tack-look-crimp.md)'s T); a knee press or a4c's one-nest die set if a few kilograms ride the bed |
| **B. The Ender on its back** | The printer lies on its back in front of a bench-fixed press. The carriage still gives across; the gantry's two Z lead screws now run along the wire; the bed axis stands vertical and unused. The fan block hangs from the carriage | The Z lead screws | Any press that cannot ride a bed: the idle 12-ton shop press, a 38–55 kg mute press, b1b's crank frame |
| **C. Two rails in front of the press** | borrowed-machines' b1 shuttle: two MGN12 rails ($20.49 [Prime]) with NEMA 17 Tr8×2 steppers ($27.99 [Prime]), across and along, bolted to the press table; height fixed | The second rail | The same presses as B, built rather than bought whole |
| **D. The head on the carriage** | b3's ~1 kg crimp head, whose force closes inside its own laser-cut C-frame, on the carriage; v1's fan block and keys on the bed; v1's cameras on the head's frame | The bed moves the ribbon; the head moves across and down | A head light enough for a printer carriage |

**What moves (A–C).** The runner sends `G1` moves and `M400` (wait until moves
finish), then asks for a picture ([v7](v7-the-run.md), stack A). The picture
closes the loop, so the printer's own accuracy only has to be monotonic and
repeatable over a few tenths of a millimetre, approached from one side.

**How the fan block mounts.** A kinematic seat: three steel balls (6 mm chrome
steel, $6.65 per 100 [Prime]) on the block, in three pairs of hardened dowel
pins ($6.49 [Prime]) pressed into the carriage bracket, pulled home by a magnet
(N52 10 × 3 mm, $23.99 [Prime]). Only steel touches steel, at 877–1,658 MPa of
Hertz peak, fine for hardened pins; a ball on printed PETG flanks peaks at
67–126 MPa, above PETG's ~50 MPa yield, and would bed in and creep [rap P §7].
Repeatability of a steel-on-steel seat in printed bodies is [estimate: a few
µm]; a dial indicator over 50 seatings measures it.

**The loom's tail.** The XH end is made first, so the tail is an unterminated
cut end. It coils in a printed cup on the fan block, its cut face in a small
pogo block wired to the station MCU through a light cable in the drag chain.

**What locates what.** As v1: the nest locates the contact; the key and the
picture locate the conductor. **The printer is the arm, not the reference;**
the reference for "fixed" is the anvil as the camera sees it. In D the anvil
travels with the head and the cameras travel with it, so camera-to-anvil still
never changes.

**What drives the crimp and carries its force.** The press, through its own
frame (A–C), or the head's C-frame (D). The printer's belts and screws carry
nothing during the stroke except holding still. The only printer axis that
carries a real load is the along-wire one during the ~20 N proof pull:
- on the bed's belt (20-tooth GT2) that is 0.13 N·m at the motor, about a third
  of a small NEMA 17's holding torque [estimate];
- on a Tr8 lead screw (arrangement B) it is 0.02–0.09 N·m [bm W §7], and a
  lead screw holds position unpowered;
- a missed step during the pull shows in the picture anyway, since the edge
  moves and the force drops.

**How it knows it worked.** v1's pictures, force trace, continuity and proof
pull.

**What the person does.** Loads fan blocks onto the seat and contacts into the
supply, and answers the queue.

**Steps it covers:** the motion for v1's placement and lay-in, v8's tack
station, and the pallet tour; the proof pull's travel.
**What it hands back:** everything v1 hands back; the stage itself decides
nothing.

## What it changes from v1

Only where the motion comes from. v1 needs a
three-axis stage that software can drive in 0.05 mm steps; it need not be
accurate, because the picture steers it. A bed-slinger printer is that, bought
whole. The same stage serves [v8](v8-tack-look-crimp.md)'s tack station,
ribbon-as-pallet's [a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md) pallet
tour, and hand-tool-as-press's
[a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md).
Arrangement D combines it with borrowed-machines'
[b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md).

## Why a printer and not a built stage

- **Effort.** It is the lowest-effort route to a working three-axis motion
  system; it arrives in days rather than being designed.
- **Its limits don't matter here.** Belt stretch, 0.02–0.05 mm-class
  repeatability [estimate] and no absolute encoders are all acceptable when a
  picture closes the loop and every target is approached from the same side.
- **The lead-screw alternative.** A 3018-class desktop CNC frame (SainSmart
  Genmitsu 3018-PROVer V2, $269 [Prime]) holds position unpowered and would
  hold the proof pull stiffly. into-the-housing's
  [i4](../../into-the-housing/ideas/i4-gantry-hand-with-eyes.md) names that
  frame. It changes nothing else here.

## Arrangement B, the Ender on its back

- The frame lies on its back, gantry toward the press. The carriage's belt axis
  runs across the conductors. The two Z lead screws, now horizontal, carry the
  gantry and so the carriage along the wire. The bed hangs vertical, unused, or
  comes off.
- Height is set once per press by shimming the printer's frame, since the key
  does the lowering.
- **Uncertain:** the frame's stiffness lying on its back with a ~1 kg fan block
  on the carriage, and whether stock firmware homes a Z that no longer works
  against gravity [assumption]; a reflash to Klipper or FluidNC removes the
  second question.

## Arrangement D, the head on the carriage

A combination with borrowed-machines'
[b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md), whose
crimp head takes the crimp to a still ribbon.
- **What each brings.** b3: a light head that closes its crimp force inside its
  own C-frame, so the carriage and belts carry none of it. v1: the fan block and
  keys, which hold the neighbours 5 mm up, and cameras on the head's frame.
- **What it does that neither does alone.** v1's "the press rides the bed" is
  heavy for a bed; here the heavy object is on the axis built for a tool head.
  b3's fan fixture has no lifted neighbours; here the waiting conductors are
  out of the head's way.
- **Open problems:**
  - the head's punch must stay under 7.45 mm wide at the neighbours' height, as
    in v1 [calc: w3htp §7];
  - the C-frame's throat must reach past a 5P fan at 5 mm pitch (±10 mm across);
  - b3's own: harvested punches, and C-frame stiffness at low mass.

## Problems, and what answers them

- **A press's mass on a bed-slinger bed (A).** A die-set press with a NEMA 23
  may weigh 3–6 kg [estimate]; Ender beds are built for a few hundred grams. At
  5–20 mm/s the motor's torque is not the problem; the bed wheels' preload and
  the bed's sag are. A stiffer steel plate on the same carriage, or B, C or D.
- **Firmware surprises.** Stock firmware may release idle steppers, home
  unexpectedly, or complain without a hot end [assumption: the V3 SE's stock
  behaviour is unchecked]. `M84 S0`, re-homing and re-finding the fiducials
  whenever the port reconnects, or a reflash ([v7](v7-the-run.md) stacks B
  and C).

## Contribution

A concrete, purchasable stage for v1, v8, a4c and ribbon-as-pallet's a1, at
about $190–220, with four ways to give a bench-fixed or heavy press the axes
the pallet needs. Derek already builds and runs G-code machines, and the rest is
Python.

## Major unresolved problems

- Which arrangement suits the host chosen: whether it rides a bed (A), or needs
  B, C or D.
- The stock firmware's behaviour as a plain G-code stage, upright or on its back.
- The Ender frame's stiffness on its back.
- The pogo block's cable run on the carriage, and a tail cup that holds a
  600 mm coil without it creeping out during moves.
- D's throat reach past a 5P fan.

## What rests on assumptions

- Bed-carriage stiffness under a few kilograms.
- The belt pulley size (20-tooth GT2).
- The stock firmware's commands.
- Seat repeatability until measured.
