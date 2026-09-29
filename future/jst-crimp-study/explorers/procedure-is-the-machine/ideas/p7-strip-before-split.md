# p7 Strip before split: one stroke takes the whole end's slug while the web still holds the pitch

Sketch: [`../sketches/p7-strip-before-split.svg`](../sketches/p7-strip-before-split.svg)
(schematic cross-section and side section). Numbers:
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §7 (cited as [calc wave2 §7]),
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) §5 (cited as [calc wave3 §5]),
[`../calc/exchange_ribbon_w3.out.txt`](../calc/exchange_ribbon_w3.out.txt) §1
(cited as [calc P3 §1]), force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
§6–7 (cited as [calc FP §n]).

An order change. Today's procedure, and nearly every arrangement in the study,
splits the web first and then strips each conductor on its own [repo
cable-assemblies.md steps 2–3]. Here the whole ribbon end is stripped at once,
while it is still webbed, flat and registered in its clamp: two straight blades
close from above and below 2.4 mm from the flush cut, and the slug comes off
web and all. The split then starts from the open gap the slug left.

## Picture it: a 5P end at a clamp

**Where things start.**
- A 5P end is held in a channel clamp 0.2 mm under the ribbon's width, the marked
  edge on the wall: [p6](p6-spool-end-bench-that-grows.md)'s reel clamp, a
  [p1](p1-cassette-and-benches.md) cassette's clamp at loading, or a
  ribbon-as-pallet pallet.
- The end has just been flush-cut at the clamp face; at a reel, the previous
  loom's cut did it. Nothing is split.

**The station**, a small two-blade press in front of the clamp face:
- **The floor is split.** The fixed channel floor ends 2.4 mm ahead of the clamp
  face. Ahead of that, under the slug, the floor is part of a **carriage** that
  can slide +Y 4 mm. The joint between them is the strip line.
- **The blades** are single-edge razor blades, 0.009 in [Prime: AccuTec Pro
  APBL-7064, $12.90 per 100], in printed carriers on the carriage: the upper one
  comes down across the whole width, the lower one rises through the floor joint.
  Each carrier runs in an inclined slot, so the blade **slices**, drawn 2–4 mm
  along its own edge, as it closes.
- **Each blade stops against a steel stop** referenced to the channel floor. The
  conductors' centre plane is 0.85 mm above the floor; with *zs* = strand radius
  + ligament = 0.36 + 0.2–0.3 mm, the upper edge stops 1.41–1.51 mm above the
  floor and the lower 0.19–0.29 mm.
- **A pad pair** on the carriage, finely toothed or knurled, closes on the slug's
  top and bottom ahead of the blades.

**One stroke.**
1. **Close.** The pads close on the slug; the blades slice in to their stops.
   Each conductor's crown is cut top and bottom to a chord. Left uncut is the band
   |z| < *zs* of every jacket (its flanks) and the web in each valley.
2. **Push.** The carriage slides forward 3–4 mm. The pads carry the push into the
   slug's crowns, and the blades' faces help where they bear on the cut caps. The
   band tears around each conductor, and the slug (five jackets and four webs,
   2.4 mm long) slides off the strands like one sleeve.
   - The tension bound is 10–15 N per conductor at a 0.2 mm ligament, 54–74 N for
     a 5P; tearing from the score lines takes less, 3–15 N per conductor on other
     explorers' figures [calc wave2 §7].
   - The clamp holds the ribbon across its whole width, so the pull never
     reaches an unwebbed part: there is none yet.
3. **Open.** The pads open, the blades retract, the slug drops or is brushed off.
4. **Look.** One backlit ELP frame sees every bare length and insulation edge on
   one line: each conductor's 60-strand brush in silhouette, a nicked strand, a
   ragged tear.
5. **Split from the open gap.** The bare strand bundles (0.72 mm across at
   1.7 mm pitch) leave ~0.98 mm gaps. The splitter's nose enters a gap and meets
   the web's front edge at the strip line, already opened by the slug's tear:
   ribbon-as-pallet's [a7](../../ribbon-as-pallet/ideas/a7-zip-station.md) zip
   wedge, or p1b's razor comb. The tear runs back toward the clamp face, which
   stops it.
6. **Fan** the conductors to 2.5 mm by their insulation, never by the bare tips.
7. **Crimp** at any station; the insulation edge was measured in step 4.

## Why pads, and why they must bite

The blades' faces bear only on the end faces of the caps they cut: 0.28–0.65 mm²
per conductor. Pushing 10–15 N per conductor through them is 15–54 MPa, 2–5×
silicone's 8–11 MPa, on a lip that is free on top; the caps crush and can roll
over the edges before the flanks tear. A thicker, safer ligament makes the cap
smaller and this worse [calc FP §6].

