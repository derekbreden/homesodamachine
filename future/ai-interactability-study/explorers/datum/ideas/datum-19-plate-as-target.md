# datum-19-plate-as-target: the rim and the ports calibrate the camera from every frame

Scene: `scenes/datum-19-plate-as-target/index.html`. Depth: developed. Origin: swarm (my own idea, in the thin region "calibrating the observation itself"); extends `datum-05-fiducial-collar` (the work wears its own coordinate system) without a collar, and `trials-03-dot-touch-probe` (its camera A reading). Calc: `calc/plate_target.js`.

## Picture it

A camera over the bore. In its picture: two concentric circles for the rim (the inner edge at 61.85 mm radius, the outer at 63.5, both in one plane), two round holes on a diameter for the plate's ports (Ø11.1 mm, 19.05 mm either side of the axis, at the plate face 6.35 mm and a little more below the rim), a corner circle just inside the rim edge (the wall's inner face shows as a thin strip between them when the camera stands off-axis), and the dot. The scene fits the camera's pose to the rim and ports, predicts where the corner is, and reads the dot against it.

## The proposal

The tube carries its own calibration target. From the rim circles and the two ports a Gauss-Newton fit gives the camera's position and tilt in the *tube's* frame (five numbers) and, more weakly, the seat depth (a sixth), in every frame, with no fiducial added and no reference to the room. That is hand-eye calibration from the work, repeated per frame: a camera that drifts or is knocked is recalibrated by the next picture. It needs the roll about the tube axis, which the ports give modulo 180 degrees (a tack or a paint dot resolves the rest); it assumes a calibrated lens.

The reason it matters is a fact about the corner. The rim edge is the sharp, bright feature; the corner is 6.35 mm below it. Seen from an off-axis camera the corner appears displaced from the rim edge by 6.35 x tan(psi), psi being the angle between the line of sight and the axis at the station: 1.31 mm for a level camera on the axis at 300 mm over the rim, 2.1 mm at 200 mm, 2.8 at 150, 0.78 mm 25 mm toward the station. Reading the dot against the rim edge is wrong by that; the fit predicts it.

## What carries the loads, what establishes position, what is free or restrained

Nothing carries or moves anything. The camera may be fixed to the room or ride on the shell (the fit recovers the pose against the tube either way). Position is established by the rim circles and ports, plus the fit.

## What software could command, observe, and what stays manual

- **Command:** nothing required.
- **Observe:** the dot, the rim edge and the port centres in one frame; from them, camera pose, seat depth (weakly), and the dot's offset from the corner with the parallax removed.
- **Blind:** the corner itself if the wall's foot is in shadow (it is predicted, not seen); the melt.
- **Manual:** the 360 degree roll (a mark); a touch of the plate if the perspective depth is too loose.

## What was tried to break it

From `calc/plate_target.js`: dot reading error at the station, mm rms over 60 draws, pixel noise 0.15 px, f = 1500 px.

1. **The naive reading** (rim edge is the seam) is off by the whole parallax: 0.5 to 2.8 mm.
2. **A nominal-camera correction** (a level camera on the axis) leaves 0.04 mm when the camera really is there, 0.21 mm when it is 10 mm off, 0.53 mm at 25 mm, 0.85 mm for a camera 40 mm toward the station tilted 8 degrees. **The fit** leaves 0.04 to 0.08 mm in all of these.
3. **The fit adds noise when the camera is where it was assumed.** At H = 300 mm the seat depth from perspective is weak (0.35 mm one standard deviation), it enters the prediction by the tangent (0.2) and costs about 0.07 mm, so the fitted reading of a perfectly placed camera (0.08) is worse than the nominal (0.04). Repairs: the seat depth from a touch (0.03 mm; the reading error falls to 0.04 in a tilted, offset case where the perspective fit gives 0.07 and an assumed depth 0.10), or bring the camera close: at H = 150 mm the depth from perspective is 0.10 mm, at 200 mm 0.18, at 450 mm 0.87 (and the fitted reading is then worse than nominal).
4. **Pixel noise:** at 0.5 px the fitted error is 0.26 mm and the depth 1.3 mm. The idea needs 0.15 px edge and centroid fits; that is an assumption about a clean image of the rim.
5. **Left standing:** lens distortion; glare on polished 316L washing out the rim edge; a deburred chamfer or band-saw kerf on the inner edge moving the apparent edge with viewpoint (the fit would read it as pose); the gun and wire hiding parts of the rim; the corner's shadow.

## Branches and combinations

- Extends `datum-05-fiducial-collar` (no collar: the rim and ports are the target). Feeds `trials-03` (camera A's reading of the dot against the seam), `datum-14` (the tube's own angle for the work piece of the map, modulo 180 degrees), `eyes-01` (a gun-borne eye needs exactly this pose), `datum-06` (seat depth by eddy current: an alternative to the perspective depth).
- Transferable: the work is its own calibration target; parallax of a recessed corner is depth times tangent; perspective gives depth only when the camera is near.

## Unresolved problems and questions for Derek

- Photograph the bore from 300 mm and from 150 mm straight above with a phone: are both rim circles and both ports sharp in the picture, and does the wall's inner face show as a strip outside the corner? Is the inner rim edge sharp or chamfered?

## Assumptions

Geometry `[repo]` (rim radii, port spacing and size, recess 6.35 mm); pinhole camera, 1500 px focal length, 1280 x 960 px, calibrated lens, pixel noise: illustrative. Correspondences between rim samples and azimuths follow from the ports' roll and are assumed resolved.

## Sourcing pointers

`sourcing/datum.md`: Arducam OV9281 global-shutter camera (wave 1); a low-distortion M12 lens (this pass, if found).

## Scene id

`datum-19-plate-as-target`.
