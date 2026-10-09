# eyes-17 Lit bar and brake wall: the hand supplies the motion, the eye tells it and holds it

Scene: `scenes/eyes-17-lit-bar-brake-wall/` (3D; developed deep). Origin: wave 3 new direction ("the hand supplies the motion and software supplies feedback or resistance"), a combination of `use-06-coach-loop` and `eyes-01-gun-borne-eye`; freedom-14 (a force through a soft anchor) and borrowed-19 (a knob whose torque is a program) are its neighbours. Lens on it: `eyes-18-what-the-estimate-owes`. Maturity: deep (a scene with the layer's rules and its faults; nothing measured).

## Picture it

The coach loop's friction arm, locked once per closure, carries a small two-slide stage; the gun rides on it and **the hand pushes the gun** along a radial and a vertical slide, instead of turning two knobs. On the shell, behind the camera, two eight-LED sticks show the eye's radial and vertical error: the lit LED moves away from the middle as the error grows, green inside a band, amber outside. On each slide a small clamp (a solenoid pulling a printed pad onto the rail) can refuse a move: free inside a band around the estimated seam, and outside it only moves toward the seam are free. The gun is never moved by anything but the hand.

## The proposal

Give a hand-held gun a feedback layer whose sensor is the gun-borne eye of eyes-01 (the seam against the dot, in the gun's own frame) and whose two outputs are **a cue** (a bar on the shell, where the operator's eyes already are) and **a wall** (a brake, passive: it can only refuse). Three things are new against the neighbouring arrangements:

- **The estimate the layer needs is the seam in the gun frame, not the gun in the world.** An encoded arm (borrowed-03) can tell where the gun is only to about 15 mm with a cheap magnetic encoder (its own number: an AS5600's 1° integral nonlinearity at 0.3 to 0.7 m of arm), and a pose logger from six draw-wires or tags (0.06 to 0.09 mm and 0.14 to 0.21 mm at the dot) is not fine enough for a 0.1 mm band. The eye at the dot reads r and z directly to hundredths. What the arm's or the slides' encoders supply is only the *direction of motion* (a differential quantity, far better than the absolute one) which decides which way is "away".
- **A passive wall is a different kind of thing from a pull.** A spring pull (freedom-14) or a motor-driven wall can push the gun the wrong way when the estimate is wrong, or stuck; a brake cannot. A wrong estimate can stop a good move but cannot throw the gun off the seam. Overpower it and it slips; the slip is a reading (below).
- **The override is data.** When the hand pushes through the wall, the position advances while the clamp is held: the scales see a slip, and the hand's target minus the estimate at that moment is the hand's disagreement with the eye. If the hand steers by its own view and that view is unbiased, the mean disagreement is the eye's bias, which no closed loop of the eye alone can see (eyes-01, entry 3); ten pushes give it to about 0.03 mm at a hand resolution of 0.1 mm (calc/feedback-budget.mjs). A light, tone or spring leaves no such trace: there is nothing to disagree with.

## What carries the loads, what establishes position, what is free or restrained, what drives or adjusts

- **Carries.** Gun and shell to a lug; the lug rod to the slide carriages; the carriages on two rails; the rails on a base plate at the end of the locked friction arm; a constant-force spring carries the gun's weight on the vertical slide so the hand pushes friction, not weight. The umbilical's pull also goes through the radial rail.
- **Establishes position.** The corner in the gun-borne image (eyes-01) is the reference; the friction arm is locked once and leaves the dot within the stage's ±6 mm (illustrative: 1.2 mm radial, -0.9 mm vertical in the scene); the two linear scales give the slide positions and speeds.
- **Free.** The hand's motion along both slides inside the stage travel; everything the slides do not touch (the tilt of the beam, the tangent) stays where the arm and the hand leave it and is neither seen nor held by this layer.
- **Restrained.** By the brake, softly: refused moves away from the estimated seam outside the band, up to the clamp's capacity (2 N in the scene, unmeasured); by the stage's end stops.
- **Driven.** Nothing moves the gun. The clamps are the only things software commands that touch the hand's path, and the LEDs.

## What software could command, what it could observe, what stays manual

- **Command.** A clamp on each slide (off = free; power off = free), the band, the light bar pattern (radial stick, vertical stick, live / stale / blind).
- **Observe.** The eye's corner minus dot, radial and vertical, with a valid / stale / blind flag; the two scales (position and speed); slips (position advances while clamped); the clamp state.
- **Manual.** Pushing the gun; locking the friction arm and placing the neighbourhood; the trigger; deciding whether to trust the bar or the wall.

The brake rule per axis is one line: *clamp if the hand is moving away from the estimated seam and the estimate is already at the band's edge.* It needs the estimate's sign and size, its freshness, and the slide's direction of motion. Two safety rules are drawn: a blind or missing estimate releases the brakes and darkens the bar, and power off is free.

## What was tried to break it

1. **The wall sits where the estimate says.** Conflict: with a bias of 0.3 mm the wall stands 0.3 mm from the true seam. The hand that steers by eye and starts inside the band is stopped 0.2 mm short of the true seam and must push through at the clamp's capacity; a hand approaching from outside is not stopped at all (moves toward the estimated seam are free), which is why the scene has buttons for both. Assumption: that a wall placed by the estimate is a wall in the right place. What the change alters: the slip is logged as the hand's disagreement; the strip panel draws the estimated seam, the band, the refused side and the hand's target at the scale of the error. What it leaves uncertain: whether the hand aims at the true seam or at what its own eye sees through a shield; the log cannot separate the eye's bias from the hand's (a touch or a sectioned tube can: freedom-12, eyes-07).
2. **A frozen estimate.** Conflict: the bar looks live and green while the dot drifts (the seam moves at most 0.02 mm/s: 0.2 mm in 10 s); and a frozen value outside the band turns the wall into a one-way valve: moves toward the frozen value are free, moves away are refused for as long as it stays frozen (the scene reproduces this). Assumption: that the last value is a safe fallback. What the change alters: a stale reading shows as a dimmed, dotted bar, and the brakes should release after an age limit. What it leaves uncertain: a real timeout.
3. **The eye is blind.** Conflict: at some hand poses or camera mountings the corner is not visible (pose B with the camera on top, eyes-01 entry 2); the estimate is gone. Assumption: that the layer can be available whenever the hand is working. What the change alters: the layer degrades to no layer: bar dark with one violet mark, brakes released; the scene's camera position, clock angle and pose variant show where the holes are. What it leaves uncertain: how often a real hand-held pose falls in one.
4. **The operator cannot see the bar.** Conflict: from the gun's own side the wall hides the dot; from across the bore the bar may be behind the barrel. Sweeping the bar position (70 to 120 mm behind the tip), its clock angle and the operator's azimuth in the scene: from 150° to 210° round the tube, 250 mm above the rim, the operator sees the dot; the bar is in the line of sight for most clock angles at 70 to 90 mm and the angle between bar and dot is 3° to 13° (16 to 17° at 120 mm), inside one glance; from 90° and 120° the dot is hidden, and the bar is in view at 12 to 19° from where the dot would be. Assumption: that the operator's eyes are where the dome analysis puts the good stations. What it leaves uncertain: which side Derek stands, the eyewear he wears (does it pass a green and an amber LED?) and the process glow: the bar's brightness against the bead is unmeasured.
5. **A brake that engages late.** Conflict: at 3 mm/s and 78 ms from the event to holding (33 ms frame, 15 ms processing, 30 ms clamp) the gun crosses 0.24 mm past the band's edge, more than the band itself; a light bar acts after 249 ms, mostly the operator's own 200 ms (0.75 mm). Assumption: that the wall is where it is drawn when the hand reaches it. What the change alters: the band must be sized against speed times latency, or the brake engaged early with the wall drawn inside the band. What it leaves uncertain: clamp latency and stiction (a release step is a jump the hand feels): no listing read gives either.
6. **A brake on a bought arm instead of a slide.** The encoded arm (borrowed-03) has six joints, and a brake on a joint resists both the radial and the tangential motion that joint makes at the dot; the hand's force finds another path in a redundant arm. A per-joint rule ("clamp joint i in the direction that increases |e|") is a passive rectifier in joint space, but it needs the Jacobian from joint angles to the eye's error, which the arm's own kinematics gives only to the arm's accuracy and which could instead be learned by nudging each joint and reading the eye (borrowed-05's method). Not drawn: the coach loop's slides give a Cartesian wall with no Jacobian.
7. **Power off.** The weight is on a constant-force spring, so a released vertical slide is at rest only if the spring matches the gun and the umbilical's pull; otherwise it runs to its end stop. The travel stops (±6 mm here) keep the nozzle off the work. Left standing: the balance.

## Branches and combinations

- `use-06-coach-loop` (this arrangement with knobs and a screen, advice rounded to the knob step); `freedom-14-hand-plus-guidance` (a force through a soft anchor, the wall/centring/damper helps); `borrowed-19-haptic-jog` (the feel on a knob, not on the gun); `borrowed-03-encoded-arm` (the hand-held arm; here its encoders give direction only).
- `eyes-18-what-the-estimate-owes`: the lens on this layer: seven channels (bar, tone, buzz, spring, brake, stylus, hand alone) against five faults.
- `eyes-19-touch-cue`: a stylus that says "wall" with no estimate behind it.
- `freedom-09-pose-logger` with `eyes-03-marker-cube` tags (freedom's named combination): a hand-held gun on a passive support, the pose observed and logged, no springs pulling; the layer on it would be the bar only, fed by the eye, and the tags would supply the coarse pose.
- A knob or a second hand-held eye station could take the operator's view off the shell.

## Unresolved problems, questions for Derek

What a printed pad on a rail holds, how fast a 5 N solenoid clamps it and what it does on release; whether a hand tolerates a wall that arrives without warning; whether the eye sees the corner from hand-held poses at all (eyes-01: glare, fume, spatter); the eye's bias is the wall's bias; the beam's tilt is neither seen nor held; the gun's mass, the umbilical's pull and how much a hand yields per newton (freedom-14's question).

- Which side do you stand on, and which hand holds the gun?
- Do you wear eyewear that passes a green or an amber LED near the nozzle?
- Would you accept a wall you can always push through at about 2 N?
- How far does your relaxed hand yield per newton at the grip? (Push on the gun with a spring scale, gun on its rest, and read how far it moves.)
- Does a green line laser on the plate look like a kink in the corner to your own eye, from where you stand? (If yes, the line laser of eyes-01 is also the operator's guide.)

## Assumptions

- **[unknown]** the hand (no model here: two sliders), clamp capacity and latency, stiction, the gun's mass, the umbilical's pull, the operator's side and eyewear.
- Illustrative: stage travel ±6 mm; setup offset 1.2 / -0.9 mm; capacity 2 N; band 0.10 mm; LED step 0.05 mm; operator eye 330 mm from the tube axis at the chosen azimuth and 250 mm above the rim, 30° field of view; camera 85 mm behind the tip on top; bar 80 mm behind the tip at clock 45°.
- Derived: latency arithmetic and pushes-to-detect in `calc/feedback-budget.mjs`; visibility from the drawn geometry, not optics.

## Sourcing pointers

`sourcing/eyes.md` wave 3 (Prime only): WS2812B 8-LED stick, 10 for $18.99 (4.8 stars, 35 ratings, "100+ bought", product page opened); push-pull solenoid 12 V, 5 N, 10 mm stroke, $7.99 (4.1 stars, 383 ratings, "50+ bought", product page opened); MGN9 100 mm rail with carriage, $9.99 (search card); 20 coin vibration motors $12.99 ("100+ bought", search card) and a DRV2605L haptic driver breakout $11.81 (search card, thin volume evidence) for the buzz of eyes-18; a gun-borne camera and green line laser as in eyes-01. No magnetic-particle brake or small friction clutch at a hobby price was found on Prime (spring-applied 24 V brakes are $211 and up). All of these are printer-class parts with next-day delivery; what none states is a stiction or a latency.

## Scene

`eyes-17-lit-bar-brake-wall`. Branch: layer (none / bar / brake / both), the estimate's fault (good / biased / frozen / dropout), gun pose. Actuator (software commands): the band. State: brakes powered, clear the log. Scene edits: the hand's target (radial, vertical) and push force, clamp capacity, bias, camera position and clock, bar position and clock, operator azimuth. Panels: the wall at the scale of the error, the log of pushes that slipped the brake.
