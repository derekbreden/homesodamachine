# room-18: the cabinet as a station

**Origin:** wave 3 new direction (the station around the arrangement), a branch of room-05 that answers eyes's remark that a cabinet is a designed light environment and adds what a closed box does to the air. **Scene:** `scenes/room-18-cabinet-station`. **Depth:** developed (the gas balance and the lamp geometry are computed; the light is geometry only).

## Picture it

room-05's cabinet with its drawer, dock, gun stage and two fixed cameras, plus: a fan and a 100 mm duct at the top over the gun, a low vent on the back wall and a make-up louvre low on the door; lamps chosen from a ring at camera A, two low side bars or a diffuse panel under the roof; two neoprene sleeves through the door at hand height. In the controls column a polar map shows, for camera A and the plate's mirror-like stainless, where a lamp would send its reflection.

## The proposal

Design the station around the two things the cabinet has to be, a laser enclosure and a room for a gas.

- **The box is the hood.** Extraction is sized to the argon, not the fume. At 18 L/min into a 342 L box (760 x 620 x 725 mm, illustrative), argon being 1.4 times as dense as air, a box that can only lose gas by displacement falls to 19.5 % oxygen in 1.3 minutes (well mixed). A 100 CFM fan (2,830 L/min) keeps the steady argon share at 0.6 % and the oxygen at 20.8 %, with about 8 changes of air a minute; the laser permit gains a "fan airflow proven" contact beside door, dock, seat, software and pedal (room-14). A low vent takes the settled layer; an oxygen sensor at floor level is the proposed observer.
- **A designed light environment.** Matte black interior, a red band-pass on the top camera, lamps software switches, one frame for gun, cameras and lamps. A lamp is placed where its plate reflection and the corner's double bounce do not land in the camera.
- **A hand port.** Two sleeves reach the nozzle (300 to 350 mm from the port centres) for a stuck wire, with the laser interlocked off and the sleeve as protected as the window.

## What carries, what locates, what is free

As room-05: the frame carries the gun stage, cameras, lamps, duct and fan; the drawer carries the rotator; the three-ball dock locates it. New: the fan is a switch (purple in the scene), the duct and vents are fixed, the sleeves are compliant.

## What software could command, observe, and what stays manual

- **Command:** drawer, gun stage X Y Z, rotator, fan on and off, lamps on and off.
- **Observe:** two cameras; dock, door and fan-airflow switches; an oxygen sensor low in the box (proposed); step counts. The interlock (drawer seated, door closed, fan airflow proven) is a state machine.
- **Manual:** loading, seating, indicating and tacking with the drawer out; a stuck wire through the sleeve; setting up gun, cameras and lamps once.

## What was tried to break it

1. **"A cabinet is a designed light environment; the stainless throws the red dot's reflection" (eyes, wave 2).** *Variant:* camera A at elevation 52.5 and azimuth 141 degrees from the station, the plate a mirror. *Assumption:* light beside the camera lights the corner. *Finding:* for a mirror plate the reflection of a lamp reaches a camera when the lamp sits at the opposite azimuth at the same elevation (here azimuth 321, elevation 52.5); the corner is a dihedral mirror whose double bounce goes back to a lamp at the camera's direction mirrored across the section plane (azimuth 219), not beside the camera. So a ring light at camera A lights neither the plate glare nor the corner band, a diffuse panel that begins below about 60 degrees elevation glares on the plate, and low side bars give raking light without a specular reflection. *Change:* the map and its verdicts. *Leaves:* everything photometric: how specular real brushed 316L is (8 degrees of spread is a guess), the red dot's own reflection, the melt's glow; the answer is a phone photograph of the corner under a phone flashlight (eyes-06b).
2. **"The box is sealed for the laser."** *Finding:* 1.3 minutes to 19.5 % oxygen at 18 L/min in 342 L, well mixed [derived, ordinary gas data; 19.5 % is the common oxygen-deficiency threshold]. *Change:* extraction of at least 10 to 20 times the argon flow (100 CFM is 157 times), a low vent and a make-up louvre. *Leaves:* stratification makes the floor layer worse than the average; the number is a model; nothing here is a safety design and the laser's own interlocks, OD-rated glazing and a competent review stand.
3. **"Camera B is blocked by the gun" (eyes, wave 2).** *Finding:* the drawn test used the kit's default 0.8 mm end tolerance on a point on the axis of a thin part, which hides it behind its own skin; with eps 3 camera B reads the tip over the rim from the far side. The profile station eyes drew lies on the line the drawer travels along: the tube would reach a camera at y = 330 mm. *Change:* room-05's scene corrected; both stations offered. *Leaves:* whether the wire tip crosses B's view.
4. **"Reach in."** *Finding:* the two ports are 304 and 348 mm from the nozzle tip in the scene. *Leaves:* seeing the nozzle through a sleeve (it is not possible: the window and camera B are the eyes), and whether the sleeve is protected to the OD of the window.

## Branches and combinations

Combines room-05 with eyes-06b (the corner mirror). The permit chain of room-14 gains the fan contact. The same box holds room-17's tilting plate on a fixed base in place of the drawer.

## Unresolved problems, and questions that need Derek's observation

- One phone photograph of the plate corner, stainless as it is, with a flashlight beside the phone and from the side.
- Fan, duct run, make-up path and where the outlet goes; an oxygen monitor's response in a box with fume.
- Everything room-05 lists: dock hardware, motorised drawer, box size and place, the second closure's service bore.

## Assumptions

Box 760 x 620 x 725 mm inside, duct, fan and lamp places: **[illustrative]**. Argon flow 15 to 20 L/min: **[manual]** p. 19. Densities and 1 CFM = 28.3 L/min: ordinary data. Gas balance V dc/dt = Q - c E with outflow the larger of the fan flow and the argon flow: **[derived]**. Glare map: pure geometry **[derived]**; spread **[illustrative]**.

## Sourcing pointers

`sourcing/room.md` entries 20 (inline duct fan), 21 (four-gas monitor with O2), 24 (gloves for the sleeves), 14 (OD6+ window).

## Scene

`scenes/room-18-cabinet-station`
