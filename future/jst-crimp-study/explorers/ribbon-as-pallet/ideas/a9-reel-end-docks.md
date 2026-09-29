# a9 The reel end docks: terminate at the reel clamp, dock onto reel strip, crimp through a feedless applicator, cut last

## Picture it

A combination. From procedure-is-the-machine:
[p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md)'s
reel rewound onto an 80 mm hub radius with a hub socket, the clamp face as the
cut line, draw to length and cut last;
[p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)'s strip of
the whole webbed end in one stroke;
[p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)'s
puller and partner nest; and three transfers from that explorer's reading of
this directory (a short eccentric, a pilot in the carrier slot, a pull through
the box). From this directory: [a4](a4-spool-as-magazine.md) (the spool as
magazine), [a2e](a2e-docked-strip-through-a-feedless-applicator.md) (docking
onto strip, the feedless applicator, continuity to the carrier),
[a7](a7-zip-station.md) (a tear stopped at the clamp face),
[a6](a6-housing-as-last-comb.md) (closing block, insertion clamp, real-wafer
nest), and an **equal-path fan** ([a5](a5-part-fan-strip-in-the-pallet.md) F5,
order B). procedure-is-the-machine named it X1. Sketch:
[`../sketches/a9-reel-end-docks.svg`](../sketches/a9-reel-end-docks.svg)
(schematic).

Why the pieces meet: stripping the webbed end before the split puts every strip
line on one line while the web still holds the pitch, but a fan made afterwards
pulls a 5P's outer tips back 2.77 mm at 7.1 mm [calc W2 §3], which docking
cannot absorb. Equal-length grooves make the two compatible. In return, docking
gives the reel bench a crimp in which every contact is crimped floor-down on one
anvil by bought dies.

**Where things start: the 4P reel making J11.**
- **Reels.** Three printed reels (3P, 4P, 5P) on axles behind the bench. Each
  BNTECHGO spool is rewound once, through a printed roller straightener, onto an
  80 mm hub radius, which adds no new set [procedure-is-the-machine calc wave2
  §2]. The inner end comes out through the hub and is hand-crimped into an XH
  housing plugged into a small board in the hub: the **hub socket**.
- **The hub lead.** The reel stands still while an end is terminated, but the
  puller turns it about a turn per loom when it draws the length off (600 mm on
  an 80–95 mm radius). So the hub socket's wires run through a 6-circuit capsule
  slip ring on the axle ($9.99 [Prime]); a flying lead would have to be
  unplugged for every draw.
- **Feed and clamp.** The 4P runs through a belt feed with an encoder wheel into
  a channel clamp 0.2 mm under the ribbon's width. The clamp rides an **X
  carriage**: MGN12 300 mm rail with MGN12H carriage ($20.49 [Prime]) and a NEMA
  17 on a Tr8×2 screw ($27.99 [Prime]). **The clamp face is the cut line and the
  split root.** A hinged **fan block** for the 4P rides on the clamp, one per
  ribbon type, since a reel's type never changes during its run.
- **Contacts.** SXH-001T-P0.6 from its reel run along a fixed steel track from
  +X, flush with the applicator's track, continuous through the anvil and ~45 mm
  past it. The track has grooves along X under the lance line and under the
  carrier's slot line. An SMT-style sprocket feeder (borrowed-machines'
  [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md)) advances the
  strip on its own slots.
- **The press.** A side-feed OTP XH applicator on the VEVOR press's bed with its
  feed finger, pressure plate and shear punch removed, driven by a **3–4 mm
  eccentric** from a NEMA 17 with a 26.85:1 planetary ($41.91 [Prime]); a
  bullet-nosed **pilot** in the shear punch's pocket; a strain gauge on the
  eccentric rod and an AS5600 on the shaft ($7.99 for three [Prime]).
- **The insertion lane:** a real B4B-XH-A wafer on a test board, on a load cell,
  fed from a small XHP-4 magazine. **The draw lane:** a belt puller on a rail
  along +Y.

