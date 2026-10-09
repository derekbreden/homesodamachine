# trials-16-tube-moves-gun-hangs: the only actuator is under the tube

No scene of its own; the follower radio in `trials-04-seam-map-replay` shows the tube-side branch.

## Picture it

The gun hangs from a passive support (a stand, a rigid arm, rings on bungees: not chosen). The rotator sits on a small stage. A camera watches the dot; the stage moves the tube until the seam is under the dot, then keeps it there through the revolution. All the motors are on the stationary workpiece side.

## The proposal

Split the positioning problem by which body moves. The gun's job is to hold still enough; the tube's job is to find it. With a camera in the loop the stage corrects slow gun sway, cable-pull drift and the tube's own wobble at once. It is `trials-04b-follower-under-tube` with the map dropped and the camera doing the work, or with both: the map as feed-forward, the camera as feedback.

## Carries, locates, free

The passive support carries the gun and umbilical; its compliance is what the loop must absorb. Only radial and vertical matter, so the stage needs an X axis and a lift. The judge camera sets position.

## Software

Command: stage X and lift; rotator speed. Observe: dot-to-seam error (camera); stage position. Manual: rough placement of the gun's support.

## Tried to break it

1. **Bandwidth.** A several-kilogram stage limits how fast it can chase gun sway; a slow loop only removes drift. Leaves: how fast the passive support sways, **[unknown]**.
2. **The passive support must not drift out of the stage's range.** Leaves: range versus support creep.
3. **A stage under a running rotator** must carry it stiffly (four Ø10 clamp holes to the bench **[repo]**).

4. **The passive support has to be stiff on two axes before the follower has anything to follow (from datum's exchange, wave 2, section 5).** See `trials-04b` item 5: the gun's static offset under the cable's pull (1 N is about 40 mm on bungees and wires) is far outside a tube-side stage's range and the dot knee's capture range; the passive support of this idea must be stiff on radial and vertical and stand on the work (a crown on the rim, `datum-03` and `datum-16`), and the camera loop's bandwidth (a few tenths of a hertz) then need only chase the slow part. The scene shows the numbers (`trials-04`, support radio).

## Combinations

`trials-04b`, `trials-03` (find the seam first), `trials-02` (the dock resets the support).

## Unresolved

Q: How far does a gun on a passive support wander in ten minutes with nobody touching it?

## Assumptions

All **[illustrative]**.
