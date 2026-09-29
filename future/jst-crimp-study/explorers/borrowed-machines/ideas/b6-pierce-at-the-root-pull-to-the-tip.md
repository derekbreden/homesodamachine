# b6 — Pierce at the root, pull toward the tip: splitting borrowed from zip cord and the sewing machine

Zip cord is split by pushing a pin through the web between its conductors and
pulling: the tear runs along the web, ahead of the pin. A sewing machine does
the same kind of act millions of times a day: a hardened pointed needle goes
through soft work into a hole in a steel needle plate, and the work is drawn
along while the needle is in it. A seam ripper is the hand version, a point to
go in and a crotch blade to cut. This idea borrows all three for the 22 AWG
silicone ribbon: a needle enters each web **at the split root**, and the ribbon
is drawn so the needle travels **toward the tip**, stopping at the strip line.

**Related:** [b8](b8-spool-fed-borrowed-line.md) and
[b8b](b8b-flat-spool-line-over-a-crown.md) use this rip with the spool feed's
retraction as the draw; [b1](b1-press-and-applicator-with-shuttle.md) and
[b3](b3-gantry-carries-the-crimp-head.md) take its split and whole-tip strip.
ribbon-as-pallet's [a7](../../ribbon-as-pallet/ideas/a7-zip-station.md) and
[a7b](../../ribbon-as-pallet/ideas/a7b-plough-station.md) split from the other
end (tip toward a clamp that stops the tear); procedure-is-the-machine's
[p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md) strips the
whole end while it is webbed and splits after. All of them rest on the same
unknown: whether the neck between two fused jackets is the cheapest path for a
tear (repo Open item 5).

Sketch: [`../sketches/w2-b6-pierce-and-pull.svg`](../sketches/w2-b6-pierce-and-pull.svg).

Labels: [calc wave2 §n], [calc wave3 §n] are this explorer's
[`wave2.out.txt`](../calc/wave2.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.** A ribbon end in b1's cassette on the shuttle: in the
under-width channel, centred datum, tip flush-cut, not yet split.

**The station**, one position on the shuttle's Y rail beside the crimper:
- **Needle plate.** A steel strip under the ribbon's path at the root line, with
  a short slot, 0.65 mm along X and ~1.4 mm along Y, for the needle's tip: a
  laser-cut stainless stencil (JLCPCB 304 stencils from $3, shipped in about a
  day [into-the-housing, source]), several layers bonded, or a 1.5 mm steel strip
  drilled on the WEN drill press.
- **Top guide.** The same slot in a second strip above the ribbon, with room for
  the ribbon between the two.
- **Needle.** A 0.6 mm hardened steel pin ground to a ~15° cone: a cut-down
  sewing-machine needle, or 0.025 in (0.635 mm) music wire (K&S, $7.24 for four
  [Prime]). It rides a small Z slide on a servo lever, and the slide sits on two
  thin flexures that let it **float ±0.4 mm in Y** against a light centring
  spring.
- **Cutting-edge option.** A #11 scalpel point (100 for $13.09 [Prime]) stood in
  the same slide, edge toward the tip, cuts instead of tears: a seam ripper's
  crotch on a post.

**One web (seam *k*).**
1. The shuttle puts seam *k*'s nominal Y under the needle and the root line (the
   cassette's clamp edge, or the recipe's root) at the needle's X.
2. **Pierce.** The needle comes down. Its cone lands in the V-valley on the
   ribbon's top face; near the bottom of the valley the walls are steep, so the
   floating needle slides to the neck and goes through it, 0.5–3 N [estimate],
   into the needle plate's slot.
3. **Pull.** The shuttle draws the cassette back along X. The needle, fixed in X,
   travels through the ribbon toward the tip. A round needle tears the neck at
   3–15 N, depending on the neck's height (0.2–0.6 mm, unmeasured); an edge cuts
   it at ~0.2–3 N [calc wave2 §2].
4. **Stop at the strip line**, Ls from the tip (2.4 mm for genuine JST contacts,
   1.85–2.1 mm for clone contacts [facts §1; TS §3]). The needle lifts. The tip is
   still webbed.
5. Y indexes to the next seam. A 5P's four seams take ~80 s of machine time
   [estimate].
