# eyes-02 Where can an eye stand?

Scene: `scenes/eyes-02-where-can-an-eye-stand/` (developed). Origin: swarm (eyes framing). Maturity: developed. An analysis instrument more than an arrangement; it produces station presets that other ideas use.

**Picture it.** A dome of small spheres wraps the laser dot. Each sphere is a place a camera could stand; it glows green if it can see the dot past the wall, the rim, the gun and the wire, and grey or orange if not. The green region is a band across the bore and a cap above it, with a narrow orange cone cut out by the barrel. Switch the colouring and the same dome shows how squarely each place looks at the plate or the wall, how well it can tell radial from vertical error, and how sharply a dot sweeping across the seam would change direction in its picture.

## The proposal

Before choosing what an observer is, ask where it may stand. For the current gun pose, test a ray from every point of a dome (60 azimuths x 18 elevation rows (1080 directions) at 260 mm, adjustable) to the dot, and to three more seam points (the corner 8 mm either side along the seam, the wall 3 mm above the dot), against the drawn tube, rim, gun and wire guide. Colour by blocker, or by a sensitivity. Then drop presets of fixed eyes on it and count who sees what.

## What carries loads, what establishes position, what is free or restrained

Nothing carries the gun here. The dome asks where an observer could be. The fixed eyes are drawn on nothing (posts not drawn). Position is established by the dot at the joint; the dome is centred on it.

## What software could command, observe, and what stays manual

- **Command:** nothing.
- **Observe** (in the drawn geometry only): whether a proposed eye has a clear line to the dot and to the seam points; the share of the upper hemisphere that does; the widest triangulation angle among the eyes that do.
- **Manual / unresolved:** placing and calibrating the eyes; glare, dot brightness, fume (not modelled).

## What was tried to break it

1. **A camera outside the tube wall.** Assumption: any camera above the rim can see the corner. Conflict: the dot is at the wall, so every direction with a component toward the wall is blocked at once; 55.5 % of the upper hemisphere (solid-angle weighted) is blocked by the tube, and only 42.0 % sees the dot. The bore side is the only side that can see it.
2. **A camera straight overhead.** Visible (green) but vertical sensitivity falls to zero at the zenith: it cannot tell a dot on the wall from a dot on the plate. What changes: the Both mode colours only views with radial and vertical sensitivity at least 0.5 (29.0 % of the hemisphere).
3. **A low camera across the bore.** Assumption: the rim hides the corner from across the bore. Found: it does not; the dot is visible from 2.9 degrees elevation (6.35 mm over 125 mm, calc/view-sensitivity.mjs). What it costs: radial sensitivity at 5 degrees is 0.09, so one pixel is about 11 mm of radial error on the plate; vertical sensitivity is 1.0. Good for height on the wall, poor for the plate radius.
4. **The gun's shadow.** Assumption: the gun blocks a large part of the view. Found: 2.6 % of the hemisphere at the opening pose, and the visible share moves from 42.0 % to 42.1 % over the whole grip-axis roll range; the wall, not the gun, decides where fixed eyes can stand. The gun decides only whether one particular direction is lost. Uncertain: the wire guide is 5 mm wide and at 5 to 6 degree sampling it is almost never hit, so its shadow is under-sampled; the test eye shows it directly.
5. **The look-ahead station.** Two eyes above the rim 35 degrees of arc either side of the station, 46 mm above the rim. Both see the dot and all four seam points, with a 76 degree triangulation angle. But the wall's inner face is seen almost edge-on: 0.05 of square-on, against 0.79 for the plate (calc/look-ahead-geometry.mjs). They see the corner line, not the wall. It also has to be at least about 25 mm above the rim at 35 degrees to clear it.
6. **One eye per surface.** The wall faces the bore centre; it is seen square-on from across the bore (98 of 1080 directions have both a face-on wall at least 0.7 and the whole seam in view: azimuth 138 to 222 degrees, elevation 7.5 to 42.5). The plate is seen square-on from above (elevation 47.5 degrees and up). So no single eye is good at both; two are.
7. **The sweet spot.** The directions that tell radial and vertical apart best (both sensitivities 0.92 to 0.95) and make a sweeping dot change direction most sharply (kink 0.99) lie about 100 to 110 degrees round the tube from the station, 17 to 23 degrees above the dot: beside the tube, slightly above the rim, looking along a chord. Two eyes there (the "Beside" preset) see the whole seam and are 130 degrees apart. 159 of 1080 directions pass a looser test (both sensitivities at least 0.6 and the whole seam in view; azimuth 96 to 264, elevation 7.5 to 52.5).

## Branches and combinations

- Wave 3, from freedom's exchange: the dome with the support's own parts as occluders (a cup, a collar, a stage rod, a stalk): `freedom-11-eye-on-the-seat` draws it (47 of 66 stations clear with a rigid lug, 34 of 66 with the nose seat at 70 mm); `eyes-15-what-the-holder-hides` did it for the four holders of Derek's examples. Both scenes stay; this scene is tagged a lens.

- `eyes-02b-sensor-crown`: a ring of fixed eyes (preset "Crown of six": 3 of 6 see the dot, widest pair 87 degrees).
- Kink colouring is the input to `eyes-06-dot-as-probe`: it tells where a sweep can find the corner.
- The "beside" and "far side" presets say where the section-camera view (`eyes-07-sectioned-tube`) can be approximated on a real tube: not at all at the tangent (blocked by the wall), reasonably at 100 to 110 degrees.
- Feeds `eyes-03-marker-cube` (where cameras go) and `eyes-01-gun-borne-eye` (why a camera riding with the gun is the only one that always keeps a view).

## Unresolved problems, questions for Derek

- Being visible in the drawn scene is not being seen: glare on stainless, whether the 0.3 mW dot shows on the plate, fume, spatter, the camera's field of view are not modelled.
- The dome is for one dot position and no wire tip or hand. It assumes the proxy gun is the right size (needs the scan).
- **Question for Derek:** from about 25 cm to the side of the tube and 6 cm above the rim (the Beside station), can you see the red dot in the corner at all with the gun in your usual pose?

## Assumptions

- Gun proxy from the manual's envelope **[manual]** p.17; barrel, collar, housing, grip, wire guide, pitch 60 degrees and clearance 16 mm illustrative (kit). Tube and plate from the fabrication sources **[repo]**.
- Sensitivity = sqrt(1 - (v.n)^2) for unit viewing ray v and axis n (radial +X, vertical +Z). **[derived]**
- Kink = sine of the angle between the projected directions of the plate motion and the wall motion. **[derived]**
- Dome radius 260 mm, fixed-eye positions and the 35 degree arc are illustrative.

## Sourcing pointers

`sourcing/eyes.md`: Logitech C920 (high-volume webcam), Arducam OV9281 global-shutter USB camera, endoscope cameras.

## Scene

`eyes-02-where-can-an-eye-stand`. All controls are scene edits or view choices; nothing is an actuator.
