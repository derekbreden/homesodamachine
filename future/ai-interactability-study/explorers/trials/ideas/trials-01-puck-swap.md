# trials-01-puck-swap: the nest and the tube swap as one lift

Scene: `scenes/trials-01-puck-swap/index.html` (worked deeply). Calc: `explorers/trials/calc/swap_budget.py`. Sourcing: `sourcing/trials.md` (balls, dowels, magnets, Hall sensor, NFC).

## Picture it

The tube stands in a printed puck (the nest with its three radial adjusters) that sits on three ball-and-dowel seats on the turntable, pulled down by magnets. To swap tubes, a hand (or a gripper) lifts the whole puck 45 mm and carries it to a prep stand at the bench edge; the next puck, already indicated at the stand while the rig was running, is lowered onto the same three seats. A small magnet on the puck's rim passes a Hall sensor on the base once a turn, so the rotator has an absolute zero; a tag on the flange names the tube.

## The proposal

The replaceable nest **[repo]** (`weld-rotation-rig.md`: three M3 screws hold it to the turntable) becomes a puck: the nest body plus a flange with three steel balls under it, seated on three pairs of steel dowels in the turntable (a Kelvin coupling: six contacts, no redundancy). Three pieces of context ride on it:

1. **A seated certificate.** Each ball-and-dowel pair is a switch. Three closed contacts is the software's proof that the puck is in its one place before anything spins. Three open ones after a lift is the proof that it is out.
2. **Rotational phase.** The seats are spaced asymmetrically (0, 115, 240 degrees in the scene), so the puck seats in one phase only. The tube's phase relative to the rotator is then the same every time that puck is on the rig.
3. **An index and an identity.** The rim magnet plus a Hall sensor gives one pulse per turn (the rotator only counts turned-so-far degrees today **[repo]**). A tag holds the tube ID; the seam map (trials-04) and the trial history are stored in software under that ID.

The nest indicating that takes minutes on the rig moves to a **prep stand**: a second seat set (or a hand-turned bearing) with the indicator on its stand, so the AI runs trials on puck A while a person indicates puck B.

## What carries the loads, what establishes position, what stays free

- Loads: the three ball-and-dowel seats carry puck and tube (1.40 kg with one plate, 2.01 kg with two **[repo]**, plus the puck, illustrative 0.6 kg). The magnets only keep the balls seated; they do not locate. The 165 mm ball race and belt drive below are unchanged.
- Position: the seats fix all six degrees of freedom of the puck to the turntable, phase included. The tube's position *inside* the nest is set by the nest's 0.20 mm ID pilot, 0.40 mm OD guide and three M3 adjusters **[repo]**: the puck does not touch that.
- Free / restrained: puck is fully restrained when seated; in the swap it is free (hand or gripper). Nothing rotates during a swap; a swap interlock is proposed.

## What software could command, observe, and what stays manual

- Command: rotator speed (existing controller); a swap interlock (no motion while a puck is lifted); which puck is expected next.
- Observe: seat certificate (three contacts); tag read (at the stand, where the reader is not near a spinning tube); index pulse per turn; and from the judge cameras (trials-03/-04/-05) the tube-in-nest eccentricity, which the puck cannot see.
- Manual / unresolved: the lift and carry (or the gripper of trials-07), the indicating at the stand, tagging a new puck, and how a 2 kg lift is done safely.

## Tried to break it

1. **Throughput.** Conflict: if a loaded tube supports many trials, the swap barely matters. Assumption behind my first claim: swap time dominates. Change: with a 10 minute hand swap and 20 trials per load the rig is used about 80 % of the time; with a 30 second puck swap, 99 % (trial 120 s; `swap_budget.py`; times are illustrative, nobody has timed a swap **[unknown]**). What it leaves: the puck does not earn its place on throughput. It earns it when many *different* tubes are wanted (30 tubes: 5 hours of indicating on the rig versus 15 minutes of swapping, with the same 5 hours done off the rig) and when swap-to-swap repeatability is itself the measurement.
2. **The coupling does not fix the tube in the nest.** Conflict: the seam still wobbles with the tube's seating (scene slider). Assumption: repeatable puck means repeatable seam. Change: the coupling repeatability adds only about 20 micrometres lateral and 4 vertical at 10 micrometres (first order, `swap_budget.py`); tube-in-nest dominates. What it leaves: how repeatable a lift-out and re-seat of the tube in the *present* nest is has never been measured **[unknown]**. Ten lifts and re-seats with the Neoteck indicator would put a number on it, and would tell whether the puck is needed at all.
3. **Torque through the seats.** Conflict: a wire catch could twist the puck off its seats. Assumption: magnets hold. Change: three balls at 80 mm with 30 N of preload hold about 2.4 N·m before a ball leaves its groove; each newton of tangential wire pull at the weld radius is 0.062 N·m. Leaves: the wire-pull force is **[unknown]**; preload is illustrative.
4. **Printed seats.** Conflict: a printed body on printed seats wears. Repair: steel balls and dowels set into the print; plastic only positions them. Leaves: creep of the PET-GF around the steel under magnet preload, untested.
5. **The seats sit above the ball race.** The 36-ball race is at 82.5 mm radius **[repo]** and the seats at 86 mm in the scene: the load path from seat to race through a printed turntable is not checked. Leaves: turntable stiffness at the seats.
6. **Phase without an index sensor.** Conflict: the rotator has none **[repo]**. Repair: the rim magnet and Hall sensor. Leaves: a Hall sensor near the puck rim has a gap tolerance and a 3 to 4 mm switching distance that nobody has tried.

