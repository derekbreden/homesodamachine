# trials: "The machine runs trials", every arrangement held

Framing: the station is an instrument for many repeated dry-run experiments conducted by software, an AI iterating for hours or days across tubes, judging by cameras and the laser dot. Maturity says how far an idea has been taken, not how good it is; nothing here is ranked. Kept current through wave 3 (observed 2026-09-29). Bold rows were added after wave 1 (waves 2 and 3).

Files: idea files `ideas/<id>.md`; scenes `scenes/<id>/index.html`; calc scripts `calc/`; sourcing `../../sourcing/trials.md`; log `notebook.md`; exchange with borrowed `../../exchange/trials--on--borrowed-w2.md`; my reply to datum's critique `../../exchange/trials--reply-to-datum-w3.md`.

| id | arrangement, one line | maturity | scene | idea file |
|---|---|---|---|---|
| trials-01-puck-swap | Nest and tube form a puck on three kinematic seats; indicating moves to a prep stand; the puck carries a seated check, phase, an index and a tag (wave 2: or a tag ring read by the judge camera, borrowed from datum-05; wave 3: a seat-pattern radio: asymmetric, symmetric with the phase read from the work's ports, or two groove sets 70 degrees apart) | deep | `scenes/trials-01-puck-swap` | `ideas/trials-01-puck-swap.md` |
| trials-01b-nest-as-puck | Smallest puck: keep the nest, replace its three M3 screws with ball-and-dowel seats | sketch | (branch radio in 01) | `ideas/trials-01b-nest-as-puck.md` |
| trials-02-dock-reset | The gun returns to a kinematic cradle between trials: re-anchors the shell (not the trial: the corner is probed on each tube), clears the swap, weighs gun and umbilical on three cells, one-sided final approach (wave 3: a coupon under the docked dot as a toggle, adopted from datum-15) | deep | `scenes/trials-02-dock-reset` | `ideas/trials-02-dock-reset.md` |
| trials-03-dot-touch-probe | Sweep the dot across the corner; the plate part vanishes at the seam (the knee); spot size gives standoff; the plate's reflection is a ruler (wave 3: camera A looks at the wall face from over the bore, so the dot no longer vanishes and the rim edge is 6.35 tan psi from the seam foot; the knee needs the seam foot's image position) | deep | `scenes/trials-03-dot-touch-probe` | `ideas/trials-03-dot-touch-probe.md` |
| trials-04-seam-map-replay | Learn the seam's radial and height wobble per rotator angle in the first turns, replay it on a small follower (wave 3: the judge's own angle-locked bias is replayed as seam; touches at K azimuths as a check or a correction; a passive support's static offset against the follower's travel) | deep | `scenes/trials-04-seam-map-replay` | `ideas/trials-04-seam-map-replay.md` |
| trials-04b-follower-under-tube | The follower is an X slide plus a small lift under the rotator; the gun hangs passive | sketch | (radio in 04) | `ideas/trials-04b-follower-under-tube.md` |
| trials-05-artefact-ladder | Five workpieces isolate difficulties: board, coupon, notch tube, printed zoo, real tube; two judge cameras | developed | `scenes/trials-05-artefact-ladder` | `ideas/trials-05-artefact-ladder.md` |
| trials-06-mule-gun | Instrumented printed stand-in for the gun: ballast, switchable dot, IMU, tip switch, dummy umbilical | developed | `scenes/trials-06-mule-gun` | `ideas/trials-06-mule-gun.md` |
| trials-07-toolchange-swap | One positioner parks the gun, picks a gripper, exchanges pucks with a rack; a coupling moment check | sketch | `scenes/trials-07-toolchange-swap` | `ideas/trials-07-toolchange-swap.md` |
| trials-08-loader-tended-cell | Everything motorised except the tube swap; software asks for tube N and verifies the seat (wave 2: the swap as a drawer, from room-05) | sketch | none | `ideas/trials-08-loader-tended-cell.md` |
| trials-09-tube-zoo | Printed tubes with designed errors: plate depth, offset, ovality, tilt | sketch | (rung 4 in 05) | `ideas/trials-09-tube-zoo.md` |
| trials-10-human-labelled-jog | Motors jog the dot; Derek taps good or a nudge; the taps train a camera judge | sketch | none | `ideas/trials-10-human-labelled-jog.md` |
| trials-11-arrangement-yardstick | One judge and one script score any way of holding the gun; the first entry is Derek's hands (wave 2: the encoded arm is its recorder; wave 3: the hand is scored on a clear twin with no judge in the number, machines by K touches at rest) | sketch | none | `ideas/trials-11-arrangement-yardstick.md` |
| trials-12-encoded-manual-axes | Hand-driven stages with digital scales; software reads every knob and advises | sketch | none | `ideas/trials-12-encoded-manual-axes.md` |
| trials-13-pivot-calibration | Tilt the gun about where the software thinks the dot is, with the dot on a board; the wander gives the dot's true offset (wave 2: generalised in trials-19) | sketch | (in 05) | `ideas/trials-13-pivot-calibration.md` |
| trials-14-contact-sense | The gun's circuit or the wire tip as a touch probe; the ready lamp as a free sensor (wave 3: with the dot's knee it gives the vector from the dot to the wire tip, `datum-20`) | sketch | none | `ideas/trials-14-contact-sense.md` |
| trials-15-one-tube-many-poses | Swaps are the outer loop: hundreds of trials per loaded tube, blocked by tube with a golden reference | sketch | none | `ideas/trials-15-one-tube-many-poses.md` |
| trials-16-tube-moves-gun-hangs | The only actuator is a stage under the rotator; a camera closes the loop (wave 3: the passive support must be stiff on radial and vertical; a crown is one) | sketch | (radio in 04) | `ideas/trials-16-tube-moves-gun-hangs.md` |
| trials-17-trial-card | The table of nuisance factors: reset by design, recorded, randomised or uncontrolled (wave 2: drift, calibration id and golden-tube rows; wave 3: rows for the dot and camera coupon, the judge's bias, the map's owners, camera pose and lens, latency, the ledger) | lens | none | `ideas/trials-17-trial-card.md` |
| **trials-18-steerable-mule** | A steerable pointer, a nose mirror or the gun's own swing offset moves the mule's dot across the corner with nothing else moving; the knee finds the seam in pointer units and every later command is a labelled offset (combination: borrowed-10, borrowed-06, trials-06, trials-03) | developed | `scenes/trials-18-steerable-mule` | `ideas/trials-18-steerable-mule.md` |
| **trials-19-fixed-point-cal** | The dot on one printed cross from many orientations, read by a camera: a fit calibrates an encoded arm (borrowed-03) or a gimbal-and-gantry formula (borrowed-02); scored on fresh poses (combination) | developed | `scenes/trials-19-fixed-point-cal` | `ideas/trials-19-fixed-point-cal.md` |
| **trials-20-guide-at-the-knee** | Borrowed-05's guide loop guides on the visible fraction (50 %) instead of the centroid, because the wall hides half the dot at the seam (branch of borrowed-05) | developed | `scenes/trials-20-guide-at-the-knee` | `ideas/trials-20-guide-at-the-knee.md` |
| **trials-21-rim-vs-seam** | Does a tonearm foot on the rim help? It removes what the rim and the plate face share and adds what they do not; break-even is 0.135 degrees of parallelism; a corner ball needs no such assumption (branch of borrowed-07) | rough | `scenes/trials-21-rim-vs-seam` | `ideas/trials-21-rim-vs-seam.md` |
| **trials-22-reference-pucks** | The artefact ladder made into pucks on the same three kinematic seats as any tube: a matte board with the tube's rim ring and ports and a dense grid, a real-steel coupon, a notch puck, a clear twin, a golden tube. The board's frame is the tube's frame; the same rim-and-ports fit runs on both; a camera pose from the board turns the next tube's rim edge into a seat-depth gauge (branch and combination of trials-01 and trials-05, with datum-19, datum-15, datum-17) | deep | `scenes/trials-22-reference-pucks` | `ideas/trials-22-reference-pucks.md` |
| **trials-23-frame-clock** | Time is a calibration: sweep the dot across the seam both ways at two speeds and the seam, the chain's latency and the backlash come out of four knees; a step at a random phase finds latency to a millisecond; compare at rest; trigger the exposure from the axis or put a Gray-coded counter in the frame (a lens; combines trials-03, trials-18, trials-04) | developed | `scenes/trials-23-frame-clock` | `ideas/trials-23-frame-clock.md` |
| **trials-24-calibration-graph** | The loop's calibrations form a graph: an event makes some stale (a full trial) and what leans on them suspect (a cheap check); run upstream first or the result inherits the error; a comparison in one picture does not lean on the camera's pose; four other explorers' arrangements (gantry, cords, hexapod, encoded arm) add their own numbers (a lens) | developed | `scenes/trials-24-calibration-graph` | `ideas/trials-24-calibration-graph.md` |

