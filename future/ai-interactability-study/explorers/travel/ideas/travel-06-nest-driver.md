# travel-06-nest-driver: the rotator indexes its own screws to a powered driver

**Picture it.** Looking down on the existing rotator: three small hex heads sit round the collar of the tube nest and turn with the table. Beside the table stands a small stepper with a hex bit, and on the other side a probe reads the tube wall. Software turns the table until a screw is at the driver, the driver gives it a fraction of a turn, the table moves to the next screw, and after three moves the probe trace, a sinusoid whose size is the runout, has shrunk toward zero.

Scene: `scenes/travel-06-nest-driver` (top view; eccentricity is drawn exaggerated). Calculations: `calc/04-cascade.mjs` (runout signal), the three-jaw rule below.

## The proposal

The tube nest already has a fine radial stage that nobody counts: three radial M3 adjusters bearing on the tube OD inside 0.20 mm (ID pilot) and 0.40 mm (outer guide) of nominal radial clearance **[repo]** (`hardware/printed-parts/fixtures/weld-rotator/README.md`). They turn with the table, so today a person jogs each to an open side and turns it. The rotator can present each to a stationary driver: the table is the indexer, and it already has 0.025 degree resolution and a serial console **[repo]**.

Three-jaw rule (equal contacts, **[derived]**): to move the tube centre by delta, screw k advances by delta dot u_k (u_k its inward unit direction); with three equal contacts the tube moves about 2/3 of one screw's advance, so a quarter turn of an M3 (0.125 mm of screw) moves the tube about 0.08 mm and 1/16 of a turn about 0.005 mm.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the existing ball race, turntable and nest. The driver and probe stand on the bench and carry nothing.
- **Establishes position:** the tube wall as read by the probe against the rotator's own axis.
- **Free / restrained / driven:** the tube is restrained by three screw tips and free within 0.20 mm; driven only when a screw is at the driver.

## What software could command, observe, what stays manual

- **Commands:** rotator jog to an angle and one revolution for measuring (existing controller); driver engage and turn in 1/N turn steps.
- **Observes:** the probe reading against rotation angle (amplitude and phase = the eccentricity vector); the table angle. The screw advance is counted only; whether the tube moved is seen by measuring again.
- **Manual / unresolved:** loading the tube and bringing the tips to contact; installing probe and driver; which surface the probe reads; the sensor itself.

## What was tried to break it

Round 1 (scene default): 0.18 mm eccentricity (TIR 0.36 mm), slip 0.7, 1/16 turn, three passes: TIR 0.360 -> 0.111 -> 0.024 -> 0.024 mm in 260 s of dry-run time at 15 mm/s (illustrative model).

**1. Over-determination.** *Conflict:* three contacts on a rigid tube cannot all be adjusted independently; a net advance jams it. *Change:* the plan has zero net advance (the three a_k sum to zero) and the tube's compliance (thin wall, springy shoe) distributes it. *Leaves:* whether the real contact stiffnesses are equal is **[unknown]**.

**2. Slip and compliance.** *Conflict:* a 0.065 in wall and printed screws will not deliver every micron. *Assumption:* slip 0.7 is made up. *Change:* the loop measures again; convergence still takes about two passes. *Leaves:* stick-slip of printed threads; backing a screw out lets the tube move by an unknown amount.

**3. Range.** *Conflict:* the stage cannot move the tube past the 0.20 mm ID-pilot clearance **[repo]**; an initial eccentricity of 0.3 mm clips. *Change:* none; a larger error is a hand job. *Leaves:* the residual may be a second harmonic (ovality), which three screws cannot remove.

**3b. What it cannot touch.** The rotator's own bearing wobble and the plate-face runout live below the nest; this stage neither sees nor reaches them. So it reduces the radial part of the runout at its source (0.25 mm limit) but not the face part (0.30 mm).

**4. Engagement.** *Conflict:* a hex bit must find a 2.5 mm hex socket on a rotating printed part at 0.025 degree index accuracy. *Change:* jog the table slowly to a mechanical detent; a flexible or spring-loaded bit; a cone-shaped guide. *Leaves:* unproven.

**Wave 3 entries, from use's exchange (`exchange/use--on--travel-w2.md` section 4), answered in `exchange/travel--reply-to-use-w3.md`.**

