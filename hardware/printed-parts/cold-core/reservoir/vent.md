# Reservoir air tubes

Each reservoir has an independent, bidirectional **4 mm OD / 2.5 mm ID**
neoFlo LLDPE air tube. Air enters as liquid is drawn out and leaves as the
reservoir fills. The open upper end stands **6 mm above the outer foam cap**
in the appliance's equipment space. Filtering is deferred.

## Lid and splash protection

A TPU 90A spool seats in matching 45° countersinks through the lid's 4 mm
flat plate. Both annular faces are flush. The air spool has a 6 mm waist,
8 mm flares and 3.9 mm bore, with 0.3 mm lead-ins opening to 4.5 mm.
Print two [reservoir-air-grip.step](reservoir-air-grip.step) parts per machine.
The production geometry is shared in [../_reservoir_ports.py](../_reservoir_ports.py).

The integral baffle below the lid has a closed floor and four 3 × 2 mm side
slots. Its OD is 13 mm, ID 9 mm, total drop 3 mm and floor thickness 1 mm.
The chamber clears the lower TPU flare. Air passes sideways through the
slots to the tube opening; the closed floor intercepts direct upward splash.
The tube ends 1 mm below the plate and 1 mm above the baffle floor.

## Through the insulation

Air axes in the native cold-core frame are A **(120, -26)** and
B **(-102, -32.5)** mm. The top foam-cap cup has an integral 5.2 mm passage
with 2 mm printed wall at each station. Each passage continues through the
pour lid. The 0.6 mm radial clearance lets the tube slide through; the TPU
grip in the reservoir lid sets its insertion depth. Foam fills around the
printed passage rather than contacting the tube.

The nominal straight cut length is **31.25 mm per tube**. Fit the three flush
spools to each reservoir lid before closing it. Feed each air tube through
the casing passage and its TPU grip, leaving 6 mm visible above the casing
face. This places its lower end clear of the baffle floor. Keep the bore
open in both directions. Existing white 4 mm stock supplies both pieces.

## Qualification

[The approved review](tube-vent-proposal/README.md) records the dimensions
and native assembly clearance. Geometry establishes an open path; printed
grip, splash performance and installed airflow have no physical acceptance
result yet. The [manufacturer tubing sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
specifies the 2.5 mm ID and 25 mm minimum bend radius. These short runs are straight.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