**What moves, for one end.**
1. **Feed out and touch off.** The last loom's cut left the 4P end flush at the
   clamp face. The clamp opens and the belt feed pushes the webbed end out along
   a covered floor until its copper faces touch a grounded tip stop, ~29 mm out
   for a 4P. Every conductor reads continuous through the hub as it touches; one
   that never touches, or a spread over ~0.1 mm, stops the end. The clamp closes.
2. **Strip, webbed (p7).** Two single-edge razors close across the whole width
   2.4 mm behind the stop, on steel stops at strand radius + 0.2–0.3 mm from the
   centre plane (AccuTec 0.009 in blades, $12.90 / 100 [Prime]). The stop drops
   away and the blades slide 3–4 mm toward the tip, pushing the whole slug (four
   jackets and three webs) off as one sleeve, ~40–60 N for a 4P
   [procedure-is-the-machine calc wave2 §7]. The blades are isolated, so a blade
   touching copper names the conductor through the hub. One backlit ELP frame
   reads all four bare lengths and insulation edges on one line.
3. **Zip from the slug's gaps (a7).** The tine comb comes in along −Y from beyond
   the tips. Its noses enter the ~0.98 mm gaps between bare bundles, meet each web
   at the strip line (already opened by the slug's tear), and drive the tears to
   1 mm short of the clamp face, where they stop. No nicker.
4. **Fan, equal-path.** The fan block swings down about a hinge at the clamp
   face and takes the conductors from 1.7 mm to 7.1 mm at its front face. Its
   grooves start at 1.7 mm where the conductors already lie, so capture begins at
   the root, limited only by the ribbon's pitch stack there (0.23 mm worst for a
   5P against 0.85 mm of half-pitch) [w3 §2]. **Each inner groove carries a
   vertical hump** that makes its path as long as the outer groove's: for a 4P
   the inner pair's hump is 3.3 mm over the fan's 16.7 mm, bent at R ~4.3 mm; a
   5P's centre conductor needs 5.1 mm over 21.4 mm at R ~4.5 [P3 §1]. Every tip
   recedes by the same 2.05 mm (4P) or 2.77 mm (5P), so the tip line and strip
   line stay straight; the 29 mm feed-out allowed for it.
5. **Dock.** X brings the clamp over the dock position, where the sprocket
   feeder has put four open contacts. **Grip pins on the carriage drop first**
   into the carrier's slots just beyond contacts 1 and 4, so the segment is on
   the carriage's X, and a small guillotine cuts the strip behind the segment.
   Then a cam drops the clamp and fan block ~3 mm onto three balls on hardened
   seats on the carriage, and every conductor settles into every contact at once
   (pressed in by a finger comb if the open wings are narrower than the jacket
   [calc F §4]). The hub socket reads each conductor to the grounded carrier:
   placement is confirmed before any force. The end uses N contacts.
6. **Crimp, one per revolution.** The carriage, floating ±0.5 mm in X on a light
   spring, indexes the docked row −X through the anvil one strip pitch per
   eccentric turn (~10 s). The pilot enters the slot beside the anvil contact
   before the crimpers touch and draws the row to the strip's own X. The rod gauge
   draws ~40–47 HX711 samples through the last 0.2 mm [P3 §5]; a curve out of band
   stops the shaft short of bottom and backs it off.
7. **Back at the dock position: pull and shear.** The feeder holds the next
   contacts back. A comb of pins on the carriage drops into every carrier slot,
   and a pad comes down on the crimped barrels; a hook pulls each conductor in
   turn to 20 N at the fan block face. The pull goes conductor → crimp → contact
   → tab (in compression) → carrier → slot pins, and the pad stops the contact
   pitching about its tab, which it otherwise does at 2.5–4.6 N [w3 §4;
   calc F §3]. Where the neck between box and conductor barrel takes a 0.3 mm
   blade, a blade dropped behind every box, stopping ~1.2 mm above the floor to
   clear the brush, takes the pull on the box's rear face instead (~25 MPa)
   [calc F §3]. Then a notched shear comb cuts all four tabs, and the carrier
   scrap and grips go to a chute.
