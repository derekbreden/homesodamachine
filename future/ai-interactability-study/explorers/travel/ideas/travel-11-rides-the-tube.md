# travel-11-rides-the-tube: the collar on the tube carries the gun

**Picture it.** A ring sits round the top of the tube on three small rollers on the tube's outer wall and three more resting on the rim. It does not turn with the tube: a light arm to the room stops it rotating, and that is all the room does. The gun's shell is bolted to the ring, so as the tube wobbles, the gun wobbles with it, and the corner stays put relative to the nozzle.

Scene: none yet. Idea only.

## The proposal

Change *who carries the gun*: the work, not the room. Position of the gun relative to the tube is then set by the tube itself (its outer wall for radial, its rim for vertical), so the runout (0.25 mm radial, 0.30 mm face **[repo]**) is cancelled by construction, with no stage. The room supplies only anti-rotation. This is `datum`'s territory viewed as an allocation: nothing moves under software control, the reference does the work.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the tube, through the rim rollers, into the nest and the rotator's ball race (adding the collar and gun weight to the 2 kg vessel).
- **Establishes position:** the tube's outer wall (radial and plan) and the rim (vertical).
- **Free:** the collar follows the tube's wobble in all directions except rotation. **Restrained:** by the anti-rotation arm, which must be soft in the radial and vertical directions and stiff in rotation (a flat flexure or a parallelogram).

## What software could command, observe, what stays manual

- **Commands:** none, except a vertical trim screw between collar and shell (hand or motor). **Observes:** nothing new. **Manual:** placing the collar, loading the tube.

## What was tried to break it

**1. The rim is not the seam.** *Conflict:* the plate sits 6.35 mm (nominal) below the rim, and the seat depth varies tube to tube (**[unknown]** by how much). A rim datum therefore carries the seat-depth variation into the dot. *Change:* a vertical trim between the collar and the shell (a screw or shim, per tube, or a motor). *Leaves:* variation, unknown.

**2. Outer wall versus the plate.** *Conflict:* the plate is a slip fit, about 0.005 in radial slip **[repo]**, so the seam can sit about 0.13 mm off the tube's own axis; the outer-wall rollers cancel the tube's wobble but not that offset. *Change:* a radial trim. *Leaves:* ovality: rollers on a 0.065 in wall follow its out-of-roundness twice per revolution, and the seam has its own shape.

**3. Load and wear.** *Conflict:* rollers on a thin wall and 316L; the collar's mass adds to a printed ball race sized for a vessel. *Change:* light collar; ball transfer units. *Leaves:* unknown wear and marking.

**4. Access.** *Conflict:* the collar sits round the rim where the gun, wire and camera also need access. *Leaves:* open.

## Branches and combinations

- **With travel-06:** the nest screws still reduce the eccentricity between the tube and the axis; the ring removes the remaining wobble.
- **With `datum`:** direct neighbour: the collar is a datum carried by the work.
- **The work contact for the laser interlock** could be the rollers instead of the copper shoe (the interlock needs a complete circuit through the work **[manual]** p. 19): not evaluated.

## Unresolved problems and questions for Derek

- Seat depth variation, ovality of the tubes (indicator readings on five tubes).
- Whether he would accept anything touching the tube during the weld.

## Assumptions

- Runout limits and plate slip **[repo]**; roller and collar mass, wear: **illustrative or unknown**.

## Sourcing pointers

None yet (ball transfer units, skate wheels: not searched).

## Scene id

None yet.

## Wave 2

The seat of this arrangement is worked in `travel-14-exact-crown` (branch of datum-03-rim-crown): pads or rockers that centre soft and lock, three rim pads, a wire-pair tether for the free axis in place of the anti-rotation arm; k equal pads pass out-of-round harmonics k-1 and k+1 at gain 1, so the radial win over an indicated tube is not established (`exchange/travel--on--datum-w2.md` section 1). The gun-carrying variants are `travel-14b-crown-cartridge` and `travel-16-radial-plane`.
