# Notebook: use (the day of use)

Framing: someone or something sets up for a tube, establishes a working neighbourhood, dry-runs the dot, welds, retracts, swaps, repeats. The arrangement is a sequence of states with handovers.

Tags used below follow `context/shared-context.md`: **[Derek] [repo] [manual] [derived] [unknown]**, plus **[illustrative]** for a number I made up to see its effect and **[assumed]** for a handbook or common-practice value I did not check.

## Wave 1, step 1: arrangements the framing suggests (one line each, before developing any)

Written before drawing or calculating. Silly and flawed ones included on purpose.

- **A1 Flight recorder.** Nothing moves. The hand welds as today, but a camera, the rotator's degrees readout and a trigger-sensing tap log every weld as an experiment record. The AI reads traces plus PT/section results. Software observes, moves nothing.
- **A2 Programmed table.** Nothing observed but degrees. The ESP32 runs `index 8 tacks`, `dry lap`, `bead 380 deg` under the pedal deadman; the hand holds the gun on a plain rest. Software moves the tube, observes nothing new.
- **A3 Coach with instrumented manual axes.** The gun sits on a friction/locking arm with hand knobs on three fine axes that each carry a digital scale. A camera reads the dot against the seam; the screen tells the hand "z +0.40". The hand is the actuator; software is the witness and the instructor.
- **A4 Swing head.** Two commanded states, not positions: swing (park / seat) and plunge (retract / engage along the beam). Position comes from a kinematic seat and hard stops; the fine pose is set by three screws once per campaign. The AI can run repeat-seat dry-run experiments unattended.
- **A5 Preset cartridge.** The nest plus tube is loaded, height-set and indicated off-line at a presetter while the last tube is still on the rotator; the gun sees a pre-normalised seam. The tube brings its own correction; the gun is not re-aimed between tubes.
- **A6 Ping-pong stations.** Two rotators, one gun that swings (or a table that slides) between them, so loading, indicating, PT and cooling overlap laser time. Same head, two seats.
- **A7 Wire-first dry run.** The feeder's jog button advances the wire with the laser off [manual p.18]; the wire tip shows where the wire lands relative to the dot. Continuity to the shoe says "wire touching metal". The consumable becomes the probe. (Silly form: wire-touch corner finding with an insulated plate. Useful form: a wire-landing check inside the dry lap.)
- **A8 Gates: attended vs unattended.** The day is a state machine whose transitions have owners: dry-run states can be AI-only (red dot, 0.3 mW [manual p.12]); the weld states need the hand. Software may veto, only a hand fires. Exceptions (blink, stuck wire, seat not proven) are states of their own.
- **A9 Setup gauge ("tube 0").** A printed gauge tube with an open window and a target replaces the tube in the nest. The gun is set on the gauge where eyes and a camera can see the corner, then the real tube is swapped in. Other reference, other sequence.
- **A10 Golden-tube morning.** First thing each day a reference tube runs the whole cycle as a drift check; today's dry-lap trace is compared with the stored baseline, so the AI notices what moved overnight before any real tube is committed.
- **A11 Lap 1 is the dry run, lap 2 is the weld (feed-forward).** The table never stops. The dry lap records the dot-to-seam signature against tube angle; the weld lap replays a correction keyed to the rotator's degrees. A one-axis follower (or the hand) does the slow correction.
- **A12 Silly ones taken far enough to find a use.** (a) Tilt the rotator so the gun can point straight down: it fights downhand welding, but a tilted setup state could show the dot to a camera. (b) Rotate the human: a stool on a turntable so the hand never crosses the umbilical: silly, but it names a real issue, the hand-plus-cable orbit. (c) Teleoperation with motion scaling: the hand drives a replica handle, the machine follows at 1:5 with a clutch: the useful form is "coarse by hand, fine scaled through a micrometer-style reduction", which is what A3's knobs are.

Lens scenes (not arrangements; ways to see the same day): the swim-lane day (who holds, who looks, who decides in each state), the lap (what changes over one revolution and at what rate), and the gates (which transitions the software may take alone).

## Wave 1, step 2: what I chose to develop

