# a5 Part, fan and strip inside the pallet (module)

## Picture it

The preparation half of every arrangement in this directory: what happens to a
ribbon end between being clamped and being presented to a contact. It hands the
crimp conductors that are parted, at a known pitch and height, cut to one line,
stripped to a known length, and not nicked. It is a module, not a machine.
Sketch: [`../sketches/a5-part-fan-strip.svg`](../sketches/a5-part-fan-strip.svg)
(the three orders and the catalogue); the stations are drawn in
[`../sketches/a7-zip-station.svg`](../sketches/a7-zip-station.svg),
[`../sketches/a8-rolling-ring-scorer.svg`](../sketches/a8-rolling-ring-scorer.svg)
and [`../sketches/a8b-spindle-with-touch-off.svg`](../sketches/a8b-spindle-with-touch-off.svg).

A ribbon end, or one ribbon of a pair, is clamped with the clamp's front face at
the split root and 35–50 mm standing out on a covered floor. The pallet (or the
stage carrying it, or a fixed clamp at a reel) moves against fixed tools, and
the steps come in one of three orders. Each order keeps every tip and every
insulation edge where the crimp needs it; they differ in what they leave in the
finished loom.

**Order A: part, fan, then flush-cut and strip at the fan block face.**
([a1](a1-pallet-tour.md), [a1c](a1c-crimp-upstream-first-park-after.md),
[a2](a2-two-pallets-meet.md) and its branches, [a4](a4-spool-as-magazine.md),
[a10](a10-dock-tack-then-nest.md).)
1. **Part** back to the clamp face ([a7](a7-zip-station.md) or
   [a7b](a7b-plough-station.md)); trim J2's conductor 3 and J7's spare there.
2. **Fan** to the working pitch in a fan block.
3. **Flush-cut** every conductor at the fan block's face + a fixed overhang.
4. **Strip** at a fixed distance behind that line, the whole row at once
   ([a8](a8-rolling-ring-scorer.md)).

A conductor anchored at the split root follows its groove, and a curved groove
is longer than its straight span, so the outer tips recede against the centre
one [calc W2 §3]:

| Fanned to | 3P outer | 4P outer | 5P outer |
|---|---|---|---|
| 2.5 mm | 0.11 mm | 0.20 mm | 0.31 mm |
| 5.0 mm | 0.76 mm | 1.20 mm | 1.65 mm |
| 7.1 mm | 1.32 mm | 2.05 mm | 2.77 mm |

These are for a compact S (R 5 mm, 30°, then straight). The groove's shape sets
the figure: a gentle S spread over the whole split gives a 5P 0.10–0.19 mm at
2.5 mm, and 2.0–3.1 mm at 7.1 mm [P3 §1]. Cut after the fan, the tips and
insulation edges lie on one line in the crimp pose. **What it leaves:** the
outer conductors are longer than the centre one by their recession. Closed to
2.5 mm and latched at one depth, a 5P fanned to 5 mm carries 1.34 mm of excess
in its outer conductors and one fanned to 7.1 mm 2.46 mm, a 3–5 mm arc over a
20–30 mm split [calc F §5]. At insertion the same excess is a V staircase
([a6](a6-housing-as-last-comb.md)).

**Order B: flush-cut at the clamp face, strip webbed, zip from the slug's gap,
then an equal-path fan.** ([a9](a9-reel-end-docks.md); the strip is
procedure-is-the-machine's
[p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md).)
1. **Flush-cut** at the clamp face: at a reel, the cut that freed the last loom.
2. **Strip webbed:** two single-edge razors close from above and below across
   the whole width 2.4 mm ahead of the face, stopping on steel stops at strand
   radius + 0.2–0.3 mm from the centre plane, then slide forward and push the
   slug (every jacket and web) off as one sleeve, 40–60 N for a 4P
   [p7; calc wave2 §7]. One backlit frame reads every bare length.
3. **Zip from the slug's gaps:** the tines enter the ~0.98 mm gaps between bare
   bundles and meet each web at the strip line, already opened by the slug's
   tear. No nicker is needed.
