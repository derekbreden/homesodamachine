# p5b The camshaft squeezes the hand tool: one turn per conductor, one motor, no press

Sketch: [`../sketches/p5b-cam-timing.svg`](../sketches/p5b-cam-timing.svg)
(schematic timing). Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §5
(cited as [calc wave2 §n]), [`../calc/wave3.out.txt`](../calc/wave3.out.txt)
(cited as [calc wave3 §n]), hand-tool-as-press's
[`exchange_procedure.out.txt`](../../hand-tool-as-press/calc/exchange_procedure.out.txt)
§5 (cited as [calc H §5]).

**A branch of [p5](p5-camshaft-one-revolution-per-conductor.md), and a
combination** with hand-tool-as-press
[a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md) (the SN-2549 in a
cradle, squeezed by a machine). It keeps p5's one slow motor turning one shaft
once per conductor, the cassette on a rail with its printed rack as the
escapement, the skip and end bumps as the program, and the timing diagram as the
machine. The steel eccentric, the stop blocks, the fin and the punch give way to
a squeeze lobe on the same shaft pushing the SN-2549's handle; the presser gives
way to a lift cam, so the order is [p1c](p1c-lift-once-tip-down-module.md)'s
lift once. The crimp force closes inside the hand tool, so the frame carries
only the handle's reaction, ≤ ~275 N.

## Picture it: J2 in its cassette, keys 1–6, key 3 blank

**Where things start.**
- The J2 cassette sits on the carriage rail, loaded as in p1 with a 30–35 mm
  split. Trim and strip were done in the lifted pose at a bench A whose lift
  matches this machine's, or by [p7](p7-strip-before-split.md)'s whole-end
  stroke before the person peeled the web.
- The far end sits in a pogo block on the cassette.
- A **post wheel** is fixed to the frame in front of the tool, on the station
  line. It holds J2's five contacts box-first on 0.64 mm posts parallel to the
  wire axis, in key order, with the post for key 3 left empty. Its top post
  points back at the tool at nest height, so the lifted conductor *k*, the tool
  and the next contact lie on one line along Y, and the tool shuttles between
  them.

**The tool's pose.** The SN-2549 [Prime: iCrimp SN-2549, $22.29] lies **on its
side** in a cradle on the Y carriage: its long axis runs across the row, its
jaws close vertically, and the anvil half is underneath. A contact sits in the
nest floor-down, and every crimp comes out upright. (Hung tip-down over a flat
row, closing along the row, it would roll every crimp 90°.) The cradle
insulates the tool, which is wired as an electrode.

**The frame.**
- Printed side plates carry a 10–12 mm steel shaft on two ball bearings.
- A 12 V self-locking worm gearmotor, 40 kg·cm (3.9 N·m) at 10 rpm, turns it,
  with an AS5600 on the shaft for its angle [Prime: Greartisan, $26.99; Prime:
  AS5600, $7.99 for three]. A NEMA 17 worm-gear stepper had no Prime listing.
- On the shaft sit an index cam and pawl, a **lift cam**, a **Y cam** driving the
  tool carriage along the wire axis against a return spring, a **squeeze lobe**
  with a steel wear strip, a flap cam, a post-wheel pawl, a presser cam and a
  switch cam.
- The squeeze lobe's roller follower drives a lever, and the lever pushes the
  moving handle through a spring link preloaded to ~275 N, with a load cell in
  the link [Prime: bar load cell with HX711, $9.99].
- A microswitch on the tool's ratchet pawl reads whether the ratchet has
  released [Prime: KW12-3 roller micro switches, $5.99].

**One turn, ~40–60 s** (schematic; the sketch):

