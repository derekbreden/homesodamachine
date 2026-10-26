# Reservoir floor and dip tube

The cavity floor is one flat [3 mm](RESERVOIR_WALL_T) slab, and the body stands on its bag pocket's
own floor, [0.25 mm](RESERVOIR_CLEARANCE) over it, so the reservoir fills its pocket from floor to
rim. The wet floor is at z = [5.25 mm](FLOOR_Z) in the cold-core frame. The body prints mouth up
with that floor on the bed and needs no support under it. The cavity holds
[1.37 L](RESERVOIR_CAPACITY) floor to rim, [1.13 L](RESERVOIR_WINDOW) of it between the first and
last reed's heights ([level sensing](level-sensing.md)).

Both of the reservoir's mouths are in its cap, each a ⌀[7.5 mm](FILL_BORE_D) bore on a
⌀[11.5 mm](FILL_BOSS_OD) boss hanging into the headspace:

- **Fill**, at A [(102.5, -57.5)](FILL_POSITION_A) and B [(-90.5, 43.5)](FILL_POSITION_B). The line
  from the fill valve ends in the bore, and what it carries falls into the headspace above the
  liquid.
- **Draw**, at A [(84.2, -45)](DRAW_POSITION_A) and B [(-94.3, 9.5)](DRAW_POSITION_B). The line to
  the draw valve is its own dip tube: one length of the black 1/4" LLDPE, down the top cap's
  conduit and the cap's draw bore to the floor. Its end is cut at 45° and rests on the floor, so
  the cut face can never seal flat against it. The bore and the conduit over it hold the tube
  upright, clear of the float's travel.

Everything that enters the reservoir crosses the cavity before it leaves, which is what the
purge and rinse modes rely on. The wetted parts are the printed body and cap, the rod, the float
and the tube; no fitting stands in the cavity.

## Fitting the dip tube

The tube goes in from above once the reservoir is closed and in its pocket. Straighten the length
by hand, cut its end at 45°, and push it down the conduit and the draw bore until the tip touches
the floor. The other end goes on to the draw valve with the rest of its run
([internal plumbing](/hardware/assembly/internal-plumbing.md)).

The current 7.5 mm bores are guides with clearance around the 1/4-inch tube;
they supply no specified axial grip. Derek reports easy tube insertion into
the printed lid. The remote push-fit connection retains the tube at its
fitting, while no local grip in the lid fixes the dip-tube depth.

The [tube-grip review](tube-grip-vent-review.json) records a matched PETG/TPU
candidate: a spool-shaped TPU insert with a cylindrical waist and 45° flares
at both ends, seated flush in matching countersinks in the lid port. Both
objects are designed together. The bore controls sliding grip; the flares
capture the insert and block the direct splash gap. The present port spans
11 mm through its boss, including the 4 mm cap plate, so its complete span
sets the captured waist. Bore interference and printed retention have no
physical result yet. This candidate is not in the current printed geometry.

## Open items

- [ ] The floor and walls are the reservoir's fluid barrier — the print has to hold syrup under
  working head with no weep. Print guidance in [`watertight-petg.md`](watertight-petg.md); attempts
  tracked in [`print-log.md`](print-log.md). The September water-hold result belongs to the
  articles it tested.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