4. **Equal-path fan:** the inner grooves carry a vertical hump that makes their
   path as long as the outer groove's. For a 4P at 7.1 mm the inner pair's hump
   is 3.3 mm over 16.7 mm, bent at R ~4.3 mm; a 5P's centre conductor needs
   5.1 mm over 21.4 mm; at 5 mm pitch 1.7–3.2 mm; at 2.5 mm under 1 mm [P3 §1].
   Every tip then recedes by the same amount, so the tip line and strip line made
   before the split stay straight, and the split must allow that recession.

**What it leaves:** every conductor one length from the root, so the finished
loom carries no excess. The humps take a set (the strands yield below a bend
radius of 39–78 mm [P3 C11]), and the insertion clamp's forward push pulls them
straight at 0.06–0.23 N [calc F §5].

**Order C: part, fan, then touch off and strip each conductor at its own tip.**
([a4](a4-spool-as-magazine.md) or [a1c](a1c-crimp-upstream-first-park-after.md)
with [a8b](a8b-spindle-with-touch-off.md).) Any fan; each conductor's own tip is
found through the far-end port and its crimp Y is set from that record. The
spindle head needs a snout no wider than 7.8 mm at 5 mm pitch, or the conductor
lifted into the head [P3 §8]. What it leaves is order A's excess if the fan is
closed afterwards.

**At housing pitch alone (2.5 mm)** the recession is 0.11–0.31 mm and the orders
barely differ.

**What locates what, and the reference for fixed.**
- **"Fixed" is the clamp face**, which is also the split root.
- The clamp channel is cut ~0.2 mm under the ribbon's nominal width, so the
  silicone is squeezed into register (AMP US 4,230,008). The ribbon's own pitch
  then places each conductor within 0.12–0.43 mm of nominal from a centred
  datum, even for J1's nine [calc §1].
- The tip line is the flush cut (order A: the fan block face; order B: the clamp
  face).
- The strip line is one steel part's distance behind the tips: a8's stop bar
  and blades, or p7's blades and stop; or behind each tip found by touch (a8b).

**Forces.**
- Parting: 1.5–17.5 N per web by tearing, depending on the unmeasured neck
  thickness [calc W2 §2]; about a newton by cutting [assumption].
- Stripping pull-off: 2–13 N per conductor from a scored ring [calc W2 §4];
  40–60 N for a webbed 4P slug [p7].
- The clamp: up to ~70 N while all webs of a 5P tear at once, less with
  staggered tines. No crimp force passes through this module.

