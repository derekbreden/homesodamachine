# Reservoir floor and dip tube

The body stands on its pocket's floor and prints mouth up on its own flat
floor. The dip tube reaches the wet floor. The reservoir source owns the
cavity, and the reed reference owns the sensing heights.
[Reservoir source](reservoir.rs) · [Level sensing](level-sensing.md)

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

Install A-fill and both draw and air tubes before the body foam pour, with
the reservoirs closed and seated in their pockets. Straighten each draw tube,
cut its end at the specified angle and feed it through the TPU grip until its
tip touches the floor. Locate the free upper end on the lid-hole axis so the
lid can pass over it after cure. Feed B-fill through the front after closing
the lid.
[Cold-core assembly](/hardware/assembly/cold-core.md#7-close-and-populate-the-top-lid)

The local TPU grip is designed to hold dip-tube depth while permitting hand adjustment.
The equipment-lid opening guides it from above; cured foam surrounds only
the dry span outside the reservoir, and the remote fitting retains the other
end. The two 45° flares capture the spool and obstruct the direct splash gap.
Print four [reservoir-tube-grip.step](reservoir-tube-grip.step) parts per machine.
A 6.35 mm nominal tube has 0.15 mm diametral interference with the candidate
bore; actual tube OD and printed TPU determine sliding feel. No printed
insertion-force or retention result is recorded. The
[approved geometry review](https://github.com/derekbreden/homesodamachine/blob/2fe626524a2af57d1b057789d2359bd71bab89c9/hardware/printed-parts/cold-core/reservoir/tube-vent-proposal/README.md) establishes nominal fit.

## Open items

- [ ] The floor and walls are the reservoir's fluid barrier — the print has to hold syrup under
  working head with no weep. Print guidance in [`watertight-petg.md`](watertight-petg.md); attempts
  tracked in [`print-log.md`](print-log.md). The September water-hold result belongs to the
  articles it tested.
