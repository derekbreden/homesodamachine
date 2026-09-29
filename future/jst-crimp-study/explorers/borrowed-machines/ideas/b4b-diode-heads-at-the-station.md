# b4b — Two small diode heads at the station: score and slit in the pose the crimp uses, no dock, no flip

**Branch of [b4](b4-laser-slits-and-scores.md).**

**What it changes:** the cassette does not go to an engraver. Two hobby diode
laser modules, the kind sold by the thousand as bolt-on heads for open-frame
engravers, are mounted one above and one below the ribbon at a station on
[b1](b1-press-and-applicator-with-shuttle.md)'s shuttle rail, or at
[b8](b8-spool-fed-borrowed-line.md)'s or [b8b](b8b-flat-spool-line-over-a-crown.md)'s
work clamp. The shuttle's own X and Y move the ribbon under them. Both faces
are worked with the ribbon in one pose, so there is no flip and no dock, and
the H2C stays printing. procedure-is-the-machine proposed it as the way to cut
b4's person time.

Sketch: [`../sketches/b4b-diode-station.svg`](../sketches/b4b-diode-station.svg).

**What stays from b4:** score, don't strip; scores before slits; slits that stop
at the score line so the tip stays webbed; one pinch pull for the whole tip;
the cassette datum.

Labels: [Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [calc wave2 §n] is this explorer's
[`wave2.out.txt`](../calc/wave2.out.txt).

## Picture it

- **Where things start.** The cassette sits on the shuttle as in b1, its end
  flush-cut and not yet split. The ribbon end hangs over a slot in a steel bed
  plate, so its underside is open.
- **The heads.** Two fixed-focus 450 nm modules, 5–10 W optical (LASER TREE
  10 W optical module with air assist, $137.17 each, 71 ratings [Prime]), one
  looking down through the top of a light-tight box, one looking up through the
  bed slot, each with an air-assist nozzle. They do not move; the shuttle does.
- **Score.** The shuttle sweeps Y at the strip-line X. The top head scores every
  crown on the top face; the bottom head does the bottom face in the same sweep,
  each to ~60–70 % of the wall ([b4](b4-laser-slits-and-scores.md), score depth).
- **Slit.** The shuttle holds Y on each web in turn and sweeps X from the clamp
  edge to the score line. Top and bottom heads each slit to about the mid-plane.
- **Pull.** Two TPU pads on a servo close on the webbed tip and the shuttle backs
  off 3 mm. The slug drops into a cup. A brush and an air puff clean the strands.
- **Look.** A backlit frame of every stripped tip.
- **Enclosure.** The station is a light-tight box that the shuttle enters
  through a brush slot, with an interlock on its lid and a fan ducted outdoors.

**What locates what; the reference for "fixed."** The shuttle's axes, which
already carry the cassette datum to the crimper. The strip line and the root
are placed in the coordinates the crimp uses, so nothing is re-registered
between laser and crimp.

**What drives and carries the force.** No cutting force; the pull (4.7–13 N a
conductor at a 60 % score) is carried by the cassette clamp through the
shuttle's X axis, as in b4.

**How it knows it worked.** The backlit frame of each tip after the pull, as in
b4; a conductor that keeps its slug is scored once more in place and pulled
again.

**What the person does.** Nothing at the station beyond what b1 already asks:
the cassette arrives, is scored, slit, pulled and folded, and goes to the
applicator on the same rail. A redo (a whole end cut back ~6 mm) is scored
again in place.

## Steps it covers and what it hands back

- **Covers:** split (web slits), strip (crown scores and pinch pull), a backlit
  check.
- **Hands back:** nothing new at the station; the cassette loading, fold lid and
  all crimping belong to the crimper it serves.

## What it adds and what it costs

- **Adds:** no dock, no flip, no module swap on the H2C, a redo handled
  locally. With it, b1's person time is ~22–27 min a unit against 46 today
  [calc wave2 §5, counted with b6's rip in the same row; b4b's person time is the
  same or less].
- **Costs:** a Class 4 laser at a bench station, with an enclosure, interlock,
  fume path and eye protection of its own (450 nm safety glasses are a sourcing
  request); two lenses facing silicone ash, the lower one facing up into falling
  ash.

## Major unresolved problems

- **455 nm on this silicone:** char, residue, depth control, all untested (as in
  b4).
- **The lower head's window** fouling with ash and silica.
- **Enclosure and interlock** around a moving shuttle.
- **Fume path.**

## What rests on what

- **Facts:** the module listing [Prime].
- **Calculations:** person minutes [calc wave2 §5].
- **Assumptions:** 5–10 W optical modules score 0.3–0.35 mm of silicone in a few
  passes; shuttle positioning ~0.05 mm, as in b1.
