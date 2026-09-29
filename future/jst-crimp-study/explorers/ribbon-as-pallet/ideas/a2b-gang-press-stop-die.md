# a2b Gang stroke: the docked cassette in the idle 12-ton press

## Picture it

A branch of [a2](a2-two-pallets-meet.md). The walking head goes away. The docked
cassette slides into a guided die set with one punch and one anvil per contact
at strip pitch. The VEVOR 12-ton shop press closes the die set until it bottoms
on hardened stop blocks. Every contact of the ribbon end is crimped in one
stroke, to a height set by the stop blocks, not the press. Sketch:
[`../sketches/a2b-gang-press-stop-die.svg`](../sketches/a2b-gang-press-stop-die.svg)
(schematic). force-and-form's
[f5](../../force-and-form/ideas/f5-die-cassette-and-the-shop-press.md) reached
the same press-and-stop-block idea from its side.

**The cassette.** a2's strip pallet plus the docked ribbon pallet: every
conductor already in its open contact, stripped at the fan block's face so every
insulation edge lies on one line ([a8](a8-rolling-ring-scorer.md)). The strip
pallet has a window under each contact.

**The die set.** A two-post guided set on the press bed:
- the **lower shoe** carries N anvils at strip pitch (~7.1 mm), each rising
  through its window to cradle a contact's barrels, **each with a relief for
  the lance** so the contact sits flat [w3 §5];
- the **upper shoe** carries N punches, each with a stepped B-profile for both
  barrels;
- **hardened stop blocks** on the lower shoe meet the upper shoe at the crimp
  height.

The cassette slides in on rails against an end stop; the strip pallet's slot
pins engage holes in the lower shoe, so the contacts sit over the anvils.

**The stroke.** The person pumps the press handle, about ten strokes of the
jack. The punches meet the wings, curl them and compact the strands; the upper
shoe lands on the stop blocks, and further pumping loads only the blocks. The
person opens the valve and springs lift the upper shoe.

**What locates what, and the reference for fixed.** "Fixed" is the lower shoe:
anvils, stop blocks and the holes for the strip pallet's pins are one steel
part. The contacts are located by the carrier on the slot pins; the conductors
by the docking (as a2); the crimp height by the stop blocks.

**What drives the crimp and carries its force.** The VEVOR jack → upper shoe →
N punches → contacts → N anvils → lower shoe → bed. The guide posts keep the
shoes square; the stop blocks take all force beyond the crimp.

| Ribbon | Force for the stroke |
|---|---|
| 3 contacts | 2.4–7.8 kN |
| 5 contacts | 4.0–12.9 kN |
| J1's 9, as one cassette | 7–23 kN |

That is against ~118 kN available [calc §7]. Overdriving to 20 kN puts 50–200
MPa on 100–400 mm² of stop block [calc §7].

**How it knows.**
- **End of stroke:** the upper shoe touching the stop blocks, read electrically
  (both steel, insulated from each other).
- **One load reading for the stroke:** a load cell or strain gauges under the
  lower shoe, read while the person pumps. For a 5-contact stroke a missing
  conductor drops the total by 12–20 % and a missing contact by 20 %, against a
  monitor's ±4 % band; one strand of 60 is invisible (0.34 %) [calc X §11,
  borrowed-machines]. The station is named by the camera frame and by
  continuity before the stroke.
- **Placement before the stroke:** every conductor to the carrier, as a2.
- **Crimp height** is checked on the session's first cassette with a micrometer,
  then trusted to the blocks.

**What the person does.** Pumps the press, moves the cassette in and out, plus
a2's loading. An air-over-hydraulic jack on the shop compressor would pump it:
the BIG RED TA91206 12 t is $136.04 [Prime], but it is a lifting jack and its fit
in the VEVOR frame and return springs is not stated.

## Steps it covers and what it hands back

- **Machine (fixture and press):** placement by docking, the crimp of a whole
  ribbon end in one stroke to a fixed height, a gross-fault load reading.
- **Person:** pumping (unless an air jack is fitted), moving the cassette, a2's
  loading, strip segments, far ends.

## Why this is interesting

- An idle tool does the stroke, and the stroke is one event per ribbon end.
- Crimp height becomes a property of the die set: a guided set bottoming on
  stops makes the press's speed, force and repeatability irrelevant.
