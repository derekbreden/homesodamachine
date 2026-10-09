# travel-02-cascade: hand, then motor, then follow

**Picture it.** Three stages in series, each sized by what the one above leaves. The hand puts the gun (or the work) within a couple of millimetres. A motor stage trims the offset for this tube, once, from what a camera or probe saw in a dry revolution. A tiny follow stage then replays that revolution's runout as the tube turns: a quarter of a millimetre of motion, a few microns per step, about six steps a second at the fastest bead speed. On the plot, the error at the dot drops from millimetres to a few hundredths as each stage is switched on.

Scene: `scenes/travel-02-cascade` (small multiples: one row per stage). Calculations: `calc/04-cascade.mjs`, `calc/06-holder-and-flexure-stiffness.mjs`.

## The proposal

Precision engineers call this a macro-micro (coarse-fine) split. For this problem it comes with three facts that make it cheap. **[derived / repo]**

- Runout is slow. 0.25 mm radial TIR and 0.30 mm face TIR are the rig doc's acceptance limits **[repo]**; as sinusoids of amplitude 0.125 and 0.15 mm the fastest they change is 30 and 36 microns per second at 15 mm/s (10 and 12 at 5 mm/s). A follow stage needs range about +-0.5 mm, steps of a few microns and almost no bandwidth (`calc/04`, `calc/06` D).
- The error is repeatable per tube. The rotator turns the same tube through the same phases every revolution, so a table indexed by rotation angle from a dry-run measurement replaces a live loop.
- Each stage's job is set by the previous one, so range and resolution shrink together: hand (room, about 1 mm) -> motor (+-5 mm, 0.02 mm) -> follow (+-0.5 mm, 0.005 mm).

The idea says nothing about which body carries each stage: see the break on allocation.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** not decided. In the scene nothing is drawn as carrying anything; the argument below says where each stage should sit.
- **Establishes position:** the hand sets the neighbourhood; the dot against the seam (as seen) sets the trim and the follow table.
- **Free / restrained / driven:** the hand stage is free in setup and locked in the weld; the motor stage is driven once per tube and then holds; the follow stage is driven continuously through the weld.

## What software could command, observe, what stays manual

