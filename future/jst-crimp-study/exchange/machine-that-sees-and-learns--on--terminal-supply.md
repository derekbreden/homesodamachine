# machine-that-sees-and-learns on terminal-supply

machine-that-sees-and-learns builds the first stage of a cell as something
software can move and observe. Every act is bracketed by a look, and the
strictest look comes before the one step that cannot be undone. This file reads
[terminal-supply](../explorers/terminal-supply/summary.md)'s nine arrangements
that way: its idea files, its [notebook](../explorers/terminal-supply/notebook.md)
and its [calc output](../explorers/terminal-supply/calc/terminal_supply.out.txt).
Four questions run through it:

- What can a camera see before the stroke, given how the contact arrives?
- Which positions are set by a taught number, and which should be set by a
  picture?
- What does "back out" mean for each supply form?
- Which steps handed back to the person could the machine take?

Numbers marked **[calc §n]** are in
[`../explorers/machine-that-sees-and-learns/calc/on_terminal_supply.py`](../explorers/machine-that-sees-and-learns/calc/on_terminal_supply.py),
with output in
[`on_terminal_supply.out.txt`](../explorers/machine-that-sees-and-learns/calc/on_terminal_supply.out.txt).
Contact dimensions are the clone drawings in
[xh-facts §1](../context/xh-facts.md). The carrier pitch is terminal-supply's
7.1 mm Würth analog.

Coordinates follow a2's plan view:
- X runs along the strip, and **upstream** is where fresh contacts come from.
- Y runs along the contact.
- Z is up, with the barrels open up.

---

## a2 — strip indexer

[a2](../explorers/terminal-supply/ideas/a2-strip-indexer.md) places and holds
the contact without touching it: pins in the neighbours' pilot holes, the
carrier flat on the anvil, and a drop-shear. That is the part of Derek's
priority step that a strip answers well. The conductor's side of the same step
is where it breaks.

### Break 1: the ribbon's other conductors land on the fresh contacts

- **The conflict.**
  - The conductor at the station comes in from behind, over the carrier.
  - The ribbon's other conductors come in the same way, at whatever pitch the
    fan gives them.
  - Upstream of the station, fresh open contacts stand every 7.1 mm, with
    insulation wings up to 3.0 mm wide and 2.75–3.2 mm tall.
  - A 1.7 mm conductor lying in the plane of the strip hits one of them if it
    lands within 2.35 mm of a contact centre.
- **The numbers [calc §2].**
  - With every other conductor on the upstream side, 3P is clear only for fan
    pitches of 1.7–2.3 mm.
  - 4P and 5P are clear at no fan pitch from 1.7 to 15 mm.
  - At the unsplit web's 1.7 mm, conductors 3 and 4 sit on a fresh contact.
  - At my own v1 fan-comb pitch of 5.5 mm, conductors 1, 3 and 4 do.
- **Consequence.**
  - A stripped tip lies in a fresh contact's open U, or on its wing tips.
  - The next index then drags that contact, or the ribbon, sideways.
  - Or the tip gets under the punch holder, which is wider than the punch.
  - a2 lists "the unused conductors bent up" as unresolved. The calc says
    that lifting them is required, not optional, for every 4P and 5P end.
