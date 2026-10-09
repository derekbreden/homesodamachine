# datum-21-mates-on-the-tube: what each feature of the tube lets a part do, and what it costs

Scene: `scenes/datum-21-mates-on-the-tube/index.html` (a lens on a drawn arrangement). Depth: developed. Origin: swarm, wave 3 (the region "shells, seats and interfaces formed by the work"). Numbers: `calc/mate_harmonics.js` (`mate_harmonics.out`).

## Picture it

The tube, see-through, with the gun in its opening pose. A radio picks one feature of the tube and the part that mates it appears: a ring on three rim pads; a skirt with three soft rockers on the outside; three spring fingers in the bore; three set-screw feet on the plate face; a post on two pins in the plate's ports; the first plate's ports from below (only after the flip); a hook on the gun that straddles the wall at the station. A card lists which of the six freedoms it fixes, whether it follows the tube's motion or its shape, what it costs in fit and access, what is unknown per tube, and what the flip changes. A chart shows what four references pass to the gun: a room-fixed gun on an indicated tube, a ring on the outside, a ring on the bore, a roller on the bore at the station.

## The proposal

Ask of every part that could touch the tube: which feature, which freedoms, what it follows. Two findings organise the region.

**A mate on the whole circle follows the tube's motion and none of its shape.** A ring, skirt or set of fingers rigid on the tube follows the tube's rigid offset and tilt from the rotation axis (harmonic 1 of the table angle), so the runout a room-fixed gun sees is not seen. It cannot follow ovality, three-lobing or wall eccentricity, and its k equal pads or fingers pass out-of-round harmonics k-1 and k+1 at gain 1 into the ring's own centre (three pads pass the ovality, four pass the three-lobing, six reject 2 to 4; `travel/calc/08`). So a three-pad ring on an oval tube adds a first harmonic as large as the ovality (`mate_harmonics.out` E: 0.114 mm rms against 0.085 for the room-fixed gun on a tube oval to the rig's limit). The bore reference removes exactly the wall eccentricity and nothing else (D: 0.058 against 0.121 when the eccentricity is 0.15). **A mate at the station reads the shape too**, up to the phase its lead costs: 2 sin(n s / 2R) of harmonic n (0.32 of the ovality at 10 mm, 0.57 at 18); on the default tube 0.028 mm rms against 0.10 to 0.13 for the others. The chart is the reason to care which feature is mated.

**The crown's radial win is the wobble left after indicating minus what its seat passes.** The wall eccentricity is common to a room-fixed gun and to every ring on the outside (it is the corner's own offset from the outside's centre), so it raises the floor of both and cannot cancel the crown's win. For tubes the rig would accept (the OD indicator reads 0.25 TIR at most, so w and the lobes together are at most about 0.125), the crown wins at most 0.05 mm rms and loses up to 0.03 with three pads on an oval tube; four pads or rockers are at worst neutral (`mate_harmonics.out` G). So radial is a wash inside a few hundredths of a millimetre; the crown's lasting case is height, and height needs the plate: the crown follows the rim, the corner is on the plate, and the slip fit does not square the plate (`datum-22`).

## What carries the loads, what establishes position, what is free or restrained

Not a support proposal: each mate is drawn as a locating part. What carries weight is `datum-16`'s question. The atlas, one row per mate (fixed / weak / free):

| mate | fixes | follows | the cost |
|---|---|---|---|
| ring on the rim, three pads | z, tilt x, tilt y | motion; rim height through the pads | flat 1.65 mm rim, deburred; ring at r >= 62.2 is clear of the nozzle |
| skirt with rockers on the outside | x, y; tilts weakly | motion; lobes k-1, k+1 | OD tolerance and out-of-round; soft to centre then lock; the other end is a fresh draw |
| three fingers in the bore | x, y | motion; bore lobes k-1, k+1; removes eccentricity | in the beam and nozzle pocket: a finger that turns with the tube meets the beam at the station (drawn clash test): seating only, then retract |
| three feet on the plate face | z, tilt x, tilt y | the plate's own | temporary, 10 mm from a tack; makes seat depth and tilt |
| post on two ports | x, y, turn (mod 180 degrees) | the plate's own | cone in the 82 degree countersink, one pin in a slot; the thread untouched; plate slip 0.127 mm is the radial term |
| plate 1's ports from below | x, y, turn of the first plate | the first plate's own | closure 2 only; fixes the tube's bottom end, not the working end 146 mm above |
| hook with a bore roller at the station | x (radial), z (rim wheel) | motion and shape up to the lead | on the arriving side, 1.5 to 2 mm of gap at 6 to 10 mm in the kit proxy; heat and spatter |

