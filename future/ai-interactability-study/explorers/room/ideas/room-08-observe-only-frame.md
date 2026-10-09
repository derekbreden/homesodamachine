# room-08: observe-only frame (software watches, moves nothing)

**Origin:** swarm (room framing; a partial arrangement where software observes and nothing moves). **Scene:** `scenes/room-08-observe-only-frame` (drawn in wave 3). **Depth:** developed (was a sketch).

## Picture it

A rigid frame of aluminium extrusion standing round the bench, holding three cameras on kinematic mounts (so they can be taken off and put back in the same place) on the side of the tube away from the operator's hand. The operator holds the gun as today. The printed shell around the gun carries a few fiducial tags on the barrel top and the housing back. Software sees the dot, the seam, the tags and the forearm, and says what it sees: a line on a screen, a tone.

## The proposal

Make the room a measurement volume. The frame is calibrated once (cameras to frame, frame to rotator by looking at a tag on the tube's nest). While a weld is done by hand, software records where the dot was relative to the seam and the shell's pose over time: a record of what a good hand does. It can cue the operator ("dot 0.4 mm inside the wall") without moving anything, and the recording is data for the later, moving arrangements (teach, record, replay). **Two recordings, not one:** the dry dot (laser at the red reference only) and the bead (trigger held), the second exposed for the process glow with a short exposure and a neutral-density filter.

## What carries, what establishes position, what is free

Carries: the frame carries the cameras; the bench carries the rotator; the hand carries the gun. Position: the frame is the reference for every observation; the tags say where the shell is, the dot says where the beam is. Free: the gun (hand-held). Driven: nothing but the existing rotator.

## Software

- **Observe:** the dot and seam from the cameras that see them (the dot is a point source, easy to find); shell pose from tags on the barrel top and housing back; the forearm as an occluder (masked); rotator degrees from the console. With ideal optics and a 20 mm tag at 400 mm a tag's pose is about 0.011 mm lateral, 0.22 mm in depth and 0.03 degrees in tilt (`calc/fiducial-pose-error.mjs`); a marker cube 40 to 80 mm behind the nozzle gives 0.14 to 0.21 mm at the dot with two cameras at 500 mm (eyes-03); a real rig is 5 to 10 times worse than the ideal, so the dot, not the tag, is the precise thing.
- **Command:** nothing but the rotator speed (existing console).
- **Manual:** everything else: holding, aiming, firing, the wire.

## What was tried to break it

1. **"A frame camera sits above the tube, not beside it."** *Variant:* the frame over the bench. *Assumption:* overhead is the good place (my wave 1 reading, from the top camera in room-01). *Finding (eyes, wave 2, from `eyes-02` and `eyes-15`):* an overhead camera loses vertical sensitivity at the zenith (it cannot tell wall from plate) and only 29 % of the upper hemisphere both sees the dot and separates radial from vertical error; the good stations are 100 to 190 degrees round the tube from the station (beside, far side low). The operator's forearm costs 0 to 1 points of the dome behind the gun and 6 to 10 from the +Y side, and the beside and far-side presets never lose an eye at any operator side. *Change:* the frame's three cameras sit at 130, 170 and 205 degrees (up 45, 22 and 10 degrees), on the side away from the hand, with a left-hand and a right-hand preset; the scene (`room-08-observe-only-frame`) drives the operator round the tube: at 90 degrees (the +Y side) two of the three lose the dot, at every other side sampled all three keep it. *Leaves:* a real forearm, sleeve, head and the wire feeder; glare.
2. **Tags on a hand-held shell (eyes, wave 2).** *Assumption:* tags go anywhere on the shell. *Finding:* the hand covers the grip; on the barrel top and housing back they are seen; but the housing back is 230 mm from the dot, so at 520 mm the camera needs about 50 degrees of field of view to hold the dot and both tags (1920 px across 485 mm is 0.25 mm per pixel); at 26 degrees only the barrel tag is in frame (the scene's field-of-view slider). *Change:* tags on the barrel top and housing back, a wide camera or a second, tighter camera for the dot. *Leaves:* tag glare, and the umbilical and conduit that sit where tags want to be.
3. **During the bead the frame sees the process, not necessarily the dot (eyes, wave 2).** *Assumption:* one recording serves. *Finding:* whether the red dot stays on while the trigger is held is **[unknown]** (the manual does not say); the glow may saturate a camera set for a 0.3 mW dot. *Change:* two recordings; a melt-pool exposure with an ND filter sees melt against seam directly, which is the quantity that matters. *Leaves:* the filter, the exposure, and whether one sensor can do both.
4. **The frame is in the operator's way.** *Change:* it stands behind and above; the operator's arm and the wire feed keep their approach. *Leaves:* a person leaning on it: kinematic mounts and a stiff frame.

## Branches and combinations

The frame is the observation layer of every scene in this set; room-05 draws it as the cell frame and room-18 adds lamps to it. Combines eyes-15 (what the holder hides) and eyes-02 (where an eye can stand). In room-15 the frame is the table.

## Unresolved, questions for Derek

- Which side does Derek stand, and which hand holds the gun? (a left- and a right-hand preset otherwise)
- With the trigger held, is the red dot still visible? (one minute at the machine)
- What does the operator see that no camera would (the puddle)? Would recorded hand-welds be useful as training data?

## Assumptions

Camera field of view 50 degrees, 520 mm from the dot, 1920 px, corner noise 0.1 px, tag 20 mm: **[illustrative]**. Forearm a cylinder 76 mm across and 300 mm long leaving the grip base 20 degrees below horizontal: **[illustrative]**. Real-world factors: **[unknown]**.

## Sourcing pointers

None of my own; cameras are left to the eyes and trials explorers. 2020 extrusion (sourcing 12) is the frame.

## Scene

`scenes/room-08-observe-only-frame`

## Wave 2

- In `room-15-one-knob-table` the record of `use-08-flight-recorder` is nearly free: knob scale, rotator degrees, the lever switch of `room-14` (trigger time), and one camera. The frame there is the table.
