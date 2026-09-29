# v5 — The inspection booth: look at and pull every crimp, whoever made it

Explorer: machine-that-sees-and-learns.

Sketches: [`../sketches/v5-inspection-booth.svg`](../sketches/v5-inspection-booth.svg)
(schematic); [`../sketches/w2-v5-box-roll-gauge.svg`](../sketches/w2-v5-box-roll-gauge.svg).

Numbers:
- **[calc: vision_budget §n]** [`../calc/vision_budget.out.txt`](../calc/vision_budget.out.txt);
- **[calc: campaign §n]** [`../calc/campaign.out.txt`](../calc/campaign.out.txt);
- **[calc: wave2 §n]** [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
- **[rap P §n]** ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt);
- **[bm W §n]** borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt);
- **[Prime]** a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

Related: in line in [v1](v1-watched-nest.md), [v6](v6-patient-cell.md),
[v8](v8-tack-look-crimp.md) and [v9](v9-tack-at-the-anvil.md)'s dwell; its
pallet mode is with ribbon-as-pallet's
[a1b](../../ribbon-as-pallet/ideas/a1b-hand-shuttle.md) and
[a2d](../../ribbon-as-pallet/ideas/a2d-by-hand.md); its housing mode with
into-the-housing's [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md);
its pull jig is the same part as hand-tool-as-press's
[a6](../../hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md) backed plate.

## Picture it

**Where things start.** A printed booth about the size of a shoebox on the
bench.
- **Support.** A hardened steel blade on edge under where the crimp's conductor
  barrel will rest: the back of a razor blade (AccuTec steel-back single-edge
  blades, $12.90 for 100 [Prime]) or a ground feeler strip. A micrometer's blade
  anvil turned sideways. A channel with a lance relief runs along it.
- **Roll flat.** Beside the blade, a ground flat at the height of the box's
  floor. A light spring finger presses the box onto it, so the square box, not
  the round insulation, sets the crimp's roll.
