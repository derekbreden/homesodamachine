# Notebook: procedure-is-the-machine

Running log, directions set aside, and open questions.

## Log

- **Read the brief, shared context, working method, xh-facts and prior-art.**
  Then the repo sources behind the loom table:
  - `hardware/assembly/cable-assemblies.md`;
  - `hardware/wiring/ac-wiring-schedule.md` (LEN_* figures);
  - `hardware/wiring/_run_lengths.py` (J3 not measured);
  - `hardware/pcb/pcba/pcba.tsx` (wafer pin orders);
  - `hardware/ledger/labor.md`.
- **Pin orders from pcba.tsx:**
  - J1 = OUT8…OUT1, COM (straight for a 5 | 4 split);
  - J2 = COM, FAN, OUT4, OUT3, OUT2, OUT1 (OUT4 empty);
  - J4 = 3V3, GND, V5, IO25, IO26, IO27, IO23;
  - J7 = RB1–RB4, CLO, CHI, GND.

  With the ribbon assignments in cable-assemblies.md, J4 and J7 are not in
  ribbon order: J4's 3P GND must reach pin 2, and J7's 5P GND must reach pin 7
  past CLO/CHI. into-the-housing found the same (handover.md,
  calc/insertion_geometry). Here it matters for which arrangements the
  machine can finish alone.
- **Unit inventory** [calc/unit_inventory.out.txt]:
  - 14 ends, 53 crimps, 10 housings;
  - 6 single-ribbon housings (25 crimps) and 4 pairs (28 crimps);
  - 5 of 10 housings are 4P → XHP-4 (20 crimps, 38%);
  - ~6.0 m of ribbon per unit;
  - spool lives of ~5.4 (4P), ~8 (3P), ~11 (5P) units.
- **Recovery** [calc/recovery_length.out.txt]:
  - a whole-end redo cuts back 4.5–6.7 mm;
  - cut-first orders need a length allowance per loom, and scrap looms past
    it;
  - cut-last makes redo cost spool only.

  This is the strongest single consequence of order found.
- **Geometry of order** [calc/selector_and_bow.out.txt]:
  - selecting one conductor at 2.5 mm pitch needs ~6–10 mm of out-of-plane
    separation for real tooling;
  - fanning wider for crimping builds in a length error unless trimmed in the
    converged pose;
  - per-conductor insertion with the ribbon clamped needs an 8–11 mm bow per
    conductor, and gang insertion needs none.
- **Transfers** [calc/transfer_capture.out.txt]: every transfer from a person
  to a carousel to a hobby arm lands inside a dowel or V-groove lead-in. The
  axial chain (insulation edge in the window) is the tight one, dominated by
  strip-length scatter and the split point.
- **Camshaft** [calc/cam_drive.out.txt]:
  - a NEMA 17 through a 30:1 worm and a 2.5 mm eccentric gives 3.4–4.9 kN
    through the compaction zone;
  - the frame (≥15–30 kN/mm) and the over-travel hazard at bottom dead centre
    are the limits.
- **Person's minutes** [calc/person_timeline.out.txt]: a person-paced station
  saves no minutes; loading an end's worth at once does. The absolute minutes
  are probably high: the same task estimates give 46 min for the XH work alone,
  against the ledger's 45 min for everything. Compare rows only.
- **Sourcing.**
  - Web search was already exhausted for this session when this explorer
    started; direct page fetches worked for Adafruit, BIQU and Pololu.
  - StepperOnline returned 403.
  - Findchips had no B9B-XH-A result.
  - Commodity parts went to sourcing-requests.md for the Prime pass.
- **summary.md was not written.** The harness refuses summary files from this
  subagent. The summary (arrangements, findings, transferable mechanisms,
  questions) went back to the coordinator in the structured return, and the
  questions are also below.
- **Convergences seen in other explorers' directories** (read after my own
  arrangements were sketched):
  - ribbon-as-pallet a4 (spool as magazine) ≈ p3;
  - into-the-housing's crossing analysis ≈ my pin-order reading.

  Each file cross-references where useful.

## Log, wave 2

