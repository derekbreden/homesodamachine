# room-12: one-axis head, the gun or the tube clears the swap

**Origin:** branch of `use-02-swing-head` (and, in its two-station mode, of `use-07-two-stations`), made in the wave 2 exchange (`exchange/room--on--use-w2.md`, section 1 and 3). **Scene:** `scenes/room-12-one-axis-head`. **Depth:** developed (three calculations behind it).

## Picture it

The gun sits in its printed shell with a flange of three balls a hand's width behind the nozzle. Behind the housing a short rail runs along the barrel axis, rising at 45°; a carriage on it holds the gun by a back plate, tie-rods and a float spring. In front of the flange, fixed in the room, a ring plate with a hole the barrel passes through carries three grooves; it stands on its own short box column with its own foot. To end a bead, the carriage runs back along the rail: that is the lift. Run it 130 mm and the gun is out of the way of a tube lift. Or leave it at 20 mm and the rotator, on two rails in the bench, slides away to a loading end 520 mm off, while a second rotator on the same carriage arrives.

## The proposal

use-02 swings the head aside so a tube can be lifted out. This idea removes the swing and asks who else can get out of the way.

- **Head clears (tube stays).** Plunge along the barrel axis about 130 mm. With use-02's own gun samples and swap volume (radius 95 mm, 65 mm above the rim) the proxy leaves the volume at 88 mm and has 30 mm to spare at 130 mm (`calc/plunge-only.mjs`). The seat becomes a ring the barrel retracts through, placed at gun-local z 138 (a ring at 108 intrudes 12 mm into the volume; at 138 it clears by 9 mm at Rc 45).
- **Tube clears (head stays).** The rotator rides a carriage to a loading end. The head needs only its 20 mm retract; the swap volume is above a tube that is elsewhere. With two rotators on the carriage, one head has two seats' worth of work and the fibre never moves.
- **Two carriers.** The seat ring has its own short box column; the rail's mast (about 590 mm tall) carries the gun only in transit and may be sloppy.

## What carries the loads, what establishes position, what is free or restrained

- **Travelling:** gun, shell, back plate, tie-rods, float spring, carriage, rail, mast, bench. **Seated:** gun, shell, flange balls, ring plate, its column, the bench. The float lets go of the rail.
- **Position:** six ball-to-groove contacts (a Maxwell coupling). Amplification at the dot 4.25 for a ring at z 138 with Rc 45 (5.1 for use-02's fork at Rc 30; 3.3 at Rc 60; `calc/ring-seat.mjs`).
- **Free:** the carriage on its rails between two stops. **Restrained:** all six at the seat. **Driven:** one plunge axis; optionally one carriage.
- **Escape at the end of a bead:** the plunge itself: the first 10 mm is the lift that breaks the wire in air [repo]; at 40 mm/s that is 0.25 s (speed illustrative).

## What software could command, observe, and what stays manual

- **Command:** plunge (retract, clear, seat); carriage (only when the plunge is out 20 mm); the existing rotator.
- **Observe:** plunge and carriage end-stops; seat continuity through the three pairs; carriage position; a dot camera as in use-02 (not drawn).
- **Manual:** campaign trim (three screws between gun and shell), loading, trigger, snipping a stuck wire.

## What was tried to break it

1. **The shared post.** use-02's fork hangs off the same post as the swing arm. In statics (`calc/seat-loop.mjs`; load at the cable exit, dot 124 mm from the seat) a newton of pull moves the dot 25 µm (round steel bars, as drawn), 71 µm (aluminium bars), 119 µm (2020 T-slot); use-02's seat scatter is 25 to 30 µm RMS. *Assumption:* the seat is the only source of pose scatter. *Change:* the ring on its own column: 3 µm/N in a 40×40×3 aluminium box, 6 µm/N in a 25×25×2.5 steel tube (column 342 mm, arm 100 mm), 42 to 52 µm/N in T-slot along the cable's exit line. *Leaves:* joints, bench flexure, contact compliance, T-slot torsion (guessed).
2. **A long plunge.** 88 mm clears use-02's volume; 130 mm gives 30 mm. *Assumption:* the swap volume is real (it is use-02's illustrative one). *Leaves:* how far a hand lifts a tube before sliding it.
3. **The ring hole.** The gun retracts through the seat, so the barrel, collar, wire bracket and conduit must pass: Ø50 mm assumed. *Leaves:* the real wire-guide and conduit envelope; a wider Rc keeps the balls on the ring.
4. **Tube clears.** The rim passes under the nozzle with 5 mm at plunge 0 (19 mm at 20 mm). *Cost:* rails, a carriage, and (two stations) a second nest, shoe and purge line, the same as use-07. *Leaves:* whether sliding a seated tube disturbs its 0.20 mm seat; stop repeatability.
5. **The cable.** No swing, so nothing turns the fibre about a vertical axis. The hook is fixed on the mast; the exit moves along a line 25° from the run to the hook. *Leaves:* the Bezier stand-in has no stiffness or twist.
6. **A wire fused into the bead.** Retract stops after 4 mm (HOLD); a hand snips; the plunge stays force-limited (use-02 R6).
7. **Printed grooves.** A 6 mm steel ball on a printed groove sinks 25 µm at 20 N (Hertz, illustrative); a steel insert about 2 µm. *Leaves:* wear and creep of anything printed: unmeasured, no repair found beyond hardened inserts.

## Branches and combinations

- Two rotators on the carriage is `use-07` with the stations moving instead of the head. The spare station is the natural home of `use-12-golden-tube`.
- The carriage is `room-01b` (slot) and `room-05` (drawer) with use-02's seat on the head.
- Combines with `room-13` (the pull slider uses the same statics) and `room-14` (a hand that fires without holding).
- Test the sequence with `trials-06`'s mule (a printed dummy in the shell with ballast) before the real gun goes on the rail.

## Unresolved problems, and questions that need Derek's observation

- Gun mass, centre of mass, umbilical pull, trigger force (the weigh-in of room-02 measures three of them).
- Which side the operator sits on and how far a tube lift needs to clear; how fast and how far he lifts at the end of a bead today.
- Whether a slot in the bench for a carriage is acceptable.

## Assumptions

- **[illustrative]** kit gun proxy and opening pose; swap volume (use-02); stroke 150 mm, carriage 520 mm, column 342 mm, ring hole Ø50 mm, plunge speed 40 mm/s.
- **[derived]** statics of a 3D beam frame; Hertz contact; Maxwell coupling (a port of use-02's matrix).
- **[manual]** cable radii 350 / 240 mm (p.20). **[repo]** rim 238.4 mm above the bench, retract with the trigger held, snip the wire with the head where it stopped, 0.20 mm pilot.
- **[unknown]** real nozzle and wire-guide geometry, printed seat wear, the umbilical's pull.

## Sourcing pointers

`sourcing/room.md` entry 19 (aluminium square tube, the seat column), entries 10 and 12 (MGN12H rails, 2020 extrusion), `sourcing/use.md` (NEMA 17 with T8 lead screw, 6 mm G25 balls).

## Scene

`scenes/room-12-one-axis-head`