8. **Insert (a6).** X moves to the insertion lane. The fan block lifts, and a
   2.5 mm closing block with plain grooves and the insertion clamp take the row.
   The humps are not pressed flat, so the fronts stand as a V staircase: for a 4P
   closed from 7.1 mm the outer pair ~1.85 mm ahead of the inner pair
   [P3 §10]. The clamp's jaw face is stepped to match. The nest's slide pushes the
   XHP-4 on; the load cell sees the outer pair's lances snap, then the inner
   pair's; the clamp follows home by slide-along jaws, and its forward push pulls
   the humps straight (0.06–0.23 N [calc F §5]). A spring-limited pull-back and
   the camera check each latch.
9. **Test.** The controller drives each wafer post and reads the hub socket:
   pin order, opens, adjacent shorts, and J2's cavity 3 open when the 3P reel
   runs J2.
10. **Draw and cut.** X moves to the draw lane. The puller grips the ribbon just
    behind the housing, by a fold around a bar ([a3](a3-backshell-that-ships.md)'s
    fold, 14–69 N from a 3 N clip [calc X §8]); the clamp opens; the puller draws
    J11's ~600 mm off the reel, measured on its encoder; the clamp closes; a razor
    guillotine cuts at the clamp face. J11 drops into the bin with its far end
    square, and the 4P end is flush at the clamp face for the next recipe, J3.

**What locates what, and the reference for fixed.** "Fixed" is the clamp face
for everything up to the dock; the carriage (and through the pilot, the strip's
own slot) at the dock and the crimp; the nest at insertion.

| Moment | Located | Against | Held to |
|---|---|---|---|
| Cut | tip line | guillotine running on the clamp face | ±0.05 mm [estimate] |
| Feed-out | every tip | grounded stop, touch-off through the hub | ±0.01–0.05 mm [calc W2 §6] |
| Strip | strip line; depth | blades 2.4 mm from the stop; steel stops to the channel floor | ±0.05 axial; ligament 0.2–0.3 ±0.08–0.12 RSS [procedure-is-the-machine calc wave2 §7] |
| Split root | tear end | clamp face | ~±1 mm |
| Fan | lateral 7.1 mm pitch; tip line | grooves; equal paths | ±0.1 lateral; tip line ±0.05–0.1 [estimate, groove path accuracy] |
| Dock | conductor into contact | kinematic seat on the carriage; segment on the carriage's grips | capture ~0 to ±0.5 mm (open-wing reading [P3 §2]) |
| Crimp, X | contact on the anvil | pilot in the carrier's own slot | ±0.02–0.05 mm [assumption, stamping] |
| Crimp, Y | insulation edge in the window | strip line and carrier edge, both referenced to the carriage and track | ~±0.15 mm RSS [estimate] |
| Crimp height | barrels | applicator dials; eccentric bottom set once to shut height | ±8–23 µm frame scatter, read as ΔF/k [calc X §9] |
| Length | loom | puller encoder from the clamp face | ±1–2 mm [procedure-is-the-machine calc wave2 §6] |

**What drives the crimp and carries its force.** NEMA 17 → planetary →
eccentric shaft in pillow blocks on the VEVOR frame's crosshead → rod →
applicator ram → crimpers → contact → anvil → applicator base → press bed. The
eccentric needs ~1.0–1.7 N·m against ~2.2–6 N·m for a 15–20 mm crank [P3 §5], so
the bench's NEMA 23 and DM542T stay in the cap-weld tube rotator. The carriage,
grips, track and fan block carry positioning loads only.

**How it knows.** One wire per conductor, through the hub socket, from the tip
stop to the wafer:
- touch-off at the tip stop (all N present, tips on one line);
- blade and tine touch on copper;
- one backlit frame of every bare length;
- continuity to the carrier at docking;
- a force curve and ΔF/k crimp height per contact, and a camera frame;
- a 20 N pull per conductor;
- latch events and pull-back;
- pin map and shorts through the real wafer;
- the loom's length.

