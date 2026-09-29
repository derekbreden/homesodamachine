# b4 — A laser engraver slits the webs and scores the strip line in the cassette

The mass-produced machine here is the hobby laser engraver. It may be a module
away from Derek's own H2C printers: Bambu's laser upgrade kit fits the H2C. The
engraver does the two steps where soft, tearing silicone defeats blades:
splitting the web between conductors and scoring the tip for stripping. It works
on a ribbon end clamped in the cassette that
[b1](b1-press-and-applicator-with-shuttle.md),
[b1b](b1b-applicator-in-slow-crank-press.md) and
[b2](b2-hand-crimper-in-a-frame.md) use, so the split root and the strip line
come out referenced to the cassette's datum.

**Branch:** [b4b](b4b-diode-heads-at-the-station.md) puts two small diode
heads at the crimp station instead of taking the cassette to an engraver.
**Feeds:** b1, b1b, b1c, b2 (shuttle-presented), and
[b3](b3-gantry-carries-the-crimp-head.md), which needs its strip line cut while
the ribbon is flat.

Sketch: [`../sketches/b4-laser-score.svg`](../sketches/b4-laser-score.svg).

Labels: [calc geometry §n], [calc wave3 §n], [calc cycle_and_arm §n] are this
explorer's [`geometry.out.txt`](../calc/geometry.out.txt),
[`wave3.out.txt`](../calc/wave3.out.txt) and
[`cycle_and_arm.out.txt`](../calc/cycle_and_arm.out.txt);
[procedure calc §n] is procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.**
- The person cuts the ribbon, lays it in the cassette's under-width channel,
  and flush-cuts the tip in the cassette's guillotine slot.
- The end sticks out 10–20 mm past the clamp.
- They set the cassette on two pins in a printed dock on the laser bed: the
  H2C's laser platform, or a CO₂ engraver's bed.

**What the laser does, in one job file per ribbon size, in this order.**
1. **Score top.** One line across all conductors at the strip line, Ls from the
   tip (2.4 mm for genuine JST contacts, 1.85–2.1 mm for clone contacts [facts
   §1; terminal-supply calc w3 §3]), deep enough to take ~60–70 % of the
   0.49 mm wall at each conductor's crown, never through it.
2. **Slit top.** A line down the centre of each web, **from the clamp edge
   forward to the score line, not to the tip**, cutting from the top face to
   about the ribbon's mid-plane in several low-power passes.
3. **Flip.** The person lifts the cassette, turns it over about the ribbon axis
   and drops it back on the same pins. The web's lower half still holds the
   ribbon's pitch and plane.
4. **Score bottom**, then **slit bottom** last, the same way.

Every precise line is cut while the ribbon is still one piece. The conductors
are free along the split and still joined at the tip, ahead of the strip line.

**Then off the laser: pinch and pull the whole tip.**
- Two TPU-faced pads close lightly on the webbed tip, forward of the score,
  across all conductors at once.
- The cassette backs off 3 mm, by hand or by lever. The whole tip comes off as
  one comb-shaped slug: each conductor's jacket tears at its score ring, and the
  webs ahead of the strip line leave with it.
- A nylon brush ($15.90 assortment [Prime]) and a puff of air clear the silica
  ash from the strands.
- **Result:** webs split to the clamp edge, Ls of bare strands on every
  conductor, and the end goes to the crimper in the same cassette.

**What locates what; the reference for "fixed."**
- The cassette's two pins in the dock are the reference, and the flip turns
  about them.
- The laser's own coordinates place every line relative to the dock; the laser
  kit's "birdseye" camera aligns the dock once.
- So the split root and strip line sit at known distances from the cassette's
  clamp edge. With the insulation edge made by a score placed from the
  cassette, the axial chain to the crimp's window falls from ±0.34 mm to
  ~±0.10 mm RSS [procedure calc §10].

**What drives and carries the force.** No cutting force. The only force is the
pull, carried by the cassette's clamp on the insulation:
- per conductor, scored top and bottom at 60 % of the wall: 4.7–13 N with
  silicone at 4–11 MPa, 9.4–13 N at the digest's 8–11 MPa [calc geometry §3,
  calc wave3 §8];
- a whole 5P tip: ~24–65 N;
- a 22 AWG conductor breaks at ~85–100 N [facts §1].