## Questions that need Derek's observation, with the idea they belong to

- **Gun mass and centre of mass** (weigh it; hang it from two points): trials-02 (dock cells), trials-06 (mule ballast), trials-07 (coupling moment), trials-19 (borrowed-02's balance, borrowed-03's spring rating).
- **Which way the umbilical pulls at each working pose, and how hard**: trials-02, trials-06.
- **Photograph the dot on the plate at three heights, and at the seam**: is there a second spot on the wall; how big; does it fade or cut at the seam (trials-03, trials-20).
- **Can the laser box blink its dot, or light the red light alone**; what does the RS232 or DB25 port offer (trials-03, trials-06, trials-18).
- **With the clip on and the laser disabled, does any lamp change when the nozzle or wire touches the tube** (trials-14).
- **Lift and re-seat one tube ten times with the indicator; how long a swap plus indicating takes** (trials-01, trials-08, trials-15).
- **Indicator at the rim over ten revolutions, the same angle each time: how much of the runout repeats** (trials-04).
- **Two indicators (rim, plate face) over one revolution on three tubes; how the 6.35 mm recess is set** (borrowed-07, trials-04; exchange section 5).
- **How far off the seam can the dot be, at what angle, and still make a good weld** (trials-04, trials-11).
- **Would you hold the gun in a dry run for ten revolutions while a camera watches** (trials-11).
- **Ten measurements of real tubes: length, plate seat depth, out-of-round** (trials-09, trials-04b).
- **Scrap tube ends for a notch tube; can the Bambu printers make a 127 mm tube with an inserted plate** (trials-05).
- **Are you comfortable with an unattended class 2 red pointer running near the bench** (trials-06, trials-18).
- **How thin the printed nose can be at the nozzle tip (from the scan)**: decides whether a mirror fits (trials-18).
- **Play in a monitor-arm joint under 1 kg at a 500 mm lever** (a dial gauge across the joint): trials-19.
- **How many different tubes in one unattended session: five or fifty** (trials-07).
- **A phone picture of the bore from 300 mm and from 150 mm straight above: are both rim circles and both ports sharp; does the wall's inner face show as a strip?** (trials-22, trials-03; datum-19's question, still the cheapest photograph).
- **A printed sheet against calipers: how far off is the grid pitch over 100 mm?** (trials-22: the printed board's scale is the ruler).
- **Ten lifts and re-seats of any puck-shaped print with the indicator on the flange: is 10 micrometres per landing believable?** (trials-22, trials-01).
- **Indicate a tube at the rim, turn it 100 degrees in its nest, indicate again: what part of the runout turned with the tube?** (trials-04, trials-01: sizes the tube-owned part of the seam map and decides whether a designed puck turn is worth a lap).
- **A phone in slow motion (240 fps) filming a display and the camera's preview at once: how far behind is the preview?** (trials-23: a rough latency in one take; does the camera you would use have a trigger input?).
- **When something is suspect but not stale, should the loop stop and ask a person, or carry on with provisional readings?** And which events really happen on the bench in a week (a bumped camera, the light through the day, a re-routed cable)? (trials-24).

## Supporting material

- Calc: `calc/dot_probe.py`, `seam_rates.py`, `swap_budget.py`, `dock_scale.py`, `pivot_cal.py`, `map_learning.py`; wave 2: `arm_touch_cal.py`, `gimbal_fixed_point.py`, `guide_at_knee.py`; wave 3: `map_bias_touch.py`, `seat_sets.py`, `knee_view_angle.py`, `frame_clock.py`, `reference_pucks_fit.py`, `lens_from_pucks.py`, `eye_ledger.py` (each with its `.out`).
- Sourcing (wave 1 and wave 2): `../../sourcing/trials.md`.
- Wave 2 exchange (my critique of borrowed): `../../exchange/trials--on--borrowed-w2.md`. Wave 3 (my reply to datum's critique): `../../exchange/trials--reply-to-datum-w3.md`.