- **Read** hand-tool-as-press's critique of this view
  ([`../../exchange/hand-tool-as-press--on--procedure-is-the-machine.md`](../../exchange/hand-tool-as-press--on--procedure-is-the-machine.md)),
  every explorer's summary, the digest, and the first wave-2 files appearing
  in other directories:
  - hand-tool-as-press a6 (foot-closed jig bench);
  - borrowed-machines b2b (C2 developed as a station);
  - terminal-supply x1 (post feeds the hand tool);
  - ribbon-as-pallet a7 and a8 (zip station, rolling ring scorer).
- **What the critique broke, and what happened to each break:**
  - **p1-1, presser over strip hardware.** My own exchange calc §1 had found
    it. Agreed. p1's bench B now stands in two forms: B-drop keeps the
    presser only with the contact cut free before a tall fin anvil, and
    B-lift is the new branch p1c.
  - **p1-2, set in waiting conductors.** Agreed and recomputed with a
    closed-form elastic-plastic strand model [calc wave2 §1]. It matches
    hand-tool-as-press's calc H §1 within its range. It led to the order rule
    "lift once, do everything to *k* in that pose" (p1c).
  - **p1-3 and p5-1, fork on the tab line through the stroke.** Agreed. The
    fork moves back 5–6 mm and releases at 150–170°, and a wire-hold leaf on the
    punch stack takes over (p1, p5).
  - **p1-4, axial chain missing the contact's reference.** Agreed. Added, and
    the camera bare-length correction brings the chain to ±0.07–0.09 mm RSS
    [calc wave2 §3].
  - **p2-1 and p2-2, crimp exit and head depth.** Agreed. The head stands in two
    forms: C with a parting lead-in, and T tip-down.
  - **p4-1, proof pull through the dies.** Agreed; my wave-1 text was wrong.
  - **p4-2, lead-in and shuttle on the carrier.** Partly disagreed. The carrier
    being the lead-in's floor is how every side-feed applicator is fed. It is
    flat, in the barrel floor plane, and the strands enter 0.5 mm above the
    barrel floor inside a 1.5 mm open U. What the strip form needs is an
    upward exit after the shear. Kept, with the squeezer form beside it.
  - **p5-2, crimp height at bottom dead centre.** Agreed. The stop blocks and
    disc-spring stack are now in p5, and stiffness becomes a torque question.
- **Combinations developed as files:**
  - C2 → p4b (two heads);
  - C3 → p5b (camshaft squeezes the SN-2549);
  - R1 with a3 → p1c;
  - C1 → p3 step 4 and p6 stage 2.
- **New direction: p6, the spool-end bench that grows.**
  - The coordinator suggested an incremental path. From this view the path
    follows the order: terminate first, cut last, done by hand at a reel
    clamp with no motor. Motors join in the order Derek wants work taken
    away, the crimp first.
  - Two things fell out of it:
    - the flying lead to the hub never twists if it is plugged only while
      the reel stands still, so no slip ring is needed until the draw-off is
      powered;
    - a puller drawing the ribbon by a clip behind the housing replaces p3's
      push-out down a drop tube.
- **Second new direction: p7, strip before split.** This revives wave-1
  direction 6. Straight razor blades, stopped on steel, are insensitive to
  pitch error. That is what makes the whole-end strip practical [calc wave2
  §7].
- **Spool curl** [calc wave2 §2]. An issue nobody had raised.
  - Copper wound below a ~40–80 mm radius keeps a set.
  - Off a 25 mm hub radius, a 40 mm free end rises 3–15 mm.
  - A rewind reel with an 80 mm hub radius adds none, and a roller
    straightener removes what is there.
  - It matters to every spool arrangement (p3, p3b, p6, c5, ribbon-as-pallet
    a4) and to any cut ribbon taken from the inner turns.
- **Two heads** [calc wave2 §4]. The person's pace sets the rhythm for any
  head cycle up to ~2× the present-and-insert time, so the attended minutes
  are 28–39 against ~46 by hand. This overturns p4's "saves no minutes" for the
  two-head case only.
- **The stage table in p6** [calc wave2 §6]. Stages 0–1 cost minutes (51,
  61) and buy recovery, testing and a record. The minutes fall from stage 2
  (40, 33, 24, 15). Costs are rough.