A pad pair spreads the push over each crown's top. But the pads' squeeze also
presses the jacket onto the strands, raising the slug's own friction on them.
The net push per conductor is 2 N (μ_pad − μ_jacket-on-strands) plus what the
caps carry [calc wave3 §5]:

| Pad | μ_pad, μ_js [assumption] | Pad force per side, 5P, tear 3–15 N per conductor |
|---|---|---|
| Smooth TPU | 0.8, 0.5 | 32–132 N |
| Grippy TPU | 1.2, 0.3 | 11–44 N |
| Fine teeth or knurl | ~2.0, 0.4 | 6–25 N |

So the pads bite rather than squeeze. The teeth mark only the slug, which is
thrown away.

**Slicing.** A sharp edge pressed straight into silicone indents it by the order
of 0.03–0.25 mm before it starts to cut [force-and-form estimate], comparable to
the 0.2–0.3 mm ligament, so a pressed kerf can stop short of its steel stop.
Drawing each blade along its edge as it closes lowers the force to cut soft
solids [assumption, from the cutting literature force-and-form cites] and lets
the kerf reach the stop.

## What the order changes

- **The stripper sees a registered, flat ribbon, not floppy individuals.** The web
  holds every conductor at its 1.7 mm pitch while the blades close: no lifting,
  no selecting, no tip wander.
- **One stroke per end instead of one per conductor:** 14 strokes a unit instead
  of 53.
- **Straight blades do not care about pitch error.** They cut every crown at one
  height whatever its x. The ribbon's ±0.1 mm per conductor, up to 0.43 mm worst
  on nine from a centred datum [ribbon-as-pallet calc §1], does not move the cut
  toward any strands. Scalloped cutters (US 4,046,045) would cut the flanks too,
  but their notches must sit on each conductor within the ligament: with a
  0.25 mm ligament, a notch 0.2 mm off leaves 0.05 mm, and one 0.43 mm off cuts
  strands [calc wave2 §7].
- **The depth reference is mechanical.** The margins stack to ±0.08–0.12 mm RSS
  [calc wave2 §7]: the strand bundle's offset in its jacket (0.05–0.10
  [assumption]), the blade stop (0.02–0.03), the jacket OD tolerance (0.05),
  floor flatness (0.02–0.03). A 0.15 mm ligament is inside that scatter at its
  high end, so the ligament is 0.20–0.30 mm.
- **Every strip line is on one straight line, found in one frame.** Fanning
  afterwards pulls the outer fronts back, by an amount the fan's shape sets
  [calc P3 §1; calc wave2 §7; calc FP §7]:

  | Fan to 2.5 mm | Straight diagonal over a 15 mm split | Compact R 5 / 30° S |
  |---|---|---|
  | 4P | 0.05 mm | 0.20 mm |
  | 5P | 0.09 mm | 0.31 mm |
  | J1's nine together | 0.35–0.41 mm | — |

  Each conductor's insulation edge stays where it is on that conductor, so the
  crimp's own axial chain is unchanged; only the fronts used for gang insertion
  move. Each ribbon of a pair is stripped on its own.
- **The split has a start.** The slug's removal leaves an open gap at the strip
  line: the notch a zip tear needs.

## Where it fits

- **[p6](p6-spool-end-bench-that-grows.md)**: at the reel clamp the flush cut, the
  whole-end strip and (at stage 5) the split all happen at one face, before the
  crimp. Before stage 5 the machine strips and the person splits.
- **[p6b](p6b-reel-end-docks-on-a-strip.md)**: docking needs every tip and strip
  line on one line after the fan, so p7 is paired with an **equal-path fan** whose
  inner grooves carry humps that make every path as long as the outer one (a 5P
  at 7.1 mm: 5.1 mm over 21.4 mm [calc P3 §1]).
- **[p1d](p1d-lift-once-fin-from-below.md) and [p5c](p5c-camshaft-turns-a-knee.md)**:
  p7's lever at the cassette's clamp, at loading, before the person peels the web.
  The crimp station then only lifts, looks, places and crimps.
- **[p1b](p1b-carousel-joins-the-benches.md) station A**: flush cut, strip webbed,
  split, fan into the cassette's comb.
