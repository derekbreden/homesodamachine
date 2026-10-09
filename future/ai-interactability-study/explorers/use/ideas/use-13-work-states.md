# use-13-work-states: the tube travels, state by state

Scene: `scenes/use-13-work-states/index.html`. Origin: branch of `travel-01-tube-travels` (exchange wave 2, `exchange/use--on--travel-w2.md` section 1). Maturity: developed. Numbers: `explorers/use/calc/w2_t1_states.mjs`.

## Picture it

travel-01's rig (a fixed gun in a locked holder; a shuttle, Z and X stack under the rotator) followed through eleven states of one closure: load and indicate at the out position, seat the plate, approach 1 (drop, shuttle in, rise), trim and tack, face check out again, approach 2, trim and dry lap, weld, escape, hold (a fused wire), unload. A panel on the stage names, for the state you pick, what the hand does, what an eye is for, what software commands and what holds the pose; an amber marker shows where the hand is.

## The proposal

Read travel-01 as a sequence and its Z axis has three jobs (a fine trim, clearance for the shuttle, and, if the bead must end with the head leaving, the escape) and the closure has two approaches. Put a drop tier with hard stops under the fine Z (travel's own stack rule: long axes at the bottom) and the swap clearance and the escape become one commanded motion.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the fixed holder carries the gun and (by a hanger, not drawn) the cables; the shuttle, the drop tier and the fine plate carry the rotator and tube.
- **Establishes position:** the shuttle hard stop and the drop tier's top stop, then a camera-driven trim after the last approach.
- **Free / restrained / driven:** everything on the gun side is fixed; shuttle, drop tier, fine Z and X are driven.

## What software could command, observe, and what stays manual

- **Command:** shuttle in and out to hard stops, the drop tier down and up, fine Z and X, the rotator; an interlock (no shuttle unless the barrel is clear of the rim); a hold state that inhibits every axis.
- **Observe:** end-stop switches, step counts, the dot by an overhead camera. Blind: nozzle-to-rim clearance, return error, a fused wire.
- **Manual:** loading, indicating and plate seating at the out position, firing the tacks and the weld, snipping, the escape distance.

## What was tried to break it

1. **Z's range against the swap margin.** In the kit's pose the tip is 5.0 mm above the rim plane; fine Z is +-6 mm. In travel-01's own scene the shuttle rim badge is red from Z = +2 mm (measured), so 8 of 12 mm are shuttle-safe. *Change:* an interlock, or the drop tier. *Leaves:* the real margin.
2. **The escape has no owner.** 20 mm along the beam is 28.1 mm of Z (vertical component 0.712), 0.47 s at 60 mm/s; the fine range gives at most 8.5 mm. *Assumption:* the sequence has a lift; guide 46 says only "release the trigger, then the pedal". *Change:* the drop tier; or the gun plunges back on a slide (room-12's branch, a radio in the scene; force-limited, it stops after 4 mm on a fused wire). *Leaves:* whether a lift is needed, how far, how fast.
3. **A return axis's tilt is face runout.** 0.05 degrees is 0.054 mm at r = 61.85 mm once per revolution at the fixed gun. *Leaves:* the tier's real tilt repeatability.
4. **Two approaches.** Tack, verify face TIR, then weld: two hard-stop landings; the trim follows the second. *Leaves:* a dial opposite the gun removes one.
5. **A fused wire** is a hold state: every axis inhibited until a hand cuts.

## Branches and combinations

- `room-12-one-axis-head` draws the alternative (the gun escapes, the work swaps).
- With `use-15-examples-as-days` (the hand-on-gun minutes of this arrangement) and `use-05-gates` (a hold state).

## Unresolved problems and questions for Derek

- How do you end a bead today, how far does the head go before the wire is free, and does it lift at all?
- Could the dial stand opposite the gun for the face check after tacking?
- Tube length and plate seat depth spread (ten tubes, calipers).

## Assumptions

- Kit proxy gun and reference pose; stack height 100 mm, shuttle 200 mm, fine Z +-6, fine X +-8, drop 40 mm, escape 20 mm, return error 0.4 mm: illustrative. Sequence order **[repo]** guide 46; the lift-away is from the shared context.

## Sourcing pointers

`sourcing/travel.md`: lab jack (6, 25 kg), MGN12 rails, dovetail tables. Nothing new.

Scene id: `use-13-work-states`.