7. **Phase from the seats, or from the work (from datum's exchange, wave 2, section 1: "would you trade asymmetric seats for a symmetric pattern and an index from the work?").** *Conflict:* an asymmetric pattern gives a unique phase but forbids turning the puck; a symmetric one allows a 120 degree turn that separates the rig's part of the seam map from the tube's in one extra lap. *Assumption behind the asymmetric choice:* phase must come from the geometry. *What the change alters* (`calc/seat_sets.py`, brute force): (a) the plate's two symmetric ports read modulo 180 degrees still tell the three symmetric seatings apart (0, 120 and 60), so a work index is enough for phase, at the price of the seats no longer certifying it; (b) a 120 degree turn leaves harmonic 3 of a tube-owned error unchanged (weights 2 |sin(k theta / 2)| are 1.7, 1.7, 0.0 for harmonics 1 to 3), so it cannot be told from the rig's; (c) a turntable with **two groove sets 70 degrees apart** keeps the asymmetric puck's unique phase in each set and gives a turn that exposes harmonics 1 to 4 (1.2, 1.9, 1.9, 1.3): only rotations 0 and 70 degrees seat, and a contact per set says which. Three more dowel pairs in the printed turntable. The scene has a seat pattern radio for the three. *What it leaves uncertain:* whether a designed turn is worth an extra lap and a lift depends on how large the tube-owned part of the map is, which nobody has measured.

## Branches and combinations

- `trials-01b-nest-as-puck` (branch, idea file): the smallest version. Keep the present nest, replace its three M3 screws by the three ball-and-dowel seats. Nothing else changes.
- Combines with `trials-02-dock-reset` (the gun is docked and interlocked during the swap), `trials-04-seam-map-replay` (the tag carries the map's key), `trials-07-toolchange-swap` (a gripper does the lift).
- Borrowed: industrial zero-point pallets are exactly this (pallet with a stud, receiver with ball-lock); one Prime listing is in `sourcing/trials.md`, with thin sales evidence.

- **Wave 2, borrowed from `datum-05-fiducial-collar`:** a ring of sixteen small tags on the puck flange, one of them a distinct zero tag, read by the same fixed judge camera that watches the dot. Phase and identity then need no Hall sensor on the base and no reader at the stand, and a drifting camera shows on the ring, which sits in its frame every frame. It is a radio in the scene (`How the puck's phase and identity are read`); the scene counts the tags in line of sight of the drawn camera (8 of 16 at the default view). The limit is datum-05's own lever-arm rule: the ring is 147 mm below the seam, so a tag's tilt error times that lever (0.3 degrees is 0.77 mm) rules it out as a position reference; it gives angle about the axis and the tube's name only. Phase error of 0.1 degrees is 0.1 mm *along* the seam, which does not matter (`trials-04`).

## Unresolved, and questions for Derek

- Q: How repeatable is a lift-out and re-seat of a tube in the present nest, read at the rim with the indicator (10 tries)?
- Q: How long does a swap plus indicating take today, in minutes, as you do it?
- Turntable stiffness at the seats; where the tag reader lives; who lifts a 2 kg puck.

## Assumptions

Dimensions of tube, plate, recess **[repo]**; masses **[repo]** and **[derived]**; nest clearances **[repo]**; seat radius, ball size, magnet preload, puck outline, prep stand: **[illustrative]**; swap and indicating times: **[unknown]**, illustrative in the scene.
