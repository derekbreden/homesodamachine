# eyes-03 Marker cube

Scene: `scenes/eyes-03-marker-cube/` (developed). Origin: swarm (eyes framing). Maturity: developed.

**Picture it.** A small printed cube sits on a stalk on top of the gun's barrel, each visible face carrying a black-and-white fiducial tag. Two ordinary cameras on the bench look at the gun from across the bore. Software reads the tag corners and knows where the gun is in the tube's frame, to a few tenths of a millimetre, without either camera ever seeing the laser dot or the seam.

## The proposal

Move the line-of-sight problem from the canyon to a cube. Tags on the printed shell (or a cube on a stalk), plus tags on the rotator turntable and bench as the tube frame. Fixed cameras solve the gun pose from the tag corners; the dot follows from a fixed offset measured once from a scan of the shell (or from a section view, eyes-07). The price is the lever arm from the cube to the dot: a tiny angular error in the tag pose becomes millimetres at the dot.

## What carries loads, what establishes position, what is free or restrained

- **Loads:** as in other ideas (the shell carries the gun); the cube is a small printed block on a stalk. Cameras stand on bench posts.
- **Position:** the tag frame (bench and turntable tags) establishes the tube frame; the cube tags establish the gun in it. The tube's own position in its nest (0.2 mm clearance, runout up to 0.25 mm TIR) is **not** observed by frame tags unless a tag rides on the tube.
- **Free / driven:** nothing is commanded here.

## What software could command, observe, and what stays manual

- **Observe:** gun pose (six numbers) in the tube frame; which faces each camera sees; an uncertainty that depends on where the cube is. It does **not** see the dot, the corner or the wire tip.
- **Command:** nothing; the pose could drive any actuator in other ideas.
- **Manual:** fixing the cube; calibrating cube-to-dot and the camera pair.

## What was tried to break it

1. **The expected trade: line of sight against lever arm.** Assumption: the wall would hide a cube placed near the nozzle, forcing the cube far back. What the scene shows instead: the barrel rises above the rim within a few centimetres (58 degree pitch, illustrative), so a cube 40 to 80 mm behind the tip is in plain view of cameras across the bore, at the side and even over the wall. The trade I expected is mostly absent. What actually bites: **the cube has to fit** (a 25 mm cube close behind the nozzle at the side of the barrel, clock angle -90, runs into the rim: grey squares in the plot, refused), and heat, spatter and fume are strongest exactly where the lever arm is shortest (unresolved).
2. **The cube on the housing.** 230 mm from the dot, 25 mm faces, two cameras at 500 mm: about 0.5 mm at the dot (1 sigma, first-order model, calc/marker-error.mjs). With 45 mm faces 0.3 mm. What this changes: use the pose only to seed a fine local sensor (eyes-01, eyes-04).
3. **A cube 40 to 80 mm behind the tip.** 0.14 to 0.21 mm with 25 mm faces; 0.12 to 0.14 with 45 mm faces; the floor is the assumed 0.10 mm cube-to-dot calibration. What this changes: a 0.15 mm class world pose from two ordinary cameras is plausible, if the noise figure holds.
4. **One camera.** The tag's depth along the viewing ray is the weak axis (about 0.6 mm at 500 mm with a 25 mm tag). A second camera turns that into the other's lateral direction: the position part of the uncertainty falls from 0.29 mm at 5 degrees between the two rays to 0.09 at 20 and 0.04 at 40 degrees or more (calc/marker-error.mjs, summed information). What I first assumed (that 10 degrees would lose most of the benefit) was too pessimistic and was wrong; what actually happens is that past about 20 degrees the total at the dot barely changes, because the lever-arm term dominates. Separation matters for the position part, not for orientation through the lever.
5. **Tags do not know where the seam is.** They say where the gun is. The seam comes from the frame tags and an assumption that the tube is where the nest says. What this changes: a tube-side observation is still needed (the sweep or corner sensors). Left standing.

## Branches and combinations

- Coarse pose (this idea) plus fine local sensor (`eyes-01-gun-borne-eye` or `eyes-04-proximity-skin`): the natural pairing.
- Where the cameras go: `eyes-02-where-can-an-eye-stand` (Beside preset).
- Calibration of cube-to-dot: `eyes-07-sectioned-tube`.
- `eyes-11-what-each-eye-sees`: tags are the only row that touches all six coordinates, all inferred through a chain.
- Wave 3, from freedom's exchange: **tags in place of the six draw-wire encoders of freedom-09 (pose logger).** Six 2 N return springs pull the gun with a net 8.9 N and a torque; tags load nothing. The trade is this idea's 0.14 to 0.21 mm at the dot (cube 40 to 80 mm back, two cameras) against the encoders' 0.06 to 0.09 mm (0.05 mm length step), and a place on the barrel the eye's camera also wants. Adopted here, not drawn. Neither is fine enough for a 0.1 mm band: for the hand-held feedback layer (`eyes-17-lit-bar-brake-wall`) the seam has to come from the eye at the dot, and the tags or encoders would serve only for the coarse pose and the direction of motion.

## Unresolved problems, questions for Derek

Tag detection under process light next to a laser; whether a printed cube survives near a laser head; whether cube-to-dot calibration holds when the shell is refitted; how the frame tags are held rigid to the tube; auto-exposure through the weld flash. The 0.15 px corner noise and 0.10 mm calibration floor are assumptions, not measurements. **Question for Derek:** can a printed cube of PETG or PA-CF stand about 5 cm from the nozzle during a bead without warping (it is heat and spatter, not the beam)?

## Assumptions

- Camera 1920 px across, adjustable field of view; corner noise 0.15 px; cube-to-dot calibration 0.10 mm **[illustrative]**.
- Model (calc/marker-error.mjs): per camera lateral (sc/2) Z/f and along the ray sc Z^2/(sqrt2 a f); camera information adds, so position depends on the angle between rays; orientation sc Z/(a f)/max(sin tilt, 0.35), x0.7 with two faces, over sqrt of the camera count; quadrature with the lever arm and the floor. **illustrative first-order**
- A face counts as seen when the camera has it in its field of view, the line of sight is clear in the drawn scene and the face looks toward the camera within 70 degrees.
- Scanning a gun and printing a shell that fits it are established **[Derek]** (shared context).

## Sourcing pointers

`sourcing/eyes.md`: Logitech C920 (32.7K reviews, "500+ bought in past month"); Arducam OV9281 global-shutter USB (mono, 100+ bought). Tags are printed; nothing to buy.

## Scene

`eyes-03-marker-cube`. Scene edits: cube position, clock angle, size; camera azimuth, separation, elevation, distance, field of view. The plot shows uncertainty at the dot against cube position with visibility and collision.