**The flip.** Closure 1 has a bare tube (the bore is open below the plate, the far end is open, the float rod hangs from the plate). Closure 2 stands on the first plate: the float rod and the float stand up inside, plate 1's ports are reachable from below through the 90 mm service bore, the ring that served closure 1 moves to the other rim (whose outside is a fresh draw of everything), and a crown or presetter that stays on its tube serves one closure.

## What software could command, observe, and what stays manual

Nothing is commanded or observed beyond the rotator. The point is which measurements would make a mate worth building: five tubes, eight positions each, outside diameter by calipers and wall thickness by ball micrometer; rim flatness on a plate with a feeler gauge; a look at the bore for a longitudinal weld seam.

## What was tried to break it

1. **The atlas is illustrative in its amplitudes.** *Left standing:* nobody knows the real ovality, eccentricity or lobing. Every bar in the chart moves with them; the *shape* of the finding (motion versus shape, the lead's cost) does not.
2. **A mast on the ports as a gun carrier** (`datum-08`, tried again). *What the atlas shows:* the plate face gives height and tilt directly and the ports the plate's centre, but only the plate's: the slip gap round the plate (0.127 mm) is the radial term, and a mast on the axis puts the gun on a boom 55 to 120 mm long. As a carrier it loses to the ring; as a temporary part that places the plate it is the plug of `datum-22`. *Kept as:* the "ports" row.
3. **Threaded studs in the ports.** *What breaks:* galling of taper threads in 316L, and the ports are used again for the elbows. *Replaced by:* a cone collar in the countersink.
4. **Plate 1's ports from below.** *What the atlas shows:* it centres the tube's bottom end on the turntable axis by the welded plate, which is not where the runout is (146 mm up, through the tube's straightness and the nest's tilt). *Kept as:* a row, not an idea.
5. **A nose skid or shoe on the rim** (`borrowed-07`, `trials-21`). *What the atlas shows:* a rim contact at the station is one row of the hook (a wheel, since a dry skid drags 1.25 N at 5 N of load), not a separate mate; height at the station follows the local rim and not the plate.
6. **An index ring, sketch only.** A ring on the rim that carries an angle scale (a printed slit ring or a ring of magnets) read by a fixed sensor gives the tube's own angle at the gun instead of the rotator's step count: the replay of `datum-02` would be keyed to the work, so a tube that slips in the nest or is re-seated no longer breaks it, and the plate's port axis (mod 180 degrees, `datum-19`) sets the index. *Not drawn:* a photointerrupter and a slit ring are ordinary parts; the open question is whether the tube slips in the nest at all.

## Branches and combinations

- Feeds `datum-22-setting-ring` (rim + outside + plate face + ports), `datum-23-wall-clip` (the wall at the station), `datum-03` (the seat control), `datum-01` (what the plate seating does to the chain).
- A lens, not an arrangement: its scene-meta tags say so.

## Unresolved problems and questions for Derek

- Five tubes, eight positions each: outside diameter (calipers) and wall thickness (ball micrometer, or calipers on the cut end); rim flatness on a plate with a feeler gauge; is there a longitudinal weld seam on the bore and can a fingernail feel it; may anything touch the finished tube's rim, bore or outside.
- The port centres against the plate edge (laser-cut position) and the plate's slip gap round its edge.

## Assumptions

- Wall harmonics 1 to 4 with fixed phases; outside lobes equal the bore's; equal-force pads and fingers, rigid locked ring (`travel/calc/08`); the kit's proxy gun. All amplitudes illustrative.

## Sourcing pointers

`sourcing/datum.md` (wave 3): the iGaging caliper class for the survey.

## Scene id

`datum-21-mates-on-the-tube`.
