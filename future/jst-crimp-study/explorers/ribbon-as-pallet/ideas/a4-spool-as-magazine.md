# a4 Spool as magazine: terminate the leading end, then feed out and cut

## Picture it

In [a1](a1-pallet-tour.md) to [a3](a3-backshell-that-ships.md) the ribbon is cut
first and carried in a pallet. Here it is never cut before it is terminated. The
spool is the magazine, the web holds the conductors in order all the way from
the spool, and a **fixed clamp** at the leading end is the pallet. The stations
come to the clamp. When the end is finished the feed pushes the loom's length
out and a guillotine at the clamp face cuts it free; the same cut squares the
next end. procedure-is-the-machine reached the same arrangement as
[p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md).
Sketch: [`../sketches/a4-spool-as-magazine.svg`](../sketches/a4-spool-as-magazine.svg)
(schematic).

**Where things start.**
- **Spools.** 3P, 4P and 5P spools (15.2 m each [repo]) on a rack behind the
  machine. One ribbon, or two for a pair, runs through a roller straightener and
  a **belt feed** with an encoder wheel into a clamp channel cut 0.2 mm under the
  ribbon's width. Belt feed, not rollers, is what the ribbon cut-split-strip
  machines use on wide ribbon [prior-art §1].
- **The far-end port through the spool.** Either the BNTECHGO spool's inner end
  is brought out through the hub to a 6-circuit capsule slip ring on the axle
  ($9.99 [Prime]; two for a pair), or each spool is rewound once onto a printed
  reel with an 80 mm hub radius, which adds no new set, and its inner end is
  crimped into a hub socket (procedure-is-the-machine's
  [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md)).
  The reel stands still while an end is terminated, so a hub socket and a flying
  lead need no ring until a powered draw-off turns the reel [P3 C10].
- **Curl.** Off a 25 mm hub the ribbon keeps a residual curl radius of
  55–242 mm, which lifts a 35 mm protrusion's tip 2.5–12.6 mm out of plane
  [P3 §9]; a7's nicker noses sit just above and below a 1.7 mm ribbon and would
  miss it. So a **covered floor** runs from the clamp face to the tools and is
  lifted only for the tines, and the straightener or the 80 mm rewind removes
  most of the curl.
- **Loose parts.** Housings in a small magazine or dropped into the nest;
  contacts on the applicator's reel.

**What moves.**
1. The belt feed advances the leading end until its copper faces touch a
   grounded **tip stop**. Each conductor closes its circuit through the spool as
   it touches (Schleuniger's trigger-by-touch [prior-art §2], done through the
   conductors). The clamp closes; its front face is the split root.
2. The tip stop swings away.
3. The stations come to the fixed end on short slides: **zip**
   ([a7](a7-zip-station.md)), with the clamp face as the tear stop; **fan**, flat,
   to 5 mm, downstream of the applicator's anvil
   ([a1c](a1c-crimp-upstream-first-park-after.md)); **flush cut and strip** at the
   fan face with the rolling scorer ([a8](a8-rolling-ring-scorer.md)).