Depth (several rounds each): **A4 swing head** (`use-02-swing-head`), **A5 preset cartridge** (`use-03-preset-cartridge`), **A3 coach with instrumented manual axes** (`use-06-coach-loop`). Lenses developed: the swim-lane day (`use-01-day-lanes`), the lap and time axis (`use-04-the-lap`, which carries A11), the gates (`use-05-gates`, A8). Rough scenes: two stations (`use-07-two-stations`, A6), wire-first (`use-10-wire-first`, A7), setup gauge (`use-11-setup-gauge`, A9). Sketch ideas with files and no scene: flight recorder (`use-08-flight-recorder`, A1), programmed table (`use-09-programmed-table`, A2), golden tube (`use-12-golden-tube`, A10). A12 (silly ones) is worked in place in the arrangement list above: its useful forms are the hand-and-cable orbit (folded into the swing head's cable rule) and coarse-by-hand, fine-by-reduction (A3's knobs).

**The order I worked in, and why.** The lanes scene came first in my head but I built the swing head first: a mechanism with a sequence exposes ambiguities (what the arm does at the seat, where the cable goes) that a lens does not. The lens scenes then came out of what the mechanism scenes forced me to say: the hand-time readout after the preset cartridge showed the presetter does not save hand time; the gates lens after the swing head asked who may run the sequence alone.

## Round log: A4 swing head (use-02-swing-head)

**R1, the first shape.** Two states the machine spends most of the day in are "head clear of the tube" (load, indicate, plate, PT handling) and "head at the seam" (tack, dry lap, weld). Today the hand makes that handover for free; a supported gun makes it a mechanism. First thought: a hinge about a horizontal axis outside the tube. Numbers (`calc/swing_path.mjs`, kit proxy gun at the opening pose, which is illustrative): the nozzle tip sits at (54.6, -8.6, 157.4), only 5 mm above the rim (152.4), so a single hinge about a horizontal axis moves it up and inward over the bore, the wrong way. A vertical-axis swing about a post 330 mm behind, moving the head outward (clockwise from above), leaves over the near wall and clears the swap volume (r 95 mm, top 217 mm, both illustrative) after only 10 to 30 degrees for posts 260 to 380 mm away, roughly 65 to 150 mm of arc at the nozzle. So the swing is short; a linear slide is the limiting case of a far post, and the scene's post-distance slider shows the family.