- **Repair (a branch of a2's carriage).** A pallet with a lifter for each slot.
  - Only conductor k is lowered. The others sit ≥3.5 mm above the carrier plane,
    clear of the 3.2 mm wings.
  - A crimp order can also put every waiting conductor on the empty-carrier
    (downstream) side. Then each crimped conductor is upstream and must stay
    lifted, so the lifter is needed either way.
  - **Changes:** the carriage gains a small actuator per slot, or one
    comb-shaped lifter that indexes. My
    [v6](../explorers/machine-that-sees-and-learns/ideas/v6-patient-cell.md)
    servo tweezer already picks one conductor out of a comb.
  - **Leaves uncertain:** whether the lifted neighbours spring back when their
    lifter lets go. The copper keeps its set below a ~67 mm bend radius
    [digest]. A picture before the stroke shows "no tip other than k below the
    fresh wing tips", and that check belongs in a2's gate.

### Break 2: one taught Y for the conductor

- **The conflict.**
  - a2's carriage "stops at a taught position" and the camera confirms.
  - The insulation edge has to land in the window between the barrels, about
    0.5–1.0 mm long [my calc: vision_budget §4].
  - Two things move it from conductor to conductor:
    - **The fan itself.** A conductor bent out by θ and back again loses
      d·tan(θ/2) of reach, where d is its lateral move [calc §3].

      | Fan | d | Shortfall at 20° |
      |---|---:|---:|
      | 5P into 2.5 mm pitch, outer conductor | 1.6 mm | 0.28 mm |
      | J1's 5P + 4P into XHP-9, outermost | 3.2 mm | 0.56 mm |
      | 5P fanned to 5.5 mm (v1's comb) | 7.6 mm | 1.34 mm |
      | 5P fanned to 7.1 mm (a2b's comb) | 10.8 mm | 1.90 mm |

      If the end is cut square and stripped before it is fanned, the outer
      insulation edges stand this far behind the centre one.
    - **The strip.** Its length is 2.4 mm (JST) or 1.6–2.1 mm (clone
      specification), and silicone tears rather than cutting cleanly
      [xh-facts §1, §7; digest].
- **Consequence.** A taught Y for each slot absorbs the repeatable fan
  shortfall. It does not absorb the tear scatter, or a conductor that slipped
  in its slot. An insulation edge under the conductor barrel is a JST fault
  [mfr S5], and it is made irreversible by the stroke.
- **Repair A (transfer from v1).** Steer Y by the picture.
  - The carriage's Y axis is already driven by software.
  - Capture, fit the insulation edge and the barrel edges, move by 0.7 of the
    error, and repeat. Approach from one side.
  - It converges in 3–8 rounds
    ([v1 step 5](../explorers/machine-that-sees-and-learns/ideas/v1-watched-nest.md)).
  - **Changes:** the taught position becomes a starting guess.
  - **Leaves uncertain:** seeing the insulation edge from above while the
    conductor still rides on the carrier. Black silicone against a tin-plated
    carrier is high contrast, so this is probably easy [assumption].
- **Repair B (procedure).** Cut and strip after fanning, against one datum line
  on the pallet.
  - **Changes:** the systematic shortfall mostly disappears at the source.
  - **Leaves uncertain:** the tear scatter remains, so A still does the
    fine work.

### Break 3: the drop-shear bends the carrier between the pins

- **The conflict.**
  - The drop plate pushes the station's carrier down 0.3–0.5 mm.
  - The tapered pins hold the neighbouring holes at ±7.1 mm, and the sprung
    hold-down holds the rest flat.
  - The carrier between the drop plate's edge and the next pin, about 4.6 mm,
    bends in an S.
- **The numbers [calc §6].**
  - The carrier yields at 0.16 mm of drop, whatever its width. The slots only
    decide where the hinge forms.
  - A 0.3–0.5 mm drop leaves 0.14–0.34 mm of permanent set.
  - That is a kink of about 1.7–4.2° next to the upstream pilot hole: the hole
    of the next contact.
- **Consequence.**
  - The kink is about the contact's own axis, so the next contact arrives
    rolled by that much.
  - That is inside the 5–11° roll window at first die touch [digest], but it
    uses up to half of it. The MKS-L manual traces "rolling" to a contact not
    square on the anvil [mfr MKS-L §7-9].
- **Repair.** Drop only the downstream, scrap side.
  - The downstream pin rides on the drop plate.
  - The upstream carrier is clamped flat right up to the anvil's rear edge, so
    the bend happens in carrier that is thrown away. An applicator's floating
    shear does the same.
  - **Leaves uncertain:** the tab stub's shape when the shear edge is on one
    side only.
- **What the camera adds.** The waiting contact's roll is measured on every
  cycle from the grazing view (Break 4). A drift in roll over a strip is the
  first sign of this kink, or of a pin wearing.

### Break 4 (seeing): the across-the-strip silhouette meets the next contact

- **What was assumed.**
  - a2 checks bend-up, bend-down and twist "from the side". Taken at the
    station, before the carriage lifts the crimp out, that view runs along the
    strip.
  - My v1 gate looks for strands above the wing tips in silhouette, across the
    nest.
  - Both lines of sight run along X, and one pitch upstream stands an identical
    fresh contact.
- **The numbers [calc §1].**
  - The gaps to the upstream neighbour are 5.2–5.4 mm at the conductor barrel
    and 4.1–4.6 mm at the insulation barrel.
  - A camera upstream, tilted down by θ, sees over the neighbour when
    tan θ ≥ (dh + 0.02)/7.1, where dh is how much taller the neighbour's
    wings stand.
  - The same tilt hides the near wing tip by 1.9·tan θ.

  | Neighbour taller by | θ at least | A strand on the near wing tip shows as |
  |---|---:|---|
  | 0 | 0.16° | 75 µm: 3.4 px at 45 px/mm, 6.4 px at 86 px/mm |
  | 0.10 mm | 0.97° | 48 µm: 2.2 px, 4.1 px |
  | 0.15 mm | 1.37° | 35 µm: 1.6 px, 3.0 px |
  | 0.25 mm | 2.18° | 8 µm: invisible |

- **Consequence.**
  - With a flat strip whose wings match to ~0.15 mm, the grazing view works
    and the backlight sits downstream over the empty carrier.
  - A bent-up wing on the next contact, the handling damage a kinked cut strip
    brings, blinds the gate for this contact.
- **Repair: a vane.**
  - A white vane about 1 mm thick, lit from above, slides in from the box side
    into the 5.2 mm gap before the look, and out again before the stroke.
  - The backlight then sits between the two contacts. The camera can look from
    downstream, over empty carrier, at θ ≈ 0.
  - **Changes:** one more servo move per cycle.
  - **Leaves uncertain:** clearance to the punch holder and the lifted
    neighbours.
- **After the crimp the problem is gone.** a2's carriage lifts the crimped
  contact out of the strip, and any view is free.

### Transfer: measure every waiting contact instead of re-teaching per reel

- a2's repair 5 re-teaches the axial offset per strip or reel, by camera.
- But the pre-feed dwell gives a free look at **every** contact: its conductor
  barrel's rear edge against two fiducials on the anvil block.
- The ±0.1 mm bellmouth window is ±4.5 px on the stock ELP and ±8.6 px with a
  close-up lens. An edge fit repeats to 1–7 µm [calc §9].
- A fence on a small stepper moves the strip in Y by the error, every cycle.
- **Changes:**
  - within-strip tab variation stops mattering, and nobody has measured it
    yet (a2 lists it as unresolved);
  - the same picture reads roll (Break 3), bent wings, and a missing or
    flattened lance.
- **Leaves uncertain:** whether the fence moving under a pinned strip drags the
  pins. The fence can move with the pins down and the hold-down lifted.

### Transfer: what "back out" means on a strip

- **A contact that fails its look before the wire arrives.**
  - The machine indexes past it, uncut.
  - That needs a downstream path that clears a whole uncut contact: the drop
    plate, the downstream hold-down and the take-up.
  - As a2 is drawn, only tab stubs pass downstream.
- **A crimp that fails its look after the stroke.**
  - The digest says a single conductor cannot be re-crimped; the whole ribbon
    end is cut back ~6 mm.
  - So the machine stops that end at once. It does not spend contacts on the
    remaining conductors.
  - It queues "cut back and restart J5's end?" with the photo, and moves to
    the next ribbon end.
- **The log.** Carry the strip or reel lot and the index count into each
  crimp's record, so a drift that a later
  [v3](../explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
  re-check finds can be traced to the crimps it touched.

---

## a2b — the carrier kept as a handle

### Break 1: a proof pull through the tag bends the tag

- **The conflict.**
  - [a2b](../explorers/terminal-supply/ideas/a2b-carrier-as-handle.md) proposes
    "a proof pull [that] tugs the wire against the tag", noting the tab neck
    carries 66–110 N in tension.
  - But the pull enters the contact through the crimp, 0.35–0.85 mm above the
    tab's mid-plane. The 30° lift that frees the pad makes it ~1.2 mm.
  - The tab sees an eccentric load, not tension. Pulling the wire rearward
    against a tag behind the contact is in fact eccentric compression.
- **The numbers [calc §4].**
  - The neck's plastic moment is 3.0–5.0 N·mm.
  - The tab yields at a pull of 2.5–14 N, depending on neck width and height.
  - A 20 N proof pull, half of JST's 39.2 N, always bends it.
- **Consequence.** After a proof pull through the tag, the contact is tilted
  relative to the hole, and the tag no longer serves as a datum for insertion.
- **Repair.** Use the tag for pose only.
  - The pull reacts on the box's rear face through a slotted plate that passes
    the barrels but not the box
    ([v1 step 10](../explorers/machine-that-sees-and-learns/ideas/v1-watched-nest.md),
    [v5](../explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md)).
  - The gripper's pin and pad let go during the pull, so the tag moves with
    the contact. They take the tag again afterwards, and the camera checks the
    box tip against the hole once more.
  - **Leaves uncertain:** whether the box's 0.2 mm walls take 20 N on a plate
    edge. That is my own open question in v1.

### Break 2: the hole is a datum for the tag, not for the box tip

- **The conflict.**
  - a2b "aligns it with cavity k from the hole position alone".
  - The box tip sits 5.0–6.5 mm ahead of the hole.
  - Between them are the crimp's bend-up, bend-down and twist, and any set
    the neck took when the carrier was cut.
- **The numbers [calc §4].**
  - 1° of either puts the box tip 0.09–0.11 mm off.
  - 2° puts it 0.17–0.23 mm off.
  - 3° puts it 0.26–0.34 mm off.
  - The cavity entry window is about ±0.2 mm [my calc: arm_and_feeder §1].
- **Consequence.** Pure dead reckoning from the hole works while the crimp is
  within about 2°. Beyond that it depends on a rear-mouth lead-in nobody has
  measured.
- **Repair (a transfer, nearly free).**
  - a2b already poses each crimp for its side and top cameras. The same picture
    measures the box tip's offset from the hole in Y–Z and X–Y.
  - The insertion gripper adds that offset to its approach.
  - This replaces "hole alone" with "hole plus one measured correction per
    contact", which is what Cellios does with its gripper [prior-art §0], here
    against a stamped datum rather than a gripper.
  - **Leaves uncertain:** whether the offset measured at inspection still holds
    at insertion. The neck is compliant, ~59 N·mm/rad [calc §12].
    - A conductor's drape of 0.05–0.1 N at the box moves its tip
      0.02–0.07 mm.
    - 0.5 N moves it 0.21–0.36 mm, the whole cavity window, and the neck
      yields just above that.

    So the sturdier version looks at the box tip once more just before it
    meets the mouth, which is v6's lit-square approach.

### The comb, seen

- **In a comb, every interior crimp has crimped neighbours 7.1 mm away** on
  both sides.
  - The grazing view of Break 4 works across a comb when the neighbours'
    heights match to ~0.1 mm (crimped barrels, ±0.05 [xh-facts §5]).
  - It then reads 3–5 crimp silhouettes in one frame, each on its own blade
    support.
  - So the comb is inspectable in one pose, which makes it a candidate
    [v5](../explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md)
    tray.
- **The comb is also a pallet with its own kinematic datum.**
  - Two pins in two carrier holes, plus the carrier edge on a fence.
  - That is the dock my
    [v2](../explorers/machine-that-sees-and-learns/ideas/v2-arm-taught-by-hand.md)
    arm needs, and here nothing has to be printed onto the ribbon to get it.

### Transfer: find the tags by their holes, on a backlight

- The a2b tags dangle and overlap at the web's 1.7 mm spacing, which is a2b's
  snagging worry.
- On a backlight each unobstructed hole is a bright 1.5 mm disc: 67 px across
  at 45 px/mm.
- A tag lying on top of another shows its full disc. An underneath one shows
  a crescent or nothing.
- So the picture says which tag is free to pick, and the comb finger holds back
  the rest in the order the picture gives.

---

## a2c — the strip gives the hand tool its locator

### Break: a ±90° swing of the strip twists the next contact

- **The conflict.** [a2c](../explorers/terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)
  separates the crimped contact with "a printed finger [that] bends the strip
  down … about ±90° about the tab until it breaks".
  - The tab hinges about an axis along the strip.
  - Swinging the carrier 90° about it rotates the whole strip about its own
    length, and the strip is still held in its track and feed.
- **The numbers [calc §5].**
  - A 90° twist taken up over one pitch (7.1 mm) puts 1,800 MPa of shear in
    the carrier, against ~290 MPa shear yield.
  - Over 30 mm it is 430 MPa. The carrier needs ~50 mm of free length before
    the twist is elastic.
- **Consequence.** The next contact, one pitch upstream, is twisted and rolled
  before it reaches the nest. Several are, if the twist spreads.
- **Repair A.** Hold the handles closed after the ratchet releases, and
  drop-shear against the closed jaw's rear face.
  - The ratchet only releases at full closure, and the actuator can keep
    squeezing.
  - The hardened jaw is then a2's anvil edge.
  - **Changes:** a2c gains a2's drop plate behind the tool.
  - **Leaves uncertain:** whether the SN-2549's jaw rear face is square and
    flush enough to leave a stub inside JST's "not too long" criterion.
- **Repair B.** Cut the carrier at the slot upstream of the station first, then
  bend off the freed tag alone.
  - **Leaves uncertain:** a second small shear and its scrap.

### Seeing inside a hand tool

- After the first ratchet click the wings are inside the upper die. No camera
  sees strands against wing tips from then on.
- a2c's look before the irreversible act is therefore:
  - the stripped tip alone on a backlight, before entry;
  - the insulation edge seen from the wire side as the carriage stops;
  - the actuator current trace, and the after-crimp look.
- A strand riding a wing tip is found only after the crimp. That is acceptable
  for a day-one aid, and it is the reason the booth
  ([v5](../explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md))
  exists.

### The crimp height the tool gives

- "Checks now and then that the tool's jaws still meet the stop" is handed to
  the person.
- v5's silhouette crimp height on every crimp does it continuously:
  - ~2–9 µm repeatability on the stock ELP against a ±50 µm tolerance [my
    calc: vision_budget §3];
  - it also answers the digest's open question, whether the SN-2549's jaws
    bottom face to face, the first afternoon it runs.

---

## a1 — a stock applicator on a slow screw ram

### Uncertainty that decides a1's gate: lines of sight inside an applicator

- **The conflict.**
  - At top dead centre the crimpers are 30–40 mm above the anvil. A
    front-oblique look at the waiting contact is available, and a1 uses it.
  - Along the strip, at wing height, sit the next contact (Break 4 of a2), the
    feed finger, the strip guides and, downstream, the shear and scrap path.
  - No public drawing of the OTP applicator shows whether any line along X at
    wing height reaches a backlight.
- **Consequence.**
  - If none does, a1's pre-stroke look is limited to the front-oblique view:
    insulation edge in the window, contact present.
  - A strand riding a wing tip then shows only after the crimp.
- **Repair.**
  - Move the strand check upstream: the stripped tip on a backlight before the
    carriage enters, as in v1 step 4.
  - Accept that the stroke's gate in a1 is weaker than on an open nest.
  - A photograph of the applicator from the side at anvil height, the day it
    arrives, settles whether a vane can reach the gap.

### Transfer: run the crimp-height campaign on the applicator's own die

- a1's largest unknown is "what the OTP die does on 60 × 0.08 mm strands and
  1.7 mm silicone".
- [v3](../explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
  answers exactly that in one night: ~150 crimps, ~$2 of contacts, ~1.2 m of
  5P, each crimp photographed and pulled to failure.
- a1's hard stop, local to the applicator, becomes v3's settable stop by
  putting it on a stepper-driven wedge.
  - It sweeps shut height in 0.02 mm steps, finer than a crimp dial's
    graduation (~0.05 mm on the MKS-L [mfr MKS-L §5]; the OTP dial is
    unknown).
  - Genuine SXH and clone reels can both go through the same die.
- **Changes:** a1's "measured on arrival" becomes "measured on arrival, then
  swept".
- **Leaves uncertain:**
  - shut height moves both barrels together, so the insulation crimp is swept
    by the dials by hand;
  - whether a1's spring overtravel stack masks a stop that is set too high.
    The ram indicator and force trace show that.

### Wire stop or insulation edge

- An applicator's axial reference for the wire is the operator's wire stop,
  which the strand tip touches [prior-art §3].
- On torn silicone the insulation edge then lands wherever the tear put it,
  ±0.2 mm or so [estimate].
- a1's carriage has no wire stop and a camera, so it can reference the
  insulation edge instead, or split the error between brush and window.
- That choice exists only because the machine sees both edges.

---

## a3 — loose contacts hang on a slotted rail

### Transfer: read the U from below, and make the rail edges black

- The camera "looks straight down into the insulation U". But the contact's
  wings rest on steel rail edges: silver on silver.
- **Two cheap fixes.**
  - **Black the rail edges** (black oxide, or a black printed cap on the
    ground edge).
  - **Light from below through the slot.** The hanging contact's outline is
    then the box's rectangle inside the insulation U. Light passes only between
    the wing tips, on the open side.
- **The numbers [calc §11].** That notch is 0.40–1.00 mm deep: 18–45 px on the
  stock ELP.
- **What else the same silhouette shows.**
  - A tangled pair appears as two outlines, or a doubled wall.
  - A bent wing shows as an asymmetric notch.
  - All of these go back to the hopper, not on to the station.

### Transfer: measure the heads by the dozen, not one by caliper

- a3's feasibility turns on whether the kit contacts have a head: open wings
  wider than 2.4 mm, against a box that passes 2.05 mm.
- a3 asks for one kit contact under a caliper. One caliper reading does not
  give the spread of a bag.
- Twenty kit contacts poured on [v4](../explorers/machine-that-sees-and-learns/ideas/v4-tap-look-pick.md)'s
  light pad and photographed once give a distribution:
  - every open-wing width and box width, to ~0.02 mm at 45 px/mm;
  - the pose odds v4 needs, from the same pictures.
- The slot widths (2.05 and 2.4 mm) can then be set from the tail of that
  distribution, not from clone drawings.

### Jams as a look-act-decide loop

- "Clears the occasional jam" is handed to the person.
- **The machine's first answer:** no contact reaches the escapement's
  photo-interrupter within N seconds, or the camera sees a contact riding high
  at the wiper. Then:
  - reverse the vibration;
  - run one extra brush pass;
  - look again.
- **Only then does it ask**, with a photo.
- The tangle and jam rate, a3's unknown, is counted by the same log from the
  first day.

---

## a3b — crimp it where it hangs

### Break 1: the punch travels along the rail

- **The conflict.**
  - A contact hangs with its wings across the slot, so its U opens fore or aft
    along the rail [terminal-supply calc §6].
  - The punch must close the wings, so it moves along the rail axis.
  - The pocket's back wall, which carries the crimp force, is on the other side
    of the contact along the same axis.
  - One of them, punch or wall, therefore sits across the line the contact
    arrived along. Either the contact cannot enter, or the punch comes through
    the rail.
- **Repair A: a shuttle anvil.**
  - The back wall is a steel slide that closes behind the contact after it
    enters, and seats against a fixed abutment. The punch comes from
    downstream.
  - **Changes:** the shuttle carries 0.8–2.6 kN and is the anvil, so its
    seating repeatability enters the crimp height directly. The hard stop must
    reference the abutment, not the slide.
  - **Leaves uncertain:** seating to ~0.01 mm, cycle after cycle.
- **Repair B: the end pocket is the turn pocket.**
  - The pocket turns 90° or 270° about the contact's own axis. The camera,
    looking down the U, picks which, so the upstream 180° turn pocket
    disappears.
  - The U then faces across the rail. The punch comes across, and the fixed
    steel wall sits beside the rail's line, out of it.
  - The rotating part only locates. The force goes from the contact's floor
    into the fixed wall.
  - **Leaves uncertain:** that the contact stays hanging on the pocket's own
    edges through the turn, and that the floor meets the wall squarely. The
    punch's first touch pushes it there.

### Break 2: nothing holds the conductor inside the U

- **The conflict.**
  - Conductor k comes down along the contact's axis.
  - The U opens sideways, toward the punch, and has no wall on that side.
  - Nothing pushes the bundle toward the floor. The strands can hang past the
    wing tips on the punch side.
  - Then the punch closes the wings onto them: the "strands outside the
    barrel" fault [xh-facts §5], made by the geometry.
- **Repair (transfer).**
  - v1's hold-down finger, turned 90°, presses the insulation toward the floor
    before the punch moves.
  - A look from above and in front, on the punch side, before the punch
    arrives, sees strands against wing tips: the view v1's gate uses, rotated.
  - **Leaves uncertain:** the pocket's side walls, which hold the contact
    square, block a lateral silhouette unless they stop below the conductor
    barrel or have a window.

### Break 3: the ribbon's other conductors hang beside the pocket

- Hanging vertically, they sit either over the rail and its waiting contacts,
  or in the punch's path, or behind the wall. It depends on how the ribbon's
  plane is turned.
- **Repair.** Fold the other conductors back up along the ribbon and clip them
  there. This is easier with a vertical ribbon than with a flat one. It is the
  same out-of-plane requirement as a2's Break 1.

---

## a4 — hold the contact by mating it on a post

### Break: a nozzle cannot load a post

- **The conflict.**
  - a4 hands loading to Derek (3–5 min a unit) or to a3's rail.
  - The obvious machine loader is a vacuum pick, my
    [v4](../explorers/machine-that-sees-and-learns/ideas/v4-tap-look-pick.md).
  - A 1.0 mm nozzle at 80 kPa holds 63 mN normal and ~19 mN sideways
    [calc §7]. Mating onto a post takes 200–2,000 mN
    [terminal-supply calc §7].
- **Consequence.** The nozzle lets go and the contact stays on the post's tip,
  or skews. terminal-supply parked vacuum pick because a post also locates and
  holds. The forces say the two are not alternatives but a sequence: the
  nozzle places, the post holds.
- **Repair (a combination; see C2 below).**
  - The nozzle only places the contact in a **loading nest**. The nest has a
    front stop with a hole for the post and a rear stop at the insulation
    barrel's edge.
  - The turret's post comes through the hole and spears the box, with the rear
    stop reacting.
  - The camera confirms U-up on the post before the turret moves on.
  - **Changes:** the person pours contacts. The machine builds the magazine in
    recipe order, with an empty post for J2's cavity 3.
  - **Leaves uncertain:**
    - post entry into a clone box whose entry is 0.60–0.70 mm, from a nest
      the nozzle filled to ±0.05 mm;
    - grip scatter.

  A branch spears straight from the tray. A backstop finger drops behind a
  barrels-up contact the camera found, and the post approaches along that
  contact's heading.

### The release check and a real proof pull

- a4's slide-off at 0.2–2 N is a check that the crimp gripped at all. It is
  1–5 % of JST's 39.2 N.
- A fork swung in behind the box, between the box and the conductor barrel,
  lets the carriage proof-pull to ~20 N against the box while the camera
  watches the insulation edge for slip (v1 step 10).
- On a turret there is room for the fork beside the station.
- **Leaves uncertain:** the same box-wall question as v1.

### Continuity through the post says joined or open, and needs a bared far end

- The conductor is 58 mΩ per metre: 6–35 mΩ over a loom, 0.9 Ω over a whole
  50 ft spool.
- A good crimp is ~0.2–1 mΩ. The post-to-box contact at 0.2–2 N grip is
  ~5–30 mΩ, and variable [estimates, calc §10].
- The check therefore separates open from joined and cannot grade a crimp.
- It also needs the far end bared, through a pogo pin on the cut face or the
  spool's slip ring (the digest's "far end as an electrode array").

### Seeing U-up on the post

- From above, U-up shows two wing tips and the open U. U-down shows the flat
  floor and the lance: distinct at any resolution in the budget.
- A turret whose post sockets turn 180° under a servo corrects U-down instead
  of skipping it.

---

## a4b — the post goes through the housing first

### Transfer: the lit cavity is the test of a4b's premise

- a4b's first unknown is whether a 0.64 mm post passes straight through a
  cavity, from the front post opening to the rear.
- My [v6](../explorers/machine-that-sees-and-learns/ideas/v6-patient-cell.md)
  lights the housing from under its mating face and finds each empty cavity as
  a bright square seen from the rear.
- **That bright square is a straight line of sight along the cavity's axis.**
  - Its size and position, seen square-on, give the clear aperture along the
    axis and its offset from the rear mouth.
  - If the square is at least 0.64 mm plus clearance, the post passes.
- One phone photograph with a flashlight behind an XHP-4 answers a4b's
  question, and v6's premise that the white PA 6 passes light, together.
- **In the machine,** the same square guides the post in. Its going dark, after
  the post withdraws, is the seat check (below).

### Repair: a post the box drags, instead of a second synchronised axis

- a4b retracts the post "in step" with the fork, to keep its tip ~2.5 mm inside
  the box.
- **Branch.** The post slides freely in a low-friction guide, and the box's
  grip carries it forward. The grip is 0.2–2 N against guide friction of
  ~0.01–0.05 N [estimate].
  - A flag on the post's rear end, seen by the camera or a switch, confirms
    the post travelled with the box.
  - **Changes:** the post needs no drive during the push; only the withdrawal
    is driven.
  - **Leaves uncertain:** that the post is not held back by the cavity walls
    it runs through.
- The driven version is also easy. Two steppers on one controller making a
  coordinated move is what a printer board does all day (v1b).

### Seat check by light

- Before insertion, with the post in, the cavity is mostly dark: the post
  fills the opening.
- After the post withdraws out of the front:
  - a seated contact's box sits behind the post opening, so the square
    stays dark;
  - if the contact came out with the post, the square is lit again.
- The picture and a4b's pull-back check each confirm the other.

---

## a5 — the housing is the fixture

### Break: the staged box pivots in the cavity mouth

- **The conflict.**
  - The bare contact is 1.5 mm into the mouth, and the barrels stand out
    behind.
  - Any clearance between box and cavity is a pivot.
  - The anvil "rises under the barrels right behind the rear face".
- **The numbers [calc §8].**
  - At 1.5 mm engagement, 0.05–0.10 mm of clearance a side lets the contact
    tilt ±3.8–7.6°.
  - The conductor barrel's centre, ~1.8 mm out, can sit ±0.12–0.24 mm off the
    anvil's height.
  - At 1.0 mm engagement the barrel can sit up to ±0.46 mm off.
- **Consequence.** An anvil rising to a fixed height either lifts the barrels
  and bends the transition against the box held in the mouth, or leaves a gap
  the punch closes by bending. Either way it is bend-up or bend-down, a JST
  shape fault [xh-facts §5].
- **Repair (transfer).** Measure every staged contact and set the anvil's Z
  per cavity, not once per housing lot.
  - A side look along the row, from the empty side, sees the staged contact's
    floor against the anvil.
  - The done side's swept wires are black silicone, a free dark background
    for a front-lit silver contact.
  - The gate before the stroke requires the contact's axis to match the
    cavity's axis within a threshold.
  - **Leaves uncertain:** the clearance itself. One kit contact in one kit
    housing, photographed from the side at 1.5 mm, shows it.
- **Related.** [force-and-form's exchange on into-the-housing](force-and-form--on--into-the-housing.md)
  finds the lance tip over the anvil's front edge when crimping at a cavity
  mouth. a5's staging at 1.5 mm puts the lance tip 0.94 mm outside the face,
  which is the same neighbourhood.

### Staging without a hand: gravity, and the front post as a depth stop

- A nozzle cannot push a box into a mouth against any friction (calc §7).
- **a5's own "rear face up" note, taken further.**
  - The housing lies rear face up.
  - The contact arrives box-down: exactly the pose a3's rail delivers, or
    that a hanging plate holds (C3 below).
  - It drops into the mouth under its own weight.
- **The problem.** It then slides until the lance tip meets the rear face at
  ~2.4 mm depth [xh-facts §1]. That leaves the conductor barrel only ~0.2–1.6 mm
  from the face.
- **The repair, look-act-look.**
  - A short post from the front, through the post opening, stands where the
    box's spring leaves should first touch it. The box stops there.
  - The camera measures the staged depth from the side.
  - The post's stage moves by the error, and the camera looks again.
- **Leaves uncertain:** where inside the box the leaves first touch a post.
  Nobody has measured it, and the camera finds out on the first contact.

### Checking the person's staging

- When Derek stages by hand at the lit cavity, the machine runs the same look
  on his placement as on its own: depth, tilt, and the right cavity by the
  recipe.
- It proceeds only after that look. The person becomes one station among
  several, with the same gate, and a mis-staged contact is caught before the
  stroke rather than by the tester.

---

## Across all of terminal-supply

### What each supply form lets the camera see before the stroke

| Look before the stroke | a1 applicator | a2 strip indexer | a2c hand tool + strip | a3b hanging pocket | a4 post turret | a5 housing mouth |
|---|---|---|---|---|---|---|
| Stripped tip alone on a backlight | anywhere upstream | anywhere upstream | anywhere upstream | anywhere upstream | anywhere upstream | anywhere upstream |
| Waiting contact: present, roll, wings, lance | front-oblique, crowded by plates | from above; roll by grazing view | only before the first click | down the U, if the pocket is blackened | from above, clear | from the empty side, against black wires |
| Insulation edge in the window | front-oblique | from above | from the wire side | from above and in front | from above | from above |
| Strands against wing tips, in silhouette | unknown until the applicator is on the bench | grazing view if the wings match to ~0.15 mm; vane otherwise [calc §1] | hidden | punch side, before the punch; the side walls block it | along the rim's tangent; neighbouring posts curve away | along the row from the empty side |
| After-crimp silhouette and proof pull | after the carriage lifts it out | same | same | after it lifts out | with a fork behind the box | one look before the push; no crimp proof pull once seated |

The supply form decides the camera's lines of sight as much as it decides the
feeder. a4b and a5 give up the per-crimp proof pull once the contact is in its
cavity: a pull then tests the lance, not the crimp. There, v3's destructive
re-check coupons carry the pull strength by sample.

### Back-out, by supply form

| Supply | A contact rejected before the wire | A crimp rejected after the stroke |
|---|---|---|
| Strip (a1, a2, a2c) | index past it; the downstream path must clear an uncut contact | stop the end, queue a cut-back |
| Comb (a2b) | as strip | the whole comb segment is scrap; stop the end |
| Rail (a3, a3b) | back to the hopper | stop the end |
| Post turret (a4) | skip the post, or turn it 180° | stop the end; the rest of the magazine waits |
| Housing (a4b, a5) | withdraw the post or unstage the contact | the crimp is still outside the cavity (on a4b's post tip, at a5's mouth): draw it back out with its conductor, stop the end, queue a cut-back. A fault found only at the seat check means extraction with an XJ-06-style pin, and an ask |

### Stop reached is not crimp height

- Every terminal-supply arrangement's "how it knows" is a proxy:
  - pins home;
  - ram at the stop;
  - a force trace;
  - a look at brush and window.
- The stop is where the tooling was, not what the crimp became. Die wear, a
  knife set seating differently in its holder, and a new contact lot all move
  crimp height with the stop unchanged.
- The silhouette height on each crimp, and v3's periodic pulls to failure,
  close that loop.
- With a2's knife set in a printed or simple steel holder, a2's own most
  serious open problem, this is how the holder's alignment is watched in
  service.

---

## Combinations

- **C1. The watched strip station (a2 + v1 + v3).**
  - *a2 gives:* the contact located by pins without touching it, the
    drop-shear, and the supply.
  - *v1 gives:*
    - the conductor steered by the insulation edge as seen;
    - the per-slot lifter and the neighbour check;
    - the grazing silhouette or vane;
    - the after-crimp silhouette and proof pull.
  - *v3 gives:*
    - a stepper wedge under a2's hard stop, so the anvil block becomes a
      settable-stop press;
    - one night's sweep of the OTP knife set on this ribbon.
  - The strip in turn makes v3's campaign cleaner: 100 identical contacts in
    identical pose for $4.71, so contact placement drops out as a variable.
- **C2. The machine-loaded post magazine (a4 + v4).**
  - The v4 tray finds a barrels-up contact, and the nozzle drops it into a
    loading nest.
  - The turret's post spears it through the nest's front stop.
  - The camera confirms U-up, and the recipe fills posts in loom order.
  - *a4 gives:* the holding, the release, and the magazine as the build list.
  - *v4 gives:* singulation and loading without hands.
- **C3. The hanging plate (a3's slot geometry + v4b's plate + a4 from below).**
  - A static plate of stepped through-slots, 2.05 mm at the box and 2.4 mm at
    the barrels, filled by tapping or brushing as v4b fills its channels.
  - A backlight under it shows each hanging contact's U direction by its
    notch [calc §11].
  - A post on an X–Y stage under the plate rises into the chosen box and turns
    180° if needed.
  - It removes a3's vibrating rail, escapement and turn pocket.
  - *Leaves uncertain:*
    - whether a contact lying on a flat plate finds a slot and tips box-first
      into it;
    - a3's head question, which applies unchanged.
- **C4. Lit cavity, through-post and staged contact (v6 + a4b + a5).**
  - The camera finds cavity k by its square and checks the axis is clear.
  - The post goes through.
  - The contact is staged box-down by gravity onto the post's tip, and its
    depth is corrected by the post under the camera.
  - The crimp is made at the mouth, with the anvil Z set per cavity.
  - The push follows, and the square stays dark after the post withdraws.
- **C5. The tag as the booth's datum (a2b + v5).**
  - The tag's hole goes on a pin for pose, and the camera measures the box tip
    against the hole.
  - The slotted plate carries the pull.
  - The insertion gripper receives the measured offset.
- **C6. Applicator and campaign (a1 + v3).** As in a1 above: a stepper wedge as
  the hard stop, and the sweep on the actual production die.
- **C7. The first week's bench (a2c's clip + v5).**
  - Hand crimps located by the clip on a Digi-Key strip.
  - Each is dropped in the booth, measured, proof-pulled and logged.
  - Nothing moves under motor power yet. Placement is repeatable because of
    the strip, and every crimp is measured because of the booth.
- **C8. The comb as a pallet for an arm (a2b + v2).**
  - The carrier holes give the dock its pins, so the arm's 1–2 mm slop is
    taken out by holes the stamping die already made.
  - The comb is inspectable in one frame by the grazing view.

---

## What their view has not yet seen

- **The conductor's position is a picture's job, not a carriage's.**
  terminal-supply's references are all for the contact: pins, posts, pocket
  edges, cavities. The conductor arrives at "a taught position".
  - The fan shortfall is 0.3–1.9 mm [calc §3].
  - The strip-length disagreement is 1.6–2.4 mm, and silicone tears.
  - Both sit inside a 0.5–1.0 mm window, so each conductor's Y comes from its
    own insulation edge as seen.
- **The supply form sets the lines of sight**, as in the table above. The strip
  puts an identical part one pitch from the view. The hand tool and the
  applicator hide the wings. The hanging pocket's walls block the silhouette.
- **The ribbon's other conductors** meet the fresh contacts on a strip, the
  rail beside a hanging pocket, and the dies at a housing. No flat fan clears a
  4P or 5P [calc §2].
- **Back-out is different for each supply form,** and the strip's
  "index past" needs a downstream path nobody has drawn yet.
- **A proxy of the tooling is not a measurement of the crimp.**
- **Hand-backs the machine could take:**

  | Handed back | How the machine could take it |
  |---|---|
  | a4's post loading, 3–5 min a unit | C2 |
  | a5's staging at a lit cavity | C4, or at least a gate on the person's staging |
  | a3's jam clearing | look, reverse vibration, extra brush pass, then ask |
  | a3's check of "which contacts have heads" | one photograph of twenty on a light pad |
  | a2's per-reel re-teach | a per-contact picture and a fence stepper |
  | a2c's "check the jaws still meet the stop" | a silhouette crimp height on every crimp |
  | a4b/a5's housing load and final continuity | v6's housing nest and v5's wafer-board tester |
  | Splay and strip, handed to other views everywhere | v6's split, twist and strip stations, each bracketed by a look, with the tip as seen as the reference for where the stripper lands |

---

## Four photographs that settle several of these questions

Each is a question for Derek, and none blocks the ideas above.

1. **An XHP-4 held against a flashlight, photographed square-on from the rear
   face.** It shows whether a straight line runs through each cavity (a4b's
   premise), how big it is, and whether white PA 6 lights up for v6.
2. **Twenty kit contacts poured on a light pad, one photograph from above.** It
   gives the spread of open-wing and box widths (a3's head question, the slot
   widths), and the pose odds v4 needs.
3. **A Digi-Key 100-piece strip, photographed from the side along the strip at
   wing height, with a light behind.** It shows how closely neighbouring wing
   heights match (the grazing view, calc §1), whether the strip arrives bent
   from its bag, and the carrier pitch.
4. **One kit contact pushed 1.5 mm into a kit housing's rear mouth,
   photographed from the side, then nudged up and down with a needle.** The
   pivot it allows is a5's clearance (calc §8).

---

## Where their work changes my own ideas

- **v1 step 11 (a servo flush cutter trims the tab after the crimp) conflicts
  with a2's geometry.**
  - The wire's insulation lies on the tab and the carrier, and no jaw fits
    between them.
  - For strip contacts, the tab is cut during the stroke by a drop-shear, as in
    a2, or the carrier is kept as a2b's tag.
  - Step 11 remains only for a contact whose tab has already been lifted clear
    of the wire.
- **v1's camera 2 (across the nest, at wing height)** assumed nothing stands
  beside the nest. With strip supply it becomes a2's grazing view, θ at most
  ~1.4°, or the vane [calc §1]. The anvil block and drop plate must leave that
  line clear.
- **v1's fan-comb at 5.5 mm pitch in the strip's plane** would lay conductors 1,
  3 and 4 onto fresh strip contacts [calc §2]. With a strip, the pallet needs
  a lifter for each slot.
- **v1's "the camera doesn't care where the contact comes from"** is true for
  the look and false for the fixture. The supply form sets:
  - the wire's approach, over the carrier from behind;
  - how the tab is cut;
  - the neighbour lift;
  - the camera's lines.

  The nest differs for each supply form.
- **v4's nozzle** can place into an open nest and nothing more (calc §7). To feed
  a4's posts it needs a loading nest (C2), and to stage into a5's cavities it
  needs gravity and a post (C4).
- **v4b's channel is 1.95 mm at the floor.** terminal-supply's slot calc (box
  1.85 ± 0.10) shows that width has no margin for a large box. It wants
  ≥2.05 mm, flaring above so the wings clear. a3's hanging geometry is a
  branch of v4b (C3).
- **v6's insertion station** (slide-along jaws pushing a crimped contact on a
  floppy conductor) sits beside three other mechanisms:
  - a2b's tag handle;
  - a4b's through-post;
  - a5's contact staged before the crimp.

  a5 changes v6's station order: the housing comes before the crimp, and crimp
  and insert happen at one place. v6's lit square is also the test of a4b's
  premise.
- **v3 has to run per supply form.**
  - Genuine SXH on strip in a knife set, and kit contacts on posts or from a
    rail, are different contact-and-die pairs. a3 finds they may not even
    share a shape (a head or none).
  - a2's anvil block with a wedge stop is a concrete v3 press.
  - a4's posts on the same anvil let one campaign compare genuine strip with
    kit loose contacts.
- **v5 gains the tag hole as a pose datum** (C5). It records supply form and
  lot per crimp.
- **The queue (v6) needs a back-out vocabulary for each supply form**, as in
  the table above.
