# Reservoir floor and dip tube

The cavity floor is one flat [3 mm](RESERVOIR_WALL_T) slab, and the body stands on its bag pocket's
own floor, [0.25 mm](RESERVOIR_CLEARANCE) over it, so the reservoir fills its pocket from floor to
rim. The wet floor is at z = [5.25 mm](FLOOR_Z) in the cold-core frame. The body prints mouth up
with that floor on the bed and needs no support under it. The cavity holds
[1.37 L](RESERVOIR_CAPACITY) floor to rim, [1.13 L](RESERVOIR_WINDOW) of it between the first and
last reed's heights ([level sensing](level-sensing.md)).

The fill and draw mouths are in the cap's 4 mm flat plate. Each has a TPU
90A spool seated flush in matching 45° countersinks: 9 mm waist, 11 mm
flares and a 6.2 mm gripping bore with 7 mm entry lead-ins.

- **Fill**, at A [(102.5, -61)](FILL_POSITION_A) and B [(-90.5, 43.5)](FILL_POSITION_B).
  A's continuous tube ends 1 mm below the plate in the headspace. B receives
  the captured NeoFit stem elbow, with its existing trimmed tip position.
- **Draw**, at A [(84.2, -45)](DRAW_POSITION_A) and B [(-94.3, 6)](DRAW_POSITION_B).
  One continuous 1/4-inch tube passes through the casing guide and TPU grip
  to the flat floor. Its end is cut at 45° so it cannot seal flat against it.

Everything that enters the reservoir crosses the cavity before it leaves, which is what the
purge and rinse modes rely on. The wetted parts are the printed body and cap, the rod, the float, the TPU grips, the B-fill stem
and the tube. No fitting crosses the floor or sidewall.

## Fitting the dip tube

The tube goes in from above once the reservoir is closed and in its pocket. Straighten the length
by hand, cut its end at 45°, and push it down the conduit and the draw bore until the tip touches
the floor. The other end goes on to the draw valve with the rest of its run
([internal plumbing](/hardware/assembly/internal-plumbing.md)).

The local TPU grip is designed to hold dip-tube depth while permitting hand adjustment.
The casing passage guides it from above; the remote fitting retains the other
end. The two 45° flares capture the spool and obstruct the direct splash gap.
Print four [reservoir-tube-grip.step](reservoir-tube-grip.step) parts per machine.
A 6.35 mm nominal tube has 0.15 mm diametral interference with the candidate
bore; actual tube OD and printed TPU determine sliding feel. No printed
insertion-force or retention result is recorded. The
[approved geometry review](tube-vent-proposal/README.md) establishes nominal fit.

## Open items

- [ ] The floor and walls are the reservoir's fluid barrier — the print has to hold syrup under
  working head with no weep. Print guidance in [`watertight-petg.md`](watertight-petg.md); attempts
  tracked in [`print-log.md`](print-log.md). The September water-hold result belongs to the
  articles it tested.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
