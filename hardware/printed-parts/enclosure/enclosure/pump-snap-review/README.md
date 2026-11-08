# Pump retainer snap evidence

The [cartridge trial](../../../../print-tests/pump-cartridge-snaps/README.md) binds
the production 2.0 mm leaves, 22.25 mm root-to-catch length, 1.5 mm inside root
blend and 2.6 mm seated catch overlap. Both full-Y wings have 0.25 mm receiver
end clearance. The receiver floor has 0.4 mm static catch allowance and a
centered 5 mm tool opening beneath one continuous 45° corbel.

Both front wings use the common approved planar lead-in from the above-core
design, with matching receiver roofs and pry openings. The fitted pump wells,
retaining planes, lateral catch reach, spring section and roots retain their
datums. The [long-tip reading](long-tip-fit.json) records the production solids
and seated receiver clearance. Physical insertion effort remains to be verified.

The standalone STEP/STL carries the relaxed 0.35 mm outward tip pose. Both
complete assemblies and the front-top/pump-mount GLBs carry the 0.10 mm seated
pose. The cubic curves illustrate positions; they are not elastic analysis.
The retainer prints Y-end down, with X/Z spring bending within the layer
plane. Front-top retains its seam-plane pose. Its pockets keep their broad
outer backing. The tool openings retain the wall section beneath the flute
valleys and admit the screwdriver working envelope.

The [cartridge-trial geometry reading](../../../../print-tests/pump-cartridge-snaps/geometry-review.json)
measures the exported fine/printed meshes, both pumps, seated overlap and
retaining-floor contact for its identified articles. [Print jobs](../../../../print-tests/pump-cartridge-snaps/print-jobs.json)
bind the compact full-Y ramp comparison, complete two-pump fixture and
separate pointed rear-cap comparison. They are prepared and unsubmitted.
Physical support removal, distributed bending, force, retention, repeated
release, vibration, load capacity, creep and lifetime remain unqualified.

[`native-review.json`](native-review.json), [`print-review.json`](print-review.json)
and [`baseline-hardware.json`](baseline-hardware.json) identify their own
archived articles, source hashes, member lists and print processes. Their
results apply to those inputs. The manual analytic reader,
[`review.py`](https://github.com/derekbreden/homesodamachine/blob/5d633291918a02e34734ef15445158dcaa97d8c8/hardware/printed-parts/enclosure/enclosure/pump-snap-review/review.py),
is in Git history.