6. **Trims.** For J2 and J7, a servo flush cutter at the clamp edge trims the
   recipe's unused conductor at its root; the rip has already freed its sides.

**Then, still at the station: the whole-tip strip.** With the tip webbed, all
the conductors' slugs come off as one piece. Two flat blades close on the
crowns at the strip line, top and bottom, to a stop set for 50–60 % of the wall,
or riding a shoe on the jacket's top (at 70–80 % a fixed stop reaches the strands
in the worst case [TS §8]); [b4b](b4b-diode-heads-at-the-station.md)'s diode heads
are the laser alternative. TPU pads close on the tip and the shuttle backs off
3 mm. The slug is comb-shaped: the webs ahead of the strip line leave with it.
The pull is 4.7–13 N a conductor (24–65 N for a 5P) [calc wave3 §8].

**What locates what; the reference for "fixed."**
- **Across:** the ribbon's own valley steers the floating needle into the neck.
  From a centred datum the seams are off nominal by at most ±0.05 (3P), ±0.10
  (4P) and ±0.15 mm (5P) [calc wave2 §2]; the valley captures a point within
  about half a pitch, and the float allows ±0.4 mm.
- **Along:** the root is **where the needle went in**, at the shuttle's X,
  ±0.05 mm plus any slip of the ribbon in the clamp [estimate]. The tear runs
  only ahead of a needle moving toward the tip, so it cannot run back past the
  pierce.
- **Stop:** the strip line, in the cassette coordinates the crimp uses.
- The reference for "fixed" is the cassette datum, carried by the shuttle.

**What drives and carries the force.** The shuttle's X axis pulls the cassette;
the ribbon between the clamp and the needle is **in tension**, so it cannot
buckle. The needle is a beam supported by both guide strips over ~2.2 mm: at
15 N a 0.6 mm pin sees ~390 MPa, well inside hardened steel [calc, by hand from
M = FL/4].

**How it knows it worked.**
- **Rip force.** b1's cassette load cell reads it. A steady 3–15 N along X is a
  tear following the neck; a jump means the needle has left the neck.
- **Needle as electrode.** The needle is isolated and wired, and the loom's far
  end is in a pogo block. If the needle reaches copper, channel *k* or *k*+1 reads
  continuous to it: the shuttle stops and backs out.
- **Backlit look.** After the rip, a backlight under the bed plate shows every
  split as a bright slit to the ELP camera, and each conductor's silhouette
  width along the split shows whether a jacket was thinned.

**What the person does.** Nothing beyond b1's loading: the cassette goes from
the rip station to the fold lid to the crimper on the same shuttle.

## Steps it covers and what it hands back

- **Covers:** split (to a placed root), strip (the whole-tip slug at the same
  station), the J2/J7 root trims, and checks (rip trace, needle continuity,
  backlit split).
- **Hands back:** loading the cassette; everything from placing the contact
  onward.

## Why enter at the root and travel toward the tip

| | Pierce at the root, pull to the tip (b6) | Enter at the tip, push toward the root (a7, a7b, a harp) |
|---|---|---|
| Ribbon between clamp and tool | in tension | in compression; a 5P buckles at ~6–56 N over 15–5 mm free [calc wave2 §2], so it needs guide combs over the free length |
| What sets the root | the pierce | the tear stop: a wedge opening 0.2–0.5 mm drives a tear 0.6–2 mm ahead of itself [calc wave2 §2, double-cantilever estimate], so the tool stops short and the clamp face stops the tear |
| Where the root can be | anywhere the needle can reach | at a clamp face |
| The tip | can stay webbed: stop at the strip line | split first |
| Start | the valley on the top face guides the point | the square end face has no valley; a nick or a V-nose starts it |

Where the root is not at a clamp face, the pierce is the only way to set it:
b8's spool line rips before its clamp closes, and b1's split-on-demand variant
wants a partial split that ends short of the clamp.

## The hand rip board: useful the week it is printed

No motors. A printed channel with an under-width fit and a lever clamp on a
short rail; a needle plate and top guide at the root line; a hinged needle bar
with N−1 pins at 1.7 mm pitch.
1. Lay the ribbon with its tip against a stop and close the clamp.
2. Push the needle bar down: every pin pierces its web at the root.
3. Pull the clamp carriage back along the rail to the strip-line stop: 6–30 N for
   a 3P, up to 60 N for a 5P [calc wave2 §2], easy by hand.
