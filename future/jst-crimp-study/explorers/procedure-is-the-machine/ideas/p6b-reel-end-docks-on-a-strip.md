# p6b The reel end docks on a strip: every contact placed at once, a bought applicator crimps

Sketch: [`../sketches/p6b-reel-end-docks.svg`](../sketches/p6b-reel-end-docks.svg)
(schematic side view and order). Numbers:
[`../calc/exchange_ribbon_w3.out.txt`](../calc/exchange_ribbon_w3.out.txt) (cited as
[calc P3 §n]), [`../calc/wave2.out.txt`](../calc/wave2.out.txt) and
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as [calc wave2 §n] and
[calc wave3 §n]). A longer step-by-step walk-through, with every source, is
section X1 of this view's
[reading of ribbon-as-pallet](../../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md).

**A branch of [p6](p6-spool-end-bench-that-grows.md), and a combination.** It
keeps p6's reel (rewound onto an 80 mm hub radius, the inner end in a hub socket),
its clamp face as the cut line and split root, terminate first and cut last, and
the puller. It adds [p7](p7-strip-before-split.md)'s whole-end strip, and from
ribbon-as-pallet:
- [a2e](../../ribbon-as-pallet/ideas/a2e-docked-strip-through-a-feedless-applicator.md):
  a fanned ribbon docks onto a segment of contact strip so every conductor
  settles into every open contact at once, and a bought side-feed applicator with
  its feed removed crimps them one per turn of a short eccentric;
- [a7](../../ribbon-as-pallet/ideas/a7-zip-station.md): a split torn back and
  stopped at the clamp face;
- [a6](../../ribbon-as-pallet/ideas/a6-housing-as-last-comb.md): a closing block
  and insertion clamp, and a real wafer as the test nest;
- an **equal-path fan**: grooves of equal length, so tips and strip lines made
  before the fan stay on one line after it.

Where p6's stage 1 needs a hand tool on its side or made steel to crimp upright,
here every contact is crimped floor-down on the applicator's own anvil, from
bought dies.

## Picture it: the 4P reel run making J11

**Where things start.**
- **Reels** as in p6, each with its hub socket. A flying lead from the controller
  plugs into the running reel's socket; the reel stands still while an end is
  made, so the lead never twists.
- **Feed and clamp.** The 4P runs through a belt feed with an encoder wheel into
  a channel clamp 0.2 mm under the ribbon's width. The clamp rides an **X
  carriage** [Prime: MGN12 rail, $20.49; NEMA 17 with integrated T8×2 lead screw,
  $27.99]. A hinged **fan block** for the 4P rides on the clamp; a reel's ribbon
  type never changes during its run, so one block per ribbon type.
