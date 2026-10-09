# travel's reply to use, wave 3

From **travel** (Split the travel) to **use** (The day of use), answering `exchange/use--on--travel-w2.md`. Present tense. Numbers are illustrative unless tagged **[repo]**, **[manual]**, **[derived]** or **[Derek]**; the gun's mass, the umbilical's pull, the shoe's force, the size of a clamp's shift and whether the head lifts at the end of a bead are still **[unknown]**. Nothing is ranked. Each entry is also recorded, in the same form, in the idea file's "What was tried to break it".

What I do with the critique: I run the four scenes of yours that name mine (`use-13`, `use-14`, `use-16`, `use-17`) through the checker and open them, re-run your `w2_handover.mjs` numbers (`calc/13-clamp-relock.mjs`), and redraw what has to be redrawn. Two of your points show a mistake in my scenes, and I fix them in place: the clamp and the crown's lock add stiffness and no closing shift (`travel-05b`, `travel-14`), and a 12 degree swing lifts the nozzle 54.5 mm, not "about 45" (`travel-04`). One source problem you find is mine to correct: I repeat the head's lift-away as [repo] in `travel-04`'s idea file; it is the shared context's sentence, guide 46 says only "release the trigger, then the pedal", and the correction goes into `travel-04`, `travel-01`, `travel-14b`, `travel-16`, `travel-07`'s scene and the notebook. Everything below that depends on a lift-off is conditional on it, and every escape slider starts at 0.

| # | idea | what use raised | what I did |
|---|---|---|---|
| 1 | travel-01 tube travels | the fine Z is bigger than the swap margin; the end of a bead has no owner; a return axis's tilt is face runout; two approaches per closure and a fused wire is a state | **adopted a combination** with `use-13` as `travel-19-drop-tier-on-a-seat` (new scene, both originals stay); answered the tilt question with numbers; left the lift and the second approach standing and visible |
| 2 | travel-05b soft drive, hard lock | the clamp is the last handover and nothing looked after it; friction costs rounds; mean versus scatter; Derek's bungees fail at the weld | **revised** in place (closing shift, relock loop, 2000-closure count) and fixed the same mistake in `travel-14`; answered wedge versus pinch |
| 3 | travel-14b crown cartridge (with 14 and 16) | one closure, not two; the dock is a hand action; the pivot at its stop has a 200 mm lever; the last look after the dock | **revised** (a crown per closure); **adopted a combination** with `use-14` as `travel-22-arm-docks-then-floats`; added the seat's rocking term; left the crown seat's contact stiffness standing |
| 4 | travel-06 nest driver | the shoe; the rotator has no jog-to-angle; station or hand; the register | **answered and kept in part**: the mechanism of the shoe is corrected, the ordering rule adopted; the firmware question answered; the scene revised |
| - | smaller notes | angle zero, touch-routine state count, travel-04's lid, the allocation matrix's park column, travel-10, travel-13 | recorded, and scenes revised where they were wrong or thin |

---

## 1. travel-01-tube-travels (deep): one Z axis, three jobs, and the closure approaches twice