**How it knows.** Every step reports itself: touch-off of every tip through the
far-end port or the reel; isolated blades and tines that name a conductor they
touch (a nick detector, the industry's SmartDetect principle [prior-art §2]); a
backlit silhouette of every parted conductor; a load plateau at the zip; one
backlit frame of every stripped stub, the only guard against a few cut strands
(machine-that-sees-and-learns).

**What the person does.** Nothing at a station on a stage or at a reel clamp.
Each station has a bench-block version worked by hand (below).

## Steps it covers and what it hands back

- **Covers:** split, trim, fan, flush cut, strip, nick detection, stub
  inspection.
- **Hands back:** nothing by itself; whoever runs the pallet runs these.

## The catalogue

### Parting

Silicone is soft (Shore 50–70A), weak in tension (8–11 MPa) and easy to tear:
15–25 N/mm for wire grades, ~10 N/mm for general grades
([source](https://www.primasil.com/materials/wire-cable-silicone/)). The
conductors are round jackets 1.7 mm across at 1.7 mm pitch, so neighbours meet
at a line, fused over a neck of unknown thickness t_n. 0.98 mm of silicone lies
between two strand bundles on the mid-plane [calc W2 §1].

- **P1 Floating plough:** a razor sliver behind a V-nose riding its valley on a
  flexure. Developed as [a7b](a7b-plough-station.md).
- **P2 Fixed gang slitter** in an under-width channel. A fixed gang of 0.23 mm
  blades on a 5P carries up to 0.32 mm of lateral error and can come within
  ~0.1 mm of the outer strands [calc W2 §1]; floating blades replace it.
- **P3 Nick, then wedge,** stopped at the clamp. Developed as
  [a7](a7-zip-station.md). It needs t_n well under the 0.49 mm wall.
- **P4 Interlaced toothed jaws** (US 4,179,964 [prior-art §1]): opposed combs of
  conductor-wide cradles shear each web and push odd and even conductors into
  two planes, the input for change-the-question's
  [c1](../../change-the-question/ideas/c1-half-rows.md). Steel faces.
- **P5 Punch a slot** between conductors [prior-art §1]: clean gaps, a punch and
  die per pitch. Not developed.
- **P6 Laser slit** (borrowed-machines'
  [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md)): needs no web
  geometry, adds char and ash, and copper absorbs ~65 % at 450 nm, so a
  wandering slit reaches strands. A cartridge for a7's station.

### Fanning

- **F1 Recipe fan block:** S-curved grooves from 1.7 mm to the target pitch. The
  copper keeps the shape (set below R 39–78 mm).
- **F2 Diverging-slot pitch changer:** fingers on pins in parallel slots and in
  a plate with diverging slots; sliding the plate changes every finger's pitch
  together. One mechanism replaces the crimp-pitch block and the closing block.
- **F3 Tines that stay:** [a7](a7-zip-station.md)'s wedge comb diverges from
  1.7 mm to 2.5 mm, so the tool that parts is also a housing-pitch fan.
- **F4 Form, then let go:** a two-piece die presses the fan and withdraws; the
  copper keeps it within the silicone's springback. Untested.
- **F5 Equal-path grooves:** humps in the inner grooves (order B).

### Stripping

JST's rule is "no cut or nicked strands" [mfr S5], on 60 strands of 0.08 mm
under a ~0.49 mm wall that tears rather than parting cleanly [xh-facts §7].
Slowness allows cutting shallow and tearing the rest: a score that stops
0.15–0.25 mm short of the strands leaves a ring that tears at 2–13 N
[calc W2 §4]. Strip length is 2.4 mm for JST's contact [mfr S6], or 1.6–2.1 mm
by KONNRA's clone spec ([source](https://konnra.com/jst-xh-2-5-connector-complete-guide/));
the contact in use decides.

- **S1 Crown score across the row, flanks torn.** Two flat razors from above and
  below across the row. On a split row each cuts only ±40–54° of each crown and
  leaves 144–200° of every circumference to tear from full wall [calc W2 §5].
  Done on the webbed end before the split, it is p7 (order B), and its ligament
  is set by steel stops to 0.2–0.3 mm ±0.08–0.12 RSS [calc wave2 §7]. The flank
  tear is its unknown.
- **S2 V-blades per conductor:** a 90° V pair cuts four arcs and leaves the top,
  bottom and sides shallowest.
- **S3 Ring score by turning:** [a8](a8-rolling-ring-scorer.md) (the conductors
  roll under fixed blades) and [a8b](a8b-spindle-with-touch-off.md) (the blades
  turn around one conductor).
- **S4 Pinch and pull:** blunt jaws crush the jacket at the strip line and the
  pull tears it. It cannot nick [assumption]. Bench test with smooth-jaw pliers
  (TEKTON PMN23001, $17.00 [Prime]).
- **S5 Laser score** (b4): score a ring to 60–80 % of the wall, flip, add flank
  passes; a slot comb pulls the slugs at 1.6–4.4 N [borrowed-machines calc
  geometry §3]. Silica ash among the strands; the isolated-blade nick detector
  cannot watch a beam.
- **S6 Hot blade:** silicone does not melt; it decomposes above ~300 °C
  [prior-art §2]. Not developed.
- **S7 Strip and crimp in one applicator:** JST calls MKS-SC (and MKS-L) a
  "strip-crimp applicator" [mfr S2, S4]. If an OTP unit for XH exists
  [assumption], stripping moves into the crimp station.

**Nick detector, for any blade or tine.** The blades are isolated; the far-end
port ([a6](a6-housing-as-last-comb.md)) or the reel's hub socket gives a wire
to every conductor; a blade touching copper closes that conductor's circuit, and
the event is logged against it. One nicked conductor means re-cutting that end,
~6 mm of ribbon in a cut-first order [procedure-is-the-machine calc
recovery_length], or the end's whole split at a reel clamp.

## What the insulation barrel does to the prepared end

KONNRA's clone insulation crimp is 1.80 ± 0.10 mm high and at most 2.05 mm wide
[source]. Inside a 0.2 mm barrel of that size there is room for ~1.8 mm² of
conductor; this ribbon's conductor is 2.27 mm². So the jacket is squeezed to
~70–80 % of its area [calc W2 §9], and, being nearly incompressible, bulges out
of both ends of the barrel. force-and-form's calc reaches the same figure
separately (20–30 % of the jacket squeezed out) [w3 C5]. The front bulge
lands in the window between the barrels, where the insulation edge must be
seen; a strip edge with a flap or tail makes it worse, which is one more reason
the strip edge must be clean, and the frame after the crimp should look for
silicone in the window.

## Two ribbons of a pair

- **Processed as two:** fewer webs at once, a shorter fan at wide pitches
  [calc §2], no shared edge to treat as a valley. The two meet at insertion.
- **Clamped together, parted as one:** the boundary between the ribbons needs no
  parting. Kept for the housing-pitch fan, where the extra length is small.
- **J4 and J7** cross conductors between their ribbons
  ([a6](a6-housing-as-last-comb.md)).

## By hand, first

Each station has a bench block: a7's comb on a rail, a8's knob-and-lever block,
p7's two razors on a hinged jaw with steel stops. The two-minute tests: a razor
on a drill blank across one conductor, rolled a turn, then pulled (a8); a 5P end
squeezed between two razors on shims and pushed off, then a flat feeler driven
into the gap (p7 and a7).

## What it contributes

- **Three orders that follow from the ribbon's geometry,** each keeping every
  tip and insulation edge where the crimp needs it, and a statement of what each
  leaves in the finished loom.
- **Stations developed in depth,** each with a bench-block first version: a7,
  a7b, a8, a8b.
- **Measured error, not assumed:** touch-off, nick detection, silhouettes and
  the stub frame make each step report itself.

## Major unresolved problems

- **Web geometry and tear path** (repo Open item 5): neck thickness, valley
  depth, whether a tear stays in the web. One fresh cross-section under the ELP
  camera and a metre peeled by hand settle them.
- **Bundle eccentricity** in the jacket, which sets how deep a score may go.
- **Whether a ring score tears cleanly,** and whether p7's flank tear leaves a
  clean edge.
- **Strand behaviour** on a 2.4 mm untwisted stub.
- **The equal-path fan block's capture** of tine-fanned conductors, humps
  included, and the set the humps leave.
- **Laser selectivity** on tinned copper at 455 nm.

## Related ideas

- Stations: [a7](a7-zip-station.md), [a7b](a7b-plough-station.md),
  [a8](a8-rolling-ring-scorer.md), [a8b](a8b-spindle-with-touch-off.md).
- Users: every arrangement in this directory; order B is [a9](a9-reel-end-docks.md)'s.
- Other explorers: procedure-is-the-machine
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md);
  borrowed-machines [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md);
  change-the-question [c1](../../change-the-question/ideas/c1-half-rows.md).

## What rests on assumptions

- Silicone properties are grade values [source: Primasil], not BNTECHGO's.
- Cutting force; blunt-jaw safety for strands; diode-laser behaviour
  [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels); [calc wave2 §n] is procedure-is-the-machine's
[`wave2.out.txt`](../../procedure-is-the-machine/calc/wave2.out.txt); [w3 Cn] is a
consistency item in
[`../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md`](../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md).
