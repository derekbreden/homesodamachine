# travel-14-exact-crown: soft to centre, locked to hold (a repair of the crown's seat)

Scene: `scenes/travel-14-exact-crown`. Origin: branch of `datum-03-rim-crown` (exchange wave 2, `exchange/travel--on--datum-w2.md` section 1). Depth: developed. Numbers: `calc/08-crown-seat.mjs` (`calc/08-crown-seat.out`). Framing: split the travel; which element locates, which carries, which is free.

## Picture it

Seen from above: the tube's outside, slightly out of round, with a ring around it. Three small rockers ride on the outside, each with two pads, and after the ring has settled a cam or three set screws lock them. On the rim the ring rests on three fixed pads, not a full annulus. Round the ring a pair of steel wires is wrapped and pre-tensioned, running to two posts: they hold the ring against turning about the tube axis, stiffly, and hold nothing else. The gun rides on the ring as in datum-03 and follows the ring's centre.

## The proposal

datum-03 centres a ring on the outside of the tube and lets the gun follow it. In the scene the ring sits exactly on the outside diameter; in the hardware the ring has a clearance and something has to take it up, and that something decides the crown's radial error. Four facts, all from `calc/08`:

1. **A ring on a plain clearance fit is a one-point follower.** With a steady sideways pull it rides the tube at the loaded point, so it follows the whole local out-of-round; a change of pull direction moves it by the full clearance (datum-01 charges 0.20 mm as +-0.10).
2. **k equal pads pass out-of-round harmonics k-1 and k+1 at gain 1 and reject the rest.** Three pads pass ovality (n=2) at unity and reject three-lobing; four pads reject ovality and pass three-lobing; six reject n=2 to 4. Three rockers each averaging a pair at +-45 degrees reject n=2 and 3, pass n=5 at 1 and magnify n=4 to 1.41. A rigid V magnifies ovality (1.0 to 1.7 by angle, 5.4 at 80 degrees). n=1, the offset of the outside from the bore (wall thickness), passes every seat at gain 1: the ring cannot know it.
3. **A pad soft enough to take up the outside-diameter spread is as stiff as the ring.** A pad must stay between about 2 and 20 N over 0.36 mm of spread (illustrative: +-0.127 mm OD tolerance plus 0.10 mm out-of-round): 50 N/mm at most. Three of them are 75 N/mm; 3 N sideways moves the ring 0.04 mm, 1 N of change 0.013 mm; a 1 N/mm cord-class pad 0.67 mm per newton. Lock the pads after they settle (a cam, three set screws): the ring keeps the centre the soft pads found and is stiff (500 N/mm per pad assumed: 0.004 mm for 3 N). That is `travel-05b-soft-drive-hard-lock` read as a seat.
4. **The free axis is where a stiff element costs nothing at the seam, but its reaction is a force.** Turning about the tube axis does not move the dot. datum-03 leaves it to two soft cords (1 N/mm each): 3.5 degrees at 3 N, 17 degrees at 0.2 N/mm. A tab tether (two cords or a rod to one tab at 76 mm radius) reacts the 233 mm-arm drag torque as a net force 3.07 times the drag into the ring seat. A pre-tensioned wire pair wrapped on the ring (two equal and opposite tangential pulls) reacts a pure couple, is about 900 times stiffer than the cords (0.00 degrees at 3 N), and one strain-gauged wire reads the drag torque nobody has measured.

Vertical: a full annulus on the rim rests on the three highest spots it finds and, with a fourth, has two stable seatings. Three pads at fixed clock give one repeatable plane per tube. Rim flatness f gives a once-per-revolution vertical error up to about f (rough bound; `calc/08` D).

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the rim (three fixed pads) carries ring, yoke or boom, gun. The wire pair carries only torque about the axis.
- **Establishes position:** the outside of the tube through pads that centre and then lock (radial); three rim pads (vertical). n=1 and seat depth stay unknown to the seat.
- **Free / restrained / driven:** rotation about the tube axis is restrained by the wire pair (stiff, no effect on the seam); the pads are locked by hand at seating; nothing is driven by software.

## What software could command, observe, and what stays manual

