# Reservoir floor and dip tube

The cavity floor is one flat slab, and the body stands on its bag pocket's
own floor, over it, so the reservoir fills its pocket from floor to
rim. The wet floor is at z = in the cold-core frame. The body prints mouth up
with that floor on the bed and needs no support under it. The cavity holds
 floor to rim, of it between the first and
last reed's heights ([level sensing](level-sensing.md)).

The fill and draw mouths are in the cap's 4 mm flat plate. Each has a TPU
90A spool seated flush in matching 45° countersinks: 9 mm waist, 11 mm
flares and a 6.2 mm gripping bore with 7 mm entry lead-ins.

- **Fill**, at A and B.
  Both continuous 1/4-inch tubes end 1 mm below the plate in the headspace.
  B's tube turns through its independent R14 holder before entering the TPU grip.
- **Draw**, at A and B.
  One continuous 1/4-inch tube passes through the equipment lid and TPU grip
  to the flat floor. Its end is cut at 45° so it cannot seal flat against it.

Everything that enters the reservoir crosses the cavity before it leaves, which is what the
purge and rinse modes rely on. The wetted parts are the printed body and cap,
the rod, the float, the TPU grips and the tubing. No fitting crosses the floor
or sidewall.

## Fitting the dip tube

Install the fill, draw and air tubes before the body foam pour, with the
reservoir closed and seated in its pocket. Straighten the draw tube by hand,
cut its end at 45°, and feed it through the TPU grip until the tip touches
the floor. Position its free upper end on the equipment-lid opening's axis;
after cure, thread the lid over it. The other end goes on to the draw valve
with the rest of its run ([internal plumbing](/hardware/assembly/internal-plumbing.md)).

The local TPU grip is designed to hold dip-tube depth while permitting hand adjustment.
The equipment-lid opening guides it from above; cured foam surrounds only
the dry span outside the reservoir, and the remote fitting retains the other
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