| Degrees | What happens | Driven by |
|---|---|---|
| 0–20 | escapement advances the cassette one key (2.5 mm) | index cam + pawl |
| 20–50 | lift finger raises key *k* by *h* = *a* + 2.7 mm (8.7–14.7 mm) | lift cam |
| 40–70 | post wheel turns one post; the next contact stands at nest height | pawl |
| 60–90 | Y carriage forward: the open jaws slide over the contact's barrels on its post | Y cam |
| 70–110 | handle approach to a **dwell just short of wing touch**: the contact is located on the anvil, its wings open | squeeze lobe (0.3–0.4 N·m) |
| 100–115 | flap blade drops into the neck against the box's rear face | flap cam |
| 110–160 | Y carriage back past neutral: the contact comes off its post, then slides onto *k* to the depth set by the cam | Y cam |
| 160–175 | lobe closes to the end of the wing curl; **the shaft pauses** and the tool reads *k* through the far end | squeeze lobe; controller |
| 175–235 | crimp: the last ~8 mm of grip | squeeze lobe (2.1–3.2 N·m) |
| 235–250 | the ratchet completes and releases; the lobe falls | lobe, tool spring |
| 250–255 | **release check**: if the pawl switch has not seen release, the shaft stops here | controller |
| 255–285 | proof pull: the Y follower backs 0.5 mm and a 20 N spring pulls the tool through the blade and box; a switch sees whether the tool followed | Y cam, spring, switch |
| 285–300 | flap lifts; jaws open fully | flap cam |
| 300–335 | lift lowers *k*; the crimp leaves through the jaws' side mouth; a presser squares it into the slot bar | lift and presser cams |
| 335–360 | Y to neutral; camera frame; the switch cam decides go or stop | Y cam, switch cam |

**Why the approach stops short of wing touch.** At the SN-2549's first ratchet
tooth the wing tips are pinched to the crimper channel, 1.4–1.6 mm apart. A
1.7 mm jacket then meets a wing tip edge-on unless the barrel floor is 1.9 mm or
wider [force-and-form calc wave2 §1]. Held just short of wing touch, the
insulation wings stay open at 2.46–3.0 mm and the conductor barrel at
1.68–1.90 mm [xh-facts §1], so *k* enters without meeting an edge.

**Why the release check.** A ratcheting tool releases only at its end position.
If a crimp needed more than the link's 275 N to get there, the lobe would finish
its rise, the link would compress, and the pawl would stay engaged: the jaws
clamped on the contact while the Y and lift cams moved on. The switch catches
that at 250–255°, and a gearmotor or stepper that can stop by angle stops the
shaft before the Y and lift cams act. The branch without the pawl
(hand-tool-as-press [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md))
drives the handle by displacement through the link instead: if the jaws bottom
face to face, the jaws are the stop and the link caps the surplus; if they do
not, the tool's 10–40:1 handle-to-die ratio shrinks a printed lobe's
±0.1–0.2 mm to ±0.005–0.02 mm at the dies [estimate].

**Key 3.** The skip bump lifts a lever that holds the post-wheel pawl clear and
lifts the squeeze follower off the lobe for one turn. The post for key 3 was
empty anyway: the empty cavity is decided twice in plastic.

**End.** The end bump stops the shaft at 0°.

**Knowing it worked.**
- **Force against shaft angle** from the load cell in the spring link, judged
  against taught curves (empty tool, contact without wire, good crimp), because
  the handle-side curve includes the tool's linkage (hand-tool-as-press a1).
- **Identity** at the end of the curl, through the tool and the far end.
- **The release check** and **the proof-pull switch**.
- **A camera frame** at 335°.

## Why the camshaft becomes small

- **The motor is sized by the handle, not the die** [calc wave2 §5, calc H §5]:

  | Lobe | Travel and angle | Load | Shaft torque |
  |---|---|---|---|
  | Approach | 45 mm over 120° | ~20 N | 0.43 N·m |
  | Crimp | 8 mm over 40° | 220 N | 2.5 N·m |
  | Crimp, spring link preloaded 275 N | 8 mm over 40° | 275 N | 3.2 N·m |
  | Crimp, stretched | 8 mm over 60° | 275 N | 2.1 N·m |

  The 3.9 N·m gearmotor covers the 60° lobe with margin and the 40° lobe at
  ~80 % of its rating. A NEMA 17 with a 26.85:1 planetary, 3 N·m permissible
  [Prime: STEPPERONLINE 17HS19-1684S-PG27, $41.91], covers the 60° lobe only.
- **The torque figures err high.** 220–275 N over the last 8 mm of grip is
  1.8–2.2 J at the handle, against 0.13–0.48 J of crimp work [calc wave3 §7]:
  either the linkage loses 75–90 % or the constant-force assumption overstates
  the lobe 2–4×.
- **No steel frame for the crimp.** The frame sees ≤275 N at the handle and
  ~50 N at the other cams. The follower on the squeeze lobe is the one printed
  part near its limit: a 16 mm roller, 8 mm wide, on a printed lobe reaches
  84–119 MPa; 16 mm wide, 59–84 MPa [calc wave2 §5]. The steel wear strip
  carries it.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Index | cassette | its own rack tooth and the escapement |
