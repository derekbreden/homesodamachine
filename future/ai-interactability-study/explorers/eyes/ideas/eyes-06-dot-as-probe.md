# eyes-06 The dot as the probe (sweep to find the corner)

Scene: `scenes/eyes-06-dot-as-probe/` (developed; mode "A sweeping probe"). Origin: swarm (eyes framing). Maturity: developed. Branch: `eyes-06b-corner-mirror` (the other mode of the same scene).

**Picture it.** A small radial axis moves the beam a few millimetres across the seam while a camera watches the red spot. The spot crawls along the plate, reaches the corner, then climbs the wall a little faster. In the camera's picture the spot's path changes speed, or turns, exactly at the corner. Software fits two lines, reads the break, and now knows where the corner is in the axis's own units.

## The proposal

Stop measuring where the gun is. Use the dot itself as the probe, and let the camera only detect *that the path changed*. The break of the spot's image path locates the corner in actuator coordinates without calibrating the camera or knowing where the gun is. That is exactly the offset needed to place the dot a chosen distance from the corner ("aim 0.4 mm short of the corner on the plate": go to break minus 0.4). The dot is the actual beam aim, so the result is the quantity that matters, not an inference from a sensor frame.

Geometry (section plane): plate top z = 0, wall face r = 0. The beam is tilted beta from vertical toward the wall. Shifting the beam by s moves the spot along the plate at 1 mm per mm; past the corner the spot climbs the wall at cot(beta) mm per mm (1.6 at 32 degrees). Any camera direction v projects those two motions to two image vectors; the path is straight at constant speed only when they are equal.

## What carries loads, what establishes position, what is free or restrained

Nothing new carries the gun. Any small axis (the trim stage of eyes-01, a rail, a micrometer turned by hand) sweeps the beam radially over about 8 to 16 mm. The corner is the reference. The actuator's zero is unknown to the software (the scene hides a 1.7 mm offset), which is the point.

## What software could command, observe, and what stays manual

- **Command:** step the sweep axis (-7 to +9 mm in the scene), then move to break plus the chosen offset.
- **Observe:** the spot's position in each frame; the break in the fitted path and its uncertainty; the Lambert brightness of the spot on each surface (how squarely the camera sees it). Not observed: the wire tip, the puddle; whether the visible break is the geometric corner.
- **Manual:** placing the camera; choosing the offset from the corner.

## What was tried to break it

1. **The camera in the section plane at about 58 degrees elevation.** The plate motion and the wall motion look equally fast in the same image direction; the kink vanishes (kink strength 0.00, calc/dot-probe.mjs). What this changes: move off 58 degrees or off the plane; the kink returns (0.23 at 45 degrees, 0.47 at 30). The dome (eyes-02, Kink colouring) shows the same hole.
2. **A camera at a grazing angle.** A low camera across the bore has a kink strength of 0.9 (the wall motion is 18 times faster in the picture than the plate motion) but sees the plate spot at a Lambert factor of 0.09 and 11 times compressed. Assumption: high contrast in speed means easy detection. What breaks: the plate spot is dim. What it leaves uncertain: whether the dot shows on the plate at all from there.
3. **Tangential views need a sectioned tube.** The strongest kink (a right-angle turn, 0.72) comes from the tangential view, which the wall blocks on a real tube. Near-tangent views from above the rim (about 100 to 110 degrees round the tube, 17 to 23 degrees up: the "Beside" preset of eyes-02) keep the dome's direction-change score at 0.99 (sine of the angle between the plate and wall image directions) with both sensitivities above 0.9. The dome's score counts only a change of direction; the scene's K also counts a change of speed, which is why a low in-plane camera (dome score 0) still finds the corner (K 0.9 at 5 degrees). What this changes: the sweep works from the sides of the tube, not from the far side.
4. **The corner is not sharp.** A fillet at the root, a tack weld, or the slip gap (about 0.13 mm) can shift the visible break away from the geometric corner. The sweep finds what the camera sees as the break. Left standing.
5. **How precisely.** At 0.05 mm per pixel and 0.3 pixel noise the model puts the corner within a few micrometres (0.003 to 0.005 mm 1 sigma, calc/dot-probe.mjs, ignoring slope uncertainty of the slow segment); the scene draws noisy frames at 0.6 pixel and finds it to a few hundredths. What this changes: the limit is not the camera; it is the corner's shape and the dot's visibility.
6. **The pilot's behaviour.** Whether the red pilot stays on and steady during the sweep, and whether the wobble (80 Hz x 2 mm during welding) applies to the pilot, are **[unknown]**. The spot is drawn as a point.

7. **A sweep through an axis that sticks reads as a corner, and "aim 0.4 mm short of it" needs the axis's gain** *(from freedom's exchange, smaller remarks)*. Conflict: through a seat, a rail or a bungee-carried gun the dot advances in jumps; the image path is still the same two lines, but the fit is told the commanded position, so the staircase reads as speed changes and the break moves by up to about the step (scene, stick 0.8 mm: error +0.22 mm against +0.02; with stop-and-look, +0.01). And a break in actuator units is a location; "0.4 mm short of the corner" needs the gain of the axis that swept: the nose stage of freedom-01b moves the dot 1.06 to 1.35 mm per mm, the tail wires 0.06 to 0.4 with cross terms of -0.05 to -0.47 in the tangent; the rim and the wall height in the same image give the scale. Assumption behind it: mine, that the axis is a clean stage. What the change alters: sweep by **stop-and-look** (each frame paired with a reading of where the gun really is: a scale on the gun side) or through the stiffest axis, or read the direction change, which stick-slip does not fake. What it leaves uncertain: how large a real slip is.

## Branches and combinations

- `eyes-06b-corner-mirror`: read the bounce spot instead of sweeping.
- With `eyes-01-gun-borne-eye`: the gun-borne camera can do the sweep (its trim axis is the sweep axis) and removes the need for the line laser.
- With `eyes-07-sectioned-tube`: the sectioned view is the tangential camera that makes the kink a right angle, for calibration.
- With `eyes-09-scan-then-weld`: a sweep at each of several tube angles gives the seam map without a separate sensor.

## Unresolved problems, questions for Derek

Whether the dot is visible on stainless; spot size (0.3 mW class, diameter unknown); a camera position with a view of both surfaces on a real tube. **Question for Derek:** slowly move the dot toward the wall until it climbs the wall. Does its path visibly change direction in a phone video taken from the side of the tube?

## Assumptions

Beam tilt 32 degrees in section (reference pose, illustrative). Plate and wall dimensions **[repo]**. Camera orthographic; 0.05 mm per pixel; 0.3 to 0.6 pixel noise **illustrative**. Kink strength K = |u_wall - u_plate| / (|u_wall| + |u_plate|) **[derived]**.

## Sourcing pointers

`sourcing/eyes.md`: Arducam OV9281 global-shutter USB camera; a red-pass filter is unresolved (only 650 nm IR-cut filters and expensive band-passes seen).

## Scene

`eyes-06-dot-as-probe`. Actuator: the radial sweep axis. Scene edits: beam tilt, camera azimuth and elevation, pixel size, noise, aim offset.
