# datum-08-port-pin-mast: two pins in the ports carry a mast on the plate

No scene (sketch). Depth: sketch. Origin: swarm. Branch of datum-03-rim-crown (same idea, carried by the plate instead of the rim).

## Picture it

Two pins drop into the plate's two 11.1 mm ports, 38.1 mm apart. A short mast rises from them along the tube axis and carries a hub above the rim; a boom from the hub reaches out to the gun. The datum is the plate itself: its centre, its clock angle (the port axis) and its face. Like the crown, the gun then follows the work's own wobble.

## The proposal

The plate is the part the joint belongs to, and it carries three features nothing else does: two ports at +/-0.750 in, a register hole on the perpendicular axis [repo], and a flat face. Pins in the ports give the plate's centre and clock; a shoulder on the plate face gives height with no seat-depth term. A bearing at the top of the mast keeps the boom non-rotating while the mast turns with the tube.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** the plate, through two 11.1 mm holes and a shoulder on its face. The plate is a slip fit tacked into the bore.
- **Position:** plate centre (0.127 mm radial play against the bore [repo], so the *radial* datum is worse than the wall's), plate clock, plate-face height (best available: no seat-depth term).
- **Free / restrained:** the mast is restrained by the pins and shoulder; the hub's rotation about the axis is free, tethered.

## What software could command, observe, and what stays manual

As datum-03: vertical stage optional (height is already the plate's); no plunger needed. It could observe the plate clock by reading a mark on the hub against the ports. Manual: seating the pins.

## What was tried to break it

1. **The ports are the purge path.** *Conflict:* pins block them. *Assumption:* the ports are free during the weld. *Change:* hollow pins that pass gas, or pins only in the port that is not used for purge (only the *lower* plate's ports carry purge in the second closure [repo]; the plate being welded is the upper one). *Uncertain:* a hollow pin's fit in an 11.1 mm hole.
2. **The plate is only tacked.** *Conflict:* the gun's weight hangs from it. *What the numbers say* [calc/sketches.py]: with the gun 118 mm out and no counterweight (illustrative masses 0.6 to 1.65 kg) the overturning moment is 0.7 to 1.9 N.m; two pins 38.1 mm apart resist it with +/-18 to +/-50 N, and about the pin line itself the pins have no lever, so a 30 mm base on the plate face would carry +/-23 to +/-64 N. *Assumption:* the tacks hold that. *Change:* the counterweight (datum-03) brings the moment near zero. *Uncertain:* tack strength [unknown].
3. **Radial datum.** *What the datum-chain scene shows:* choosing "plate centre" for radial adds the plate's 0.127 mm slip as a term the wall reference does not have. *Change:* use the mast for height and clock only, and the crown or a wall pad for radial.
4. **The mast is in the corner's line of sight.** It stands inside the bore: nothing sees the corner from outside anyway, and the gun approaches over the rim; the boom must pass over the rim without hitting the nozzle and barrel.

## Branches and combinations

Parent datum-03. Best combined with a wall pad for radial and the mast for height. The mast could also carry the eddy or touch stage, at the axis.

## Unresolved problems and questions for Derek

- Tack count and strength. Whether the second closure's upper plate ports are open during the weld. Whether pins in the ports are acceptable to the purge.

## Assumptions

Ports, register hole, slip [repo]; gun mass, cg from the crown calc (proxy pose) illustrative.

## Sourcing pointers

None: printed hub, machined or printed pins; a bearing is the same class as datum-03's.

## Scene id

None. Represented in `datum-01-datum-chain` by the "Plate centre (ports)" radial option and the "Plate face" height option.