- **Sourcing.** Web search was used up this wave, and no pages were fetched.
  New sources are cited from other explorers' fetched findings (named in each
  file). Amazon items went to sourcing-requests.md.

## Log, exchange on ribbon-as-pallet

Written to [`../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md`](../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md);
numbers in [`calc/exchange_ribbon_w3.out.txt`](calc/exchange_ribbon_w3.out.txt).

- **My tip-down module rolls every crimp 90°** on a flat cassette or clamp
  (p1c, p5b, p6 stages 1–4, C1). into-the-housing found it on
  hand-tool-as-press a3 (its exchange calc §8). ribbon-as-pallet a6's rule,
  floor-down on one anvil with the ribbon never turned over, is the correct
  one. The routes are the on-edge cassette, docking (X1 in the exchange), or
  p4/p4b's single-conductor funnel set to the right roll.
- **p7 meets docking only through an equal-path fan.** ribbon-as-pallet
  rejected staggered-length grooves unless a station needs tips on a line
  before the fan; p7 is that station. Humps: under 1 mm at 2.5 mm pitch,
  1.7–3.2 mm at 5 mm, 2.6–5.1 mm at 7.1 mm.
- **p7's "single ribbons inside ±0.3 mm" is shape-dependent**: 0.09–0.16 mm for
  a fan spread over the split, 0.31 mm for a 5P in a compact R 5 / 30° S.
- **With the feed removed, a2e's stroke only has to clear open wings**, so p5's
  short eccentric (3–4 mm) fits under it at ~1.0–1.7 N·m.
- **A pilot in the carrier's slot**, in the removed shear punch's pocket,
  clears both neighbouring conductors by ~2.1 mm at 7.1 mm pitch.

## Log, final pass

Read force-and-form's reading of this view
([`../../exchange/force-and-form--on--procedure-is-the-machine-w3.md`](../../exchange/force-and-form--on--procedure-is-the-machine-w3.md))
and its calc output. Numbers for this pass are in
[`calc/wave3.out.txt`](calc/wave3.out.txt); `calc/wave2.py` was re-run so its
stored output matches the idea files (the p6 stage table and a duplicated
fragment at the end of §7 were stale), and the stage-2 label in it names the
post revolver.