Each end is logged with the reel's ID and the metre mark it came from.

**What the person does.**
- Once per spool: the rewind, straightening and hub-socket crimp, ~6 min, about
  three spools per five units.
- Per reel run: mount the reel and connect it; load the run's recipe list; keep
  the contact reel and the housing magazine; empty the bin and scrap cup.
- Per unit, four pair events at the partner nest, when called: J1 and J2 (put the
  half-housed housing in the nest; the machine inserts the second ribbon through
  a straight closing block); J4 and J7 (the machine inserts the first ribbon
  through a gapped closing block, J4's 4P into 1 and 3–5, J7's 5P into 1–4 and 7;
  the person inserts the other ribbon's five crossing contacts by hand
  ([a6](a6-housing-as-last-comb.md))).
- Also per unit: label 10 housings; make every far end.
- About **12 attended minutes a unit**, against ~46 by hand on the same task
  library [P3 §7, estimate]. The longest stretch alone is one 4P reel run: 35
  ends at ~5.5 min each, ~3.5 h, unless pair calls interrupt it; half-housed
  housings waiting in a magazine by the nest keep them out.

## Steps it covers and what it hands back

- **Machine:** feed and touch-off, strip, split, fan, contact supply from the
  reel, placement by docking, crimp, crimp verification, pull, tab cut,
  insertion of single-ribbon ends and first ribbons, test through the reel, draw
  to length and cut.
- **Person:** spools and rewinds, recipe lists, contact and housing supply, pair
  events and J4/J7's five crossing contacts, labels, far ends.

## What the pairing does that neither side does alone

