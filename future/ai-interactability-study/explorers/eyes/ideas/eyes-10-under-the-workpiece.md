# eyes-10 Under the workpiece

No scene. Origin: swarm (eyes framing). Maturity: sketch (taken far enough to break it; the useful form is small).

**Picture it.** For the first closure only, the tube stands on the rotator with its lower end open, and the rotator has a 90 mm service bore through the nest, turntable and base. A camera underneath looks up the bore at the underside of the plate that is being welded; a ring light above the plate shines down. The thin slip gap between plate and tube glows as a ring of light: its width around the circumference is a map of how the plate sits.

## The proposal

Use the open bottom of the tube as a window. Two things could be seen from below: **light through the slip gap** (a pre-weld map of plate eccentricity and root gap: the plate has about 0.005 in of radial slip, so the gap runs from 0 to 0.127 mm around the circle) and **heat on the plate underside** after the bead passes (a thermal camera, a check that the bead completed, not a control input).

## What carries loads, what establishes position, what is free or restrained

Nothing new carries the gun. The camera sits on the bench under the base (not drawn). The tube's bottom is in the nest; the plate seat is the reference. Second closure: the first plate closes the bottom, so nothing is visible from below. Restricted to the first closure by construction.

## What software could command, observe, and what stays manual

- **Observe:** ring of light and its width around the circle (gap map, eccentricity); thermal image of the underside. **Command:** ring light on/off; rotator to step the gap map. **Manual:** placing the camera; the back-purge hose sits in that same bore on the first closure (argon through the open held end, **[repo]** per-weld sequence), so the window is shared with a purge hose. Unresolved.

## What was tried to break it

1. **The ring of light.** Assumption: a camera below, looking at the plate edge through the bore, sees light leaking through the gap. Conflict: the gap is a slot 6.35 mm deep and 0.127 mm wide, so light passes only within about +-1.15 degrees of the tube axis (calc/under-workpiece.mjs). A camera on the axis sees the edge at 61.85 mm radius at an angle of atan(r / distance) from the axis: 22 degrees at 150 mm, 5.9 at 600 mm, 1.2 at 3 m. The gap looks dark from every distance a bench allows. What this changes: only a telecentric view (parallel rays; its front element about 125 mm wide) or a camera at about 3 m sees it. Left standing: the idea in its plain form fails on a number.
2. **A conical mirror below.** The slot emits an annular near-parallel beam along the axis; a 45 degree conical mirror under the plate would turn it outward, so a side camera could see the azimuths that face it, one at a time. Not drawn; the tube would have to turn to scan. What it leaves uncertain: whether the cone can be made and sits in the service bore.
3. **Reaching the edge through the bore.** Through a 90 mm bore (bore plane about 140 mm below the plate, illustrative) a camera close to the bore sees a big enough field (108 mm radius at 100 mm below the bore, reaching the 61.85 mm edge), so field of view is not the problem; the slot's acceptance angle is.
4. **Thermal view.** Heat crosses the 6.35 mm plate in about L^2 / alpha = 10 s (calc, alpha 4e-6 m^2/s illustrative): an infrared view of the underside lags the bead by about 10 seconds, about 80 mm of arc at 8 mm/s, and blurs it. Useful as a record that a bead reached a place, not for aiming. A 32 x 24 array (MLX90640) has pixels several millimetres wide on a 127 mm tube.
5. **Second closure.** The first plate is in the way; nothing is visible from below.

## Branches and combinations

The thermal record could go into the per-tube log of `eyes-07-sectioned-tube` style labelled data. The idea of "seeing through the workpiece" is otherwise a dead end here.

## Unresolved problems, questions for Derek

Whether a gap map would change what is done (tacks are already placed by hand); whether the plate slip is ever near 0 or 0.127 mm in practice. **Question for Derek:** with a torch behind a first-closure tube, can you see light through the slip gap from below at all?

## Assumptions

Plate thickness 6.35 mm; slip 0.005 in radial; Ø90 mm service bore; weld radius 61.85 mm **[repo]**. Geometry beyond that, thermal diffusivity and bore-to-plate distance illustrative. The slit acceptance angle is arithmetic **[derived]**.

## Sourcing pointers

`sourcing/eyes.md`: Waveshare MLX90640 (Prime, $68.99, 10 reviews, no volume figure); endoscope camera (Prime, $25.99, 7,785 reviews, "6K+ bought").

## Scene

None.
