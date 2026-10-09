# travel-10-software-moves-person-sees: software moves, a person is the eye

**Picture it.** Stepper axes with home switches under the rotator or on the gun, driven by software, with no measurement of the dot at all. Derek looks at the corner through a loupe or a camera image and types "0.2 in and 0.1 up". The AI moves the axes by exactly that, remembers every position it went to, and writes down what was said. The next tube starts from the last tube's commands.

Scene: none of its own; the `Software can see the dot = off` branch of `scenes/travel-02-cascade` shows what stale commands leave, and the stack of `scenes/travel-01-tube-travels` is the hardware.

## The proposal

Software moves and observes nothing. Motion is cheap to add (a stepper, a driver, an ESP32 that Derek already uses for the rotator), observation is the hard part (`eyes`, `datum`). Splitting them lets the motion half be built and used now: a chat loop with a person as the sensor turns each dry run into logged data. It also answers, by experiment, the question every arrangement depends on: how much does tube-to-tube variation actually move the required trim?

## What carries the loads, what establishes position, what is free or restrained

As travel-01. Position is set by the stepper counts and a home switch per axis; the person's eye judges the result.

## What software could command, observe, what stays manual

- **Commands:** each axis to an absolute position or a relative move; stored per-lot offsets; rotator speed.
- **Observes:** nothing about the dot; step counts only (open loop).
- **Manual / person:** looking at the dot against the seam and saying how far off it is and in which direction; tube swaps.

## What was tried to break it

**1. Stale commands.** *Conflict:* applying the last tube's trim to the next tube leaves the tube-to-tube variation (the scene, observation off, New tube). *Assumption:* tubes in a lot vary. *Change:* a person's look after each tube; the AI applies the last reported offset as a starting point. *Leaves:* how large the variation is: unknown.

**2. The eye.** *Conflict:* can a person judge 0.1 mm at a recessed corner? *Change:* a magnified image with a reticle (a camera on a post, or a USB microscope; `eyes` framing). *Leaves:* the sightline (the wall blocks a low camera, see the reference scene).

**3. The loop time.** *Conflict:* a conversation round trip per correction. *Change:* corrections are in whole steps, several at once ("0.2 in, 0.1 up, then check"). *Leaves:* attention.

**Wave 3 entry, from use's exchange ("Also noticed").** **The same idea as trials-10 (human-labelled jog), found independently (use).** The eye is needed in one state (trim), not in the dry lap or the weld, and the real recess denies it a view. `use-11-setup-gauge` gives a person's eye the corner once per campaign (a gauge tube with a wall window); each tube then brings its correction by cartridge (`use-03`), so "narrate a dozen tubes" becomes one gauge session plus corrections. Not drawn: `use-11` already draws the gauge. *Assumption behind it:* the person sees the dot every tube. *What it leaves uncertain:* the size of tube-to-tube variation.

## Branches and combinations

- **With travel-09:** together they are a manual system with both channels instrumented; each half can be built alone.
- **With travel-02:** turns the observe-off branch into a method.

## Unresolved problems and questions for Derek

- How large is the variation (measure the recess depth on a handful of tubes with the indicator)?
- Would he narrate corrections for a dozen tubes to give the AI a dataset?

## Assumptions

- The ESP32 controller pattern is the rotator's: **[repo]** `firmware/src_weld_rotator/README.md`. Everything about person accuracy: **illustrative**.

## Sourcing pointers

`sourcing/travel.md`: linear stages with steppers (3, 4), rails (5).

## Scene id

None (uses branches of travel-01 and travel-02).
