# a8 Rolling ring scorer: every conductor of the row spins in place under two fixed blades, then the slugs tear off at the score

## Picture it

A stripping station built on what soft silicone is good and bad at: it cuts
easily under a sharp edge, tears easily from a notch, and squashes rather than
parting under a blade squeezed from two sides. So the blades only score a ring
to a depth that cannot reach the strands, and a pull tears the thin ring left.
The ring is made by turning the conductors, not the blades: each conductor of a
fanned row lies between two pads sliding in opposite directions, which spins it
about its own axis without moving it, the way a pencil turns between two palms.
One straight blade above and one below score all of them at once, at any pitch.
Sketch: [`../sketches/a8-rolling-ring-scorer.svg`](../sketches/a8-rolling-ring-scorer.svg)
(schematic).

**Where things start.** The pallet holds a ribbon end parted
([a7](a7-zip-station.md) or [a7b](a7b-plough-station.md)), fanned to its working
pitch (2.5 mm or wider), and **flush-cut at the fan block's face**, so all the
tips lie on one line (order A of [a5](a5-part-fan-strip-in-the-pallet.md)).
About 9 mm of each conductor stands past the fan block, parallel and in one
plane.

**The station.**
- **Bed:** a flat steel plate under the overhang, with a slot across it at the
  strip line for the bottom blade, and between the strip line and the front stop
  a clear window over an LED panel.
