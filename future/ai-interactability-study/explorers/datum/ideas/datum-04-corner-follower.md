# datum-04-corner-follower: feel the seam, and the tacks announce themselves

Scene: `scenes/datum-04-corner-follower/index.html`. Depth: developed. Origin: swarm.

## Picture it

A small ball, a millimetre or two in radius, sits in the inside corner and is held there by a light spring arm hanging from the gun's shell. A ball in a right-angle corner has its centre a ball-radius from each surface, so where the ball is against the gun *is* where the corner is against the gun. It rides a few millimetres ahead of the dot, where the wall is still cold. As the tube turns the ball lifts over each tack, and the height trace shows the tacks as spikes.

## The proposal

Touch the seam instead of looking at it. A leading feeler reports the corner's radial and vertical position in the gun's frame with no line of sight into the pocket. The circle's own curvature (s squared over 2r, 0.81 mm at a 10 mm lead) is known and subtracted. What is left is the dot's offset plus the lead times the gun's yaw against the seam tangent; two feelers at different leads solve for both. The tacks come free: each is a bump in the height reading, so "carry the bead about 20 degrees past the first tack" [repo] can be counted from the reading.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** none of the gun's. The arm hangs from the printed shell; a light spring keeps the ball in the corner.
- **Position:** the corner itself, at a lead ahead of the dot; the arm's pivot against the dot is calibrated once.
- **Free / restrained / driven:** the ball is free to follow the corner, restrained by the spring; nothing driven by the follower itself. Its reading can drive a fine stage (datum-02, datum-03) or the rotator.

## What software could command, observe, and what stays manual

- **Command:** nothing by the follower; the rotator angle (existing).
- **Observe:** ball centre (r, z) at each lead; tack angles from the height trace; gun yaw only with two leads. Blind: heat or spatter on the arm.
- **Manual:** placing the arm in the corner, calibrating it against the dot, moving it out of the way before the last overlap.

## What was tried to break it

Numbers from `calc/follower_leads.py` (`calc/follower_leads.out`); noise illustrative.

1. **One leading feeler with unknown yaw.** *Conflict:* the estimate carries lead times tan(yaw): 0.175 mm at a 10 mm lead and 1 degree; 0.105 mm at 6 mm. *Assumption:* the gun is tangent. *Change:* a shorter lead, or a second lead: with two leading feelers (6 and 15 mm) the offset error is 1.8 times the noise and the yaw error 0.18 degrees at 0.02 mm noise. *Uncertain:* real noise.
2. **The feeler and the wire are both ahead.**
   - *Conflict:* the wire arrives on the same side as the barrel. In the side view the wire leaves the dot at an elevation angle. At 30 degrees a 6 mm lead has 0.08 mm to spare, at 20 degrees a 6 mm lead has none; with a 1.5 mm ball the clearance is lead times tan(elevation) minus the ball diameter minus the wire radius (0.38 mm [repo]). The scene shows a LIMIT badge when the ball meets the corridor.
   - *Change:* a longer lead (more curvature term, more yaw error), a steeper wire, or an arm that comes from the plate side.
   - *Uncertain:* the wire's true approach angle and guide position; the drawn ones are the kit's proxy.
3. **Symmetric pair (lead and trail) to cancel yaw and curvature.** *Conflict:* the trailing feeler rides the fresh, hot, rough bead. *What the scene shows:* modelled as four times the noise, the pair gives 0.041 mm offset error and 0.30 degrees yaw error against 0.035 / 0.13 for two leading leads at 8 and 20 mm. It does not beat two leading feelers. *Uncertain:* bead roughness and heat.
4. **A ball reads the highest thing under it.** *What the scene shows:* a tack lifts the ball. *Change:* use the bumps, and take a median for the seam estimate.
5. **The 0.13 mm plate slip gap.** *Left standing:* a ball far larger than the gap should ride over it; nobody has looked.

### Wave 3 note

`datum-23-wall-clip` is this idea with a body: a stiff hook on the gun's nose whose roller on the bore wall, a few millimetres ahead of the dot, is the gun's radial position, instead of a feeler whose deflection a fine stage must act on. It follows the wall's shape at a lead (a passive clip cannot delay the reading; a fine stage behind it can). `travel`'s named combination, the follower's two-lead yaw estimate nulled by tangent travel of the work (a plan-angle stage with a 1/r reduction, 1.08 mm of tangent travel per degree), gives the feeler an actuator for its second output; not drawn.

## Branches and combinations

- **Feeler with the seam signature** (datum-02): the follower supplies the dry-rotation samples and can close the loop in the weld rotation.
- **Feeler on the crown** (datum-03): the crown's stage drives to the feeler's estimate.
- **Wire-touch or stylus corner finding** (datum-07) is the same physics with the tip driven instead of dragged.

## Unresolved problems and questions for Derek

- How the arm reaches the corner past the nozzle and wire, what it is made of near the weld, and whether it survives the last overlap.
- The sensor on the arm. Number and size of the tacks; the wire's elevation angle in use.

## Assumptions

- Circle radius 61.85 mm [repo][derived]; wire 0.030 in [repo] = 0.76 mm [derived]. Wire elevation, guide length 40 mm (kit proxy), ball radius, noise, gun yaw, dot offset, tack size, hot-bead multiplier: illustrative. Face runout amplitude 0.15 mm is half the 0.30 mm limit [repo].

## Sourcing pointers

`sourcing/datum.md`: linear Hall sensors (SS49E class, Prime, "100+ bought in past month" on the first card) for a magnet-and-spring feeler; nothing else.

## Scene id

`datum-04-corner-follower`.
