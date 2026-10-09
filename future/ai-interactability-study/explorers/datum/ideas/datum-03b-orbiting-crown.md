# datum-03b-orbiting-crown: the tube holds still and the gun goes around it

Scene: `scenes/datum-03b-orbiting-crown/index.html`. Depth: developed. Origin: branch of datum-03-rim-crown. Read `datum-03-rim-crown.md` first; this file only records what changes.

## Picture it

The same crown on the same tube, but the tube sits on a plain stand and does not turn. The lower ring is fixed to the tube and carries a ring gear; the upper ring, boom, gun and counterweight are driven round it by a small motor and pinion on the upper ring. The dark umbilical follows the gun round: either hanging from a fixed hook over the tube axis, or trailing behind the gun and laying itself on a big ring track.

## The proposal

Swap which body moves. Only the relative rotation between gun and tube matters, so hold the tube still (a plain stand and clamp; no turntable, belt, ball race or motor tower) and drive the gun assembly around it. Gun-to-corner pose is the same at every angle. The one thing this changes for pose is that the rotator's own runout disappears (the tube is not turning on a printed race); the crown's own ball race and ring gear add theirs (not modelled).

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** as in datum-03, plus the drive motor (0.35 kg, illustrative) at the ring's edge. There is no tether: the ring is free to turn and the motor turns it.
- **Position:** rim top and outside wall locate the lower ring; the plunger sets fine height. The ring angle is set by the drive's step count.
- **Free / restrained / driven:** the ring's rotation is *driven*; the tube is restrained by the stand and clamp; vertical stage driven (proposed).

## What software could command, observe, and what stays manual

- **Command:** ring drive angle and speed (7.4 deg/s at 8 mm/s bead speed [derived]; the rotator's 5-15 mm/s window [repo] would have to be reproduced), vertical stage.
- **Observe:** ring angle from the step count (no encoder), plunger reading. Nothing observes the dot, nor twist or wrap in any line.
- **Manual:** seating the crown, the routing and support of the umbilical, wire conduit and gas hose, unwinding after each weld with the laser off.

## What was tried to break it

1. **Maypole (fixed hook on the axis).**
   - *Conflict:* the gun's cable leaves the grip base pointing away from the axis. To reach a hook above the axis the cable has to U-turn: the scene reports a bend radius of about 16 mm against the fibre's 350 mm emitting limit [manual p. 20].
   - *Assumption:* a cable hanging from above just swings with the gun.
   - *What else:* with the top end fixed on the axis, the cable's twist about its own axis grows with the orbit angle: 380 degrees for one weld. The manual says twisting the fibre is strictly forbidden [manual p. 20] and gives no number; the 15-degree threshold in the scene is illustrative.
   - *Uncertain:* no rotary joint for a fibre of this power is known to me.
2. **Trailing wrap on a ring track.**
   - *Conflict:* a cable laid flat behind the gun cannot twist, so the wrap is torsion-free. But it leaves the grip base radially outward and has to turn onto a circle without breaking 350 mm bend radius. Scene numbers for the proxy pose: bend 262 mm at a 700 mm track, 373 mm at 1000 mm; length for 380 degrees 5.6 m at 700 mm and 8.0 m at 1000 mm, against a 5 m fibre.
   - *Change:* none found inside the 5 m. A different gun roll or pitch changes the exit direction and the numbers; that was not explored.
   - *Uncertain:* the wire conduit and gas hose share the path and are stiffer together.
3. **The drive.** *Left standing:* tooth form, backlash, deadman and the turned-so-far readout that the rotator controller provides today [repo]; the motor's own cable is another line that must follow the ring.
4. **What did not break:** pose. Seat-depth, tilt and OD-offset terms are the same as datum-03. The rotator's belt, race and turntable are simply not needed.

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 4)

5. **The exit direction is not the fix; a weld that can go either way round is.** *Conflict (travel):* I left "a different gun roll or pitch changes the exit direction and the numbers" unexplored, hoping the wrap would fit. *Assumption:* the exit direction is what decides the cable. *What travel found* (`travel/calc/09`, `scenes/travel-16-radial-plane`): in the tangent pose (A) and the radial-plane pose (B) the fibre still leaves radially outward and needs a turn of 142 to 155 degrees before it can run round the tube at 350 mm; a route with every bend at 350 mm needs 5.6 m (A) and 5.8 m (B) for 380 degrees, against a 5 m fibre. What does fit: two halves of 190 degrees from the first tack, 3.25 to 3.4 m with every bend at 350 mm by construction. *What the change alters:* the scene has `The weld goes round: two halves` (the ring stops at 190 degrees). At a 700 mm track my scene's wrap uses 3.25 m for 190 degrees, but its simple lead-in still bends to 145 mm: travel's route does not. *Leaves uncertain:* two halves need no wire at the gun (a preplaced filler ring, `datum-09`, or a guide carried by the ring), two starts and two stops with a double-crater joint, and the cable re-laid as its mirror image between halves; the real exit direction.

## Branches and combinations

- Parent: datum-03-rim-crown.
- The problem it exposes (a line that must follow a circle without twisting) belongs to every arrangement where the gun orbits; it is the price of the "gun goes round" assignment of motion.

## Unresolved problems and questions for Derek

- Can the fibre be wrapped (not twisted) at 350 mm? Is there a way to rotate the laser unit end or a rotary joint?
- Is a plain stand acceptable for the tube, and is there room for a track of about a metre radius around the station?
- What would the wire feeder do over 380 degrees?

## Assumptions

- Same as datum-03; the drive motor mass 0.35 kg is illustrative. Fibre 5 m, 350/240 mm bend radii, no twisting: [manual p. 20]. The scene's twist rule (twist equals orbit angle with a fixed top; zero when laid flat) is a geometric argument, not a cable model.

## Sourcing pointers

Same as datum-03. No rotary fibre joint sourced.

## Scene id

`datum-03b-orbiting-crown`.
