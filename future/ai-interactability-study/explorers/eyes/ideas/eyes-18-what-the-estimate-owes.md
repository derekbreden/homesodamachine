# eyes-18 What the estimate owes the hand: seven ways of telling or holding it

Scene: `scenes/eyes-18-what-the-estimate-owes/` (custom 2D; a **lens**, not an arrangement). Origin: wave 3 new direction, a combination of `freedom-14-hand-plus-guidance` and `borrowed-19-haptic-jog` with `eyes-01-gun-borne-eye`; the arrangement it is a lens on is `eyes-17-lit-bar-brake-wall`. Maturity: developed (arithmetic on statics and delays; no hand model; every number illustrative). Numbers: `calc/feedback-budget.mjs`.

## Picture it

A table with seven rows (the hand alone, a light bar, a tone, a buzz at the grip, a spring pull, a brake wall, a touch stylus) and five columns of what each needs from the estimate and what a fault does to it, above a strip picture of where the gun ends up when the estimate reads high, and below a curve of how many pushes through a wall it takes to learn the bias. A radio picks the fault (biased, late, frozen, blind, noisy); sliders change the numbers.

## The proposal

Once a gun-borne eye reports how far the dot is from the corner, there are many ways to use that number on a hand that is supplying the motion: light it, sound it, buzz it, pull with it, hold with it, or skip it and use a switch. They look like one decision ("give the operator feedback") but each asks a different thing of the estimate, and each answers a wrong estimate in a different way. The page lays them side by side, for the same estimate and the same fault.

What each needs from the estimate (the sensor requirement, per channel):

- **Bar, tone, buzz (cues):** the signed error, or only its side and a threshold (buzz); a validity and age flag; a separate blind display (never silence, never the last value). A reading every 33 ms is more than a hand can use (it corrects at a few hertz); the delay that matters is the operator's own (200 ms to a light, 150 ms to a tone or a buzz), which puts a cue at 200 to 250 ms from the event.
- **Spring pull:** a fresh, signed error fast enough to servo an anchor (tens of milliseconds) and the anchor's position; a stale reading is a force at the wrong place.
- **Brake wall:** the sign of the error, whether it is outside the band, whether it is fresh, and the slide's direction of motion from its own scale; a decision in one frame and a clamp 30 ms later (78 ms from the event).
- **Touch stylus:** nothing. A contact is a switch, and which contact opened is a direction.

## What carries the loads, what establishes position, what is free or restrained

Nothing here carries the gun: it is a lens. The arrangement is eyes-17's (a friction arm, a two-slide stage, an LED bar and a brake on each slide); the spring channel is freedom-14's (a bungee between the gun and a motor-moved anchor); the stylus is freedom-12's. The reference for "where the gun ends up" is the true seam.

## What software could command, what it could observe, what stays manual

- **Command:** an LED pattern, a tone, a buzz pattern; a spring anchor's position (force = k × error); a brake clamp; nothing for the stylus.
- **Observe:** the estimate with its valid / stale / blind state and age; the slide scales (position, speed); slips; the stylus contacts.
- **Manual:** the hand's judgement and its push; which channel to trust when they disagree.

## What was tried to break it

