# eyes-07 Sectioned calibration tube

Scene: `scenes/eyes-07-sectioned-tube/` (developed). Origin: swarm (eyes framing). Maturity: developed.

**Picture it.** A spare tube with a plate seated in it has been sawn in half through the axis and the weld station. It stands on the rotator nest with the gun on the intact half. On the free side a camera looks along the tangent, a few degrees above the plate, and its picture is the corner cross-section itself: the plate's top edge, the wall's face, the tip of the nozzle and the red spot, all in one frame, edge-on. The whole L-shape that the kit's corner inset draws as exact scene geometry is here a real camera view.

## The proposal

A **ground-truth view** used to calibrate everything that is inferred elsewhere. On an intact tube no camera can see the corner cross-section: the wall is in the way of every tangent view. On a half-tube it can. Move the gun to a set of offsets; for each one the section camera gives a direct reading of the dot against the corner, and whatever sensor is under test (the gun-borne eye, tags, proximity pads) gives its own. The pairs give the sensor's bias (mean residual) and noise (scatter). Apply the bias; the mean residual of later samples goes to zero. The same procedure labels each dry run for an AI that is learning what a good aim looks like.

What the section view actually measures: the spot's position along the L-profile (a single number: short of the corner on the plate, or above it on the wall), plus the nozzle tip and axis in the same picture, from which the focus offset follows given the fixed nozzle-to-focus clearance. The along-seam offset and the out-of-plane tilt are not visible edge-on.

## What carries loads, what establishes position, what is free or restrained

The half-tube stands in the existing nest (its fit and height are unchanged); how it is clamped with half the wall missing is unresolved. The section camera has its own bench stand, not drawn. Nothing new carries the gun. The section face (cut edges in one plane) is the reference.

## What software could command, observe, and what stays manual

- **Observe:** dot (focus) against corner, radial and vertical, at about 0.02 mm per pixel for the drawn camera; where the beam lands along the profile; the residual of any inferred sensor. On a real tube: nothing (badge "section camera blocked").
- **Command:** nothing new; the gun is moved by whatever moves it in other ideas.
- **Manual:** sawing and mounting the half-tube; aiming and focusing the section camera; choosing the sample poses.

## What was tried to break it

1. **A full-height wall on both sides.** The tangent view is blocked by the wall for any camera (Real tube mode: the frame turns red). Repaired by the half-tube.
2. **The dot exactly on the cut plane.** Half of it would sit on the cut edge. Repaired: the gun is offset 1 mm into the intact half; the section face is then 1 mm in front of the dot, invisible to a camera a few degrees above the plate.
3. **The phantom is not the real part.** Half the wall is missing, so light reflecting off the missing half is missing, and a heat-free dry run stands in for welding. Assumption: a bias found on the phantom transfers to a real tube. What this leaves uncertain: whether reflections from the missing wall change a real sensor's bias. Suggested check: compare against a section of a real welded tube afterwards.
4. **Calibration on one gun pose does not carry to another** if the mapping depends on pose. Three pose variants are in the scene; the same procedure has to be repeated per pose or sampled across the poses that will be used.
5. **How many samples.** With the stand-in sensor's 0.05 mm noise and a 0.30 / -0.20 mm hidden bias, ten random samples find the bias to within about 0.02 mm (the scene finds 0.285 / -0.184); the standard error of the mean falls as the noise over the square root of n (about 0.016 mm at n = 10).
6. **Grazing incidence.** Seen from a few degrees above the plate the plate top is edge-on: the spot on it is foreshortened and dim. Uncertain whether the dot is visible at all (bare stainless, 0.3 mW).
7. **One phantom is not many tubes.** The plate seat depth varies tube to tube (**[unknown]** by how much). Several half-tubes with different seat depths would be needed to say how much of the calibration depends on it.

8. **The tip-to-dot vector of a touch stylus is a calibration the phantom can take** *(from freedom's exchange, smaller remarks; no objection to the idea)*. The calibration compares two views of the same corner at the same instant, so how the half-tube seats does not enter it; the same procedure that finds a camera's bias finds the vector between a stylus tip and the dot (touch the cut wall and the cut plate with the stylus while the tangent camera sees the dot). What it alters: eyes-05 and freedom-12 get a way to measure the vector they lack, off the real tube. What it leaves uncertain: whether a steel ball at 0.2 N marks the cut edge of a phantom (it should not matter: it is a phantom).

## Branches and combinations

Calibrates `eyes-01-gun-borne-eye` (its bias), `eyes-03-marker-cube` (cube-to-dot), `eyes-04-proximity-skin` (its model), and the sweep of `eyes-06-dot-as-probe`. Not itself a welding arrangement.

## Unresolved problems, questions for Derek

Whether the dot shows at grazing incidence on bare stainless; whether the section face glares; how to hold and re-seat a half-tube repeatably; whether a half-tube made from the same stock (a saw cut through the axis) is usable at the plate (the plate's ports lie on the cut line and would show as slots). **Question for Derek:** take a spare tube half, set the gun to your usual pose, and look along the tangent with a phone from 20 cm. Is the dot on the plate visible against the section?

## Assumptions

- Tube and plate dimensions from the fabrication sources **[repo]**; plate ports omitted. Gun proxy from the manual **[manual]** p.17; poses A, B, C are reference-scene rotations (illustrative).
- Section camera: 8 degrees at 200 mm, about 0.02 mm per pixel, direct reading = scene value + 0.01 mm. **illustrative**
- Stand-in sensor: scene value + hidden bias (0.30, -0.20 mm) + 0.05 mm noise; the same numbers as the defaults of eyes-01. **illustrative**
- A band saw and a printed clamp are available **[repo]** tools.md (metal band saw).

## Sourcing pointers

`sourcing/eyes.md`: none specific; a section camera can be the Arducam OV9281 with a longer M12 lens, or a phone. The tube stock is what the project already buys.

## Scene

`eyes-07-sectioned-tube`. Scene edits: tube on the nest (sectioned or real), gun pose variant, section camera elevation, gun offsets; the calibration log has state buttons (sample, ten samples, apply, clear).