4. **Crimp.** The clamp and feed ride a short X slide (~60 mm) that indexes each
   conductor to a fixed side-feed applicator in a slow crank press
   (borrowed-machines' [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)),
   in a1c's order: upstream end first, each crimped conductor folded back over
   the clamp toward the spool. The spool stays on the rack; the ribbon between
   spool and feed bends ~30 mm sideways over half a metre.
5. **Insert** as [a6](a6-housing-as-last-comb.md), and test pin by pin through
   the spool on a real XH wafer.
6. **Feed out and cut.** The clamp opens and the feed pushes out the loom length,
   measured by the encoder wheel. The finished end, housing first, curves down a
   **drop tube**; gravity carries a floppy ribbon where pushing cannot. The clamp
   closes and the guillotine cuts; the loom falls into a bin with its far end
   square, and the new leading end is at the clamp face.

**What locates what, and the reference for fixed.** **"Fixed" is the clamp
face.**
- The guillotine makes the leading end square; touch-off records where each tip
  is.
- Laterally, the under-width channel (the ribbon's own pitch from a centred
  datum, 0.12–0.43 mm worst [calc §1]).
- **The fan's recession:** the flat 5 mm fan pulls a 5P's outer tips back
  1.65 mm [calc W2 §3]. With a8 the flush cut at the fan face puts the tips on a
  line again (order A of [a5](a5-part-fan-strip-in-the-pallet.md)). The spindle
  head [a8b](a8b-spindle-with-touch-off.md) could instead find each tip by
  touch and set that conductor's crimp Y from the record (order C), but its
  15 mm head butts the flat neighbours at 5 mm unless it has a snout no wider
  than 7.8 mm [P3 §8].
- The split is 17–23 mm (3P–5P) for the flat 5 mm fan [calc §2].
- The loom's length, from the encoder, to ~±3–6 mm on 600 mm at 0.5–1 % slip
  [procedure-is-the-machine calc]; a puller measuring from the clamp face does
  ±1–2 mm [procedure-is-the-machine calc wave2 §6].

**What drives the crimp and carries its force.** The applicator in its crank
press, as a1c. The clamp holds the ribbon against strip pulls (a few newtons per
conductor) and insertion pushes (up to ~90 N for a straight gang insertion into
an XHP-9 [calc §8]).

**How it knows.**
- **Through the spool:** touch-off at the tip stop, nick detection at isolated
  blades and tines, each conductor in its contact before a crimp, pin map,
  shorts and J2's empty cavity after insertion. The loom is tested before it
  exists as a separate piece.
- **At the crimp:** the crank's force curve, ΔF/k height, a camera frame.

**What the person does.** Threads (or rewinds) the spools a batch needs and
connects each inner end; loads the loom list; keeps housings and the contact
reel stocked; empties the bin; makes the far ends; rethreads between loom types.

## Steps it covers and what it hands back

- **Machine:** feed and reference by touch-off, split, fan, flush cut, strip,
  contact supply, place and crimp (a1c's order), insert, test through the spool,
  cut to length.
- **Person:** spools and inner ends, the recipe list, housing and reel supply,
  bin, far ends, rethreading.

## Batching

For ten units:

| Thread | Looms | Board-end crimps |
|---|---|---:|
| 4P | J3, J5, J9, J11, J13 × 10 | 200 |
| 5P | J6 × 10 | 50 |
| 5P + 4P | J1 × 10 | 90 |
| 3P + 3P | J2 × 10 (one conductor trimmed each) | 50 |
| 4P + 3P | J4 × 10 | 70 |
| 5P + 3P | J7 × 10 (one trimmed each) | 70 |

Six threadings for 530 crimps. One 4P spool covers ~5.4 units of 4P ends
[procedure-is-the-machine unit_inventory §4].

**Pairs.** Two ribbons from two spools, each with its own belt feed, enter one
channel edge to edge, hit the same stop, and are clamped, terminated and fed out
together. Feed slip between them shows as a length difference at the far end,
not the board end. The recipe says which ribbon lies on the datum side. J4 and
J7 cross conductors between their two ribbons, which a clamp holding both in
ribbon order cannot make ([a6](a6-housing-as-last-comb.md)).

**The guillotine exposes two ends at once.** When it cuts, the finished loom's
far end lies just past the blade at the top of the drop tube. A second bought
applicator for 6.3 mm Fastons on reel could terminate it there [assumption: sold
in the same OTP market; borrowed-machines]. Every other arrangement in this
directory hands all far ends back; this is where one could stop.

**Bought instead of built.** Bench wire cut-to-length machines (a stepper belt
feed, an encoder, a guillotine) are mass-produced [assumption on ribbon-width
guides and price], so the feed-and-cut module may not need designing.

## Problems, repairs and branches

1. **600 mm of silicone ribbon cannot be pushed.** It goes down a drop tube; or
   a puller on a belt takes the ribbon behind the housing and walks it out
   (p6's puller, [a9](a9-reel-end-docks.md); the grip is
   [a3](a3-backshell-that-ships.md)'s fold).
2. **The leading end comes off the spool curved.** Covered floor, straightener,
   80 mm rewind (above).
3. **Every loom-type change is a rethread.** It is the person's.
4. **The finished housing travels out through the clamp.** The clamp opens wider
   than the housing (XHP-9 is 24.8 mm overall [xh-facts §3]).
5. **A bad crimp** is cut off at the clamp face with its whole split, ~20–35 mm
   of spool, and the end is made again. No loom is lost; at a 2 % crimp failure
   rate it is ~37 mm of spool per unit [P3 §12].
6. **A docking crimp station instead of a1c's,** with the strip made before the
   split, is [a9](a9-reel-end-docks.md).

## What it contributes

- **No loading step:** nothing is cut first, handled, laid in a pallet or taken
  out.
- **A batch of fifty looms runs unattended,** suiting the ten-unit and Founder
  Edition runs.
- **One cut serves two looms:** it frees the finished loom and squares the next.
- **The loom is tested before it is cut,** through the spool.

## Major unresolved problems

- **Size:** a 0.6–0.7 m drop, or a puller rail, plus the spool rack.
- **Whether a BNTECHGO spool's inner end is reachable,** or each spool is
  rewound, and whether the straightener marks silicone or twists the web.
- **Threading pairs from two spools** without twist between the ribbons.
- **Housing supply** for mixed loom types.
- **The applicator's downstream envelope** (a1c) and the crank's pause window.

## Related ideas

- The docking version at a reel clamp: [a9](a9-reel-end-docks.md).
- Crimp order: [a1c](a1c-crimp-upstream-first-park-after.md). Stations:
  [a7](a7-zip-station.md), [a8](a8-rolling-ring-scorer.md),
  [a6](a6-housing-as-last-comb.md).
- Other explorers: procedure-is-the-machine
  [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md),
  [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md);
  change-the-question [c5](../../change-the-question/ideas/c5-ends-as-stock.md);
  borrowed-machines [b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md),
  [b8b](../../borrowed-machines/ideas/b8b-flat-spool-line-over-a-crown.md).

## What rests on assumptions

- Encoder accuracy [procedure-is-the-machine estimate].
- Spool hub radius and inner-end access [assumption].
- That the drop-tube path does not snag the housing [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels).