1. **"A cue can be trusted because the operator watches the dot too."** Conflict: a biased cue at trust τ moves the hand by τ × bias (0.21 mm for a 0.3 mm bias at τ 0.7), and the hand notices only if that is bigger than its own resolution of the dot against the corner (0.1 mm, illustrative): below that the cue and the eye agree and both are wrong. Assumption: that an independent operator is an independent check. What the change alters: the strip shows where the hand settles per channel; the log panel shows what it would take to learn the bias from the hand. What it leaves uncertain: the trust parameter, the hand's resolution, and whether the operator's eye has the same bias as the camera (both look at a spot on a surface, eyes-13).
2. **"A gentle assist is a safe assist."** Conflict: a spring pull of 0.15 N/mm on a 0.3 mm bias, band 0.1 mm, is 30 mN and moves a relaxed hand (0.5 N/mm) 0.05 mm: too small to feel on a held gun and too small to veto. A gentle wrong push is an invisible one. The brake goes the other way: it does nothing until it refuses, and a refusal is unmistakable (2 N to get through). Assumption: that a small force is a safe one. What the change alters: the table's "does the hand notice" cell; the property "does a wrong estimate reveal itself" is a design axis distinct from accuracy. What it leaves uncertain: what a hand notices on a held gun (0.3 N here, unmeasured).
3. **"The last value is the safest fallback."** Conflict: frozen, a bar looks live and green, a spring keeps pulling with its last force, and a brake becomes a one-way valve. Every channel wants a distinct blind state and an age limit, and the physical ones want to fail toward free. What it leaves uncertain: the age limit.
4. **Latency is millimetres.** Conflict: a wall that closes after the gun has crossed the band is a wall in the wrong place: at 3 mm/s the brake crosses 0.24 mm before it holds, the spring 0.33 mm, a light 0.75 mm (most of it the operator). What the change alters: the band is sized against speed × delay, or the wall is engaged early. What it leaves uncertain: hand speed, clamp latency.
5. **Noise turns a wall into a chatter.** Conflict: at the band's edge with 0.03 mm noise a brake toggles up to 15 times a second on 30 Hz frames without hysteresis, 4.8 at one sigma of hysteresis, 0.7 at two; a bar flickers ±0.6 LED. What the change alters: hysteresis of two sigma or smoothing that costs delay. What it leaves uncertain: stiction of a real clamp (stick-slip on release).
6. **The override is data.** A channel that resists lets the hand disagree, and the disagreement is a measurement: with the hand seeing to 0.1 mm the mean of n pushes through the wall is the estimate's bias to 0.1/√n mm (0.03 mm at 10), and about 4 pushes show a 0.1 mm bias at 95 % if the hand's own eye is unbiased. It cannot tell the eye's bias from the hand's; that needs a third look (a touch, or the sectioned tube). It exists only for channels that resist: a cue that is simply followed leaves nothing to log.

## Branches and combinations

- `eyes-17-lit-bar-brake-wall`: the arrangement behind two of the rows; `eyes-19-touch-cue`: the stylus row as a hand-held cue.
- `freedom-14-hand-plus-guidance` (the spring row, its wall / centring / damper helps and its four entries, especially "the eye's bias becomes a push"); `borrowed-19-haptic-jog` (the same helps as feel on a knob): a knob is a seventh place to put a channel and the gun is never touched.
- `use-06-coach-loop` (the screen advice is a cue with a rounding step); `use-05-gates` (a force cap is a gate that is physical); `room-14-trigger-path` (the trigger path: a hand fires, software can only stop, the same "can only refuse" property as the brake).

## Unresolved problems, questions for Derek

Every number is illustrative: hand resolution, the force a held gun lets a hand notice, the human delays, the clamp latency, the hand's speed. A phone video of the dot against the corner during a real hand-held bead would give the hand's speed, tremor and how it steers. Not modelled: a hand that pushes harder when it feels resistance, tone and buzz perception, eyewear. **Questions for Derek:** does your hand slow down or stop when the gun resists? Which would you rather have wrong: a light you can look away from, or a wall you can feel?

## Assumptions

Frame rate 30 Hz, processing 15 ms, light bar 1 ms, clamp engage 30 ms, spring servo 60 ms, human delay 200 ms (visual), 150 ms (buzz or tone): illustrative. Hand: resolution 0.1 mm, stiffness 0.5 N/mm at the grip (freedom-14's illustrative figure), speed 3 mm/s, trust 0.7, detectable force 0.3 N: **[unknown]**. LED step 0.05 mm (eyes-17), tone step 0.1 mm, buzz threshold 0.15 mm, runout rate 0.02 mm/s **[derived]** (calc/runout-rates.mjs). The spring channel is freedom-14's (0.15 N/mm, cap 2 N).

## Sourcing pointers

As eyes-17: `sourcing/eyes.md` wave 3 (LED sticks, a solenoid, coin vibration motors and a haptic driver, a rail). A 100 fps global-shutter USB camera is $49.99 on Prime (wave 1).

## Scene

`eyes-18-what-the-estimate-owes`. Branch: the fault. Actuator (software command): the band. Scene edits: bias, frozen age, noise, eye frame rate, processing delay, clamp latency, spring stiffness, brake capacity, trust, hand speed, hand resolution, pushes so far.