**5. The driver's last pass belongs with the shoe on (use).** *Conflict:* guide 46 indicates the tube first and only then engages the copper shoe, which wipes the tube on one side; a shoe-off centring is not the weld state's, and the shoe's push over the nest's stiffness (2 N over 10 N/mm at each tip, 1.5 tips: 0.13 mm) is the size of the routine's whole result. *Assumption behind it:* that the push moves the tube in a way the passes would have caught. *Answer (kept in part, corrected):* the push is a force fixed in the room and the tube turns under it, so its static part is a constant at the station, trimmed by X, and the cosine-and-sine fit does not see it. What can matter is the part that turns with the table: unequal contacts (or slack) make the nest's response depend on the direction of the push, a once-per-turn term of anisotropy times push over stiffness, 0.05 mm at the defaults (40 % anisotropy). The ordering rule costs nothing, since the guide already engages the shoe before the dry revolution, so I adopt it: run the driver after "engage the shoe", treat a presetter's result as a starting point, and finish with a station verify pass, shoe on. The scene's toggle runs the passes with the shoe on and its weld-state line shows the difference. *What it leaves uncertain:* whether the shoe moves the tube at all: an indicator on the tube with the shoe engaged and disengaged says in a minute.

**6. The rotator has one input, the pedal (use).** *Conflict:* held, the table turns at the stored speed; released, it stops and after ten seconds the motor lets go; the degrees are a readout. A driver that presents a screw to a bit needs go-to-an-angle-and-hold, which does not exist. *Assumption behind it:* jog to an angle is available. *What the change alters, and the answer to use's question (deadman or a hold command?):* both. The pedal stays the permit (held while anything moves); the controller takes a "go to this angle and hold" command while the pedal is held, and keeps the coils energised for the routine's duration (a flag) instead of releasing after ten seconds. It is firmware, Derek's own ESP32 code, and small. *What it leaves uncertain:* a jog speed above the weld range is not documented.

**7. Station or hand (use, `use-17-driven-presetter`).** *Conflict:* the routine occupies the station for its passes (260 s in the scene), and use-03 found that a presetter frees the station and not the hand; at use's defaults a driver on the station cuts the hand from 12.0 to 7.5 minutes and leaves the station at 13.7. *Assumption behind it:* the routine's place in the day is wherever indicating is today. *What the change alters:* nothing here except the ordering above; `use-17`'s four rows stand as the comparison. *What it leaves uncertain:* the missing part is still the probe: no Prime-listed indicator with a documented data output was found.

## Branches and combinations

- **With `travel-02`:** the nest screws are the innermost static stage (radial), the follow stage handles what remains.
- **A second use of the same indexing:** the driver could also turn the ground-shoe adjustment or any other screw on the turntable; the rotator as an indexer is the transferable mechanism.
- **The AI's per-tube routine:** the log in the scene is the routine.

## Unresolved problems and questions for Derek

- What TIR values does he actually get today after hand indicating (radial and face), and how many minutes does it take?
- Which surface does he indicate: tube OD, ID, or the plate at the weld circle? The plate's 0.005 in radial slip **[repo]** means OD-centring leaves up to about 0.13 mm of seam eccentricity unless the plate is indicated.
- Probe: a micron-class software-readable sensor is the gap (nothing found on Prime).
- **Wave 3, questions for Derek (from use's exchange):** read the indicator on the tube at the weld circle before and after you engage the copper shoe: does the tube move, and by how much? What is the rotator's fastest safe jog, and does the console accept a command while the pedal is held?

## Assumptions

- Screws at 90, 210 and 330 degrees, equal contact stiffness (2/3 rule), slip, noise, turn resolution: **illustrative**. M3 pitch 0.5 mm, 0.20 / 0.40 mm clearances, 0.025 degree per pulse, 5-15 mm/s window, 0.25 mm TIR: **[repo]**.

## Sourcing pointers

`sourcing/travel.md`: digital indicator (12), micrometer head (16); no stepper-with-hex-bit or probe entry (unresolved).

## Scene id

`travel-06-nest-driver` (wave 3: a ground-shoe group; the passes can run with the shoe on; the weld-state TIR is shown)

## Wave 2

In `travel-18-signature-parity` the nest screws take the radial 1x of a fitted signature (90 percent assumed), leaving the 2x and the vertical terms; against a +-0.30 mm window a static trim is nearly the whole job. The touch signature of `travel-15-touch-stack` supplies the once-per-turn trace the advisor turns into screw advice.
