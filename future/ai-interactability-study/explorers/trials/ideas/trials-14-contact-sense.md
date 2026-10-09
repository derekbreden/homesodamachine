# trials-14-contact-sense: the gun's own circuit as a touch probe

No scene. Everything here is a question with a cheap experiment behind it.

## Picture it

The laser emits only while a clip on the work and the gun form a complete circuit **[manual p.19]**. The rotator's copper shoe already supplies the work side **[repo]**. If touching the workpiece with the nozzle or the wire closes that circuit, then "in contact" is a signal the gun already produces, and the laser box's ready lamp (yellow: ready for emission, green: emitting, red: alarm **[manual p.15]**) might show it. A camera watching a lamp is a contact sensor that needs no wiring into the laser box.

## The proposal

Robotic welders find seams by touching the wire to the work and sensing the contact; this is the same idea with the laser box's circuit or a separate low-voltage sense on an insulated wire. The **wire tip is the real weld reference**, better than the red dot, which is only aligned to it. Touch the plate face (z) and the wall (r) with the wire tip at low speed and the corner is found in the wire's own coordinates within about the wire diameter (0.76 mm for .030 ER316L **[repo]**), and repeated touches average that down.

## Carries, locates, free

No support is proposed; the wire feed (a separate box with its own conduit **[Derek]**) advances the wire; the positioner moves the gun.

## Software

- Command: wire jog (the feeder has feed and retract buttons **[manual p.18]**; whether software can drive it is **[unknown]**).
- Observe: the ready lamp by camera; or a continuity reading on an isolated wire (own hardware).
- Manual: everything about the laser box's I/O; what the DB25 exposes is **[unknown]** (the RS232 pins are in the manual; the protocol and the DB25 map are not in the pages available **[manual p.16]**).

## Tried to break it

1. **Whether contact changes the lamp is unknown.** Cheap test: with the laser disabled and the clip on, touch the nozzle and the wire to the tube; watch the lamps. Leaves: the answer.
2. **Wire stiffness.** A 0.76 mm wire bends under contact; the tip deflects. Repair: touch at low feed, count a touch when the circuit closes, back off. Leaves: bend at the tip.
3. **Interlock.** Do not defeat any interlock; use a separate sense circuit if in doubt. Leaves: safety is Derek's.
4. **Wire is a consumable and a mess.** Each touch may stick. Leaves: the retract cycle handles it in the weld today **[repo]**.

5. **The wire and the dot are two probes of one corner, and nobody differenced them (from datum's exchange, wave 2, section 4; drawn as `datum-20-dot-and-wire`).** *Conflict, in this variant:* this idea says the wire tip is the real weld reference and finds the corner "within about the wire diameter"; `trials-03` finds the wall with the dot; the difference of the two readings on the same corner is the vector from the dot to the wire tip, the part of dot-versus-melt a dry run can reach without emitting. Three geometric facts this file lacked: (a) a straight wire lying along the tangent runs into a wall that curves away at 61.85 mm radius (the wall recedes y squared over 2R with tangent offset y): for 35 degrees of elevation, a tip 3 mm upstream and 0.3 mm of miss the wire needs at least 4.8 degrees of outward lean, and at zero lean the body is 0.77 mm inside the wall; (b) the tip moves along the wire's line, not along the seam: per millimetre of feed 0.57 mm in height, 0.09 radially, 0.81 along the seam, so each weld's cut or retract makes the vector something to re-measure at every start; (c) the wall touch is the tip's, at the tip's own tangent position (0.05 mm further out at 2.4 mm upstream). *Assumption behind it:* a wire touch is a point probe at the dot's place. *Answered and kept:* this idea file keeps the electrical probe and takes the vector as its output; the drawing stays with `datum-20`. The height half of the vector is the weaker reading (the spot-size curve is flat near focus), and a stylus touch in the same run reads it better (`datum-07`). *Leaves uncertain:* whether contact changes anything the laser box shows (the cheap test above), whether the feeder can be driven by software, and that the tip is where the wire is, not where the melt is. The mule could carry a wire stub with its own contact sense (`trials-06`).

## Combinations

Complements `trials-03-dot-touch-probe` (optical) and `trials-06-mule-gun` (a tip switch instead of a wire).

## Unresolved

Q: With the clip on and the laser disabled, does anything (lamp, beep, screen) change when the nozzle or the wire touches the tube?

## Assumptions

Manual and repo facts as cited; the rest **[unknown]**.
