# travel-12-heads-own-stage: the head's own fine stage

**Picture it.** Inside the gun a mirror already sweeps the beam a couple of millimetres across the joint at 80 Hz. If the laser's software could offset the centre of that sweep, the head would have a fine radial stage with no moving mass at all: plus or minus a millimetre, micron resolution, kilohertz bandwidth, commanded over the port the laser unit already has for "PC-based supervisory software". The gun would not move.

Scene: none. Idea only, held with a question mark.

## The proposal

Look for a stage that already exists before adding one. The X1 Pro has a wobble (swing width 2 mm at 80 Hz in Derek's recorded settings **[repo]**; the manual's example is 2 mm at 10 Hz **[manual]** p. 13), a "red light alignment" adjustment with left and right buttons **[manual]** pp. 25, 39, and an RS232 port ("PC-based supervisory software") and a DB25 port ("PLC integration") **[manual]** p. 16. In the kit's reference scene the sweep is along the gun's local x, which at zero plan rotation is the radial direction, the direction in which runout and seam offset matter.

## What carries the loads, what establishes position, what is free or restrained

Nothing new carries anything. Position: the head's own calibration of where the beam lands relative to the nozzle; the red dot is a separate pilot.

## What software could command, observe, what stays manual

- **Commands (if they exist):** swing width, swing centre offset. Whether the RS232 port exposes them is **[unknown]**.
- **Observes:** nothing new. **Manual:** everything else.

## What was tried to break it

**1. The red light is not the beam.** *Conflict:* a third-party explainer for handheld guns (not this manufacturer) says the red light comes from a separate diode aligned parallel to the beam, and that the software offset moves *only the red light, not the welding beam* (`sourcing/travel.md`, non-Amazon notes; not verified for the X1 Pro). *Change:* the "red light alignment" screen is then a calibration of the pilot to the beam, not a stage. *Leaves:* useful anyway: it means the dot-to-melt offset is a setting that a dry-run-and-coupon procedure could calibrate, which matters to every arrangement in the study.

**2. The sweep centre.** *Conflict:* no source read says the swing can be offset, only its width and frequency. *Change:* none available. *Leaves:* a question that costs Derek two minutes at the touch screen, and maybe a question to the manufacturer (not contacted).

**3. It is one axis.** Even if it existed it moves the beam in the sweep direction only, over about a millimetre: a trim for radial error, not a replacement for anything else.

## Branches and combinations

- **With travel-02:** if it existed, the follow stage of the cascade would be this: no moving mass, no cable pull.
- **With `datum` and `eyes`:** a coupon test that sets the red-light offset to the real melt position.

## Unresolved problems and questions for Derek

- On the touch screen: is there any setting that shifts the swing off-centre? Does the swing width change what the red light does?
- Does the RS232 port document commands for swing parameters?
- What is the dot-to-melt offset at working standoff, and does it change with standoff?

## Assumptions

- Kit reference scene: sweep along local x, 2 mm. Manual pages as cited. Everything about offset capability: **[unknown]**.

## Sourcing pointers

`sourcing/travel.md`: XLaserlab product page (gun weight and control not stated); the explainer on red-light behaviour.

## Scene id

None.

## Wave 2

The same idea as `datum-13-head-swing-centre` and `borrowed-06-swing-offset`: three explorers, one open question. One two-minute look at the touch screen (is there any way to offset the swing centre, does the red light move with it) serves all three.