**R2, break: does the swing need a plunge at all?** In the proxy geometry a horizontal swing at seat height clears the rim by about 3 mm with no collision, so the plunge is not strictly required for clearance. But 3 mm on an unmeasured nozzle is not a margin, and the end-of-bead sequence (lift the head "straight away" with the trigger held, so the wire breaks in the air [repo]) already needs a short motion along the beam. Each mm of plunge along the barrel axis adds about 0.7 mm of clearance over the rim (0.712 is the axis's vertical component). The plunge stays, doing three jobs: the retract, the seating stroke, and margin over the rim. Rule: no swing until the plunge is at least 20 mm out. What it leaves: the real nozzle, standoff and pitch have not been measured.

**R3, break: what locates the dot, the arm or the seat?** An arm on a bearing has slop; a printed stop has slop; a rail has play; the dot sits ~280 mm from a grip pivot (derived, shared context). If the arm sets the pose, every one of those is in the error chain. Repair: let the arm only bring the gun near a seat and let a six-contact kinematic coupling (three balls into three grooves) locate it. The gun is then held by the fork and the arm is compliant; a float (spring, plus tie-rods with nuts for the lost motion) hands the load from arm to seat. `calc/seat_amplification.mjs`: for a coupling contact circle of 30 mm and the dot about 130 mm from its centre, a random 5 um error at each contact moves the dot about 25 to 30 um RMS (amplification about 5 to 6). So the seat contacts are not what limits repeatability if they are hardened; the preload against umbilical pull is (same script: a 5 N pull at 250 mm lever with a 30 mm contact circle needs about 40 N of preload, all illustrative because the umbilical stiffness is [unknown]). Leaves: printed groove wear and creep, and the gun-to-shell fit, nobody has measured.

**R4, break: the umbilical.** The fibre must not bend tighter than 240 mm stored or 350 mm emitting [manual p.20] and the cable leaves the grip base along the dot-to-grip-base line, up and back (`calc/cable_swing.mjs`). A Bezier stand-in from that exit to a hook gets below 200 mm at any hook closer than about 0.4 m; the run must be nearly straight for the first half metre. A hook on a fixed mast makes the swing bend it (a 150 mm sideways miss over 450 mm gives 326 mm, under the emitting figure but fine for the stored swing); a hook on the arm moves with the gun and only the 40 mm plunge changes the bend (min radius above 1100 mm at 450 mm). Rule: the cable rides on whatever moves with the gun. Leaves: the drawn Bezier has no stiffness, weight or twist. Twist is forbidden by the manual and a swing about a vertical axis with a fixed cable end twists it unless the run is long and free.

**R5, break: the fork itself.** Drawing the fixed fork showed it sits in the tube-swap volume: its low corner dips because the fork plane is normal to the barrel axis, tilted 45 degrees (`calc/fork_clearance.mjs`). At the first flange position it clears the illustrative volume by 2 mm; at 100 mm behind the nozzle it intrudes 6 to 13 mm. Repair: move the seat back along the barrel (a 130 mm seat clears by 12 mm) at the price of a slightly longer lever (amplification 5.1 to 5.6). The scene has this as a slider. Leaves: cantilever stiffness of the fork and seat arm under preload.

**R6, break: the exception.** A wire fused into the bead (the repo snips it with the head where it stopped) means the retract cannot complete. The plunge stops after a few millimetres (in the scene 4). The software sees it as a timeout on the retract end-stop; the hand snips. The force at which the plunge gives up matters: a 0.030 in (0.76 mm) wire has 0.46 mm^2 of section, so at about 590 MPa (the spec-sheet figure for deposited ER316L, from a search summary; spool wire unchecked) it takes about 270 N to break, far more than a small lead screw should push; the retract must be force-limited and must not be the thing that breaks a fused wire. Leaves: what force the tube and the backdrivable rotator would tolerate before something moves.

**What the drawing exposed that thinking had not:** (1) the two load paths and the handover between them (the float), (2) the fork versus swap volume, (3) that the arm needs a hook-carrying jib to keep the cable geometry, (4) the swing being tiny, so slide and swing are one family, (5) that a "commanded state" can be verified with one bit (seat continuity) but says nothing about where the dot is: only a camera or a dry lap does.

## Round log: A5 preset cartridge (use-03-preset-cartridge)

**R1, the shape.** The seam's height above the nest depends on this tube's length (rim is the reference for the 6.35 mm recess [repo]); the radial position depends on the three screws and the nest. If both are set off the rotator, the gun never needs re-aiming between tubes. Measurement and setting move to a presetter; the pallet (nest + tube) is the unit that travels. Software's job is to turn a one-dimensional gauge reading and an indicator trace into advice.

**R2, break: the height ring.** First idea for setting height: a fine-pitch threaded ring. A thread with 0.1 mm of clearance over 40 mm engagement tips the tube 2.5 mrad, 0.36 mm at the rim, more than the whole radial allowance [repo 0.25 mm TIR]. Repair: flat stacked or printed rings, and keep their parallelism error d small: it goes 1:1 into face TIR and 1.15:1 into radial eccentricity at the weld end (`calc/preset_budget.mjs`). Unmeasured.

**R3, break: the register.** The cartridge can sit anywhere within its register clearance on the rotator; that clearance adds directly to the radial TIR after the indicating was finished. Repair: a three-ball, three-groove register with magnets, or a verify pass on the rotator. Unmeasured.

**R4, break: the advisor.** The three-screw geometry gives `advance_i = e . r_i` for screw i at 120 degrees; they sum to zero so one always backs off. `calc/screw_advisor.mjs`: converges in 1 to 3 rounds for a hand accurate to 15 degrees of a turn unless the tube's own out-of-roundness makes the floor (2 o) exceed the target; nothing any screw does helps then. That is a finding about the tube, surfaced by the measurement.

**R5, break: does it save any time?** Building the lane scene's hand-time readout showed that preparing the next tube at the presetter costs the same person the same minutes. Presetting frees the *station*, not the *hand*. What cuts hand time is the advisor (fewer rounds of indicating) or a seat (no aiming). I had assumed parallelism was the win; it is only a win if the station, not the person, is the bottleneck. Left standing and visible in both scenes.

**What drawing exposed:** the cartridge's z compensation needed the tube group to sit on a wrapper so the kit's seam maths could be corrected by the length deviation; the ID pattern on the collar made "the pallet carries its own record" tangible; and putting the corner inset next to the trace made it obvious that a wobble exaggeration scales the inset numbers too (default 1).

## Round log: A3 coach with instrumented manual axes (use-06-coach-loop)

**R1, the shape.** A hand is a perfectly good actuator if it is told what to do and its result is read back. A magic-arm-class friction arm carries the gun; a two-knob stage with digital scales trims it; a camera estimates the dot's offset from the seam; the screen says "knob X plus 4 notches".

**R2, break: the lock.** My first loop locked the arm every round; a lock shift comparable to the window (0.20 mm against 0.10 mm) left 39 percent of loops unconverged. Repair, found by writing the loop as a script rather than arguing it: put the fine knobs downstream of the lock, so the arm locks once and the knobs trim after it. The arm lock shift then barely matters; the camera noise and any shift the stage itself suffers each round set the rounds (`calc/coach_loop.mjs`). A design rule for any supported gun: **the last adjustment must come after the last thing that shifts**.

**R3, break: camera noise against the knob step.** Advice chases noise when the camera's error exceeds the knob step; at 0.05 mm noise about 2 rounds, at 0.20 mm about 60 percent never converge (illustrative). The real camera error at a 6 mm recess against a wall may be much larger, or the view may not exist (see `use-11-setup-gauge`).

**R4, break: the supported gun without a seat loses its pose at each swap.** The coarse-error slider is what the hand leaves each time. This is what `use-02-swing-head`'s seat is for; they are two answers to one problem (per-tube re-aiming), kept side by side.

**R5, break: payload.** Magic arms are sold for cameras; the gun's mass is unknown. Left as a question with a kitchen scale as the answer.

## Round log: the lenses and the smaller scenes

**Lanes (`use-01-day-lanes`).** Two things surprised me while filling the grid. (1) The dry lap has no home in the repo's sequence (only a continuity revolution and the commissioning rehearsal), so the column had to say so. (2) With illustrative durations the laser is on for a sliver of a closure; the weld is not where the day goes. Both are visible at once because of the to-scale bar above the columns. The first version of the readouts (station time, laser time) misled about presetting, which is why I added the hand-time readout. Totals appear only for the selected arrangement; nothing is coloured better or worse.

**Lap (`use-04-the-lap`).** `calc/lap_rates.mjs`: a 0.25 mm radial runout at 8 mm/s slews at 0.016 mm/s (0.030 mm/s at 15 mm/s); to hold 0.02 mm the correction needs an update about once a second. That reframes what a corrector must be: slow and weak, with resolution and backlash the real specification. Fast disturbances (tremor, the head's vibration motor, the 80 Hz wobble) want a rest or a seat, not a servo. The gun-side lever (0.081 mm per arcminute at the dot) says any slow axis belongs at the dot end.

**Gates (`use-05-gates`).** The interesting design choice was making the *policy* the variable rather than deciding. In every policy emission needs a person, closed hardware and a hand; software gets a veto only. Faults became states because "a blink" and "a fused wire" each need a place to go that only a hand can leave. Two questions only the machine can answer: does the red dot stay on with the key out, and does the X1 Pro have an input that can take an inhibit (its DB25 is documented only as "for PLC integration by customers" [manual p.16]).

**Two stations (`use-07-two-stations`).** Two results I did not expect. (1) The fibre's bend radii make a moving head's cable the binding constraint: with a fixed cart 500 mm beyond the rail, a half-speed trolley meets 350 mm at the seats only with the cable rail about 1.0 m behind the tubes; a fixed midway hook needs about 1.2 m; a hook riding with the head moves the problem to the cart run (`calc/two_stations.mjs`). (2) A second station recovers only the hands-free window: with the illustrative durations four tubes finish at 68.4 min on one or two stations if the dry lap needs a person and 64.4 min if it may run alone. One person prepares one tube at a time.

**Wire first (`use-10-wire-first`).** The kit aims the wire at the dot by construction, so no other scene can ask where the wire lands. The useful finding is that rotation direction sets the arriving side and therefore the side of the gun: it is a campaign-level state, not a parameter. The feeder's jog buttons (manual p.18) make a wire-inclusive dry run possible in principle.

**Setup gauge (`use-11-setup-gauge`).** The line-of-sight test in the kit is what made this idea concrete: with the real tube in, the outside camera is blocked at every azimuth tried; with a window in the gauge it is not. The swap cost is the gauge's own error plus the register's repeatability, both unmeasured.

## Sourcing highlights

See `sourcing/use.md`. What mattered: printer-class motion parts (NEMA 17 with a T8 lead screw at $25.59; a 27:1 planetary NEMA 17 from the same vendor as the rotator's motor at $41.91), a 6 inch lazy-Susan at $6.95 with 300+ bought in past month, 6 mm G25 balls at $7.99 for 200 (1,865 ratings), a magic-arm kit at $19.99 (3K+ bought in past month; camera payload only), a UVC camera at $19.99 (100+ bought in past month), and the honest gap: no Prime-listed digital indicator under $100 lists a data output. The cheap route to software-readable gauges is the caliper-style clock/data pads or a Digimatic port and cable ($58.67 cable; the indicators are about $551), both documented by open-source readers but unchecked here. A 12 V actuator with limit switches is $29.99 but rated 1500 N: far too strong for a retract that must never break a fused wire (about 270 N to break, derived).

## Practical notes on the goals (lead time, price, volume, building, function)

- Every part named for the swing head, presetter and coach loop is a printer- or camera-class commodity available with Prime delivery the same week; none needs a quote. The only long lead item in the whole set is not a part: it is the measurement of the gun's mass and the tube-length spread, which are free.
- The idea set is deliberately printable: shells, forks, nests, rings, gauges, brackets. The seat's balls and the indicators are the bought precision.
- "Function very well" is most at risk in three places: seat wear and creep on printed grooves, the umbilical's bend radius, and whether the wire lands where the dot is. Each has a cheap physical test that no drawing replaces (20 seat cycles with the indicator; a paper test with the cable; a paper test with the wire).

## Summary of every arrangement held (end of wave 1)

(The coordinator's convention is a separate `summary.md`; the tool refused to write a file by that name, so the summary lives here and is repeated in the structured return.)

Framing: someone or something sets up for a tube, establishes a working neighbourhood, dry-runs the dot, welds, retracts, swaps, repeats. Every idea is swarm-originated (Derek's named examples were not seen). Nothing is ranked; maturity is depth only.

### Ideas with scenes

| id | what it is | maturity | scene |
|---|---|---|---|
| use-02-swing-head | Swing arm + short plunge along the barrel axis bring the gun beside a three-ball seat and seat it; software commands states, the seat sets position; a float hands the load from arm to seat; re-seat scatter | deep | `scenes/use-02-swing-head` |
| use-03-preset-cartridge | Nest + tube travel as a cartridge, height-set and indicated at a presetter while the last tube is on the rotator; software turns gauge and indicator readings into screw and ring advice; the gun never moves | deep | `scenes/use-03-preset-cartridge` |
| use-06-coach-loop | Gun on a locking friction arm with a two-knob fine stage; camera estimates dot vs seam, screen says which knob and how far; fine knobs downstream of the lock | developed | `scenes/use-06-coach-loop` |
| use-01-day-lanes | Lens: ten states of one closure as lanes (hand does, hand holds, eye judges or watches, software, pose owner, laser); six arrangements; handovers; to-scale bar | developed | `scenes/use-01-day-lanes` |
| use-04-the-lap | Lens: dial and trace of one lap; runout slews at hundredths of a mm per second; four correctors; disturbances and correctors on one time axis; carries A11 | developed | `scenes/use-04-the-lap` |
| use-05-gates | State machine with owners; three policies for what may run alone; software may veto, only a hand fires; hold states (A8) | rough | `scenes/use-05-gates` |
| use-07-two-stations | Two rotators, one head translating on a rail; cable trolley vs 350/240 mm; schedule shows only the hands-free window overlaps (A6) | rough | `scenes/use-07-two-stations` |
| use-10-wire-first | Wire-inclusive dry run: the feeder jog puts the tip on the plate; plan and section; direction flips the arriving side (A7) | rough | `scenes/use-10-wire-first` |
| use-11-setup-gauge | Printed gauge tube with a window and target line in the nest; set the gun where the dot can be seen, swap in the real tube (A9) | rough | `scenes/use-11-setup-gauge` |

### Ideas with a file and no scene yet

use-08-flight-recorder (A1: hand-held weld logged as an experiment; observe only), use-09-programmed-table (A2: the table runs index / lap / bead under the deadman; move only), use-12-golden-tube (A10: a reference tube runs the dry cycle each morning). All sketch.

### Connections

Commanded states with geometric positions (swing head) vs a hand-driven manual axis with a scale (coach loop): two answers to per-tube re-aiming. The last adjustment must come after the last thing that shifts. Measure where the gun is not; hand time moves, it does not vanish. Angle as the clock; slow correctors suffice. Software may veto, only a hand fires; faults are states. The fibre's bend radius binds a moving head's cable. Rotation direction is a campaign state.

## Wave 2: the exchange with travel, Derek's examples, borrowed pieces

Partner this wave: **travel** (Split the travel). room works on my ideas (its file `exchange/room--on--use-w2.md` is answered in wave 3). My file on travel: `exchange/use--on--travel-w2.md`. travel's set grew while I worked (idea files 14, 14b, 15, 16, 17, 18, `index.md`); I read the versions in place at about 03:00 and revised against them. I ran `check-scene --shot --exercise` on all thirteen of travel's scenes and drove `travel-01` and `travel-04` by hand at states no shot shows (probing `__app.gun.local('nozzleTip')` while moving `swing`, and Z with the shuttle in `travel-01`).

### A source finding that changes how I write "escape"

The shared context says the head lifts away with the trigger held and the retract cycle breaks the wire in air, cited to `46-the-per-weld-sequence.html`. That guide's text says only "release the trigger, then the pedal" (and the snip of a stuck wire). Neither guide 46, `weld-rotation-rig.md`, `pressure-vessel.md` nor `weld-position.md` contains lift, retract or "in the air" (searched). It is repeated as [repo] in travel-04, room-01, use-01, use-02 and other files. I corrected use-01 (scene text and source tag) and the use-02 idea file, made every scene use of it conditional (a slider whose 0 is the written sequence: use-13, use-15, use-16) and put the question first in the return.

### What I chose in travel's set, and why

Four sections, since travel's own new work had already covered two of my first candidates: travel-18 (a second dry turn in the weld state) is my "learn the map after the last change" concern, so travel-02 and travel-18 became a note (the replay's zero and the guide's order); travel-16 and travel-04 note that with no wire at the gun the lift-away reason is gone, so the crown-escape idea became a pivot with three possible jobs.

1. **travel-01 (deep, stressed):** Z's range (+-6) against the swap margin (in their own scene the shuttle badge is red from Z = +2 mm: 8 of 12 mm safe), the escape (28.1 mm of Z for 20 mm along the beam) and two approaches per closure (tack, verify face TIR, weld). Scene `use-13-work-states`.
2. **travel-05b (sketch, developed):** the clamp closing is the last handover. Scene `use-14-handover-shift` (also the suspension example's release).
3. **travel-14b (sketch, developed):** a crown per closure (the second closure inverts the tube), a hand-run dock, the pivot at its stop. Scene `use-16-yoke-escape`.
4. **travel-06 (developed):** shoe-on order, the pedal-only rotator, station versus hand. Scene `use-17-driven-presetter`.

### Rounds

**use-14-handover-shift.** R1 model: one axis, elements engaged per state, Coulomb dead band around the spring equilibrium, look-and-correct loop stopping at half the window; defaults from travel-05b (soft drive, clamp) and freedom-01 (arm, bungees). The first table had a bug (the trim step's move was zero because the loop mutated the position before the step was pushed); fixed with a `from` argument, found because the RMS bars showed zero for the loop. R2 found by running: friction dead band costs rounds, not accuracy (the loop winds the anchor up until the gun breaks out and lands on the band edge), the opposite of what I had assumed from travel-05b's badge. R3: Derek's release, after the arm lets go, needs zero arm force, and the null of a soft spring has a floor (force noise over stiffness = 0.33 mm at 0.15 N/mm). R4: added a mean shift and a "learned" toggle after the numbers showed learning a bias equals a look (81 versus 82 percent); this is the piece of the AI's job that no other scene shows. Default seed chosen so the opening closure shows a clamp shift pushing the gun out of the window and two relocks (the histogram shows the truth).

**use-13-work-states.** R1: the closure planned as a list of states, each with target shuttle, drop, fine Z and X, spin and laser, simulated in order so a trim is remembered across an out-and-in. R2: the drop tier is only needed if the fine Z is short of the swap margin; measured in travel-01's own scene: badge red from Z = +2 mm (barrel not tip), so I replaced my tip-only figure (safe to +4 mm) with the measured one. R3: the escape check needed a rounding fix (the slider's 0.5 mm step left 19.9 mm delivered of 20 needed; 0.1 mm step and ceiling). R4: the tube length only matters at the approach and the plate depth only after a trim (after a trim the rim sits 5.0 mm minus the plate depth below the tip regardless of the tube's length); the scene keeps them as two separate sliders because the effect differs.

**use-15-examples-as-days.** R1 states from the written sequence with BRING and TRIM added; R2 recognised that a hand at the tube and a hand on the gun are different resources, which made the summary bars; R3 the hand-held row sets a scale: 11.0 of 15.6 minutes are tube states in every row.

**use-16-yoke-escape.** R1 calculation with the kit pose (script `w2_yoke.mjs`): the trunnion axis in attitude B is 185 mm from the nozzle and 202 mm from the dot; 10 degrees gives 26 mm of tip height and 21 mm of standoff. R2 the scene text was rewritten after reading travel-16 and travel-04, which say that with no wire at the gun the lift is unconstrained: the pivot is then the dock's axis and the angle setter; the escape is conditional twice.

**use-17-driven-presetter.** R1 a time budget for four ways of centring; R2 the shoe term added after re-reading guide 46's order (indicate, then tack, verify, then engage the shoe); R3 error bars changed from stacked segments (which added linearly what the number adds in quadrature) to one bar and a text of the three terms. Finding from running: at the defaults the station binds in all four rows, and moving plate seating to the presetter makes the person the binding resource in two.

### Derek's examples, seen as days (part B)

Scene `use-15-examples-as-days` (branch of freedom-01, freedom-02, room-01), plus `use-14` for the suspension's release. See the return's `examplesTreatment`. What the framing saw that the examples' owners did not: parking as a state (the recess must be open for indicating, seating the plate and the swap: free under the table, a swing held by friction on the monitor arm, a lift of the whole hanging assembly in the suspension); the loops need not be opened per tube (freedom-01 assumes they are); the monitor arm keeps today's two big hand actions and takes only the hold; none of the three touches the hand's minutes at the tube; and the release of an arm into soft supports has to be at zero arm force and cannot hold the weld.

### Borrowed (part C)

- **room-13** (dot shift = load change over stiffness) and **travel-18** (a second dry turn in the weld state) -> the "dry state carries the weld loads" toggle in `use-14`.
- **freedom-01** (auto-null of the arm force by moving the bungee anchors) and **freedom-01c** -> arrangement C's null before release in `use-14`.
- **travel-05b** (soft drive, clamp defaults) -> arrangement B in `use-14`.
- **travel-06** (the rotator indexes the nest screws to a driver) -> the driver rows of `use-17`; also its interface problem (pedal-only controller) which I read in `firmware/src_weld_rotator/README.md`.
- **travel-16 / travel-04 / travel-14b** (yoke, seat, dock) -> `use-16`.
- **room-01 / room-15** (the shelf drops the tube; 26 mm at 60 mm/s in room-15's scene) -> the escape numbers in `use-13` and `use-15`.
- **room-12** (one-axis head) -> named in `use-13` as the alternative (the gun escapes, the work swaps).
- **trials-01** (index magnet on the puck) -> a hall pulse for the angle zero; sourced in `sourcing/use.md`.
- **borrowed-05** (guide star: nudge and watch) -> the idea of learning a bias, in `use-14`'s learned-bias toggle.
- **use-11 (mine) with trials-10 and travel-10** -> a gauge session for the person's eye (named, not drawn).

### Own ideas (part D)

No new variant of the crowded families. Two of mine were revised: `use-01` (the lift-away is not in guide 46) and `use-03` (the station verify pass belongs with the shoe on; it applies to my own presetter as much as to travel-06). `use-02`'s plunge keeps its seating and clearance jobs whether or not the sequence has a lift. The idea I would develop next is the flight recorder (`use-08`): its first output is Derek's real durations for `use-01`, `use-15` and `use-17`, and the answers to several unknowns (shoe shift, end-of-bead lift, clamp shift).

### Kit and process notes

- Long `transferable` strings are non-wrapping chips: on a 390 px viewport they pushed the whole page sideways and the checker only said "page scrolls horizontally"; short chips fixed it. Custom stages with `minWidth` set also flagged.
- The file-write hook rewrites `\uXXXX` escapes into characters in files I wrote, so later Python replaces have to use the character, not the escape (a replacement that "did nothing" left `prev` undefined in a scene).
- `app.ui.enable(id, false)` is the way to grey out controls that belong to another arrangement; the checker then skips their "no visible effect" warning.
- `ws.setWorkPose` and a wrapper group under `ws.work` (for a longer tube) worked without reparenting.
- `app.stageOverlay(node, {corner:'br'})` takes a DOM node, which I keep updating.

### Sourcing

`sourcing/use.md`, wave 2 additions: hall-effect sensor module 5-pack (an index pulse; $5.99, 135 ratings, 100+ bought in past month) and a re-check of the AS5600 3-pack (a presetter's hand-turned table angle; $7.99, 70 ratings). Prime confirmed on both product pages; one tab opened and closed; nothing ordered.

## Open threads

1. **Measure the gun**: mass and centre of mass (a kitchen scale), the umbilical's stiffness and pull at the grip base (a fish scale, before and after the wire feed starts and the gas comes on), and the wire's landing point on paper. Unchanged from wave 1; `use-14` and room-13 both need the load change.
2. **The end of a bead.** Does the head lift before you release the trigger, how far and along which direction? The whole escape family (use-02's plunge, use-13, use-15, use-16, room-01's shelf drop, travel-04's lift-off) is conditional on a sentence that guide 46 does not contain.
3. **The shoe.** Read the indicator at the weld circle with the copper shoe disengaged and engaged. Decides whether `use-17`'s shoe term is zero and whether travel-06 and my presetter (`use-03`) must verify shoe-on.
4. **Clamp closing.** What does a cam, clamp or magic-arm knob do to a dot when tightened (indicator on the shell)? Decides the size and the mean of the shift in `use-14`.
5. **Measure ten tubes** (length, plate seat depth, out-of-roundness) and **time the day** (type Derek's real durations into `use-01`, `use-07`, `use-15`, `use-17`).
6. **The recorder first?** `use-08`'s first output would be the durations table and the answers to 3 and 4 above; it still has no scene. It is the next thing I would draw.
7. **Rotator interface.** Go-to-angle-and-hold and an index pulse are firmware and a $6 part; `use-09` (programmed table), `use-17` (driver) and the six map-and-replay ideas all assume them. Whether the console accepts a command while the pedal is held is unknown.
8. **Combinations named and not drawn:** travel-10 + use-11 + trials-10 (a gauge session for the eye); travel-13 with `use-14`'s learned bias (the printer recentres the coarse stage from logged closures); `use-12` on room-12's spare station.
9. **Answer room** (`exchange/room--on--use-w2.md`) in wave 3: the swing versus a long plunge (with the swap volume), whether the coach step is load-matched (now: `use-14`'s toggle), which resource is scarce (now: `use-17` says the station binds at my defaults and the person binds once the plate leaves the station), the plain rest, and the trigger path (room-14).
10. **Unrepaired and visible:** the umbilical's twist under a swing about a vertical axis (`use-02`); the presetter not saving hand time (`use-03`, `use-01`, `use-17`); the camera's view of the dot in the recess (`use-06`, `use-11`); a crown per closure (travel-14b's second closure); the hand-run dock; printed-groove creep at every seat.
11. **Kit notes** are in the section above and in the return.