What each point did to the ideas:
- **Rolled crimps (their B1).** Agreed on geometry: an SN tool's nest axis is
  normal to its jaw plane, so its closing direction is the contact's floor
  normal. Hung tip-down over a flat row it closes along the row and rolls every
  crimp 90°. Every SN head in this view now lies on its side (jaws closing
  normal to the row, anvil half underneath), or the row stands on edge
  (hand-tool-as-press a3's fixture). The lift becomes *a* + 2.7 = 8.7–14.7 mm,
  which leaves 0–8.2 mm of rise at 30 mm free [calc wave3 §1]: p1c, p2 head T,
  p3's station, p5b and p6 stage 1-SN all ask for a 30–35 mm split and a
  squaring push each crimp.
- **FP1 developed as [p1d](ideas/p1d-lift-once-fin-from-below.md).** A fin rising
  from below through *k*'s own slot needs 3.5 mm of lift and makes an upright
  crimp. Checked their clearances with my own geometry (0.56–1.42 mm a side,
  same as theirs) and found one thing to add: the tip comb has to stand ≥ ~4.7 mm
  behind the tip line, or its pins collide with the fin's insulation step
  (half-gap 0.93 mm against a 0.94 mm half-width) [calc wave3 §2]. Fin travel
  comes out ~4.8 mm with my heights (theirs 4.3 mm; the difference is where rest
  is measured from). Order within an end: odd keys first, then even.
- **FP2 developed as [p5c](ideas/p5c-camshaft-turns-a-knee.md).** The knee lobe
  goes through straight, so the printed lobe's error does not reach crimp height
  [calc wave3 §3]. Added the systematic fan-recession term to its fixed-depth
  chain.
- **FP3 and X1 together as [p6b](ideas/p6b-reel-end-docks-on-a-strip.md).** Both
  put a bought applicator at the reel after p7's strip; X1 docks every contact
  at once through an equal-path fan, FP3 (force-and-form f2c) presents one
  conductor at a time. p6b holds X1 as its picture and f2c as its branch.
- **FP4 and FP5** went into p7 ("where it fits") and p6 (stages 0–1 as the
  qualification rig).
- **Capture at the first tooth (B2).** Agreed. Every SN head closes only to wing
  touch before the conductor enters; p1d puts the contact on the conductor first
  and closes the tool once.
- **Two stops on one axis (B3).** Agreed. With camera depth, identity comes from
  copper touched anyway: the grounded trim blade, the tool at the end of the
  curl, a grounded tip stop at presentation (p4b), or the fin at lay-in (B-drop).
  Touch-off depth (p6 stage 1) keeps depth and identity on the same touch.
- **Stops and surplus (B4).** Agreed, and reproduced in closed form: frame load at
  bottom = F + k m, a doubled contact meets F + k (m + 0.2) [calc wave3 §4]. p5
  drops the preloaded stack; its outer loop is allowed to be soft; the load cell
  sits under the whole lower die. The claim that applicators set height "on
  dials" as a different principle is removed: both are positions; the
  difference is dead stop against kinematic bottom.
- **Ratchet lock-up (B5).** Agreed. p5b reads a pawl switch at 250–255° and the
  shaft stops by angle; the pawl-out branch (a1b) is named.
- **Slug push through cut caps (B6).** Agreed, and extended: pads that squeeze
  also press the jacket onto the strands, so the net drive is 2 N (μ_pad − μ_js).
  Smooth pads need 32–132 N a side on a 5P; toothed pads 6–25 N [calc wave3 §5].
  p7 now slices, pushes through toothed pads, and has a split floor.
- **Proof-pull reaction (B7).** Agreed: every clamp that reacts a pull has a hard
  stop setting a 15–30 % squeeze; at a reel the reel anchors the copper.
- **Fin width (B8).** Agreed: stepped 1.45 / 1.88 mm everywhere. Euler for a
  1.45 mm fin 9–10 mm tall is 5.1–6.3 kN [calc wave3 §2].
- **Idea files rewritten to read cold**: "Picture it", locating, force path,
  checks, hand-backs and open problems in each; no wave narrative.
- **Sketches**: `sketches/make_sketches_w3.py` draws every sketch whose labels had
  gone stale, plus p1d, p5c and p6b. The older scripts no longer overwrite
  them, and `calc/cam_drive.py` no longer writes the p5 timing sketch.

## Directions set aside, why, and what would revive them

1. **Fan wider than housing pitch for crimping (w = 4–6 mm), then converge.**
   - Why set aside: trimming in the fanned pose leaves J1's outer conductors
     1.2–4.4 mm long, a 4–7 mm bow at the housing.
   - Revives if: the trim is done in the converged pose, or on an
     equal-length arc, or the crimp tooling cannot fit with neighbours dropped
     out of plane.
2. **Gantry visiting stations.** A three-axis gantry carrying the ribbon end
   (or the tools) between fixed stations on a bed.
   - Why set aside: under this view it is p1's cassette with a gantry as the
     carrier, or p2 with a linear tool changer, and the capture calc says any
     carrier works.
   - Covered elsewhere: borrowed-machines b3 and into-the-housing i4.
   - Revives if: a spare printer-class gantry is on the bench and the stations
     are laid out flat.
3. **A cheap arm carrying cassettes between benches** (SO-101 class,
   ±1–3 mm [estimate]; Dobot MG400 ±0.05 mm, $3,495 at Pololu [source]).
   - Why set aside: a carousel does the same with one motor.
   - Revives if: the benches are spread round a room, or the arm also does
     J4/J7's crossings. It would need fingers for that.
4. **Insert before crimp** (the housing as the contact locator).
   - Why set aside: it is into-the-housing's i2, and from this view it is an
     order change whose cost is tooling width at 2.5 mm pitch.
   - Revives if: the contacts' open wings can sit in alternate cavities.
5. **Two-step crimp split across stations**: tack the insulation barrel first
   at a light station, move, then coin the conductor barrel at a heavy one.
   - Why set aside: the open conductor barrel's strands get disturbed in
     transfer.
   - Revives as: pre-form both barrels lightly (the wing-curl phase, tens to
     hundreds of newtons [xh-facts §4]), move, then coin. That is
     force-and-form's two-station forming.
6. **Strip the whole ribbon end at once, before splitting.** Revived in wave 2
   as [p7](ideas/p7-strip-before-split.md), with straight blades rather than
   scallops. Straight edges do not need registering to each conductor; scallops
   do [calc wave2 §7].
7. **A dedicated 4P → XHP-4 machine.** Five of ten housings (J3, J5, J9, J11,
   J13) are identical ends at different lengths: 20 crimps, 38% of the unit.
   A machine with a fixed fan, fixed housing and no program would do only
   that.
   - Why set aside: it covers less than half the unit and every other loom
     still needs the general machine.
   - Revives if: the general machine proves hard and Derek wants the largest
     slice of identical work removed with the least machine. p3 running the
     4P spool is close to this already.
8. **Terminate both ends on the machine.** No: the far ends are Fastons,
   ferrules, IDC and screw terminals with branching legs [repo]. They are a
   different machine.
9. **Crimp on the ribbon at its own 1.7 mm pitch before splitting.**
   Impossible: the contact is 1.95 mm wide [mfr S1].
10. **Hang the spool above the bench and terminate downward** (wave 2). Gravity
    would feed the finished loom out, and a2b's flat tool would take the
    hanging conductor.
    - Why set aside:
      - a flat tool with a vertical nest brings back the neighbour-offset
        problem in the vertical plane;
      - spool curl keeps a hanging ribbon from hanging straight at a few
        grams of tension;
      - p6's puller solves the feed-out without it.
    - Revives if: bench front is short and height is free.
11. **Buy the gantry for p6's stage 2** (a $199 Ender-3 V3 SE
    [source via machine-that-sees-and-learns]) instead of growing stage 1's
    knob-turned slides.
    - Why not the main line: stage 1's slides are already the axes, so motors
      on the same screws cost less and keep the stage-1 geometry.
    - Revives if: stage 1 is skipped, or the module needs Z.