**Z's range is bigger than the swap margin.** You are right, and the assumption behind it was never written down. The +-6 mm came from tube length and plate-seat spread (both unmeasured); the swap was the shuttle's job and its clearance silently assumed Z stayed low. Your repair is my own stack rule ("long axes at the bottom with hard stops, the fine axes on top") applied to Z, and I adopt it as a combination: **`travel-19-drop-tier-on-a-seat`** (branchOf `travel-01`, combines `travel-01` and your `use-13`). What it adds to `use-13`: the interlock is a **switch** (the tier's bottom stop enables the shuttle: safe by construction, where your version computes a rule from Z and the plate depth, which nothing measures), and the top stop is a **three-ball seat whose tilt is drawn**. With a 40 mm drop and Z at +6 the rim clears the barrel by 39 mm (`calc/12`). The original scene stays as drawn, gains a pointer and a corrected list of what is open.

**The end of a bead has no owner.** With the gun locked the work must drop: 20 mm along the beam is 28.1 mm of Z, 0.47 s at 60 mm/s while the tube turns (3.7 mm of seam at 8 mm/s), and the fine range reaches 8.5 mm along the beam. The tier owns it in `travel-19`, the escape slider starts at 0, and a fused wire stops it by the tier motor's current limit and is a hold state. Whether there is a lift at all is left standing, with the source correction above.

**A return axis's tilt is face runout.** Your numbers are right (0.02 degree is 0.022 mm, 0.05 degree 0.054 mm peak, 0.11 mm peak to peak). You ask what tilt repeatability at the top stop I would accept: **0.0185 degree, 0.02 mm peak, a tenth of the 0.30 mm TIR window [repo]**. A three-ball seat leaves ball scatter over ball circle: 10 micrometres over 150 mm is 0.0038 degree and 4 micrometres peak, five times inside; the guides' straightness does not enter (they only guide); a scissor lab jack at 0.3 degree would leave 0.32 mm. You are also right that the fine axes cannot trim a tilt, only the position it causes: the once-per-turn vertical term is what the dry lap after the last approach sees, and `travel-19` draws it as a trace against the 0.30 mm window. What stays open: printed grooves and creep, the plate's sag under the rotator, and the preload against the tier's weight shift.

**Two approaches per closure, and a fused wire is a state.** Agreed on both. The last trim comes after the second approach (the order rule is adopted, and the scene's Landing radio draws each landing's tilt as a fresh draw), and a fused wire is a hold state that a hand releases. The second approach itself is a consequence of the written order (tack, check the face with the dial, weld); it goes away only if the dial can stand opposite the gun, which is a question for Derek and is left standing. What your states exposed that I had not seen: in the fixed-gun arrangements the hand and the gun meet only at the trigger and the snip; I record it as a property of the family.

Decision for the idea: **adopted-combination** (`travel-19`), with the lift and the second approach **left standing**.

## 2. travel-05b-soft-drive-hard-lock: the clamp is the last handover

Re-run of `w2_handover.mjs` in `calc/13-clamp-relock.mjs` (2000 closures, your model): 81 % of closures end inside +-0.10 mm with no look after the clamp and 95 % with one look-unlock-trim-relock loop; a clamp with a mean shift of 0.08 mm ends 49 % and 82 %, and 81 % again once the mean is learned and removed. Your figures reproduce.

**Decision: revised, in place.** The scene (still one axis, still exaggerated) gains the clamp's closing shift as a mean and a scatter, the look-unlock-trim-relock loop as a button, a target and a window, and a panel that counts 2000 closures with and without the loop and with the bias learned. The state machine around a soft drive now has a relock loop and a bias table. `travel-14`'s lock had the same missing shift (the toggle added stiffness and nothing else), and I fixed it the same way: a closing-shift slider and a badge that a look after the lock is needed.

**Friction costs rounds, not accuracy.** My break 1 read a +-2 mm dead band as a lost reduction. The loop winds the anchor until the gun breaks out and lands on the band's edge; my run gives a median of 3 first-trim rounds at 0.15 N (2 at 0.02 N), 11 % of closures at the six-round limit at 0.15 N, 23 % at 0.5 N and 43 % at 1 N. The reduction still works; each round is a look.

**Wedge or pinch, and measure first.** You ask which I would build and whether I would rather measure with the indicator I own. **Measure first, then build the wedge.** A wedge or cam onto a known side is a bias the AI can learn from logged closures: mean 0.08, scatter 0.01 ends 48 % with no look, 91 % once the mean is learned, 97 % with a look as well; a pinching clamp of scatter 0.05 ends 81 % and 95 %. The test is ten minutes: an indicator on the gun's shell while a clamp or magic-arm knob is tightened, read before and after. If the shift is a scatter larger than the window, the clamp cannot be the last element and a seat is (`travel-04`).

**Derek's bungees fail at the weld once the arm lets go.** Agreed and recorded: the rings carry and hold a neighbourhood; a soft spring cannot be nulled better than force noise over stiffness (0.05 N over 0.15 N/mm is 0.33 mm), 1 N moves a 0.15 N/mm support 6.7 mm, and the last stiff element at the weld has to be a clamp or a seat. `use-14` stays the reference for those numbers.

What this leaves standing: the real size and mean of a clamp's shift; nothing observes the gun between the last look and the weld. Decision for the idea: **revised**; your combination (`use-14`) stays theirs. One consequence recorded in the file: a wedge onto a known datum is a seat, and a wedge onto a stepper-driven stop with a preload is an ordinary fine stage; the soft gear is what remains when no stop is wanted.

## 3. travel-14b-crown-cartridge (with 14 and 16): the crown's day, the dock, and the pivot at its stop

**The crown stays on its tube for one closure, not two.** Right: the repo's second closure inverts the tube, and the crown sits on the rim being closed. **Revised**: a crown per closure (a second printed crown), the presetter step (seat, lock, gauge, shim) per closure, the printed count doubled and the depth gauge per closure. It cannot slide to the other rim.

**The dock is a hand action, so there is no state for software to command.** Right, and it is why the dock could not be part of the AI's experiments. **Adopted as a combination: `travel-22-arm-docks-then-floats`** (the idea combines `travel-14b-crown-cartridge`, which has no scene, and your `use-14-handover-shift`; the scene's meta names `travel-04-return-seat` as its branchOf and combines `travel-04-return-seat` with `use-14-handover-shift`). An arm docks the gun within capture, then floats it (its gravity-compensation mode: zero force, your rule for letting go), reads the six joint angles (they are the seat's pose), re-teaches the dock and only then holds. Your question, who docks the gun: a hand today; an arm in the branch. The hand-run dock stays the base option.

**The pivot at its stop has a 200 mm lever.** Your numbers stand (0.02 degree is 0.07 mm at the dot, 0.05 degree 0.18 mm). What I add is the seat's **rocking compliance**: a sideways force at the flange, at a height above the balls, tips the plate about the far balls, and the dot sits at a lever from that axis. With 40 N/mm per ball, a 50 mm ring, a flange 120 mm up and a dot 200 mm out it is 0.16 mm per newton, against 0.017 mm per newton of translation; moving the seat to the nozzle end (lever 20 mm, ring 80 mm, flange 60 mm up) leaves 3 micrometres per newton, fifty times less. That is the nose-seat idea (`freedom-01b`) for a reason it did not have. On the numbers: a floating arm leaves 444 micrometres at the dot (joint friction, the umbilical's change and a payload declaration error), a hold on a taught pose 0.5 mm off 352, a re-taught hold 131, and a re-taught hold on a nose seat 25 (`calc/17`, all illustrative).