| | [a2e](a2e-docked-strip-through-a-feedless-applicator.md) alone | p6 alone | a9 |
|---|---|---|---|
| Ribbon pallet | one per end, loaded by hand from a cut length | the reel clamp | the reel clamp; one fan block per ribbon type |
| Far-end port | a pogo block on each loom's cut far end | hub socket | hub socket, through a slip ring |
| Crimp orientation | floor-down on the anvil | a tip-down hand-tool module that rolls every contact 90° (into-the-housing's finding) | floor-down on the anvil |
| Crimp height | applicator dials | the SN-2549's fixed dies | applicator dials |
| Contacts per unit | ~67 (segments laid by hand) | a revolver loaded by hand | **55**, N per end from the reel; an 8,000 reel is ~145 units, $1.29 a unit [calc F §7] |
| Cut and strip | a guillotine and ring scorer after the fan | V-jaws per conductor, or p7 | the loom-freeing cut plus one p7 stroke, before the split |
| A bad crimp costs | the loom's length, if cut first | ~6 mm of reel | the end's whole split, ~22–33 mm of reel; ~37 mm per unit at 2 % crimp failures [P3 §12]; never a loom |
| The finished loom | outer conductors 1.2–2.5 mm long: a 3–5 mm arc [calc F §5] | straight | every conductor one length from the root |
| Person, per end | ~40–220 s | stage-dependent | ~0 for single-ribbon ends |

## Stage 0, with no motors

The same reel clamp on a hand-slid X plate with ball detents at strip pitch:
- p7 as a lever with two razors on shim stops; a7's hand comb on a rail;
- the equal-path fan block closed by a lever;
- a strip segment laid on the shelf by hand, docked by a lever, continuity on
  LEDs through the hub socket;
- **the crimp, today:** tack every insulation barrel with a notched comb, shear
  the tabs, and crimp each tacked contact in the SN-2549 by hand
  ([a10b](a10b-tacked-row-into-the-hand-tool.md));
- **the crimp, once an applicator arrives:** one stroke per contact by pumping
  the VEVOR jack against a hard-stop collar over the applicator
  (borrowed-machines' zero-build test);
- a luggage-scale pull, the shear comb on a lever, a hand insertion jig;
- draw to a peg and cut at the clamp face.

Docking, p7's slug and the equal-path fan can be tried the week they are printed
with no crimp tool (dock, photograph, read continuity). The applicator is the
long-lead item, with no Prime listing; eBay and Alibaba list it at $150–250 plus
shipping [force-and-form key findings].

## Where this differs from procedure-is-the-machine's X1, and why

- **The lead twists at the draw.** The reel stands still while an end is made,
  but the puller turns it about a turn per loom, so the hub socket needs a slip
  ring (or an unplug per draw).
- **Grips before the dock.** With the contacts on a fixed track and the fan block
  on the carriage, their X agreement at docking would otherwise rest on the
  feeder's and the leadscrew's accuracy together. Dropping the grips first puts
  the segment on the carriage's X.
- **The V staircase at insertion comes from the humps.** The conductors are cut
  to one length at the root, so once the humps are pulled straight the loom is
  equal-length; the V exists only while the humps stand. Pressed flat in the
  closing block instead, the fronts would stand on one line within the 2.5 mm
  fan's own 0.1–0.3 mm, for a straight gang push (up to 39 N for a 4P [calc §8])
  or Sogang's lean-and-slide.

## Major unresolved problems

- **p7's flank tear.** Two straight scores leave 144–200° of each jacket to tear
  from full wall [calc W2 §5]. A ragged edge worsens the silicone bulge the
  insulation barrel pushes into the window [calc W2 §9].
- **Starting the zip from a slug's gap** rests on the neck thickness t_n well
  under ~0.6 of the wall (repo Open item 5).
- **Closing the equal-path fan block** over tine-fanned conductors, humps
  included, without a conductor riding up; and the vertical set the humps leave.
- **Parted length:** 22 / 27 / 33 mm (3P / 4P / 5P) at 7.1 mm including the
  recession allowance [calc F §8]; a backshell there stands 44–55 mm above the
  board. Derek's split-length question.
- **The applicator scan:** which parts unbolt, whether the shear punch's pocket
  takes a pilot, whether the ram has a return spring, and the downstream room
  (~32–35 mm for a 5P with grips in the end slots [P3 §4]).
- **The eccentric's frame:** pillow blocks on the VEVOR crosshead at shut height,
  with a stiffness still to be found.
- **The reel:** whether a BNTECHGO spool's inner end is reachable without a
  rewind, and whether the straightener marks silicone or twists the web.
- **Batching:** per-reel runs of 5–11 units hold finished looms and half-housed
  pairs ahead of units. Derek's call.
- **J4 and J7:** five crossing contacts a unit stay with the person, and the
  gapped closing blocks are per-loom parts; the J7 wiring choice would make J7
  straight ([a6](a6-housing-as-last-comb.md)).

## Related ideas

- In this directory: [a4](a4-spool-as-magazine.md),
  [a2e](a2e-docked-strip-through-a-feedless-applicator.md),
  [a5](a5-part-fan-strip-in-the-pallet.md) (order B), [a6](a6-housing-as-last-comb.md),
  [a7](a7-zip-station.md), [a3](a3-backshell-that-ships.md) (the puller's grip),
  [a10b](a10b-tacked-row-into-the-hand-tool.md) (stage 0's crimp).
- Other explorers: procedure-is-the-machine
  [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md),
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md),
  [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md),
  [p5](../../procedure-is-the-machine/ideas/p5-camshaft-one-revolution-per-conductor.md);
  borrowed-machines [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md),
  [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md),
  [b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md).

## What rests on assumptions

- Strip pitch ~7.1 mm [Würth analog]; the stamping's slot-to-contact tolerance.
- That the OTP applicator is laid out like MKS-L [assumption].
- Groove path accuracy for the equal-path fan [estimate].
- Person-time and run-time figures [estimate, one task library].

## Labels

As [a1](a1-pallet-tour.md#labels) and [a2](a2-two-pallets-meet.md#labels);
[procedure-is-the-machine calc wave2 §n] is its
[`wave2.out.txt`](../../procedure-is-the-machine/calc/wave2.out.txt).