**How it knows it worked.**
- The camera photographs each tip after the pull, backlit: bare strand length, a
  clean insulation edge, no char on the strands, no leftover ligament, and the
  strand silhouette (the guard against cut strands that force monitoring cannot
  see [digest]).
- If a conductor keeps its slug, it is pinched and pulled on its own after one
  more score pass.

**What the person does.**
- Cuts, flush-cuts and clamps the end.
- Docks the cassette, starts the job, flips it once.
- Pinches, pulls and brushes.
- About 60–80 s of attention per end [estimate], about what a hand peel and
  strip takes (~16 min a unit by procedure's library [procedure calc §5]), so b4
  buys a datum, not minutes. [b4b](b4b-diode-heads-at-the-station.md) removes the
  dock and the flip.

## Steps it covers and what it hands back

- **Covers:** split (webs slit from the clamp edge to the strip line), strip
  (crown scores and a whole-tip pinch pull), and a backlit check of the tips.
- **Hands back:** cutting and clamping the end, the flip, the pull and brush,
  and everything from placing the contact onward, to whichever crimper receives
  the cassette.

## Why the flanks are not scored, and why the tip stays webbed

- **At ribbon pitch the flanks are shadowed.** A beam tilted 45° reaches a
  conductor's vertical flank only if the pitch is above 2.05 mm; a 60° beam only
  above 2.55 mm [procedure calc §8]. Conductors touching at 1.7 mm shadow each
  other's flanks.
- **A slot comb cannot enter at ribbon pitch** for the same reason: there is no
  gap between necks for a tooth [procedure calc §8].
- **So the tip stays one piece.** Stopping the slits at the score line keeps the
  tip webbed; the pads take all conductors' slugs together, and each flank tears
  from its top and bottom scores.

## Score depth

The bundle can sit up to 0.06 mm off centre in a 0.43–0.55 mm wall [facts §7].
A score of 80 % of the nominal wall (0.39 mm) leaves as little as 0.04 mm over
the strands on the thin side; 60–70 % (0.29–0.34 mm) leaves at least ~0.09 mm.
Unlike a blade closed to a stop, the laser's depth does not depend on where
the clamp holds the conductor's centre, only on energy per area and the local
wall, so a test strip at a few powers sets it.

## Variant: a partial slit for splitting on demand

The slit can stop short of severing, leaving a 0.05–0.2 mm ligament along each
web.
- The ribbon stays a ribbon.
- One conductor peels off along its slit at ~1–5 N (tear strength 15–25 N/mm
  [Primasil, via calc geometry §3]; [procedure calc §9]).
- An unscored web of 0.4–0.6 mm [assumption] needs 6–15 N and tears where it
  chooses.

That lets [b1](b1-press-and-applicator-with-shuttle.md)'s fork split each
conductor off the edge of the ribbon inside the crimp loop, with the clamp edge
as the root by construction.

## Which laser

| Laser | What it is | Evidence | What it means here |
|---|---|---|---|
| **H2C laser module**, 455 nm diode, 10 W or 40 W | Bambu's upgrade kit for H2D/H2C: module, safety windows, birdseye camera, air pump, e-stop | $698 (10 W) / $1,348 (40 W), "In-Stock Now" at [3D Universe](https://shop3duniverse.com/products/bambu-lab-laser-upgrade-kit-laser-module-included); "H2D/H2C supports both 10W and 40W laser" [same]. No Prime listing [Prime] | Enclosed and camera-aligned. Copper absorbs ~65 % at 450 nm against ~5 % in the near-IR ([search summary of Laserax and blue-diode welding literature](https://www.laserax.com/blog/laser-welding-copper)), so it scores and never strips through; the slits stop at the mid-plane |
| **CO₂**, 10.6 µm, 40–45 W | Desktop CO₂ engraver, ~12 × 8 in bed | VEVOR 45 W CO₂ engraver with air assist, $759.90 [Prime], thin listing (4 ratings); OMTech K40+ at CA$999.99 on OMTech Canada (search summary) | Copper reflects 10.6 µm, so the process self-limits at the strands: "every polymer will absorb light and every metal will reflect it" ([Wiring Harness News](https://wiringharnessnews.com/basics-of-laser-wire-stripping/)). Needs water cooling, venting and its own enclosure |
| XLaserlab X1 Pro fibre laser [repo] | kW-class handheld welder and cleaner | [facts §7] | Near-IR into metal; far too powerful without heavy attenuation. Not used |

The industry's own description of laser stripping matches this idea: a ring
burned from above and below, "allowing you to pull off the insulation", with
residue "on the sides where the laser beam spread out" [Wiring Harness News].

## References and tolerances

| Quantity | Needed | Provided by |
|---|---|---|
| Strip length Ls | a per-reel value, so the insulation edge lands in the ~0.6–1.0 mm window | score line at a known distance from the datum; laser positioning ~0.05–0.1 mm [estimate] |
| Split length | 8–15 mm for b1's fold-back band | slit from the clamp edge, which is the root |
| Score depth | 60–70 % of the 0.49 mm wall at the crown, never to copper with 455 nm | power, speed and passes, set on a test strip |
| Flip registration | slits and scores from below meet those from above within ~0.1 mm | two pins; cassette symmetric about the ribbon axis |

## Problems and their repairs, as they stand

- **The blue laser could fuse or cut strands**, at 65 % absorption on bare tinned
  copper. The repair is never to expose copper: score to a set fraction of the
  wall and let the tear do the rest; slit only to the mid-plane from each side.
  Whether 455 nm chars black silicone into a conductive or stiff residue, and how
  consistent the depth is on a round surface, is one test strip.
- **Ash in the crimp.** Silica ash is an insulator. The slug carries most of the
  scored zone away; brush and air clear the rest. Ash packed between 60 strands,
  and its effect on crimp resistance, is open.
- **The second slit would free the conductors before the second score** if
  slitting came first; hence the order above.
- **Fumes.** Burning silicone gives off silica and organics [assumption]. The H2C
  kit has its own exhaust arrangement; a CO₂ engraver needs a vent line.
- **The H2Cs are busy printing.** Laser work per unit is ~14 ends × ~1 min of
  beam [calc cycle_and_arm §1]: batch all ends of a unit in one module swap, or
  use b4b.
- **A redo** (a whole end cut back ~6 mm) goes back to the laser: a held batch or
  a module swap on the H2C. b4b keeps the laser at the station.

## Printed and bought

- **Printed:** laser dock with two pins; the cassette, shared with the crimpers;
  pinch pads (TPU); flip handle.
- **Bought:** the H2C laser kit ($698 / $1,348, 3D Universe) or a CO₂ engraver
  ($759.90 [Prime]); nylon brushes [Prime]; vent hose.
- **On hand:** H2Cs, camera.

## Contribution

- Split and strip without a blade, on a machine the bench may already have.
- A cassette that leaves the laser with its split root and strip line at known
  distances from its datum.
- Scoring as a way to aim silicone's tear rather than fight it, and a tip left
  webbed so one pinch takes every slug.

## Major unresolved problems

- **Silicone under 455 nm.** Char, residue, depth control on a round surface:
  unsourced and untested [facts Unresolved 9].
- **Web geometry.** Whether the seam slit leaves both neighbours' insulation
  intact; the neck is unmeasured (repo Open item 5).
- **Flank tear.** Whether each flank tears cleanly from top and bottom scores when
  the whole tip is pulled at once, or leaves flags.
- **Ash** in the strands, and its effect on the crimp.
- **Person time.** The dock and the flip keep it near a hand strip's.

## What rests on what

- **Derek:** the H2Cs print about a week per unit [Derek]; whether he has or wants
  the laser kit is his question.
- **Facts:** wall and bundle [facts §7]; strip lengths [facts §1]; laser
  behaviour by wavelength is unsourced [facts §7].
- **Calculations:** tear-off by ligament [calc geometry §3, calc wave3 §8]; flank
  shadowing, axial chain, peel [procedure calc §8–10]; beam time [calc
  cycle_and_arm §1].
- **Estimates:** laser positioning ~0.05–0.1 mm; person time per end.
- **Assumptions:** the cos² depth model for a vertical beam on a round conductor;
  silicone tensile 4–11 MPa for this grade (the digest takes 8–11 MPa; the lower
  bound only moves the pull forces' low end); tear governed by the ligament's
  tensile area.