- The only precision in the system lives in parts that do not move relative to
  each other during the stroke.

## The hard part: N matched punches and anvils

A B-crimp punch for 22 AWG is a precise profile about 1.5–1.75 mm wide with two
arches. JST's 22 AWG width is licence-gated; KONNRA's clone spec gives conductor
crimp 1.75 ± 0.15 × 0.73 ± 0.05 mm and insulation crimp 1.80 ± 0.10 high,
2.05 max wide ([source](https://konnra.com/jst-xh-2-5-connector-complete-guide/)).
KONNRA's 0.73 at 1.75 wide and the context's ~0.88 at 1.5 wide are the same
compaction, 1.28–1.32 mm² [w3 §7]: **the target height scales with the channel
width**, and a height copied from a 1.5 mm reference to a 1.6 mm channel
over-compacts by 3–10 % [w3 §7]. Routes to N copies:

1. **Harvest.** Two sources of steel:
   - N XH-capable ratchet crimpers, each jaw cut down to its XH nest. The jaws
     of this tool class are EDM-cut steel plates [prior-art §4]. A loose 2549
     die on Prime comes only inside the iCrimp IWS-0723K set, $46.59 [Prime, thin
     listing]; SN-2549 jaws sold alone had no Prime listing.
   - N OTP applicator crimper-and-anvil sets ($125–165 each [borrowed-machines
     b1]; no Prime listing).

   Each pair was aligned in its own tool. In the die set each needs its own side
   adjustment and height shim, because the stop blocks set the shoe gap, not
   each punch's protrusion.
2. **Made to order.** One upper plate with N punch profiles and one lower plate
   with N anvils, from the same program. Quick-turn wire EDM at ±0.05 mm exists
   (force-and-form). At 7.1 mm pitch a one-piece crimper plate leaves 5.1–5.6 mm
   webs between profiles ([f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md)).
   It needs a profile drawing, which needs the crimp dimensions.
3. **Two strokes with simpler dies.** Stroke one crimps only the conductor
   barrels, stroke two only the insulation barrels, as the PA-09 does by hand
   [xh-facts §2]. Each plate is a simpler single-arch profile.

## Branch within the branch: gang the conductor barrels, walk the insulation barrels

The conductor barrel is where the force and the precision are: 0.75–2.3 kN,
crimp height ±0.05 mm [xh-facts §4]. The insulation barrel needs 30–130 N and a
height that suits silicone. So the press does all conductor barrels at once with
one plate pair, and a light head or a hand plier closes each insulation barrel
to its own height. On silicone that height matters: a clone-spec 1.80 mm
insulation crimp squeezes the jacket to 70–80 % of its area [calc W2 §9], and
force-and-form's [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)
sets each insulation crimp by its own blade and sweep. This splits the problem
where the physics splits.

## Major unresolved problems

- **Die making.** None of the three routes is simple or cheap. Harvesting is
  the cheapest to try and the least certain in alignment.
- **A missing contact.** One punch meets nothing and the others still crimp; the
  stop blocks take the overdrive. The load reading sees a 20 % drop, and
  continuity before the stroke already flags a missing conductor.
- **Punch retraction.** Crimped wings can grip a punch. The pattern is the
  applicator's terminal stripper (item 147 in JST's MKS-L manual), a plate that
  holds the work down as the crimper rises; here a spring plate with one finger
  per contact. Not designed further.
- **The strip pallet windows** must pass N anvils while holding the carrier flat.
- **The lance** at each anvil (relief), and the pull and shear as in
  [a2](a2-two-pallets-meet.md).

## Related ideas

- Parent: [a2](a2-two-pallets-meet.md). Siblings: [a2e](a2e-docked-strip-through-a-feedless-applicator.md)
  (one bought applicator, one contact per turn), [a10](a10-dock-tack-then-nest.md).
- Other explorers: force-and-form
  [f5](../../force-and-form/ideas/f5-die-cassette-and-the-shop-press.md),
  [f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md),
  [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md);
  borrowed-machines [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
  (load sensing under the shoe).

## What rests on assumptions

- Crimp forces [xh-facts §4, estimate]; strip pitch [estimate].
- That KONNRA's clone numbers are close to JST's for this wire [assumption].
- That an air-over-hydraulic jack fits the press [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels) and [a2](a2-two-pallets-meet.md#labels).