- **Stop.** A **lance-notched stop** behind the box: a steel plate thinner than
  the neck gap, notched to pass the floor strip and the lance (≥0.9 mm deep
  below the floor, wider than the lance), bearing on the box's side walls, and
  on its top wall if it comes down from above. The lance tip stands 0.24–0.64 mm
  behind the box and 0.6–0.9 mm below its floor [into-the-housing's [`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt) §1, CJT drawing 2.44 ±0.20 mm; xh-facts §1]. Material under the floor strip would meet the lance tip, and a
  20 N pull there loads the lance at its rated retention (19.6 N clone minimum)
  [rap P §3].
- **Light.** An LED backlight on the far side; the camera on the near side,
  looking straight across at crimp height. A 45° first-surface mirror above
  ($20.90 [Prime], cut down) puts a top view into the same frame at a second
  focus setting.
- **Clamp and pull.** A servo-closed clamp with soft jaws waits for the
  insulation 20 mm behind the contact; behind it a small lead-screw axis with a
  load cell pulls.
- **Reference.** A gauge pin of known diameter lies across the blade beside the
  crimp in every frame (Accusize pin gauge set, $45.58 [Prime]).

**What moves.**
1. The person drops a freshly crimped conductor into the channel, box against
   the stop.
2. The roll finger and the clamp close.
3. The camera takes its pictures.
4. The pull axis draws the wire back to ~20 N while the camera watches the
   insulation edge in the window.
5. The clamp opens.

About twenty seconds a crimp [estimate].

**What locates what.** The blade sets the height reference: crimp height is
measured from the blade's top edge to the crimp's top edge at the barrel centre,
where a point micrometer would measure [prior-art §6]. The roll flat and the
box's own silhouette set roll. The stop sets the axial position. The gauge pin
sets the scale. The reference for "fixed" is the blade.

**What drives and carries force.** Only the proof pull: ~20 N through the clamp,
the wire, the crimp, the box's side walls and the notched stop. The booth never
crimps.

**How it knows.** OpenCV's readings:
- **Side silhouette:** conductor and insulation crimp heights, roll-corrected;
  bellmouth; brush length; bend-up or bend-down.
- **Top view (mirror):** crimp width; seam centred; strands escaping; twist
  against the box; insulation visible in the window, "approximately 50/50"
  [mfr S5].
- **Proof pull:** peak force, and whether the conductor moved in the barrel.

Borderlines go to Claude with reference crops ([v7](v7-the-run.md)). Thresholds
come from [v3](v3-press-that-runs-experiments.md) once it has run; until then
from the published criteria [xh-facts §5], plus crimp height checked against ten
crimps under a point micrometer (Shars 303-2307, $61.95 [Prime]).

**What the person does.** Drops each crimp in, reads PASS or a reason, re-makes
the ones that fail. The log keeps every picture with loom and pin.

**Steps it covers:** verify the crimp (per crimp), and in mode 3 verify
insertion and pin order. **What it hands back:** all making.

## Where it sits

The smallest machine in this view. It makes nothing and automates only the
verify step. It can be built and used before anything else here exists: with
Derek's hand crimps from the SN-2549 today, and later as the inspection station
every other machine in the study hands its crimps to. It is rung 0 of
[v7](v7-the-run.md)'s ladder, where the log, the capture app and the judge are
first built.

## Roll is part of the height, and the box reads it

- **The problem.** Seen across the wire, a crimp rolled by r shows
  H cos r + W sin r: +0.028–0.033 mm per degree for a rectangular section, about
  half that for a rounded bottom [rap P §5]. Against ±0.05 mm, roll must be held
  to ~1–2°, and the error only ever reads tall: a rolled good crimp can read as
  under-crimped, and an over-crimp can read as good.
- **What answers it, used together:**
  1. **The roll flat** above.
  2. **The box as its own gauge.** The box's front 1 mm, ahead of the lance, is
     a clean square section of 1.85–1.95 × 2.2–2.4 mm. Its silhouette grows
     32–34 µm per degree of roll [calc: wave2 §1]. Against the lot's reference
     box height, roll is read to ~0.05–0.3° (45–122 px/mm) and the crimp height
     is corrected by the crimp's width × sin(roll). Correcting with the mean of
     the rectangular and rounded bounds leaves ~±0.015 mm at 2°; a crimp rolled
     more than 2° is re-seated.
  3. **The lot's reference box height:** the minimum over a ±4° roll sweep of
     five contacts at lot start. Box-to-box spread inside a lot enters directly:
     ±10 µm is ±0.3°, ~±0.01 mm of height.
  4. **In a pallet** (mode 4) the ribbon holds roll to ≤1° at 10–20 mN of
     set-down [rap P §5].
- **What stays uncertain:** whether the box's flats are true to the crimp. A
  crimp twisted against its box is a defect in itself, and the top view looks
  for it.

## Modes

1. **After the hand tool.** Derek crimps with the SN-2549 as today and drops each
   crimp in: ~20 s a crimp, ~18 min a unit. The machine learns what his hand
   crimps measure and how much they vary: the baseline any automated crimp is
   judged against.
2. **In line with a machine.** v1's silhouette window is this booth built into
   the press. v6 passes each crimp through it. v8's station C uses it after the
   heavy crimp. On an applicator (borrowed-machines'
   [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
   [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md),
   [v9](v9-tack-at-the-anvil.md)) it sits at the dwell's withdraw position, the
   crimp ≥7 mm out of the applicator with nothing above or beside it: a
   backlight, a blade under the barrel, and the box's front 1 mm read for roll.
   That gives those machines an in-line crimp height, with the crank's own
   re-touch as a second reading ([v3](v3-press-that-runs-experiments.md)).
   There the pull reacts on a thin fork in the neck, since neither the box's
   width nor its height separates it from a crimped insulation barrel across
   lots [bm W §8].
3. **The finished housing.** A small PCB carries one of each XH wafer the board
   uses (4, 5, 6, 7 and 9-way). The finished housing plugs on, and a harness
   tester checks pin-to-pin continuity and adjacent shorts against the loom's
   recipe; J2's empty cavity 3 must read open [repo: cable-assemblies.md]. JST's
   handling precautions say to check continuity only against the applicable
   header [into-the-housing, mfr]. into-the-housing's i5 makes the same board
   the insertion nest. A camera on the mating face first confirms every contact
   sits at the same depth and, where the lance shows in its window, that it has
   latched.
4. **The booth docks a whole pallet** (with ribbon-as-pallet's a1b and a2d). A
   ribbon end crimped by hand on a docked strip segment comes to the booth still
   on its carrier. The pallet sits on a kinematic seat and a detented slide steps
   each crimp over the blade. Roll is held by the ribbon; the proof pull reacts
   through the still-attached tab with a hold-down on the box; one dock per
   ribbon end (14 a unit) replaces 53 drop-ins; tabs are sheared after
   inspection. This mode needs no neck gap.
5. **With a foot bench.** hand-tool-as-press's a6 pull jig is a backed slotted
   plate on the box's rear walls: this booth's lance-notched stop. Adding the
   blade, the roll flat, the backlight and the camera gives every foot-closed
   crimp a roll-corrected height, bellmouth, brush and window reading, while a6's
   capstan lever pulls to its leaf switch. a6's side frame holds roll only to
   ±10–15°, loose for a silhouette, so the roll flat and the box gauge do the
   work.

## Problems, and what answers them

- **The crimp lies rolled on a knife edge.** The roll flat, the box gauge, the
  lot reference, the pallet.
- **A V-groove hides the bottom edge** in silhouette. The blade is used instead:
  its top edge is the lower reference and everything above it is visible.
- **Non-telecentric optics.** A crimp 0.5 mm nearer the camera than the gauge
  pin is scaled 0.5 %, ~4 µm at 100 mm [calc: vision_budget §3]. The channel
  keeps both on one line.
- **The stop and the lance.** The notched stop. If the neck is too short for any
  plate, the booth checks shape without a pull in mode 1, and pulls in mode 4.
- **Is the proof pull worth it on hand crimps?** It is the one check that reads
  grip rather than shape. Whether 20 N is harmless is tested in v3.

## Contribution

- A verify station for the whole study, built first on the bench as it is and
  used with the process as it is.
- A baseline of Derek's own crimps before any automated crimp exists.
- Pictures and pull results that become the labels for every other idea.
- An in-line crimp height for applicator machines, read outside the applicator.

## Major unresolved problems

- **Silhouette against micrometer height.** Offset and scatter are unmeasured;
  the Shars point micrometer is on Prime, a point-and-blade crimp micrometer is
  not [Prime].
- **The neck gap,** which decides whether the notched stop fits a kit contact.
- **Hand-drop consistency.** Whether dropped crimps lie the same way each time;
  a funnel lead-in on the channel may be needed.

## What rests on assumptions

- Edge-fit repeatability.
- Box-to-box height spread in a lot.
- That the proof pull is harmless.
- That the published criteria [xh-facts §5] are the right thresholds before v3
  measures better ones.
