# use-01-day-lanes: the day, lane by lane

Scene: `scenes/use-01-day-lanes/index.html`. Origin: swarm. Maturity: developed. A lens, not an arrangement: it is the framing's way of seeing the whole problem, drawn so the other scenes can be compared state by state. Nothing in it is a score or a ranking.

## Picture it

Ten columns run left to right, each one a state of one closure (load, indicate, plate and tack, contact and set-up, dry lap, weld lap, retract, an exception for a stuck wire, swap, review). Six rows run down: what a hand does, what a hand only holds, what an eye judges or merely watches, what software commands or observes, what sets the gun's pose, and what the laser is doing. Amber blocks, hatched blocks and teal blocks show where hands and eyes are needed; small diamonds mark where the pose changes owner. A thin bar across the top shows the real proportion of time; the laser-on part is a red sliver.

## The proposal

Treat the sequence of states, not the weld itself, as the object of design. For each arrangement (today's hand-held sequence, a flight recorder, a programmed table, a coach with a locking arm, a swing head with a seat, a swing head with preset cartridges) fill the same grid: who does what, who only holds, who judges, who is spare. Then ask, per state, what could be removed, what could be replaced by a sensor, and what must change hands.

Three readings fall out of it.

1. **The laser is on for a small fraction of a closure** (illustrative: tacks about 15 s and the weld lap about 51 s against 15 minutes on the station). An arrangement that only improves the weld lap improves a sliver of the day; indicating, plate seating and set-up dominate.
2. **Today the hand is actuator, support and safety guard at once** during tack, weld and retract. The arrangements differ mainly in which role they take away from the hand and give to something else: a rest takes the support role, a coach takes part of the aiming, a seat takes the position, a gate takes the veto.
3. **Presetting moves hand time off the station; it does not remove it.** With the presetter's load and indicate time added back the hand spends about as long per tube. The readout says so; only an advisor that shortens indicating, or a seat that removes aiming, cuts hand time.

## What carries the loads, what establishes position, what is free or restrained

Not a mechanism. The pose-owner lane is the load-and-reference answer in time: HAND (a person carries and aims), ARM (a support carries; something moved it), SEAT (a locating seat carries and fixes the pose), PARKED (out of the way), or nothing (no head aimed).

## What software could command, observe, and what stays manual

The software lane uses five chips: CMD (a command to something that moves), OBS (an observation), LOG (a record kept), ADV (advice to a hand), GATE (a check that can stop the next state). The laser is never commanded by software in any arrangement here; a hand fires it. What the hand lanes show is what stays manual.

## What was tried to break it

1. **Time as columns.** *Conflict:* short states (weld lap, retract) vanish or crush their text if columns are strictly proportional. *Assumption:* one axis can show both proportion and detail. *Change:* columns are widened to read and a to-scale bar sits above them. *Leaves:* the two representations disagree by design.
2. **Durations that are guesses.** *Conflict:* every duration except one lap (48.6 s at 8 mm/s [repo]) is illustrative, and the per-arrangement factors (dry lap 0.8 with a seat, 2.5 with coached aiming, on-station load 0.3 and indicate 0.2 with cartridges) are assumed. *Assumption:* a reader will not take them as findings. *Change:* nine sliders let Derek set his own numbers; the assumptions are listed on the page. *Leaves:* until he types real numbers this is shape, not measurement.
3. **A total looks like a score.** *Conflict:* station time or hand time totals invite ranking arrangements. *Assumption:* description is harmless. *Change:* totals are shown for the selected arrangement only, as three readouts (station time, laser-on time, hand time), and nothing is sorted or coloured better or worse. *Leaves:* a reader can still compare by switching.
4. **"Spare" is an opinion.** *Conflict:* marking a hand's hold or an eye's watch as spare assumes something else could do it. *Assumption:* the proposed sensors work. *Change:* the marks are toggleable and worded "spare use", not "waste"; the guard role of the eye during emission is kept as judge in every arrangement.
5. **The dry lap is not in the repo sequence.** *Conflict:* it is what the study needs and what the repo only does as a continuity revolution and a commissioning rehearsal [repo gate 9]. *Change:* the column is labelled with both.

## Branches and combinations

Each arrangement column points at its scene: `use-02-swing-head`, `use-03-preset-cartridge`; the coach, the recorder and the programmed table have their own ideas (`use-06-coach-loop`, `use-08-flight-recorder`, `use-09-programmed-table`). `use-04-the-lap` and `use-05-gates` are sibling lenses (rate of change; who may act alone). `use-07-two-stations` uses the same tasks for its schedule.

## Unresolved problems and questions for Derek

- Real durations of every state on a good day, and which of them repeat.
- How often a wire sticks (the snip column) and how often continuity blinks.
- Whether the operator would accept a screen for the aiming step in place of looking into the recess.

## Assumptions

- **[repo]** state order and content (per-weld sequence, rig guide 46); lap time 388.61 mm at 8 mm/s = 48.6 s; 380 degrees is 51.3 s **[derived]**.
- **[manual]** the head contains a vibration motor (p.20), listed among the things that change at the weld.
- **[unknown]** every duration except the lap; whether heat and tack shrink change the runout that was just indicated (assumed).
- Illustrative: base durations and factors as listed on the page.

## Sourcing pointers

None specific; the arrangements' parts are in `sourcing/use.md`.

Scene id: `use-01-day-lanes`.