- **Stop bar:** a grounded steel bar across the front, exactly one strip length
  (2.4 mm for SXH-001T-P0.6 [mfr S6], or the contact's own value) ahead of the
  blades.
- **Blades:** two single-edge razors (0.23 mm, with spines), one above and one
  below, edges across the row at the strip line, each on a screw depth stop. The
  top blade drops onto its stop on a servo lever; the bottom rises through the
  bed slot on a cam. Both are isolated and wired.
- **Pads:** behind the blades, on the conductors' bodies, a bottom and a top pad
  faced with printed TPU, on two racks with one pinion between them, so when one
  slides +X the other slides −X by the same amount. A small stepper turns the
  pinion.

**What moves, for one ribbon end.**
1. **Touch-off.** The pallet creeps toward the stop bar. Through the far-end port
   ([a6](a6-housing-as-last-comb.md)) or the reel's hub socket, each conductor
   reads continuous to the bar as its copper face touches, and the stage records
   where. Early tips bow a little over their 9 mm as the pallet creeps on. A
   spread over ~0.2 mm, or a conductor that never touches, is flagged. The stage
   settles where the median tip touches.
2. **Clamp.** The top pad comes down with ~1–2 N per conductor.
3. **Score.** The blades close to their stops, each edge a quarter of a
   millimetre into every crown. The pinion turns: the pads move ±1.6 mm apart and
   every conductor turns about 0.6 of a revolution in place, enough for the two
   blades' arcs to meet into a full ring. The pads return.
4. **Pull.** The top pad lifts; the blades stay in their scores; the pallet draws
   back 3 mm. Each slug tears off at its score and stays between blades and stop
   bar.
5. **Clear.** The blades open; a puff from the shop compressor through a
   solenoid valve blows the slugs into a cup.
6. **Look.** The pallet moves forward until the stubs lie over the window, and
   the camera takes one backlit frame of the row.

**What locates what, and the reference for fixed.**
- **"Fixed" is the bed,** with the blades and stop bar mounted to it.
- **Axially:** stop bar and blades are one steel assembly; strip length is their
  distance, the same for every conductor. Touch-off confirms the tip line
  conductor by conductor.
- **Radially:** each conductor's axis sits half its diameter above the bed.
  Blade heights are set against the bed with a 1.45 mm gauge pin under the top
  blade and a 0.25 mm feeler under the bottom one, for a score radius of
  0.60 mm.
- **Laterally:** nothing needs locating; a straight edge scores every conductor
  it crosses, at any pitch.

**Forces.** No crimp force. Scoring is well under a newton per conductor
[calc W2 §4, cutting energy 0.1–1 N/mm assumed]; the pads' ~1 N per conductor
on TPU turns them without slipping. Tear-off is 2.6–9.2 N per conductor at a
0.58–0.63 mm score radius [calc W2 §4], 13–46 N for a 5P, taken by the clamp at
the split root; a 22 AWG conductor breaks at 85–100 N [source S23].

**How it knows the strip is good.**
- **Nick detection while scoring:** a blade touching strands closes that
  conductor's circuit; the pinion stops, and the log names the conductor and the
  angle (Schleuniger/Komax SmartDetect's principle [prior-art §2], for a whole
  row).
- **The backlit frame:** for every stub, bare length, bundle width (splayed
  strands widen the silhouette), the edge profile (a flap or tail shows as a
  bump), and any strand off the bundle. It is the guard against a few cut
  strands (machine-that-sees-and-learns' finding).
- **Touch-off** before anything cuts.

**What the person does.** Nothing at a station on a stage. The bench version is
below.

## Steps it covers and what it hands back

Covers the strip of a whole row at once, touch-off of every tip, nick detection
and stub inspection. Hands back nothing at the station.

## The physics it rests on

- **Order.** A conductor anchored at the split root follows its groove, and a
  curved groove is longer than its span, so outer tips recede: 0.31 mm for a 5P
  at 2.5 mm, 1.65 at 5 mm, 2.77 at 7.1 mm [calc W2 §3]. a8 therefore strips
  after the fan, at the fan face. The alternative order strips before the split
  (procedure-is-the-machine's
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)) and fans
  with equal paths ([a9](a9-reel-end-docks.md)); there a8 is not needed.
- **How deep the score may go.** The score radius must clear the outermost
  strand with margin [calc W2 §4]: bundle radius 0.37 mm; a loose strand 0.04 mm
  proud; the bundle off-centre in its jacket by e (unmeasured, 0.05–0.10 mm);
  the conductor's axis height ±0.05 mm; blade setting ±0.02 mm; 0.05 mm clear.
  That puts the score radius at 0.58–0.63 mm, 0.22–0.27 mm deep in a 0.49 mm
  wall, leaving 0.22–0.27 mm to tear.
- **Why the tear follows the score.** A pull loads the remaining ring in tension
  along the conductor, and a notch under tension grows straight across the
  section. How clean the edge is on silicone with 200–500 % elongation
  [source: Primasil] is the unknown.
- **Why roll the conductors.** Two blades squeezing from above and below cut
  only the crowns, ±40–54° each, leaving 144–200° of each circumference to tear
  from full wall [calc W2 §5]. A turning head ([a8b](a8b-spindle-with-touch-off.md))
  works one conductor at a time. Rolling the row under fixed blades gives every
  conductor a full ring at once.
- **Why the pads move in opposite directions.** A cylinder under one moving pad
  travels half the pad's distance and walks into its neighbour; between two pads
  moving equal and opposite, its axis stays put. A pinion between two racks makes
  the motions equal by construction.
- **Twist.** Each conductor turns 0.6 turn and back. With the fan block's lid
  lifted, the twist spreads over the whole parted length (~210° over 20–35 mm),
  and the strands may keep a little of it [estimate].
- **Neighbours.** Two touching cylinders turning the same way rub in opposite
  directions; at housing pitch there is 0.8 mm between jackets.

## References and tolerances

| Moment | What must be right | Set by | Tolerance |
|---|---|---|---|
| Touch-off | every tip on the line | flush cut at the fan face, confirmed per conductor | ±0.05 mm [estimate] |
| Score | blade 0.58–0.63 mm from each axis | blade height gauged against the bed | ±0.02 setting, ±0.05 from conductor diameter |
| Score | ring square to the axis | pad motion square to the conductors | 1° walks the ring 0.03 mm over 1.6 mm of travel |
| Pull | slug held on both sides | both blades in the score | coarse |
| Strip length | 2.4 mm (JST) or 1.6–2.1 mm (KONNRA clone spec) | stop bar to blade, one steel part | ±0.05 mm |

## By hand, first

A bench block with the same bed, stop bar, blades and pads on a pinion turned by
a knob: lay a fanned, flush-cut end against the stop bar, lower the top pad and
blades with two levers, turn the knob a little over half a turn and back, pull
back. It answers whether the tear follows the score, what score radius this
ribbon tolerates, and how much twist the strands keep. Smaller still: lay one
conductor on a steel rule, rest a razor across it on a 1.45 mm pin as a spacer,
roll it one turn under a finger, pull.

## Parts

| Part | Source | Note |
|---|---|---|
| Bed, slot, stop bar, blade holders | laser-cut steel or steel flat drilled on the WEN | flat; the radial reference |
| Blades | bought | AccuTec 0.009 in single-edge, 100 for $12.90 [Prime, thin listing]; American Cutting Edge $10 / 100 |
| Pads, racks, pinion | printed (TPU 90A faces, PET-CF racks) | module 0.5 steel racks requested for the Prime pass |
| Pinion drive, blade lever, cam, pad lift | bought servos or a small stepper | MG996R 4-pack $18.99 [Prime] |
| 1.45 mm gauge pin, 0.25 mm feeler | bought | Accusize 0.28–1.52 mm pin set (includes 1.448 mm), $45.58; Hotop feelers $8.99 [Prime] |
| Window light | bought | XIAOSTAR A5 light pad $16.99 [Prime] |
| Air valve | bought | Beduan 12 V NC 2-way valve, $9.99 [Prime]; its 1/4 NPT body is large for the job |

## What it contributes

- **A full ring on every conductor at once, with two razors:** no form blades,
  no pitch match, no rotating head.
- **A strip line that is a property of one steel part,** measured from tips the
  pallet has put on a line.
- **A self-reporting strip:** touch-off before, nick detection during, a
  silhouette after, per conductor and logged.

## Major unresolved problems

- **Whether the tear follows the score on this silicone,** or pulls a tail or a
  flap.
- **Bundle eccentricity e,** which sets how deep the score may go; one fresh
  cross-section measures it.
- **Pads that roll without slipping** at a normal force low enough not to flatten
  the jacket.
- **Strand twist** kept after the turn and return, and whether it helps or harms.
- **Slugs** clinging to blades or stop bar.

## Related ideas

- Branch: [a8b](a8b-spindle-with-touch-off.md). Module: [a5](a5-part-fan-strip-in-the-pallet.md).
- Used by [a1](a1-pallet-tour.md), [a1c](a1c-crimp-upstream-first-park-after.md),
  [a2](a2-two-pallets-meet.md) and branches, [a4](a4-spool-as-magazine.md),
  [a10](a10-dock-tack-then-nest.md).
- Other explorers: procedure-is-the-machine
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md) (the other
  order); machine-that-sees-and-learns (the backlit stub check).

## What rests on assumptions

- Cutting force (0.1–1 N/mm); bundle eccentricity 0.05–0.10 mm; touch-off
  contact force 0.05–0.2 N on tinned strand ends [assumption].
- The tear following the score [estimate].

## Labels

As [a1](a1-pallet-tour.md#labels).
