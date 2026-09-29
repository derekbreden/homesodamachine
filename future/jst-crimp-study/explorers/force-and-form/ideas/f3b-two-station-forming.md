# f3b — Branch of f3: form at a light station, finish at another

Explorer: force-and-form. Parent: [`f3-knee-micropress.md`](f3-knee-micropress.md).
Numbers: [`../calc/stroke_model.out.txt`](../calc/stroke_model.out.txt) §1–2,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt).
Combinations built on it: [`f9-tack-station-feeds-crimp-station.md`](f9-tack-station-feeds-crimp-station.md)
(station A as the alternative light station) and
[`f9b-tack-on-the-strip.md`](f9b-tack-on-the-strip.md) (station A as a gang
curl tack on the strip).

## Picture it

The crimp stroke has two very different halves
([`../sketches/force-stroke.svg`](../sketches/force-stroke.svg)):
- **Shaping.** The wings curl over about 0.7 mm of travel at tens to a few
  hundred newtons.
- **Coining.** The last 0.1–0.2 mm needs 0.75–2.4 kN.

This branch splits them across two stations.

- **Station A — capture, thread, curl.** A light, open machine.
  - Steel dies in a frame driven by a small servo or NEMA 17, with room for
    cameras.
  - Everything f3 does before its crimp happens here: strip feed, flush pilot
    pin, capture, look, neck blade, thread.
  - The crimpers then come down only until the wing tips land on the strands:
    the end of the flat curl plateau, roughly 150–450 N at 0.15–0.2 mm above
    bottom [calc: stroke_model §1].
  - The insulation barrel is crimped fully here (30–130 N).
  - What leaves station A is a contact whose insulation crimp is done and whose
    conductor wings are curled closed around the strands, not compacted. The
    conductor cannot fall out; contact and wire are one piece.
- **One product, three finishes.** Station A commits to none of them, and the
  finish can differ per loom or change later [change-the-question on f3b]:
  - **coin** at a small, stiff steel press with a ~0.3 mm working stroke and
    the same B profile (an eccentric of 1–2 mm throw, a wedge, f3's knee, or
    the shop press), crimp height set and re-touched there;
  - **crimp** by hand in any single die (the SN-2549 today), where the
    contact now arrives already on its wire, square and at depth;
  - **solder** (change-the-question c3), outside JST's support.
- **What locates what.** At A, f3's: the strip's pilot hole on a flush pin,
  then the capture. At a coining station B, the curled crimp's own width in the
  channel's flare (laterally), the box against a steel stop (axially, ±0.05 mm)
  and the anvil's cradle (roll).
- **What drives and carries the force.** At A, a small servo or NEMA 17 into a
  light frame, stopped on the curve's shape (the end of the curl plateau), not
  on a height. At B, a stiff, very short stroke in steel.
- **How it knows.** A's force curve shows the plateau's end; a camera frame
  after the curl shows any strand outside the wings before anything is
  committed as good; B's re-touch reads the final height.
- **The person.** As f3, plus carrying each part from A to its finish, unless
  the uncut carrier strip carries it one pitch at a time.
- **Without a motor.** Station A on a hand lever, and the finish in today's
  SN-2549: the contact arrives at the hand tool already on its wire, square and
  at depth.

## What changes from f3

- **Station A's force is small.** Per contact, the end of the curl plateau plus
  the insulation crimp is ~180–580 N. A single station A is harmless in a
  printed frame, which opens ~0.16 mm at 450 N [calc: force_loop §1], because it
  stops on the force curve's shape, not on a height.
- **A gang station A is not small.** A half-row of 2–5 contacts takes
  ~0.4–2.9 kN, past the ~450 N at which a printed frame stays harmless
  [change-the-question on f3b]. A gang station A wants a steel local stop, or it
  splits again: gang the insulation tack alone (change-the-question c1b's
  66–660 N) and curl one contact at a time.
- **Station B barely moves.** Its stroke is so short that its drive can be
  crude and very stiff. With the strip as the transfer, several station-B
  anvils can sit at the strip pitch and coin several contacts per stroke,
  which meets f5.
- **An inspection point after curl and before coin.** A strand that escaped
  outside the wings is visible after station A. It is still scrap, but it is
  caught before any record says "good".

## Where station A sits among the other "put together, then join" ideas

| Idea | What holds contact to wire before the heavy stroke | Force |
|---|---|---|
| change-the-question c1b (tack first) | insulation barrel closed loosely | 66–660 N per half-row |
| **f3b station A** | insulation crimped, conductor wings curled onto the strands | ~180–580 N per contact |
| change-the-question c3 (fold and solder) | both barrels folded, no coining | tens to ~300 N |

Wings curled round the strands hold a contact more firmly than an insulation
tack does on silicone [estimate]: the tack's grip on this wire is a few newtons
at most ([`f6`](f6-two-blades-two-drives.md) [calc: wave2 §5]), while curled
wings trap the strands mechanically. That shrinks c1b's first open problem,
the tack's grip under a carriage's side loads.

## What was tried against it

1. **Re-registration.**
   - *Conflict.* The coining crimper has to meet the curled B exactly where
     station A left it. Laterally, the crimp's width is the channel width, so
     the flare self-centres it. Axially, the box against a steel stop gives
     about ±0.05 mm. Rotationally, a curled crimp is not flat-bottomed like an
     open barrel.
   - *Repair.* The anvil's cradle shape.
   - *Still open.* Whether a second die meeting a curled, sprung-back B
     produces the same compaction pattern as a single stroke.
2. **Springback between stations.** Curled wings open a little when the load
   comes off [estimate: tens of µm]. The flare re-gathers them; the arches
   reshape them.
3. **It is a non-standard process.** JST's two-step tools split the crimp by
   barrel (conductor, then insulation), not by phase (curl, then coin)
   [mfr S4, prior-art §4]. Nothing published says a curl-then-coin B-crimp is
   equivalent to a one-stroke B-crimp. The reloading argument of f3's
   "chase the height" variant [calc: wave2 §10] applies only if station B's die
   meets the crimp in the same place station A left it; a shifted die starts a
   new deformation, not a continued one.

A further variant, recorded and not developed: coin in narrow bands, a 0.4 mm
die walked along the barrel in three or four presses. Metal flows sideways out
of a narrow band instead of being confined, so the compaction pressure a band
reaches is lower [estimate]. It is the least standard of all.

## One experiment answers four ideas

Section and pull ten crimps on the ribbon made each of four ways
[change-the-question on f3b]:
- in one stroke (f3);
- insulation first, then conductor (c1b);
- curl, then coin (f3b);
- fold, then solder (c3).

f3's press makes all four; a non-ratchet PA-09 makes the first two; the JST
reference lead gives the target for the first. machine-that-sees-and-learns'
v3 could run it unattended overnight.

## Major unresolved problems

- **Crimp quality** of a two-die, curl-then-coin B-crimp. This is the whole
  branch's risk.
- **Transfer.** The strip carrying parts from A to B needs the tab uncut until
  B, and the conductor then trails from the strip across two stations.
- **Two die sets** cost more.

## Which conclusions rest on assumptions

- **Where the curl plateau ends** (150–450 N at 0.15–0.2 mm) is the model
  family's shape, not measurement.
- **Springback size** is an estimate.
- **Curled wings grip better than a tack** is an estimate until c1b's tack is
  pulled.