4. Lift the bar, lift the ribbon out.

About 25 s an end [estimate]. It replaces peeling by hand in today's procedure
and in [b2b](b2b-pedal-less-hand-station.md). Pins at a fixed pitch cannot
float, so a 5P's outer seams, ±0.15 mm off plus the channel's own error, bring a
0.5 mm pin within reach of the outer strands (copper edges sit ±0.48 mm from each
seam); 0.4 mm pins, or the outer seams done with the ribbon shifted, keep the
margin.

## Looked at alongside: the harp (egg slicer)

Taut music wire at each seam, held at 1.7 mm pitch by two printed combs, with the
square-cut end pushed through: every seam at once, and wires thinner than any
divider a printer can make. 0.2–0.3 mm music wire at 20–40 N is at 12–55 % of its
strength, bows 0.4–0.75 mm under a 5 N cutting load and has a side stiffness of
7–13 N/mm, low enough for the jackets to steer it [calc wave2 §2]. It pushes the
ribbon in compression and its tear runs ahead, so it needs guide combs and a
clamp at the root: a7's arrangement with wires for tines. It is a note, not a
developed idea.

## Problems and their repairs, as they stand

- **The needle lands on a crown and pierces a jacket.** The centred datum and
  under-width channel bring each seam within ±0.15 mm, and the float lets the
  cone follow the valley. The needle-as-electrode catches the case where it still
  goes wrong, before the pull.
- **The tear wanders into a jacket instead of following the neck.** Whether the
  neck is the cheapest path is repo Open item 5. The rip-force trace and the
  backlit silhouette show a wandering tear; the cutting-edge needle does not rely
  on the neck being weakest.
- **Pierce force squashes the ribbon.** 0.5–3 N [estimate] on a ribbon lying on
  the needle plate; the top guide keeps it flat.
- **The needle bends.** At 15 N over a 2.2 mm span between the guide strips, a
  0.6 mm pin is at ~390 MPa. Without the lower plate, as a cantilever, it would be
  at several times that.

## Printed and bought

- **Printed:** station body, flexure float, servo lever, channel and clamp for
  the hand board, needle bar.
- **Bought:** stainless stencil strips (JLCPCB) or 1.5 mm steel strip; music wire
  or sewing-machine needles (size 80/12 and similar); #11 scalpel blades
  [Prime]; a servo (MG90S, $13.88 for four [Prime]); TPU for the pads; flat
  blades for the crown scores (single-edge 0.009 in blades, $12.90 [Prime]).
- **On hand:** the WEN drill press, the ELP camera, b1's shuttle and load cell.

## Contribution

- A split whose root is placed, not stopped, and a ribbon kept in tension while
  it is split.
- A split that ends at the strip line, so the tip stays one piece for a
  whole-tip strip.
- A first-week hand board that replaces peeling.
- The needle as an electrode; the rip force as a trace.

## Major unresolved problems

- **The neck** (repo Open item 5): its height, and whether a tear follows it.
  Peeling a metre by hand and sectioning a ribbon decides between tearing (round
  needle) and cutting (edge).
- **Capture.** How far the floating cone can be off the valley and still slide
  into the neck on grippy silicone; ±0.5 mm is an estimate.
- **The needle-plate slot** and the float together: the slot has to be long in Y
  and tight in X.
- **The whole-tip strip** after the split: whether each flank tears cleanly from
  crown scores when all slugs come off together.

## What rests on what

- **Derek:** peeling the web by hand is today's step [repo cable-assemblies.md].
- **Facts:** conductor pitch 1.7 ±0.1 mm and the wall [facts §7]; strip lengths
  [facts §1].
- **Calculations:** rip and buckling forces, seam error, harp numbers [calc wave2
  §2]; strip pull [calc wave3 §8]; score depth at a fixed stop [TS §8]; needle
  stress by hand.
- **Estimates:** pierce force 0.5–3 N; cutting resistance 1–5 N/mm of neck;
  capture ±0.5 mm; times.
- **Assumptions:** tear strength 15–25 N/mm for this silicone [Primasil, wire
  grade]; conductor pitch error ±0.1 mm per conductor, worst case one way.
