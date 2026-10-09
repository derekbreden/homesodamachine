# datum-05-fiducial-collar: the work wears its own coordinate system

Scene: `scenes/datum-05-fiducial-collar/index.html`. Depth: developed. Origin: swarm. **Software observes and moves nothing.**

## Picture it

A printed ring sits on the tube, turns with it, and carries a row of square black-and-white tags around its top face. A small camera on the gun's printed shell looks down at the ring. Tags in view light up green in the main view and in the camera's own picture. From them software knows where the tube is in the gun's frame, and infers the hidden corner from a fixed offset. A blue estimate marker in the seam cross-section shows the inferred dot position beside the exact one.

## The proposal

The wall hides the corner from anything outside, but the tube is a rigid body: anything on the outside that is fixed to it can stand in. Tags on a ring on the work give the tube's pose in the camera's (that is, the gun's) frame, with runout included because the tags move with the work, and with no reference to the room, the bench or the rotator. The dot's offset from the seam is then inferred (tags plus a known offset), not seen.

Nothing has to move, so this is a pure observer. Uses: a flight recorder for the hand-held weld (log the gun's pose against the seam through a whole weld, to learn what good hand welds look like, or to replicate them later); a check on a positioner that does the moving; cues to the hand (LEDs on the shell) that are software controlling the person.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** the ring seats on the tube and carries nothing but itself; the camera hangs from the printed shell (a light bracket). Nothing here carries the gun.
- **Position:** the tags on the ring, plus a fixed offset to the corner; seat depth is *not* known and has to be entered per tube.
- **Free / restrained / driven:** nothing driven by the sensing.

## What software could command, observe, and what stays manual

- **Command:** nothing required. Optional: cues to the hand, corrections to an arm.
- **Observe:** tags in view and their size and viewing angle; the tube pose from them; the inferred dot offset. Blind: the corner and dot (the wall hides them), plate seat depth unless entered.
- **Manual:** seating the ring; entering a measured seat depth (the scene's toggle); aiming the camera once.

## What was tried to break it

Numbers from `calc/tag_lever.py` (`calc/tag_lever.out`); noise, systematic angle and fit error are illustrative.

1. **Tags on the vertical outer wall of a collar.** *Conflict:* the camera on the gun is above the rim and the tags are on a vertical face, so they are seen 70 to 78 degrees off-normal: about 29 px wide for an 8 mm tag at 96 mm, 13 px at a longer range, with 0.63 to 1.33 degrees of tilt error per tag. *Change:* put the tags on the top face of a flange on the rim: about 30 degrees off-normal and 110 px wide, 0.31 degrees of tilt error. *Cost:* the flange is a turning ring near the nozzle and beam, which the crown scene shows must stay outside the beam corridor.
2. **The lever arm.** *Conflict:* error at the seam is tilt error times the distance from tag to seam. 8 mm tag at 100 mm and 30 degrees: 0.11 mm at a 5 mm lever, 0.22 mm at 20, 0.39 at 40, 0.76 at 80 mm, with a 0.3 degree systematic error and 0.10 mm ring fit error. A collar 60 mm below the rim gives about 1.4 mm from one tag; a flange 13 mm away gives 0.14 mm. *Change:* tags near the rim; more tags in view reduce the random part but not the systematic part.
3. **The tags do not know the plate.** *Conflict:* the corner is a fixed offset from the collar. *What the scene shows:* the estimate misses the plate's seat-depth error and the seam cross-section shows the gap. *Change:* enter a measured seat depth per tube (a toggle in the scene), or take it from a plunger (datum-03) or the eddy scan (datum-06).
4. **Systematic calibration error.** *What the model does:* it scales with the lever arm and does not average away. *Uncertain:* the real size; a bench test against the dial indicator would give it.

## Branches and combinations

- Combination worth building: the crown's lower ring (datum-03) carrying the tags on its top face, which puts the lever arm at about 13 mm and makes the ring both the mechanical and the optical reference.
- The hand-held branch: the same camera and tags as a flight recorder with a person holding the gun. No scene of its own.
- Transferable: tags on the work; the lever-arm rule.
- Without a collar: the tube's rim circles and the plate's two ports are a target that every camera over the bore already sees; `datum-19-plate-as-target` fits the camera's pose from them in every frame, and finds that the rim edge is displaced from the corner by 6.35 x tan(line of sight to the axis) (0.5 to 2.8 mm). The collar's lever-arm rule applies to it too: the corner is 6.35 mm from the rim edge, so the fit's pose error acts over a short lever.

## Unresolved problems and questions for Derek

- Detection near a weld: glare on polished steel, fume, welding light; illumination is not modelled and the kit's line of sight is drawn geometry only.
- Where a camera can live on the shell without being blocked by the wire guide or covered by fume.
- Is the OD clear from the rim to the nest on the tubes you use? Does the wire guide leave room?

## Assumptions

- Geometry: tube, plate, rim [repo]; gun proxy [manual envelope; sections illustrative]. Camera pinhole, 1280 px across, 12 px minimum tag; corner noise 0.3 px, systematic angle 0.3 degrees, fit error 0.10 mm, hand error 0.8 / -0.6 mm, seat-depth error 0.30 mm: illustrative.

## Sourcing pointers

`sourcing/datum.md`: Arducam 100 fps mono global-shutter USB camera (Prime confirmed, "100+ bought in past month", $49.99); printed tags need only a printer.

## Scene id

`datum-05-fiducial-collar`.