- **A gang's strip line in one stroke** (force-and-form's
  [f5b](../../force-and-form/ideas/f5b-half-row-cassette.md) half-row cassette,
  [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md) tack
  pallet): every barrel of a row sits at one Y, and p7 puts every insulation edge
  on one line. Spreading into 5.0 mm half-rows then moves the outer edges back
  0.02–0.03 mm for rows of 2, 0.08–0.13 for rows of 3, 0.17–0.29 for rows of 4 and
  0.31–0.51 for rows of 5 (12–20 mm splits) [calc FP §7]. Rows of 2–3 carry 68 %
  of a unit's crimps; rows of 4–5 want their pockets staggered by the computed
  amount.
- **An applicator station at the reel** (force-and-form's
  [f2c](../../force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md)): one
  frame gives every conductor's insulation edge, and the carriage that presents
  each conductor to the applicator corrects its depth from that frame (p6b's
  branch).
- **By hand, at stage 0.** A lever version, two razor blades on a hinged printed
  jaw with shim stops and a toothed pad, strips a whole end in one squeeze and
  one pull. It is useful the day it is printed.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Strip line along the wire | blades | clamp face (the cut guide), 2.4 mm |
| Cut depth | blade edges | steel stops referenced to the channel floor |
| Conductor height | each conductor's centre | channel floor + jacket OD/2 |
| Lateral | nothing needed | straight blades span the ribbon |

"Fixed" is the channel floor and the clamp face.

## What drives it and carries its force

A lever, or a NEMA 17 on a lead screw [Prime: NEMA 17 with integrated T8×2 lead
screw, $27.99] for the close and an MGN9 slide [Prime: MGN9 rail, $16.12] for the
push. The cutting load is a few tens of newtons across the width; the push is
20–75 N for 3P–5P. The load path is carriage → pads and blades → slug, reacted by
the clamp across the whole webbed width.

## How it knows it worked

One backlit frame: every bare length, every edge, the brush. With the blades
isolated and the far end connected (a hub socket at a reel, a pogo block on a
cassette), a blade touching copper names the conductor.

## Steps it covers, and what it hands back

- **Automated (station form):** flush cut, strip of the whole end in one stroke,
  one-frame inspection, the start of the split.
- **Handed back:** the split itself until a split station exists; crimping and
  insertion elsewhere. As a hand lever: the squeeze and the pull.

## Printed and bought

- **Printed:** blade carriers with inclined slots, the lever or slide body, the
  split floor, the pad holders.
- **Bought:** single-edge razor blades ($12.90 per 100 [Prime]); two steel stop
  screws and a ground plate under the channel floor (ground flat stock
  requested, not Prime-confirmed); toothed pads cut from a knurled steel strip or
  printed in PET-CF with fine teeth; an MGN9 slide for the push.

## Branches kept beside it

- **p7-laser.** Score one line across the whole webbed ribbon with a 455 nm
  module, top then bottom (borrowed-machines
  [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md)). Depth is set
  by absorption and focus, not a stop, and copper absorbs ~65 % at 455 nm
  [digest], so the score must stay in the jacket.
- **p7-scallop.** Scalloped cutters that also cut the flanks, leaving a thin ring
  to tear. The channel's registration (±0.1–0.4 mm [ribbon-as-pallet]) makes it
  marginal on a 5P and unworkable on nine.

## Contribution

- A **strip method whose depth is set by a steel stop** and whose position across
  the ribbon does not matter, built from razor blades.
- A **reason to strip before splitting:** the web does the registering, one
  stroke does the end, one frame measures it, and the split gets its start.
- **The rule for pushing a slug off silicone:** push through pads that bite, not
  through a cut face, and slice rather than press.

## Major unresolved problems

- **The tear itself:** how silicone parts across flanks and web from two straight
  scores, and at what pull. Derek's hand trial (two razors across a fresh 5P end
  with shim stops, pulled) is best run twice, with and without pads on the slug:
  do the caps roll over the edges?
- **Strand splay** at bare tips through split and fan; the splitter's nose must be
  ≤ ~0.9 mm between bundles, and the fan must hold insulation only.
- **The strand bundle's offset in its jacket**, which sets the minimum ligament.
  One cross-section photo measures it.
- **The web in the valley** may be thicker than the flanks (repo Open item 5): a
  thick neck raises the pull and may tear back along the valley. That is the
  start of the split, and the clamp face stops it.
- **The split floor's joint** marking the ribbon when the clamp closes.

## What rests on assumptions

- Silicone at 8–11 MPa [source: Primasil via the digest]; tear forces are other
  explorers' estimates.
- Strand bundle radius 0.36 mm and wall 0.49 mm [digest].
- Strand offset 0.05–0.10 mm.
- The friction coefficients in the pad table.
