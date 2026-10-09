# trials-08-loader-tended-cell: the software runs, a person swaps when asked

No scene of its own; the state walk in `trials-02-dock-reset` (step 7, "Swap", drawn for a hand) is its picture.

## Picture it

The AI is running trials. When the tube's batch of trials is done it parks the gun in its dock and asks for the next tube by number, on a screen or a light. Somebody lifts the tube (or the puck) out, sets the next one in and presses a button. The software reads the ID, checks the seat, and carries on. Between visits the person does something else; the AI schedules its work so that visits are rare.

## The proposal

Take Derek's motorised vision **[Derek]** (XY, Z, two rolls, two PTZ cameras) with the tube swap left manual, and make the human a first-class part of the state machine: "waiting for a swap" is a state with a timeout, a request, a verification and a refusal (no verified seat: no motion). The AI groups its work: all the trials a tube can inform (`trials-15-one-tube-many-poses`), and idle-time jobs while it waits (dock weigh-in, board calibration, self-tests).

## Carries, locates, free

The arrangement is not chosen: this idea is about the loop around it. Position comes from whichever positioner is in use plus the dock (trials-02); the tube's from the nest or the puck.

## Software

- Command: everything the vision lists; a request to the human; the interlock.
- Observe: tube present (camera or the seat certificate), ID (tag or a label the camera reads), seat check, time waiting.
- Manual: the swap, and unloading.

## Tried to break it

1. **The human is a source of variation.** Assumption: any swap is equivalent. Change: record who and when, and have the AI test swap noise itself (re-seat the same tube ten times). Leaves: whether the swap noise is small next to tube-to-tube variation is **[unknown]**.
2. **Waiting is the cost.** With a 10 minute swap and 20 trials per load about 80 % of the rig's time is trials (`swap_budget.py`, illustrative). Repair: batch. Leaves: nothing if the AI can generate 20 informative trials per tube.
3. **It stops overnight.** Yes: that is the boundary. It supports a working day of the AI and one person, not weeks.

## Combinations

Feeds `trials-01`, `trials-02`, `trials-15`; the unattended version is `trials-07`.

## Wave 2, borrowed from `room-05-drawer-cell`

The swap can be a drawer: the rotator rides out on slides for loading and rolls back into a kinematic dock under the fixed gun, instead of a hand lifting a puck out from under a docked gun. It changes what "waiting for a swap" means (the person loads at arm's length in a laser-safe cabinet; the interlock is the drawer) and it makes the puck (trials-01) optional. Not drawn here.

## Unresolved

Q: How long does a swap take you today from lifting the tube out to a tube ready to run?

## Assumptions

Times **[unknown]**, illustrative.