| Lift | key *k* | lift finger (frame) |
| Pick | contact axially | post wheel on the frame + the Y cam's forward dwell |
| Hold | contact laterally, roll | SN anvil nest and the upper jaw just clear of the wings |
| Feed | insulation edge in the window | the Y cam's back dwell, the cassette's trim line, the strip line made in the same pose |
| Crimp height | dies | the SN-2549's own, if they bottom |
| Timing | every motion | shaft angle |

**The axial chain is fixed by the cam**: ±0.21 mm RSS with the strip made in the
same lifted pose and the contact on the neck blade [calc wave2 §3], the
strip-length tear the largest term. A small stepper on Y instead of the Y cam
takes a camera correction and gives up "one motor".

## Steps it covers, and what it hands back

- **Covered:** index, lift, place the contact (pick from a post), place the
  conductor in it, crimp, proof pull, identity, square, skip and end.
- **Handed back:** cut, peel, load the cassette (crossings in the loft); trim and
  strip (bench A or p7); load the post wheel in key order; insert (bench C);
  label. Person time ~36 min a unit, the shaft ~40–60 min a unit with a cassette
  magazine [calc person_timeline; estimate].

## Printed and bought

- **Printed:** side plates, face cams (PET-CF), follower levers, the insulating
  tool cradle and Y carriage, the post wheel, lift finger, presser and slot bar,
  cassettes with racks and bumps.
- **Bought** (Prime rows observed 2026-09-28): a dedicated SN-2549 ($22.29); the
  gearmotor ($26.99) and AS5600 ($7.99); a 10 mm ground shaft [Prime: $17.99 for
  four]; 16 mm roller followers (608 bearings on pins); a steel strip for the
  squeeze lobe; a compression spring for the link [Prime: Dianrui spring
  assortment, $6.99, light springs only; a ~275 N link spring is a catalogue
  die spring, not Prime-confirmed]; the bar load cell and HX711 ($9.99); micro
  switches ($5.99); header pins [Prime: $7.99]; P75 pogo pins [Prime: $6.49].

## Problems, and what answers each

1. **The handle travels ~45 mm; a plate cam that big is huge** (~170 mm across
   for 53 mm of rise). A 3:1 lever between follower and handle cuts the rise to
   ~18 mm at 3× the follower force; the shaft torque does not change. The
   printed lobe then carries ~660–825 N at the follower, so the lever version
   wants the steel lobe.
2. **Picking a contact off a post needs a Z axis.** It does not: the post wheel
   presents one contact at nest height, and the Y cam slides the open jaws over
   its barrels, locates it, and draws it off (terminal-supply x1's pick without
   its Z).
3. **The lifted conductor's set leaves the crimp standing proud.** At 8.7–14.7 mm
   of lift the rise is 0–8.2 mm at 30 mm free and 0–5.7 mm at 35 mm [calc wave3
   §1]. The presser cam squares each crimp before the next index; the next
   key's lower jaw passes over it.
4. **The proof pull's reaction** passes through the cassette clamp on the
   jacket; p1's clamp stop sets a 15–30 % squeeze over 10–20 mm so the copper
   cannot creep [force-and-form calc exchange_procedure_w3 §4].
5. **A camshaft cannot adapt.** It adapts through the cassette and the post
   wheel, both loaded in the same key order with gaps in the same places.

## Contribution

- **The whole priority step on one motor**, around a tool that already makes XH
  crimps on this bench. No applicator, eccentric press or steel frame.
- **The torque figure makes the point:** 2.1–3.2 N·m at the shaft, set by
  Derek's own hand-force range at the handle.
- **The program is physical three times over:** the blanked key, the skip bump
  and the empty post.

## Major unresolved problems

- **The SN-2549's *a*, handle travel and wing-touch position**, all unmeasured;
  *a* sets the lift and the 30–35 mm split.
- **The lever and follower geometry** for a tool lying on its side, handles
  across the row.
- **The fixed-depth axial chain** (±0.21 mm) leaves little margin if the strip
  tear is ragged.
- **Retiming means reprinting cams.**
- **The post wheel's pick** repeatability, and kit contacts' grip on a post.
- **The SN-2549's fixed crimp height and insulation step** on silicone.

## What rests on assumptions

- Handle force and travel are hand-tool-as-press's estimates; the release force
  is unmeasured.
- *a* = 6–12 mm.
- The ~40–60 s turn and the minutes.
- PET-CF contact strength.