- **Commands:** one motor trim (radial, vertical) per tube; a follow table (harmonics of the revolution) replayed by rotation angle; rotator speed.
- **Observes:** 36 noisy samples of the dot against the seam per dry revolution (the scene's noise is made up); rotation angle from the rotator's step count (0.025 degree per pulse **[repo]**). The follow stage position is counted, not read.
- **Manual / unresolved:** the hand-set neighbourhood; the tube swap; any drift during the weld (nothing observes it); whether the dry-run runout repeats during the weld; what sensor measures dot-to-seam at micron scale through glare and fume (`eyes` and `datum` framings).

## What was tried to break it

Round 1 is the scene at defaults: hand error 1.7 / -0.9 mm, runout at the acceptance limits, 0.02 mm motor step, 0.005 mm follow step. Peak error at the dot: 1.86 / 1.06 mm after the hand, 0.14 / 0.16 mm after the motor trim, 0.04 / 0.013 mm after the follow stage (`calc/04`, illustrative).

**1. Latency.** *Conflict:* a live loop that reacts two seconds late leaves a quarter of the runout amplitude at 8 mm/s (0.12 mm peak-to-peak radial versus 0.08 mm without lag). *Assumption:* the follow reacts to a measurement rather than replaying a table. *Change:* the table is learned in the dry run and replayed by angle, so latency is a fixed phase advance the software can remove. *Leaves:* if the runout differs during the weld, a table is wrong and only a live measurement could see it.

**2. Steps.** *Conflict:* a 0.02 mm follow step leaves about 0.10 mm peak-to-peak radial (staircase in the scene). *Change:* micron-class steps: a stepper on a micrometer head (0.5 mm per turn) or a spring-steel-leaf flexure driven through a reduction (`travel-05-lever-map`). *Leaves:* backlash and stick-slip of whatever is used, which the scene does not model.

**3. Range.** *Conflict:* a follow range of +-0.10 mm clips a 0.25 mm TIR runout (red marks in the scene). *Change:* raise the range or remove the radial part at its source with the nest screws (`travel-06-nest-driver`). Face runout cannot be removed by the nest screws (it is the plate's tilt and the bearing's wobble), so a vertical follow remains.

**4. The wrong side.** *Conflict:* if the follow stage carries the gun, the umbilical pulls on it. A printed parallelogram flexure (PETG-like leaves, illustrative) gives 0.26 to 2 mm per newton; spring-steel leaves of the same footprint 3 to 27 microns per newton (`calc/06` C); the pull itself is **[unknown]**. *Assumption:* the force is around a newton. *Change:* put the follow stage under the work, where the load is dead weight and there is no cable, and where mass is irrelevant at 30 microns per second; put nothing soft on the gun side. *Leaves:* the follow stage then moves the rotator (about 2-5 kg, **[unknown]**) on a small cross slide; its tilt matters through the 232 mm Abbe height, but only over the +-0.5 mm actually used.

**5. Nothing observes.** *Conflict:* switch observation off in the scene: the stages can only apply the last tube's commands, and the residual is the tube-to-tube variation (press New tube). *Change:* none is possible without an observation; the two sensor-free variants (a person as the eye, `travel-10`; hand cranks with scales, `travel-09`) keep the same ladder with a different eye.

**Wave 3 entry, from use's exchange ("Also noticed").** **A follow table keyed by angle needs an angle zero that survives (use).** *Conflict:* the controller lets the motor go ten seconds after the pedal is released and its degrees are a readout, so the table's zero is not defined by the rotator. *Assumption behind it:* the rotator knows its angle. *What the change alters:* the zero is the index mark the guide already returns the table to (by eye, about 1 degree, 1 mm of arc); a once-per-revolution hall pulse (a five-pack is $5.99 on Prime, `sourcing/use.md`) makes it readable by software. The tolerance is generous: a phase error phi on a 0.125 mm first harmonic leaves 2 x 0.125 x sin(phi/2), 0.022 mm at 10 degrees; counting the first three harmonics (0.125, 0.03, 0.01 mm) the table stays inside 0.02 mm to about 5 degrees and inside 0.05 mm to about 13 degrees (use's `calc/w2_angle_key.mjs`). `travel-18` has the slider. *What it leaves uncertain:* nothing reads the angle in software today.

## Branches and combinations

- **Combination with `travel-01`:** the tube-travels stack is the medium stage; the follow stage is a small Z (and X) cross slide on top of it, or the rotator base itself on flexures.
- **With `travel-06` (nest driver):** the nest screws are the innermost *static* stage for radial runout; the follow stage then handles only face runout and the tube's ovality is what remains.
- **With `travel-04`:** the seat makes the hand stage repeatable, so the medium stage's job shrinks between tubes.
- **Feed-forward on the head itself:** `travel-12-heads-own-stage` if the galvo can be offset (unknown).

## Unresolved problems and questions for Derek

- Whether the dry-run runout repeats in the weld (a dry run and a real weld with the indicator: are TIR readings the same before and after?).
- What Derek measures today after "seat and indicate the tube": radial and face TIR at the weld circle, and where the indicator reads (OD, ID, plate edge).
- Which sensor could give dot-to-seam at micron scale; nothing found on Prime (`sourcing/travel.md`, entry 12).

## Assumptions

- Runout limits 0.25 / 0.30 mm TIR: **[repo]** acceptance numbers. Everything else in the scene (hand error, ovality 0.03 mm, bearing wobble 0.01 mm, drift 0.05 mm/min, steps, ranges, noise, latency, phases): **illustrative**.
- Face runout treated as vertical error at the station and radial runout as seam eccentricity, first order: **[derived]**.
- Flexure stiffness formulas are handbook beam formulas; material moduli and strain limits illustrative.

## Sourcing pointers

`sourcing/travel.md`: MGN12 rails (5), micrometer head (16), planetary gearbox (14), digital indicator (12), shim stock (17). No Prime micron-class probe found.

## Scene id

`travel-02-cascade`

## Wave 2

`travel-18-signature-parity` adds what this file left implicit: the replay's constant is only valid if the gun is in the same place in the weld turn as in the dry turn (change of force times compliance, 6 to 128 micron per newton); a second dry turn in the weld state measures it, and the fitted terms are assigned to the cheapest stage (constants to a static trim, radial 1x to the nest screws, vertical 1x to a Z follow).
