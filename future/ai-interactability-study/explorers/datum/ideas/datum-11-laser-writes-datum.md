# datum-11-laser-writes-datum: a witness pass, and marks the laser leaves on the work

No scene (sketch). Depth: sketch. Origin: swarm.

## Picture it

Before the real weld, the laser itself is used as a pen. On a scrap L-shaped coupon (a straight inside corner in 316L) it fires short low-energy pulses at several standoffs and the marks are photographed against the corner: the *witness* of where the beam really lands compared with where the red dot is. Separately, a low-power scribe on the rim of a real tube can leave a ring of index ticks, so the tube carries an angle scale that came from the machine that will weld it.

## The proposal

Every position datum in this set ends at the *dot*, but the weld happens at the *melt*, and how closely the red dot sits on the melt position at working standoff is unknown [shared-context; manual pp. 25, 39 show a red-light alignment adjustment]. No reference on the work can remove that term (the datum-chain scene shows it is a floor in every option). Only a witness pass touches it. A pass on a coupon (or an L-shaped offcut in the same tube stock) gives the dot-to-melt offset as a function of standoff and orientation, once, and it can be repeated after any change to the head.

The ticks are a second use of the same trick: the marks give an along-seam angle datum that belongs to *this tube* and was written by the machine that welds it.

## What carries the loads, what establishes position, what is free or restrained

A coupon on any fixture; no support proposal. Position is established by the corner of the coupon and a scale.

## What software could command, observe, and what stays manual

Command: the laser's pulse parameters (through the RS232 or DB25 port if it allows, [manual p. 16], protocol unknown), the gun's fine axes across a grid of standoffs. Observe: a camera above the coupon reading crater positions against the corner. Manual: the laser safety measures, fixing the coupon, aiming the first pulse.

## What was tried to break it

1. **The coupon is not the joint.** *Conflict:* a straight corner and a 6.35 mm plate against a 1.65 mm wall on a curved pocket. *Change:* an L-coupon cut from the same tube and plate stock; the curvature is a second-order effect at the dot. *Uncertain:* reflectivity and heat flow differ.
2. **It operates the laser.** *Left standing:* the study does not operate equipment; this is a proposal and the operating conditions are Derek's to decide.
3. **Ticks in the weld.** *Conflict:* marks on the plate face near the corner would be in the fusion zone. *Change:* on the rim top, 6.35 mm above the corner and outside it. *Uncertain:* the gun's reach and the low-power behaviour of the head [unknown].

## Branches and combinations

Checks datum-02's sensor bias (an unlike second observer); its dot-to-melt result is the missing term in every scene's I/O panel.

## Unresolved problems and questions for Derek

Is there a low-power or single-pulse mode you would use for witness marks? Would you accept scrap L-coupons in the workflow?

## Assumptions

Red dot 630-670 nm, 0.3 mW [manual p. 12]; red-light alignment adjustment [manual pp. 25, 39]; RS232 and DB25 ports [manual p. 16]. No mark geometry is modelled.

## Sourcing pointers

None looked up; an L-shaped offcut is the same 316L stock.

## Scene id

None.