- **Command:** nothing in the seat (the lock is a hand action). The rotator as in datum-03.
- **Observe:** ring azimuth (known by construction with the wire pair); the drag torque from a strain gauge on one wire (an HX711-class amplifier, `sourcing/travel.md` 21). Blind: the ring's radial float and centre error; the dot.
- **Manual:** seating the crown, letting the pads settle, locking, a one-time radial trim of the gun on the boom.

## What was tried to break it

1. **Assumption: the clearance is a random spread.** *What the scene shows:* it is a follower under load (see 1 above). *Change:* pads. *Leaves:* real clearance and pull direction.
2. **Assumption: three pads centre the ring.** *What the numbers say:* they pass ovality at gain 1, so with an ovality e the ring's radial error is e. *Change:* six pads or rockers at 45 degrees. *Leaves:* the tube's real out-of-round (unknown); n=1.
3. **Assumption: soft pads are fine because the cable pulls only a newton or so.** *What the numbers say:* 40 N/mm pads give 60 N/mm, which is 0.017 mm per newton of change; a plunger of the off-the-shelf class (12 N end force over a stroke of a millimetre or two) is well below that. *Change:* lock after settling. *Leaves:* a locked ring on a tube that grows 0.03 to 0.06 mm when it heats (the lock would have to yield or the pad be a spring flat that only stiffens sideways).
4. **Assumption: the tether only has to stop wandering.** *What the scene shows:* 3.5 degrees is 3.7 mm of seam at the default, 17 degrees at 0.2 N/mm cords; a tab tether triples the sideways load on the seat. *Change:* the wire pair. *Leaves:* pretension over a lap; how the wires wrap and where they anchor.
5. **The plunger is on the ring, not the gun.** In the scene it sits on the non-rotating ring 22 degrees from the dot (23.8 mm of arc, 3.0 s at 8 mm/s), so the loop closes on plate-versus-ring and excludes the boom and gun shell; the 1x tilt term arrives phase-shifted by 22 degrees (0.038 mm of a 0.10 mm term) unless the table is delayed 3 s. The lug on the barrel middle keeps the lever from the gun's single attachment to the dot at 93 mm (1.62 mm per degree, `calc/01`): 0.05 degree of clamp creep is 0.08 mm.

**Wave 3 entry, from use's exchange (sections 2 and 3).** **The lock is a handover with a shift (use).** *Conflict:* the scene's lock toggle added stiffness and no closing shift, and the hand trim on the boom came before it; the lock is the last handover. *Assumption behind it:* a lock only stiffens. *What the change alters:* a closing-shift slider adds a constant to the error at the station when the pads lock, with a badge that a look after the lock is needed; the relock loop of `travel-05b` (81 % of closures inside a +-0.10 mm window with no look after a 0.05 mm shift, 95 % with one) applies. *What it leaves uncertain:* the real shift and its mean; whether a cam pushes to one side (learnable) or pinches (scatter).

## Branches and combinations

- `travel-14b-crown-cartridge`: the crown stays on its tube from the presetter; the gun docks.
- With `travel-16-radial-plane`: no counterweight, no ring gap; the seat then carries a lighter, nearer load.
- With `datum-04` or `datum-07`/`travel-15`: the n=1 term is what a measurement has to take out; a radial slide or a touch at the station.
- With `travel-11-rides-the-tube` (my sketch): this is its seat, with the anti-rotation arm replaced by the wire pair.

## Unresolved problems and questions for Derek

- **Questions that need Derek's observation:** five tubes, eight positions each, OD by calipers and wall thickness by ball micrometer or the calipers on the cut end: what are n=2 and n=1? Rim flatness on a surface plate with a feeler gauge. The gun's weight and the umbilical's pull and its direction at the exit.
- Heat and spatter on pads near the pocket; whether a ring may touch the tube while the plate is only tacked.

## Assumptions

- Outside diameter 127 mm, bore 123.70 mm **[repo]**; drag arm 233 mm and tether radius 76 mm from datum-03's scene; lobe amplitude 0.10 mm, OD-to-bore offset 0.08 mm, spring rates, lock stiffness 500 N/mm per pad, wire stiffness (1.5 mm rope, 100 GPa effective, 1.1 mm^2, 120 mm): **illustrative**. Rig-doc runout 0.25 mm TIR **[repo]**.

## Sourcing pointers

`sourcing/travel.md`: detent plungers (19: light springs), 1/16 in 304 wire rope with crimps (20), load-cell amplifier (21).

## Scene id

`travel-14-exact-crown`