12. **Put the strip cams on p5b's shaft too.**
    - Why set aside: the strip pull is the step with the most unknowns
      (stretch, tear). A cam fixes its motion in plastic before it is
      understood.
    - Revives once p7 or an in-pose strip has been run by hand and its motion
      is known.
13. **An SN-2549 hung tip-down over a flat row, closing along the row.** Set aside:
    it rolls every crimp 90°, and no housing slides onto that row; twisting each
    conductor back strains the strands 2.3–4× past torsional yield
    [into-the-housing calc ex §8].
    - Revives if: the person inserts every contact by hand and a quarter-turn
      behind the housing is acceptable, or a rotating lift finger's untwist
      (force-and-form's a3-t) proves to leave a residual roll inside the
      cavity's lead-in (±10–15° [estimate]).
14. **A preloaded disc-spring stack under the eccentric's stops.** Set aside: the
    preload is a floor every stroke reaches once the stops touch, 1.5–2.1× the
    crimp in a stiff frame [calc wave3 §4]. A soft, unpreloaded loop is used.
    - Revives if: the frame is so soft that the margin *m* must be large, and a
      stack is the only way to cap an obstruction.
15. **Capturing the contact at the first ratchet tooth and then feeding the
    conductor axially.** Set aside: the tooth pinches the insulation wings to
    1.4–1.6 mm against a 1.7 mm jacket.
    - Revives if: the kit contact's barrel floor measures 1.9 mm or wider, when
      the bore at the tooth clears the jacket [force-and-form calc wave2 §1].
16. **Depth from the camera with identity from strands touching the neck
    blade.** Set aside: two stops on one axis; half the conductors get pushed
    into the blade.
    - Revives if: the contact's neck is ≥0.9 mm and the blade is moved to the
      far end of it, so strands never reach it and it serves the pull only.
17. **Smooth squeeze pads to push a slug.** Set aside: their squeeze raises the
    slug's own friction on the strands nearly as much as it adds drive.
    - Revives if: the jacket-on-strand friction measures low (μ ≤ 0.2).

## Questions for Derek

Measurements, each settling several ideas at once:
1. **The SN-2549's anvil jaw half, *a*.** With the tool lying on its side, how
   deep is the anvil half below the nest floor, over ~20 mm of jaw on the pivot
   side? It sets the lift (a + 2.7 mm) for p1c, p5b, p6 stage 1-SN and p2's head
   T.
2. **One crimp from the SN-2549 held tip-down over a flat row, jaws closing along
   the row, photographed end-on.** It shows the roll by looking.
3. **One kit contact side-on and end-on under the ELP camera.** Side-on: the neck
   between box and conductor barrel (p1d's fin relief needs 0.34–0.74 mm; a neck
   blade clear of the tips needs 0.70–0.90 mm). End-on: the insulation barrel
   floor's inner width (whether the first ratchet tooth pinches the bore).
4. **One crimped conductor in a TPU clamp, pulled at 20 N through the box with a
   luggage scale.** Does the copper creep back inside the jacket?
5. **The two-razor hand trial for p7, run twice, with and without toothed pads on
   the slug.** Two single-edge blades squeezed across a fresh 5P end with shims
   as stops, 2.4 mm from the cut, then pushed. Does the whole slug come off, or do
   the cut caps roll over the edges?
6. **The SN-2549's handle force at the moment the ratchet releases**, on a
   bathroom scale, against p5b's 275 N link.
7. **A fresh ribbon cross-section under the ELP camera**: how far the strand
   bundle sits off-centre in its jacket (p7's ligament).
8. **One conductor lifted 3.5 mm and 11 mm at 20–35 mm free, released, and
   photographed from the side**: the set behind the lift tables.

Choices only Derek can make:
9. **Split length.** How long may the unwebbed length be behind the housing: 20,
   25, 30 or 35 mm? A fin from below (p1d) wants 20–25 mm; an SN lying on its side
   wants 30–35 mm.
10. **Steel.** Would made dies (a ground-stock fin, an EDM or knife-set crimper)
    be welcome for p1d/p5c, or should every crimp head stay a bought hand tool?
11. **The spool hub.** What is the BNTECHGO spool's hub diameter, can its inner
    end be reached, and is ribbon from near the hub visibly curled?
12. **Terminating on the reel.** Would making each XH end on the reel, tested pin
    to pin through the reel before it is cut, suit how the bench is used? It asks
    for a rewind once per spool and ~5 more attended minutes a unit, and makes a
    bad crimp cost 6 mm of reel.
13. **J7's ribbon assignment.** Would GND riding the 3P with CLO/CHI, and the 5P's
    fifth conductor being the trimmed one, be acceptable? It makes J7 straight.
14. **Batching.** Would you hold finished looms ahead of units (one reel's life of
    one ribbon type), or should the machine work one unit at a time?
15. **Length tolerance.** How much shorter than its cut length may a loom end up?
    It sets how many whole-end redos a cut-first order allows.
16. **Order of ends today.** Which end of a loom is made first? The recovery
    numbers argue for the XH end first.
17. **Contacts.** Would you switch the machines to SXH-001T-P0.6 on cut strip
    (Digi-Key ~$0.04, in stock), keeping kit contacts for hand repair? Every
    lift-once station takes either on posts; only p6b needs strip.
18. **A second (and third) dedicated SN-2549** for a squeezer module or two
    alternating heads (p4b), leaving the bench tool for hand use?

## Open

- *a*, the neck *n*, the barrel floor width, and wing touch as a repeatable force
  threshold on the SN-2549.
- The steel for p1d and p5c: crimper profile, fin temper, gate and fin-slide wear.
- The squaring step after a lift: does copper that yielded twice stay within
  0.5 mm of the row?
- p7's tear, with and without toothed pads; the web's neck thickness.
- The puller's clip on silicone at a few newtons.
- Whether a straightener takes curl out of silicone ribbon without marking or
  twisting it.
- Carrier width and temper, and whether the clone drawings' wing widths are
  inside or outside dimensions: the $4.71 strip.
- Whether an equal-path fan block closes over tine-fanned conductors and keeps
  the tip line within ~0.1 mm (p6b).
- Whether a load cell separates the symmetric pairs of lance snaps in a V
  staircase (p6b).
