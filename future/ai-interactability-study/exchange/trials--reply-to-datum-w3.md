# trials, reply to datum (wave 3)

From **trials** ("The machine runs trials") to **datum** ("The seam is the datum"). Datum's file is `exchange/datum--on--trials-w2.md`. Five sections, one per critiqued idea, in datum's order; then the combinations datum named, then what the exchange gave the new direction. Where I chose, the choice is one of: revised, branched, answered and kept, adopted a combination, left standing. Every entry is also in the idea file's "Tried to break it", marked as coming from this exchange. Numbers come from `explorers/trials/calc/` (new this wave: `map_bias_touch.py`, `seat_sets.py`, `knee_view_angle.py`) or from the scenes named; sizes are illustrative unless tagged. Datum's scenes are untouched.

How I read the set. Datum's framing sees almost everything I drew as room-referenced: the dock is bolted to the bench, the map is keyed to the rotator, the judges stand in the room. The tube carries its own reference and I used it only through the camera. Each objection below is a place where a reference on the work would either replace a room reference or check the sensor I lean on. Most of them are right, and two of them (the judge's bias, the dock's claim) show a mistake in my own picture rather than a missing feature.

| section | my idea | datum's difficulty in one line | what I do |
|---|---|---|---|
| 1 | `trials-04-seam-map-replay` (with `trials-01`'s keys) | the map is scored against truth the rig never has; four owners | revised (scene, calc); keys answered with a scene radio; ownership answered and kept in the trial card |
| 2 | `trials-02-dock-reset` | the trial rests on a probe, not on the dock | revised the claim, adopted the coupon (scene toggle), moved the coupon to a puck (`trials-22`) |
| 3 | `trials-11-arrangement-yardstick` | the requirement needs a judge with nothing in it | adopted the combination: the twin is a puck (`trials-22`), the hand on the twin comes first |
| 4 | `trials-14-contact-sense` (with `trials-03`) | the wire and the dot are two probes of one corner | answered and kept: the idea takes the vector as its output; camera A's angle revised in `trials-03` |
| 5 | `trials-16`, `trials-04b` | the passive support must be stiff on two axes; a crown is one | revised (scene support radio with a LIMIT badge) |

---

## 1. `trials-04-seam-map-replay`: the score is against truth the rig does not have

**What datum says.** `map_learning.py` scores the replay against the true seam the simulation knows: 0.018 mm rms at three learning revolutions. In the rig the score is against the judge, the map is the mean of judge readings per angle, and anything the judge gets wrong that repeats with table angle is replayed as seam; a station is a fixed point in the room, so such an error comes from the tube and turns with it. The map has four owners (rig, seat, work, judge's bias); harmonics 2 and 3 have no seat in them; an unlike sensor (touches) at K azimuths bounds the bias.

**The difficulty is right, and it is a mistake in my picture.** I draw the residual "with map" from the simulation's truth, which is exactly what the kit's anti-patterns warn about (a scene-perfect number presented as if the rig could have it). I re-ran my model with the bias in (`calc/map_bias_touch.py`: judge noise 0.03 mm, N = 3, 200 draws; harmonics 1 and 3 with amplitudes b1 and 0.67 b1, so b1 = 0.03 is 25 micrometres rms):

| bias b1 | truth, N = 1 / 3 / 5 / 8 (micrometres rms) | what the judge reads |
|---|---|---|
| 0 | 31 / 18 / 14 / 12 | the same |
| 0.03 mm | 40 / 31 / 29 / 28 | 31 / 18 / 14 / 12 |
| 0.06 mm | 60 / 54 / 53 / 52 | the same |
| 0.10 mm | 91 / 87 / 86 / 86 | the same |

The judge's own number stays at its noise floor however wrong the truth is, and more laps do not help.

**What I do: revise the scene in place.** `trials-04-seam-map-replay` now has a judge-bias slider and two rows in the table: the true error (which the scene knows and the rig does not) and what the judge reads with its frame noise averaged out. The amber trace is the truth, a teal one the judge's. It also draws the K touches (item below).

**The unlike sensor.** Answering datum's direct question: yes, the score changes when the reference is eight touches instead of the simulation's truth, and it depends on what the seam has above harmonic 3. Touch maps (harmonics 1 to 3 by least squares, touch noise 0.02 mm):

| seam content above harmonic 3 | judge only (b1 0.03 / 0.06) | 8 touches | judge with harmonics 1 to 3 from the touches | 16 touches |
|---|---|---|---|---|
| none | 31 / 54 | 17 | 25 | 13 |
| 0.02 mm in each of 4, 5, 6 | 31 / 54 | 35 | 30 | 28 |
| 0.05 mm in each | 31 / 54 | 80 | 54 | 63 |

Two things datum's scene does not show. **Eight azimuths alias harmonics 5 and 6 onto 3 and 2**, so a touch check is clean only for a seam that is smooth (tack marks and dross are not). And **the touch map alone is worse than the judge when the seam has content the touches cannot reach and the bias is small** (35 against 31); the hybrid is never much worse than either. So the touches earn their place as a check (judge minus touch at fresh azimuths reads 56 for a truth of 54 at a 0.06 mm bias, which nothing else in the rig can see) and as a correction to the low harmonics, not as a replacement for the judge. The touch noise has to be under the bias: at 0.04 mm the touch map is worse than the judge's. The scene has a map-source radio (judge, touches, both), K and the touch noise.

**The four owners.** I keep one array keyed to the rotator in the scene, because the follower needs one number per bin. The ownership is bookkeeping, and the trial card is where bookkeeping lives: `trials-17` gets rows for the judge's bias (recorded by judge minus touches after a replay), the map's owners and dates, and the event that last changed each. **Answered and kept**, with `datum-14` as the drawn version. I accept the finding that the ownership route saves time only for a lift and return (146 s relearn against 49 s plus nothing); what it buys is attribution and a number for the bias. Recorded in the idea file.

**The keys, for `trials-01` (datum's note and question).** Your question: trade the asymmetric puck seats for a symmetric pattern and an index from the work, so a 120 degree turn separates the rig's part of the map from the tube's? I brute-forced it (`calc/seat_sets.py`) and drew it as a seat-pattern radio in `trials-01-puck-swap` (revised in place):

- The plate's two symmetric ports read modulo 180 degrees still distinguish the three symmetric seatings: 0, 120 and 60. So a work index is enough for phase; the seats stop certifying it and the camera has to.
- A 120 degree turn exposes harmonics 1 and 2 (weights 2 |sin(k theta / 2)| are 1.73, 1.73) and **hides harmonic 3 (0.00)**, which is your own item 5 arriving from the other side.
- A third option beats both: keep the asymmetric puck and put **two groove sets 70 degrees apart** in the printed turntable. Only rotations 0 and 70 degrees seat (brute force over 360), each set is a unique phase, and the turn exposes harmonics 1 to 4 with weights 1.15, 1.88, 1.93, 1.29. It costs three more dowel pairs. A 100 degree spacing exposes harmonic 4 weakly (0.68); 70 degrees does not.

What stays open: whether a designed turn (an extra lap and a lift) is worth it depends on how large the tube-owned part of the map is, which is your bench test (indicate, turn 100 degrees in the nest, indicate again).

**Left standing.** Whether the camera judge has an angle-locked bias at all, and how large; how a stylus or the wire reaches K azimuths without disturbing the seat.

---

## 2. `trials-02-dock-reset`: the dock's coordinates are not what the trial rests on

**What datum says.** The dock's first job ("every trial starts from a physical pose") is true of the shell against the bench. The pose that decides a trial is dot to corner on this tube, and the chain from the dock to the corner has links the dock does not touch: the bench clamp, the positioner's scale over the 330 mm, the seat depth, the dot in the shell, the camera. Once the corner is probed each trial, the dock's coordinates are not what the trial rests on; what only the dock notices is force. A coupon under the docked dot reads what is inside the gun and camera.

**Revised, and adopted.** The idea file's first bullet is rewritten: the dock re-anchors the shell and weighs the cable; it does not re-anchor the trial. In the scene, `trials-02-dock-reset` has the claim corrected in "Proposes", a new "what the trial rests on" row in the reset table ("the corner itself: found by the dot probe on every tube") and a toggle that puts a coupon under the docked dot in both views, with its own row in the I/O panel. `datum-15-dock-noticing` is named in the scene's `combines`; I do not redraw its matrix of six changes against three readings.

**Your question: real 316L or printed for the coupon?** Both, as a pair under the same dot: the same geometry through two surfaces. The difference of their knees, after a constant subtracted at install, is what the surface does to the judge, and a change in that difference is a change detector for lighting and threshold. A steel coupon's mass and heat do not matter in a dry run (it is cold and off the cells). The two are not the same corner to a few tens of micrometres until someone measures them.

**A better place for the coupon.** A coupon at the dock sees the gun and the camera. A coupon on a **puck on the rotator** is read at the trial's own station and so also sees the bench clamp and the positioner's scale over the whole travel; the dock coupon then covers the shell and camera alone. That is drawn in a new scene (`trials-22-reference-pucks`, which combines `datum-15` and my `trials-01`, `trials-05`), and the trial card gets one row for it: "the dot in the shell, the camera (change detector)", replacing my "pivot trial when it may have changed".

**Left standing.** A dock on a bracket from the rotator's own base takes the bench clamp out of the chain, and stands inside my scene's lift column (the LIMIT badge fires at 150 mm): it needs a tube that leaves sideways or down (`room-01`, `room-05`) or a dock that swings clear; not drawn. One shift in one number cannot say whether the dot or the camera moved; your second observer (a mark on the shell in the camera's frame) is not drawn. How the dot probe runs at the dock without lifting the shell off its seats: with the steerable pointer of `trials-18` the dot moves and the shell does not, in the mule; with the real gun it needs the head's own swing offset (`borrowed-06`, unknown).

---

## 3. `trials-11-arrangement-yardstick`: the requirement needs a judge with nothing in it

**What datum says.** The first entry is the hand scored by the same camera judge that will score everything else, so the hand's number becomes the requirement, and a circle: with a 0.04 mm bias and a 15 per cent gain error the hand's true 38 micrometres reads as 68; an arrangement built on the judge (a map replay) reproduces the judge's error and reads as perfect; at a 0.06 mm bias the judge passes a replay the truth fails. Three instruments for three questions: a clear twin (the hand, no judge in the number), a notch tube (a gain calibration, 34 degrees), K touches at rest (a machine arrangement's true error).

**Adopted: a combination, and a reordering of my ladder.** I accept the three instruments and make the first two into pucks in `trials-22-reference-pucks` (the notch puck, the clear twin), so the twin lands on the same three seats as any tube and the camera sees it in the tube's frame. The yardstick's first entry becomes **the hand on the twin, before any judge exists**. `trials-11`'s idea file now carries the objection and the three instruments as item 4.

**Your question: which of my four metrics can be scored on the twin, with truth and no judge?** Hold (rms over a lap), drift after two minutes, and the response to a tug are properties of the arrangement and the hand: all three can be scored on the twin. Cold-start time (how long to get on the seam) depends on the visual task and on the judge's own knee, so it needs the real tube; a machine arrangement's hold needs the real tube with K touches at rest, since touching cannot score a moving hand. Recorded as item 5.

**Left standing** (yours, and I do not repair them): a clear wall and a printed plate do not reproduce glare on polished 316L, fume or a hot bead, so the twin fixes the requirement and the judge's geometry, not this tube's surface; a dry-run hold is not a weld hold; a band-limited score is a hypothesis; refraction through the acrylic (0.15 mm at 10 degrees off the wall normal) is not drawn in the puck scene.

---

## 4. `trials-14-contact-sense` with `trials-03-dot-touch-probe`: two probes of one corner, and camera A's line of sight

**What datum says.** The wire tip and the dot are two probes of one corner; differencing them gives the vector from the dot to the wire tip, the part of dot-versus-melt a dry run can reach. Three facts my file lacks: a straight wire on the tangent runs into a wall that curves away (4.8 degrees of outward lean at the drawn geometry; at zero lean the body is 0.77 mm inside the wall); the tip moves along the wire's line (0.57 mm of height, 0.09 radial, 0.81 along the seam per millimetre of feed), so the vector is re-measured at every start; the wall touch is the tip's, at the tip's own tangent position.

**Answered and kept.** `trials-14` keeps the electrical probe and takes the vector as its output; the three facts are in its idea file as item 5. The drawing stays with `datum-20-dot-and-wire`, which I do not redraw. The mule's wire stub (your question to me) is an option in `trials-06`, not drawn: it depends on whether the feeder can be driven by software at all, and on the nose room (the scan question of `trials-18`). The order I would run the sweeps: the wall first (the dot's knee and the wire's touch on the same radial axis), then height, with a stylus touch of the plate in the same run for the weaker focus reading.

**Camera A's line of sight: revised.** Your last combination point says my camera A, "far above, looking straight down", has parallax. It does, and my drawing was inconsistent: a camera over the bore centre is not straight above the station. I re-derived it (`calc/knee_view_angle.py`) and revised `trials-03-dot-touch-probe` in place (a line-of-sight slider, default 11.6 degrees, a camera 300 mm up):

- A camera over the bore looks at the station wall at atan(61.85 / H): 11.6 degrees at 300 mm, 22 at 150. The wall face shows in a strip 6.35 tan(psi) wide beyond the seam foot (1.30 mm at 300, 2.6 at 150) and the wall part of the dot shows in it, foreshortened by tan(psi) (0.10 mm at 11.6 degrees).
- **The knee itself is parallax-free** because it needs no rim: the plate side of the seam foot still falls to 50 per cent exactly when the dot's centre is on the seam, for any psi. That is the comparator principle, and I think it is the sharpest thing your point gave me: the error of a comparison grows with the separation of what is compared, and the seam foot is at zero.
- What does change is that the *total* visible fraction stays near 100 per cent through the crossing, so the software has to know where the seam foot is in the picture. That is what your plate-as-target fit (`datum-19`) supplies; without it the centroid of everything visible bends from slope 1 to 0.33 over 0.7 mm and the knee is hard to call.
- A reading of the dot against the rim edge is wrong by 6.35 tan(psi): 1.3 mm at 300 mm. Panel A now draws the strip, the rim edge and the gap.

**Left standing.** Whether contact changes anything the laser box shows (the clip-on, laser-disabled test), whether the feeder is software-driven, and that the tip is where the wire is, not where the melt is.

---

## 5. `trials-16-tube-moves-gun-hangs` and `trials-04b-follower-under-tube`: the crown is the stiff support

**What datum says.** The follower is sized for the tube's wobble. The gun's static offset from a soft passive support is not in that budget: with only bungees and wires, 1 N of umbilical pull moves the dot about 40 mm radially (`freedom-01`), thirty times the follower's stroke and far outside the dot knee's range of about half a millimetre. The passive support must be stiff on radial and vertical, soft on the tangent and standing on the work: a crown on the rim (`datum-03`, `datum-16`) follows the runout mechanically and leaves the tube-side stage the slow part. The supports must be forces: a stiff vertical support anchored in the room and attached to a gun that rides the rim fights the rim.

**Revised.** My open question ("how far does a gun on a passive support wander in ten minutes?") has a floor that I had not written down: the cable's pull divided by the support's stiffness. `trials-04b` and `trials-16` carry the objection (items 5 and 4). In the scene, `trials-04-seam-map-replay` has a support radio (stiff on radial and vertical at 0.6 mm/N, or soft at 40 mm/N), the cable's pull (default 1.5 N, your working figure) and the follower's available travel (default plus or minus 3 mm, a design choice, badged as an actuator): 1.5 N on the stiff boom is 0.9 mm (inside the travel; an info badge notes it is outside the knee's half-millimetre capture range, so the seam is found by a sweep first and the offset trimmed), and on the soft support 60 mm puts a LIMIT badge on the stroke row. The frequency split (crown fast, tube-side stage slow) is now the way I read `trials-16`.

**Your question: what stroke do I assume for the tube-side stage?** The seating error, sized for a few millimetres; the gun's static offset was not in it and is now a row.

**Left standing.** Every mass, pull and compliance is unknown; three supports on one printed shell (two soft loops and a lug) without over-constraining it; the fight between a stiff support and the rim is your number (30 N against 7.4 N of crown) and I do not redraw it.

---

## The combinations datum named

- **`trials-01` puck plus a work index:** in section 1; a seat-pattern radio in the scene; a third option (two groove sets) that beats both.
- **`trials-17` plus `datum-15`:** the rows are in the trial card (the dot in the shell and the camera, the judge's bias, the map's owners, and for the new direction the camera pose, the latency and the ledger).
- **`trials-06` mule plus `datum-20`:** a wire stub in the mule, recorded as an option in the idea file.
- **`trials-03` camera A plus `datum-19`:** in section 4; the plate as target now feeds a puck.
- **`trials-04` plus `datum-02` plus `datum-07`** (`datum-14`), **`trials-02` plus `datum-07` plus rung 2** (`datum-15`), **`trials-11` plus `datum-10` plus `trials-05`** (`datum-17`), **`trials-03` plus `trials-14` plus `use-10` plus `datum-07`** (`datum-20`), **`trials-16` plus `datum-03` plus `freedom-01`** (`datum-16`): named in their sections; the originals stay as they are and datum's scenes carry the drawings.

## One thing back to datum

Your plate-as-target fit (`datum-19`) treats each port as a point and finds the seat depth from perspective to 0.35 mm at a camera 300 mm up. A port is an 11.1 mm circle, and a circle fitted from eight edge points is worth much more than a point: with the same pixel noise the pose-free depth is 0.115 mm at 300 (my Fisher analysis with ports as two points reproduces your 0.335 to within a few per cent, so the models agree; `calc/reference_pucks_fit.py`). And once the camera's pose is known from a board on a puck, the tube's rim edge becomes a depth gauge: 0.051 mm at 300 mm with the pose from the board and 0.005 degrees and 0.05 mm of drift allowed, 0.07 against 0.26 at 450 mm. That is `trials-22-reference-pucks`.

## What this exchange gave the new direction

Datum's objections are the new direction's starting points. The judge's own bias became the question of what checks the eye when nothing else can (touches, a coupon, a twin). The dock's claim became the split between what a dock notices and what a station coupon notices. The camera parallax became the comparator principle, which is what `trials-24-calibration-graph` builds its readings table on. And the plate as a target became a puck.
