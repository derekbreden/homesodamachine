# D. Gauge-set, lock-held — the setup tool is not the holding tool (sketch level)

Not developed as far as A–C. Kept because it stores the pose in a different place.

## Picture it (original, and branch D-r as it now stands)

**Original.** A printed gauge sits on the tube's rim at the weld station and
receives the gun shell in exactly one position. A general lockable holder (an
articulated arm) takes the shell while the gauge sets it, then locks, and the
gauge comes out sideways past the wire. The gauge references this tube, so each
tube's length and seating are absorbed at setup. Nothing touches the tube during
the weld.

**D-r (who-moves-what's split).** Each part of the pose goes to whatever holds it
at its own rate:

- the angles to a printed recipe block;
- yaw and radial position to lead-screw slides, where stopping turning is locking;
- per-tube height to the work's Z screw, found by a small retractable foot on the
  shell that touches the plate face and bore on the free +Y side, between tacks.

**D-m.** The foot reads a dial at eight angles: the tube's runout map.

**Fixed to.** The holder's base and the slides are on the bench; the rim gauge and
the foot reference the tube.

Sketch: `../sketches/d-gauge-foot.svg` (true pose: original gauge, foot pads, stack).

## Major unresolved problems

1. **Lock shift** of real single-knob holders (original D).
2. **Calibrating the foot's pads** against the optical dot.
3. **Whether a wire touch-off** can replace the Z pad.
4. **Heavy-duty lockable holders.** Prime indicator arms are sized for grams.

## The idea

Split the two jobs that A and B give to one mechanism:

- **Setting** the pose is done by a printed *pose gauge* that sits on the tube's rim
  at the station (registering on the rim top and the bore of the lip, ahead of and
  behind the dot) and receives the gun shell in exactly one position — nozzle
  socket plus two locating pins on the shell. The gauge *is* the recipe: a new pose
  is a new print with a version number on it.
- **Holding** is done by a general lockable support (an articulated arm with a
  single central lock, or a ball clamp on a post) that accepts whatever pose it is
  given and then locks.

Sequence: unlock holder → seat gauge on rim → push shell into gauge (holder
follows) → lock holder → slide gauge away → dry run → weld. The gauge references
this tube, so per-tube length/seating is absorbed at setup, like C, but nothing
touches the tube during the weld, like A/B.

```
      holder (locks)                    setup                    weld
         o====o                  o====o                    o====o
               \                       \                         \
              [shell]                 [shell]                   [shell]
                 \  nozzle               \                          \
   rim  ___       \          rim ___[GAUGE]___          rim ___      \
        |  |_______\             |  |_______\               |  |______\  <- dot
        |  plate    .            |  plate                   |  plate
```

## First breaks

- **Lock shift.** Single-knob articulated arms move their tip when locked
  (typically tenths of a millimetre or more at the tip; not measured here). With
  the gauge still in place while locking, the gauge takes that shift as a force;
  when the gauge slides away the gun springs back by the stored strain.
  *Repair:* the holder ends in a small stage (two or three screws) that is locked
  *last*, after the coarse lock, while the gauge is seated and nothing is
  preloaded; the coarse lock's shift is taken up before the fine lock closes.
  *Leaves:* real shift of real holders, and whether the fine lock itself shifts.
- **Getting the gauge out.** The gauge surrounds the nozzle at the rim. It must be
  split or open on one side so it can slide out sideways past the wire. The wire
  stickout must be short during gauging.
- **Stiffness of general holders** with a ~1 kg gun at 300 mm is low; they sag and
  creep. Pair with a balancer (as in C) so the holder only positions.

## Why it is worth keeping

The pose lives in a cheap, versioned, printable object that anyone can put on a
rim; the holder can be almost anything. It is the most direct form of "knowledge
in equipment" for handing the job to a second person, and gauges can also
*check* A/B/C poses (drop the gauge on, see if the shell mates).

## Parts

Not sourced this wave (a heavy-duty single-lock articulated arm is the part to
look for). Printed gauge.

---

## Wave 3 — branch D-r and D-m (from who-moves-what), with sequence notes

who-moves-what located the difficulty in one assumption: that one gauge sets all
six freedoms per tube and one general holder holds all six. They split the pose by
how often each part changes:

| Part of the pose | Changes | Set by | Held by |
|---|---|---|---|
| roll, hole tilt | per recipe | a printed recipe block ("the gauge is the recipe", made literal) | the block |
| yaw, radial | per recipe | X/Y dials (yaw 1.08 mm/°) | the slides' own lead screws: no lock step, so no lock shift |
| height | per tube | a retractable gauge foot on the shell (two pads on a 3 mm cam slide) | the work's Z screw |

**D-m (measuring foot):** a dial on the Z pad instead of a hard stop, read at the
eight between-tack angles. Set height to the mean; the eight numbers are the tube's
runout map.

**I take both.** D's original rim gauge stays, as the tool that *checks* a pose (drop
it on, see whether the shell mates) and that first sets a new recipe's dials.

**Sequence notes:**

- At the true pose (dial 30) the wire and barrel are on −Y. The foot's pads on the
  +Y side, 8 mm along the seam from the dot, are on the free side.
- The rotator becomes part of the gauge sequence:
  1. Index 22.5° off the first tack (between tacks).
  2. Touch the foot, then read (D-m) or set.
  3. Retract the foot.
  4. Index back to tack 1.

  This is phase 7 extended, and the pedal's degree readout is enough for the
  indexing. The eight D-m readings belong on the per-tube record (kit K7).
- With the stand-hung plate head of my exchange file, the plate face is already at P.
  The foot then only *measures* (D-m); height is set by the head and rim flag.
