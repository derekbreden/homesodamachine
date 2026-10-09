# borrowed-08-manual-stack-spotter: hands turn the knobs, software watches the scales and says which

Origin: swarm. Maturity: rough. Scene: `scenes/borrowed-08-manual-stack-spotter/index.html` (the geometry is borrowed-02's, the coach is borrowed-03's). Numbers: `calc/spotter_rounds.py`.

## Picture it

A stack of parts from a machine shop and a camera shop: a cross-slide table under a lab jack under a geared photo head, each axis with a digital scale or an angle readout, the gun clamped on top. No motors. A screen says: "turn X to +1.32, Z to -0.40, pitch to 34.5 degrees", and after the camera has looked, "now X by -0.11". A person turns the knobs; software reads the numbers and never touches anything.

## The proposal

Software observes and computes; a human is the actuator. The coupling that makes a manual stack fiddly (turning the pitch knob moves the dot, so two other knobs must follow) is exactly borrowed-02's formula, `dot = C - t * g(yaw, pitch)`: software converts a wanted orientation into the three linear scale readings that keep the dot on the seam, and then closes the residual from a camera. Every part is a stock product: manual cross-slide tables and digital linear scales are on Prime today (sourcing/borrowed.md: MYSWEETY compound slide table $59.99, 1,068 ratings; a 150 mm LCD digital scale $26.99, 207 ratings; geared heads were not sourced). It is the cheapest and fastest-in-hand rung of the ladder that borrowed-02 and borrowed-03 climb.

## What carries the loads, establishes position, is free, restrained, driven

- Load path: gun, geared head, jack, cross-slide, bench. Position: the scales, then the camera. Free: none between corrections; each knob locks. Driven: nothing; a person turns knobs. Restrained: gib screws and locks.

## Software: command, observe, manual

- Could command: nothing. Could observe: scale readings (if the scales have a data port; the LCD scale's output was not checked), a camera estimate of the dot. Displays the next instruction.
- Manual: everything physical.

## What was tried to break it

1. **Is the hand the limit?** A model (calc/spotter_rounds.py, illustrative): an instruction each round equal to minus the camera's estimate; the person lands within +-hand of the number on a 0.01 mm scale; a reversal loses backlash. Results, 400 trials each, start 1.5 / -1.0 mm, target 0.1 mm: with a clean camera (0.03 mm noise, no bias) one round suffices for a hand error up to 0.05 mm, and 2 rounds at 0.15 mm; with a noisy camera (0.15 mm) about 4 rounds regardless of the hand; with a 0.15 mm camera bias the true error never gets reliably below 0.1 mm whatever the hand does. Assumption: the person is the noisy part. Finding: the camera is; the hand is not the limit.
2. **Backlash of a cheap slide.** In the model 0.1 mm of lost motion adds almost nothing when the instruction carries the sign. Not checked on a real table.
3. **Reading the scales.** LCD scales need a person or a camera to read them unless they have a data port (unchecked). A machinist's DRO with an interface is the alternative ($60 5-micron kits with 3 to 4 ratings each on Prime, unverified quality).

4. **The trim can make it worse.** In the scene, after position numbers that leave 0.05 mm, a camera with 0.3 mm of bias asks for a trim that moves the true error to about 0.27 mm, and it does not improve on further presses. Change: trust the camera only when its bias is smaller than the mechanical error. Left standing: no camera's bias on this corner is known.
5. **The first move.** Turn the head by a few degrees with the slides at home and the dot leaves the seam by about 3 mm per degree, then the gun meets the tube; the scene holds the last valid pose (LIMIT). A person has to turn head and slides together or in small steps: the spotter's numbers assume the pose after the move.

## Branches and combinations

- Combines with borrowed-02 (same formula, motors instead of knobs; a stepper on each knob is a printed adapter), borrowed-03 (the coach line), borrowed-05 (calibrating the camera to the knobs).

## Unresolved problems and questions that need Derek

- Whether a geared head can hold a gun and its umbilical without creep; the gun's mass.
- Questions for Derek: how much manual adjustment he tolerates per tube, and whether he already owns a cross-slide or a geared head.

## Assumptions

- Hand error, backlash, camera noise and bias are illustrative; the pipeline is a toy two-axis loop. The 0.01 mm scale resolution is a typical figure, unchecked for the listed scale.

## Sourcing pointers

sourcing/borrowed.md: cross-slide table, LCD digital scale, and the note about 5-micron DRO kits.

## Scene

`borrowed-08-manual-stack-spotter`