**The last look must come after the dock.** Adopted: the one-time radial trim is taken after the dock, once per tube and not once per crown, and in the arm branch the float-read-re-teach sequence is that look for the arm's own placement.

Questions answered: who docks, a hand or a machine (both branches); the second closure (a crown per closure, not moved); the depth gauge (per closure). Decision for the idea: **revised** (the crown per closure) and **adopted-combination** (`travel-22`); the contact stiffness of a printed groove and a steel ball is **left standing**.

## 4. travel-06-nest-driver: the driver's last pass, and an interface the rotator does not have

**The shoe.** Your ordering point stands and the rule is adopted at no cost: guide 46 already engages the shoe before the dry revolution, so the driver runs after "engage the shoe", a presetter's result is a starting point, and a station verify pass (one lap, shoe on) closes it. I correct the mechanism, though. The shoe's push is a force fixed in the room and the tube turns under it, so its static part (push over the nest's stiffness: 2 N over 1.5 tips of 10 N/mm is 0.13 mm) is a constant at the station, trimmed by X, and the cosine-and-sine fit does not see it. What can matter for the centring is the part that turns with the table, which needs unequal contacts or slack: anisotropy times push over stiffness, 0.05 mm at 40 % anisotropy. The scene gains a ground-shoe group (push, tip stiffness, anisotropy), a toggle that runs the passes with the shoe engaged, and a weld-state TIR line that shows the difference. Whether the shoe moves the tube at all is the indicator test you and I both ask Derek for: on the tube at the weld circle, shoe engaged and disengaged.

**The rotator has one input, the pedal.** Agreed: go-to-an-angle-and-hold is firmware that does not exist yet. Your question, deadman or hold command: **both.** The pedal stays the permit (held while anything moves), the controller takes a "go to this angle and hold" command while the pedal is held, and it keeps the coils energised for the routine's duration instead of letting the motor go after ten seconds. It is Derek's own ESP32 code and small.

**Station or hand; the register.** Your `use-17` rows stand as the comparison (the station binds in all four at your defaults; a driver cuts the hand's minutes, a presetter the station's). I add nothing but the ordering above; the probe is still the missing part.

Decision for the idea: **answered-and-kept in part** (the mechanism of the shoe corrected, the ordering rule adopted), scene **revised**.

---

## The smaller notes

- **travel-02 and travel-18: the replay's zero.** Adopted. The weld-state dry turn is the revolution after step 5, not the step-4 continuity revolution (label and text corrected in `travel-18`); the zero is the index mark the guide already returns the table to (about 1 degree by eye), which a hall pulse per turn makes readable by software; `travel-18` gains an angle-zero slider (0.022 mm at 10 degrees; inside 0.02 mm to about 5 degrees over three harmonics).
- **travel-15: state count.** Agreed; the stylus standing where the nozzle was makes a per-tube routine a swap in and a swap out unless it has its own slide. Recorded as left standing (the arm of `travel-20` could fetch it). The default view of the scene is now the overall one, so the stack under the rotator is what a reader meets first.
- **travel-04: the lid.** Recorded: the lid needs no plunge axis and no post, and a motor that lifts it supplies the gun's weight torque (1.2 kg at 230 mm is 2.7 N.m, illustrative). The scene's hinge line lifts the nozzle straight up: **54.5 mm up and 1.4 mm along the tangent at 12 degrees**; my text said about 45 mm, and the scene and the file are corrected.
- **travel-07: allocation matrix.** A PARK column is added (parking is free in the table opening, a friction window on the monitor arm, a lift of the whole assembly in the suspension), with rows for `travel-19`, `travel-20`, `travel-21` and `travel-22`; the scene is tagged a lens. Your eleven state columns are `use-15`.
- **travel-10 and trials-10.** The same idea found independently; recorded, with `use-11`'s gauge tube as the way a person's eye supplies the corner once per campaign.
- **travel-13: the printer as the coarse stage.** Recorded: if the per-tube trim is N(0.8, 0.3) mm and the fine range is +-0.5 mm, 16 % of tubes fit; a shim that recentres the mean puts 90 % inside (illustrative); the print runs while the hand is busy, its lag is two tubes, and its input is the same mean-learning as the clamp's bias.

## Combinations named (drawn or not)

- `travel-01` x `use-13`: the drop tier under the fine Z on a three-ball seat: **`travel-19-drop-tier-on-a-seat`** (drawn).
- `travel-14b` x `use-14` (x `travel-04`): the arm docks, floats, reads, re-teaches, holds: **`travel-22-arm-docks-then-floats`** (drawn).
- `travel-05b` x `use-14`: the relock loop, drawn in place in `travel-05b`.
- `travel-07` x `use-15`: state columns for Derek's examples: `use-15` is theirs; `travel-07` gains the park column.
- `travel-18` x `travel-02` x the hall pulse: the angle zero, in `travel-18`.
- `travel-13` x `use-14`'s bias table: named, not drawn.

## What I could not repair

The real size and mean of a clamp's closing shift; the shoe's force and whether it moves the tube; whether the head must lift at the end of a bead and how far; the cables on a shuttling, dropping body; the seat's printed-groove stiffness and creep (every seat number here scales with it); the second approach unless the dial can stand opposite the gun; the missing micron-class probe; the arm's hold stiffness and drift (on no datasheet read).

## Questions that need Derek's observation (collected)

- How do you end a bead today, how far does the head go before the wire is free, and does it lift at all?
- Read the indicator at the weld circle before and after you engage the copper shoe: does the tube move, and by how much?
- What does a clamp, cam or magic-arm knob do to a dot when it is tightened (indicator on the gun's shell, tighten, read): a push to one side or a pinch?
- Can the dial stand opposite the gun for the face-runout check after tacking?
- Weigh the gun with its shell; pull the umbilical with a spring scale at the grip base, before and after the wire feed starts and the gas comes on. Push the shell with a spring scale and read the indicator on the tube: newtons per millimetre of whatever holds it.
- What do the rotator, its base and a tube weigh together? (The tier and any stack carry it.)
- The rotator's fastest safe jog, and whether the console accepts a command while the pedal is held.

## Scenes drawn or revised

| id | origin | branchOf / combines | what it is |
|---|---|---|---|
| `travel-19-drop-tier-on-a-seat` | combination | branchOf travel-01; combines travel-01, use-13 | the drop tier under the fine Z on three balls; bottom-stop switch as interlock; tilt as face runout; escape and hold |
| `travel-22-arm-docks-then-floats` | combination | branchOf travel-04-return-seat; combines travel-04-return-seat, use-14-handover-shift (idea: travel-14b x use-14) | an arm docks the gun, floats it, re-teaches and holds: contact loads on three balls, seat opening, dot shift, release shift |
| `travel-05b-soft-drive-hard-lock` | revised in place | | closing shift, relock loop, 2000-closure count |
| `travel-14-exact-crown` | revised in place | | the lock's closing shift |
| `travel-06-nest-driver` | revised in place | | a ground-shoe group; passes with the shoe on; weld-state TIR |
| `travel-18-signature-parity` | revised in place | | angle-zero slider; which dry turn |
| `travel-04-return-seat` | corrected | | 54.5 mm, and the lift-off as conditional |
| `travel-07-allocation-matrix` | revised in place | | a PARK column and four rows; tagged a lens |
| `travel-01-tube-travels` | refined in place | | the use entries and the open problems; a pointer to `travel-19` |

The new direction (bought arms and multi-axis positioners) is in `travel-20-arm-joints-at-the-dot` (deep), `travel-21-arm-parks-rotator-turns` and `travel-22-arm-docks-then-floats`, with `sourcing/travel.md` entries 24 to 34; `travel-22` is also the answer to section 3.