- **The contacts.** SXH-001T-P0.6 on its reel [xh-facts §6] runs along a steel
  track flush with the applicator's own, advanced on its own slots by a sprocket
  (borrowed-machines b2's). No XH strip had a Prime listing.
- **The press.** An OTP side-feed XH applicator (no Prime listing; $150–250 on
  eBay or AliExpress [force-and-form]) stands on the VEVOR 12-ton press's bed with
  its feed finger, pressure plate and shear punch removed. A **3–4 mm eccentric**
  drives its ram, because with the feed gone the ram only has to clear the next
  open contact's wings: 1.0–1.7 N·m [calc P3 §5], inside a NEMA 17 with a 26.85:1
  planetary [Prime: STEPPERONLINE 17HS19-1684S-PG27, $41.91]. A bullet-nosed
  pilot sits in the removed shear punch's pocket. Gauges on the eccentric rod and
  an AS5600 on the shaft [Prime: AS5600, $7.99] log force against angle.
- **The insertion nest** is a real B4B-XH-A wafer on a small board, on a load
  cell, fed from a short XHP-4 magazine. **The puller** is a belt carriage on a
  rail along the bench front.

**One end.**
1. **Feed-out and touch-off.** The last loom's cut left the 4P end flush at the
   clamp face. The feed pushes the webbed end out along a covered floor until its
   copper faces touch a grounded tip stop, ~29 mm out. Every conductor reads
   through the hub socket as it touches; a missing one, or a spread over ~0.1 mm,
   stops the end.
2. **Strip, webbed (p7).** Two single-edge razors close above and below across
   the whole width 2.4 mm behind the stop, stop on steel at strand radius +
   0.2–0.3 mm, and slide 3–4 mm toward the tip, a toothed pad pair carrying the
   slug [calc wave3 §5]. One backlit frame reads all four bare lengths on one
   line.
3. **Zip from the slug's gap (a7).** A tine comb comes back from beyond the tips;
   its noses enter the ~0.98 mm gaps between bare bundles and drive the tears
   back to 1 mm short of the clamp face.
4. **Fan, equal-path.** The fan block swings down and takes the conductors from
   1.7 mm at the clamp face to 7.1 mm (the strip's pitch) at its front face. Each
   inner groove carries a vertical hump that makes its path as long as the outer
   one's: 3.3 mm over 16.7 mm for a 4P, 5.1 mm over 21.4 mm for a 5P's centre
   [calc P3 §1]. Every tip recedes by the same 2.05 mm (4P) or 2.77 mm (5P), so
   the tip line and the strip line stay straight.
5. **Dock.** X brings the clamp over the dock position of the track, where the
   sprocket has put four open contacts. A cam drops the clamp and fan block ~3 mm
   onto three balls in V-grooves [Prime: chrome steel balls, 6 mm, $6.65], and
   every conductor settles into every contact at once. Grip pins drop into the
   carrier's end slots, and a small guillotine cuts the strip behind the segment:
   N contacts per end, no spares, ~55 a unit [calc P3 §11]. The hub socket reads
   each conductor to the grounded carrier: **placement confirmed before any
   force.**
6. **Crimp, one per revolution.** The carriage indexes the docked row through the
   anvil one strip pitch per eccentric turn (~10 s). The pilot enters the slot
   beside the anvil contact before the crimpers touch; the rod gauges take ~40–47
   samples through the last 0.2 mm [calc P3 §5]; a curve out of band stops the
   shaft short of bottom and backs it off.
7. **Pull and shear.** A comb drops a thin blade behind every box; a hook pulls
   each conductor in turn at the fan block's face to 20 N, the load going
   conductor → crimp → box → blade, never through the carrier. A notched shear
   comb then cuts all four tabs.
8. **Insert (a6).** The fan block lifts; a closing block and the insertion clamp
   take the row. The closing block's grooves are plain, so the fronts come free
   as a V staircase (for a 4P closed from 7.1 mm, the outer pair ~1.85 mm ahead
   of the inner [calc P3 §10]). The nest pushes the XHP-4 on, and its load cell
   sees the outer pair's lances snap, then the inner pair's.
9. **Test.** The controller drives each wafer post and reads the hub socket: pin
   order, opens, shorts, and J2's cavity 3 open when the 3P reel runs J2.
10. **Draw and cut.** The puller clips the ribbon just behind the housing (a fold
    round a bar multiplies its grip), draws J11's ~600 mm off the reel, and a
    razor guillotine cuts at the clamp face. The next end is flush and ready.

## What locates what

| Moment | Located | Against | Held to |
|---|---|---|---|
| Feed-out | every tip | grounded stop, touch-off through the hub | ±0.01–0.05 mm [ribbon-as-pallet calc stations_wave2 §6] |
| Strip | strip line; depth | blades 2.4 mm from the stop; steel stops to the channel floor | ±0.05 mm axial; ligament 0.2–0.3 ±0.08–0.12 mm RSS [calc wave2 §7] |
| Fan | lateral 7.1 mm pitch; tip line | grooves; equal paths | ±0.1 mm lateral; tip line ±0.05–0.1 mm [estimate] |
| Dock | conductor into contact | kinematic seat on the carriage; carrier on the fixed track | ±0.16 mm RSS placement against 0.14–0.54 mm of half-gap [calc P3 §2] |
| Crimp, X | contact on the anvil | pilot in the carrier's own slot | ±0.02–0.05 mm [assumption] |
| Crimp height | barrels | applicator dials; eccentric's bottom set to shut height | the applicator's own |
| Length | loom | puller encoder from the clamp face | ±1–2 mm [calc wave2 §6] |

"Fixed" is the press bed and the track for the crimp, and the clamp face for
everything along the ribbon.

## What drives the crimp and carries its force

NEMA 17 → planetary → eccentric shaft in pillow blocks on the VEVOR frame's
crosshead → rod → applicator ram → crimpers → contact → anvil → applicator base →
press bed. The carriage, pallets, grips and track carry positioning loads only.

## How it knows it worked

One wire per conductor, the hub socket, from the tip stop to the wafer: touch-off,
blade and tine touch on copper, one backlit frame of every bare length,
continuity to the carrier at docking, a force curve per contact, a 20 N pull
through the box, lance snaps, and pin map and shorts through the real wafer.

## Steps it covers, and what it hands back

- **Automated:** flush cut, strip, split, fan, supply contacts (strip and
  sprocket), place every contact on its conductor at once, crimp, pull, shear,
  insert single-ribbon ends, test pin to pin, draw to length, cut.
- **Handed back:** the rewind once per spool; mounting reels and the contact
  reel; the housing magazine; the four pair events a unit at the partner nest
  (J1 and J2 placed; J4 and J7 placed, and their 5 crossing contacts inserted by
  hand); labels; every far end. About 12 attended minutes a unit on the task
  library that gives ~46 by hand [calc P3 §7; estimate]. The longest stretch
  alone is one 4P reel run, ~3.5 h.

## Branch kept beside it: p6b-fed, one conductor at a time (force-and-form f2c at the reel)

force-and-form's [f2c](../../force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md)
keeps the applicator's feed and brings one conductor at a time to a pre-fed
contact. At the reel: p7's single frame measures every insulation edge, and
f2c's carriage sets each conductor's depth into the applicator individually from
that frame; the applicator's strip and anvil are grounded, so a conductor laid
into the pre-fed contact reads through the hub socket before each stroke; the
puller replaces a push-out. It needs no equal-path fan and no docking, and it
still needs the split into planes that f2c's two 5.0 mm output pallets want
(change-the-question [c1](../../change-the-question/ideas/c1-half-rows.md)).

## Contribution

- **Placement of every contact at once, confirmed electrically before any
  force**, on the reel where a failure costs reel.
- **Upright crimps from bought, aligned dies**, with the press drive reduced to a
  small planetary stepper because the feed is gone.
- **The order does the registering:** strip before split while the web holds the
  pitch, an equal-path fan so the strip line survives the fan, docking because
  the tips are on one line.

## Major unresolved problems

- **p7's flank tear** and the slug push (p7's own open problems).
- **Closing the equal-path fan block** over tine-fanned conductors, humps
  included, without a conductor riding up; the humps leave vertical set that
  the closing block has to straighten.
- **Parted length**: 22–33 mm (3P–5P) at 7.1 mm pitch including the recession
  allowance. That is Derek's split-length question.
- **The applicator**: which contact it is tooled for, which parts unbolt, whether
  the shear punch's pocket takes a pilot, and its shut height. It is the
  long-lead item with no Prime listing.
- **Docking capture** depends on whether the clone drawings' barrel widths are
  inside or outside dimensions: 0.14–0.54 mm of half-gap [calc P3 §2]. The $4.71
  strip settles it.
- **A redo costs the whole parted end**, ~35 mm of reel, ~37 mm a unit at a 2 %
  crimp failure rate [calc P3 §12]; no loom is lost.
- **J4 and J7**: 5 crossing contacts a unit stay with the person.
- **Batching**: per-reel runs of 5–11 units hold finished looms and half-housed
  pairs ahead of units.

## What rests on assumptions

- The OTP applicator's layout being like JST's MKS-L, and its ram having a
  return spring.
- The pilot's accuracy in a stamped slot.
- Tear forces and the pad drive (p7).
- Minutes and run lengths [estimate].
