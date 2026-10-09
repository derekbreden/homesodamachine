# use-04-the-lap: what changes over one turn, and how fast

Scene: `scenes/use-04-the-lap/index.html`. Origin: swarm. Maturity: developed. A lens plus one arrangement idea (lap 1 is the dry run, lap 2 replays a correction), the framing's "angle as the clock".

## Picture it

A round dial of the seam turns under a fixed red dot at the right. Eight numbered tack marks sit on it in the opposite-side order, a gold bead grows from the first tack around to 380 degrees, and a shaded wedge shows the 20 degrees laid twice. Beside it a flat plot shows the dot-versus-seam offset over the lap, two gentle waves (radial and vertical) that a chosen corrector flattens. Underneath, one time axis puts every disturbance (beam wobble, hand tremor, runout, tack shrink, tube-to-tube offsets, printed-part creep) and every corrector (hand by eye, camera loop, replayed map, follower, micrometer, shim, seat) on the same seconds scale, with the lap period marked in red.

## The proposal

Use the **angle** the rotator already reports as the clock of the weld. The dry lap (red dot on, laser disabled, same cables) records the dot-versus-seam offset against angle; the weld lap replays a correction keyed to the same angle. The correction only has to be slow: the runout the rig already accepts is a once-per-lap change, so whatever corrects it can be weak and slow, and what matters is resolution and backlash. Fast disturbances (a hand's tremor, the head's vibration motor, the beam's 80 Hz wobble) live in a different band and want a different answer: a rest or a seat, not a servo.

The four correctors in the scene (none, a hand by eye, a replayed map on one slow axis, a mechanical follower on the tube) are ways of assigning the slow band; the time axis assigns the others.

## What carries the loads, what establishes position, what is free or restrained

Not a support scene. The corrector lanes say who could own each band. The replayed map needs one slow axis (radial at least; vertical for the face runout) carried by whichever support the gun has; a mechanical follower is a roller on the tube's OD or rim carried by the gun's support (another explorer has a scene named `datum-04-corner-follower`, not read).

## What software could command, observe, and what stays manual

- **Command:** the existing rotator; one slow correction axis in the replay mode.
- **Observe:** degrees turned so far [repo]; dot versus seam from a camera or indicator during the dry lap. The scene models the replay as perfect except for the resolution you set, and lets you set a "change since the dry lap" that a real replay would inherit unseen.
- **Manual:** holding the gun (hand mode), the trigger, marking the first tack.

## What was tried to break it

1. **"A follower must be fast."** *Conflict:* none, numerically. `calc/lap_rates.mjs`: at 5 to 15 mm/s the peak slew of a once-per-lap 0.25 mm radial runout is 0.010 to 0.030 mm/s and of a 0.30 mm face runout 0.012 to 0.036 mm/s; updating about every 0.5 to 1.5 s holds 0.02 mm. *Assumption:* runout is a pure once-per-lap cosine. *Change:* a hand-turned micrometer or a hobby servo behind a reduction is fast enough; resolution and backlash are the real specification. *Leaves:* real runout also has an out-of-round part at twice the lap frequency, and tack shrink, neither modelled.
2. **Feed-forward fails if the weld lap differs from the dry lap.** *Conflict:* the weld adds heat, wire feed conduit push and argon hose push; the tube may move [assumed]. *Assumption:* the dry lap is representative. *Change:* the "change since the dry lap" slider shows the error you would only find after the weld; the repo's disabled-laser rehearsal already asks for the same cables and hoses present [repo gate 9]. *Leaves:* how large the change is: unknown.
3. **Vertical (face) runout needs its own axis.** *Conflict:* correcting radial only leaves the face runout untouched. *Change:* a toggle for radial only vs radial plus vertical; the plate face TIR only exists after the plate is tacked. *Leaves:* the vertical axis doubles the mechanism.
4. **A hand cannot do both bands.** *Conflict:* a hand can plausibly follow a slow drift but not remove a tremor. *Change:* hand mode shows the tremor as a band because it changes many times per degree; the tracking percentage and tremor amplitude are sliders, both illustrative. *Leaves:* real hand tracking is unmeasured.
5. **Gun-side lever.** A pivot at the grip base 279 mm from the dot [derived] turns one arcminute into 0.081 mm at the dot and one degree into 4.9 mm: any slow axis should be at the dot end, not at the grip.

## Branches and combinations

- Lap replay is the software half of a seam-signature idea; other explorers have scenes named `datum-02-seam-signature` and `trials-04-seam-map-replay`, known to me only by directory name (not read). This scene only names the clock and the rates.
- Combines with `use-02-swing-head` (the seat removes the per-tube part; the replay handles the per-lap part) and with `use-06-coach-loop` (the coach sets the per-campaign pose).

## Unresolved problems and questions for Derek

- Real runout shape and size on this rotator with a real tube; only the acceptance limits are known [repo].
- How many dry laps are acceptable per weld.
- Whether the beam's 2 mm wobble [repo recipe] makes a 0.1 mm dot error irrelevant to the melt; nobody has measured it, so the window is a slider.

## Assumptions

- **[repo]** circumference 388.61 mm; 5 to 15 mm/s; 20 degrees of overlap; eight tacks in the opposite-side order; radial 0.25 mm and face 0.30 mm TIR limits; 80 Hz x 2 mm wobble in the recorded recipe.
- **[manual]** the head's vibration motor (p.20), frequency unknown.
- **[derived]** rates and lever arm as above.
- Illustrative: every band on the time axis except the lap period and the recipe's wobble, the tremor, tracking and follower values, the exaggeration, the offset window.

## Sourcing pointers

Slow axis parts are in `sourcing/use.md` (NEMA 17 with T8 screw, 27:1 gearbox, AS5600 encoder for a knob).

Scene id: `use-04-the-lap`. Numbers: `explorers/use/calc/lap_rates.mjs`.
